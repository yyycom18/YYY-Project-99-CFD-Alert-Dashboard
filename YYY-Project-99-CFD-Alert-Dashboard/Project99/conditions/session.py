"""
Condition 7: SESSION (Behavioral trigger)
HKT: Asia 05–16, EU 15–24, US 20–05.
Returns {"long": bool, "short": bool}. Long = breakout up, short = breakout down.
"""

from typing import Any, Dict

import pandas as pd

from .. import config as default_config
from ..structural import body_size, dominant_direction


def _in_asia_hkt(h: int, start: int, end: int) -> bool:
    return start <= h < end


def _in_eu_hkt(h: int, start: int, end: int) -> bool:
    if start <= end:
        return start <= h < end
    return h >= start or h < end


def _in_us_hkt(h: int, start: int, end: int) -> bool:
    if start > end:
        return h >= start or h < end
    return start <= h < end


def session(df: pd.DataFrame, config: Any = None) -> Dict[str, bool]:
    out = {"long": False, "short": False}
    if df.empty or len(df) < 24:
        return out
    if not isinstance(df.index, pd.DatetimeIndex):
        return out
    cfg = config or default_config
    asia_start = getattr(cfg, "SESSION_ASIA_START_HKT", 5)
    asia_end = getattr(cfg, "SESSION_ASIA_END_HKT", 16)
    eu_start = getattr(cfg, "SESSION_EU_START_HKT", 15)
    eu_end = getattr(cfg, "SESSION_EU_END_HKT", 24)
    us_start = getattr(cfg, "SESSION_US_START_HKT", 20)
    us_end = getattr(cfg, "SESSION_US_END_HKT", 5)

    hours = pd.Series(
        [getattr(ts, "hour", pd.Timestamp(ts).hour) for ts in df.index],
        index=df.index,
    )
    last_hour = hours.iloc[-1]
    in_eu = _in_eu_hkt(last_hour, eu_start, eu_end)
    in_us = _in_us_hkt(last_hour, us_start, us_end)
    if not in_eu and not in_us:
        return out

    asia_mask = hours.apply(lambda h: _in_asia_hkt(h, asia_start, asia_end))
    if not asia_mask.any():
        return out
    asia_high = df.loc[asia_mask, "high"].max()
    asia_low = df.loc[asia_mask, "low"].min()
    if pd.isna(asia_high) or pd.isna(asia_low):
        return out
    asia_range = asia_high - asia_low
    if asia_range <= 0:
        return out

    direction = dominant_direction(df, lookback=min(30, len(df) - 1))
    if direction is None:
        return out

    last_close = float(df["close"].iloc[-1])
    breakout_up = last_close > asia_high
    breakout_down = last_close < asia_low

    body = body_size(df["open"], df["close"])
    recent_body = body.tail(5).sum()
    avg_body = body.rolling(20).mean().iloc[-6:-1].sum()
    strong_opposite = False
    if direction == "up" and breakout_down and recent_body > avg_body * 1.2:
        strong_opposite = True
    if direction == "down" and breakout_up and recent_body > avg_body * 1.2:
        strong_opposite = True
    if strong_opposite:
        return out

    out["long"] = breakout_up
    out["short"] = breakout_down
    return out
