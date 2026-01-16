import time
from configuration import settings
from execution_service import OrderExecutionService


def main():
    print("Starting execution engine...")
    engine = OrderExecutionService()

    while True:
        try:
            results = engine.run_once()
            if results:
                print("FILLED:", results)
        except Exception as e:
            print("[ERROR] execution engine crashed:", e)

        time.sleep(2)


if __name__ == "__main__":
    main()
