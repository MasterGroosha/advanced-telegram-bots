from datetime import datetime

import pytest
from aiogram import Dispatcher
from aiogram.enums import ChatType
from aiogram.fsm.context import StorageKey, FSMContext
from aiogram.methods import SendMessage
from aiogram.methods.base import TelegramType
from aiogram.types import Message, Update, User, Chat

from bot.states import CalculatorStates
from tests.mocked_aiogram import MockedBot

user_id = 123456


def make_message(text: str) -> Message:
    user = User(id=user_id, first_name="User", is_bot=False)
    chat = Chat(id=user_id, type=ChatType.PRIVATE)
    return Message(
        message_id=1,
        from_user=user,
        chat=chat,
        date=datetime.now(),
        text=text
    )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "num1, num2, operation, expected_text",
    [
        [1, 1, "+", "Ответ: 2"],
        [6, 2, "-", "Ответ: 4"],
        [7, 8, "*", "Ответ: 56"],
        [8, 0, "/", "На ноль делить нельзя!"],
        [8, 9, "/", "Ответ: 0.89"],
    ]
)
async def test_calc(
        dp: Dispatcher,
        bot: MockedBot,
        num1: int,
        num2: int,
        operation: str,
        expected_text: str
):
    # Подготавливаем нужный стейт и данные с ним
    fsm_context: FSMContext = dp.fsm.get_context(bot=bot, user_id=user_id, chat_id=user_id)
    await fsm_context.set_state(CalculatorStates.choosing_operation)
    await fsm_context.set_data({"num1": num1, "num2": num2})

    # Альтернативный вариант
    # fsm_storage_key = StorageKey(bot_id=bot.id, user_id=user_id, chat_id=user_id)
    # await dp.storage.set_data(fsm_storage_key, {"num1": num1, "num2": num2})
    # await dp.storage.set_state(fsm_storage_key, CalculatorState.choosing_operation)

    bot.add_result_for(SendMessage, ok=True)
    await dp.feed_update(
        bot,
        Update(
            message=make_message(operation),
            update_id=1
        )
    )

    # Получаем отправленное ботом сообщение
    outgoing_message: TelegramType = bot.get_request()
    assert isinstance(outgoing_message, SendMessage)
    assert outgoing_message.text == expected_text
    assert outgoing_message.reply_markup is not None
    assert outgoing_message.reply_markup.remove_keyboard is True
