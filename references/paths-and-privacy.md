# Paths and privacy

## Rules for this repo

1. **No machine-specific absolute paths** in Python, config, docs, or JSON metadata  
   (e.g. no `/Users/...`, `/home/...`, real usernames).
2. **Build scripts** resolve the repo via `Path(__file__).resolve().parents[...]` only.
3. **Spark deployment** uses **repo-relative** or **environment** paths:
   - Sibling checkout: `../spark/assets/sprites/<pack>/`
   - Or set `SPARK_ASSETS_SPRITES` to your Spark `assets/sprites` directory (absolute path is OK in **local shell env**, not committed to git).
4. **Do not commit:** see root `.gitignore` — `.venv/`, `*.egg-info/`, `pixel-art/**/out/`, `.cursor/`, secrets (`.env`, keys), local reference uploads under `pixel-art/_study/`.
5. **User reference images** dropped in chat should not be copied into the repo unless the user explicitly wants them; use `study.py` output only under `_study/` (ignored).

## Copying art into Spark

```bash
# From spark-pix repo root; Spark as sibling folder "spark"
PACK=robot_ranger
cp pixel-art/$PACK/out/*.png pixel-art/$PACK/out/*.spark-atlas.json ../spark/assets/sprites/$PACK/
```

## Agent / skill authors

- Read the user’s workspace for Spark location; do not assume a fixed disk path.
- Generated `*.sparkpix.json` projects must not embed home-directory paths (only relative asset names).

## CI / pre-push check

```bash
./scripts/audit_privacy.sh
```

Uses `git ls-files` when the repo is initialized (only tracked paths). Exits non-zero on real `/Users/<name>` or `/home/<name>` paths and common secret patterns.
