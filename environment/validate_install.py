#!/usr/bin/env python3
"""Validate a freshly installed archive without simulation or network calls by default."""
from __future__ import annotations

import argparse
import importlib
import importlib.metadata
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACKAGES = {
    "numpy": "2.2.6",
    "scipy": "1.15.2",
    "PyYAML": "6.0.3",
    "attrs": "25.4.0",
    "mujoco": "3.5.0",
    "cma": "4.4.4",
    "openai": "2.30.0",
    "matplotlib": "3.10.8",
    "Pillow": "12.1.1",
    "imageio": "2.37.2",
    "imageio-ffmpeg": "0.6.0",
    "pandas": "2.3.3",
    "openpyxl": "3.1.5",
    "pytest": "9.0.2",
}
RUNTIME_MODULES = ("compiler", "dsl", "evaluation", "mutation", "primitives", "search", "simulation")
PUBLIC_SCRIPTS = (
    "reproduce_paper_results.py",
    "run_structural_search.py",
    "run_parameter_optimization.py",
    "render_skill.py",
    "validate_archive.py",
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate the installed public runtime.")
    parser.add_argument(
        "--check-render-context",
        action="store_true",
        help="Create a minimal 1x1 MuJoCo render context; this is skipped by default for CI portability.",
    )
    parser.add_argument(
        "--headless-render-context",
        action="store_true",
        help="Set MUJOCO_GL=osmesa when unset and perform --check-render-context.",
    )
    return parser


def check_render_context(mujoco_module: object | None = None) -> None:
    """Create, render through, and release a minimal MuJoCo OpenGL context.

    The caller deliberately opts into this host-dependent test. Exceptions are
    converted to a concise installation error by :func:`main`.
    """
    mujoco = mujoco_module or importlib.import_module("mujoco")
    context = None
    renderer = None
    try:
        context = mujoco.GLContext(1, 1)
        context.make_current()
        model = mujoco.MjModel.from_xml_string("<mujoco><worldbody/></mujoco>")
        data = mujoco.MjData(model)
        renderer = mujoco.Renderer(model, height=1, width=1)
        renderer.update_scene(data)
        renderer.render()
    finally:
        if renderer is not None:
            renderer.close()
        if context is not None:
            context.free()


def main(argv: list[str] | None = None) -> None:
    args = build_parser().parse_args(argv)
    if args.headless_render_context:
        args.check_render_context = True
        os.environ.setdefault("MUJOCO_GL", "osmesa")
    if sys.version_info[:2] != (3, 10):
        raise SystemExit(f"expected Python 3.10, found {sys.version.split()[0]}")
    for distribution, expected in PACKAGES.items():
        actual = importlib.metadata.version(distribution)
        if actual != expected:
            raise SystemExit(f"{distribution}={actual}; expected {expected}")
    for module in RUNTIME_MODULES:
        importlib.import_module(module)
    for script in PUBLIC_SCRIPTS:
        completed = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / script), "--help"],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        if completed.returncode != 0:
            raise SystemExit(f"{script} --help failed:\n{completed.stderr}")
    if args.check_render_context:
        try:
            check_render_context()
        except Exception as exc:
            raise SystemExit(
                "MuJoCo render-context check failed. Configure a display or a supported "
                "headless backend (for example, rerun with --headless-render-context): "
                f"{exc}"
            ) from exc
        print("MuJoCo render-context check passed.")
    else:
        print("MuJoCo render-context check skipped (use --check-render-context to enable it).")
    print("Installation validation passed.")


if __name__ == "__main__":
    main()
