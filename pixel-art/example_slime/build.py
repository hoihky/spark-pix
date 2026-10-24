#!/usr/bin/env python3
"""Example: idle + walk slime for Spark uniform-grid atlas."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from sparkpix import Sprite, ramp  # noqa: E402
from sparkpix.game_palette import GRASS, INK, PAPER  # noqa: E402

OUT = Path(__file__).resolve().parent / "out"
BODY = GRASS
EYE = PAPER


def draw_slime(s: Sprite, squash: int = 0, eye_shift: int = 0) -> None:
    s.clear()
    y = 5 + squash
    s.ellipse(3, y + 2, 12, 14, fill=BODY[0])
    s.ellipse(3, y, 12, 13, fill=BODY[2], only="opaque")
    s.ellipse(5, y + 1, 10, 9, fill=BODY[4], only="opaque")
    s.px(6 + eye_shift, y + 4, INK)
    s.px(9 + eye_shift, y + 4, INK)
    s.px(7, y + 5, EYE)
    s.px(8, y + 5, EYE)
    s.outline(BODY[0], where="outside")


def main() -> None:
    s = Sprite(16, 16, palette=BODY + [INK, EYE])
    draw_slime(s, squash=0)
    s.add_frame(copy=True)
    draw_slime(s, squash=1, eye_shift=0)
    s.frame(0)
    s.add_frame(copy=True)
    draw_slime(s, squash=0, eye_shift=-1)
    s.add_frame(copy=True)
    draw_slime(s, squash=1, eye_shift=0)
    s.add_frame(copy=True)
    draw_slime(s, squash=0, eye_shift=1)

    OUT.mkdir(parents=True, exist_ok=True)
    s.preview(OUT / "preview.png", scale=10)
    s.save_gif(OUT / "slime.gif", scale=8)
    s.tag_clip("idle", 0, 0, fps=2.0, loop=True)
    s.tag_clip("walk", 1, 3, fps=8.0, loop=True)
    s.save_spritesheet(OUT / "slime", columns=4)
    print(s.stats())
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
