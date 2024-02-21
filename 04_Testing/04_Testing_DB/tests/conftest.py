from pathlib import Path

import pytest
import pytest_asyncio
from aiogram import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from alembic.command import upgrade, downgrade
from alembic.config import Config as AlembicConfig
from bot.config_reader import parse_settings, Settings
from bot.handlers import get_routers
from bot.middlewares import DbSessionMiddleware
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from tests.mocked_aiogram import MockedBot, MockedSession


# Фикстура для получения экземпляра фейкового бота
@pytest.fixture(scope="session")
def bot() -> MockedBot:
    bot = MockedBot()
    bot.session = MockedSession()
    return bot


# Фикстура, которая получает объект настроек
@pytest.fixture(scope="session")
def settings() -> Settings:
    return parse_settings()


# Фикстура, которая создаёт объект конфигурации alembic для применения миграций
@pytest.fixture(scope="session")
def alembic_config(settings: Settings) -> AlembicConfig:
    project_dir = Path(__file__).parent.parent
    alembic_ini_path = Path.joinpath(project_dir.absolute(), "alembic.ini").as_posix()
    alembic_cfg = AlembicConfig(alembic_ini_path)

    migrations_dir_path = Path.joinpath(project_dir.absolute(), "bot", "db", "migrations").as_posix()
    alembic_cfg.set_main_option("script_location", migrations_dir_path)
    alembic_cfg.set_main_option("sqlalchemy.url", str(settings.db_url))
    return alembic_cfg


# Фикстура для получения асинхронного "движка" для работы с СУБД
@pytest.fixture(scope="session")
def engine(settings):
    engine = create_async_engine(str(settings.db_url))
    yield engine
    engine.sync_engine.dispose()


# Обновлённая фикстура для получения экземпляра диспетчера aiogram
# Здесь же надо ещё раз подключить все нужные мидлвари
@pytest.fixture(scope="session")
def dp(engine) -> Dispatcher:
    dispatcher = Dispatcher(storage=MemoryStorage())
    sessionmaker = async_sessionmaker(engine, expire_on_commit=False)
    dispatcher.update.middleware(DbSessionMiddleware(session_pool=sessionmaker))
    dispatcher.include_routers(*get_routers())
    return dispatcher


# Фикстура, которая в каждом модуле применяет миграции
# А после завершения тестов в модуле откатывает базу к нулевому состоянию (без данных)
@pytest_asyncio.fixture(scope="module")
def create(engine, alembic_config: AlembicConfig):
    upgrade(alembic_config, "head")
    yield engine
    downgrade(alembic_config, "base")


# Фикстура, которая передаёт в тест сессию из "движка"
@pytest_asyncio.fixture(scope="function")
async def session(engine, create):
    async with AsyncSession(engine) as s:
        yield s
