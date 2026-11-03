# JRPG “Q” / cute hero proportions

**Use when** the brief asks for **Q-style** chibi heroes, cartoon JRPG leads, or cute side-view characters.

## Canvas

Same **64×64** cell as standard heroes; feet on **`FOOT_Y = 61`**.

## Body (~2.5–3 heads tall)

| Region | Q share | Notes |
|--------|---------|--------|
| Head + hair | **~32–38%** | `profile_head_facing_right(..., cute=True)` + `JrpgHeadLook` |
| Torso | **~18–22%** | Shorter hoodie/tunic block (`torso_hoodie(..., cute=True)`) |
| Legs | **~28–32%** | Stubby; knees near row **54** |

Shared skeleton defaults: **`sparkpix.q_style.Q64`** — import in every Q hero `build.py`.

## API

```python
from sparkpix.q_style import Q64, FOOT_Y, KNEE_Y, MIN_HEIGHT_FILL
from sparkpix.jrpg_face import JrpgHeadLook

HEAD_LOOK = JrpgHeadLook(hair_style="spiky", eye_style="vertical", forehead="bandana")

ch.profile_head_facing_right(..., look=HEAD_LOOK, cute=True)
ch.torso_hoodie(..., cute=True, width_half=7)
```

Quality sidecar: `min_height_fill=MIN_HEIGHT_FILL` (0.76).

## vs standard hero

See [humanoid-hero.md](humanoid-hero.md) for **~5 heads tall** realistic proportions. Do not mix defaults in one atlas without relabeling the art direction.
