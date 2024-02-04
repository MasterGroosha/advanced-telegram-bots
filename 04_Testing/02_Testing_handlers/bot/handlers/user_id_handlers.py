from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters import Command


router = Router()


@router.message(Command("id"))
async def cmd_id(message: Message):
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(
            text="Узнать свой ID",
            callback_data="myid"
        )
    )
    await message.answer(
        "Нажмите на кнопку ниже:",
        reply_markup=builder.as_markup()
    )


@router.callback_query(F.data == "myid")
async def get_my_id(callback: CallbackQuery):
    await callback.answer(
        text=f"Ваш айди: {callback.from_user.id}"
    )
