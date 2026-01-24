from decimal import Decimal

from django.test import TestCase
from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.test import APIClient

from api.trading.models import Instrument


User = get_user_model()


class InstrumentAPITests(TestCase):
    """
    Tests for Instrument read-only operations:
    - GET /api/trading/instruments/
    - GET /api/trading/instruments/{symbol}/
    """

    def setUp(self):
        self.client = APIClient()

        self.instrument1 = Instrument.objects.create(
            symbol="AAPL",
            name="Apple Inc.",
            type="STOCK",
            exchange="NASDAQ",
            is_active=True,
        )
        self.instrument2 = Instrument.objects.create(
            symbol="GOOGL",
            name="Alphabet Inc.",
            type="STOCK",
            exchange="NASDAQ",
            is_active=True,
        )
        self.inactive_instrument = Instrument.objects.create(
            symbol="DEAD",
            name="Inactive Corp",
            type="STOCK",
            is_active=False,
        )

        self.url = "/api/trading/instruments/"

    def test_list_instruments_unauthenticated(self):
        """Instruments can be listed without authentication."""
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        symbols = [i["symbol"] for i in res.json()]
        self.assertIn("AAPL", symbols)
        self.assertIn("GOOGL", symbols)

    def test_list_excludes_inactive_instruments(self):
        """Inactive instruments are excluded from list."""
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        symbols = [i["symbol"] for i in res.json()]
        self.assertNotIn("DEAD", symbols)

    def test_retrieve_instrument_by_symbol(self):
        """Retrieve instrument by symbol."""
        res = self.client.get(f"{self.url}AAPL/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.json()["symbol"], "AAPL")
        self.assertEqual(res.json()["name"], "Apple Inc.")

    def test_retrieve_nonexistent_instrument_returns_404(self):
        """Retrieve nonexistent instrument returns 404."""
        res = self.client.get(f"{self.url}NONEXIST/")
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)