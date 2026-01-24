from django.urls import path
from .views import StripeCheckoutView, StripeWebhookView, PayPalCreateOrderView, PayPalCaptureOrderView, SubscriptionListView, SubscriptionSuccessView, SubscriptionCancelView

urlpatterns = [
    path("stripe/checkout/", StripeCheckoutView.as_view()),
    path("stripe/webhook/", StripeWebhookView.as_view()),
    path("paypal/create/", PayPalCreateOrderView.as_view()),
    path("paypal/capture/", PayPalCaptureOrderView.as_view()),
    path("packages/", SubscriptionListView.as_view()),

    # Browser redirect endpoints expected by Stripe (non-API)
    path("subscription/success", SubscriptionSuccessView.as_view()),
    path("subscription/cancel", SubscriptionCancelView.as_view()),

    # Also support API-prefixed paths in case Stripe was configured to return to /api/subscription/...
    path("api/subscription/success", SubscriptionSuccessView.as_view()),
    path("api/subscription/cancel", SubscriptionCancelView.as_view()),

    # Trailing slash tolerant variants
    path("subscription/success/", SubscriptionSuccessView.as_view()),
    path("subscription/cancel/", SubscriptionCancelView.as_view()),
    path("api/subscription/success/", SubscriptionSuccessView.as_view()),
    path("api/subscription/cancel/", SubscriptionCancelView.as_view()),
]
