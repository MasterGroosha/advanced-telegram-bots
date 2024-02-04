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
    # В зависимости от raise_exception возвращаем успех или http 403
    bot.add_result_for(
        method=SendMessage,
        ok=(not raise_exception),
        error_code=403 if raise_exception else 200
        # result сейчас не нужен
    )

    # Отправляем сообщение с командой /generate
    update = await dp.feed_update(
        bot,
        Update(message=make_incoming_message(), update_id=1)
    )

    # Убеждаемся, что сообщение обработано
    assert update is not UNHANDLED
    # Получаем отправленное ботом сообщение
    outgoing_message: TelegramType = bot.get_request()
    # Проверяем различные свойства этого сообщения
    assert isinstance(outgoing_message, SendMessage)
    assert outgoing_message.text == "тестовый текст"
