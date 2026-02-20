from playwright.sync_api import sync_playwright

def get_card_name(detail_url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(detail_url)

        page.wait_for_selector("h1")

        name = page.locator("h1").inner_text().strip()

        browser.close()
        return name
