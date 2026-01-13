# users/admin.py
from typing import Any

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _
from .models import User, UserProfile, UserPortfolio, ContactMessage


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ("email", "username", "is_staff", "is_superuser", "is_active")
    list_filter = ("is_staff", "is_superuser", "is_active", "groups")
    search_fields = ("email", "username")
    ordering = ("email",)

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (_("Personal info"), {"fields": ("username", "first_name", "last_name")}),
        (_("Permissions"), {
            "fields": (
                "is_active",
                "is_staff",
                "is_superuser",
                "groups",
                "user_permissions",
            )
        }),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": (
                "email",
                "is_active",
                "is_staff",
                "is_superuser",
            ),
        }),
    )

    filter_horizontal = ("groups", "user_permissions",)

    def save_model(self, request: HttpRequest, obj: User, form: Any, change: bool) -> None:
        obj.set_unusable_password()
        super().save_model(request, obj, form, change)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'bio', 'avatar_url')
    search_fields = ('user__username',)


@admin.register(UserPortfolio)
class UserPortfolioAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'created_at', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'user__user__username')


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = (
        "created_at",
        "email",
        "full_name",
        "subject",
        "user",
        "ip_address",
    )

    list_filter = (
        "created_at",
        "user",
    )

    search_fields = (
        "email",
        "full_name",
        "subject",
        "message",
        "ip_address",
        "user_agent",
        "user__user__username",
        "user__user__email",
    )

    ordering = ("-created_at",)

    list_select_related = ("user",)

    list_display_links = ("created_at", "email", "subject")

    readonly_fields = (
        "user",
        "full_name",
        "email",
        "subject",
        "message",
        "created_at",
        "ip_address",
        "user_agent",
    )

    fieldsets = (
        ("Message", {
            "fields": ("full_name", "email", "subject", "message"),
        }),
        ("Metadata", {
            "fields": ("user", "created_at", "ip_address", "user_agent"),
        }),
    )
