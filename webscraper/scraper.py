from typing import List, Dict
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin

PRICE_RE = re.compile(r'(\d[\d\s.,]*)(\s?(?:₸|KZT|₽|USD|\$|€|EUR)?)', re.I)
YEAR_RE = re.compile(r'\b(19|20)\d{2}\b')

def extract_from_soup(soup, base_url=None):
    """Heuristics: title, price, sku, images, year"""
    item = {}
    # title
    h1 = soup.find('h1')
    if h1:
        item['title'] = h1.get_text(strip=True)
    else:
        title_tag = soup.find('title')
        if title_tag:
            item['title'] = title_tag.get_text(strip=True)

    text = soup.get_text(' ', strip=True)

    # price
    m = PRICE_RE.search(text)
    if m:
        item['price'] = m.group(1).strip() + (m.group(2) or '')

    # sku heuristics - look for patterns like SKU: 12345 or артикул
    sku = None
    sku_tag = soup.find(text=re.compile(r'(SKU|Артикул|арт\.)', re.I))
    if sku_tag:
        # try to capture nearby number
        match = re.search(r'((SKU|Артикул|арт\.)[:\s]*)([A-Za-z0-9\-_/]+)', sku_tag, re.I)
        if match:
            sku = match.group(3)
    if not sku:
        # search anywhere for "Артикул 12345" text
        msku = re.search(r'(?:Артикул|арт\.|SKU)[:\s]*([A-Za-z0-9\-_/]+)', text, re.I)
        if msku:
            sku = msku.group(1)
    if sku:
        item['sku'] = sku

    # year
    y = YEAR_RE.search(text)
    if y:
        item['year'] = y.group(0)

    # images: first few <img> src
    imgs = []
    for img in soup.find_all('img')[:10]:
        src = img.get('data-src') or img.get('src') or img.get('data-original')
        if src:
            if base_url:
                src = urljoin(base_url, src)
            imgs.append(src)
    if imgs:
        item['images'] = imgs

    return item

def parse_html(html, base_url=None, wanted_fields=None):
    soup = BeautifulSoup(html, 'lxml')
    # First try JSON-LD? (if heavy, skip)
    # heuristics for multiple product cards: look for repeat blocks
    # find candidate product blocks
    candidates = soup.find_all(['article','div','li'], recursive=True)
    # choose blocks with images and text
    product_blocks = []
    for c in candidates:
        if c.find('img') and len(c.get_text(strip=True)) > 20:
            product_blocks.append(c)
        if len(product_blocks) >= 15:
            break

    if product_blocks:
        items = []
        for b in product_blocks[:20]:
            item = extract_from_soup(b, base_url)
            if item:
                items.append(item)
        if items:
            return items

    # fallback single page
    item = extract_from_soup(soup, base_url)
    return [item] if item else []

def scrape_url(url: str, wanted_fields: List[str]=None, timeout_seconds: int = 30) -> List[Dict]:
    """
    Sync function: renders page with Playwright and parses content.
    Returns list of dict items.
    """
    wanted_fields = wanted_fields or []
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, timeout=timeout_seconds * 1000, wait_until='networkidle')
            html = page.content()
            base_url = url
            browser.close()
    except PlaywrightTimeout as e:
        # try a simple requests fallback
        import httpx
        r = httpx.get(url, timeout=10)
        html = r.text
        base_url = url
    except Exception as e:
        # raise to be handled by caller
        raise

    items = parse_html(html, base_url=base_url, wanted_fields=wanted_fields)
    return items
