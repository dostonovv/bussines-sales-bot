from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def amount_keyboard(current_quantity: int) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="➖"),
                KeyboardButton(text=f"{current_quantity} dona"),
                KeyboardButton(text="➕")
            ],
            [
                KeyboardButton(text="✅ Tasdiqlash"),
                KeyboardButton(text="🔙 Orqaga")
            ]
        ],
        resize_keyboard=True,
        one_time_keyboard=False,
        input_field_placeholder="➕ yoki ➖ tugmasini bosing"
    )
