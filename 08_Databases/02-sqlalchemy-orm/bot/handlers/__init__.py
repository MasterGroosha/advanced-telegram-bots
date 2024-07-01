from aiogram import Router
from . import commands, for_admin


def get_routers() -> list[Router]:
    return [
        for_admin.router,
        commands.router
    ]
