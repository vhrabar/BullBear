from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal

from repo import MarketDataRepository
from django_client import DjangoOrdersClient


@dataclass(frozen=True)
class ExecutionResult:
    order_id: int
    filled_qty: Decimal
    fill_price: Decimal


class OrderExecutionService:
    """
    Executes open orders using latest quote price.
    - MARKET: fill immediately at last_price
    - LIMIT: fill when price crosses limit
    - STOP: trigger -> fill at market
    - STOP_LIMIT: trigger -> treat as LIMIT
    Calls Django /api/trading/buy or /api/trading/sell to update portfolio.
    """

    def __init__(self):
        self.repo = MarketDataRepository()
        self.instrument_map = self.repo.load_instrument_map()
        self.django_client = DjangoOrdersClient()

    def run_once(self) -> list[ExecutionResult]:
        orders = self.repo.load_open_orders()
        if not orders:
            return []

        instrument_id_to_symbol = self._load_instrument_symbol_map()

        symbols = []
        for o in orders:
            sym = instrument_id_to_symbol.get(o.instrument_id)
            if sym:
                symbols.append(sym)

        prices = self.repo.get_latest_prices_for_instruments(symbols)

        results: list[ExecutionResult] = []

        for o in orders:
            sym = instrument_id_to_symbol.get(o.instrument_id)
            if not sym:
                continue

            price = prices.get(sym.upper())
            if price is None:
                continue

            should_fill = self._should_fill(o, Decimal(str(price)))
            if not should_fill:
                continue

            remaining = Decimal(str(o.quantity)) - Decimal(str(o.filled_quantity))
            if remaining <= 0:
                continue

            fill_qty = remaining.quantize(Decimal('0.0001'))
            fill_price = Decimal(str(price))

            # Call Django buy/sell endpoint to update portfolio
            try:
                if o.side == "BUY":
                    success = self.django_client.buy(
                        portfolio_id=o.portfolio_id,
                        instrument_symbol=sym,
                        quantity=fill_qty,
                        price=fill_price,
                    )
                else:  # SELL
                    success = self.django_client.sell(
                        portfolio_id=o.portfolio_id,
                        instrument_symbol=sym,
                        quantity=fill_qty,
                        price=fill_price,
                    )

                if not success:
                    print(f"[WARN] Order {o.id} - Django buy/sell failed, skipping")
                    continue

            except Exception as e:
                print(f"[ERROR] Failed to call Django for order {o.id}: {e}")
                continue

            # Update order status in DB (create fill record and mark as filled)
            self.repo.create_fill_and_update_order(o.id, fill_qty, fill_price)

            print(f"[EXEC] Order {o.id} filled: {o.side} {fill_qty} {sym} @ {fill_price}")
            results.append(ExecutionResult(order_id=o.id, filled_qty=fill_qty, fill_price=fill_price))

        return results

    def _should_fill(self, order, current_price: Decimal) -> bool:
        side = order.side
        ot = order.order_type

        limit_price = Decimal(str(order.limit_price)) if order.limit_price is not None else None
        stop_price = Decimal(str(order.stop_price)) if order.stop_price is not None else None

        if ot == "MARKET":
            return True

        if ot == "LIMIT":
            if limit_price is None:
                return False
            return current_price <= limit_price if side == "BUY" else current_price >= limit_price

        if ot == "STOP":
            if stop_price is None:
                return False
            return current_price >= stop_price if side == "BUY" else current_price <= stop_price

        if ot == "STOP_LIMIT":
            if stop_price is None or limit_price is None:
                return False

            triggered = current_price >= stop_price if side == "BUY" else current_price <= stop_price
            if not triggered:
                return False

            return current_price <= limit_price if side == "BUY" else current_price >= limit_price

        return False

    def _load_instrument_symbol_map(self) -> dict[int, str]:
        inv = {}
        for sym, iid in self.instrument_map.items():
            inv[iid] = sym
        return inv