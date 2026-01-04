from decimal import Decimal
from django.db import models
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from .models import Fund, FundHolding


def validate_fund_holdings(fund: Fund):
    """
    Ensure that all holdings for a fund sum to exactly 100%.
    """
    total = fund.holdings.aggregate(total=models.Sum('weight_percent'))['total'] or Decimal("0")
    if total != Decimal("100.000"):
        raise ValidationError(
            f"Fund '{fund.name}' holdings must sum to 100%. Current sum: {total}%."
        )


@receiver(post_save, sender=FundHolding)
@receiver(post_delete, sender=FundHolding)
def fund_holdings_changed(sender, instance, **kwargs):
    """
    Trigger validation whenever a FundHolding is saved or deleted.
    """
    fund = instance.fund
    try:
        validate_fund_holdings(fund)
    except ValidationError as e:
        raise e
