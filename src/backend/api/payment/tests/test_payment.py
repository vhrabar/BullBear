from django.test import TestCase
from django.contrib.auth import get_user_model
from api.payment.models import SubscriptionType, UserSubscriptionPackage,Payment

User = get_user_model()


class PaymentModelTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="payer",
            password="password123"
        )

        self.subscription_type = SubscriptionType.objects.create(
            name="Premium",
            description="Premium plan",
            price=20.00,
            duration_days=30
        )

        self.package = UserSubscriptionPackage.objects.create(
            subscription_type=self.subscription_type,
            price=20.00
        )

    def test_payment_creation(self):
        """Regular case: creating a payment record"""
        payment = Payment.objects.create(
            user=self.user,
            provider="paypal",
            subscription_type=self.subscription_type,
            provider_payment_id="TEST123",
            package=self.package,
            amount=20.00,
            status="paid"
        )

        self.assertEqual(payment.amount, 20.00)
        self.assertEqual(payment.status, "paid")
