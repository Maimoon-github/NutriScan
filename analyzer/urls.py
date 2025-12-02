# Endpoint definitions

from django.urls import path
from . import views

app_name = 'analyzer'

urlpatterns = [
    # Frontend routes
    path('', views.HomeView.as_view(), name='home'),
    path('upload/', views.UploadView.as_view(), name='upload'),
    path('results/<str:analysis_id>/', views.ResultsView.as_view(), name='results'),
    path('results/<str:analysis_id>/', views.ResultsView.as_view(), name='result'),
    path('history/', views.HistoryView.as_view(), name='history'),
    
    # API routes
    path('api/v1/scan/', views.ScanAnalyzeView.as_view(), name='scan-analyze'),
]
