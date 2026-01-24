from django.urls import path
from .views import StripeCheckoutView, StripeWebhookView, PayPalCreateOrderView, PayPalCaptureOrderView

urlpatterns = [
    path("stripe/checkout/", StripeCheckoutView.as_view()),
    path("stripe/webhook/", StripeWebhookView.as_view()),
    path("paypal/create/", PayPalCreateOrderView.as_view()),
    path("paypal/capture/", PayPalCaptureOrderView.as_view()),
]
