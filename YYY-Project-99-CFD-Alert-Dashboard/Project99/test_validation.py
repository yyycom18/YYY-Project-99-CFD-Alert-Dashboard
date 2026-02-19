"""
Validation tests for Phase 1 v2.0 (directional, resampling).
Run: python -m Project99.test_validation
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd
import numpy as np
from Project99 import score
from Project99.utils import compute_rr_ratio


def test_invalid_ohlc():
    df = pd.DataFrame({"open": [100], "high": [90], "low": [80], "close": [85]})
    r = score(df)
    assert r["error"] is not None
    assert "High" in r["error"] or "Low" in r["error"]
    print("OK: Invalid OHLC rejected")


def test_rr_in_fib():
    """R:R logic lives in Fib condition; engine has no rr_valid."""
    r = score(pd.DataFrame())
    assert "rr_valid" not in r
    assert "total_score" not in r
    assert "long_score" in r and "short_score" in r
    print("OK: v2 output format (long_score, short_score)")


def test_output_format():
    df = pd.DataFrame({
        "open": [100, 101], "high": [101, 102], "low": [99, 100], "close": [101, 102],
    })
    df.index = pd.date_range("2024-01-01 09:00", periods=2, freq="1h")
    r = score(df)
    assert "long_score" in r and "short_score" in r
    assert "bias" in r
    assert "long_conditions" in r and "short_conditions" in r
    assert "alert_long" in r and "alert_short" in r
    assert r["bias"] == r["long_score"] - r["short_score"]
    print("OK: Output format (bias, long_conditions, short_conditions, alert_long, alert_short)")


def test_empty_df():
    r = score(pd.DataFrame())
    assert r["long_score"] == 0 and r["short_score"] == 0
    assert r["error"] == "Empty DataFrame"
    print("OK: Empty df handled")


def test_nan_handling():
    df = pd.DataFrame({
        "open": [100, np.nan], "high": [101, 102], "low": [99, 100], "close": [101, 102],
    })
    r = score(df)
    assert r["error"] is not None
    print("OK: NaN rejected")


def test_compute_rr_ratio():
    valid, _ = compute_rr_ratio(100, 95, 110, 1.3)
    assert valid
    invalid, _ = compute_rr_ratio(100, 105, 110, 1.3)
    assert not invalid
    print("OK: R:R ratio (used inside Fib condition)")


if __name__ == "__main__":
    test_invalid_ohlc()
    test_rr_in_fib()
    test_output_format()
    test_empty_df()
    test_nan_handling()
    test_compute_rr_ratio()
    print("\nAll validation tests passed.")
