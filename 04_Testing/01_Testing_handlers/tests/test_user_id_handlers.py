# Часть импортов нужна будет далее,
# когда перейдём непосредственно к тестовой функции
from datetime import datetime

import pytest
from aiogram.dispatcher.event.bases import UNHANDLED
from aiogram.enums import ChatType
from aiogram.methods import SendMessage, AnswerCallbackQuery
from aiogram.methods.base import TelegramType
from aiogram.types import (
    Update, Chat, User, Message, CallbackQuery,
    InlineKeyboardMarkup, InlineKeyboardButton
)

# Константы для этого набора тестов
user_id = 123456
callback_data = "myid"


def make_incoming_message() -> Message:
    """
    Генерирует текстовое сообщение с командой /id от юзера к боту
    :return: объект Message с текстовой командой /id
    """
    return Message(
        message_id=1,
        chat=Chat(id=user_id, type=ChatType.PRIVATE),
        from_user=User(id=user_id, is_bot=False, first_name="User"),
        date=datetime.now(),
        text="/id"
    )


def make_incoming_callback() -> CallbackQuery:
    """
    Генерирует объект CallbackQuery,
    имитирующий результат нажатия юзером кнопки
    с callback_data "myid"
    :return: объект CallbackQuery
    """
    return CallbackQuery(
        id="1111111111111",
        chat_instance="22222222222222",
        from_user=User(id=user_id, is_bot=False, first_name="User"),
        data=callback_data,
        # message необязателен в этом тесте, пропускаем
    )


@pytest.mark.asyncio
async def test_id_command(dp, bot):
    # Создаём ответное сообщение от Telegram в ответ на команду /id
    bot.add_result_for(
        method=SendMessage,
        ok=True,
        # result сейчас не нужен
    )

    # Отправляем сообщение с командой /id
    update = await dp.feed_update(
        bot,
        Update(message=make_incoming_message(), update_id=1)
    )

    # Убеждаемся, что сообщение обработано
    assert update is not UNHANDLED

    # Получаем отправленное ботом сообщение
    outgoing_message: TelegramType = bot.get_request()
    # Проверяем содержимое: тип, текст, наличие клавиатуры, содержимое клавиатуры
    assert isinstance(outgoing_message, SendMessage)
    assert outgoing_message.text == "Нажмите на кнопку ниже:"
    assert outgoing_message.reply_markup is not None
    markup = outgoing_message.reply_markup
    assert isinstance(markup, InlineKeyboardMarkup)
    button: InlineKeyboardButton = markup.inline_keyboard[0][0]
    assert button.text == "Узнать свой ID"
    assert button.callback_data == "myid"


@pytest.mark.asyncio
async def test_myid_callback(dp, bot):
    # Создаём ответное сообщение от Telegram при ответе на колбэк
    bot.add_result_for(
        method=AnswerCallbackQuery,
        ok=True
    )

    # Отправляем коллбэк с data = myid
    update = await dp.feed_update(
        bot,
        Update(callback_query=make_incoming_callback(), update_id=1)
    )

    # Убеждаемся, что коллбэк обработан
    assert update is not UNHANDLED

    # Получаем отправленный ботом коллбэк
    outgoing_callback: TelegramType = bot.get_request()

    # Проверяем содержимое: тип, текст, вид алерта
    assert isinstance(outgoing_callback, AnswerCallbackQuery)
    assert outgoing_callback.text == f"Ваш айди: {user_id}"
    assert outgoing_callback.show_alert in (None, False)

