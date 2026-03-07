from ranking_scraper import get_top5
from detail_scraper import get_card_name
from datetime import datetime
from zoneinfo import ZoneInfo

from db.database import (
    init_db,
    insert_record,
    show_all,
    get_yesterday_price,
    get_consecutive_days
)

from utils import clean_price, clean_rate
from logic.script_builder import build_script
from delivery.slack_notifier import send_to_slack


def run(mode, label):
    print(f"\n=== {label} ===")

    cards = get_top5(mode)
    items = []

    for card in cards:
        try:
            name = get_card_name(card["detail_url"])
        except Exception as exc:
            print(f"カード名取得失敗: {card['detail_url']} ({exc})")
            name = card["detail_url"].rstrip("/").split("/")[-1]

        price = clean_price(card["price"])
        rate = clean_rate(card["change_rate"])

        # 前日価格取得
        yesterday_price = get_yesterday_price(name)
        diff = price - yesterday_price if yesterday_price is not None else None

        # ランクイン回数（現状は出現回数）
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
    date_label = datetime.now(ZoneInfo("Asia/Tokyo")).strftime("%-m月%-d日")
    rising_title = f"{date_label}高騰TOP5"
    falling_title = f"{date_label}下落TOP5"

    # DB初期化
    init_db()

    # データ取得
    rising_items = run(5, rising_title)
    falling_items = run(6, falling_title)

    # 台本生成（ハイブリッド）
    rising_script = build_script(rising_title, rising_items)
    falling_script = build_script(falling_title, falling_items)

    # ログ出力
    print("\n=== 高騰動画台本 ===")
    print(rising_script)

    print("\n=== 下落動画台本 ===")
    print(falling_script)

    # Slack送信（ここが追加）
    try:
        send_to_slack(f"📈 {rising_title} 台本", rising_script, cards=rising_items)
    except Exception as exc:
        print(f"高騰通知の送信に失敗: {exc}")

    try:
        send_to_slack(f"📉 {falling_title} 台本", falling_script, cards=falling_items)
    except Exception as exc:
        print(f"下落通知の送信に失敗: {exc}")

    # DB確認（デバッグ用）
    show_all()
