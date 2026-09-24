#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

os.environ.setdefault("MUJOCO_GL", "osmesa")
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from compiler import compile as compile_skill
from dsl.serialiser import load_skill
from evaluation.metrics import compute_metrics
from evaluation.runner import run_evaluation
from evaluation.task_spec import TaskSpec
from scripts.task_configs import SIM_CONFIGS, TASK_CONFIGS
from search.parameter_optimiser import optimise_parameters
from search.public_catalog import resolve_record
from simulation.realized_scene import RealizedSceneConfigBank, activate_realized_scene_configuration, materialize_realized_scene_config_bank

SOURCES = ("llm_created", "expert_reference", "scaffold", "grammar_random", "skill")
PAPER_TASKS = ("door_push", "push_to_goal", "peg_insert", "peg_channel", "obstacle_reach", "grasp_place")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Optimise a catalogued skill's continuous parameters with CMA-ES.")
    parser.add_argument("--source", choices=SOURCES, default="expert_reference")
    parser.add_argument("--task", choices=PAPER_TASKS, default="obstacle_reach")
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--skill", type=Path, help="Explicit skill YAML; required for --source skill.")
    parser.add_argument("--record-id")
    parser.add_argument("--catalog", type=Path, default=ROOT / "data" / "catalog.csv")
    parser.add_argument("--scene-bank", type=Path, help="Archived frozen scene-bank JSON; otherwise materialize deterministically.")
    parser.add_argument("--out-dir", type=Path, default=Path("runs/parameter_optimization"))
    parser.add_argument("--cma-budget", type=int, default=8)
    parser.add_argument("--basins", type=int, default=1)
    parser.add_argument("--episodes", type=int, default=1)
    parser.add_argument("--backend", choices=("mujoco", "mock"), default="mujoco")
    parser.add_argument("--paper-protocol", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    return parser


def resolve_skill(source: str, task: str, seed: int, skill: Path | None, catalog: Path, record_id: str | None) -> Path:
    if source == "skill":
        if skill is None:
            raise ValueError("--source skill requires --skill")
        if not skill.is_file():
            raise FileNotFoundError(f"skill does not exist: {skill}")
        return skill
    if skill is not None:
        raise ValueError("--skill is only valid with --source skill")
    return resolve_record(catalog, ROOT, source=source, task=task, seed=seed, record_id=record_id).path


def _trace_rows(traces: list[Any]) -> list[dict[str, Any]]:
    return [{"success": trace.success, "final_pose_error": trace.final_pose_error, "peak_contact_force": trace.peak_contact_force, "parameter_values": getattr(trace, "parameter_values", {})} for trace in traces]


def _backend(task: str, seed: int, kind: str):
    if kind == "mock":
        from simulation.mock_backend import MockSimulatorBackend
        return MockSimulatorBackend(), None
    from simulation.mujoco_backend import MuJoCoBackend
    from simulation.scene import SceneConfig
    sim = SIM_CONFIGS[task]
    backend = MuJoCoBackend(SceneConfig(robot=sim.get("robot", "panda"), gripper=sim.get("gripper"), object_xml=sim.get("object_xml"), target_markers=sim.get("target_markers", ()), tcp_markers=sim.get("tcp_markers", ())))
    backend._rand_config = TASK_CONFIGS[task].get("randomisation", {})
    import numpy as np
    backend._rand_rng = np.random.default_rng(seed)
    return backend, True


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.paper_protocol:
        args.cma_budget, args.basins, args.episodes = 200, 3, 3
    if min(args.cma_budget, args.basins, args.episodes) < 1:
        parser.error("all budgets must be positive")
    try:
        path = resolve_skill(args.source, args.task, args.seed, args.skill, args.catalog, args.record_id)
    except (FileNotFoundError, LookupError, ValueError) as exc:
        parser.error(str(exc))
    if args.dry_run:
        print(json.dumps({"skill": str(path), "source": args.source, "task": args.task, "seed": args.seed, "backend": args.backend}, indent=2))
        return
    skill = load_skill(path.read_text(encoding="utf-8"))
    spec = TaskSpec(**TASK_CONFIGS[args.task]["task_spec"])
    backend, scientific = _backend(args.task, args.seed, args.backend)
    bank: RealizedSceneConfigBank | None = None
    if args.backend == "mujoco":
        if args.scene_bank:
            bank = RealizedSceneConfigBank.from_dict(json.loads(args.scene_bank.read_text(encoding="utf-8")))
            if bank.task_name != args.task or len(bank.configurations) != args.basins:
                parser.error("scene bank task or basin count does not match this run")
        else:
            bank = materialize_realized_scene_config_bank(backend, args.task, spec, outer_seed=args.seed, k_runs=args.basins)
    artifact = compile_skill(skill)
    metrics, best_params, diagnostics = optimise_parameters(artifact, backend, task_spec=spec, budget=args.cma_budget, K_basin_runs=args.basins, seed=args.seed, task_name=args.task, randomized_config_bank=bank)
    if bank is not None:
        activate_realized_scene_configuration(backend, bank.configurations[0])
    traces = run_evaluation(artifact, backend, n_samples=args.episodes, seed=args.seed, task_spec=spec, fixed_params=best_params)
    final_metrics = compute_metrics(traces, skill, task_spec=spec, task_name=args.task, K_basin_runs=args.basins)
    out = args.out_dir / args.source / args.task / f"seed_{args.seed}"
    out.mkdir(parents=True, exist_ok=True)
    (out / "best_parameters.json").write_text(json.dumps(best_params, indent=2, sort_keys=True))
    (out / "optimization_metrics.json").write_text(json.dumps(metrics.to_dict(), indent=2, sort_keys=True))
    (out / "final_metrics.json").write_text(json.dumps(final_metrics.to_dict(), indent=2, sort_keys=True))
    (out / "cma_diagnostics.json").write_text(json.dumps(diagnostics, indent=2, sort_keys=True))
    (out / "final_traces.json").write_text(json.dumps(_trace_rows(traces), indent=2, sort_keys=True))
    identity: dict[str, Any] = {"backend": args.backend, "scientific": bool(scientific), "scene_bank_sha256": bank.sha256 if bank else None, "replay_configuration_index": 0 if bank else None}
    (out / "replay_identity.json").write_text(json.dumps(identity, indent=2, sort_keys=True))
    if bank is not None:
        (out / "scene_bank.json").write_text(json.dumps(bank.to_dict(), indent=2, sort_keys=True))
    print(out)


if __name__ == "__main__":
    main()
