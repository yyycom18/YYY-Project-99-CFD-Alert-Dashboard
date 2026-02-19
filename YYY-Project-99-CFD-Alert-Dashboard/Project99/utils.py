"""
Project99 — Shared utilities (R:R calculation, etc.)
Avoids circular imports between engine and conditions.
"""

from typing import Optional, Any, Tuple


def compute_rr_ratio(
    entry: float,
    stop: float,
    target: float,
    min_rr: float = 1.3,
) -> Tuple[bool, float]:
    """
    Compute R:R ratio and validate setup.
    Returns (is_valid, actual_ratio).
    Validates long/short setup (stop and target on opposite sides of entry).
    """
    if entry == stop or entry == target:
        return False, 0.0
    # Long: stop < entry < target
    if entry > stop and entry < target:
        risk = entry - stop
        reward = target - entry
    # Short: stop > entry > target
    elif entry < stop and entry > target:
        risk = stop - entry
        reward = entry - target
    else:
        return False, 0.0
    if risk <= 0 or reward <= 0:
        return False, 0.0
    ratio = reward / risk
    return ratio >= min_rr, ratio
