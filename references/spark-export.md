# Spark engine export

Target engine: **Spark** (open-source game engine). Asset root: `assets/sprites/<pack-id>/` in that repo.

## Sprite animation (uniform grid)

`SpriteAnimatorComponent` expects a **uniform grid** atlas:

- Frame **0** = bottom-left cell.
- Frames increase along **+X**, then **+Y** (row-major).
- `ComputeUniformGridUv(columns, rows, linearFrame, atlasWidth, atlasHeight)` sets `SpriteComponent` UV.

### Files to ship

| File | Purpose |
|------|---------|
| `name.png` | Atlas at 1× pixel size (RGBA) |
| `name.spark-atlas.json` | Grid metadata + clip definitions |
| `name@6x.png` | Optional preview (nearest upscale) |

### Manifest fields (`spark-sprite-atlas-v1`)

```json
{
  "format": "spark-sprite-atlas-v1",
  "texture": "hero.png",
  "columns": 4,
  "rows": 2,
  "frameWidth": 32,
  "frameHeight": 32,
  "nearestFilter": true,
  "clips": [
    {
      "name": "idle",
      "firstFrame": 0,
      "frameCount": 1,
      "framesPerSecond": 1.0,
      "loop": true
    }
  ]
}
```

### C++ wiring (manual today)

1. Load PNG into `Texture2D`; call `SetSceneUploadNearest(true)` for crisp pixels.
2. `SpriteAnimatorComponent::SetUniformGrid(columns, rows)`.
3. For each clip in JSON: `AddClip(SpriteAnimationClip{firstFrame, frameCount, fps, loop})`.
4. Pair with `SpriteComponent` on the same `GameObject`.

Place textures under:

`spark/assets/sprites/<pack-id>/`

Register in game code with `GameWorld::RegisterTexture` (see `Platformer2DDemo.cpp`).

## Tilemaps (Tiled)

Export with `TilesetBuilder.export_tiled(out_dir)`:

- `tileset.png` — combined tiles (fixed `tilewidth` × `tileheight`)
- `tileset.tsx` — Tiled 1.8 tileset XML

Spark reads **TMX** via `TilemapMapSourceComponent` / `TmxImporter`.

### Recommended tile properties

| Property | Values | Effect |
|----------|--------|--------|
| `spark_walkable` | `true` / `false` | Gameplay grid walkability |
| `spark_collision` | `full`, etc. | `TilemapCollider2D` baking |
| `spark_blocks_pathfinding` | `true` / `false` | A* grid |

Optional tileset property: `spark_tileset_gameplay` — string id for gameplay kits.

Kenney sample: `assets/sprites/kenney_tiny-dungeon/Tiled/sampleSheet.tsx`.

## Non-uniform atlases

For arbitrary rectangles (UI icons, variable props), export a **TexturePacker-style XML**
is not built into spark-pix yet — prefer uniform grids for animation, or single PNG +
manual `SpriteComponent::SetUvRect` per sprite.

## Validation

```bash
python3 scripts/validate.py path/to/out
```

Checks PNG dimensions against manifest grid math and clip bounds.
