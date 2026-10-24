"""Shared Spark game palette — use across characters, tiles, and VFX."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Sequence, Union

from sparkpix.color import RGBA, ramp

# Transparent background (only alpha=0 swatch; not counted in color budget).
TRANSPARENT: RGBA = (0, 0, 0, 0)

# Core neutrals
INK: str = "#1a1c2c"
PAPER: str = "#f4f4f4"
SHADOW: str = "#2d1b3d"

# Ramps (darkest → lightest)
SKIN = ramp("#e8b080", 4)
HAIR = ramp("#4a3020", 4)
METAL = ramp("#8a9aaa", 4)
GRASS = ramp("#3d9a48", 5)
DIRT = ramp("#8a5a38", 4)
STONE = ramp("#6a6a78", 4)
WATER = ramp("#3a88c8", 4)
MAGIC = ramp("#9a58d8", 4)
FIRE = ramp("#e85830", 4)

# Flat accents
ACCENT_GOLD = "#f0c040"
ACCENT_RED = "#d03048"
ACCENT_GREEN = "#48c070"

SPARK_GAME_HEX: List[str] = (
    [INK, PAPER, SHADOW, ACCENT_GOLD, ACCENT_RED, ACCENT_GREEN]
    + [f"#{r:02x}{g:02x}{b:02x}" for r, g, b, a in SKIN + HAIR + METAL + GRASS + DIRT + STONE + WATER + MAGIC + FIRE]
)

# Deduplicate while preserving order
_seen: set[RGBA] = set()
SPARK_GAME: List[RGBA] = []
for h in SPARK_GAME_HEX:
    from sparkpix.color import parse_color

    c = parse_color(h)
    if c and c not in _seen and c[3] > 0:
        _seen.add(c)
        SPARK_GAME.append(c)


def palette_for_sprite() -> List[Union[str, RGBA]]:
    """Pass to ``Sprite(..., palette=palette_for_sprite())``."""
    return list(SPARK_GAME)


def index_of(hex_color: str) -> int:
    from sparkpix.color import parse_color, nearest_palette_index

    c = parse_color(hex_color)
    if c is None:
        raise ValueError(hex_color)
    return nearest_palette_index(c, SPARK_GAME)


def export_json(path: Path) -> None:
    data: Dict[str, Any] = {
        "name": "spark_game",
        "colors": [f"#{r:02x}{g:02x}{b:02x}" for r, g, b, a in SPARK_GAME],
        "ramps": {
            "skin": [f"#{r:02x}{g:02x}{b:02x}" for r, g, b, a in SKIN],
            "grass": [f"#{r:02x}{g:02x}{b:02x}" for r, g, b, a in GRASS],
            "stone": [f"#{r:02x}{g:02x}{b:02x}" for r, g, b, a in STONE],
        },
        "constants": {
            "ink": INK,
            "paper": PAPER,
            "shadow": SHADOW,
        },
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def describe() -> str:
    return f"spark_game: {len(SPARK_GAME)} colors (shared character/tile palette)"
