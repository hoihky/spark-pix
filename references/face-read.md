# Face read (hair + eye)

See **[jrpg-profile-face.md](jrpg-profile-face.md)** for **`JrpgHeadLook`** knobs and examples.

**Production standard:** At **8× preview**, read **hair color/volume** and **eye direction** — no mouth, **no neck** on Q heroes.

Use **`character.profile_head_facing_right(..., look=HEAD_LOOK)`** — do not hand-draw face pixels in `build.py`.

## Checklist

- [ ] **Hair ramp** ≥4 steps (shadow → highlight); style matches brief.
- [ ] **No neck** — jaw meets collar / back hair (16-bit ref).
- [ ] **Eye** — `vertical` = 2×3 dark \| sclera under bangs; `hero` = dark tick under brow.
- [ ] **Fringe** — `fringe_over_eye=True` shadows top eye row only.
- [ ] **Forehead** accessory documented (`bandana` / `wrap` / `none`).

Reject ship if squint test at 1× fails on `preview_idle.png`.
