from decimal import Decimal
from datetime import timedelta

from django.test import TestCase
from django.utils import timezone
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from api.users.models import UserProfile, UserPortfolio, PortfolioSnapshot
from django.contrib.auth import get_user_model

User = get_user_model()


class PortfolioRiskAPITests(TestCase):
    """
    Tests GET /api/users/snapshots/risk/
    """

    def setUp(self):
        self.client = APIClient()

        # ----------------------
        # Create normal users
        # ----------------------
        self.user1 = User.objects.create_user(
            username="user1",
            password="pass12345",
            email="user1@example.com",
        )
        self.user2 = User.objects.create_user(
            username="user2",
            password="pass12345",
            email="user2@example.com",
        )

        # ----------------------
        # access profiles
        # ----------------------
        self.profile1 = self.user1.profile
        self.profile2 = self.user2.profile

        # ----------------------
        # access  account portfolios
        # ----------------------
        self.portfolio1 = self.profile1.portfolios.first()

        self.portfolio2 = self.profile2.portfolios.first()

        # ----------------------
        # delete initial snapshot created by signal on portfolio creation
        # ----------------------

        PortfolioSnapshot.objects.filter(portfolio=self.portfolio1).delete()
        PortfolioSnapshot.objects.filter(portfolio=self.portfolio2).delete()

        self.url = "/api/users/snapshots/risk/"

    def auth(self, user):
        self.client.force_authenticate(user=user)

    def create_snapshots(self, portfolio, values, interval="10m"):
        """
        Creates snapshots with exact total_value series.
        values: list[float | Decimal]
        interval controls spacing: 10m / 1h / 1d
        """
        now = timezone.now()

        if interval == "10m":
            step = timedelta(minutes=10)
        elif interval == "1h":
            step = timedelta(hours=1)
        else:
            step = timedelta(days=1)

        # oldest -> newest
        ts0 = now - step * (len(values) - 1)

        for i, v in enumerate(values):
            PortfolioSnapshot.objects.create(
                portfolio=portfolio,
                ts=ts0 + i * step,
                total_value=Decimal(str(v)),
                cash_balance=Decimal("0"),
                equity_value=Decimal(str(v)),
            )

    def assert_has_metrics(self, data):
        NUMERIC_KEYS = (
            "return_pct",
            "volatility_pct",
            "max_drawdown_pct",
            "sharpe",
            "sortino",
            "var_95_pct",
            "cvar_95_pct",
            "beta",
            "alpha_pct",
        )

        self.assertIn("metrics", data)
        m = data["metrics"]
        self.assertIsInstance(m, dict)

        for k in NUMERIC_KEYS:
            self.assertIn(k, m, msg=f"Missing metric: {k}")
            self.assertIsInstance(m[k], (int, float), msg=f"Metric {k} must be numeric")

        # optional metadata
        if "benchmark_symbol" in m:
            self.assertIsInstance(m["benchmark_symbol"], str)

    def test_missing_portfolio_returns_400(self):
        self.auth(self.user1)
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_portfolio_returns_400(self):
        self.auth(self.user1)
        res = self.client.get(self.url, {"portfolio": "abc"})
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_range_returns_400(self):
        self.auth(self.user1)
        res = self.client.get(self.url, {"portfolio": self.portfolio1.id, "range": "9Y", "interval": "10m"})
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_interval_returns_400(self):
        self.auth(self.user1)
        res = self.client.get(self.url, {"portfolio": self.portfolio1.id, "range": "1W", "interval": "5m"})
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_non_owner_forbidden_or_empty(self):
        """
        - either 403
        - or 200 with all zeros
        """
        self.create_snapshots(self.portfolio1, [100, 101, 102], interval="10m")

        self.auth(self.user2)
        res = self.client.get(self.url, {"portfolio": self.portfolio1.id, "range": "1W", "interval": "10m"})

        self.assertIn(res.status_code, (status.HTTP_403_FORBIDDEN, status.HTTP_200_OK))

        if res.status_code == status.HTTP_200_OK:
            data = res.json()
            self.assert_has_metrics(data)

    def test_no_snapshots_returns_zero_metrics(self):
        """
        No snapshots -> all metrics zero
        """
        self.auth(self.user1)

        res = self.client.get(self.url, {"portfolio": self.portfolio1.id, "range": "1W", "interval": "10m"})
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        data = res.json()
        self.assert_has_metrics(data)

        m = data["metrics"]
        self.assertEqual(m["return_pct"], 0.0)
        self.assertEqual(m["volatility_pct"], 0.0)
        self.assertEqual(m["max_drawdown_pct"], 0.0)

    def test_return_pct_correct_simple(self):
        """
        values: 100 -> 110 => return_pct = 10%
        """
        self.create_snapshots(self.portfolio1, [100, 110], interval="10m")
        self.auth(self.user1)

        res = self.client.get(self.url, {"portfolio": self.portfolio1.id, "range": "1W", "interval": "10m"})
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        data = res.json()
        self.assert_has_metrics(data)

        ret = data["metrics"]["return_pct"]
        self.assertAlmostEqual(ret, 10.0, places=6)

    def test_max_drawdown_correct(self):
        """
        values: 100 -> 120 -> 90 -> 130
        peak=120 drop to 90 => drawdown = -25%
        """
        self.create_snapshots(self.portfolio1, [100, 120, 90, 130], interval="10m")
        self.auth(self.user1)

        res = self.client.get(self.url, {"portfolio": self.portfolio1.id, "range": "1W", "interval": "10m"})
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        dd = res.json()["metrics"]["max_drawdown_pct"]
        self.assertAlmostEqual(dd, -25.0, places=6)

    def test_volatility_non_negative(self):
        """
        Volatility should never be negative.
        """
        self.create_snapshots(self.portfolio1, [100, 101, 99, 100], interval="10m")
        self.auth(self.user1)

        res = self.client.get(self.url, {"portfolio": self.portfolio1.id, "range": "1W", "interval": "10m"})
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        vol = res.json()["metrics"]["volatility_pct"]
        self.assertGreaterEqual(vol, 0.0)

    def test_var_cvar_consistency_monotonic_up(self):
        """
        If total_value increases monotonically, returns are >= 0,
        then the worst 5% return should be >= 0 -> var/cvar should be >= 0.
        """
        self.create_snapshots(self.portfolio1, [100, 101, 102, 103, 104], interval="10m")
        self.auth(self.user1)

        res = self.client.get(self.url, {"portfolio": self.portfolio1.id, "range": "1W", "interval": "10m"})
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        m = res.json()["metrics"]
        self.assertGreaterEqual(m["var_95_pct"], 0.0)
        self.assertGreaterEqual(m["cvar_95_pct"], 0.0)

    def test_endpoint_is_deterministic(self):
        """
        Multiple calls produce same result.
        """
        self.create_snapshots(self.portfolio1, [100, 120, 90, 130], interval="10m")
        self.auth(self.user1)

        res1 = self.client.get(self.url, {"portfolio": self.portfolio1.id, "range": "1W", "interval": "10m"})
        res2 = self.client.get(self.url, {"portfolio": self.portfolio1.id, "range": "1W", "interval": "10m"})

        self.assertEqual(res1.status_code, 200)
        self.assertEqual(res2.status_code, 200)
        self.assertEqual(res1.json(), res2.json())
