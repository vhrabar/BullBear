from django.contrib import admin
from .models import SubscriptionType, UserSubscriptionPackage, UserSubscription, Payment


@admin.register(SubscriptionType)
class SubscriptionTypeAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "price", "duration_days")
    search_fields = ("name",)
    list_filter = ("duration_days",)


@admin.register(UserSubscriptionPackage)
class UserSubscriptionPackageAdmin(admin.ModelAdmin):
    list_display = ("id", "subscription_type", "price", "is_active")
    search_fields = ("subscription_type__name",)
    list_filter = ("is_active",)


class UserSubscriptionInline(admin.TabularInline):
    model = UserSubscription
    extra = 0
    readonly_fields = ("start_date", "end_date", "is_active")
    autocomplete_fields = ("user", "package")


@admin.register(UserSubscription)
class UserSubscriptionAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "package", "start_date", "end_date", "is_active")
    search_fields = ("user__username", "package__subscription_type__name")
    list_filter = ("is_active",)
    autocomplete_fields = ("user", "package")


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "provider", "provider_payment_id", "amount", "status", "created_at")
    search_fields = ("user__username", "provider_payment_id")
    list_filter = ("provider", "status", "created_at")
    autocomplete_fields = ("user", "subscription_type", "package")
