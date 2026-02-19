"""
Three-panel figure: 4H, 1H, 15M. Shared x only for same TF family optional; here shared_xaxes=False.
"""

from typing import Any, Dict, Optional

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from .data_provider import get_visualization_data
from .plot_trend import plot_trend
from .plot_structure import plot_structure
from .plot_deployment import plot_deployment


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
) -> go.Figure:
    """
    Build 3-row Plotly figure. Overlays controlled by show_* toggles.
    """
    fig = make_subplots(
        rows=3,
        cols=1,
        shared_xaxes=False,
        vertical_spacing=0.08,
        subplot_titles=("4H Trend", "1H Structure", "15M Deployment"),
        row_heights=[0.35, 0.35, 0.3],
    )
    viz = get_visualization_data(df_15m, df_1h, df_4h, result)

    if df_4h is not None and not df_4h.empty:
        plot_trend(
            fig, df_4h, viz.get("4h", {}), row=1, col=1,
            show_trend=show_trend, show_blocking=show_blocking, show_zone=show_zone,
        )
    if df_1h is not None and not df_1h.empty:
        plot_structure(
            fig, df_1h, viz.get("1h", {}), row=2, col=1,
            result=result,
            show_impulse=show_impulse, show_stop_hunt=show_stop_hunt, show_stop_money=show_stop_money,
            show_blocking=show_blocking, show_zone=show_zone, show_session=show_session,
        )
    plot_deployment(
        fig, df_15m, viz.get("15m", {}), row=3, col=1,
        result=result,
        show_fib=show_fib, show_zone=show_zone,
    )

    fig.update_layout(
        height=900,
        template="plotly_white",
        showlegend=True,
        xaxis_rangeslider_visible=False,
        xaxis2_rangeslider_visible=False,
        xaxis3_rangeslider_visible=False,
    )
    return fig
