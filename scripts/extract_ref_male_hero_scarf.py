#!/usr/bin/env python3
"""Rebuild ``ref_male_hero_scarf.json`` from male_hero reference strips (idle/walk/run)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
STUDY = ROOT / "pixel-art" / "_study" / "male_hero_ref"
OUT = ROOT / "scripts" / "sparkpix" / "ref_male_hero_scarf.json"

CLIP_FRAMES = {"idle": 10, "walk": 10, "run": 10}

SCARF_RGB: dict[tuple[int, int, int], int] = {
    (0x5C, 0x2C, 0x4F): 0,
    (0x8B, 0x10, 0x8F): 1,
    (0xCD, 0x30, 0x73): 2,
    (0xFF, 0xC5, 0xB4): 4,
    (0x70, 0x10, 0x70): 1,
    (0xCD, 0x30, 0x72): 2,
    (0x8B, 0x0F, 0x8F): 1,
    (0xD7, 0x7E, 0x86): 4,  # halo pixels on knot edge
}


def _is_scarf(rgb: tuple[int, int, int]) -> int | None:
    if rgb in SCARF_RGB:
        return SCARF_RGB[rgb]
    r, g, b = rgb
    if r > 95 and b > 75 and g < 95:
        return 2
    return None


def _merge_stamps(primary: list, extra: list) -> list:
    seen = {(s[0], s[1]) for s in primary}
    out = list(primary)
    for s in extra:
        key = (s[0], s[1])
        if key not in seen:
            out.append(s)
            seen.add(key)
    return out


def _prune_back(back: list, front: list) -> list:
    """Drop floater / foot islands; keep back tail connected to the neck knot (front stamps)."""
    if not back:
        return back
    seeds: set[tuple[int, int]] = set()
    for dx, dy, _ in front:
        for ox in range(-4, 5):
            for oy in range(-6, 7):
                seeds.add((dx + ox, dy + oy))
    cells = {(dx, dy): step for dx, dy, step in back}
    reachable: set[tuple[int, int]] = set()
    stack: list[tuple[int, int]] = []
    for p in cells:
        if p in seeds:
            stack.append(p)
    while stack:
        p = stack.pop()
        if p not in cells or p in reachable:
            continue
        reachable.add(p)
        x, y = p
        for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if (nx, ny) in cells and (nx, ny) not in reachable:
                stack.append((nx, ny))

    return [[dx, dy, cells[(dx, dy)]] for dx, dy in sorted(reachable) if -2 <= dy <= 14]


def _extract_cell(cell: Image.Image, anchor: tuple[int, int]) -> tuple[list, list]:
    ax, ay = anchor
    back: list[list[int]] = []
    front: list[list[int]] = []
    for y in range(cell.size[1]):
        for x in range(cell.size[0]):
            p = cell.getpixel((x, y))
            if p[3] == 0 or p[:3] == (0, 0, 0):
                continue
            step = _is_scarf(p[:3])
            if step is None:
                continue
            dx, dy = x - ax, y - ay
            stamp = [dx, dy, step]
            if x >= ax - 5 and x <= ax + 3 and ay - 2 <= y <= ay + 8:
                front.append(stamp)
            else:
                back.append(stamp)
    return back, front


def main() -> int:
    sys.path.insert(0, str(ROOT / "scripts"))
    from sparkpix.platform_style import P128

    anchor = list(P128.neck)
    clips: dict[str, list[dict]] = {}

    design = STUDY / "design" / "source_1x.png"

    for clip, n in CLIP_FRAMES.items():
        src = STUDY / clip / "source_1x.png"
        if not src.is_file():
            print(f"skip {clip}: missing {src}", file=sys.stderr)
            continue
        sheet = Image.open(src).convert("RGBA")
        fw = sheet.size[0] // n
        frames: list[dict] = []
        for i in range(n):
            cell = sheet.crop((i * fw, 0, (i + 1) * fw, sheet.size[1]))
            back, front = _extract_cell(cell, tuple(anchor))
            frames.append({"i": i, "back": back, "front": front})
        clips[clip] = frames
        print(f"{clip}: back stamps avg {sum(len(f['back']) for f in frames)//n} front {sum(len(f['front']) for f in frames)//n}")

    if not clips:
        print("no strip data extracted", file=sys.stderr)
        return 1

    payload = {"anchor": anchor, "clips": clips}
    OUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
