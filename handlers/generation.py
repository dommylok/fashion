"""Основной пайплайн генерации."""
import logging
import time

from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from aiogram.types import BufferedInputFile

from states import FashinFlow
from services import grok_imagine
from services.image_utils import make_two_panel
from keyboards.inline import post_result_kb
from config import PRICE_IMAGINE, USD_TO_RUB
from catalog import GARMENT_TYPES

logger = logging.getLogger(__name__)
router = Router()


async def run_generation(message: types.Message, state: FSMContext):
    await state.set_state(FashinFlow.generating)
    data = await state.get_data()

    # Ждём фоновую задачу rembg (почти всегда уже готова)
    from handlers.garment import get_clean_garment
    raw = data["raw_garment"]
    garment_bytes = await get_clean_garment(message.chat.id, raw)

    # Debug: показать clean garment (после rembg)
    await message.answer_photo(
        photo=BufferedInputFile(garment_bytes, filename="rembg.jpg"),
        caption="Одежда без фона (debug)",
    )

    model_bytes = data["selected_model_bytes"]
    bg_mode = data.get("bg_mode", "white")
    bg_scene = data.get("bg_scene")
    outfit_style = data.get("outfit_style")
    analysis_cost = data.get("analysis_cost", 0.0)
    items_chosen = data.get("items_chosen", [])
    custom_prompt = data.get("custom_prompt")
    # Тип фото одежды (hanger / person / mannequin / flat_lay)
    photo_type = "hanger"
    analysis_data = data.get("analysis")
    if analysis_data:
        photo_type = analysis_data.get("photo_type", "hanger")

    # Инфо для статуса
    if custom_prompt:
        items_desc = "✍️ Свой промт"
    else:
        names = []
        for item in items_chosen:
            tid = item.get("type_id")
            t = GARMENT_TYPES.get(tid, {})
            names.append(t.get("name_ru", tid))
        items_desc = " + ".join(names)

    style_name = data.get("outfit_style_name", "")
    scene_name = data.get("bg_scene_name", "")

    parts = [f"Генерация: {items_desc}"]
    if style_name:
        parts.append(f"стиль: {style_name}")
    if scene_name:
        parts.append(f"фон: {scene_name}")
    status = await message.answer(", ".join(parts) + "...")

    t0 = time.time()

    try:
        result_bytes, usage = await grok_imagine.tryon(
            garment_bytes, model_bytes,
            items_chosen=items_chosen,
            scene=bg_scene if bg_mode == "scene" else None,
            outfit_style=outfit_style,
            photo_type=photo_type,
            custom_prompt=custom_prompt,
        )
        gen_cost = PRICE_IMAGINE

        await state.update_data(
            last_result=result_bytes,
            tryon_result=result_bytes,
            garment_desc=items_desc,
        )

        two_panel = make_two_panel(result_bytes)

        elapsed = time.time() - t0
        total_cost = analysis_cost + gen_cost
        cost_rub = total_cost * USD_TO_RUB

        await message.answer_photo(
            photo=BufferedInputFile(two_panel, filename="result.jpg"),
            caption=(
                f"Готово за {elapsed:.1f}с\n"
                f"Вещи: {items_desc}\n"
                f"Анализ: ${analysis_cost:.4f} | Генерация: ${gen_cost:.2f}\n"
                f"Итого: ${total_cost:.4f} (~{cost_rub:.1f} руб)"
            ),
            reply_markup=post_result_kb(),
        )
        await status.delete()

    except Exception as e:
        logger.error("Ошибка генерации: %r", e)
        err_msg = str(e)[:200].replace("<", "&lt;").replace(">", "&gt;")
        await status.edit_text(f"Ошибка: {err_msg}")

    await state.set_state(FashinFlow.post_result)
