import requests
from configuration import settings


class DjangoOrdersClient:
    def __init__(self):
        self.base = settings.DJANGO_API_BASE_URL.rstrip("/")
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Token {settings.DJANGO_SERVICE_TOKEN}",
            "Content-Type": "application/json",
        })

    def get_open_orders(self) -> list[dict]:
        url = f"{self.base}/api/orders/orders/open/"
        r = self.session.get(url, timeout=10)
        r.raise_for_status()
        return r.json()

    def execute_order(self, order_id: int) -> bool:
        url = f"{self.base}/api/orders/orders/{order_id}/execute/"
        r = self.session.post(url, json={}, timeout=10)

        # 200 => executed
        if r.status_code == 200:
            return True

        # 409 => not executable now
        if r.status_code == 409:
            return False

        # others => error
        print("[EXECUTE ERROR]", r.status_code, r.text)
        return False
