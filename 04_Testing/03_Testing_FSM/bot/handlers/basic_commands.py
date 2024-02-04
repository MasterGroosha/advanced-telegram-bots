from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

router = Router(name="Basic Commands Router")


@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer("Привет! Нажмите /food для заказа еды или /calc для перехода к калькулятору.")
