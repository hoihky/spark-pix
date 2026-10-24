# spark-pix

Agent skill + Python toolkit for generating **2D pixel game art** (sprites, animation,
tilesets) with **Pillow**, exported for the [Spark](https://hoihky.github.io/spark/) game engine.

**Introduction (web):** [docs/index.html](docs/index.html)

## Install

```bash
cd spark-pix   # repository root
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

(`pip install -r requirements.txt` works too; `-e .` enables `python -m sparkpix`.)

## Use as a Cursor skill

Copy or symlink this folder into your skills path, or open this repo in Cursor and
invoke the **spark-pix** skill. The agent reads `SKILL.md` and runs `build.py` workflows.

## CLI

```bash
python -m sparkpix palette show
python -m sparkpix palette export pixel-art/_shared/spark_game.palette.json
python -m sparkpix validate pixel-art/example_slime/out
python -m sparkpix manifest summary assets/for-spark/slime.spark-atlas.json
python -m sparkpix study reference.png pixel-art/_study/ref
```

## Shared palette

Use `from sparkpix.game_palette import GRASS, INK, SPARK_GAME, palette_for_sprite` in any `build.py`, or import via `pixel-art/_shared/game_palette.py`.

## Quick example

```bash
python3 pixel-art/example_slime/build.py
python -m sparkpix validate pixel-art/example_slime/out
```

Outputs: `out/slime.png`, `out/slime.spark-atlas.json`, preview GIF/PNG.

## Spark deployment

Copy `out/*.png` and `*.spark-atlas.json` to your Spark tree:

`../spark/assets/sprites/<your-pack>/` (sibling checkout) or see [references/paths-and-privacy.md](references/paths-and-privacy.md).

Wire `SpriteAnimatorComponent` using grid size and clips from the JSON manifest
(see `references/spark-export.md`), or run Spark demo **30 — Spark-pix atlas** (see
`spark-integration/INTEGRATION.md`).

## Layout

| Path | Role |
|------|------|
| `SKILL.md` | Agent instructions |
| `scripts/sparkpix/` | Drawing & export library |
| `scripts/validate.py` | Atlas manifest checks |
| `scripts/study.py` | Reference PNG analysis |
| `references/` | Techniques, Spark formats, [paths & privacy](references/paths-and-privacy.md) |
| `pixel-art/` | Per-asset `build.py` projects |

## License

[MIT](LICENSE) — see [paths & privacy](references/paths-and-privacy.md) for what not to commit.
