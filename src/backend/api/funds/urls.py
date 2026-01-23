from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FundViewSet, FundSubscriptionViewSet, FundCommentViewSet

router = DefaultRouter()
router.register(r'funds', FundViewSet, basename='fund')
router.register(r'subscriptions', FundSubscriptionViewSet, basename='fundsubscription')
router.register(r'comments', FundCommentViewSet, basename='fundcomment')

urlpatterns = [
    path('', include(router.urls)),
]
