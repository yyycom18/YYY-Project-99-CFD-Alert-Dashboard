"""
Condition 4: STOP MONEY (打錢) — v2.1 Liquidity doctrine
Forward liquidity target existence + space validation. Pre-deployment; no breakout required.
LONG: trend +1, double top ahead, distance <= ATR*mult, no blocking structure.
SHORT: trend -1, double bottom below, valid space, no blocking.
Returns {"long": bool, "short": bool}.
"""

from typing import Any, Dict, Optional, Tuple

import pandas as pd

from .. import config as default_config
from ..structural import atr, swing_highs, swing_lows, trend_state


def _double_top_ahead(
    df: pd.DataFrame, tolerance_pct: float, lookback: int
) -> Optional[Tuple[float, int]]:
    """(double_top_level, bar_index). Ahead = above current close. None if not found."""
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
        level = max(h1[1], h2[1])
        current = float(df["close"].iloc[-1])
        if level > current:
            return (level, h2[0])
    return None


def _double_bottom_below(
    df: pd.DataFrame, tolerance_pct: float, lookback: int
) -> Optional[Tuple[float, int]]:
    """(double_bottom_level, bar_index). Below = below current close."""
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
        level = min(l1[1], l2[1])
        current = float(df["close"].iloc[-1])
        if level < current:
            return (level, l2[0])
    return None


def _blocking_swing_high_above(df: pd.DataFrame, target_price: float, lookback: int) -> bool:
    """True if any swing high in lookback is above target (blocking path to target)."""
    idx = swing_highs(df, 2, 2)
    in_range = [i for i in idx if i >= len(df) - lookback]
    for i in in_range:
        if float(df["high"].iloc[i]) > target_price:
            return True
    return False


def _blocking_swing_low_below(df: pd.DataFrame, target_price: float, lookback: int) -> bool:
    """True if any swing low in lookback is below target."""
    idx = swing_lows(df, 2, 2)
    in_range = [i for i in idx if i >= len(df) - lookback]
    for i in in_range:
        if float(df["low"].iloc[i]) < target_price:
            return True
    return False


def stop_money(df: pd.DataFrame, config: Any = None) -> Dict[str, bool]:
    out = {"long": False, "short": False}
    if df.empty or len(df) < 15:
        return out
    cfg = config or default_config
    lookback = getattr(cfg, "DOUBLE_LOOKBACK", 20)
    tol_pct = getattr(cfg, "DOUBLE_TOLERANCE_PCT", 0.005)
    atr_mult = getattr(cfg, "SPACE_DISTANCE_ATR_MULT", 2.0)
    atr_period = getattr(cfg, "ATR_PERIOD", 20)

    state = trend_state(df, lookback=min(lookback, len(df) - 1))
    if state is None:
        return out

    atr_val = atr(df, atr_period)
    if atr_val is None or atr_val <= 0:
        return out
    max_distance = atr_val * atr_mult
    current = float(df["close"].iloc[-1])

    # LONG: trend_state == +1, double top ahead, distance > 0 and <= ATR*mult, no blocking
    if state == 1:
        target = _double_top_ahead(df, tol_pct, lookback)
        if target is None:
            return out
        level, _ = target
        distance = level - current
        if distance <= 0:
            return out
        if distance > max_distance:
            return out
        if _blocking_swing_high_above(df, level, lookback):
            return out
        out["long"] = True
        return out

    # SHORT: trend_state == -1, double bottom below, valid space, no blocking
    if state == -1:
        target = _double_bottom_below(df, tol_pct, lookback)
        if target is None:
            return out
        level, _ = target
        distance = current - level
        if distance <= 0:
            return out
        if distance > max_distance:
            return out
        if _blocking_swing_low_below(df, level, lookback):
            return out
        out["short"] = True
    return out
