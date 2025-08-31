from django.urls import path
from . import views

urlpatterns = [
    path('', views.scraping_view, name='scraping'),
]