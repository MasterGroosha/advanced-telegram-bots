from typing import cast

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as upsert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload

from bot.db.models import User, Game


async def upsert_user(
    session: AsyncSession,
    telegram_id: int,
    first_name: str,
    last_name: str | None = None,
):
    """
    Добавление или обновление пользователя
    в таблице users
    :param session: сессия СУБД
    :param telegram_id: айди пользователя
    :param first_name: имя пользователя
    :param last_name: фамилия пользователя
    """
    stmt = upsert(User).values(
        {
            "telegram_id": telegram_id,
            "first_name": first_name,
            "last_name": last_name,
        }
    )
    stmt = stmt.on_conflict_do_update(
        index_elements=['telegram_id'],
        set_=dict(
            first_name=first_name,
            last_name=last_name,
        ),
    )
    await session.execute(stmt)
    await session.commit()


async def add_score(
    session: AsyncSession,
    telegram_id: int,
    score: int,
):
    """
    Добавление записи об игровой сессии пользователя
    :param session: сессия СУБД
    :param telegram_id: айди пользователя
    :param score: счёт пользователя
    """
    new_game = Game(
        user_id=telegram_id,
        score=score,
    )
    session.add(new_game)
    await session.commit()


async def get_total_score_for_user(
    session: AsyncSession,
    telegram_id: int,
) -> int:
    """
    Возвращает сумму очков для заданного игрока
    :param session: сессия СУБД
    :param telegram_id: айди пользователя в Telegram
    :return: сумма очков пользователя, число
    """
    user = await session.get(
        User, {"telegram_id": telegram_id},
        options=[selectinload(User.games)]
    )
    return sum(item.score for item in user.games)


async def get_last_games(
    session: AsyncSession,
    number_of_games: int,
) -> list[Game]:
    """
    Получение N последних игр всех пользователей
    :param session: сессия СУБД
    :param number_of_games: количество игр
    :return: требуемое количество объектов Game (может быть меньше запрашиваемого)
    """
    stmt = (
        select(Game)
        .order_by(Game.created_at.desc())
        .limit(number_of_games)
        .options(joinedload(Game.user))
    )
    result = await session.execute(stmt)
    games = result.scalars().all()
    games = cast(list[Game], games)
    return games
