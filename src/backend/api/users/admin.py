# users/admin.py
from typing import Any

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _
from .models import User, UserProfile, UserPortfolio


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