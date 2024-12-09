from django.urls import path
from . import views

urlpatterns = [
    path('data-manager/', views.process_violation_data, name='process_violation'),
    path('data-manager/batch/', views.batch_process_violations, name='batch_process_violations'),
]
