# Validation checklist

Before delivery, verify:

- [ ] Silhouette readable at 1× (squint test on `preview_idle.png`).
- [ ] **Humanoid hero:** read [humanoid-hero.md](humanoid-hero.md) — limbs ≥2 px wide, head ≤22% height, feet on baseline.
- [ ] Outline consistent width (mostly 1px; 2px only on outer hull if style demands).
- [ ] Light direction consistent across frames and tiles.
- [ ] No orphan single pixels (`used_colors` + visual scan).
- [ ] Animation: feet / contact points stable; no subpixel drift (integer coords only).
- [ ] Color count within brief budget.
- [ ] `python3 scripts/validate.py out/` passes for atlases.
- [ ] Spark manifest `columns * rows` fits all frames; clips within range.
- [ ] Tile size matches TSX `tilewidth` / `tileheight`; collision props on solid tiles.
