"""Flowing scarf / cape tail — keyed to reference strip tip_dx/dy per frame."""

from __future__ import annotations

import math
from typing import Optional, Sequence, Tuple

from sparkpix.canvas import Sprite
from sparkpix.color import ColorLike

ColorSeq = Sequence[ColorLike]


def draw_scarf_mass(
    s: Sprite,
    neck: Tuple[int, int],
    *,
    scarf: ColorSeq,
    phase: float,
    behind: bool,
    compact: bool = True,
    wave_offset: int = 0,
    lift_offset: int = 0,
    tip_dx: Optional[int] = None,
    tip_dy: Optional[int] = None,
    tip_world_x: Optional[int] = None,
    head_y: Optional[int] = None,
    face_y_adj: int = 0,
) -> None:
    nx, ny = neck
    dark, mid, light, hi = scarf[0], scarf[1], scarf[2], scarf[-1]
    span = 18 if compact else 28
    jaw_floor = (head_y + face_y_adj + 9) if head_y is not None else ny + 1

    if tip_world_x is not None:
        tip_x = int(tip_world_x)
        mid_y = ny + int(tip_dy if tip_dy is not None else 0) + lift_offset
    elif tip_dx is not None:
        tip_x = nx + int(tip_dx)
        mid_y = ny + int(tip_dy if tip_dy is not None else 0) + lift_offset
    else:
        amp = 1 if compact else 3
        wave = int(math.sin(phase * math.pi * 2) * amp) + wave_offset
        lift = int(math.cos(phase * math.pi * 2) * (1 if compact else 2)) + lift_offset
        tip_x = nx - span + wave
        mid_y = ny - 1 + lift

    if behind:
        attach_y0 = max(ny, jaw_floor)
        bulge_x = nx - max(8, (nx - tip_x) // 2)
        pts = [
            (nx - 1, attach_y0),
            (tip_x, mid_y),
            (tip_x - 2, mid_y + 4),
            (bulge_x, ny + 3),
            (nx - 4, ny + 2),
        ]
        s.polygon(pts, fill=mid)
        s.polygon(
            [
                (nx - 2, attach_y0),
                (tip_x + 1, mid_y + 1),
                (tip_x, mid_y + 3),
                (bulge_x + 2, ny + 2),
            ],
            fill=light,
            only="opaque",
        )
        s.ellipse(tip_x - 3, mid_y, tip_x + 1, mid_y + 4, fill=dark, only="opaque")
        s.line(nx - 5, attach_y0, tip_x, mid_y, hi)
        s.px(tip_x, mid_y + 2, scarf[2], only="opaque")
    else:
        ky0, ky1 = ny + 1, ny + 4
        s.rect(nx - 4, ky0, nx - 1, ky1, fill=scarf[1])
        s.rect(nx - 3, ky0 + 1, nx - 1, ky1 - 1, fill=scarf[2], only="opaque")
        s.px(nx - 3, ky0, hi, only="opaque")
        s.px(nx - 2, ky1 - 1, scarf[0], only="opaque")
