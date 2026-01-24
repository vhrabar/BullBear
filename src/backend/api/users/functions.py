from math import sqrt

def _safe_float(x: float) -> float:
    """
    Convert x to float, return 0.0 on failure.
    """
    try:
        return float(x)
    except Exception:
        return 0.0


def _pct(a: float, b: float) -> float:
    """
    Safe percentage change from a to b.
    """
    if a == 0:
        return 0.0
    return (b - a) / a


def _std(values: list[float]) -> float:
    """
    Sample standard deviation of a list of numbers.
    """
    n = len(values)
    if n < 2:
        return 0.0
    mean = sum(values) / n
    var = sum((v - mean) ** 2 for v in values) / (n - 1)
    return sqrt(var)


def _max_drawdown(values: list[float]) -> float:
    """
    returns max drawdown as negative fraction
    """
    if not values:
        return 0.0

    peak = values[0]
    max_dd = 0.0
    for v in values:
        if v > peak:
            peak = v
        dd = (v - peak) / peak if peak > 0 else 0.0
        if dd < max_dd:
            max_dd = dd
    return max_dd


def _var_cvar(returns: list[float] , alpha: float=0.95) -> tuple[float, float]:
    """
    Historical VaR/CVaR
    5% 1-alpha quantile
    """
    if not returns:
        return 0.0, 0.0

    rs = sorted(returns)
    q = int((1.0 - alpha) * len(rs))
    q = max(0, min(q, len(rs) - 1))
    var = rs[q]

    tail = rs[: q + 1]
    cvar = sum(tail) / len(tail) if tail else var
    return var, cvar
