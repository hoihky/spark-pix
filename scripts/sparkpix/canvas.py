"""Multi-frame sprite canvas API."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple, Union

from PIL import Image

from sparkpix.color import PALETTES, RGBA, ColorLike, parse_color, ramp
from sparkpix import draw_ops
from sparkpix.export import (
    AnimationClip,
    SpritesheetMeta,
    preview_with_grid,
    save_gif,
    save_png,
    save_spark_atlas,
)


class Sprite:
    """Pixel canvas with optional animation frames and named layers."""

    def __init__(
        self,
        width: int,
        height: int,
        palette: Optional[Union[str, Sequence[ColorLike]]] = None,
    ) -> None:
        if width <= 0 or height <= 0:
            raise ValueError("width and height must be positive")
        self._fw = width
        self._fh = height
        self._palette: List[RGBA] = self._resolve_palette(palette)
        self._frames: List[Dict[str, Image.Image]] = [{"main": self._blank()}]
        self._durations_ms: List[int] = [100]
        self._frame_idx = 0
        self._layer = "main"
        self._clips: List[AnimationClip] = []

    @staticmethod
    def _resolve_palette(palette: Optional[Union[str, Sequence[ColorLike]]]) -> List[RGBA]:
        if palette is None:
            return []
        if isinstance(palette, str):
            if palette in PALETTES:
                return list(PALETTES[palette])
            raise KeyError(f"unknown palette preset: {palette}")
        out: List[RGBA] = []
        for c in palette:
            pc = parse_color(c, out)
            if pc is not None:
                out.append(pc)
        return out

    def _blank(self) -> Image.Image:
        return Image.new("RGBA", (self._fw, self._fh), (0, 0, 0, 0))

    @property
    def palette(self) -> List[RGBA]:
        return list(self._palette)

    def _img(self) -> Image.Image:
        return self._frames[self._frame_idx][self._layer]

    def _mask(self, only: Optional[ColorLike]) -> draw_ops.MaskFn:
        return draw_ops.build_mask(only, self._palette)

    def _color(self, c: ColorLike) -> Optional[RGBA]:
        return parse_color(c, self._palette)

    # --- navigation ---

    def layer(self, name: str) -> "Sprite":
        if name not in self._frames[self._frame_idx]:
            self._frames[self._frame_idx][name] = self._blank()
        self._layer = name
        return self

    def frame(self, index: int) -> "Sprite":
        self._frame_idx = max(0, min(index, len(self._frames) - 1))
        if self._layer not in self._frames[self._frame_idx]:
            self._frames[self._frame_idx][self._layer] = self._blank()
        return self

    def use(self, frame: Optional[int] = None, layer: Optional[str] = None) -> "Sprite":
        if frame is not None:
            self.frame(frame)
        if layer is not None:
            self.layer(layer)
        return self

    def add_frame(self, copy: bool = True) -> int:
        if copy:
            layers = {k: v.copy() for k, v in self._frames[self._frame_idx].items()}
        else:
            layers = {k: self._blank() for k in self._frames[self._frame_idx]}
        self._frames.append(layers)
        self._durations_ms.append(self._durations_ms[-1] if self._durations_ms else 100)
        self._frame_idx = len(self._frames) - 1
        return self._frame_idx

    def set_duration(self, ms: int, frames: Optional[Sequence[int]] = None) -> None:
        if frames is None:
            self._durations_ms[self._frame_idx] = ms
            return
        for i in frames:
            if 0 <= i < len(self._durations_ms):
                self._durations_ms[i] = ms

    def tag_clip(
        self,
        name: str,
        from_frame: int,
        to_frame: int,
        fps: float = 8.0,
        loop: bool = True,
    ) -> None:
        count = max(1, to_frame - from_frame + 1)
        self._clips.append(
            AnimationClip(name=name, first_frame=from_frame, frame_count=count, fps=fps, loop=loop)
        )

    def flatten_frame(self, index: int) -> Image.Image:
        base = self._blank()
        for layer_img in self._frames[index].values():
            base.alpha_composite(layer_img)
        return base

    def all_flat_frames(self) -> List[Image.Image]:
        return [self.flatten_frame(i) for i in range(len(self._frames))]

    # --- draw ---

    def px(self, x: int, y: int, color: ColorLike, only: Optional[ColorLike] = None) -> None:
        c = self._color(color)
        if c is None:
            c = (0, 0, 0, 0)
        draw_ops.set_px(self._img(), x, y, c, self._mask(only))

    def get(self, x: int, y: int) -> RGBA:
        return draw_ops.get_px(self._img(), x, y)

    def line(self, x0: int, y0: int, x1: int, y1: int, color: ColorLike, only: Optional[ColorLike] = None) -> None:
        c = self._color(color)
        if c is None:
            return
        draw_ops.line(self._img(), x0, y0, x1, y1, c, self._mask(only))

    def rect(
        self,
        x0: int,
        y0: int,
        x1: int,
        y1: int,
        fill: Optional[ColorLike] = None,
        outline: Optional[ColorLike] = None,
        only: Optional[ColorLike] = None,
    ) -> None:
        f = self._color(fill) if fill is not None else None
        o = self._color(outline) if outline is not None else None
        draw_ops.rect(self._img(), x0, y0, x1, y1, f, o, self._mask(only))

    def circle(
        self,
        cx: int,
        cy: int,
        r: int,
        fill: Optional[ColorLike] = None,
        outline: Optional[ColorLike] = None,
        only: Optional[ColorLike] = None,
    ) -> None:
        f = self._color(fill) if fill is not None else None
        o = self._color(outline) if outline is not None else None
        draw_ops.circle(self._img(), cx, cy, r, f, o, self._mask(only))

    def ellipse(
        self,
        x0: int,
        y0: int,
        x1: int,
        y1: int,
        fill: Optional[ColorLike] = None,
        only: Optional[ColorLike] = None,
    ) -> None:
        f = self._color(fill) if fill is not None else None
        draw_ops.ellipse(self._img(), x0, y0, x1, y1, f, self._mask(only))

    def polygon(self, points: Sequence[Tuple[int, int]], fill: ColorLike, only: Optional[ColorLike] = None) -> None:
        f = self._color(fill)
        if f is None:
            return
        draw_ops.polygon(self._img(), points, f, self._mask(only))

    def fill(self, x: int, y: int, color: ColorLike, only: Optional[ColorLike] = None) -> None:
        c = self._color(color)
        if c is None:
            return
        draw_ops.flood_fill(self._img(), x, y, c, self._mask(only))

    def clear(self) -> None:
        self._frames[self._frame_idx][self._layer] = self._blank()

    def outline(self, color: ColorLike, where: str = "outside", only: Optional[ColorLike] = None) -> None:
        c = self._color(color)
        if c is None:
            return
        draw_ops.outline_region(self._img(), c, where=where, mask=self._mask(only))

    def mirror_x(self) -> None:
        self._frames[self._frame_idx][self._layer] = self._img().transpose(Image.Transpose.FLIP_LEFT_RIGHT)

    def mirror_y(self) -> None:
        self._frames[self._frame_idx][self._layer] = self._img().transpose(Image.Transpose.FLIP_TOP_BOTTOM)

    def replace(self, old: ColorLike, new: ColorLike) -> None:
        o = self._color(old)
        n = self._color(new)
        if o is None or n is None:
            return
        draw_ops.replace_color(self._img(), o, n)

    def dither(
        self,
        box: Tuple[int, int, int, int],
        c1: ColorLike,
        c2: ColorLike,
        mix_ratio: float = 0.5,
        pattern: str = "checker",
    ) -> None:
        a = self._color(c1)
        b = self._color(c2)
        if a is None or b is None:
            return
        draw_ops.dither_box(self._img(), box, a, b, mix_ratio, pattern)

    def paste_png(self, path: Union[str, Path], x: int, y: int) -> None:
        im = Image.open(path).convert("RGBA")
        self._img().paste(im, (x, y), im)

    # --- inspect / export ---

    def used_colors(self) -> List[RGBA]:
        seen: Dict[RGBA, None] = {}
        for fr in self._frames:
            flat = Image.new("RGBA", (self._fw, self._fh), (0, 0, 0, 0))
            for layer_img in fr.values():
                flat.alpha_composite(layer_img)
            for px in flat.getdata():
                if px[3] > 0:
                    seen[px] = None
        return list(seen.keys())

    def stats(self) -> str:
        colors = self.used_colors()
        lines = [
            f"frames={len(self._frames)} size={self._fw}x{self._fh} layers={len(self._frames[self._frame_idx])}",
            f"unique_opaque_colors={len(colors)}",
        ]
        if self._clips:
            lines.append(f"clips={len(self._clips)}")
        return "\n".join(lines)

    def preview(
        self,
        path: Union[str, Path],
        scale: int = 8,
        grid: bool = False,
    ) -> None:
        flat = self.flatten_frame(self._frame_idx)
        if grid:
            preview_with_grid(flat, Path(path), scale=scale, cell=(self._fw, self._fh))
        else:
            save_png(flat, Path(path), scale=scale)

    def save_png(
        self,
        path: Union[str, Path],
        frame: Optional[int] = None,
        scale: int = 1,
    ) -> None:
        idx = self._frame_idx if frame is None else frame
        save_png(self.flatten_frame(idx), Path(path), scale=scale)

    def save_gif(self, path: Union[str, Path], scale: int = 1) -> None:
        save_gif(self.all_flat_frames(), Path(path), self._durations_ms, scale=scale)

    def save_spritesheet(
        self,
        path: Union[str, Path],
        columns: int,
        scale: int = 1,
        padding: int = 0,
        spark_json: bool = True,
    ) -> SpritesheetMeta:
        out = Path(path)
        out_dir = out.parent
        base = out.stem
        meta = save_spark_atlas(
            self.all_flat_frames(),
            out_dir,
            base,
            columns=columns,
            padding=padding,
            clips=self._clips,
            preview_scale=max(scale, 1),
        )
        if not spark_json:
            (out_dir / f"{base}.spark-atlas.json").unlink(missing_ok=True)
        return meta

    def save_project(self, path: Union[str, Path]) -> None:
        data = {
            "width": self._fw,
            "height": self._fh,
            "palette": self._palette,
            "durations_ms": self._durations_ms,
            "clips": [c.to_spark_dict() for c in self._clips],
            "frames": [],
        }
        for fr in self._frames:
            layers: Dict[str, str] = {}
            for name, img in fr.items():
                import base64
                import io

                buf = io.BytesIO()
                img.save(buf, format="PNG")
                layers[name] = base64.b64encode(buf.getvalue()).decode("ascii")
            data["frames"].append(layers)
        Path(path).write_text(json.dumps(data), encoding="utf-8")

    @classmethod
    def load_project(cls, path: Union[str, Path]) -> "Sprite":
        import base64
        import io

        raw = json.loads(Path(path).read_text(encoding="utf-8"))
        s = cls(raw["width"], raw["height"], palette=raw.get("palette") or None)
        s._frames = []
        for fr in raw["frames"]:
            layers: Dict[str, Image.Image] = {}
            for name, b64 in fr.items():
                layers[name] = Image.open(io.BytesIO(base64.b64decode(b64))).convert("RGBA")
            s._frames.append(layers)
        s._durations_ms = raw.get("durations_ms", [100] * len(s._frames))
        s._clips = [
            AnimationClip(
                name=c["name"],
                first_frame=c["firstFrame"],
                frame_count=c["frameCount"],
                fps=c.get("framesPerSecond", 8.0),
                loop=c.get("loop", True),
            )
            for c in raw.get("clips", [])
        ]
        s._frame_idx = 0
        return s


# re-export helpers on module for convenience in build scripts
__all__ = ["Sprite", "ramp", "PALETTES"]
