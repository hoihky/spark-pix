"""Platform fighter profile head (+X): ref-traced hair, forward eye, blush."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Sequence

from sparkpix.canvas import Sprite
from sparkpix.color import ColorLike
from sparkpix import jrpg_face as jf
from sparkpix.platform_ref_face import draw_ref_male_hero_face
from sparkpix.platform_ref_hair import draw_ref_male_hero_hair
from sparkpix.platform_style import face_y_from_head_joint

ColorSeq = Sequence[ColorLike]
HeadLayer = Literal["full", "hair_back", "face_front", "fringe"]

_HQ = 0
_HQB = 0


@dataclass
class FighterHeadLook:
    """
    Platform fighter face knobs (document in ``PROMPT.md`` and ``references/hero-config.md``).

    hair_style:
        ``ref_design`` — traced male_hero sheet silhouette; change colors via ``HAIR`` ramp only.
        ``hero_spiky`` — JRPG spiky crown + short nape @ q=0.
    eye_style:
        ``forward`` — 4×3 fighter eye (default).
    show_blush: cheek pixels on or off.
    compact: scale tweaks for anchored P128 skeleton.
    """

    hair_style: str = "ref_design"
    eye_style: str = "forward"
    show_blush: bool = True
    compact: bool = True


def _head_cy(cy: int, hair_style: str) -> int:
    """``ref_design``: facial stamp row from skeleton head joint Y (see ``P128.face``)."""
    if hair_style == "ref_design":
        return face_y_from_head_joint(cy)
    return cy


def _draw_face_base(
    s: Sprite,
    cx: int,
    cy: int,
    skin: ColorSeq,
    blush: ColorLike,
    *,
    blush_on: bool,
    hair_style: str,
    eye_kw: dict | None = None,
    hair_sway: int = 0,
) -> None:
    hcy = _head_cy(cy, hair_style)
    if hair_style == "ref_design":
        kw = eye_kw or {}
        draw_ref_male_hero_face(
            s,
            cx,
            hcy,
            skin,
            pupil=kw.get("pupil", skin[0]),
            iris=kw.get("iris", skin[-1]),
            sclera=kw.get("sclera", "#ffffff"),
            sway=hair_sway,
            layer="skin",
        )
    else:
        jf._draw_face_skin_youth(s, cx, hcy, skin, q=_HQ, qb=_HQB)
        if blush_on:
            s.px(cx + 6, hcy + 4, blush, only="opaque")
            s.px(cx + 7, hcy + 5, blush, only="opaque")


def _draw_forward_eye(
    s: Sprite,
    cx: int,
    cy: int,
    *,
    pupil: ColorLike,
    sclera: ColorLike,
    iris: ColorLike,
    paper: ColorLike,
    brow: ColorLike,
    hair_style: str,
) -> None:
    hcy = _head_cy(cy, hair_style)
    if hair_style == "ref_design":
        return
    else:
        ex, ey = cx + 4, hcy + 1
        s.px(ex, ey - 1, brow, only="opaque")
        s.px(ex, ey, iris)
        s.px(ex + 1, ey, sclera)
        s.px(ex + 2, ey, sclera)
        s.px(ex + 1, ey + 1, sclera)
        s.px(ex, ey + 1, pupil)
        s.px(ex + 1, ey, paper, only="opaque")


def _draw_hair_jrpg(s: Sprite, cx: int, cy: int, hair: ColorSeq, sway: int, *, layer: HeadLayer) -> None:
    hx, hy = cx + sway, cy
    if layer in ("full", "hair_back"):
        jf._draw_hair_back_short(s, hx, hy, hair, q=0, qb=0)
    if layer in ("full", "face_front"):
        jf._draw_hair_crown_base(s, hx, hy, hair, q=0, qt=0)
        jf._draw_hair_style_spiky(s, hx, hy, hair, q=0, qt=0)
        jf._draw_fringe_bangs(s, hx, hy, hair, style="spiky", q=0, qt=0)
        jf._draw_hair_finish(s, hx, hy, hair, paper="#ffffff", q=0, qt=0, qb=0)


def _draw_hair(s: Sprite, cx: int, cy: int, hair: ColorSeq, sway: int, style: str, *, layer: HeadLayer) -> None:
    hcy = _head_cy(cy, style)
    if style == "ref_design":
        draw_ref_male_hero_hair(s, cx, hcy, hair, sway=sway, layer=layer)
        return
    _draw_hair_jrpg(s, cx, cy, hair, sway, layer=layer)


def _draw_ref_full_head(
    s: Sprite,
    cx: int,
    cy: int,
    *,
    skin: ColorSeq,
    hair: ColorSeq,
    blush: ColorLike,
    sway: int,
    cfg: FighterHeadLook,
    eye_kw: dict,
) -> None:
    draw_ref_male_hero_hair(s, cx, _head_cy(cy, "ref_design"), hair, sway=sway, layer="hair_back")
    _draw_face_base(
        s, cx, cy, skin, blush, blush_on=cfg.show_blush, hair_style="ref_design", eye_kw=eye_kw, hair_sway=sway
    )
    draw_ref_male_hero_hair(s, cx, _head_cy(cy, "ref_design"), hair, sway=sway, layer="face_front")
    draw_ref_male_hero_hair(s, cx, _head_cy(cy, "ref_design"), hair, sway=sway, layer="fringe")
    draw_ref_male_hero_face(
        s,
        cx,
        _head_cy(cy, "ref_design"),
        skin,
        pupil=eye_kw["pupil"],
        iris=eye_kw["iris"],
        sclera=eye_kw["sclera"],
        sway=sway,
        layer="eye",
    )


def draw_fighter_profile_head(
    s: Sprite,
    cx: int,
    cy: int,
    *,
    skin: ColorSeq,
    hair: ColorSeq,
    pupil: ColorLike,
    iris: ColorLike,
    sclera: ColorLike,
    paper: ColorLike,
    blush: ColorLike,
    look: FighterHeadLook | None = None,
    hair_sway: int = 0,
    layers: HeadLayer = "full",
) -> None:
    cfg = look or FighterHeadLook()
    eye_kw = dict(pupil=pupil, sclera=sclera, iris=iris, paper=paper, brow=hair[0])

    if cfg.hair_style == "ref_design" and layers == "full":
        _draw_ref_full_head(s, cx, cy, skin=skin, hair=hair, blush=blush, sway=hair_sway, cfg=cfg, eye_kw=eye_kw)
        return

    if layers == "hair_back":
        _draw_hair(s, cx, cy, hair, hair_sway, cfg.hair_style, layer="hair_back")
        return

    if layers == "face_front":
        if cfg.hair_style == "ref_design":
            _draw_face_base(
                s,
                cx,
                cy,
                skin,
                blush,
                blush_on=cfg.show_blush,
                hair_style=cfg.hair_style,
                eye_kw=eye_kw,
                hair_sway=hair_sway,
            )
            draw_ref_male_hero_hair(
                s, cx, _head_cy(cy, "ref_design"), hair, sway=hair_sway, layer="face_front"
            )
            draw_ref_male_hero_hair(s, cx, _head_cy(cy, "ref_design"), hair, sway=hair_sway, layer="fringe")
            draw_ref_male_hero_face(
                s,
                cx,
                _head_cy(cy, "ref_design"),
                skin,
                pupil=eye_kw["pupil"],
                iris=eye_kw["iris"],
                sclera=eye_kw["sclera"],
                sway=hair_sway,
                layer="eye",
            )
        else:
            _draw_face_base(s, cx, cy, skin, blush, blush_on=cfg.show_blush, hair_style=cfg.hair_style)
            _draw_hair(s, cx, cy, hair, hair_sway, cfg.hair_style, layer="face_front")
            if cfg.eye_style == "forward":
                _draw_forward_eye(s, cx, cy, **eye_kw, hair_style=cfg.hair_style)
        return

    _draw_hair(s, cx, cy, hair, hair_sway, cfg.hair_style, layer="full")
    _draw_face_base(s, cx, cy, skin, blush, blush_on=cfg.show_blush, hair_style=cfg.hair_style)
    if cfg.eye_style == "forward":
        _draw_forward_eye(s, cx, cy, **eye_kw, hair_style=cfg.hair_style)
