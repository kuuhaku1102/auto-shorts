from ranking_scraper import get_top5
from detail_scraper import get_card_name

def run(mode, label):
    print(f"\n=== {label} ===")

    cards = get_top5(mode)

    for card in cards:
        name = get_card_name(card["detail_url"])

        print({
            "rank": card["rank"],
            "name": name,
            "price": card["price"],
            "change_rate_7d": card["change_rate"]
        })

if __name__ == "__main__":
    run(5, "7日高騰TOP5")
    run(6, "7日下落TOP5")
