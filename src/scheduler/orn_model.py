from sqlalchemy.orm import declarative_base, mapped_column, Mapped
from sqlalchemy import (
    String,
    DateTime,
    Numeric,
    BigInteger,
    ForeignKey,
    UniqueConstraint,
    Index,
)

Base = declarative_base()


class InstrumentIntervalData(Base):
    __tablename__ = "trading_instrumentintervaldata"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    instrument_id: Mapped[int] = mapped_column(
        ForeignKey("trading_instrument.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    start_time: Mapped["datetime"] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    end_time: Mapped["datetime"] = mapped_column(DateTime(timezone=True), nullable=False)

    open_price: Mapped[float] = mapped_column(Numeric(20, 6), nullable=False)
    high_price: Mapped[float] = mapped_column(Numeric(20, 6), nullable=False)
    low_price: Mapped[float] = mapped_column(Numeric(20, 6), nullable=False)
    close_price: Mapped[float] = mapped_column(Numeric(20, 6), nullable=False)

    volume: Mapped[int] = mapped_column(BigInteger, nullable=True)
    data_source: Mapped[str] = mapped_column(String(64), nullable=True)

    updated_at: Mapped["datetime"] = mapped_column(DateTime(timezone=True), nullable=False)

    __table_args__ = (
        UniqueConstraint("instrument_id", "start_time", name="instrument_start_time_unique"),
        Index("instrument_start_time_idx", "instrument_id", "start_time"),
    )
