#!/usr/bin/env python3
"""Render one archived robot skill as MP4 or looping GIF.

Examples:
    python scripts/render_skill.py --record-id p-random-language-fixed-push_to_goal-seed-02 \
        --output outputs/push-to-goal.gif
    python scripts/render_skill.py --task push_to_goal --skill data/skills/push.yaml \
        --parameters data/parameters/push.json --scene-bank data/scenes/push.json \
        --output outputs/push.mp4
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Ensure the extracted archive runtime wins over a same-named package when a
# reviewer invokes this script from another working directory.
_ARCHIVE_ROOT = Path(__file__).resolve().parents[1]
if str(_ARCHIVE_ROOT) not in sys.path:
    sys.path.insert(0, str(_ARCHIVE_ROOT))

from simulation.public_renderer import RenderInputError, render_spec, resolve_spec


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--record-id", help="stable record_id in data/catalog.csv")
    source.add_argument("--task", help="task name for explicit skill replay")
    parser.add_argument("--skill", help="archive-relative skill YAML path")
    parser.add_argument("--parameters", help="archive-relative JSON parameter map")
    parser.add_argument("--scene-bank", help="archive-relative JSON frozen scene bank")
    parser.add_argument("--scene-index", type=int, default=0, help="frozen scene index (default: 0)")
    parser.add_argument("--catalog", type=Path, help="alternate catalog CSV inside the archive")
    parser.add_argument("--output", type=Path, required=True, help="output .mp4 or .gif (outside data/)")
    parser.add_argument("--format", choices=("mp4", "gif"), help="override format inferred from output suffix")
    parser.add_argument("--fps", type=int, default=15)
    parser.add_argument("--width", type=int, default=640)
    parser.add_argument("--height", type=int, default=480)
    parser.add_argument(
        "--max-gif-mib",
        type=float,
        default=10.0,
        help="maximum GIF size in MiB (default: 10; use MP4 for larger output)",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.record_id is None and any(
            value is None for value in (args.skill, args.parameters, args.scene_bank)
        ):
            raise RenderInputError(
                "explicit rendering requires --task, --skill, --parameters, and --scene-bank"
            )
        output = args.output
        if args.format:
            output = output.with_suffix(f".{args.format}")
        elif output.suffix.lower() not in (".mp4", ".gif"):
            raise RenderInputError("--output must end in .mp4 or .gif (or provide --format)")
        spec = resolve_spec(
            record_id=args.record_id,
            task=args.task,
            skill=args.skill,
            parameters=args.parameters,
            scene_bank=args.scene_bank,
            scene_index=args.scene_index,
            catalog_path=args.catalog,
        )
        if args.max_gif_mib <= 0:
            raise RenderInputError("--max-gif-mib must be positive")
        path = render_spec(
            spec,
            output,
            fps=args.fps,
            width=args.width,
            height=args.height,
            max_gif_bytes=round(args.max_gif_mib * 1024 * 1024),
        )
    except (RenderInputError, RuntimeError, OSError) as exc:
        print(f"error: {exc}")
        return 2
    print(f"rendered {spec.record_id} ({spec.task}) -> {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
