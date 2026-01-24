from decimal import Decimal

from django.test import TestCase
from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.test import APIClient

from api.users.models import UserPortfolio
from api.orders.models import Order, OrderFill, OrderEvent
from api.trading.models import Instrument, InstrumentQuote


User = get_user_model()


class OrderAPITests(TestCase):
    """
    Tests for Order CRUD operations:
    - GET /api/orders/orders/
    - GET /api/orders/orders/{id}/
    - POST /api/orders/orders/
    - PUT /api/orders/orders/{id}/
    - DELETE /api/orders/orders/{id}/
    - POST /api/orders/orders/{id}/cancel/
    - GET /api/orders/orders/open/ (service endpoint)
    - POST /api/orders/orders/{id}/execute/ (service endpoint)
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

        # Create executor service user
        self.executor = User.objects.create_user(
            username="executor",
            password="pass12345",
            email="executor@example.com",
            is_staff=True,
            is_superuser=True,
        )

        # Access profiles and portfolios
        self.profile1 = self.user1.profile
        self.profile2 = self.user2.profile
        self.portfolio1 = self.profile1.portfolios.first()
        self.portfolio2 = self.profile2.portfolios.first()

        # Create an instrument
        self.instrument = Instrument.objects.create(
            symbol="AAPL",
            name="Apple Inc.",
            type="STOCK",
            exchange="NASDAQ",
            is_active=True,
        )

        # Create a quote for the instrument
        self.quote = InstrumentQuote.objects.create(
            instrument=self.instrument,
            bid_price=Decimal("150.00"),
            ask_price=Decimal("150.50"),
            last_price=Decimal("150.25"),
        )

        self.url = "/api/orders/orders/"

    def auth(self, user):
        self.client.force_authenticate(user=user)

    def clear_auth(self):
        self.client.force_authenticate(user=None)

    def create_order(self, user=None, **kwargs):
        """Helper to create an order."""
        if user is None:
            user = self.user1
        profile = user.profile
        portfolio = profile.portfolios.first()

        defaults = {
            "user": profile,
            "portfolio": portfolio,
            "instrument": self.instrument,
            "side": Order.Side.BUY,
            "order_type": Order.OrderType.MARKET,
            "quantity": Decimal("10"),
            "status": Order.Status.OPEN,
        }
        defaults.update(kwargs)
        return Order.objects.create(**defaults)

    # Permission tests
    def test_unauthenticated_user_is_forbidden(self):
        """Unauthenticated user cannot access orders."""
        self.clear_auth()
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_user_can_list_orders(self):
        """Authenticated user can list their orders."""
        self.auth(self.user1)
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    # CRUD tests
    def test_create_market_order(self):
        """Create a new MARKET order."""
        self.auth(self.user1)
        payload = {
            "instrument_symbol": "AAPL",
            "side": "BUY",
            "order_type": "MARKET",
            "quantity": "10.00",
        }
        res = self.client.post(self.url, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.json()["side"], "BUY")
        self.assertEqual(res.json()["order_type"], "MARKET")
        self.assertEqual(Decimal(res.json()["quantity"]), Decimal("10.00"))

    def test_create_limit_order_requires_limit_price(self):
        """LIMIT order requires limit_price."""
        self.auth(self.user1)
        payload = {
            "instrument_symbol": "AAPL",
            "side": "BUY",
            "order_type": "LIMIT",
            "quantity": "10.00",
        }
        res = self.client.post(self.url, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_limit_order_with_limit_price(self):
        """LIMIT order with limit_price succeeds."""
        self.auth(self.user1)
        payload = {
            "instrument_symbol": "AAPL",
            "side": "BUY",
            "order_type": "LIMIT",
            "quantity": "10.00",
            "limit_price": "145.00",
        }
        res = self.client.post(self.url, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Decimal(res.json()["limit_price"]), Decimal("145.00"))

    def test_create_stop_order_requires_stop_price(self):
        """STOP order requires stop_price."""
        self.auth(self.user1)
        payload = {
            "instrument_symbol": "AAPL",
            "side": "SELL",
            "order_type": "STOP",
            "quantity": "10.00",
        }
        res = self.client.post(self.url, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_stop_limit_order(self):
        """STOP_LIMIT order requires both stop_price and limit_price."""
        self.auth(self.user1)
        payload = {
            "instrument_symbol": "AAPL",
            "side": "BUY",
            "order_type": "STOP_LIMIT",
            "quantity": "10.00",
            "stop_price": "155.00",
            "limit_price": "156.00",
        }
        res = self.client.post(self.url, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_list_only_own_orders(self):
        """User can only list their own orders."""
        self.create_order(user=self.user1)
        self.create_order(user=self.user2)

        self.auth(self.user1)
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        data = res.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["user"], self.profile1.id)

    def test_retrieve_own_order(self):
        """User can retrieve their own order."""
        order = self.create_order(user=self.user1)

        self.auth(self.user1)
        res = self.client.get(f"{self.url}{order.id}/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.json()["id"], order.id)

    # Cancel tests
    def test_cancel_order_via_delete(self):
        """DELETE cancels an open order."""
        order = self.create_order(user=self.user1, status=Order.Status.OPEN)

        self.auth(self.user1)
        res = self.client.delete(f"{self.url}{order.id}/")
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

        order.refresh_from_db()
        self.assertEqual(order.status, Order.Status.CANCELLED)
        self.assertIsNotNone(order.cancelled_at)

    def test_cancel_order_via_action(self):
        """POST /orders/{id}/cancel/ cancels an open order."""
        order = self.create_order(user=self.user1, status=Order.Status.OPEN)

        self.auth(self.user1)
        res = self.client.post(f"{self.url}{order.id}/cancel/", {"reason": "Changed my mind"})
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        order.refresh_from_db()
        self.assertEqual(order.status, Order.Status.CANCELLED)
        self.assertEqual(order.cancel_reason, "Changed my mind")

    def test_cannot_cancel_filled_order(self):
        """Cannot cancel a filled order."""
        order = self.create_order(user=self.user1, status=Order.Status.FILLED)

        self.auth(self.user1)
        res = self.client.delete(f"{self.url}{order.id}/")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cannot_cancel_cancelled_order(self):
        """Cannot cancel an already cancelled order."""
        order = self.create_order(user=self.user1, status=Order.Status.CANCELLED)

        self.auth(self.user1)
        res = self.client.post(f"{self.url}{order.id}/cancel/")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    # Service endpoint tests
    def test_open_orders_requires_executor(self):
        """GET /orders/open/ requires executor service user."""
        self.auth(self.user1)
        res = self.client.get(f"{self.url}open/")
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_open_orders_as_executor(self):
        """Executor can access open orders."""
        self.create_order(user=self.user1, status=Order.Status.OPEN)
        self.create_order(user=self.user2, status=Order.Status.PARTIALLY_FILLED)
        self.create_order(user=self.user1, status=Order.Status.FILLED)

        self.auth(self.executor)
        res = self.client.get(f"{self.url}open/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.json()), 2)  # Only OPEN and PARTIALLY_FILLED

    def test_execute_order_requires_executor(self):
        """POST /orders/{id}/execute/ requires executor service user."""
        order = self.create_order(user=self.user1, status=Order.Status.OPEN)

        self.auth(self.user1)
        res = self.client.post(f"{self.url}{order.id}/execute/")
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_execute_market_order_as_executor(self):
        """Executor can execute a MARKET order."""
        order = self.create_order(
            user=self.user1,
            status=Order.Status.OPEN,
            order_type=Order.OrderType.MARKET,
            quantity=Decimal("5"),
        )

        self.auth(self.executor)
        res = self.client.post(f"{self.url}{order.id}/execute/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        order.refresh_from_db()
        self.assertEqual(order.status, Order.Status.FILLED)
        self.assertEqual(order.filled_quantity, Decimal("5"))

    def test_execute_limit_order_condition_not_met(self):
        """LIMIT order not executed if price condition not met."""
        order = self.create_order(
            user=self.user1,
            status=Order.Status.OPEN,
            order_type=Order.OrderType.LIMIT,
            side=Order.Side.BUY,
            quantity=Decimal("5"),
            limit_price=Decimal("140.00"),  # Price is above current (150.25)
        )

        self.auth(self.executor)
        res = self.client.post(f"{self.url}{order.id}/execute/")
        self.assertEqual(res.status_code, status.HTTP_409_CONFLICT)
        self.assertIn("conditions not met", res.json()["detail"])

