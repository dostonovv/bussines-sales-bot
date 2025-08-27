import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN
from database.db import Base, engine
from handlers.admin import admin_router
from handlers.user import user_router

from database import models
# 📋 Logging sozlash
logging.basicConfig(level=logging.INFO)

async def main():
    # 🗄️ Ma’lumotlar bazasini yaratish (faqat test uchun)
    Base.metadata.create_all(bind=engine)

    # 🤖 Bot va Dispatcher yaratish
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )

    # 🧠 FSM uchun storage
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    # 🔗 Routerlarni birlashtirish
    dp.include_router(admin_router)
    dp.include_router(user_router)

    # 🚀 Botni ishga tushirish
    print("🚀 Bot ishga tushdi...")
    await dp.start_polling(bot)

# 🏁 Asosiy ishga tushirish nuqtasi
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("🧨 Dastur to‘xtatildi")
