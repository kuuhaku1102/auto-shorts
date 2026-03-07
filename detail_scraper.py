from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
import time

BLOCK_WORD = "申し訳ございません"


def get_card_name(detail_url, retries=3):
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

        last_error = None
        for attempt in range(1, retries + 1):
            try:
                page.goto(detail_url, wait_until="domcontentloaded", timeout=60000)
                page.wait_for_selector("h1", timeout=45000)
                name = page.locator("h1").inner_text().strip()

                if BLOCK_WORD in name:
                    raise RuntimeError("アクセス制限ページが返されました")

                context.close()
                browser.close()
                return name
            except (PlaywrightTimeoutError, RuntimeError) as exc:
                last_error = exc
                if attempt < retries:
                    time.sleep(attempt)

        context.close()
        browser.close()
        raise RuntimeError(f"カード詳細ページの取得に失敗しました: {detail_url}") from last_error
