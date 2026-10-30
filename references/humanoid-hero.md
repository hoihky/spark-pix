# Humanoid hero (side-view RPG)

**Production standard:** Default for **hero**, **warrior**, **adventurer**, or “professional RPG sprite” briefs.
Must pass [validations.md](validations.md) before atlas export. Not for chibi/icons unless requested.

Use this whenever the user asks for a **hero**, **warrior**, **adventurer**, or art matching modern pixel RPG reference (not chibi, not icons).

## Canvas

| Use | Size |
|-----|------|
| Hero with greatsword | **64×64** (or 48×64 tall) |
| Enemy / NPC | 48×48 |

Character should occupy **85–92% of canvas height** with feet on **row height−2**.

## Proportions (mandatory)

Side view facing **+X** (right). Target **~4.5–5 heads tall**.

| Region | Share of body height | Rules |
|--------|----------------------|--------|
| Head + hair | ≤ 22% | Hair volume sideways/back, not a tall “hat” stack |
| Torso + belt | ~28% | Chest wider than head; 10–14 px wide on 64px canvas |
| Legs | ~45% | **Thigh and shin each ≥ 2 px wide**; visible knee bend |
| Arms | reach mid-thigh | Upper arm + forearm **≥ 2 px thick** |

**Never** draw legs or arms as a single-pixel-wide `line()` only — use `rect` / filled `ellipse` masses, or **`character.limb(..., radius=2–3)`** (wraps `Sprite.capsule`).

After all body parts are drawn on the frame, call **`character.finish_outside_outline(ink)`** for a readable hull (see `pixel-art/platform_hero/build.py`).

## Silhouette workflow

1. Draw **filled** legs + torso + head as separate blocks (darkest ramp first).
2. `save_silhouette` or preview at 8× — must read as a **person**, not a pole or emoji.
3. If legs are taller than torso+head combined, or limbs are 1px wide, **stop and fix** before animating.

## Style (modern RPG pixel)

- Earthy limited palette (12–24 colors); selective outline (darker **same-hue**, not black rim everywhere).
- Light from **upper left**; highlight on hair top and weapon edge.
- Greatsword: blade **2 px** wide, tip highlight, gold guard, small blue gem OK.
- One visible eye (3/4 face); green/teal accent is fine.

## Animation

- **Idle**: 3–4 frames, ±1 px vertical breath only; weapon sway ≤ 2°.
- **Walk/run**: feet stay on baseline ±1 px; knees bend (shin/thigh **blocks** rotate via offset, not spaghetti lines).
- **Attack**: 6–8 frames; arc smear uses semi-transparent pixels along prior blade angles.
- Parametrize with a **rig** (`hip`, `knee`, `foot`, `shoulder`, `hand`, `sword_angle`) — do not hardcode unrelated pixels per frame.

## Anti-patterns (reject before ship)

- Chibi giant head unless user asked for chibi.
- Stick-figure legs (1 px × 20 px).
- Floating disjoint blocks (head stack separated from neck).
- Neon palette on a “realistic” brief.
- Skipping preview loop (minimum **2** critique passes on `preview_idle.png`).

Reference implementation: `pixel-art/vanguard_hero/build.py`.
