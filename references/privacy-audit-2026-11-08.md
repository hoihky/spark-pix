# Privacy audit report — 2026-11-08

Scope: scripts, config, markdown, and Python under `spark-pix` (workspace + git-tracked).

## Commands run

```bash
./scripts/audit_privacy.sh           # tracked files only
./scripts/audit_privacy.sh --all     # full tree (excl. .gitignore: _study, out, .cursor, .venv)
```

## Summary

| Result | Detail |
|--------|--------|
| **Secrets / API keys** | No matches (ghp_, sk-, AKIA, .env, private keys, etc.) |
| **Absolute home paths** | None in tracked files; none in workspace after fixes |
| **`.env` / credentials** | No committed files (`.gitignore` covers `.env`, `*.pem`, `credentials.json`) |
| **`pixel-art/_study/`** | Gitignored — reference uploads stay local |
| **`pixel-art/**/out/`** | Gitignored — generated atlases |

## Findings (fixed this session)

### 1. Hardcoded Cursor project slug (username leakage)

**File:** `scripts/scarf_keys_from_strips.py`  
**Was:** Hardcoded path under `~/.cursor/projects/` using a Cursor-encoded machine slug (username + project path).  
**Fix:** Use `SPARK_PIX_REF_ASSETS` env or `pixel-art/_ref_assets`; strips default to `pixel-art/_study/male_hero_ref/<clip>/source_1x.png`.

### 2. Chat-upload filenames in repo metadata

**Files:** `scripts/scarf_keys_from_strips.py` `CLIP_TABLE`, `pixel-art/male_hero/scarf_keys.json`  
**Was:** `male_hero-idle-<uuid>.png` style names from Cursor chat assets  
**Fix:** Generic strip names + `source` field now `source_1x.png` from study paths.

### 3. Audit blind spot

**Was:** `audit_privacy.sh` only scanned `git ls-files` — new packs (`male_hero`, `platform_*`, etc.) were untracked and not scanned.  
**Fix:** `--all` mode + pattern for Cursor-encoded path slugs; documented in `paths-and-privacy.md`.

## Remaining notes (not blocking)

| Item | Risk | Mitigation |
|------|------|------------|
| Many workspace files **not yet git-tracked** | Leaks could land on first `git add` | Run `./scripts/audit_privacy.sh --all` before first commit of new dirs |
| `scarf_keys.json` / build outputs | Low — keys are animation data only | Keep `out/` ignored; regenerate keys from `_study` |
| `analyze_strip` stores `source` basename | Low | Only `source_1x.png` when using study layout |
| Docs mention `/Users/...` as **examples** | None | Audit regex requires a username segment after `/Users/` |

## Checklist for contributors

- [ ] `./scripts/audit_privacy.sh --all` passes
- [ ] No `Path.home() / ".cursor" / "projects" / Users-...` in committed code
- [ ] Reference art only under `pixel-art/_study/` (ignored) or sanitized `_study` exports
- [ ] Optional local strips: `export SPARK_PIX_REF_ASSETS=...` in shell only
- [ ] Before push: `./scripts/audit_privacy.sh` (tracked) + validate/critique on packs

## Related

- [paths-and-privacy.md](paths-and-privacy.md)
- [validations.md](validations.md) — pre-ship gate
