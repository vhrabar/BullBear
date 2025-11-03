from rest_framework import viewsets, permissions
from .models import PortfolioHolding, InstrumentIntervalData, Instrument
from .serializers import PortfolioHoldingSerializer, InstrumentIntervalDataSerializer, InstrumentSerializer


class PortfolioHoldingViewSet(viewsets.ModelViewSet):
    serializer_class = PortfolioHoldingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Only return holdings belonging to the logged-in user
        user = self.request.user
        return PortfolioHolding.objects.select_related('portfolio', 'instrument').filter(
            portfolio__user=user
        )

    def perform_create(self, serializer):
        # Automatically assign the user’s portfolio if applicable
        user = self.request.user
        portfolio = user.userportfolio
        serializer.save(portfolio=portfolio)


class InstrumentIntervalDataViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = InstrumentIntervalData.objects.select_related('instrument').all()
    serializer_class = InstrumentIntervalDataSerializer
    permission_classes = [permissions.AllowAny]


class InstrumentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Instrument.objects.filter(is_active=True)
    serializer_class = InstrumentSerializer
    permission_classes = [permissions.AllowAny]

