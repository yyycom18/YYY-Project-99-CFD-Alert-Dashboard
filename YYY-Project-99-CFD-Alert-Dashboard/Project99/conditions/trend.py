"""
Condition 1: TREND
Structural only. Returns {"long": bool, "short": bool}.
Long = uptrend intact (retrace <= 0.618). Short = downtrend intact.
"""

from typing import Any, Dict

import pandas as pd

from .. import config as default_config
from ..structural import (
    dominant_direction,
    recent_swing_high,
    recent_swing_low,
    retracement_depth,
)


def trend(df: pd.DataFrame, config: Any = None) -> Dict[str, bool]:
    out = {"long": False, "short": False}
    if df.empty or len(df) < 20:
        return out
    cfg = config or default_config
    lookback = getattr(cfg, "SWING_LOOKBACK", 5) * 3
    left = getattr(cfg, "SWING_LEFT", 2)
    right = getattr(cfg, "SWING_RIGHT", 2)
    max_trend = getattr(cfg, "RETRACE_MAX_TREND", 0.618)
    range_lim = getattr(cfg, "RETRACE_RANGE", 0.7)

    direction = dominant_direction(df, lookback=min(lookback, len(df) - 1))
    if direction is None:
        return out

    sh = recent_swing_high(df, lookback, left, right)
    sl = recent_swing_low(df, lookback, left, right)
    if sh is None or sl is None:
        return out
    current = float(df["close"].iloc[-1])
    span = sh - sl
    if span <= 0:
        return out

    if direction == "up":
        depth = retracement_depth(sh, sl, current, "up")
    else:
        depth = retracement_depth(sh, sl, current, "down")

    if depth is None or depth > range_lim:
        return out
    if depth <= max_trend:
        out["long"] = direction == "up"
        out["short"] = direction == "down"
    return out
