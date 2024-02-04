from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.db.models import RegisteredUser, Order


async def get_user_by_id(session: AsyncSession, user_id: int) -> RegisteredUser | None:
    """
    Получает пользователя по его айди.
    :param session: объект AsyncSession
    :param user_id: айди пользователя
    :return: объект RegisteredUser или None
    """
    stmt = select(RegisteredUser).where(RegisteredUser.telegram_id == user_id)
    return await session.scalar(stmt)


async def ensure_user(session: AsyncSession, user_id: int) -> None:
    """
    Создаёт пользователя, если его раньше не было
    :param session: объект AsyncSession
    :param user_id: айди пользователя
    """
    existing_user = await get_user_by_id(session, user_id)
    if existing_user is not None:
        return
    user = RegisteredUser(telegram_id=user_id)
    session.add(user)
    await session.commit()


async def create_order(session: AsyncSession, fsm_data: dict, user_id: int) -> None:
    """
    Создаёт заказ в СУБД с привязкой к пользователю
    :param session: объект AsyncSession
    :param fsm_data: данные из FSM с информацией о заказе
    :param user_id: айди пользователя
    """

    def get_order_text(data: dict):
        return f"{data['chosen_size']} порцию {data['chosen_food']}"

    await ensure_user(session, user_id)
    order = Order(
        telegram_id=user_id,
        order_contents=get_order_text(fsm_data)
    )
    session.add(order)
    await session.commit()


async def test_connection(session: AsyncSession):
    """
    Проверка соединения с СУБД
    :param session: объект AsyncSession
    """
    stmt = select(1)
    return await session.scalar(stmt)
