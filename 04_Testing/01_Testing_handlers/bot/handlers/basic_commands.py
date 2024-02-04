from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from aiogram.enums import DiceEmoji

router = Router(name="Basic Commands Router")


@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer("Привет!")


@router.message(Command("dice"))
async def cmd_dice(message: Message):
    dice_msg = await message.answer_dice(emoji=DiceEmoji.DICE)
    if dice_msg.dice.value == 1:
        await message.answer("Успех!")
    else:
        await message.answer("В другой раз повезёт!")
