from aiogram import Router

from . import basic_commands
from . import ordering_food
from . import calculator


def get_routers() -> list[Router]:
    return [
        basic_commands.router,
        ordering_food.router,
        calculator.router
    ]
