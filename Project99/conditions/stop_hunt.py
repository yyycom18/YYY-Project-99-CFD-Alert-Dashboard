"""
Condition 3: STOP HUNT (打止蝕) — v2.1 Liquidity doctrine
Liquidity cluster inside retracement zone. Pre-deployment; no sweep/break required.
LONG: trend +1, retracement 0.5–0.7, double bottom cluster, price in zone.
SHORT: trend -1, retracement 0.5–0.7, double top cluster, price in zone.
Returns {"long": bool, "short": bool}.
"""

from typing import Any, Dict, Optional, Tuple

import pandas as pd

from .. import config as default_config
from ..structural import (
    recent_swing_high,
    recent_swing_low,
    retracement_depth,
    swing_highs,
    swing_lows,
    trend_state,
)


def _double_bottom_cluster(
    df: pd.DataFrame, tolerance_pct: float, lookback: int
) -> Optional[Tuple[float, float]]:
    """(cluster_level, span_for_tol). Cluster level = min of two lows. None if no cluster."""
    idx = swing_lows(df, 2, 2)
    in_range = [i for i in idx if i >= len(df) - lookback]
    if len(in_range) < 2:
        return None
    lows = [(i, float(df["low"].iloc[i])) for i in in_range]
    lows.sort(key=lambda x: x[0])
    l1, l2 = lows[-2], lows[-1]
    span = float(df["low"].max() - df["low"].min()) or 1.0
    tol = span * tolerance_pct
    if abs(l1[1] - l2[1]) <= tol:
        return (min(l1[1], l2[1]), span)
    return None


def _double_top_cluster(
    df: pd.DataFrame, tolerance_pct: float, lookback: int
) -> Optional[Tuple[float, float]]:
    """(cluster_level, span_for_tol). None if no cluster."""
    idx = swing_highs(df, 2, 2)
    in_range = [i for i in idx if i >= len(df) - lookback]
    if len(in_range) < 2:
        return None
    highs = [(i, float(df["high"].iloc[i])) for i in in_range]
    highs.sort(key=lambda x: x[0])
    h1, h2 = highs[-2], highs[-1]
    span = float(df["high"].max() - df["high"].min()) or 1.0
    tol = span * tolerance_pct
    if abs(h1[1] - h2[1]) <= tol:
        return (max(h1[1], h2[1]), span)
    return None


def stop_hunt(df: pd.DataFrame, config: Any = None) -> Dict[str, bool]:
    out = {"long": False, "short": False}
    if df.empty or len(df) < 15:
        return out
    cfg = config or default_config
    lookback = getattr(cfg, "DOUBLE_LOOKBACK", 20)
    tol_pct = getattr(cfg, "DOUBLE_TOLERANCE_PCT", 0.005)
    ret_min = getattr(cfg, "RETRACE_MIN_STOP_HUNT", 0.5)
    ret_max = getattr(cfg, "RETRACE_MAX_STOP_HUNT", 0.7)
    left = getattr(cfg, "SWING_LEFT", 2)
    right = getattr(cfg, "SWING_RIGHT", 2)

    state = trend_state(df, lookback=min(lookback, len(df) - 1))
    if state is None:
        return out

    sh = recent_swing_high(df, lookback, left, right)
    sl = recent_swing_low(df, lookback, left, right)
    if sh is None or sl is None:
        return out
    span = sh - sl
    if span <= 0:
        return out
    current = float(df["close"].iloc[-1])

    # LONG: trend_state == +1, retracement 0.5–0.7, double bottom cluster, price in zone
    if state == 1:
        depth = retracement_depth(sh, sl, current, "up")
        if depth is None or not (ret_min <= depth <= ret_max):
            return out
        cluster = _double_bottom_cluster(df, tol_pct, lookback)
        if cluster is None:
            return out
        zone_low = sh - ret_max * span
        zone_high = sh - ret_min * span
        if zone_low <= current <= zone_high:
            out["long"] = True
        return out

    # SHORT: trend_state == -1, retracement 0.5–0.7, double top cluster, price in zone
    if state == -1:
        depth = retracement_depth(sh, sl, current, "down")
        if depth is None or not (ret_min <= depth <= ret_max):
            return out
        cluster = _double_top_cluster(df, tol_pct, lookback)
        if cluster is None:
            return out
        zone_low = sl + ret_min * span
        zone_high = sl + ret_max * span
        if zone_low <= current <= zone_high:
            out["short"] = True
    return out
