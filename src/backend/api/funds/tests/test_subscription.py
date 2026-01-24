from decimal import Decimal

from django.test import TestCase
from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.test import APIClient

from api.users.models import UserPortfolio
from api.funds.models import Fund, FundHolding, FundSubscription, FundNAVHistory
from api.trading.models import Instrument

User = get_user_model()


class FundSubscriptionAPITests(TestCase):
    """
    Tests for FundSubscription CRUD operations:
    - GET /api/funds/subscriptions/
    - GET /api/funds/subscriptions/{id}/
    - POST /api/funds/subscriptions/
    - PATCH /api/funds/subscriptions/{id}/
    - DELETE /api/funds/subscriptions/{id}/
    - GET /api/funds/subscriptions/unsubscribed/
    - GET /api/funds/subscriptions/by-fund/{fund_id}/
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

        # Create a fund owned by user2
        self.fund = Fund.objects.create(
            creator_portfolio=self.portfolio2,
            name="Test Fund",
            description="A fund by user2",
            nav_per_unit=Decimal("10.00"),
        )

        self.url = "/api/funds/subscriptions/"

    def auth(self, user):
        self.client.force_authenticate(user=user)

    def clear_auth(self):
        self.client.force_authenticate(user=None)

    # Permission tests
    def test_unauthenticated_user_is_forbidden(self):
        """Unauthenticated user cannot access subscriptions."""
        self.clear_auth()
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_user_can_list_subscriptions(self):
        """Authenticated user can list their subscriptions."""
        self.auth(self.user1)
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    # CRUD tests
    def test_create_subscription(self):
        """Create a new subscription."""
        self.auth(self.user1)
        payload = {
            "subscriber_portfolio": self.portfolio1.id,
            "fund": self.fund.id,
            "invested_amount": "100.00",
        }
        res = self.client.post(self.url, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.json()["fund"], self.fund.id)

    def test_list_only_own_subscriptions(self):
        """User can only list their own subscriptions."""
        # Create subscription for user1
        FundSubscription.objects.create(
            subscriber_portfolio=self.portfolio1,
            fund=self.fund,
            invested_amount=Decimal("100.00"),
        )

        self.auth(self.user1)
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        data = res.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["subscriber_portfolio"], self.portfolio1.id)

    def test_update_subscription(self):
        """User can update their subscription."""
        subscription = FundSubscription.objects.create(
            subscriber_portfolio=self.portfolio1,
            fund=self.fund,
            invested_amount=Decimal("100.00"),
        )

        self.auth(self.user1)
        payload = {
            "subscriber_portfolio": self.portfolio1.id,
            "fund": self.fund.id,
            "invested_amount": "200.00",
        }
        res = self.client.patch(f"{self.url}{subscription.id}/", payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_delete_subscription(self):
        """User can delete (unsubscribe) their subscription."""
        subscription = FundSubscription.objects.create(
            subscriber_portfolio=self.portfolio1,
            fund=self.fund,
            invested_amount=Decimal("100.00"),
        )

        self.auth(self.user1)
        res = self.client.delete(f"{self.url}{subscription.id}/")
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(FundSubscription.objects.filter(id=subscription.id).exists())

    # Unsubscribed endpoint tests
    def test_unsubscribed_returns_funds_not_subscribed_to(self):
        """GET /api/funds/subscriptions/unsubscribed/ returns funds user is not subscribed to."""
        # Create another fund that user1 is not subscribed to
        other_fund = Fund.objects.create(
            creator_portfolio=self.portfolio2,
            name="Other Fund",
            is_active=True,
        )

        # Subscribe user1 to the first fund
        FundSubscription.objects.create(
            subscriber_portfolio=self.portfolio1,
            fund=self.fund,
            invested_amount=Decimal("100.00"),
        )

        self.auth(self.user1)
        res = self.client.get(f"{self.url}unsubscribed/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        fund_ids = [f["id"] for f in res.json()]
        self.assertIn(other_fund.id, fund_ids)
        self.assertNotIn(self.fund.id, fund_ids)

    def test_unsubscribed_excludes_own_funds(self):
        """Unsubscribed endpoint excludes user's own funds."""
        # Create a fund owned by user1
        own_fund = Fund.objects.create(
            creator_portfolio=self.portfolio1,
            name="My Own Fund",
            is_active=True,
        )

        self.auth(self.user1)
        res = self.client.get(f"{self.url}unsubscribed/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        fund_ids = [f["id"] for f in res.json()]
        self.assertNotIn(own_fund.id, fund_ids)

    # By-fund endpoint tests
    def test_by_fund_returns_subscription(self):
        """GET /api/funds/subscriptions/by-fund/{fund_id}/ returns user's subscription."""
        subscription = FundSubscription.objects.create(
            subscriber_portfolio=self.portfolio1,
            fund=self.fund,
            invested_amount=Decimal("100.00"),
        )

        self.auth(self.user1)
        res = self.client.get(f"{self.url}by-fund/{self.fund.id}/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.json()["id"], subscription.id)

    def test_by_fund_returns_404_if_not_subscribed(self):
        """By-fund endpoint returns 404 if user is not subscribed."""
        self.auth(self.user1)
        res = self.client.get(f"{self.url}by-fund/{self.fund.id}/")
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
