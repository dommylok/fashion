"""Выбор модели — показать 10 случайных, пользователь выбирает."""
import logging

from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.types import InputMediaPhoto, FSInputFile

from states import FashinFlow
from services.model_picker import pick_random_models
from keyboards.inline import model_select_kb

logger = logging.getLogger(__name__)
router = Router()

MODELS_PER_PAGE = 10


async def show_models_page(message: types.Message, state: FSMContext):
    """Показать страницу из 10 случайных моделей."""
    data = await state.get_data()
    shown = data.get("shown_models", set())

    models = pick_random_models(count=MODELS_PER_PAGE, exclude=shown)
    if not models:
        await message.answer("Больше нет доступных моделей.")
        return

    model_names = [m.name for m in models]

    shown = shown | set(model_names)
    await state.update_data(shown_models=shown, current_page_models=model_names)

    media = []
    for i, model_path in enumerate(models):
        media.append(InputMediaPhoto(
            media=FSInputFile(model_path),
            caption=f"<b>{i + 1}</b>" if i == 0 else str(i + 1),
        ))

    await message.answer_media_group(media=media)
    await message.answer(
        "Выберите модель по номеру:",
        reply_markup=model_select_kb(model_names),
    )
    await state.set_state(FashinFlow.browsing_models)


@router.callback_query(FashinFlow.browsing_models, F.data.startswith("model:"))
async def select_model(callback: types.CallbackQuery, state: FSMContext):
    """Пользователь выбрал модель или хочет ещё."""
    value = callback.data.split(":", 1)[1]

    if value == "more":
        await callback.answer("Загружаю ещё...")
        await show_models_page(callback.message, state)
        return

    from services.model_picker import get_model_by_name
    model_path = get_model_by_name(value)
    if not model_path:
        await callback.answer("Модель не найдена, выберите другую.")
        return

    model_bytes = model_path.read_bytes()
    await state.update_data(
        selected_model_bytes=model_bytes,
        selected_model_name=value,
    )

    await callback.answer(f"Модель выбрана!")
    await callback.message.edit_reply_markup(reply_markup=None)

    from keyboards.inline import bg_type_kb
    await callback.message.answer(
        "Выберите тип фона:",
        reply_markup=bg_type_kb(),
    )
    await state.set_state(FashinFlow.choosing_bg_type)
