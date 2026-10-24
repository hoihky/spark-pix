#!/usr/bin/env bash
# Fail if tracked (or, without git, project) text files contain home paths or secret-like strings.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

RED='\033[0;31m'
NC='\033[0m'
fail=0

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  echo "Usage: $0" >&2
  echo "Scans non-ignored project files for home paths and common secret patterns." >&2
  exit 0
fi

# Real home dirs (username must start with a letter; skips doc examples like /Users/...)
PATH_PATTERNS=(
  '/Users/[A-Za-z][A-Za-z0-9._-]*'
  '/home/[a-z][a-z0-9._-]*'
  '\\\\Users\\\\[A-Za-z][A-Za-z0-9._-]*'
)

SECRET_PATTERNS=(
  'ghp_[0-9A-Za-z]{20,}'
  'github_pat_[0-9A-Za-z_]{20,}'
  'sk-[a-zA-Z0-9]{20,}'
  'AKIA[0-9A-Z]{16}'
  'xox[baprs]-[0-9A-Za-z-]{10,}'
  '-----BEGIN (RSA |OPENSSH |EC )?PRIVATE KEY-----'
  '(?i)(api[_-]?key|secret[_-]?key|access[_-]?token|auth[_-]?token)\s*=\s*["\x27][^"\x27]{8,}["\x27]'
  '(?i)(CURSOR_|OPENAI_|ANTHROPIC_)[A-Z0-9_]*\s*=\s*["\x27]?[A-Za-z0-9_./+-]{16,}'
)

is_text_file() {
  case "$1" in
    *.py|*.md|*.html|*.css|*.json|*.toml|*.txt|*.tsx|*.sh|*.yml|*.yaml|*.ini|*.cfg|*.gitignore|LICENSE) return 0 ;;
    *) return 1 ;;
  esac
}

match_in_file() {
  local pattern="$1" file="$2"
  if command -v rg >/dev/null 2>&1; then
    rg -n --no-heading -e "$pattern" "$file" 2>/dev/null || true
  else
    grep -nE "$pattern" "$file" 2>/dev/null || true
  fi
}

report() {
  local label="$1" file="$2" lines="$3"
  echo -e "${RED}FAIL:${NC} $label" >&2
  while IFS= read -r line; do
    [[ -n "$line" ]] && echo "  $file:$line" >&2
  done <<< "$lines"
  fail=1
}

check_patterns() {
  local file="$1"
  local p label lines
  for p in "${PATH_PATTERNS[@]}"; do
    lines="$(match_in_file "$p" "$file")"
    if [[ -n "$lines" ]]; then
      report "machine-specific path ($p)" "$file" "$lines"
    fi
  done
  for p in "${SECRET_PATTERNS[@]}"; do
    lines="$(match_in_file "$p" "$file")"
    if [[ -n "$lines" ]]; then
      report "possible secret ($p)" "$file" "$lines"
    fi
  done
}

iter_files() {
  if git rev-parse --git-dir >/dev/null 2>&1; then
    git ls-files -z
  else
    echo "note: not a git repo; scanning tree (excluding .venv, out/, .cursor)" >&2
    find . \
      -path './.git' -prune -o \
      -path './.venv' -prune -o \
      -path './venv' -prune -o \
      -path './.cursor' -prune -o \
      -path './pixel-art/*/out' -prune -o \
      -path './pixel-art/_study' -prune -o \
      -type f -print0 2>/dev/null | sed 's|^\./||'
  fi
}

while IFS= read -r -d '' file; do
  file="${file#./}"
  [[ -f "$file" ]] || continue
  is_text_file "$file" || continue
  check_patterns "$file"
done < <(iter_files)

if [[ "$fail" -ne 0 ]]; then
  echo >&2
  echo "Privacy audit failed. Remove or redact the matches above before pushing." >&2
  exit 1
fi

echo "Privacy audit passed."
