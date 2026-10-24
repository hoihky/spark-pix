"""Export PNG, GIF, spritesheets, and Spark engine manifests."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

from PIL import Image

from sparkpix.color import RGBA


@dataclass
class AnimationClip:
    name: str
    first_frame: int = 0
    frame_count: int = 1
    fps: float = 8.0
    loop: bool = True

    def to_spark_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "firstFrame": self.first_frame,
            "frameCount": self.frame_count,
            "framesPerSecond": self.fps,
            "loop": self.loop,
        }


@dataclass
class SpritesheetMeta:
    columns: int
    rows: int
    frame_width: int
    frame_height: int
    padding: int = 0
    clips: List[AnimationClip] = field(default_factory=list)
    texture_name: str = "atlas.png"

    def spark_manifest(self) -> Dict[str, Any]:
        return {
            "format": "spark-sprite-atlas-v1",
            "texture": self.texture_name,
            "columns": self.columns,
            "rows": self.rows,
            "frameWidth": self.frame_width,
            "frameHeight": self.frame_height,
            "padding": self.padding,
            "gridOrigin": "bottom-left",
            "frameOrder": "row-major-x-then-y",
            "nearestFilter": True,
            "clips": [c.to_spark_dict() for c in self.clips],
            "notes": (
                "Matches Spark::SpriteAnimatorComponent uniform grid: frame 0 is bottom-left, "
                "+X then +Y. Use SetUniformGrid(columns, rows) and SpriteAnimationClip fields."
            ),
        }


def scale_nearest(img: Image.Image, scale: int) -> Image.Image:
    if scale <= 1:
        return img.copy()
    w, h = img.size
    return img.resize((w * scale, h * scale), Image.Resampling.NEAREST)


def compose_spritesheet(
    frames: Sequence[Image.Image],
    columns: int,
    padding: int = 0,
) -> Tuple[Image.Image, SpritesheetMeta]:
    if not frames:
        raise ValueError("no frames")
    fw, fh = frames[0].size
    for f in frames:
        if f.size != (fw, fh):
            raise ValueError("all frames must share the same size")
    n = len(frames)
    rows = (n + columns - 1) // columns
    sheet_w = columns * fw + (columns - 1) * padding
    sheet_h = rows * fh + (rows - 1) * padding
    sheet = Image.new("RGBA", (sheet_w, sheet_h), (0, 0, 0, 0))
    for i, frame in enumerate(frames):
        col = i % columns
        row = i // columns
        x = col * (fw + padding)
        y = row * (fh + padding)
        sheet.paste(frame, (x, y))
    meta = SpritesheetMeta(
        columns=columns,
        rows=rows,
        frame_width=fw,
        frame_height=fh,
        padding=padding,
    )
    return sheet, meta


def save_png(img: Image.Image, path: Path, scale: int = 1) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    out = scale_nearest(img, scale)
    out.save(path, format="PNG")


def save_gif(frames: Sequence[Image.Image], path: Path, durations_ms: Sequence[int], scale: int = 1) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    scaled = [scale_nearest(f, scale) for f in frames]
    durs = list(durations_ms)
    if len(durs) < len(scaled):
        durs.extend([durs[-1] if durs else 100] * (len(scaled) - len(durs)))
    scaled[0].save(
        path,
        save_all=True,
        append_images=scaled[1:],
        duration=durs[: len(scaled)],
        loop=0,
        disposal=2,
        transparency=0,
    )


def save_spark_atlas(
    frames: Sequence[Image.Image],
    out_dir: Path,
    base_name: str,
    columns: int,
    padding: int = 0,
    clips: Optional[List[AnimationClip]] = None,
    preview_scale: int = 6,
) -> SpritesheetMeta:
    out_dir.mkdir(parents=True, exist_ok=True)
    sheet, meta = compose_spritesheet(frames, columns, padding)
    png_name = f"{base_name}.png"
    meta.texture_name = png_name
    meta.clips = clips or []
    save_png(sheet, out_dir / png_name, scale=1)
    if preview_scale > 1:
        save_png(sheet, out_dir / f"{base_name}@{preview_scale}x.png", scale=preview_scale)
    manifest = meta.spark_manifest()
    json_path = out_dir / f"{base_name}.spark-atlas.json"
    json_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return meta


def preview_with_grid(
    img: Image.Image,
    path: Path,
    scale: int = 8,
    grid_color: RGBA = (255, 0, 255, 80),
    cell: Optional[Tuple[int, int]] = None,
) -> None:
    scaled = scale_nearest(img, scale)
    if cell:
        cw, ch = cell
        from sparkpix.draw_ops import line as draw_line

        w, h = scaled.size
        for x in range(0, w, cw * scale):
            draw_line(scaled, x, 0, x, h - 1, grid_color)
        for y in range(0, h, ch * scale):
            draw_line(scaled, 0, y, w - 1, y, grid_color)
    save_png(scaled, path, scale=1)
