import requests
from bs4 import BeautifulSoup
import pandas as pd
from django.core.management.base import BaseCommand
from parser_app.models import ParsedData

class Command(BaseCommand):
    help = "Парсит сайт и сохраняет данные в БД + XLSX/CSV/JSON"

    def add_arguments(self, parser):
        parser.add_argument("url", type=str, help="URL для парсинга")
        parser.add_argument("--format", type=str, choices=["xlsx", "csv", "json"], default="xlsx",
                            help="Формат выгрузки (xlsx, csv, json)")

    def handle(self, *args, **options):
        url = options["url"]
        export_format = options["format"]

        self.stdout.write(self.style.SUCCESS(f"Парсим: {url}"))

        try:
            response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
            response.raise_for_status()
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Ошибка при запросе: {e}"))
            return

        soup = BeautifulSoup(response.text, "html.parser")

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
            raw_html=response.text[:2000]  # для отладки сохраняем кусок
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

        if export_format == "xlsx":
            df.to_excel("parsed_data.xlsx", index=False)
            self.stdout.write(self.style.SUCCESS("Экспортировано в parsed_data.xlsx"))
        elif export_format == "csv":
            df.to_csv("parsed_data.csv", index=False)
            self.stdout.write(self.style.SUCCESS("Экспортировано в parsed_data.csv"))
        elif export_format == "json":
            df.to_json("parsed_data.json", orient="records", force_ascii=False, indent=2)
            self.stdout.write(self.style.SUCCESS("Экспортировано в parsed_data.json"))
