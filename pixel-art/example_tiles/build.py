#!/usr/bin/env python3
"""Production-style tileset sample: 16×16 grass + wall with Spark TSX gameplay props.

Extend with edge/corner kits per references/patterns.md for full terrain packs.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from sparkpix import Sprite, ramp, TilesetBuilder, TileProps  # noqa: E402

OUT = Path(__file__).resolve().parent / "out"
GRASS = ramp("#4a9f4a", 4)
STONE = ramp("#6a6a78", 4)


def make_grass_tile() -> Sprite:
    s = Sprite(16, 16, palette=GRASS)
    s.rect(0, 0, 15, 15, fill=GRASS[1])
    for x in range(0, 16, 4):
        s.px(x, 3, GRASS[3])
        s.px(x + 1, 7, GRASS[2])
    s.rect(0, 0, 15, 0, outline=GRASS[0])
    return s


def make_wall_tile() -> Sprite:
    s = Sprite(16, 16, palette=STONE)
    s.rect(0, 0, 15, 15, fill=STONE[1])
    for y in range(0, 16, 4):
        s.line(0, y, 15, y, STONE[0])
    for x in range(8, 16, 8):
        for y in range(0, 16, 8):
            s.rect(x - 1, y, x + 6, y + 3, fill=STONE[2])
    s.outline(STONE[0], where="outside")
    return s


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    ts = TilesetBuilder(16, 16, columns=4, name="spark_pix_demo", gameplay_id="spark_pix_demo")
    ts.add_tile(make_grass_tile().flatten_frame(0), TileProps(walkable=True))
    ts.add_tile(make_wall_tile().flatten_frame(0), TileProps(collision="full", blocks_pathfinding=True))
    ts.export_tiled(OUT)
    print(f"wrote {OUT}/tileset.png and tileset.tsx")


if __name__ == "__main__":
    main()
