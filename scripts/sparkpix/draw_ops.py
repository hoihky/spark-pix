"""Low-level drawing helpers on a PIL image."""

from __future__ import annotations

from collections import deque
from typing import Callable, List, Optional, Sequence, Tuple

from PIL import Image

from sparkpix.color import RGBA, ColorLike, parse_color

MaskFn = Optional[Callable[[RGBA], bool]]


def _match_mask(px: RGBA, mask: MaskFn) -> bool:
    return mask is None or mask(px)


def set_px(img: Image.Image, x: int, y: int, color: RGBA, mask: MaskFn = None) -> None:
    w, h = img.size
    if x < 0 or y < 0 or x >= w or y >= h:
        return
    cur = img.getpixel((x, y))
    if not _match_mask(cur, mask):
        return
    img.putpixel((x, y), color)


def get_px(img: Image.Image, x: int, y: int) -> RGBA:
    return img.getpixel((x, y))


def line(
    img: Image.Image,
    x0: int,
    y0: int,
    x1: int,
    y1: int,
    color: RGBA,
    mask: MaskFn = None,
) -> None:
    dx = abs(x1 - x0)
    dy = -abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx + dy
    x, y = x0, y0
    while True:
        set_px(img, x, y, color, mask)
        if x == x1 and y == y1:
            break
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x += sx
        if e2 <= dx:
            err += dx
            y += sy


def rect(
    img: Image.Image,
    x0: int,
    y0: int,
    x1: int,
    y1: int,
    fill: Optional[RGBA] = None,
    outline: Optional[RGBA] = None,
    mask: MaskFn = None,
) -> None:
    if fill is not None:
        for y in range(min(y0, y1), max(y0, y1) + 1):
            for x in range(min(x0, x1), max(x0, x1) + 1):
                set_px(img, x, y, fill, mask)
    if outline is not None:
        xa, xb = min(x0, x1), max(x0, x1)
        ya, yb = min(y0, y1), max(y0, y1)
        for x in range(xa, xb + 1):
            set_px(img, x, ya, outline, mask)
            set_px(img, x, yb, outline, mask)
        for y in range(ya, yb + 1):
            set_px(img, xa, y, outline, mask)
            set_px(img, xb, y, outline, mask)


def circle(
    img: Image.Image,
    cx: int,
    cy: int,
    radius: int,
    fill: Optional[RGBA] = None,
    outline: Optional[RGBA] = None,
    mask: MaskFn = None,
) -> None:
    if radius < 0:
        return
    if fill is not None:
        for y in range(cy - radius, cy + radius + 1):
            for x in range(cx - radius, cx + radius + 1):
                if (x - cx) ** 2 + (y - cy) ** 2 <= radius ** 2:
                    set_px(img, x, y, fill, mask)
    if outline is not None and radius > 0:
        x = radius
        y = 0
        err = 0
        while x >= y:
            for ox, oy in (
                (cx + x, cy + y),
                (cx - x, cy + y),
                (cx + x, cy - y),
                (cx - x, cy - y),
                (cx + y, cy + x),
                (cx - y, cy + x),
                (cx + y, cy - x),
                (cx - y, cy - x),
            ):
                set_px(img, ox, oy, outline, mask)
            y += 1
            err += 1 + 2 * y
            if 2 * (err - x) + 1 > 0:
                x -= 1
                err += 1 - 2 * x


def ellipse(
    img: Image.Image,
    x0: int,
    y0: int,
    x1: int,
    y1: int,
    fill: Optional[RGBA] = None,
    mask: MaskFn = None,
) -> None:
    if fill is None:
        return
    xa, xb = min(x0, x1), max(x0, x1)
    ya, yb = min(y0, y1), max(y0, y1)
    cx = (xa + xb) / 2.0
    cy = (ya + yb) / 2.0
    rx = max(0.5, (xb - xa) / 2.0)
    ry = max(0.5, (yb - ya) / 2.0)
    for y in range(ya, yb + 1):
        for x in range(xa, xb + 1):
            nx = (x - cx) / rx
            ny = (y - cy) / ry
            if nx * nx + ny * ny <= 1.0:
                set_px(img, x, y, fill, mask)


def polygon(img: Image.Image, points: Sequence[Tuple[int, int]], fill: RGBA, mask: MaskFn = None) -> None:
    if len(points) < 3:
        return
    ys = [p[1] for p in points]
    y_min, y_max = min(ys), max(ys)
    pts = list(points)

    def inside(x: float, y: float) -> bool:
        inside_flag = False
        j = len(pts) - 1
        for i in range(len(pts)):
            xi, yi = pts[i]
            xj, yj = pts[j]
            if ((yi > y) != (yj > y)) and (x < (xj - xi) * (y - yi) / (yj - yi + 1e-9) + xi):
                inside_flag = not inside_flag
            j = i
        return inside_flag

    for y in range(y_min, y_max + 1):
        for x in range(img.size[0]):
            if inside(x + 0.5, y + 0.5):
                set_px(img, x, y, fill, mask)


def flood_fill(img: Image.Image, x: int, y: int, fill: RGBA, mask: MaskFn = None) -> None:
    w, h = img.size
    if x < 0 or y < 0 or x >= w or y >= h:
        return
    target = img.getpixel((x, y))
    if target == fill:
        return
    q: deque[Tuple[int, int]] = deque([(x, y)])
    seen = {(x, y)}
    while q:
        cx, cy = q.popleft()
        if not _match_mask(img.getpixel((cx, cy)), mask):
            continue
        if img.getpixel((cx, cy)) != target:
            continue
        img.putpixel((cx, cy), fill)
        for nx, ny in ((cx + 1, cy), (cx - 1, cy), (cx, cy + 1), (cx, cy - 1)):
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in seen:
                seen.add((nx, ny))
                q.append((nx, ny))


def outline_region(
    img: Image.Image,
    color: RGBA,
    where: str = "outside",
    mask: MaskFn = None,
) -> None:
    w, h = img.size
    neighbors = ((1, 0), (-1, 0), (0, 1), (0, -1))
    for y in range(h):
        for x in range(w):
            px = img.getpixel((x, y))
            alpha = px[3]
            is_opaque = alpha > 0
            touches_transparent = False
            touches_opaque = False
            for dx, dy in neighbors:
                nx, ny = x + dx, y + dy
                if nx < 0 or ny < 0 or nx >= w or ny >= h:
                    touches_transparent = True
                    continue
                npx = img.getpixel((nx, ny))
                if npx[3] == 0:
                    touches_transparent = True
                else:
                    touches_opaque = True
            if where == "outside" and is_opaque and touches_transparent:
                set_px(img, x, y, color, mask)
            elif where == "inside" and not is_opaque and touches_opaque:
                set_px(img, x, y, color, mask)


def build_mask(only: Optional[ColorLike], palette: Optional[Sequence[RGBA]]) -> MaskFn:
    if only is None:
        return None
    if only == "opaque":
        return lambda p: p[3] > 0
    if only == "empty":
        return lambda p: p[3] == 0
    target = parse_color(only, palette)
    if target is None:
        return None
    return lambda p: p == target


def dither_box(
    img: Image.Image,
    box: Tuple[int, int, int, int],
    c1: RGBA,
    c2: RGBA,
    mix_ratio: float,
    pattern: str = "checker",
) -> None:
    x0, y0, x1, y1 = box
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            if pattern == "checker":
                use_c2 = (x + y) % 2 == 0
            else:
                use_c2 = (x * 3 + y * 5) % 4 < int(mix_ratio * 4)
            img.putpixel((x, y), c2 if use_c2 else c1)


def replace_color(img: Image.Image, old: RGBA, new: RGBA) -> None:
    w, h = img.size
    for y in range(h):
        for x in range(w):
            if img.getpixel((x, y)) == old:
                img.putpixel((x, y), new)
