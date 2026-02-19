"""
Project99 — Structural scoring engine config.
All thresholds here. No EMA / no generic indicators.
Timezone: HKT (UTC+8).
"""

# Scoring (v2.0 directional)
SCORE_THRESHOLD = 4  # alert_long / alert_short when score >= 4
RR_MIN = 1.3        # R:R enforced inside Fib condition only

# Resampling: 15m input → auto 1h, 4h
RESAMPLE_FREQ_MINUTES = 15

# Trend (Condition 1) — structural retracement only
RETRACE_MAX_TREND = 0.618   # Trend intact if retracement <= this
RETRACE_RANGE = 0.7        # Above this → treat as range (0.618–0.7 tolerance)

# Swing detection (structural)
SWING_LOOKBACK = 5        # Bars left/right to confirm swing high/low
SWING_LEFT = 2
SWING_RIGHT = 2

# Impulse Break (Condition 2)
IMPULSE_CANDLES_COUNT = 3
IMPULSE_BODY_RATIO = 1.5   # Body vs recent average
IMPULSE_EXTREME_RATIO = 2.0  # Single candle “extremely large” vs average
WICK_TO_BODY_MAX = 0.5     # Small wick = wick <= body * this

# Stop Hunt / Stop Money (Conditions 3 & 4) — v2.1 liquidity doctrine
DOUBLE_TOLERANCE_PCT = 0.005
DOUBLE_LOOKBACK = 20
# Stop Hunt: retracement zone 0.5–0.7 (pre-deployment, no sweep)
RETRACE_MIN_STOP_HUNT = 0.5
RETRACE_MAX_STOP_HUNT = 0.7
# Stop Money: forward liquidity target space validation
SPACE_DISTANCE_ATR_MULT = 2.0
ATR_PERIOD = 20

# Zone (Condition 5)
ZONE_IMPULSE_BODY_RATIO = 1.2
ZONE_WICK_TO_BODY_MAX = 0.5
ZONE_REVISIT_TOLERANCE_PCT = 0.01

# Fibonacci (Condition 6)
FIB_PRIMARY = 0.618
FIB_SECONDARY = 0.5
FIB_STOP_AT_88 = 0.88
FIB_TOLERANCE_PCT = 0.01

# Session (Condition 7) — HKT
# Asia: 05:00–16:00
SESSION_ASIA_START_HKT = 5
SESSION_ASIA_END_HKT = 16
# EU: 15:00–24:00
SESSION_EU_START_HKT = 15
SESSION_EU_END_HKT = 24
# US: 20:00–05:00 (wrap)
SESSION_US_START_HKT = 20
SESSION_US_END_HKT = 5  # 05:00 next day
