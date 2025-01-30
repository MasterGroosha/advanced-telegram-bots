import pytest

from aiogram import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

import logs
from bot.handling.schema import assemble
from bot.tests.mocked_aiogram import MockedBot, MockedSession
from config import Config, parse_config


async def get_dp():
    return Dispatcher(storage=MemoryStorage())


@pytest.fixture(scope="session")
async def dp() -> Dispatcher:
    dispatcher = await assemble(dispatcher_factory=get_dp())
    return dispatcher


@pytest.fixture(scope="session")
def bot() -> MockedBot:
    bot = MockedBot()
    bot.session = MockedSession()
    return bot
