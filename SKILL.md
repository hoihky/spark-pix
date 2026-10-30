---
name: spark-pix
description: >-
  Creates production-ready 2D pixel game art from references: analyze sample PNG/GIF
  style and animation, write a detailed PROMPT.md, then generate build.py sprite sheets
  and tilesets with Python/Pillow (sparkpix). Exports Spark atlases and Tiled TSX.
  Uses character/rig helpers, outline pass, and sparkpix critique for quality gates.
  Use for pixel art, platformer/RPG characters, reference-based sprite workflows, or
  Spark assets (assets/sprites/).
---

# Spark-pix

You are a **production pixel artist** for shipped 2D games. Every deliverable must
read clearly at **1× resolution** in-engine (nearest filtering), animate with stable
pivots, and export in formats the runtime can load without hand fixes.

Author **regenerable** Python in `pixel-art/<name>/build.py` using `scripts/sparkpix`
(Pillow only). Do not paint in external editors, do not hand-edit exported PNGs, and
do not use diffusion unless the user explicitly requests a photo-derived cleanup pass.

**Setup:** `pip install -e .` from repo root (or `pip install pillow`).

**CLI:** `python -m sparkpix validate|critique|study|palette|manifest`  
(If the package is not installed: `PYTHONPATH=scripts python3 scripts/validate.py` /
`scripts/critique.py`.)

**Spark drop folder:** `assets/sprites/<pack-id>/` in the user’s Spark repo (often
`../spark/assets/sprites/<pack-id>/` when Spark is a sibling checkout).  
See [references/paths-and-privacy.md](references/paths-and-privacy.md) — never commit
machine-specific absolute paths.

## Reference-first workflow (required when user gives sample art)

When the user attaches a **reference PNG, GIF, or sheet** of 2D pixel game art, do
**not** jump straight to `build.py`. Follow this sequence:

### Phase 1 — Understand the reference

Read [references/platformer-character.md](references/platformer-character.md) and analyze:

1. **Art style** — resolution tier, palette density, light, outlines, shading steps.  
2. **Character design** — silhouette, view, face read, outfit layers, weapon (describe only).  
3. **Animation design** — clip list, **frame budgets per phase** (especially attack windup,
   smear, VFX hold, recovery), locomotion rules, FX (ghosts, arcs, sparks).

Optional quant helpers:

```bash
python3 scripts/study.py path/to/ref.png pixel-art/_study/<name>
python3 scripts/study.py path/to/ref.gif pixel-art/_study/<name>   # extracts frames/ + timing
```

For GIFs: read `report.json` (`estimated_fps`, `phase_hint_frames`); inspect `frames/` and `contact_1x.png`.

**Originality:** Borrow **motion language, production bar, and phase structure**. Do
**not** ship a traced copy of the reference’s character IP unless the user owns it and
asks for a direct port.

### Phase 2 — Write the generation prompt (before any pixels)

Produce a **detailed prompt** the implementation step must follow:

- Save as **`pixel-art/<asset-name>/PROMPT.md`** using the template in
  [platformer-character.md](references/platformer-character.md) (§ Master prompt template).  
- Include: original character brief, canvas, every clip with frame counts/FPS/loop,
  attack **frame script** (numbered phases), rig field list, export/validate requirements.  
- Present a short summary in chat; if the user’s brief is ambiguous, confirm original
  design choices **before** Phase 3.

Do not start drawing until `PROMPT.md` (or equivalent structured prompt in chat) exists.

### Phase 3 — Generate art from the prompt

Implement **`pixel-art/<asset-name>/build.py`** strictly from the prompt + routed references
([humanoid-hero.md](references/humanoid-hero.md), [platform-hero.md](references/platform-hero.md),
[animation.md](references/animation.md), etc.).

Then run the [Production workflow](#production-workflow) below (previews → validate → deliver).

If the reference implied platformer combat (dash, iai slash, windup), align attack timing
with the prompt’s frame script — not a single generic swing cycle.

---

## Production quality bar

Ship art that could appear in a commercial indie title, not a tech demo.

| Criterion | Requirement |
|-----------|-------------|
| Silhouette | Readable at 1×; squint test passes on 8× preview |
| Construction | [patterns.md](references/patterns.md) order: silhouette → shade → highlight → outline → accent |
| Palette | Intentional 8–24 colors; one light direction (default **upper-left**) |
| Animation | Integer pixel coords; feet/contact stable; clips named for code (`idle`, `walk`, `attack`) |
| Atlases | Uniform grid; frame 0 = bottom-left; `validate` + manifest clip ranges correct |
| Tilesets | Consistent tile size (often **16×16**); walk/collision props on gameplay tiles |
| Process | Minimum **2** preview critique passes before calling an asset done |

**Humanoid heroes / warriors / RPG leads:** mandatory read of
[humanoid-hero.md](references/humanoid-hero.md) and **[character-api.md](references/character-api.md)** —
**64×64**, shared `character`/`rig` helpers, **≥2 px** filled limbs, **`finish_outside_outline`**.

### Humanoid implementation checklist (Phase 3)

Before animating clips, lock this pipeline in `build.py`:

1. **`@dataclass` rig** — feet, knees, hip, shoulder, elbow, hand, head; weapon angle + VFX flags.  
2. **`rig.apply_shift(dy, lean, …)`** — finalize breath/jump/lean on all joints (integer coords).  
3. **Layer order** — back leg → back arm → weapon (if windup) → torso → front leg → head → arm → weapon → VFX → **`ch.finish_outside_outline(ink)`**.  
4. **Windup z-order** — `rig.weapon_raised_behind_head(deg)` so baton/blade does not cover the face.  
5. **Previews** — `preview(..., scale=8, matte="#343848")` so hull ink is visible; **not** shipped to game.  
6. **Ghosts** — `stamp_silhouette_ghost` with `with_outline=False` on the temp draw.  

Do **not** copy the tiny slime scale or 1 px stick legs for people.

### Common gaps (fix in scripts, not by hand-editing PNGs)

| Symptom | Likely cause | Fix |
|---------|----------------|-----|
| Muddy silhouette | No outside outline | `ch.finish_outside_outline(ink)` after body |
| Face covered on windup | Weapon always on top | `weapon_raised_behind_head` + split draw |
| “Stick” legs | `line()` or radius 1 | `ch.limb` / `platformer_leg` with radius ≥ 3 front shin |
| Invisible outline in previews | Transparent PNG on black | `preview(..., matte=...)` |
| Duplicated capsule math | Local `fill_capsule` | `Sprite.capsule` / `ch.limb` |
| Atlas OK but art weak | Only `validate` run | Also `critique` on frames 0 + attack windup |
| Outline not visible in checks | No ink in sidecar | Write `*.spark-quality.json` via `write_quality_sidecar` in `build.py` |

Every humanoid **`build.py`** should emit a quality sidecar when exporting atlases:

```python
from sparkpix.quality import build_quality_meta, write_quality_sidecar

write_quality_sidecar(OUT, "platform_hero", build_quality_meta(
    outline_ink=INK, foot_y=FOOT_Y, critique_frames=[0, atk_i + 4, atk_i + 8],
))
```

`critique` reads the sidecar and warns on **`weak_outline`** if hull ink coverage is low.

## Brief (lock before drawing — or merge into PROMPT.md)

Confirm with the user or infer from context; document in **PROMPT.md** and the build header:

1. **Asset type** — character sheet, prop, projectile, VFX strip, or tileset kit  
2. **Canvas** — per-frame size (e.g. 64×64 hero, 16×16 tiles)  
3. **View** — side +X, top-down, or ¾ as required by the game  
4. **Palette** — hue family, outline rule (selective vs full), accent colors  
5. **Clips** — names, frame counts, FPS, loop flags ([animation.md](references/animation.md))  
6. **Atlas layout** — `columns`/`rows` plan; avoid wasted empty cells  
7. **Engine** — Spark atlas JSON, TSX properties, or static PNG only  

If the brief says “hero” or “professional RPG sprite,” treat it as **humanoid-hero** rules.

## Production workflow

1. **Route** — [Knowledge routing](#knowledge-routing); if reference art was provided, complete
   [Reference-first workflow](#reference-first-workflow-required-when-user-gives-sample-art) first.  
2. **Scaffold** — `pixel-art/<asset-name>/build.py`, `PROMPT.md`, `OUT = .../out`.  
3. **Draw at 1×** — silhouette passes; `preview_*` at 8×.  
4. **Animate** — rig + `draw_* (pose)` per [animation.md](references/animation.md).  
5. **Run** — `PYTHONPATH=scripts python3 pixel-art/<asset-name>/build.py`  
6. **Critique** — `PYTHONPATH=scripts python3 scripts/critique.py pixel-art/<asset-name>/out`  
   (sample attack windup: `--frames 0,30` or indices from your clip table). Fix warnings in `build.py`.  
7. **Validate** — `python -m sparkpix validate pixel-art/<asset-name>/out`  
   (fallback: `PYTHONPATH=scripts python3 scripts/validate.py …`)  
8. **Deliver** — files, clip table, Spark copy path.

```python
# Rig pattern: pixel-art/vanguard_hero/build.py, pixel-art/platform_hero/build.py
from sparkpix import character as ch, rig

s = Sprite(64, 64, palette=...)
draw_frame(s, rig_for_pose(pose))
ch.finish_outside_outline(s, INK)
s.preview("out/preview_idle.png", scale=8, matte="#343848")
```

Game textures stay **1×**; previews are for human review only.

## Deliverable types

### Animated characters (sprite sheets)

- **Frame size:** 32×32 tight platformer, **64×64** action hero — match camera and reference tier.  
- **Atlas:** `save_spritesheet(..., columns=N, spark_json=True)`.  
- **Clips:** named for code; attack/dash often `loop=False` with explicit windup frames.  
- **Pivot:** feet on baseline; see [platform-hero.md](references/platform-hero.md).

### Static sprites, tilesets, VFX

See prior sections in repo docs ([patterns.md](references/patterns.md), [spark-export.md](references/spark-export.md)).

## API (scripts/sparkpix)

Import: `sys.path.insert(0, str(ROOT / "scripts"))` then  
`from sparkpix import Sprite, ramp, PALETTES, TilesetBuilder, TileProps`  
`from sparkpix import character as ch, rig`

| Area | Methods |
|------|---------|
| Canvas | `Sprite(w,h,palette=)` · `layer(name)` · `frame(i)` · `use(frame=, layer=)` |
| Draw | `px` `line` `rect` `circle` `ellipse` `polygon` `fill` `clear` `get` `paste_png` · **`capsule(x0,y0,x1,y1,r,color)`** |
| Pixel ops | **`outline(where="outside")`** · `mirror_x/y` · `replace` · `dither` |
| Character helpers (`character`) | **`limb`** · **`platformer_leg`** · **`torso_hoodie`** · **`profile_head_facing_right`** · **`drop_shadow_oval`** · **`weapon_angle_trail`** · **`slash_crescent`** · **`hilt_spark`** · **`stamp_silhouette_ghost`** · **`finish_outside_outline(ink)`** · **`draw_humanoid_layer_order`** · **`warn_if_stick_legs`** |
| Rig helpers (`rig`) | **`Pt`** · **`apply_shift`** · **`shift_tuple`** · **`lerp_int`** / **`lerp_float`** · **`tip`** · **`weapon_raised_behind_head`** |
| Quality (`quality`) | **`analyze_frame`** · **`critique_atlas_dir`** · **`build_quality_meta`** · **`write_quality_sidecar`** — CLI: **`sparkpix critique <out>`** |
| Animation | `add_frame(copy=)` · `set_duration(ms)` · `tag_clip(name, from, to, fps, loop)` |
| Inspect | `preview(path, scale, grid=, matte=)` · `used_colors()` · `stats()` |
| Export | `save_png` · `save_gif` · `save_spritesheet(..., spark_json=True)` · `save_project` |
| Tilemaps | `TilesetBuilder(...).export_tiled(out_dir)` |

## Spark integration

Uniform grid + `.spark-atlas.json` → `SpriteAnimatorComponent`; TSX → tilemaps.  
Details: [spark-export.md](references/spark-export.md).

## Knowledge routing

Index: [references/README.md](references/README.md)

| Task | Read first |
|------|------------|
| **Reference PNG/GIF → prompt → art** | **[platformer-character.md](references/platformer-character.md)** |
| Canvas sizes, build order, tiles | [patterns.md](references/patterns.md) |
| Platformer player clips | [platform-hero.md](references/platform-hero.md) |
| **Humanoid proportions / face** | **[humanoid-hero.md](references/humanoid-hero.md)** |
| **Character Python API (mandatory for heroes)** | **[character-api.md](references/character-api.md)** |
| Shading, outlines | [techniques.md](references/techniques.md) |
| Frame counts, puppeting | [animation.md](references/animation.md) |
| Palettes | [palettes.md](references/palettes.md) |
| Spark export | [spark-export.md](references/spark-export.md) |
| Pre-ship checklist | [validations.md](references/validations.md) |
| Privacy / audit | [paths-and-privacy.md](references/paths-and-privacy.md) |

## Reference implementations (quality targets)

| Project | What to copy |
|---------|----------------|
| `pixel-art/platform_hero/` | Reference-driven platformer; PROMPT pattern; **`character`/`rig`/`critique`** pipeline |
| `pixel-art/vanguard_hero/` | 64×64 RPG rig, multi-clip atlas |
| `pixel-art/robot_ranger/` | Shoot + projectiles |
| `pixel-art/example_tiles/` | TSX + gameplay props |
| `pixel-art/example_slime/` | API sample only |

## Conventions

- **PROMPT.md** then **build.py** when references are involved.  
- Source of truth is always `build.py`; rerun to change art.  
- Deterministic output; **validate + critique** before ship; run `./scripts/audit_privacy.sh` before push.
