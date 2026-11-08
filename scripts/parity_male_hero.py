#!/usr/bin/env python3
"""Compare male_hero frame 0 bbox/palette to design reference study."""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from sparkpix.platform_parity import run_male_hero_idle_regions  # noqa: E402


def _bbox(img: Image.Image, *, skip_black: bool = True) -> tuple | None:
    w, h = img.size
    xs, ys, x2, y2 = w, h, 0, 0
    n = 0
    for y in range(h):
        for x in range(w):
            p = img.getpixel((x, y))
            if p[3] == 0:
                continue
            if skip_black and p[:3] == (0, 0, 0):
                continue
            n += 1
            xs = min(xs, x)
            ys = min(ys, y)
            x2 = max(x2, x)
            y2 = max(y2, y)
    if n == 0:
        return None
    return xs, ys, x2, y2, x2 - xs + 1, y2 - ys + 1, n


def main() -> int:
    out = ROOT / "pixel-art" / "male_hero" / "out"
    ref = ROOT / "pixel-art" / "_study" / "male_hero_ref" / "design" / "source_1x.png"
    gen_path = out / "frame0_art.png"
    if not ref.is_file() or not gen_path.is_file():
        print("missing ref or frame0_art.png (run male_hero build)", file=sys.stderr)
        return 1

    ref_i = Image.open(ref).convert("RGBA")
    gen_i = Image.open(gen_path).convert("RGBA")
    rb = _bbox(ref_i)
    gb = _bbox(gen_i)
    report = {"ref_bbox": rb, "gen_bbox": gb}
    if rb and gb:
        report["foot_delta_y"] = gb[3] - rb[3]
        report["center_delta_x"] = (gb[0] + gb[4] // 2) - (rb[0] + rb[4] // 2)

    ref_colors = {f"#{r:02x}{g:02x}{b:02x}" for (r, g, b, a) in ref_i.getdata() if a and (r, g, b) != (0, 0, 0)}
    gen_colors = {f"#{r:02x}{g:02x}{b:02x}" for (r, g, b, a) in gen_i.getdata() if a and (r, g, b) != (0, 0, 0)}
    report["ref_color_count"] = len(ref_colors)
    report["gen_color_count"] = len(gen_colors)
    report["overlap_hex"] = len(ref_colors & gen_colors)
    report["missing_from_gen"] = sorted(ref_colors - gen_colors)[:12]

    region_report = run_male_hero_idle_regions(ref_i, gen_i)
    report["regions"] = region_report["regions"]
    report["regions_ok"] = region_report["regions_ok"]

    sidecar = out / "parity_report.json"
    sidecar.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))

    # composite preview
    canvas = Image.new("RGBA", (128 * 2 + 8, 128), (52, 56, 72, 255))
    canvas.paste(ref_i, (0, 0))
    canvas.paste(gen_i, (136, 0))
    canvas.save(out / "parity_ref_vs_gen.png")

    coarse = rb and gb and abs(report.get("foot_delta_y", 99)) <= 3 and report["overlap_hex"] >= 8
    ok = coarse and report["regions_ok"]
    if not report["regions_ok"]:
        failed = [r["name"] for r in report["regions"] if not r["ok"]]
        print(f"region parity failed: {', '.join(failed)}", file=sys.stderr)
    return 0 if ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
