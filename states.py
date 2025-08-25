from aiogram.fsm.state import State, StatesGroup

class TextoidStates(StatesGroup):
    waiting_for_input = State()
    generated = State()  # <-- добавляем это
