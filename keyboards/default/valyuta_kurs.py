from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# Tugmalarni yaratish (emojilar bilan chiroyli dizayn)
start_knopka = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="💱 Valyuta kurslari"),
            KeyboardButton(text="♻️ Konvertatsiya qilish"),
        ],


    ],
    resize_keyboard=True
)
