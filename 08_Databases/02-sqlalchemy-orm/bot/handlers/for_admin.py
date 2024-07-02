from aiogram import F, Router
from aiogram.filters import Command, MagicData
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.db.requests import get_last_games

router = Router(name="admin commands router")
# Фильтр: роутер доступен только chat id, равному admin_id,
# который передан в диспетчер
router.message.filter(MagicData(F.event.chat.id == F.admin_id))  # noqa


@router.message(Command("last3"))
async def cmd_last3(
    message: Message,
    session: AsyncSession,
):
    games = await get_last_games(
        session=session,
        number_of_games=3
    )
    result = [
        "Последние 3 игры:\n"
    ]
    for game in games:
        result.append(
            f"{game.user.first_name} набрал(а) {game.score} очк."
        )
    await message.answer("\n".join(result))
