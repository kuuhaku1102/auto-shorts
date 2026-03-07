from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
import re
import time

BASE_URL = "https://pokeca-chart.com"
CARD_SELECTOR = ".cp_card"


def _open_ranking_page(page, url, retries=3):
    last_error = None

    for attempt in range(1, retries + 1):
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=60000)
            page.wait_for_load_state("networkidle", timeout=30000)
            page.wait_for_selector(CARD_SELECTOR, state="visible", timeout=45000)
            return
        except PlaywrightTimeoutError as exc:
            last_error = exc

            # アクセス制限やメンテ文言の検知
            body_text = page.locator("body").inner_text(timeout=5000) if page.locator("body").count() else ""
            if "申し訳ございません" in body_text or "アクセス" in body_text:
                time.sleep(2 * attempt)
            else:
                time.sleep(attempt)

            # 最終リトライ以外は再読込
            if attempt < retries:
                page.reload(wait_until="domcontentloaded", timeout=60000)

    raise RuntimeError(f"ランキングページの読込に失敗しました: {url}") from last_error


def get_top5(mode):
    """
    mode=5 → 高騰順
    mode=6 → 下落順
    """

    url = f"{BASE_URL}/all-card?mode={mode}"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            )
        )
        page = context.new_page()

        _open_ranking_page(page, url)

        cards = page.locator(CARD_SELECTOR).all()

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

        context.close()
        browser.close()

        # rank順にソート
        return sorted(result, key=lambda x: x["rank"])
