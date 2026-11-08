"""Outfit dispatch — maps ``hero_config`` style ids to body drawers."""

from __future__ import annotations

from typing import Sequence, Tuple

from sparkpix.canvas import Sprite
from sparkpix.color import ColorLike
from sparkpix import character as ch
from sparkpix import jrpg_body as jb
from sparkpix import platform_body as pb

ColorSeq = Sequence[ColorLike]


def draw_jrpg_torso(
    s: Sprite,
    style: str,
    *,
    hip: Tuple[int, int],
    shoulder: Tuple[int, int],
    palette,
    squash: float = 1.0,
) -> None:
    if style == "tunic":
        jb.draw_q_tunic_torso(s, hip, tunic=palette.shirt, pants=palette.pants, squash=squash)
    elif style == "elder_cape":
        jb.draw_q_elder_cape_torso(
            s, hip, shoulder, cape=palette.shirt, tunic=palette.trim_or_shirt(), pants=palette.pants, squash=squash
        )
    elif style == "dress":
        jb.draw_q_dress_torso(s, hip, dress=palette.shirt, trim=palette.trim_or_shirt(), squash=squash)
    elif style == "long_coat":
        jb.draw_q_long_coat_torso(
            s,
            hip,
            coat=palette.shirt,
            shirt=palette.trim_or_shirt(),
            pants=palette.pants,
            belt=palette.belt_or_pants(),
            squash=squash,
        )
    elif style == "hoodie":
        ch.torso_hoodie(
            s,
            hip,
            shoulder,
            hood=palette.shirt,
            shirt=palette.trim_or_shirt(),
            shorts=palette.pants,
            cute=True,
        )
    else:
        raise ValueError(f"unknown jrpg outfit {style!r}")


def draw_jrpg_chest_bridge(s: Sprite, style: str, shoulder: Tuple[int, int], palette) -> None:
    cloth = palette.shirt
    if style == "dress":
        jb.draw_q_chest_bridge_dress(s, shoulder, dress=cloth)
    else:
        jb.draw_q_chest_bridge(s, shoulder, cloth=cloth)


def draw_jrpg_leg(
    s: Sprite,
    style: str,
    *,
    hip,
    knee,
    foot,
    back: bool,
    palette,
    shoe: str,
) -> None:
    boot = palette.boot
    if style == "dress":
        jb.draw_q_leg_dress(
            s, hip, knee, foot, back=back, stockings=palette.pants, shoe=boot
        )
    else:
        jb.draw_q_leg(s, hip, knee, foot, back=back, pants=palette.pants, boot=boot)


def draw_jrpg_arm(
    s: Sprite,
    style: str,
    *,
    shoulder,
    elbow,
    hand,
    palette,
) -> None:
    if style == "dress":
        jb.draw_q_arm_dress(s, shoulder, elbow, hand, dress=palette.shirt, skin=palette.skin)
    elif style in ("long_coat", "elder_cape"):
        jb.draw_q_arm_coat(
            s,
            shoulder,
            elbow,
            hand,
            coat=palette.shirt,
            shirt=palette.trim_or_shirt(),
            skin=palette.skin,
        )
    else:
        jb.draw_q_arm_sleeve(s, shoulder, elbow, hand, tunic=palette.shirt, skin=palette.skin)


def draw_platform_torso(
    s: Sprite,
    style: str,
    *,
    hip,
    shoulder,
    palette,
    squash: float = 1.0,
    compact: bool = True,
) -> None:
    if style == "gi_shorts":
        pb.draw_torso_gi(
            s,
            hip,
            shoulder,
            shirt=palette.shirt,
            trim=palette.trim_or_shirt(),
            belt=palette.belt_or_pants(),
            squash=squash,
            compact=compact,
        )
    elif style == "hoodie_shorts":
        ch.torso_hoodie(
            s,
            hip,
            shoulder,
            hood=palette.shirt,
            shirt=palette.trim_or_shirt(),
            shorts=palette.pants,
            cute=False,
        )
    else:
        raise ValueError(f"unknown platform outfit {style!r}")


def draw_platform_leg(
    s: Sprite,
    *,
    hip,
    knee,
    foot,
    back: bool,
    palette,
    compact: bool = True,
) -> None:
    pb.draw_shorts_leg(
        s,
        hip,
        knee,
        foot,
        back=back,
        pants=palette.pants,
        boot=palette.boot,
        glove=palette.glove_or_shirt(),
        compact=compact,
    )


def draw_platform_arm(
    s: Sprite,
    *,
    shoulder,
    elbow,
    hand,
    palette,
    back: bool = False,
    compact: bool = True,
) -> None:
    pb.draw_arm_gi(
        s,
        shoulder,
        elbow,
        hand,
        shirt=palette.shirt,
        skin=palette.skin,
        glove=palette.glove_or_shirt(),
        back=back,
        compact=compact,
    )
