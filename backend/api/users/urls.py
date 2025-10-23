from django.urls import path
from .views import api_auth

urlpatterns = [
    path('auth', api_auth, name='api-auth'),
]
