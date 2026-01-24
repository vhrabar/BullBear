import requests
from base64 import b64encode
from django.conf import settings
import logging

BASE_URL = "https://api-m.sandbox.paypal.com"

logger = logging.getLogger(__name__)


class PayPalAPIError(Exception):
    """Represents a non-2xx response from PayPal with optional parsed JSON or text."""

    def __init__(self, status_code, data=None, text=None):
        self.status_code = status_code
        self.data = data
        self.text = text
        message = f"PayPal API returned {status_code}: {data or text}"
        super().__init__(message)


def get_access_token():
    auth = b64encode(f"{settings.PAYPAL_CLIENT_ID}:{settings.PAYPAL_CLIENT_SECRET}".encode()).decode()

    r = requests.post(
        f"{BASE_URL}/v1/oauth2/token",
        headers={"Authorization": f"Basic {auth}", "Content-Type": "application/x-www-form-urlencoded"},
        data={"grant_type": "client_credentials"},
    )
    r.raise_for_status()
    return r.json()["access_token"]


def create_order(subscription_type):
    token = get_access_token()

    payload = {
        "intent": "CAPTURE",
        "purchase_units": [{
            "amount": {
                "currency_code": "USD",
                "value": f"{subscription_type.price:.2f}"
            }
        }]
    }

    # Include application_context with return/cancel URLs so PayPal redirects back after payer approval
    frontend_base = getattr(settings, "FRONTEND_BASE_URL", None) or getattr(settings, "BASE_URL", None)
    if frontend_base:
        frontend_base = frontend_base.rstrip('/')
        # Add subscription_type_id to the return/cancel URLs so the frontend can call the capture endpoint
        payload["application_context"] = {
            "return_url": f"{frontend_base}/payment/paypal/return?subscription_type_id={subscription_type.id}",
            "cancel_url": f"{frontend_base}/payment/paypal/cancel?subscription_type_id={subscription_type.id}",
        }

    r = requests.post(
        f"{BASE_URL}/v2/checkout/orders",
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        json=payload,
    )

    if r.status_code >= 400:
        # Try to parse JSON error body, otherwise fall back to text
        data = None
        try:
            data = r.json()
        except ValueError:
            data = None
        text = (r.text or "")[:2000]
        logger.error("PayPal create order failed: status=%s, body=%s", r.status_code, data or text)
        raise PayPalAPIError(r.status_code, data=data, text=text)

    return r.json()


def capture_order(order_id):
    token = get_access_token()
    r = requests.post(
        f"{BASE_URL}/v2/checkout/orders/{order_id}/capture",
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    )

    if r.status_code >= 400:
        data = None
        try:
            data = r.json()
        except ValueError:
            data = None
        text = (r.text or "")[:2000]
        logger.error("PayPal capture failed for order %s: status=%s, body=%s", order_id, r.status_code, data or text)
        raise PayPalAPIError(r.status_code, data=data, text=text)

    return r.json()
