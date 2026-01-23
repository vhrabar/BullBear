import traceback
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, Optional, List, Dict

from sqlalchemy import create_engine, desc
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.postgresql import insert
from orm_model import InstrumentQuote, InstrumentIntervalData, Instrument, Fund, FundHolding, FundNAVHistory
from configuration import settings


engine = create_engine(settings.DB_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine)


class MarketDataRepository:
    @staticmethod
    def load_instrument_map() -> dict[Any, InstrumentedAttribute[int]]:
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
                    ts= payload["end_time"]
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
                    total_units=total_units
                )
                session.add(history)
                session.commit()
        except SQLAlchemyError as exc:
            print(f"[ERROR] Failed to record NAV history: {exc}")
            traceback.print_exc()

