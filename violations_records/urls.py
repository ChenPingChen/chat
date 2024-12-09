from django.urls import path, include

app_name = 'violations_records'

urlpatterns = [
    path('violation/', include('violations_records.data_manager.urls', namespace='data_manager')),
    path('search/', include('violations_records.hybrid_search.urls', namespace='hybrid_search')),
]