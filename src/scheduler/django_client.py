import requests
from decimal import Decimal
from configuration import settings


class DjangoOrdersClient:
    def __init__(self):
        self.base = settings.DJANGO_API_BASE_URL.rstrip("/")
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
        })

    def get_open_orders(self) -> list[dict]:
        url = f"{self.base}/api/orders/orders/open/"
        r = self.session.get(url, timeout=10)
        r.raise_for_status()
        return r.json()

    def buy(self, portfolio_id: int, instrument_symbol: str, quantity: Decimal, price: Decimal) -> bool:
        """Call /api/trading/buy endpoint"""
        url = f"{self.base}/api/trading/buy"
        payload = {
            "portfolio_id": portfolio_id,
            "instrument_symbol": instrument_symbol,
            "quantity": f"{quantity:.4f}",
            "price": f"{price:.6f}",
        }
        print(f"[DEBUG] POST {url} payload={payload}")
        r = self.session.post(url, json=payload, timeout=10)

        if r.status_code == 200:
            print(f"[DEBUG] BUY success: {r.json()}")
            return True

        print(f"[BUY ERROR] {r.status_code}: {r.text[:500]}")
        return False

    def sell(self, portfolio_id: int, instrument_symbol: str, quantity: Decimal, price: Decimal) -> bool:
        """Call /api/trading/sell endpoint"""
        url = f"{self.base}/api/trading/sell"
        payload = {
            "portfolio_id": portfolio_id,
            "instrument_symbol": instrument_symbol,
            "quantity": f"{quantity:.4f}",
            "price": f"{price:.6f}",
        }
        print(f"[DEBUG] POST {url} payload={payload}")
        r = self.session.post(url, json=payload, timeout=10)

        if r.status_code == 200:
            return True

        print(f"[SELL ERROR] {r.status_code}: {r.text[:500]}")
        return False
