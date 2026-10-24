---
name: spark-pix
description: >-
  Generates 2D pixel game art (sprites, flipbook animation, tilesets, tilemaps)
  with Python and Pillow via scripts/sparkpix. Exports PNG, GIF, uniform-grid
  spritesheets, Spark SpriteAnimator manifests (.spark-atlas.json), and Tiled TSX
  tilesets for the Spark engine. Use when the user asks for pixel art, sprites,
  sprite sheets, 8-bit/16-bit retro art, tilesets, pixel animation, or assets
  for the Spark game engine (assets under spark/assets/sprites/).
---

# Spark-pix

You are the pixel artist. Author **regenerable** Python build scripts that draw
every pixel with `scripts/sparkpix` (Pillow only). No external art tools, no
diffusion models unless the user explicitly wants a cleanup pass from a photo.

**Dependency:** `pip install -e .` from repo root (or `pip install pillow`).

**CLI:** `python -m sparkpix validate|study|palette|manifest` — see README.

**Spark asset drop:** `assets/sprites/<pack>/` inside the user’s Spark repo.  
If Spark is a sibling directory: `../spark/assets/sprites/<pack>/`.  
See [references/paths-and-privacy.md](references/paths-and-privacy.md) — never hardcode `/Users/...` paths.

## Workflow

1. **Brief** — canvas size, palette budget, light direction, outline rule, animation
   list. Read [references/patterns.md](references/patterns.md) and
   [references/spark-export.md](references/spark-export.md).
   **Human / hero / warrior:** you **must** read [references/humanoid-hero.md](references/humanoid-hero.md)
   and use a **rig + filled limb blocks** (≥2 px wide). Do **not** default to the tiny
   slime example or 1px stick legs.
2. **Build script** — `pixel-art/<asset-name>/build.py` (source of truth).

   Humanoid heroes: 64×64, rig-driven `draw_*` with `rect`/`ellipse` masses, then
   `preview_idle.png` at 8× and fix silhouette before other clips.

   ```python
   # Minimal pattern — see pixel-art/vanguard_hero/build.py for full hero rig
   s = Sprite(64, 64, palette=...)
   draw_human_frame(s, rig_from_pose(pose))  # filled torso/legs, not line()-only limbs
   s.preview("preview_idle.png", scale=8)
   ```

3. **Run** — `cd pixel-art/<asset-name> && python3 build.py`
4. **Look** — open `preview.png` (and GIF/atlas previews). Critique with
   [references/validations.md](references/validations.md). Iterate 2–3 passes minimum.
5. **Validate** — `python3 scripts/validate.py pixel-art/<asset-name>/out`
6. **Deliver** — 1× PNG master, scaled preview, optional GIF, Spark atlas JSON.
   Copy final assets into Spark `assets/sprites/<your-pack>/` when requested.

Work at **true pixel size**; scale only on export (integer 4–10× for previews).

## API (scripts/sparkpix)

Import path: add `scripts/` to `sys.path`, then `from sparkpix import Sprite, ramp, PALETTES, TilesetBuilder`.
Shared colors: `from sparkpix.game_palette import GRASS, INK, SPARK_GAME, palette_for_sprite`.

| Area | Methods |
|------|---------|
| Canvas | `Sprite(w,h,palette=)` · `layer(name)` · `frame(i)` · `use(frame=, layer=)` |
| Draw | `px` `line` `rect` `circle` `ellipse` `polygon` `fill` `clear` `get` `paste_png` |
| Pixel ops | `outline(c, where="outside"/"inside")` · `mirror_x/y` · `replace` · `dither` |
| Animation | `add_frame(copy=)` · `set_duration(ms)` · `tag_clip(name, from, to, fps, loop)` |
| Inspect | `preview(path, scale, grid=)` · `used_colors()` · `stats()` |
| Export | `save_png` · `save_gif` · `save_spritesheet(path, columns, spark_json=True)` · `save_project` / `Sprite.load_project` |
| Tilemaps | `TilesetBuilder(tile_w, tile_h).add_tile(...).export_tiled(out_dir)` |
| Projectiles | Separate small `build.py` (e.g. 16×16 bolt); `bolt.spark-meta.json` pivot; see `pixel-art/robot_ranger/bullets/` |

Colors: `"#rrggbb"`, `(r,g,b[,a])`, palette index `int`, or `None` to erase.

**Masking:** most draw calls accept `only=` — `"opaque"`, `"empty"`, a color, or palette index.

## Spark integration

- **Animated characters:** uniform grid atlas + `.spark-atlas.json` for
  `SpriteAnimatorComponent::SetUniformGrid(columns, rows)` and
  `SpriteAnimationClip{firstFrame, frameCount, framesPerSecond, loop}`.
- **Static sprites:** single PNG; set `SpriteComponent` UV to full texture or one cell.
- **Tilemaps:** export TSX + PNG; import `.tmx` in Spark via `TilemapMapSourceComponent`.
  Use tile properties `spark_walkable`, `spark_collision`, `spark_blocks_pathfinding`.

Details: [references/spark-export.md](references/spark-export.md).

## Reference art study

When the user provides a PNG to match:

```bash
python3 scripts/study.py path/to/ref.png pixel-art/_study/ref_name
```

Read `preview_8x.png`, `swatch.png`, and `report.json`. Capture rules in
`references/learned/<name>.md` (create the folder if needed).

## Knowledge routing

| Task | Read |
|------|------|
| Sizes, silhouettes, tiles | [references/patterns.md](references/patterns.md) |
| **Humanoid hero proportions** | **[references/humanoid-hero.md](references/humanoid-hero.md)** |
| Shading, outlines, dither | [references/techniques.md](references/techniques.md) |
| Frame counts, timing | [references/animation.md](references/animation.md) |
| Palettes | [references/palettes.md](references/palettes.md) |
| Spark paths & manifests | [references/spark-export.md](references/spark-export.md) |
| Pre-ship checklist | [references/validations.md](references/validations.md) |
| Paths / privacy | [references/paths-and-privacy.md](references/paths-and-privacy.md) |

## Conventions

- Never hand-edit exported PNGs — change `build.py` and rerun.
- Keep color count intentional (typical 8–24 per asset).
- Name outputs clearly: `hero_walk.spark-atlas.json`, `dungeon_floor.tsx`.
- Deterministic output only (no unseeded randomness).
