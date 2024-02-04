from datetime import datetime
from typing import Sequence

import pytest
from aiogram import Dispatcher
from aiogram.enums import ChatType
from aiogram.methods import SendMessage
from aiogram.types import Message, Update, User, Chat
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.db.models import RegisteredUser, Order
from tests.mocked_aiogram import MockedBot


def make_message(user_id: int, text: str) -> Message:
    user = User(id=user_id, first_name="User", is_bot=False)
    chat = Chat(id=user_id, type=ChatType.PRIVATE)
    return Message(message_id=1, from_user=user, chat=chat, date=datetime.now(), text=text)


@pytest.mark.asyncio
async def test_making_orders(dp: Dispatcher, bot: MockedBot, session: AsyncSession):
    user_id = 123456
    flow_messages = [
        make_message(user_id, "/start"),
        make_message(user_id, "/food"),
        make_message(user_id, "Суши"),
        make_message(user_id, "Большую"),
    ]
    for message in flow_messages:
        bot.add_result_for(SendMessage, ok=True)
        await dp.feed_update(bot, Update(message=message, update_id=1))

    stmt = select(RegisteredUser).where(RegisteredUser.telegram_id == user_id)
    user_response = await session.scalar(stmt)
    assert user_response is not None
    assert user_response.telegram_id == user_id

    order_stmt = select(Order).where(Order.telegram_id == user_id)
    orders: Sequence[Order] = (await session.scalars(order_stmt)).all()
    assert len(orders) == 1
    order = orders[0]
    assert order.order_contents == "большую порцию суши"
