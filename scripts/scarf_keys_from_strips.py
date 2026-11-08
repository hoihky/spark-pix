#!/usr/bin/env python3
"""Extract per-frame scarf keys from male_hero reference strips (all clips)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

# ``filename`` is only used under ``SPARK_PIX_REF_ASSETS`` / ``_ref_assets``; strips in
# ``pixel-art/_study/male_hero_ref/<clip>/source_1x.png`` are resolved automatically.
CLIP_TABLE: dict[str, tuple[int, str]] = {
    "idle": (10, "idle_strip.png"),
    "walk": (10, "walk_strip.png"),
    "run": (10, "run_strip.png"),
    "jump": (6, "jump_strip.png"),
    "fall": (4, "fall_strip.png"),
    "fall_loop": (3, "fall_loop_strip.png"),
    "combo_1": (3, "combo_1_strip.png"),
    "combo_1_end": (4, "combo_1_end_strip.png"),
}


def _is_scarf(rgb: tuple[int, int, int]) -> bool:
    r, g, b = rgb
    known = {
        (0x8B, 0x10, 0x8F),
        (0xCD, 0x30, 0x73),
        (0x5C, 0x2C, 0x4F),
        (0x70, 0x10, 0x70),
    }
    if rgb in known:
        return True
    return r > 95 and b > 75 and g < 95


def analyze_strip(strip_path: Path, *, frames: int = 10) -> dict:
    from PIL import Image

    sheet = Image.open(strip_path).convert("RGBA")
    w, h = sheet.size
    frame_w = w // frames
    keys: list[dict] = []
    tips: list[int] = []
    tops: list[int] = []

    for i in range(frames):
        cell = sheet.crop((i * frame_w, 0, (i + 1) * frame_w, h))
        scarf_pts: list[tuple[int, int]] = []
        top = h
        for y in range(h):
            row_hit = False
            for x in range(frame_w):
                p = cell.getpixel((x, y))
                if p[3] == 0 or p[:3] == (0, 0, 0):
                    continue
                row_hit = True
                if _is_scarf(p[:3]):
                    scarf_pts.append((x, y))
            if row_hit:
                top = min(top, y)

        tops.append(top)
        if not scarf_pts:
            keys.append(
                {
                    "i": i,
                    "phase_hint": i / max(1, frames - 1),
                    "wave": 0,
                    "lift": 0,
                    "dy": 0,
                    "tip_dx": -14,
                    "tip_dy": -2,
                }
            )
            continue

        xs = [p[0] for p in scarf_pts]
        ys = [p[1] for p in scarf_pts]
        tip_x = min(xs)
        attach_x = max(xs)
        tips.append(tip_x)
        attach_pts = [(x, y) for x, y in scarf_pts if x >= attach_x - 2]
        attach_y = int(round(sum(y for _, y in attach_pts) / max(1, len(attach_pts))))
        tail_pts = [(x, y) for x, y in scarf_pts if x <= tip_x + 3]
        tip_y = int(round(sum(y for _, y in tail_pts) / max(1, len(tail_pts))))
        cy = sum(ys) / len(ys)

        keys.append(
            {
                "i": i,
                "tip_x": tip_x,
                "attach_x": attach_x,
                "tip_dx": int(tip_x - attach_x),
                "tip_dy": int(tip_y - attach_y),
                "centroid_y": round(cy, 2),
                "phase_hint": 0.0,
                "wave": 0,
                "lift": 0,
            }
        )

    if tips:
        lo, hi = min(tips), max(tips)
        cy_mean = sum(k.get("centroid_y", 50) for k in keys if "centroid_y" in k) / max(1, len(tips))
        for k in keys:
            if "tip_x" not in k:
                continue
            k["phase_hint"] = round((k["tip_x"] - lo) / max(1, hi - lo), 3)
            k["wave"] = int(round((lo + hi) / 2 - k["tip_x"]))
            k["lift"] = int(round(cy_mean - k["centroid_y"]))

    base_top = sum(tops) / len(tops)
    for i, k in enumerate(keys):
        k["dy"] = int(round(tops[i] - base_top))

    return {
        "source": strip_path.name,
        "frame_w": frame_w,
        "frames": frames,
        "tip_range": [min(tips), max(tips)] if tips else [],
        "keys": keys,
    }


def default_assets_root() -> Path:
    """Optional local strips: ``SPARK_PIX_REF_ASSETS`` or ``pixel-art/_ref_assets``."""
    import os

    root = Path(__file__).resolve().parents[1]
    env = os.environ.get("SPARK_PIX_REF_ASSETS", "").strip()
    if env:
        p = Path(env).expanduser()
        if p.is_dir():
            return p
    repo_assets = root / "pixel-art" / "_ref_assets"
    if repo_assets.is_dir():
        return repo_assets
    return repo_assets


def resolve_strip(root: Path, assets: Path, clip: str, filename: str) -> Path | None:
    direct = assets / filename
    if direct.is_file():
        return direct
    study = root / "pixel-art" / "_study" / "male_hero_ref" / clip / "source_1x.png"
    if study.is_file():
        return study
    return None


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    assets = default_assets_root()
    bundle: dict = {"clips": {}}
    for clip, (frames, filename) in CLIP_TABLE.items():
        path = resolve_strip(root, assets, clip, filename)
        if path is None:
            print(f"skip {clip}: missing strip", file=sys.stderr)
            continue
        bundle["clips"][clip] = analyze_strip(path, frames=frames)

    if "idle" in bundle["clips"]:
        idle_keys = bundle["clips"]["idle"]["keys"]
        for clip, (frames, _) in CLIP_TABLE.items():
            if clip in bundle["clips"]:
                continue
            bundle["clips"][clip] = {
                "source": "synthetic_from_idle",
                "frame_w": bundle["clips"]["idle"].get("frame_w", 128),
                "frames": frames,
                "tip_range": bundle["clips"]["idle"].get("tip_range", [0, 0]),
                "keys": [idle_keys[i % len(idle_keys)] for i in range(frames)],
            }

    out = root / "pixel-art/male_hero/scarf_keys.json"
    if out.is_file():
        try:
            prev = json.loads(out.read_text(encoding="utf-8"))
            for clip_name, data in prev.get("clips", {}).items():
                bundle["clips"].setdefault(clip_name, data)
        except json.JSONDecodeError:
            pass
    out.write_text(json.dumps(bundle, indent=2) + "\n", encoding="utf-8")
    summary = {
        k: {"frames": v.get("frames"), "frame_w": v.get("frame_w"), "tip_range": v.get("tip_range")}
        for k, v in bundle["clips"].items()
    }
    print(json.dumps(summary, indent=2))
    print("wrote", out)
    return 0 if bundle["clips"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
