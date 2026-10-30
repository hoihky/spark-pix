# Vanguard hero (stoic swordsman)

**Production reference** — side-view RPG pixel art at shippable quality.  
Regenerate with `build.py` only — not traced from third-party art.

Follows [humanoid-hero.md](../../references/humanoid-hero.md) and [validations.md](../../references/validations.md).

## Clips

| Clip | Frames | FPS | Loop |
|------|--------|-----|------|
| **idle** | 4 | 4 | yes |
| walk | 6 | 10 | yes |
| run | 6 | 14 | yes |
| attack | 8 | 14 | no (sword arc smear) |
| jump | 4 | 10 | no |
| die | 6 | 8 | no |

Atlas: **64×64** cells, 10 columns × 4 rows (34 frames).

## Build

```bash
PYTHONPATH=scripts python3 pixel-art/vanguard_hero/build.py
python -m sparkpix validate pixel-art/vanguard_hero/out
```

Review `out/preview_idle.png` (8×) before treating other projects as done.
