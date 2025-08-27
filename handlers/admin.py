import os
from datetime import datetime, timedelta
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from config import ADMINS, IMAGES_DIR
from keyboards.admin_kb import admin_menu
from keyboards.inline_kb import get_product_detail_keyboard
from database.db import SessionLocal
from database.models import Product, Category, Order, ActivityLog
from states.product_states import ProductStates
from sqlalchemy import func
from states.category_states import CategoryStates
from states.broadcast_states import BroadcastStates
admin_router = Router()

# 🛠 Admin panelga kirish
@admin_router.message(F.text == "/admin")
async def admin_panel(message: Message):
    if message.from_user.id in ADMINS:
        await message.answer("Admin panelga xush kelibsiz", reply_markup=admin_menu)
    else:
        await message.answer(f"Siz admin emassiz! Sizning ID: {message.from_user.id}")

# ➕ Mahsulot qo‘shish jarayoni — FSM
@admin_router.message(F.text == "➕ Mahsulot qo'shish")
async def add_product_start(message: Message, state: FSMContext):
    await message.answer("📝 Mahsulot nomini kiriting:")
    await state.set_state(ProductStates.waiting_for_product_name)

@admin_router.message(ProductStates.waiting_for_product_name)
async def add_product_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("📄 Mahsulot tavsifini kiriting:")
    await state.set_state(ProductStates.waiting_for_product_description)

@admin_router.message(ProductStates.waiting_for_product_description)
async def add_product_description(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    await message.answer("💰 Mahsulot narxini kiriting:")
    await state.set_state(ProductStates.waiting_for_product_price)

@admin_router.message(ProductStates.waiting_for_product_price)
async def add_product_price(message: Message, state: FSMContext):
    try:
        price = float(message.text)
        await state.update_data(price=price)

        session = SessionLocal()
        categories = session.query(Category).all()
        session.close()

        if not categories:
            await message.answer("❌ Kategoriya topilmadi. Avval kategoriya qo‘shing.")
            await state.clear()
            return

        buttons = [
            [InlineKeyboardButton(text=cat.name, callback_data=f"select_category_{cat.id}")]
            for cat in categories
        ]
        markup = InlineKeyboardMarkup(inline_keyboard=buttons)
        await message.answer("📂 Mahsulot kategoriyasini tanlang:", reply_markup=markup)
        await state.set_state(ProductStates.waiting_for_product_category)

    except ValueError:
        await message.answer("❌ Narx raqam bo'lishi kerak. Qayta kiriting:")

@admin_router.callback_query(F.data.startswith("select_category_"))
async def select_product_category(callback: CallbackQuery, state: FSMContext):
    category_id = int(callback.data.split("_")[2])
    await state.update_data(category_id=category_id)
    await callback.message.answer("🖼 Mahsulot rasmini yuboring:")
    await state.set_state(ProductStates.waiting_for_product_image)
    await callback.answer()

@admin_router.message(ProductStates.waiting_for_product_image, F.photo)
async def add_product_image(message: Message, state: FSMContext):
    data = await state.get_data()
    file_id = message.photo[-1].file_id
    file = await message.bot.get_file(file_id)
    file_path = file.file_path
    local_image_path = os.path.join(IMAGES_DIR, f"{file_id}.jpg")
    await message.bot.download_file(file_path, local_image_path)

    session = SessionLocal()
    product = Product(
        name=data["name"],
        description=data["description"],
        price=data["price"],
        image_path=local_image_path,
        category_id=data["category_id"]
    )
    session.add(product)
    session.commit()
    session.close()

    await message.answer("✅ Mahsulot qo'shildi", reply_markup=admin_menu)
    await state.clear()

# 📋 Mahsulotlar ro‘yxati
@admin_router.message(F.text == "📋 Mahsulotlar ro'yxati")
async def show_admin_products(message: Message):
    session = SessionLocal()
    products = session.query(Product).all()
    session.close()

    if not products:
        await message.answer("Mahsulotlar topilmadi.")
        return

    buttons = [
        [InlineKeyboardButton(text=p.name, callback_data=f"admin_product_{p.id}")]
        for p in products
    ]
    markup = InlineKeyboardMarkup(inline_keyboard=buttons)
    await message.answer("📋 Mahsulotlar ro'yxati:", reply_markup=markup)

# 📦 Mahsulot tafsiloti
@admin_router.callback_query(F.data.startswith("admin_product_"))
async def admin_product_detail(callback: CallbackQuery):
    product_id = int(callback.data.split("_")[2])
    session = SessionLocal()
    product = session.query(Product).filter(Product.id == product_id).first()

    if not product:
        session.close()
        await callback.answer("Mahsulot topilmadi!")
        return

    caption = f"📦 {product.name}\nNarxi: {product.price} so'm\n\n📝 {product.description}"
    is_admin = callback.from_user.id in ADMINS
    keyboard = get_product_detail_keyboard(product_id, is_admin=is_admin)

    if os.path.exists(product.image_path):
        photo = FSInputFile(product.image_path)
        await callback.message.answer_photo(photo=photo, caption=caption, reply_markup=keyboard)
    else:
        await callback.message.answer(caption, reply_markup=keyboard)

    session.close()
    await callback.answer()

# 🗑 Mahsulotni o‘chirish
@admin_router.callback_query(F.data.startswith("delete_product_"))
async def admin_delete_product(callback: CallbackQuery):
    if callback.from_user.id not in ADMINS:
        await callback.answer("Sizda bu amalni bajarish huquqi yo'q!", show_alert=True)
        return

    product_id = int(callback.data.split("_")[2])
    session = SessionLocal()
    product = session.query(Product).filter(Product.id == product_id).first()

    if product:
        session.delete(product)
        session.commit()
        await callback.message.answer(f"🗑 Mahsulot o'chirildi: {product.name}")
    else:
        await callback.message.answer("Mahsulot topilmadi.")
    session.close()
    await callback.answer()

# 📦 Buyurtmalar ro‘yxati
@admin_router.message(F.text == "📦 Buyurtmalar ro'yxati")
async def show_orders_list(message: Message):
    session = SessionLocal()
    orders = session.query(Order).all()

    if not orders:
        await message.answer("Hozircha buyurtmalar yo'q")
        session.close()
        return

    text = "📦 Barcha buyurtmalar:\n\n"
    for order in orders:
        product = session.query(Product).filter(Product.id == order.product_id).first()
        product_name = product.name if product else "Noma'lum mahsulot"

        text += (
            f"🔢 ID: {order.id}\n"
            f"👤 User ID: {order.user_id}\n"
            f"📞 Telefon: {order.phone_number}\n"
            f"📱 Mahsulot: {product_name}\n"
            f"📊 Miqdor: {order.quantity}\n"
            f"📋 Status: {order.status}\n"
            f"{'=' * 25}\n\n"
        )

    session.close()
    await message.answer(text)
    await message.answer("❌ Buyurtmani o'chirish uchun buyurtma ID ni yuboring:")

# ❌ Buyurtmani o‘chirish
@admin_router.message(F.text.regexp(r"^\d+$"))
async def admin_cancel_order_by_id(message: Message):
    order_id = int(message.text)
    session = SessionLocal()
    order = session.query(Order).filter(Order.id == order_id).first()

    if order:
        session.delete(order)
        session.commit()
        await message.answer(f"❌ Buyurtma #{order_id} o'chirildi.")
    else:
        await message.answer("Buyurtma topilmadi.")
    session.close()

# 📊 Statistika
@admin_router.message(F.text == "📊 Statistika")
async def show_activity_stats(message: Message):
    session = SessionLocal()

    activity_stats = session.query(ActivityLog.hour, func.count(ActivityLog.id))\
        .group_by(ActivityLog.hour).all()

    text = "📊 Foydalanuvchi aktivligi (soat bo‘yicha):\n\n"
    for hour, count in sorted(activity_stats):
        text += f"🕒 {hour}: {count} ta foydalanuvchi\n"

    now = datetime.now()
    today = now.date()
    yesterday = today - timedelta(days=1)
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)

    def get_sales_count(start_date):
        return session.query(Order).filter(Order.created_at >= start_date).count()

    text += "\n📈 Sotuv statistikasi:\n"
    text += f"📅 Bugun: {get_sales_count(today)} ta\n"
    text += f"📅 Kecha: {get_sales_count(yesterday)} ta\n"
    text += f"🗓 Oxirgi 7 kun: {get_sales_count(week_ago)} ta\n"
    text += f"🗓 Oxirgi 30 kun: {get_sales_count(month_ago)} ta\n"

    session.close()
    await message.answer(text)

# ➕ Kategoriya qo‘shish — boshlanishi
@admin_router.message(F.text == "➕ Kategoriya qo'shish")
async def start_add_category(message: Message, state: FSMContext):
    await message.answer("📝 Yangi kategoriya nomini kiriting:")
    await state.set_state(CategoryStates.waiting_for_name)

# 📝 Kategoriya nomini qabul qilish
@admin_router.message(CategoryStates.waiting_for_name)
async def receive_category_name(message: Message, state: FSMContext):
    category_name = message.text.strip()

    if not category_name:
        await message.answer("❌ Kategoriya nomi bo‘sh bo‘lmasligi kerak. Qayta kiriting:")
        return

    session = SessionLocal()
    existing = session.query(Category).filter(Category.name == category_name).first()

    if existing:
        await message.answer("❌ Bu nomdagi kategoriya allaqachon mavjud.")
        session.close()
        await state.clear()
        return

    new_category = Category(name=category_name)
    session.add(new_category)
    session.commit()
    session.close()

    await message.answer(f"✅ Kategoriya qo‘shildi: {category_name}", reply_markup=admin_menu)
    await state.clear()
@admin_router.message(F.text == "✏️ Kategoriya tahrirlash")
async def start_edit_category(message: Message):
    session = SessionLocal()
    categories = session.query(Category).all()
    session.close()

    if not categories:
        await message.answer("❌ Kategoriya topilmadi.")
        return

    buttons = [
        [InlineKeyboardButton(text=cat.name, callback_data=f"edit_category_{cat.id}")]
        for cat in categories
    ]
    markup = InlineKeyboardMarkup(inline_keyboard=buttons)
    await message.answer("✏️ Tahrirlash uchun kategoriyani tanlang:", reply_markup=markup)

@admin_router.callback_query(F.data.startswith("edit_category_"))
async def edit_category_selected(callback: CallbackQuery, state: FSMContext):
    category_id = int(callback.data.split("_")[2])
    await state.update_data(category_id=category_id)
    await callback.message.answer("📝 Yangi nomni kiriting:")
    await state.set_state(CategoryStates.waiting_for_edit_name)
    await callback.answer()

@admin_router.message(CategoryStates.waiting_for_edit_name)
async def receive_new_category_name(message: Message, state: FSMContext):
    new_name = message.text.strip()
    data = await state.get_data()
    category_id = data["category_id"]

    session = SessionLocal()
    category = session.query(Category).filter(Category.id == category_id).first()

    if category:
        category.name = new_name
        session.commit()
        await message.answer(f"✅ Kategoriya nomi yangilandi: {new_name}", reply_markup=admin_menu)
    else:
        await message.answer("❌ Kategoriya topilmadi.")
    session.close()
    await state.clear()
@admin_router.message(F.text == "🗑 Kategoriya o'chirish")
async def start_delete_category(message: Message):
    session = SessionLocal()
    categories = session.query(Category).all()
    session.close()

    if not categories:
        await message.answer("❌ Kategoriya topilmadi.")
        return

    buttons = [
        [InlineKeyboardButton(text=cat.name, callback_data=f"delete_category_{cat.id}")]
        for cat in categories
    ]
    markup = InlineKeyboardMarkup(inline_keyboard=buttons)
    await message.answer("🗑 O'chirish uchun kategoriyani tanlang:", reply_markup=markup)

@admin_router.callback_query(F.data.startswith("delete_category_"))
async def delete_category_selected(callback: CallbackQuery):
    category_id = int(callback.data.split("_")[2])

    session = SessionLocal()
    category = session.query(Category).filter(Category.id == category_id).first()

    if category:
        session.delete(category)
        session.commit()
        await callback.message.answer(f"🗑 Kategoriya o'chirildi: {category.name}", reply_markup=admin_menu)
    else:
        await callback.message.answer("❌ Kategoriya topilmadi.")
    session.close()
    await callback.answer()
@admin_router.message(F.text == "📢 Reklama jo'natish")
async def start_broadcast(message: Message, state: FSMContext):
    await message.answer("📝 Reklama matnini kiriting:")
    await state.set_state(BroadcastStates.waiting_for_text)

@admin_router.message(BroadcastStates.waiting_for_text)
async def receive_broadcast_text(message: Message, state: FSMContext):
    await state.update_data(text=message.text)
    await message.answer("🖼 Reklama uchun rasm yuboring:")
    await state.set_state(BroadcastStates.waiting_for_image)

@admin_router.message(BroadcastStates.waiting_for_image, F.photo)
async def receive_broadcast_image(message: Message, state: FSMContext):
    data = await state.get_data()
    ad_text = data["text"]
    file_id = message.photo[-1].file_id

    session = SessionLocal()
    user_ids = session.query(ActivityLog.user_id).distinct().all()
    session.close()

    count = 0
    for (user_id,) in user_ids:
        try:
            await message.bot.send_photo(chat_id=user_id, photo=file_id, caption=ad_text)
            count += 1
        except Exception as e:
            print(f"❌ {user_id} ga jo'natilmadi: {e}")

    await message.answer(f"✅ Reklama {count} ta foydalanuvchiga jo'natildi.")
    await state.clear()
