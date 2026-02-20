from ranking_scraper import get_top5
from detail_scraper import get_card_name

from db.database import (
    init_db,
    insert_record,
    show_all,
    get_yesterday_price,
    get_consecutive_days
)

from utils import clean_price, clean_rate
from logic.script_builder import build_script


def run(mode, label):
    print(f"\n=== {label} ===")

    cards = get_top5(mode)
    items = []

    for card in cards:
        name = get_card_name(card["detail_url"])

        price = clean_price(card["price"])
        rate = clean_rate(card["change_rate"])

        # 🔥 前日価格取得
        yesterday_price = get_yesterday_price(name)
        diff = price - yesterday_price if yesterday_price is not None else None

        # 🔥 連続ランクイン回数
        consecutive = get_consecutive_days(name, mode)

        data = {
            "rank": card["rank"],
            "name": name,
            "price": price,
            "change_rate": rate,
            "diff_from_yesterday": diff,
            "consecutive_days": consecutive,
            "detail_url": card["detail_url"],
            "image_url": card.get("image_url")
        }

        print(data)

        insert_record(mode, data)
        items.append(data)

    return items


if __name__ == "__main__":
    # DB初期化
    init_db()

    # データ取得
    rising_items = run(5, "7日高騰TOP5")
    falling_items = run(6, "7日下落TOP5")

    # 台本生成（ハイブリッド）
    rising_script = build_script("7日高騰TOP5", rising_items)
    falling_script = build_script("7日下落TOP5", falling_items)

    print("\n=== 高騰動画台本 ===")
    print(rising_script)

    print("\n=== 下落動画台本 ===")
    print(falling_script)

    # DB確認（デバッグ用）
    show_all()
