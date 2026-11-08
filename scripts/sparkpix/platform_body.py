"""Platform fighter body blocks — gi, shorts, boots, gloves (side +X)."""

from __future__ import annotations

from typing import Literal, Sequence, Tuple

ArmPass = Literal["full", "upper", "lower"]

from sparkpix.canvas import Sprite
from sparkpix.color import ColorLike
from sparkpix import render as rd

ColorSeq = Sequence[ColorLike]


def draw_neck_bridge(
    s: Sprite,
    neck: Tuple[int, int],
    head: Tuple[int, int],
    *,
    skin: ColorSeq,
    face_y_adj: int = 0,
) -> None:
    """Narrow skin columns — avoid a wide rect over the eye/cheek box."""
    nx, ny = neck
    hy = head[1] + face_y_adj
    jaw = hy + 8
    y0, y1 = min(ny, jaw), max(ny, jaw)
    s.rect(nx - 3, y0, nx - 2, y1, fill=skin[1])
    s.rect(nx + 2, y0, nx + 3, y1, fill=skin[1])
    s.rect(nx - 2, jaw, nx + 2, jaw + 2, fill=skin[2], only="opaque")


def draw_chest_bridge(
    s: Sprite,
    shoulder: Tuple[int, int],
    *,
    shirt: ColorSeq,
    compact: bool = True,
) -> None:
    sx, sy = shoulder
    d = 4 if compact else 8
    s.rect(sx - d, sy - 4, sx + d - 2, sy + 4, fill=shirt[1])
    s.rect(sx - d + 1, sy - 3, sx + d - 3, sy + 3, fill=shirt[2], only="opaque")


def draw_torso_gi(
    s: Sprite,
    hip: Tuple[int, int],
    shoulder: Tuple[int, int],
    *,
    shirt: ColorSeq,
    trim: ColorSeq,
    belt: ColorSeq,
    squash: float = 1.0,
    compact: bool = True,
) -> None:
    hx, hy = hip
    sx, sy = shoulder
    sq = max(0.88, min(1.0, squash))
    drop = int((1.0 - sq) * (2 if compact else 4))
    pad = 6 if compact else 12
    gi_top = sy + (4 if compact else -1) + drop
    x0, x1 = hx - pad, hx + pad - 2
    y0, y1 = gi_top, hy + 2
    s.ellipse(x0, y0, x1, y1, fill=shirt[0])
    s.ellipse(x0 + 1, y0 + 1, x1 - 1, y1 - 1, fill=shirt[2], only="opaque")
    s.ellipse(x0 + 2, y0 + 2, x0 + 5, y0 + 6, fill=shirt[-1], only="opaque")
    s.rect(x1 - 2, y0 + 2, x1, y1 - 1, fill=shirt[0], only="opaque")
    collar_y0, collar_y1 = gi_top - 4, gi_top - 1
    s.ellipse(sx - 5, collar_y0, sx + 5, collar_y1, fill=trim[1])
    s.rect(sx - 4, collar_y0 + 1, sx + 4, collar_y1, fill=trim[2], only="opaque")
    s.px(sx + 3, collar_y0 + 1, trim[0], only="opaque")
    by = hy - 1
    s.rect(x0, by, x1, by + 2, fill=belt[0])
    s.rect(x0 + 1, by + 1, x1 - 1, by + 1, fill=belt[2], only="opaque")
    s.px(hx, by + 1, trim[-1])


def draw_shorts_leg(
    s: Sprite,
    hip: Tuple[int, int],
    knee: Tuple[int, int],
    foot: Tuple[int, int],
    *,
    back: bool,
    pants: ColorSeq,
    boot: ColorSeq,
    glove: ColorSeq | None = None,
    compact: bool = True,
) -> None:
    tr = (2 if compact else 3) if not back else (1 if compact else 2)
    col = pants[0] if back else pants[2]
    rd.limb_shaded(s, hip, knee, tr, pants if not back else pants[:3])
    rd.limb_shaded(s, knee, foot, max(1, tr), pants if not back else pants[:3])
    fx, fy = foot
    if compact:
        w = 1 if back else 2
        top = boot[0] if back else boot[1]
        s.rect(fx - w, fy - 2, fx + (3 if back else 5), fy - 1, fill=top)
        s.rect(fx - w, fy - 1, fx + (4 if back else 6), fy, fill=boot[0])
        s.px(fx + (2 if back else 4), fy - 1, boot[-1], only="opaque")
    else:
        w = 4
        s.rect(fx - w, fy - 2, fx + 6, fy, fill=boot[0] if back else boot[1])
        s.rect(fx - w + 1, fy, fx + 7, fy + 2, fill=boot[0])
        s.px(fx + 5, fy - 1, boot[-1], only="opaque")
        if back:
            s.rect(fx - 1, fy - 4, fx + 2, fy - 2, fill=boot[2], only="opaque")


def draw_arm_gi(
    s: Sprite,
    shoulder: Tuple[int, int],
    elbow: Tuple[int, int],
    hand: Tuple[int, int],
    *,
    shirt: ColorSeq,
    skin: ColorSeq,
    glove: ColorSeq,
    back: bool = False,
    compact: bool = True,
    part: ArmPass = "full",
) -> None:
    r = (2 if compact else 3) if not back else (1 if compact else 2)
    fr = max(1, r - 1)
    thin = compact and back
    shirt_ramp = shirt if not back else shirt[:3]
    if part in ("full", "upper"):
        rd.limb_shaded(
            s,
            shoulder,
            elbow,
            r,
            shirt_ramp,
            min_radius=1 if thin else 2,
        )
    if part in ("full", "lower"):
        rd.limb_shaded(s, elbow, hand, fr, skin[:3], min_radius=1 if thin else 2)
        hx, hy = hand
        if back and compact:
            s.rect(hx, hy - 1, hx + 2, hy + 2, fill=glove[1])
            s.rect(hx, hy, hx + 1, hy + 1, fill=glove[0], only="opaque")
            s.px(hx + 2, hy, glove[1], only="opaque")
        elif compact:
            s.rect(hx - 1, hy - 2, hx + 2, hy + 1, fill=glove[1])
            s.rect(hx, hy - 1, hx + 1, hy, fill=glove[2], only="opaque")
            s.px(hx + 1, hy, skin[1], only="opaque")
        else:
            s.rect(hx - 2, hy - 3, hx + 3, hy + 2, fill=glove[1])
            s.rect(hx - 1, hy - 2, hx + 2, hy + 1, fill=glove[2], only="opaque")
            s.px(hx + 2, hy, skin[1], only="opaque")
