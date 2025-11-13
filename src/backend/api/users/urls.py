from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserPortfolioViewSet

router = DefaultRouter()
router.register(r'portofolio-details', UserPortfolioViewSet, basename='portfolio-details')

urlpatterns = [
    path('', include(router.urls)),
    path('', include('dj_rest_auth.urls')),
    path('registration/', include('dj_rest_auth.registration.urls')),
    path('', include('allauth.socialaccount.urls')),

]
