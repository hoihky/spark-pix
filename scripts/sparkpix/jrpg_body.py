"""Q-proportion JRPG body blocks (tunic, stubby legs, fist hands) — side view +X."""

from __future__ import annotations

from typing import Sequence, Tuple

from sparkpix.canvas import Sprite
from sparkpix.color import ColorLike
from sparkpix import character as ch
from sparkpix import render as rd

ColorSeq = Sequence[ColorLike]


def draw_q_chest_bridge(
    s: Sprite,
    shoulder: Tuple[int, int],
    *,
    cloth: ColorSeq,
) -> None:
    """Upper chest under the jaw — connects head silhouette to torso (not a neck tube)."""
    sx, sy = shoulder
    y0, y1 = sy - 6, sy + 1
    s.rect(sx - 6, y0, sx + 4, y1, fill=cloth[0])
    s.rect(sx - 5, y0 + 1, sx + 3, y1, fill=cloth[1], only="opaque")
    s.rect(sx - 6, y0 + 2, sx - 2, y1 - 1, fill=cloth[0])
    s.px(sx - 3, y0 + 1, cloth[-1], only="opaque")


def draw_q_tunic_torso(
    s: Sprite,
    hip: Tuple[int, int],
    *,
    tunic: ColorSeq,
    pants: ColorSeq,
    squash: float = 1.0,
    collar: bool = True,
) -> None:
    """Short olive-style tunic + waist band (reference youth hero)."""
    hx, hy = hip
    sq = max(0.84, min(1.0, squash))
    extra = int((1.0 - sq) * 3)
    x0, x1 = hx - 6, hx + 6
    y0, y1 = hy - 7 + extra, hy + 2
    s.rect(x0, y0, x1, y1, fill=tunic[0])
    s.rect(x0 + 1, y0 + 1, x1 - 1, y1 - 1, fill=tunic[2], only="opaque")
    s.rect(x0 + 2, y0 + 2, x0 + 5, y0 + 6, fill=tunic[-1], only="opaque")
    s.rect(x1 - 2, y0 + 2, x1, y1 - 2, fill=tunic[0], only="opaque")
    s.rect(x0 - 2, y0 + 5, x0, y0 + 10, fill=tunic[0])
    s.px(x0 + 1, y0 + 1, tunic[-1])
    sy = hy - 1
    s.rect(x0, sy, x1, sy + 3, fill=pants[0])
    s.rect(x0 + 1, sy + 1, x1 - 1, sy + 4, fill=pants[1], only="opaque")
    if collar:
        s.rect(hx - 5, y0 - 3, hx + 6, y0 - 1, fill=tunic[1])
        s.rect(hx - 4, y0 - 2, hx + 5, y0 - 1, fill=tunic[2], only="opaque")
        s.px(hx - 2, y0 - 2, tunic[-1], only="opaque")


def draw_q_leg(
    s: Sprite,
    hip: Tuple[int, int],
    knee: Tuple[int, int],
    foot: Tuple[int, int],
    *,
    back: bool,
    pants: ColorSeq,
    boot: ColorSeq,
) -> None:
    tr = 2 if back else 3
    col = pants[0] if back else pants[2]
    rd.limb_shaded(s, hip, knee, tr, pants if not back else pants[:3])
    rd.limb_shaded(s, knee, foot, tr, pants)
    ch.limb(s, knee, foot, tr, pants[1])
    fx, fy = foot
    s.rect(fx - 3, fy - 2, fx + 4, fy, fill=boot[0] if back else boot[1])
    s.rect(fx - 2, fy, fx + 5, fy + 1, fill=boot[0])


def draw_q_arm_sleeve(
    s: Sprite,
    shoulder: Tuple[int, int],
    elbow: Tuple[int, int],
    hand: Tuple[int, int],
    *,
    tunic: ColorSeq,
    skin: ColorSeq,
    fist: bool = True,
) -> None:
    ch.limb(s, shoulder, elbow, 2, tunic[2])
    ch.limb(s, elbow, hand, 2, skin[2])
    hx, hy = hand
    if fist:
        s.rect(hx - 1, hy - 1, hx + 2, hy + 2, fill=skin[2])
        s.rect(hx, hy, hx + 2, hy + 2, fill=skin[1], only="opaque")
        s.px(hx + 2, hy, skin[0])
        s.px(hx, hy - 1, tunic[1], only="opaque")


def draw_q_long_coat_torso(
    s: Sprite,
    hip: Tuple[int, int],
    *,
    coat: ColorSeq,
    shirt: ColorSeq,
    pants: ColorSeq,
    belt: ColorSeq,
    squash: float = 1.0,
) -> None:
    """Long open coat, visible shirt panel, belt — side view +X."""
    hx, hy = hip
    sq = max(0.84, min(1.0, squash))
    extra = int((1.0 - sq) * 3)
    x0, x1 = hx - 6, hx + 7
    y0, y1 = hy - 8 + extra, hy + 5
    s.rect(hx - 5, y0 - 3, hx + 1, y0 - 1, fill=coat[0])
    s.rect(hx - 4, y0 - 2, hx, y0 - 1, fill=coat[1], only="opaque")
    s.rect(x0, y0, x1, y1, fill=coat[0])
    s.rect(x0 + 1, y0 + 1, x1 - 1, y1 - 1, fill=coat[1], only="opaque")
    s.rect(x0 + 2, y0 + 2, x0 + 6, y0 + 9, fill=shirt[2], only="opaque")
    s.rect(x0 + 3, y0 + 3, x0 + 5, y0 + 8, fill=shirt[-1], only="opaque")
    s.rect(x1 - 2, y0 + 2, x1, y1 - 3, fill=coat[0], only="opaque")
    s.rect(x0 - 2, y0 + 6, x0, y0 + 12, fill=coat[0])
    s.line(x0 + 1, y0 + 1, x0 + 1, y1 - 2, coat[-1])
    sy = hy + 1
    s.rect(x0, sy, x1 - 1, sy + 2, fill=belt[1])
    s.rect(x0 + 1, sy, x1 - 2, sy + 1, fill=belt[2], only="opaque")
    s.px(hx, sy, belt[0])
    py = hy + 3
    s.rect(x0 + 1, py, x1 - 2, py + 3, fill=pants[0])
    s.rect(x0 + 2, py + 1, x1 - 3, py + 4, fill=pants[1], only="opaque")
    s.polygon([(x1 - 1, y0 + 4), (x1 + 1, y0 + 10), (x1, y1 - 1), (x1 - 2, y0 + 8)], fill=coat[2], only="opaque")


def draw_q_arm_coat(
    s: Sprite,
    shoulder: Tuple[int, int],
    elbow: Tuple[int, int],
    hand: Tuple[int, int],
    *,
    coat: ColorSeq,
    shirt: ColorSeq,
    skin: ColorSeq,
    fist: bool = True,
) -> None:
    ch.limb(s, shoulder, elbow, 2, coat[2])
    s.px(elbow[0], elbow[1], shirt[1], only="opaque")
    ch.limb(s, elbow, hand, 2, coat[1])
    hx, hy = hand
    if fist:
        s.rect(hx - 1, hy - 1, hx + 2, hy + 2, fill=skin[2])
        s.rect(hx, hy, hx + 2, hy + 2, fill=skin[1], only="opaque")
        s.px(hx + 2, hy, skin[0])
        s.px(hx - 1, hy, coat[0], only="opaque")


def draw_q_elder_cape_torso(
    s: Sprite,
    hip: Tuple[int, int],
    shoulder: Tuple[int, int],
    *,
    cape: ColorSeq,
    tunic: ColorSeq,
    pants: ColorSeq,
    squash: float = 1.0,
) -> None:
    """Gold shoulder cape + brown tunic/pants (elder ref)."""
    hx, hy = hip
    sx, sy = shoulder
    sq = max(0.84, min(1.0, squash))
    extra = int((1.0 - sq) * 2)
    s.rect(sx - 7, sy - 5, sx + 5, sy + 3, fill=cape[1])
    s.rect(sx - 6, sy - 4, sx + 4, sy + 2, fill=cape[2], only="opaque")
    s.polygon([(sx - 7, sy - 3), (sx - 9, sy + 6), (sx - 2, sy + 8), (sx + 4, sy + 1)], fill=cape[0])
    s.px(sx - 4, sy - 3, cape[-1], only="opaque")
    y0, y1 = hy - 6 + extra, hy + 2
    s.rect(hx - 5, y0, hx + 5, y1, fill=tunic[1])
    s.rect(hx - 4, y0 + 1, hx + 4, y1 - 1, fill=tunic[2], only="opaque")
    s.rect(hx - 4, hy, hx + 4, hy + 4, fill=pants[0])
    s.rect(hx - 3, hy + 1, hx + 3, hy + 5, fill=pants[1], only="opaque")


def draw_q_dress_torso(
    s: Sprite,
    hip: Tuple[int, int],
    *,
    dress: ColorSeq,
    trim: ColorSeq,
    squash: float = 1.0,
) -> None:
    """Fitted bodice + flared skirt (heroine dress, side +X)."""
    hx, hy = hip
    sq = max(0.84, min(1.0, squash))
    extra = int((1.0 - sq) * 3)
    x0, x1 = hx - 6, hx + 7
    bodice_y0, bodice_y1 = hy - 8 + extra, hy + 1
    s.rect(x0, bodice_y0, x1, bodice_y1, fill=dress[0])
    s.rect(x0 + 1, bodice_y0 + 1, x1 - 1, bodice_y1 - 1, fill=dress[2], only="opaque")
    s.rect(x0 + 2, bodice_y0 + 2, x0 + 5, bodice_y0 + 6, fill=dress[-1], only="opaque")
    s.rect(x1 - 2, bodice_y0 + 2, x1, bodice_y1 - 2, fill=dress[0], only="opaque")
    s.rect(hx - 5, bodice_y0 - 3, hx + 6, bodice_y0 - 1, fill=trim[1])
    s.rect(hx - 4, bodice_y0 - 2, hx + 5, bodice_y0 - 1, fill=trim[-1], only="opaque")
    s.px(hx - 2, bodice_y0 - 2, trim[0])
    waist = hy + 1
    s.rect(x0, waist, x1, waist + 1, fill=trim[0])
    skirt_y0, skirt_y1 = waist + 1, hy + 8
    s.polygon([(x0, skirt_y0), (x1, skirt_y0), (x1 + 2, skirt_y1), (x0 - 1, skirt_y1)], fill=dress[0])
    s.polygon([(x0 + 1, skirt_y0 + 1), (x1 - 1, skirt_y0 + 1), (x1 + 1, skirt_y1 - 1), (x0, skirt_y1 - 1)], fill=dress[1], only="opaque")
    s.line(x0 + 2, skirt_y0 + 2, x0 + 1, skirt_y1 - 2, dress[-1])
    s.px(x1, skirt_y0 + 3, trim[-1], only="opaque")


def draw_q_chest_bridge_dress(
    s: Sprite,
    shoulder: Tuple[int, int],
    *,
    dress: ColorSeq,
) -> None:
    """Collar bridge under chin — dress fabric, not a neck."""
    sx, sy = shoulder
    y0, y1 = sy - 6, sy + 1
    s.rect(sx - 5, y0, sx + 4, y1, fill=dress[0])
    s.rect(sx - 4, y0 + 1, sx + 3, y1, fill=dress[2], only="opaque")
    s.px(sx - 2, y0 + 1, dress[-1], only="opaque")


def draw_q_arm_dress(
    s: Sprite,
    shoulder: Tuple[int, int],
    elbow: Tuple[int, int],
    hand: Tuple[int, int],
    *,
    dress: ColorSeq,
    trim: ColorSeq,
    skin: ColorSeq,
) -> None:
    """Puff sleeve + open hand (heroine)."""
    ch.limb(s, shoulder, elbow, 3, dress[1])
    s.px(shoulder[0], shoulder[1], trim[-1], only="opaque")
    s.px(elbow[0] - 1, elbow[1], dress[-1], only="opaque")
    ch.limb(s, elbow, hand, 2, skin[2])
    hx, hy = hand
    s.rect(hx - 1, hy - 2, hx + 2, hy + 1, fill=skin[2])
    s.px(hx, hy - 2, skin[-1], only="opaque")
    s.px(hx + 2, hy, skin[1], only="opaque")


def draw_q_leg_dress(
    s: Sprite,
    hip: Tuple[int, int],
    knee: Tuple[int, int],
    foot: Tuple[int, int],
    *,
    back: bool,
    stockings: ColorSeq,
    shoe: ColorSeq,
) -> None:
    tr = 2 if back else 3
    rd.limb_shaded(s, hip, knee, tr, stockings if not back else stockings[:3])
    rd.limb_shaded(s, knee, foot, tr, stockings)
    ch.limb(s, knee, foot, tr, stockings[1])
    fx, fy = foot
    s.rect(fx - 2, fy - 1, fx + 4, fy + 1, fill=shoe[1] if not back else shoe[0])
    s.px(fx + 3, fy, shoe[-1], only="opaque")
