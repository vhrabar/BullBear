from django.db.models import OuterRef, Subquery
from rest_framework import viewsets, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import PortfolioHolding, InstrumentIntervalData, Instrument
from .serializers import PortfolioHoldingSerializer, InstrumentIntervalDataSerializer, InstrumentSerializer, \
    BuySellSerializer, LatestInstrumentDataSerializer
from .services import buy_instrument, sell_instrument
from api.users.models import UserProfile, UserPortfolio
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator


class PortfolioHoldingViewSet(viewsets.ModelViewSet):
    serializer_class = PortfolioHoldingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Only return holdings belonging to the logged-in user
        user = self.request.user
        return PortfolioHolding.objects.select_related('portfolio', 'instrument').filter(
            portfolio__user=user.profile
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


class LatestInstrumentDataViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Returns the latest interval data per instrument.
    Optional filter: ?instrument=<instrument_name>
    """
    serializer_class = LatestInstrumentDataSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        instrument_name = self.request.query_params.get('instrument')

        # If instrument name is provided -> filter by that instrument
        if instrument_name:
            return (
                InstrumentIntervalData.objects
                .select_related('instrument')
                .filter(instrument__name__iexact=instrument_name)
                .order_by('-start_time')[:1]
            )

        # if no instrument name is provided -> return latest data for all instruments
        subquery = (
            InstrumentIntervalData.objects
            .filter(instrument=OuterRef('instrument'))
            .order_by('-start_time')
            .values('id')[:1]
        )

        queryset = (
            InstrumentIntervalData.objects
            .filter(id__in=Subquery(subquery))
            .select_related('instrument')
            .order_by('instrument__symbol')
        )

        return queryset



class InstrumentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Instrument.objects.filter(is_active=True)
    serializer_class = InstrumentSerializer
    permission_classes = [permissions.AllowAny]


@method_decorator(csrf_exempt, name='dispatch')
class BuyInstrumentView(APIView):
    permission_classes = []

    def post(self, request):
        serializer = BuySellSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        profile = request.user.profile
        portfolio = UserPortfolio.objects.get(user=profile)

        holding = buy_instrument(
            portfolio=portfolio,
            instrument_symbol=serializer.validated_data['instrument_symbol'],   # type: ignore
            quantity=serializer.validated_data['quantity'], # type: ignore
            price=serializer.validated_data.get('price')    # type: ignore
        )

        return Response(PortfolioHoldingSerializer(holding).data, status=status.HTTP_200_OK)


@method_decorator(csrf_exempt, name='dispatch')
class SellInstrumentView(APIView):
    permission_classes = []

    def post(self, request):
        serializer = BuySellSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        profile = request.user.profile
        portfolio = UserPortfolio.objects.get(user=profile)

        holding = sell_instrument(
            portfolio=portfolio,
            instrument_symbol=serializer.validated_data['instrument_symbol'],   # type: ignore
            quantity=serializer.validated_data['quantity'], # type: ignore
            price=serializer.validated_data.get('price')    # type: ignore
        )

        return Response(PortfolioHoldingSerializer(holding).data, status=status.HTTP_200_OK)

