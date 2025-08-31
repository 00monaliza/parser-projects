from django.urls import path
from . import views

urlpatterns = [
    path('jobs/', views.JobListCreateAPIView.as_view(), name='jobs'),
    path('jobs/<int:pk>/', views.JobRetrieveAPIView.as_view(), name='job-detail'),
    path('jobs/<int:pk>/results/', views.JobResultsAPIView.as_view(), name='job-results'),
    # (optional) endpoint to download xlsx: views.JobDownloadAPIView
    path('run-sync/', views.run_sync_view, name='run-sync'),  # testing quick call
]
