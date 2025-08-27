from aiogram.fsm.state import StatesGroup, State

class BroadcastStates(StatesGroup):
    waiting_for_text = State()
    waiting_for_image = State()
