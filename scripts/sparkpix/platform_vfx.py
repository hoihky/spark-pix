"""Combat VFX helpers — slash arcs, spark streaks."""

from __future__ import annotations

import math
from typing import Sequence

from sparkpix.canvas import Sprite
from sparkpix.color import ColorLike


def draw_slash_arc(
    s: Sprite,
    hx: int,
    hy: int,
    *,
    deg0: float,
    deg1: float,
    radius: int,
    core: ColorLike,
    fade: ColorLike,
    steps: int = 14,
) -> None:
    """White crescent arc (combo reference)."""
    for i in range(steps):
        t = i / max(1, steps - 1)
        ang = math.radians(deg0 + (deg1 - deg0) * t)
        col = fade if i < steps // 3 else core
        for r in range(radius - 2, radius + 3):
            px = int(hx + math.cos(ang) * r)
            py = int(hy + math.sin(ang) * r)
            s.px(px, py, col, only="opaque")
            s.px(px + 1, py, col, only="opaque")


def draw_spark_streak(
    s: Sprite,
    x0: int,
    y0: int,
    x1: int,
    y1: int,
    *,
    core: ColorLike,
    count: int = 5,
) -> None:
    for i in range(count):
        t = i / max(1, count - 1)
        px = int(x0 + (x1 - x0) * t)
        py = int(y0 + (y1 - y0) * t)
        s.px(px, py, core, only="opaque")
        s.px(px + 1, py - 1, core, only="opaque")
