"""
1H Structure Chart: candlestick + impulse + stop hunt + stop money + blocking + zone + session.
"""

from typing import Any, Dict, Optional

import pandas as pd
import plotly.graph_objects as go

from .overlays import (
    add_blocking_levels,
    add_candlestick,
    add_cluster_markers,
    add_horizontal_line,
    add_impulse_rects,
    add_retracement_zone_rect,
    add_session_arrow,
    add_weekly_star_markers,
    add_zone_rect,
)


def plot_structure(
    fig: go.Figure,
    df: pd.DataFrame,
    data: Dict[str, Any],
    row: int,
    col: int,
    result: Optional[Dict[str, Any]] = None,
    show_impulse: bool = True,
    show_stop_hunt: bool = True,
    show_stop_money: bool = True,
    show_blocking: bool = True,
    show_zone: bool = True,
    show_session: bool = True,
) -> None:
    if df is None or df.empty:
        return
    df = df.rename(columns={c: c.lower() for c in df.columns if c.lower() in ("open", "high", "low", "close")})
    add_candlestick(fig, df, row, col, name="1H")
    if not data:
        return
    x_min, x_max = df.index[0], df.index[-1]
    lc = (result or {}).get("long_conditions", {})
    sc = (result or {}).get("short_conditions", {})

    if show_impulse and data.get("impulse_bars"):
        long_bars = [i for i in data["impulse_bars"] if i < len(df) and float(df["close"].iloc[i]) > float(df["open"].iloc[i])]
        short_bars = [i for i in data["impulse_bars"] if i < len(df) and float(df["close"].iloc[i]) <= float(df["open"].iloc[i])]
        add_impulse_rects(fig, df, long_bars, row, col, long_impulse=True)
        add_impulse_rects(fig, df, short_bars, row, col, long_impulse=False)

    # PATCH 2.1.1: Stop Hunt retracement band only when engine scored stop_hunt True
    if show_stop_hunt and (lc.get("stop_hunt") or sc.get("stop_hunt")):
        if lc.get("stop_hunt") and data.get("stop_hunt_double_bottom"):
            db = data["stop_hunt_double_bottom"]
            level, z_low, z_high = db
            add_retracement_zone_rect(fig, x_min, x_max, z_low, z_high, row, col, long_zone=True, opacity=0.15)
            add_cluster_markers(fig, [df.index[-1]], level, row, col, long_cluster=True)
        if sc.get("stop_hunt") and data.get("stop_hunt_double_top"):
            dt = data["stop_hunt_double_top"]
            level, z_low, z_high = dt
            add_retracement_zone_rect(fig, x_min, x_max, z_low, z_high, row, col, long_zone=False, opacity=0.15)
            add_cluster_markers(fig, [df.index[-1]], level, row, col, long_cluster=False)

    if show_stop_money and data.get("stop_money_target"):
        side, level = data["stop_money_target"]
        add_horizontal_line(fig, level, row, col, color="green" if side == "long" else "red", dash="dash", width=2)

    if show_blocking:
        add_blocking_levels(
            fig,
            data.get("blocking_highs", [])[:2],
            data.get("blocking_lows", [])[:2],
            x_min, x_max,
            row, col,
        )

    if show_zone and data.get("zone"):
        ztype, zhigh, zlow, t0, t1 = data["zone"]
        add_zone_rect(fig, t0, t1, zlow, zhigh, row, col, zone_type="demand" if ztype == "demand" else "supply", opacity=0.2)

    if show_session:
        if data.get("session_breakout_long"):
            add_session_arrow(fig, df.index[-1], float(df["high"].iloc[-1]), row, col, long_breakout=True)
        if data.get("session_breakout_short"):
            add_session_arrow(fig, df.index[-1], float(df["low"].iloc[-1]), row, col, long_breakout=False)

    # Weekly high-score star markers (last 4 weeks) – 1H only
    add_weekly_star_markers(fig, df, data.get("weekly_signal", []), row, col, size=10)
