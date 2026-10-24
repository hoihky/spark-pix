# Shared art constants

Import from build scripts after adding the repo `scripts/` directory to `sys.path`:

```python
from sparkpix.game_palette import GRASS, INK, SPARK_GAME, palette_for_sprite
# or
from game_palette import GRASS, INK  # if cwd is pixel-art/_shared
```

Export palette JSON for reference:

```bash
python -m sparkpix palette export pixel-art/_shared/spark_game.palette.json
```
