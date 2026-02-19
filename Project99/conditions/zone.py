"""
Condition 5: SUPPLY / DEMAND ZONE (禁區)
Returns {"long": bool, "short": bool}.
Long = demand zone (up impulse) revisit. Short = supply zone (down impulse) revisit.
"""

from typing import Any, Dict, Optional, Tuple

import pandas as pd

from .. import config as default_config
from ..structural import body_size, wick_small_relative_to_body


def _find_impulse_origin(
    df: pd.DataFrame,
    body_ratio: float,
    wick_ratio: float,
    lookback: int,
) -> Optional[Tuple[int, float, float, str]]:
    """(index, zone_high, zone_low, 'up'|'down')."""
    body = body_size(df["open"], df["close"])
    avg = body.rolling(10, min_periods=3).mean()
    for i in range(len(df) - 1, max(len(df) - lookback, 0), -1):
        if avg.iloc[i] <= 0:
            continue
        if body.iloc[i] < avg.iloc[i] * body_ratio:
            continue
        row = df.iloc[i]
        if not wick_small_relative_to_body(row, wick_ratio):
            continue
        if df["close"].iloc[i] > df["open"].iloc[i]:
            return (i, float(df["high"].iloc[i]), float(df["low"].iloc[i]), "up")
        else:
            return (i, float(df["high"].iloc[i]), float(df["low"].iloc[i]), "down")
    return None


def zone(df: pd.DataFrame, config: Any = None) -> Dict[str, bool]:
    out = {"long": False, "short": False}
    if df.empty or len(df) < 10:
        return out
    cfg = config or default_config
    body_ratio = getattr(cfg, "ZONE_IMPULSE_BODY_RATIO", 1.2)
    wick_ratio = getattr(cfg, "ZONE_WICK_TO_BODY_MAX", 0.5)
    revisit_pct = getattr(cfg, "ZONE_REVISIT_TOLERANCE_PCT", 0.01)
    lookback = min(30, len(df) - 2)

    found = _find_impulse_origin(df, body_ratio, wick_ratio, lookback)
    if found is None or found[0] >= len(df) - 1:
        return out
    idx, z_high, z_low, direction = found
    span = z_high - z_low
    tol = span * revisit_pct if span > 0 else 0
    current = float(df["close"].iloc[-1])
    if not (z_low - tol <= current <= z_high + tol):
        return out
    out["long"] = direction == "up"
    out["short"] = direction == "down"
    return out
