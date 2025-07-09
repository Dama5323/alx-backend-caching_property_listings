from django.urls import path
from .views import property_list
from .views import property_list, cache_metrics

urlpatterns = [
    path('properties/', property_list, name='property_list'),
    path('cache-metrics/', cache_metrics, name='cache_metrics'),
]
