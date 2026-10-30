#!/usr/bin/env python3
"""
Stoic swordsman — rig-based humanoid (64×64), side-view RPG proportions.
See references/humanoid-hero.md and repo SKILL.md.
"""

from __future__ import annotations

import math
import sys
from dataclasses import dataclass
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
BLADE_LEN = 35  # long greatsword — nearly shin to ground when idle

SKIN = ramp("#e0b090", 4)
HAIR = ramp("#e8e6f0", 5)  # silver-white volume (original character)
TUNIC = ramp("#8a9070", 4)  # olive-khaki tunic
PANTS = ramp("#3a2820", 4)
BOOT = ramp("#4a3428", 3)
BELT_C = ramp("#2a1810", 3)
METAL = ramp("#788898", 4)
GOLD = ramp("#d0a838", 3)
INK = "#1a1c2c"
PAPER = "#f4f4f4"
EYE = "#58c878"
GUARD_BLUE = "#4088c8"
SWIPE = (200, 220, 255, 150)
SWIPE_FADE = (150, 170, 200, 80)

PALETTE = [INK, PAPER, EYE, GUARD_BLUE] + SKIN + HAIR + TUNIC + PANTS + BOOT + BELT_C + METAL + GOLD


@dataclass
class Rig:
    dy: int = 0
    lean: int = 0
    # front leg (nearer camera) / back leg
    foot_f: Tuple[int, int] = (30, FOOT_Y)
    foot_b: Tuple[int, int] = (24, FOOT_Y)
    knee_f: Tuple[int, int] = (29, 50)
    knee_b: Tuple[int, int] = (25, 51)
    hip: Tuple[int, int] = (27, 40)
    shoulder: Tuple[int, int] = (30, 30)
    elbow: Tuple[int, int] = (35, 37)
    hand: Tuple[int, int] = (37, 40)
    head: Tuple[int, int] = (26, 19)
    sword_deg: float = 74.0
    sword_trail: Tuple[float, ...] = ()
    die: float = 0.0


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
        sword_deg=r.sword_deg,
        sword_trail=r.sword_trail,
        die=r.die,
    )


def draw_shadow(s: Sprite, r: Rig) -> None:
    cx = (r.foot_f[0] + r.foot_b[0]) // 2
    ch.drop_shadow_oval(s, cx, FOOT_Y, INK, half_w=6)


def draw_leg(s: Sprite, hip: Tuple[int, int], knee: Tuple[int, int], foot: Tuple[int, int], back: bool) -> None:
    col_t = PANTS[0] if back else PANTS[2]
    col_s = PANTS[1]
    col_b = BOOT[0] if back else BOOT[1]
    ch.limb(s, hip, knee, 2 if back else 3, col_t)
    ch.limb(s, knee, foot, 2 if back else 3, col_s)
    fx, fy = foot
    s.rect(fx - 3, fy - 2, fx + 4, fy, fill=col_b)
    s.rect(fx - 2, fy, fx + 5, fy + 1, fill=INK)


def draw_torso(s: Sprite, r: Rig) -> None:
    hx, hy = r.hip
    x0, x1 = hx - 6, hx + 5
    y0, y1 = hy - 12, hy + 2
    s.rect(x0, y0, x1, y1, fill=TUNIC[1])
    s.rect(x0 + 1, y0 + 1, x1 - 1, y1 - 1, fill=TUNIC[2], only="opaque")
    s.rect(x1 - 2, y0 + 2, x1, y1 - 2, fill=TUNIC[0], only="opaque")
    # belt
    by = hy - 1
    s.rect(x0, by, x1, by + 2, fill=BELT_C[1])
    s.rect(hx - 1, by, hx + 1, by + 2, fill=METAL[3])
    # back arm hint
    s.rect(x0 - 2, y0 + 5, x0, y0 + 11, fill=TUNIC[0])


def draw_messy_hair(s: Sprite, cx: int, cy: int, tilt: int, sway: int = 0) -> None:
    """Layered messy volume — back mass, crown spikes, face-framing clumps."""
    t = tilt
    sw = sway
    # shadow mass behind head (left / back)
    s.ellipse(cx - 9 + sw, cy - 5 + t, cx + 1 + sw, cy + 10 + t, fill=HAIR[0])
    s.ellipse(cx - 8 + sw, cy - 4 + t, cx + 2 + sw, cy + 9 + t, fill=HAIR[1], only="opaque")
    # crown volume
    s.ellipse(cx - 4 + sw, cy - 10 + t, cx + 8 + sw, cy + 2 + t, fill=HAIR[1])
    s.ellipse(cx - 3 + sw, cy - 9 + t, cx + 7 + sw, cy + 1 + t, fill=HAIR[2], only="opaque")
    spikes = [
        [(cx - 2 + sw, cy - 4 + t), (cx + 1 + sw, cy - 12 + t), (cx + 5 + sw, cy - 8 + t), (cx + 4 + sw, cy - 3 + t)],
        [(cx + 3 + sw, cy - 5 + t), (cx + 7 + sw, cy - 11 + t), (cx + 10 + sw, cy - 6 + t), (cx + 7 + sw, cy - 2 + t)],
        [(cx - 6 + sw, cy - 2 + t), (cx - 4 + sw, cy - 8 + t), (cx - 1 + sw, cy - 7 + t), (cx - 2 + sw, cy - 1 + t)],
    ]
    for i, pts in enumerate(spikes):
        s.polygon(pts, fill=HAIR[2 + (i % 2)])
    # messy fringe over forehead (not covering eye)
    s.polygon(
        [(cx + 1 + sw, cy - 3 + t), (cx + 5 + sw, cy - 6 + t), (cx + 8 + sw, cy - 2 + t), (cx + 6 + sw, cy + 1 + t)],
        fill=HAIR[3],
        only="opaque",
    )
    # highlights (upper-left light)
    s.polygon([(cx + 2 + sw, cy - 8 + t), (cx + 6 + sw, cy - 9 + t), (cx + 5 + sw, cy - 6 + t)], fill=HAIR[4])
    s.px(cx + 4 + sw, cy - 7 + t, PAPER)
    s.px(cx + 5 + sw, cy - 8 + t, PAPER)
    # dangling back strand
    s.rect(cx - 8 + sw, cy + 4 + t, cx - 6 + sw, cy + 9 + t, fill=HAIR[1])
    s.rect(cx - 7 + sw, cy + 5 + t, cx - 5 + sw, cy + 10 + t, fill=HAIR[2], only="opaque")


def draw_head(s: Sprite, r: Rig) -> None:
    cx, cy = r.head
    tilt = int(r.die * 8)
    sway = int(math.sin(r.sword_deg * 0.05) * 1)  # micro hair sway with pose
    s.ellipse(cx - 5, cy - 5 + tilt, cx + 6, cy + 8 + tilt, fill=SKIN[1])
    s.ellipse(cx - 4, cy - 4 + tilt, cx + 5, cy + 7 + tilt, fill=SKIN[2], only="opaque")
    s.rect(cx - 3, cy + 4 + tilt, cx + 2, cy + 7 + tilt, fill=SKIN[0], only="opaque")
    draw_messy_hair(s, cx, cy, tilt, sway)
    s.px(cx + 4, cy + 3 + tilt, EYE)
    s.px(cx + 3, cy + 4 + tilt, SKIN[0])


def draw_arm(s: Sprite, r: Rig) -> None:
    ch.limb(s, r.shoulder, r.elbow, 2, SKIN[2])
    ch.limb(s, r.elbow, r.hand, 2, SKIN[1])


def draw_sword(s: Sprite, r: Rig) -> None:
    hx, hy = r.hand
    if r.sword_trail:
        ch.weapon_angle_trail(s, hx, hy, r.sword_trail, BLADE_LEN, SWIPE_FADE, SWIPE)
    s.rect(hx - 2, hy - 1, hx + 4, hy + 1, fill=GOLD[1])
    s.rect(hx - 1, hy - 2, hx + 3, hy + 2, fill=GOLD[2], only="opaque")
    s.px(hx + 1, hy, GUARD_BLUE)
    bx, by = hx + 2, hy
    ex, ey = rig.tip(bx, by, r.sword_deg, BLADE_LEN)
    ch.limb(s, (bx, by), (ex, ey), 2, METAL[1])
    rad = math.radians(r.sword_deg - 90)
    ox, oy = int(math.cos(rad) * 2), int(math.sin(rad) * 2)
    ch.limb(s, (bx + ox, by + oy), (ex + ox, ey + oy), 1, METAL[3])
    s.px(ex, ey, PAPER)
    s.px(ex - 1, ey, METAL[3])


def draw_body_content(s: Sprite, r: Rig, *, with_outline: bool = True) -> None:
    sword_back = rig.weapon_raised_behind_head(r.sword_deg, 75.0)
    draw_leg(s, r.hip, r.knee_b, r.foot_b, back=True)
    if sword_back:
        draw_sword(s, r)
    draw_torso(s, r)
    draw_leg(s, r.hip, r.knee_f, r.foot_f, back=False)
    draw_head(s, r)
    draw_arm(s, r)
    if not sword_back:
        draw_sword(s, r)
    if with_outline:
        ch.finish_outside_outline(s, INK)


def draw_human(s: Sprite, rig: Rig) -> None:
    s.clear()
    r = finalize(rig)
    if rig.die > 0.05:
        r = Rig(
            dy=r.dy,
            lean=r.lean + int(rig.die * 10),
            foot_f=(r.foot_f[0] + int(rig.die * 4), r.foot_f[1]),
            foot_b=(r.foot_b[0] + int(rig.die * 2), r.foot_b[1]),
            hip=(r.hip[0] + int(rig.die * 6), r.hip[1] + int(rig.die * 3)),
            knee_f=r.knee_f,
            knee_b=r.knee_b,
            shoulder=r.shoulder,
            elbow=r.elbow,
            hand=r.hand,
            head=r.head,
            sword_deg=r.sword_deg + rig.die * 40,
            sword_trail=r.sword_trail,
            die=rig.die,
        )
    draw_shadow(s, r)
    draw_body_content(s, r)


def check_silhouette(s: Sprite, frame_index: int = 0) -> None:
    ch.warn_if_stick_legs(s, FOOT_Y, frame=frame_index)


def idle_rig(i: int) -> Rig:
    breath = (i % 4) - 1
    return Rig(dy=breath, sword_deg=73 + (i % 3) - 1, hand=(37, 40), elbow=(35, 37))


def walk_rig(phase: float) -> Rig:
    s = math.sin(phase)
    return Rig(
        dy=int(s * 1),
        foot_f=(30 + int(s * 3), FOOT_Y),
        foot_b=(24 - int(s * 2), FOOT_Y),
        knee_f=(29 + int(s * 2), 50 - int(abs(s) * 2)),
        knee_b=(25 - int(s), 51),
        hip=(27, 40),
        hand=(37, 40),
        sword_deg=72 + s * 4,
    )


def run_rig(phase: float) -> Rig:
    s = math.sin(phase)
    return Rig(
        dy=int(s * 2),
        lean=2,
        foot_f=(32 + int(s * 4), FOOT_Y),
        foot_b=(22 - int(s * 3), FOOT_Y),
        knee_f=(30 + int(s * 3), 48 - int(abs(s) * 3)),
        knee_b=(24 - int(s * 2), 49),
        hip=(28, 39),
        shoulder=(31, 29),
        hand=(38, 39),
        sword_deg=62 + s * 8,
    )


def attack_rigs() -> List[Rig]:
    angles = [74, 102, 132, 108, 78, 42, 24, 70]
    trails: List[Tuple[float, ...]] = [
        (),
        (74, 102),
        (74, 102, 132),
        (102, 132, 108),
        (132, 108, 78),
        (108, 78, 42),
        (78, 42, 24),
        (70,),
    ]
    rigs = []
    for ang, tr in zip(angles, trails):
        rigs.append(
            Rig(
                lean=4,
                shoulder=(31, 29),
                elbow=(35, 33),
                hand=(37, 36),
                sword_deg=float(ang),
                sword_trail=tr,
            )
        )
    return rigs


def jump_rigs() -> List[Rig]:
    return [
        Rig(dy=3, foot_f=(30, FOOT_Y), foot_b=(24, FOOT_Y), knee_f=(29, 52), knee_b=(25, 52), sword_deg=74),
        Rig(dy=0, knee_f=(30, 49), knee_b=(25, 50), sword_deg=70),
        Rig(dy=-12, foot_f=(29, 54), foot_b=(25, 54), knee_f=(28, 48), knee_b=(26, 48), sword_deg=62),
        Rig(dy=-3, foot_f=(30, FOOT_Y), foot_b=(24, FOOT_Y), sword_deg=70),
    ]


def die_rigs() -> List[Rig]:
    return [Rig(die=t, dy=int(t * 6), lean=int(t * 12), sword_deg=70 + t * 30) for t in [i / 5 for i in range(6)]]


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
    add("walk", [walk_rig(i / 6 * math.pi * 2) for i in range(6)], 10.0, True)
    add("run", [run_rig(i / 6 * math.pi * 2) for i in range(6)], 14.0, True)
    add("attack", attack_rigs(), 14.0, False)
    add("jump", jump_rigs(), 10.0, False)
    add("die", die_rigs(), 8.0, False)
    return rigs, clips


def main() -> None:
    rigs, clips = build_all()
    s = Sprite(W, H, palette=PALETTE)
    for i, rig in enumerate(rigs):
        if i > 0:
            s.add_frame(copy=False)
        draw_human(s, rig)
        if i == 0:
            check_silhouette(s)

    OUT.mkdir(parents=True, exist_ok=True)
    matte = "#343848"
    s.preview(OUT / "preview_idle.png", scale=8, matte=matte)
    s.preview(OUT / "preview_sheet.png", scale=4, grid=True, matte=matte)
    atk_i = next(c[1] for c in clips if c[0] == "attack")
    s.frame(atk_i + 4)
    s.preview(OUT / "preview_attack_slash.png", scale=8, matte=matte)

    for name, a, b, fps, loop in clips:
        s.tag_clip(name, a, b, fps=fps, loop=loop)

    s.save_gif(OUT / "vanguard_all.gif", scale=4)
    s.save_spritesheet(OUT / "vanguard", columns=10, padding=0, spark_json=True)
    s.save_project(OUT / "vanguard.sparkpix.json")

    from sparkpix.quality import build_quality_meta, critique_atlas_dir, format_report, write_quality_sidecar

    write_quality_sidecar(
        OUT,
        "vanguard",
        build_quality_meta(
            outline_ink=INK,
            foot_y=FOOT_Y,
            critique_frames=[0, atk_i + 2, atk_i + 4],
        ),
    )
    report = critique_atlas_dir(OUT)
    text = format_report(report)
    if text != "OK (no quality warnings)":
        print(text)

    print(s.stats())
    print("clips:", [c[0] for c in clips])
    print("wrote", OUT)


if __name__ == "__main__":
    main()
