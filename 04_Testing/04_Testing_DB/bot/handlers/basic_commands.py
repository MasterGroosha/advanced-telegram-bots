from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.db.requests import ensure_user

router = Router(name="Basic Commands Router")


@router.message(CommandStart())
async def cmd_start(message: Message, session: AsyncSession):
    await ensure_user(session, message.from_user.id)
    await message.answer("Привет! Нажмите /food для заказа еды.")
