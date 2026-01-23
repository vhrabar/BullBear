from __future__ import annotations

import argparse
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Iterable, List, Optional, Dict, Any

from massive import RESTClient

from configuration import settings
from repo import MarketDataRepository


# -----------------------------
# Helpers
# -----------------------------

def utc_now() -> datetime:
    return datetime.now(tz=timezone.utc)


def parse_utc_datetime(s: str) -> datetime:
    """
    Accepts:
      - YYYY-MM-DD
      - YYYY-MM-DDTHH:MM:SSZ
      - YYYY-MM-DDTHH:MM:SS+00:00
    Returns timezone-aware UTC datetime.
    """
    s = s.strip()

    # Date only
    if len(s) == 10 and s.count("-") == 2:
        d = datetime.strptime(s, "%Y-%m-%d")
        return d.replace(tzinfo=timezone.utc)

    # Common "Z" form
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"

    # ISO with timezone offset
    return datetime.fromisoformat(s).astimezone(timezone.utc)


def dt_to_datestr(d: datetime) -> str:
    return d.strftime("%Y-%m-%d")


def floor_to_10min(dt: datetime) -> datetime:
    # Ensure strict 10-minute boundary alignment
    # dt is timezone-aware UTC
    minute = (dt.minute // 10) * 10
    return dt.replace(minute=minute, second=0, microsecond=0)


def chunk_range(start: datetime, end: datetime, chunk_days: int) -> Iterable[tuple[datetime, datetime]]:
    """
    Generate [start,end) in chunked intervals.
    """
    cur = start
    while cur < end:
        nxt = min(cur + timedelta(days=chunk_days), end)
        yield cur, nxt
        cur = nxt


@dataclass
class Agg1m:
    """
    Normalized 1-minute bar structure from Massive.
    Times are UTC datetimes.
    """
    t: datetime
    o: float
    h: float
    l: float
    c: float
    v: int


@dataclass
class Candle10m:
    start_time: datetime
    end_time: datetime
    open_price: float
    high_price: float
    low_price: float
    close_price: float
    volume: int


def fetch_massive_1m_bars(
        client: RESTClient,
        symbol: str,
        start: datetime,
        end: datetime,
        *,
        limit: int = 50000
) -> List[Agg1m]:
    """
    Fetches 1-minute OHLCV aggregates from Massive for [start,end).
    Returns list sorted by timestamp ascending.
    """

    bars: List[Agg1m] = []

    from_str = dt_to_datestr(start)
    to_str = dt_to_datestr(end)

    it = client.list_aggs(symbol, 1, "minute", from_str, to_str, limit=limit)

    for a in it:
        ts_ms = getattr(a, "timestamp", None)
        if ts_ms is None:
            ts_ms = getattr(a, "t", None)

        if ts_ms is None:
            # unexpected
            continue

        t = datetime.fromtimestamp(ts_ms / 1000, tz=timezone.utc)

        o = float(getattr(a, "open", getattr(a, "o", 0.0)))
        h = float(getattr(a, "high", getattr(a, "h", 0.0)))
        l = float(getattr(a, "low", getattr(a, "l", 0.0)))
        c = float(getattr(a, "close", getattr(a, "c", 0.0)))
        v = int(getattr(a, "volume", getattr(a, "v", 0)) or 0)

        if t < start or t >= end:
            continue

        bars.append(Agg1m(t=t, o=o, h=h, l=l, c=c, v=v))

    bars.sort(key=lambda x: x.t)
    return bars


def aggregate_10m(bars: List[Agg1m]) -> List[Candle10m]:
    """
    Aggregate sorted 1-minute bars into strict 10-minute candles aligned on 10-minute UTC boundaries.
    """
    if not bars:
        return []

    out: List[Candle10m] = []

    # group by 10-min bucket
    bucket_start = floor_to_10min(bars[0].t)
    bucket_end = bucket_start + timedelta(minutes=10)

    o = None
    h = None
    l = None
    c = None
    v_sum = 0

    def flush_bucket():
        nonlocal o, h, l, c, v_sum, bucket_start, bucket_end
        if o is None or h is None or l is None or c is None:
            return
        out.append(Candle10m(
            start_time=bucket_start,
            end_time=bucket_end,
            open_price=o,
            high_price=h,
            low_price=l,
            close_price=c,
            volume=v_sum,
        ))

    for b in bars:
        while b.t >= bucket_end:
            flush_bucket()
            bucket_start = bucket_end
            bucket_end = bucket_start + timedelta(minutes=10)
            o = h = l = c = None
            v_sum = 0

        if b.t < bucket_start or b.t >= bucket_end:
            continue

        if o is None:
            o = b.o
            h = b.h
            l = b.l
        else:
            h = max(h, b.h)
            l = min(l, b.l)

        c = b.c
        v_sum += b.v

    flush_bucket()
    return out


# -----------------------------
# Insert into DB
# -----------------------------

def upsert_10m_candles(
        repo: MarketDataRepository,
        instrument_id: int,
        candles: List[Candle10m],
        *,
        data_source: str = "massive_backfill",
        dry_run: bool = False,
        sleep_seconds: float = 0.0
) -> int:
    """
    Upsert candles using the existing repository.
    Returns number of candles processed.
    """
    count = 0
    for c in candles:
        payload = {
            "instrument_id": instrument_id,
            "start_time": c.start_time,
            "end_time": c.end_time,
            "open_price": c.open_price,
            "high_price": c.high_price,
            "low_price": c.low_price,
            "close_price": c.close_price,
            "volume": c.volume,
            "data_source": data_source,
            "updated_at": utc_now(),
        }

        if dry_run or settings.TEST_MODE:
            print("[DRY] UPSERT CANDLE:", payload)
        else:
            repo.upsert_candle(payload)

        count += 1
        if sleep_seconds:
            time.sleep(sleep_seconds)

    return count


# -----------------------------
# CLI
# -----------------------------

def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Backfill Massive 1-minute bars -> 10-minute candles into Postgres.")

    p.add_argument("--start", type=str, default=None,
                   help="UTC start date/time. Formats: YYYY-MM-DD or ISO like 2025-07-01T00:00:00Z")
    p.add_argument("--end", type=str, default=None,
                   help="UTC end date/time. Formats: YYYY-MM-DD or ISO like 2026-01-01T00:00:00Z")

    p.add_argument("--months", type=int, default=6,
                   help="How many months back to backfill (approx 30 days each). Used only if --start not provided.")

    p.add_argument("--chunk-days", type=int, default=7,
                   help="Fetch history in chunks of N days (rate-limit friendly). Default 7.")

    p.add_argument("--symbols", nargs="*", default=None,
                   help="Optional explicit tickers to backfill. If omitted, uses active instruments in DB.")

    p.add_argument("--dry-run", action="store_true",
                   help="Do not write to DB; only print what would happen.")

    p.add_argument("--sleep", type=float, default=0.0,
                   help="Sleep seconds between candle upserts (usually 0).")

    p.add_argument("--limit", type=int, default=50000,
                   help="Massive list_aggs limit parameter.")

    return p.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    args = parse_args(argv)

    if not settings.MASSIVE_API_KEY:
        print("ERROR: MASSIVE_API_KEY not set.")
        return 2

    if args.months <= 0:
        print("ERROR: --months must be positive.")
        return 2

    repo = MarketDataRepository()
    instrument_map = repo.load_instrument_map()

    if args.symbols:
        symbols = [s.upper().replace("AM.", "") for s in args.symbols]
    else:
        symbols = sorted(instrument_map.keys())

    client = RESTClient(settings.MASSIVE_API_KEY)

    if args.end:
        end = parse_utc_datetime(args.end)
    else:
        end = utc_now()

    if args.start:
        start = parse_utc_datetime(args.start)
    else:
        start = end - timedelta(days=args.months * 30)

    if start >= end:
        print("ERROR: start must be < end.")
        return 2

    # Normalize start to 10-min boundary to keep perfect alignment
    start = floor_to_10min(start)

    print("========== BACKFILL CONFIG ==========")
    print("Start:", start.isoformat())
    print("End:  ", end.isoformat())
    print("Symbols:", len(symbols))
    print("Chunk days:", args.chunk_days)
    print("Dry-run:", args.dry_run or settings.TEST_MODE)
    print("=====================================")

    total_candles = 0

    for sym in symbols:
        instrument_id = instrument_map.get(sym)
        if not instrument_id:
            print(f"[SKIP] Symbol {sym} not found in DB instrument map.")
            continue

        print(f"\n=== Backfilling {sym} (instrument_id={instrument_id}) ===")

        sym_candles = 0

        for cstart, cend in chunk_range(start, end, args.chunk_days):
            try:
                bars_1m = fetch_massive_1m_bars(
                    client=client,
                    symbol=sym,
                    start=cstart,
                    end=cend,
                    limit=args.limit,
                )

                if not bars_1m:
                    print(f"[{sym}] {dt_to_datestr(cstart)} -> {dt_to_datestr(cend)} : no 1m bars")
                    continue

                candles_10m = aggregate_10m(bars_1m)

                print(
                    f"[{sym}] {dt_to_datestr(cstart)} -> {dt_to_datestr(cend)} : "
                    f"1m={len(bars_1m)} => 10m={len(candles_10m)}"
                )

                sym_candles += upsert_10m_candles(
                    repo=repo,
                    instrument_id=instrument_id,
                    candles=candles_10m,
                    dry_run=args.dry_run,
                    sleep_seconds=args.sleep,
                )

            except Exception as exc:
                print(f"[ERROR] {sym} chunk {cstart.isoformat()} -> {cend.isoformat()}: {type(exc).__name__}: {exc}")
                # continue with next chunk
                continue

        total_candles += sym_candles
        print(f"=== Done {sym}. candles_upserted={sym_candles} ===")

    print("\n========== BACKFILL DONE ==========")
    print("Total candles upserted:", total_candles)
    print("==================================")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
