import asyncio

from aiogram import Bot, Dispatcher
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from bot.config_reader import get_config, BotConfig, DbConfig
from bot.db.base import Base
from bot.handlers import get_routers
from bot.middlewares import DbSessionMiddleware, TrackAllUsersMiddleware


async def main():
    # В get_config передаются два аргумента:
    # 1. Модель Pydantic, в которую будет преобразована часть конфига
    # 2. Корневой "ключ", из которого данные читаются и накладываются на модель
    db_config = get_config(DbConfig, "db")

    engine = create_async_engine(
        url=str(db_config.dsn),  # здесь требуется приведение к строке
        echo=db_config.is_echo
    )

    # Проверка соединения с СУБД
    async with engine.begin() as conn:
        await conn.execute(text("SELECT 1"))

    # Создание таблиц
    async with engine.begin() as connection:
        # Если ловите ошибку "таблица уже существует",
        # раскомментируйте следующую строку:
        # await connection.run_sync(Base.metadata.drop_all)
        await connection.run_sync(Base.metadata.create_all)

    # Создание диспетчера
    dp = Dispatcher(db_engine=engine)

    # Подключение мидлварей
    Sessionmaker = async_sessionmaker(engine, expire_on_commit=False)
    dp.update.outer_middleware(DbSessionMiddleware(Sessionmaker))
    dp.message.outer_middleware(TrackAllUsersMiddleware())

    dp.include_routers(*get_routers())

    bot_config = get_config(BotConfig, "bot")
    bot = Bot(token=bot_config.token.get_secret_value())

    print("Starting polling...")
    await dp.start_polling(bot)


asyncio.run(main())
