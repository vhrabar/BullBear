from rest_framework import viewsets, request
from rest_framework.response import Response

from .models import UserPortfolio, UserProfile
from .serializers import UserPortofolioSerializer, UserProfileSerializer
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


class ResetUserPortfolioViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def reset_portfolio(self, request: request.Request, pk=None):
        try:
            profile = request.user.profile
            portfolio = UserPortfolio.objects.get(pk=pk, user=profile)

            # Reset balance
            portfolio.balance = 10000
            portfolio.save()

            # Delete all related holdings
            portfolio.holdings.all().delete()

            serializer = UserPortofolioSerializer(portfolio)
            return Response(serializer.data)

        except UserPortfolio.DoesNotExist:
            return Response(
                {"detail": "Portfolio not found."},
                status=404
            )
