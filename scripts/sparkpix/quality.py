"""Heuristic quality checks for humanoid sprite frames (agent + CI helpers)."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Sequence, Tuple

from PIL import Image

from sparkpix.character import thin_leg_column_count
from sparkpix.color import parse_color


def hull_outline_coverage(img: Image.Image, ink_rgb: Tuple[int, int, int], tolerance: int = 18) -> float:
    """
    Fraction of opaque edge pixels with ink (or near-ink) within 1px outside the hull.
    Used to detect missing finish_outside_outline pass.
    """
    w, h = img.size
    boundary = 0
    covered = 0

    def is_ink(px: Tuple[int, ...]) -> bool:
        if px[3] == 0:
            return False
        return all(abs(px[i] - ink_rgb[i]) <= tolerance for i in range(3))

    for y in range(h):
        for x in range(w):
            if img.getpixel((x, y))[3] == 0:
                continue
            edge = False
            for dx, dy in ((0, 1), (0, -1), (1, 0), (-1, 0)):
                nx, ny = x + dx, y + dy
                if nx < 0 or ny < 0 or nx >= w or ny >= h or img.getpixel((nx, ny))[3] == 0:
                    edge = True
                    break
            if not edge:
                continue
            boundary += 1
            found = False
            for dx in range(-2, 3):
                for dy in range(-2, 3):
                    if abs(dx) + abs(dy) > 2:
                        continue
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < w and 0 <= ny < h and is_ink(img.getpixel((nx, ny))):
                        found = True
                        break
                if found:
                    break
            if found:
                covered += 1
    if boundary == 0:
        return 1.0
    return covered / boundary


def load_quality_sidecar(path: Path) -> Optional[dict]:
    for candidate in sorted(path.glob("*.spark-quality.json")):
        import json

        data = json.loads(candidate.read_text(encoding="utf-8"))
        if data.get("format") == "spark-pix-quality-v1":
            return data
    return None


def write_quality_sidecar(out_dir: Path, atlas_stem: str, meta: dict) -> Path:
    import json

    out_dir.mkdir(parents=True, exist_ok=True)
    payload = {"format": "spark-pix-quality-v1", **meta}
    out_path = out_dir / f"{atlas_stem}.spark-quality.json"
    out_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return out_path


def build_quality_meta(
    *,
    outline_ink: str,
    foot_y: int,
    critique_frames: Sequence[int],
    humanoid: bool = True,
    min_outline_coverage: float = 0.45,
) -> dict:
    return {
        "outlineInk": outline_ink,
        "footY": foot_y,
        "critiqueFrames": list(critique_frames),
        "humanoid": humanoid,
        "minOutlineCoverage": min_outline_coverage,
    }


@dataclass
class QualityIssue:
    level: str  # "warn" | "error"
    code: str
    message: str


@dataclass
class QualityReport:
    issues: List[QualityIssue] = field(default_factory=list)

    def ok(self) -> bool:
        return not any(i.level == "error" for i in self.issues)

    def warn_count(self) -> int:
        return sum(1 for i in self.issues if i.level == "warn")


def _opaque_bbox(img: Image.Image) -> Optional[Tuple[int, int, int, int]]:
    w, h = img.size
    xs, ys = [], []
    for y in range(h):
        for x in range(w):
            if img.getpixel((x, y))[3] > 0:
                xs.append(x)
                ys.append(y)
    if not xs:
        return None
    return min(xs), min(ys), max(xs), max(ys)


def isolated_pixel_count(img: Image.Image) -> int:
    """Opaque pixels with no opaque 4-neighbor (specks and noise)."""
    w, h = img.size
    n = 0
    for y in range(h):
        for x in range(w):
            if img.getpixel((x, y))[3] == 0:
                continue
            neighbors = 0
            for dx, dy in ((0, 1), (0, -1), (1, 0), (-1, 0)):
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h and img.getpixel((nx, ny))[3] > 0:
                    neighbors += 1
            if neighbors == 0:
                n += 1
    return n


def unique_opaque_colors(img: Image.Image) -> int:
    seen = set()
    for px in img.getdata():
        if px[3] > 0:
            seen.add(px[:3])
    return len(seen)


def analyze_frame(
    img: Image.Image,
    *,
    foot_y: Optional[int] = None,
    frame_h: Optional[int] = None,
    max_colors: int = 32,
    min_height_fill: float = 0.82,
    stick_leg_threshold: int = 12,
    outline_ink: Optional[str] = None,
    min_outline_coverage: float = 0.45,
    check_humanoid: bool = True,
) -> QualityReport:
    """Run humanoid-oriented heuristics on one RGBA frame."""
    report = QualityReport()
    fh = frame_h or img.size[1]
    fy = foot_y if foot_y is not None else fh - 2

    bbox = _opaque_bbox(img)
    if bbox is None:
        report.issues.append(QualityIssue("error", "empty", "frame has no opaque pixels"))
        return report

    _, y0, _, y1 = bbox
    span = y1 - y0 + 1
    if span < int(fh * min_height_fill):
        report.issues.append(
            QualityIssue(
                "warn",
                "short_silhouette",
                f"character height {span}px < {int(fh * min_height_fill)}px "
                f"({min_height_fill:.0%} of {fh}px) — see humanoid-hero.md",
            )
        )

    colors = unique_opaque_colors(img)
    if colors > max_colors:
        report.issues.append(
            QualityIssue(
                "warn",
                "palette",
                f"{colors} opaque RGB colors > budget {max_colors} — merge ramps (palettes.md)",
            )
        )

    specks = isolated_pixel_count(img)
    if specks > 0:
        report.issues.append(
            QualityIssue(
                "warn",
                "orphan_pixels",
                f"{specks} isolated opaque pixel(s) — remove stray px (validations.md)",
            )
        )

    if check_humanoid:
        thin = thin_leg_column_count(img, max(0, fy - 18), fy)
        if thin > stick_leg_threshold:
            report.issues.append(
                QualityIssue(
                    "warn",
                    "stick_legs",
                    f"{thin} leg rows with 1px columns — use character.limb(..., radius>=3)",
                )
            )

    if outline_ink and check_humanoid:
        parsed = parse_color(outline_ink)
        if parsed:
            ratio = hull_outline_coverage(img, parsed[:3])
            if ratio < min_outline_coverage:
                report.issues.append(
                    QualityIssue(
                        "warn",
                        "weak_outline",
                        f"hull outline coverage {ratio:.0%} < {min_outline_coverage:.0%} "
                        f"— call character.finish_outside_outline({outline_ink!r})",
                    )
                )

    return report


def extract_sheet_frame(img: Image.Image, fw: int, fh: int, index: int, pad: int = 0) -> Image.Image:
    cols = max(1, (img.width + pad) // (fw + pad))
    row = index // cols
    col = index % cols
    x = col * (fw + pad)
    y = row * (fh + pad)
    return img.crop((x, y, x + fw, y + fh)).convert("RGBA")


def critique_atlas_dir(
    path: Path,
    *,
    sample_frames: Sequence[int] = (0,),
    max_colors: int = 32,
) -> QualityReport:
    """Load first *.spark-atlas.json in dir; critique selected frame indices."""
    merged = QualityReport()
    json_files = list(path.glob("*.spark-atlas.json"))
    if not json_files:
        merged.issues.append(QualityIssue("error", "manifest", f"no *.spark-atlas.json in {path}"))
        return merged

    import json

    manifest_path = json_files[0]
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    tex_name = data.get("texture")
    if not tex_name:
        merged.issues.append(QualityIssue("error", "manifest", f"{manifest_path}: missing texture"))
        return merged
    tex_path = path / tex_name
    if not tex_path.is_file():
        merged.issues.append(QualityIssue("error", "texture", f"missing {tex_name}"))
        return merged

    fw = int(data.get("frameWidth", 64))
    fh = int(data.get("frameHeight", 64))
    pad = int(data.get("padding", 0))
    sheet = Image.open(tex_path).convert("RGBA")
    foot_y = fh - 2
    outline_ink: Optional[str] = None
    min_outline = 0.45
    humanoid = True
    sidecar = load_quality_sidecar(path)
    if sidecar:
        foot_y = int(sidecar.get("footY", foot_y))
        outline_ink = sidecar.get("outlineInk")
        min_outline = float(sidecar.get("minOutlineCoverage", min_outline))
        humanoid = bool(sidecar.get("humanoid", True))
        if not sample_frames or sample_frames == (0,):
            cf = sidecar.get("critiqueFrames")
            if cf:
                sample_frames = tuple(int(x) for x in cf)

    for idx in sample_frames:
        frame = extract_sheet_frame(sheet, fw, fh, idx, pad)
        sub = analyze_frame(
            frame,
            foot_y=foot_y,
            frame_h=fh,
            max_colors=max_colors,
            outline_ink=outline_ink,
            min_outline_coverage=min_outline,
            check_humanoid=humanoid,
        )
        for issue in sub.issues:
            tagged = QualityIssue(
                issue.level,
                issue.code,
                f"frame[{idx}]: {issue.message}",
            )
            merged.issues.append(tagged)

    if len(sample_frames) >= 2:
        bottoms: List[int] = []
        for idx in sample_frames:
            frame = extract_sheet_frame(sheet, fw, fh, idx, pad)
            bbox = _opaque_bbox(frame)
            if bbox:
                bottoms.append(bbox[3])
        if bottoms and max(bottoms) - min(bottoms) > 1:
            merged.issues.append(
                QualityIssue(
                    "warn",
                    "foot_drift",
                    f"opaque bottom row varies {min(bottoms)}..{max(bottoms)} across sampled frames "
                    "— stabilize walk/run contact (animation.md)",
                )
            )

    return merged


def format_report(report: QualityReport) -> str:
    if not report.issues:
        return "OK (no quality warnings)"
    lines = []
    for i in report.issues:
        prefix = "ERROR" if i.level == "error" else "WARN"
        lines.append(f"{prefix} [{i.code}]: {i.message}")
    return "\n".join(lines)
