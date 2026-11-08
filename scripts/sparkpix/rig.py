"""Skeleton point helpers for rig-based character builds."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Callable, Tuple, TypeVar

T = TypeVar("T")


@dataclass(frozen=True)
class Pt:
    x: int
    y: int

    def shift(self, dx: int = 0, dy: int = 0) -> "Pt":
        return Pt(self.x + dx, self.y + dy)

    def as_tuple(self) -> Tuple[int, int]:
        return self.x, self.y


def lerp_int(a: int, b: int, t: float) -> int:
    return int(round(a + (b - a) * t))


def lerp_float(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def tip(px: int, py: int, deg: float, length: float) -> Tuple[int, int]:
    """Weapon / limb tip from origin, angle in degrees (0=+X, 90=+Y)."""
    rad = math.radians(deg)
    return int(px + math.cos(rad) * length), int(py + math.sin(rad) * length)


def weapon_raised_behind_head(weapon_deg: float, threshold: float = 78.0) -> bool:
    """
    True when weapon should draw behind the head (overhead windup).

    Angles use screen math: 0°=+X, 90°=+Y down, **negative°=tip above grip**.
    """
    if weapon_deg < -38:
        return True
    return weapon_deg > threshold


def apply_shift(
    dy: int,
    lean: int,
    foot_f: Tuple[int, int],
    foot_b: Tuple[int, int],
    knee_f: Tuple[int, int],
    knee_b: Tuple[int, int],
    hip: Tuple[int, int],
    shoulder: Tuple[int, int],
    elbow: Tuple[int, int],
    hand: Tuple[int, int],
    head: Tuple[int, int],
    neck: Tuple[int, int] | None = None,
) -> dict[str, Tuple[int, int]]:
    """Apply vertical breath/jump (dy) and horizontal lean to all rig points."""

    def p(pt: Tuple[int, int]) -> Tuple[int, int]:
        return pt[0] + lean, pt[1] + dy

    out = {
        "foot_f": p(foot_f),
        "foot_b": p(foot_b),
        "knee_f": p(knee_f),
        "knee_b": p(knee_b),
        "hip": p(hip),
        "shoulder": p(shoulder),
        "elbow": p(elbow),
        "hand": p(hand),
        "head": p(head),
    }
    if neck is not None:
        out["neck"] = p(neck)
    return out


def shift_tuple(pt: Tuple[int, int], dx: int, dy: int = 0) -> Tuple[int, int]:
    return pt[0] + dx, pt[1] + dy
