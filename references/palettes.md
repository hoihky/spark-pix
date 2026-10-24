# Palettes

Built-in presets (`Sprite(palette="name")`):

| Name | Use |
|------|-----|
| `spark_neutral` | UI, stone, metal |
| `spark_forest` | outdoor platformer |
| `spark_dungeon` | interior, purple stone + torch orange |
| `spark_sky` | sky + clouds |

Custom: pass a list of hex strings or `ramp("#hex", 5) + ["#1a1c2c"]`.

## Budget

- **8–12** colors: Game Boy–style clarity.
- **16–24** colors: SNES-like characters + tiles in one pack.
- One transparent color only: `(0,0,0,0)` — do not use near-black alpha.

## Shared game palette

Define once in `pixel-art/_shared/palette.py` and import from every `build.py`
so characters and tiles match.
