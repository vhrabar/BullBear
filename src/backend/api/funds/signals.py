from decimal import Decimal
from django.db import models
from django.db.models import Sum
from django.db.models.functions import Coalesce
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from .models import Fund, FundHolding


def validate_fund_holdings(fund_id: int):
    """
    Ensure that all holdings for a fund sum to exactly 100%.
    """
    fund = Fund.objects.get(pk=fund_id)
    total = FundHolding.objects.filter(fund_id=fund_id).aggregate(
        total=Coalesce(Sum('weight_percent'), Decimal("0.000"))
    )['total']
    # Round to 3 decimal places to match field precision
    total = total.quantize(Decimal("0.001"))
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
    Fund.objects.filter(pk=instance.fund_id).update(updated_at=models.functions.Now())
