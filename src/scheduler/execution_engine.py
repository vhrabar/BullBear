from __future__ import annotations

from decimal import Decimal
from typing import Dict
from django_client import DjangoOrdersClient


class ExecutionEngine:
    """
    reads open orders from Django
    decides which should execute at current price snapshot
    alls Django to execute them
    """

    def __init__(self):
        self.client = DjangoOrdersClient()

    def run_once(self, prices: Dict[str, Decimal]):

        orders = self.client.get_open_orders()

        for o in orders:
            sym = (o.get("instrument_display") or "").split(" ")[0].strip()
            if not sym:
                continue

            px = prices.get(sym.upper())
            if px is None:
                continue

            if self.should_execute(o, px):
                self.client.execute_order(o["id"])

    @staticmethod
    def should_execute(order: dict, price: Decimal) -> bool:
        side = order["side"]
        ot = order["order_type"]

        limit_price = order.get("limit_price")
        stop_price = order.get("stop_price")

        limit_price = Decimal(limit_price) if limit_price is not None else None
        stop_price = Decimal(stop_price) if stop_price is not None else None

        if ot == "MARKET":
            return True

        if ot == "LIMIT":
            if limit_price is None:
                return False
            return price <= limit_price if side == "BUY" else price >= limit_price

        if ot == "STOP":
            if stop_price is None:
                return False
            return price >= stop_price if side == "BUY" else price <= stop_price

        if ot == "STOP_LIMIT":
            if stop_price is None or limit_price is None:
                return False

            triggered = price >= stop_price if side == "BUY" else price <= stop_price
            if not triggered:
                return False

            return price <= limit_price if side == "BUY" else price >= limit_price

        return False
