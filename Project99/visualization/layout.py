"""
Three-panel figure: 4H, 1H, 15M. Shared x only for same TF family optional; here shared_xaxes=False.
Phase 2.3 & 2.4: weekend gaps removed, ~500 bars visible, weekly stars, smart Y-axis, grid, proportions.
"""

from typing import Any, Callable, Dict, List, Optional, Tuple

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from .data_provider import ensure_asia_hong_kong, get_visualization_data
from .plot_trend import plot_trend
from .plot_structure import plot_structure
from .plot_deployment import plot_deployment

# Approximate bars to show per timeframe (Patch 2)
PLOT_BARS = 500


def _resample_15m_to_1h_viz(df_15m: pd.DataFrame) -> pd.DataFrame:
    """Resample 15m to 1H (same logic as engine). Visualization layer only."""
    if df_15m is None or df_15m.empty or not isinstance(df_15m.index, pd.DatetimeIndex):
        return pd.DataFrame()
    df = df_15m.rename(columns={c: c.lower() for c in df_15m.columns if c.lower() in ("open", "high", "low", "close")})
    if "open" not in df.columns:
        return pd.DataFrame()
    agg = {"open": "first", "high": "max", "low": "min", "close": "last"}
    return df.resample("1h").agg(agg).dropna(how="all")


def _compute_weekly_crossings(
    df_15m: pd.DataFrame,
    score_fn: Callable[..., Dict[str, Any]],
    asset_name: str,
    lookback_weeks: int = 4,
) -> List[Dict[str, Any]]:
    """
    Weekly crossing detection (1H only). Receives RAW df only; all score_fn calls use raw data.
    Display date/time converted to Asia/Hong_Kong when storing record.
    Direction: LONG, SHORT, BIAS_LONG, BIAS_SHORT. Condition source strictly by direction.
    """
    out: List[Dict[str, Any]] = []
    if df_15m is None or df_15m.empty or len(df_15m) < 50:
        return out
    if not isinstance(df_15m.index, pd.DatetimeIndex):
        return out
    df_1h = _resample_15m_to_1h_viz(df_15m)
    if df_1h.empty or len(df_1h) < 2:
        return out
    cutoff = df_1h.index[-1] - pd.Timedelta(weeks=lookback_weeks)
    prev_long = -1
    prev_short = -1
    prev_abs_bias = -1
    for ts in df_1h.index:
        if ts < cutoff:
            continue
        slice_15m = df_15m[df_15m.index <= ts]
        if len(slice_15m) < 50:
            continue
        try:
            res = score_fn(slice_15m, freq_minutes=15)
        except Exception:
            continue
        curr_long = res.get("long_score", 0)
        curr_short = res.get("short_score", 0)
        curr_bias = res.get("bias", 0)
        curr_abs_bias = abs(curr_bias)
        long_cross = prev_long >= 0 and prev_long < 4 and curr_long >= 4
        short_cross = prev_short >= 0 and prev_short < 4 and curr_short >= 4
        bias_cross = prev_abs_bias >= 0 and prev_abs_bias < 2 and curr_abs_bias >= 2
        prev_long = curr_long
        prev_short = curr_short
        prev_abs_bias = curr_abs_bias
        direction = None
        if long_cross:
            direction = "LONG"
        elif short_cross:
            direction = "SHORT"
        elif bias_cross:
            direction = "BIAS_LONG" if curr_bias > 0 else "BIAS_SHORT"
        if direction is None:
            continue
        if direction == "LONG":
            conds = res.get("long_conditions", {})
        elif direction == "SHORT":
            conds = res.get("short_conditions", {})
        elif direction == "BIAS_LONG":
            conds = res.get("long_conditions", {})
        elif direction == "BIAS_SHORT":
            conds = res.get("short_conditions", {})
        else:
            conds = {}
        try:
            if getattr(ts, "tzinfo", None) is None:
                dt_hkt = ts.tz_localize("UTC").tz_convert("Asia/Hong_Kong")
            else:
                dt_hkt = ts.tz_convert("Asia/Hong_Kong")
        except Exception:
            dt_hkt = ts
        date_str = dt_hkt.strftime("%d%m%Y") if hasattr(dt_hkt, "strftime") else str(ts)[:10]
        time_str = dt_hkt.strftime("%H:%M") if hasattr(dt_hkt, "strftime") else (str(ts)[11:16] if len(str(ts)) >= 16 else "")
        out.append({
            "datetime": ts,
            "date_str": date_str,
            "time_str": time_str,
            "asset": asset_name,
            "tf": "1H",
            "direction": direction,
            "long_score": curr_long,
            "short_score": curr_short,
            "bias": curr_bias,
            "conditions": conds,
        })
    return out


def _slice_lookback(df: Optional[pd.DataFrame], n: int) -> Optional[pd.DataFrame]:
    """Last n bars only; no change to data provider or engine."""
    if df is None or df.empty or n <= 0:
        return df
    return df.tail(n).copy()


def _compute_weekly_high_score_markers(
    df_15m: pd.DataFrame,
    df_1h: Optional[pd.DataFrame],
    score_fn: Callable[..., Dict[str, Any]],
    lookback_weeks: int = 4,
) -> Tuple[List[Tuple[Any, str]], List[Tuple[Any, str]]]:
    """
    For last 4 calendar weeks: bars where long_score>=4 or short_score>=4 or abs(bias)>=2.
    Returns ([(ts, 'long'|'short'), ...] for 1H, same for 15M). Visualization layer only; calls score_fn.
    """
    markers_1h: List[Tuple[Any, str]] = []
    markers_15m: List[Tuple[Any, str]] = []
    if df_15m is None or df_15m.empty or len(df_15m) < 50:
        return markers_1h, markers_15m
    if not isinstance(df_15m.index, pd.DatetimeIndex):
        return markers_1h, markers_15m
    cutoff = df_15m.index[-1] - pd.Timedelta(weeks=lookback_weeks)

    # 1H bars in last 4 weeks
    if df_1h is not None and not df_1h.empty and isinstance(df_1h.index, pd.DatetimeIndex):
        for ts in df_1h.index:
            if ts < cutoff:
                continue
            slice_15m = df_15m[df_15m.index <= ts]
            if len(slice_15m) < 50:
                continue
            try:
                res = score_fn(slice_15m, freq_minutes=15)
                if res.get("long_score", 0) >= 4 or res.get("short_score", 0) >= 4 or abs(res.get("bias", 0)) >= 2:
                    side = "long" if (res.get("long_score", 0) >= 4 or res.get("bias", 0) >= 2) else "short"
                    markers_1h.append((ts, side))
            except Exception:
                pass

    # 15M bars in last 4 weeks (sample every 4 bars to keep responsive)
    for i in range(len(df_15m) - 1, -1, -4):
        if i < 50:
            break
        ts = df_15m.index[i]
        if ts < cutoff:
            break
        slice_15m = df_15m.iloc[: i + 1]
        try:
            res = score_fn(slice_15m, freq_minutes=15)
            if res.get("long_score", 0) >= 4 or res.get("short_score", 0) >= 4 or abs(res.get("bias", 0)) >= 2:
                side = "long" if (res.get("long_score", 0) >= 4 or res.get("bias", 0) >= 2) else "short"
                markers_15m.append((ts, side))
        except Exception:
            pass

    return markers_1h, markers_15m


def _y_range_for_row(
    df: pd.DataFrame,
    blocking_highs: List[float],
    blocking_lows: List[float],
    stop_money_level: Optional[float],
    padding_pct_range: float = 0.05,
    padding_pct_abs: float = 0.002,
) -> Tuple[float, float]:
    """Smart Y-axis: visible range + padding; expand to include blocking and stop_money."""
    df = df.rename(columns={c: c.lower() for c in df.columns if c.lower() in ("open", "high", "low", "close")})
    if "high" not in df.columns or "low" not in df.columns:
        return 0.0, 1.0
    visible_high = float(df["high"].max())
    visible_low = float(df["low"].min())
    price_range = visible_high - visible_low
    padding = max(price_range * padding_pct_range, visible_high * padding_pct_abs)
    y_min = visible_low - padding
    y_max = visible_high + padding
    for y in blocking_highs + blocking_lows:
        if y < y_min:
            y_min = y - padding
        if y > y_max:
            y_max = y + padding
    if stop_money_level is not None:
        if stop_money_level < y_min:
            y_min = stop_money_level - padding
        if stop_money_level > y_max:
            y_max = stop_money_level + padding
    return y_min, y_max


def build_three_panel_figure(
    df_15m: pd.DataFrame,
    df_1h: Optional[pd.DataFrame],
    df_4h: Optional[pd.DataFrame],
    result: Optional[Dict[str, Any]] = None,
    show_trend: bool = True,
    show_impulse: bool = True,
    show_stop_hunt: bool = True,
    show_stop_money: bool = True,
    show_zone: bool = True,
    show_fib: bool = True,
    show_session: bool = True,
    show_blocking: bool = True,
    score_fn: Optional[Callable[..., Dict[str, Any]]] = None,
) -> go.Figure:
    """
    Build 3-row Plotly figure. Overlays controlled by show_* toggles.
    Phase 2.3/2.4: ~500 bars per TF, weekend gaps removed, weekly stars (1H/15M), smart Y-axis, grid.
    """
    # Patch 2: extend visible history (slice before plotting only)
    df_4h_plot = _slice_lookback(df_4h, PLOT_BARS)
    df_1h_plot = _slice_lookback(df_1h, PLOT_BARS)
    df_15m_plot = _slice_lookback(df_15m, PLOT_BARS)

    # Phase 2.6: timezone alignment to Asia/Hong_Kong (TradingView UTC+8)
    df_4h_plot = ensure_asia_hong_kong(df_4h_plot)
    df_1h_plot = ensure_asia_hong_kong(df_1h_plot)
    df_15m_plot = ensure_asia_hong_kong(df_15m_plot)

    # Patch 5: row heights and spacing (Phase 2.6: vertical_spacing 0.08)
    fig = make_subplots(
        rows=3,
        cols=1,
        shared_xaxes=False,
        vertical_spacing=0.08,
        subplot_titles=("4H Trend", "1H Structure", "15M Deployment"),
        row_heights=[0.35, 0.35, 0.30],
    )
    viz = get_visualization_data(df_15m_plot, df_1h_plot, df_4h_plot, result)

    # Weekly high-score markers (Patch 3) – last 4 weeks, 1H and 15M only
    if score_fn is not None:
        weekly_1h, weekly_15m = _compute_weekly_high_score_markers(
            df_15m_plot, df_1h_plot, score_fn, lookback_weeks=4
        )
        viz.setdefault("1h", {})["weekly_signal"] = weekly_1h
        viz.setdefault("15m", {})["weekly_signal"] = weekly_15m

    if df_4h_plot is not None and not df_4h_plot.empty:
        plot_trend(
            fig, df_4h_plot, viz.get("4h", {}), row=1, col=1,
            show_trend=show_trend, show_blocking=show_blocking, show_zone=show_zone,
        )
    if df_1h_plot is not None and not df_1h_plot.empty:
        plot_structure(
            fig, df_1h_plot, viz.get("1h", {}), row=2, col=1,
            result=result,
            show_impulse=show_impulse, show_stop_hunt=show_stop_hunt, show_stop_money=show_stop_money,
            show_blocking=show_blocking, show_zone=show_zone, show_session=show_session,
        )
    plot_deployment(
        fig, df_15m_plot, viz.get("15m", {}), row=3, col=1,
        result=result,
        show_fib=show_fib, show_zone=show_zone,
    )

    fig.update_layout(
        height=1100,
        template="plotly_white",
        showlegend=True,
        xaxis_rangeslider_visible=False,
        xaxis2_rangeslider_visible=False,
        xaxis3_rangeslider_visible=False,
    )

    # Patch 1: Remove weekend gaps (per subplot)
    for r in [1, 2, 3]:
        fig.update_xaxes(rangebreaks=[dict(bounds=["sat", "mon"])], row=r, col=1)

    # Patch 4: Smart Y-axis per subplot
    if df_4h_plot is not None and not df_4h_plot.empty:
        v4 = viz.get("4h", {})
        y_min_1, y_max_1 = _y_range_for_row(
            df_4h_plot,
            v4.get("blocking_highs", [])[:2],
            v4.get("blocking_lows", [])[:2],
            None,
        )
        fig.update_yaxes(range=[y_min_1, y_max_1], row=1, col=1, autorange=False)
    if df_1h_plot is not None and not df_1h_plot.empty:
        v1 = viz.get("1h", {})
        sm = v1.get("stop_money_target")
        stop_level = sm[1] if isinstance(sm, (list, tuple)) and len(sm) == 2 else None
        y_min_2, y_max_2 = _y_range_for_row(
            df_1h_plot,
            v1.get("blocking_highs", [])[:2],
            v1.get("blocking_lows", [])[:2],
            stop_level,
        )
        fig.update_yaxes(range=[y_min_2, y_max_2], row=2, col=1, autorange=False)
    if df_15m_plot is not None and not df_15m_plot.empty:
        v15 = viz.get("15m", {})
        y_min_3, y_max_3 = _y_range_for_row(
            df_15m_plot,
            v15.get("blocking_highs", [])[:2],
            v15.get("blocking_lows", [])[:2],
            None,
        )
        fig.update_yaxes(range=[y_min_3, y_max_3], row=3, col=1, autorange=False)

    # Patch 6: Grid
    for r in [1, 2, 3]:
        fig.update_xaxes(showgrid=True, gridcolor="rgba(200,200,200,0.15)", row=r, col=1)
        fig.update_yaxes(showgrid=True, gridcolor="rgba(200,200,200,0.15)", row=r, col=1)

    return fig
