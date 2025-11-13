from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import PortfolioHolding


@receiver(post_save, sender=PortfolioHolding)
def remove_empty_stock(sender, instance, **kwargs):
    # If all shares are sold
    if instance.quantity == 0:
        instance.delete()