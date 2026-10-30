"""Reusable drawing helpers for production humanoid / platformer sprites."""

from __future__ import annotations

import math
from typing import Callable, Sequence, Tuple, Union

from PIL import Image

from sparkpix.canvas import Sprite
from sparkpix.color import RGBA, ColorLike
from sparkpix import draw_ops

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
    """Filled thigh/shin + boot block (platformer baseline)."""
    tr = thigh_radius if thigh_radius is not None else (2 if back else 3)
    sr = shin_radius if shin_radius is not None else tr
    col_u = shorts[0] if back else shorts[2]
    col_l = shorts[1]
    limb(s, hip, knee, tr, col_u)
    limb(s, knee, foot, sr, col_l)
    fx, fy = foot
    s.rect(fx - 4, fy - 2, fx + 5, fy, fill=boot[0] if back else boot[1])
    s.rect(fx - 3, fy, fx + 6, fy + 1, fill=boot_dark[1])
    if not back:
        s.px(fx + 5, fy - 1, boot[2] if len(boot) > 2 else boot[1])


def torso_hoodie(
    s: Sprite,
    hip: Tuple[int, int],
    *,
    squash: float,
    hood: ColorSeq,
    shirt: ColorSeq,
    shorts: ColorSeq,
    width_half: int = 6,
) -> None:
    """Hoodie + shirt panel + shorts waist (side view +X)."""
    hx, hy = hip
    sq = max(0.82, min(1.0, squash))
    extra = int((1.0 - sq) * 4)
    x0, x1 = hx - width_half, hx + width_half
    y0, y1 = hy - 13 + extra, hy + 2
    s.rect(x0, y0, x1, y1, fill=hood[1])
    s.rect(x0 + 1, y0 + 1, x1 - 1, y1 - 1, fill=hood[2], only="opaque")
    s.rect(x0 + 1, y0 + 2, x1 - 2, y0 + 8, fill=shirt[1], only="opaque")
    s.rect(x1 - 2, y0 + 3, x1, y1 - 3, fill=hood[0], only="opaque")
    s.rect(x0 - 2, y0 + 6, x0, y0 + 12, fill=hood[0])
    sy = hy - 1
    s.rect(x0, sy, x1, sy + 4, fill=shorts[2])
    s.rect(x0 + 1, sy + 1, x1 - 1, sy + 5, fill=shorts[1], only="opaque")


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
    mouth_shadow: ColorLike,
) -> None:
    """3/4 profile (+X): readable human face at 64×64 scale."""
    # back hair
    s.ellipse(cx - 9, cy - 3, cx + 1, cy + 11, fill=hair[0])
    s.ellipse(cx - 8, cy - 2, cx + 2, cy + 10, fill=hair[1], only="opaque")
    s.rect(cx - 8, cy + 6, cx - 5, cy + 11, fill=hair[1])
    # neck
    s.rect(cx - 2, cy + 7, cx + 1, cy + 10, fill=skin[1])
    # face mass (+X cheek)
    s.ellipse(cx - 5, cy - 4, cx + 7, cy + 8, fill=skin[1])
    s.ellipse(cx - 4, cy - 3, cx + 6, cy + 7, fill=skin[2], only="opaque")
    s.rect(cx + 3, cy, cx + 6, cy + 5, fill=skin[2], only="opaque")
    # jaw / chin (read as human at 8×)
    s.px(cx + 5, cy + 6, skin[1])
    s.px(cx + 6, cy + 5, skin[2])
    s.px(cx + 6, cy + 6, skin[0])
    # nose bridge + mouth
    s.px(cx + 6, cy + 1, skin[3] if len(skin) > 3 else skin[0])
    s.px(cx + 6, cy + 2, skin[3] if len(skin) > 3 else skin[0])
    s.px(cx + 5, cy + 2, skin[0])
    s.px(cx + 4, cy + 5, mouth_shadow)
    s.px(cx + 5, cy + 5, mouth_shadow)
    s.px(cx + 3, cy + 5, mouth_shadow)
    # bandana — forehead band only
    s.rect(cx - 4, cy - 8, cx + 7, cy - 5, fill=band[1])
    s.rect(cx - 3, cy - 7, cx + 6, cy - 6, fill=band[2], only="opaque")
    s.px(cx + 2, cy - 7, band[0])
    s.px(cx - 1, cy - 5, band[2])
    # front hair
    s.polygon(
        [(cx - 2, cy - 7), (cx + 3, cy - 11), (cx + 9, cy - 5), (cx + 7, cy - 1)],
        fill=hair[2],
    )
    s.polygon(
        [(cx + 3, cy - 4), (cx + 9, cy - 2), (cx + 8, cy + 4), (cx + 4, cy + 3)],
        fill=hair[3] if len(hair) > 3 else hair[2],
    )
    s.px(cx + 5, cy - 9, "#f4f4ec")
    s.px(cx + 4, cy - 6, hair[2] if len(hair) > 2 else hair[1])
    # eye block — 3×2 sclera + iris + highlight (camera-facing)
    ex, ey = cx + 2, cy
    s.rect(ex, ey, ex + 2, ey + 1, fill=sclera)
    s.px(ex + 1, ey + 1, eye_green)
    s.px(ex + 2, ey + 1, eye_green)
    s.px(ex + 2, ey, "#f4f4ec")
    s.px(ex + 2, ey, "#f4f4ec")
    s.px(ex + 3, ey + 1, skin[0])
    s.px(ex, ey - 1, hair[2] if len(hair) > 2 else hair[1])
    # ear hint (profile +X)
    s.px(cx - 1, cy + 2, skin[0])


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
    for deg in range(int(center_deg - span_deg // 2), int(center_deg + span_deg // 2), 3):
        rad = math.radians(deg)
        for dist in range(radius_inner, radius_outer, 2):
            px = int(cx + math.cos(rad) * dist)
            py = int(cy + math.sin(rad) * dist)
            col = bright if dist > radius_inner + 8 else fade
            s.px(px, py, col)
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
