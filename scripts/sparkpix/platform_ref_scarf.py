"""Reference-traced scarf stamps (male_hero strips) — palette-swappable."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Sequence

from sparkpix.canvas import Sprite
from sparkpix.color import ColorLike

ColorSeq = Sequence[ColorLike]

_TEMPLATE = Path(__file__).resolve().parent / "ref_male_hero_scarf.json"


@lru_cache(maxsize=1)
def _bundle() -> dict:
    if not _TEMPLATE.is_file():
        return {}
    return json.loads(_TEMPLATE.read_text(encoding="utf-8"))


def scarf_stamp_clip(bundle: dict, clip: str, frame_i: int) -> dict | None:
    clips = bundle.get("clips", {})
    frames = clips.get(clip)
    if not frames:
        return None
    idx = frame_i % len(frames)
    return frames[idx]


def _bridge_scarf_tail(
    s: Sprite,
    nx: int,
    ny: int,
    layer: list,
    scarf: ColorSeq,
    *,
    foot_floor_y: int | None,
    tip_world_x: int | None = None,
) -> None:
    """Solid limb from the hooked tail down to ``foot_floor_y`` (stamps leave a y-gap in ref)."""
    if not layer or foot_floor_y is None:
        return
    hook = [(dx, dy) for dx, dy, _ in layer if dx <= 3 and dy <= 14]
    if not hook:
        return
    y_top = max(dy for _, dy in hook)
    y_stop_rel = foot_floor_y - ny
    if tip_world_x is not None:
        x_end_w = int(tip_world_x)
    else:
        left = [dx for dx, dy, _ in layer if dy >= y_top - 3 and dx < 0]
        x_end_w = nx + (min(left) if left else min(dx for dx, _, _ in layer))
    if y_stop_rel <= y_top + 1:
        return
    hang = [(dx, dy) for dx, dy in hook if dy >= y_top - 3]
    x_top = min(dx for dx, _ in hang) if hang else min(dx for dx, _ in hook)
    y0 = min(ny + y_top, foot_floor_y)
    y1 = min(ny + y_stop_rel, foot_floor_y)
    if y1 <= y0:
        return
    dark, mid, light = scarf[0], scarf[1], scarf[2] if len(scarf) > 2 else scarf[1]
    x_attach = nx + min(dx for dx, _ in hang)
    x_attach_end = nx + max(dx for dx, _ in hang)
    span = max(4, x_attach_end - x_attach + 1)
    for y in range(y0, y1 + 1):
        t = (y - y0) / max(1, y1 - y0)
        xc = int(x_attach + (x_end_w - x_attach) * t)
        if t >= 0.92:
            xc = x_end_w
        half = max(1, 2 if t >= 0.9 else max(1, span // 2 - int(t * 2)))
        s.rect(xc - half, y, xc + 1, y, fill=mid)
        s.px(xc - half, y, dark)
        s.px(xc + 1, y, light, only="opaque")


def draw_ref_male_hero_scarf(
    s: Sprite,
    nx: int,
    ny: int,
    scarf: ColorSeq,
    *,
    clip: str = "idle",
    frame_i: int = 0,
    behind: bool,
    foot_floor_y: int | None = None,
    tip_world_x: int | None = None,
) -> bool:
    """
    Stamp scarf from ``ref_male_hero_scarf.json``. Returns False if clip missing (use procedural).
    """
    bundle = _bundle()
    if not bundle:
        return False
    frame = scarf_stamp_clip(bundle, clip, frame_i)
    if not frame:
        return False
    layer = frame["back"] if behind else frame["front"]
    if not layer:
        return False
    for dx, dy, step in layer:
        y = ny + dy
        if foot_floor_y is not None and y > foot_floor_y:
            continue
        idx = max(0, min(int(step), len(scarf) - 1))
        s.px(nx + dx, y, scarf[idx])
    if behind:
        _solidify_back_stamps(s, nx, ny, layer, scarf, foot_floor_y=foot_floor_y)
    return True


def _solidify_back_stamps(
    s: Sprite,
    nx: int,
    ny: int,
    layer: list,
    scarf: ColorSeq,
    *,
    foot_floor_y: int | None,
) -> None:
    """One step of horizontal fill on each tail row so 1× stamps read as a solid ribbon."""
    from collections import defaultdict

    rows: dict[int, list[int]] = defaultdict(list)
    steps: dict[tuple[int, int], int] = {}
    for dx, dy, step in layer:
        rows[dy].append(dx)
        steps[(dx, dy)] = int(step)
    mid = scarf[1] if len(scarf) > 1 else scarf[0]
    for dy, xs in rows.items():
        if dy < -3:
            continue
        y = ny + dy
        if foot_floor_y is not None and y > foot_floor_y:
            continue
        if len(xs) < 2:
            continue
        x0, x1 = min(xs), max(xs)
        if x1 - x0 < 2:
            continue
        for x in range(x0, x1 + 1):
            st = steps.get((x, dy))
            fill = scarf[max(0, min(st, len(scarf) - 1))] if st is not None else mid
            s.px(nx + x, y, fill)
    ordered = sorted(rows)
    for i in range(len(ordered) - 1):
        dy0, dy1 = ordered[i], ordered[i + 1]
        if dy1 != dy0 + 1 or dy0 < -2:
            continue
        y0, y1 = ny + dy0, ny + dy1
        if foot_floor_y is not None and y1 > foot_floor_y:
            continue
        for x in set(rows[dy0]) | set(rows[dy1]):
            if (x, dy0) in steps and (x, dy1) in steps:
                continue
            has_above = x in rows[dy0] or (x - 1) in rows[dy0] or (x + 1) in rows[dy0]
            has_below = x in rows[dy1] or (x - 1) in rows[dy1] or (x + 1) in rows[dy1]
            if has_above and has_below:
                st = steps.get((x, dy0)) or steps.get((x, dy1))
                fill = scarf[max(0, min(st, len(scarf) - 1))] if st is not None else mid
                s.px(nx + x, y1 if (x, dy1) not in steps else y0, fill)
    for dx, dy, step in layer:
        y = ny + dy
        if foot_floor_y is not None and y > foot_floor_y:
            continue
        idx = max(0, min(int(step), len(scarf) - 1))
        col = scarf[idx]
        s.px(nx + dx, y, col)
        for ox, oy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            sx, sy = nx + dx + ox, y + oy
            if foot_floor_y is not None and sy > foot_floor_y:
                continue
            if s.get(sx, sy)[3] == 0:
                s.px(sx, sy, scarf[1])
