# JRPG profile face (hair + eye)

Side view **+X**, **no mouth**. Q heroes: jaw overlaps **`draw_q_chest_bridge`** (not a neck tube).

## Reference characters

| Project | Ref image | `HEAD_LOOK` |
|---------|-----------|-------------|
| `pixel-art/ref_youth/` | Cyan spiky youth | `spiky`, `vertical`, fringe |
| `pixel-art/ref_elder/` | Silver beard elder | `puffy`, `hero`, `beard=True` |

## Tune in `build.py`

| Knob | Examples |
|------|----------|
| `hair_style` | `spiky`, `puffy`, `quiff`, `short` |
| `eye_style` | `vertical` (2×3 dark \| white), `hero` (dark tick) |
| `beard` | `True` — uses `_draw_beard_bushy` |
| `fringe_over_eye` | Top row hair shadow on vertical eye |

Implementation: `scripts/sparkpix/jrpg_face.py` via `character.profile_head_facing_right`.
