# Character & rig API (`scripts/sparkpix`)

Use these helpers in **`build.py`** so humanoid art stays on the production bar in
[humanoid-hero.md](humanoid-hero.md) and [validations.md](validations.md). Do **not**
copy-paste `fill_capsule` into every project.

Import pattern:

```python
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from sparkpix import Sprite, ramp
from sparkpix import character as ch
from sparkpix import rig
from sparkpix import render as rd
```

## Draw order (side view +X)

| Step | Layer | Notes |
|------|--------|--------|
| 1 | Ground shadow | `ch.drop_shadow_oval` — before body |
| 2 | Dash ghosts / wisps | Behind body |
| 3 | Back leg | `ch.platformer_leg(..., back=True)` |
| 4 | Back arm | `ch.limb(..., radius=2)` |
| 5 | Weapon (windup) | When `rig.weapon_raised_behind_head(deg)` |
| 6 | Torso | `ch.torso_hoodie` or custom blocks |
| 7 | Front leg | `ch.platformer_leg(..., back=False)` — **radius ≥ 3** on shin |
| 8 | Head | `ch.profile_head_facing_right` or `ch.mech_head_facing_right` |
| 9 | Front arm + weapon | Weapon in front when not windup |
| 10 | Slash / sparks | After body |
| 11 | Hull outline | **`ch.finish_production_humanoid(ink)`** — **not** on ghost stamps |

Optional orchestrator: `ch.draw_humanoid_layer_order(...)` with callables for each step.

## `character` module

| Function | Purpose |
|----------|---------|
| `limb(s, p0, p1, radius, color)` | Filled limb capsule (≥2 px) |
| `platformer_leg(...)` | Thigh + shin + boot block |
| `torso_hoodie(...)` | Hoodie + shirt + shorts waist |
| `profile_head_facing_right(...)` | Wrapper → `jrpg_face.draw_jrpg_profile_head`; pass **`look=JrpgHeadLook(...)`** |
| `JrpgHeadLook` | `scripts/sparkpix/jrpg_face.py` — hair/eye/forehead/beard knobs |
| `jrpg_body` | `draw_q_tunic_torso`, `draw_q_long_coat_torso`, `draw_q_leg`, arm helpers, **`draw_q_chest_bridge`** |
| `mech_head_facing_right(...)` | Robot helmet + vertical visor eye (no mouth); **`cute=True`** for Q dome |
| `drop_shadow_oval(...)` | Foot-centered oval shadow |
| `weapon_angle_trail(...)` | Multi-angle smear |
| `slash_crescent(...)` | Held slash arc VFX |
| `hilt_spark(...)` | Windup glint pixels |
| `stamp_silhouette_ghost(...)` | Dash afterimage (draw fn without outline) |
| `finish_outside_outline(s, ink)` | Outline only |
| **`finish_production_humanoid(s, ink)`** | **Speck trim + outline (ship pass)** |
| `warn_if_stick_legs(s, foot_y, frame=0)` | Print WARN if legs too thin |

## `render` module

| Function | Purpose |
|----------|---------|
| **`limb_shaded(s, p0, p1, r, ramp)`** | 3-step ramp limb + upper-left highlights |
| **`finish_production_pass(s, ink)`** | Trim specks + outline |
| `matte_composite(img)` | Gray matte for preview PNGs |

## `rig` module

| Function | Purpose |
|----------|---------|
| `Pt` | Integer skeleton point |
| `apply_shift(dy, lean, foot_f, …)` | Apply breath / jump / lean to all joints |
| `shift_tuple(pt, dx, dy=0)` | Offset one point |
| `lerp_int` / `lerp_float` | Pose blending |
| `tip(x, y, deg, length)` | **0°=+X**, **90°=down (+Y)**, **negative°=tip above hand** (overhead windup) |
| `weapon_raised_behind_head(deg)` | Draw weapon behind head when **deg &lt; -38** (overhead) or **deg &gt; 78** |

## `quality` module

Run after export (or from `build.py`):

```bash
PYTHONPATH=scripts python3 scripts/critique.py pixel-art/<name>/out
# or: python -m sparkpix critique pixel-art/<name>/out --frames 0,12,30
```

Requires **`*.spark-quality.json`** (from `write_quality_sidecar`) for outline ink checks.

| Check | Meaning |
|-------|---------|
| `stick_legs` | 1 px leg columns in lower body |
| `short_silhouette` | Character uses &lt; ~82% canvas height |
| `orphan_pixels` | Isolated single-pixel specks |
| `palette` | Opaque RGB count over budget |
| `foot_drift` | Bottom silhouette row jumps between sampled frames |
| **`weak_outline`** | Hull ink coverage below `minOutlineCoverage` (needs sidecar `outlineInk`) |

Use `--strict` to fail CI on warnings.

## Quality sidecar (`*.spark-quality.json`)

Written next to the atlas by `build.py`:

```python
write_quality_sidecar(OUT, "platform_hero", build_quality_meta(
    outline_ink="#141820",
    foot_y=61,
    critique_frames=[0, 28, 32],
    min_outline_coverage=0.45,
))
```

## Previews

Game textures stay **1× transparent**. For human review:

```python
MATTE = "#343848"  # so dark ink outline is visible
s.preview(OUT / "preview_idle.png", scale=8, matte=MATTE)
```

## Anti-patterns

- Local `fill_capsule` instead of `Sprite.capsule` / `ch.limb`
- Skipping **`finish_production_humanoid`** on humanoids
- Drawing weapon always on top of head during windup
- Previews on black with no `matte=` (hides outline quality)
- Validating atlas only — run **`critique`** before calling art done

Reference implementation: `pixel-art/platform_hero/build.py`.
