import requests
from bs4 import BeautifulSoup
import pandas as pd
from django.core.management.base import BaseCommand
from parser_app.models import ParsedData
from parsers.playwright_parser import parse_with_playwright
from urllib.parse import urlparse  

class Command(BaseCommand):
    help = "Парсит сайт и сохраняет данные в БД + XLSX/CSV/JSON"

    def add_arguments(self, parser):
        parser.add_argument("url", type=str, help="URL для парсинга")
        parser.add_argument("--format", type=str, choices=["xlsx", "csv", "json"], default="xlsx",
                            help="Формат выгрузки (xlsx, csv, json)")
        parser.add_argument("--dynamic", action="store_true", help="Использовать Playwright для парсинга динамических сайтов")

    def handle(self, *args, **options):
        url = options["url"]
        export_format = options["format"]
        use_dynamic = options["dynamic"]

        self.stdout.write(self.style.SUCCESS(f"Парсим: {url} (dynamic={use_dynamic})"))

        # Если указан --dynamic → используем Playwright
        if use_dynamic:
            try:
                html = parse_with_playwright(url, wait_selector="div")
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Ошибка Playwright: {e}"))
                return
        else:
            try:
                response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, verify=False)
                response.raise_for_status()
                html = response.text
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Ошибка при запросе: {e}"))
                return

        soup = BeautifulSoup(html, "html.parser")

        # Простейшая логика авто-определения
        title = soup.find("h1")
        if not title:
            title = soup.find("title")
        title = title.get_text(strip=True) if title else None

        price = None
        for tag in soup.find_all(["span", "div"]):
            if tag.get_text().strip().lower().startswith(("price", "цена")):
                price = tag.get_text(strip=True)
                break

        image = None
        img_tag = soup.find("img")
        if img_tag and img_tag.get("src"):
            image = img_tag["src"]

        # Сохраняем в БД
        parsed = ParsedData.objects.create(
            url=url,
            title=title,
            price=price,
            image_url=image,
            raw_html=html[:2000]
        )

        self.stdout.write(self.style.SUCCESS(f"Сохранено: {parsed.id} — {parsed.title}"))

        # Экспортируем
        data = [{
            "url": url,
            "title": title,
            "price": price,
            "image_url": image
        }]

        df = pd.DataFrame(data)

        # Получаем домен и формируем имя файла
        parsed_url = urlparse(url)
        domain = parsed_url.netloc.replace('.', '_')
        filename = f"{domain}.{export_format}"

        if export_format == "xlsx":
            df.to_excel(filename, index=False)
            self.stdout.write(self.style.SUCCESS(f"Экспортировано в {filename}"))
        elif export_format == "csv":
            df.to_csv(filename, index=False)
            self.stdout.write(self.style.SUCCESS(f"Экспортировано в {filename}"))
        elif export_format == "json":
            df.to_json(filename, orient="records", force_ascii=False, indent=2)
            self.stdout.write(self.style.SUCCESS(f"Экспортировано в {filename}"))