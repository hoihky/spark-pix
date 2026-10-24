# Vanguard hero (stoic swordsman)

Side-view RPG pixel style: silver hair, olive tunic, brown kit, gold/blue greatsword hilt.  
Regenerate with `build.py` — not traced from third-party art.

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
