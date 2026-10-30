#!/usr/bin/env python3
"""Command-line interface for spark-pix."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from sparkpix import game_palette


def _cmd_validate(args: argparse.Namespace) -> int:
    from sparkpix.validate_atlas import validate_atlas_dir

    root = Path(args.directory)
    errors = validate_atlas_dir(root)
    if errors:
        for e in errors:
            print(f"ERROR: {e}", file=sys.stderr)
        return 1
    print("OK")
    return 0


def _cmd_critique(args: argparse.Namespace) -> int:
    from sparkpix.quality import critique_atlas_dir, format_report

    root = Path(args.directory)
    frames = tuple(int(x) for x in args.frames.split(",") if x.strip())
    report = critique_atlas_dir(root, sample_frames=frames or (0,), max_colors=args.max_colors)
    print(format_report(report))
    if not report.ok():
        return 1
    if report.warn_count() and args.strict:
        return 1
    return 0


def _cmd_study(args: argparse.Namespace) -> int:
    scripts = Path(__file__).resolve().parent.parent
    sys.path.insert(0, str(scripts))
    from study import analyze  # noqa: WPS433

    report = analyze(Path(args.input), Path(args.output))
    print(json.dumps(report, indent=2))
    return 0


def _cmd_palette(args: argparse.Namespace) -> int:
    if args.palette_cmd == "list":
        print("spark_game")
        return 0
    if args.palette_cmd == "show":
        for i, (r, g, b, a) in enumerate(game_palette.SPARK_GAME):
            print(f"{i:2d}  #{r:02x}{g:02x}{b:02x}  a={a}")
        print(f"\n{game_palette.describe()}")
        return 0
    if args.palette_cmd == "export":
        out = Path(args.path) if args.path else Path("pixel-art/_shared/spark_game.palette.json")
        game_palette.export_json(out)
        print(f"wrote {out}")
        return 0
    return 2


def _cmd_manifest(args: argparse.Namespace) -> int:
    path = Path(args.manifest)
    data = json.loads(path.read_text(encoding="utf-8"))
    if args.manifest_cmd == "show":
        print(json.dumps(data, indent=2))
        return 0
    if args.manifest_cmd == "summary":
        clips = data.get("clips", [])
        print(f"texture={data.get('texture')} grid={data.get('columns')}x{data.get('rows')}")
        print(f"frame={data.get('frameWidth')}x{data.get('frameHeight')} padding={data.get('padding', 0)}")
        for c in clips:
            print(
                f"  clip {c.get('name')}: frames {c.get('firstFrame')}.."
                f"{int(c.get('firstFrame', 0)) + int(c.get('frameCount', 1)) - 1} "
                f"@ {c.get('framesPerSecond')} fps loop={c.get('loop')}"
            )
        return 0
    return 2


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="sparkpix", description="Spark-pix pixel art toolkit")
    sub = p.add_subparsers(dest="command", required=True)

    v = sub.add_parser("validate", help="Validate atlas PNG + .spark-atlas.json in a directory")
    v.add_argument("directory")
    v.set_defaults(func=_cmd_validate)

    cr = sub.add_parser("critique", help="Heuristic art-quality warnings on atlas frames")
    cr.add_argument("directory")
    cr.add_argument(
        "--frames",
        default="0",
        help="Comma-separated frame indices to sample (default: idle frame 0)",
    )
    cr.add_argument("--max-colors", type=int, default=32, help="Opaque RGB budget per frame")
    cr.add_argument(
        "--strict",
        action="store_true",
        help="Exit 1 when any WARN (for CI gates)",
    )
    cr.set_defaults(func=_cmd_critique)

    st = sub.add_parser("study", help="Analyze a reference PNG or GIF")
    st.add_argument("input")
    st.add_argument("output")
    st.set_defaults(func=_cmd_study)

    pal = sub.add_parser("palette", help="Shared game palette")
    pal_sub = pal.add_subparsers(dest="palette_cmd", required=True)
    pal_list = pal_sub.add_parser("list", help="List preset palette names")
    pal_list.set_defaults(func=_cmd_palette)
    pal_show = pal_sub.add_parser("show", help="Print spark_game swatches")
    pal_show.set_defaults(func=_cmd_palette)
    pal_export = pal_sub.add_parser("export", help="Write spark_game.palette.json")
    pal_export.add_argument("path", nargs="?")
    pal_export.set_defaults(func=_cmd_palette)

    man = sub.add_parser("manifest", help="Inspect .spark-atlas.json")
    man_sub = man.add_subparsers(dest="manifest_cmd", required=True)
    man_show = man_sub.add_parser("show", help="Pretty-print manifest JSON")
    man_show.add_argument("manifest")
    man_show.set_defaults(func=_cmd_manifest)
    man_sum = man_sub.add_parser("summary", help="Human-readable clip summary")
    man_sum.add_argument("manifest")
    man_sum.set_defaults(func=_cmd_manifest)

    return p


def main(argv: list[str] | None = None) -> int:
    # Allow `python -m sparkpix validate` to find scripts/validate.py
    scripts_dir = Path(__file__).resolve().parent.parent
    if str(scripts_dir) not in sys.path:
        sys.path.insert(0, str(scripts_dir))
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
