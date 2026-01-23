from decimal import Decimal
from datetime import datetime, timezone
from typing import Optional

from repo import MarketDataRepository


class FundNAVCalculationService:
    """
    Calculates Fund NAV (Net Asset Value) based on the weighted performance
    of the fund's underlying holdings.
    """

    def __init__(self):
        self.repo = MarketDataRepository()

    def calculate_and_update_all_funds(self):
        """
        Calculate NAV for all active funds and record history.
        """
        funds = self.repo.get_active_funds()

        for fund in funds:
            try:
                new_nav = self.calculate_fund_nav(fund['id'])
                if new_nav is not None:
                    self.repo.update_fund_nav(fund['id'], new_nav)
                    self.repo.record_nav_history(fund['id'], new_nav, fund.get('total_units', 0))
                    print(f"Updated NAV for fund {fund['name']}: {new_nav}")
            except Exception as e:
                print(f"Error calculating NAV for fund {fund['id']}: {e}")

    def calculate_fund_nav(self, fund_id: int) -> Optional[Decimal]:
        """
        Calculate the NAV per unit for a fund based on its holdings' current prices.
        """
        holdings = self.repo.get_fund_holdings(fund_id)

        if not holdings:
            return None

        total_nav = Decimal('0')
        total_weight = Decimal('0')

        for holding in holdings:
            instrument_id = holding['instrument_id']
            weight = Decimal(str(holding['weight_percent']))

            # Get latest price for this instrument
            latest_price = self.repo.get_latest_price(instrument_id)

            if latest_price is None:
                print(f"Warning: No price data for instrument {instrument_id}")
                continue

            # Get base price (price when fund was created or first recorded)
            base_price = self.repo.get_base_price(instrument_id, fund_id)

            if base_price is None or base_price == 0:
                base_price = latest_price  # Use current as base if no history

            # Calculate price change ratio
            price_ratio = latest_price / base_price

            # Add weighted contribution to NAV
            # Each holding contributes: (weight/100) * price_ratio
            total_nav += (weight / Decimal('100')) * price_ratio
            total_weight += weight

        if total_weight == 0:
            return None

        # Normalize if weights don't sum to 100
        if total_weight != Decimal('100'):
            total_nav = total_nav * (Decimal('100') / total_weight)

        return total_nav.quantize(Decimal('0.000001'))


def run_nav_calculation():
    """Entry point for running NAV calculation."""
    service = FundNAVCalculationService()
    service.calculate_and_update_all_funds()


if __name__ == "__main__":
    run_nav_calculation()

