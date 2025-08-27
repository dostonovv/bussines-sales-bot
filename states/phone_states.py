from aiogram.fsm.state import StatesGroup, State

class PhoneStates(StatesGroup):
    waiting_for_phone_number_input = State()
