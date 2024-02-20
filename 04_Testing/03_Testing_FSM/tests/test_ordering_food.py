from datetime import datetime

import pytest
from aiogram import Dispatcher
from aiogram.enums import ChatType
from aiogram.fsm.context import FSMContext
from aiogram.methods import SendMessage
from aiogram.methods.base import TelegramType
from aiogram.types import Message, Update, User, Chat

from bot.states import OrderFoodStates
from tests.mocked_aiogram import MockedBot

user_id = 123456


def make_message(text: str) -> Message:
    user = User(id=user_id, first_name="User", is_bot=False)
    chat = Chat(id=user_id, type=ChatType.PRIVATE)
    return Message(message_id=1, from_user=user, chat=chat, date=datetime.now(), text=text)


@pytest.mark.asyncio
async def test_states_flow_orders(dp: Dispatcher, bot: MockedBot):

    # Получение контекста FSM для текущего юзера
    fsm_context: FSMContext = dp.fsm.get_context(bot=bot, user_id=user_id, chat_id=user_id)
    await fsm_context.set_state(None)

    # Альтернативный вариант
    # fsm_storage_key = StorageKey(bot_id=bot.id, user_id=user_id, chat_id=user_id)
    # # Очистка стейта
    # await dp.storage.set_state(fsm_storage_key, None)

    starting_messages = [
        make_message("/start"),
        make_message("/food")
    ]

    for message in starting_messages:
        bot.add_result_for(SendMessage, ok=True)
        await dp.feed_update(bot, Update(message=message, update_id=1))
        # Здесь и далее таким вызовом забирается
        # очередное сообщение бота из списка отправленных
        # Но пока что его содержимое не интересует
        bot.get_request()

    # Проверка стейта "выбор блюда"
    current_state = await fsm_context.get_state()
    # Альтернативный вариант
    # current_state = await dp.storage.get_state(fsm_storage_key)
    assert current_state == OrderFoodStates.choosing_food_name

    # Отправка некорректного значения названия блюда
    bot.add_result_for(SendMessage, ok=True)
    await dp.feed_update(bot, Update(message=make_message("ХЗ ЧТО"), update_id=1))
    bot.get_request()

    # Проверка, что стейт не изменился
    current_state = await fsm_context.get_state()
    assert current_state == OrderFoodStates.choosing_food_name

    # Отправка корректного значения названия блюда
    bot.add_result_for(SendMessage, ok=True)
    await dp.feed_update(bot, Update(message=make_message("Суши"), update_id=1))
    bot.get_request()

    # Проверка, что стейт изменился на "выбор размера"
    current_state = await fsm_context.get_state()
    assert current_state == OrderFoodStates.choosing_food_size

    # Отправка некорректного значения размера блюда
    bot.add_result_for(SendMessage, ok=True)
    await dp.feed_update(bot, Update(message=make_message("ХЗ ЧТО"), update_id=1))
    bot.get_request()

    # Проверка, что стейт не изменился
    current_state = await fsm_context.get_state()
    assert current_state == OrderFoodStates.choosing_food_size

    # Отправка корректного значения размера блюда
    bot.add_result_for(SendMessage, ok=True)
    await dp.feed_update(bot, Update(message=make_message("Большую"), update_id=1))

    # Получение отправленного ботом сообщения
    outgoing_message: TelegramType = bot.get_request()
    # Проверка, что бот написал "заказ" правильно
    assert isinstance(outgoing_message, SendMessage)
    assert outgoing_message.text == "Вы выбрали большую порцию суши.\nСпасибо за заказ! Чтобы сделать ещё один, снова нажмите на /food."

    # Проверка, что стейт сбросился
    current_state = await fsm_context.get_state()
    assert current_state is None
