"""
Gather overlay coordinates for rendering. Uses structural helpers only; no scoring.
Returns dict keyed by timeframe and overlay type for the viz layer to draw.
"""

from typing import Any, Dict, List, Optional, Tuple

import pandas as pd

from .. import config as default_config
from ..structural import (
    body_size,
    recent_swing_high,
    recent_swing_low,
    swing_highs,
    swing_lows,
    trend_state,
    wick_small_relative_to_body,
)


def _normalize(df: pd.DataFrame) -> pd.DataFrame:
    m = {c: c.lower() for c in df.columns if c.lower() in ("open", "high", "low", "close")}
    return df.rename(columns=m) if m else df


def _swing_points(df: pd.DataFrame, left: int = 2, right: int = 2) -> Tuple[List[Tuple[Any, float]], List[Tuple[Any, float]]]:
    """(times, high), (times, low) for swing high/low. Uses index for x."""
    df = _normalize(df)
    sh_idx = swing_highs(df, left, right)
    sl_idx = swing_lows(df, left, right)
    idx = df.index
    highs = [(idx[i], float(df["high"].iloc[i])) for i in sh_idx]
    lows = [(idx[i], float(df["low"].iloc[i])) for i in sl_idx]
    return highs, lows


def _top_n_levels(highs: List[Tuple[Any, float]], lows: List[Tuple[Any, float]], n: int = 2
) -> Tuple[List[float], List[float]]:
    """Top n swing high levels and top n swing low levels (by price)."""
    h_vals = sorted([p for _, p in highs], reverse=True)[:n]
    l_vals = sorted([p for _, p in lows])[:n]
    return h_vals, l_vals


def _impulse_bars(df: pd.DataFrame, body_ratio: float = 1.5, extreme_ratio: float = 2.0,
                  wick_ratio: float = 0.5, n: int = 3) -> List[int]:
    """Indices of last n bars that are impulse (large body, small wick). Returns at most n."""
    df = _normalize(df)
    if len(df) < 10:
        return []
    body = body_size(df["open"], df["close"])
    avg = body.rolling(10, min_periods=3).mean()
    out = []
    for i in range(len(df) - 1, max(len(df) - 15, 0), -1):
        if len(out) >= n:
            break
        if avg.iloc[i] <= 0:
            continue
        if body.iloc[i] >= avg.iloc[i] * extreme_ratio:
            out.append(i)
            continue
        if body.iloc[i] >= avg.iloc[i] * body_ratio and wick_small_relative_to_body(df.iloc[i], wick_ratio):
            out.append(i)
    return out


def _double_bottom_cluster(df: pd.DataFrame, lookback: int, tol_pct: float
) -> Optional[Tuple[float, float, float]]:
    """(level, zone_low, zone_high) retracement zone for long. None if not found."""
    idx = swing_lows(df, 2, 2)
    in_r = [i for i in idx if i >= len(df) - lookback]
    if len(in_r) < 2:
        return None
    lows = [(i, float(df["low"].iloc[i])) for i in in_r]
    lows.sort(key=lambda x: x[0])
    l1, l2 = lows[-2], lows[-1]
    span = float(df["low"].max() - df["low"].min()) or 1.0
    if abs(l1[1] - l2[1]) > span * tol_pct:
        return None
    sh = recent_swing_high(df, lookback, 2, 2)
    sl = recent_swing_low(df, lookback, 2, 2)
    if sh is None or sl is None or sh <= sl:
        return None
    span_leg = sh - sl
    zone_high = sh - 0.5 * span_leg
    zone_low = sh - 0.7 * span_leg
    return (min(l1[1], l2[1]), zone_low, zone_high)


def _double_top_cluster(df: pd.DataFrame, lookback: int, tol_pct: float
) -> Optional[Tuple[float, float, float]]:
    """(level, zone_low, zone_high) for short retracement zone."""
    idx = swing_highs(df, 2, 2)
    in_r = [i for i in idx if i >= len(df) - lookback]
    if len(in_r) < 2:
        return None
    highs = [(i, float(df["high"].iloc[i])) for i in in_r]
    highs.sort(key=lambda x: x[0])
    h1, h2 = highs[-2], highs[-1]
    span = float(df["high"].max() - df["high"].min()) or 1.0
    if abs(h1[1] - h2[1]) > span * tol_pct:
        return None
    sl = recent_swing_low(df, lookback, 2, 2)
    sh = recent_swing_high(df, lookback, 2, 2)
    if sh is None or sl is None or sh <= sl:
        return None
    span_leg = sh - sl
    zone_low = sl + 0.5 * span_leg
    zone_high = sl + 0.7 * span_leg
    return (max(h1[1], h2[1]), zone_low, zone_high)


def _stop_money_target(df: pd.DataFrame, lookback: int, tol_pct: float
) -> Optional[Tuple[str, float]]:
    """('long', level) or ('short', level) or None. One target only."""
    cfg = default_config
    state = trend_state(df, lookback)
    if state == 1:
        # double top ahead
        idx = swing_highs(df, 2, 2)
        in_r = [i for i in idx if i >= len(df) - lookback]
        if len(in_r) < 2:
            return None
        highs = [(i, float(df["high"].iloc[i])) for i in in_r]
        highs.sort(key=lambda x: x[0])
        h1, h2 = highs[-2], highs[-1]
        span = float(df["high"].max() - df["high"].min()) or 1.0
        if abs(h1[1] - h2[1]) <= span * tol_pct:
            level = max(h1[1], h2[1])
            if level > float(df["close"].iloc[-1]):
                return ("long", level)
    if state == -1:
        idx = swing_lows(df, 2, 2)
        in_r = [i for i in idx if i >= len(df) - lookback]
        if len(in_r) < 2:
            return None
        lows = [(i, float(df["low"].iloc[i])) for i in in_r]
        lows.sort(key=lambda x: x[0])
        l1, l2 = lows[-2], lows[-1]
        span = float(df["low"].max() - df["low"].min()) or 1.0
        if abs(l1[1] - l2[1]) <= span * tol_pct:
            level = min(l1[1], l2[1])
            if level < float(df["close"].iloc[-1]):
                return ("short", level)
    return None


def _one_zone(df: pd.DataFrame, lookback: int = 30) -> Optional[Tuple[str, float, float, Any, Any]]:
    """('demand'|'supply', high, low, start_time, end_time). One zone per TF."""
    df = _normalize(df)
    body = body_size(df["open"], df["close"])
    avg = body.rolling(10, min_periods=3).mean()
    body_ratio = getattr(default_config, "ZONE_IMPULSE_BODY_RATIO", 1.2)
    wick_ratio = getattr(default_config, "ZONE_WICK_TO_BODY_MAX", 0.5)
    for i in range(len(df) - 1, max(len(df) - lookback, 0), -1):
        if avg.iloc[i] <= 0 or body.iloc[i] < avg.iloc[i] * body_ratio:
            continue
        if not wick_small_relative_to_body(df.iloc[i], wick_ratio):
            continue
        h, l = float(df["high"].iloc[i]), float(df["low"].iloc[i])
        t0, t1 = df.index[i], df.index[-1]
        if df["close"].iloc[i] > df["open"].iloc[i]:
            return ("demand", h, l, t0, t1)
        return ("supply", h, l, t0, t1)
    return None


def _fib_levels(df: pd.DataFrame, body_ratio: float = 1.5) -> Optional[Tuple[float, float, float, float, float]]:
    """(impulse_high, impulse_low, f50, f618, f88). From high for down retrace."""
    df = _normalize(df)
    body = body_size(df["open"], df["close"])
    avg = body.rolling(10, min_periods=3).mean()
    for i in range(len(df) - 1, max(len(df) - 25, 0), -1):
        if avg.iloc[i] > 0 and body.iloc[i] >= avg.iloc[i] * body_ratio:
            ih = float(df["high"].iloc[i:].max())
            il = float(df["low"].iloc[i:].min())
            span = ih - il
            if span <= 0:
                return None
            return (ih, il, ih - 0.5 * span, ih - 0.618 * span, ih - 0.88 * span)
    ih = float(df["high"].tail(20).max())
    il = float(df["low"].tail(20).min())
    span = ih - il
    if span <= 0:
        return None
    return (ih, il, ih - 0.5 * span, ih - 0.618 * span, ih - 0.88 * span)


def get_visualization_data(
    df_15m: pd.DataFrame,
    df_1h: Optional[pd.DataFrame],
    df_4h: Optional[pd.DataFrame],
    result: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Build overlay data for 4H, 1H, 15M. Does not modify or recompute score.
    result is optional (for session breakout / condition-driven highlights).
    """
    cfg = default_config
    lookback = getattr(cfg, "DOUBLE_LOOKBACK", 20)
    tol_pct = getattr(cfg, "DOUBLE_TOLERANCE_PCT", 0.005)
    left, right = getattr(cfg, "SWING_LEFT", 2), getattr(cfg, "SWING_RIGHT", 2)

    out = {"4h": {}, "1h": {}, "15m": {}}

    for label, df in [("4h", df_4h), ("1h", df_1h), ("15m", df_15m)]:
        if df is None or len(df) < 5:
            continue
        df = _normalize(df)
        lb = min(lookback, len(df) - 1)

        highs, lows = _swing_points(df, left, right)
        out[label]["swing_highs"] = highs
        out[label]["swing_lows"] = lows
        h_vals, l_vals = _top_n_levels(highs, lows, n=2)
        out[label]["blocking_highs"] = h_vals
        out[label]["blocking_lows"] = l_vals

        zone = _one_zone(df, lookback=min(30, len(df) - 1))
        out[label]["zone"] = zone

        if label == "1h":
            out[label]["impulse_bars"] = _impulse_bars(df, body_ratio=1.5, extreme_ratio=2.0, wick_ratio=0.5, n=3)
            out[label]["stop_hunt_double_bottom"] = _double_bottom_cluster(df, lb, tol_pct)
            out[label]["stop_hunt_double_top"] = _double_top_cluster(df, lb, tol_pct)
            out[label]["stop_money_target"] = _stop_money_target(df, lb, tol_pct)
            out[label]["session_breakout_long"] = result.get("long_conditions", {}).get("session", False) if result else False
            out[label]["session_breakout_short"] = result.get("short_conditions", {}).get("session", False) if result else False
        if label == "15m":
            out[label]["fib"] = _fib_levels(df, body_ratio=1.5)

    return out
