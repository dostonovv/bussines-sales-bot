from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

user_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🛍 Mahsulotlar ro'yxati")],
        [KeyboardButton(text="📦 Mening buyurtmalarim")],
        [KeyboardButton(text="📞 Admin bilan bog'lanish")]  # 🆕 Qo‘shildi
    ],
    resize_keyboard=True
)
