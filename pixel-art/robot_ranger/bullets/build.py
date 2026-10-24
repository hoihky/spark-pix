#!/usr/bin/env python3
"""Energy bolts for robot_ranger — static + short animated spark."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))

from sparkpix import Sprite, ramp  # noqa: E402

OUT = Path(__file__).resolve().parent / "out"
CORE = ramp("#fff8d0", 3)
BOLT = ramp("#58e8ff", 4)
TRAIL = ramp("#3088c8", 3)
INK = "#101820"

PALETTE = [INK] + CORE + BOLT + TRAIL


def draw_bolt(s: Sprite, core_shift: int = 0, trail_len: int = 4) -> None:
    s.clear()
    cx, cy = 8, 8
    # elongated plasma bolt (motion along +X)
    for i in range(trail_len):
        x = cx - 2 + i
        col = TRAIL[min(i, 2)] if i < trail_len - 1 else BOLT[2]
        s.rect(x, cy - 1, x + 1, cy + 1, fill=col)
    s.rect(cx + core_shift, cy - 2, cx + core_shift + 3, cy + 2, fill=BOLT[3])
    s.rect(cx + core_shift + 1, cy - 1, cx + core_shift + 2, cy + 1, fill=CORE[2])
    s.px(cx + core_shift + 2, cy, CORE[2])


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)

    # Single frame — use for pooled projectiles in Spark
    single = Sprite(16, 16, palette=PALETTE)
    draw_bolt(single, 0, 5)
    single.preview(OUT / "bolt_preview.png", scale=8)
    single.save_png(OUT / "bolt.png", scale=1)

    # 3-frame loop for optional animated projectile
    anim = Sprite(16, 16, palette=PALETTE)
    for i, (shift, trail) in enumerate([(0, 4), (1, 5), (0, 6)]):
        if i > 0:
            anim.add_frame(copy=False)
        draw_bolt(anim, shift, trail)
    anim.tag_clip("fly", 0, 2, fps=16.0, loop=True)
    anim.save_gif(OUT / "bolt_anim.gif", scale=8)
    anim.save_spritesheet(OUT / "bolt_anim", columns=3, padding=0)

    # Spark manifest for uniform grid (optional animated bullet)
    manifest = {
        "format": "spark-sprite-atlas-v1",
        "texture": "bolt_anim.png",
        "columns": 3,
        "rows": 1,
        "frameWidth": 16,
        "frameHeight": 16,
        "nearestFilter": True,
        "clips": [{"name": "fly", "firstFrame": 0, "frameCount": 3, "framesPerSecond": 16.0, "loop": True}],
        "notes": "For static bullets use bolt.png + full UV. Animated: SpriteAnimator clip 'fly'.",
    }
    import json

    (OUT / "bolt_anim.spark-atlas.json").write_text(json.dumps(manifest, indent=2) + "\n")
    (OUT / "bolt.spark-meta.json").write_text(
        json.dumps(
            {
                "format": "spark-static-sprite-v1",
                "texture": "bolt.png",
                "size": [16, 16],
                "pivot": [0.25, 0.5],
                "notes": "Pivot near rear of trail; spawn at muzzle facing +X.",
            },
            indent=2,
        )
        + "\n"
    )
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
