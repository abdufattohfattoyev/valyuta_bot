import asyncio
from datetime import datetime, timedelta
import pytz
import aiohttp
from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandStart
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
from decimal import Decimal
import time
from keyboards.inline.inline_knopka import menu
from loader import dp, bot, user_db
from keyboards.default.valyuta_kurs import start_knopka
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from utils.notify_admins import notify_admin
# O'zbekiston vaqt zonasini olish
uzb_tz = pytz.timezone('Asia/Tashkent')

# Global o'zgaruvchilar
last_updated = 0
cache = {}
selected_currency = {}


# Valyuta kurslarini olish funksiyasi
async def get_currency_rate():
    global last_updated, cache
    current_time = time.time()

    # Agar kesh yangilanmagan bo'lsa yoki eski bo'lsa, uni yangilash
    if current_time - last_updated > 3600:  # Keshni har soatda yangilash
        async with aiohttp.ClientSession() as session:
            try:
                # CBU API URL
                async with session.get("https://cbu.uz/uz/arkhiv-kursov-valyut/json/") as response:
                    if response.status == 200:
                        data = await response.json()
                        # Valyutalar ro'yxatini keshga olish
                        new_cache = {item['Ccy']: Decimal(item['Rate']) for item in data}
                        # Agar eski kesh bilan yangi kesh o'rtasida farq bo'lsa, yangilanishni yuborish
                        if cache != new_cache:
                            cache = new_cache
                            last_updated = current_time
                            await send_updates_to_users()  # Foydalanuvchilarga yangilanish yuborish
                    else:
                        print(f"API xatolik: {response.status}")
            except Exception as e:
                print(f"Valyuta olishda xatolik: {e}")
                cache = {}
    return cache


# Foydalanuvchi valyutalar kurslarini ko'rsatishi
@dp.message_handler(text="💱 Valyuta kurslari")
async def show_currency_rates(message: types.Message):
    rates = await get_currency_rate()
    if rates:
        text = "<b>📊 <u>Valyuta kurslari</u>:</b>\n\n"

        currency_list = {
            "USD": "🇺🇸 Dollar",
            "EUR": "🇪🇺 Yevro",
            "GBP": "🇬🇧 Funt",
            "RUB": "🇷🇺 Rubl",
            "CNY": "🇨🇳 Yuan",
            "KRW": "🇰🇷 Von",
            "TRY": "🇹🇷 Lira",
            "TMT": "🇹🇲 Manat",
            "KZT": "🇰🇿 Tenge",
            "TJS": "🇹🇯 Somoni",
            "KGZ": "🇰🇬 Som",
            "AED": "🇦🇪 Dirham"
        }

        # Valyutalar ro'yxatini ko'rsatish, bayroqlar bilan
        for currency, flag in currency_list.items():
            rate = rates.get(currency)
            if rate:
                text += f"1 {flag} = <b>{rate:.2f}</b> so'm\n"

        # Qo'shimcha ma'lumotlar va yangiliklar
        text += "\n<b>💡 Kurslar har soatda yangilanadi.</b>\n"
        text += "<b>⚠️ Diqqat! Kurslar o'zgarishi mumkin.</b>\n\n"

        await message.answer(text, parse_mode="HTML")
    else:
        await message.answer(
            "⚠️ <b>Valyuta kurslarini olishda xatolik yuz berdi. Iltimos, keyinroq qayta urinib ko'ring.</b>",
            parse_mode="HTML")


# Foydalanuvchilarni yangilanishlar bilan yuborish
async def send_updates_to_users():
    rates = await get_currency_rate()
    for user_id, settings in selected_currency.items():
        from_currency = settings["from"]
        to_currency = settings["to"]
        threshold = settings["threshold"]

        if from_currency in rates and to_currency in rates:
            rate = rates[from_currency] / rates[to_currency]
            if rate > threshold:
                await bot.send_message(user_id, f"⚠️ Kurs yangilandi: {from_currency} dan {to_currency} ga konvertatsiya qilish kursi {rate} so'mdan oshdi.")



async def send_daily_currency_updates():
    while True:
        now = datetime.now(uzb_tz)  # O'zbekiston vaqti bilan
        # Kelgusi 10:00 ni olish
        next_run_time = now.replace(hour=10, minute=0, second=0, microsecond=0)

        # Agar hozirgi vaqt 10:00 dan o'tgan bo'lsa, ertangi 10:00 ni kutish
        if now >= next_run_time:
            next_run_time += timedelta(days=1)

        # Kutish vaqti
        wait_time = (next_run_time - now).total_seconds()

        # Belirlangan vaqtda yangilanishlarni yuborish
        await asyncio.sleep(wait_time)
        await send_updates_to_users()  # Foydalanuvchilarga yangilanish yuborish


@dp.message_handler(CommandStart())
async def bot_start(message: types.Message):
    # Foydalanuvchini ro'yxatga olish
    user_info = {
        "user_id": message.from_user.id,
        "full_name": message.from_user.full_name,
        "username": message.from_user.username,
    }

    try:
        # Foydalanuvchi bazada mavjudligini tekshirish
        existing_user = user_db.get_user_by_id(user_info['user_id'])
        if existing_user:
            print(f"Foydalanuvchi {message.from_user.full_name} allaqachon mavjud.")
        else:
            # Foydalanuvchini bazaga qo'shish
            user_db.add_user(user_info['user_id'], user_info['username'])
            print(f"Foydalanuvchi {message.from_user.full_name} ro'yxatga olindi.")

            # Foydalanuvchini bazaga qo'shganidan so'ng, adminga xabar yuborish
            users_count = user_db.count_users()
            await notify_admin(message.from_user.full_name, message.from_user.id, users_count, dp.bot)
    except Exception as e:
        print(f"Xatolik: {e}")

    # Salomlashish stikeri va xush kelibsiz xabarini yuborish
    await message.answer_sticker(
        "CAACAgEAAxkBAcIs8meL4ha6zipaYRyZoyD_2pRwHd1rAALOAgACBkQYRM-YkXjyXK5oNgQ")  # Salomlashish stikeri
    await message.answer(
        f"<b>Assalomu alaykum, {message.from_user.full_name}!</b>\n<i>Valyuta botiga xush kelibsiz!</i>",
        reply_markup=start_knopka,
        parse_mode=ParseMode.HTML
    )


# Valyuta kurslarini ko'rsatish
@dp.message_handler(text="💱 Valyuta kurslari")
async def show_currency_rates(message: types.Message):
    rates = await get_currency_rate()
    if rates:
        text = "<b>📊 <u>Valyuta kurslari</u>:</b>\n\n"

        for currency in ["USD", "EUR", "RUB", "GBP"]:
            rate = rates.get(currency)
            if rate:
                text += f"💵 1 <b>{currency}</b> = <i>{rate:.2f}</i> so'm\n"

        # Qo'shimcha ma'lumotlar va eng so'nggi yangiliklar
        text += "\n<b>💡 Kurslar har soatda yangilanadi.</b>\n"
        text += "<b>⚠️ Diqqat! Kurslar o'zgarishi mumkin.</b>\n\n"


        await message.answer(text, parse_mode="HTML")
    else:
        await message.answer(
            "⚠️ <b>Valyuta kurslarini olishda xatolik yuz berdi. Iltimos, keyinroq qayta urinib ko'ring.</b>",
            parse_mode="HTML")


# Konvertatsiya qilish uchun valyutani tanlash
@dp.message_handler(text="♻️ Konvertatsiya qilish")
async def choose_conversion(message: types.Message):
    await message.answer("🔄 <b>Konvertatsiya qilish uchun valyutani tanlang:</b>", reply_markup=menu, parse_mode="HTML")

# Valyuta konvertatsiyasi uchun callback
@dp.callback_query_handler(lambda callback: callback.data.startswith('som_to_') or callback.data.startswith('usd_to_') or callback.data.startswith('eur_to_') or callback.data.startswith('rub_to_') or callback.data.startswith('gbp_to_'))
async def convert_currency(callback: types.CallbackQuery):
    try:
        conversion_type = callback.data.split("_to_")
        from_currency, to_currency = conversion_type[0].upper(), conversion_type[1].upper()
        selected_currency[callback.from_user.id] = {"from": from_currency, "to": to_currency, "threshold": 0.1}

        if from_currency == "SOM":
            await callback.message.answer(
                f"💰 <b>So'mdan {to_currency} ga konvertatsiya qilish uchun miqdorni kiriting:</b>\n\n"
                "⚠️ <b>Foydalanuvchi, iltimos, faqat sonlar kiriting!</b> Masalan, 1000 yoki 10.5 kabi.",
                parse_mode="HTML"
            )

        else:
            await callback.message.answer(
                f"💰 <b>{from_currency} dan So'mga konvertatsiya qilish uchun miqdorni kiriting:</b>\n\n"
                "⚠️ <b>Foydalanuvchi, iltimos, faqat sonlar kiriting!</b> Masalan, 1000 yoki 10.5 kabi.",
                parse_mode="HTML"
            )

        await callback.answer()
    except Exception as e:
        print(f"Xatolik: {e}")
        await callback.message.answer("⚠️ <b>Xatolik yuz berdi. Qayta urinib ko'ring.</b>", parse_mode="HTML")


# Mavjud valyutalar bo'yicha konvertatsiya qilish
@dp.message_handler(lambda message: message.text.replace(',', '.', 1).isdigit() or ('.' in message.text and message.text.count('.') == 1) or (',' in message.text and message.text.count(',') == 1))
async def handle_conversion(message: types.Message):
    try:
        # Kiritilgan qiymatni tekshirish va to'g'ri formatga o'tkazish
        amount_text = message.text.replace(',', '.', 1)

        # Decimal tipiga o'tkazish
        try:
            amount = Decimal(amount_text)
        except:
            # Agar Decimal'ga aylantirishda xatolik yuz bersa, ogohlantirish yuborish
            await message.answer("⚠️ <b>Foydalanuvchi, iltimos, faqat sonlarni kiriting!</b>", parse_mode="HTML")
            return

        # Musbat son ekanligini tekshirish
        if amount <= 0:
            await message.answer("⚠️ <b>Qiymat musbat bo'lishi kerak!</b>", parse_mode="HTML")
            return

        user_id = message.from_user.id
        currency_pair = selected_currency.get(user_id)

        if not currency_pair:
            await message.answer("⚠️ <b>Iltimos, avval valyutani tanlang!</b>", parse_mode="HTML")
            return

        from_currency, to_currency = currency_pair["from"], currency_pair["to"]
        rates = await get_currency_rate()

        if from_currency == "SOM":
            rate = rates.get(to_currency)
            if rate:
                result = amount / rate
                await message.answer(f"✅ <b>{amount}</b> so'm = <i>{result:.2f}</i> {to_currency}", parse_mode="HTML")
        else:
            rate = rates.get(from_currency)
            if rate:
                result = amount * rate
                await message.answer(f"✅ <b>{amount}</b> {from_currency} = <i>{result:.2f}</i> so'm", parse_mode="HTML")
    except Exception as e:
        print(f"Xatolik: {e}")
        await message.answer("⚠️ <b>Hisoblashda xatolik yuz berdi. Iltimos, faqat raqamlar kiriting.</b>", parse_mode="HTML")


@dp.message_handler(lambda message: not (message.text.replace(',', '.', 1).isdigit() or ('.' in message.text and message.text.count('.') == 1) or (',' in message.text and message.text.count(',', 1) == 1)) and message.text.lower() != '/reklama')
async def handle_invalid_input(message: types.Message):
    await message.answer("⚠️ <b>Foydalanuvchi, iltimos, kerakli bo'limlar orqali ishlang </b>", parse_mode="HTML")




# Asinxron ravishda kurs yangilanishlarini boshlash
async def on_start():
    # Kurs yangilanishini tekshirib yuborish uchun birinchi marta ishlatamiz
    await get_currency_rate()

