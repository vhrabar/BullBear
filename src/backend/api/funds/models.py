from decimal import Decimal
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models import Sum


class Fund(models.Model):
    """
    Creator-managed fund inside a user's portfolio.
    """
    creator_portfolio = models.ForeignKey(
        "users.UserPortfolio",
        on_delete=models.CASCADE,
        related_name="created_funds",
        help_text="Portfolio of the creator who manages this fund."
    )
    name = models.CharField(max_length=128)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    total_units = models.DecimalField(max_digits=20, decimal_places=6, default=0)
    nav_per_unit = models.DecimalField(max_digits=20, decimal_places=6, default=1)

    instruments = models.ManyToManyField(
        "trading.Instrument",
        through="FundHolding",
        related_name="funds"
    )

    class Meta:
        unique_together = ("creator_portfolio", "name")
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} [{self.creator_portfolio.name}]"

    def total_allocation(self):
        """
        Return sum of all FundHolding weights.
        """
        return self.holdings.aggregate(total=Sum("weight_percent"))["total"] or Decimal("0")


class FundHolding(models.Model):
    """
    Weighted allocation of an instrument in a fund.
    """
    fund = models.ForeignKey(
        Fund,
        on_delete=models.CASCADE,
        related_name="holdings",
    )
    instrument = models.ForeignKey(
        "trading.Instrument",
        on_delete=models.CASCADE,
        related_name="fund_holdings",
    )
    weight_percent = models.DecimalField(
        max_digits=6,
        decimal_places=3,
        validators=[
            MinValueValidator(Decimal("0.000")),
            MaxValueValidator(Decimal("100.000")),
        ],
        help_text="Percentage allocation of this instrument in the fund."
    )

    class Meta:
        unique_together = ("fund", "instrument")
        indexes = [
            models.Index(fields=["fund"]),
            models.Index(fields=["instrument"]),
        ]

    def __str__(self):
        return f"{self.fund.name}: {self.instrument.symbol} ({self.weight_percent}%)"


class FundSubscription(models.Model):
    """
    A user subscribes to a fund.
    """
    subscriber_portfolio = models.ForeignKey(
        "users.UserPortfolio",
        on_delete=models.CASCADE,
        related_name="fund_subscriptions",
        help_text="Portfolio that holds this subscription."
    )
    fund = models.ForeignKey(
        Fund,
        on_delete=models.CASCADE,
        related_name="subscriptions"
    )
    units = models.DecimalField(max_digits=20, decimal_places=6, default=0)
    invested_amount = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("subscriber_portfolio", "fund")

    def __str__(self):
        return f"{self.subscriber_portfolio.name}: {self.fund.name} ({self.units} units)"

