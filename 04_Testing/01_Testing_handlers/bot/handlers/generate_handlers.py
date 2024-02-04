from asyncio import sleep

from aiogram import Router
from aiogram.exceptions import TelegramForbiddenError
from aiogram.filters import Command
from aiogram.types import Message

router = Router()


async def generate_text():
    await sleep(5.0)
    return "<сгенерированный текст>"


@router.message(Command("generate"))
async def cmd_generate(message: Message):
    text = await generate_text()
    try:
        await message.answer(text)
    except TelegramForbiddenError:
        # Тут можно залогировать или что-то ещё
        print("Пользователь заблокировал бота")
        return
