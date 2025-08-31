from rest_framework import serializers
from .models import ScrapeJob, ScrapeResult

class ScrapeResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScrapeResult
        fields = ['id','data','created_at']

class ScrapeJobSerializer(serializers.ModelSerializer):
    results = ScrapeResultSerializer(many=True, read_only=True)
    class Meta:
        model = ScrapeJob
        fields = ['id','url','fields','status','meta','created_at','updated_at','results']
