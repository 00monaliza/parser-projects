from playwright.async_api import async_playwright

async def run_playwright():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto("https://quotes.toscrape.com/")
        title = await page.title()
        await browser.close()
        return f"Заголовок страницы: {title}"
