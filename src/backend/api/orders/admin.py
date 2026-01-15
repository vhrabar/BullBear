from __future__ import annotations

from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest

from .models import Order, OrderFill, OrderEvent


class OrderFillInline(admin.TabularInline):
    model = OrderFill
    extra = 0
    can_delete = False
    show_change_link = True
    readonly_fields = (
        "quantity",
        "price",
        "executed_at",
        "created_at",
    )
    ordering = ("executed_at",)


class OrderEventInline(admin.TabularInline):
    model = OrderEvent
    extra = 0
    can_delete = False
    show_change_link = True
    readonly_fields = (
        "type",
        "message",
        "created_at",
    )
    ordering = ("created_at",)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """
    Main admin interface for Orders.
    """

    list_display = (
        "id",
        "placed_at",
        "user",
        "portfolio",
        "instrument",
        "side",
        "order_type",
        "status",
        "quantity",
        "filled_quantity",
        "remaining_qty",
        "avg_fill_price",
        "limit_price",
        "stop_price",
        "time_in_force",
        "revision",
    )

    list_filter = (
        "status",
        "order_type",
        "side",
        "time_in_force",
        "instrument",
        "portfolio",
        "placed_at",
    )

    search_fields = (
        "id",
        "instrument__symbol",
        "portfolio__name",
        "user__user__username",
        "user__user__email",
    )

    date_hierarchy = "placed_at"
    ordering = ("-placed_at",)

    readonly_fields = (
        "filled_quantity",
        "avg_fill_price",
        "opened_at",
        "closed_at",
        "cancelled_at",
        "revision",
        "created_at",
        "updated_at",
    )

    fieldsets = (
        ("Scope", {
            "fields": ("user", "portfolio", "instrument")
        }),
        ("Order", {
            "fields": (
                "side",
                "order_type",
                "time_in_force",
                "quantity",
                "limit_price",
                "stop_price",
            )
        }),
        ("Status", {
            "fields": (
                "status",
                "filled_quantity",
                "avg_fill_price",
                "revision",
                "placed_at",
                "opened_at",
                "closed_at",
            )
        }),
        ("Cancel / Reject", {
            "fields": (
                "cancelled_at",
                "cancel_reason",
                "reject_reason",
            )
        }),
        ("System", {
            "fields": (
                "created_at",
                "updated_at",
            )
        }),
    )

    inlines = (OrderFillInline, OrderEventInline)

    list_select_related = ("user", "portfolio", "instrument")

    @admin.display(description="Remaining")
    def remaining_qty(self, obj: Order):
        return obj.remaining_quantity

    def get_queryset(self, request: HttpRequest) -> QuerySet[Order]:
        qs = super().get_queryset(request)
        return qs.select_related("user", "portfolio", "instrument")


@admin.register(OrderFill)
class OrderFillAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "order",
        "executed_at",
        "quantity",
        "price",
        "created_at",
    )
    list_filter = ("executed_at", "created_at")
    search_fields = (
        "id",
        "order__id",
        "order__instrument__symbol",
        "order__portfolio__name",
        "order__user__user__username",
    )
    date_hierarchy = "executed_at"
    ordering = ("-executed_at",)

    readonly_fields = (
        "order",
        "quantity",
        "price",
        "executed_at",
        "created_at",
    )

    list_select_related = ("order", "order__instrument", "order__portfolio", "order__user")

    def has_add_permission(self, request: HttpRequest) -> bool:
        return False

    def has_change_permission(self, request: HttpRequest, obj=None) -> bool:
        return False

    def has_delete_permission(self, request: HttpRequest, obj=None) -> bool:
        return False


@admin.register(OrderEvent)
class OrderEventAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "order",
        "type",
        "created_at",
        "message",
    )
    list_filter = ("type", "created_at")
    search_fields = (
        "id",
        "order__id",
        "order__instrument__symbol",
        "order__portfolio__name",
        "order__user__user__username",
        "message",
    )
    date_hierarchy = "created_at"
    ordering = ("-created_at",)

    readonly_fields = (
        "order",
        "type",
        "message",
        "created_at",
    )

    list_select_related = ("order", "order__instrument", "order__portfolio", "order__user")

    def has_add_permission(self, request: HttpRequest) -> bool:
        return False

    def has_change_permission(self, request: HttpRequest, obj=None) -> bool:
        return False

    def has_delete_permission(self, request: HttpRequest, obj=None) -> bool:
        return False
