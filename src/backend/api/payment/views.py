from datetime import timedelta
from django.utils.timezone import now
from django.shortcuts import get_object_or_404, redirect
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
import stripe
from django.conf import settings
from django.http import HttpResponse
import logging

from .models import SubscriptionType, UserSubscription, Payment, UserSubscriptionPackage
from .services.stripe_service import create_checkout_session
from .services.paypal_service import create_order, capture_order

logger = logging.getLogger(__name__)


class StripeCheckoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        subscription_type = get_object_or_404(
            SubscriptionType, id=request.data["subscription_type_id"]
        )

        base = settings.BASE_URL.rstrip('/')
        # Ensure redirect goes to the payment app endpoints so SubscriptionSuccessView handles creation
        success_url = f"{base}/api/payment/subscription/success?session_id={{CHECKOUT_SESSION_ID}}"
        cancel_url = f"{base}/api/payment/subscription/cancel?session_id={{CHECKOUT_SESSION_ID}}"

        session = create_checkout_session(
            user=request.user,
            subscription_type=subscription_type,
            success_url=success_url,
            cancel_url=cancel_url,
        )

        return Response({"checkout_url": session.url})


class StripeWebhookView(APIView):
    permission_classes = []

    def post(self, request):
        # Print raw webhook arrival for debugging
        try:
            print("[stripe webhook] received request")
        except Exception:
            pass

        event = stripe.Webhook.construct_event(
            request.body,
            request.META.get("HTTP_STRIPE_SIGNATURE"),
            settings.STRIPE_WEBHOOK_SECRET,
        )

        print(f"[stripe webhook] event type={event.get('type')}")

        if event["type"] == "checkout.session.completed":
            session = event["data"]["object"]
            meta = session.get("metadata", {}) or {}
            print(f"[stripe webhook] session id={session.get('id')} metadata={meta}")
            subscription_type_id = meta.get("subscription_type_id")
            user_id = meta.get("user_id")

            if subscription_type_id and user_id:
                try:
                    subscription_type = SubscriptionType.objects.get(id=subscription_type_id)
                except SubscriptionType.DoesNotExist:
                    print(f"[stripe webhook] SubscriptionType {subscription_type_id} not found")
                    return HttpResponse(status=400)

                package, _ = UserSubscriptionPackage.objects.get_or_create(
                    subscription_type=subscription_type,
                    price=subscription_type.price,
                    defaults={"is_active": True},
                )

                if not Payment.objects.filter(provider_payment_id=session.get("id"), provider="stripe").exists():
                    print(f"[stripe webhook] creating Payment and UserSubscription for user_id={user_id}")
                    Payment.objects.create(
                        user_id=user_id,
                        provider="stripe",
                        provider_payment_id=session.get("id"),
                        subscription_type=subscription_type,
                        package=package,
                        amount=subscription_type.price,
                        status="paid",
                    )

                    UserSubscription.objects.filter(user_id=user_id, is_active=True).update(is_active=False)

                    UserSubscription.objects.create(
                        user_id=user_id,
                        package=package,
                        start_date=now(),
                        end_date=now() + timedelta(days=subscription_type.duration_days),
                        is_active=True,
                    )

        return HttpResponse(status=200)


class PayPalCreateOrderView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        subscription_type = get_object_or_404(
            SubscriptionType, id=request.data["subscription_type_id"]
        )
        order = create_order(subscription_type)
        return Response({"order_id": order["id"]})


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

        if not Payment.objects.filter(provider_payment_id=order_id, provider="paypal").exists():
            Payment.objects.create(
                user=request.user,
                provider="paypal",
                provider_payment_id=order_id,
                subscription_type=subscription_type,
                package=package,
                amount=subscription_type.price,
                status="paid",
            )

            UserSubscription.objects.filter(user=request.user, is_active=True).update(is_active=False)

            UserSubscription.objects.create(
                user=request.user,
                package=package,
                start_date=now(),
                end_date=now() + timedelta(days=subscription_type.duration_days),
                is_active=True,
            )

        return Response({"status": "success"})


class SubscriptionListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        packages = UserSubscriptionPackage.objects.filter(is_active=True).select_related("subscription_type")

        data = []
        for pkg in packages:
            data.append({
                "package_id": pkg.id,
                "price": str(pkg.price),
                "subscription_type": {
                    "id": pkg.subscription_type.id,
                    "name": pkg.subscription_type.name,
                    "description": pkg.subscription_type.description,
                    "price": str(pkg.subscription_type.price),
                    "duration_days": pkg.subscription_type.duration_days,
                }
            })

        return Response(data)


class SubscriptionSuccessView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        session_id = request.GET.get("session_id") or request.GET.get("session")

        if session_id:
            try:
                print(f"[stripe success] retrieving session {session_id}")
                session = stripe.checkout.Session.retrieve(session_id, expand=["payment_intent"])
                print(f"[stripe success] retrieved session id={getattr(session, 'id', None)}")
            except Exception as exc:
                print(f"[stripe success] failed to retrieve session {session_id}: {exc}")
                frontend_base = getattr(settings, "FRONTEND_BASE_URL", "/")
                return redirect(frontend_base.rstrip("/") + "/subscription/success")

            paid = False
            try:
                if getattr(session, "payment_status", None) == "paid":
                    paid = True

                pi = getattr(session, "payment_intent", None)
                if getattr(pi, "status", None) == "succeeded":
                    paid = True

                charges = getattr(getattr(pi, "charges", None), "data", None)
                if charges and len(charges) > 0:
                    first = charges[0]
                    print(f"[stripe success] charge first={first}")
                    if first.get('status') == 'succeeded' or first.get('paid') is True:
                        paid = True
            except Exception as exc:
                print(f"[stripe success] error evaluating payment status: {exc}")

            meta = getattr(session, "metadata", {}) or {}
            user_id = meta.get("user_id")
            subscription_type_id = meta.get("subscription_type_id")

            print(f"[stripe success] paid={paid} metadata={meta}")

            if paid and user_id and subscription_type_id:
                if not Payment.objects.filter(provider_payment_id=session.id, provider="stripe").exists():
                    try:
                        subscription_type = SubscriptionType.objects.get(id=subscription_type_id)

                        package, _ = UserSubscriptionPackage.objects.get_or_create(
                            subscription_type=subscription_type,
                            price=subscription_type.price,
                            defaults={"is_active": True},
                        )

                        print(f"[stripe success] creating DB entries user_id={user_id} subscription_type={subscription_type_id}")

                        Payment.objects.create(
                            user_id=user_id,
                            provider="stripe",
                            provider_payment_id=session.id,
                            subscription_type=subscription_type,
                            package=package,
                            amount=subscription_type.price,
                            status="paid",
                        )

                        UserSubscription.objects.filter(user_id=user_id, is_active=True).update(is_active=False)

                        UserSubscription.objects.create(
                            user_id=user_id,
                            package=package,
                            start_date=now(),
                            end_date=now() + timedelta(days=subscription_type.duration_days),
                            is_active=True,
                        )
                    except SubscriptionType.DoesNotExist:
                        print(f"[stripe success] SubscriptionType {subscription_type_id} not found")
                else:
                    print(f"[stripe success] payment with id={session.id} already exists, skipping creation")
            else:
                print("[stripe success] session not paid or missing metadata; skipping subscription creation")

        frontend_base = getattr(settings, "FRONTEND_BASE_URL", "/")
        return redirect(frontend_base.rstrip("/") + "/subscription/success")


class SubscriptionCancelView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        frontend_base = getattr(settings, "FRONTEND_BASE_URL", "/")
        return redirect(frontend_base.rstrip("/") + "/subscription/cancel")
