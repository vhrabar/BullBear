from decimal import Decimal

from django.test import TestCase
from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.test import APIClient

from api.trading.models import Instrument, InstrumentQuote


User = get_user_model()


class InstrumentQuoteAPITests(TestCase):
    """
    Tests for InstrumentQuote operations:
    - GET /api/trading/latest-instrument-quote/{symbol}/quote/
    """

    def setUp(self):
        self.client = APIClient()

        self.instrument = Instrument.objects.create(
            symbol="AAPL",
            name="Apple Inc.",
            type="STOCK",
            is_active=True,
        )

        self.quote = InstrumentQuote.objects.create(
            instrument=self.instrument,
            bid_price=Decimal("150.00"),
            bid_size=1000,
            ask_price=Decimal("150.50"),
            ask_size=800,
            last_price=Decimal("150.25"),
            daily_change=Decimal("2.25"),
            daily_change_percent=Decimal("1.52"),
        )

        self.url = "/api/trading/latest-instrument-quote/"

    def test_get_quote_by_symbol(self):
        """Get quote for instrument by symbol."""
        res = self.client.get(f"{self.url}AAPL/quote/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        data = res.json()
        self.assertEqual(Decimal(data["bid_price"]), Decimal("150.00"))
        self.assertEqual(Decimal(data["ask_price"]), Decimal("150.50"))
        self.assertEqual(Decimal(data["last_price"]), Decimal("150.25"))

    def test_get_quote_nonexistent_returns_404(self):
        """Get quote for nonexistent symbol returns 404."""
        res = self.client.get(f"{self.url}NONEXIST/quote/")
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
