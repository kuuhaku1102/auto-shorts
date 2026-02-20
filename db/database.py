import sqlite3
from datetime import datetime

DB_PATH = "state/prices.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS prices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        mode INTEGER,
        rank INTEGER,
        name TEXT,
        price INTEGER,
        change_rate REAL,
        detail_url TEXT
    )
    """)

    conn.commit()
    conn.close()

def insert_record(mode, card):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO prices (date, mode, rank, name, price, change_rate, detail_url)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        datetime.now().strftime("%Y-%m-%d"),
        mode,
        card["rank"],
        card["name"],
        card["price"],
        card["change_rate"],   # ← 修正
        card["detail_url"]
    ))

    conn.commit()
    conn.close()
