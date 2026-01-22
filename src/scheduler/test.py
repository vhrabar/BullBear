from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

from service import MinuteAggregateIngestionService
from configuration import settings

def fake_equity_agg(symbol: str, start_dt: datetime, o=100, h=101, l=99, c=100.5, v=1000):
    """
    Creates a fake object shaped like massive.websocket.models.EquityAgg
    """
    return SimpleNamespace(
        event_type="AM",
        symbol=symbol,
        start_timestamp=int(start_dt.timestamp() * 1000),
        open=o,
        high=h,
        low=l,
        close=c,
        volume=v,
    )

def main():
    settings.TEST_MODE = False

    svc = MinuteAggregateIngestionService()

    now = datetime.now(tz=timezone.utc)
    start = now - timedelta(minutes=5)

    # fakse EE for Nvidia
    msgs = [
        fake_equity_agg("NVDA", start, o=100, h=102, l=99, c=101, v=500),
        fake_equity_agg("NVDA", start + timedelta(minutes=1), o=101, h=103, l=100, c=102, v=600),
    ]

    svc.handle_messages(msgs)

    print("Done. Check DB for candle/quote/snapshot inserts.")

if __name__ == "__main__":
    main()
