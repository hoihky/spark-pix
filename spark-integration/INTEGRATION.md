# Spark engine integration

**Production standard:** Deploy only **validated** 1× atlases and tilesets into Spark.
Regenerate from `build.py` when art changes — do not patch PNGs in `assets/sprites/`.

C++ sources live in the Spark repo (not duplicated here):

| File | Role |
|------|------|
| `include/spark/demo/SparkPixAtlasLoad.hpp` | Parse `*.spark-atlas.json`, load PNG, apply clips |
| `src/spark/demo/SparkPixAtlasLoad.cpp` | Implementation |
| `include/spark/demo/SparkPixShowcase2DDemo.hpp` | Minimal 2D demo |
| `src/spark/demo/SparkPixShowcase2DDemo.cpp` | Loads `/sprites/spark_pix/slime.spark-atlas.json` |

## Assets

After building art in spark-pix:

```bash
PYTHONPATH=scripts python3 pixel-art/example_slime/build.py
python -m sparkpix validate pixel-art/example_slime/out

# Spark as sibling checkout "spark"
cp pixel-art/example_slime/out/slime.png pixel-art/example_slime/out/slime.spark-atlas.json \
   ../spark/assets/sprites/spark_pix/
```

Production packs (hero, mech, tiles): same pattern with `pixel-art/<pack>/out/` →
`../spark/assets/sprites/<pack>/`. See [references/paths-and-privacy.md](../references/paths-and-privacy.md).

Bundled samples: `assets/for-spark/` in this repo (regenerate from examples when updating).

## Run the demo

Build Spark, launch **SparkDemo**, menu **30 — Spark-pix atlas** (hotkey **Z**).

- **Space** — cycle animation clips from the manifest
- **Scroll** — zoom ortho camera

## Use the loader in your game

```cpp
#include "spark/demo/SparkPixAtlasLoad.hpp"

SparkPixAtlasManifest manifest{};
Utf8String manifestPath{};
if (TryLoadSparkPixAtlasManifest("/sprites/spark_pix/slime.spark-atlas.json", manifest, manifestPath)) {
    Texture2D tex{Utf8String("MyAtlas")};
    if (TryLoadSparkPixAtlasTexture(manifest, manifestPath, tex)) {
        tex.SetSceneUploadNearest(true);
        auto texPtr = MakeShared<Texture2D>(MoveTemp(tex));
        world.RegisterTexture(texPtr, "game/my_atlas");
        // ... SpriteComponent + SpriteAnimatorComponent ...
        auto* anim = object->AddComponent<SpriteAnimatorComponent>();
        ApplySparkPixManifestToAnimator(manifest, *anim);
    }
}
```

Move `SparkPixAtlasLoad.*` from `spark/demo/` to a production module (e.g. `spark/scene/assets/`) when you ship a game.

## Pre-ship checklist

- [ ] `python -m sparkpix validate` passed on the pack copied to Spark
- [ ] `SetSceneUploadNearest(true)` on pixel art textures
- [ ] Clip names in C++ match manifest (`idle`, `walk`, …)
- [ ] Tilemaps: TMX references TSX exported from spark-pix with gameplay properties set
