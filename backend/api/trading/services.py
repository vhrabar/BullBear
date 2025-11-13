from decimal import Decimal
from typing import Optional
from django.core.exceptions import ValidationError
from .models import PortfolioHolding, Instrument
from api.users.models import UserPortfolio as Portfolio
from django.db.models import QuerySet


def buy_instrument(portfolio: Portfolio, instrument_symbol: str, quantity: Decimal, price: Optional[Decimal] = None):
    """
    Buys a given quantity of an instrument for the given portfolio.
    Updates or creates PortfolioHolding and recalculates average price.
    """
    instrument = Instrument.objects.get(symbol=instrument_symbol)
    quantity = Decimal(quantity)

    # Use latest close price if price not provided
    if price is None:
        latest_data = instrument.interval_data.order_by("-start_time").first()  # type: ignore
        if not latest_data:
            raise ValidationError("No market data available for this instrument.")
        price = latest_data.close_price
    assert price is not None
    price = Decimal(price)

    holding, created = PortfolioHolding.objects.get_or_create(
        portfolio=portfolio,
        instrument=instrument,
        defaults={'quantity': 0, 'average_price': 0}
    )

    # update portofolio balance
    total_purchase_cost = quantity * price
    if portfolio.balance < total_purchase_cost:
        raise ValidationError("Insufficient balance in portfolio to complete purchase.")
    portfolio.balance -= total_purchase_cost
    portfolio.save()


    # Weighted average price calculation
    total_cost = holding.quantity * holding.average_price + quantity * price
    holding.quantity += quantity
    holding.average_price = total_cost / holding.quantity
    holding.save()

    return holding


def sell_instrument(portfolio: Portfolio, instrument_symbol: str, quantity: Decimal, price: Optional[Decimal] = None):
    """
    Sells a given quantity of an instrument from the portfolio.
    Updates PortfolioHolding quantity.
    """
    instrument = Instrument.objects.get(symbol=instrument_symbol)
    quantity = Decimal(quantity)

    try:
        holding = PortfolioHolding.objects.get(portfolio=portfolio, instrument=instrument)
    except PortfolioHolding.DoesNotExist:
        raise ValidationError("Cannot sell an instrument that is not in the portfolio.")

    if holding.quantity < quantity:
        raise ValidationError("Not enough holdings to sell.")

    # Update portfolio balance
    total_sale_revenue = quantity * price
    portfolio.balance += total_sale_revenue

    # Use latest close price if price not provided
    if price is None:
        latest_data = instrument.interval_data.order_by("-start_time").first()  # type: ignore
        if not latest_data:
            raise ValidationError("No market data available for this instrument.")
        price = latest_data.close_price

    holding.quantity -= quantity
    holding.save()

    return holding
