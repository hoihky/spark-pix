"""Reusable drawing helpers for production humanoid / platformer sprites."""

from __future__ import annotations

import math
from typing import Callable, Sequence, Tuple, Union

from PIL import Image

from sparkpix.canvas import Sprite
from sparkpix.color import RGBA, ColorLike
from sparkpix import draw_ops
from sparkpix.jrpg_face import JrpgHeadLook, draw_jrpg_eye, draw_jrpg_profile_head
from sparkpix.platform_face import FighterHeadLook, draw_fighter_profile_head

ColorSeq = Sequence[ColorLike]


def drop_shadow_oval(
    s: Sprite,
    center_x: int,
    foot_y: int,
    color: ColorLike,
    half_w: int = 7,
) -> None:
    cy = foot_y + 1
    for dx in range(-half_w, half_w + 1):
        for dy in range(0, 3):
            if (dx * dx) / max(1, half_w * half_w) + (dy * dy) / 4.0 <= 1.0:
                s.px(center_x + dx, cy + dy, color)


def limb(
    s: Sprite,
    p0: Tuple[int, int],
    p1: Tuple[int, int],
    radius: int,
    color: ColorLike,
    only: ColorLike = None,
) -> None:
    s.capsule(p0[0], p0[1], p1[0], p1[1], radius, color, only=only)


def platformer_leg(
    s: Sprite,
    hip: Tuple[int, int],
    knee: Tuple[int, int],
    foot: Tuple[int, int],
    *,
    back: bool,
    shorts: ColorSeq,
    boot: ColorSeq,
    boot_dark: ColorSeq,
    thigh_radius: int | None = None,
    shin_radius: int | None = None,
) -> None:
    """Filled thigh/shin + boot block (platformer baseline, ramp-shaded)."""
    tr = thigh_radius if thigh_radius is not None else (2 if back else 3)
    sr = shin_radius if shin_radius is not None else tr
    from sparkpix import render as rd

    rd.limb_shaded(s, hip, knee, tr, shorts)
    rd.limb_shaded(s, knee, foot, sr, shorts)
    fx, fy = foot
    s.rect(fx - 4, fy - 2, fx + 5, fy, fill=boot[0] if back else boot[1])
    s.rect(fx - 3, fy, fx + 6, fy + 1, fill=boot_dark[1])
    if not back:
        s.px(fx + 5, fy - 1, boot[2] if len(boot) > 2 else boot[1])
        s.px(fx + 4, fy - 2, boot[-1], only="opaque")
        s.px(fx - 3, fy - 1, boot[0], only="opaque")


def torso_hoodie(
    s: Sprite,
    hip: Tuple[int, int],
    *,
    squash: float,
    hood: ColorSeq,
    shirt: ColorSeq,
    shorts: ColorSeq,
    width_half: int = 6,
    cute: bool = False,
) -> None:
    """Hoodie + shirt panel + shorts waist (side view +X, upper-left light)."""
    hx, hy = hip
    sq = max(0.82, min(1.0, squash))
    extra = int((1.0 - sq) * 4)
    torso_h = 8 if cute else 13
    wh = width_half + (1 if cute else 0)
    x0, x1 = hx - wh, hx + wh
    y0, y1 = hy - torso_h + extra, hy + 2
    s.rect(x0, y0, x1, y1, fill=hood[0])
    s.rect(x0 + 1, y0 + 1, x1 - 1, y1 - 1, fill=hood[1])
    s.rect(x0 + 1, y0 + 1, x1 - 1, y1 - 1, fill=hood[2], only="opaque")
    s.rect(x0 + 1, y0 + 2, x1 - 2, y0 + 8, fill=shirt[1], only="opaque")
    s.rect(x0 + 2, y0 + 2, x0 + 5, y0 + 5, fill=shirt[-1], only="opaque")
    s.rect(x1 - 2, y0 + 3, x1, y1 - 3, fill=hood[0], only="opaque")
    s.rect(x0 - 2, y0 + 6, x0, y0 + 12, fill=hood[0])
    s.px(x0 + 1, y0 + 1, hood[-1])
    s.px(x0 + 2, y0 + 1, hood[-1], only="opaque")
    sy = hy - 1
    s.rect(x0, sy, x1, sy + 4, fill=shorts[0])
    s.rect(x0 + 1, sy + 1, x1 - 1, sy + 5, fill=shorts[1], only="opaque")
    s.rect(x0 + 1, sy + 2, x1 - 2, sy + 3, fill=shorts[-1], only="opaque")
    if cute:
        # Hood collar under chin — bridges big Q head to torso
        s.rect(hx - 5, y0 - 4, hx + 6, y0 - 1, fill=hood[1])
        s.rect(hx - 4, y0 - 3, hx + 5, y0 - 2, fill=hood[2], only="opaque")
        s.px(hx - 3, y0 - 3, hood[-1], only="opaque")


def fighter_head_facing_right(
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
    layers: str = "full",
) -> None:
    """Platform fighter head (+X): forward eye + spiky hair + optional blush."""
    draw_fighter_profile_head(
        s,
        cx,
        cy,
        skin=skin,
        hair=hair,
        pupil=pupil,
        iris=iris,
        sclera=sclera,
        paper=paper,
        blush=blush,
        look=look,
        hair_sway=hair_sway,
        layers=layers,
    )


def profile_head_facing_right(
    s: Sprite,
    cx: int,
    cy: int,
    *,
    skin: ColorSeq,
    hair: ColorSeq,
    band: ColorSeq,
    eye_green: ColorLike,
    sclera: ColorLike,
    paper: ColorLike = "#f4f4ec",
    pupil: ColorLike = "#282830",
    lash: ColorLike | None = None,
    iris_shadow: ColorLike | None = None,
    look: JrpgHeadLook | None = None,
    cute: bool = False,
) -> None:
    """
    JRPG profile head (+X): shared hair + eye drawer (no mouth).

    Tune ``look`` (:class:`JrpgHeadLook`) and ramps in each hero ``PROMPT.md``.
    """
    draw_jrpg_profile_head(
        s,
        cx,
        cy,
        skin=skin,
        hair=hair,
        band=band,
        iris=eye_green,
        pupil=pupil,
        paper=paper,
        sclera=sclera,
        iris_shadow=iris_shadow,
        lash=lash,
        look=look,
        cute=cute,
    )


def mech_head_facing_right(
    s: Sprite,
    cx: int,
    cy: int,
    *,
    chassis: ColorSeq,
    accent: ColorSeq,
    dark: ColorLike,
    paper: ColorLike,
    visor_glow: bool = False,
    cute: bool = False,
) -> None:
    """Robot profile (+X): helmet + visor eye (no mouth vent). ``cute`` = Q-scale dome."""
    q = 2 if cute else 0
    qt = 1 if cute else 0
    s.rect(cx - 5 - q // 2, cy - 4 - qt, cx + 7 + q, cy + 9 + (1 if cute else 0), fill=chassis[1])
    s.rect(cx - 4 - q // 2, cy - 3 - qt, cx + 6 + q, cy + 8 + (1 if cute else 0), fill=chassis[2], only="opaque")
    s.rect(cx - 3 - q // 2, cy - 2 - qt, cx + 5 + q, cy + 2, fill=chassis[3], only="opaque")
    iris = accent[3] if visor_glow else accent[2]
    draw_jrpg_eye(
        s,
        cx,
        cy,
        style="vertical",
        iris=iris,
        pupil=dark,
        paper=paper,
        iris_shadow=accent[0],
        brow=chassis[0],
        cute=cute,
    )
    s.line(cx + 3, cy - 4 - qt, cx + 3, cy - 8 - qt, chassis[0])
    s.px(cx + 3, cy - 8 - qt, accent[3])
    s.px(cx + 6 + q // 2, cy - 2 - qt, chassis[3])
    s.px(cx - 4 - q // 2, cy + 6 + (1 if cute else 0), chassis[0])
    s.px(cx + 1, cy + 5 + (1 if cute else 0), chassis[2], only="opaque")


def draw_humanoid_layer_order(
    *,
    draw_back_leg: Callable[[], None],
    draw_back_arm: Callable[[], None],
    draw_weapon_back: Callable[[], None] | None,
    draw_torso: Callable[[], None],
    draw_front_leg: Callable[[], None],
    draw_head: Callable[[], None],
    draw_front_arm: Callable[[], None],
    draw_weapon_front: Callable[[], None] | None,
    draw_vfx: Callable[[], None] | None = None,
    outline_ink: ColorLike | None = None,
    sprite: Sprite | None = None,
) -> None:
    """Standard z-order + optional outside outline (platformer / RPG side view)."""
    draw_back_leg()
    draw_back_arm()
    if draw_weapon_back:
        draw_weapon_back()
    draw_torso()
    draw_front_leg()
    draw_head()
    draw_front_arm()
    if draw_weapon_front:
        draw_weapon_front()
    if draw_vfx:
        draw_vfx()
    if outline_ink is not None and sprite is not None:
        finish_outside_outline(sprite, outline_ink)


def weapon_angle_trail(
    s: Sprite,
    hx: int,
    hy: int,
    angles: Sequence[float],
    length: float,
    fade: RGBA,
    bright: RGBA,
    thickness: int = 2,
) -> None:
    if len(angles) < 2:
        return
    for i in range(len(angles) - 1):
        col = fade if i < len(angles) - 3 else bright
        a0, a1 = angles[i], angles[i + 1]
        for step in range(10):
            ang = math.radians(a0 + (a1 - a0) * (step / 9))
            for u in range(0, int(length), 2):
                f = u / length
                px = int(hx + math.cos(ang) * length * f)
                py = int(hy + math.sin(ang) * length * f)
                s.px(px, py, col)
                if thickness >= 2:
                    s.px(px + 1, py, col)


def slash_downward(
    s: Sprite,
    cx: int,
    cy: int,
    *,
    fade: RGBA = (130, 210, 150, 95),
    bright: RGBA = (190, 255, 210, 170),
    span_deg: int = 55,
) -> None:
    """Downward strike crescent (tip travel top → bottom, character facing +X)."""
    slash_crescent(s, cx, cy, center_deg=92.0, span_deg=span_deg, radius_inner=8, radius_outer=24, fade=fade, bright=bright)


def slash_crescent(
    s: Sprite,
    cx: int,
    cy: int,
    center_deg: float,
    span_deg: int = 70,
    radius_inner: int = 10,
    radius_outer: int = 26,
    fade: RGBA = (130, 210, 150, 95),
    bright: RGBA = (190, 255, 210, 170),
) -> None:
    core = bright
    for deg in range(int(center_deg - span_deg // 2), int(center_deg + span_deg // 2), 2):
        rad = math.radians(deg)
        for dist in range(radius_inner, radius_outer, 2):
            px = int(cx + math.cos(rad) * dist)
            py = int(cy + math.sin(rad) * dist)
            col = core if dist > radius_inner + 12 else (bright if dist > radius_inner + 6 else fade)
            s.px(px, py, col)
            s.px(px + 1, py, col)
            s.px(px, py + 1, col)


def hilt_spark(s: Sprite, hx: int, hy: int, color: ColorLike) -> None:
    for dx, dy in ((0, 0), (1, -1), (-1, 0), (2, 0), (0, 1), (1, 1)):
        s.px(hx + dx, hy + dy, color)


def stamp_silhouette_ghost(
    s: Sprite,
    width: int,
    height: int,
    palette: Sequence[RGBA],
    ghost_color: RGBA,
    draw_fn: Callable[[Sprite], None],
) -> None:
    tmp = Sprite(width, height, palette=palette)
    draw_fn(tmp)
    img = tmp.flatten_frame(0)
    for y in range(height):
        for x in range(width):
            if img.getpixel((x, y))[3] > 0:
                s.px(x, y, ghost_color)


def finish_outside_outline(s: Sprite, ink: ColorLike) -> None:
    """Selective hull outline — call after full character on current layer."""
    s.outline(ink, where="outside")


def finish_production_humanoid(s: Sprite, ink: ColorLike, *, trim_specks: bool = True) -> None:
    """Outline + speck cleanup — preferred end pass for shipped humanoids."""
    from sparkpix import render as rd

    rd.finish_production_pass(s, ink, trim_specks=trim_specks)


def finish_selective_humanoid(
    s: Sprite,
    buckets: Sequence[tuple[Sequence[ColorLike], ColorLike]],
    *,
    fallback: ColorLike,
    trim_specks: bool = True,
) -> None:
    """Same-hue selective hull outline (platform / JRPG heroes)."""
    from sparkpix import render as rd

    rd.finish_production_selective(s, buckets, fallback=fallback, trim_specks=trim_specks)


def thin_leg_column_count(
    img: Image.Image,
    y0: int,
    y1: int,
    max_single_px_rows: int = 12,
) -> int:
    """Count rows in [y0,y1) with a 1px-wide opaque column (stick-leg detector)."""
    w, h = img.size
    thin = 0
    for y in range(y0, min(y1, h)):
        for x in range(w):
            if img.getpixel((x, y))[3] == 0:
                continue
            width = sum(1 for xx in range(max(0, x - 2), min(w, x + 3)) if img.getpixel((xx, y))[3] > 0)
            if width == 1:
                thin += 1
                break
    return thin


def warn_if_stick_legs(s: Sprite, foot_y: int, frame: int = 0, threshold: int = 12) -> None:
    img = s.flatten_frame(frame)
    y0 = max(0, foot_y - 18)
    count = thin_leg_column_count(img, y0, foot_y)
    if count > threshold:
        print("WARN: thin leg columns — use character.limb(..., radius>=3); see humanoid-hero.md")
