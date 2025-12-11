
# List of stock ticker symbols for subscription (US market only)
STOCKS = [
    "AMD", # Advanced Micro Devices
    "NVDA", # NVIDIA Corporation
    "ASML", # ASML Holding N.V.
    "INTC", # Intel Corporation
    "SFTBY", # SoftBank Group Corp.
    "ARM", # Arm Holdings plc
    "TXN", # Texas Instruments Incorporated
]

def get_subscribed_stocks() -> list[str]:
    return [f"AM.{s.upper()}" for s in STOCKS]
