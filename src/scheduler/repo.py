import traceback
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, Optional, List, Dict

from sqlalchemy import create_engine, desc
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.postgresql import insert
from orm_model import (
    InstrumentQuote, InstrumentIntervalData, Instrument, Fund, FundHolding,
    FundNAVHistory, Order, OrderFill, UserPortfolio, PortfolioHolding, PortfolioSnapshot
)
from configuration import settings


engine = create_engine(settings.DB_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine)


class MarketDataRepository:
    @staticmethod
    def load_instrument_map() -> dict[str, int]:
        with SessionLocal() as session:
            rows = session.query(Instrument).filter(Instrument.is_active.is_(True)).all()
            return {row.symbol.upper(): row.id for row in rows}

    @staticmethod
    def upsert_quote(payload: dict):
        try:
            with SessionLocal() as session:
                if "instrument_id" not in payload:
                    if "instrument" in payload:
                        sym = payload.pop("instrument")
                        inst = session.query(Instrument).filter(Instrument.symbol == sym.upper()).one_or_none()
                        if inst is None:
                            raise ValueError(f"Unknown instrument symbol '{sym}'")
                        payload["instrument_id"] = inst.id
                    else:
                        raise ValueError(
                            "InstrumentQuote expects FK field 'instrument_id' in payload. "
                            "Provide 'instrument_id' or an 'instrument' symbol."
                        )

                conflict_keys = {"instrument_id"}
                update_payload = {k: v for k, v in payload.items() if k not in conflict_keys}

                stmt = insert(InstrumentQuote).values(payload)
                stmt = stmt.on_conflict_do_update(
                    index_elements=["instrument_id"],
                    set_=update_payload
                )

                session.execute(stmt)
                session.commit()

        except (SQLAlchemyError, Exception) as exc:
            print("\n[ERROR] Quote UPSERT failed.")
            print("[PAYLOAD]:", payload)
            print(type(exc).__name__, str(exc))
            traceback.print_exc()

    @staticmethod
    def upsert_candle(payload: dict):
        try:
            print("[upsert_candle] called with payload:", payload)
            with SessionLocal() as session:
                conflict_keys = {"instrument_id", "start_time"}
                update_payload = {k: v for k, v in payload.items() if k not in conflict_keys}

                # Upsert interval data (InstrumentIntervalData)
                stmt = insert(InstrumentIntervalData).values(payload)
                stmt = stmt.on_conflict_do_update(
                    index_elements=["instrument_id", "start_time"],
                    set_=update_payload
                )
                res = session.execute(stmt)
                print(f"[upsert_candle] interval upsert executed, result rowcount={getattr(res, 'rowcount', None)}")

                close_price = payload.get("close_price")
                if close_price is not None:
                    now = datetime.now(tz=timezone.utc)
                    quote_payload = {
                        "instrument_id": payload["instrument_id"],
                        "bid_price": close_price,
                        "bid_size": 0,
                        "ask_price": close_price,
                        "ask_size": 0,
                        "last_price": close_price,
                        "currency": payload.get("currency", "USD"),
                        "exchange": payload.get("exchange", ""),
                        "market_state": payload.get("market_state", ""),
                        "daily_change": payload.get("daily_change", 0),
                        "daily_change_percent": payload.get("daily_change_percent", 0),
                        "timestamp": payload.get("end_time") or payload.get("updated_at") or now,
                        "updated_at": payload.get("updated_at") or now,
                    }

                    q_update = {k: v for k, v in quote_payload.items() if k != "instrument_id"}
                    stmt2 = insert(InstrumentQuote).values(quote_payload)
                    stmt2 = stmt2.on_conflict_do_update(
                        index_elements=["instrument_id"],
                        set_=q_update,
                    )
                    res2 = session.execute(stmt2)

                # Create snapshots for portfolios affected by this instrument
                MarketDataRepository.create_snapshots_for_instrument(
                    session=session,
                    instrument_id=payload["instrument_id"],
                    ts=payload["end_time"]
                )

                session.commit()

        except SQLAlchemyError as exc:
            print("\n[ERROR] Candle UPSERT failed.")
            print("[PAYLOAD]:", payload)
            print(type(exc).__name__, str(exc))
            traceback.print_exc()
        except Exception as exc:
            print("\n[ERROR] Candle UPSERT unexpected error.")
            print("[PAYLOAD]:", payload)
            print(type(exc).__name__, str(exc))
            traceback.print_exc()

    # Fund NAV Methods
    @staticmethod
    def get_active_funds() -> List[Dict]:
        """Get all active funds."""
        try:
            with SessionLocal() as session:
                funds = session.query(Fund).filter(Fund.is_active == True).all()
                return [
                    {
                        'id': f.id,
                        'name': f.name,
                        'nav_per_unit': f.nav_per_unit,
                        'total_units': f.total_units
                    }
                    for f in funds
                ]
        except SQLAlchemyError as exc:
            print(f"[ERROR] Failed to get active funds: {exc}")
            return []

    @staticmethod
    def get_fund_holdings(fund_id: int) -> List[Dict]:
        """Get all holdings for a fund."""
        try:
            with SessionLocal() as session:
                holdings = session.query(FundHolding).filter(
                    FundHolding.fund_id == fund_id
                ).all()
                return [
                    {
                        'id': h.id,
                        'instrument_id': h.instrument_id,
                        'weight_percent': h.weight_percent
                    }
                    for h in holdings
                ]
        except SQLAlchemyError as exc:
            print(f"[ERROR] Failed to get fund holdings: {exc}")
            return []

    @staticmethod
    def get_latest_price(instrument_id: int) -> Optional[Decimal]:
        """Get the latest close price for an instrument."""
        try:
            with SessionLocal() as session:
                candle = session.query(InstrumentIntervalData).filter(
                    InstrumentIntervalData.instrument_id == instrument_id
                ).order_by(desc(InstrumentIntervalData.start_time)).first()

                if candle:
                    return Decimal(str(candle.close_price))
                return None
        except SQLAlchemyError as exc:
            print(f"[ERROR] Failed to get latest price: {exc}")
            return None

    @staticmethod
    def get_base_price(instrument_id: int, fund_id: int) -> Optional[Decimal]:
        """
        Get the base price for an instrument when the fund was created.
        Uses the oldest NAV history record or falls back to oldest price data.
        """
        try:
            with SessionLocal() as session:
                # Try to get the first NAV history record date for the fund
                first_nav = session.query(FundNAVHistory).filter(
                    FundNAVHistory.fund_id == fund_id
                ).order_by(FundNAVHistory.recorded_at).first()

                if first_nav:
                    # Get price around that time
                    candle = session.query(InstrumentIntervalData).filter(
                        InstrumentIntervalData.instrument_id == instrument_id,
                        InstrumentIntervalData.start_time <= first_nav.recorded_at
                    ).order_by(desc(InstrumentIntervalData.start_time)).first()

                    if candle:
                        return Decimal(str(candle.close_price))

                # Fallback: get the oldest price we have
                oldest_candle = session.query(InstrumentIntervalData).filter(
                    InstrumentIntervalData.instrument_id == instrument_id
                ).order_by(InstrumentIntervalData.start_time).first()

                if oldest_candle:
                    return Decimal(str(oldest_candle.close_price))

                return None
        except SQLAlchemyError as exc:
            print(f"[ERROR] Failed to get base price: {exc}")
            return None

    @staticmethod
    def update_fund_nav(fund_id: int, nav_per_unit: Decimal):
        """Update the current NAV per unit for a fund."""
        try:
            with SessionLocal() as session:
                fund = session.query(Fund).filter(Fund.id == fund_id).first()
                if fund:
                    fund.nav_per_unit = nav_per_unit
                    fund.updated_at = datetime.now(tz=timezone.utc)
                    session.commit()
        except SQLAlchemyError as exc:
            print(f"[ERROR] Failed to update fund NAV: {exc}")
            traceback.print_exc()

    @staticmethod
    def record_nav_history(fund_id: int, nav_per_unit: Decimal, total_units: Decimal):
        """Record a NAV history entry for performance tracking."""
        try:
            with SessionLocal() as session:
                history = FundNAVHistory(
                    fund_id=fund_id,
                    nav_per_unit=nav_per_unit,
                    total_units=total_units,
                    recorded_at=datetime.now(tz=timezone.utc)
                )
                session.add(history)
                session.commit()
        except SQLAlchemyError as exc:
            print(f"[ERROR] Failed to record NAV history: {exc}")
            traceback.print_exc()

    # Order Execution Methods
    @staticmethod
    def load_open_orders() -> List:
        """Load all open orders (status = OPEN or PARTIALLY_FILLED)."""
        try:
            with SessionLocal() as session:
                orders = session.query(Order).filter(
                    Order.status.in_(["OPEN", "PARTIALLY_FILLED"])
                ).all()
                # Detach from session to use outside
                session.expunge_all()
                return orders
        except SQLAlchemyError as exc:
            print(f"[ERROR] Failed to load open orders: {exc}")
            traceback.print_exc()
            return []

    @staticmethod
    def get_latest_prices_for_instruments(symbols: List[str]) -> Dict[str, Decimal]:
        """Get the latest prices for a list of instrument symbols."""
        if not symbols:
            return {}
        try:
            with SessionLocal() as session:
                # Get instrument IDs for symbols
                instruments = session.query(Instrument).filter(
                    Instrument.symbol.in_([s.upper() for s in symbols])
                ).all()

                symbol_to_id = {inst.symbol.upper(): inst.id for inst in instruments}

                prices = {}
                for symbol, inst_id in symbol_to_id.items():
                    # Try quote first
                    quote = session.query(InstrumentQuote).filter(
                        InstrumentQuote.instrument_id == inst_id
                    ).first()

                    if quote and quote.last_price:
                        prices[symbol] = Decimal(str(quote.last_price))
                    else:
                        # Fallback to latest candle
                        candle = session.query(InstrumentIntervalData).filter(
                            InstrumentIntervalData.instrument_id == inst_id
                        ).order_by(desc(InstrumentIntervalData.start_time)).first()

                        if candle:
                            prices[symbol] = Decimal(str(candle.close_price))

                return prices
        except SQLAlchemyError as exc:
            print(f"[ERROR] Failed to get latest prices: {exc}")
            traceback.print_exc()
            return {}

    @staticmethod
    def create_fill_and_update_order(order_id: int, fill_qty: Decimal, fill_price: Decimal):
        """Create a fill record and update the order status."""
        try:
            with SessionLocal() as session:
                order = session.query(Order).filter(Order.id == order_id).first()
                if not order:
                    print(f"[WARN] Order {order_id} not found")
                    return

                now = datetime.now(tz=timezone.utc)

                # Create fill record
                fill = OrderFill(
                    order_id=order_id,
                    quantity=fill_qty,
                    price=fill_price,
                    executed_at=now,
                    created_at=now,
                )
                session.add(fill)

                # Update order
                prev_qty = Decimal(str(order.filled_quantity))
                new_qty = prev_qty + fill_qty

                if prev_qty == 0:
                    order.avg_fill_price = fill_price
                else:
                    prev_cost = (Decimal(str(order.avg_fill_price)) if order.avg_fill_price else Decimal("0")) * prev_qty
                    new_cost = fill_price * fill_qty
                    order.avg_fill_price = (prev_cost + new_cost) / new_qty

                order.filled_quantity = new_qty
                order.revision += 1
                order.updated_at = now

                if new_qty >= Decimal(str(order.quantity)):
                    order.status = "FILLED"
                    order.closed_at = now
                else:
                    order.status = "PARTIALLY_FILLED"

                session.commit()
                print(f"[FILL] Order {order_id}: filled {fill_qty} @ {fill_price}, total filled: {new_qty}")

        except SQLAlchemyError as exc:
            print(f"[ERROR] Failed to create fill and update order: {exc}")
            traceback.print_exc()

    @staticmethod
    def get_portfolio_balance(portfolio_id: int) -> Optional[Decimal]:
        """Get the current balance for a portfolio."""
        try:
            with SessionLocal() as session:
                portfolio = session.query(UserPortfolio).filter(
                    UserPortfolio.id == portfolio_id
                ).first()
                if portfolio:
                    return Decimal(str(portfolio.balance))
                return None
        except SQLAlchemyError as exc:
            print(f"[ERROR] Failed to get portfolio balance: {exc}")
            return None

    @staticmethod
    def reject_order(order_id: int, reason: str):
        """Reject an order due to insufficient balance or other reasons."""
        try:
            with SessionLocal() as session:
                order = session.query(Order).filter(Order.id == order_id).first()
                if not order:
                    print(f"[WARN] Order {order_id} not found for rejection")
                    return

                now = datetime.now(tz=timezone.utc)

                order.status = "REJECTED"
                order.reject_reason = reason
                order.closed_at = now
                order.revision += 1
                order.updated_at = now

                session.commit()
                print(f"[REJECT] Order {order_id}: {reason}")

        except SQLAlchemyError as exc:
            print(f"[ERROR] Failed to reject order: {exc}")
            traceback.print_exc()

    @staticmethod
    def create_snapshots_for_instrument(session, instrument_id: int, ts: datetime):
        """
        Create portfolio snapshots for all portfolios that hold the given instrument.
        Called when instrument price updates to capture portfolio value at that point in time.
        """
        try:
            # Find all holdings for this instrument
            holdings = session.query(PortfolioHolding).filter(
                PortfolioHolding.instrument_id == instrument_id
            ).all()

            if not holdings:
                return

            # Get all unique portfolio IDs that hold this instrument
            portfolio_ids = set(h.portfolio_id for h in holdings)

            # Get latest prices for all instruments (for calculating equity value)
            for portfolio_id in portfolio_ids:
                try:
                    # Get portfolio
                    portfolio = session.query(UserPortfolio).filter(
                        UserPortfolio.id == portfolio_id
                    ).first()

                    if not portfolio:
                        continue

                    # Get all holdings for this portfolio
                    portfolio_holdings = session.query(PortfolioHolding).filter(
                        PortfolioHolding.portfolio_id == portfolio_id
                    ).all()

                    # Calculate equity value using latest prices
                    equity_value = Decimal("0")
                    total_cost_basis = Decimal("0")

                    for holding in portfolio_holdings:
                        # Get latest price for this instrument
                        quote = session.query(InstrumentQuote).filter(
                            InstrumentQuote.instrument_id == holding.instrument_id
                        ).first()

                        if quote and quote.last_price:
                            price = Decimal(str(quote.last_price))
                        else:
                            # Fallback to latest candle
                            candle = session.query(InstrumentIntervalData).filter(
                                InstrumentIntervalData.instrument_id == holding.instrument_id
                            ).order_by(InstrumentIntervalData.start_time.desc()).first()

                            if candle:
                                price = Decimal(str(candle.close_price))
                            else:
                                price = Decimal(str(holding.average_price))

                        quantity = Decimal(str(holding.quantity))
                        avg_price = Decimal(str(holding.average_price))

                        equity_value += price * quantity
                        total_cost_basis += avg_price * quantity

                    cash_balance = Decimal(str(portfolio.balance))
                    total_value = cash_balance + equity_value

                    # Calculate unrealized P/L
                    unrealized_pl = equity_value - total_cost_basis
                    unrealized_pl_pct = (unrealized_pl / total_cost_basis * 100) if total_cost_basis > 0 else Decimal("0")

                    # Upsert snapshot (update if exists for same portfolio+ts, else insert)
                    existing = session.query(PortfolioSnapshot).filter(
                        PortfolioSnapshot.portfolio_id == portfolio_id,
                        PortfolioSnapshot.ts == ts
                    ).first()

                    if existing:
                        existing.cash_balance = cash_balance
                        existing.equity_value = equity_value
                        existing.total_value = total_value
                        existing.unrealized_pl = unrealized_pl
                        existing.unrealized_pl_pct = unrealized_pl_pct
                    else:
                        snapshot = PortfolioSnapshot(
                            portfolio_id=portfolio_id,
                            ts=ts,
                            cash_balance=cash_balance,
                            equity_value=equity_value,
                            total_value=total_value,
                            unrealized_pl=unrealized_pl,
                            unrealized_pl_pct=unrealized_pl_pct,
                            realized_pl=Decimal("0"),
                            realized_pl_pct=Decimal("0"),
                        )
                        session.add(snapshot)

                except Exception as e:
                    print(f"[WARN] Failed to create snapshot for portfolio {portfolio_id}: {e}")
                    continue

        except Exception as exc:
            print(f"[ERROR] Failed to create snapshots for instrument {instrument_id}: {exc}")
            traceback.print_exc()

