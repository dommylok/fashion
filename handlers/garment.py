"""Загрузка фото → параллельно анализ+rembg → уточнение каждой вещи."""
import asyncio
import logging

from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.types import BufferedInputFile

from states import FashinFlow
from services.analyzer import analyze_garment
from services.image_utils import remove_bg_local, preprocess_garment
from keyboards.inline import (
    type_suggestions_kb, type_groups_kb, type_list_kb,
    styling_kb, length_kb, fit_kb,
)

logger = logging.getLogger(__name__)
router = Router()


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


def _rembg_sync(raw: bytes) -> bytes:
    """Синхронная обёртка для rembg + preprocess."""
    png = remove_bg_local(raw)
    return preprocess_garment(png)


# Глобальный dict фоновых задач rembg по user_id
_rembg_tasks: dict[int, asyncio.Task] = {}


async def get_clean_garment(user_id: int, fallback: bytes) -> bytes:
    """Получить clean (без фона) garment. Ждём задачу если ещё не готова.
    Если упала — возвращаем оригинал."""
    task = _rembg_tasks.pop(user_id, None)
    if task is None:
        return fallback
    try:
        return await task
    except Exception as e:
        logger.warning("rembg failed for user %d: %r", user_id, e)
        return fallback


# ==================== Фаза 1: Загрузка фото ====================

@router.message(FashinFlow.waiting_garments, F.photo | F.document)
async def receive_garment_photo(message: types.Message, state: FSMContext):
    """Получили фото → параллельно rembg + analyze → сразу показываем результат."""
    status_msg = await message.answer("Анализирую одежду...")

    raw = await _get_photo_bytes(message)
    if not raw:
        await status_msg.edit_text("Отправьте фото или файл изображения.")
        return

    user_id = message.from_user.id

    # rembg запускаем В ФОНЕ — не ждём его, пользователь идёт дальше
    rembg_task = asyncio.create_task(asyncio.to_thread(_rembg_sync, raw))
    _rembg_tasks[user_id] = rembg_task

    # Анализ — ждём (он быстрее rembg)
    try:
        analysis, cost = await analyze_garment(raw)
    except Exception as e:
        logger.error("Ошибка анализа: %r", e)
        await status_msg.edit_text(f"Ошибка: {e}")
        _rembg_tasks.pop(user_id, None)
        return

    # Сохраняем raw на случай если rembg упадёт
    await state.update_data(
        raw_garment=raw,
        analysis=analysis.model_dump(),
        analysis_cost=cost,
        items_chosen=[],
        current_item_idx=0,
    )

    await status_msg.delete()

    # Показываем сводку + сразу начинаем уточнения (rembg продолжает в фоне)
    await message.answer(
        f"{analysis.items_summary()}\n\nСтоимость анализа: ${cost:.4f}"
    )
    await _ask_type_for_current_item(message, state)


# ==================== Фаза 2: Уточнения по каждой вещи ====================

async def _ask_type_for_current_item(message: types.Message, state: FSMContext):
    """Показать варианты типа для текущей вещи."""
    data = await state.get_data()
    from models.garment import GarmentAnalysis
    analysis = GarmentAnalysis(**data["analysis"])

    idx = data.get("current_item_idx", 0)
    if idx >= len(analysis.items):
        # Все вещи уточнены — переходим к стайлингу
        await _show_styling(message, state)
        return

    item = analysis.items[idx]
    pos_ru = {"top": "верх", "bottom": "низ", "dress": "платье", "full": "образ"}
    pos_label = pos_ru.get(item.position, f"вещь {idx + 1}")

    header = ""
    if len(analysis.items) > 1:
        header = f"<b>Вещь {idx + 1}/{len(analysis.items)} — {pos_label}</b>\n\n"

    await message.answer(
        f"{header}Что на фото?",
        reply_markup=type_suggestions_kb(
            [s.model_dump() for s in item.suggestions]
        ),
    )
    await state.set_state(FashinFlow.confirming_analysis)


async def _show_styling(message: types.Message, state: FSMContext):
    """Все вещи уточнены → показываем стайлинг."""
    data = await state.get_data()
    from models.garment import GarmentAnalysis
    analysis = GarmentAnalysis(**data["analysis"])

    if analysis.styling:
        await message.answer(
            analysis.styling_card_text(),
            reply_markup=styling_kb(),
        )
        await state.set_state(FashinFlow.confirming_analysis)
    else:
        await state.update_data(outfit_style=None, outfit_style_name=None)
        from handlers.model_select import show_models_page
        await show_models_page(message, state)


@router.callback_query(FashinFlow.confirming_analysis, F.data.startswith("type:"))
async def choose_type(callback: types.CallbackQuery, state: FSMContext):
    type_id = callback.data.split(":", 1)[1]

    if type_id == "other":
        await callback.answer()
        await callback.message.edit_text(
            "Выберите категорию:",
            reply_markup=type_groups_kb(),
        )
        return

    if type_id == "custom_prompt":
        await callback.answer()
        await callback.message.answer(
            "✍️ <b>Режим ручного промта</b>\n\n"
            "Напишите промт как есть — он уйдёт в генерацию без модификаций.\n\n"
            "<i>Image 1 = фото одежды, Image 2 = модель</i>"
        )
        await state.set_state(FashinFlow.waiting_custom_prompt)
        return

    # Тип выбран — сохраняем выбор для текущей вещи
    from catalog import GARMENT_TYPES
    t = GARMENT_TYPES.get(type_id)
    if not t:
        await callback.answer("Тип не найден")
        return

    # Сохраняем текущий выбор типа во временное поле
    category = t.get("category", "upper_body")
    await state.update_data(current_type_id=type_id, current_category=category)
    await callback.answer(f"Выбрано: {t['name_ru']}")
    await callback.message.edit_reply_markup(reply_markup=None)

    # Спрашиваем длину для текущей вещи — клавиатура по категории
    await callback.message.answer(
        f"<b>{t['name_ru']}</b>\n\nВыберите длину (или '⏭ По фото'):",
        reply_markup=length_kb(category),
    )
    await state.set_state(FashinFlow.choosing_length)


@router.callback_query(FashinFlow.confirming_analysis, F.data.startswith("group:"))
async def choose_group(callback: types.CallbackQuery, state: FSMContext):
    group = callback.data.split(":", 1)[1]
    await callback.answer()
    await callback.message.edit_text(
        "Выберите тип:",
        reply_markup=type_list_kb(group),
    )


@router.callback_query(FashinFlow.choosing_length, F.data.startswith("length:"))
async def choose_length(callback: types.CallbackQuery, state: FSMContext):
    length_id = callback.data.split(":", 1)[1]
    data = await state.get_data()
    category = data.get("current_category", "upper_body")

    if length_id == "auto":
        length_id = None
        await callback.answer("Длина: по фото")
    else:
        from catalog import get_lengths_for_category
        lengths = get_lengths_for_category(category)
        l = lengths.get(length_id)
        await callback.answer(f"Длина: {l['label_ru']}" if l else length_id)

    await state.update_data(current_length_id=length_id)
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(
        "Выберите посадку (или '⏭ По фото'):",
        reply_markup=fit_kb(category),
    )
    await state.set_state(FashinFlow.choosing_fit)


@router.callback_query(FashinFlow.choosing_fit, F.data.startswith("fit:"))
async def choose_fit(callback: types.CallbackQuery, state: FSMContext):
    fit_id = callback.data.split(":", 1)[1]
    data = await state.get_data()
    category = data.get("current_category", "upper_body")

    if fit_id == "auto":
        fit_id = None
        await callback.answer("Посадка: по фото")
    else:
        from catalog import get_fits_for_category
        fits = get_fits_for_category(category)
        f = fits.get(fit_id)
        await callback.answer(f"Посадка: {f['label_ru']}" if f else fit_id)

    # Сохраняем полный выбор для ТЕКУЩЕЙ вещи
    items_chosen = data.get("items_chosen", [])
    items_chosen.append({
        "type_id": data["current_type_id"],
        "length_id": data.get("current_length_id"),
        "fit_id": fit_id,
    })

    # Переходим к следующей вещи или к стайлингу
    next_idx = data.get("current_item_idx", 0) + 1
    await state.update_data(
        items_chosen=items_chosen,
        current_item_idx=next_idx,
        current_type_id=None,
        current_length_id=None,
        current_category=None,
    )

    await callback.message.edit_reply_markup(reply_markup=None)
    await _ask_type_for_current_item(callback.message, state)


# ==================== Фаза 3: Стайлинг ====================

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


# ==================== Свой промт ====================

@router.message(FashinFlow.waiting_custom_prompt, F.text)
async def receive_custom_prompt(message: types.Message, state: FSMContext):
    custom_prompt = message.text.strip()
    await state.update_data(
        custom_prompt=custom_prompt,
        items_chosen=[{"type_id": "custom", "length_id": None, "fit_id": None}],
        outfit_style=None,
        outfit_style_name=None,
    )
    await message.answer(f"Промт принят ({len(custom_prompt)} символов).")
    from handlers.model_select import show_models_page
    await show_models_page(message, state)
