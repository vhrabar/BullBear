from datetime import timedelta
from django.utils.timezone import now
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
import stripe
from django.conf import settings
from django.http import HttpResponse

from .models import SubscriptionType, UserSubscription, Payment, UserSubscriptionPackage
from .services.stripe_service import create_checkout_session
from .services.paypal_service import create_order, capture_order


class StripeCheckoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        subscription_type = get_object_or_404(
            SubscriptionType, id=request.data["subscription_type_id"]
        )

        success_url = f"{settings.BASE_URL}/subscription/success"
        cancel_url = f"{settings.BASE_URL}/subscription/cancel"

        session = create_checkout_session(
            user=request.user,
            subscription_type=subscription_type,
            success_url=success_url,
            cancel_url=cancel_url,
        )

        return Response({"checkout_url": session.url})



# Stripe Webhook
class StripeWebhookView(APIView):
    permission_classes = []

    def post(self, request):
        event = stripe.Webhook.construct_event(
            request.body, request.META.get("HTTP_STRIPE_SIGNATURE"), settings.STRIPE_WEBHOOK_SECRET
        )

        if event["type"] == "checkout.session.completed":
            session = event["data"]["object"]
            subscription_type = SubscriptionType.objects.get(
                id=session["metadata"]["subscription_type_id"]
            )

            Payment.objects.create(
                user_id=session["metadata"]["user_id"],
                provider="stripe",
                provider_payment_id=session["id"],
                subscription_type=subscription_type,
                amount=subscription_type.price,
                status="paid",
            )

            UserSubscription.objects.create(
                user_id=session["metadata"]["user_id"],
                subscription_type=subscription_type,
                start_date=now(),
                end_date=now() + timedelta(days=subscription_type.duration_days),
                is_active=True,
            )

        return HttpResponse(status=200)


# PayPal Create Order
class PayPalCreateOrderView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        subscription_type = get_object_or_404(
            SubscriptionType, id=request.data["subscription_type_id"]
        )
        order = create_order(subscription_type)
        return Response({"order_id": order["id"]})


# PayPal Capture Order
class PayPalCaptureOrderView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        order_id = request.data["order_id"]
        subscription_type = get_object_or_404(
            SubscriptionType, id=request.data["subscription_type_id"]
        )
        capture_order(order_id)

        package, _ = UserSubscriptionPackage.objects.get_or_create(
            subscription_type=subscription_type,
            price=subscription_type.price,
            defaults={"is_active": True},
        )

        Payment.objects.create(
            user=request.user,
            provider="paypal",
            provider_payment_id=order_id,
            subscription_type=subscription_type,
            amount=subscription_type.price,
            status="paid",
            package=package,
        )

        UserSubscription.objects.create(
            user=request.user,
            package=package,
            start_date=now(),
            end_date=now() + timedelta(days=subscription_type.duration_days),
            is_active=True,
        )

        return Response({"status": "success"})
