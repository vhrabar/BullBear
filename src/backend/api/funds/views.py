from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from .models import Fund, FundSubscription, FundNAVHistory
from .serializers import FundSerializer, FundSubscriptionSerializer, FundNAVHistorySerializer


class FundViewSet(viewsets.ModelViewSet):
    queryset = Fund.objects.all()
    serializer_class = FundSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Fund.objects.filter(creator_portfolio__user=self.request.user.profile)

    def retrieve(self, request, *args, **kwargs):
        """
        Allow retrieving any fund by ID (for viewing/subscribing)
        """
        pk = kwargs.get('pk')
        try:
            fund = Fund.objects.get(pk=pk)
            serializer = self.get_serializer(fund)
            return Response(serializer.data)
        except Fund.DoesNotExist:
            return Response({"detail": "Fund not found."}, status=404)

    @action(
        detail=False,
        methods=["get"],
        url_path="all",
        permission_classes=[IsAuthenticated],
    )
    def all_funds(self, request):
        """
        List all active funds for exploration
        GET /api/funds/funds/all/
        """
        funds = Fund.objects.filter(is_active=True)
        serializer = FundSerializer(funds, many=True)
        return Response(serializer.data)

    @action(
        detail=True,
        methods=["get"],
        url_path="performance",
        permission_classes=[IsAuthenticated],
    )
    def performance(self, request, pk=None):
        """
        Get historical NAV data for a fund (for performance graphs)
        GET /api/funds/funds/{id}/performance/
        Optional query params: ?days=30 (default 30 days)
        """
        from datetime import timedelta
        from django.utils import timezone

        try:
            fund = Fund.objects.get(pk=pk)
        except Fund.DoesNotExist:
            return Response({"detail": "Fund not found."}, status=404)

        days = int(request.query_params.get('days', 30))
        start_date = timezone.now() - timedelta(days=days)

        history = FundNAVHistory.objects.filter(
            fund=fund,
            recorded_at__gte=start_date
        ).order_by('recorded_at')

        serializer = FundNAVHistorySerializer(history, many=True)
        return Response(serializer.data)


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
        list funds to which user is not subscribed
        GET /api/funds/subscriptions/unsubscribed/
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

    @action(
        detail=False,
        methods=["get"],
        url_path="by-fund/(?P<fund_id>[^/.]+)",
        permission_classes=[IsAuthenticated],
    )
    def by_fund(self, request, fund_id=None):
        """
        Get user's subscription for a specific fund
        GET /api/funds/subscriptions/by-fund/{fund_id}/
        """
        subscription = FundSubscription.objects.filter(
            subscriber_portfolio__user=request.user.profile,
            fund_id=fund_id
        ).first()

        if subscription:
            serializer = FundSubscriptionSerializer(subscription)
            return Response(serializer.data)
        return Response({"detail": "Subscription not found."}, status=404)
