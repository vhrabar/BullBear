from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model
from api.payment.models import SubscriptionType, UserSubscriptionPackage, UserSubscription


User = get_user_model()


class SubscriptionComponentTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="password123"
        )

        self.subscription_type = SubscriptionType.objects.create(
            name="Premium",
            description="Premium access",
            price=20.00,
            duration_days=30
        )

        self.package = UserSubscriptionPackage.objects.create(
            subscription_type=self.subscription_type,
            price=20.00,
            is_active=True
        )

    def test_user_without_subscription(self):
        """Regular case: user without active subscription"""
        active = UserSubscription.objects.filter(
            user=self.user,
            is_active=True
        ).exists()

        self.assertFalse(active)

    def test_user_with_active_subscription(self):
        """Regular case: active subscription"""
        UserSubscription.objects.create(
            user=self.user,
            package=self.package,
            start_date=timezone.now(),
            end_date=timezone.now() + timedelta(days=30),
            is_active=True
        )

        active = UserSubscription.objects.filter(
            user=self.user,
            is_active=True
        ).exists()

        self.assertTrue(active)

    def test_expired_subscription(self):
        """Edge case: expired subscription"""
        sub = UserSubscription.objects.create(
            user=self.user,
            package=self.package,
            start_date=timezone.now() - timedelta(days=40),
            end_date=timezone.now() - timedelta(days=10),
            is_active=True
        )

        self.assertTrue(sub.end_date < timezone.now())

    def test_subscription_requires_package(self):
        """Exception case: missing package"""
        with self.assertRaises(Exception):
            UserSubscription.objects.create(
                user=self.user,
                start_date=timezone.now(),
                end_date=timezone.now() + timedelta(days=30),
                is_active=True
            )
