#!/usr/bin/env python3
"""Validate spark-pix outputs (PNG atlases + manifest)."""

from __future__ import annotations

import sys
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from sparkpix.validate_atlas import validate_atlas_dir


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print("usage: validate.py <output-dir>", file=sys.stderr)
        return 2
    target = Path(argv[1])
    if not target.is_dir():
        print(f"not a directory: {target}", file=sys.stderr)
        return 2
    errors = validate_atlas_dir(target)
    if errors:
        for e in errors:
            print("ERROR:", e)
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
