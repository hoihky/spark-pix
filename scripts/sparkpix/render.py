"""Production shading and finish passes (upper-left light, ramp discipline)."""

from __future__ import annotations

from typing import Sequence, Tuple

from PIL import Image

from sparkpix.canvas import Sprite
from sparkpix.color import ColorLike, RGBA

ColorSeq = Sequence[ColorLike]


def limb_shaded(
    s: Sprite,
    p0: Tuple[int, int],
    p1: Tuple[int, int],
    radius: int,
    ramp: ColorSeq,
    *,
    only: ColorLike = None,
) -> None:
    """Filled limb: dark underpaint → mid body → upper-left highlight ticks."""
    r = max(2, radius)
    dark = ramp[0]
    mid = ramp[2] if len(ramp) > 2 else ramp[1]
    hi = ramp[-1]
    s.capsule(p0[0], p0[1], p1[0], p1[1], r, dark, only=only)
    inner_only = "opaque" if only is None else only
    s.capsule(p0[0], p0[1], p1[0], p1[1], max(1, r - 1), mid, only=inner_only)
    sx, sy = min(p0[0], p1[0]), min(p0[1], p1[1])
    s.px(sx - 1, sy - 1, hi, only="opaque")
    s.px(sx, sy - 1, hi, only="opaque")
    s.px(sx - 1, sy, hi, only="opaque")


def finish_production_pass(
    s: Sprite,
    ink: ColorLike,
    *,
    trim_specks: bool = True,
    min_speck_neighbors: int = 0,
) -> None:
    """
    Standard ship pass: optional speck cleanup, then outside hull outline.
    Call after all body/VFX on the layer (ghosts/outlines drawn separately).

    Pre-outline trim uses ``min_speck_neighbors=0`` so 1-wide hair/antenna pixels
    are not erased (see profile_head_facing_right crown bridge).
    """
    if trim_specks:
        s.trim_isolated_specks(min_neighbors=min_speck_neighbors)
    s.outline(ink, where="outside")
    if trim_specks:
        # Outline can leave 0-neighbor ink on the canvas edge (frame border).
        s.trim_isolated_specks(min_neighbors=0)


def matte_composite(img: Image.Image, matte: RGBA = (52, 56, 72, 255)) -> Image.Image:
    """Review background for previews (not for game export)."""
    base = Image.new("RGBA", img.size, matte)
    base.alpha_composite(img)
    return base
