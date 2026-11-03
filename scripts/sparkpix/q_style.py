"""JRPG \"Q\" / cute chibi proportions for 64×64 side-view heroes (~2.5–3 heads tall)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

FOOT_Y = 61
"""Feet baseline row (validations.md)."""

# Quality heuristics: Q heroes are head-heavy; silhouette fill is still ~78–86%.
MIN_HEIGHT_FILL = 0.76


@dataclass(frozen=True)
class Skeleton64Q:
    foot_f: Tuple[int, int] = (31, FOOT_Y)
    foot_b: Tuple[int, int] = (25, FOOT_Y)
    knee_f: Tuple[int, int] = (30, 54)
    knee_b: Tuple[int, int] = (26, 54)
    hip: Tuple[int, int] = (28, 48)
    shoulder: Tuple[int, int] = (30, 38)
    elbow: Tuple[int, int] = (34, 42)
    hand: Tuple[int, int] = (36, 44)
    head: Tuple[int, int] = (28, 25)


Q64 = Skeleton64Q()
KNEE_Y = Q64.knee_f[1]
HIP_Y = Q64.hip[1]
SHOULDER_Y = Q64.shoulder[1]
