from massive import WebSocketClient
from massive.websocket.models import Feed, Market
from service import MinuteAggregateIngestionService
from fund_nav_service import FundNAVCalculationService
from configuration import settings
from stocks import get_subscribed_stocks
import time
import threading


"""
PRE-MARKET
    EST: 09:00–14:30 UTC
    EDT: 08:00–13:30 UTC

REGULAR TRADING
    EST: 14:30–21:00 UTC
    EDT: 13:30–20:00 UTC

AFTER-HOURS
    EST: 21:00–01:00 UTC (next day)
    EDT: 20:00–00:00 UTC (midnight)
"""


# How often to update fund NAVs (in seconds)
NAV_UPDATE_INTERVAL = 60


def nav_update_loop():
    """Background thread to periodically update fund NAVs."""
    nav_service = FundNAVCalculationService()
    while True:
        try:
            print("\n[NAV] Calculating fund NAVs...")
            nav_service.calculate_and_update_all_funds()
            print("[NAV] Fund NAV update complete.\n")
        except Exception as e:
            print(f"[NAV ERROR] {e}")
        time.sleep(NAV_UPDATE_INTERVAL)


def main():
    print("Starting Massive ingestion client...")

    if settings.TEST_MODE:
        print("TEST_MODE = TRUE — No DB writes will occur.")

    # Start NAV calculation background thread
    nav_thread = threading.Thread(target=nav_update_loop, daemon=True)
    nav_thread.start()
    print(f"[NAV] Background NAV calculator started (interval: {NAV_UPDATE_INTERVAL}s)")

    service = MinuteAggregateIngestionService()

    client = WebSocketClient(
        api_key=settings.MASSIVE_API_KEY,
        feed=Feed.Delayed,
        market=Market.Stocks,
    )

    client.subscribe(*get_subscribed_stocks())
    client.run(service.handle_messages)


if __name__ == "__main__":
    main()
