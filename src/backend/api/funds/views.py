from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from .models import Fund, FundSubscription, FundNAVHistory, FundComment
from .serializers import FundSerializer, FundSubscriptionSerializer, FundNAVHistorySerializer, FundCommentSerializer


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
        # Get all portfolios belonging to this user
        user_portfolios = self.request.user.profile.portfolios.all()
        return FundSubscription.objects.filter(
            subscriber_portfolio__in=user_portfolios,
            fund__is_active=True
        ).select_related('fund')

    def list(self, request, *args, **kwargs):
        """
        List all subscriptions for the current user
        GET /api/funds/subscriptions/
        """
        # Debug: print all subscriptions for this user's profile
        all_subs = FundSubscription.objects.all()
        print(f"DEBUG: Total subscriptions in DB: {all_subs.count()}")

        user_profile = request.user.profile
        print(f"DEBUG: User profile: {user_profile}")

        user_portfolios = user_profile.portfolios.all()
        print(f"DEBUG: User portfolios: {list(user_portfolios.values_list('id', 'name'))}")

        queryset = self.get_queryset()
        print(f"DEBUG: Filtered subscriptions count: {queryset.count()}")

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(
        detail=False,
        methods=["get"],
        url_path="unsubscribed",
        permission_classes=[IsAuthenticated],
    )
    def unsubscribed(self, request):
        """
        list active funds to which user is not subscribed and does not own
        GET /api/funds/subscriptions/unsubscribed/
        """
        user_portfolios = request.user.profile.portfolios.all()

        subscribed_fund_ids = FundSubscription.objects.filter(
            subscriber_portfolio__in=user_portfolios
        ).values_list("fund__id", flat=True)
        user_funds_id = Fund.objects.filter(
            creator_portfolio__in=user_portfolios
        ).values_list("id", flat=True)
        unsubscribed_funds = Fund.objects.filter(is_active=True).exclude(id__in=subscribed_fund_ids).exclude(id__in=user_funds_id)

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
        user_portfolios = request.user.profile.portfolios.all()
        subscription = FundSubscription.objects.filter(
            subscriber_portfolio__in=user_portfolios,
            fund_id=fund_id
        ).first()

        if subscription:
            serializer = FundSubscriptionSerializer(subscription)
            return Response(serializer.data)
        return Response({"detail": "Subscription not found."}, status=404)


class FundCommentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for CRUD operations on fund comments.
    """
    queryset = FundComment.objects.all()
    serializer_class = FundCommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Optionally filter by fund_id query parameter.
        """
        queryset = FundComment.objects.all()
        fund_id = self.request.query_params.get('fund_id', None)
        if fund_id is not None:
            queryset = queryset.filter(fund_id=fund_id)
        return queryset

    def perform_create(self, serializer):
        """
        Set the user automatically when creating a comment.
        """
        serializer.save(user=self.request.user)

    def update(self, request, *args, **kwargs):
        """
        Only allow users to update their own comments.
        """
        comment = self.get_object()
        if comment.user != request.user:
            return Response({"detail": "You can only edit your own comments."}, status=403)
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """
        Only allow users to delete their own comments.
        """
        comment = self.get_object()
        if comment.user != request.user:
            return Response({"detail": "You can only delete your own comments."}, status=403)
        return super().destroy(request, *args, **kwargs)

    @action(
        detail=False,
        methods=["get"],
        url_path="by-fund/(?P<fund_id>[^/.]+)",
        permission_classes=[IsAuthenticated],
    )
    def by_fund(self, request, fund_id=None):
        """
        Get all comments for a specific fund.
        GET /api/funds/comments/by-fund/{fund_id}/
        """
        comments = FundComment.objects.filter(fund_id=fund_id).order_by('-created_at')
        serializer = FundCommentSerializer(comments, many=True)
        return Response(serializer.data)

