# Shared art constants

**Production standard:** One palette module per game pack so characters, tiles, and props match at 1×.

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

See [references/palettes.md](../references/palettes.md), [character-api.md](../references/character-api.md), and [validations.md](../references/validations.md).
