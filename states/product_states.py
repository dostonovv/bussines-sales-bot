from aiogram.fsm.state import StatesGroup, State

class ProductStates(StatesGroup):
    waiting_for_product_name = State()
    waiting_for_product_description = State()
    waiting_for_product_price = State()
    waiting_for_product_category = State()  # 🆕 Kategoriya tanlash bosqichi
    waiting_for_product_image = State()
