from massive import WebSocketClient
from massive.websocket.models import Feed, Market
from service import MinuteAggregateIngestionService
from configuration import settings
from stocks import get_subscribed_stocks


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


def main():
    print("Starting Massive ingestion client...")

    if settings.TEST_MODE:
        print("TEST_MODE = TRUE — No DB writes will occur.")

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
