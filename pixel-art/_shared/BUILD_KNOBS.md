# Shared: character knob header

Copy into new `pixel-art/<name>/build.py` after `OUT` / `INK` definitions.
See **[references/hero-config.md](../../references/hero-config.md)** for allowed style ids.

```python
from sparkpix.color import ramp
from sparkpix.hero_config import (
    AnimationPlan,
    CharacterPalette,
    EyeColors,
    JrpgHeroKnobs,  # or PlatformHeroKnobs
    JRPG_CLIP_TABLE,  # or PLATFORM_CLIP_TABLE
    validate_knobs,
)
from sparkpix.jrpg_face import JrpgHeadLook  # JRPG
# from sparkpix.platform_face import FighterHeadLook  # 128 fighter

INK = "#141820"
HEAD_LOOK = JrpgHeadLook(hair_style="spiky", eye_style="vertical")
HAIR = ramp("#0c2840", 5)

PALETTE = CharacterPalette(
    hair=HAIR,
    skin=ramp("#f5c4b8", 3),
    shirt=ramp("#6a7848", 4),
    pants=ramp("#382820", 4),
    boot=ramp("#201810", 3),
    ink=INK,
    eye=EyeColors(),
)

KNOBS = JrpgHeroKnobs(head=HEAD_LOOK, outfit="tunic", shoe="q_boot", weapon="none")
validate_knobs(KNOBS)
```
