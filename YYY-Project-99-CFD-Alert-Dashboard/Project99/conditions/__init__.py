"""
Project99 — One file per condition. Structural + behavioral only.
"""

from .trend import trend
from .impulse_break import impulse_break
from .stop_hunt import stop_hunt
from .stop_money import stop_money
from .zone import zone
from .fib import fib
from .session import session

CONDITION_NAMES = [
    "trend",
    "impulse_break",
    "stop_hunt",
    "stop_money",
    "zone",
    "fib",
    "session",
]

CONDITION_FUNCS = [
    trend,
    impulse_break,
    stop_hunt,
    stop_money,
    zone,
    fib,
    session,
]

CONDITION_STATUS = {name: "implemented" for name in CONDITION_NAMES}
