import logging
from aiogram import Dispatcher, Bot
from data.config import ADMINS  # ADMINS ro'yxati

# Bot obyektini to'g'ri import qilish
async def notify_admin(user_full_name: str, user_id: int, users_count: int, bot: Bot):
    """Adminlarga foydalanuvchi haqida xabar yuborish"""
    try:
        message = f"Yangi foydalanuvchi botga kirgan:\nFull Name: {user_full_name}\nUser ID: {user_id}\nJami foydalanuvchilar soni: {users_count}"
        for admin_id in ADMINS:  # ADMINS ro'yxatidagi barcha adminlarga xabar yuborish
            await bot.send_message(admin_id, message)
    except Exception as e:
        logging.error(f"Adminga xabar yuborishda xatolik: {e}")


async def on_startup_notify(dp: Dispatcher):
    """Bot ishga tushganida adminlarga xabar yuborish"""
    try:
        bot = dp.bot  # Bot obyektini Dispatcher orqali olish
        for admin in ADMINS:
            await bot.send_message(admin, "Bot faollashdi!")
    except Exception as err:
        logging.exception(f"Xatolik: {err}")
