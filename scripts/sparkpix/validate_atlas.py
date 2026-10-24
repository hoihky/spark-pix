"""Atlas manifest validation (library)."""

from __future__ import annotations

import json
from pathlib import Path

from PIL import Image


def validate_atlas_dir(path: Path) -> list[str]:
    errors: list[str] = []
    json_files = list(path.glob("*.spark-atlas.json"))
    if not json_files:
        errors.append(f"no *.spark-atlas.json in {path}")
        return errors
    for manifest_path in json_files:
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
        tex_name = data.get("texture")
        if not tex_name:
            errors.append(f"{manifest_path}: missing texture")
            continue
        tex_path = path / tex_name
        if not tex_path.is_file():
            errors.append(f"{manifest_path}: texture missing: {tex_name}")
            continue
        img = Image.open(tex_path)
        cols = int(data.get("columns", 0))
        rows = int(data.get("rows", 0))
        fw = int(data.get("frameWidth", 0))
        fh = int(data.get("frameHeight", 0))
        pad = int(data.get("padding", 0))
        expected_w = cols * fw + max(0, cols - 1) * pad
        expected_h = rows * fh + max(0, rows - 1) * pad
        if img.size != (expected_w, expected_h):
            errors.append(
                f"{tex_path}: size {img.size} != expected {(expected_w, expected_h)} from manifest"
            )
        for clip in data.get("clips", []):
            first = int(clip.get("firstFrame", 0))
            count = int(clip.get("frameCount", 1))
            if first + count > cols * rows:
                errors.append(f"{manifest_path}: clip {clip.get('name')} exceeds grid")
    return errors
