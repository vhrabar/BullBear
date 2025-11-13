from rest_framework import viewsets, request
from .models import UserPortfolio
from .serializers import UserPortofolioSerializer
from rest_framework import permissions


class UserPortfolioViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = UserPortofolioSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        profile = self.request.user.profile
        return UserPortfolio.objects.filter(user=profile)


