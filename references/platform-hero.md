# Platformer player character

**Production standard:** Same rig rules as [humanoid-hero.md](humanoid-hero.md), usually **64×64** for a lead with combat + dash clips (not 48×48 unless the game camera is very tight).

## Canvas & pivot

- Feet on **`height − 2`** row; locomotion clips stay on that baseline ±1 px.
- Facing **+X**; one visible eye; filled limbs **≥2 px** (prefer **3 px** on front leg).
- Apply **`dy` / `lean` to the whole skeleton** (`finalize()` pattern in `platform_hero/build.py`) — do not only move the head for jump/idle.

## Clips (typical platformer set)

| Clip | Notes |
|------|--------|
| idle | 4 frames, ±1 px breath, weapon sway ≤2° |
| walk | **8** frames, clear knee lift, alternating contact |
| run | 6 frames, +lean, larger stride |
| jump | 6 frames: squash → takeoff → apex (feet off ground) → fall → land squash |
| dash | 6–8 frames: crouch → burst with **ghosts behind** + wisps → brake → recover |
| attack | **11** frames: ready → crouch/hilt → **spark** → snap smear → **lingering arc** → recover, `loop=false` |

## Reference implementation

`pixel-art/platform_hero/build.py` — validate before ship:

```bash
PYTHONPATH=scripts python3 pixel-art/platform_hero/build.py
PYTHONPATH=scripts python3 scripts/validate.py pixel-art/platform_hero/out
```

Previews: `preview_idle.png`, `preview_walk.png`, `preview_dash.png`, `preview_attack.png` at 8×.

## Anti-patterns

- 48×48 canvas with RPG-level detail (silhouette collapses at 1×).
- Dash that only slides pixels without anticipation/recovery or contact with baseline on exit.
- Jump that never lifts feet off `FOOT_Y` on apex frames.
- Stick legs or baton drawn as a single `line()`.
