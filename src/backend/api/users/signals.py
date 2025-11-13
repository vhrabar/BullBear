from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, UserProfile
from django.apps import apps


@receiver(post_save, sender=User)
def create_user_profile_and_portfolio(sender, instance, created, **kwargs):
    """
    Automatically create profile and portfolio when a new user is created.
    """
    if created:
        # Create user's profile
        profile = UserProfile.objects.create(user=instance)

        # Create user's portfolio
        UserPortfolio = apps.get_model('users', 'UserPortfolio')

        UserPortfolio.objects.create(
            user=profile,
            name=f"{instance.username}'s Portfolio",
            balance=10000.00
        )
