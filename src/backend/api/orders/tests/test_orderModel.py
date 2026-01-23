from decimal import Decimal

from django.test import TestCase
from django.contrib.auth import get_user_model

from api.users.models import UserPortfolio
from api.orders.models import Order, OrderFill, OrderEvent
from api.trading.models import Instrument, InstrumentQuote


User = get_user_model()

class OrderModelTests(TestCase):
    """
    Unit tests for Order model methods.
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
        )

    def test_remaining_quantity(self):
        """remaining_quantity property calculates correctly."""
        order = Order.objects.create(
            user=self.profile,
            portfolio=self.portfolio,
            instrument=self.instrument,
            side=Order.Side.BUY,
            order_type=Order.OrderType.MARKET,
            quantity=Decimal("10"),
            filled_quantity=Decimal("3"),
        )
        self.assertEqual(order.remaining_quantity, Decimal("7"))

    def test_apply_fill_partial(self):
        """apply_fill correctly updates partial fill."""
        order = Order.objects.create(
            user=self.profile,
            portfolio=self.portfolio,
            instrument=self.instrument,
            side=Order.Side.BUY,
            order_type=Order.OrderType.MARKET,
            quantity=Decimal("10"),
            status=Order.Status.OPEN,
        )

        order.apply_fill(Decimal("5"), Decimal("150.00"))

        self.assertEqual(order.filled_quantity, Decimal("5"))
        self.assertEqual(order.avg_fill_price, Decimal("150.00"))
        self.assertEqual(order.status, Order.Status.PARTIALLY_FILLED)

    def test_apply_fill_complete(self):
        """apply_fill correctly updates complete fill."""
        order = Order.objects.create(
            user=self.profile,
            portfolio=self.portfolio,
            instrument=self.instrument,
            side=Order.Side.BUY,
            order_type=Order.OrderType.MARKET,
            quantity=Decimal("10"),
            status=Order.Status.OPEN,
        )

        order.apply_fill(Decimal("10"), Decimal("150.00"))

        self.assertEqual(order.filled_quantity, Decimal("10"))
        self.assertEqual(order.status, Order.Status.FILLED)
        self.assertIsNotNone(order.closed_at)

    def test_apply_fill_weighted_average_price(self):
        """apply_fill correctly calculates weighted average price."""
        order = Order.objects.create(
            user=self.profile,
            portfolio=self.portfolio,
            instrument=self.instrument,
            side=Order.Side.BUY,
            order_type=Order.OrderType.MARKET,
            quantity=Decimal("10"),
            status=Order.Status.OPEN,
        )

        order.apply_fill(Decimal("4"), Decimal("100.00"))  # 4 @ 100 = 400
        order.apply_fill(Decimal("6"), Decimal("150.00"))  # 6 @ 150 = 900

        # Total: 10 shares, cost = 1300, avg = 130
        self.assertEqual(order.filled_quantity, Decimal("10"))
        self.assertEqual(order.avg_fill_price, Decimal("130.00"))

    def test_is_executable_at_price_market_order(self):
        """MARKET orders are always executable."""
        order = Order.objects.create(
            user=self.profile,
            portfolio=self.portfolio,
            instrument=self.instrument,
            side=Order.Side.BUY,
            order_type=Order.OrderType.MARKET,
            quantity=Decimal("10"),
        )
        self.assertTrue(order.is_executable_at_price(Decimal("999.99")))

    def test_is_executable_at_price_limit_buy(self):
        """LIMIT BUY executes when price <= limit_price."""
        order = Order.objects.create(
            user=self.profile,
            portfolio=self.portfolio,
            instrument=self.instrument,
            side=Order.Side.BUY,
            order_type=Order.OrderType.LIMIT,
            quantity=Decimal("10"),
            limit_price=Decimal("150.00"),
        )
        self.assertTrue(order.is_executable_at_price(Decimal("149.00")))
        self.assertTrue(order.is_executable_at_price(Decimal("150.00")))
        self.assertFalse(order.is_executable_at_price(Decimal("151.00")))

    def test_is_executable_at_price_limit_sell(self):
        """LIMIT SELL executes when price >= limit_price."""
        order = Order.objects.create(
            user=self.profile,
            portfolio=self.portfolio,
            instrument=self.instrument,
            side=Order.Side.SELL,
            order_type=Order.OrderType.LIMIT,
            quantity=Decimal("10"),
            limit_price=Decimal("150.00"),
        )
        self.assertTrue(order.is_executable_at_price(Decimal("151.00")))
        self.assertTrue(order.is_executable_at_price(Decimal("150.00")))
        self.assertFalse(order.is_executable_at_price(Decimal("149.00")))

    def test_is_executable_at_price_stop_buy(self):
        """STOP BUY executes when price >= stop_price."""
        order = Order.objects.create(
            user=self.profile,
            portfolio=self.portfolio,
            instrument=self.instrument,
            side=Order.Side.BUY,
            order_type=Order.OrderType.STOP,
            quantity=Decimal("10"),
            stop_price=Decimal("160.00"),
        )
        self.assertTrue(order.is_executable_at_price(Decimal("161.00")))
        self.assertTrue(order.is_executable_at_price(Decimal("160.00")))
        self.assertFalse(order.is_executable_at_price(Decimal("159.00")))

    def test_is_executable_at_price_stop_sell(self):
        """STOP SELL executes when price <= stop_price."""
        order = Order.objects.create(
            user=self.profile,
            portfolio=self.portfolio,
            instrument=self.instrument,
            side=Order.Side.SELL,
            order_type=Order.OrderType.STOP,
            quantity=Decimal("10"),
            stop_price=Decimal("140.00"),
        )
        self.assertTrue(order.is_executable_at_price(Decimal("139.00")))
        self.assertTrue(order.is_executable_at_price(Decimal("140.00")))
        self.assertFalse(order.is_executable_at_price(Decimal("141.00")))
