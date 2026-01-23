from decimal import Decimal
from datetime import timedelta

from django.test import TestCase
from django.utils import timezone
from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.test import APIClient

from api.trading.models import Instrument, InstrumentIntervalData


User = get_user_model()


class InstrumentIntervalDataAPITests(TestCase):
    """
    Tests for InstrumentIntervalData read-only operations:
    - GET /api/trading/instrument-data/
    - GET /api/trading/instrument-data/?instrument=<symbol>
    """

    def setUp(self):
        self.client = APIClient()

        self.instrument = Instrument.objects.create(
            symbol="AAPL",
            name="Apple Inc.",
            type="STOCK",
            is_active=True,
        )
        self.instrument2 = Instrument.objects.create(
            symbol="GOOGL",
            name="Alphabet Inc.",
            type="STOCK",
            is_active=True,
        )

        now = timezone.now()
        InstrumentIntervalData.objects.create(
            instrument=self.instrument,
            start_time=now - timedelta(minutes=20),
            end_time=now - timedelta(minutes=10),
            open_price=Decimal("150.00"),
            high_price=Decimal("152.00"),
            low_price=Decimal("149.00"),
            close_price=Decimal("151.00"),
            volume=1000000,
        )
        InstrumentIntervalData.objects.create(
            instrument=self.instrument,
            start_time=now - timedelta(minutes=10),
            end_time=now,
            open_price=Decimal("151.00"),
            high_price=Decimal("153.00"),
            low_price=Decimal("150.50"),
            close_price=Decimal("152.50"),
            volume=1200000,
        )
        InstrumentIntervalData.objects.create(
            instrument=self.instrument2,
            start_time=now - timedelta(minutes=10),
            end_time=now,
            open_price=Decimal("2800.00"),
            high_price=Decimal("2850.00"),
            low_price=Decimal("2790.00"),
            close_price=Decimal("2840.00"),
            volume=500000,
        )

        self.url = "/api/trading/instrument-data/"

    def test_list_all_interval_data(self):
        """List all interval data without filter."""
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.json()), 3)

    def test_filter_by_instrument(self):
        """Filter interval data by instrument symbol."""
        res = self.client.get(f"{self.url}?instrument=AAPL")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        data = res.json()
        self.assertEqual(len(data), 2)
        for item in data:
            self.assertIn("AAPL", item["instrument"])