from __future__ import annotations

from decimal import Decimal

from django.db.models import QuerySet
from django.utils import timezone

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Order, OrderFill, OrderEvent
from .serializers import OrderSerializer, OrderFillSerializer, OrderEventSerializer
from .permissions import IsOrderOwner, IsServiceExecutor
from api.trading.models import InstrumentQuote


class OrderViewSet(viewsets.ModelViewSet):
    """
    CRUD for Orders.
    """

    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated, IsOrderOwner]
    filterset_fields = ["status", "instrument__symbol"]

    def get_queryset(self) -> QuerySet[Order]:
        profile = self.request.user.profile

        return (
            Order.objects
            .filter(user=profile)
            .select_related("portfolio", "instrument", "user")
            .prefetch_related("fills", "events")
            .order_by("-placed_at")
        )

    def perform_create(self, serializer):
        """
        POST /orders/
        """
        serializer.save(user=self.request.user.profile)

    def perform_update(self, serializer):
        """
        PUT /orders/{id}/
        Only allow editing while order is still OPEN.
        """
        order: Order = self.get_object()

        if order.status not in {Order.Status.PENDING, Order.Status.OPEN}:
            raise ValueError("Only PENDING/OPEN orders can be modified.")

        serializer.save(revision=order.revision + 1)
        OrderEvent.objects.create(order=order, type=OrderEvent.EventType.UPDATED, message="Order updated.")

    def destroy(self, request, *args, **kwargs):
        """
        DELETE /orders/{id}/
        AKA cancel the order
        """
        order: Order = self.get_object()
        if order.status not in {Order.Status.PENDING, Order.Status.OPEN, Order.Status.PARTIALLY_FILLED}:
            return Response(
                {"detail": "Order cannot be cancelled in its current status."},
                status=status.HTTP_400_BAD_REQUEST
            )

        order.status = Order.Status.CANCELLED
        order.cancelled_at = timezone.now()
        order.cancel_reason = "Cancelled via API DELETE."
        order.closed_at = timezone.now()
        order.revision += 1
        order.save(update_fields=["status", "cancelled_at", "cancel_reason", "closed_at", "revision", "updated_at"])

        OrderEvent.objects.create(order=order, type=OrderEvent.EventType.CANCELLED, message=order.cancel_reason)

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        """
        POST /orders/{id}/cancel/
        """
        order: Order = self.get_object()

        if order.status not in {Order.Status.PENDING, Order.Status.OPEN, Order.Status.PARTIALLY_FILLED}:
            return Response(
                {"detail": "Order cannot be cancelled in its current status."},
                status=status.HTTP_400_BAD_REQUEST
            )

        order.status = Order.Status.CANCELLED
        order.cancelled_at = timezone.now()
        order.cancel_reason = request.data.get("reason", "Cancelled by user.")
        order.closed_at = timezone.now()
        order.revision += 1
        order.save(update_fields=["status", "cancelled_at", "cancel_reason", "closed_at", "revision", "updated_at"])

        OrderEvent.objects.create(order=order, type=OrderEvent.EventType.CANCELLED, message=order.cancel_reason)

        return Response(OrderSerializer(order, context={"request": request}).data)

    @action(
        detail=False,
        methods=["get"],
        url_path="open",
        permission_classes=[IsServiceExecutor],
    )
    def open_orders(self, request):
        """
        Service endpoint:
        GET /api/orders/orders/open/
        Returns OPEN + PARTIALLY_FILLED orders for execution engine.
        """
        qs = (
            Order.objects
            .filter(status__in=[Order.Status.OPEN, Order.Status.PARTIALLY_FILLED])
            .select_related("instrument", "portfolio", "user")
            .order_by("placed_at")
        )

        data = OrderSerializer(qs, many=True, context={"request": request}).data
        return Response(data)

    @action(
        detail=True,
        methods=["post"],
        url_path="execute",
        permission_classes=[IsServiceExecutor],
    )
    def execute(self, request, pk=None):
        """
        Service endpoint:
        POST /api/orders/orders/{id}/execute/
        Executes ONE order if its condition matches market price.
        """
        order: Order = Order.objects.select_related("instrument", "portfolio").get(pk=pk)

        if order.status not in {Order.Status.OPEN, Order.Status.PARTIALLY_FILLED}:
            return Response({"detail": "Order not executable."}, status=status.HTTP_400_BAD_REQUEST)

        quote = InstrumentQuote.objects.filter(instrument=order.instrument.symbol).first()
        if not quote:
            return Response({"detail": "No quote available."}, status=status.HTTP_409_CONFLICT)

        current_price = Decimal(str(quote.last_price))

        if not order.is_executable_at_price(current_price):
            return Response({"detail": "Order conditions not met."}, status=status.HTTP_409_CONFLICT)

        fill_qty = order.remaining_quantity
        if fill_qty <= 0:
            return Response({"detail": "No remaining quantity."}, status=status.HTTP_400_BAD_REQUEST)


        OrderFill.objects.create(
            order=order,
            quantity=fill_qty,
            price=current_price,
            executed_at=timezone.now(),
        )
        OrderEvent.objects.create(
            order=order,
            type=OrderEvent.EventType.FILL,
            message=f"Filled {fill_qty} @ {current_price}",
        )

        order.apply_fill(fill_qty, current_price)
        order.save()

        return Response({"detail": "Executed", "order_id": order.id})


class OrderFillViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only fills for the authenticated user.
    """
    serializer_class = OrderFillSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self) -> QuerySet[OrderFill]:
        profile = self.request.user.userprofile
        return (
            OrderFill.objects
            .filter(order__user=profile)
            .select_related("order", "order__instrument", "order__portfolio")
            .order_by("-executed_at")
        )


class OrderEventViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only order events for the authenticated user.
    """
    serializer_class = OrderEventSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self) -> QuerySet[OrderEvent]:
        profile = self.request.user.profile
        return (
            OrderEvent.objects
            .filter(order__user=profile)
            .select_related("order")
            .order_by("-created_at")
        )
