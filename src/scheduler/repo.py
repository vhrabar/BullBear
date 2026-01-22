import traceback
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import create_engine, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker, InstrumentedAttribute
from sqlalchemy.dialects.postgresql import insert
from orm_model import InstrumentQuote, InstrumentIntervalData, Instrument
from orm_model import Order as ORMOrder, OrderFill as ORMOrderFill, InstrumentQuote, Instrument

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


    @staticmethod
    def load_open_orders():
        with SessionLocal() as session:
            stmt = (
                select(ORMOrder)
                .where(ORMOrder.status.in_(["OPEN", "PARTIALLY_FILLED"]))
            )
            return list(session.execute(stmt).scalars().all())

    @staticmethod
    def get_latest_prices_for_instruments(symbols: list[str]) -> dict[str, float]:
        if not symbols:
            return {}
        with SessionLocal() as session:
            stmt = select(InstrumentQuote).where(InstrumentQuote.instrument.in_(symbols))
            rows = session.execute(stmt).scalars().all()
            return {r.instrument.upper(): float(r.last_price) for r in rows}

    @staticmethod
    def create_fill_and_update_order(order_id: int, fill_qty, fill_price):
        now = datetime.now(tz=timezone.utc)

        with SessionLocal() as session:
            # insert fill
            fill = ORMOrderFill(
                order_id=order_id,
                quantity=fill_qty,
                price=fill_price,
                executed_at=now,
                created_at=now,
            )
            session.add(fill)

            # update order quantities & avg fill price
            order = session.get(ORMOrder, order_id)
            prev_qty = float(order.filled_quantity)
            new_qty = prev_qty + float(fill_qty)

            # weighted avg
            if prev_qty == 0:
                avg = float(fill_price)
            else:
                avg = (float(order.avg_fill_price) * prev_qty + float(fill_price) * float(fill_qty)) / new_qty

            order.filled_quantity = new_qty
            order.avg_fill_price = avg
            order.revision += 1

            if new_qty >= float(order.quantity):
                order.status = "FILLED"
                order.closed_at = now
            else:
                order.status = "PARTIALLY_FILLED"

            order.updated_at = now

            session.commit()
