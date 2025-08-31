from django.http import JsonResponse
import asyncio
from webscraper.scraper import run_playwright

def run_scraper(request):
    result = asyncio.run(run_playwright())
    return JsonResponse({"result": result})
