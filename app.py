import logging
from aiogram import executor

from loader import dp, user_db
from utils.db_api.currency import init_currency_cache  # Keshni boshqarish uchun import
import middlewares, filters, handlers
from utils.notify_admins import on_startup_notify
from utils.set_bot_commands import set_default_commands


# Logger sozlash
logging.basicConfig(level=logging.INFO)

async def on_startup(dispatcher):
    """Botni ishga tushirishda bajariladigan funksiya"""
    # Birlamchi komandalar (/start va /help)
    await set_default_commands(dispatcher)

    try:
        # Foydalanuvchilar jadvalini yaratish
        user_db.create_table_users()
        logging.info("Foydalanuvchilar jadvali yaratildi yoki allaqachon mavjud.")
    except Exception as e:
        logging.error(f"Foydalanuvchilar jadvali yaratishda xatolik: {e}")

    try:
        # Valyuta keshini yaratish va ma'lumotlarni qo'shish
        init_currency_cache()
        logging.info("Valyuta kesh jadvali yaratildi va dastlabki ma'lumotlar qo'shildi.")
    except Exception as e:
        logging.error(f"Keshni yaratishda yoki ma'lumot qo'shishda xatolik: {e}")

    # Bot ishga tushgani haqida adminga xabar berish
    await on_startup_notify(dispatcher)


if __name__ == '__main__':
    # Botni boshlash
    executor.start_polling(dp, on_startup=on_startup)
