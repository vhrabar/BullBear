from __future__ import annotations

from decimal import Decimal
from django.utils import timezone
from rest_framework import serializers

from .models import Order, OrderFill, OrderEvent


class OrderFillSerializer(serializers.ModelSerializer):
    """
    Serializer for OrderFill model.
    """
    class Meta:
        model = OrderFill
        fields = (
            "id",
            "order",
            "quantity",
            "price",
            "fee",
            "executed_at",
            "created_at",
        )
        read_only_fields = fields


class OrderEventSerializer(serializers.ModelSerializer):
    """
    Serializer for OrderEvent model.
    """
    class Meta:
        model = OrderEvent
        fields = (
            "id",
            "order",
            "type",
            "message",
            "created_at",
        )
        read_only_fields = fields


class OrderSerializer(serializers.ModelSerializer):
    """
    Serializer for Order model, including nested fills and events.
    """
    remaining_quantity = serializers.DecimalField(
        max_digits=20,
        decimal_places=6,
        read_only=True,
    )

    fills = OrderFillSerializer(many=True, read_only=True)
    events = OrderEventSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = (
            "id",
            "user",
            "portfolio",
            "instrument",

            "side",
            "order_type",
            "time_in_force",
            "quantity",
            "limit_price",
            "stop_price",

            "status",
            "filled_quantity",
            "remaining_quantity",
            "avg_fill_price",

            "revision",
            "placed_at",
            "opened_at",
            "closed_at",
            "cancelled_at",
            "cancel_reason",
            "reject_reason",

            "created_at",
            "updated_at",

            "fills",
            "events",
        )

        read_only_fields = (
            "id",
            "user",
            "status",
            "filled_quantity",
            "remaining_quantity",
            "avg_fill_price",
            "revision",
            "opened_at",
            "closed_at",
            "cancelled_at",
            "cancel_reason",
            "reject_reason",
            "created_at",
            "updated_at",
            "fills",
            "events",
        )

    def validate(self, attrs):
        """
        Enforce pricing requirements based on order_type.
        """
        order_type = attrs.get("order_type") or getattr(self.instance, "order_type", None)
        limit_price = attrs.get("limit_price", getattr(self.instance, "limit_price", None))
        stop_price = attrs.get("stop_price", getattr(self.instance, "stop_price", None))

        if order_type == Order.OrderType.LIMIT and not limit_price:
            raise serializers.ValidationError({"limit_price": "LIMIT order requires limit_price."})

        if order_type == Order.OrderType.STOP and not stop_price:
            raise serializers.ValidationError({"stop_price": "STOP order requires stop_price."})

        if order_type == Order.OrderType.STOP_LIMIT:
            if not stop_price:
                raise serializers.ValidationError({"stop_price": "STOP_LIMIT requires stop_price."})
            if not limit_price:
                raise serializers.ValidationError({"limit_price": "STOP_LIMIT requires limit_price."})

        return attrs

    def create(self, validated_data):
        """
        Automatically associate the order with the requesting user's profile.
        """
        request = self.context.get("request")
        if request and request.user and hasattr(request.user, "userprofile"):
            validated_data["user"] = request.user.userprofile

        order = super().create(validated_data)

        OrderEvent.objects.create(order=order, type=OrderEvent.EventType.CREATED, message="Order created.")
        OrderEvent.objects.create(order=order, type=OrderEvent.EventType.OPENED, message="Order opened.")

        order.opened_at = timezone.now()
        order.save(update_fields=["opened_at"])

        return order
