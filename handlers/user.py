from aiogram import Router, F
from aiogram.types import (
    Message, CallbackQuery, FSInputFile,
    ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove,
    InlineKeyboardMarkup, InlineKeyboardButton
)
from utils.creator import get_creator_name
from aiogram.fsm.context import FSMContext
from keyboards.user_kb import user_menu
from keyboards.inline_kb import (
    get_product_detail_keyboard,
    get_contact_admin_button
)
from database.db import SessionLocal
from database.models import Product, Category, Order, ActivityLog
from states.phone_states import PhoneStates
from datetime import datetime
import os

user_router = Router()
ADMIN_IDS = [123456789, 987654321 ,]  # Admin Telegram ID lar

# 🟢 /start komandasi
@user_router.message(F.text == "/start")
async def start(message: Message):
    session = SessionLocal()
    log = ActivityLog(user_id=message.from_user.id, hour=datetime.now().hour)
    session.add(log)
    session.commit()
    session.close()
    await message.answer("Xush kelibsiz!", reply_markup=user_menu)

# 📂 Kategoriyalar ro‘yxati
@user_router.message(F.text.in_(["🛍 Mahsulotlar", "🛍 Mahsulotlar ro'yxati"]))
async def show_categories(message: Message):
    session = SessionLocal()
    categories = session.query(Category).all()
    session.close()

    if not categories:
        await message.answer("Hozircha kategoriyalar yo'q")
        return

    buttons = [
        [InlineKeyboardButton(text=cat.name, callback_data=f"category_{cat.id}")]
        for cat in categories
    ]
    markup = InlineKeyboardMarkup(inline_keyboard=buttons)
    await message.answer("📂 Kategoriyalar ro'yxati:\nQuyidagilardan birini tanlang:", reply_markup=markup)

# 📦 Kategoriya ichidagi mahsulotlar
@user_router.callback_query(F.data.startswith("category_"))
async def show_products_in_category(callback: CallbackQuery):
    category_id = int(callback.data.split("_")[1])
    session = SessionLocal()
    products = session.query(Product).filter(Product.category_id == category_id).all()
    session.close()

    if not products:
        await callback.message.answer("Bu kategoriyada mahsulotlar yo'q.")
        await callback.answer()
        return

    buttons = [
        [InlineKeyboardButton(text=p.name, callback_data=f"product_{p.id}")]
        for p in products
    ]
    markup = InlineKeyboardMarkup(inline_keyboard=buttons)
    await callback.message.answer("📱 Mahsulotlar ro'yxati:", reply_markup=markup)
    await callback.answer()

# 📱 Mahsulot tafsiloti
@user_router.callback_query(F.data.startswith("product_"))
async def show_product_detail(callback: CallbackQuery):
    product_id = int(callback.data.split("_")[1])
    user_id = callback.from_user.id

    session = SessionLocal()
    product = session.query(Product).filter(Product.id == product_id).first()
    session.close()

    if not product:
        await callback.answer("Mahsulot topilmadi!")
        return

    is_admin = user_id in ADMIN_IDS
    caption = (
        f"📱 {product.name}\n\n"
        f"💰 Narx: {product.price} so'm\n\n"
        f"📝 Tavsif:\n{product.description}"
    )
    keyboard = get_product_detail_keyboard(product_id, is_admin=is_admin)

    if os.path.exists(product.image_path):
        photo = FSInputFile(product.image_path)
        await callback.message.delete()
        await callback.message.answer_photo(photo=photo, caption=caption, reply_markup=keyboard)
    else:
        await callback.message.edit_text(text=caption, reply_markup=keyboard)

    await callback.answer()

# 🛒 Buyurtma bosqichi: to‘g‘ridan-to‘g‘ri buyurtma yaratish
@user_router.callback_query(F.data.startswith("order_"))
async def start_order(callback: CallbackQuery, state: FSMContext):
    product_id = int(callback.data.split("_")[1])
    user_id = callback.from_user.id

    session = SessionLocal()
    order = Order(
        user_id=user_id,
        product_id=product_id,
        quantity=1,  # ✅ Default 1 dona
        status="pending"
    )
    session.add(order)
    session.commit()
    order_id = order.id
    session.close()

    await callback.message.answer(
        f"✅ Buyurtma qabul qilindi!\n\n"
        f"🔢 Buyurtma ID: {order_id}\n"
        f"📊 Miqdor: 1 dona\n\n"
        f"Tez orada siz bilan bog'lanamiz!"
    )

    phone_kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="📱 Raqamni yuborish", request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    await callback.message.answer("Iltimos, telefon raqamingizni yuboring:", reply_markup=phone_kb)
    await state.set_state(PhoneStates.waiting_for_phone_number_input)
    await callback.answer()

# 📱 Telefon raqamini qabul qilish
@user_router.message(F.contact, PhoneStates.waiting_for_phone_number_input)
async def receive_phone(message: Message, state: FSMContext):
    phone = message.contact.phone_number
    await message.answer(
        f"✅ Raqamingiz qabul qilindi: {phone}\n/start ni bosing",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.clear()

# 🔙 Orqaga qaytish
@user_router.callback_query(F.data == "back_to_products")
async def back_to_products(callback: CallbackQuery):
    session = SessionLocal()
    categories = session.query(Category).all()
    session.close()

    buttons = [
        [InlineKeyboardButton(text=cat.name, callback_data=f"category_{cat.id}")]
        for cat in categories
    ]
    markup = InlineKeyboardMarkup(inline_keyboard=buttons)
    await callback.message.answer("📂 Kategoriyalar ro'yxati:", reply_markup=markup)
    await callback.answer()

# 📦 Mening buyurtmalarim
@user_router.message(F.text == "📦 Mening buyurtmalarim")
async def my_orders(message: Message):
    session = SessionLocal()
    orders = session.query(Order).filter(Order.user_id == message.from_user.id).all()
    session.close()

    if not orders:
        await message.answer("Sizda buyurtmalar yo'q")
    else:
        text = "📦 Sizning buyurtmalaringiz:\n\n"
        for o in orders:
            text += (
                f"🔢 ID: {o.id}\n"
                f"📱 Mahsulot ID: {o.product_id}\n"
                f"📊 Miqdor: {o.quantity}\n"
                f"📋 Status: {o.status}\n\n"
            )
        text += "❌ Buyurtmani bekor qilish uchun buyurtma ID ni yuboring:"
        await message.answer(text)

# ❌ Buyurtmani bekor qilish
@user_router.message(F.text.regexp(r"^\d+$"))
async def cancel_order_by_id(message: Message):
    order_id = int(message.text)
    session = SessionLocal()
    order = session.query(Order).filter(
        Order.id == order_id,
        Order.user_id == message.from_user.id
    ).first()

    if order:
        order.status = "Bekor qilingan"
        session.commit()
        await message.answer(f"❌ Buyurtma #{order_id} bekor qilindi.")
    else:
        await message.answer("Buyurtma topilmadi yoki sizga tegishli emas.")
    session.close()

# 🗑 Mahsulotni o‘chirish (faqat admin)
@user_router.callback_query(F.data.startswith("delete_product_"))
async def delete_product(callback: CallbackQuery):
    user_id = callback.from_user.id
    if user_id not in ADMIN_IDS:
        await callback.answer("Sizda bu amalni bajarish huquqi yo'q.")
        return

    product_id = int(callback.data.split("_")[2])
    session = SessionLocal()
    product = session.query(Product).filter(Product.id == product_id).first()

    if product:
        session.delete(product)
        session.commit()
        await callback.message.answer("✅ Mahsulot o'chirildi.")
    else:
        await callback.message.answer("Mahsulot topilmadi.")
    session.close()
    await callback.answer()

@user_router.message(F.text == "/creator")
async def show_creator(message: Message):
    await message.answer(get_creator_name())

@user_router.message(F.contact, PhoneStates.waiting_for_phone_number_input)
async def receive_phone(message: Message, state: FSMContext):
    phone = message.contact.phone_number
    user_id = message.from_user.id

    session = SessionLocal()
    # Oxirgi pending buyurtmani topamiz
    order = session.query(Order).filter(
        Order.user_id == user_id,
        Order.status == "pending",
        Order.phone_number == None
    ).order_by(Order.id.desc()).first()

    if order:
        order.phone_number = phone
        session.commit()
        await message.answer(
            f"✅ Raqamingiz qabul qilindi: {phone}\n"
            f"Buyurtma ID: {order.id}\n/start ni bosing",
            reply_markup=ReplyKeyboardRemove()
        )
    else:
        await message.answer("⚠️ Buyurtma topilmadi yoki raqam allaqachon saqlangan.", reply_markup=ReplyKeyboardRemove())

    session.close()
    await state.clear()


# 📞 Admin bilan bog‘lanish
@user_router.message(F.text == "📞 Admin bilan bog'lanish")
async def contact_admin(message: Message):
    await message.answer(
        "📞 Admin bilan bog‘lanish uchun quyidagi profilga murojaat qiling:\n\n"
        "👉 @@aziiza_erkinova"
    )
