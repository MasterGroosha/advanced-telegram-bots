from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from fluentogram import TranslatorRunner
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import User

get_user_router = Router()


@get_user_router.message(Command("get_info"))
async def get_user_handler(msg: Message, i18n: TranslatorRunner, db: AsyncSession):
    user = await db.get(User, msg.from_user.id)
    await msg.answer(i18n.db_get_user(user=user))
