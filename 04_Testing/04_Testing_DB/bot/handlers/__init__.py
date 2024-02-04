from aiogram import Router

from . import basic_commands
from . import ordering_food


def get_routers() -> list[Router]:
    return [
        basic_commands.router,
        ordering_food.router,
    ]
