#!/usr/bin/env python3
"""Mech ranger — rig-based robot hero with shoot animation. Bullets: bullets/build.py."""

from __future__ import annotations

import math
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List, Sequence, Tuple

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from sparkpix import Sprite, ramp  # noqa: E402

OUT = Path(__file__).resolve().parent / "out"
W, H = 64, 64
FOOT_Y = 61
CANNON_LEN = 14

CHASSIS = ramp("#5a6478", 4)
CHASSIS_HI = ramp("#8aa0b8", 3)
DARK = ramp("#2a3038", 3)
ACCENT = ramp("#48c8e8", 4)  # cyan visor / LEDs
WARN = ramp("#e8a030", 3)
INK = "#12141c"
PAPER = "#e8f0f8"
MUZZLE = (255, 240, 160, 200)
MUZZLE_CORE = (255, 255, 220, 255)

PALETTE = [INK, PAPER] + CHASSIS + CHASSIS_HI + DARK + ACCENT + WARN


@dataclass
class Rig:
    dy: int = 0
    lean: int = 0
    foot_f: Tuple[int, int] = (30, FOOT_Y)
    foot_b: Tuple[int, int] = (24, FOOT_Y)
    knee_f: Tuple[int, int] = (29, 50)
    knee_b: Tuple[int, int] = (25, 51)
    hip: Tuple[int, int] = (27, 40)
    shoulder: Tuple[int, int] = (30, 28)
    cannon_pivot: Tuple[int, int] = (36, 30)
    cannon_deg: float = 0.0  # 0 = forward +X
    recoil: int = 0
    muzzle_flash: bool = False
    visor_glow: int = 0
    die: float = 0.0
    run: bool = False
    leg: float = 0.0


def blade_tip(px: int, py: int, deg: float, length: float) -> Tuple[int, int]:
    r = math.radians(deg)
    return int(px + math.cos(r) * length), int(py + math.sin(r) * length)


def fill_capsule(s: Sprite, x0: int, y0: int, x1: int, y1: int, radius: int, color) -> None:
    r = max(1, radius)
    for y in range(min(y0, y1) - r, max(y0, y1) + r + 1):
        for x in range(min(x0, x1) - r, max(x0, x1) + r + 1):
            dx, dy = x1 - x0, y1 - y0
            if dx == 0 and dy == 0:
                d = math.hypot(x - x0, y - y0)
            else:
                t = max(0, min(1, ((x - x0) * dx + (y - y0) * dy) / (dx * dx + dy * dy)))
                px, py = x0 + t * dx, y0 + t * dy
                d = math.hypot(x - px, y - py)
            if d <= r + 0.4:
                s.px(x, y, color)


def draw_leg(s: Sprite, hip: Tuple[int, int], knee: Tuple[int, int], foot: Tuple[int, int], back: bool) -> None:
    col = DARK[1] if back else CHASSIS[2]
    fill_capsule(s, hip[0], hip[1], knee[0], knee[1], 3 if not back else 2, col)
    fill_capsule(s, knee[0], knee[1], foot[0], foot[1], 3 if not back else 2, CHASSIS[1])
    fx, fy = foot
    s.rect(fx - 4, fy - 2, fx + 4, fy, fill=DARK[2])
    s.rect(fx - 3, fy, fx + 5, fy + 1, fill=ACCENT[0])


def draw_torso(s: Sprite, r: Rig) -> None:
    hx, hy = r.hip
    x0, x1 = hx - 7, hx + 6
    y0, y1 = hy - 14, hy + 1
    s.rect(x0, y0, x1, y1, fill=CHASSIS[1])
    s.rect(x0 + 1, y0 + 1, x1 - 1, y1 - 1, fill=CHASSIS[2], only="opaque")
    s.rect(x0 + 2, y0 + 3, x1 - 2, y0 + 8, fill=CHASSIS_HI[2], only="opaque")
    # chest port
    s.rect(hx - 1, hy - 10, hx + 2, hy - 7, fill=ACCENT[2 + (r.visor_glow % 2)])
    s.rect(x0, hy - 2, x1, hy, fill=WARN[1])


def draw_head(s: Sprite, r: Rig) -> None:
    cx, cy = 26 + r.lean, 17 + r.dy
    s.rect(cx - 5, cy - 4, cx + 7, cy + 8, fill=CHASSIS[2])
    s.rect(cx - 4, cy - 3, cx + 6, cy + 7, fill=CHASSIS[3], only="opaque")
    # visor slit
    s.rect(cx, cy + 1, cx + 5, cy + 3, fill=ACCENT[1])
    s.rect(cx + 1, cy + 1, cx + 4, cy + 2, fill=ACCENT[3] if r.visor_glow else ACCENT[2])
    # antenna
    s.line(cx + 3, cy - 4, cx + 3, cy - 8, DARK[2])
    s.px(cx + 3, cy - 8, ACCENT[3])


def draw_cannon(s: Sprite, r: Rig) -> None:
    px, py = r.cannon_pivot
    px -= r.recoil
    deg = r.cannon_deg
    ex, ey = blade_tip(px, py, deg, CANNON_LEN)
    fill_capsule(s, px, py, ex, ey, 3, CHASSIS[0])
    fill_capsule(s, px, py - 1, ex, ey - 1, 2, CHASSIS_HI[1])
    s.rect(px - 2, py - 3, px + 2, py + 3, fill=DARK[1])
    if r.muzzle_flash:
        mx, my = ex, ey
        for dx, dy in ((0, 0), (1, 0), (0, 1), (-1, 0), (2, 0)):
            s.px(mx + dx, my + dy, MUZZLE_CORE)
            s.px(mx + dx + 1, my + dy, MUZZLE)
        s.rect(mx, my - 2, mx + 5, my + 2, fill=MUZZLE)


def draw_robot(s: Sprite, r: Rig) -> None:
    s.clear()
    if r.die > 0.1:
        r = Rig(
            dy=r.dy + int(r.die * 6),
            lean=r.lean + int(r.die * 8),
            foot_f=(r.foot_f[0], r.foot_f[1]),
            foot_b=(r.foot_b[0], r.foot_b[1]),
            knee_f=r.knee_f,
            knee_b=r.knee_b,
            hip=(r.hip[0] + int(r.die * 4), r.hip[1] + int(r.die * 5)),
            shoulder=r.shoulder,
            cannon_pivot=(r.cannon_pivot[0] - int(r.die * 3), r.cannon_pivot[1]),
            cannon_deg=r.cannon_deg + r.die * 30,
            recoil=r.recoil,
            muzzle_flash=False,
            visor_glow=0,
            die=r.die,
            leg=r.leg,
        )
    draw_leg(s, r.hip, r.knee_b, r.foot_b, back=True)
    draw_torso(s, r)
    draw_leg(s, r.hip, r.knee_f, r.foot_f, back=False)
    draw_head(s, r)
    draw_cannon(s, r)


def walk_rig(phase: float) -> Rig:
    s = math.sin(phase)
    return Rig(
        dy=int(s),
        leg=phase,
        foot_f=(30 + int(s * 3), FOOT_Y),
        foot_b=(24 - int(s * 2), FOOT_Y),
        knee_f=(29 + int(s * 2), 50 - int(abs(s) * 2)),
        knee_b=(25, 51),
        cannon_deg=2 + s * 3,
    )


def run_rig(phase: float) -> Rig:
    s = math.sin(phase)
    return Rig(
        dy=int(s * 2),
        lean=2,
        leg=phase * 1.3,
        run=True,
        foot_f=(31 + int(s * 4), FOOT_Y),
        foot_b=(22 - int(s * 3), FOOT_Y),
        knee_f=(30 + int(s * 3), 48),
        cannon_deg=5 + s * 5,
    )


def shoot_rigs() -> List[Rig]:
    """Aim → fire (flash + recoil) → recover."""
    return [
        Rig(cannon_deg=-4, visor_glow=1),
        Rig(cannon_deg=0, visor_glow=2, recoil=0),
        Rig(cannon_deg=0, visor_glow=2, recoil=3, muzzle_flash=True),
        Rig(cannon_deg=1, visor_glow=2, recoil=2, muzzle_flash=True),
        Rig(cannon_deg=0, visor_glow=1, recoil=1),
        Rig(cannon_deg=-2, visor_glow=0),
    ]


def idle_rigs() -> List[Rig]:
    return [
        Rig(visor_glow=0, dy=0),
        Rig(visor_glow=1, dy=-1),
        Rig(visor_glow=1, dy=0),
        Rig(visor_glow=0, dy=1),
    ]


def die_rigs() -> List[Rig]:
    return [Rig(die=t, visor_glow=0 if t > 0.5 else 1) for t in [i / 5 for i in range(6)]]


def build() -> Tuple[List[Rig], List[Tuple[str, int, int, float, bool]]]:
    rigs: List[Rig] = []
    clips: List[Tuple[str, int, int, float, bool]] = []
    idx = 0

    def add(name: str, items: List[Rig], fps: float, loop: bool) -> None:
        nonlocal idx
        start = idx
        rigs.extend(items)
        idx += len(items)
        clips.append((name, start, idx - 1, fps, loop))

    add("idle", idle_rigs(), 4.0, True)
    add("walk", [walk_rig(i / 6 * math.pi * 2) for i in range(6)], 10.0, True)
    add("run", [run_rig(i / 6 * math.pi * 2) for i in range(6)], 14.0, True)
    add("shoot", shoot_rigs(), 12.0, False)
    add("die", die_rigs(), 8.0, False)
    return rigs, clips


def main() -> None:
    rigs, clips = build()
    s = Sprite(W, H, palette=PALETTE)
    for i, rig in enumerate(rigs):
        if i > 0:
            s.add_frame(copy=False)
        draw_robot(s, rig)

    OUT.mkdir(parents=True, exist_ok=True)
    s.preview(OUT / "preview_idle.png", scale=8)
    shoot_start = next(c[1] for c in clips if c[0] == "shoot")
    s.frame(shoot_start + 2)
    s.preview(OUT / "preview_shoot.png", scale=8)

    for name, a, b, fps, loop in clips:
        s.tag_clip(name, a, b, fps=fps, loop=loop)

    s.save_gif(OUT / "robot_ranger.gif", scale=4)
    s.save_spritesheet(OUT / "robot_ranger", columns=8, padding=0)
    s.save_project(OUT / "robot_ranger.sparkpix.json")
    print(s.stats())
    print("clips:", [c[0] for c in clips])
    print("wrote", OUT)


if __name__ == "__main__":
    main()
