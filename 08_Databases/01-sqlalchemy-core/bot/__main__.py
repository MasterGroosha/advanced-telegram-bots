import asyncio

from aiogram import Bot, Dispatcher
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from bot.config_reader import get_config, BotConfig, DbConfig
from bot.db.tables import metadata
from bot.handlers import get_routers


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
    async with engine.begin() as conn:
        # Если ловите ошибку "таблица уже существует",
        # раскомментируйте следующую строку:
        # await conn.run_sync(metadata.drop_all)
        await conn.run_sync(metadata.create_all)

    dp = Dispatcher(db_engine=engine)
    dp.include_routers(*get_routers())

    bot_config = get_config(BotConfig, "bot")
    bot = Bot(token=bot_config.token.get_secret_value())

    print("Starting polling...")
    await dp.start_polling(bot)


asyncio.run(main())
