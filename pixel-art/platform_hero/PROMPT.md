# Art generation prompt: platform_hero ("Skip")

## Source

- Reference: user platformer combat GIF — **motion & quality only** (low combat stance, long attack windup, hilt charge, forward burst, weapon smear, lingering crescent slash, dash afterimages).
- Originality: **Original hero** — chestnut hair, yellow bandana, teal hoodie, cargo shorts, orange boots, **hook baton** (not katana, not horned cap, not lavender hair/kimono).

## Style

- Canvas: **64×64** per frame, side view **+X**
- Palette budget: **~24–36** colors; light **upper-left**; selective same-hue shading
- Quality bar: `SKILL.md`, `humanoid-hero.md`, `platform-hero.md`, `validations.md`
- Export: 1× PNG + `platform_hero.spark-atlas.json`; nearest filter

## Original character

- **Body:** Athletic platformer proportions ~5 heads tall; feet on row **61**; filled limbs **≥3 px** front leg
- **Face:** 3/4 profile — neck, forward cheek, nose/mouth shadow, **sclera + green iris + highlight** (human read)
- **Outfit:** Teal hoodie, cream shirt panel, brown cargo shorts, orange boots, yellow bandana on forehead
- **Weapon:** Short hook baton from hand — 2 px wood shaft, metal hook, green glow tip

## Clips

| Clip   | Frames | FPS | Loop | Notes |
|--------|--------|-----|------|-------|
| idle   | 4      | 4   | yes  | ±1 px body breath; baton sway |
| walk   | 8      | 10  | yes  | Knee lift; baseline ±1 px |
| run    | 6      | 14  | yes  | Lean +2; longer stride |
| jump   | 6      | 12  | no   | Squash → air → land |
| dash   | 7      | 18  | no   | Crouch → burst; **2 ghost offsets** + wisps |
| attack | 11     | 12  | no   | See frame script below |

### Attack frame script

1. Combat ready, slight crouch  
2. Hand lowering toward hilt  
3. Deep windup — lean back, baton angled back  
4. Deeper crouch, grip pose  
5. **Hilt spark** charge pixels at hand  
6. Snap forward — smear begins (96°→70°)  
7. Peak slash — strong lean, smear 70°→42°→22°  
8. Extended low pose, smear tail  
9. **Lingering crescent slash VFX** (arc hold)  
10. Arc fade  
11. Recover to idle baton angle  

## Rig parameters

- `FOOT_Y = 61`; `finalize()` applies `dy` + `lean` to full skeleton
- Fields: hip, knees, feet, shoulder, elbow, hand, head, `baton_deg`, `baton_trail`, `hilt_spark`, `slash_arc`, `ghost_offsets`, `dash_wisps`, `squash`
- Atlas: **10 columns**; clip names exactly as table above

## Export

- `out/platform_hero.png`, `platform_hero.spark-atlas.json`, previews at 8×
- `python -m sparkpix validate out/` or `scripts/validate.py`

## Anti-patterns

- Tracing reference GIF pixels; stick legs; attack without windup; editing PNGs by hand
