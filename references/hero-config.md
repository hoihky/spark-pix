# Hero configuration knobs

Developers control shipped art **at the top of `pixel-art/<name>/build.py`** and in
**`PROMPT.md`**. Implementation lives in `scripts/sparkpix/hero_config.py` plus style
dispatchers (`platform_outfit`, `platform_weapon`, `jrpg_face`, `platform_face`).

## Quick map

| Outcome | What to change | Module |
|---------|----------------|--------|
| Hair **shape** | `JrpgHeadLook.hair_style` or `FighterHeadLook.hair_style` | `jrpg_face`, `platform_face`, `platform_ref_hair` |
| Hair **color** | `HAIR = ramp("#…", 5)` in `CharacterPalette.hair` | `build.py` |
| Face **layout** | `JrpgHeadLook` / `FighterHeadLook` (eye, beard, fringe, blush) | `jrpg_face`, `platform_face` |
| Eye **color** | `CharacterPalette.eye` (`pupil`, `iris`, `sclera`, `paper`) | `build.py` → head draw |
| Clothes **shape** | `JrpgHeroKnobs.outfit` / `PlatformHeroKnobs.outfit` | `platform_outfit` |
| Clothes **color** | `shirt`, `pants`, `trim`, `belt`, `glove` ramps | `CharacterPalette` |
| Shoe **shape** | `shoe` id (`q_boot`, `gi_boot`, `dress_slip`) — selects leg drawer | `jrpg_body`, `platform_body` |
| Shoe **color** | `boot` ramp | `CharacterPalette` |
| Weapon **type** | `weapon` id (`none`, `scarf`, `baton`, `stick`, `blade`) | `platform_weapon` |
| Weapon **color** | `weapon` ramp | `CharacterPalette` |
| **Animations** | `AnimationPlan.from_table(..., only=, disable=)` | `hero_config` → `tag_on_sprite` |

## Track choice

| Track | Canvas | Knob dataclass | Default clips |
|-------|--------|----------------|---------------|
| JRPG Q | 64×64 | `JrpgHeroKnobs` | `JRPG_CLIP_TABLE` |
| Platform fighter | 128×128 | `PlatformHeroKnobs` | `PLATFORM_CLIP_TABLE` |

See [platform-fighter.md](platform-fighter.md) for the full fighter clip list.

## Canonical reference packs

| Pack | Track | Highlights |
|------|-------|------------|
| **`pixel-art/ref_youth/`** | JRPG Q 64×64 | `platform_outfit.draw_jrpg_*`, 3 locomotion clips |
| **`pixel-art/male_hero/`** | Platform 128×128 | `scarf_keys.json`, layered head + scarf, `PLATFORM_CLIP_TABLE` |

Production prompts: each pack’s **`PROMPT.md`**. Template for new assets:
[prompt-example-production.md](prompt-example-production.md).

## `build.py` pattern

```python
from sparkpix.color import ramp
from sparkpix.hero_config import (
    AnimationPlan,
    CharacterPalette,
    EyeColors,
    PlatformHeroKnobs,
    PLATFORM_CLIP_TABLE,
    validate_knobs,
)
from sparkpix.jrpg_face import JrpgHeadLook  # JRPG track
from sparkpix.platform_face import FighterHeadLook
from sparkpix.platform_outfit import draw_platform_torso, draw_platform_leg, draw_platform_arm
from sparkpix.platform_weapon import draw_weapon
from sparkpix import rig

INK = "#141820"

PALETTE = CharacterPalette(
    hair=ramp("#3a2818", 5),
    skin=ramp("#f5c4b8", 3),
    shirt=ramp("#f0f0f0", 4),
    pants=ramp("#202830", 4),
    boot=ramp("#181c24", 3),
    trim=ramp("#c03030", 3),
    belt=ramp("#181c20", 3),
    glove=ramp("#303840", 3),
    scarf=ramp("#a24e57", 4),
    weapon=ramp("#a0a8b8", 4),
    ink=INK,
    eye=EyeColors(iris="#4080c0", blush="#ffc5b4"),
)

KNOBS = PlatformHeroKnobs(
    head=FighterHeadLook(hair_style="ref_design", show_blush=True),
    outfit="gi_shorts",
    shoe="gi_boot",
    weapon="scarf",
    animation=AnimationPlan.from_table(PLATFORM_CLIP_TABLE, disable={"dash"}),
)
validate_knobs(KNOBS)

def draw_weapon_layers(s, r):
    if KNOBS.weapon == "scarf":
        return  # scarf drawn via platform_scarf
    draw_weapon(s, r.hand, r.weapon_deg, PALETTE.weapon, KNOBS.weapon)
```

## Hair styles

### JRPG (`JrpgHeadLook.hair_style`)

`spiky`, `quiff`, `short`, `puffy`, `flowing` — see [jrpg-profile-face.md](jrpg-profile-face.md).

### Platform (`FighterHeadLook.hair_style`)

| Value | Behavior |
|-------|----------|
| `ref_design` | Stamp from design sheet; **palette-only** customization |
| `hero_spiky` | Procedural JRPG spiky hair @ q=0 |

Regenerate stamps: `python3 scripts/extract_ref_male_hero_hair.py`

## Outfit styles

### JRPG (`JRPG_OUTFIT_STYLES`)

`tunic`, `elder_cape`, `dress`, `long_coat`, `hoodie` → `platform_outfit.draw_jrpg_*`

### Platform (`PLATFORM_OUTFIT_STYLES`)

`gi_shorts`, `hoodie_shorts` → `draw_platform_*`

## Animations

Use a single atlas frame stream; tag clips after all frames are drawn:

```python
PLAN = KNOBS.animation
# ... add_frame / draw per clip ...
ranges = PLAN.tag_on_sprite(s)
```

`AnimationPlan.from_table(PLATFORM_CLIP_TABLE, only={"idle", "walk"})` ships a minimal set.
`disable={"dash", "combo_1"}` keeps table order but skips baking (implement by not drawing
disabled clips in your loop).

## PROMPT.md

Copy the **Character knobs** table from the [master template](platformer-character.md) into
each project prompt so art direction matches `build.py` constants.
