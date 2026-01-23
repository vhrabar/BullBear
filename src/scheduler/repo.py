import traceback
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, Optional, List, Dict

from sqlalchemy import create_engine, desc
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker, InstrumentedAttribute
from sqlalchemy.dialects.postgresql import insert
from orm_model import InstrumentQuote, InstrumentIntervalData, Instrument, Fund, FundHolding, FundNAVHistory
from configuration import settings


engine = create_engine(settings.DB_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine)


class MarketDataRepository:
    @staticmethod
    def load_instrument_map() -> dict[Any, InstrumentedAttribute[int]]:
        with SessionLocal() as session:
            rows = session.query(Instrument).filter(Instrument.is_active == True).all()
            return {row.symbol.upper(): row.id for row in rows}

    @staticmethod
    def upsert_quote(payload: dict):
        try:
            with SessionLocal() as session:
                stmt = insert(InstrumentQuote).values(payload)
                stmt = stmt.on_conflict_do_update(
                    index_elements=["instrument"],
                    set_=payload
                )

                session.execute(stmt)
                session.commit()

        except SQLAlchemyError as exc:
            print("\n[ERROR] Quote UPSERT failed.")
            print("[PAYLOAD]:", payload)
            print(type(exc).__name__, str(exc))
            traceback.print_exc()


    @staticmethod
    def upsert_candle(payload: dict):
        try:
            with SessionLocal() as session:
                stmt = insert(InstrumentIntervalData).values(payload)
                stmt = stmt.on_conflict_do_update(
                    index_elements=["instrument_id", "start_time"],
                    set_=payload
                )

                session.execute(stmt)
                session.commit()

        except SQLAlchemyError as exc:
            print("\n[ERROR] Candle UPSERT failed.")
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

