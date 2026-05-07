from django.urls import path
from .views import get_catalog

urlpatterns = [
    path('api/catalog/', get_catalog, name='api_catalog'),
]
