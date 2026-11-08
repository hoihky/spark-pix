"""
Canonical 128×128 platform fighter draw order (see ``references/platform-fighter.md``).

Pack ``build.py`` files supply palette, knobs, outline buckets, and a rig dataclass;
this module owns layer order and gi arm attach offsets.
"""

from __future__ import annotations

from dataclasses import dataclass, replace, is_dataclass
from typing import Callable, Protocol, Sequence, Tuple

from sparkpix import character as ch
from sparkpix.canvas import Sprite
from sparkpix.color import ColorLike, parse_color
from sparkpix.hero_config import CharacterPalette, PlatformHeroKnobs
from sparkpix.platform_body import draw_arm_gi, draw_chest_bridge, draw_neck_bridge
from sparkpix.platform_face import FighterHeadLook
from sparkpix.platform_outfit import draw_platform_leg, draw_platform_torso
from sparkpix.platform_scarf import draw_scarf_mass
from sparkpix.platform_vfx import draw_slash_arc, draw_spark_streak

ColorBucket = tuple[Sequence[ColorLike], ColorLike]
ArmChain = tuple[Tuple[int, int], Tuple[int, int], Tuple[int, int]]


class PlatformFighterRig(Protocol):
    dy: int
    lean: int
    squash: float
    scarf_phase: float
    scarf_wave: int
    scarf_lift: int
    scarf_tip_dx: int | None
    scarf_tip_dy: int | None
    scarf_tip_world_x: int | None
    hair_sway: int
    foot_f: Tuple[int, int]
    foot_b: Tuple[int, int]
    knee_f: Tuple[int, int]
    knee_b: Tuple[int, int]
    hip: Tuple[int, int]
    shoulder: Tuple[int, int]
    elbow: Tuple[int, int]
    hand: Tuple[int, int]
    head: Tuple[int, int]
    neck: Tuple[int, int]
    slash: float
    spark: bool
    dash_ghost: bool
    scarf_stamp_clip: str | None
    scarf_stamp_frame: int


@dataclass(frozen=True)
class PlatformArmOffsets:
    """Gi arm attach vs ``P128`` joints — idle tuned to male_hero design sheet."""

    # ``back_*`` deltas apply to shoulder / elbow / hand; ``front_dy`` shifts the front chain.

    back_shoulder: Tuple[int, int] = (-6, 4)
    back_elbow: Tuple[int, int] = (-8, 9)
    back_hand: Tuple[int, int] = (-10, 11)
    front_dy: int = 2


DEFAULT_PLATFORM_ARM_OFFSETS = PlatformArmOffsets()


def back_arm_chain(r: PlatformFighterRig, off: PlatformArmOffsets = DEFAULT_PLATFORM_ARM_OFFSETS) -> ArmChain:
    return (
        (r.shoulder[0] + off.back_shoulder[0], r.shoulder[1] + off.back_shoulder[1]),
        (r.elbow[0] + off.back_elbow[0], r.elbow[1] + off.back_elbow[1]),
        (r.hand[0] + off.back_hand[0], r.hand[1] + off.back_hand[1]),
    )


def front_arm_chain(r: PlatformFighterRig, off: PlatformArmOffsets = DEFAULT_PLATFORM_ARM_OFFSETS) -> ArmChain:
    dy = off.front_dy
    return (
        (r.shoulder[0], r.shoulder[1] + dy),
        (r.elbow[0], r.elbow[1] + dy),
        (r.hand[0], r.hand[1] + dy),
    )


@dataclass(frozen=True)
class PlatformFighterDrawConfig:
    palette: CharacterPalette
    knobs: PlatformHeroKnobs
    foot_y: int
    face_rel_dy: int
    outline_buckets: Sequence[ColorBucket]
    shadow_rgba: tuple[int, int, int, int]
    swipe_core: ColorLike
    swipe_fade: tuple[int, int, int, int]
    sprite_palette: Sequence[ColorLike | tuple[int, int, int, int]]
    canvas_w: int = 128
    canvas_h: int = 128
    arm_offsets: PlatformArmOffsets = DEFAULT_PLATFORM_ARM_OFFSETS
    scarf_tip_nudge_dx: int = 0
    clip_preserve_rgb: frozenset[tuple[int, int, int]] = frozenset()


def _draw_scarf(s: Sprite, r: PlatformFighterRig, cfg: PlatformFighterDrawConfig, *, behind: bool) -> None:
    draw_scarf_mass(
        s,
        r.neck,
        scarf=cfg.palette.scarf or cfg.palette.hair,
        phase=r.scarf_phase,
        behind=behind,
        wave_offset=r.scarf_wave,
        lift_offset=r.scarf_lift,
        tip_dx=r.scarf_tip_dx,
        tip_dy=r.scarf_tip_dy,
        tip_world_x=r.scarf_tip_world_x,
        head_y=r.head[1],
        face_y_adj=cfg.face_rel_dy,
        foot_floor_y=cfg.foot_y,
        stamp_clip=r.scarf_stamp_clip,
        stamp_frame=r.scarf_stamp_frame,
    )


def _draw_head(s: Sprite, r: PlatformFighterRig, cfg: PlatformFighterDrawConfig, *, layers: str) -> None:
    cx, cy = r.head
    eye = cfg.palette.eye
    ch.fighter_head_facing_right(
        s,
        cx,
        cy,
        skin=cfg.palette.skin,
        hair=cfg.palette.hair,
        pupil=eye.pupil,
        iris=eye.iris,
        sclera=eye.sclera,
        paper=eye.paper,
        blush=eye.blush,
        look=cfg.knobs.head,
        hair_sway=r.hair_sway,
        layers=layers,
    )


def _draw_head_pass(s: Sprite, r: PlatformFighterRig, cfg: PlatformFighterDrawConfig) -> None:
    look: FighterHeadLook = cfg.knobs.head
    if look.hair_style == "ref_design":
        _draw_head(s, r, cfg, layers="face_front")
    else:
        _draw_head(s, r, cfg, layers="full")


def _draw_back_arm(s: Sprite, r: PlatformFighterRig, cfg: PlatformFighterDrawConfig, *, part: str) -> None:
    sh, el, ha = back_arm_chain(r, cfg.arm_offsets)
    draw_arm_gi(
        s,
        sh,
        el,
        ha,
        shirt=cfg.palette.shirt,
        skin=cfg.palette.skin,
        glove=cfg.palette.glove_or_shirt(),
        back=True,
        part=part,
    )


def _draw_front_arm(s: Sprite, r: PlatformFighterRig, cfg: PlatformFighterDrawConfig) -> None:
    sh, el, ha = front_arm_chain(r, cfg.arm_offsets)
    draw_arm_gi(
        s,
        sh,
        el,
        ha,
        shirt=cfg.palette.shirt,
        skin=cfg.palette.skin,
        glove=cfg.palette.glove_or_shirt(),
        back=False,
    )


def _clip_opaque_below(
    s: Sprite,
    floor_y: int,
    *,
    preserve_rgb: frozenset[tuple[int, int, int]] | None = None,
) -> None:
    """Clip boots/shadow spill; keep scarf tail pixels below ``FOOT_Y`` when requested."""
    img = s._img()
    w, h = img.size
    clear = (0, 0, 0, 0)
    keep = preserve_rgb or frozenset()
    for y in range(floor_y + 1, h):
        for x in range(w):
            px = img.getpixel((x, y))
            if px[3] == 0:
                continue
            if px[:3] in keep:
                continue
            img.putpixel((x, y), clear)


def preserve_rgb_from_colors(
    colors: Sequence[ColorLike | tuple[int, int, int, int]],
    palette: Sequence[ColorLike | tuple[int, int, int, int]],
) -> frozenset[tuple[int, int, int]]:
    """Resolve hex/ramp colors to RGB keys for floor clip preservation."""
    pal = list(palette)
    out: set[tuple[int, int, int]] = set()
    for c in colors:
        if isinstance(c, tuple) and len(c) >= 3 and not isinstance(c[0], str):
            out.add((int(c[0]), int(c[1]), int(c[2])))
            continue
        rgba = parse_color(c, pal)
        if rgba is not None:
            out.add(rgba[:3])
    return frozenset(out)


def draw_platform_fighter_shadow(s: Sprite, r: PlatformFighterRig, cfg: PlatformFighterDrawConfig) -> None:
    cx = (r.foot_f[0] + r.foot_b[0]) // 2
    ch.drop_shadow_oval(s, cx, cfg.foot_y, cfg.shadow_rgba, half_w=6, max_y=cfg.foot_y)


def draw_platform_fighter_content(
    s: Sprite,
    r: PlatformFighterRig,
    cfg: PlatformFighterDrawConfig,
    *,
    vfx: bool = True,
    outline: bool = True,
) -> None:
    """Layers 3–8 from ``platform-fighter.md`` (no shadow / dash ghost)."""
    pal = cfg.palette
    draw_platform_leg(s, hip=r.hip, knee=r.knee_b, foot=r.foot_b, back=True, palette=pal)
    _draw_back_arm(s, r, cfg, part="upper")
    draw_platform_torso(s, cfg.knobs.outfit, hip=r.hip, shoulder=r.shoulder, palette=pal, squash=r.squash)
    draw_chest_bridge(s, r.shoulder, shirt=pal.shirt)
    draw_platform_leg(s, hip=r.hip, knee=r.knee_f, foot=r.foot_f, back=False, palette=pal)
    _draw_back_arm(s, r, cfg, part="lower")
    draw_neck_bridge(s, r.neck, r.head, skin=pal.skin, face_y_adj=cfg.face_rel_dy)
    _draw_head(s, r, cfg, layers="hair_back")
    _draw_scarf(s, r, cfg, behind=False)
    _draw_front_arm(s, r, cfg)
    # Tail after limbs + hair; before face so iris is not overpainted.
    _draw_scarf(s, r, cfg, behind=True)
    _draw_head_pass(s, r, cfg)
    if vfx and r.slash > 0.1:
        hx, hy = front_arm_chain(r, cfg.arm_offsets)[2]
        draw_slash_arc(
            s,
            hx,
            hy - 8,
            deg0=-120 + r.slash * 40,
            deg1=-40 + r.slash * 20,
            radius=28,
            core=cfg.swipe_core,
            fade=cfg.swipe_fade,
        )
    if vfx and r.spark:
        hx, hy = front_arm_chain(r, cfg.arm_offsets)[2]
        draw_spark_streak(s, hx - 6, hy + 4, hx + 18, hy - 12, core=cfg.swipe_core)
    if outline:
        ch.finish_selective_humanoid(s, cfg.outline_buckets, fallback=pal.ink)
        _clip_opaque_below(s, cfg.foot_y, preserve_rgb=cfg.clip_preserve_rgb)


def draw_platform_fighter_frame(
    s: Sprite,
    r: PlatformFighterRig,
    cfg: PlatformFighterDrawConfig,
    *,
    shadow: bool = True,
    finalize: Callable[[PlatformFighterRig], PlatformFighterRig] | None = None,
) -> PlatformFighterRig:
    """
    Full fighter frame: optional ``finalize(r)``, shadow, body, outline.

    Returns the rig used for drawing (after ``finalize`` when provided).
    """
    if finalize is not None:
        r = finalize(r)
    if shadow:
        draw_platform_fighter_shadow(s, r, cfg)
    if r.dash_ghost:
        if is_dataclass(r):
            ghost_r = replace(r, lean=r.lean - 6, dash_ghost=False)
        else:
            ghost_r = r
        ch.stamp_silhouette_ghost(
            s,
            cfg.canvas_w,
            cfg.canvas_h,
            cfg.sprite_palette,
            (24, 16, 28, 72),
            lambda tmp, gr=ghost_r: draw_platform_fighter_content(tmp, gr, cfg, vfx=False, outline=False),
        )
    draw_platform_fighter_content(s, r, cfg)
    return r
