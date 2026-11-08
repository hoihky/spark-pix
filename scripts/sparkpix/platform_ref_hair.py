"""Reference-traced hair stamp (male_hero design) — palette-swappable."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Sequence

from sparkpix.canvas import Sprite
from sparkpix.color import ColorLike
from sparkpix.platform_style import FACE_REL_DY  # noqa: F401 — re-export for legacy imports

REF_DESIGN_FACE_Y_ADJ = FACE_REL_DY  # deprecated: use platform_style.FACE_REL_DY / face_y_from_head_joint

ColorSeq = Sequence[ColorLike]

# Stamps are relative to the design facial row (see ``platform_ref_face``).
REF_HAIR_ANCHOR_DY = 0
# Cheek bangs (dy<=9) draw in face_front — after skin — nape stays in hair_back.
REF_HAIR_FRINGE_DY_MAX = 9
_TEMPLATE = Path(__file__).resolve().parent / "ref_male_hero_hair.json"


@lru_cache(maxsize=1)
def _stamps() -> list[tuple[int, int, int]]:
    data = json.loads(_TEMPLATE.read_text(encoding="utf-8"))
    return [tuple(s) for s in data["stamps"]]


def draw_ref_male_hero_hair(
    s: Sprite,
    cx: int,
    cy: int,
    hair: ColorSeq,
    *,
    sway: int = 0,
    layer: str = "full",
) -> None:
    """Stamp hair from design PNG; ``hair`` ramp replaces reference browns."""
    oy = REF_HAIR_ANCHOR_DY
    for dx, dy, step in _stamps():
        if layer == "full":
            pass
        elif layer == "hair_back" and dy <= REF_HAIR_FRINGE_DY_MAX:
            continue
        elif layer == "face_front" and dy > 0:
            continue
        elif layer == "fringe" and not (1 <= dy <= REF_HAIR_FRINGE_DY_MAX):
            continue
        elif layer not in ("hair_back", "face_front", "fringe", "full"):
            continue
        idx = max(0, min(step, len(hair) - 1))
        s.px(cx + dx + sway, cy + dy + oy, hair[idx])
