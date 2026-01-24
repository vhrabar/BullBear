from datetime import timedelta
from decimal import Decimal
from math import sqrt

import pandas as pd

from django.db.models import Avg
from django.db.models.functions import TruncDay, TruncHour, TruncMinute
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from rest_framework import permissions, request, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from ..orders.models import Order
from ..orders.permissions import IsServiceExecutor
from ..trading.models import Instrument, InstrumentIntervalData, PortfolioHolding
from .functions import _max_drawdown, _pct, _safe_float, _std, _var_cvar
from .models import ContactMessage, PortfolioSnapshot, UserPortfolio, UserProfile, User
from .serializers import (
    ContactDefaultsSerializer,
    ContactMessageSerializer,
    PortfolioSnapshotSerializer,
    UserPortofolioSerializer,
    UserProfileSerializer,
)



class UserPortfolioViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = UserPortofolioSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        profile = self.request.user.profile
        return UserPortfolio.objects.filter(user=profile)

@csrf_exempt
@require_POST
def import_csv(request):
    """
    Import orders from a CSV file for the current authenticated user.
    Required CSV columns: portfolio_name, instrument_symbol, side, order_type, quantity
    Optional columns: time_in_force, limit_price, stop_price
    """
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Authentication required"}, status=401)

    # Get the current user's profile
    try:
        profile = request.user.profile
    except UserProfile.DoesNotExist:
        return JsonResponse({"error": "User profile not found"}, status=404)

    file = request.FILES.get("file")
    if not file:
        return JsonResponse({"error": "No file uploaded"}, status = 400)
    try:
        df = pd.read_csv(file)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)
    records = df.to_dict(orient = "records")
    required_fields = {"portfolio_name", "instrument_symbol", "side", "order_type", "quantity"}
    for i, row in enumerate(records):
        for field in required_fields:
            if field not in row or pd.isna(row[field]) or row[field] == "":
                return JsonResponse(
                    {"error": f"Missing value for '{field}' in row {i+1}"},
                    status = 400
                    )

    created_orders = []
    for row in records:
        portfolio, _ = UserPortfolio.objects.get_or_create(
            user = profile,
            name = row["portfolio_name"],
            defaults = {"balance": 10000}
        )
        instrument, _ = Instrument.objects.get_or_create(
            symbol = row["instrument_symbol"],
            defaults = {"name": row.get("instrument_name") or row["instrument_symbol"], "type": "STOCK"}
        )

        # Map side and order_type to model choices
        side = row["side"].upper()
        if side not in [Order.Side.BUY, Order.Side.SELL]:
            return JsonResponse({"error": f"Invalid side '{side}' in row. Use BUY or SELL."}, status=400)

        order_type = row["order_type"].upper()
        valid_order_types = [ot[0] for ot in Order.OrderType.choices]
        if order_type not in valid_order_types:
            return JsonResponse({"error": f"Invalid order_type '{order_type}'. Use MARKET, LIMIT, STOP, or STOP_LIMIT."}, status=400)

        time_in_force = row.get("time_in_force", "GTC")
        if pd.isna(time_in_force) or time_in_force == "":
            time_in_force = "GTC"
        time_in_force = time_in_force.upper()

        limit_price = row.get("limit_price")
        if pd.isna(limit_price) or limit_price == "":
            limit_price = None
        else:
            limit_price = Decimal(str(limit_price))

        stop_price = row.get("stop_price")
        if pd.isna(stop_price) or stop_price == "":
            stop_price = None
        else:
            stop_price = Decimal(str(stop_price))

        # Create the order for the current user
        order = Order.objects.create(
            user=profile,
            portfolio=portfolio,
            instrument=instrument,
            side=side,
            order_type=order_type,
            time_in_force=time_in_force,
            quantity=Decimal(str(row["quantity"])),
            limit_price=limit_price,
            stop_price=stop_price,
            status=Order.Status.OPEN,
        )
        created_orders.append(order.id)

    return JsonResponse({"message": f"Successfully imported {len(created_orders)} orders", "order_ids": created_orders})

def export_csv(request):
    """
    Export orders for the current authenticated user to CSV.
    """
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Authentication required"}, status=401)

    # Get the current user's profile
    try:
        profile = request.user.profile
    except UserProfile.DoesNotExist:
        return JsonResponse({"error": "User profile not found"}, status=404)

    # Export only the current user's orders
    orders = Order.objects.select_related(
        "portfolio", "instrument"
    ).filter(user=profile)

    data = []
    for o in orders:
        data.append({
            "portfolio_name": o.portfolio.name,
            "instrument_symbol": o.instrument.symbol,
            "instrument_name": o.instrument.name,
            "side": o.side,
            "order_type": o.order_type,
            "time_in_force": o.time_in_force,
            "quantity": float(o.quantity),
            "limit_price": float(o.limit_price) if o.limit_price else "",
            "stop_price": float(o.stop_price) if o.stop_price else "",
            "status": o.status,
            "filled_quantity": float(o.filled_quantity),
            "avg_fill_price": float(o.avg_fill_price) if o.avg_fill_price else "",
            "placed_at": o.placed_at.strftime("%Y-%m-%d %H:%M:%S") if o.placed_at else "",
        })

    df = pd.DataFrame(data)
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="my_orders.csv"'
    df.to_csv(response, index=False)
    return response

class UserProfileViewSet(viewsets.ModelViewSet):
    """
    GET /api/users/user-profile/ -> list current user's profile(s)
    PATCH /api/users/user-profile/{pk}/ -> update profile (only own profile allowed)
    PATCH /api/users/user-profile/me/ -> update current user's profile + optional user fields
    """
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UserProfile.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        # Use the update serializer for write operations
        if self.action in ("update", "partial_update", "me"):
            from .serializers import UserProfileUpdateSerializer

            return UserProfileUpdateSerializer
        return UserProfileSerializer

    def perform_update(self, serializer):
        # ensure user owns the profile
        instance = serializer.instance
        if instance.user != self.request.user:
            raise PermissionDenied("You can only update your own profile.")
        serializer.save()

    @action(detail=False, methods=["GET", "PATCH"], url_path="me")
    def me(self, request):
        """
        PATCH /api/users/user-profile/me/
        Accepts fields: bio, avatar_url, username, first_name, last_name
        Updates both UserProfile and User accordingly for the authenticated user.
        """
        user = request.user
        if not hasattr(user, "profile"):
            return Response({"detail": "Profile missing."}, status=400)

        profile = user.profile
        if request.method == "GET":
            return Response(UserProfileSerializer(profile).data)

        # PATCH
        serializer = self.get_serializer(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(UserProfileSerializer(profile).data)


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
    permission_classes = [permissions.IsAuthenticated | IsServiceExecutor]

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

    @action(detail=False, methods=["GET"], url_path="chart")
    def chart(self, request):
        """
        GET /api/trading/snapshots/chart/?portfolio=<id>&range=1D&interval=10m
        Returns downsampled + aggregated points for charts.
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

        range_code = request.query_params.get("range", "1D")
        interval = request.query_params.get("interval", "10m")

        now = timezone.now()

        # range -> start time
        ranges = {
            "1D": timedelta(days=1),
            "1W": timedelta(days=7),
            "1M": timedelta(days=30),
            "3M": timedelta(days=90),
            "1Y": timedelta(days=365),
        }
        if range_code not in ranges:
            return Response({"detail": "Invalid range. Use 1D/1W/1M/3M/1Y"}, status=400)

        start = now - ranges[range_code]

        # base queryset
        qs = PortfolioSnapshot.objects.filter(
            portfolio_id=portfolio_id,
            portfolio__user=user.profile,
            ts__gte=start,
            ts__lte=now
        )

        # interval bucketing
        if interval == "10m":
            bucket_expr = TruncMinute("ts")
        elif interval == "1h":
            bucket_expr = TruncHour("ts")
        elif interval == "1d":
            bucket_expr = TruncDay("ts")
        else:
            return Response({"detail": "Invalid interval. Use 10m/1h/1d"}, status=400)

        # aggregate per bucket
        rows = list(
            qs.annotate(bucket=bucket_expr)
            .values("bucket")
            .annotate(
                cash_balance=Avg("cash_balance"),
                equity_value=Avg("equity_value"),
                total_value=Avg("total_value"),
                unrealized_pl=Avg("unrealized_pl"),
                unrealized_pl_pct=Avg("unrealized_pl_pct"),
                realized_pl=Avg("realized_pl"),
                realized_pl_pct=Avg("realized_pl_pct"),
            )
            .order_by("bucket")
        )

        points = [
            {
                "ts": r["bucket"],
                "cash_balance": r["cash_balance"],
                "equity_value": r["equity_value"],
                "total_value": r["total_value"],
                "unrealized_pl": r["unrealized_pl"],
                "unrealized_pl_pct": r["unrealized_pl_pct"],
                "realized_pl": r["realized_pl"],
                "realized_pl_pct": r["realized_pl_pct"],
            }
            for r in rows
        ]

        return Response({
            "portfolio_id": portfolio_id,
            "range": range_code,
            "interval": interval,
            "count": len(points),
            "points": points,
        })

    @action(detail=False, methods=["GET"], url_path="risk")
    def risk(self, request):
        """
        GET /api/users/snapshots/risk/?portfolio=<id>&range=<range>&interval=<interval>&benchmark=<symbol>&rf=<annual>
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

        range_code = request.query_params.get("range", "1W")
        interval = request.query_params.get("interval", "1h")
        benchmark_symbol = request.query_params.get("benchmark", "SPY")

        rf = request.query_params.get("rf", None)

        now = timezone.now()

        ranges = {
            "1D": timedelta(days=1),
            "1W": timedelta(days=7),
            "1M": timedelta(days=30),
            "3M": timedelta(days=90),
            "1Y": timedelta(days=365),
        }
        if range_code not in ranges:
            return Response({"detail": "Invalid range. Use 1D/1W/1M/3M/1Y"}, status=400)

        start = now - ranges[range_code]

        qs = PortfolioSnapshot.objects.filter(
            portfolio_id=portfolio_id,
            portfolio__user=user.profile,
            ts__gte=start,
            ts__lte=now
        )

        # interval bucketing
        if interval == "10m":
            bucket_expr = TruncMinute("ts")
            periods_per_year = 252 * 6.5 * 6
        elif interval == "1h":
            bucket_expr = TruncHour("ts")
            periods_per_year = 252 * 6.5
        elif interval == "1d":
            bucket_expr = TruncDay("ts")
            periods_per_year = 252
        else:
            return Response({"detail": "Invalid interval. Use 10m/1h/1d"}, status=400)

        # Portfolio values by bucket
        prows = list(
            qs.annotate(bucket=bucket_expr)
            .values("bucket")
            .annotate(total_value=Avg("total_value"))
            .order_by("bucket")
        )

        port_series = {r["bucket"]: _safe_float(r["total_value"]) for r in prows if r["total_value"] is not None}
        port_keys = sorted(port_series.keys())
        port_values = [port_series[k] for k in port_keys]

        if len(port_values) < 2:
            return Response({
                "portfolio_id": portfolio_id,
                "range": range_code,
                "interval": interval,
                "count": len(port_values),
                "metrics": {
                    "return_pct": 0.0,
                    "volatility_pct": 0.0,
                    "downside_volatility_pct": 0.0,
                    "max_drawdown_pct": 0.0,
                    "sharpe": 0.0,
                    "sortino": 0.0,
                    "var_95_pct": 0.0,
                    "cvar_95_pct": 0.0,
                    "beta": 0.0,
                    "alpha_pct": 0.0,
                    "benchmark": benchmark_symbol,
                }
            })

        # Risk-free
        if rf is not None:
            try:
                rf_annual = float(rf)
            except ValueError:
                return Response({"detail": "Invalid rf. Must be decimal annual (e.g. 0.02)."}, status=400)
        else:
            # German gov bonds
            rf_annual = 0.02

        rf_per_period = (1.0 + rf_annual) ** (1.0 / periods_per_year) - 1.0

        # portfolio returns
        port_rets = []
        for i in range(1, len(port_values)):
            prev = port_values[i - 1]
            cur = port_values[i]
            if prev > 0:
                port_rets.append((cur - prev) / prev)

        if not port_rets:
            port_rets = [0.0]

        # total return
        total_ret = _pct(port_values[0], port_values[-1])

        # max drawdown
        mdd = _max_drawdown(port_values)

        # volatility
        vol = _std(port_rets) * sqrt(periods_per_year)

        # downside volatility
        downside = [r for r in port_rets if r < 0]
        downside_std = _std(downside) * sqrt(periods_per_year) if len(downside) >= 2 else 0.0

        # sharpe
        mean_ret = sum(port_rets) / len(port_rets)
        excess = mean_ret - rf_per_period
        std_rets = _std(port_rets)
        sharpe = (excess / std_rets) * sqrt(periods_per_year) if std_rets > 0 else 0.0

        # sortino
        sortino = (excess / downside_std) if downside_std > 0 else 0.0

        # VaR/CVaR 95%
        var95, cvar95 = _var_cvar(port_rets, alpha=0.95)

        # beta/alpha
        benchmark_instr = Instrument.objects.filter(symbol=benchmark_symbol).first()

        beta = 0.0
        alpha = 0.0
        alpha_annual = 0.0

        if benchmark_instr:
            # benchmark bucket expr
            if interval == "10m":
                bucket_expr_b = TruncMinute("start_time")
            elif interval == "1h":
                bucket_expr_b = TruncHour("start_time")
            else:
                bucket_expr_b = TruncDay("start_time")

            bqs = InstrumentIntervalData.objects.filter(
                instrument=benchmark_instr,
                start_time__gte=start,
                start_time__lte=now
            )

            brows = list(
                bqs.annotate(bucket=bucket_expr_b)
                .values("bucket")
                .annotate(close=Avg("close_price"))
                .order_by("bucket")
            )

            bench_series = {r["bucket"]: _safe_float(r["close"]) for r in brows if r["close"] is not None}

            common_keys = sorted(set(port_series.keys()) & set(bench_series.keys()))

            if len(common_keys) >= 3:
                port_vals = [port_series[k] for k in common_keys]
                bench_vals = [bench_series[k] for k in common_keys]

                bench_rets = []
                aligned_port_rets = []

                for i in range(1, len(common_keys)):
                    p0, p1 = port_vals[i - 1], port_vals[i]
                    b0, b1 = bench_vals[i - 1], bench_vals[i]

                    if p0 > 0 and b0 > 0:
                        aligned_port_rets.append((p1 - p0) / p0)
                        bench_rets.append((b1 - b0) / b0)

                if len(aligned_port_rets) >= 2:
                    mean_p = sum(aligned_port_rets) / len(aligned_port_rets)
                    mean_b = sum(bench_rets) / len(bench_rets)

                    cov = sum((aligned_port_rets[i] - mean_p) * (bench_rets[i] - mean_b)
                              for i in range(len(aligned_port_rets))) / (len(aligned_port_rets) - 1)
                    var_b = sum((x - mean_b) ** 2 for x in bench_rets) / (len(bench_rets) - 1)

                    beta = cov / var_b if var_b > 0 else 0.0

                    # alpha per period
                    alpha = mean_p - (rf_per_period + beta * (mean_b - rf_per_period))

                    # annualize alpha
                    alpha_annual = ((1.0 + alpha) ** periods_per_year - 1.0) if alpha != 0 else 0.0

        return Response({
            "portfolio_id": portfolio_id,
            "range": range_code,
            "interval": interval,
            "count": len(port_values),
            "metrics": {
                "return_pct": total_ret * 100.0,
                "volatility_pct": vol * 100.0,
                "downside_volatility_pct": downside_std * 100.0,
                "max_drawdown_pct": mdd * 100.0,
                "sharpe": sharpe,
                "sortino": sortino,
                "var_95_pct": var95 * 100.0,
                "cvar_95_pct": cvar95 * 100.0,
                "beta": beta,
                "alpha_pct": alpha_annual * 100.0,
                "benchmark": benchmark_symbol,
            }
        })
