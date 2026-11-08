"""Platform action-hero proportions — 128×128 side view +X.

Reference ``male_hero-design`` places a Q-scale (~36px tall) hero on a 128 canvas
with feet on row 79 — not a full-height 3.5-head figure.
"""

from __future__ import annotations

from dataclasses import dataclass
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


@dataclass(frozen=True)
class P128:
    """Anchored Q64 skeleton — matches male_hero design sheet placement."""

    foot_f: Tuple[int, int] = _anchor(Q64.foot_f)
    foot_b: Tuple[int, int] = _anchor(Q64.foot_b)
    knee_f: Tuple[int, int] = _anchor(Q64.knee_f)
    knee_b: Tuple[int, int] = _anchor(Q64.knee_b)
    hip: Tuple[int, int] = _anchor(Q64.hip)
    shoulder: Tuple[int, int] = _anchor(Q64.shoulder)
    elbow: Tuple[int, int] = _anchor(Q64.elbow)
    hand: Tuple[int, int] = _anchor(Q64.hand)
    head: Tuple[int, int] = (_anchor(Q64.head)[0], _anchor(Q64.head)[1] + HEAD_Y_ADJ)
    neck: Tuple[int, int] = _anchor(NECK_PT)
