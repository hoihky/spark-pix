#!/usr/bin/env python3
"""Rebuild ``ref_male_hero_face.json`` from the male_hero design PNG (skin + eye stamps)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "pixel-art" / "_study" / "male_hero_ref" / "design" / "source_1x.png"
OUT = ROOT / "scripts" / "sparkpix" / "ref_male_hero_face.json"

def _face_anchor() -> tuple[int, int]:
    import sys
    from pathlib import Path

    root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(root / "scripts"))
    from sparkpix.platform_style import face_anchor_at_rest

    return face_anchor_at_rest()


FACE_ANCHOR = _face_anchor()
Y_MIN, Y_MAX = 53, 67

SKIN_RGB: dict[tuple[int, int, int], int] = {
    (0xC8, 0x90, 0x78): 0,
    (0xD2, 0x94, 0x7F): 1,
    (0xFF, 0xC5, 0xB4): 2,
    (0xD7, 0x7E, 0x86): 2,
}

EYE_KIND: dict[tuple[int, int, int], str] = {
    (0x59, 0xC1, 0x35): "iris",
    (0x24, 0x52, 0x3B): "pupil",
    (0xFF, 0xFF, 0xFF): "sclera",
    (0xB3, 0xB9, 0xD1): "sclera",  # design anti-alias around eye
}


def main() -> int:
    if not SRC.is_file():
        print(f"missing {SRC}", file=sys.stderr)
        return 1
    ref = Image.open(SRC).convert("RGBA")
    skin: list[list[int]] = []
    eye: list[list] = []
    for y in range(ref.size[1]):
        if y < Y_MIN or y > Y_MAX:
            continue
        for x in range(ref.size[0]):
            p = ref.getpixel((x, y))
            if p[3] == 0 or p[:3] == (0, 0, 0):
                continue
            rgb = p[:3]
            if rgb in SKIN_RGB:
                skin.append([x - FACE_ANCHOR[0], y - FACE_ANCHOR[1], SKIN_RGB[rgb]])
            elif rgb in EYE_KIND:
                eye.append([x - FACE_ANCHOR[0], y - FACE_ANCHOR[1], EYE_KIND[rgb]])
    payload = {"anchor": list(FACE_ANCHOR), "skin": skin, "eye": eye}
    OUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"wrote skin={len(skin)} eye={len(eye)} -> {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
