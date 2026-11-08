# Production prompt example (copy for new heroes)

Use this as a **filled** `pixel-art/<asset-name>/PROMPT.md` before writing `build.py`.
The reference implementation that matches this doc: **`pixel-art/ref_youth/`** (JRPG Q).

For **128×128 platform fighters**, swap track row and clip table per [platform-fighter.md](platform-fighter.md).

---

```markdown
# Art generation prompt: forest_scout

## Source

- Reference: user GIF — side-view platformer locomotion timing only (walk 8f, run 6f feel).
- Originality: New scout IP — green cloak, copper dagger, auburn messy hair; borrow **phase structure**, not silhouette pixels.

## Style

- Canvas: 64×64, side +X
- Palette budget: 18 colors max; upper-left light; selective outline ink `#141820`
- Quality: SKILL.md + validations.md + critique frame 0 + attack windup if combat clips exist

## Character knobs (must match build.py)

| Category | Value | build.py |
|----------|-------|----------|
| Track | JRPG Q | `JrpgHeroKnobs` |
| Hair style | short | `JrpgHeadLook(hair_style="short", …)` |
| Hair color | auburn | `PALETTE.hair = ramp("#502818", 5)` |
| Eye style | vertical | `eye_style="vertical"` |
| Eye colors | hazel iris | `EyeColors(iris="#887040", …)` |
| Clothes style | tunic | `outfit="tunic"` |
| Clothes colors | forest green / tan pants | `shirt`, `pants` ramps |
| Shoes | q_boot | `shoe="q_boot"`, `boot` ramp |
| Weapon | none (scout fists) | `weapon="none"` |
| Animations | idle, walk, run | `AnimationPlan((ClipSpec(...), …))` |

## Original character brief

- Silhouette: Q scout; short hair; small backpack read optional in PROMPT only (implement in torso if scoped).
- Face: vertical eye, fringe optional, no mouth.
- Outfit: Green short tunic, tan leggings, brown boots.
- Weapon: None for v1 — add `weapon="blade"` only if attack clip is in scope.

## Clips

| Clip | Frames | FPS | Loop | Notes |
|------|--------|-----|------|-------|
| idle | 4 | 4 | yes | breath |
| walk | 8 | 10 | yes | stable FOOT_Y |
| run | 6 | 14 | yes | lean + squash |

## Rig

- Q64 skeleton; `finalize()` before every draw
- Draw order per character-api.md

## Export

- `pixel-art/forest_scout/out/` — PNG atlas + `.spark-atlas.json`
- Spark deploy path: `assets/sprites/spark_pix/forest_scout/` (document in README)

## Anti-patterns

- No traced reference pixels; no hand-edited PNGs; knobs only at top of build.py
```

---

## Phase 3 checklist for the agent

1. Create `pixel-art/forest_scout/PROMPT.md` from the block above (edited).
2. Scaffold `build.py` from [pixel-art/_shared/BUILD_KNOBS.md](../pixel-art/_shared/BUILD_KNOBS.md) + `ref_youth/build.py`.
3. Set `PALETTE`, `KNOBS`, `validate_knobs(KNOBS)`.
4. Implement `rigs_for_clip` / pose functions per clip table.
5. Run build → critique → validate → ship.
