from __future__ import annotations

from rest_framework import serializers
from django.db import transaction

from .models import Order, OrderFill, OrderEvent


class OrderFillSerializer(serializers.ModelSerializer):
    """
    Serializer for OrderFill model.
    """
    class Meta:
        model = OrderFill
        fields = ("id", "order", "quantity", "price", "executed_at", "created_at")
        read_only_fields = fields


class OrderEventSerializer(serializers.ModelSerializer):
    """
    Serializer for OrderEvent model.
    """
    class Meta:
        model = OrderEvent
        fields = ("id", "order", "type", "message", "created_at")
        read_only_fields = fields


class OrderSerializer(serializers.ModelSerializer):
    """
      Serializer for Order model, including nested fills and events.
    """
    instrument_symbol = serializers.CharField(write_only=True, required=False)
    instrument = serializers.PrimaryKeyRelatedField(
        queryset=Order._meta.get_field("instrument").remote_field.model.objects.all(),
        required=False,
        allow_null=True,
    )

    instrument_display = serializers.SerializerMethodField(read_only=True)

    user = serializers.PrimaryKeyRelatedField(read_only=True)
    portfolio = serializers.PrimaryKeyRelatedField(read_only=True)

    limit_price = serializers.DecimalField(
        max_digits=20, decimal_places=6, required=False, allow_null=True
    )
    stop_price = serializers.DecimalField(
        max_digits=20, decimal_places=6, required=False, allow_null=True
    )

    remaining_quantity = serializers.DecimalField(
        max_digits=20, decimal_places=6, read_only=True
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
            "instrument_symbol",
            "instrument_display",
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
            "portfolio",
            "instrument_display",
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

    def get_instrument_display(self, obj: Order) -> str:
        inst = obj.instrument
        return f"{inst.symbol} ({inst.name})"

    def validate(self, attrs):
        """
        Validate only business rules.
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

        instrument = attrs.get("instrument")
        instrument_symbol = self.initial_data.get("instrument_symbol")

        if self.instance is None and instrument is None and not instrument_symbol:
            raise serializers.ValidationError(
                {"instrument_symbol": "This field is required (or provide instrument id)."}
            )

        return attrs

    @transaction.atomic
    def create(self, validated_data):
        """
        Automatically associate the order with the requesting user's profile.
        """
        request = self.context["request"]
        profile = request.user.profile

        validated_data["user"] = profile

        portfolio = profile.portfolios.filter(is_active=True).first()
        if portfolio is None:
            raise serializers.ValidationError({"portfolio": "No active portfolio found for this user."})
        validated_data["portfolio"] = portfolio

        if not validated_data.get("instrument"):
            instrument_symbol = (self.initial_data.get("instrument_symbol") or "").strip()
            if not instrument_symbol:
                raise serializers.ValidationError(
                    {"instrument_symbol": "This field is required (or provide instrument id)."}
                )

            Instrument = Order._meta.get_field("instrument").remote_field.model
            try:
                validated_data["instrument"] = Instrument.objects.get(symbol__iexact=instrument_symbol)
            except Instrument.DoesNotExist:
                raise serializers.ValidationError(
                    {"instrument_symbol": f"Unknown instrument symbol: {instrument_symbol}"}
                )

        validated_data.pop("instrument_symbol", None)

        order = super().create(validated_data)

        OrderEvent.objects.create(order=order, type=OrderEvent.EventType.CREATED, message="Order created.")
        OrderEvent.objects.create(order=order, type=OrderEvent.EventType.OPENED, message="Order opened.")

        return order
