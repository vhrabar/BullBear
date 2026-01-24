from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from django.utils import timezone
from .models import UserSubscription


@receiver(user_logged_in)
def deactivate_expired_subscriptions(sender, request, user, **kwargs):
    now = timezone.now()

    expired_subs = UserSubscription.objects.filter(user=user, is_active=True, end_date__lte=now)

    for sub in expired_subs:
        sub.is_active = False
        sub.save()

        sub.package.is_active = False
        sub.package.save()
