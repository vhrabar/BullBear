from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import InstrumentViewSet, InstrumentIntervalDataViewSet, PortfolioHoldingViewSet

router = DefaultRouter()
router.register(r'instruments', InstrumentViewSet)
router.register(r'instrument-data', InstrumentIntervalDataViewSet)
router.register(r'portfolio-holdings', PortfolioHoldingViewSet, basename='portfolio-holdings')

urlpatterns = [
    path('', include(router.urls)),
]
