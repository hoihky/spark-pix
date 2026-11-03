# Reference elder (beard + cape)

Side +X match for the **silver puffy hair / bushy beard / gold cape** reference screenshot.

| Knob | Value |
|------|--------|
| `HEAD_LOOK` | `puffy`, `hero`, `beard=True`, `fringe_over_eye=True` |
| `HAIR` | silver ramp (hair + beard) |
| `CAPE` | gold shoulder cape |
| Body | `draw_q_elder_cape_torso` + `draw_q_chest_bridge` |

```bash
PYTHONPATH=scripts python3 pixel-art/ref_elder/build.py
```
