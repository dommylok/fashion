"""Выбор фона: белый vs сцена с текстовым описанием."""
import logging

from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext

from states import FashinFlow
from keyboards.inline import bg_category_kb, bg_scene_kb

logger = logging.getLogger(__name__)
router = Router()


@router.callback_query(FashinFlow.choosing_bg_type, F.data == "bg_type:white")
async def choose_white_bg(callback: types.CallbackQuery, state: FSMContext):
    """Белый фон — сразу к генерации."""
    await state.update_data(bg_mode="white", bg_scene=None)
    await callback.answer("Белый фон выбран")
    await callback.message.edit_reply_markup(reply_markup=None)

    from handlers.generation import run_generation
    await run_generation(callback.message, state)


@router.callback_query(FashinFlow.choosing_bg_type, F.data == "bg_type:scene")
async def choose_scene_bg(callback: types.CallbackQuery, state: FSMContext):
    """Фон со сценой — показать категории."""
    await callback.answer()
    await callback.message.edit_text(
        "Выберите категорию фона:",
        reply_markup=bg_category_kb(),
    )
    await state.set_state(FashinFlow.choosing_bg_category)


@router.callback_query(FashinFlow.choosing_bg_category, F.data.startswith("bg_cat:"))
async def choose_bg_category(callback: types.CallbackQuery, state: FSMContext):
    """Выбрана категория — показать сцены."""
    category = callback.data.split(":", 1)[1]
    await callback.answer()
    await callback.message.edit_text(
        "Выберите сцену:",
        reply_markup=bg_scene_kb(category),
    )
    await state.set_state(FashinFlow.choosing_bg_photo)


@router.callback_query(FashinFlow.choosing_bg_photo, F.data.startswith("bg_scene:"))
async def select_scene(callback: types.CallbackQuery, state: FSMContext):
    """Выбрана конкретная сцена."""
    from keyboards.inline import SCENES
    scene_key = callback.data.split(":", 1)[1]

    scene = SCENES.get(scene_key)
    if not scene:
        await callback.answer("Сцена не найдена")
        return

    await state.update_data(
        bg_mode="scene",
        bg_scene=scene["prompt"],
        bg_scene_name=scene["label"],
    )

    await callback.answer(f"Фон: {scene['label']}")
    await callback.message.edit_reply_markup(reply_markup=None)

    from handlers.generation import run_generation
    await run_generation(callback.message, state)


@router.callback_query(FashinFlow.choosing_bg_photo, F.data == "bg:back_categories")
async def back_to_categories(callback: types.CallbackQuery, state: FSMContext):
    """Назад к категориям."""
    await callback.answer()
    await callback.message.edit_text(
        "Выберите категорию фона:",
        reply_markup=bg_category_kb(),
    )
    await state.set_state(FashinFlow.choosing_bg_category)
