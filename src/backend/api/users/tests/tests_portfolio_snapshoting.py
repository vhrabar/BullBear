from datetime import timedelta
from decimal import Decimal

from django.test import override_settings
from django.utils import timezone
from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.test import APITestCase

from api.users.models import UserProfile, UserPortfolio, PortfolioSnapshot


User = get_user_model()


@override_settings(ROOT_URLCONF="core_api.urls")
class PortfolioSnapshotAPITests(APITestCase):
    """
    Full integration tests for:
    - GET /api/users/snapshots/
    - GET /api/users/snapshots/latest/?portfolio=<id>
    - POST /api/users/snapshots/
    """

    def setUp(self):
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

        # ----------------------
        # Create snapshots for portfolio1
        # ----------------------
        now = timezone.now()
        self.t1 = now - timedelta(minutes=30)
        self.t2 = now - timedelta(minutes=20)
        self.t3 = now - timedelta(minutes=10)

        PortfolioSnapshot.objects.create(
            portfolio=self.portfolio1,
            ts=self.t1,
            cash_balance=Decimal("9000.00"),
            equity_value=Decimal("1000.00"),
            total_value=Decimal("10000.00"),
            unrealized_pl=Decimal("0.00"),
            unrealized_pl_pct=Decimal("0.0000"),
            realized_pl=Decimal("0.00"),
            realized_pl_pct=Decimal("0.0000"),
        )
        PortfolioSnapshot.objects.create(
            portfolio=self.portfolio1,
            ts=self.t2,
            cash_balance=Decimal("8800.00"),
            equity_value=Decimal("1400.00"),
            total_value=Decimal("10200.00"),
            unrealized_pl=Decimal("200.00"),
            unrealized_pl_pct=Decimal("2.0000"),
            realized_pl=Decimal("0.00"),
            realized_pl_pct=Decimal("0.0000"),
        )
        PortfolioSnapshot.objects.create(
            portfolio=self.portfolio1,
            ts=self.t3,
            cash_balance=Decimal("8500.00"),
            equity_value=Decimal("1800.00"),
            total_value=Decimal("10300.00"),
            unrealized_pl=Decimal("300.00"),
            unrealized_pl_pct=Decimal("3.0000"),
            realized_pl=Decimal("0.00"),
            realized_pl_pct=Decimal("0.0000"),
        )

        # Create one snapshot for portfolio2
        PortfolioSnapshot.objects.create(
            portfolio=self.portfolio2,
            ts=self.t2,
            cash_balance=Decimal("9900.00"),
            equity_value=Decimal("200.00"),
            total_value=Decimal("10100.00"),
            unrealized_pl=Decimal("100.00"),
            unrealized_pl_pct=Decimal("1.0000"),
            realized_pl=Decimal("0.00"),
            realized_pl_pct=Decimal("0.0000"),
        )

        # ----------------------
        # Create executor service user
        # ----------------------
        self.executor = User.objects.create_user(
            username="executor",
            password="pass12345",
            email="executor@example.com",
            is_staff=True,
            is_superuser=True,
        )

        self.snapshots_url = "/api/users/snapshots/"
        self.latest_url = "/api/users/snapshots/latest/"


    def test_owner_can_list_snapshots(self):
        self.client.force_authenticate(self.user1)

        res = self.client.get(self.snapshots_url, {"portfolio": self.portfolio1.id})
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        data = res.json()
        self.assertEqual(len(data), 3)
        for row in data:
            self.assertEqual(row["portfolio"], self.portfolio1.id)

    def test_non_owner_sees_none(self):
        """
        User2 tries to list snapshots of portfolio1 -> should return empty.
        """
        self.client.force_authenticate(self.user2)

        res = self.client.get(self.snapshots_url, {"portfolio": self.portfolio1.id})
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        data = res.json()
        self.assertEqual(data, [])

    def test_filter_from_to(self):
        """
        from excludes earlier snapshots, to excludes later snapshots.
        """
        self.client.force_authenticate(self.user1)

        # from = t2 should include t2,t3 => 2 points
        res = self.client.get(self.snapshots_url, {"portfolio": self.portfolio1.id, "from": self.t2.isoformat()})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.json()), 2)

        # to = t2 should include t1,t2 => 2 points
        res = self.client.get(self.snapshots_url, {"portfolio": self.portfolio1.id, "to": self.t2.isoformat()})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.json()), 2)

        # from=t2,to=t2 => only t2 => 1 point
        res = self.client.get(
            self.snapshots_url,
            {"portfolio": self.portfolio1.id, "from": self.t2.isoformat(), "to": self.t2.isoformat()},
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.json()), 1)

    def test_order_asc_desc(self):
        """
        order=asc returns earliest first, order=desc returns latest first.
        """
        self.client.force_authenticate(self.user1)

        res = self.client.get(self.snapshots_url, {"portfolio": self.portfolio1.id, "order": "asc"})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        data = res.json()
        self.assertEqual(data[0]["ts"], self.t1.isoformat().replace("+00:00", "Z"))

        res = self.client.get(self.snapshots_url, {"portfolio": self.portfolio1.id, "order": "desc"})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        data = res.json()
        self.assertEqual(data[0]["ts"], self.t3.isoformat().replace("+00:00", "Z"))

    def test_limit(self):
        """
        limit=N returns at most N snapshots.
        """
        self.client.force_authenticate(self.user1)

        res = self.client.get(self.snapshots_url, {"portfolio": self.portfolio1.id, "order": "asc", "limit": 2})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.json()), 2)

    def test_invalid_datetime_does_not_crash(self):
        """
        Bad from/to should not crash or 500.
        """
        self.client.force_authenticate(self.user1)

        res = self.client.get(
            self.snapshots_url,
            {"portfolio": self.portfolio1.id, "from": "not-a-datetime", "to": "still-bad"},
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.json()), 3)



    def test_latest_snapshot(self):
        """
        GET latest snapshot for portfolio1
        """
        self.client.force_authenticate(self.user1)

        res = self.client.get(self.latest_url, {"portfolio": self.portfolio1.id})
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        snap = res.json()
        self.assertEqual(snap["portfolio"], self.portfolio1.id)
        # latest ts should be t3
        self.assertEqual(snap["ts"], self.t3.isoformat().replace("+00:00", "Z"))

    def test_latest_returns_404_if_none(self):
        """
        GET latest snapshot for a portfolio with no snapshots -> 404
        """
        self.client.force_authenticate(self.user1)

        # portfolio with no snapshots
        empty_portfolio = UserPortfolio.objects.create(
            user=self.profile1,
            name="EMPTY",
            balance=Decimal("10000.00"),
            is_active=True,
        )

        res = self.client.get(self.latest_url, {"portfolio": empty_portfolio.id})
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)



    def test_user_cannot_create_snapshot_for_other_portfolio(self):
        """
        User1 tries to create snapshot for portfolio2 (owned by user2) -> 403 Forbidden
        """
        self.client.force_authenticate(self.user1)

        payload = {
            "portfolio": self.portfolio2.id,  # portfolio owned by user2
            "ts": (timezone.now() - timedelta(minutes=5)).isoformat(),
            "cash_balance": "10000.00",
            "equity_value": "0.00",
            "total_value": "10000.00",
            "unrealized_pl": "0.00",
            "unrealized_pl_pct": "0.0000",
            "realized_pl": "0.00",
            "realized_pl_pct": "0.0000",
        }

        res = self.client.post(self.snapshots_url, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_executor_can_create_snapshot_any_portfolio(self):
        """
        Executor service can create snapshot for any portfolio.
        """
        self.client.force_authenticate(self.executor)

        t = timezone.now() - timedelta(minutes=5)

        payload = {
            "portfolio": self.portfolio1.id,
            "ts": t.isoformat(),
            "cash_balance": "7777.00",
            "equity_value": "333.00",
            "total_value": "8110.00",
            "unrealized_pl": "10.00",
            "unrealized_pl_pct": "0.1234",
            "realized_pl": "0.00",
            "realized_pl_pct": "0.0000",
        }

        res = self.client.post(self.snapshots_url, payload, format="json")
        self.assertIn(res.status_code, (status.HTTP_200_OK, status.HTTP_201_CREATED))

        self.assertTrue(
            PortfolioSnapshot.objects.filter(portfolio=self.portfolio1, ts=t).exists()
        )
