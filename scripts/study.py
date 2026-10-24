#!/usr/bin/env python3
"""Analyze a reference PNG and emit a small study report for the agent."""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

from PIL import Image

from sparkpix.export import save_png, scale_nearest


def analyze(path: Path, out_dir: Path) -> dict:
    img = Image.open(path).convert("RGBA")
    w, h = img.size
    colors = [p for p in img.getdata() if p[3] > 0]
    counts = Counter(colors)
    palette = [c for c, _ in counts.most_common(32)]
    report = {
        "source": path.name,
        "size": [w, h],
        "opaque_pixels": len(colors),
        "unique_colors": len(counts),
        "top_colors_hex": [f"#{r:02x}{g:02x}{b:02x}" for r, g, b, a in palette[:16]],
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    save_png(img, out_dir / "source_1x.png", scale=1)
    save_png(img, out_dir / "preview_8x.png", scale=8)
    # swatch strip
    sw = Image.new("RGBA", (len(palette) * 8, 8), (0, 0, 0, 0))
    for i, c in enumerate(palette):
        for x in range(8):
            for y in range(8):
                sw.putpixel((i * 8 + x, y), c)
    sw.save(out_dir / "swatch.png")
    (out_dir / "report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report


def main(argv: list[str]) -> int:
    if len(argv) < 3:
        print("usage: study.py <input.png> <out-study-dir>", file=sys.stderr)
        return 2
    path = Path(argv[1])
    out = Path(argv[2])
    if not path.is_file():
        print(f"missing file: {path}", file=sys.stderr)
        return 2
    report = analyze(path, out)
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
