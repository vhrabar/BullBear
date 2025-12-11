from datetime import datetime, timezone
from typing import List
from massive.websocket.models import EquityAgg
from configuration import settings
from repo import MarketDataRepository


class MinuteAggregateIngestionService:

    def __init__(self):
        self.repo = MarketDataRepository()
        self.instrument_map = self.repo.load_instrument_map()

    def handle_messages(self, messages: List[EquityAgg]):
        for m in messages:
            if m.event_type != "AM":
                continue

            instrument_id = self.map_symbol_to_id(m.symbol)

            # -----------------------------
            # CANDLE (InstrumentIntervalData)
            # -----------------------------
            candle_payload = {
                "instrument_id": instrument_id,
                "start_time": datetime.utcfromtimestamp(m.start_timestamp / 1000),
                "end_time": datetime.utcfromtimestamp(m.end_timestamp / 1000),
                "open_price": m.open,
                "high_price": m.high,
                "low_price": m.low,
                "close_price": m.close,
                "volume": m.volume,
                "data_source": "massive",
                "updated_at": datetime.now(tz=timezone.utc),
            }

            # -----------------------------
            # QUOTE (InstrumentQuote)
            # -----------------------------
            quote_payload = {
                "instrument": m.symbol,
                "bid_price": m.open,
                "bid_size": m.volume,

                "ask_price": m.close,
                "ask_size": m.volume,

                "last_price": m.close,
                "currency": "USD",
                "exchange": "NASDAQ",
                "market_state": "open",

                "daily_change": m.close - m.open,
                "daily_change_percent": ((m.close - m.open) / m.open) * 100 if m.open else 0,

                "timestamp": datetime.now(tz=timezone.utc),
                "updated_at": datetime.now(tz=timezone.utc),
            }

            if settings.TEST_MODE:
                print("\n=== TEST MODE ===")
                print("CANDLE:", candle_payload)
                print("QUOTE:", quote_payload)
                print("=================\n")
                continue

            self.repo.upsert_candle(candle_payload)
            self.repo.upsert_quote(quote_payload)

    def map_symbol_to_id(self, symbol: str) -> int:
        symbol = symbol.upper()

        # cached
        if symbol in self.instrument_map:
            return self.instrument_map[symbol]

        # reload from DB
        print(f"Symbol '{symbol}' not found. Reloading instrument table...")
        self.instrument_map = self.repo.load_instrument_map()

        # and check again
        if symbol in self.instrument_map:
            return self.instrument_map[symbol]

        # still not found
        print(f"ERROR: Instrument '{symbol}' does not exist in Django DB.")
        return -1


