#!/usr/bin/env python3
"""Rebuild ``ref_male_hero_hair.json`` from the male_hero design PNG."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
SRC = ROOT / "pixel-art" / "_study" / "male_hero_ref" / "design" / "source_1x.png"
OUT = ROOT / "scripts" / "sparkpix" / "ref_male_hero_hair.json"

HAIR_RGB = {
    (0x4C, 0x26, 0x41): 0,
    (0x5C, 0x2C, 0x4F): 1,
    (0x7D, 0x55, 0x56): 2,
    (0xA2, 0x4E, 0x57): 3,
    (0xD7, 0x7E, 0x86): 4,
}
# Stamp origin = design facial landmark (``P128.face`` / ``ref_male_hero_landmarks.json``).
def _face_anchor() -> tuple[int, int]:
    from sparkpix.platform_style import face_anchor_at_rest

    return face_anchor_at_rest()


ANCHOR = _face_anchor()
MAX_Y = 70  # exclude scarf/boot pixels that reuse hair ramp colors


def main() -> int:
    if not SRC.is_file():
        print(f"missing {SRC}", file=sys.stderr)
        return 1
    ref = Image.open(SRC).convert("RGBA")
    stamps: list[list[int]] = []
    for y in range(ref.size[1]):
        if y > MAX_Y:
            continue
        for x in range(ref.size[0]):
            p = ref.getpixel((x, y))
            if p[3] == 0 or p[:3] == (0, 0, 0):
                continue
            step = HAIR_RGB.get(p[:3])
            if step is None:
                continue
            stamps.append([x - ANCHOR[0], y - ANCHOR[1], step])
    OUT.write_text(
        json.dumps({"anchor": list(ANCHOR), "stamps": stamps}, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"wrote {len(stamps)} stamps -> {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
