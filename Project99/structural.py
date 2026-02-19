"""
Project99 — Structural helpers only.
Swing high/low, retracement depth. No EMA, no generic indicators.
"""

from typing import List, Optional, Tuple

import pandas as pd


def swing_highs(
    df: pd.DataFrame,
    left: int = 2,
    right: int = 2,
) -> List[int]:
    """Indices where high is >= left and >= right neighbors."""
    if len(df) < left + right + 1:
        return []
    idx = []
    for i in range(left, len(df) - right):
        h = df["high"].iloc[i]
        if all(df["high"].iloc[i - j] <= h for j in range(1, left + 1)) and all(
            df["high"].iloc[i + j] <= h for j in range(1, right + 1)
        ):
            idx.append(i)
    return idx


def swing_lows(
    df: pd.DataFrame,
    left: int = 2,
    right: int = 2,
) -> List[int]:
    """Indices where low is <= left and <= right neighbors."""
    if len(df) < left + right + 1:
        return []
    idx = []
    for i in range(left, len(df) - right):
        l = df["low"].iloc[i]
        if all(df["low"].iloc[i - j] >= l for j in range(1, left + 1)) and all(
            df["low"].iloc[i + j] >= l for j in range(1, right + 1)
        ):
            idx.append(i)
    return idx


def recent_swing_high(df: pd.DataFrame, lookback: int, left: int = 2, right: int = 2) -> Optional[float]:
    """Latest swing high in last lookback bars."""
    idx = swing_highs(df, left, right)
    in_range = [i for i in idx if i >= len(df) - lookback]
    if not in_range:
        return None
    i = max(in_range)
    return float(df["high"].iloc[i])


def recent_swing_low(df: pd.DataFrame, lookback: int, left: int = 2, right: int = 2) -> Optional[float]:
    """Latest swing low in last lookback bars."""
    idx = swing_lows(df, left, right)
    in_range = [i for i in idx if i >= len(df) - lookback]
    if not in_range:
        return None
    i = max(in_range)
    return float(df["low"].iloc[i])


def retracement_depth(
    leg_high: float,
    leg_low: float,
    current_price: float,
    direction: str,
) -> Optional[float]:
    """
    Retracement depth 0..1 from the leg.
    direction 'up': leg was up (low -> high), we measure pullback from high.
    direction 'down': leg was down (high -> low), we measure pullback from low.
    """
    span = leg_high - leg_low
    if span <= 0:
        return None
    if direction == "up":
        # Pullback from high: depth = (high - price) / span
        return (leg_high - current_price) / span
    if direction == "down":
        # Pullback from low: depth = (price - low) / span
        return (current_price - leg_low) / span
    return None


def dominant_direction(df: pd.DataFrame, lookback: int = 30) -> Optional[str]:
    """
    Structural bias: compare recent swing high/low to prior.
    Returns 'up', 'down', or None (no clear structure).
    """
    idx_high = swing_highs(df, 2, 2)
    idx_low = swing_lows(df, 2, 2)
    if len(idx_high) < 2 or len(idx_low) < 2:
        return None
    recent_highs = [i for i in idx_high if i >= len(df) - lookback]
    recent_lows = [i for i in idx_low if i >= len(df) - lookback]
    if len(recent_highs) < 2 or len(recent_lows) < 2:
        return None
    h1, h2 = sorted(recent_highs)[-2], sorted(recent_highs)[-1]
    l1, l2 = sorted(recent_lows)[-2], sorted(recent_lows)[-1]
    if df["high"].iloc[h2] > df["high"].iloc[h1] and df["low"].iloc[l2] > df["low"].iloc[l1]:
        return "up"
    if df["high"].iloc[h2] < df["high"].iloc[h1] and df["low"].iloc[l2] < df["low"].iloc[l1]:
        return "down"
    return None


def trend_state(df: pd.DataFrame, lookback: int = 30) -> Optional[int]:
    """
    Returns +1 (uptrend), -1 (downtrend), or None.
    For v2.1 stop_hunt / stop_money liquidity doctrine.
    """
    d = dominant_direction(df, lookback)
    if d == "up":
        return 1
    if d == "down":
        return -1
    return None


def atr(df: pd.DataFrame, period: int = 20) -> Optional[float]:
    """
    Average True Range (structural volatility). Returns last value or None.
    True range = max(high-low, |high-prev_close|, |low-prev_close|).
    """
    if len(df) < period + 1:
        return None
    high = df["high"]
    low = df["low"]
    close = df["close"]
    prev_close = close.shift(1)
    tr = (high - low).combine((high - prev_close).abs(), max).combine((low - prev_close).abs(), max)
    atr_series = tr.rolling(period, min_periods=period).mean()
    return float(atr_series.iloc[-1])


def body_size(series_open: pd.Series, series_close: pd.Series) -> pd.Series:
    return (series_close - series_open).abs()


def wick_small_relative_to_body(
    row: pd.Series,
    body_ratio_max: float,
) -> bool:
    """One row: body large enough, wicks small vs body."""
    body = abs(row["close"] - row["open"])
    range_ = row["high"] - row["low"]
    wick = range_ - body if range_ >= body else 0
    if body <= 0:
        return False
    return wick <= body * body_ratio_max
