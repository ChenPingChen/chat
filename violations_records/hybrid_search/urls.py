from django.urls import path
from .views import HybridSearchView

app_name = 'hybrid_search'

urlpatterns = [
    path('hybrid/', HybridSearchView.as_view(), name='hybrid_search'),
]