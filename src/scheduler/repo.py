from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.postgresql import insert
from orm_model import InstrumentQuote, InstrumentIntervalData, Instrument
from configuration import settings


engine = create_engine(settings.DB_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine)


class MarketDataRepository:
    def load_instrument_map(self) -> dict[str, int]:
        with SessionLocal() as session:
            rows = session.query(Instrument).filter(Instrument.is_active == True).all()
            return {row.symbol.upper(): row.id for row in rows}

    def upsert_quote(self, payload: dict):
        with SessionLocal() as session:
            stmt = insert(InstrumentQuote).values(payload)
            stmt = stmt.on_conflict_do_update(
                index_elements=["instrument"],
                set_=payload
            )
            session.execute(stmt)
            session.commit()

    def upsert_candle(self, payload: dict):
        with SessionLocal() as session:
            stmt = insert(InstrumentIntervalData).values(payload)
            stmt = stmt.on_conflict_do_update(
                index_elements=["instrument_id", "start_time"],
                set_=payload
            )
            session.execute(stmt)
            session.commit()
