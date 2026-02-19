"""
Project99 — Scoring Engine (Phase 1 v2.0)
Structural + behavioral. Directional: long_score / short_score, alert_long / alert_short.
15m input → auto-resample to 1h and 4h. No EMA. R:R in Fib condition only.
"""

import logging
import pandas as pd
from typing import Any, Dict, Optional, Tuple

from . import config
from .conditions import CONDITION_NAMES, CONDITION_FUNCS

logger = logging.getLogger(__name__)

# Directional result type from each condition
DIRECTIONAL = Dict[str, bool]  # {"long": bool, "short": bool}


def _normalize_ohlc(df: pd.DataFrame) -> pd.DataFrame:
    mapping = {
        c: c.lower()
        for c in df.columns
        if c.lower() in ("open", "high", "low", "close")
    }
    if mapping:
        return df.rename(columns=mapping)
    return df


def _validate_ohlc(df: pd.DataFrame) -> Tuple[bool, str]:
    required = ["open", "high", "low", "close"]
    missing = set(required) - set(df.columns)
    if missing:
        return False, f"Missing columns: {missing}"
    for col in required:
        if not pd.api.types.is_numeric_dtype(df[col]):
            return False, f"Column '{col}' is not numeric"
    if (df["high"] < df["low"]).any():
        return False, "High < Low in some rows"
    if (df["high"] < df["open"]).any() or (df["high"] < df["close"]).any():
        return False, "High < Open or Close in some rows"
    if (df["low"] > df["open"]).any() or (df["low"] > df["close"]).any():
        return False, "Low > Open or Close in some rows"
    if df[required].isnull().any().any():
        return False, "NaN in OHLC"
    if (df[required] <= 0).any().any():
        return False, "Non-positive prices"
    return True, "OK"


def _resample_ohlc(df: pd.DataFrame, rule: str) -> pd.DataFrame:
    """Resample OHLC: open=first, high=max, low=min, close=last."""
    if not isinstance(df.index, pd.DatetimeIndex):
        return pd.DataFrame()
    agg = {"open": "first", "high": "max", "low": "min", "close": "last"}
    return df.resample(rule).agg(agg).dropna(how="all")


def _resample_15m_to_1h_4h(
    df: pd.DataFrame,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """From 15m DataFrame produce 1h and 4h. Returns (df_1h, df_4h)."""
    df_1h = _resample_ohlc(df, "1h")
    df_4h = _resample_ohlc(df, "4h")
    return df_1h, df_4h


def get_resampled(
    df: pd.DataFrame,
    freq_minutes: Optional[int] = 15,
) -> Tuple[Optional[pd.DataFrame], Optional[pd.DataFrame]]:
    """
    Return (df_1h, df_4h) for visualization. Use when freq_minutes=15.
    """
    df = _normalize_ohlc(df)
    if freq_minutes != 15 or not isinstance(df.index, pd.DatetimeIndex) or len(df) < 16:
        return None, None
    return _resample_15m_to_1h_4h(df)


def score(
    df: pd.DataFrame,
    freq_minutes: Optional[int] = None,
    config_obj: Any = None,
) -> Dict[str, Any]:
    """
    v2.0 Contract:
    - Input: OHLC DataFrame with datetime index. Optional freq_minutes (15 → auto 1h, 4h).
    - Each condition returns {"long": bool, "short": bool}.
    - long_score / short_score; bias = long_score - short_score.
    - alert_long = (long_score >= 4), alert_short = (short_score >= 4).
    - R:R is inside Fib condition only; no top-level rr_valid.
    """
    cfg = config_obj or config
    df = _normalize_ohlc(df)

    default_result = {
        "long_score": 0,
        "short_score": 0,
        "bias": 0,
        "long_conditions": {n: False for n in CONDITION_NAMES},
        "short_conditions": {n: False for n in CONDITION_NAMES},
        "alert_long": False,
        "alert_short": False,
    }

    if df.empty:
        default_result["error"] = "Empty DataFrame"
        return default_result

    valid, msg = _validate_ohlc(df)
    if not valid:
        default_result["error"] = f"Data validation failed: {msg}"
        return default_result

    freq = freq_minutes if freq_minutes is not None else getattr(cfg, "RESAMPLE_FREQ_MINUTES", None)
    df_1h = df_4h = None
    if freq == 15 and isinstance(df.index, pd.DatetimeIndex) and len(df) >= 16:
        df_1h, df_4h = _resample_15m_to_1h_4h(df)

    # Timeframe assignment: trend on 4h (or df), others on 1h (or df); fib on lowest (df)
    df_trend = df_4h if df_4h is not None and len(df_4h) >= 10 else df
    df_mid = df_1h if df_1h is not None and len(df_1h) >= 10 else df
    df_entry = df

    long_conditions = {}
    short_conditions = {}

    # Condition order: trend, impulse_break, stop_hunt, stop_money, zone, fib, session
    run_df = {
        "trend": df_trend,
        "impulse_break": df_mid,
        "stop_hunt": df_mid,
        "stop_money": df_mid,
        "zone": df_mid,
        "fib": df_entry,
        "session": df_mid,
    }

    for name, fn in zip(CONDITION_NAMES, CONDITION_FUNCS):
        try:
            cdf = run_df.get(name, df_mid)
            if cdf is None or cdf.empty or len(cdf) < 5:
                long_conditions[name] = False
                short_conditions[name] = False
                continue
            result = fn(cdf, cfg)
            if isinstance(result, dict) and "long" in result and "short" in result:
                long_conditions[name] = bool(result["long"])
                short_conditions[name] = bool(result["short"])
            else:
                long_conditions[name] = False
                short_conditions[name] = False
        except Exception as exc:
            logger.warning("Condition %r raised: %s", name, exc, exc_info=True)
            long_conditions[name] = False
            short_conditions[name] = False

    long_score = sum(1 for v in long_conditions.values() if v)
    short_score = sum(1 for v in short_conditions.values() if v)
    bias = long_score - short_score
    alert_long = long_score >= cfg.SCORE_THRESHOLD
    alert_short = short_score >= cfg.SCORE_THRESHOLD

    return {
        "long_score": long_score,
        "short_score": short_score,
        "bias": bias,
        "long_conditions": long_conditions,
        "short_conditions": short_conditions,
        "alert_long": alert_long,
        "alert_short": alert_short,
    }
