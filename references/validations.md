# Validation checklist

**Production standard:** Do not deliver assets until every item below passes.
Agents: minimum **2** critique passes on 8× previews before checking boxes.

## Visual & construction

- [ ] Silhouette readable at **1×** (squint test on `preview_idle.png` or tile at 1×).
- [ ] Built in order from [patterns.md](patterns.md) (silhouette → shade → highlight → outline → accent).
- [ ] **Humanoid hero:** [humanoid-hero.md](humanoid-hero.md) — limbs ≥2 px wide, head ≤22% height, feet on baseline.
- [ ] Outline consistent width (mostly 1 px; 2 px only on outer hull if style demands).
- [ ] Light direction consistent across frames and tiles (default upper-left).
- [ ] No orphan single pixels (`used_colors()` + visual scan).
- [ ] Color count within brief budget ([palettes.md](palettes.md), typical 8–24).

## Animation (characters)

- [ ] Integer pixel coordinates only — no subpixel drift.
- [ ] Feet / contact points stable across walk/run; horizontal drift ≤1 px/frame unless intentional.
- [ ] Clip names match game code (`idle`, `walk`, …); FPS and loop flags documented in build header.
- [ ] Attack / hit / die clips use `loop=false` where appropriate ([animation.md](animation.md)).

## Export & engine

- [ ] `python -m sparkpix validate pixel-art/<name>/out` passes for atlases.
- [ ] **`python -m sparkpix critique pixel-art/<name>/out`** — sidecar present; no stick legs / weak outline on sampled frames.
- [ ] Spark manifest: `columns × rows` fits all frames; every clip within `[0, frameCount)`.
- [ ] Texture filenames in JSON match shipped PNGs; **1×** master PNG (previews are not game assets).
- [ ] **Tilesets:** `tilewidth` / `tileheight` match art; `spark_walkable` / `spark_collision` / `spark_blocks_pathfinding` set on gameplay tiles.
- [ ] TSX + PNG pair exported together; spot-check one solid and one walkable tile in Tiled if user maps levels.

## Process & repo hygiene

- [ ] Only `build.py` changed — exported PNGs regenerated, not hand-painted.
- [ ] Deterministic output (no unseeded randomness).
- [ ] `./scripts/audit_privacy.sh` passes before push (no home paths or secrets).

## Quality gate (reject ship)

Reject delivery if any of the following appear:

- Stick-figure humanoids (1 px limbs) when the brief asked for a hero or RPG character.
- First-pass art without preview iteration when quality is below commercial indie bar.
- Atlas with empty grid waste and no documented clip table for programmers.
