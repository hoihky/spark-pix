# Layout patterns

## Canvas sizes (characters)

| Style | Size | Notes |
|-------|------|-------|
| Icon / pickup | 8–16 | 1–2 colors of detail |
| **Humanoid hero (side RPG)** | **64×64** | See **[humanoid-hero.md](humanoid-hero.md)** — default for warriors |
| Platformer | 32×32 | Readable at 720p |
| Chibi (only if asked) | 16×16 or 24×24 | Big head — **not** default for “hero” |
| Tall NPC | 32×48 | Feet on bottom row |

## Order of construction

1. Silhouette (darkest ramp step or flat fill).
2. Local shading (shifted duplicate shapes with `only="opaque"`).
3. Highlights (smallest shapes last).
4. Outline (usually outside; skip on lit edge for selective outline).
5. Accents (eyes, weapon glint).

## Tiles

- Use **power-of-two** or consistent multiples (16×16 common for Spark demos).
- Design **edge tiles** and **corners** as separate indices in the tileset.
- Leave 0–1 px inner highlight on top surfaces for readability.

## Animation layout

Pack frames left-to-right in the atlas; **row 0 is the bottom row** in Spark’s UV math.
When planning a sheet, lay out in code in linear order 0..N-1 matching that grid.
