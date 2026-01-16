from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import OrderViewSet, OrderFillViewSet, OrderEventViewSet

router = DefaultRouter()
router.register(r"orders", OrderViewSet, basename="orders")
router.register(r"order-fills", OrderFillViewSet, basename="order-fills")
router.register(r"order-events", OrderEventViewSet, basename="order-events")

urlpatterns = [
    path("", include(router.urls)),
]
