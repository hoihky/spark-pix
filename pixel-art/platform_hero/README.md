# Platform hero ("Skip")

**Production platformer reference** — **64×64** cells, humanoid-hero proportions, side +X.

Spec: [`PROMPT.md`](PROMPT.md) (reference → prompt → `build.py`).

Original design: bandana, teal hoodie, shorts, hook baton (not third-party art).

## Clips

| Clip | Frames | FPS | Loop |
|------|--------|-----|------|
| idle | 4 | 4 | yes |
| walk | 8 | 10 | yes |
| run | 6 | 14 | yes |
| jump | 6 | 12 | no |
| dash | 7 | 18 | no |
| attack | 11 | 12 | no |

Atlas: **64×64**, 10 columns (43 frames).

## Build

```bash
PYTHONPATH=scripts python3 pixel-art/platform_hero/build.py
PYTHONPATH=scripts python3 scripts/validate.py pixel-art/platform_hero/out
```

Review `out/preview_idle.png`, `preview_walk.png`, `preview_dash.png`, `preview_attack.png` at 8× before ship.

## Spark

Copy `out/platform_hero.png` + `platform_hero.spark-atlas.json` to
`../spark/assets/sprites/platform_hero/`.
