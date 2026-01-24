"""
URL configuration for DjangoProject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.urls import include
from django.conf import settings
from django.shortcuts import redirect
from urllib.parse import urlparse

urlpatterns = [
    # Admin site
    path('admin/', admin.site.urls),

    # ===== API Endpoints =====

    # Main
    path('api/main/', include('api.main.urls')),

    # Users
    path('accounts/', include('allauth.account.urls')),
    path('auth/', include('allauth.socialaccount.urls')),
    path('auth/', include('allauth.socialaccount.providers.google.urls')),
    path('auth/', include('allauth.socialaccount.providers.microsoft.urls')),

    # Trading
    path('api/trading/', include('api.trading.urls')),

    # Funds
    path('api/funds/', include('api.funds.urls')),

    # Users
    path('api/users/', include('api.users.urls')),

    # Payment
    path('api/payment/', include('api.payment.urls')),
    # Orders
    path('api/orders/', include('api.orders.urls')),

    # Leaderboard
    path('api/leaderboard/', include('api.leaderboard.urls')),

    # DJ-Rest-Auth
    path("api/auth/", include("dj_rest_auth.urls")),
    path("api/auth/registration/", include("dj_rest_auth.registration.urls")),
]


# Lightweight redirect views to handle external payment provider redirects
def _frontend_subscription_base():
    # Prefer an explicit FRONTEND_BASE_URL setting if available
    frontend_base = getattr(settings, 'FRONTEND_BASE_URL', None)
    if frontend_base:
        return frontend_base.rstrip('/')

    # Fallback to LOGIN_REDIRECT_URL or LOGOUT_REDIRECT_URL, but extract origin (scheme+netloc)
    candidate = getattr(settings, 'LOGIN_REDIRECT_URL', None) or getattr(settings, 'LOGOUT_REDIRECT_URL', None) or '/'
    if candidate.startswith('http'):
        parsed = urlparse(candidate)
        origin = f"{parsed.scheme}://{parsed.netloc}"
        return origin.rstrip('/')

    return '/'


def subscription_success_redirect(request):
    target = _frontend_subscription_base() + '/subscription/success'
    return redirect(target)


def subscription_cancel_redirect(request):
    target = _frontend_subscription_base() + '/subscription/cancel'
    return redirect(target)


# Expose subscription redirect endpoints at top-level as some payment providers may return here
# (mapped to both /subscription/... and /api/subscription/...) to be tolerant of different callback URLs
urlpatterns += [
    # without trailing slash
    path('subscription/success', subscription_success_redirect),
    path('subscription/cancel', subscription_cancel_redirect),
    path('api/subscription/success', subscription_success_redirect),
    path('api/subscription/cancel', subscription_cancel_redirect),

    # with trailing slash variants to be tolerant of providers appending a slash
    path('subscription/success/', subscription_success_redirect),
    path('subscription/cancel/', subscription_cancel_redirect),
    path('api/subscription/success/', subscription_success_redirect),
    path('api/subscription/cancel/', subscription_cancel_redirect),
]
