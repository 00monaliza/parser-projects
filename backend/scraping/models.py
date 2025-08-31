from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.utils import timezone
import json

# If ArrayField isn't available on sqlite, use JSONField fallback
try:
    from django.contrib.postgres.fields import ArrayField
except Exception:
    ArrayField = None

class ScrapeJob(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('done', 'Done'),
        ('failed', 'Failed'),
    )
    url = models.URLField()
    fields = models.JSONField(default=list)  # e.g. ["title","price","sku","images"]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    meta = models.JSONField(default=dict, blank=True)  # store errors, count etc
    result_file = models.FileField(upload_to='results/', null=True, blank=True)

    def __str__(self):
        return f"Job {self.id} {self.url} [{self.status}]"

class ScrapeResult(models.Model):
    job = models.ForeignKey(ScrapeJob, on_delete=models.CASCADE, related_name='results')
    data = models.JSONField(default=dict)  # one item per result
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Result {self.id} for Job {self.job_id}"
