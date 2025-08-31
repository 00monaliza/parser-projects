from playwright.sync_api import sync_playwright

def parse_with_playwright(url, wait_selector=None):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url)

        # Ждем, пока прогрузится нужный элемент (например, список товаров)
        if wait_selector:
            page.wait_for_selector(wait_selector, timeout=10000)

        html = page.content()
        browser.close()
        return html
