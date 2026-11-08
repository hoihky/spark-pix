#!/usr/bin/env python3
"""Deprecated — use ``scripts/scarf_keys_from_strips.py`` (idle/walk/run)."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

if __name__ == "__main__":
    script = Path(__file__).resolve().parent / "scarf_keys_from_strips.py"
    raise SystemExit(subprocess.call([sys.executable, str(script)]))
