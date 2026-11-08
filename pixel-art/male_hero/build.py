#!/usr/bin/env python3
"""
Platform scarf fighter — canonical ``hero_config`` 128×128 pack.

Reference strips + ``scarf_keys.json``; ``FighterHeadLook`` + ``platform_outfit``.
"""

from __future__ import annotations

import json
import math
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from sparkpix import Sprite  # noqa: E402
from sparkpix.color import parse_color  # noqa: E402
from sparkpix import character as ch  # noqa: E402
from sparkpix import rig  # noqa: E402
from sparkpix.hero_config import (  # noqa: E402
    AnimationPlan,
    CharacterPalette,
    ClipSpec,
    EyeColors,
    PlatformHeroKnobs,
    PLATFORM_CLIP_TABLE,
    validate_knobs,
)
from sparkpix.platform_body import draw_arm_gi, draw_chest_bridge, draw_neck_bridge  # noqa: E402
from sparkpix.platform_ref_hair import REF_DESIGN_FACE_Y_ADJ  # noqa: E402
from sparkpix.platform_face import FighterHeadLook  # noqa: E402
from sparkpix.platform_outfit import draw_platform_leg, draw_platform_torso  # noqa: E402
from sparkpix.platform_scarf import draw_scarf_mass  # noqa: E402
from sparkpix.platform_style import FOOT_Y, MIN_HEIGHT_FILL, P128, SCARF_TIP_NUDGE_DX  # noqa: E402
from sparkpix.platform_vfx import draw_slash_arc, draw_spark_streak  # noqa: E402

OUT = Path(__file__).resolve().parent / "out"
W, H = 128, 128
NAME = "male_hero"

# --- Developer knobs (see PROMPT.md) ------------------------------------------------

PALETTE = CharacterPalette(
    hair=["#4c2641", "#5c2c4f", "#7d5556", "#a24e57", "#d77e86"],
    skin=["#c89078", "#d2947f", "#ffc5b4", "#d77e86"],
    shirt=["#ffffff", "#c0d5dc", "#a0acc5", "#ffffff"],
    trim=["#69799e", "#1c548e", "#143464"],
    pants=["#143464", "#1c548e", "#69799e", "#9f95ab"],
    boot=["#5c2c4f", "#a24e57", "#7d5556", "#d77e86"],
    glove=["#5c2c4f", "#a24e57", "#7d5556"],
    belt=["#4c2641", "#5c2c4f", "#7d5556"],
    scarf=["#5c2c4f", "#8b108f", "#cd3073", "#cd3073", "#ffc5b4"],
    ink="#4c2641",
    eye=EyeColors(pupil="#24523b", iris="#59c135", sclera="#ffffff", paper="#ffffff", blush="#ffc5b4"),
)

KNOBS = PlatformHeroKnobs(
    head=FighterHeadLook(hair_style="ref_design", eye_style="forward", show_blush=True),
    outfit="gi_shorts",
    shoe="gi_boot",
    weapon="scarf",
    animation=AnimationPlan(PLATFORM_CLIP_TABLE),
)
validate_knobs(KNOBS)

SWIPE = "#ffffff"
SWIPE_FADE = (220, 220, 240, 180)
SHADOW = (12, 8, 18, 90)

SPRITE_PALETTE = (
    [PALETTE.ink, PALETTE.eye.paper, PALETTE.eye.pupil, PALETTE.eye.iris, PALETTE.eye.sclera, PALETTE.eye.blush, SWIPE]
    + list(PALETTE.skin)
    + list(PALETTE.hair)
    + list(PALETTE.shirt)
    + list(PALETTE.trim)
    + list(PALETTE.pants)
    + list(PALETTE.boot)
    + list(PALETTE.glove)
    + list(PALETTE.belt)
    + list(PALETTE.scarf)
    + [SWIPE_FADE, SHADOW]
)

_SCARF_BUNDLE = json.loads((Path(__file__).resolve().parent / "scarf_keys.json").read_text(encoding="utf-8"))


def _scarf_keys(clip: str) -> list:
    return _SCARF_BUNDLE["clips"][clip]["keys"]


OUTLINE_BUCKETS = [
    (list(PALETTE.hair) + list(PALETTE.skin), PALETTE.hair[0]),
    (list(PALETTE.shirt) + [PALETTE.eye.paper, "#c0d5dc", "#a0acc5"], PALETTE.trim[2]),
    (list(PALETTE.trim) + list(PALETTE.pants), PALETTE.pants[0]),
    (list(PALETTE.boot) + list(PALETTE.glove) + list(PALETTE.belt), PALETTE.boot[0]),
    (list(PALETTE.scarf) + [PALETTE.eye.blush], PALETTE.scarf[0]),
    ([PALETTE.eye.pupil, PALETTE.eye.iris, PALETTE.eye.sclera], PALETTE.eye.pupil),
]


@dataclass
class Rig:
    dy: int = 0
    lean: int = 0
    squash: float = 1.0
    scarf_phase: float = 0.0
    scarf_wave: int = 0
    scarf_lift: int = 0
    scarf_tip_dx: int | None = None
    scarf_tip_dy: int | None = None
    scarf_tip_world_x: int | None = None
    hair_sway: int = 0
    foot_f: Tuple[int, int] = P128.foot_f
    foot_b: Tuple[int, int] = P128.foot_b
    knee_f: Tuple[int, int] = P128.knee_f
    knee_b: Tuple[int, int] = P128.knee_b
    hip: Tuple[int, int] = P128.hip
    shoulder: Tuple[int, int] = P128.shoulder
    elbow: Tuple[int, int] = P128.elbow
    hand: Tuple[int, int] = P128.hand
    head: Tuple[int, int] = P128.head
    neck: Tuple[int, int] = P128.neck
    slash: float = 0.0
    spark: bool = False
    dash_ghost: bool = False


def finalize(r: Rig) -> Rig:
    pts = rig.apply_shift(
        r.dy,
        r.lean,
        r.foot_f,
        r.foot_b,
        r.knee_f,
        r.knee_b,
        r.hip,
        r.shoulder,
        r.elbow,
        r.hand,
        r.head,
        neck=r.neck,
    )
    return Rig(
        dy=0,
        lean=0,
        squash=r.squash,
        scarf_phase=r.scarf_phase,
        scarf_wave=r.scarf_wave,
        scarf_lift=r.scarf_lift,
        scarf_tip_dx=r.scarf_tip_dx,
        scarf_tip_dy=r.scarf_tip_dy,
        scarf_tip_world_x=r.scarf_tip_world_x,
        hair_sway=r.hair_sway,
        slash=r.slash,
        spark=r.spark,
        dash_ghost=r.dash_ghost,
        **pts,
    )


def _scarf_fields(k: dict, *, body_dy: bool = True) -> dict:
    fields = {
        "scarf_phase": float(k.get("phase_hint", 0)),
        "scarf_wave": int(k.get("wave", 0)),
        "scarf_lift": int(k.get("lift", 0)),
        "scarf_tip_dx": None,
        "scarf_tip_dy": int(k.get("tip_dy", -2)),
        "scarf_tip_world_x": (int(k["tip_x"]) + SCARF_TIP_NUDGE_DX) if "tip_x" in k else None,
    }
    if body_dy:
        fields["dy"] = int(k.get("dy", 0))
    return fields


def _rig_with_scarf(k: dict, **extra) -> Rig:
    body_dy = extra.pop("body_dy", True)
    return Rig(**_scarf_fields(k, body_dy=body_dy), **extra)


def _draw_scarf(s: Sprite, r: Rig, *, behind: bool) -> None:
    draw_scarf_mass(
        s,
        r.neck,
        scarf=PALETTE.scarf,
        phase=r.scarf_phase,
        behind=behind,
        wave_offset=r.scarf_wave,
        lift_offset=r.scarf_lift,
        tip_dx=r.scarf_tip_dx,
        tip_dy=r.scarf_tip_dy,
        tip_world_x=r.scarf_tip_world_x,
        head_y=r.head[1],
        face_y_adj=REF_DESIGN_FACE_Y_ADJ,
    )


def _draw_head(s: Sprite, r: Rig, *, layers: str = "full") -> None:
    cx, cy = r.head
    eye = PALETTE.eye
    ch.fighter_head_facing_right(
        s,
        cx,
        cy,
        skin=PALETTE.skin,
        hair=PALETTE.hair,
        pupil=eye.pupil,
        iris=eye.iris,
        sclera=eye.sclera,
        paper=eye.paper,
        blush=eye.blush,
        look=KNOBS.head,
        hair_sway=r.hair_sway,
        layers=layers,
    )


def _draw_head_pass(s: Sprite, r: Rig) -> None:
    """Face + fringe + eye on top of scarf knot and front arm."""
    if KNOBS.head.hair_style == "ref_design":
        _draw_head(s, r, layers="face_front")
    else:
        _draw_head(s, r, layers="full")


def _back_arm_pts(r: Rig) -> tuple:
    """Back gi arm — left/down from P128; idle tuned to design glove bbox ~(54–67, 64–79)."""
    return (
        (r.shoulder[0] - 6, r.shoulder[1] + 4),
        (r.elbow[0] - 8, r.elbow[1] + 10),
        (r.hand[0] - 12, r.hand[1] + 12),
    )


def _draw_back_arm_upper(s: Sprite, r: Rig) -> None:
    sh, el, ha = _back_arm_pts(r)
    draw_arm_gi(
        s,
        sh,
        el,
        ha,
        shirt=PALETTE.shirt,
        skin=PALETTE.skin,
        glove=PALETTE.glove,
        back=True,
        part="upper",
    )


def _draw_back_arm_lower(s: Sprite, r: Rig) -> None:
    sh, el, ha = _back_arm_pts(r)
    draw_arm_gi(
        s,
        sh,
        el,
        ha,
        shirt=PALETTE.shirt,
        skin=PALETTE.skin,
        glove=PALETTE.glove,
        back=True,
        part="lower",
    )


def _draw_body_no_outline(s: Sprite, r: Rig) -> None:
    draw_platform_leg(s, hip=r.hip, knee=r.knee_b, foot=r.foot_b, back=True, palette=PALETTE)
    _draw_scarf(s, r, behind=True)
    _draw_back_arm_upper(s, r)
    draw_platform_torso(s, KNOBS.outfit, hip=r.hip, shoulder=r.shoulder, palette=PALETTE, squash=r.squash)
    draw_chest_bridge(s, r.shoulder, shirt=PALETTE.shirt)
    draw_platform_leg(s, hip=r.hip, knee=r.knee_f, foot=r.foot_f, back=False, palette=PALETTE)
    _draw_back_arm_lower(s, r)
    draw_neck_bridge(s, r.neck, r.head, skin=PALETTE.skin, face_y_adj=REF_DESIGN_FACE_Y_ADJ)
    _draw_head(s, r, layers="hair_back")
    _draw_scarf(s, r, behind=False)
    _draw_front_arm(s, r)
    _draw_head_pass(s, r)


def _front_arm_pts(r: Rig) -> tuple:
    """Shoulder/hand sit ~2px lower on gi — matches design sheet idle."""
    dy = 2
    return (
        (r.shoulder[0], r.shoulder[1] + dy),
        (r.elbow[0], r.elbow[1] + dy),
        (r.hand[0], r.hand[1] + dy),
    )


def _draw_front_arm(s: Sprite, r: Rig) -> None:
    sh, el, ha = _front_arm_pts(r)
    draw_arm_gi(
        s,
        sh,
        el,
        ha,
        shirt=PALETTE.shirt,
        skin=PALETTE.skin,
        glove=PALETTE.glove,
        back=False,
    )


def draw_shadow(s: Sprite, r: Rig) -> None:
    cx = (r.foot_f[0] + r.foot_b[0]) // 2
    ch.drop_shadow_oval(s, cx, FOOT_Y, SHADOW, half_w=6)


def draw_frame_content(s: Sprite, r: Rig) -> None:
    if r.dash_ghost:
        g = Rig(**{**r.__dict__, "lean": r.lean - 6, "dash_ghost": False})
        ch.stamp_silhouette_ghost(
            s,
            W,
            H,
            SPRITE_PALETTE,
            (24, 16, 28, 72),
            lambda tmp, gr=g: _draw_body_no_outline(tmp, gr),
        )
    draw_platform_leg(s, hip=r.hip, knee=r.knee_b, foot=r.foot_b, back=True, palette=PALETTE)
    _draw_scarf(s, r, behind=True)
    _draw_back_arm_upper(s, r)
    draw_platform_torso(s, KNOBS.outfit, hip=r.hip, shoulder=r.shoulder, palette=PALETTE, squash=r.squash)
    draw_chest_bridge(s, r.shoulder, shirt=PALETTE.shirt)
    draw_platform_leg(s, hip=r.hip, knee=r.knee_f, foot=r.foot_f, back=False, palette=PALETTE)
    _draw_back_arm_lower(s, r)
    draw_neck_bridge(s, r.neck, r.head, skin=PALETTE.skin, face_y_adj=REF_DESIGN_FACE_Y_ADJ)
    _draw_head(s, r, layers="hair_back")
    _draw_scarf(s, r, behind=False)
    _draw_front_arm(s, r)
    _draw_head_pass(s, r)
    if r.slash > 0.1:
        hx, hy = _front_arm_pts(r)[2]
        draw_slash_arc(
            s,
            hx,
            hy - 8,
            deg0=-120 + r.slash * 40,
            deg1=-40 + r.slash * 20,
            radius=28,
            core=SWIPE,
            fade=SWIPE_FADE,
        )
    if r.spark:
        hx, hy = _front_arm_pts(r)[2]
        draw_spark_streak(s, hx - 6, hy + 4, hx + 18, hy - 12, core=SWIPE)
    ch.finish_selective_humanoid(s, OUTLINE_BUCKETS, fallback=PALETTE.ink)


def draw_frame(s: Sprite, rig_in: Rig) -> None:
    s.clear()
    r = finalize(rig_in)
    draw_shadow(s, r)
    draw_frame_content(s, r)


def idle_rig(i: int) -> Rig:
    keys = _scarf_keys("idle")
    k = keys[i % len(keys)]
    return _rig_with_scarf(
        k,
        hair_sway=(i % 3) - 1,
        squash=0.98 + (i % 2) * 0.02,
    )


def walk_rig(i: int) -> Rig:
    keys = _scarf_keys("walk")
    k = keys[i % len(keys)]
    ph = i / 10.0 * math.pi * 2
    s = math.sin(ph)
    return _rig_with_scarf(
        k,
        lean=int(s),
        hair_sway=int(s * 2),
        foot_f=(P128.foot_f[0] + int(s * 5), FOOT_Y),
        foot_b=(P128.foot_b[0] - int(s * 4), FOOT_Y),
        knee_f=(P128.knee_f[0] + int(s * 4), P128.knee_f[1] - int(max(0, s) * 3)),
        knee_b=(P128.knee_b[0] - int(s * 2), P128.knee_b[1] + int(max(0, -s) * 2)),
        hand=(P128.hand[0] + int(s * 2), P128.hand[1] + int(s)),
    )


def run_rig(i: int) -> Rig:
    keys = _scarf_keys("run")
    k = keys[i % len(keys)]
    ph = i / 10.0 * math.pi * 2
    s = math.sin(ph)
    return _rig_with_scarf(
        k,
        lean=3,
        squash=0.94,
        hair_sway=int(s * 3),
        foot_f=(P128.foot_f[0] + int(s * 7), FOOT_Y),
        foot_b=(P128.foot_b[0] - 4 - int(s * 5), FOOT_Y),
        knee_f=(P128.knee_f[0] + int(s * 5), P128.knee_f[1] - 5 - int(abs(s) * 4)),
        knee_b=(P128.knee_b[0] - 3, P128.knee_b[1] - 4),
        shoulder=(P128.shoulder[0] + 2, P128.shoulder[1] - 1),
        hand=(P128.hand[0] + 4, P128.hand[1] - 2),
    )


def jump_rigs() -> List[Rig]:
    extras = [
        {"dy": 0, "squash": 0.88},
        {"dy": -4, "squash": 0.92, "hair_sway": 1},
        {"dy": -14, "foot_f": (P128.foot_f[0], FOOT_Y - 10), "foot_b": (P128.foot_b[0], FOOT_Y - 8)},
        {
            "dy": -16,
            "foot_f": (P128.foot_f[0], FOOT_Y - 12),
            "foot_b": (P128.foot_b[0], FOOT_Y - 10),
            "hair_sway": 2,
        },
        {"dy": -8, "foot_f": (P128.foot_f[0], FOOT_Y - 4), "foot_b": (P128.foot_b[0], FOOT_Y - 2)},
        {"dy": 0, "squash": 0.9},
    ]
    jump_keys = _scarf_keys("jump")
    return [_rig_with_scarf(jump_keys[i], body_dy=False, **extras[i]) for i in range(6)]


def fall_rigs() -> List[Rig]:
    extras = [
        {"dy": -10, "foot_f": (P128.foot_f[0], FOOT_Y - 8), "foot_b": (P128.foot_b[0], FOOT_Y - 6)},
        {"dy": -6, "lean": 1},
        {"dy": -2},
        {"dy": 0, "squash": 0.9},
    ]
    fall_keys = _scarf_keys("fall")
    return [_rig_with_scarf(fall_keys[i], body_dy=False, **extras[i]) for i in range(4)]


def fall_loop_rigs() -> List[Rig]:
    extras = [
        {"dy": -12, "foot_f": (P128.foot_f[0], FOOT_Y - 14), "foot_b": (P128.foot_b[0], FOOT_Y - 12), "lean": 2},
        {"dy": -12, "foot_f": (P128.foot_f[0], FOOT_Y - 14), "foot_b": (P128.foot_b[0], FOOT_Y - 12), "hair_sway": 1},
        {"dy": -12, "foot_f": (P128.foot_f[0], FOOT_Y - 14), "foot_b": (P128.foot_b[0], FOOT_Y - 12), "lean": 1},
    ]
    fall_loop_keys = _scarf_keys("fall_loop")
    return [_rig_with_scarf(fall_loop_keys[i], body_dy=False, **extras[i]) for i in range(3)]


def dash_rigs() -> List[Rig]:
    out: List[Rig] = []
    for i in range(8):
        t = i / 7.0
        out.append(
            Rig(
                dy=int(t * 2) - 1,
                lean=4 + int(t * 3),
                squash=0.9,
                scarf_phase=t,
                dash_ghost=i in (2, 3, 4),
                hand=(P128.hand[0] + 6, P128.hand[1]),
                elbow=(P128.elbow[0] + 5, P128.elbow[1]),
            )
        )
    return out


def combo_1_rigs() -> List[Rig]:
    extras = [
        {"lean": 2, "squash": 0.92, "hand": (P128.hand[0] + 2, P128.hand[1] + 6), "elbow": (P128.elbow[0], P128.elbow[1] + 4)},
        {"lean": 3, "slash": 0.5, "spark": True, "hand": (P128.hand[0] + 8, P128.hand[1] - 4)},
        {"lean": 2, "slash": 1.0, "hand": (P128.hand[0] + 10, P128.hand[1] + 2)},
    ]
    combo_keys = _scarf_keys("combo_1")
    return [_rig_with_scarf(combo_keys[i], body_dy=False, **extras[i]) for i in range(3)]


def combo_1_end_rigs() -> List[Rig]:
    extras = [
        {"lean": 2, "slash": 0.6, "hand": (P128.hand[0] + 6, P128.hand[1])},
        {"lean": 1, "slash": 0.3, "hand": (P128.hand[0] + 2, P128.hand[1] + 2)},
        {"lean": 0, "hand": P128.hand},
        {"lean": 0},
    ]
    combo_end_keys = _scarf_keys("combo_1_end")
    return [_rig_with_scarf(combo_end_keys[i], body_dy=False, **extras[i]) for i in range(4)]


def rigs_for_clip(spec: ClipSpec) -> List[Rig]:
    n = spec.frames
    if spec.name == "idle":
        return [idle_rig(i) for i in range(n)]
    if spec.name == "walk":
        return [walk_rig(i) for i in range(n)]
    if spec.name == "run":
        return [run_rig(i) for i in range(n)]
    if spec.name == "jump":
        return jump_rigs()
    if spec.name == "fall":
        return fall_rigs()
    if spec.name == "fall_loop":
        return fall_loop_rigs()
    if spec.name == "dash":
        return dash_rigs()
    if spec.name == "combo_1":
        return combo_1_rigs()
    if spec.name == "combo_1_end":
        return combo_1_end_rigs()
    raise KeyError(spec.name)


def build_all() -> List[Rig]:
    rigs: List[Rig] = []
    for spec in KNOBS.animation.enabled():
        rigs.extend(rigs_for_clip(spec))
    return rigs


def main() -> None:
    rigs = build_all()
    s = Sprite(W, H, palette=SPRITE_PALETTE)
    for i, rig_item in enumerate(rigs):
        if i > 0:
            s.add_frame(copy=False)
        draw_frame(s, rig_item)
        if i == 0:
            ch.warn_if_stick_legs(s, FOOT_Y, frame=0)

    OUT.mkdir(parents=True, exist_ok=True)
    matte = "#343848"
    from sparkpix.export import save_png

    s.use(frame=0)
    save_png(s.flatten_frame(0), OUT / "frame0_art.png", scale=1)
    s.preview(OUT / "preview_idle.png", scale=8, matte=matte)
    from PIL import Image as PILImage

    clip_ranges = KNOBS.animation.tag_on_sprite(s)

    matte_rgba = parse_color(matte, SPRITE_PALETTE) or (52, 56, 72, 255)
    idle_a, idle_b = clip_ranges["idle"]
    idle_contact = PILImage.new("RGBA", (W * (idle_b - idle_a + 1), H), matte_rgba)
    for fi, frame_idx in enumerate(range(idle_a, idle_b + 1)):
        s.use(frame=frame_idx)
        idle_contact.alpha_composite(s.flatten_frame(frame_idx), (fi * W, 0))
    save_png(idle_contact, OUT / "idle_strip_art.png", scale=4)

    def _strip_contact(frame_range: tuple[int, int], path: Path) -> None:
        a, b = frame_range
        sheet = PILImage.new("RGBA", (W * (b - a + 1), H), matte_rgba)
        for fi, frame_idx in enumerate(range(a, b + 1)):
            s.use(frame=frame_idx)
            sheet.alpha_composite(s.flatten_frame(frame_idx), (fi * W, 0))
        save_png(sheet, path, scale=4)

    _strip_contact(clip_ranges["walk"], OUT / "walk_strip_art.png")
    _strip_contact(clip_ranges["run"], OUT / "run_strip_art.png")
    walk_start = clip_ranges["walk"][0]
    combo_start = clip_ranges["combo_1"][0]
    s.use(frame=walk_start).preview(OUT / "preview_walk.png", scale=8, matte=matte)
    s.use(frame=combo_start).preview(OUT / "preview_combo.png", scale=8, matte=matte)
    s.preview(OUT / "preview_sheet.png", scale=2, grid=True, matte=matte)
    s.save_gif(OUT / f"{NAME}_all.gif", scale=2)
    s.save_spritesheet(OUT / NAME, columns=12, padding=0, spark_json=True)
    s.save_project(OUT / f"{NAME}.sparkpix.json")

    from sparkpix.quality import build_quality_meta, critique_atlas_dir, format_report, write_quality_sidecar

    write_quality_sidecar(
        OUT,
        NAME,
        build_quality_meta(
            outline_ink=PALETTE.ink,
            foot_y=FOOT_Y,
            critique_frames=[0, walk_start, combo_start],
            max_colors=48,
            min_height_fill=MIN_HEIGHT_FILL,
        ),
    )
    text = format_report(critique_atlas_dir(OUT))
    if text != "OK (no quality warnings)":
        print(text)
    print(s.stats())
    print("wrote", OUT)


if __name__ == "__main__":
    main()

