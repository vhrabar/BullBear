from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Dict, List
from massive.websocket.models import EquityAgg
from configuration import settings
from repo import MarketDataRepository
from execution_service import OrderExecutionService
from execution_engine import ExecutionEngine


class MinuteAggregateIngestionService:
    """
    Aggregates live 1-minute aggregates into STRICT 10-minute candles.
    """

    BUCKET_MINUTES = 10

    def __init__(self):
        self.repo = MarketDataRepository()
        self.instrument_map = self.repo.load_instrument_map()
        self.execution = OrderExecutionService()

        # in-memory aggregation store
        # key: (instrument_id, bucket_start)
        self.buckets: Dict[tuple[int, datetime], dict] = {}

        # executor helpper
        self.latest_prices = {}
        self.engine = ExecutionEngine()

    def handle_messages(self, messages: List[EquityAgg]):
        hasBeenChanged = False

        for m in messages:
            if m.event_type != "AM":
                continue
            self.latest_prices[m.symbol.upper()] = Decimal(str(m.close))
            touched = True

            instrument_id = self.map_symbol_to_id(m.symbol)
            if instrument_id < 0:
                continue

            start = self._to_utc(m.start_timestamp)
            bucket_start = self._bucket_start(start)
            bucket_end = bucket_start + timedelta(minutes=self.BUCKET_MINUTES)

            key = (instrument_id, bucket_start)

            if key not in self.buckets:
                self._create_bucket(
                    key=key,
                    instrument_id=instrument_id,
                    bucket_start=bucket_start,
                    bucket_end=bucket_end,
                    m=m,
                )
            else:
                self._update_bucket(self.buckets[key], m)

            self._flush_completed_buckets(now=start)
        if hasBeenChanged:
            self.engine.run_once(self.latest_prices)

    def _create_bucket(self, key, instrument_id, bucket_start, bucket_end, m):
        self.buckets[key] = {
            "instrument_id": instrument_id,
            "start_time": bucket_start,
            "end_time": bucket_end,
            "open_price": m.open,
            "high_price": m.high,
            "low_price": m.low,
            "close_price": m.close,
            "volume": m.volume,
            "data_source": "massive-test",
            "updated_at": datetime.now(tz=timezone.utc),
        }

    def _update_bucket(self, bucket: dict, m):
        bucket["high_price"] = max(bucket["high_price"], m.high)
        bucket["low_price"] = min(bucket["low_price"], m.low)
        bucket["close_price"] = m.close
        bucket["volume"] += m.volume
        bucket["updated_at"] = datetime.now(tz=timezone.utc)

    def _flush_completed_buckets(self, now: datetime):
        """
        Persist only buckets whose window has CLOSED.
        """
        to_flush = []

        for key, bucket in self.buckets.items():
            if now >= bucket["end_time"]:
                to_flush.append(key)

        for key in to_flush:
            payload = self.buckets.pop(key)

            if settings.TEST_MODE:
                print("\n=== TEST MODE (10m Candle) ===")
                print(payload)
                print("=============================\n")
                continue

            self.repo.upsert_candle(payload)

    @staticmethod
    def _to_utc(ms: int) -> datetime:
        return datetime.fromtimestamp(ms / 1000, tz=timezone.utc)

    def _bucket_start(self, dt: datetime) -> datetime:
        minute = (dt.minute // self.BUCKET_MINUTES) * self.BUCKET_MINUTES
        return dt.replace(minute=minute, second=0, microsecond=0)

    def map_symbol_to_id(self, symbol: str) -> int:
        symbol = symbol.upper()

        if symbol in self.instrument_map:
            return self.instrument_map[symbol]

        self.instrument_map = self.repo.load_instrument_map()

        if symbol in self.instrument_map:
            return self.instrument_map[symbol]

        print(f"[ERROR] Instrument '{symbol}' not found.")
        return -1
