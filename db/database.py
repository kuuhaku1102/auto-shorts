import sqlite3
import os
from datetime import datetime
from zoneinfo import ZoneInfo

DB_PATH = "state/prices.db"


def get_today_jst():
    """JSTの日付を取得"""
    return datetime.now(ZoneInfo("Asia/Tokyo")).strftime("%Y-%m-%d")


def init_db():
    """DBとテーブル初期化"""
    os.makedirs("state", exist_ok=True)

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
        detail_url TEXT,
        UNIQUE(date, mode, rank)   -- 同日・同モード・同順位は重複不可
    )
    """)

    conn.commit()
    conn.close()


def insert_record(mode, card):
    """レコード挿入（重複は無視）"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    INSERT OR IGNORE INTO prices
    (date, mode, rank, name, price, change_rate, detail_url)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        get_today_jst(),
        mode,
        card["rank"],
        card["name"],
        card["price"],
        card["change_rate"],
        card["detail_url"]
    ))

    conn.commit()
    conn.close()


def show_all():
    """全レコード表示"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM prices ORDER BY id DESC")
    rows = cursor.fetchall()

    print("\n=== DB保存内容 ===")
    for row in rows:
        print(row)

    conn.close()
def get_yesterday_price(name):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    SELECT price
    FROM prices
    WHERE name = ?
      AND date = (
          SELECT date FROM prices
          WHERE name = ?
          ORDER BY date DESC
          LIMIT 1 OFFSET 1
      )
    """, (name, name))

    row = cursor.fetchone()
    conn.close()

    if row:
        return row[0]
    return None

def get_consecutive_days(name, mode):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    SELECT COUNT(*)
    FROM prices
    WHERE name = ?
      AND mode = ?
    """, (name, mode))

    count = cursor.fetchone()[0]
    conn.close()
    return count
