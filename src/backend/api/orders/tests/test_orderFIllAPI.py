from decimal import Decimal

from django.test import TestCase
from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.test import APIClient

from api.users.models import UserPortfolio
from api.orders.models import Order, OrderFill, OrderEvent
from api.trading.models import Instrument, InstrumentQuote


User = get_user_model()

class OrderFillAPITests(TestCase):
    """
    Tests for OrderFill read-only operations:
    - GET /api/orders/order-fills/
    - GET /api/orders/order-fills/{id}/
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
        )

        self.order = Order.objects.create(
            user=self.profile1,
            portfolio=self.portfolio1,
            instrument=self.instrument,
            side=Order.Side.BUY,
            order_type=Order.OrderType.MARKET,
            quantity=Decimal("10"),
            status=Order.Status.FILLED,
        )

        self.fill = OrderFill.objects.create(
            order=self.order,
            quantity=Decimal("10"),
            price=Decimal("150.00"),
        )

        self.url = "/api/orders/order-fills/"

    def auth(self, user):
        self.client.force_authenticate(user=user)

    def test_unauthenticated_user_is_forbidden(self):
        """Unauthenticated user cannot access order fills."""
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_own_order_fills(self):
        """User can list fills for their own orders."""
        self.auth(self.user1)
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
