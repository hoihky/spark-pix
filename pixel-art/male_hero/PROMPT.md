# Male platform fighter (scarf gi hero)

Production **128×128** side view (+X), matched to `pixel-art/_study/male_hero_ref` strips and design sheet.

## Design intent (v2)

| Element | Look | Knob |
|---------|------|------|
| Hair | Traced brown silhouette from design PNG | `FighterHeadLook(hair_style="ref_design")`, `PALETTE.hair` |
| Face | Compact skin + forward green eye + blush | `eye_style="forward"`; stamps use `P128.face` / `FACE_REL_DY` (not head joint Y) |
| Scarf | Traced tail idle/walk/run | `ref_male_hero_scarf.json`, `Rig.scarf_stamp_*`; else `draw_scarf_mass` |
| Outfit | White gi, blue trim, navy shorts, brown boots/gloves | `PlatformHeroKnobs(outfit="gi_shorts", shoe="gi_boot")` |
| Weapon | Scarf only (no blade) | `weapon="scarf"` |

Recolor by editing `PALETTE` in `build.py` only — hair stamps palette-swap via `draw_ref_male_hero_hair`.

## Skeleton & draw order

- Joints: `platform_style.P128` (anchored Q64). `head` = neck/rig joint; `face` = traced hair/face anchor (`face_anchor_from_head` each frame).
- **Back arm**: `platform_fighter.PlatformArmOffsets` + split `draw_arm_gi(..., part="upper"|"lower")` via shared `draw_platform_fighter_frame`.
- **Head**: `hair_back` → scarf knot + front arm → `face_front` (skin + bangs + eye on top).

## Clips

See `PLATFORM_CLIP_TABLE` in `scripts/sparkpix/hero_config.py` (idle/walk/run/jump/fall/dash/combo).

## Build

```bash
python3 scripts/scarf_keys_from_strips.py    # refresh scarf_keys.json from study strips
python3 scripts/extract_ref_male_hero_hair.py
python3 scripts/extract_ref_male_hero_face.py
PYTHONPATH=scripts python3 scripts/calibrate_p128_from_design.py  # landmarks JSON
PYTHONPATH=scripts python3 pixel-art/male_hero/build.py
PYTHONPATH=scripts python3 scripts/critique.py pixel-art/male_hero/out
python3 scripts/parity_male_hero.py
```

Outputs: `out/preview_idle.png` (8×), atlas `male_hero.spark-atlas.json`, `frame0_art.png`.
