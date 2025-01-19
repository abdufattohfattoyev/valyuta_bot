import sqlite3
from datetime import datetime

from loader import user_db


def create_rates_cache_table():
    """Rates cache jadvalini yaratish"""
    conn = sqlite3.connect("data/currency_bot.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS rates_cache (
            currency TEXT PRIMARY KEY,
            rate REAL NOT NULL,
            updated_at DATETIME NOT NULL
        )
    """)

    conn.commit()
    conn.close()

def update_cache(rates):
    """Keshni yangilash yoki qo'shish"""
    conn = sqlite3.connect("currency_bot.db")
    cursor = conn.cursor()

    for currency, rate in rates.items():
        cursor.execute("""
            INSERT OR REPLACE INTO rates_cache (currency, rate, updated_at)
            VALUES (?, ?, ?)
        """, (currency, rate, datetime.now()))

    conn.commit()
    conn.close()

def get_cached_rates():
    """Keshdan ma'lumotni olish"""
    conn = sqlite3.connect("data/currency_bot.db")
    cursor = conn.cursor()

    cursor.execute("SELECT currency, rate FROM rates_cache")
    rates = {row[0]: row[1] for row in cursor.fetchall()}

    conn.close()
    return rates

def init_currency_cache():
    sql = """
        CREATE TABLE IF NOT EXISTS rates_cache(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            currency_name VARCHAR(255),
            exchange_rate DECIMAL(10, 4),
            updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
    """
    user_db.execute(sql, commit=True)
    # Valyuta ma'lumotlarini kiritish yoki yangilash uchun kodlar

