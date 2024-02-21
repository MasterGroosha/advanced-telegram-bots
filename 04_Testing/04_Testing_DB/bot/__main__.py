import asyncio

from aiogram import Bot, Dispatcher
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from bot.config_reader import parse_settings
from bot.handlers import get_routers
from bot.middlewares import DbSessionMiddleware
from bot.db.requests import test_connection


async def main():
    # Получение настроек текущего приложения
    settings = parse_settings()

    # Создание асинхронного "движка" с указанием URL подключения
    engine = create_async_engine(url=str(settings.db_url), echo=True)
    # Создание пула сессий
    sessionmaker = async_sessionmaker(engine, expire_on_commit=False)

    # Из пула извлекается одна сессия
    # и проверяется подключение к СУБД
    # Если связи нет, то код "упадёт".
    # Но это нормально, потому что ситуация критическая
    async with sessionmaker() as session:
        await test_connection(session)

    # Создание диспетчера aiogram
    dp = Dispatcher()
    # На тип Update (родительский тип всех видов апдейтов)
    # навешивается мидлварь, из которой будут пробрасываться сессии в хэндлеры
    dp.update.middleware(DbSessionMiddleware(session_pool=sessionmaker))
    # Подключение цепочки роутеров к диспетчеру
    dp.include_routers(*get_routers())

    # Создание объекта бота с токеном, полученным из настроек
    bot = Bot(token=settings.bot_token.get_secret_value())

    print("Starting polling...")

    # Запуск поллинга
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
