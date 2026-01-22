from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserPortfolioViewSet, UserProfileViewSet, ContactViewSet, PortfolioSnapshotViewSet

router = DefaultRouter()
router.register(r'portofolio-details', UserPortfolioViewSet, basename='portfolio-details')
router.register(r'user-profile', UserProfileViewSet, basename='user-profile')
router.register(r"contact", ContactViewSet, basename="contact")
router.register(r"snapshots", PortfolioSnapshotViewSet, basename="snapshots")


urlpatterns = [
    path('', include(router.urls)),
    path('', include('dj_rest_auth.urls')),
    path('registration/', include('dj_rest_auth.registration.urls')),
    path('', include('allauth.socialaccount.urls')),

]
