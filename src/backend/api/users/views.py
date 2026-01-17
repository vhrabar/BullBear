from django.utils.dateparse import parse_datetime
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from .models import UserPortfolio, UserProfile, ContactMessage, PortfolioSnapshot
from .serializers import (
    UserPortofolioSerializer,
    UserProfileSerializer,
    ContactDefaultsSerializer,
    ContactMessageSerializer,
    PortfolioSnapshotSerializer,
)
from ..orders.permissions import IsServiceExecutor
from rest_framework import permissions


class UserPortfolioViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = UserPortofolioSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        profile = self.request.user.profile
        return UserPortfolio.objects.filter(user=profile)


class UserProfileViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UserProfile.objects.filter(user=self.request.user)


class ContactViewSet(viewsets.ViewSet):
    """
    GET  /api/account/contact/ -> list() returns {full_name, email}
    POST /api/account/contact/ -> create() stores ContactMessage
    """
    permission_classes = [permissions.AllowAny]  # can be IsAuthenticated if you want

    def list(self, request):
        defaults = {"full_name": "", "email": ""}

        if request.user.is_authenticated:
            # Full name priority: "First Last" -> username fallback
            full_name = (request.user.get_full_name() or "").strip()
            if not full_name:
                full_name = request.user.username

            defaults["full_name"] = full_name
            defaults["email"] = request.user.email or ""

        serializer = ContactDefaultsSerializer(defaults)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request):
        serializer = ContactMessageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        ip = request.META.get("REMOTE_ADDR")
        ua = request.META.get("HTTP_USER_AGENT", "")

        profile = None
        if request.user.is_authenticated:
            profile = UserProfile.objects.filter(user=request.user).first()

        msg: ContactMessage = serializer.save(
            user=profile,
            ip_address=ip,
            user_agent=ua[:2000],
        )

        return Response(
            {"detail": "Message received.", "id": msg.id},
            status=status.HTTP_201_CREATED,
        )

class PortfolioSnapshotViewSet(viewsets.ModelViewSet):
    """
    - portfolio=<id>
    - from=<iso datetime>
    - to=<iso datetime>
    - order=asc|desc
    - limit=<int>
    """
    serializer_class = PortfolioSnapshotSerializer
    permission_classes = [IsServiceExecutor]

    def get_queryset(self):
        user = self.request.user

        if not hasattr(user, "profile"):
            return PortfolioSnapshot.objects.none()

        qs = PortfolioSnapshot.objects.filter(portfolio__user=user.profile)

        portfolio_id = self.request.query_params.get("portfolio")
        if portfolio_id:
            qs = qs.filter(portfolio_id=portfolio_id)

        dt_from = self.request.query_params.get("from")
        if dt_from:
            parsed = parse_datetime(dt_from)
            if parsed:
                qs = qs.filter(ts__gte=parsed)

        dt_to = self.request.query_params.get("to")
        if dt_to:
            parsed = parse_datetime(dt_to)
            if parsed:
                qs = qs.filter(ts__lte=parsed)

        order = self.request.query_params.get("order", "asc").lower()
        if order == "desc":
            qs = qs.order_by("-ts")
        else:
            qs = qs.order_by("ts")

        limit = self.request.query_params.get("limit")
        if limit:
            try:
                limit = max(1, min(int(limit), 5000))
                qs = qs[:limit]
            except ValueError:
                pass

        return qs.select_related("portfolio")

    def perform_create(self, serializer):
        """
        POST /api/trading/snapshots/
        Only allow creating snapshots for portfolios owned by the user.
        """
        user = self.request.user
        # Allow executor service to post snapshots for any portfolio
        if not (user.username == "executor" and user.is_staff and user.is_superuser):
            if not hasattr(user, "profile"):
                raise PermissionDenied("Profile missing.")

            portfolio: UserPortfolio = serializer.validated_data["portfolio"]
            if portfolio.user_id != user.profile.id:
                raise PermissionDenied("You do not own this portfolio.")

        serializer.save()

    def perform_update(self, serializer):
        """
        PUT /api/trading/snapshots/{id}/
        Only allow updating snapshots for portfolios owned by the user.
        """
        user = self.request.user
        # Allow executor service to update snapshots for any portfolio
        if not (user.username == "executor" and user.is_staff and user.is_superuser):
            if not hasattr(user, "profile"):
                raise PermissionDenied("Profile missing.")

            portfolio: UserPortfolio = serializer.validated_data.get("portfolio", serializer.instance.portfolio)
            if portfolio.user_id != user.profile.id:
                raise PermissionDenied("You do not own this portfolio.")

        serializer.save()

    @action(detail=False, methods=["GET"], url_path="latest")
    def latest(self, request):
        """
        GET /api/trading/snapshots/latest/?portfolio=<id>
        Get latest snapshot for a portfolio.
        """
        user = request.user
        if not hasattr(user, "profile"):
            raise PermissionDenied("Profile missing.")

        portfolio_id = request.query_params.get("portfolio")
        if not portfolio_id:
            return Response({"detail": "Missing required query param: portfolio"}, status=400)

        try:
            portfolio_id = int(portfolio_id)
        except ValueError:
            return Response({"detail": "Invalid portfolio id"}, status=400)

        snap = (
            PortfolioSnapshot.objects
            .filter(portfolio_id=portfolio_id, portfolio__user=user.profile)
            .order_by("-ts")
            .first()
        )

        if not snap:
            return Response({"detail": "No snapshots found."}, status=404)

        return Response(self.get_serializer(snap).data)
