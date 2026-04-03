from django.urls import path
from .views import submit_lead

urlpatterns = [
    path('lead/', submit_lead, name='api_lead'),
]
