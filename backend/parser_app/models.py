from django.db import models

class ParsedData(models.Model):
    url = models.URLField()
    title = models.CharField(max_length=255, blank=True, null=True)
    price = models.CharField(max_length=50, blank=True, null=True)
    article = models.CharField(max_length=100, blank=True, null=True)
    image_url = models.URLField(blank=True, null=True)
    year = models.CharField(max_length=10, blank=True, null=True)
    raw_html = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title or self.url
