"""
Project99 — Phase 2 Transparent Visualization Layer.
Pure rendering: consumes score result + OHLC; no scoring logic.
"""

from .data_provider import ensure_asia_hong_kong, get_visualization_data
from .layout import _compute_weekly_crossings, build_three_panel_figure

compute_weekly_crossings = _compute_weekly_crossings

__all__ = ["get_visualization_data", "build_three_panel_figure", "ensure_asia_hong_kong", "compute_weekly_crossings"]
