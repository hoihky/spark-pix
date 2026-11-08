"""Production shading and finish passes (upper-left light, ramp discipline)."""

from __future__ import annotations

from collections import Counter
from typing import Iterable, Sequence, Tuple

from PIL import Image

from sparkpix.canvas import Sprite
from sparkpix.color import ColorLike, RGBA, parse_color
from sparkpix import draw_ops

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


def _rgb_key(px: RGBA) -> tuple[int, int, int]:
    return px[0], px[1], px[2]


def _lit_edge_skip(img: Image.Image, x: int, y: int, w: int, h: int) -> bool:
    """Skip outline on upper-left lit silhouette (techniques.md)."""

    def trans(px: int, py: int) -> bool:
        if px < 0 or py < 0 or px >= w or py >= h:
            return True
        return img.getpixel((px, py))[3] == 0

    lit = trans(x, y - 1) or trans(x - 1, y) or trans(x - 1, y - 1)
    shadow_side = trans(x, y + 1) or trans(x + 1, y)
    return lit and not shadow_side


def selective_outside_outline(
    s: Sprite,
    buckets: Sequence[tuple[Sequence[ColorLike], ColorLike]],
    *,
    fallback: ColorLike,
    skip_lit_edge: bool = True,
) -> None:
    """
    Hull outline with same-hue dark inks per material group (not one global rim).
    ``buckets``: ``(fill_colors, outline_ink)`` — fill may be hex strings.
    """
    img = s._img()
    w, h = img.size
    pal = s.palette
    ink_map: dict[tuple[int, int, int], RGBA] = {}
    for fills, ink in buckets:
        out = parse_color(ink, pal)
        if out is None:
            continue
        for f in fills:
            c = parse_color(f, pal)
            if c is not None:
                ink_map[_rgb_key(c)] = out

    fallback_rgba = parse_color(fallback, pal)
    if fallback_rgba is None:
        return

    neighbors = ((1, 0), (-1, 0), (0, 1), (0, -1))
    for y in range(h):
        for x in range(w):
            px = img.getpixel((x, y))
            if px[3] == 0:
                continue
            touches_t = any(
                x + dx < 0 or y + dy < 0 or x + dx >= w or y + dy >= h or img.getpixel((x + dx, y + dy))[3] == 0
                for dx, dy in neighbors
            )
            if not touches_t:
                continue
            if skip_lit_edge and _lit_edge_skip(img, x, y, w, h):
                continue
            interior: Counter = Counter()
            for dx, dy in neighbors:
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h:
                    npx = img.getpixel((nx, ny))
                    if npx[3] > 0:
                        interior[_rgb_key(npx)] += 1
            if not interior:
                draw_ops.set_px(img, x, y, fallback_rgba)
                continue
            fill_rgb, _ = interior.most_common(1)[0]
            ink = ink_map.get(fill_rgb, fallback_rgba)
            draw_ops.set_px(img, x, y, ink)


def finish_production_selective(
    s: Sprite,
    buckets: Sequence[tuple[Sequence[ColorLike], ColorLike]],
    *,
    fallback: ColorLike,
    trim_specks: bool = True,
) -> None:
    if trim_specks:
        s.trim_isolated_specks(min_neighbors=0)
    selective_outside_outline(s, buckets, fallback=fallback)
    if trim_specks:
        s.trim_isolated_specks(min_neighbors=0)


def matte_composite(img: Image.Image, matte: RGBA = (52, 56, 72, 255)) -> Image.Image:
    """Review background for previews (not for game export)."""
    base = Image.new("RGBA", img.size, matte)
    base.alpha_composite(img)
    return base
