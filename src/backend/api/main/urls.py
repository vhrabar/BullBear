from django.urls import path
from .views import api_main

urlpatterns = [
    path('', api_main, name='api-main'),
]
