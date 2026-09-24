from __future__ import annotations
import argparse
import concurrent.futures
import json
import math
import os
import pathlib
import random
import time
import numpy as np
os.environ.setdefault('MUJOCO_GL', 'osmesa')
import sys as _sys
_sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from scripts.task_configs import TASK_CONFIGS, SIM_CONFIGS as _SIM_CONFIGS
from scripts.artifact_paths import active_experiments_dir
from compiler import compile as compile_skill
from dsl.serialiser import load_skill, dump_skill
from dsl.subtask_sanitizer import sanitize_subtasks
from dsl.validator import validate
from evaluation.metrics import compute_metrics, compute_sub_scores, safe_task_subscores, split_optimiser_posthoc_diagnostics
from evaluation.task_spec import TaskSpec
from mutation.validator import NoValidMutantError, mutate_and_validate
from mutation.operators import random_mutation
from search.archive import SkillArchive
from search.parameter_optimiser import optimise_parameters
from search.proposal_metrics import append_proposal_attempt, build_attempt_record, build_evaluated_proposal_metrics
from search.proposer import BanditProposer, RandomProposer, RoundRobinProposer, load_agent_skill
from search.structural_diff import structural_diff
from search.scaffold_init import GrammarUniformInitialiser
_PROPOSER_REGISTRY: dict[str, type] = {'bandit': BanditProposer, 'random': RandomProposer, 'round_robin': RoundRobinProposer}

def _is_no_valid_mutant_error(exc: Exception) -> bool:
    if isinstance(exc, NoValidMutantError):
        return True
    if not isinstance(exc, RuntimeError):
        return False
    message = str(exc)
    return 'mutate_and_validate: no valid mutant produced' in message or ('mutate_and_validate: min_phases=' in message and 'not satisfiable' in message)

def _score_logging_fields(metrics, *, cma_diagnostics: dict | None=None, posthoc_diagnostics: dict | None=None) -> dict:
    fields = metrics.to_dict()
    if cma_diagnostics is not None:
        (optimiser, posthoc) = split_optimiser_posthoc_diagnostics(cma_diagnostics)
        fields['skill_parameter_optimisation_scores'] = optimiser
        fields['optimiser_diagnostics'] = optimiser
        fields['posthoc_diagnostics'] = {**fields.get('posthoc_diagnostics', {}), **posthoc}
    else:
        fields['optimiser_diagnostics'] = fields.get('skill_parameter_optimisation_scores', {})
    if posthoc_diagnostics:
        fields['posthoc_diagnostics'] = {**fields.get('posthoc_diagnostics', {}), **posthoc_diagnostics}
    return fields

def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description='Hybrid experiment: agent seed structures + BanditProposer + CMA-ES.', formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--task', default='obstacle_reach', help='Public task name (default: obstacle_reach).')
    p.add_argument('--seeds-dir', default=None, help='Directory containing agent-proposed *.yaml seed files (optional).')
    p.add_argument('--n-iters', type=int, default=None, help='Number of mutation iterations. Defaults to task run_config value in task_configs.py (15 for all tasks). Supplying this flag overrides the per-task default.')
    p.add_argument('--n-samples', type=int, default=3, help='CMA-ES samples per evaluation episode (default: 3).')
    p.add_argument('--cma-budget', type=int, default=None, help='CMA-ES budget per iteration. Defaults to task run_config value in task_configs.py (200 for all tasks). Supplying this flag overrides the per-task default.')
    p.add_argument('--seeds', type=int, nargs='+', default=None, help='Explicit list of seed integers to run (default: 0 1 2 3 4). Example: --seeds 0 2 4 runs only seeds 0, 2, and 4.')
    p.add_argument('--out-dir', default=None, help="Base output directory for artifacts. Each seed's results go in <out-dir>/<task>_seed<N>/. ")
    p.add_argument('--no-structural-mutation', action='store_true', default=False, help='Disable structural mutations (parameter-only CMA-ES baseline). BanditProposer will return the skill unchanged each iteration.')
    p.add_argument('--proposer', choices=['bandit', 'random', 'round_robin'], default='bandit', help="Structural mutation proposer strategy (default: bandit). 'bandit' uses UCB1 BanditProposer with decomposed rewards; 'random' selects operators uniformly at random; 'round_robin' cycles through operators in fixed order. --no-structural-mutation is honoured only with 'bandit'.")
    p.add_argument('--k-basin', type=int, default=None, help='Number of frozen randomised CMA-ES runs/configs. Defaults to task run_config value in task_configs.py (3 for all tasks). Basin fraction is logged as a diagnostic only. When provided, overrides the per-task default.')
    p.add_argument('--plot', action='store_true', default=False, help='Generate per-seed diagnostic figures (expressivity_curve.png, subscores_heatmap.png) after each seed completes. Requires matplotlib. Default: off.')
    p.add_argument('--init-mode', choices=['expert', 'task_conditioned_random', 'grammar_uniform_random'], default='expert', dest='init_mode', help="Initialisation strategy for the starting skill. 'expert': load from tasks/seeds/<task>/seed_00.yaml. 'task_conditioned_random': use ScaffoldInitialiser to generate a grammar-valid task-conditioned random skill without LLM. 'grammar_uniform_random': use GrammarUniformInitialiser to generate a skill sampled uniformly from the full DSL grammar space (no task prior).")
    p.add_argument('--subtask-mode', choices=['fixed', 'free'], default='fixed', dest='subtask_mode', help="Subtask binding mode. 'fixed' (default): subtasks come from task_spec; phases reference them by subtask_id. 'free': LLM creates its own subtasks block; sanitizer validates against the skill's own subtask declarations.")
    p.add_argument('--initial-skill', default=None, dest='initial_skill', metavar='YAML_PATH', help='Path to a YAML skill file to use as the generation-0 starting point. When supplied, all --init-mode logic is bypassed and this skill is loaded directly.  --init-mode is silently ignored.')
    return p.parse_args()

def _resolve_output_dir(out_dir: str | None, task_name: str) -> pathlib.Path:
    return pathlib.Path(out_dir) if out_dir else active_experiments_dir() / task_name

def _run_final_episodes(artifact, best_params, backend, task_spec, n):
    traces = []
    for _ in range(n):
        trace = backend.run_episode(artifact, best_params, task_spec=task_spec)
        traces.append(trace)
    return traces

def _write_progress_status(out_dir: pathlib.Path | str, *, task: str, seed: int, iteration: int, stage: str, label: str, **extra) -> None:
    payload = {'task': task, 'seed': seed, 'iteration': iteration, 'stage': stage, 'label': label, 'timestamp': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), 'pid': os.getpid(), **extra}
    path = pathlib.Path(out_dir) / 'progress_status.json'
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_name(f'{path.name}.tmp.{os.getpid()}.{time.time_ns()}')
    try:
        tmp_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + '\n', encoding='utf-8')
        os.replace(tmp_path, path)
    except Exception:
        try:
            tmp_path.unlink(missing_ok=True)
        except OSError:
            pass
        raise
    print(f'[seed {seed}][progress] iter={iteration} stage={stage} label={label}', flush=True)

def run_one_seed(seed: int, task_name: str, n_iterations: int, cma_budget: int, n_samples: int, out_dir, no_structural_mutation: bool, seeds_dir, k_basin: int=1, proposer: str='bandit', init_mode: str='expert', subtask_mode: str='fixed', initial_skill_path: str | None=None) -> dict:
    N_FINAL_EPISODES = n_samples
    if task_name not in _SIM_CONFIGS:
        raise ValueError(f"Task '{task_name}' has no SIM_CONFIGS entry. Add it to scripts/task_configs.SIM_CONFIGS before running.")
    _sim_cfg = _SIM_CONFIGS[task_name]
    _run_cfg = TASK_CONFIGS.get(task_name, {}).get('run_config', {})
    LAMBDA_PENALTY: float = _run_cfg.get('lambda_penalty', 0.05)
    effective_cma_budget: int = cma_budget
    try:
        from simulation.mujoco_backend import MuJoCoBackend
        from simulation.scene import SceneConfig
        from simulation.realized_scene import activate_realized_scene_configuration, materialize_realized_scene_config_bank
        backend = MuJoCoBackend(SceneConfig(robot=_sim_cfg.get('robot', 'panda'), gripper=_sim_cfg['gripper'], object_xml=_sim_cfg['object_xml'], target_markers=_sim_cfg.get('target_markers', ()), tcp_markers=_sim_cfg.get('tcp_markers', ())))
        _rand_cfg = TASK_CONFIGS.get(task_name, {}).get('randomisation', {})
        if _rand_cfg.get('enabled', False):
            backend._rand_config = _rand_cfg
            backend._rand_rng = np.random.default_rng(seed)
            backend.freeze_scene_randomisation()
        backend_name = 'mujoco'
        print(f'[seed {seed}][backend] MuJoCoBackend initialised (MUJOCO_GL=osmesa)')
    except Exception as _e:
        raise RuntimeError(f'[seed {seed}] MuJoCo backend initialization failed; rerun through the public --backend mock option only for non-scientific checks') from _e
    task_spec = TaskSpec(**TASK_CONFIGS[task_name]['task_spec'])
    randomized_config_bank = materialize_realized_scene_config_bank(backend, task_name, task_spec, outer_seed=seed, k_runs=k_basin)
    out_dir = pathlib.Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / 'scene_bank.json').write_text(json.dumps(randomized_config_bank.to_dict(), indent=2, sort_keys=True), encoding='utf-8')
    proposal_attempts_path = out_dir / 'proposal_attempts.jsonl'
    rng = random.Random(seed)
    _no_mutation = no_structural_mutation
    from mutation.operators import ALL_OPERATORS
    _operators = ALL_OPERATORS[:7]
    if proposer in _PROPOSER_REGISTRY:
        if proposer == 'bandit':
            _proposer = _PROPOSER_REGISTRY[proposer](seed=seed, operators=_operators, reward_mode='decomposed', disable_mutations=_no_mutation)
            _proposer_name = 'BanditProposer(decomposed)'
            if _no_mutation:
                print(f'[seed {seed}] Running in PARAMETER-ONLY mode -- structural mutations disabled')
        else:
            _proposer = _PROPOSER_REGISTRY[proposer](seed=seed, operators=_operators)
            _proposer_name = f'{proposer.capitalize()}Proposer'
    else:
        _proposer = BanditProposer(operators=_operators, seed=seed, reward_mode='decomposed')
        _proposer_name = 'BanditProposer(decomposed)'
    bandit = _proposer
    archive = SkillArchive()
    seed_skills = []
    seed_files = []
    if seeds_dir:
        seeds_path = pathlib.Path(seeds_dir)
        yaml_files = sorted(seeds_path.glob('*.yaml'))
        if yaml_files:
            print(f'[seed {seed}][seeds] Loading {len(yaml_files)} seed YAML(s) from {seeds_path}')
            for yf in yaml_files:
                try:
                    skill = load_agent_skill(yf)
                    seed_skills.append(skill)
                    seed_files.append(str(yf))
                    print(f'  [seed {seed}][seed] loaded {yf.name}')
                except Exception as _load_err:
                    print(f'  [seed {seed}][seed] SKIP {yf.name}: {_load_err}')
        else:
            print(f'[seed {seed}][seeds] No *.yaml files found in {seeds_path}; using random seed')
    else:
        print(f'[seed {seed}][seeds] --seeds-dir not provided; using random seed (standard bandit+CMA-ES)')
    method = 'param_only_cma_es' if _no_mutation and proposer == 'bandit' else f'hybrid_agent_seed+{proposer}+cma_es' if seed_skills else f'{proposer}+cma_es'
    if initial_skill_path is not None:
        _init_label = 'supplied_skill'
        method = f'supplied_skill+param_only_cma_es' if _no_mutation and proposer == 'bandit' else f'supplied_skill+{proposer}+cma_es'
    elif init_mode == 'task_conditioned_random':
        _init_label = 'task_conditioned_random'
        method = f'task_conditioned_random+param_only_cma_es' if _no_mutation and proposer == 'bandit' else f'task_conditioned_random+{proposer}+cma_es'
    elif init_mode == 'grammar_uniform_random':
        _init_label = 'grammar_uniform_random'
        method = f'grammar_uniform_random+param_only_cma_es' if _no_mutation and proposer == 'bandit' else f'grammar_uniform_random+{proposer}+cma_es'
    else:
        _init_label = init_mode
    print(f'[seed {seed}][config] task={task_name}  method={method}  proposer={_proposer_name}  seeds={len(seed_skills)}')
    run_log = []
    preseed_skips = []
    for (seed_idx, seed_skill) in enumerate(seed_skills):
        t_seed = time.time()
        label = f'seed_{seed_idx}'
        print(f'[seed {seed}][{label}] Evaluating agent seed {seed_idx + 1}/{len(seed_skills)} ...')
        try:
            artifact_s = compile_skill(seed_skill)
            preseed_cma_seed = rng.randint(0, 2 ** 31 - 1)
            (seed_metrics, seed_params, seed_cma_diagnostics) = optimise_parameters(artifact_s, backend, task_spec, budget=effective_cma_budget, n_samples_per_eval=n_samples, seed=preseed_cma_seed, lambda_penalty=LAMBDA_PENALTY, task_name=task_name, K_basin_runs=k_basin, randomized_config_bank=randomized_config_bank)
            activate_realized_scene_configuration(backend, randomized_config_bank.configurations[0])
            final_traces_s = _run_final_episodes(artifact_s, seed_params, backend, task_spec, n=N_FINAL_EPISODES)
            sub_scores_s = compute_sub_scores(task_name=task_name, episode_results=final_traces_s, task_spec=task_spec)
            archive.add(seed_skill, seed_metrics, generation=-1)
            proposal_fields_s = build_evaluated_proposal_metrics(task=task_name, candidate_skill=seed_skill, parent_skill=None, candidate_yaml=dump_skill(seed_skill), parent_yaml=None, candidate_metrics=seed_metrics, parent_metrics=None, task_spec=task_spec, subtask_mode=subtask_mode, proposal_source='agent_seed', accepted_as_elite=True, parse_status='evaluated')
            wall_s = time.time() - t_seed
            print(f'[seed {seed}][{label}] composite={seed_metrics.composite_score:.4f}  task_score={seed_metrics.task_score:.4f}  ({wall_s:.1f}s)')
            run_log.append({'iteration': -(len(seed_skills) - seed_idx), 'generation': -1, 'label': label, 'skill_yaml': dump_skill(seed_skill), 'task_score': seed_metrics.task_score, 'fitness_score': seed_metrics.fitness_score, 'task_subscores': safe_task_subscores(seed_metrics.task_subscores), 'skill_parameter_optimisation_scores': seed_cma_diagnostics, 'composite_score': seed_metrics.composite_score, 'termination_fidelity': seed_metrics.termination_fidelity, 'force_compliance': seed_metrics.force_compliance, 'complexity_penalty': seed_metrics.complexity_penalty, **_score_logging_fields(seed_metrics, cma_diagnostics=seed_cma_diagnostics, posthoc_diagnostics={'final_replay_task_subscores': safe_task_subscores(sub_scores_s)}), 'best_params': seed_params, 'reasoning_trace': {'proposer': 'agent_seed', 'operator_stats': [], 'last_operator_applied': None, 'iteration': -(len(seed_skills) - seed_idx), 'note': f'agent-proposed seed {seed_idx + 1} (generation=-1)'}, **proposal_fields_s, 'structural_diff': {'summary': f'agent seed {seed_idx + 1} (no parent)'}, 'wall_time_s': wall_s})
        except Exception as _seed_err:
            skip_record = {'label': label, 'stage': 'preseed', 'seed_index': seed_idx, 'seed_file': seed_files[seed_idx] if seed_idx < len(seed_files) else None, 'error': str(_seed_err)}
            preseed_skips.append(skip_record)
            print(f'  [seed {seed}][seed] SKIP preseed {label}: {skip_record}')
    if initial_skill_path is not None:
        _skill_path = pathlib.Path(initial_skill_path)
        initial_skill_yaml = _skill_path.read_text()
        initial_skill = load_skill(initial_skill_yaml)
        print(f'[seed {seed}][init] supplied skill from {_skill_path}')
        _effective_init_mode = 'supplied_skill'
    elif init_mode == 'task_conditioned_random':
        from search.scaffold_init import sample_scaffold_skill
        initial_skill = sample_scaffold_skill(task_name, rng)
        print(f'[seed {seed}][init] task_conditioned_random via ScaffoldInitialiser')
        _effective_init_mode = 'task_conditioned_random'
    elif init_mode == 'grammar_uniform_random':
        initial_skill = GrammarUniformInitialiser(task_name, rng, min_phases=_sim_cfg.get('min_phases', 1)).sample()
        print(f'[seed {seed}][init] grammar_uniform_random via GrammarUniformInitialiser')
        _effective_init_mode = 'grammar_uniform_random'
    else:
        seed_path = pathlib.Path(__file__).resolve().parents[1] / 'tasks' / 'seeds' / task_name / 'seed_00.yaml'
        if not seed_path.exists():
            seed_path = pathlib.Path(__file__).resolve().parents[1] / 'tasks' / 'seeds' / task_name / 'seed_00.yaml'
        initial_skill_yaml = seed_path.read_text()
        initial_skill = load_skill(initial_skill_yaml)
        print(f'[seed {seed}][init] expert seed from {seed_path}')
        _effective_init_mode = 'expert'
    _write_progress_status(out_dir, task=task_name, seed=seed, iteration=0, stage='start', label='gen_0_baseline')
    print(f'[seed {seed}][gen 0] Evaluating initial skill ...', flush=True)
    t0 = time.time()
    (initial_skill, _fallback0) = sanitize_subtasks(initial_skill, task_spec)
    if _fallback0 > 0:
        print(f'[seed {seed}][gen 0] subtask sanitizer: {_fallback0} phase(s) repaired')
    artifact0 = compile_skill(initial_skill)
    gen0_cma_seed = rng.randint(0, 2 ** 31 - 1)
    (best_metrics0, best_params0, cma_diagnostics0) = optimise_parameters(artifact0, backend, task_spec, budget=effective_cma_budget, n_samples_per_eval=n_samples, seed=gen0_cma_seed, lambda_penalty=LAMBDA_PENALTY, task_name=task_name, K_basin_runs=k_basin, randomized_config_bank=randomized_config_bank)
    activate_realized_scene_configuration(backend, randomized_config_bank.configurations[0])
    final_traces0 = _run_final_episodes(artifact0, best_params0, backend, task_spec, n=N_FINAL_EPISODES)
    sub_scores0 = compute_sub_scores(task_name=task_name, episode_results=final_traces0, task_spec=task_spec)
    archive.add(initial_skill, best_metrics0, generation=0)
    proposal_fields0 = build_evaluated_proposal_metrics(task=task_name, candidate_skill=initial_skill, parent_skill=None, candidate_yaml=dump_skill(initial_skill), parent_yaml=None, candidate_metrics=best_metrics0, parent_metrics=None, task_spec=task_spec, subtask_mode=subtask_mode, proposal_source=_effective_init_mode, accepted_as_elite=True, parse_status='evaluated')
    wall0 = time.time() - t0
    print(f'[seed {seed}][gen 0] composite={best_metrics0.composite_score:.4f}  task_score={best_metrics0.task_score:.4f}  ({wall0:.1f}s)', flush=True)
    _write_progress_status(out_dir, task=task_name, seed=seed, iteration=0, stage='done', label='gen_0_baseline', wall_time_s=round(wall0, 2), composite_score=best_metrics0.composite_score, task_score=best_metrics0.task_score)
    run_log.append({'iteration': 0, 'generation': 0, 'label': 'gen_0_baseline', 'skill_yaml': dump_skill(initial_skill), 'task_score': best_metrics0.task_score, 'fitness_score': best_metrics0.fitness_score, 'task_subscores': safe_task_subscores(best_metrics0.task_subscores), 'skill_parameter_optimisation_scores': cma_diagnostics0, 'composite_score': best_metrics0.composite_score, 'termination_fidelity': best_metrics0.termination_fidelity, 'force_compliance': best_metrics0.force_compliance, 'complexity_penalty': best_metrics0.complexity_penalty, **_score_logging_fields(best_metrics0, cma_diagnostics=cma_diagnostics0, posthoc_diagnostics={'final_replay_task_subscores': safe_task_subscores(sub_scores0)}), 'best_params': best_params0, 'reasoning_trace': {'proposer': _proposer_name, 'operator_stats': [], 'last_operator_applied': None, 'iteration': 0, 'note': 'baseline -- no mutation applied'}, **proposal_fields0, 'structural_diff': {'summary': 'seed (no parent)'}, 'wall_time_s': wall0})
    for i in range(1, n_iterations + 1):
        t_iter = time.time()
        _write_progress_status(out_dir, task=task_name, seed=seed, iteration=i, stage='start', label=f'iter_{i}')
        best_entry = archive.best()
        parent_skill = best_entry.skill
        parent_metrics = best_entry.metrics
        parent_yaml = dump_skill(parent_skill)
        raw_candidate_yaml: str | None = None
        proposal_used_fallback = False
        proposal_fallback_reason: str | None = None
        proposal_used_parent_fallback = False
        try:
            candidate = bandit(parent_skill, parent_metrics, archive)
            raw_candidate_yaml = dump_skill(candidate)
            raw_action = bandit.last_action()
            raw_op_idx = raw_action.get('operator_idx')
            raw_op_name = ALL_OPERATORS[raw_op_idx].__name__ if raw_op_idx is not None else 'random_mutation_fallback'
            append_proposal_attempt(proposal_attempts_path, build_attempt_record(iteration=i, attempt_kind='candidate', proposal_source=proposer, task=task_name, candidate_yaml=raw_candidate_yaml, parent_skill=parent_skill, parent_yaml=parent_yaml, task_spec=task_spec, subtask_mode=subtask_mode, condition=None, accepted=None, parse_status='raw', extra={'operator': raw_op_name}))
            errors = validate(candidate)
            _min_ph = _sim_cfg.get('min_phases', 1)
            if errors or len(candidate.phases) < _min_ph:
                proposal_used_fallback = True
                if errors:
                    proposal_fallback_reason = '; '.join((str(e) for e in errors))
                else:
                    proposal_fallback_reason = f'candidate had {len(candidate.phases)} phase(s); minimum is {_min_ph}'
                try:
                    candidate = mutate_and_validate(parent_skill, operator=random_mutation, rng=rng, min_phases=_min_ph)
                except Exception as _fallback_err:
                    if not _is_no_valid_mutant_error(_fallback_err):
                        raise
                    proposal_used_parent_fallback = True
                    proposal_fallback_reason = (f'{proposal_fallback_reason}; ' if proposal_fallback_reason else '') + f'no_valid_mutant_parent_fallback: {_fallback_err}'
                    candidate = parent_skill
                    append_proposal_attempt(proposal_attempts_path, build_attempt_record(iteration=i, attempt_kind='candidate', proposal_source=proposer, task=task_name, candidate_yaml=parent_yaml, parent_skill=parent_skill, parent_yaml=parent_yaml, task_spec=task_spec, subtask_mode=subtask_mode, condition=None, accepted=None, parse_status='parent_fallback', error=str(_fallback_err), extra={'operator': 'parent_skill_fallback'}))
        except Exception as _propose_err:
            print(f'  [seed {seed}][warn] proposer error ({_propose_err}); using random mutation')
            proposal_used_fallback = True
            proposal_fallback_reason = f'proposer error: {_propose_err}'
            append_proposal_attempt(proposal_attempts_path, build_attempt_record(iteration=i, attempt_kind='candidate', proposal_source=proposer, task=task_name, candidate_yaml=raw_candidate_yaml, parent_skill=parent_skill, parent_yaml=parent_yaml, task_spec=task_spec, subtask_mode=subtask_mode, condition=None, accepted=None, parse_status='proposer_error', error=str(_propose_err), extra={'operator': 'random_mutation_fallback'}))
            try:
                candidate = mutate_and_validate(parent_skill, operator=random_mutation, rng=rng, min_phases=_sim_cfg.get('min_phases', 1))
            except Exception as _fallback_err:
                if not _is_no_valid_mutant_error(_fallback_err):
                    raise
                proposal_used_parent_fallback = True
                proposal_fallback_reason = (f'{proposal_fallback_reason}; ' if proposal_fallback_reason else '') + f'no_valid_mutant_parent_fallback: {_fallback_err}'
                candidate = parent_skill
                append_proposal_attempt(proposal_attempts_path, build_attempt_record(iteration=i, attempt_kind='candidate', proposal_source=proposer, task=task_name, candidate_yaml=parent_yaml, parent_skill=parent_skill, parent_yaml=parent_yaml, task_spec=task_spec, subtask_mode=subtask_mode, condition=None, accepted=None, parse_status='parent_fallback', error=str(_fallback_err), extra={'operator': 'parent_skill_fallback'}))
        last_action = bandit.last_action()
        op_stats_dict = bandit.stats()
        last_op_idx = last_action.get('operator_idx')
        if proposal_used_parent_fallback:
            last_op_name = 'parent_skill_fallback'
        elif last_op_idx is not None:
            from mutation.operators import ALL_OPERATORS
            last_op_name = ALL_OPERATORS[last_op_idx].__name__
        else:
            last_op_name = 'random_mutation_fallback'
        candidate_before_sanitize_yaml = dump_skill(candidate)
        (candidate, _fallback_iter) = sanitize_subtasks(candidate, task_spec)
        evaluated_candidate_yaml = dump_skill(candidate)
        if _fallback_iter > 0:
            proposal_used_fallback = True
            proposal_fallback_reason = (f'{proposal_fallback_reason}; ' if proposal_fallback_reason else '') + f'subtask sanitizer repaired {_fallback_iter} phase(s)'
        artifact = compile_skill(candidate)
        cma_seed = rng.randint(0, 2 ** 31 - 1)
        (best_metrics, best_params, cma_diagnostics) = optimise_parameters(artifact, backend, task_spec, budget=effective_cma_budget, n_samples_per_eval=n_samples, seed=cma_seed, lambda_penalty=LAMBDA_PENALTY, task_name=task_name, K_basin_runs=k_basin, randomized_config_bank=randomized_config_bank)
        activate_realized_scene_configuration(backend, randomized_config_bank.configurations[0])
        final_traces = _run_final_episodes(artifact, best_params, backend, task_spec, n=N_FINAL_EPISODES)
        sub_scores = compute_sub_scores(task_name=task_name, episode_results=final_traces, task_spec=task_spec)
        prev_best_composite = archive.best().metrics.composite_score
        archive.add(candidate, best_metrics, generation=i)
        iter_structural_diff = structural_diff(parent_skill, candidate)
        proposal_fields = build_evaluated_proposal_metrics(task=task_name, candidate_skill=candidate, parent_skill=parent_skill, candidate_yaml=evaluated_candidate_yaml, parent_yaml=parent_yaml, candidate_metrics=best_metrics, parent_metrics=parent_metrics, task_spec=task_spec, subtask_mode=subtask_mode, proposal_source=proposer, accepted_as_elite=best_metrics.composite_score >= prev_best_composite, parse_status='evaluated')
        wall_iter = time.time() - t_iter
        print(f"[seed {seed}][iter {i:2d}/{n_iterations}] composite={best_metrics.composite_score:.4f} task_score={best_metrics.task_score:.4f} op={last_op_name} diff={iter_structural_diff['summary'][:60]} ({wall_iter:.1f}s)", flush=True)
        _write_progress_status(out_dir, task=task_name, seed=seed, iteration=i, stage='done', label=f'iter_{i}', wall_time_s=round(wall_iter, 2), composite_score=best_metrics.composite_score, task_score=best_metrics.task_score, operator=last_op_name)
        run_log.append({'iteration': i, 'generation': i, 'label': f'iter_{i}', 'skill_yaml': dump_skill(candidate), 'task_score': best_metrics.task_score, 'fitness_score': best_metrics.fitness_score, 'task_subscores': safe_task_subscores(best_metrics.task_subscores), 'skill_parameter_optimisation_scores': cma_diagnostics, 'composite_score': best_metrics.composite_score, 'termination_fidelity': best_metrics.termination_fidelity, 'force_compliance': best_metrics.force_compliance, 'complexity_penalty': best_metrics.complexity_penalty, **_score_logging_fields(best_metrics, cma_diagnostics=cma_diagnostics, posthoc_diagnostics={'final_replay_task_subscores': safe_task_subscores(sub_scores)}), 'best_params': best_params, 'reasoning_trace': {'proposer': _proposer_name, 'operator_stats': op_stats_dict, 'last_operator_applied': last_op_name, 'last_action': last_action, 'iteration': i}, 'raw_proposed_skill_yaml': raw_candidate_yaml, 'evaluated_candidate_yaml': evaluated_candidate_yaml, 'proposal_used_fallback': proposal_used_fallback, 'proposal_fallback_reason': proposal_fallback_reason, 'subtask_sanitizer_fallbacks': _fallback_iter, 'proposal_candidate_changed_before_evaluation': raw_candidate_yaml is not None and raw_candidate_yaml.strip() != evaluated_candidate_yaml.strip() or candidate_before_sanitize_yaml.strip() != evaluated_candidate_yaml.strip(), **proposal_fields, 'structural_diff': iter_structural_diff, 'wall_time_s': wall_iter})
    for record in run_log:
        record['configuration_bank_sha256'] = randomized_config_bank.sha256
    with open(out_dir / 'run_log.json', 'w') as f:
        json.dump(run_log, f, indent=2)
    print(f'\n[seed {seed}][output] run_log.json written ({len(run_log)} entries)')
    best_overall = archive.best()
    best_yaml = dump_skill(best_overall.skill)
    (out_dir / 'best_skill.yaml').write_text(best_yaml)
    best_iter = next((e['iteration'] for e in run_log if e['skill_yaml'] == best_yaml), None)
    print(f'[seed {seed}][output] best_skill.yaml written (iteration={best_iter})')
    total_wall = sum((e['wall_time_s'] for e in run_log))
    best_expr_idx = max(range(len(run_log)), key=lambda idx: run_log[idx].get('canonical_task_score', run_log[idx]['task_score']))
    best_comp_idx = max(range(len(run_log)), key=lambda idx: run_log[idx]['composite_score'])
    summary = {'task': task_name, 'method': method, 'init_mode': _effective_init_mode, 'initial_skill_path': initial_skill_path, 'subtask_mode': subtask_mode, 'backend_name': backend_name, 'seed': seed, 'n_iterations': n_iterations, 'cma_budget': effective_cma_budget, 'k_basin': k_basin, 'n_samples_per_eval': n_samples, 'lambda_penalty': LAMBDA_PENALTY, 'n_seeds_loaded': len(seed_skills), 'seed_files': seed_files, 'n_preseed_skips': len(preseed_skips), 'preseed_skips': preseed_skips, 'best_iteration': run_log[best_expr_idx]['iteration'], 'best_task_score': run_log[best_expr_idx].get('canonical_task_score', run_log[best_expr_idx]['task_score']), 'best_composite_score': run_log[best_comp_idx]['composite_score'], 'total_wall_time_s': round(total_wall, 2)}
    with open(out_dir / 'summary.json', 'w') as f:
        json.dump(summary, f, indent=2)
    print(f'[seed {seed}][output] summary.json written')
    print('\n' + '=' * 60)
    print(f'  Experiment complete -- seed={seed}  {n_iterations} iters on {task_name}')
    print(f'  Method          : {method}')
    print(f'  Seeds loaded    : {len(seed_skills)}')
    print(f'  Backend         : {backend_name}')
    print(f"  Best iter       : {summary['best_iteration']}")
    print(f"  Best task score : {summary['best_task_score']:.4f}")
    print(f"  Best composite  : {summary['best_composite_score']:.4f}")
    print(f'  Total wall time : {total_wall:.1f}s')
    print(f'  Artifacts       : {out_dir}/')
    print('=' * 60)
    return summary

def main() -> None:
    args = _parse_args()
    task_name = args.task
    _run_cfg = TASK_CONFIGS.get(task_name, {}).get('run_config', {})
    if task_name not in TASK_CONFIGS:
        print(f'[warn] Task {task_name!r} not in TASK_CONFIGS; using hardcoded defaults')
    n_iterations: int = args.n_iters if args.n_iters is not None else _run_cfg.get('n_iterations', 20)
    k_basin: int = args.k_basin if args.k_basin is not None else _run_cfg.get('k_basin', 1)
    cma_budget: int = args.cma_budget if args.cma_budget is not None else _run_cfg.get('cma_budget', 25)
    seeds: list[int] = args.seeds if args.seeds is not None else [0, 1, 2, 3, 4]
    out_dir_base = _resolve_output_dir(args.out_dir, task_name)
    print(f'[main] task={task_name}  n_iterations={n_iterations}  cma_budget={cma_budget}  seeds={seeds}')
    max_workers = min(len(seeds), max(1, (os.cpu_count() or 2) // 2))
    print(f'[main] Launching {len(seeds)} seed(s) in parallel (max_workers={max_workers})')
    n_failed = 0
    with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers) as executor:
        future_to_seed = {executor.submit(run_one_seed, seed=s, task_name=task_name, n_iterations=n_iterations, cma_budget=cma_budget, n_samples=args.n_samples, out_dir=out_dir_base / f'{task_name}_seed{s}', no_structural_mutation=args.no_structural_mutation, seeds_dir=args.seeds_dir, k_basin=k_basin, proposer=args.proposer, init_mode=args.init_mode, subtask_mode=args.subtask_mode, initial_skill_path=args.initial_skill): s for s in seeds}
        for future in concurrent.futures.as_completed(future_to_seed):
            s = future_to_seed[future]
            try:
                summary = future.result()
                print(f"[main] seed {s} done -- composite={summary['best_composite_score']:.4f}  task_score={summary['best_task_score']:.4f}")
                if args.plot:
                    print('[info] plotting is intentionally not included in this runtime archive')
            except Exception as exc:
                print(f'[main] seed {s} FAILED: {exc}')
                n_failed += 1
    if n_failed:
        import sys
        sys.exit(1)
if __name__ == '__main__':
    main()
