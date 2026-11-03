# Reference youth (blue spiky hero)

Side +X match for the **cyan spiky hair / olive tunic** reference screenshot.

| Knob | Value |
|------|--------|
| `HEAD_LOOK` | `spiky`, `vertical`, `forehead=none`, `fringe_over_eye=True` |
| `HAIR` | `ramp("#0c2840", 5)` |
| `TUNIC` / `PANTS` | olive / brown |
| Body | `draw_q_tunic_torso` + `draw_q_chest_bridge` |

```bash
PYTHONPATH=scripts python3 pixel-art/ref_youth/build.py
```
