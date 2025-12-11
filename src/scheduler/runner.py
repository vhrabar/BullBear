# runner.py
from massive import WebSocketClient
from massive.websocket.models import Feed, Market
from service import MinuteAggregateIngestionService
from configuration import settings


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

    client.subscribe("AM.AMD")

    client.run(service.handle_messages)


if __name__ == "__main__":
    main()
