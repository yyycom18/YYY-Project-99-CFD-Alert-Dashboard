"""
Condition 2: IMPULSE BREAK
Returns {"long": bool, "short": bool}.
Long = break above prior structure. Short = break below.
"""

from typing import Any, Dict

import pandas as pd

from .. import config as default_config
from ..structural import (
    body_size,
    swing_highs,
    swing_lows,
    wick_small_relative_to_body,
)


def impulse_break(df: pd.DataFrame, config: Any = None) -> Dict[str, bool]:
    out = {"long": False, "short": False}
    if df.empty or len(df) < 15:
        return out
    cfg = config or default_config
    n_candles = getattr(cfg, "IMPULSE_CANDLES_COUNT", 3)
    body_ratio = getattr(cfg, "IMPULSE_BODY_RATIO", 1.5)
    extreme_ratio = getattr(cfg, "IMPULSE_EXTREME_RATIO", 2.0)
    wick_ratio = getattr(cfg, "WICK_TO_BODY_MAX", 0.5)
    left = getattr(cfg, "SWING_LEFT", 2)
    right = getattr(cfg, "SWING_RIGHT", 2)

    body = body_size(df["open"], df["close"])
    avg_body = body.rolling(10, min_periods=3).mean()
    tail = df.tail(n_candles)
    body_tail = body.tail(n_candles)
    avg_tail = avg_body.tail(n_candles)

    large = (body_tail.values >= (avg_tail.values * body_ratio)).all()
    small_wicks = all(
        wick_small_relative_to_body(tail.iloc[i], wick_ratio)
        for i in range(len(tail))
    )
    three_ok = large and small_wicks
    one_extreme = (body.tail(3) > avg_body.tail(3) * extreme_ratio).any()

    if not three_ok and not one_extreme:
        return out

    last_close = float(df["close"].iloc[-1])
    sh_idx = swing_highs(df, left, right)
    sl_idx = swing_lows(df, left, right)
    prior_highs = [df["high"].iloc[i] for i in sh_idx if i < len(df) - n_candles]
    prior_lows = [df["low"].iloc[i] for i in sl_idx if i < len(df) - n_candles]

    if prior_highs and last_close > max(prior_highs):
        out["long"] = True
    if prior_lows and last_close < min(prior_lows):
        out["short"] = True
    return out
