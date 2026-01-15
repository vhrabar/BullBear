from __future__ import annotations

from decimal import Decimal
from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone


class Order(models.Model):
    """
    Represents a user's order intent.
    """

    class Side(models.TextChoices):
        BUY = "BUY", "Buy"
        SELL = "SELL", "Sell"

    class OrderType(models.TextChoices):
        MARKET = "MARKET", "Market"
        LIMIT = "LIMIT", "Limit"
        STOP = "STOP", "Stop (Market)"
        STOP_LIMIT = "STOP_LIMIT", "Stop-Limit"

    class TimeInForce(models.TextChoices):
        GTC = "GTC", "Good Till Cancelled"
        DAY = "DAY", "Day"
        IOC = "IOC", "Immediate Or Cancel"
        FOK = "FOK", "Fill Or Kill"

    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        OPEN = "OPEN", "Open"
        PARTIALLY_FILLED = "PARTIALLY_FILLED", "Partially Filled"
        FILLED = "FILLED", "Filled"
        CANCELLED = "CANCELLED", "Cancelled"
        EXPIRED = "EXPIRED", "Expired"
        REJECTED = "REJECTED", "Rejected"

    user = models.ForeignKey(
        "users.UserProfile",
        on_delete=models.CASCADE,
        related_name="orders",
        db_index=True,
    )
    portfolio = models.ForeignKey(
        "users.UserPortfolio",
        on_delete=models.CASCADE,
        related_name="orders",
        db_index=True,
    )

    instrument = models.ForeignKey(
        "trading.Instrument",
        on_delete=models.PROTECT,
        related_name="orders",
        db_index=True,
    )

    side = models.CharField(max_length=4, choices=Side.choices)
    order_type = models.CharField(max_length=16, choices=OrderType.choices)

    time_in_force = models.CharField(
        max_length=8,
        choices=TimeInForce.choices,
        default=TimeInForce.GTC,
    )

    quantity = models.DecimalField(
        max_digits=20,
        decimal_places=6,
        validators=[MinValueValidator(Decimal("0.000001"))],
    )

    limit_price = models.DecimalField(
        max_digits=20,
        decimal_places=6,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal("0.000001"))],
    )
    stop_price = models.DecimalField(
        max_digits=20,
        decimal_places=6,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal("0.000001"))],
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.OPEN,
        db_index=True,
    )

    revision = models.PositiveIntegerField(default=0)

    filled_quantity = models.DecimalField(
        max_digits=20,
        decimal_places=6,
        default=Decimal("0"),
        validators=[MinValueValidator(Decimal("0"))],
    )

    avg_fill_price = models.DecimalField(
        max_digits=20,
        decimal_places=6,
        null=True,
        blank=True,
    )

    placed_at = models.DateTimeField(default=timezone.now, db_index=True)
    opened_at = models.DateTimeField(null=True, blank=True)
    closed_at = models.DateTimeField(null=True, blank=True)

    cancelled_at = models.DateTimeField(null=True, blank=True)
    cancel_reason = models.CharField(max_length=255, blank=True)
    reject_reason = models.CharField(max_length=255, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-placed_at"]
        indexes = [
            models.Index(fields=["portfolio", "status"]),
            models.Index(fields=["instrument", "status"]),
            models.Index(fields=["user", "placed_at"]),
        ]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(quantity__gt=0),
                name="orders_order_quantity_gt_0",
            ),
            models.CheckConstraint(
                condition=models.Q(filled_quantity__gte=0),
                name="orders_order_filled_quantity_gte_0",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.portfolio_id}:{self.side} {self.quantity} {self.instrument_id} ({self.order_type})"

    @property
    def remaining_quantity(self) -> Decimal:
        return max(Decimal("0"), self.quantity - self.filled_quantity)

    def mark_opened(self) -> None:
        if not self.opened_at:
            self.opened_at = timezone.now()

    def mark_closed(self) -> None:
        self.closed_at = timezone.now()

    def can_fill(self) -> bool:
        return self.status in {self.Status.OPEN, self.Status.PARTIALLY_FILLED}

    def apply_fill(self, fill_qty: Decimal, fill_price: Decimal) -> None:
        """
        Called by execution engine after creating an OrderFill.
        """
        if fill_qty <= 0:
            raise ValueError("fill_qty must be > 0")
        if fill_price <= 0:
            raise ValueError("fill_price must be > 0")

        prev_qty = self.filled_quantity
        new_qty = prev_qty + fill_qty

        if new_qty > self.quantity:
            raise ValueError("Fill exceeds order quantity")

        if prev_qty == 0:
            self.avg_fill_price = fill_price
        else:
            prev_cost = (self.avg_fill_price or Decimal("0")) * prev_qty
            new_cost = fill_price * fill_qty
            self.avg_fill_price = (prev_cost + new_cost) / new_qty

        self.filled_quantity = new_qty

        if self.filled_quantity == self.quantity:
            self.status = self.Status.FILLED
            self.mark_closed()
        else:
            self.status = self.Status.PARTIALLY_FILLED

        self.revision += 1


class OrderFill(models.Model):
    """
    Represents an execution (fill) against an order.
    """

    order = models.ForeignKey(
        "orders.Order",
        on_delete=models.CASCADE,
        related_name="fills",
        db_index=True,
    )

    quantity = models.DecimalField(
        max_digits=20,
        decimal_places=6,
        validators=[MinValueValidator(Decimal("0.000001"))],
    )
    price = models.DecimalField(
        max_digits=20,
        decimal_places=6,
        validators=[MinValueValidator(Decimal("0.000001"))],
    )

    executed_at = models.DateTimeField(default=timezone.now, db_index=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["executed_at"]
        indexes = [
            models.Index(fields=["order", "executed_at"]),
        ]

    def __str__(self) -> str:
        return f"Fill {self.quantity} @ {self.price} for order={self.order_id}"


class OrderEvent(models.Model):
    """
    Audit log / timeline for order changes.
    """

    class EventType(models.TextChoices):
        CREATED = "CREATED", "Created"
        OPENED = "OPENED", "Opened"
        UPDATED = "UPDATED", "Updated"
        FILL = "FILL", "Fill"
        CANCELLED = "CANCELLED", "Cancelled"
        EXPIRED = "EXPIRED", "Expired"
        REJECTED = "REJECTED", "Rejected"

    order = models.ForeignKey(
        "orders.Order",
        on_delete=models.CASCADE,
        related_name="events",
        db_index=True,
    )

    type = models.CharField(max_length=16, choices=EventType.choices)
    message = models.CharField(max_length=255, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["created_at"]
        indexes = [
            models.Index(fields=["order", "created_at"]),
            models.Index(fields=["type", "created_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.type} order={self.order_id}"
