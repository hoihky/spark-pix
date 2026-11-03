"""
Side-view JRPG profile head (+X): volumetric **hair** + **eye**, no mouth.

16-bit JRPG read (see ``references/jrpg-profile-face.md``):
compact cheek patch, **2×3 vertical eye** (dark | white), **no neck** on Q bodies.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from sparkpix.canvas import Sprite
from sparkpix.color import ColorLike

ColorSeq = Sequence[ColorLike]


@dataclass
class JrpgHeadLook:
    """
    Art-direction knobs (document in each hero ``PROMPT.md``).

    hair_style:
        ``spiky`` — layered spikes + heavy forehead fringe.
        ``quiff`` — forward swoop + tall crown.
        ``short`` — cropped cap + small nape (no long tail).
        ``puffy`` — round volume + heavy fringe (elder ref).
    eye_style:
        ``vertical`` — 2×3 strip: pupil column + sclera column (youth ref).
        ``hero`` — dark vertical tick under brow (elder ref).
    forehead:
        ``none`` | ``bandana`` | ``wrap`` (thin strip).
    beard: hair ramp on lower face (hides jaw — no neck).
    fringe_over_eye: bangs shadow on **top row** of eye after it is drawn.
    """

    hair_style: str = "spiky"
    eye_style: str = "vertical"
    forehead: str = "bandana"
    beard: bool = False
    fringe_over_eye: bool = True


def _normalize_eye_style(style: str) -> str:
    return style


def _hair_tones(hair: ColorSeq) -> tuple[ColorLike, ColorLike, ColorLike, ColorLike]:
    dark = hair[0]
    mid = hair[2] if len(hair) > 2 else hair[1]
    light = hair[-1]
    hi = hair[4] if len(hair) > 4 else light
    return dark, mid, light, hi


def _draw_vertical_eye(
    s: Sprite,
    cx: int,
    cy: int,
    *,
    pupil: ColorLike,
    hi: ColorLike,
    sclera: ColorLike,
    cute: bool,
) -> tuple[int, int, int]:
    """2×3 vertical eye (youth ref): dark column | bright column."""
    ex = cx + 3
    ey = cy + 1
    h = 3
    s.rect(ex, ey, ex, ey + h - 1, fill=pupil)
    s.px(ex + 1, ey, hi)
    s.px(ex + 1, ey + 1, sclera)
    s.px(ex + 1, ey + 2, sclera)
    return ex, ey, h


def _draw_hero_eye_minimal(
    s: Sprite,
    cx: int,
    cy: int,
    *,
    pupil: ColorLike,
    brow: ColorLike,
    cute: bool,
) -> None:
    """Dark vertical tick (+ optional L) tucked under the hair brow — elder ref."""
    ex, ey = cx + 3, cy + 1
    s.px(ex, ey, pupil)
    s.px(ex, ey + 1, pupil)
    s.px(ex, ey + 2, pupil)
    if cute:
        s.px(ex + 1, ey + 2, pupil)
    s.px(ex, ey - 1, brow)
    s.px(ex + 1, ey - 1, brow)


def _apply_fringe_eye_cap(
    s: Sprite,
    ex: int,
    ey: int,
    *,
    pupil: ColorLike,
    sclera: ColorLike,
    hi: ColorLike,
    dark: ColorLike,
) -> None:
    """Bangs on top row; restore rows below (youth ref)."""
    s.px(ex, ey - 1, dark, only="opaque")
    s.px(ex + 1, ey - 1, dark, only="opaque")
    s.px(ex, ey, dark, only="opaque")
    s.px(ex + 1, ey, dark, only="opaque")
    s.px(ex, ey + 1, pupil)
    s.px(ex, ey + 2, pupil)
    s.px(ex + 1, ey + 1, sclera)
    s.px(ex + 1, ey + 2, sclera)
    s.px(ex + 1, ey, hi, only="opaque")


def _draw_hair_back(s: Sprite, cx: int, cy: int, hair: ColorSeq, *, q: int, qt: int, qb: int) -> None:
    dark, mid, light, _ = _hair_tones(hair)
    s.ellipse(cx - 11 - q, cy - 2 - qt, cx + 1, cy + 13 + qb, fill=dark)
    s.ellipse(cx - 10 - q, cy - 1 - qt, cx + 2, cy + 12 + qb, fill=hair[1])
    s.rect(cx - 10 - q, cy + 4, cx - 7, cy + 14 + qb, fill=mid)
    s.polygon(
        [(cx - 11 - q, cy + 6), (cx - 12 - q, cy + 12 + qb), (cx - 9 - q, cy + 14 + qb), (cx - 8 - q, cy + 9)],
        fill=dark,
    )


def _draw_hair_back_short(s: Sprite, cx: int, cy: int, hair: ColorSeq, *, q: int, qb: int) -> None:
    """Short bob at nape + ear cover — no long tail."""
    dark, mid, light, _ = _hair_tones(hair)
    s.ellipse(cx - 9 - q, cy + 3, cx - 1, cy + 10 + qb, fill=dark)
    s.ellipse(cx - 8 - q, cy + 4, cx, cy + 9 + qb, fill=hair[1], only="opaque")
    s.ellipse(cx - 7 - q, cy + 6, cx - 3, cy + 10 + qb, fill=mid, only="opaque")
    s.px(cx - 6 - q, cy + 8, light, only="opaque")
    s.px(cx - 8 - q, cy + 7, dark)


def _draw_hair_crown_short(s: Sprite, cx: int, cy: int, hair: ColorSeq, *, q: int, qt: int) -> None:
    dark, mid, light, hi = _hair_tones(hair)
    s.ellipse(cx - 8 - q, cy - 6 - qt, cx + 5 + q, cy - 1, fill=dark)
    s.ellipse(cx - 7 - q, cy - 5 - qt, cx + 4 + q, cy - 2, fill=hair[1], only="opaque")
    s.ellipse(cx - 5 - q // 2, cy - 4 - qt, cx + 3 + q, cy - 2, fill=mid, only="opaque")
    s.px(cx, cy - 5 - qt, light)
    s.px(cx + 3 + q, cy - 3 - qt, hi, only="opaque")
    s.px(cx - 5, cy - 3 - qt, dark)
    s.rect(cx - 7 - q, cy - 1, cx - 4 - q, cy + 2, fill=hair[1], only="opaque")
    s.px(cx - 6 - q, cy + 1, mid)


def _draw_hair_style_short(s: Sprite, cx: int, cy: int, hair: ColorSeq, *, q: int, qt: int) -> None:
    dark, mid, light, hi = _hair_tones(hair)
    s.polygon(
        [(cx - 2, cy - 4 - qt), (cx + 2, cy - 5 - qt), (cx + 5 + q, cy - 3 - qt), (cx + 3, cy - 1)],
        fill=mid,
        only="opaque",
    )
    s.px(cx + 1, cy - 5 - qt, hi)
    s.px(cx + 4 + q, cy - 3 - qt, light, only="opaque")
    s.px(cx - 3, cy - 3 - qt, dark, only="opaque")


def _draw_hair_finish_short(s: Sprite, cx: int, cy: int, hair: ColorSeq, *, q: int, qb: int) -> None:
    dark, mid, _, hi = _hair_tones(hair)
    s.px(cx - 9 - q, cy + 6, dark)
    s.px(cx - 7 - q, cy + 9 + qb, dark)
    s.px(cx + 4 + q, cy - 2, hi, only="opaque")
    s.px(cx + 3 + q, cy, mid, only="opaque")


def _draw_face_skin_youth(s: Sprite, cx: int, cy: int, skin: ColorSeq, *, q: int, qb: int) -> None:
    """Youth ref: cheek + chin shadow, jaw meets hair/collar."""
    s.ellipse(cx - 5 - q // 2, cy - 1, cx + 6 + q, cy + 8 + qb, fill=skin[1])
    s.ellipse(cx - 4 - q // 2, cy, cx + 5 + q, cy + 7 + qb, fill=skin[2], only="opaque")
    s.rect(cx + 2, cy + 1, cx + 6 + q, cy + 6 + qb, fill=skin[2], only="opaque")
    s.px(cx + 6 + q, cy + 4, skin[0])
    s.px(cx + 5 + q // 2, cy + 2, skin[-1], only="opaque")
    s.px(cx + 2, cy + 5 + qb, skin[2])
    s.px(cx + 3, cy + 6 + qb, skin[1])
    s.px(cx + 1, cy + 6 + qb, skin[0])
    s.rect(cx - 3, cy + 6 + qb, cx + 1, cy + 9 + qb, fill=skin[1])
    s.px(cx - 2, cy + 8 + qb, skin[0])


def _draw_face_skin_compact(s: Sprite, cx: int, cy: int, skin: ColorSeq, *, q: int, qb: int) -> None:
    """Elder ref: tiny L-shaped cheek (beard covers the rest)."""
    s.ellipse(cx - 4 - q // 2, cy, cx + 5 + q, cy + 6 + qb, fill=skin[1])
    s.rect(cx + 2, cy + 1, cx + 5 + q, cy + 4, fill=skin[2], only="opaque")
    s.px(cx + 5 + q, cy + 3, skin[0])
    s.px(cx + 2, cy + 5 + qb, skin[0], only="opaque")


def _draw_hair_crown_base(s: Sprite, cx: int, cy: int, hair: ColorSeq, *, q: int, qt: int) -> None:
    dark, mid, light, hi = _hair_tones(hair)
    s.ellipse(cx - 10 - q, cy - 9 - qt, cx + 9 + q, cy - 1, fill=dark)
    s.ellipse(cx - 9 - q, cy - 8 - qt, cx + 8 + q, cy - 2, fill=hair[1])
    s.ellipse(cx - 7 - q // 2, cy - 6 - qt, cx + 7 + q, cy - 2, fill=mid, only="opaque")
    s.rect(cx - 5, cy - 5 - qt, cx + 6 + q, cy - 3 - qt, fill=light, only="opaque")
    s.line(cx - 6 - q, cy - 7 - qt, cx + 2, cy - 9 - qt, hi)
    s.px(cx + 4, cy - 8 - qt, hi)
    s.px(cx - 4, cy - 7 - qt, dark)


def _draw_hair_style_spiky(s: Sprite, cx: int, cy: int, hair: ColorSeq, *, q: int, qt: int) -> None:
    """Shaggy spikes +X (forward) with cyan streaks — not a flat helmet."""
    dark, mid, light, hi = _hair_tones(hair)
    s.polygon(
        [(cx - 8 - q, cy - 7 - qt), (cx - 4, cy - 11 - qt), (cx - 1, cy - 8 - qt), (cx - 5, cy - 5 - qt)],
        fill=mid,
    )
    s.polygon(
        [(cx - 2, cy - 10 - qt), (cx + 3, cy - 11 - qt), (cx + 2, cy - 7 - qt), (cx - 2, cy - 7 - qt)],
        fill=light,
    )
    s.polygon(
        [(cx + 1, cy - 10 - qt), (cx + 7 + q, cy - 8 - qt), (cx + 6 + q, cy - 4 - qt), (cx + 2, cy - 6 - qt)],
        fill=mid,
    )
    s.polygon(
        [(cx + 5, cy - 9 - qt), (cx + 11 + q, cy - 6 - qt), (cx + 10 + q, cy - 2), (cx + 6, cy - 4 - qt)],
        fill=light,
    )
    s.polygon(
        [(cx + 7, cy - 5 - qt), (cx + 12 + q, cy - 2 - qt), (cx + 11 + q, cy + 2), (cx + 7, cy + 1)],
        fill=mid,
    )
    s.polygon(
        [(cx + 9 + q, cy - 4 - qt), (cx + 13 + q, cy - 1), (cx + 12 + q, cy + 3), (cx + 8 + q, cy + 1)],
        fill=hair[3] if len(hair) > 3 else light,
    )
    s.line(cx - 3, cy - 10 - qt, cx + 4, cy - 11 - qt, hi)
    s.line(cx + 5, cy - 9 - qt, cx + 11 + q, cy - 7 - qt, hi)
    s.px(cx + 10 + q, cy - 3 - qt, hi)
    s.px(cx + 12 + q, cy, dark)
    s.px(cx + 6, cy - 8 - qt, dark)
    s.px(cx - 6, cy - 8 - qt, dark)


def _draw_hair_style_quiff(s: Sprite, cx: int, cy: int, hair: ColorSeq, *, q: int, qt: int) -> None:
    dark, mid, light, hi = _hair_tones(hair)
    s.polygon([(cx - 5, cy - 8 - qt), (cx + 2, cy - 10 - qt), (cx + 8 + q, cy - 6 - qt), (cx + 6 + q, cy - 2)], fill=hair[1])
    s.polygon([(cx + 2, cy - 9 - qt), (cx + 9 + q, cy - 7 - qt), (cx + 8 + q, cy - 3 - qt), (cx + 4, cy - 5 - qt)], fill=light)
    s.line(cx + 3, cy - 9 - qt, cx + 8 + q, cy - 8 - qt, hi)
    s.px(cx + 7 + q, cy - 4 - qt, dark)
    s.px(cx - 4, cy - 7 - qt, mid)


def _draw_forehead(s: Sprite, cx: int, cy: int, band: ColorSeq, *, kind: str, q: int, qt: int) -> None:
    if kind == "none":
        return
    if kind == "wrap":
        s.rect(cx - 4 - q // 2, cy - 5 - qt, cx + 5 + q, cy - 4 - qt, fill=band[1])
        s.rect(cx - 3, cy - 4 - qt, cx + 4, cy - 4 - qt, fill=band[2], only="opaque")
        s.px(cx + 1, cy - 4 - qt, band[0])
        return
    s.rect(cx - 5 - q // 2, cy - 6 - qt, cx + 7 + q, cy - 5 - qt, fill=band[1])
    s.rect(cx - 4 - q // 2, cy - 5 - qt, cx + 6 + q, cy - 5 - qt, fill=band[2], only="opaque")
    s.px(cx + 2, cy - 5 - qt, band[0])
    s.px(cx - 7 - q // 2, cy - 5 - qt, band[2])


def _draw_fringe_bangs(
    s: Sprite,
    cx: int,
    cy: int,
    hair: ColorSeq,
    *,
    style: str,
    q: int,
    qt: int,
) -> None:
    """Forehead bang volume (before eye); does not paint over the eye strip."""
    dark, mid, light, hi = _hair_tones(hair)
    if style == "short":
        s.polygon(
            [(cx, cy - 3 - qt), (cx + 4 + q, cy - 4 - qt), (cx + 6 + q, cy - 2), (cx + 3, cy - 1)],
            fill=mid,
            only="opaque",
        )
        s.px(cx + 2, cy - 3 - qt, light)
        s.px(cx + 5 + q, cy - 2, dark, only="opaque")
        return
    if style == "puffy":
        s.polygon(
            [(cx - 3, cy - 5 - qt), (cx + 3, cy - 6 - qt), (cx + 8 + q, cy - 3 - qt), (cx + 4, cy - 1)],
            fill=mid,
        )
        s.px(cx + 1, cy - 5 - qt, dark)
        s.px(cx + 6 + q, cy - 3 - qt, light)
        return
    if style == "quiff":
        s.polygon([(cx + 1, cy - 3 - qt), (cx + 6 + q, cy - 2 - qt), (cx + 5 + q, cy + 1), (cx + 2, cy + 1)], fill=mid)
        s.px(cx + 4 + q, cy - 1 - qt, dark)
        return
    s.polygon(
        [(cx - 2, cy - 5 - qt), (cx + 3, cy - 7 - qt), (cx + 9 + q, cy - 3 - qt), (cx + 5, cy - 1)],
        fill=mid,
    )
    s.polygon(
        [(cx + 2, cy - 6 - qt), (cx + 8 + q, cy - 4 - qt), (cx + 10 + q, cy - 1), (cx + 6, cy + 1)],
        fill=light,
    )
    s.line(cx + 3, cy - 6 - qt, cx + 9 + q, cy - 3 - qt, hi)
    s.px(cx + 1, cy - 4 - qt, hi)


def _draw_hair_style_puffy(s: Sprite, cx: int, cy: int, hair: ColorSeq, *, q: int, qt: int) -> None:
    dark, mid, light, hi = _hair_tones(hair)
    s.ellipse(cx - 7 - q, cy - 7 - qt, cx + 7 + q, cy - 2, fill=hair[1])
    s.ellipse(cx - 6 - q, cy - 6 - qt, cx + 6 + q, cy - 3, fill=light, only="opaque")
    s.px(cx - 2, cy - 6 - qt, hi)
    s.px(cx + 4 + q, cy - 4 - qt, dark, only="opaque")


def _draw_hair_back_puffy(s: Sprite, cx: int, cy: int, hair: ColorSeq, *, q: int, qt: int, qb: int) -> None:
    dark, mid, light, hi = _hair_tones(hair)
    s.ellipse(cx - 11 - q, cy - 1 - qt, cx + 2, cy + 12 + qb, fill=dark)
    s.ellipse(cx - 10 - q, cy, cx + 3, cy + 11 + qb, fill=hair[1])
    s.rect(cx - 10 - q, cy + 3, cx - 6, cy + 13 + qb, fill=mid)
    s.px(cx - 9 - q, cy + 6, light)
    s.px(cx - 11 - q, cy + 9, hi, only="opaque")


def _draw_beard_bushy(s: Sprite, cx: int, cy: int, hair: ColorSeq, *, qb: int) -> None:
    """Large beard onto chest — hides jaw/neck (elder ref)."""
    dark, mid, light, hi = _hair_tones(hair)
    s.polygon([(cx - 6, cy + 3), (cx - 9, cy + 14 + qb), (cx + 1, cy + 16 + qb), (cx + 4, cy + 5)], fill=mid)
    s.polygon([(cx - 5, cy + 5), (cx - 7, cy + 12 + qb), (cx + 0, cy + 14 + qb), (cx + 2, cy + 6)], fill=light)
    s.polygon([(cx - 8, cy + 8), (cx - 10, cy + 15 + qb), (cx - 4, cy + 17 + qb), (cx - 5, cy + 10)], fill=hi)
    s.px(cx - 7, cy + 11, dark)
    s.rect(cx - 8, cy + 12, cx - 4, cy + 16 + qb, fill=mid)


def _draw_hair_finish(s: Sprite, cx: int, cy: int, hair: ColorSeq, *, paper: ColorLike, q: int, qt: int, qb: int) -> None:
    dark, mid, light, hi = _hair_tones(hair)
    s.polygon(
        [(cx - 11 - q, cy + 1), (cx - 12 - q, cy + 8), (cx - 9 - q, cy + 12 + qb), (cx - 8 - q, cy + 4)],
        fill=hair[1],
    )
    s.px(cx - 11 - q, cy + 4, hi)
    s.px(cx - 12 - q, cy + 7, dark)
    s.px(cx + 9 + q, cy + 1, dark)
    s.px(cx + 10 + q, cy - 2 - qt, dark)
    s.px(cx + 11 + q, cy - 1, light, only="opaque")
    s.rect(cx - 7 - q // 2, cy + 2, cx - 4, cy + 8 + qb, fill=mid)
    s.px(cx - 5, cy + 4, light)
    s.px(cx - 6, cy + 8 + qb, dark)
    s.px(cx - 3, cy - 7 - qt, hi, only="opaque")


def draw_jrpg_eye(
    s: Sprite,
    cx: int,
    cy: int,
    *,
    style: str,
    iris: ColorLike,
    pupil: ColorLike,
    paper: ColorLike,
    sclera: ColorLike = "#e8ece8",
    iris_shadow: ColorLike | None = None,
    brow: ColorLike,
    cute: bool = True,
    draw_brow: bool = True,
) -> None:
    """Eye only — ``vertical`` or ``hero`` (see :class:`JrpgHeadLook`)."""
    _ = iris, iris_shadow, draw_brow
    eye = _normalize_eye_style(style)
    if eye == "hero":
        _draw_hero_eye_minimal(s, cx, cy, pupil=pupil, brow=brow, cute=cute)
    else:
        _draw_vertical_eye(s, cx, cy, pupil=pupil, hi=paper, sclera=sclera, cute=cute)


def draw_jrpg_profile_head(
    s: Sprite,
    cx: int,
    cy: int,
    *,
    skin: ColorSeq,
    hair: ColorSeq,
    band: ColorSeq,
    iris: ColorLike,
    pupil: ColorLike,
    paper: ColorLike = "#f4f4f4",
    sclera: ColorLike = "#e8ece8",
    iris_shadow: ColorLike | None = None,
    lash: ColorLike | None = None,
    look: JrpgHeadLook | None = None,
    cute: bool = True,
) -> None:
    """Draw profile head (hair + eye, no mouth, no neck)."""
    cfg = look or JrpgHeadLook()
    dark_hair, _, _, _ = _hair_tones(hair)
    brow = lash if lash is not None else dark_hair
    _ = iris, iris_shadow
    eye_style = _normalize_eye_style(cfg.eye_style)
    q = 2 if cute else 0
    qt = 1 if cute else 0
    qb = 1 if cute else 0

    if cfg.hair_style == "short":
        _draw_hair_back_short(s, cx, cy, hair, q=q, qb=qb)
    elif cfg.hair_style == "puffy":
        _draw_hair_back_puffy(s, cx, cy, hair, q=q, qt=qt, qb=qb)
    else:
        _draw_hair_back(s, cx, cy, hair, q=q, qt=qt, qb=qb)
    if cfg.beard:
        _draw_face_skin_compact(s, cx, cy, skin, q=q, qb=qb)
    elif cfg.hair_style == "spiky":
        _draw_face_skin_youth(s, cx, cy, skin, q=q, qb=qb)
    else:
        _draw_face_skin_youth(s, cx, cy, skin, q=q, qb=qb)
    if cfg.hair_style == "short":
        _draw_hair_crown_short(s, cx, cy, hair, q=q, qt=qt)
        _draw_hair_style_short(s, cx, cy, hair, q=q, qt=qt)
    elif cfg.hair_style == "puffy":
        _draw_hair_crown_base(s, cx, cy, hair, q=q, qt=qt)
        _draw_hair_style_puffy(s, cx, cy, hair, q=q, qt=qt)
    else:
        _draw_hair_crown_base(s, cx, cy, hair, q=q, qt=qt)
        if cfg.hair_style == "quiff":
            _draw_hair_style_quiff(s, cx, cy, hair, q=q, qt=qt)
        else:
            _draw_hair_style_spiky(s, cx, cy, hair, q=q, qt=qt)
    _draw_forehead(s, cx, cy, band, kind=cfg.forehead, q=q, qt=qt)
    _draw_fringe_bangs(s, cx, cy, hair, style=cfg.hair_style, q=q, qt=qt)

    if cfg.beard:
        _draw_beard_bushy(s, cx, cy, hair, qb=qb)

    if cfg.hair_style == "short":
        _draw_hair_finish_short(s, cx, cy, hair, q=q, qb=qb)
    else:
        _draw_hair_finish(s, cx, cy, hair, paper=paper, q=q, qt=qt, qb=qb)

    eye_anchor: tuple[int, int, int] | None = None
    if eye_style == "hero":
        _draw_hero_eye_minimal(s, cx, cy, pupil=pupil, brow=brow, cute=cute)
    else:
        eye_anchor = _draw_vertical_eye(s, cx, cy, pupil=pupil, hi=paper, sclera=sclera, cute=cute)
        if cfg.fringe_over_eye and eye_anchor is not None:
            ex, ey, _ = eye_anchor
            _apply_fringe_eye_cap(
                s, ex, ey, pupil=pupil, sclera=sclera, hi=paper, dark=dark_hair
            )

    s.px(cx - 1, cy + 3, skin[0])
