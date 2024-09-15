from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

router = Router(name="commands router")


@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer("Hello")
