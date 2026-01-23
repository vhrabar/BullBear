from decimal import Decimal
from datetime import timedelta

from django.test import TestCase
from django.utils import timezone
from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.test import APIClient

from api.trading.models import Instrument, InstrumentIntervalData, PortfolioHolding
from api.trading.services import buy_instrument, sell_instrument


User = get_user_model()


class BuySellAPITests(TestCase):
    """
    Tests for Buy/Sell API endpoints:
    - POST /api/trading/buy
    - POST /api/trading/sell
    """

    def setUp(self):
        self.client = APIClient()

        self.user1 = User.objects.create_user(
            username="user1",
            password="pass12345",
            email="user1@example.com",
        )

        self.profile1 = self.user1.profile
        self.portfolio1 = self.profile1.portfolios.first()
        # Ensure sufficient balance
        self.portfolio1.balance = Decimal("100000.00")
        self.portfolio1.save()

        self.instrument = Instrument.objects.create(
            symbol="AAPL",
            name="Apple Inc.",
            type="STOCK",
            is_active=True,
        )

        # Create market data for price lookup
        now = timezone.now()
        InstrumentIntervalData.objects.create(
            instrument=self.instrument,
            start_time=now - timedelta(minutes=10),
            end_time=now,
            open_price=Decimal("150.00"),
            high_price=Decimal("152.00"),
            low_price=Decimal("149.00"),
            close_price=Decimal("150.00"),
        )

        self.buy_url = "/api/trading/buy"
        self.sell_url = "/api/trading/sell"

    def auth(self, user):
        self.client.force_authenticate(user=user)

    def test_buy_instrument(self):
        """Buy instrument creates holding."""
        self.auth(self.user1)
        payload = {
            "instrument_symbol": "AAPL",
            "quantity": "10",
            "portfolio_id": self.portfolio1.id,
        }
        res = self.client.post(self.buy_url, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        holding = PortfolioHolding.objects.get(
            portfolio=self.portfolio1,
            instrument=self.instrument,
        )
        self.assertEqual(holding.quantity, Decimal("10"))

    def test_buy_instrument_with_explicit_price(self):
        """Buy instrument with explicit price."""
        self.auth(self.user1)
        payload = {
            "instrument_symbol": "AAPL",
            "quantity": "5",
            "price": "155.00",
            "portfolio_id": self.portfolio1.id,
        }
        res = self.client.post(self.buy_url, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        holding = PortfolioHolding.objects.get(
            portfolio=self.portfolio1,
            instrument=self.instrument,
        )
        self.assertEqual(holding.quantity, Decimal("5"))
        self.assertEqual(holding.average_price, Decimal("155.00"))

    def test_sell_instrument(self):
        """Sell instrument reduces holding."""
        # First create a holding
        PortfolioHolding.objects.create(
            portfolio=self.portfolio1,
            instrument=self.instrument,
            quantity=Decimal("20"),
            average_price=Decimal("145.00"),
        )

        self.auth(self.user1)
        payload = {
            "instrument_symbol": "AAPL",
            "quantity": "10",
            "portfolio_id": self.portfolio1.id,
        }
        res = self.client.post(self.sell_url, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        holding = PortfolioHolding.objects.get(
            portfolio=self.portfolio1,
            instrument=self.instrument,
        )
        self.assertEqual(holding.quantity, Decimal("10"))

    def test_sell_more_than_owned_fails(self):
        """Cannot sell more than owned."""
        PortfolioHolding.objects.create(
            portfolio=self.portfolio1,
            instrument=self.instrument,
            quantity=Decimal("5"),
            average_price=Decimal("145.00"),
        )

        self.auth(self.user1)
        payload = {
            "instrument_symbol": "AAPL",
            "quantity": "10",
            "portfolio_id": self.portfolio1.id,
        }
        res = self.client.post(self.sell_url, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)


class BuySellServiceTests(TestCase):
    """
    Unit tests for buy_instrument and sell_instrument services.
    """

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="pass12345",
            email="test@example.com",
        )
        self.profile = self.user.profile
        self.portfolio = self.profile.portfolios.first()
        self.portfolio.balance = Decimal("50000.00")
        self.portfolio.save()

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
            close_price=Decimal("150.00"),
        )

    def test_buy_creates_new_holding(self):
        """buy_instrument creates a new holding."""
        holding = buy_instrument(
            portfolio=self.portfolio,
            instrument_symbol="AAPL",
            quantity=Decimal("10"),
            price=Decimal("150.00"),
        )
        self.assertEqual(holding.quantity, Decimal("10"))
        self.assertEqual(holding.average_price, Decimal("150.00"))

    def test_buy_updates_existing_holding(self):
        """buy_instrument updates existing holding with weighted average."""
        # First buy
        buy_instrument(
            portfolio=self.portfolio,
            instrument_symbol="AAPL",
            quantity=Decimal("10"),
            price=Decimal("100.00"),
        )
        # Second buy
        holding = buy_instrument(
            portfolio=self.portfolio,
            instrument_symbol="AAPL",
            quantity=Decimal("10"),
            price=Decimal("200.00"),
        )
        # 10 @ 100 = 1000, 10 @ 200 = 2000, total = 3000, avg = 150
        self.assertEqual(holding.quantity, Decimal("20"))
        self.assertEqual(holding.average_price, Decimal("150.00"))

    def test_buy_deducts_balance(self):
        """buy_instrument deducts from portfolio balance."""
        initial_balance = self.portfolio.balance
        buy_instrument(
            portfolio=self.portfolio,
            instrument_symbol="AAPL",
            quantity=Decimal("10"),
            price=Decimal("100.00"),
        )
        self.portfolio.refresh_from_db()
        expected_balance = initial_balance - Decimal("1000.00")
        self.assertEqual(self.portfolio.balance, expected_balance)

    def test_buy_insufficient_balance_fails(self):
        """buy_instrument fails with insufficient balance."""
        self.portfolio.balance = Decimal("100.00")
        self.portfolio.save()

        with self.assertRaises(Exception):
            buy_instrument(
                portfolio=self.portfolio,
                instrument_symbol="AAPL",
                quantity=Decimal("10"),
                price=Decimal("150.00"),  # Cost: 1500
            )

    def test_sell_reduces_holding(self):
        """sell_instrument reduces holding quantity."""
        # Create holding first
        PortfolioHolding.objects.create(
            portfolio=self.portfolio,
            instrument=self.instrument,
            quantity=Decimal("20"),
            average_price=Decimal("145.00"),
        )

        holding = sell_instrument(
            portfolio=self.portfolio,
            instrument_symbol="AAPL",
            quantity=Decimal("10"),
            price=Decimal("160.00"),
        )
        self.assertEqual(holding.quantity, Decimal("10"))

    def test_sell_adds_to_balance(self):
        """sell_instrument adds to portfolio balance."""
        PortfolioHolding.objects.create(
            portfolio=self.portfolio,
            instrument=self.instrument,
            quantity=Decimal("20"),
            average_price=Decimal("145.00"),
        )
        initial_balance = self.portfolio.balance

        sell_instrument(
            portfolio=self.portfolio,
            instrument_symbol="AAPL",
            quantity=Decimal("10"),
            price=Decimal("160.00"),
        )
        self.portfolio.refresh_from_db()
        expected_balance = initial_balance + Decimal("1600.00")
        self.assertEqual(self.portfolio.balance, expected_balance)

    def test_sell_no_holding_fails(self):
        """sell_instrument fails if no holding exists."""
        with self.assertRaises(Exception):
            sell_instrument(
                portfolio=self.portfolio,
                instrument_symbol="AAPL",
                quantity=Decimal("10"),
            )

    def test_sell_insufficient_quantity_fails(self):
        """sell_instrument fails if insufficient quantity."""
        PortfolioHolding.objects.create(
            portfolio=self.portfolio,
            instrument=self.instrument,
            quantity=Decimal("5"),
            average_price=Decimal("145.00"),
        )

        with self.assertRaises(Exception):
            sell_instrument(
                portfolio=self.portfolio,
                instrument_symbol="AAPL",
                quantity=Decimal("10"),
            )
