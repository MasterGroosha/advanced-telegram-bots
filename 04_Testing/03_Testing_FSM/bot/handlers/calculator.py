from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardMarkup, ReplyKeyboardRemove
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from bot.states import CalculatorStates

router = Router(name="Calculator Router")


def generate_numbers_keyboard() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    for i in range(1, 10):
        builder.button(text=str(i))
    builder.button(text="0")
    builder.adjust(3, 3, 3, 1)
    return builder.as_markup(resize_keyboard=True)


def generate_actions_keyboard() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    for action in ("+", "-", "*", "/"):
        builder.button(text=action)
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)


@router.message(Command("calc"))
async def cmd_calc(message: Message, state: FSMContext):
    await message.answer(
        "Введите первое число:",
        reply_markup=generate_numbers_keyboard()
    )
    await state.set_state(CalculatorStates.choosing_first_number)


@router.message(
    CalculatorStates.choosing_first_number,
    F.text.cast(int).as_("number")
)
async def num1_correct(message: Message, number: int, state: FSMContext):
    if number > 9:
        await message.answer("Пожалуйста, выберите число от 0 до 9")
        return
    await state.update_data(num1=message.text)
    await message.answer(
        "Введите второе число:",
        reply_markup=generate_numbers_keyboard()
    )
    await state.set_state(CalculatorStates.choosing_second_number)


@router.message(
    CalculatorStates.choosing_second_number,
    F.text.cast(int).as_("number")
)
async def num2_correct(message: Message, number: int, state: FSMContext):
    if number > 9:
        await message.answer("Пожалуйста, выберите число от 0 до 9")
        return
    await state.update_data(num2=message.text)
    await message.answer(
        "Укажите математическую операцию:",
        reply_markup=generate_actions_keyboard()
    )
    await state.set_state(CalculatorStates.choosing_operation)


@router.message(CalculatorStates.choosing_first_number)
@router.message(CalculatorStates.choosing_second_number)
async def nums_incorrect(message: Message):
    await message.answer("Некорректный ввод. Пожалуйста, выберите число от 0 до 9")


@router.message(
    CalculatorStates.choosing_operation,
    F.text.in_({"+", "-", "*", "/"}),
    F.text.as_("operation")
)
async def operation_chosen_correctly(message: Message, state: FSMContext, operation: str):
    data = await state.get_data()
    # Приводим данные к правильным типам, т.к. мы не знаем, какой FSM Storage используется
    num1 = int(data["num1"])
    num2 = int(data["num2"])

    template = "Ответ: "

    match operation:
        case "+":
            answer_text = template + str(num1 + num2)
        case "-":
            answer_text = template + str(num1 - num2)
        case "*":
            answer_text = template + str(num1 * num2)
        case "/":
            if num2 == 0:
                answer_text = "На ноль делить нельзя!"
            else:
                answer_text = template + f"{(num1 / num2):.02f}"
        case _:
            answer_text = "Как ты вообще сюда попал?!"
    await message.answer(
        answer_text,
        reply_markup=ReplyKeyboardRemove()
    )
