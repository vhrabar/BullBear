from decimal import Decimal
from datetime import timedelta

from django.test import TestCase
from django.utils import timezone
from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.test import APIClient

from api.trading.models import Instrument, InstrumentIntervalData, PortfolioHolding


User = get_user_model()


class PortfolioHoldingAPITests(TestCase):
    """
    Tests for PortfolioHolding operations:
    - GET /api/trading/portfolio-holdings/
    """

    def setUp(self):
        self.client = APIClient()

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

        self.profile1 = self.user1.profile
        self.profile2 = self.user2.profile
        self.portfolio1 = self.profile1.portfolios.first()
        self.portfolio2 = self.profile2.portfolios.first()

        self.instrument = Instrument.objects.create(
            symbol="AAPL",
            name="Apple Inc.",
            type="STOCK",
            is_active=True,
        )

        self.holding = PortfolioHolding.objects.create(
            portfolio=self.portfolio1,
            instrument=self.instrument,
            quantity=Decimal("10"),
            average_price=Decimal("150.00"),
        )

        self.url = "/api/trading/portfolio-holdings/"

    def auth(self, user):
        self.client.force_authenticate(user=user)

    def test_unauthenticated_user_is_forbidden(self):
        """Unauthenticated user cannot access holdings."""
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_own_holdings(self):
        """User can list their own holdings."""
        self.auth(self.user1)
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        data = res.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(Decimal(data[0]["quantity"]), Decimal("10"))

    def test_cannot_see_other_user_holdings(self):
        """User cannot see other user's holdings."""
        self.auth(self.user2)
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.json()), 0)

    class PortfolioHoldingModelTests(TestCase):
        """
        Unit tests for PortfolioHolding model properties.
        """

        def setUp(self):
            self.user = User.objects.create_user(
                username="testuser",
                password="pass12345",
                email="test@example.com",
            )
            self.profile = self.user.profile
            self.portfolio = self.profile.portfolios.first()

            self.instrument = Instrument.objects.create(
                symbol="AAPL",
                name="Apple Inc.",
                type="STOCK",
                is_active=True,
            )

            now = timezone.now()
            InstrumentIntervalData.objects.create(
                instrument=self.instrument,
                start_time=now - timedelta(minutes=10),
                end_time=now,
                open_price=Decimal("150.00"),
                high_price=Decimal("152.00"),
                low_price=Decimal("149.00"),
                close_price=Decimal("160.00"),  # Current price
            )

            self.holding = PortfolioHolding.objects.create(
                portfolio=self.portfolio,
                instrument=self.instrument,
                quantity=Decimal("10"),
                average_price=Decimal("150.00"),
            )

        def test_current_value_property(self):
            """current_value calculates based on latest close price."""
            # 10 shares * 160 = 1600
            self.assertEqual(self.holding.current_value, Decimal("1600.00"))

        def test_profit_loss_property(self):
            """profit_loss calculates unrealized P/L."""
            # (160 - 150) * 10 = 100
            self.assertEqual(self.holding.profit_loss, Decimal("100.00"))

        def test_current_value_no_data(self):
            """current_value returns 0 if no market data."""
            instrument2 = Instrument.objects.create(
                symbol="NODA",
                name="No Data Corp",
                type="STOCK",
            )
            holding2 = PortfolioHolding.objects.create(
                portfolio=self.portfolio,
                instrument=instrument2,
                quantity=Decimal("10"),
                average_price=Decimal("100.00"),
            )
            self.assertEqual(holding2.current_value, 0)
