"""Загрузка фото одежды → анализ → выбор типа → стайлинг."""
import asyncio
import logging

from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.types import BufferedInputFile

from states import FashinFlow
from services.analyzer import analyze_garment
from services.image_utils import remove_bg_local, preprocess_garment
from keyboards.inline import (
    analyze_kb, type_suggestions_kb, type_groups_kb, type_list_kb,
    styling_kb, length_kb, fit_kb,
)

logger = logging.getLogger(__name__)
router = Router()

MAX_GARMENTS = 4


async def _get_photo_bytes(message: types.Message) -> bytes | None:
    bot = message.bot
    if message.document and message.document.mime_type and message.document.mime_type.startswith("image/"):
        file = await bot.get_file(message.document.file_id)
    elif message.photo:
        file = await bot.get_file(message.photo[-1].file_id)
    else:
        return None
    from io import BytesIO
    buf = BytesIO()
    await bot.download_file(file.file_path, buf)
    return buf.getvalue()


# ==================== Фаза 1: Загрузка фото ====================

def _rembg_sync(raw: bytes) -> bytes:
    """Синхронная обёртка для rembg + preprocess (для asyncio.to_thread)."""
    png = remove_bg_local(raw)
    return preprocess_garment(png)


@router.message(FashinFlow.waiting_garments, F.photo | F.document)
async def receive_garment_photo(message: types.Message, state: FSMContext):
    data = await state.get_data()
    photos = data.get("garment_photos", [])

    if len(photos) >= MAX_GARMENTS:
        await message.answer(f"Максимум {MAX_GARMENTS} вещей.")
        return

    status_msg = await message.answer("Обрабатываю фото...")

    raw = await _get_photo_bytes(message)
    if not raw:
        await status_msg.edit_text("Отправьте фото или файл изображения.")
        return

    is_first = len(photos) == 0

    # Параллельно: rembg + (для первого фото) анализ
    if is_first:
        # Анализ идёт по ОРИГИНАЛЬНОМУ фото (raw), не по clean — экономим время
        rembg_task = asyncio.to_thread(_rembg_sync, raw)
        analysis_task = analyze_garment(raw)
        clean_bytes, (analysis, cost) = await asyncio.gather(rembg_task, analysis_task)

        # Сохраняем анализ сразу
        await state.update_data(
            analysis=analysis.model_dump(),
            analysis_cost=cost,
        )
    else:
        clean_bytes = await asyncio.to_thread(_rembg_sync, raw)

    # DEBUG: показать результат
    await message.answer_photo(
        photo=BufferedInputFile(clean_bytes, filename="rembg_result.jpg"),
        caption="Результат удаления фона (debug)",
    )

    photos.append(clean_bytes)
    await state.update_data(garment_photos=photos)

    count = len(photos)
    if count < MAX_GARMENTS:
        await status_msg.edit_text(
            f"Фото {count}/{MAX_GARMENTS} получено.\n"
            f"Отправьте ещё или нажмите кнопку ниже.",
            reply_markup=analyze_kb(),
        )
    else:
        await status_msg.edit_text(f"Все {MAX_GARMENTS} фото получены.")
        await _show_analysis(message, state)


@router.callback_query(FashinFlow.waiting_garments, F.data == "garment:analyze")
async def cb_analyze(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if not data.get("garment_photos"):
        await callback.answer("Сначала отправьте фото.")
        return
    await callback.answer()
    await callback.message.edit_reply_markup(reply_markup=None)
    await _show_analysis(callback.message, state)


@router.message(FashinFlow.waiting_garments, F.text.startswith("/analyze"))
async def cmd_analyze(message: types.Message, state: FSMContext):
    data = await state.get_data()
    if not data.get("garment_photos"):
        await message.answer("Сначала отправьте фото.")
        return
    await _show_analysis(message, state)


# ==================== Фаза 2: Показ результата анализа ====================

async def _show_analysis(message: types.Message, state: FSMContext):
    """Анализ уже готов (параллельно с rembg). Просто показываем."""
    data = await state.get_data()

    if "analysis" not in data:
        await message.answer("Анализ не готов, попробуйте ещё раз.")
        return

    from models.garment import GarmentAnalysis
    analysis = GarmentAnalysis(**data["analysis"])
    cost = data.get("analysis_cost", 0.0)

    await message.answer(
        analysis.suggestions_card_text(),
        reply_markup=type_suggestions_kb([s.model_dump() for s in analysis.suggestions]),
    )
    await message.answer(f"Стоимость анализа: ${cost:.4f}")
    await state.set_state(FashinFlow.confirming_analysis)


# ==================== Фаза 3: Пользователь выбирает тип ====================

@router.callback_query(FashinFlow.confirming_analysis, F.data.startswith("type:"))
async def choose_type(callback: types.CallbackQuery, state: FSMContext):
    type_id = callback.data.split(":", 1)[1]

    if type_id == "other":
        # Показать группы
        await callback.answer()
        await callback.message.edit_text(
            "Выберите категорию:",
            reply_markup=type_groups_kb(),
        )
        return

    if type_id == "custom_prompt":
        # Ручной режим — пользователь пишет свой промт
        await callback.answer()
        await callback.message.answer(
            "✍️ <b>Режим ручного промта</b>\n\n"
            "Напишите промт для Grok Imagine как хотите.\n"
            "Он уйдёт в генерацию КАК ЕСТЬ, без модификаций.\n\n"
            "<i>На входе Grok получит:\n"
            "• Image 1 = ваше фото одежды\n"
            "• Image 2 = выбранная модель\n\n"
            "Пример промта:\n"
            "<code>A person wearing a short olive jacket with belt and epaulets. "
            "Image 1 is the jacket. Image 2 is the person. Dress Image 2 in the "
            "jacket from Image 1. Keep face identical. Full body, 3:4.</code></i>"
        )
        await state.set_state(FashinFlow.waiting_custom_prompt)
        return

    # Тип выбран — сохраняем
    from catalog import GARMENT_TYPES
    t = GARMENT_TYPES.get(type_id)
    if not t:
        await callback.answer("Тип не найден")
        return

    await state.update_data(
        chosen_type_id=type_id,
        custom_prompt=None,
        chosen_length=None,
        chosen_fit=None,
    )
    await callback.answer(f"Выбрано: {t['name_ru']}")
    await callback.message.edit_reply_markup(reply_markup=None)

    # Шаг: выбор длины (опционально)
    await callback.message.answer(
        f"<b>{t['name_ru']}</b>\n\nВыберите длину (или '⏭ По фото'):",
        reply_markup=length_kb(),
    )
    await state.set_state(FashinFlow.choosing_length)


@router.callback_query(FashinFlow.choosing_length, F.data.startswith("length:"))
async def choose_length(callback: types.CallbackQuery, state: FSMContext):
    """Длина выбрана → идём на посадку."""
    length_id = callback.data.split(":", 1)[1]
    if length_id == "auto":
        await state.update_data(chosen_length=None)
        await callback.answer("Длина: по фото")
    else:
        from catalog import LENGTHS
        l = LENGTHS.get(length_id)
        await state.update_data(chosen_length=length_id)
        await callback.answer(f"Длина: {l['label_ru']}" if l else length_id)

    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(
        "Выберите посадку (или '⏭ По фото'):",
        reply_markup=fit_kb(),
    )
    await state.set_state(FashinFlow.choosing_fit)


@router.callback_query(FashinFlow.choosing_fit, F.data.startswith("fit:"))
async def choose_fit(callback: types.CallbackQuery, state: FSMContext):
    """Посадка выбрана → показываем стайлинг."""
    fit_id = callback.data.split(":", 1)[1]
    if fit_id == "auto":
        await state.update_data(chosen_fit=None)
        await callback.answer("Посадка: по фото")
    else:
        from catalog import FITS
        f = FITS.get(fit_id)
        await state.update_data(chosen_fit=fit_id)
        await callback.answer(f"Посадка: {f['label_ru']}" if f else fit_id)

    await callback.message.edit_reply_markup(reply_markup=None)

    data = await state.get_data()
    from models.garment import GarmentAnalysis
    analysis = GarmentAnalysis(**data["analysis"])

    if analysis.styling:
        await callback.message.answer(
            analysis.styling_card_text(),
            reply_markup=styling_kb(),
        )
        await state.set_state(FashinFlow.confirming_analysis)
    else:
        await state.update_data(outfit_style=None, outfit_style_name=None)
        from handlers.model_select import show_models_page
        await show_models_page(callback.message, state)


@router.message(FashinFlow.waiting_custom_prompt, F.text)
async def receive_custom_prompt(message: types.Message, state: FSMContext):
    """Пользователь ввёл свой промт — сохраняем и идём дальше."""
    custom_prompt = message.text.strip()
    await state.update_data(
        custom_prompt=custom_prompt,
        chosen_type_id="custom",
        outfit_style=None,
        outfit_style_name=None,
    )
    await message.answer(
        f"Промт принят ({len(custom_prompt)} символов).\n"
        "Пропускаю выбор стиля, переходим к выбору модели."
    )
    from handlers.model_select import show_models_page
    await show_models_page(message, state)


@router.callback_query(FashinFlow.confirming_analysis, F.data.startswith("group:"))
async def choose_group(callback: types.CallbackQuery, state: FSMContext):
    group = callback.data.split(":", 1)[1]
    await callback.answer()
    await callback.message.edit_text(
        "Выберите тип:",
        reply_markup=type_list_kb(group),
    )


# ==================== Фаза 4: Стайлинг ====================

@router.callback_query(FashinFlow.confirming_analysis, F.data.startswith("style:"))
async def choose_styling(callback: types.CallbackQuery, state: FSMContext):
    value = callback.data.split(":", 1)[1]

    if value == "custom":
        await callback.answer()
        await callback.message.answer(
            "Опишите свой стиль:\n"
            "<i>белые кроссовки, чёрные узкие джинсы, кожаный ремень</i>"
        )
        await state.set_state(FashinFlow.choosing_style)
        return

    idx = int(value)
    data = await state.get_data()
    from models.garment import GarmentAnalysis
    analysis = GarmentAnalysis(**data["analysis"])

    if idx < len(analysis.styling):
        suggestion = analysis.styling[idx]
        await state.update_data(
            outfit_style=suggestion.to_prompt(),
            outfit_style_name=suggestion.style_name,
        )
        await callback.answer(f"Стиль: {suggestion.style_name}")
    else:
        await state.update_data(outfit_style=None, outfit_style_name=None)
        await callback.answer()

    await callback.message.edit_reply_markup(reply_markup=None)

    from handlers.model_select import show_models_page
    await show_models_page(callback.message, state)


@router.message(FashinFlow.choosing_style, F.text)
async def custom_style_text(message: types.Message, state: FSMContext):
    custom = message.text.strip()
    await state.update_data(
        outfit_style=f"Pair with: {custom}",
        outfit_style_name="Свой",
    )
    from handlers.model_select import show_models_page
    await show_models_page(message, state)
