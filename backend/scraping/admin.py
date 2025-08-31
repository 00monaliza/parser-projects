from django.contrib import admin
from .models import ScrapeJob, ScrapeResult

@admin.register(ScrapeJob)
class ScrapeJobAdmin(admin.ModelAdmin):
    list_display = ('id','url','status','created_at','updated_at')
    readonly_fields = ('created_at','updated_at')

@admin.register(ScrapeResult)
class ScrapeResultAdmin(admin.ModelAdmin):
    list_display = ('id','job','created_at')
    readonly_fields = ('created_at',)
