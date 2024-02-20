from datetime import datetime

import pytest
from aiogram.dispatcher.event.bases import UNHANDLED
from aiogram.enums import ChatType
from aiogram.methods import SendPhoto
from aiogram.methods.base import TelegramType
from aiogram.types import Update, Chat, User, Message, FSInputFile


def predefined_random():
    return 1


def make_incoming_message() -> Message:
    """
    Генерирует текстовое сообщение с командой /capybara от юзера к боту
    :return: объект Message с текстовой командой /capybara
    """
    return Message(
        message_id=1,
        chat=Chat(id=123456, type=ChatType.PRIVATE),
        from_user=User(id=123456, is_bot=False, first_name="User"),
        date=datetime.now(),
        text="/capybara"
    )


@pytest.mark.asyncio
async def test_capybara_cmd(dp, bot, monkeypatch):
    monkeypatch.setattr(
        "bot.handlers.capybara_handlers.choose_random_image",
        predefined_random
    )

    bot.add_result_for(
        method=SendPhoto,
        ok=True,
        # result сейчас не нужен
    )

    # Отправка сообщения с командой /capybara
    update = await dp.feed_update(
        bot,
        Update(message=make_incoming_message(), update_id=1)
    )

    # Проверка, что сообщение обработано
    assert update is not UNHANDLED

    # Получение отправленного ботом сообщения
    outgoing_message: TelegramType = bot.get_request()
    # Проверка различных свойств этого сообщения
    assert isinstance(outgoing_message, SendPhoto)
    assert outgoing_message.caption == "Случайная капибара"
    assert isinstance(outgoing_message.photo, FSInputFile)
    assert outgoing_message.photo.path == '/opt/images/capybara_1.jpg'
