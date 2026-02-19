"""
Condition 6: FIBONACCI
R:R >= 1.3 enforced inside this condition for 0.5 level.
Returns {"long": bool, "short": bool}.
Long = at retrace from low (pullback up). Short = at retrace from high (pullback down).
"""

from typing import Any, Dict

import pandas as pd

from .. import config as default_config
from ..structural import body_size
from ..utils import compute_rr_ratio


def _last_impulse_range(df: pd.DataFrame, body_ratio: float) -> tuple:
    body = body_size(df["open"], df["close"])
    avg = body.rolling(10, min_periods=3).mean()
    for i in range(len(df) - 1, max(len(df) - 25, 0), -1):
        if avg.iloc[i] > 0 and body.iloc[i] >= avg.iloc[i] * body_ratio:
            h = float(df["high"].iloc[i:].max())
            l = float(df["low"].iloc[i:].min())
            return (h, l)
    h = float(df["high"].tail(20).max())
    l = float(df["low"].tail(20).min())
    return (h, l)


def fib(df: pd.DataFrame, config: Any = None) -> Dict[str, bool]:
    out = {"long": False, "short": False}
    if df.empty or len(df) < 20:
        return out
    cfg = config or default_config
    fib_618 = getattr(cfg, "FIB_PRIMARY", 0.618)
    fib_50 = getattr(cfg, "FIB_SECONDARY", 0.5)
    fib_88 = getattr(cfg, "FIB_STOP_AT_88", 0.88)
    tol_pct = getattr(cfg, "FIB_TOLERANCE_PCT", 0.01)
    body_ratio = getattr(cfg, "IMPULSE_BODY_RATIO", 1.5)
    min_rr = getattr(cfg, "RR_MIN", 1.3)

    impulse_high, impulse_low = _last_impulse_range(df, body_ratio)
    span = impulse_high - impulse_low
    if span <= 0:
        return out
    current = float(df["close"].iloc[-1])
    tol = span * tol_pct

    # Pullback down from high → short setup (0.618 / 0.5 with 0.88 stop, R:R in condition)
    f618 = impulse_high - fib_618 * span
    f50 = impulse_high - fib_50 * span
    f88 = impulse_high - fib_88 * span
    at_618_s = abs(current - f618) <= tol
    at_50_s = abs(current - f50) <= tol
    rr_ok_50_s, _ = compute_rr_ratio(current, f88, impulse_high, min_rr)
    if at_618_s or (at_50_s and rr_ok_50_s):
        out["short"] = True

    # Pullback up from low → long setup
    f618_l = impulse_low + fib_618 * span
    f50_l = impulse_low + fib_50 * span
    f88_l = impulse_low + fib_88 * span
    at_618_l = abs(current - f618_l) <= tol
    at_50_l = abs(current - f50_l) <= tol
    rr_ok_50_l, _ = compute_rr_ratio(current, f88_l, impulse_low, min_rr)
    if at_618_l or (at_50_l and rr_ok_50_l):
        out["long"] = True

    return out
