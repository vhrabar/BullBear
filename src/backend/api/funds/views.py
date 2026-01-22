from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Fund, FundSubscription
from .serializers import FundSerializer, FundSubscriptionSerializer


class FundViewSet(viewsets.ModelViewSet):
    queryset = Fund.objects.all()
    serializer_class = FundSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Fund.objects.filter(creator_portfolio__user=self.request.user.profile)


class FundSubscriptionViewSet(viewsets.ModelViewSet):
    queryset = FundSubscription.objects.all()
    serializer_class = FundSubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return FundSubscription.objects.filter(subscriber_portfolio__user=self.request.user.profile)

    @action(
        detail=False,
        methods=["get"],
        url_path="unsubscribed",
        permission_classes=[IsAuthenticated],
    )
    def unsubscribed(self, request):
        """
        list fonds to which user in not subscribed
        GET /api/funds/unsubscribed
        """

        subscribed_fund_ids = FundSubscription.objects.filter(
            subscriber_portfolio__user=request.user.profile
        ).values_list("fund__id", flat=True)
        user_funds_id = Fund.objects.filter(
            creator_portfolio__user=request.user.profile
        ).values_list("id", flat=True)
        unsubscribed_funds = Fund.objects.exclude(id__in=subscribed_fund_ids).exclude(id__in=user_funds_id)

        serializer = FundSerializer(unsubscribed_funds, many=True)
        return Response(serializer.data)



