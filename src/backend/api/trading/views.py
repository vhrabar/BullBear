from django.db.models import OuterRef, Subquery
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, permissions, generics, filters
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticatedOrReadOnly, BasePermission, SAFE_METHODS
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import PortfolioHolding, InstrumentIntervalData, Instrument, InstrumentQuote, Company, CompanyNews, \
    EarningsReport, Dividend
from .serializers import PortfolioHoldingSerializer, InstrumentIntervalDataSerializer, InstrumentSerializer, \
    BuySellSerializer, LatestInstrumentDataSerializer, InstrumentQuoteSerializer, CompanySerializer, \
    CompanyNewsSerializer, EarningsReportSerializer, DividendSerializer
from .services import buy_instrument, sell_instrument
from api.users.models import UserProfile, UserPortfolio
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator


class IsAdminOrReadOnly(BasePermission):
    """
    Custom permission: only admin users can modify, everyone else can read.
    """
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user and request.user.is_staff

class NewsPagination(LimitOffsetPagination):
    """
    Pagination class for company news.
    """
    default_limit = 3
    max_limit = 10


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
    """
    Returns all interval/candle data.
    Optional filter: ?instrument=<instrument_symbol>
    """
    serializer_class = InstrumentIntervalDataSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        queryset = InstrumentIntervalData.objects.select_related('instrument').all()
        instrument_name = self.request.query_params.get('instrument')

        if instrument_name:
            queryset = queryset.filter(instrument__symbol__exact=instrument_name)

        return queryset.order_by('start_time')



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
                .filter(instrument__symbol__exact=instrument_name)
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

    lookup_field = "symbol"
    lookup_value_regex = r"[A-Za-z0-9\.\-_]+"



@method_decorator(csrf_exempt, name='dispatch')
class BuyInstrumentView(APIView):
    permission_classes = []

    def post(self, request):
        serializer = BuySellSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Support service-to-service calls with portfolio_id
        portfolio_id = serializer.validated_data.get('portfolio_id')
        if portfolio_id:
            portfolio = UserPortfolio.objects.get(id=portfolio_id)
        else:
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

        # Support service-to-service calls with portfolio_id
        portfolio_id = serializer.validated_data.get('portfolio_id')
        if portfolio_id:
            portfolio = UserPortfolio.objects.get(id=portfolio_id)
        else:
            profile = request.user.profile
            portfolio = UserPortfolio.objects.get(user=profile)

        holding = sell_instrument(
            portfolio=portfolio,
            instrument_symbol=serializer.validated_data['instrument_symbol'],   # type: ignore
            quantity=serializer.validated_data['quantity'], # type: ignore
            price=serializer.validated_data.get('price')    # type: ignore
        )

        return Response(PortfolioHoldingSerializer(holding).data, status=status.HTTP_200_OK)


class InstrumentQuoteViewSet(viewsets.ViewSet):
    """
    ViewSet for instrument-related endpoints.
    Includes a custom action for latest quote retrieval.
    """

    @action(detail=True, methods=["get"], url_path="quote")
    def latest_quote(self, request, pk=None):
        quote = get_object_or_404(
            InstrumentQuote.objects.select_related("instrument"),
            instrument__symbol__iexact=pk,
        )

        return Response(InstrumentQuoteSerializer(quote).data, status=status.HTTP_200_OK)




class CompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all().order_by('name')
    serializer_class = CompanySerializer
    permission_classes = [IsAdminOrReadOnly]




class CompanyNewsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = CompanyNews.objects.all()
    serializer_class = CompanyNewsSerializer
    permission_classes = [IsAdminOrReadOnly]

    filter_backends = [
        DjangoFilterBackend,
        filters.OrderingFilter,
    ]

    filterset_fields = {
        "companies__ticker": ["exact"],
    }

    ordering_fields = ["published_at"]
    ordering = ["-published_at"]

    pagination_class = NewsPagination


class EarningsReportViewSet(viewsets.ModelViewSet):
    queryset = EarningsReport.objects.all()
    serializer_class = EarningsReportSerializer
    permission_classes = [IsAdminOrReadOnly]

    filter_backends = [
        DjangoFilterBackend,
        filters.OrderingFilter,
    ]

    filterset_fields = {
        "company__ticker": ["exact"],
    }

    ordering_fields = ["report_date"]
    ordering = ["report_date"]


class DividendViewSet(viewsets.ModelViewSet):
    queryset = Dividend.objects.all()
    serializer_class = DividendSerializer
    permission_classes = [IsAdminOrReadOnly]

    filter_backends = [
        DjangoFilterBackend,
        filters.OrderingFilter,
    ]

    filterset_fields = {
        "company__ticker": ["exact"],
    }

    ordering_fields = ["ex_date"]
    ordering = ["ex_date"]

