from rest_framework import viewsets, permissions
from .models import Fund, FundSubscription
from .serializers import FundSerializer, FundSubscriptionSerializer


class FundViewSet(viewsets.ModelViewSet):
    queryset = Fund.objects.all()
    serializer_class = FundSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Fund.objects.filter(creator_portfolio__user=self.request.user)


class FundSubscriptionViewSet(viewsets.ModelViewSet):
    queryset = FundSubscription.objects.all()
    serializer_class = FundSubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return FundSubscription.objects.filter(subscriber_portfolio__user=self.request.user)


