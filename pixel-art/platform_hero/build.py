#!/usr/bin/env python3
"""
Platformer hero "Skip" — production 64×64 rig (humanoid-hero proportions).

Original: chestnut hair, yellow bandana, teal hoodie, cargo shorts, hook baton.
Clips: idle, walk, run, jump, dash, attack.

Platformer-facing +X; feet on FOOT_Y; filled limbs ≥2 px. See SKILL.md + validations.md.
"""

from __future__ import annotations

import math
import sys
from dataclasses import dataclass, replace
from pathlib import Path
from typing import List, Sequence, Tuple

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from sparkpix import Sprite, ramp  # noqa: E402
from sparkpix import character as ch  # noqa: E402
from sparkpix import rig  # noqa: E402

OUT = Path(__file__).resolve().parent / "out"
W, H = 64, 64
FOOT_Y = 61
BATON_LEN = 24

SKIN = ramp("#c89070", 4)
HAIR = ramp("#7a4828", 5)
BAND = ramp("#e8c830", 3)
HOOD = ramp("#208890", 4)
SHIRT = ramp("#ece4d4", 3)
SHORTS = ramp("#5a5048", 4)
BOOT = ramp("#d87030", 3)
BOOT_D = ramp("#3a2820", 3)
WOOD = ramp("#5a4030", 3)
METAL = ramp("#8898a8", 4)
HOOK_GLOW = ramp("#78e048", 3)
INK = "#141820"
PAPER = "#f4f4ec"
EYE = "#282830"
EYE_GREEN = "#48a868"
SCLERA = "#e8ece8"
SWIPE = (190, 255, 210, 170)
SPARK = (240, 250, 255, 220)
SWIPE_FADE = (130, 210, 150, 95)
GHOST = (90, 110, 125, 75)
DASH_WISP = (210, 235, 255, 130)
SHADOW = (16, 14, 24, 85)

PALETTE = (
    [INK, PAPER, EYE, EYE_GREEN, SCLERA]
    + SKIN
    + HAIR
    + BAND
    + HOOD
    + SHIRT
    + SHORTS
    + BOOT
    + BOOT_D
    + WOOD
    + METAL
    + HOOK_GLOW
    + [SWIPE, SWIPE_FADE, GHOST, DASH_WISP, SHADOW, SPARK]
)


@dataclass
class Rig:
    dy: int = 0
    lean: int = 0
    foot_f: Tuple[int, int] = (30, FOOT_Y)
    foot_b: Tuple[int, int] = (24, FOOT_Y)
    knee_f: Tuple[int, int] = (29, 50)
    knee_b: Tuple[int, int] = (25, 51)
    hip: Tuple[int, int] = (27, 40)
    shoulder: Tuple[int, int] = (29, 30)
    elbow: Tuple[int, int] = (33, 36)
    hand: Tuple[int, int] = (35, 38)
    head: Tuple[int, int] = (26, 19)
    baton_deg: float = 72.0
    baton_trail: Tuple[float, ...] = ()
    squash: float = 1.0
    ghost_offsets: Tuple[int, ...] = ()
    dash_wisps: bool = False
    hilt_spark: bool = False
    slash_arc: float = 0.0


def finalize(r: Rig) -> Rig:
    """Apply dy/lean to skeleton; clear meta fields for drawing."""
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
    return Rig(
        dy=0,
        lean=0,
        foot_f=pts["foot_f"],
        foot_b=pts["foot_b"],
        knee_f=pts["knee_f"],
        knee_b=pts["knee_b"],
        hip=pts["hip"],
        shoulder=pts["shoulder"],
        elbow=pts["elbow"],
        hand=pts["hand"],
        head=pts["head"],
        baton_deg=r.baton_deg,
        baton_trail=r.baton_trail,
        squash=r.squash,
        ghost_offsets=r.ghost_offsets,
        dash_wisps=r.dash_wisps,
        hilt_spark=r.hilt_spark,
        slash_arc=r.slash_arc,
    )


def draw_shadow(s: Sprite, r: Rig) -> None:
    cx = (r.foot_f[0] + r.foot_b[0]) // 2
    ch.drop_shadow_oval(s, cx, FOOT_Y, SHADOW)


def draw_dash_wisps(s: Sprite, r: Rig) -> None:
    if not r.dash_wisps:
        return
    hx, hy = r.hip
    for i in range(8):
        x = hx - 10 - i * 3
        y = hy + 6 + (i % 3) - 1
        s.px(x, y, DASH_WISP)
        s.px(x - 1, y + 1, DASH_WISP)


def draw_leg(s: Sprite, hip: Tuple[int, int], knee: Tuple[int, int], foot: Tuple[int, int], back: bool) -> None:
    ch.platformer_leg(
        s,
        hip,
        knee,
        foot,
        back=back,
        shorts=SHORTS,
        boot=BOOT,
        boot_dark=BOOT_D,
    )


def draw_torso(s: Sprite, r: Rig) -> None:
    ch.torso_hoodie(
        s,
        r.hip,
        squash=r.squash,
        hood=HOOD,
        shirt=SHIRT,
        shorts=SHORTS,
        width_half=7,
    )


def draw_head(s: Sprite, r: Rig) -> None:
    cx, cy = r.head
    ch.profile_head_facing_right(
        s,
        cx,
        cy,
        skin=SKIN,
        hair=HAIR,
        band=BAND,
        eye_green=EYE_GREEN,
        sclera=SCLERA,
        mouth_shadow=SKIN[0],
    )


def draw_arm(s: Sprite, r: Rig) -> None:
    ch.limb(s, r.shoulder, r.elbow, 2, HOOD[2])
    ch.limb(s, r.elbow, r.hand, 2, SKIN[2])


def draw_baton(s: Sprite, r: Rig) -> None:
    hx, hy = r.hand
    if r.baton_trail:
        ch.weapon_angle_trail(s, hx, hy, r.baton_trail, BATON_LEN, SWIPE_FADE, SWIPE)
    s.rect(hx - 1, hy - 2, hx + 3, hy + 1, fill=METAL[1])
    s.px(hx + 1, hy, METAL[3])
    bx, by = hx + 2, hy
    ex, ey = rig.tip(bx, by, r.baton_deg, BATON_LEN)
    ch.limb(s, (bx, by), (ex, ey), 2, WOOD[1])
    rad = math.radians(r.baton_deg - 90)
    ox, oy = int(math.cos(rad) * 2), int(math.sin(rad) * 2)
    ch.limb(s, (bx + ox, by + oy), (ex + ox, ey + oy), 1, WOOD[2])
    s.rect(ex - 2, ey - 2, ex + 1, ey + 1, fill=METAL[2])
    s.px(ex, ey, HOOK_GLOW[2])
    s.px(ex - 1, ey, HOOK_GLOW[1])
    s.px(ex, ey - 1, PAPER)
    if r.hilt_spark:
        ch.hilt_spark(s, hx, hy, SPARK)


def draw_back_arm(s: Sprite, r: Rig) -> None:
    sx, sy = r.shoulder[0] - 3, r.shoulder[1] + 1
    ch.limb(s, (sx, sy), (sx - 4, sy + 8), 2, HOOD[1])


def draw_body_content(s: Sprite, r: Rig, *, with_outline: bool = True) -> None:
    draw_leg(s, r.hip, r.knee_b, r.foot_b, back=True)
    draw_back_arm(s, r)
    baton_back = rig.weapon_raised_behind_head(r.baton_deg)
    if baton_back:
        draw_baton(s, r)
    draw_torso(s, r)
    draw_leg(s, r.hip, r.knee_f, r.foot_f, back=False)
    draw_head(s, r)
    draw_arm(s, r)
    if not baton_back:
        draw_baton(s, r)
    if r.slash_arc > 0:
        ch.slash_crescent(s, r.hand[0] + 8, r.hand[1] - 6, r.slash_arc, fade=SWIPE_FADE, bright=SWIPE)
    if with_outline:
        ch.finish_outside_outline(s, INK)


def draw_ghost(s: Sprite, base: Rig, dx: int) -> None:
    br = replace(
        base,
        foot_f=(base.foot_f[0] + dx, base.foot_f[1]),
        foot_b=(base.foot_b[0] + dx, base.foot_b[1]),
        knee_f=(base.knee_f[0] + dx, base.knee_f[1]),
        knee_b=(base.knee_b[0] + dx, base.knee_b[1]),
        hip=(base.hip[0] + dx, base.hip[1]),
        shoulder=(base.shoulder[0] + dx, base.shoulder[1]),
        elbow=(base.elbow[0] + dx, base.elbow[1]),
        hand=(base.hand[0] + dx, base.hand[1]),
        head=(base.head[0] + dx, base.head[1]),
        baton_trail=(),
        ghost_offsets=(),
        dash_wisps=False,
        slash_arc=0.0,
    )

    def _draw(tmp: Sprite) -> None:
        draw_body_content(tmp, br, with_outline=False)

    ch.stamp_silhouette_ghost(s, W, H, PALETTE, GHOST, _draw)


def draw_frame(s: Sprite, rig: Rig) -> None:
    s.clear()
    r = finalize(rig)
    for off in rig.ghost_offsets:
        draw_ghost(s, r, off)
    draw_shadow(s, r)
    draw_dash_wisps(s, r)
    draw_body_content(s, r)


def idle_rig(i: int) -> Rig:
    breath = (i % 4) - 1
    sway = (i % 3) - 1
    return Rig(dy=breath, baton_deg=74 + sway * 0.8)


def walk_rig(phase: float) -> Rig:
    s = math.sin(phase)
    c = math.cos(phase)
    return Rig(
        dy=int(abs(s) * 1),
        foot_f=(30 + int(s * 3), FOOT_Y),
        foot_b=(24 - int(s * 2), FOOT_Y),
        knee_f=(29 + int(s * 2), 50 - int(max(0, s) * 3)),
        knee_b=(25 - int(s), 51 + int(max(0, -s) * 2)),
        hip=(27, 40),
        hand=(35, 38),
        baton_deg=68 + c * 4,
    )


def run_rig(phase: float) -> Rig:
    s = math.sin(phase)
    return Rig(
        dy=int(s * 2),
        lean=2,
        foot_f=(32 + int(s * 4), FOOT_Y),
        foot_b=(22 - int(s * 3), FOOT_Y),
        knee_f=(30 + int(s * 3), 48 - int(abs(s) * 4)),
        knee_b=(24 - int(s * 2), 49),
        hip=(28, 39),
        shoulder=(30, 28),
        hand=(36, 37),
        baton_deg=58 + s * 10,
    )


def jump_rigs() -> List[Rig]:
    return [
        Rig(dy=2, squash=0.86, knee_f=(29, 52), knee_b=(25, 52), baton_deg=76),
        Rig(dy=0, foot_f=(30, FOOT_Y), foot_b=(24, FOOT_Y), knee_f=(29, 49), baton_deg=68),
        Rig(dy=-4, lean=1, knee_f=(28, 47), knee_b=(26, 47), foot_f=(29, 55), foot_b=(25, 55), baton_deg=52),
        Rig(dy=-14, lean=1, knee_f=(27, 46), knee_b=(26, 46), foot_f=(28, 58), foot_b=(25, 58), baton_deg=44),
        Rig(dy=-6, knee_f=(29, 48), foot_f=(30, 56), foot_b=(24, 56), baton_deg=50),
        Rig(dy=1, foot_f=(30, FOOT_Y), foot_b=(24, FOOT_Y), squash=0.9, baton_deg=66),
    ]


def dash_rigs() -> List[Rig]:
    return [
        Rig(dy=2, squash=0.84, baton_deg=80),
        Rig(lean=2, squash=0.9, shoulder=(30, 31), baton_deg=12, dash_wisps=True),
        Rig(
            lean=5,
            foot_f=(33, FOOT_Y),
            foot_b=(27, FOOT_Y),
            hip=(29, 39),
            hand=(37, 36),
            baton_deg=6,
            ghost_offsets=(-6, -12),
            dash_wisps=True,
        ),
        Rig(
            lean=7,
            foot_f=(35, FOOT_Y),
            foot_b=(29, FOOT_Y),
            hip=(31, 38),
            hand=(38, 35),
            baton_deg=4,
            ghost_offsets=(-8, -16),
            dash_wisps=True,
        ),
        Rig(lean=5, foot_f=(33, FOOT_Y), foot_b=(27, FOOT_Y), baton_deg=18, dash_wisps=True),
        Rig(lean=2, baton_deg=45, dash_wisps=True),
        Rig(baton_deg=68),
    ]


def attack_rigs() -> List[Rig]:
    """Iai-style: windup (crouch + hilt spark) → snap slash → lingering arc → recover."""
    return [
        Rig(squash=0.94, baton_deg=76, lean=-1),
        Rig(squash=0.92, baton_deg=80, lean=-1, elbow=(32, 37), hand=(34, 39)),
        Rig(dy=1, squash=0.88, lean=-2, shoulder=(28, 31), elbow=(31, 38), hand=(33, 40), baton_deg=88),
        Rig(
            dy=2,
            squash=0.84,
            lean=-3,
            shoulder=(27, 32),
            elbow=(30, 39),
            hand=(32, 41),
            baton_deg=94,
            hilt_spark=True,
        ),
        Rig(
            dy=3,
            squash=0.80,
            lean=-4,
            shoulder=(26, 33),
            elbow=(28, 40),
            hand=(30, 42),
            baton_deg=100,
            hilt_spark=True,
        ),
        Rig(
            lean=4,
            dy=0,
            shoulder=(31, 28),
            elbow=(34, 32),
            hand=(37, 33),
            baton_deg=68,
            baton_trail=(100, 88, 68),
        ),
        Rig(
            lean=7,
            shoulder=(32, 27),
            elbow=(35, 31),
            hand=(38, 32),
            baton_deg=38,
            baton_trail=(100, 68, 38),
        ),
        Rig(lean=6, hand=(38, 32), baton_deg=18, baton_trail=(68, 38, 18)),
        Rig(lean=5, baton_deg=28, slash_arc=96.0, baton_trail=(38, 18)),
        Rig(lean=2, baton_deg=48, slash_arc=100.0),
        Rig(baton_deg=72),
    ]


def build_all() -> Tuple[List[Rig], List[Tuple[str, int, int, float, bool]]]:
    rigs: List[Rig] = []
    clips: List[Tuple[str, int, int, float, bool]] = []
    idx = 0

    def add(name: str, items: List[Rig], fps: float, loop: bool) -> None:
        nonlocal idx
        start = idx
        rigs.extend(items)
        idx += len(items)
        clips.append((name, start, idx - 1, fps, loop))

    add("idle", [idle_rig(i) for i in range(4)], 4.0, True)
    add("walk", [walk_rig(i / 8 * math.pi * 2) for i in range(8)], 10.0, True)
    add("run", [run_rig(i / 6 * math.pi * 2) for i in range(6)], 14.0, True)
    add("jump", jump_rigs(), 12.0, False)
    add("dash", dash_rigs(), 18.0, False)
    add("attack", attack_rigs(), 12.0, False)
    return rigs, clips


def check_silhouette(s: Sprite) -> None:
    ch.warn_if_stick_legs(s, FOOT_Y, frame=0)


def run_quality_gate() -> None:
    from sparkpix.quality import critique_atlas_dir, format_report

    report = critique_atlas_dir(OUT)
    text = format_report(report)
    if text != "OK (no quality warnings)":
        print(text)


def main() -> None:
    rigs, clip_meta = build_all()
    s = Sprite(W, H, palette=PALETTE)
    for i, rig in enumerate(rigs):
        if i > 0:
            s.add_frame(copy=False)
        draw_frame(s, rig)
        if i == 0:
            check_silhouette(s)

    atk_i = next(c[1] for c in clip_meta if c[0] == "attack")
    for j in range(11):
        s.frame(atk_i + j)
        if j < 5:
            s.set_duration(130)
        elif j < 8:
            s.set_duration(65)
        else:
            s.set_duration(100)

    OUT.mkdir(parents=True, exist_ok=True)
    matte = "#343848"
    s.preview(OUT / "preview_idle.png", scale=8, matte=matte)
    walk_i = next(c[1] for c in clip_meta if c[0] == "walk")
    s.frame(walk_i + 2)
    s.preview(OUT / "preview_walk.png", scale=8, matte=matte)
    s.preview(OUT / "preview_sheet.png", scale=3, grid=True, matte=matte)
    dash_i = next(c[1] for c in clip_meta if c[0] == "dash")
    s.frame(dash_i + 2)
    s.preview(OUT / "preview_dash.png", scale=8, matte=matte)
    atk_i = next(c[1] for c in clip_meta if c[0] == "attack")
    s.frame(atk_i + 4)
    s.preview(OUT / "preview_attack_windup.png", scale=8, matte=matte)
    s.frame(atk_i + 8)
    s.preview(OUT / "preview_attack.png", scale=8, matte=matte)

    for name, a, b, fps, loop in clip_meta:
        s.tag_clip(name, a, b, fps=fps, loop=loop)

    s.save_gif(OUT / "platform_hero_all.gif", scale=4)
    s.save_spritesheet(OUT / "platform_hero", columns=10, padding=0, spark_json=True)

    from sparkpix.quality import build_quality_meta, write_quality_sidecar

    write_quality_sidecar(
        OUT,
        "platform_hero",
        build_quality_meta(
            outline_ink=INK,
            foot_y=FOOT_Y,
            critique_frames=[0, atk_i + 4, atk_i + 8],
        ),
    )
    s.save_project(OUT / "platform_hero.sparkpix.json")
    print(s.stats())
    print("clips:", [c[0] for c in clip_meta])
    run_quality_gate()
    print("wrote", OUT)


if __name__ == "__main__":
    main()
