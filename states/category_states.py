from aiogram.fsm.state import StatesGroup, State

class CategoryStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_edit_name = State()
    waiting_for_delete_confirmation = State()
