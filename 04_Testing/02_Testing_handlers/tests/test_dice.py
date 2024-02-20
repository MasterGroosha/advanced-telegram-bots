# Часть импортов нужна будет далее,
# когда перейдём непосредственно к тестовой функции
from datetime import datetime

import pytest
from aiogram.dispatcher.event.bases import UNHANDLED
from aiogram.enums import ChatType, DiceEmoji
from aiogram.methods import SendMessage, SendDice
from aiogram.methods.base import TelegramType
from aiogram.types import Update, Chat, User, Message, Dice


def make_incoming_message(chat: Chat) -> Message:
    """
    Генерирует текстовое сообщение с командой /dice от юзера к боту
    :param chat: объект чата, в котором происходит общение
    :return: объект Message с текстовой командой /dice
    """
    return Message(
        message_id=1,
        chat=chat,
        from_user=User(id=chat.id, is_bot=False, first_name="User"),
        date=datetime.now(),
        text="/dice"
    )


def make_dice_outgoing_message(chat: Chat, is_win: bool) -> Message:
    """
    Генерирует исходящее сообщение от бота, содержащее
    кубик (dice) с предопределённым значением
    :param chat: объект чата, в котором происходит общение
    :param is_win: True, если надо сгенерировать "выигрышный" кубик
    :return: объект Message с кубиком (dice)
    """
    value = 1 if is_win else 2
    return Message(
        message_id=1,
        chat=chat,
        from_user=User(id=1, is_bot=True, first_name="Bot"),
        date=datetime.now(),
        dice=Dice(emoji=DiceEmoji.DICE, value=value)
    )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "is_win, expected_message",
    [
        [True, "Успех!"],
        [False, "В другой раз повезёт!"]
    ]
)
async def test_dice(dp, bot, is_win: bool, expected_message: str):
    chat = Chat(id=123456, type=ChatType.PRIVATE)

    # Создание ответного сообщения от Telegram с нужным кубиком
    bot.add_result_for(
        method=SendDice,
        ok=True,
        result=make_dice_outgoing_message(chat=chat, is_win=is_win)
    )

    # Создание подтверждение от Telegram в ответ на отправку ботом
    # текстовой реакции на результат
    bot.add_result_for(
        method=SendMessage,
        ok=True,
        # result, т.е. то, что ответит Telegram на этот вызов, сейчас не интересно
    )

    result = await dp.feed_update(
        bot,
        Update(message=make_incoming_message(chat=chat), update_id=1)
    )
    assert result is not UNHANDLED
    # Проверка, что первым сообщением, которое отправил бот, был дайс
    outgoing_dice_message: TelegramType = bot.get_request()
    assert isinstance(outgoing_dice_message, SendDice)

    # Проверка, что вторым сообщением, которое отправил бот, было текстовое
    # сообщение об успехе
    outgoing_text_message: TelegramType = bot.get_request()
    assert isinstance(outgoing_text_message, SendMessage)
    assert outgoing_text_message.text == expected_message
