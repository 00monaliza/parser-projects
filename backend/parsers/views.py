from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .forms import ScrapingForm
from .scraper_logic import run_scraper_logic  

def scraping_view(request):
    if request.method == 'POST':
        form = ScrapingForm(request.POST)
        if form.is_valid():
            url = form.cleaned_data['url']
            fields_to_scrape = [f.strip() for f in form.cleaned_data['fields_to_scrape'].split(',')]

            try:
                # Call the core scraping logic with user's inputs
                result = run_scraper_logic(url, fields_to_scrape)
                return JsonResponse({
                    'status': 'success',
                    'message': f"Парсинг {url} завершен. Сохранено {result['records_count']} записей.",
                    'filePath': result['file_path']
                })
            except Exception as e:
                # Handle any errors during the scraping process
                return JsonResponse({
                    'status': 'error',
                    'message': f"Произошла ошибка при парсинге: {str(e)}",
                    'filePath': None
                }, status=500)
        else:
            return JsonResponse({'status': 'error', 'message': 'Неверные данные формы.'}, status=400)
    else:
        form = ScrapingForm()
        return render(request, 'parsers/templates/index.html', {'form': form})
