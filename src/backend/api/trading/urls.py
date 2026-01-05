from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import InstrumentViewSet, InstrumentIntervalDataViewSet, PortfolioHoldingViewSet, BuyInstrumentView, \
    SellInstrumentView, LatestInstrumentDataViewSet, InstrumentQuoteViewSet, CompanyViewSet, CompanyNewsViewSet

router = DefaultRouter()
router.register(r'instruments', InstrumentViewSet)
router.register(r'instrument-data', InstrumentIntervalDataViewSet)
router.register(r'latest-instrument-data', LatestInstrumentDataViewSet, basename='latest-instrument-data')
router.register(r'latest-instrument-quote', InstrumentQuoteViewSet, basename='latest-instrument-quote')
router.register(r'portfolio-holdings', PortfolioHoldingViewSet, basename='portfolio-holdings')
router.register(r'companies', CompanyViewSet, basename='company')
router.register(r'news', CompanyNewsViewSet, basename='news')


urlpatterns = [
    path('', include(router.urls)),
    path('buy', BuyInstrumentView.as_view(), name='buy-instrument'),
    path('sell', SellInstrumentView.as_view(), name='sell-instrument'),
]
