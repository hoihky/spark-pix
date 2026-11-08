"""Reference-traced face stamps (male_hero design) — palette-swappable skin + fixed eye layout."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Sequence

from sparkpix.canvas import Sprite
from sparkpix.color import ColorLike
from sparkpix.platform_style import FACE_REL_DY, face_anchor_at_rest, face_y_from_head_joint

ColorSeq = Sequence[ColorLike]

# Deprecated alias — prefer ``platform_style.FACE_REL_DY``, ``P128.face``, ``face_y_from_head_joint``.
REF_DESIGN_FACE_Y_ADJ = FACE_REL_DY
REF_FACE_ANCHOR = face_anchor_at_rest()

_TEMPLATE = Path(__file__).resolve().parent / "ref_male_hero_face.json"


@lru_cache(maxsize=1)
def _face_data() -> dict:
    return json.loads(_TEMPLATE.read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def _skin_stamps() -> list[tuple[int, int, int]]:
    return [tuple(s) for s in _face_data()["skin"]]


@lru_cache(maxsize=1)
def _eye_stamps() -> list[tuple[int, int, str]]:
    return [tuple(s) for s in _face_data()["eye"]]


def design_face_cy(head_cy: int) -> int:
    """World Y for face/hair stamps from rig head joint Y."""
    return face_y_from_head_joint(head_cy)


def draw_ref_male_hero_face(
    s: Sprite,
    cx: int,
    cy: int,
    skin: ColorSeq,
    *,
    pupil: ColorLike,
    iris: ColorLike,
    sclera: ColorLike,
    sway: int = 0,
    layer: str = "full",
) -> None:
    """
    Stamp traced skin/eye pixels from design idle.

    ``cy`` is the facial row (``face_y_from_head_joint(head[1])``), not the head joint.
    """
    if layer in ("full", "skin"):
        for dx, dy, step in _skin_stamps():
            idx = max(0, min(step, len(skin) - 1))
            s.px(cx + dx + sway, cy + dy, skin[idx])
    if layer in ("full", "eye"):
        kind_color = {
            "pupil": pupil,
            "iris": iris,
            "sclera": sclera,
        }
        for dx, dy, kind in _eye_stamps():
            col = kind_color.get(kind)
            if col is not None:
                s.px(cx + dx + sway, cy + dy, col)
