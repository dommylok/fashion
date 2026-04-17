"""Основной пайплайн генерации."""
import logging
import time

from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from aiogram.types import BufferedInputFile

from states import FashinFlow
from services import grok_imagine
from services.image_utils import stack_images_vertical, make_two_panel
from keyboards.inline import post_result_kb
from config import PRICE_IMAGINE, USD_TO_RUB
from catalog import GARMENT_TYPES, build_ai_name

logger = logging.getLogger(__name__)
router = Router()


def _build_combined_garment(garment_photos: list[bytes]) -> bytes:
    if len(garment_photos) == 1:
        return garment_photos[0]
    return stack_images_vertical(garment_photos)


async def run_generation(message: types.Message, state: FSMContext):
    await state.set_state(FashinFlow.generating)
    data = await state.get_data()

    garment_photos = data["garment_photos"]
    model_bytes = data["selected_model_bytes"]
    bg_mode = data.get("bg_mode", "white")
    bg_scene = data.get("bg_scene")
    outfit_style = data.get("outfit_style")
    analysis_cost = data.get("analysis_cost", 0.0)
    type_id = data.get("chosen_type_id", "jacket")
    length_id = data.get("chosen_length")
    fit_id = data.get("chosen_fit")
    custom_prompt = data.get("custom_prompt")

    garment_bytes = _build_combined_garment(garment_photos)

    # Инфо для статуса
    if custom_prompt:
        type_name = "✍️ Свой промт"
        ai_name = f"custom ({len(custom_prompt)} chars)"
    else:
        t = GARMENT_TYPES.get(type_id, {})
        type_name = t.get("name_ru", type_id)
        ai_name = build_ai_name(type_id)
    style_name = data.get("outfit_style_name", "")
    scene_name = data.get("bg_scene_name", "")

    parts = [f"Генерация: {type_name}"]
    if not custom_prompt:
        parts[0] += f" ({ai_name})"
    if style_name:
        parts.append(f"стиль: {style_name}")
    if scene_name:
        parts.append(f"фон: {scene_name}")
    status = await message.answer(", ".join(parts) + "...")

    t0 = time.time()

    try:
        result_bytes, usage = await grok_imagine.tryon(
            garment_bytes, model_bytes, type_id,
            length_id=length_id, fit_id=fit_id,
            scene=bg_scene if bg_mode == "scene" else None,
            outfit_style=outfit_style,
            custom_prompt=custom_prompt,
        )
        gen_cost = PRICE_IMAGINE

        # Сохраняем full-body результат
        await state.update_data(
            last_result=result_bytes,
            tryon_result=result_bytes,
            garment_desc=ai_name,
            combined_garment=garment_bytes,
        )

        # Делаем 2-панельную картинку
        two_panel = make_two_panel(result_bytes)

        elapsed = time.time() - t0
        total_cost = analysis_cost + gen_cost
        cost_rub = total_cost * USD_TO_RUB

        await message.answer_photo(
            photo=BufferedInputFile(two_panel, filename="result.jpg"),
            caption=(
                f"Готово за {elapsed:.1f}с\n"
                f"Тип: {type_name} → {ai_name}\n"
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
