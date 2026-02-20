from playwright.sync_api import sync_playwright
import re

BASE_URL = "https://pokeca-chart.com"

def get_top5(mode):
    url = f"{BASE_URL}/all-card?mode={mode}"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url)

        page.wait_for_selector(".cp_card")

        cards = page.locator(".cp_card").all()

        result = []

        for card in cards:
            rank_text = card.locator(".category p").inner_text()
            rank_number = int(re.search(r"\d+", rank_text).group())

            if 1 <= rank_number <= 5:
                price = card.locator(".text_right p:nth-child(1)").inner_text()
                change_rate = card.locator(".text_right p:nth-child(3)").inner_text()
                detail_url = card.locator("a").get_attribute("href")

                result.append({
                    "rank": rank_number,
                    "price": price.replace("：", "").strip(),
                    "change_rate": change_rate.replace("：", "").strip(),
                    "detail_url": detail_url
                })

        browser.close()

        return sorted(result, key=lambda x: x["rank"])
