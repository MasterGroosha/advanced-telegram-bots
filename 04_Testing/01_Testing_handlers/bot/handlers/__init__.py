from aiogram import Router

from . import basic_commands
from . import user_id_handlers
from . import capybara_handlers
from . import generate_handlers


def get_routers() -> list[Router]:
    return [
        basic_commands.router,
        user_id_handlers.router,
        capybara_handlers.router,
        generate_handlers.router
    ]
