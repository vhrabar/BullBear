from decimal import Decimal
from datetime import timedelta

from django.test import TestCase
from django.utils import timezone
from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.test import APIClient

from api.users.models import UserPortfolio
from api.funds.models import Fund, FundHolding, FundSubscription, FundNAVHistory
from api.trading.models import Instrument


User = get_user_model()


class FundAPITests(TestCase):
    """
    Tests for Fund CRUD operations:
    - GET /api/funds/funds/
    - GET /api/funds/funds/{id}/
    - POST /api/funds/funds/
    - PUT /api/funds/funds/{id}/
    - DELETE /api/funds/funds/{id}/
    - GET /api/funds/funds/all/
    - GET /api/funds/funds/{id}/performance/
    """

    def setUp(self):
        self.client = APIClient()

        # Create users
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

        # Access profiles and portfolios
        self.profile1 = self.user1.profile
        self.profile2 = self.user2.profile
        self.portfolio1 = self.profile1.portfolios.first()
        self.portfolio2 = self.profile2.portfolios.first()

        # Create an instrument for holdings
        self.instrument = Instrument.objects.create(
            symbol="AAPL",
            name="Apple Inc.",
            type="STOCK",
            exchange="NASDAQ",
            is_active=True,
        )

        self.url = "/api/funds/funds/"

    def auth(self, user):
        self.client.force_authenticate(user=user)

    def clear_auth(self):
        self.client.force_authenticate(user=None)

    # Permission tests
    def test_unauthenticated_user_is_forbidden(self):
        """Unauthenticated user cannot access funds."""
        self.clear_auth()
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_user_can_list_own_funds(self):
        """Authenticated user can list their own funds."""
        self.auth(self.user1)
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    # CRUD tests
    def test_create_fund(self):
        """Create a new fund."""
        self.auth(self.user1)
        payload = {
            "creator_portfolio": self.portfolio1.id,
            "name": "Test Fund",
            "description": "A test fund",
            "holdings": [
                {"instrument": self.instrument.id, "weight_percent": "50.000"}
            ]
        }
        res = self.client.post(self.url, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.json()["name"], "Test Fund")
        self.assertEqual(len(res.json()["holdings"]), 1)

    def test_create_fund_without_holdings(self):
        """Create a fund without initial holdings."""
        self.auth(self.user1)
        payload = {
            "creator_portfolio": self.portfolio1.id,
            "name": "Empty Fund",
            "description": "Fund without holdings",
        }
        res = self.client.post(self.url, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.json()["holdings"], [])

    def test_list_only_own_funds(self):
        """User can only list their own funds."""
        # Create fund for user1
        Fund.objects.create(
            creator_portfolio=self.portfolio1,
            name="User1 Fund",
            description="Belongs to user1",
        )
        # Create fund for user2
        Fund.objects.create(
            creator_portfolio=self.portfolio2,
            name="User2 Fund",
            description="Belongs to user2",
        )

        self.auth(self.user1)
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        data = res.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["name"], "User1 Fund")

    def test_retrieve_any_fund_by_id(self):
        """User can retrieve any fund by ID (for viewing)."""
        fund = Fund.objects.create(
            creator_portfolio=self.portfolio2,
            name="Other User Fund",
            description="Belongs to user2",
        )

        self.auth(self.user1)
        res = self.client.get(f"{self.url}{fund.id}/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.json()["name"], "Other User Fund")

    def test_retrieve_nonexistent_fund_returns_404(self):
        """Retrieving a non-existent fund returns 404."""
        self.auth(self.user1)
        res = self.client.get(f"{self.url}99999/")
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_own_fund(self):
        """Owner can update their fund."""
        fund = Fund.objects.create(
            creator_portfolio=self.portfolio1,
            name="My Fund",
            description="Original description",
        )

        self.auth(self.user1)
        payload = {
            "creator_portfolio": self.portfolio1.id,
            "name": "My Fund Updated",
            "description": "Updated description",
            "holdings": []
        }
        res = self.client.put(f"{self.url}{fund.id}/", payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.json()["name"], "My Fund Updated")

    def test_delete_own_fund(self):
        """Owner can delete their fund."""
        fund = Fund.objects.create(
            creator_portfolio=self.portfolio1,
            name="To Delete",
            description="Will be deleted",
        )

        self.auth(self.user1)
        res = self.client.delete(f"{self.url}{fund.id}/")
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Fund.objects.filter(id=fund.id).exists())

    # All funds endpoint tests
    def test_all_funds_returns_active_funds(self):
        """GET /api/funds/funds/all/ returns all active funds."""
        Fund.objects.create(
            creator_portfolio=self.portfolio1,
            name="Active Fund 1",
            is_active=True,
        )
        Fund.objects.create(
            creator_portfolio=self.portfolio2,
            name="Active Fund 2",
            is_active=True,
        )
        Fund.objects.create(
            creator_portfolio=self.portfolio1,
            name="Inactive Fund",
            is_active=False,
        )

        self.auth(self.user1)
        res = self.client.get(f"{self.url}all/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        names = [f["name"] for f in res.json()]
        self.assertIn("Active Fund 1", names)
        self.assertIn("Active Fund 2", names)
        self.assertNotIn("Inactive Fund", names)

    # Performance endpoint tests
    def test_performance_returns_nav_history(self):
        """GET /api/funds/funds/{id}/performance/ returns NAV history."""
        fund = Fund.objects.create(
            creator_portfolio=self.portfolio1,
            name="Performance Fund",
        )
        now = timezone.now()
        nav1 = FundNAVHistory.objects.create(
            fund=fund,
            nav_per_unit=Decimal("10.00"),
            total_units=Decimal("100.00"),
        )
        FundNAVHistory.objects.filter(pk=nav1.pk).update(recorded_at=now - timedelta(days=5))
        nav2 = FundNAVHistory.objects.create(
            fund=fund,
            nav_per_unit=Decimal("10.50"),
            total_units=Decimal("100.00"),
        )
        FundNAVHistory.objects.filter(pk=nav2.pk).update(recorded_at=now - timedelta(days=2))

        self.auth(self.user1)
        res = self.client.get(f"{self.url}{fund.id}/performance/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.json()), 2)

    def test_performance_filters_by_days(self):
        """Performance endpoint respects days query param."""
        fund = Fund.objects.create(
            creator_portfolio=self.portfolio1,
            name="Performance Fund 2",
        )
        now = timezone.now()
        nav1 = FundNAVHistory.objects.create(
            fund=fund,
            nav_per_unit=Decimal("10.00"),
            total_units=Decimal("100.00"),
        )
        # Set recorded_at to 45 days ago using update() since auto_now_add ignores provided values
        FundNAVHistory.objects.filter(pk=nav1.pk).update(recorded_at=now - timedelta(days=45))

        nav2 = FundNAVHistory.objects.create(
            fund=fund,
            nav_per_unit=Decimal("10.50"),
            total_units=Decimal("100.00"),
        )
        FundNAVHistory.objects.filter(pk=nav2.pk).update(recorded_at=now - timedelta(days=5))

        self.auth(self.user1)
        # Default 30 days should exclude the old record
        res = self.client.get(f"{self.url}{fund.id}/performance/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.json()), 1)

        # 60 days should include both
        res = self.client.get(f"{self.url}{fund.id}/performance/?days=60")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.json()), 2)
