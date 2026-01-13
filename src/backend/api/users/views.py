from rest_framework import viewsets, request, status
from rest_framework.response import Response

from .models import UserPortfolio, UserProfile, ContactMessage
from .serializers import UserPortofolioSerializer, UserProfileSerializer, ContactDefaultsSerializer, \
    ContactMessageSerializer
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

        msg: ContactMessage = serializer.save(
            user=request.user if request.user.is_authenticated else None,
            ip_address=ip,
            user_agent=ua[:2000],
        )

        return Response(
            {"detail": "Message received.", "id": msg.id},
            status=status.HTTP_201_CREATED,
        )
