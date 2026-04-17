"""Пост-генерация: спина/бок, позы, видео, смена фона."""
import logging
import random
import time

from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.types import BufferedInputFile

from states import FashinFlow
from services import grok_imagine
from services.image_utils import crop_right_half
from keyboards.inline import post_result_kb, video_style_kb, bg_type_kb
from config import PRICE_IMAGINE, PRICE_VIDEO_720P, USD_TO_RUB

logger = logging.getLogger(__name__)
router = Router()


async def _get_reference(state: FSMContext) -> tuple[bytes, str]:
    """Получить full-body эталон и описание.
    tryon_result уже full-body (одна картинка, не 2-панельная)."""
    data = await state.get_data()
    reference = data["tryon_result"]
    garment_desc = data["garment_desc"]
    return reference, garment_desc


@router.callback_query(FashinFlow.post_result, F.data == "post:edit")
async def start_edit(callback: types.CallbackQuery, state: FSMContext):
    """Пользователь хочет изменить результат."""
    await callback.answer()
    await callback.message.answer(
        "Опишите что изменить, например:\n"
        "• <i>сделай штаны длиннее</i>\n"
        "• <i>смени обувь на белые кроссовки</i>\n"
        "• <i>фон темнее</i>\n"
        "• <i>куртка должна быть короче</i>\n"
        "• <i>добавь сумку</i>\n\n"
        "Можно указать несколько правок сразу."
    )
    await state.set_state(FashinFlow.waiting_edit_text)


@router.callback_query(FashinFlow.post_result, F.data == "post:new_prompt")
async def start_new_prompt(callback: types.CallbackQuery, state: FSMContext):
    """Новый промт для той же одежды+модели+фона — полная перегенерация."""
    await callback.answer()
    await callback.message.answer(
        "✍️ <b>Новый промт</b>\n\n"
        "Напишите новый промт для Grok Imagine.\n"
        "Одежда, модель и фон останутся те же, изменится только промт.\n\n"
        "<i>На входе Grok получит:\n"
        "• Image 1 = исходное фото одежды\n"
        "• Image 2 = выбранная модель</i>"
    )
    await state.set_state(FashinFlow.waiting_new_prompt)


@router.message(FashinFlow.waiting_new_prompt, F.text)
async def apply_new_prompt(message: types.Message, state: FSMContext):
    """Применить новый промт с той же одеждой/моделью."""
    new_prompt = message.text.strip()
    await state.update_data(custom_prompt=new_prompt, chosen_type_id="custom")

    # Запускаем generation с теми же параметрами, но новым промтом
    from handlers.generation import run_generation
    await run_generation(message, state)


@router.message(FashinFlow.waiting_edit_text, F.text)
async def apply_edit(message: types.Message, state: FSMContext):
    """Применить правку к текущему результату."""
    user_request = message.text.strip()
    data = await state.get_data()
    result_bytes = data["last_result"]
    garment_desc = data["garment_desc"]

    status = await message.answer(f"Применяю правку: {user_request}...")

    try:
        t0 = time.time()
        edited, usage = await grok_imagine.edit_image(
            result_bytes, user_request, garment_desc
        )
        elapsed = time.time() - t0
        cost = PRICE_IMAGINE

        # Обновляем last_result чтобы следующие правки шли от нового результата
        await state.update_data(last_result=edited, tryon_result=edited)

        await message.answer_photo(
            photo=BufferedInputFile(edited, filename="edited.jpg"),
            caption=f"Правка применена ({elapsed:.1f}с, ${cost:.2f})",
            reply_markup=post_result_kb(),
        )
        await status.delete()
    except Exception as e:
        logger.error("Ошибка правки: %r", e)
        err_msg = str(e)[:200].replace("<", "&lt;").replace(">", "&gt;")
        await status.edit_text(f"Ошибка: {err_msg}")

    await state.set_state(FashinFlow.post_result)


@router.callback_query(FashinFlow.post_result, F.data == "post:back_side")
async def do_back_side(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer("Генерирую спину + бок...")
    status = await callback.message.answer("Генерация спины + бока...")

    reference, garment_desc = await _get_reference(state)

    try:
        t0 = time.time()
        result, usage = await grok_imagine.generate_back_side(
            reference, garment_desc
        )
        elapsed = time.time() - t0
        cost = PRICE_IMAGINE

        await callback.message.answer_photo(
            photo=BufferedInputFile(result, filename="back_side.jpg"),
            caption=f"Спина + бок ({elapsed:.1f}с, ${cost:.3f})",
            reply_markup=post_result_kb(),
        )
        await status.delete()
    except Exception as e:
        logger.error("Спина/бок ошибка: %r", e)
        await status.edit_text(f"Ошибка: {e}")


@router.callback_query(FashinFlow.post_result, F.data == "post:poses")
async def do_poses(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer("Генерирую позы...")
    status = await callback.message.answer("Генерация поз...")

    reference, garment_desc = await _get_reference(state)

    try:
        t0 = time.time()
        variant = random.randint(0, 2)
        result, usage = await grok_imagine.generate_poses(
            reference, garment_desc, variant=variant
        )
        elapsed = time.time() - t0
        cost = PRICE_IMAGINE

        await callback.message.answer_photo(
            photo=BufferedInputFile(result, filename="poses.jpg"),
            caption=f"Позы вариант {variant + 1} ({elapsed:.1f}с, ${cost:.3f})",
            reply_markup=post_result_kb(),
        )
        await status.delete()
    except Exception as e:
        logger.error("Позы ошибка: %r", e)
        await status.edit_text(f"Ошибка: {e}")


@router.callback_query(FashinFlow.post_result, F.data == "post:video")
async def do_video_choice(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer(
        "Выберите стиль видео:",
        reply_markup=video_style_kb(),
    )


@router.callback_query(FashinFlow.post_result, F.data.startswith("video:"))
async def do_video(callback: types.CallbackQuery, state: FSMContext):
    style = callback.data.split(":", 1)[1]
    with_emotions = style == "emotion"

    await callback.answer("Генерирую видео (~60 сек)...")
    status = await callback.message.answer("Генерация видео поворота...")

    reference, _ = await _get_reference(state)
    person_bytes = reference

    try:
        t0 = time.time()
        video_bytes = await grok_imagine.generate_video(
            person_bytes, with_emotions=with_emotions
        )
        elapsed = time.time() - t0
        cost = PRICE_VIDEO_720P

        await callback.message.answer_video(
            video=BufferedInputFile(video_bytes, filename="rotation.mp4"),
            caption=f"Видео поворот ({elapsed:.1f}с, ${cost:.3f})",
            reply_markup=post_result_kb(),
        )
        await status.delete()
    except Exception as e:
        logger.error("Видео ошибка: %r", e)
        await status.edit_text(f"Ошибка: {e}")


@router.callback_query(FashinFlow.post_result, F.data == "post:change_bg")
async def change_bg(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer(
        "Выберите тип фона:",
        reply_markup=bg_type_kb(),
    )
    await state.set_state(FashinFlow.choosing_bg_type)


@router.callback_query(FashinFlow.post_result, F.data == "post:new")
async def new_garment(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    model_bytes = data.get("selected_model_bytes")
    model_name = data.get("selected_model_name")

    await state.clear()
    if model_bytes:
        await state.update_data(
            selected_model_bytes=model_bytes,
            selected_model_name=model_name,
        )

    await callback.answer("Начинаем заново!")
    await callback.message.answer("Отправьте новые фото одежды (1-4 фото).")
    await state.set_state(FashinFlow.waiting_garments)
    await state.update_data(garment_photos=[], garment_analyses=[])
