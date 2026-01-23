from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FundViewSet, FundSubscriptionViewSet

router = DefaultRouter()
router.register(r'funds', FundViewSet, basename='fund')
router.register(r'subscriptions', FundSubscriptionViewSet, basename='fundsubscription')

urlpatterns = [
    path('', include(router.urls)),
]
