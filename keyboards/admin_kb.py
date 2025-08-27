from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

admin_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="➕ Mahsulot qo'shish")],
        [KeyboardButton(text="➕ Kategoriya qo'shish")],
        [KeyboardButton(text="✏️ Kategoriya tahrirlash")],  # 🆕 Qo‘shildi
        [KeyboardButton(text="🗑 Kategoriya o'chirish")],    # 🆕 Qo‘shildi
        [KeyboardButton(text="📋 Mahsulotlar ro'yxati")],
        [KeyboardButton(text="📦 Buyurtmalar ro'yxati")],
        [KeyboardButton(text="📊 Statistika")],
        [KeyboardButton(text="📢 Reklama jo'natish")],

    ],
    resize_keyboard=True
)
