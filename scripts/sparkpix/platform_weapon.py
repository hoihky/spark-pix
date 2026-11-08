"""Side-view hand weapons (+X) — angle from rig + ``rig.tip``."""

from __future__ import annotations

from typing import Sequence, Tuple

from sparkpix import rig
from sparkpix import render as rd
from sparkpix.canvas import Sprite
from sparkpix.color import ColorLike

ColorSeq = Sequence[ColorLike]


def draw_weapon(
    s: Sprite,
    hand: Tuple[int, int],
    deg: float,
    weapon: ColorSeq,
    style: str,
    *,
    length: float = 14.0,
) -> None:
    """Dispatch on ``hero_config.WEAPON_STYLES`` ids."""
    if style in ("none", "scarf"):
        return
    if style == "baton":
        draw_weapon_baton(s, hand, deg, weapon, length=length)
    elif style == "stick":
        draw_weapon_stick(s, hand, deg, weapon, length=length)
    elif style == "blade":
        draw_weapon_blade(s, hand, deg, weapon, length=length)
    else:
        raise ValueError(f"unknown weapon style {style!r}")


def draw_weapon_baton(
    s: Sprite,
    hand: Tuple[int, int],
    deg: float,
    weapon: ColorSeq,
    *,
    length: float = 14.0,
) -> None:
    tip = rig.tip(hand[0], hand[1], deg, length)
    rd.limb_shaded(s, hand, tip, 1, weapon)
    s.px(tip[0], tip[1], weapon[-1])
    s.px(hand[0], hand[1], weapon[0], only="opaque")


def draw_weapon_stick(
    s: Sprite,
    hand: Tuple[int, int],
    deg: float,
    weapon: ColorSeq,
    *,
    length: float = 16.0,
) -> None:
    tip = rig.tip(hand[0], hand[1], deg, length)
    s.line(hand[0], hand[1], tip[0], tip[1], weapon[2])
    s.px(tip[0], tip[1], weapon[-1])


def draw_weapon_blade(
    s: Sprite,
    hand: Tuple[int, int],
    deg: float,
    weapon: ColorSeq,
    *,
    length: float = 18.0,
) -> None:
    tip = rig.tip(hand[0], hand[1], deg, length)
    rd.limb_shaded(s, hand, tip, 1, weapon)
    hx, hy = hand
    edge = rig.tip(hx, hy, deg + 92, 3)
    s.px(edge[0], edge[1], weapon[-1], only="opaque")
