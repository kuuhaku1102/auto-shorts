from playwright.sync_api import sync_playwright
import re

BASE_URL = "https://pokeca-chart.com"


def get_top5(mode):
    """
    mode=5 → 高騰順
    mode=6 → 下落順
    """

    url = f"{BASE_URL}/all-card?mode={mode}"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url)

        page.wait_for_selector(".cp_card")

        cards = page.locator(".cp_card").all()

        result = []

        for card in cards:
            # ランク取得（1位など）
            rank_text = card.locator(".category p").inner_text()
            match = re.search(r"\d+", rank_text)

            if not match:
                continue

            rank_number = int(match.group())

            # 1位〜5位のみ
            if not (1 <= rank_number <= 5):
                continue

            # 価格
            price = card.locator(".text_right p:nth-child(1)").inner_text()

            # 7日騰落率
            change_rate = card.locator(".text_right p:nth-child(3)").inner_text()

            # 詳細URL
            detail_url = card.locator("a").get_attribute("href")

            # 画像URL（動画用）
            image_url = card.locator(".photo img").get_attribute("src")

            # URLが相対パスの可能性を考慮
            if detail_url and detail_url.startswith("/"):
                detail_url = BASE_URL + detail_url

            if image_url and image_url.startswith("/"):
                image_url = BASE_URL + image_url

            result.append({
                "rank": rank_number,
                "price": price.replace("：", "").strip(),
                "change_rate": change_rate.replace("：", "").strip(),
                "detail_url": detail_url,
                "image_url": image_url
            })

        browser.close()

        # rank順にソート
        return sorted(result, key=lambda x: x["rank"])
