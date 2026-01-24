from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model
from django.contrib.auth.signals import user_logged_in

from api.payment.models import SubscriptionType, UserSubscriptionPackage, UserSubscription

User = get_user_model()


class LoginSignalTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="signaluser",
            password="password123"
        )

        sub_type = SubscriptionType.objects.create(
            name="Premium",
            description="Premium",
            price=20.00,
            duration_days=30
        )

        package = UserSubscriptionPackage.objects.create(
            subscription_type=sub_type,
            price=20.00
        )

        self.subscription = UserSubscription.objects.create(
            user=self.user,
            package=package,
            start_date=timezone.now() - timedelta(days=40),
            end_date=timezone.now() - timedelta(days=1),
            is_active=True
        )

    def test_subscription_deactivated_on_login(self):
        """Edge case: subscription deactivation on user login"""
        user_logged_in.send(sender=self.user.__class__, request=None, user=self.user)
        self.subscription.refresh_from_db()
        self.assertFalse(self.subscription.is_active)
