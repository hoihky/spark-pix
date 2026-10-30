# Techniques

**Production standard:** Limited palettes, one light direction, selective outlines —
readable at 1× without blur or fractional pixels. Pair with [palettes.md](palettes.md).

## Ramps

`ramp("#base", steps=5)` returns darkest → lightest. Shade with stacked shapes:

```python
s.ellipse(x0, y0+1, x1, y1+1, fill=BODY[0])      # shadow mass
s.ellipse(x0, y0, x1, y1, fill=BODY[2], only="opaque")
s.ellipse(x0+2, y0+1, x1-2, y1-3, fill=BODY[4], only="opaque")  # highlight
```

Use the same ramp steps across **characters and tiles** in one game pack.

## Selective outline

`outline(dark, where="outside")` on the full sprite — prefer **`character.finish_outside_outline(ink)`**
after the full humanoid is drawn ([character-api.md](character-api.md)). Remove highlights on the
top-left lit edge by painting a 1 px strip of background color over unwanted outline.
Avoid pure black rims on every edge unless the brief is Game Boy–strict.

## Dither

`dither((x0,y0,x1,y1), c_dark, c_light, mix_ratio, pattern="checker")` for
gradients without extra palette colors. Use sparingly on large flat tiles — prefer clean ramps for heroes.

## Masking

`only="opaque"` — draw only atop existing pixels (clothing layers).
`only="empty"` — draw only in transparent areas (background halos).

## Palette discipline

Pick 1–2 ramps + 1 outline + transparent background. Quantize before drawing;
`used_colors()` after each pass. If count exceeds the brief, merge nearest shades before export.

## Production anti-patterns

- Single-pixel `line()` limbs on humanoids — use **`character.limb`** / **`platformer_leg`** ([character-api.md](character-api.md)).
- Inconsistent light on tile edges vs character sprites in the same pack.
- Adding colors in the last pass without updating the shared palette import.
