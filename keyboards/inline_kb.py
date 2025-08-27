from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database.db import SessionLocal
from database.models import Product, Category

# 📁 Kategoriyalar ro‘yxati tugmasi
def get_categories_keyboard():
    session = SessionLocal()
    categories = session.query(Category).all()
    session.close()

    if not categories:
        return None

    buttons = [
        [InlineKeyboardButton(text=cat.name, callback_data=f"category_{cat.id}")]
        for cat in categories
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# 📦 Mahsulotlar ro‘yxati tugmasi (hammasi yoki kategoriya bo‘yicha)
def get_products_keyboard(category_id: int = None):
    session = SessionLocal()
    if category_id:
        products = session.query(Product).filter(Product.category_id == category_id).all()
    else:
        products = session.query(Product).all()
    session.close()

    if not products:
        return None

    buttons = [
        [InlineKeyboardButton(text=product.name, callback_data=f"product_{product.id}")]
        for product in products
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# 📱 Mahsulot tafsiloti tugmalari
def get_product_detail_keyboard(product_id: int, is_admin: bool = False):
    buttons = [
        [InlineKeyboardButton(text="🛒 Buyurtma berish", callback_data=f"order_{product_id}")]
    ]

    if is_admin:
        buttons.append(
            [InlineKeyboardButton(text="🗑 Mahsulotni o'chirish", callback_data=f"delete_product_{product_id}")]
        )

    buttons.append(
        [InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back_to_products")]
    )

    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_contact_admin_button():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📞 Admin bilan hoziroq bog‘lanish", url="https://t.me/YOUR_ADMIN_USERNAME")]
        ]
    )

def get_category_list_keyboard(categories, action: str):
    buttons = [
        [InlineKeyboardButton(text=cat.name, callback_data=f"{action}_category_{cat.id}")]
        for cat in categories
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)