# Art generation prompt: ref_youth (production example)

Canonical **64×64 JRPG Q** pack using `hero_config` — copy this structure for new heroes.

---

## Source

- Reference: in-repo **youth hero** screenshot (cyan spiky hair, olive tunic, vertical eye).
- Originality: **Borrow** Q proportions, vertical eye read, and 3-clip locomotion timing. **Do not** trace third-party IP.

---

## Style

- Canvas: **64×64**, side view **+X**
- Palette budget: **≤24** opaque RGB; light from **upper-left**
- Outline: **selective** hull ink `#101420` via `finish_production_humanoid`
- Quality bar: `SKILL.md`, `validations.md`, `critique` on frame 0

---

## Character knobs (`build.py` mapping)

| Category | Prompt value | `build.py` constant |
|----------|--------------|---------------------|
| Track | JRPG Q | `JrpgHeroKnobs` (implicit `track="jrpg_q"`) |
| Hair style | spiky + fringe over eye | `HEAD_LOOK.hair_style="spiky"`, `fringe_over_eye=True` |
| Hair color | deep cyan-blue | `PALETTE.hair = ramp("#0c2840", 5)` |
| Eye style | 2×3 vertical strip | `HEAD_LOOK.eye_style="vertical"` |
| Eye colors | blue iris, white sclera | `EyeColors(pupil="#0a1018", iris="#2878a8", sclera="#ffffff")` |
| Face extras | no beard, no forehead band | `forehead="none"`, `beard=False` |
| Clothes style | short tunic + fists | `KNOBS.outfit="tunic"` → `draw_jrpg_torso` / `draw_jrpg_arm` |
| Clothes colors | olive shirt, brown pants | `PALETTE.shirt`, `PALETTE.pants` ramps |
| Shoe style | Q stub boot block | `KNOBS.shoe="q_boot"` |
| Shoe color | warm brown | `PALETTE.boot = ramp("#503828", 3)` |
| Weapon | unarmed | `KNOBS.weapon="none"` |
| Animations | idle / walk / run only | `AnimationPlan` below |

---

## Original character brief

- **Silhouette:** Compact Q hero; large spiky hair mass; readable fist and boot blocks.
- **Face:** Youth skin ramp; **no mouth**; vertical eye with bang shadow on top row.
- **Outfit:** Olive tunic with chest bridge under jaw; brown shorts/pants line at waist; sleeve fists.
- **Weapon:** None — empty hands.

---

## Clips

| Clip | Frames | FPS | Loop | Motion notes |
|------|--------|-----|------|----------------|
| idle | 4 | 4 | yes | ±1 px breath; subtle hand sway |
| walk | 8 | 10 | yes | Opposing feet; knees flex; feet on `FOOT_Y` |
| run | 6 | 14 | yes | Lean +2; lower squash; larger stride |

Disable clips: `AnimationPlan.from_table(..., disable={"run"})` or omit from custom tuple.

---

## Rig parameters

- Skeleton: `Q64` via `sparkpix.q_style` (`FOOT_Y`, `KNEE_Y`)
- Fields: `dy`, `lean`, `squash`, full leg/arm/head chain
- Always `finalize()` → `rig.apply_shift` before draw
- Layer order: shadow → back leg → back arm → torso → bridge → front leg → head → front arm → outline

---

## Export

- Out dir: `pixel-art/ref_youth/out/`
- Atlas: `ref_youth.png` + Spark JSON, **columns=10**
- Previews: `preview_idle.png` (8×, matte `#343848`), `preview_sheet.png` (4× grid)
- Quality sidecar: `ref_youth.spark-quality.json` with `outline_ink`, `foot_y`, `critique_frames=[0]`

```bash
PYTHONPATH=scripts python3 pixel-art/ref_youth/build.py
PYTHONPATH=scripts python3 scripts/critique.py pixel-art/ref_youth/out
python -m sparkpix validate pixel-art/ref_youth/out
```

---

## Anti-patterns

- Hand-editing exported PNGs
- Stick legs (radius &lt; 2)
- Skipping `validate_knobs(KNOBS)` at import
- Scattering hex colors outside `PALETTE` / `HEAD_LOOK`
