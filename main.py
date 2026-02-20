from ranking_scraper import get_top5
from detail_scraper import get_card_name

from db.database import init_db, insert_record
from utils import clean_price, clean_rate


def run(mode, label):
    print(f"\n=== {label} ===")

    cards = get_top5(mode)

    for card in cards:
        name = get_card_name(card["detail_url"])

        price = clean_price(card["price"])
        rate = clean_rate(card["change_rate"])

        data = {
            "rank": card["rank"],
            "name": name,
            "price": price,
            "change_rate": rate,
            "detail_url": card["detail_url"]
        }

        print(data)

        insert_record(mode, data)


if __name__ == "__main__":
    init_db()
    run(5, "7日高騰TOP5")
    run(6, "7日下落TOP5")
