# Spark engine integration

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
python3 pixel-art/example_slime/build.py
cp pixel-art/example_slime/out/slime.png pixel-art/example_slime/out/slime.spark-atlas.json \
   /path/to/spark/assets/sprites/spark_pix/
```

Bundled copies: `assets/for-spark/` in this repo.

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
