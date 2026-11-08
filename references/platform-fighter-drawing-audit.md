# Platform fighter drawing audit (male_hero)

**Status:** Working notes for incremental fixes in `scripts/sparkpix/` and `pixel-art/male_hero/`.  
**Last reviewed:** 2026-11-08 (preview idle vs `pixel-art/_study/male_hero_ref/design/source_1x.png`).

## Executive summary

The character reads “ugly” mainly because the pipeline is **hybrid**: **traced hair** (pixel-perfect) sits on **procedural** face, gi torso, capsules, and scarf polygons (approximate). Those layers use **different head anchors** and **fragile draw order** fixed with build-local offsets. Foot placement and palette overlap are mostly fine; **silhouette and face/arm layering** are not.

Improve incrementally by (1) one coordinate system, (2) canonical draw API in scripts, (3) optional stamp layers like hair, (4) stronger parity tests per region.

---

## Root causes

### 1. Hybrid render model

| Region | Implementation | Module / data |
|--------|------------------|---------------|
| Hair | Traced stamps | `ref_male_hero_hair.json`, `platform_ref_hair.py` |
| Face | JRPG compact skin + manual `rect` patches | `platform_face.py`, `jrpg_face._draw_face_skin_compact` |
| Torso / shorts / boots | Ellipses + shaded capsules | `platform_body.py`, `render.limb_shaded` |
| Arms | Flat capsules (`character.limb`) | `platform_body.draw_arm_gi` |
| Scarf | Keyed tip + filled polygons | `platform_scarf.py`, `scarf_keys.json` |
| Finish | Selective hull ink | `render.finish_production_selective`, `build.py` `OUTLINE_BUCKETS` |

Reference art is hand-placed pixels; only hair matches the design sheet exactly. Everything else is a stylized primitive stack, so small rig errors become visible “glitches” (gray shirt on cheek, pink scarf through profile, floating glove).

### 2. Two head coordinate systems

- Skeleton joint: `P128.head` ≈ **(62, 41)** — `platform_style.py` (Q64 head + `ANCHOR_X/Y` + `HEAD_Y_ADJ`).
- Design facial landmark (hair extract anchor): **(62, 54)** — `extract_ref_male_hero_hair.py`, eye row ~55 on design sheet.
- Bridge constant: **`REF_DESIGN_FACE_Y_ADJ = 13`** in `platform_ref_hair.py` — hair stamps and face blocks share `cy + 13`.

Measured (design vs current skeleton): foot row **79** matches `FOOT_Y`; eye **~55** vs `head[1]+13` → **~54** (≈1px). **Shoulder (64, 56)** vs shirt mass centroid **~y 65** — gi art sits lower than the shoulder joint, forcing arm offsets in `build.py`.

Face patches in `ref_design` (`platform_face._draw_face_base`) add opaque `rect`s for cheeks/chin so skin wins over shirt/scarf after z-order fights — readable but blocky.

### 3. Limb and layering mismatch

- **Legs:** `render.limb_shaded` (toned).
- **Arms:** `character.limb` (flat, thin back radius `r=1`).

Back arm historically used **`r - 1` → 0** for forearm until fixed with `max(1, r - 1)` in `platform_body.draw_arm_gi`. Torso ellipses are **fully opaque**; a full back arm drawn before the gi **hides the forearm**. Mitigation today: **`part="upper"`** before torso, **`part="lower"`** after front leg (`male_hero/build.py`). That logic belongs in a shared module, not only in one pack.

Front arm + `draw_chest_bridge` use shirt mid-tone **`#a0acc5`**. If face is drawn before arms, shirt pixels cover the eye/cheek zone — mitigated by drawing **`face_front` after** front arm/scarf knot.

### 4. Draw order not centralized

Documented order lives in `references/platform-fighter.md` (updated for split arms/head). **`hero_config` / `platform_outfit`** do not expose:

- Split back arm passes.
- Split head (`hair_back` → body → `face_front`).
- Scarf `face_y_adj` on `draw_scarf_mass`.

`draw_platform_arm` exists but does not replace custom `_back_arm_pts` / `_front_arm_pts` in `build.py`. Pack files are easy to corrupt when merging patches (duplicate `draw_frame_content` / stale `SHIRT` symbols).

### 5. Scarf as geometry vs pixels

`draw_scarf_mass` builds **polygons** from neck + `tip_world_x` / `tip_dy`. Even with `jaw_floor = head_y + face_y_adj + 9`, the tail rarely matches reference pixel art; it reads as a large magenta wedge when tip/attach are slightly wrong. Hair extraction must **`MAX_Y=70`** because scarf/boot reuse browns from the hair ramp.

### 6. Outline pass

`finish_selective_humanoid` maps fill colors to per-material ink (`OUTLINE_BUCKETS`). Overlapping bucket membership (hair + skin, scarf + blush) can outline **wrong hull edges** on noisy procedural shapes. Outline count is similar ref vs gen (~30 ink pixels) — outline is secondary to shape/layer bugs.

---

## Known bugs and footguns

| ID | Issue | Location | Symptom / risk |
|----|--------|-----------|----------------|
| B1 | Back forearm radius 0 when `back=True`, `compact=True` | `platform_body.draw_arm_gi` (fixed: `max(1, fr)`) | Missing back forearm |
| B2 | Neck bridge wide rect over face (older) | `platform_body.draw_neck_bridge` (fixed: narrow columns) | Shirt-colored plate over eyes |
| B3 | `glove_or_shirt()` passed into `draw_shorts_leg` | `platform_outfit.draw_platform_leg` | Confusing API; unused glove on legs |
| B4 | Hair stamp color collision | `extract_ref_male_hero_hair.py` | False hair pixels without `MAX_Y` / scarf palette discipline |
| B5 | `foot_drift` in critique | `quality.py`, walk/run rigs | Bottom bbox 83..89; contact not pinned to `FOOT_Y` |
| B6 | Weak parity gate | `parity_male_hero.py` | Passes on bbox + palette overlap only; face/arm can be wrong |
| B7 | Hair layer split subtlety | `platform_ref_hair.py` | `hair_back` = `dy>9`; crown/fringe need correct pass order |

---

## What is *not* the main problem

- Global foot row vs design (`foot_delta_y` ≤ 3 in parity).
- Traced hair stamp count (**132/132**) when anchor `(62, 54)` and extract are current.
- `rig.apply_shift` with `neck=` — consistent lean/dy on joints.

---

## Incremental improvement plan

Work in small PR-sized steps. After each phase, run:

```bash
python3 scripts/extract_ref_male_hero_hair.py   # when design hair changes
PYTHONPATH=scripts python3 pixel-art/male_hero/build.py
python3 scripts/parity_male_hero.py
PYTHONPATH=scripts python3 scripts/critique.py pixel-art/male_hero/out
```

Check **`out/preview_idle.png`** (8×) and **`out/parity_ref_vs_gen.png`**.

### Phase A — Stabilize API (scripts only, minimal visual change)

- [ ] **A1** Add `platform_fighter.py` (or extend `platform_outfit`) with `draw_platform_fighter_frame(s, r, palette, knobs)` implementing the canonical layer order from `platform-fighter.md`.
- [ ] **A2** Move `_back_arm_pts` / `_front_arm_pts` into `hero_config.PlatformArmOffsets` or `platform_body` constants derived from `P128`, documented in one place.
- [ ] **A3** Thin `male_hero/build.py` to rigs + palette + call shared draw; no duplicate `draw_frame_content` paths.
- [ ] **A4** Extend `parity_male_hero.py` (or new `parity_male_hero_regions.py`) with ROI checks: eye hex, back-glove bbox, face skin count (design vs gen).

**Done when:** One draw function; build.py &lt; ~400 lines; parity fails if eye or back-hand bbox drifts.

### Phase B — Skeleton and face anchor (reduce magic numbers)

- [ ] **B1** Script `scripts/calibrate_p128_from_design.py` → JSON landmarks (foot, eye, shoulder, back hand, neck) from design sheet.
- [ ] **B2** Set `P128.head` to joint row *or* rename `head` vs `face_anchor` so `REF_DESIGN_FACE_Y_ADJ` can shrink toward 0.
- [ ] **B3** Replace ad-hoc face `rect`s in `ref_design` with either tuned compact mask **or** start face stamp table (see Phase C).

**Done when:** `REF_DESIGN_FACE_Y_ADJ` ≤ 1 or documented as deprecated; shoulder Y within ~2px of shirt attach on idle.

### Phase C — Stamp layers (reference fidelity, palette-swappable)

- [ ] **C1** `extract_ref_male_hero_face.py` + `draw_ref_male_hero_face` (skin ramps only).
- [ ] **C2** Optional torso/scarf stamps for idle frame 0 first, then keyed frames for scarf.
- [ ] **C3** Keep procedural legs/arms for animation until rig stamps exist per clip.

**Done when:** Idle face/skin ROI matches design counts within tolerance; hair still 132/132.

### Phase D — Procedural polish (if staying procedural)

- [ ] **D1** Use `limb_shaded` in `draw_arm_gi` (match legs).
- [ ] **D2** Tune `draw_torso_gi` shoulder trim to align mass with `P128.shoulder` + 2..4px.
- [ ] **D3** Scarf: bilinear sample / stamp from ref strip cells using existing `scarf_keys.json` frame index.
- [ ] **D4** Walk/run: pin `foot_f[1]` / `foot_b[1]` to `FOOT_Y` on contact frames (fix `foot_drift`).

**Done when:** critique has no `foot_drift`; walk strip contact row stable.

### Phase E — Finish and palette

- [ ] **E1** Split `OUTLINE_BUCKETS` so skin, hair, shirt, scarf do not share inks incorrectly.
- [ ] **E2** Optional: skip selective outline on head ROI when using full stamps.

---

## File map (touch during improvements)

| File | Role |
|------|------|
| `scripts/sparkpix/platform_style.py` | `P128`, `FOOT_Y`, anchors |
| `scripts/sparkpix/platform_face.py` | `FighterHeadLook`, ref vs JRPG head |
| `scripts/sparkpix/platform_ref_hair.py` | Hair stamps, `REF_DESIGN_FACE_Y_ADJ` |
| `scripts/sparkpix/platform_body.py` | Gi, arms (`ArmPass`), neck |
| `scripts/sparkpix/platform_scarf.py` | Scarf mass |
| `scripts/sparkpix/platform_outfit.py` | Style dispatch (incomplete for fighter order) |
| `scripts/sparkpix/hero_config.py` | Knobs, clip table |
| `scripts/sparkpix/render.py` | Outline, `limb_shaded` |
| `scripts/extract_ref_male_hero_hair.py` | Regenerate hair JSON |
| `scripts/parity_male_hero.py` | Coarse parity |
| `pixel-art/male_hero/build.py` | Rigs, exports, offsets (should shrink) |

---

## References

- Study art: `pixel-art/_study/male_hero_ref/`
- Production pack: `pixel-art/male_hero/`, `PROMPT.md`
- Track overview: [platform-fighter.md](platform-fighter.md)
- Knobs: [hero-config.md](hero-config.md)

---

## Changelog

| Date | Note |
|------|------|
| 2026-11-08 | Initial audit after hair/face/arm/scarf layering fixes; documents hybrid root cause and phased plan |
