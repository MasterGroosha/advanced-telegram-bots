from aiogram.fsm.state import State, StatesGroup


class Watermark(StatesGroup):
    enter_text = State()
    enter_photo = State()
