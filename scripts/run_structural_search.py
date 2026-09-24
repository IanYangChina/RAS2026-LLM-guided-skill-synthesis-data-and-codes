#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from search.public_catalog import resolve_record
from search.semantic_manifest import load_cell
from search.winner import persist_winner

TASKS = ("door_push", "push_to_goal", "peg_insert", "peg_channel", "grasp_place", "obstacle_reach")
SEMANTIC_CONDITIONS = ("full", "no_history", "no_contact_info", "no_scene_description", "misaligned_history", "misattributed_contact", "wrong_scene_targets")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the public structural-refinement matrix.")
    parser.add_argument("--method", choices=("bandit", "map_qd", "llm"), default="bandit")
    parser.add_argument("--initialization", choices=("create", "scaffold", "random"), default=None, help="Defaults to Scaffold; semantic interventions default to Random.")
    parser.add_argument("--subtask-mode", choices=("fixed", "free"), default="fixed")
    parser.add_argument("--task", choices=TASKS + ("all",), default="obstacle_reach")
    parser.add_argument("--condition", choices=SEMANTIC_CONDITIONS, default="full")
    parser.add_argument("--seed", type=int, action="append", default=None)
    parser.add_argument("--iterations", type=int, default=1)
    parser.add_argument("--cma-budget", type=int, default=8)
    parser.add_argument("--episodes", type=int, default=1)
    parser.add_argument("--out-dir", type=Path, default=Path("runs/structural_search"))
    parser.add_argument("--catalog", type=Path, default=ROOT / "data" / "catalog.csv")
    parser.add_argument("--created-skill", type=Path, help="Archived created initial skill for Create with Bandit or MAP-QD.")
    parser.add_argument("--created-record-id", help="Catalog record ID for a created initial skill.")
    parser.add_argument("--semantic-study", action="store_true", help="Run an explicit semantic intervention rather than the primary FreeST arm.")
    parser.add_argument("--semantic-manifest", type=Path, help="Manifest required only with --semantic-study.")
    parser.add_argument("--paper-protocol", action="store_true")
    parser.add_argument("--backend", choices=("mujoco", "mock"), default="mujoco")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--model", default=None)
    parser.add_argument("--base-url", default=None)
    return parser


def _apply_protocol(args: argparse.Namespace) -> None:
    if args.paper_protocol:
        args.task, args.seed, args.iterations, args.cma_budget, args.episodes = "all", list(range(10)), 15, 200, 3


def _validate(args: argparse.Namespace, parser: argparse.ArgumentParser) -> None:
    _apply_protocol(args)
    if args.initialization is None:
        args.initialization = "random" if args.semantic_study else "scaffold"
    if args.semantic_study and args.initialization != "random":
        parser.error("--semantic-study requires --initialization random")
    if min(args.iterations, args.cma_budget, args.episodes) < 1:
        parser.error("--iterations, --cma-budget, and --episodes must be positive")
    if args.subtask_mode == "free" and args.method != "llm":
        parser.error("FreeST is available only with --method llm")
    if args.semantic_study and args.subtask_mode != "free":
        parser.error("--semantic-study requires --subtask-mode free")
    if args.semantic_study and args.semantic_manifest is None:
        parser.error("--semantic-study requires --semantic-manifest")
    if args.semantic_study and args.semantic_manifest.name != "manifest.json":
        parser.error("--semantic-manifest must be named manifest.json for the standalone runner")
    if not args.semantic_study and args.semantic_manifest is not None:
        parser.error("--semantic-manifest is valid only with --semantic-study")
    if not args.semantic_study and args.condition != "full":
        parser.error("non-full conditions require --semantic-study")


def _created_skill(args: argparse.Namespace, task: str, seed: int) -> Path:
    if args.created_skill is not None:
        if not args.created_skill.is_file():
            raise FileNotFoundError(f"created skill does not exist: {args.created_skill}")
        return args.created_skill
    record = resolve_record(args.catalog, ROOT, source="llm_created", task=task, seed=seed, record_id=args.created_record_id)
    return record.path


def _semantic_arguments(args: argparse.Namespace, task: str, seed: int) -> list[str]:
    if not args.semantic_study:
        return []
    assert args.semantic_manifest is not None
    cell, _ = load_cell(args.semantic_manifest, task=task, seed=seed, condition=args.condition)
    return ["--semantic-manifest-root", str(args.semantic_manifest.parent), "--semantic-policy-version", "semantic-context-policy-v1", "--realized-scene-context-version", "skill-synthesis-realized-scene-context-v1", "--initial-skill-yaml-sha256", cell.initial_skill_yaml_sha256, "--realized-scene-state-sha256", cell.realized_scene_state_sha256, "--randomized-config-bank-sha256", cell.randomized_config_bank_sha256]


def _command(args: argparse.Namespace, task: str, seed: int, stage: Path) -> list[str]:
    scripts = ROOT / "scripts"
    shared = ["--task", task, "--seeds", str(seed), "--n-iters", str(args.iterations), "--n-samples", str(args.episodes), "--cma-budget", str(args.cma_budget), "--out-dir", str(stage)]
    if args.method == "bandit":
        init = {"scaffold": "task_conditioned_random", "random": "grammar_uniform_random", "create": "task_conditioned_random"}[args.initialization]
        command = [sys.executable, str(scripts / "_bandit_search.py"), "--proposer", "bandit", "--init-mode", init, "--subtask-mode", "fixed", *shared]
        if args.initialization == "create":
            command.extend(("--initial-skill", str(_created_skill(args, task, seed))))
        return command
    if args.method == "map_qd":
        init = {"scaffold": "task_conditioned_random", "random": "grammar_uniform_random", "create": "supplied_skill"}[args.initialization]
        command = [sys.executable, str(scripts / "_mapqd_search.py"), "--init-mode", init, "--subtask-mode", "fixed", *shared]
        if args.initialization == "create":
            command.extend(("--initial-skill", str(_created_skill(args, task, seed))))
        return command
    init = {"create": "agent_create", "scaffold": "task_conditioned_random", "random": "grammar_uniform_random"}[args.initialization]
    command = [sys.executable, str(scripts / "_llm_search.py"), "--task", task, "--condition", args.condition, "--seed", str(seed), "--T", str(args.iterations), "--k-runs", str(args.episodes), "--cma-budget", str(args.cma_budget), "--init-mode", init, "--subtask-mode", args.subtask_mode, "--out-dir", str(stage), *_semantic_arguments(args, task, seed)]
    if args.semantic_study:
        command.extend(("--system-prompt-file", str(ROOT / "search" / "prompts" / "public_semantic_pinned.txt")))
    if args.initialization == "create":
        command.append("--fail-on-agent-create-fallback")
    if args.model:
        command.extend(("--model", args.model))
    return command


def _normalize(stage: Path, destination: Path, args: argparse.Namespace, task: str, seed: int) -> dict[str, Any]:
    source = stage if args.method == "llm" else stage / f"{task}_seed{seed}"
    if not source.is_dir():
        raise FileNotFoundError(f"runner did not produce expected output: {source}")
    summary = json.loads((source / "summary.json").read_text(encoding="utf-8"))
    if summary.get("backend_name") != "mujoco":
        raise RuntimeError("scientific winner persistence requires a MuJoCo summary")
    destination.mkdir(parents=True, exist_ok=True)
    for item in source.iterdir():
        shutil.move(str(item), destination / item.name)
    if stage.exists():
        shutil.rmtree(stage)
    return persist_winner(destination, method=args.method, initialization=args.initialization, task=task, seed=seed, subtask_mode=args.subtask_mode, backend=args.backend)


def _mock_run(destination: Path, args: argparse.Namespace, task: str, seed: int) -> None:
    from compiler import compile as compile_skill
    from dsl.serialiser import dump_skill, load_skill
    from evaluation.metrics import compute_metrics
    from evaluation.runner import run_evaluation
    from evaluation.task_spec import TaskSpec
    from scripts.task_configs import TASK_CONFIGS
    from search.scaffold_init import GrammarUniformInitialiser, sample_scaffold_skill
    from simulation.mock_backend import MockSimulatorBackend
    import random
    if args.initialization == "create":
        skill = load_skill(_created_skill(args, task, seed).read_text(encoding="utf-8"))
    elif args.initialization == "scaffold":
        skill = sample_scaffold_skill(task, random.Random(seed))
    else:
        skill = GrammarUniformInitialiser(task, random.Random(seed)).sample()
    spec = TaskSpec(**TASK_CONFIGS[task]["task_spec"])
    traces = run_evaluation(compile_skill(skill), MockSimulatorBackend(), n_samples=args.episodes, seed=seed, task_spec=spec)
    metrics = compute_metrics(traces, skill, task_spec=spec, task_name=task)
    destination.mkdir(parents=True, exist_ok=True)
    (destination / "run_log.json").write_text(json.dumps([{"iteration": 0, "skill_yaml": dump_skill(skill), "task_score": metrics.task_score, "canonical_task_score": metrics.task_score, "composite_score": metrics.composite_score, "best_params": {}, "scientific": False}], indent=2))
    persist_winner(destination, method=args.method, initialization=args.initialization, task=task, seed=seed, subtask_mode=args.subtask_mode, backend="mock")


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    _validate(args, parser)
    tasks, seeds = (TASKS if args.task == "all" else (args.task,)), args.seed or [0]
    for task in tasks:
        for seed in seeds:
            destination = args.out_dir / args.method / args.initialization / args.subtask_mode / task / f"seed_{seed}"
            stage = destination / ".staging"
            command = _command(args, task, seed, stage)
            if args.dry_run:
                print(" ".join(command))
                continue
            if args.backend == "mock":
                _mock_run(destination, args, task, seed)
                continue
            environment = os.environ.copy()
            if args.base_url:
                environment["OPENAI_COMPATIBLE_BASE_URL"] = args.base_url
            subprocess.run(command, check=True, env=environment)
            metadata = _normalize(stage, destination, args, task, seed)
            print(json.dumps(metadata, sort_keys=True))


if __name__ == "__main__":
    main()
