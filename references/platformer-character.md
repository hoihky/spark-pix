# Platformer character from reference GIF / image

Use this doc when the user supplies **sample 2D pixel game art** (PNG, GIF, sheet) as a
**style and motion reference**. Extract **production language** (timing, VFX, rig rules);
**do not trace** copyrighted character designs into shipped assets unless the user owns the art.

Template for the agent-written prompt: [§ Master prompt template](#master-prompt-template).

---

## Reference analysis checklist

When viewing a reference still or GIF, record:

### Art style

| Signal | Notes to capture |
|--------|------------------|
| Resolution tier | e.g. 32×32, 48×48, **64×64**, 48×64 tall |
| Palette | Approx. color count; saturated vs muted; accent colors |
| Light | Direction (default upper-left); highlight placement |
| Outline | Full black rim vs **selective** same-hue outline |
| Shading | Flat vs 3–4 step ramps per material |
| Filter | Always **1× nearest** in-engine |

### Character design (describe factually — do not copy verbatim into ship art)

| Signal | Notes to capture |
|--------|------------------|
| Silhouette | Chibi vs heroic; weapon shape; hair mass |
| View | Side +X, top-down, ¾ |
| Face | Eye size/color; horn/hat/hair; profile vs front |
| Outfit layers | Torso, sleeves, belt, boots — separate blocks |
| Weapon | Sheathed vs drawn; length; VFX color on strike |
| Proportions | Head % height; leg length; combat stance width |

### Animation design

| Signal | Notes to capture |
|--------|------------------|
| Clips present | idle, walk, run, jump, dash, attack, hit, die, … |
| **Attack phases** | ready → **windup** (frames) → **snap** (frames) → **VFX hold** → recovery |
| Windup | Crouch depth; hand on hilt; charge spark/glint |
| Speed FX | Afterimage ghosts; motion lines; smear on weapon |
| Slash VFX | Crescent arc; color (white/cyan); frames held after body stops |
| Locomotion | Walk frame count; foot on baseline; knee bend |
| Timing feel | FPS estimate; which phases get the most frames |

### Environment (if visible)

- Background simplicity; **tilemap** bevel, edge highlights, gameplay tile size.

---

## What a hi-bit platformer combat GIF typically encodes

Example pattern (many action platformers / katana dash clips):

1. **Combat idle** — low stance, weight forward, weapon ready.
2. **Windup** — several frames: crouch, grip weapon, optional **hilt spark**.
3. **Burst** — dash or lunge; **solid silhouette afterimages** behind motion.
4. **Strike** — 1–2 frames of blade motion + **multi-angle smear**.
5. **Impact** — **large crescent slash** lingering 2–3 frames.
6. **Recovery** — wide landing, return to idle.

Your **original** hero should reuse **phase structure and frame budget**, not the
reference’s exact horns, hair color, kimono, or katana unless the user explicitly wants that IP.

---

## Phase 3 — Implement `build.py`

Route to [humanoid-hero.md](humanoid-hero.md) and implement using
**[character-api.md](character-api.md)** (layer order, outline, windup z-order, previews with `matte=`).

After export:

```bash
PYTHONPATH=scripts python3 scripts/critique.py pixel-art/<name>/out --frames 0,<attack_windup_index>
```

---

## Study tooling

For user-supplied PNG (single frame or sheet still) **or GIF**:

```bash
python3 scripts/study.py path/to/ref.png pixel-art/_study/<name>
python3 scripts/study.py path/to/ref.gif pixel-art/_study/<name>
```

PNG: `preview_8x.png`, `swatch.png`, `report.json`.  
GIF: adds `frames/frame_NNN.png`, `contact_1x.png`, `estimated_fps`, `phase_hint_frames` in `report.json`.

Optional persistent notes: `references/learned/<project>.md`.

---

## Master prompt template

**Step A — Agent fills this from reference analysis + user brief.**  
**Step B — Agent implements `pixel-art/<name>/build.py` from this prompt only.**  
Save the filled prompt as `pixel-art/<name>/PROMPT.md` (or show in chat).

```markdown
# Art generation prompt: <asset-name>

## Source
- Reference: <user description / filename — motion & quality only>
- Originality: <list what is NEW vs what is borrowed from reference timing/VFX>

## Style
- Canvas: <W×H per frame>
- View: side +X (or …)
- Palette budget: <N colors>; light from upper-left; selective outline
- Quality bar: SKILL.md + validations.md

## Original character (do not clone reference silhouette)
- Body: …
- Face: human 3/4 profile — sclera, iris, nose, chin, neck
- Outfit: …
- Weapon: …

## Clips
| Clip | Frames | FPS | Loop | Notes |
|------|--------|-----|------|-------|
| idle | | | | |
| walk | | | | |
| run | | | | |
| jump | | | | |
| dash | | | | ghosts / wisps |
| attack | | | | windup → snap → arc hold → recover |

### Attack frame script (required for combat refs)
1. …
2. …

## Rig parameters
- FOOT_Y, baseline rule, rig fields (hip, knees, feet, weapon_angle, trails, hilt_spark, slash_arc, ghost_offsets)

## Export
- Atlas columns; Spark clip names; validate before ship

## Anti-patterns
- Tracing reference pixels; stick limbs; skipping windup; hand-editing PNGs
```

---

## Short one-liner (chat)

> Analyze reference GIF for **style, character design, and animation phases**; write
> `pixel-art/<name>/PROMPT.md` using references/platformer-character.md; then implement
> **original** 64×64 rig + build.py from that prompt only; match reference **timing/VFX**,
> not reference **character IP**.

---

## Related docs

- [platform-hero.md](platform-hero.md) — platformer clip rules and rig patterns  
- [humanoid-hero.md](humanoid-hero.md) — proportions and face/limb bar  
- [animation.md](animation.md) — FPS and puppeting  
- Example implementation: `pixel-art/platform_hero/build.py`
