from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram_dialog import DialogManager, StartMode
from fluentogram import TranslatorRunner

from bot.handling.states import Watermark

start_router = Router()

@start_router.message(Command("start"))
async def handler(msg: Message, dialog_manager: DialogManager, i18n: TranslatorRunner):
    await dialog_manager.start(Watermark.enter_text, mode=StartMode.RESET_STACK)
