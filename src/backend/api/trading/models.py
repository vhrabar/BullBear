from django.db import models
from api.users.models import UserProfile as Profile, UserPortfolio as Portfolio
from rest_framework.utils import timezone


class Instrument(models.Model):
    """
    Represents a financial instrument such as a stock or ETF.
    """
    class InstrumentType(models.TextChoices):
        STOCK = "STOCK", "Stock"
        ETF = "ETF", "ETF"

    symbol = models.CharField(
        max_length=16,
        unique=True,
    )
    name = models.CharField(
        max_length=128,
    )
    type = models.CharField(
        max_length=10,
        choices=InstrumentType.choices,
    )
    exchange = models.CharField(
        max_length=32,
        blank=True,
    )
    currency = models.CharField(
        max_length=3,
        default="USD",
    )
    is_active = models.BooleanField(
        default=True,
    )

    def __str__(self):
        return f"{self.symbol} ({self.name})"


class InstrumentIntervalData(models.Model):
    """
    Stores aggregated market data for a 10-minute interval.
    Each record represents one 10-minute period for one instrument.
    """
    instrument = models.ForeignKey(
        Instrument,
        on_delete=models.CASCADE,
        related_name="interval_data"
    )
    start_time = models.DateTimeField(
        db_index=True,
    )
    end_time = models.DateTimeField(
    )

    # OHLCV data (Open, High, Low, Close, Volume)
    open_price = models.DecimalField(
        max_digits=20,
        decimal_places=6,
    )
    high_price = models.DecimalField(
        max_digits=20,
        decimal_places=6,
    )
    low_price = models.DecimalField(
        max_digits=20,
        decimal_places=6,
    )
    close_price = models.DecimalField(
        max_digits=20,
        decimal_places=6,
    )
    volume = models.BigIntegerField(
        null=True,
        blank=True,
    )

    data_source = models.CharField(
        max_length=64,
        blank=True,
    )
    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["-start_time"]
        indexes = [
            models.Index(fields=["instrument", "start_time"]),
        ]
        unique_together = ("instrument", "start_time")

    def __str__(self):
        return f"{self.instrument.symbol} [{self.start_time:%Y-%m-%d %H:%M}] = {self.close_price}"


class PortfolioHolding(models.Model):
    """Links an instrument to a portfolio with quantity and cost basis."""
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name="holdings")
    instrument = models.ForeignKey(Instrument, on_delete=models.CASCADE, related_name="holdings")
    quantity = models.DecimalField(max_digits=20, decimal_places=4, help_text="Number of shares or units owned")
    average_price = models.DecimalField(max_digits=20, decimal_places=6, help_text="Average purchase price per unit")
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("portfolio", "instrument")

    def __str__(self):
        return f"{self.instrument.symbol} x {self.quantity}"

    @property
    def current_value(self):
        """Calculates current market value based on the latest interval data."""
        latest_data = self.instrument.interval_data.order_by("-start_time").first()
        if latest_data:
            return latest_data.close_price * self.quantity
        return 0

    @property
    def profit_loss(self):
        """Returns unrealized profit or loss."""
        latest_data = self.instrument.interval_data.order_by("-start_time").first()
        if latest_data:
            return (latest_data.close_price - self.average_price) * self.quantity
        return 0


class InstrumentQuote(models.Model):
    instrument = models.CharField(max_length=50, db_index=True)

    bid_price = models.DecimalField(max_digits=12, decimal_places=6)
    bid_size = models.IntegerField(default=0)

    ask_price = models.DecimalField(max_digits=12, decimal_places=6)
    ask_size = models.IntegerField(default=0)

    last_price = models.DecimalField(max_digits=12, decimal_places=6)
    currency = models.CharField(max_length=10, default="USD")

    exchange = models.CharField(max_length=20, default="UNKNOWN")
    market_state = models.CharField(
        max_length=20,
        default="unknown",
        choices=[
            ("open", "Open"),
            ("closed", "Closed"),
            ("pre-market", "Pre-Market"),
            ("after-hours", "After Hours"),
            ("unknown", "Unknown"),
        ]
    )

    daily_change = models.DecimalField(max_digits=12, decimal_places=6, default=0)
    daily_change_percent = models.DecimalField(max_digits=6, decimal_places=3, default=0)

    timestamp = models.DateTimeField(auto_now=True)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.instrument} quote"