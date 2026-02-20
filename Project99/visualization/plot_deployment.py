"""
15M Deployment Chart: candlestick + Fib levels + one zone.
"""

from typing import Any, Dict, Optional

import pandas as pd
import plotly.graph_objects as go

from .overlays import add_candlestick, add_horizontal_line, add_weekly_star_markers, add_zone_rect


def plot_deployment(
    fig: go.Figure,
    df: pd.DataFrame,
    data: Dict[str, Any],
    row: int,
    col: int,
    result: Optional[Dict[str, Any]] = None,
    show_fib: bool = True,
    show_zone: bool = True,
) -> None:
    if df is None or df.empty:
        return
    df = df.rename(columns={c: c.lower() for c in df.columns if c.lower() in ("open", "high", "low", "close")})
    add_candlestick(fig, df, row, col, name="15M")
    if not data:
        return
    # PATCH 2.1.1: Fib only when engine scored impulse_break True (no fallback)
    lc = (result or {}).get("long_conditions", {})
    sc = (result or {}).get("short_conditions", {})
    if show_fib and data.get("fib") and (lc.get("impulse_break") or sc.get("impulse_break")):
        ih, il, f50, f618, f88 = data["fib"]
        add_horizontal_line(fig, f50, row, col, color="gray", dash="dot", width=1)
        add_horizontal_line(fig, f618, row, col, color="gray", dash="dot", width=1)
        add_horizontal_line(fig, f88, row, col, color="gray", dash="dot", width=1)
    if show_zone and data.get("zone"):
        ztype, zhigh, zlow, t0, t1 = data["zone"]
        add_zone_rect(fig, t0, t1, zlow, zhigh, row, col, zone_type="demand" if ztype == "demand" else "supply", opacity=0.2)

    # Weekly high-score star markers (last 4 weeks) – 15M only
    add_weekly_star_markers(fig, df, data.get("weekly_signal", []), row, col, size=10)
