from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import InstrumentViewSet, InstrumentIntervalDataViewSet, PortfolioHoldingViewSet, BuyInstrumentView, \
    SellInstrumentView, LatestInstrumentDataViewSet

router = DefaultRouter()
router.register(r'instruments', InstrumentViewSet)
router.register(r'instrument-data', InstrumentIntervalDataViewSet)
router.register(r'latest-instrument-data', LatestInstrumentDataViewSet, basename='latest-instrument-data')
router.register(r'portfolio-holdings', PortfolioHoldingViewSet, basename='portfolio-holdings')

urlpatterns = [
    path('', include(router.urls)),
    path('buy', BuyInstrumentView.as_view(), name='buy-instrument'),
    path('sell', SellInstrumentView.as_view(), name='sell-instrument'),
]
