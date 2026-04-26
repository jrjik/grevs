from django.urls import path
from .views import submit_lead, submit_callback

urlpatterns = [
    path('lead/', submit_lead, name='api_lead'),
    path('callback/', submit_callback, name='submit_callback'),  
]
