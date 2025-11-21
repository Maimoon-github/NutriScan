# Endpoint definitions (e.g., /scan)

from django.urls import path
from .views import ScanAnalyzeView

urlpatterns = [
    path('scan/', ScanAnalyzeView.as_view(), name='scan-analyze'),
]