from django.contrib.auth import get_user_model
from rest_framework import viewsets, permissions, mixins, status
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied, NotFound

from .models import UserPortfolio, UserProfile
from .serializers import UserPortofolioSerializer, UserProfileSerializer, UserSerializer
from rest_framework import permissions
User = get_user_model()


class UserPortfolioViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet
):
    serializer_class = UserPortofolioSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UserPortfolio.objects.filter(user=self.request.user.profile)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user.profile)

    def destroy(self, request, *args, **kwargs):
        """
        DELETE does not remove the portfolio.
        It resets it to the default state.
        """
        portfolio = self.get_object()

        if portfolio.user != request.user.profile:
            raise PermissionDenied("You do not own this portfolio.")

        # Reset business state
        portfolio.balance = 10000
        portfolio.is_active = True
        portfolio.save(update_fields=["balance", "is_active"])

        # Remove all holdings
        portfolio.holdings.all().delete()

        serializer = self.get_serializer(portfolio)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserProfileViewSet(
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        try:
            return self.request.user.profile
        except UserProfile.DoesNotExist:
            raise NotFound("Profile does not exist.")


class UserViewSet(
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSerializer
    queryset = User.objects.all()

    def get_object(self):
        pk = self.kwargs.get("pk")

        if pk is None:
            return self.request.user

        if not self.request.user.is_staff and str(self.request.user.pk) != pk:
            raise PermissionDenied("You do not have permission to access this user.")

        try:
            return User.objects.get(pk=pk)
        except User.DoesNotExist:
            raise NotFound("User not found.")