from random import randint

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, FSInputFile

router = Router()


def choose_random_image():
    return randint(1, 10_000)


@router.message(Command("capybara"))
async def cmd_capybara(message: Message):
    await message.answer_photo(
        photo=FSInputFile(f"/opt/images/capybara_{choose_random_image()}.jpg"),
        caption="Вот случайная капибара"
    )
