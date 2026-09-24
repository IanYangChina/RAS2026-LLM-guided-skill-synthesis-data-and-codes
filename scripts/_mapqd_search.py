from __future__ import annotations
import argparse
import concurrent.futures
import json
import os
import pathlib
import random
import subprocess
import sys
import time
from typing import Any, Sequence
import numpy as np
os.environ.setdefault('MUJOCO_GL', 'osmesa')
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from compiler import compile as compile_skill
from dsl.serialiser import dump_skill, load_skill
from dsl.subtask_sanitizer import sanitize_subtasks
from evaluation.metrics import compute_sub_scores, safe_task_subscores
from evaluation.task_spec import TaskSpec
from mutation.operators import ALL_OPERATORS
from mutation.validator import mutate_and_validate
from scripts.artifact_paths import active_experiments_dir
from scripts._bandit_search import _is_no_valid_mutant_error, _run_final_episodes, _score_logging_fields, _write_progress_status
from scripts.task_configs import SIM_CONFIGS as _SIM_CONFIGS, TASK_CONFIGS
from search.mapqds_archive import MAPQDSArchive, MAPQDSArchiveEntry
from search.mapqds_descriptors import compute_descriptor
from search.parameter_optimiser import optimise_parameters
from search.proposal_metrics import build_evaluated_proposal_metrics
from search.scaffold_init import GrammarUniformInitialiser
from simulation.realized_scene import activate_realized_scene_configuration, materialize_realized_scene_config_bank
from search.structural_diff import structural_diff
STRUCTURAL_OPERATORS = tuple(ALL_OPERATORS[:7])

def _parse_args(argv: Sequence[str] | None=None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Run fixed-subtask MAP-QD structural refinement for one task.')
    parser.add_argument('--task', required=True)
    parser.add_argument('--seeds', nargs='+', type=int, default=None)
    parser.add_argument('--out-dir', default=None)
    parser.add_argument('--init-mode', choices=['task_conditioned_random', 'grammar_uniform_random', 'expert', 'supplied_skill'], default='expert')
    parser.add_argument('--initial-skill', default=None, metavar='YAML_PATH')
    parser.add_argument('--n-iters', type=int, default=None)
    parser.add_argument('--n-samples', type=int, default=3)
    parser.add_argument('--cma-budget', type=int, default=None)
    parser.add_argument('--k-basin', type=int, default=None)
    parser.add_argument('--mutation-count', type=int, default=1)
    parser.add_argument('--candidate-retry-limit', type=int, default=50)
    parser.add_argument('--candidate-workers', type=int, default=1, help='Parsed for future candidate-level parallelism; evaluation is sequential.')
    parser.add_argument('--subtask-mode', choices=['fixed', 'free'], default='fixed')
    args = parser.parse_args(argv)
    if args.subtask_mode != 'fixed':
        parser.error('run_mapqds_experiment.py currently supports fixed subtasks only')
    if args.init_mode == 'supplied_skill' and (not args.initial_skill):
        parser.error('--init-mode supplied_skill requires --initial-skill')
    if args.mutation_count < 1:
        parser.error('--mutation-count must be >= 1')
    if args.candidate_retry_limit < 1:
        parser.error('--candidate-retry-limit must be >= 1')
    if args.candidate_workers < 1:
        parser.error('--candidate-workers must be >= 1')
    return args

def _resolve_output_dir(out_dir: str | None, task_name: str) -> pathlib.Path:
    return pathlib.Path(out_dir) if out_dir else active_experiments_dir() / task_name

def _quality_key(record: dict[str, Any]) -> tuple[float, float, float, int, int]:
    return (float(record.get('task_score', 0.0)), float(record.get('composite_score', 0.0)), -float(record.get('complexity_penalty', 0.0)), -int(record.get('generation', 0)), -int(record.get('candidate_index', 0)))

def _select_iteration_winner(records: Sequence[dict[str, Any]]) -> dict[str, Any] | None:
    return max(records, key=_quality_key) if records else None

def _operator_name(operator: Any) -> str:
    return getattr(operator, '__name__', repr(operator))

def _json_safe(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(k): _json_safe(v) for (k, v) in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(v) for v in value]
    if hasattr(value, 'item'):
        return value.item()
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return str(value)

def _archive_fields(archive: MAPQDSArchive) -> dict[str, Any]:
    return {'archive_size': archive.size(), 'archive_coverage': archive.coverage()}

def _load_initial_skill(*, task_name: str, init_mode: str, initial_skill_path: str | None, rng: random.Random, sim_cfg: dict[str, Any]) -> tuple[Any, str, str | None]:
    if initial_skill_path is not None:
        path = pathlib.Path(initial_skill_path)
        return (load_skill(path.read_text(encoding='utf-8')), 'supplied_skill', str(path))
    if init_mode == 'supplied_skill':
        raise ValueError('--init-mode supplied_skill requires --initial-skill')
    if init_mode == 'task_conditioned_random':
        from search.scaffold_init import sample_scaffold_skill
        return (sample_scaffold_skill(task_name, rng), 'task_conditioned_random', None)
    if init_mode == 'grammar_uniform_random':
        return (GrammarUniformInitialiser(task_name, rng, min_phases=sim_cfg.get('min_phases', 1)).sample(), 'grammar_uniform_random', None)
    seed_path = pathlib.Path(__file__).resolve().parents[1] / 'tasks' / 'seeds' / task_name / 'seed_00.yaml'
    if not seed_path.exists():
        seed_path = pathlib.Path(__file__).resolve().parents[1] / 'tasks' / 'seeds' / task_name / 'seed_00.yaml'
    return (load_skill(seed_path.read_text(encoding='utf-8')), 'expert', str(seed_path))

def _make_backend(task_name: str, seed: int) -> tuple[Any, str, dict[str, Any]]:
    if task_name not in _SIM_CONFIGS:
        raise ValueError(f'Task {task_name!r} has no SIM_CONFIGS entry. Add it to scripts/task_configs.py.')
    sim_cfg = _SIM_CONFIGS[task_name]
    try:
        from simulation.mujoco_backend import MuJoCoBackend
        from simulation.scene import SceneConfig
        from simulation.realized_scene import activate_realized_scene_configuration, materialize_realized_scene_config_bank
        backend = MuJoCoBackend(SceneConfig(robot=sim_cfg.get('robot', 'panda'), gripper=sim_cfg['gripper'], object_xml=sim_cfg['object_xml'], target_markers=sim_cfg.get('target_markers', ()), tcp_markers=sim_cfg.get('tcp_markers', ())))
        rand_cfg = TASK_CONFIGS.get(task_name, {}).get('randomisation', {})
        if rand_cfg.get('enabled', False):
            backend._rand_config = rand_cfg
            backend._rand_rng = np.random.default_rng(seed)
            backend.freeze_scene_randomisation()
        print(f'[seed {seed}][backend] MuJoCoBackend initialised (MUJOCO_GL=osmesa)')
        return (backend, 'mujoco', sim_cfg)
    except Exception as exc:
        raise RuntimeError(f'[seed {seed}] MuJoCo backend initialization failed; rerun through the public --backend mock option only for non-scientific checks') from exc

def _evaluate_skill(*, skill: Any, parent_skill: Any | None, parent_metrics: Any | None, generation: int, label: str, task_name: str, task_spec: TaskSpec, backend: Any, rng: random.Random, cma_budget: int, n_samples: int, k_basin: int, lambda_penalty: float, subtask_mode: str, proposal_source: str, operator_name: str | None, candidate_index: int | None, sanitizer_fallbacks: int, raw_skill_yaml: str | None, randomized_config_bank: Any, archive: MAPQDSArchive) -> tuple[dict[str, Any], MAPQDSArchiveEntry]:
    start = time.time()
    artifact = compile_skill(skill)
    cma_seed = rng.randint(0, 2 ** 31 - 1)
    (metrics, best_params, cma_diagnostics) = optimise_parameters(artifact, backend, task_spec, budget=cma_budget, n_samples_per_eval=n_samples, seed=cma_seed, lambda_penalty=lambda_penalty, task_name=task_name, K_basin_runs=k_basin, randomized_config_bank=randomized_config_bank)
    activate_realized_scene_configuration(backend, randomized_config_bank.configurations[0])
    final_traces = _run_final_episodes(artifact, best_params, backend, task_spec, n=n_samples)
    sub_scores = compute_sub_scores(task_name=task_name, episode_results=final_traces, task_spec=task_spec)
    skill_yaml = dump_skill(skill)
    parent_yaml = dump_skill(parent_skill) if parent_skill is not None else None
    descriptor = compute_descriptor(skill, metrics)
    replaced_cell = archive.insert(skill, metrics, generation=generation, descriptor=descriptor, metadata={'label': label, 'best_params': best_params, 'cma_diagnostics': cma_diagnostics, 'candidate_index': candidate_index, 'operator': operator_name})
    archive_entry = archive.cells[descriptor]
    proposal_fields = build_evaluated_proposal_metrics(task=task_name, candidate_skill=skill, parent_skill=parent_skill, candidate_yaml=skill_yaml, parent_yaml=parent_yaml, candidate_metrics=metrics, parent_metrics=parent_metrics, task_spec=task_spec, subtask_mode=subtask_mode, proposal_source=proposal_source, accepted_as_elite=replaced_cell, parse_status='evaluated')
    diff = structural_diff(parent_skill, skill) if parent_skill is not None else {'summary': 'seed (no parent)'}
    record = {'iteration': generation, 'generation': generation, 'label': label, 'skill_yaml': skill_yaml, 'task_score': metrics.task_score, 'fitness_score': metrics.fitness_score, 'task_subscores': safe_task_subscores(metrics.task_subscores), 'skill_parameter_optimisation_scores': cma_diagnostics, 'composite_score': metrics.composite_score, 'termination_fidelity': metrics.termination_fidelity, 'force_compliance': metrics.force_compliance, 'complexity_penalty': metrics.complexity_penalty, **_score_logging_fields(metrics, cma_diagnostics=cma_diagnostics, posthoc_diagnostics={'final_replay_task_subscores': safe_task_subscores(sub_scores)}), 'best_params': best_params, 'descriptor': list(descriptor), 'mapqds_cell_replaced': replaced_cell, 'operator': operator_name, 'candidate_index': candidate_index, 'raw_proposed_skill_yaml': raw_skill_yaml, 'evaluated_candidate_yaml': skill_yaml, 'subtask_sanitizer_fallbacks': sanitizer_fallbacks, 'proposal_candidate_changed_before_evaluation': bool(raw_skill_yaml is not None and raw_skill_yaml.strip() != skill_yaml.strip()), 'reasoning_trace': {'proposer': 'MAPQDSArchive+uniform_structural_operator', 'last_operator_applied': operator_name, 'iteration': generation}, **proposal_fields, 'structural_diff': diff, 'wall_time_s': time.time() - start}
    return (_json_safe(record), archive_entry)

def _candidate_summary(record: dict[str, Any], *, archive: MAPQDSArchive) -> dict[str, Any]:
    return {'candidate_index': record.get('candidate_index'), 'operator': record.get('operator'), 'descriptor': record.get('descriptor'), 'task_score': record.get('task_score'), 'fitness_score': record.get('fitness_score'), 'composite_score': record.get('composite_score'), 'termination_fidelity': record.get('termination_fidelity'), 'force_compliance': record.get('force_compliance'), 'complexity_penalty': record.get('complexity_penalty'), 'skill_parameter_optimisation_scores': record.get('skill_parameter_optimisation_scores'), 'best_params': record.get('best_params'), 'mapqds_cell_replaced': record.get('mapqds_cell_replaced'), 'structural_diff': record.get('structural_diff', {}).get('summary'), **_archive_fields(archive)}

def run_one_seed(*, seed: int, task_name: str, n_iterations: int, cma_budget: int, n_samples: int, out_dir: str | pathlib.Path, k_basin: int, init_mode: str='expert', initial_skill_path: str | None=None, mutation_count: int=1, candidate_retry_limit: int=50, candidate_workers: int=1, subtask_mode: str='fixed') -> dict[str, Any]:
    if subtask_mode != 'fixed':
        raise ValueError('MAP-QD runner currently supports fixed subtasks only')
    if candidate_workers != 1:
        print('[warn] --candidate-workers is parsed for future use; candidates run sequentially')
    (backend, backend_name, sim_cfg) = _make_backend(task_name, seed)
    run_cfg = TASK_CONFIGS.get(task_name, {}).get('run_config', {})
    lambda_penalty = run_cfg.get('lambda_penalty', 0.05)
    task_spec = TaskSpec(**TASK_CONFIGS[task_name]['task_spec'])
    out_path = pathlib.Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    rng = random.Random(seed)
    archive = MAPQDSArchive()
    run_log: list[dict[str, Any]] = []
    (initial_skill, effective_init_mode, initial_source) = _load_initial_skill(task_name=task_name, init_mode=init_mode, initial_skill_path=initial_skill_path, rng=rng, sim_cfg=sim_cfg)
    randomized_config_bank = materialize_realized_scene_config_bank(backend, task_name, task_spec, outer_seed=seed, k_runs=k_basin)
    (out_path / 'scene_bank.json').write_text(json.dumps(randomized_config_bank.to_dict(), indent=2, sort_keys=True), encoding='utf-8')
    (initial_skill, fallback0) = sanitize_subtasks(initial_skill, task_spec)
    _write_progress_status(out_path, task=task_name, seed=seed, iteration=0, stage='start', label='gen_0_baseline')
    (gen0_record, _) = _evaluate_skill(skill=initial_skill, parent_skill=None, parent_metrics=None, generation=0, label='gen_0_baseline', task_name=task_name, task_spec=task_spec, backend=backend, rng=rng, cma_budget=cma_budget, n_samples=n_samples, k_basin=k_basin, lambda_penalty=lambda_penalty, subtask_mode=subtask_mode, proposal_source=effective_init_mode, operator_name=None, candidate_index=None, sanitizer_fallbacks=fallback0, raw_skill_yaml=None, randomized_config_bank=randomized_config_bank, archive=archive)
    gen0_record.update({'mutation_count': mutation_count, 'invalid_attempts': 0, **_archive_fields(archive)})
    run_log.append(gen0_record)
    _write_progress_status(out_path, task=task_name, seed=seed, iteration=0, stage='done', label='gen_0_baseline', wall_time_s=round(gen0_record.get('wall_time_s', 0.0), 2), composite_score=gen0_record.get('composite_score'), task_score=gen0_record.get('task_score'), archive_size=archive.size())
    min_phases = sim_cfg.get('min_phases', 1)
    method = f'{effective_init_mode}+mapqds_fixed_st+cma_es'
    evaluated_candidate_count = 0
    candidate_shortfall_total = 0
    for iteration in range(1, n_iterations + 1):
        iter_start = time.time()
        _write_progress_status(out_path, task=task_name, seed=seed, iteration=iteration, stage='start', label=f'iter_{iteration}', mutation_count=mutation_count, archive_size=archive.size())
        parent_entry = archive.sample_parent(rng)
        parent_skill = parent_entry.skill
        parent_metrics = parent_entry.metrics
        candidate_records: list[dict[str, Any]] = []
        invalid_attempts: list[dict[str, Any]] = []
        attempts = 0
        while len(candidate_records) < mutation_count and attempts < candidate_retry_limit:
            attempts += 1
            operator = rng.choice(STRUCTURAL_OPERATORS)
            op_name = _operator_name(operator)
            try:
                candidate = mutate_and_validate(parent_skill, operator=operator, rng=rng, min_phases=min_phases)
            except Exception as exc:
                if not _is_no_valid_mutant_error(exc):
                    raise
                invalid_attempts.append({'attempt': attempts, 'operator': op_name, 'error': str(exc)})
                continue
            raw_yaml = dump_skill(candidate)
            (candidate, fallbacks) = sanitize_subtasks(candidate, task_spec)
            candidate_index = len(candidate_records)
            (record, _) = _evaluate_skill(skill=candidate, parent_skill=parent_skill, parent_metrics=parent_metrics, generation=iteration, label=f'iter_{iteration}' if mutation_count == 1 else f'iter_{iteration}_candidate_{candidate_index}', task_name=task_name, task_spec=task_spec, backend=backend, rng=rng, cma_budget=cma_budget, n_samples=n_samples, k_basin=k_basin, lambda_penalty=lambda_penalty, subtask_mode=subtask_mode, proposal_source='mapqds_uniform_structural', operator_name=op_name, candidate_index=candidate_index, sanitizer_fallbacks=fallbacks, raw_skill_yaml=raw_yaml, randomized_config_bank=randomized_config_bank, archive=archive)
            candidate_records.append(record)
        winner = _select_iteration_winner(candidate_records)
        best_entry = archive.best()
        if best_entry is None:
            raise RuntimeError('MAP-QD archive unexpectedly empty after generation 0')
        candidate_shortfall = max(0, mutation_count - len(candidate_records))
        candidate_shortfall_total += candidate_shortfall
        if winner is None:
            best_params = best_entry.metadata.get('best_params')
            cma_diagnostics = best_entry.metadata.get('cma_diagnostics', {})
            record = {'iteration': iteration, 'generation': iteration, 'label': f'iter_{iteration}_no_valid_candidates', 'skill_yaml': dump_skill(best_entry.skill), 'task_score': best_entry.metrics.task_score, 'fitness_score': best_entry.metrics.fitness_score, 'task_subscores': safe_task_subscores(best_entry.metrics.task_subscores), 'skill_parameter_optimisation_scores': cma_diagnostics, 'composite_score': best_entry.metrics.composite_score, 'termination_fidelity': best_entry.metrics.termination_fidelity, 'force_compliance': best_entry.metrics.force_compliance, 'complexity_penalty': best_entry.metrics.complexity_penalty, **_score_logging_fields(best_entry.metrics, cma_diagnostics=cma_diagnostics), 'best_params': best_params, 'descriptor': list(best_entry.descriptor), 'mutation_count': mutation_count, 'candidate_records': [], 'invalid_attempts': invalid_attempts, 'valid_candidate_count': 0, 'candidate_shortfall': candidate_shortfall, 'parent_descriptor': list(parent_entry.descriptor), 'no_valid_candidates': True, 'evaluated_candidate': False, 'effective_cma_evaluations': 0, 'reasoning_trace': {'proposer': 'MAPQDSArchive+uniform_structural_operator', 'iteration': iteration, 'note': 'no valid candidates generated; current archive best recorded without extra CMA'}, 'wall_time_s': time.time() - iter_start, **_archive_fields(archive)}
            run_log.append(_json_safe(record))
        else:
            candidate_summaries = [_candidate_summary(r, archive=archive) for r in candidate_records]
            archive_fields = _archive_fields(archive)
            for candidate_record in candidate_records:
                top_level_record = dict(candidate_record)
                top_level_record.update({'iteration': iteration, 'generation': iteration, 'mutation_count': mutation_count, 'candidate_records': candidate_summaries, 'invalid_attempts': invalid_attempts, 'valid_candidate_count': len(candidate_records), 'candidate_shortfall': candidate_shortfall, 'parent_descriptor': list(parent_entry.descriptor), 'no_valid_candidates': False, 'evaluated_candidate': True, 'is_iteration_winner': candidate_record is winner, 'archive_best_descriptor': list(best_entry.descriptor), **archive_fields})
                run_log.append(_json_safe(top_level_record))
            evaluated_candidate_count += len(candidate_records)
        print(f'[seed {seed}][iter {iteration:2d}/{n_iterations}] valid={len(candidate_records)}/{mutation_count} archive={archive.size()} best_task={best_entry.metrics.task_score:.4f}', flush=True)
        _write_progress_status(out_path, task=task_name, seed=seed, iteration=iteration, stage='done', label=f'iter_{iteration}', wall_time_s=round(time.time() - iter_start, 2), valid_candidate_count=len(candidate_records), mutation_count=mutation_count, archive_size=archive.size(), best_task_score=best_entry.metrics.task_score)
    for record in run_log:
        record['configuration_bank_sha256'] = randomized_config_bank.sha256
    (out_path / 'run_log.json').write_text(json.dumps(run_log, indent=2) + '\n', encoding='utf-8')
    best_overall = archive.best()
    if best_overall is None:
        raise RuntimeError('MAP-QD archive unexpectedly empty at save time')
    best_yaml = dump_skill(best_overall.skill)
    (out_path / 'best_skill.yaml').write_text(best_yaml, encoding='utf-8')
    (out_path / 'archive.json').write_text(json.dumps(archive.to_records(), indent=2) + '\n', encoding='utf-8')
    (out_path / 'archive.jsonl').write_text(''.join((json.dumps(record) + '\n' for record in archive.to_records())), encoding='utf-8')
    best_task_idx = max(range(len(run_log)), key=lambda idx: run_log[idx].get('canonical_task_score', run_log[idx]['task_score']))
    best_comp_idx = max(range(len(run_log)), key=lambda idx: run_log[idx]['composite_score'])
    summary = {'task': task_name, 'method': method, 'init_mode': effective_init_mode, 'initial_skill_path': initial_skill_path, 'initial_skill_source': initial_source, 'subtask_mode': subtask_mode, 'backend_name': backend_name, 'seed': seed, 'n_iterations': n_iterations, 'cma_budget': cma_budget, 'k_basin': k_basin, 'n_samples_per_eval': n_samples, 'lambda_penalty': lambda_penalty, 'mutation_count': mutation_count, 'candidate_retry_limit': candidate_retry_limit, 'candidate_workers': candidate_workers, 'requested_candidate_count': n_iterations * mutation_count, 'evaluated_candidate_count': evaluated_candidate_count, 'initial_evaluation_count': 1, 'effective_cma_evaluations': 1 + evaluated_candidate_count, 'candidate_shortfall_total': candidate_shortfall_total, 'archive_size': archive.size(), 'archive_coverage': archive.coverage(), 'best_iteration': run_log[best_task_idx]['iteration'], 'best_task_score': run_log[best_task_idx].get('canonical_task_score', run_log[best_task_idx]['task_score']), 'best_composite_score': run_log[best_comp_idx]['composite_score'], 'total_wall_time_s': round(sum((e.get('wall_time_s', 0.0) for e in run_log)), 2)}
    (out_path / 'summary.json').write_text(json.dumps(_json_safe(summary), indent=2) + '\n', encoding='utf-8')
    return _json_safe(summary)

def main(argv: Sequence[str] | None=None) -> None:
    args = _parse_args(argv)
    task_name = args.task
    run_cfg = TASK_CONFIGS.get(task_name, {}).get('run_config', {})
    n_iterations = args.n_iters if args.n_iters is not None else run_cfg.get('n_iterations', 15)
    cma_budget = args.cma_budget if args.cma_budget is not None else run_cfg.get('cma_budget', 200)
    k_basin = args.k_basin if args.k_basin is not None else run_cfg.get('k_basin', 3)
    seeds = args.seeds if args.seeds is not None else [0, 1, 2, 3, 4]
    out_dir_base = _resolve_output_dir(args.out_dir, task_name)
    max_workers = min(len(seeds), max(1, (os.cpu_count() or 2) // 2))
    print(f'[main] task={task_name} n_iterations={n_iterations} cma_budget={cma_budget} k_basin={k_basin} mutation_count={args.mutation_count} seeds={seeds}')
    failures = 0
    with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers) as executor:
        future_to_seed = {executor.submit(run_one_seed, seed=seed, task_name=task_name, n_iterations=n_iterations, cma_budget=cma_budget, n_samples=args.n_samples, out_dir=out_dir_base / f'{task_name}_seed{seed}', k_basin=k_basin, init_mode=args.init_mode, initial_skill_path=args.initial_skill, mutation_count=args.mutation_count, candidate_retry_limit=args.candidate_retry_limit, candidate_workers=args.candidate_workers, subtask_mode=args.subtask_mode): seed for seed in seeds}
        for future in concurrent.futures.as_completed(future_to_seed):
            seed = future_to_seed[future]
            try:
                summary = future.result()
                print(f"[main] seed {seed} done -- composite={summary['best_composite_score']:.4f} task_score={summary['best_task_score']:.4f}")
            except Exception as exc:
                print(f'[main] seed {seed} FAILED: {exc}')
                failures += 1
    if failures:
        raise SystemExit(1)
if __name__ == '__main__':
    main()
