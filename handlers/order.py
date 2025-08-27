from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from states.order_states import OrderStates
from database.db import SessionLocal
from database.models import Order

order_router = Router()

# 🛒 Mahsulot tanlanganda
@order_router.callback_query(F.data.startswith("order_"))
async def start_order(callback: CallbackQuery, state: FSMContext):
    product_id = int(callback.data.split("_")[1])
    await state.update_data(product_id=product_id)
    await callback.message.answer("📞 Telefon raqamingizni kiriting:")
    await state.set_state(OrderStates.waiting_for_phone_number_input)
    await callback.answer()

# 📞 Telefon raqamini qabul qilish
@order_router.message(OrderStates.waiting_for_phone_number_input)
async def receive_phone(message: Message, state: FSMContext):
    phone = message.text.strip()
    data = await state.get_data()
    product_id = data.get("product_id")
    user_id = message.from_user.id

    session = SessionLocal()
    order = Order(
        user_id=user_id,
        product_id=product_id,
        quantity=1,  # Default 1 dona
        phone_number=phone,
        status="pending"
    )
    session.add(order)
    session.commit()
    order_id = order.id
    session.close()

    # ✅ Buyurtma tasdiqlandi
    await message.answer(
        f"✅ Buyurtma qabul qilindi!\n\n"
        f"📦 Buyurtma ID: {order_id}\n"
        f"📞 Telefon: {phone}\n"
        f"Tez orada siz bilan bog'lanamiz.",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="📲 Admin bilan hoziroq bog‘lanish")]],
            resize_keyboard=True
        )
    )
    await state.clear()
