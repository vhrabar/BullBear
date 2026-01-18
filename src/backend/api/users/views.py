from datetime import timedelta
from math import sqrt

from django.db.models.functions import TruncMinute, TruncDay, TruncHour
from django.utils import timezone
from django.db.models import Avg
from django.utils.dateparse import parse_datetime

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework import permissions

from .functions import _safe_float, _pct, _max_drawdown, _std, _var_cvar
from .models import UserPortfolio, UserProfile, ContactMessage, PortfolioSnapshot
from .serializers import (
    UserPortofolioSerializer,
    UserProfileSerializer,
    ContactDefaultsSerializer,
    ContactMessageSerializer,
    PortfolioSnapshotSerializer,
)
from ..orders.permissions import IsServiceExecutor
from ..trading.models import Instrument, InstrumentIntervalData


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
