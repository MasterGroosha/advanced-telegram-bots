from aiogram import Router
from . import commands


def get_routers() -> list[Router]:
    return [
        commands.router
    ]
