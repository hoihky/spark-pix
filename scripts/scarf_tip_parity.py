#!/usr/bin/env python3
"""Report scarf tip X error per frame vs reference strips (idle/walk/run)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

# Reuse detector from scarf_keys_from_strips
sys.path.insert(0, str(Path(__file__).resolve().parent))
from scarf_keys_from_strips import _is_scarf, analyze_strip  # noqa: E402


def _tip_x(img, frame_w: int, i: int) -> int | None:
    cell = img.crop((i * frame_w, 0, (i + 1) * frame_w, img.size[1]))
    xs = []
    cut = int(frame_w * 0.55)
    for y in range(cell.size[1]):
        for x in range(cut):
            p = cell.getpixel((x, y))
            if p[3] and p[:3] != (0, 0, 0) and _is_scarf(p[:3]):
                xs.append(x)
    return min(xs) if xs else None


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    out = root / "pixel-art/male_hero/out"
    study = root / "pixel-art/_study/male_hero_ref"
    bundle_path = root / "pixel-art/male_hero/scarf_keys.json"
    bundle = json.loads(bundle_path.read_text(encoding="utf-8"))

    from PIL import Image

    gen_strips = {
        "idle": out / "idle_strip_art.png",
        "walk": out / "walk_strip_art.png",
        "run": out / "run_strip_art.png",
    }
    ref_strips = {
        "idle": study / "idle/source_1x.png",
        "walk": study / "walk/source_1x.png",
        "run": study / "run/source_1x.png",
    }

    report: dict = {}
    for clip in ("idle", "walk", "run"):
        ref_path = ref_strips[clip]
        gen_path = gen_strips[clip]
        if not ref_path.is_file() or not gen_path.is_file():
            continue
        ref = Image.open(ref_path).convert("RGBA")
        gen = Image.open(gen_path).convert("RGBA")
        fw = ref.size[0] // 10
        # gen strip is 4x scale
        gen_fw = gen.size[0] // 10
        errs = []
        for i in range(10):
            ref_tip = _tip_x(ref, fw, i)
            gen_tip = _tip_x(gen, gen_fw, i)
            if ref_tip is None or gen_tip is None:
                errs.append({"i": i, "err": None})
                continue
            # compare in 1x space
            gen_tip_1x = gen_tip // 4
            errs.append({"i": i, "ref": ref_tip, "gen": gen_tip_1x, "err": gen_tip_1x - ref_tip})
        abs_err = [abs(e["err"]) for e in errs if e.get("err") is not None]
        report[clip] = {
            "frames": errs,
            "mean_abs_err": round(sum(abs_err) / max(1, len(abs_err)), 2),
            "max_abs_err": max(abs_err) if abs_err else None,
        }

    sidecar = out / "scarf_tip_parity.json"
    sidecar.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    ok = all(report[c]["max_abs_err"] is not None and report[c]["max_abs_err"] <= 2 for c in report)
    return 0 if ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
