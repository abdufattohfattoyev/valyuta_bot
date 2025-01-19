from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

# Inline tugmalarni yaratish (chiroyli dizayn bilan)
menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="🇺🇿 So'm ➡️ 🇺🇸 USD", callback_data='som_to_usd'),
            InlineKeyboardButton(text="🇺🇸 USD ➡️ 🇺🇿 So'm", callback_data='usd_to_som'),
        ],
        [
            InlineKeyboardButton(text="🇺🇿 So'm ➡️ 🇪🇺 EUR", callback_data='som_to_eur'),
            InlineKeyboardButton(text="🇪🇺 EUR ➡️ 🇺🇿 So'm", callback_data='eur_to_som'),
        ],
        [
            InlineKeyboardButton(text="🇺🇿 So'm ➡️ 🇷🇺 RUB", callback_data='som_to_rub'),
            InlineKeyboardButton(text="🇷🇺 RUB ➡️ 🇺🇿 So'm", callback_data='rub_to_som'),
        ],
        [
            InlineKeyboardButton(text="🇺🇿 So'm ➡️ 🇬🇧 GBP", callback_data='som_to_gbp'),
            InlineKeyboardButton(text="🇬🇧 GBP ➡️ 🇺🇿 So'm", callback_data='gbp_to_som'),
        ]
    ]
)
