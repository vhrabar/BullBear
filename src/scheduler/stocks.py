
# List of stock ticker symbols for subscription
STOCKS = [
    "AMD", # Advanced Micro Devices
    "NVDA", # NVIDIA Corporation
    "ASML", # ASML Holding N.V.
    "TSM", # Taiwan Semiconductor Manufacturing Company Limited
    "INTC", # Intel Corporation
    "SFTBY", # SoftBank Group Corp.
    "ARM", # Arm Holdings plc
    "TXN", # Texas Instruments Incorporated
    "DTE", # Deutsche Telekom AG
    "RHM", # Rheinmetall AG
    "VOW", # Volkswagen AG

    "AAPL", # Apple Inc.
    "MSFT", # Microsoft Corporation
    "AMZN", # Amazon.com, Inc.
    "GOOGL", # Alphabet Inc. (Class A)
    "AVGO", # Broadcom Inc.
    "GOOG", # Alphabet Inc. (Class C)
    "META", # Meta Platforms, Inc.
    "TSLA", # Tesla, Inc.
    "BRK.B", # Berkshire Hathaway Inc. (Class B)
    "WMT", # Walmart Inc.
    "LLY", # Eli Lilly and Company
    "JPM", # JPMorgan Chase & Co.
    "V", # Visa Inc.
    "ORCL", # Oracle Corporation
    "XOM", # Exxon Mobil Corporation
    "NFLX", # Netflix, Inc.
    "BAC", # Bank of America Corporation
    "IBM", # International Business Machines Corporation
    "MS", # Morgan Stanley
    "GS", # The Goldman Sachs Group, Inc.
    "DIS", # The Walt Disney Company
    "QCOM", # QUALCOMM Incorporated
    "SCHW", # The Charles Schwab Corporation
    "BLK", # BlackRock, Inc.
    "DELL", # Dell Technologies Inc.
    "ADSK", # Autodesk, Inc.

    "SPY", # SPDR S&P 500 ETF Trust
]

def get_subscribed_stocks() -> list[str]:
    return [f"AM.{s.upper()}" for s in STOCKS]
