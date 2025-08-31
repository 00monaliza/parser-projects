from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.conf import settings
from .models import ScrapeJob, ScrapeResult
from .serializers import ScrapeJobSerializer, ScrapeResultSerializer

import threading
from webscraper.scraper import scrape_url  # our scraper function (sync)
from .exporter import export_to_xlsx_bytes  # helper to create xlsx bytes

class JobListCreateAPIView(generics.ListCreateAPIView):
    queryset = ScrapeJob.objects.all().order_by('-created_at')
    serializer_class = ScrapeJobSerializer

    def perform_create(self, serializer):
        job = serializer.save()
        # launch background thread to process job
        t = threading.Thread(target=process_job, args=(job.id,), daemon=True)
        t.start()

def process_job(job_id):
    job = ScrapeJob.objects.get(id=job_id)
    job.status = 'running'
    job.save()
    try:
        items = scrape_url(job.url, wanted_fields=job.fields)
        # items: list of dicts
        for item in items:
            ScrapeResult.objects.create(job=job, data=item)
        # create xlsx bytes and save to FileField
        try:
            buf = export_to_xlsx_bytes(items)
            from django.core.files.base import ContentFile
            job.result_file.save(f'scrape_{job.id}.xlsx', ContentFile(buf.getvalue()))
        except Exception as e:
            job.meta['export_error'] = str(e)
        job.status = 'done'
        job.meta['count'] = len(items)
        job.save()
    except Exception as e:
        job.status = 'failed'
        job.meta['error'] = str(e)
        job.save()
        raise

class JobRetrieveAPIView(generics.RetrieveAPIView):
    queryset = ScrapeJob.objects.all()
    serializer_class = ScrapeJobSerializer

class JobResultsAPIView(APIView):
    def get(self, request, pk):
        job = get_object_or_404(ScrapeJob, id=pk)
        qs = job.results.all().order_by('created_at')
        serializer = ScrapeResultSerializer(qs, many=True)
        return Response(serializer.data)

# small sync test view
from django.http import JsonResponse
def run_sync_view(request):
    url = request.GET.get('url', 'https://example.com')
    items = scrape_url(url, wanted_fields=['title'])
    return JsonResponse({'count': len(items), 'items': items})
