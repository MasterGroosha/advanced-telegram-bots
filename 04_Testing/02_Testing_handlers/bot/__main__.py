import asyncio

from aiogram import Bot, Dispatcher

from bot.config_reader import parse_settings
from bot.handlers import get_routers


async def main():
    settings = parse_settings()

    dp = Dispatcher()
    dp.include_routers(*get_routers())

    bot = Bot(token=settings.bot_token.get_secret_value())

    print("Starting polling...")
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == '__main__':
    asyncio.run(main())
