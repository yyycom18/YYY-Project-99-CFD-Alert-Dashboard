"""
4H Trend Chart: candlestick + swing markers + blocking levels + one zone.
"""

from typing import Any, Dict

import pandas as pd
import plotly.graph_objects as go

from .overlays import (
    add_blocking_levels,
    add_candlestick,
    add_swing_markers,
    add_zone_rect,
)


def plot_trend(
    fig: go.Figure,
    df: pd.DataFrame,
    data: Dict[str, Any],
    row: int,
    col: int,
    show_trend: bool = True,
    show_blocking: bool = True,
    show_zone: bool = True,
) -> None:
    if df is None or df.empty:
        return
    df = df.rename(columns={c: c.lower() for c in df.columns if c.lower() in ("open", "high", "low", "close")})
    add_candlestick(fig, df, row, col, name="4H")
    if not data:
        return
    if show_trend:
        add_swing_markers(
            fig,
            data.get("swing_highs", []),
            data.get("swing_lows", []),
            row, col,
        )
    if show_blocking:
        x_min, x_max = df.index[0], df.index[-1]
        add_blocking_levels(
            fig,
            data.get("blocking_highs", [])[:2],
            data.get("blocking_lows", [])[:2],
            x_min, x_max,
            row, col,
        )
    zone = data.get("zone")
    if show_zone and zone:
        ztype, zhigh, zlow, t0, t1 = zone
        add_zone_rect(fig, t0, t1, zlow, zhigh, row, col, zone_type="demand" if ztype == "demand" else "supply", opacity=0.2)
