"""
Plotly overlay helpers: shapes and markers. No logic, only drawing.
"""

from typing import Any, List, Optional, Tuple

import pandas as pd
import plotly.graph_objects as go


def add_candlestick(
    fig: go.Figure,
    df,
    row: int,
    col: int,
    name: str = "OHLC",
) -> None:
    """Add candlestick trace. df must have open, high, low, close and index."""
    fig.add_trace(
        go.Candlestick(
            x=df.index,
            open=df["open"],
            high=df["high"],
            low=df["low"],
            close=df["close"],
            name=name,
            increasing_line_color="#26a69a",
            decreasing_line_color="#ef5350",
        ),
        row=row,
        col=col,
    )


def add_swing_markers(
    fig: go.Figure,
    swing_highs: List[Tuple[Any, float]],
    swing_lows: List[Tuple[Any, float]],
    row: int,
    col: int,
) -> None:
    """Triangle-up for highs, triangle-down for lows."""
    if swing_highs:
        xs, ys = zip(*swing_highs)
        fig.add_trace(
            go.Scatter(
                x=xs, y=ys, mode="markers", name="Swing High",
                marker=dict(symbol="triangle-up", size=10, color="#1976d2"),
            ),
            row=row, col=col,
        )
    if swing_lows:
        xs, ys = zip(*swing_lows)
        fig.add_trace(
            go.Scatter(
                x=xs, y=ys, mode="markers", name="Swing Low",
                marker=dict(symbol="triangle-down", size=10, color="#7b1fa2"),
            ),
            row=row, col=col,
        )


def add_rect(
    fig: go.Figure,
    x0, x1, y0, y1,
    row: int,
    col: int,
    fillcolor: str = "rgba(0,0,0,0.1)",
    line_width: int = 0,
) -> None:
    fig.add_shape(
        type="rect", x0=x0, x1=x1, y0=y0, y1=y1,
        fillcolor=fillcolor, line=dict(width=line_width),
        row=row, col=col,
    )


def add_zone_rect(
    fig: go.Figure,
    x0, x1, y0, y1,
    row: int,
    col: int,
    zone_type: str,
    opacity: float = 0.2,
) -> None:
    """Demand = orange, Supply = grey."""
    if zone_type == "demand":
        fillcolor = f"rgba(255,152,0,{opacity})"
    else:
        fillcolor = f"rgba(158,158,158,{opacity})"
    add_rect(fig, x0, x1, y0, y1, row, col, fillcolor=fillcolor)


def add_retracement_zone_rect(
    fig: go.Figure,
    x0, x1, y_low: float, y_high: float,
    row: int,
    col: int,
    long_zone: bool,
    opacity: float = 0.15,
) -> None:
    """Light green for long, light red for short."""
    if long_zone:
        fillcolor = f"rgba(76,175,80,{opacity})"
    else:
        fillcolor = f"rgba(244,67,54,{opacity})"
    add_rect(fig, x0, x1, y_low, y_high, row, col, fillcolor=fillcolor)


def add_horizontal_line(
    fig: go.Figure,
    y: float,
    row: int,
    col: int,
    color: str = "green",
    dash: str = "dash",
    width: int = 2,
) -> None:
    """Full-width horizontal line (xref from layout)."""
    fig.add_hline(y=y, line_dash=dash, line_color=color, line_width=width, row=row, col=col)


def add_blocking_levels(
    fig: go.Figure,
    high_levels: List[float],
    low_levels: List[float],
    x_min,
    x_max,
    row: int,
    col: int,
) -> None:
    """Black thick horizontal lines. Top 2 highs, top 2 lows."""
    for y in high_levels:
        fig.add_shape(
            type="line", x0=x_min, x1=x_max, y0=y, y1=y,
            line=dict(color="black", width=3),
            row=row, col=col,
        )
    for y in low_levels:
        fig.add_shape(
            type="line", x0=x_min, x1=x_max, y0=y, y1=y,
            line=dict(color="black", width=3),
            row=row, col=col,
        )


def add_impulse_rects(
    fig: go.Figure,
    df,
    bar_indices: List[int],
    row: int,
    col: int,
    long_impulse: bool = True,
) -> None:
    """Green border for long impulse candles, red for short. Rect around body."""
    color = "rgba(76,175,80,0.6)" if long_impulse else "rgba(244,67,54,0.6)"
    idx = df.index
    delta = idx[-1] - idx[-2] if len(idx) >= 2 else pd.Timedelta(hours=1)
    for i in bar_indices:
        if i >= len(df):
            continue
        r = df.iloc[i]
        x0 = idx[i]
        x1 = idx[i + 1] if i + 1 < len(df) else idx[i] + delta
        y0 = min(float(r["open"]), float(r["close"]))
        y1 = max(float(r["open"]), float(r["close"]))
        fig.add_shape(
            type="rect", x0=x0, x1=x1, y0=y0, y1=y1,
            fillcolor="rgba(0,0,0,0)", line=dict(color=color, width=4),
            row=row, col=col,
        )


def add_cluster_markers(
    fig: go.Figure,
    x_vals: List[Any],
    y_val: float,
    row: int,
    col: int,
    long_cluster: bool,
) -> None:
    """Circular markers. Green for long, red for short."""
    color = "#4caf50" if long_cluster else "#f44336"
    fig.add_trace(
        go.Scatter(
            x=x_vals, y=[y_val] * len(x_vals), mode="markers",
            marker=dict(symbol="circle-open", size=12, color=color, line=dict(width=2)),
        ),
        row=row, col=col,
    )


def add_session_arrow(
    fig: go.Figure,
    x_val, y_val,
    row: int,
    col: int,
    long_breakout: bool,
) -> None:
    """Green up arrow or red down arrow."""
    symbol = "triangle-up" if long_breakout else "triangle-down"
    color = "#4caf50" if long_breakout else "#f44336"
    fig.add_trace(
        go.Scatter(
            x=[x_val], y=[y_val], mode="markers",
            marker=dict(symbol=symbol, size=14, color=color),
        ),
        row=row, col=col,
    )


def add_weekly_star_markers(
    fig: go.Figure,
    df: pd.DataFrame,
    markers_list: List[Tuple[Any, str]],
    row: int,
    col: int,
    size: int = 10,
    offset_pct: float = 0.002,
) -> None:
    """
    Weekly high-score stars: long = green star slightly below candle low; short = red star slightly above high.
    markers_list: [(timestamp, 'long'|'short'), ...].
    """
    if not markers_list or df is None or df.empty:
        return
    df = df.rename(columns={c: c.lower() for c in df.columns if c.lower() in ("open", "high", "low", "close")})
    if "high" not in df.columns or "low" not in df.columns:
        return
    idx = df.index
    price_span = float(df["high"].max() - df["low"].min()) or 1.0
    offset = price_span * offset_pct

    long_x, long_y = [], []
    short_x, short_y = [], []
    for ts, side in markers_list:
        try:
            loc = idx.get_indexer([ts], method="nearest")[0]
            if loc < 0 or loc >= len(df):
                continue
            row_ = df.iloc[loc]
            low_, high_ = float(row_["low"]), float(row_["high"])
            if side == "long":
                long_x.append(ts)
                long_y.append(low_ - offset)
            else:
                short_x.append(ts)
                short_y.append(high_ + offset)
        except Exception:
            continue
    if long_x:
        fig.add_trace(
            go.Scatter(
                x=long_x, y=long_y, mode="markers", name="Weekly High Score (Long)",
                marker=dict(symbol="star", size=size, color="green"),
            ),
            row=row, col=col,
        )
    if short_x:
        fig.add_trace(
            go.Scatter(
                x=short_x, y=short_y, mode="markers", name="Weekly High Score (Short)",
                marker=dict(symbol="star", size=size, color="red"),
            ),
            row=row, col=col,
        )
