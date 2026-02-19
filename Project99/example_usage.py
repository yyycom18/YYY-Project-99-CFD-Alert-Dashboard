"""
Example: Phase 1 v2.0 — directional scoring, 15m → 1h/4h resampling
Run from project root: python -m Project99.example_usage
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd
import numpy as np
from Project99 import score

# OHLC with datetime index (e.g. 15m). v2.0: long_score / short_score, alert_long / alert_short
n = 96  # e.g. 24h of 15m bars
np.random.seed(42)
closes = 100 + np.cumsum(np.random.randn(n) * 0.3)
df = pd.DataFrame({
    "open": np.roll(closes, 1),
    "high": closes + np.abs(np.random.randn(n)) * 0.2,
    "low": closes - np.abs(np.random.randn(n)) * 0.2,
    "close": closes,
})
df.iloc[0, 0] = 100
df["high"] = df[["open", "high", "close"]].max(axis=1)
df["low"] = df[["open", "low", "close"]].min(axis=1)
df.index = pd.date_range("2024-01-01 05:00", periods=n, freq="15min")

# v2.0: freq_minutes=15 triggers auto 1h/4h resampling
result = score(df, freq_minutes=15)

print("long_score:", result["long_score"])
print("short_score:", result["short_score"])
print("bias:", result["bias"])
print("long_conditions:", result["long_conditions"])
print("short_conditions:", result["short_conditions"])
print("alert_long:", result["alert_long"])
print("alert_short:", result["alert_short"])
if result.get("error"):
    print("error:", result["error"])
