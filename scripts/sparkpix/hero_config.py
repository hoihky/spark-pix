"""
Developer-facing character knobs — document in ``pixel-art/<name>/PROMPT.md`` and set
at the top of each ``build.py``.

Colors are :func:`sparkpix.color.ramp` stacks (3–5 steps). Styles select procedural
drawers in ``jrpg_body`` / ``platform_body`` / ``platform_weapon``.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal, Sequence

from sparkpix.canvas import Sprite
from sparkpix.color import ColorLike
from sparkpix.jrpg_face import JrpgHeadLook
from sparkpix.platform_face import FighterHeadLook

ColorSeq = Sequence[ColorLike]
Track = Literal["jrpg_q", "platform_fighter"]


@dataclass
class EyeColors:
    """Eye tints — passed into head draw helpers (style controls layout, not hue)."""

    pupil: ColorLike = "#282830"
    iris: ColorLike = "#5090c0"
    sclera: ColorLike = "#f0f0e8"
    paper: ColorLike = "#ffffff"
    blush: ColorLike = "#ffc5b4"


@dataclass
class CharacterPalette:
    """
    Material ramps for one hero. Rename in ``build.py``; swap hex roots only to recolor.

    ``weapon`` / ``scarf`` may be unused when ``WeaponStyle`` / outfit omits them.
    """

    hair: ColorSeq
    skin: ColorSeq
    shirt: ColorSeq
    pants: ColorSeq
    boot: ColorSeq
    ink: ColorLike
    trim: ColorSeq | None = None
    belt: ColorSeq | None = None
    glove: ColorSeq | None = None
    scarf: ColorSeq | None = None
    weapon: ColorSeq | None = None
    eye: EyeColors = field(default_factory=EyeColors)

    def trim_or_shirt(self) -> ColorSeq:
        return self.trim if self.trim is not None else self.shirt

    def belt_or_pants(self) -> ColorSeq:
        return self.belt if self.belt is not None else self.pants

    def glove_or_shirt(self) -> ColorSeq:
        return self.glove if self.glove is not None else self.shirt


# --- Outfit / shoe / weapon style ids (strings in build.py) -----------------

JRPG_OUTFIT_STYLES = (
    "tunic",  # ``draw_q_tunic_torso`` + ``draw_q_arm_sleeve``
    "elder_cape",  # ``draw_q_elder_cape_torso`` + cape arms
    "dress",  # ``draw_q_dress_torso`` + dress arms/legs
    "long_coat",  # ``draw_q_long_coat_torso`` + coat arms
    "hoodie",  # ``character.torso_hoodie`` (64 platform-tight heroes)
)

PLATFORM_OUTFIT_STYLES = (
    "gi_shorts",  # ``draw_torso_gi`` + ``draw_shorts_leg`` + ``draw_arm_gi``
    "hoodie_shorts",  # ``torso_hoodie`` + ``draw_shorts_leg``
)

SHOE_STYLES = (
    "q_boot",  # default blocks in ``draw_q_leg`` / ``draw_q_leg_dress``
    "gi_boot",  # ``draw_shorts_leg`` ankle wrap
    "dress_slip",  # softer shoe line on ``draw_q_leg_dress``
)

WEAPON_STYLES = (
    "none",
    "scarf",  # no hand weapon — use ``platform_scarf`` only
    "baton",  # ``platform_weapon.draw_weapon_baton``
    "stick",  # thin rod
    "blade",  # short angled blade
)


@dataclass(frozen=True)
class ClipSpec:
    name: str
    frames: int
    fps: float
    loop: bool = True
    enabled: bool = True


# Default platform fighter parity set (disable clips with ``enabled=False``).
PLATFORM_CLIP_TABLE: tuple[ClipSpec, ...] = (
    ClipSpec("idle", 10, 8),
    ClipSpec("walk", 10, 10),
    ClipSpec("run", 10, 14),
    ClipSpec("jump", 6, 12, loop=False),
    ClipSpec("fall", 4, 12, loop=False),
    ClipSpec("fall_loop", 3, 10),
    ClipSpec("dash", 8, 14, loop=False),
    ClipSpec("combo_1", 3, 14, loop=False),
    ClipSpec("combo_1_end", 4, 14, loop=False),
)

JRPG_CLIP_TABLE: tuple[ClipSpec, ...] = (
    ClipSpec("idle", 4, 4),
    ClipSpec("walk", 6, 10),
    ClipSpec("run", 6, 12),
)


@dataclass
class AnimationPlan:
    """
    Which clips to bake and how to tag the Spark atlas.

    Example::

        PLAN = AnimationPlan.from_table(PLATFORM_CLIP_TABLE, disable={"dash"})
    """

    clips: tuple[ClipSpec, ...]

    @classmethod
    def from_table(
        cls,
        table: Sequence[ClipSpec],
        *,
        only: set[str] | None = None,
        disable: set[str] | None = None,
    ) -> AnimationPlan:
        out: list[ClipSpec] = []
        for c in table:
            if only is not None and c.name not in only:
                continue
            enabled = c.enabled and (disable is None or c.name not in disable)
            out.append(
                ClipSpec(c.name, c.frames, c.fps, c.loop, enabled)
            )
        return cls(tuple(out))

    def enabled(self) -> tuple[ClipSpec, ...]:
        return tuple(c for c in self.clips if c.enabled)

    def total_frames(self) -> int:
        return sum(c.frames for c in self.enabled())

    def tag_on_sprite(self, s: Sprite, *, start_at: int = 0) -> dict[str, tuple[int, int]]:
        """Append ``tag_clip`` entries; return ``{name: (from, to)}`` frame indices."""
        cursor = start_at
        ranges: dict[str, tuple[int, int]] = {}
        for c in self.enabled():
            a, b = cursor, cursor + c.frames - 1
            s.tag_clip(c.name, a, b, fps=c.fps, loop=c.loop)
            ranges[c.name] = (a, b)
            cursor += c.frames
        return ranges


@dataclass
class JrpgHeroKnobs:
    """64×64 Q track — pair with ``JrpgHeadLook`` + ``jrpg_body`` dispatchers."""

    track: Track = "jrpg_q"
    head: JrpgHeadLook = field(default_factory=JrpgHeadLook)
    outfit: str = "tunic"
    shoe: str = "q_boot"
    weapon: str = "none"
    animation: AnimationPlan = field(default_factory=lambda: AnimationPlan(JRPG_CLIP_TABLE))


@dataclass
class PlatformHeroKnobs:
    """128×128 fighter track — ``FighterHeadLook`` + ``platform_*`` modules."""

    track: Track = "platform_fighter"
    head: FighterHeadLook = field(default_factory=FighterHeadLook)
    outfit: str = "gi_shorts"
    shoe: str = "gi_boot"
    weapon: str = "scarf"
    animation: AnimationPlan = field(
        default_factory=lambda: AnimationPlan(PLATFORM_CLIP_TABLE)
    )


def validate_knobs(knobs: JrpgHeroKnobs | PlatformHeroKnobs) -> None:
    """Raise ``ValueError`` on unknown style ids (call at import time in ``build.py``)."""
    if isinstance(knobs, JrpgHeroKnobs):
        if knobs.outfit not in JRPG_OUTFIT_STYLES:
            raise ValueError(f"unknown jrpg outfit {knobs.outfit!r}")
        if knobs.shoe not in SHOE_STYLES:
            raise ValueError(f"unknown shoe {knobs.shoe!r}")
    else:
        if knobs.outfit not in PLATFORM_OUTFIT_STYLES:
            raise ValueError(f"unknown platform outfit {knobs.outfit!r}")
        if knobs.shoe not in SHOE_STYLES:
            raise ValueError(f"unknown shoe {knobs.shoe!r}")
    if knobs.weapon not in WEAPON_STYLES:
        raise ValueError(f"unknown weapon {knobs.weapon!r}")
