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


def run(mode, label):
    print(f"\n=== {label} ===")

    cards = get_top5(mode)

    for card in cards:
        name = get_card_name(card["detail_url"])

        price = clean_price(card["price"])
        rate = clean_rate(card["change_rate"])

        # 🔥 前日価格取得
        yesterday_price = get_yesterday_price(name)

        if yesterday_price is not None:
            diff = price - yesterday_price
        else:
            diff = None

        # 🔥 連続ランクイン回数
        consecutive = get_consecutive_days(name, mode)

        data = {
            "rank": card["rank"],
            "name": name,
            "price": price,
            "change_rate": rate,
            "diff_from_yesterday": diff,
            "consecutive_days": consecutive,
            "detail_url": card["detail_url"]
        }

        print(data)

        insert_record(mode, data)


if __name__ == "__main__":
    init_db()

    run(5, "7日高騰TOP5")
    run(6, "7日下落TOP5")

    show_all()
