"""Regional idle parity for platform fighters (design sheet vs ``frame0_art.png``)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable

from PIL import Image

Pixel = tuple[int, int, int, int]
RGB = tuple[int, int, int]


@dataclass(frozen=True)
class Roi:
    x0: int
    y0: int
    x1: int  # exclusive
    y1: int


@dataclass(frozen=True)
class RegionCheck:
    name: str
    roi: Roi
    colors: frozenset[RGB]
    ref_count: int | None = None
    count_tol_frac: float = 0.35
    count_tol_abs: int = 12
    bbox_tol_px: int = 4


MALE_HERO_SKIN_RGB = frozenset(
    {
        (0xC8, 0x90, 0x78),
        (0xD2, 0x94, 0x7F),
        (0xFF, 0xC5, 0xB4),
        (0xD7, 0x7E, 0x86),
    }
)
MALE_HERO_SCARF_RGB = frozenset(
    {
        (0x5C, 0x2C, 0x4F),
        (0x8B, 0x10, 0x8F),
        (0xCD, 0x30, 0x73),
        (0x70, 0x10, 0x70),
    }
)
MALE_HERO_GLOVE_RGB = frozenset(
    {
        (0x5C, 0x2C, 0x4F),
        (0xA2, 0x4E, 0x57),
        (0x7D, 0x55, 0x56),
    }
)
MALE_HERO_IRIS_RGB = (0x59, 0xC1, 0x35)

MALE_HERO_FACE_ROI = Roi(54, 44, 76, 62)
# Back-hand mass only (exclude y60–63 front-glove column at x≥68 on design idle).
MALE_HERO_BACK_GLOVE_ROI = Roi(52, 64, 68, 78)


def _iter_roi(im: Image.Image, roi: Roi) -> Iterable[tuple[int, int, Pixel]]:
    for y in range(roi.y0, roi.y1):
        for x in range(roi.x0, roi.x1):
            p = im.getpixel((x, y))
            if p[3]:
                yield x, y, p


def count_colors(im: Image.Image, roi: Roi, colors: frozenset[RGB]) -> int:
    return sum(1 for _, _, p in _iter_roi(im, roi) if p[:3] in colors)


def count_face_skin(im: Image.Image, roi: Roi) -> int:
    return sum(
        1
        for _, _, p in _iter_roi(im, roi)
        if p[:3] in MALE_HERO_SKIN_RGB and p[:3] not in MALE_HERO_SCARF_RGB
    )


def count_color(im: Image.Image, color: RGB) -> int:
    n = 0
    for p in im.getdata():
        if p[3] and p[:3] == color:
            n += 1
    return n


def color_bbox(im: Image.Image, roi: Roi, colors: frozenset[RGB]) -> tuple[int, int, int, int] | None:
    xs: list[int] = []
    ys: list[int] = []
    for x, y, p in _iter_roi(im, roi):
        if p[:3] in colors:
            xs.append(x)
            ys.append(y)
    if not xs:
        return None
    return min(xs), min(ys), max(xs), max(ys)


def _bbox_ok(ref: tuple[int, int, int, int], gen: tuple[int, int, int, int], tol: int) -> bool:
    return all(abs(a - b) <= tol for a, b in zip(ref, gen))


def _count_ok(ref: int, gen: int, *, frac: float, abs_tol: int) -> bool:
    if ref == 0:
        return gen == 0
    lo = max(0, int(ref * (1.0 - frac)) - abs_tol)
    hi = int(ref * (1.0 + frac)) + abs_tol
    return lo <= gen <= hi


def male_hero_idle_region_checks(ref: Image.Image, gen: Image.Image) -> tuple[list[dict], bool]:
    """Compare regional metrics; return rows + pass flag."""
    ref = ref.convert("RGBA")
    gen = gen.convert("RGBA")

    ref_iris = count_color(ref, MALE_HERO_IRIS_RGB)
    gen_iris = count_color(gen, MALE_HERO_IRIS_RGB)

    ref_skin = count_face_skin(ref, MALE_HERO_FACE_ROI)
    gen_skin = count_face_skin(gen, MALE_HERO_FACE_ROI)

    ref_glove_n = count_colors(ref, MALE_HERO_BACK_GLOVE_ROI, MALE_HERO_GLOVE_RGB)
    gen_glove_n = count_colors(gen, MALE_HERO_BACK_GLOVE_ROI, MALE_HERO_GLOVE_RGB)
    ref_glove_bb = color_bbox(ref, MALE_HERO_BACK_GLOVE_ROI, MALE_HERO_GLOVE_RGB)
    gen_glove_bb = color_bbox(gen, MALE_HERO_BACK_GLOVE_ROI, MALE_HERO_GLOVE_RGB)

    rows: list[dict] = [
        {
            "name": "iris_pixels",
            "ref": ref_iris,
            "gen": gen_iris,
            "ok": ref_iris == gen_iris and gen_iris >= 1,
        },
        {
            "name": "face_skin_roi",
            "roi": MALE_HERO_FACE_ROI.__dict__,
            "ref": ref_skin,
            "gen": gen_skin,
            "ok": _count_ok(ref_skin, gen_skin, frac=0.55, abs_tol=18),
        },
        {
            "name": "back_glove_pixels",
            "roi": MALE_HERO_BACK_GLOVE_ROI.__dict__,
            "ref": ref_glove_n,
            "gen": gen_glove_n,
            "ok": _count_ok(ref_glove_n, gen_glove_n, frac=0.45, abs_tol=20),
        },
        {
            "name": "back_glove_bbox",
            "roi": MALE_HERO_BACK_GLOVE_ROI.__dict__,
            "ref": ref_glove_bb,
            "gen": gen_glove_bb,
            "ok": ref_glove_bb is not None
            and gen_glove_bb is not None
            and _bbox_ok(ref_glove_bb, gen_glove_bb, 4),
        },
    ]
    ok = all(r["ok"] for r in rows)
    return rows, ok


def run_male_hero_idle_regions(ref: Image.Image, gen: Image.Image) -> dict:
    regions, regions_ok = male_hero_idle_region_checks(ref, gen)
    return {"regions": regions, "regions_ok": regions_ok}
