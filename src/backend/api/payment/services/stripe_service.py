import stripe
from django.conf import settings

stripe.api_key = settings.STRIPE_SECRET_KEY

def create_checkout_session(user, subscription_type, success_url, cancel_url):
    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        mode="payment",
        customer_email=user.email,
        metadata={
            "user_id": str(user.id),
            "subscription_type_id": str(subscription_type.id),
        },
        line_items=[{
            "price_data": {
                "currency": "eur",
                "product_data": {"name": subscription_type.name},
                "unit_amount": int(subscription_type.price * 100),
            },
            "quantity": 1,
        }],
        success_url=success_url,
        cancel_url=cancel_url,
    )
    return session
