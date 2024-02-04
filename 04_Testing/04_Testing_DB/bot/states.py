from aiogram.fsm.state import StatesGroup, State


class OrderFoodStates(StatesGroup):
    choosing_food_name = State()
    choosing_food_size = State()
