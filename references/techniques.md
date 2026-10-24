# Techniques

## Ramps

`ramp("#base", steps=5)` returns darkest → lightest. Shade with stacked shapes:

```python
s.ellipse(x0, y0+1, x1, y1+1, fill=BODY[0])      # shadow mass
s.ellipse(x0, y0, x1, y1, fill=BODY[2], only="opaque")
s.ellipse(x0+2, y0+1, x1-2, y1-3, fill=BODY[4], only="opaque")  # highlight
```

## Selective outline

`outline(dark, where="outside")` on the full sprite. Remove highlights on the
top-left lit edge by painting a 1px strip of background color over unwanted outline.

## Dither

`dither((x0,y0,x1,y1), c_dark, c_light, mix_ratio, pattern="checker")` for
gradients without extra palette colors.

## Masking

`only="opaque"` — draw only atop existing pixels (clothing layers).
`only="empty"` — draw only in transparent areas (background halos).

## Palette discipline

Pick 1–2 ramps + 1 outline + 1 background transparent. Quantize mentally before drawing;
`used_colors()` after each pass.
