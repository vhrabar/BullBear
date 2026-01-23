from decimal import Decimal

from django.test import TestCase
from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.test import APIClient

from api.users.models import UserPortfolio
from api.orders.models import Order, OrderFill, OrderEvent
from api.trading.models import Instrument, InstrumentQuote


User = get_user_model()

class OrderEventAPITests(TestCase):
    """
    Tests for OrderEvent read-only operations:
    - GET /api/orders/order-events/
    - GET /api/orders/order-events/{id}/
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
            status=Order.Status.OPEN,
        )

        self.event = OrderEvent.objects.create(
            order=self.order,
            type=OrderEvent.EventType.CREATED,
            message="Order created.",
        )

        self.url = "/api/orders/order-events/"

    def auth(self, user):
        self.client.force_authenticate(user=user)

    def test_unauthenticated_user_is_forbidden(self):
        """Unauthenticated user cannot access order events."""
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_own_order_events(self):
        """User can list events for their own orders."""
        self.auth(self.user1)
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        data = res.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["type"], "CREATED")
