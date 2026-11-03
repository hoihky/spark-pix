#!/usr/bin/env python3
"""
Reference youth — cyan spiky hair, 2×3 vertical eye, olive tunic + fists.

Matches project reference screenshot (side +X). Clips: idle, walk, run.
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
from sparkpix import jrpg_body as jb  # noqa: E402
from sparkpix import rig  # noqa: E402
from sparkpix.jrpg_face import JrpgHeadLook  # noqa: E402
from sparkpix.q_style import FOOT_Y, KNEE_Y, MIN_HEIGHT_FILL, Q64  # noqa: E402

OUT = Path(__file__).resolve().parent / "out"
W, H = 64, 64
NAME = "ref_youth"

HEAD_LOOK = JrpgHeadLook(
    hair_style="spiky",
    eye_style="vertical",
    forehead="none",
    beard=False,
    fringe_over_eye=True,
)

SKIN = ramp("#d8a880", 4)
HAIR = ramp("#0c2840", 5)
TUNIC = ramp("#786840", 4)
PANTS = ramp("#382820", 4)
BOOT = ramp("#503828", 3)
SCARF = TUNIC
INK = "#101420"
PAPER = "#f8fcff"
PUPIL = "#0a1018"
IRIS = "#2878a8"
SCLERA = "#ffffff"
SHADOW = (12, 10, 18, 90)

PALETTE = [INK, PAPER, PUPIL, IRIS, SCLERA] + SKIN + HAIR + TUNIC + PANTS + BOOT + [SHADOW]


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
        r.dy, r.lean, r.foot_f, r.foot_b, r.knee_f, r.knee_b,
        r.hip, r.shoulder, r.elbow, r.hand, r.head,
    )
    return Rig(dy=0, lean=0, squash=r.squash, **pts)


def draw_shadow(s: Sprite, r: Rig) -> None:
    cx = (r.foot_f[0] + r.foot_b[0]) // 2
    ch.drop_shadow_oval(s, cx, FOOT_Y, SHADOW, half_w=6)


def draw_head(s: Sprite, r: Rig) -> None:
    cx, cy = r.head
    ch.profile_head_facing_right(
        s, cx, cy,
        skin=SKIN, hair=HAIR, band=SCARF,
        eye_green=IRIS, sclera=SCLERA, paper=PAPER, pupil=PUPIL,
        lash=HAIR[0], look=HEAD_LOOK, cute=True,
    )


def draw_back_arm(s: Sprite, r: Rig) -> None:
    sx, sy = r.shoulder[0] - 2, r.shoulder[1] + 1
    ch.limb(s, (sx, sy), (sx - 3, sy + 7), 2, TUNIC[1])


def draw_frame_content(s: Sprite, r: Rig) -> None:
    jb.draw_q_leg(s, r.hip, r.knee_b, r.foot_b, back=True, pants=PANTS, boot=BOOT)
    draw_back_arm(s, r)
    jb.draw_q_tunic_torso(s, r.hip, tunic=TUNIC, pants=PANTS, squash=r.squash)
    jb.draw_q_chest_bridge(s, r.shoulder, cloth=TUNIC)
    jb.draw_q_leg(s, r.hip, r.knee_f, r.foot_f, back=False, pants=PANTS, boot=BOOT)
    draw_head(s, r)
    jb.draw_q_arm_sleeve(s, r.shoulder, r.elbow, r.hand, tunic=TUNIC, skin=SKIN)
    ch.finish_production_humanoid(s, INK)


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
        dy=int(s * 2), lean=2, squash=0.92,
        foot_f=(Q64.foot_f[0] + 1 + int(s * 4), FOOT_Y),
        foot_b=(Q64.foot_b[0] - 3 - int(s * 3), FOOT_Y),
        knee_f=(Q64.knee_f[0] + int(s * 3), KNEE_Y - 4 - int(abs(s) * 3)),
        knee_b=(Q64.knee_b[0] - 2 - int(s * 2), KNEE_Y - 3),
        hip=(Q64.hip[0], Q64.hip[1] - 1),
        shoulder=(Q64.shoulder[0] + 1, Q64.shoulder[1] - 1),
        elbow=(Q64.elbow[0] + 2, Q64.elbow[1] - 1),
        hand=(Q64.hand[0] + 3, Q64.hand[1] - 2),
    )


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
    return rigs, clips


def main() -> None:
    rigs, clips = build_all()
    s = Sprite(W, H, palette=PALETTE)
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
    for name, a, b, fps, loop in clips:
        s.tag_clip(name, a, b, fps=fps, loop=loop)
    s.save_gif(OUT / f"{NAME}_all.gif", scale=4)
    s.save_spritesheet(OUT / NAME, columns=10, padding=0, spark_json=True)
    s.save_project(OUT / f"{NAME}.sparkpix.json")

    from sparkpix.quality import build_quality_meta, critique_atlas_dir, format_report, write_quality_sidecar

    write_quality_sidecar(
        OUT, NAME,
        build_quality_meta(outline_ink=INK, foot_y=FOOT_Y, critique_frames=[0], max_colors=36, min_height_fill=MIN_HEIGHT_FILL),
    )
    text = format_report(critique_atlas_dir(OUT))
    if text != "OK (no quality warnings)":
        print(text)
    print(s.stats())
    print("wrote", OUT)


if __name__ == "__main__":
    main()
