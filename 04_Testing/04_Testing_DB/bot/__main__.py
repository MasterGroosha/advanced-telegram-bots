import asyncio

from aiogram import Bot, Dispatcher
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from bot.config_reader import parse_settings
from bot.handlers import get_routers
from bot.middlewares import DbSessionMiddleware
from bot.db.requests import test_connection


async def main():
    settings = parse_settings()

    engine = create_async_engine(url=str(settings.db_url), echo=True)
    sessionmaker = async_sessionmaker(engine, expire_on_commit=False)

    async with sessionmaker() as session:
        await test_connection(session)

    dp = Dispatcher()
    dp.update.middleware(DbSessionMiddleware(session_pool=sessionmaker))
    dp.include_routers(*get_routers())

    bot = Bot(token=settings.bot_token.get_secret_value())

    print("Starting polling...")
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
