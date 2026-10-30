# Animation

**Production standard:** Clips must loop cleanly in-engine at 1× with stable pivots.
See `SKILL.md` deliverable types and [validations.md](validations.md) before ship.

## Timing

| Action | Frames | FPS (loop) |
|--------|--------|------------|
| Idle breathe | 2–4 | 3–6 |
| Walk cycle | 4–8 | 8–12 |
| Run | 6–8 | 12–16 |
| Attack | 4–8 | 10–14, `loop=false` |
| Hit / hurt | 2–4 | 10–12, `loop=false` |
| Die | 4–8 | 6–10, `loop=false` |

Use `set_duration(ms)` per frame for GIF; use `tag_clip(..., fps=)` for Spark clips.
Document the clip table in the `build.py` module docstring for engineers.

## Puppeting

Build one `draw_character(pose: dict)` (or rig struct) and call it per frame with offsets:

- `squash` on landing
- `leg_phase` 0..3 for walk
- `arm_swing` paired with legs

Use `add_frame(copy=True)` then modify only moving parts with `only=` masks.
Do not repaint unrelated pixels frame-by-frame without a pose function — that does not scale to production edits.

## Pivot stability

Keep feet on the same bottom pixel row across walk frames. Center of mass should
not drift horizontally more than 1 px per frame unless intentional (dash, knockback).

For side-view +X characters, align the **baseline row** across idle, walk, run, and combat.

## Export

```python
s.tag_clip("idle", 0, 3, fps=4, loop=True)   # frames 0..3 inclusive
s.tag_clip("walk", 4, 9, fps=10, loop=True)  # 6 frames
s.save_spritesheet("out/hero", columns=4, spark_json=True)
```

After export, run `python -m sparkpix validate out/` and verify clip `firstFrame + frameCount` ≤ total frames.

## Reference

Production multi-clip heroes: `pixel-art/vanguard_hero/build.py`, `pixel-art/robot_ranger/build.py`.
