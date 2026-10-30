# Palettes

**Production standard:** One coherent palette per **game pack** (characters + tiles + props).
Import shared ramps so art matches at 1× in the same scene.

Built-in presets (`Sprite(palette="name")`):

| Name | Use |
|------|-----|
| `spark_neutral` | UI, stone, metal |
| `spark_forest` | outdoor platformer |
| `spark_dungeon` | interior, purple stone + torch orange |
| `spark_sky` | sky + clouds |

Custom: pass a list of hex strings or `ramp("#hex", 5) + ["#1a1c2c"]`.

## Budget

| Budget | Use |
|--------|-----|
| **8–12** | Game Boy–style clarity, small props |
| **16–24** | SNES-like characters + tiles in one shippable pack |
| **24+** | Only if brief demands; justify in build header |

One transparent color only: `(0,0,0,0)` — do not use near-black alpha.

## Shared game palette

Import in every production `build.py`:

```python
from sparkpix.game_palette import GRASS, INK, SPARK_GAME, palette_for_sprite
```

Optional JSON export for designers:

```bash
python -m sparkpix palette export pixel-art/_shared/spark_game.palette.json
```

See `pixel-art/_shared/README.md`. Characters and tilesets in the same game should pull from the same module so grass, stone, and skin tones harmonize.

## Ship check

- [ ] `used_colors()` count ≤ brief budget before atlas/tileset export.
- [ ] No accidental near-duplicate shades (merge in code, not in Photoshop).
