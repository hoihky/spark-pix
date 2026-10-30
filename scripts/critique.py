#!/usr/bin/env python3
"""Heuristic sprite quality report (atlas frames)."""

from __future__ import annotations

import sys
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from sparkpix.cli import _cmd_critique  # noqa: E402
import argparse  # noqa: E402


def main(argv: list[str]) -> int:
    p = argparse.ArgumentParser(description="Critique spark-pix atlas frames")
    p.add_argument("directory")
    p.add_argument("--frames", default="0")
    p.add_argument("--max-colors", type=int, default=32)
    p.add_argument("--strict", action="store_true")
    args = p.parse_args(argv[1:])
    return _cmd_critique(args)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
