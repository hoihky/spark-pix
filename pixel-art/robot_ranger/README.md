# Robot ranger + bullets

**Production reference** — mech hero with combat clip and separate projectile art.

## Build

```bash
# From spark-pix repository root
PYTHONPATH=scripts python3 pixel-art/robot_ranger/build.py
PYTHONPATH=scripts python3 pixel-art/robot_ranger/bullets/build.py
python -m sparkpix validate pixel-art/robot_ranger/out
```

## Character clips

| Clip | Frames | Loop |
|------|--------|------|
| idle | 4 | yes |
| walk | 6 | yes |
| run | 6 | yes |
| **shoot** | 6 | no |
| die | 6 | no |

Atlas: `out/robot_ranger.png` + `robot_ranger.spark-atlas.json` (64×64 cells, 8 columns).

## Bullets

| File | Use |
|------|-----|
| `bullets/out/bolt.png` | Single 16×16 bolt — spawn as `SpriteComponent` projectile |
| `bullets/out/bolt.spark-meta.json` | Suggested pivot (rear of trail) |
| `bullets/out/bolt_anim.png` + `.spark-atlas.json` | Optional 3-frame loop |

## Spark (sketch)

1. Copy validated assets to `../spark/assets/sprites/robot_ranger/` (or your Spark `assets/sprites/robot_ranger/`).
2. Player: `SpriteAnimatorComponent` + manifest; switch to **shoot** clip on fire input; spawn bullet at muzzle world position.
3. Bullet: load `bolt.png`, `SetSceneUploadNearest(true)`, velocity along +X; despawn off-screen.

Muzzle approx. (local to 64×64 cell, facing right): **(50, 30)** — tune from `preview_shoot.png`.

See [spark-export.md](../../references/spark-export.md) and [INTEGRATION.md](../../spark-integration/INTEGRATION.md).
