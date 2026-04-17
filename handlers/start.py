"""Команда /start и главное меню."""
from aiogram import Router, types
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext

from states import FashinFlow

router = Router()


@router.message(CommandStart())
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Добро пожаловать в <b>Fashin Bot</b>\n\n"
        "Отправьте мне 1-4 фото одежды, и я помогу создать "
        "виртуальную примерку на реальной модели.\n\n"
        "Просто отправьте фото одежды сейчас (как фото или файл)."
    )
    await state.set_state(FashinFlow.waiting_garments)
    await state.update_data(garment_photos=[], garment_analyses=[])
