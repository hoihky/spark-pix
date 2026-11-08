# Platform fighter track (128×128)

Production target: **male scarf fighter** reference strips (`male_hero-idle/walk/run/jump/fall/combo`) —
**128×128** canvas, **+X** view, ~**3.5 heads** tall, **~21-color** intentional palette.

## Dual track (pick one per asset)

| Track | Canvas | Face module | Body module | Example |
|-------|--------|-------------|-------------|---------|
| **JRPG Q** | 64×64 | `jrpg_face` / `JrpgHeadLook` | `jrpg_body` | `ref_youth`, `rose_hero` |
| **Platform fighter** | 128×128 | `platform_face` / `FighterHeadLook` | `platform_body`, `platform_scarf`, `platform_vfx` | `male_hero` |

Do not mix scales in one `build.py`.

## Skeleton (`platform_style.P128`)

- **`P128` = anchored `Q64`** — design sheet feet on row **~79** (`ANCHOR_X=34`, `ANCHOR_Y=18`), not full-frame `FOOT_Y=124`.
- Locomotion clips stay on that baseline ±1 px on walk/run.
- Default joints: `foot_f`, `foot_b`, `knee_*`, `hip`, `shoulder`, `elbow`, `hand`, `neck`, `head`.
- Rig fields beyond JRPG: **`scarf_phase`** (0–1 loop), **`slash`**, **`spark`**, **`dash_ghost`**.

`rig.apply_shift(dy, lean, …, neck=)` must run in **`finalize()`** before draw.

## Clip table (reference parity)

| Clip | Frames | FPS | Loop |
|------|--------|-----|------|
| idle | 10 | 8 | yes |
| walk | 10 | 10 | yes |
| run | 10 | 14 | yes |
| jump | 6 | 12 | no |
| fall | 4 | 12 | no |
| fall_loop | 3 | 10 | yes |
| dash | 8 | 14 | no |
| combo_1 | 3 | 14 | no |
| combo_1_end | 4 | 14 | no |

Add `combo_2` / `combo_3` when reference strips are provided.

## Draw order (128 fighter)

1. Dash ghost — `ch.stamp_silhouette_ghost` (**no** outline inside `draw_fn`).
2. Ground shadow — `ch.drop_shadow_oval`.
3. Back leg, back scarf, **back arm upper** (shirt sleeve behind gi).
4. Gi torso + chest bridge, front leg, **back arm lower** (forearm + glove).
5. Neck bridge, head `hair_back`, front scarf knot, front arm.
6. Head `face_front` (skin + traced bangs + eye **on top** of arm/scarf).
7. Slash / spark (`platform_vfx`).
8. **`ch.finish_selective_humanoid(OUTLINE_BUCKETS)`**.

## Face read (fighter)

- **Forward** eye (~4×3 sclera) + optional blush `#ffc5b4`.
- Spiky brown hair; **no mouth** at 1× ([face-read.md](face-read.md)).
- Preview **idle frame 0** at **8×** before animating walk/run.

## Quality gates

```bash
PYTHONPATH=scripts python3 pixel-art/male_hero/build.py
PYTHONPATH=scripts python3 scripts/critique.py pixel-art/male_hero/out
PYTHONPATH=scripts python3 scripts/validate.py pixel-art/male_hero/out
```

Compare `preview_idle.png` (8×) to reference idle strip. **`frame0_art.png`** is upright art space
(Spark atlases flip Y on export — use art frame for parity, not `male_hero.png` cell 0).

```bash
python3 scripts/parity_male_hero.py
```

Target: `foot_delta_y` ≤ 3, `overlap_hex` ≥ 8 vs design study.

### Scarf keys (idle / walk / run)

```bash
python3 scripts/scarf_keys_from_strips.py
python3 scripts/scarf_tip_parity.py   # after build — tip X vs ref, target max err ≤ 2px
```

Writes `pixel-art/male_hero/scarf_keys.json` with per-frame **`tip_x` / `tip_dy`** for
**idle, walk, run, jump, fall, fall_loop, combo_1, combo_1_end**.
Locomotion clips use strip `dy`; combat clips keep procedural body `dy` and key only the scarf.

## Drawing quality audit

Root-cause analysis and **incremental fix checklist** (Phases A–E):  
**[platform-fighter-drawing-audit.md](platform-fighter-drawing-audit.md)**

## Development plan (phases)

1. **Scripts + docs** — `platform_*` modules, this file, drawing audit, `SKILL.md` routing. **(current)**
2. **`male_hero` MVP** — all clips export; shared `draw_platform_fighter_frame` (audit Phase A).
3. **Parity pass** — regional parity (eye, back hand, face ROI); tune scarf keys; skeleton calibration (audit Phases B–D).
4. **Spark ship** — copy `out/` atlas + JSON to game assets when requested.
5. **Extra combos** — frame scripts from new reference PNGs only.

Reference implementation: **`pixel-art/male_hero/build.py`** + **`PROMPT.md`**.
