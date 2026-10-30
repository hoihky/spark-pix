#!/usr/bin/env python3
"""Analyze a reference PNG or GIF and emit a study report for the agent."""

from __future__ import annotations

import json
import math
import sys
from collections import Counter
from pathlib import Path

from PIL import Image

from sparkpix.export import save_png, scale_nearest


def _color_report(img: Image.Image, source_name: str) -> dict:
    w, h = img.size
    colors = [p for p in img.getdata() if p[3] > 0]
    counts = Counter(colors)
    palette = [c for c, _ in counts.most_common(32)]
    return {
        "source": source_name,
        "size": [w, h],
        "opaque_pixels": len(colors),
        "unique_colors": len(counts),
        "top_colors_hex": [f"#{r:02x}{g:02x}{b:02x}" for r, g, b, a in palette[:16]],
    }


def _write_swatch(out_dir: Path, palette: list) -> None:
    sw = Image.new("RGBA", (max(1, len(palette)) * 8, 8), (0, 0, 0, 0))
    for i, c in enumerate(palette):
        for x in range(8):
            for y in range(8):
                sw.putpixel((i * 8 + x, y), c)
    sw.save(out_dir / "swatch.png")


def analyze_png(path: Path, out_dir: Path) -> dict:
    img = Image.open(path).convert("RGBA")
    report = _color_report(img, path.name)
    report["kind"] = "png"
    out_dir.mkdir(parents=True, exist_ok=True)
    save_png(img, out_dir / "source_1x.png", scale=1)
    save_png(img, out_dir / "preview_8x.png", scale=8)
    colors = [p for p in img.getdata() if p[3] > 0]
    counts = Counter(colors)
    palette = [c for c, _ in counts.most_common(32)]
    _write_swatch(out_dir, palette)
    (out_dir / "report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report


def analyze_gif(path: Path, out_dir: Path, *, max_frames: int = 64, contact_cols: int = 8) -> dict:
    im = Image.open(path)
    n_frames = getattr(im, "n_frames", 1)
    count = min(n_frames, max_frames)
    frames_dir = out_dir / "frames"
    frames_dir.mkdir(parents=True, exist_ok=True)

    durations_ms: list[int] = []
    frame_sizes: list[list[int]] = []
    all_colors: Counter = Counter()

    for i in range(count):
        im.seek(i)
        frame = im.convert("RGBA")
        frame_sizes.append(list(frame.size))
        durations_ms.append(int(im.info.get("duration", 100)))
        save_png(frame, frames_dir / f"frame_{i:03d}.png", scale=1)
        for p in frame.getdata():
            if p[3] > 0:
                all_colors[p] += 1

    w0, h0 = frame_sizes[0]
    avg_ms = sum(durations_ms) / max(1, len(durations_ms))
    est_fps = 1000.0 / avg_ms if avg_ms > 0 else 10.0
    loop = im.info.get("loop", 0)

    # Contact sheet (1× thumbnails)
    cols = min(contact_cols, count)
    rows = int(math.ceil(count / cols))
    sheet = Image.new("RGBA", (cols * w0, rows * h0), (0, 0, 0, 0))
    for i in range(count):
        im.seek(i)
        fr = im.convert("RGBA")
        c, r = i % cols, i // cols
        sheet.paste(fr, (c * w0, r * h0))

    out_dir.mkdir(parents=True, exist_ok=True)
    save_png(sheet, out_dir / "contact_1x.png", scale=1)
    save_png(sheet, out_dir / "preview_8x.png", scale=min(8, max(1, 512 // max(w0 * cols, 1))))

    palette = [c for c, _ in all_colors.most_common(32)]
    _write_swatch(out_dir, palette)

    phase_hints = []
    if count >= 8:
        q = count // 4
        phase_hints = [
            {"label": "quarter_1", "frame": 0},
            {"label": "quarter_2", "frame": q},
            {"label": "quarter_3", "frame": q * 2},
            {"label": "quarter_4", "frame": min(count - 1, q * 3)},
        ]

    report = {
        "kind": "gif",
        "source": path.name,
        "frame_count": count,
        "total_frames_in_file": n_frames,
        "frame_size": [w0, h0],
        "durations_ms": durations_ms,
        "avg_duration_ms": round(avg_ms, 2),
        "estimated_fps": round(est_fps, 2),
        "loop_forever": loop == 0,
        "unique_colors_across_frames": len(all_colors),
        "top_colors_hex": [f"#{r:02x}{g:02x}{b:02x}" for r, g, b, a in palette[:16]],
        "frames_dir": "frames/",
        "phase_hint_frames": phase_hints,
        "agent_notes": (
            "Inspect frames/ for windup vs strike boundaries; map phase_hint_frames to PROMPT.md attack script."
        ),
    }
    (out_dir / "report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report


def analyze(path: Path, out_dir: Path) -> dict:
    suffix = path.suffix.lower()
    if suffix == ".gif":
        return analyze_gif(path, out_dir)
    return analyze_png(path, out_dir)


def main(argv: list[str]) -> int:
    if len(argv) < 3:
        print("usage: study.py <input.png|gif> <out-study-dir>", file=sys.stderr)
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
