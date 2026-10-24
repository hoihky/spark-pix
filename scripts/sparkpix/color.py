"""Color parsing, ramps, and preset palettes."""

from __future__ import annotations

import colorsys
import re
from typing import Iterable, List, Optional, Sequence, Tuple, Union

RGBA = Tuple[int, int, int, int]
ColorLike = Union[str, Tuple[int, ...], int, None]

_HEX_RE = re.compile(r"^#([0-9a-fA-F]{3}|[0-9a-fA-F]{4}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})$")


def parse_color(value: ColorLike, palette: Optional[Sequence[RGBA]] = None) -> Optional[RGBA]:
    if value is None:
        return None
    if isinstance(value, int):
        if palette is None or value < 0 or value >= len(palette):
            raise ValueError(f"palette index out of range: {value}")
        return tuple(palette[value])
    if isinstance(value, str):
        m = _HEX_RE.match(value.strip())
        if not m:
            raise ValueError(f"invalid hex color: {value}")
        h = m.group(1)
        if len(h) == 3:
            r, g, b = (int(c * 2, 16) for c in h)
            return r, g, b, 255
        if len(h) == 4:
            r, g, b, a = (int(c * 2, 16) for c in h)
            return r, g, b, a
        if len(h) == 6:
            r = int(h[0:2], 16)
            g = int(h[2:4], 16)
            b = int(h[4:6], 16)
            return r, g, b, 255
        r = int(h[0:2], 16)
        g = int(h[2:4], 16)
        b = int(h[4:6], 16)
        a = int(h[6:8], 16)
        return r, g, b, a
    if len(value) == 3:
        return int(value[0]), int(value[1]), int(value[2]), 255
    if len(value) == 4:
        return int(value[0]), int(value[1]), int(value[2]), int(value[3])
    raise ValueError(f"unsupported color: {value!r}")


def mix(c1: ColorLike, c2: ColorLike, t: float, palette: Optional[Sequence[RGBA]] = None) -> RGBA:
    a = parse_color(c1, palette)
    b = parse_color(c2, palette)
    if a is None or b is None:
        raise ValueError("mix requires two opaque colors")
    t = max(0.0, min(1.0, t))
    return (
        int(a[0] + (b[0] - a[0]) * t),
        int(a[1] + (b[1] - a[1]) * t),
        int(a[2] + (b[2] - a[2]) * t),
        int(a[3] + (b[3] - a[3]) * t),
    )


def ramp(base: str, steps: int = 5, hue_shift: float = 0.08) -> List[RGBA]:
    """Build a shading ramp from a base hex color (darkest → lightest)."""
    if steps < 2:
        raise ValueError("steps must be >= 2")
    c = parse_color(base)
    if c is None:
        raise ValueError("base color required")
    r, g, b, _ = (x / 255.0 for x in c)
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    out: List[RGBA] = []
    for i in range(steps):
        t = i / (steps - 1)
        li = 0.12 + 0.78 * t
        hi = h + hue_shift * (t - 0.5)
        hi %= 1.0
        si = min(1.0, s * (0.85 + 0.3 * (1.0 - t)))
        rr, gg, bb = colorsys.hls_to_rgb(hi, li, si)
        out.append((int(rr * 255), int(gg * 255), int(bb * 255), 255))
    return out


PALETTES: dict[str, List[RGBA]] = {
    "spark_neutral": [
        (26, 28, 44, 255),
        (62, 68, 90, 255),
        (120, 128, 144, 255),
        (200, 208, 220, 255),
        (244, 244, 244, 255),
    ],
    "spark_forest": ramp("#3d8c40", 6) + [(26, 28, 44, 255), (244, 244, 244, 255)],
    "spark_dungeon": ramp("#6b4fa0", 4) + ramp("#c45c3e", 4) + [(26, 28, 44, 255)],
    "spark_sky": ramp("#4fa4d8", 5) + [(255, 248, 220, 255), (26, 28, 44, 255)],
}


def nearest_palette_index(color: RGBA, palette: Sequence[RGBA]) -> int:
    best = 0
    best_d = 1 << 30
    for i, p in enumerate(palette):
        d = sum((color[c] - p[c]) ** 2 for c in range(4))
        if d < best_d:
            best_d = d
            best = i
    return best


def map_to_palette(colors: Iterable[RGBA], palette: Sequence[RGBA]) -> List[RGBA]:
    return [palette[nearest_palette_index(c, palette)] for c in colors]
