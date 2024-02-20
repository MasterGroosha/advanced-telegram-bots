from datetime import datetime

import pytest
from aiogram.dispatcher.event.bases import UNHANDLED
from aiogram.enums import ChatType
from aiogram.methods import SendMessage
from aiogram.methods.base import TelegramType
from aiogram.types import Update, Chat, User, Message

user_id = 123456


def make_incoming_message() -> Message:
    """
    Генерирует текстовое сообщение с командой /generate от юзера к боту
    :return: объект Message с текстовой командой /generate
    """
    return Message(
        message_id=1,
        chat=Chat(id=user_id, type=ChatType.PRIVATE),
        from_user=User(id=user_id, is_bot=False, first_name="User"),
        date=datetime.now(),
        text="/generate"
    )


async def override_generate_text():
    return "тестовый текст"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ["raise_exception"],
    [
        [False],
        [True]
    ]
)
async def test_cmd_generate(dp, bot, monkeypatch, raise_exception):
    monkeypatch.setattr(
        "bot.handlers.generate_handlers.generate_text",
        override_generate_text
    )
    # В зависимости от raise_exception возвращается успех (http 200) или неуспех (http 403)
    bot.add_result_for(
        method=SendMessage,
        ok=(not raise_exception),
        error_code=403 if raise_exception else 200
        # result сейчас не нужен
    )

    # Отправка сообщения с командой /generate
    update = await dp.feed_update(
        bot,
        Update(message=make_incoming_message(), update_id=1)
    )

    # Проверка, что сообщение обработано
    assert update is not UNHANDLED
    # Получение отправленного ботом сообщения
    outgoing_message: TelegramType = bot.get_request()
    # Проверка различных свойств этого сообщения
    assert isinstance(outgoing_message, SendMessage)
    assert outgoing_message.text == "тестовый текст"
