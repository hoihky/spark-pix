"""Platform action-hero proportions — 128×128 side view +X.

Reference ``male_hero-design`` places a Q-scale (~36px tall) hero on a 128 canvas
with feet on row 79 — not a full-height 3.5-head figure.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Tuple

from sparkpix.q_style import Q64

W, H = 128, 128
ANCHOR_X = 34
ANCHOR_Y = 18
HEAD_Y_ADJ = -2
NECK_PT = (28, 35)
FOOT_Y = Q64.foot_f[1] + ANCHOR_Y
KNEE_Y = Q64.knee_f[1] + ANCHOR_Y
MIN_HEIGHT_FILL = 0.28
SCARF_TIP_NUDGE_DX = 0
"""Extra pixels added to keyed scarf tip (calibrate with ``scarf_tip_parity.py``)."""


def _anchor(pt: Tuple[int, int]) -> Tuple[int, int]:
    return pt[0] + ANCHOR_X, pt[1] + ANCHOR_Y


_HEAD_JOINT: Tuple[int, int] = (_anchor(Q64.head)[0], _anchor(Q64.head)[1] + HEAD_Y_ADJ)


@lru_cache(maxsize=1)
def _male_hero_landmarks() -> dict:
    path = Path(__file__).resolve().parent / "ref_male_hero_landmarks.json"
    if not path.is_file():
        return {
            "p128_head_joint": list(_HEAD_JOINT),
            "face_anchor": [_HEAD_JOINT[0], _HEAD_JOINT[1] + 13],
            "face_y_adj": 13,
        }
    return json.loads(path.read_text(encoding="utf-8"))


def face_rel_dy() -> int:
    """Pixels from ``P128.head`` joint row to design facial stamp row (from calibration JSON)."""
    lm = _male_hero_landmarks()
    adj = int(lm.get("face_y_adj", 0))
    if adj:
        return adj
    joint = tuple(lm.get("p128_head_joint", _HEAD_JOINT))
    anchor = tuple(lm.get("face_anchor", joint))
    return anchor[1] - joint[1]


FACE_REL_DY = face_rel_dy()


def face_y_from_head_joint(head_y: int) -> int:
    """World Y for hair/face stamps given rig ``head`` joint Y (after ``apply_shift``)."""
    return head_y + FACE_REL_DY


def face_anchor_from_head(head: Tuple[int, int]) -> Tuple[int, int]:
    """Hair + traced face stamp anchor; ``head`` is the skeleton joint, not the facial row."""
    return head[0], face_y_from_head_joint(head[1])


def face_anchor_at_rest() -> Tuple[int, int]:
    """Idle facial landmark on the design sheet (stamped hair/face anchor)."""
    lm = _male_hero_landmarks()
    anchor = lm.get("face_anchor")
    if anchor:
        return int(anchor[0]), int(anchor[1])
    return face_anchor_from_head(_HEAD_JOINT)


@dataclass(frozen=True)
class P128:
    """
    Anchored Q64 skeleton — matches male_hero design sheet placement.

    ``head`` — rig/neck joint (Q head + anchor).
    ``face`` — idle facial landmark for traced hair/face; moves as ``face_anchor_from_head(head)``.
    """

    foot_f: Tuple[int, int] = _anchor(Q64.foot_f)
    foot_b: Tuple[int, int] = _anchor(Q64.foot_b)
    knee_f: Tuple[int, int] = _anchor(Q64.knee_f)
    knee_b: Tuple[int, int] = _anchor(Q64.knee_b)
    hip: Tuple[int, int] = _anchor(Q64.hip)
    shoulder: Tuple[int, int] = _anchor(Q64.shoulder)
    elbow: Tuple[int, int] = _anchor(Q64.elbow)
    hand: Tuple[int, int] = _anchor(Q64.hand)
    head: Tuple[int, int] = _HEAD_JOINT
    face: Tuple[int, int] = face_anchor_at_rest()
    neck: Tuple[int, int] = _anchor(NECK_PT)
