from __future__ import annotations

from django.db.models import QuerySet
from django.utils import timezone

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Order, OrderFill, OrderEvent
from .serializers import OrderSerializer, OrderFillSerializer, OrderEventSerializer
from .permissions import IsOrderOwner


class OrderViewSet(viewsets.ModelViewSet):
    """
    CRUD for Orders.
    """

    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated, IsOrderOwner]

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
