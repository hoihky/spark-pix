#!/usr/bin/env python3
"""
Reference youth — canonical ``hero_config`` JRPG Q pack.

Cyan spiky hair, vertical eye, olive tunic. Clips driven by ``AnimationPlan``.
"""

from __future__ import annotations

import math
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from sparkpix import Sprite, ramp  # noqa: E402
from sparkpix import character as ch  # noqa: E402
from sparkpix import rig  # noqa: E402
from sparkpix.hero_config import (  # noqa: E402
    AnimationPlan,
    CharacterPalette,
    ClipSpec,
    EyeColors,
    JrpgHeroKnobs,
    validate_knobs,
)
from sparkpix.jrpg_face import JrpgHeadLook  # noqa: E402
from sparkpix.platform_outfit import (  # noqa: E402
    draw_jrpg_arm,
    draw_jrpg_chest_bridge,
    draw_jrpg_leg,
    draw_jrpg_torso,
)
from sparkpix.q_style import FOOT_Y, KNEE_Y, MIN_HEIGHT_FILL, Q64  # noqa: E402

OUT = Path(__file__).resolve().parent / "out"
W, H = 64, 64
NAME = "ref_youth"

# --- Developer knobs (also documented in PROMPT.md) ---------------------------------

HEAD_LOOK = JrpgHeadLook(
    hair_style="spiky",
    eye_style="vertical",
    forehead="none",
    beard=False,
    fringe_over_eye=True,
)

INK = "#101420"
PALETTE = CharacterPalette(
    hair=ramp("#0c2840", 5),
    skin=ramp("#d8a880", 4),
    shirt=ramp("#786840", 4),
    pants=ramp("#382820", 4),
    boot=ramp("#503828", 3),
    ink=INK,
    eye=EyeColors(pupil="#0a1018", iris="#2878a8", sclera="#ffffff", paper="#f8fcff"),
)

KNOBS = JrpgHeroKnobs(
    head=HEAD_LOOK,
    outfit="tunic",
    shoe="q_boot",
    weapon="none",
    animation=AnimationPlan(
        (
            ClipSpec("idle", 4, 4.0),
            ClipSpec("walk", 8, 10.0),
            ClipSpec("run", 6, 14.0),
        )
    ),
)
validate_knobs(KNOBS)

SHADOW = (12, 10, 18, 90)
SPRITE_PALETTE = (
    [INK, PALETTE.eye.paper, PALETTE.eye.pupil, PALETTE.eye.iris, PALETTE.eye.sclera]
    + list(PALETTE.skin)
    + list(PALETTE.hair)
    + list(PALETTE.shirt)
    + list(PALETTE.pants)
    + list(PALETTE.boot)
    + [SHADOW]
)


@dataclass
class Rig:
    dy: int = 0
    lean: int = 0
    squash: float = 1.0
    foot_f: Tuple[int, int] = Q64.foot_f
    foot_b: Tuple[int, int] = Q64.foot_b
    knee_f: Tuple[int, int] = Q64.knee_f
    knee_b: Tuple[int, int] = Q64.knee_b
    hip: Tuple[int, int] = Q64.hip
    shoulder: Tuple[int, int] = Q64.shoulder
    elbow: Tuple[int, int] = Q64.elbow
    hand: Tuple[int, int] = Q64.hand
    head: Tuple[int, int] = Q64.head


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
    )
    return Rig(dy=0, lean=0, squash=r.squash, **pts)


def draw_shadow(s: Sprite, r: Rig) -> None:
    cx = (r.foot_f[0] + r.foot_b[0]) // 2
    ch.drop_shadow_oval(s, cx, FOOT_Y, SHADOW, half_w=6)


def draw_head(s: Sprite, r: Rig) -> None:
    cx, cy = r.head
    eye = PALETTE.eye
    ch.profile_head_facing_right(
        s,
        cx,
        cy,
        skin=PALETTE.skin,
        hair=PALETTE.hair,
        band=PALETTE.shirt,
        eye_green=eye.iris,
        sclera=eye.sclera,
        paper=eye.paper,
        pupil=eye.pupil,
        lash=PALETTE.hair[0],
        look=KNOBS.head,
        cute=True,
    )


def draw_back_arm(s: Sprite, r: Rig) -> None:
    sx, sy = r.shoulder[0] - 2, r.shoulder[1] + 1
    ch.limb(s, (sx, sy), (sx - 3, sy + 7), 2, PALETTE.shirt[1])


def draw_frame_content(s: Sprite, r: Rig) -> None:
    draw_jrpg_leg(
        s,
        KNOBS.outfit,
        hip=r.hip,
        knee=r.knee_b,
        foot=r.foot_b,
        back=True,
        palette=PALETTE,
        shoe=KNOBS.shoe,
    )
    draw_back_arm(s, r)
    draw_jrpg_torso(
        s,
        KNOBS.outfit,
        hip=r.hip,
        shoulder=r.shoulder,
        palette=PALETTE,
        squash=r.squash,
    )
    draw_jrpg_chest_bridge(s, KNOBS.outfit, r.shoulder, PALETTE)
    draw_jrpg_leg(
        s,
        KNOBS.outfit,
        hip=r.hip,
        knee=r.knee_f,
        foot=r.foot_f,
        back=False,
        palette=PALETTE,
        shoe=KNOBS.shoe,
    )
    draw_head(s, r)
    draw_jrpg_arm(s, KNOBS.outfit, shoulder=r.shoulder, elbow=r.elbow, hand=r.hand, palette=PALETTE)
    ch.finish_production_humanoid(s, PALETTE.ink)


def draw_frame(s: Sprite, rig_in: Rig) -> None:
    s.clear()
    r = finalize(rig_in)
    draw_shadow(s, r)
    draw_frame_content(s, r)


def idle_rig(i: int) -> Rig:
    breath = (i % 4) - 1
    sway = (i % 3) - 1
    return Rig(dy=breath, squash=0.97 + (i % 2) * 0.02, hand=(Q64.hand[0], Q64.hand[1] + sway))


def walk_rig(phase: float) -> Rig:
    s = math.sin(phase)
    return Rig(
        dy=int(abs(s)),
        foot_f=(Q64.foot_f[0] + int(s * 3), FOOT_Y),
        foot_b=(Q64.foot_b[0] - int(s * 2), FOOT_Y),
        knee_f=(Q64.knee_f[0] + int(s * 2), KNEE_Y - int(max(0, s) * 2)),
        knee_b=(Q64.knee_b[0] - int(s), KNEE_Y + 1 + int(max(0, -s))),
        hand=(Q64.hand[0] + int(s), Q64.hand[1] + int(s * 2)),
    )


def run_rig(phase: float) -> Rig:
    s = math.sin(phase)
    return Rig(
        dy=int(s * 2),
        lean=2,
        squash=0.92,
        foot_f=(Q64.foot_f[0] + 1 + int(s * 4), FOOT_Y),
        foot_b=(Q64.foot_b[0] - 3 - int(s * 3), FOOT_Y),
        knee_f=(Q64.knee_f[0] + int(s * 3), KNEE_Y - 4 - int(abs(s) * 3)),
        knee_b=(Q64.knee_b[0] - 2 - int(s * 2), KNEE_Y - 3),
        hip=(Q64.hip[0], Q64.hip[1] - 1),
        shoulder=(Q64.shoulder[0] + 1, Q64.shoulder[1] - 1),
        elbow=(Q64.elbow[0] + 2, Q64.elbow[1] - 1),
        hand=(Q64.hand[0] + 3, Q64.hand[1] - 2),
    )


def rigs_for_clip(spec: ClipSpec) -> List[Rig]:
    if spec.name == "idle":
        return [idle_rig(i) for i in range(spec.frames)]
    if spec.name == "walk":
        return [walk_rig(i / spec.frames * math.pi * 2) for i in range(spec.frames)]
    if spec.name == "run":
        return [run_rig(i / spec.frames * math.pi * 2) for i in range(spec.frames)]
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
    s.preview(OUT / "preview_idle.png", scale=8, matte=matte)
    s.preview(OUT / "preview_sheet.png", scale=4, grid=True, matte=matte)
    KNOBS.animation.tag_on_sprite(s)
    s.save_gif(OUT / f"{NAME}_all.gif", scale=4)
    s.save_spritesheet(OUT / NAME, columns=10, padding=0, spark_json=True)
    s.save_project(OUT / f"{NAME}.sparkpix.json")

    from sparkpix.quality import build_quality_meta, critique_atlas_dir, format_report, write_quality_sidecar

    write_quality_sidecar(
        OUT,
        NAME,
        build_quality_meta(
            outline_ink=PALETTE.ink,
            foot_y=FOOT_Y,
            critique_frames=[0],
            max_colors=36,
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
