# Layout patterns

**Production standard:** Art must read at **1×** in-engine and match the bar in `SKILL.md`
(silhouette, palette budget, stable animation pivots, Spark-ready export). This doc covers
sizes and construction order.

## Canvas sizes (characters)

| Style | Size | Notes |
|-------|------|-------|
| Icon / pickup | 8–16 | 1–2 colors of detail |
| **Humanoid hero (side RPG)** | **64×64** | See **[humanoid-hero.md](humanoid-hero.md)** — default for warriors |
| Platformer | 32×32 | Readable at 720p |
| Chibi (only if asked) | 16×16 or 24×24 | Big head — **not** default for “hero” |
| Tall NPC | 32×48 | Feet on bottom row |
| Enemy / boss | 48×48 – 64×64 | Match hero scale for combat readability |

## Order of construction

Apply on every frame and tile before calling an asset done:

1. Silhouette (darkest ramp step or flat fill).
2. Local shading (shifted duplicate shapes with `only="opaque"`).
3. Highlights (smallest shapes last).
4. Outline (usually outside; skip on lit edge for selective outline).
5. Accents (eyes, weapon glint).

Squint-test the silhouette at 1×; if it fails, do not proceed to animation or atlas export.

## Tiles (production terrain kits)

- **Tile size:** lock one size per kit ( **16×16** is the Spark demo default).
- **Kit minimum:** ground fill, straight edges, inner/outer corners, optional transition to a second biome.
- **Props:** crates, rocks, signs as separate tile indices — not stretched ground tiles.
- **Gameplay:** every walkable/solid tile gets correct `TileProps` at export ([spark-export.md](spark-export.md)).
- **Visual:** same light direction and palette ramp as characters in the same game pack.
- Leave 0–1 px inner highlight on top surfaces for readability at 1×.

## Animation layout

Pack frames left-to-right in the atlas; **row 0 is the bottom row** in Spark’s UV math.
When planning a sheet, lay out in code in linear order 0..N-1 matching that grid.
Plan `columns` so the grid has minimal empty cells; run `validate` before ship.

## Atlas planning

- One uniform **frame width × height** per character sheet.
- Name clips for code: `idle`, `walk`, `run`, `attack`, `hit`, `die` — avoid `anim1`.
- Keep feet on a consistent baseline row across locomotion clips ([animation.md](animation.md)).
