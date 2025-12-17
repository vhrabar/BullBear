from django.contrib.auth import get_user_model
from rest_framework import viewsets, request, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import UserPortfolio, UserProfile
from .serializers import UserPortofolioSerializer, UserProfileSerializer
from rest_framework import permissions
User = get_user_model()


class UserPortfolioViewSet(viewsets.ViewSet):
    serializer_class = UserPortofolioSerializer
    permission_classes = [permissions.IsAuthenticated]

    def destroy(self, request: request.Request, pk=None):
        try:
            profile = request.user.profile
            portfolio = UserPortfolio.objects.get(user=profile)

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

    def get_queryset(self):
        profile = self.request.user.profile
        return UserPortfolio.objects.filter(user=profile)


class UserProfileViewSet(viewsets.ViewSet):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UserProfile.objects.filter(user=self.request.user)



class UserViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def destroy(self, request, pk=None):
        # admin action
        if pk:
            if not request.user.is_staff:
                return Response(
                    {"detail": "You do not have permission to delete other users."},
                    status=status.HTTP_403_FORBIDDEN
                )

            try:
                user = User.objects.get(pk=pk)
            except request.user.DoesNotExist:
                return Response(
                    {"detail": "User not found."},
                    status=status.HTTP_404_NOT_FOUND
                )
        # user action
        else:
            user = request.user

        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

