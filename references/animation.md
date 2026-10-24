# Animation

## Timing

| Action | Frames | FPS (loop) |
|--------|--------|------------|
| Idle breathe | 2–4 | 3–6 |
| Walk cycle | 4–8 | 8–12 |
| Run | 6–8 | 12–16 |
| Attack | 4–6 | 10–14, `loop=false` |

Use `set_duration(ms)` per frame for GIF; use `tag_clip(..., fps=)` for Spark clips.

## Puppeting

Build one `draw_character(pose: dict)` and call it per frame with offsets:

- `squash` on landing
- `leg_phase` 0..3 for walk
- `arm_swing` paired with legs

Use `add_frame(copy=True)` then modify only moving parts with `only=` masks.

## Pivot stability

Keep feet on the same bottom pixel row across walk frames. Center of mass should
not drift horizontally more than 1px per frame unless intentional.

## Export

```python
s.tag_clip("idle", 0, 0, fps=2, loop=True)
s.tag_clip("walk", 1, 4, fps=10, loop=True)
s.save_spritesheet("out/hero", columns=4)
```
