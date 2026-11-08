#!/usr/bin/env python3
"""Sample male_hero design sheet landmarks → ``ref_male_hero_landmarks.json``."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "pixel-art" / "_study" / "male_hero_ref" / "design" / "source_1x.png"
OUT = ROOT / "scripts" / "sparkpix" / "ref_male_hero_landmarks.json"


def main() -> int:
    sys.path.insert(0, str(ROOT / "scripts"))
    from sparkpix.platform_style import FOOT_Y, P128
    if not SRC.is_file():
        print(f"missing {SRC}", file=sys.stderr)
        return 1
    im = Image.open(SRC).convert("RGBA")
    w, h = im.size

    def pts_for(rgb: tuple[int, int, int]) -> list[tuple[int, int]]:
        return [
            (x, y)
            for y in range(h)
            for x in range(w)
            if im.getpixel((x, y))[3] and im.getpixel((x, y))[:3] == rgb
        ]

    iris = pts_for((0x59, 0xC1, 0x35))
    if not iris:
        print("no iris pixels", file=sys.stderr)
        return 1
    eye_x = sum(x for x, _ in iris) / len(iris)
    eye_y = sum(y for _, y in iris) / len(iris)

    opaque_ys = [
        y
        for y in range(h)
        for x in range(w)
        if im.getpixel((x, y))[3] and im.getpixel((x, y))[:3] != (0, 0, 0)
    ]
    foot_bottom = max(opaque_ys)

    hx, hy = P128.head
    # Design stamp origin (hair/face JSON); same row as reference extracts.
    face_anchor = [hx, int(round(eye_y)) - 1]
    data = {
        "source": "design/source_1x.png",
        "p128_head_joint": list(P128.head),
        "face_anchor": face_anchor,
        "face_y_adj": face_anchor[1] - hy,
        "face_rel_dy_source": "face_anchor[1] - p128_head_joint[1]",
        "eye_centroid": [round(eye_x, 2), round(eye_y, 2)],
        "foot_bottom_design": foot_bottom,
        "foot_y_p128": FOOT_Y,
        "foot_delta": FOOT_Y - foot_bottom,
        "neck": list(P128.neck),
        "shoulder": list(P128.shoulder),
    }
    OUT.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(data, indent=2))
    print(f"wrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
