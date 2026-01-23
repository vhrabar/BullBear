import traceback
from datetime import datetime
from typing import Any

from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.postgresql import insert
from orm_model import InstrumentQuote, InstrumentIntervalData, Instrument
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
