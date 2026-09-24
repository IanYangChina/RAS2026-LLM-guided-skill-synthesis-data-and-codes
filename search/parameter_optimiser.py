from __future__ import annotations
from dataclasses import replace as _dc_replace
from typing import Any
import numpy as np
from simulation.backend import SimulatorBackend
from evaluation.runner import run_evaluation
from evaluation.metrics import DesignMetrics, compute_lipschitz_from_pairs, compute_metrics, split_optimiser_posthoc_diagnostics
from simulation.realized_scene import RealizedSceneConfigBank, activate_realized_scene_configuration

class _SkillProxy:
    __slots__ = ('param_dim', 'phases')

    def __init__(self, n_params: int, n_phases: int=0) -> None:
        self.param_dim: int = n_params
        self.phases: list = [None] * n_phases

def _to_physical(normalised: np.ndarray, ranges: dict[str, tuple[float, float]], param_names: list[str]) -> dict[str, float]:
    clipped = np.clip(normalised, -1.0, 1.0)
    result: dict[str, float] = {}
    for (i, name) in enumerate(param_names):
        (lo, hi) = ranges[name]
        result[name] = float(lo + (clipped[i] + 1.0) / 2.0 * (hi - lo))
    return result

def _to_normalised(physical: dict[str, float], ranges: dict[str, tuple[float, float]], param_names: list[str]) -> np.ndarray:
    result = np.zeros(len(param_names), dtype=float)
    for (i, name) in enumerate(param_names):
        (lo, hi) = ranges[name]
        span = hi - lo
        if span == 0.0:
            result[i] = 0.0
        else:
            result[i] = 2.0 * (physical[name] - lo) / span - 1.0
    return result

def _jsonable(value: Any) -> Any:
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, dict):
        return {str(k): _jsonable(v) for (k, v) in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(v) for v in value]
    return value

def _mean_supported_mapping(run_metrics: list[DesignMetrics], attribute: str) -> dict[str, float | str | None]:
    mappings = [getattr(metrics, attribute) for metrics in run_metrics]
    keys = sorted({key for mapping in mappings for key in mapping})
    aggregated: dict[str, float | str | None] = {}
    for key in keys:
        values = [mapping.get(key) for mapping in mappings]
        if all((value is None for value in values)):
            aggregated[key] = None
        elif all((isinstance(value, (int, float, np.number)) and (not isinstance(value, bool)) for value in values)):
            aggregated[key] = float(np.mean(values))
        elif all((value == values[0] for value in values)):
            aggregated[key] = values[0]
        else:
            aggregated[key] = None
    return aggregated

def _budget_accounting(requested_budget: int, run_diagnostics: list[dict[str, Any]]) -> dict[str, Any]:
    basin_runs = [{'run_index': int(run['run_index']), 'allocated_candidate_evaluations': int(run['allocated_candidate_evaluations']), 'consumed_candidate_evaluations': int(run['consumed_candidate_evaluations']), 'stop_reason': str(run['stop_reason'])} for run in run_diagnostics]
    allocated = sum((run['allocated_candidate_evaluations'] for run in basin_runs))
    consumed = sum((run['consumed_candidate_evaluations'] for run in basin_runs))
    return {'requested_candidate_evaluations': int(requested_budget), 'allocated_candidate_evaluations': int(allocated), 'consumed_candidate_evaluations': int(consumed), 'unallocated_candidate_evaluations': max(0, int(requested_budget) - allocated), 'unconsumed_allocated_candidate_evaluations': allocated - consumed, 'basin_runs': basin_runs}

def _snapshot_randomised_state(backend: SimulatorBackend) -> dict[str, Any]:
    state: dict[str, Any] = {}
    for attr in ('_rand_frozen_body_deltas', '_rand_frozen_qpos_delta'):
        if hasattr(backend, attr):
            state[attr.removeprefix('_rand_')] = _jsonable(getattr(backend, attr))
    if hasattr(backend, '_rand_scene_frozen'):
        state['scene_frozen'] = bool(getattr(backend, '_rand_scene_frozen'))
    return state
_REPRESENTATIVE_TASK_STATE_KEYS: tuple[str, ...] = ('object_initial_position', 'object_initial_pose', 'actual_object_initial_position', 'goal_position', 'goal_object_position', 'actual_goal_position', 'actual_goal_object_position', 'place_goal_position', 'actual_place_goal_position', 'fixture_position', 'actual_fixture_position', 'socket_position', 'initial_hinge_angle', 'hinge_angle_initial', 'hinge_initial_angle', 'hinge_angle', 'final_hinge_angle', 'realised_initial_hinge_angle')

def _semantic_randomised_result(metrics: DesignMetrics, raw_backend_state: dict[str, Any]) -> dict[str, Any]:
    episode_states = [_jsonable(state) for state in getattr(metrics, 'episode_task_state', []) if isinstance(state, dict)]
    representative: dict[str, Any] = {}
    randomised_state = getattr(metrics, 'randomised_task_state', {})
    if isinstance(randomised_state, dict):
        representative.update(_jsonable(randomised_state))
    if episode_states:
        representative.update(episode_states[0])
    semantic_state = dict(representative)
    for state in [representative, *episode_states]:
        if not isinstance(state, dict):
            continue
        for key in _REPRESENTATIVE_TASK_STATE_KEYS:
            if key in state and key not in semantic_state:
                semantic_state[key] = state[key]
    return {'randomised_task_state': dict(semantic_state), 'episode_task_state': episode_states, 'representative_task_state': dict(semantic_state), 'randomisation_debug': _jsonable(raw_backend_state)}

def _freeze_new_randomised_config(backend: SimulatorBackend, seed: int) -> dict[str, Any]:
    if not hasattr(backend, 'freeze_scene_randomisation'):
        return {}
    if hasattr(backend, '_rand_config') and getattr(backend, '_rand_config', None) is not None:
        setattr(backend, '_rand_rng', np.random.default_rng(int(seed) % 2 ** 32))
    for attr in ('_rand_frozen_body_deltas', '_rand_frozen_qpos_delta'):
        if hasattr(backend, attr):
            try:
                delattr(backend, attr)
            except AttributeError:
                pass
    try:
        backend.unfreeze_scene_randomisation()
        backend.freeze_scene_randomisation()
    except Exception:
        return {}
    return _snapshot_randomised_state(backend)

def optimise_parameters(artifact, backend: SimulatorBackend, task_spec=None, sigma0: float=0.3, budget: int=20, n_samples_per_eval: int=4, seed: int=42, lambda_penalty: float=0.05, task_name: str | None=None, K_basin_runs: int=1, randomized_config_bank: RealizedSceneConfigBank | None=None) -> tuple[DesignMetrics, dict[str, float], dict]:
    import cma
    param_names: list[str] = list(artifact.parameter_names)
    ranges: dict[str, tuple[float, float]] = artifact.parameter_ranges
    d = len(param_names)
    _n_phases_actual: int = len(artifact.phases) if hasattr(artifact, 'phases') else 0
    _K = max(1, int(K_basin_runs))
    _per_run_budget = max(1, budget // _K)
    if randomized_config_bank is not None:
        if len(randomized_config_bank.configurations) != _K:
            raise ValueError('randomized configuration bank size must equal K_basin_runs')
        if task_name is not None and randomized_config_bank.task_name != task_name:
            raise ValueError('randomized configuration bank task mismatch')

    def _activate_run_configuration(k: int, run_seed: int) -> tuple[dict[str, Any], dict[str, Any]]:
        if randomized_config_bank is None:
            return (_freeze_new_randomised_config(backend, run_seed), {})
        configuration = randomized_config_bank.configurations[k]
        activate_realized_scene_configuration(backend, configuration)
        return (configuration.backend_state, {'configuration_index': configuration.config_index, 'configuration_seed': configuration.seed, 'configuration_sha256': configuration.sha256, 'realized_scene_sha256': configuration.snapshot.sha256, 'realized_scene': configuration.snapshot.to_dict(), 'configuration_bank_sha256': randomized_config_bank.sha256})
    if d == 0:
        proxy = _SkillProxy(0, n_phases=_n_phases_actual)
        run_metrics: list[DesignMetrics] = []
        randomised_config_results: list[dict[str, Any]] = []
        for k in range(_K):
            run_seed_k = int(seed) + k
            (frozen_state, configuration_fields) = _activate_run_configuration(k, run_seed_k)
            traces = run_evaluation(artifact, backend, n_samples=n_samples_per_eval, seed=run_seed_k, task_spec=task_spec)
            m = compute_metrics(traces, proxy, lambda_penalty=lambda_penalty, task_spec=task_spec, task_name=task_name, K_basin_runs=_K)
            run_metrics.append(m)
            semantic_state = _semantic_randomised_result(m, frozen_state)
            randomised_config_results.append({'run_index': k, 'seed': run_seed_k, **configuration_fields, **semantic_state, 'best_task_score': m.task_score, 'best_fitness_score': m.fitness_score, 'best_composite_score': m.composite_score, 'best_params': {}, 'allocated_candidate_evaluations': _per_run_budget, 'consumed_candidate_evaluations': 1, 'stop_reason': 'no_parameters'})
        metrics = run_metrics[0]
        budget_accounting = _budget_accounting(budget, randomised_config_results)
        zero_param_posthoc = {'randomised_config_count': _K, 'randomised_config_results': randomised_config_results, **({'configuration_bank_sha256': randomized_config_bank.sha256} if randomized_config_bank is not None else {})}
        if _K > 1:
            mean_task = float(np.mean([m.task_score for m in run_metrics]))
            mean_fitness = float(np.mean([m.fitness_score for m in run_metrics]))
            mean_term = float(np.mean([m.termination_fidelity for m in run_metrics]))
            mean_force = float(np.mean([m.force_compliance if m.force_compliance is not None else 0.0 for m in run_metrics]))
            zero_param_optimiser = {**metrics.skill_parameter_optimisation_scores, 'K_basin_runs': float(_K), 'randomised_config_count': float(_K)}
            metrics = _dc_replace(metrics, task_score=mean_task, fitness_score=mean_fitness, termination_fidelity=mean_term, force_compliance=mean_force, composite_score=mean_fitness + mean_term - metrics.complexity_penalty, task_subscores=_mean_supported_mapping(run_metrics, 'task_subscores'), task_score_components=_mean_supported_mapping(run_metrics, 'task_score_components'), optimiser_fitness_components=_mean_supported_mapping(run_metrics, 'optimiser_fitness_components'), safety_diagnostics=_mean_supported_mapping(run_metrics, 'safety_diagnostics'), termination_diagnostics=_mean_supported_mapping(run_metrics, 'termination_diagnostics'), skill_parameter_optimisation_scores=zero_param_optimiser, optimiser_diagnostics=zero_param_optimiser, posthoc_diagnostics=zero_param_posthoc)
        else:
            metrics = _dc_replace(metrics, posthoc_diagnostics=zero_param_posthoc)
        empty_diagnostics = {'best_score': metrics.composite_score, 'best_fitness_score': metrics.fitness_score, 'best_task_score': metrics.task_score, 'canonical_task_score': metrics.task_score, 'search_fitness_score': metrics.fitness_score, 'median_score': float(np.median([run_metric.composite_score for run_metric in run_metrics])), 'k_run_variance': float(np.var([run_metric.composite_score for run_metric in run_metrics])), 'stagnated': False, 'stop_reason': 'no_parameters', 'n_generations_mean': 0.0, 'params_at_lower_bound': [], 'params_at_upper_bound': [], 'final_sigma_mean': 0.0, 'randomised_config_count': _K, 'posthoc_diagnostics': zero_param_posthoc, 'robust_task_score': metrics.task_score, 'robust_fitness_score': metrics.fitness_score, 'robust_composite_score': metrics.composite_score, 'budget_accounting': budget_accounting}
        zero_param_optimiser = {**dict(metrics.skill_parameter_optimisation_scores), **{key: value for (key, value) in empty_diagnostics.items() if key != 'posthoc_diagnostics'}}
        metrics = _dc_replace(metrics, skill_parameter_optimisation_scores=zero_param_optimiser, optimiser_diagnostics=zero_param_optimiser)
        return (metrics, {}, empty_diagnostics)
    proxy = _SkillProxy(d, n_phases=_n_phases_actual)
    _expr_threshold: float = float(task_spec.expressivity_threshold) if task_spec is not None and hasattr(task_spec, 'expressivity_threshold') else 0.3

    def _single_cma_run(run_seed: int, run_budget: int, frozen_state: dict[str, Any], base_iteration: int=0, total_iters: int=50) -> tuple[DesignMetrics | None, dict[str, float], float, dict]:
        default_popsize = 4 + int(3 * np.log(max(d, 1)))
        _popsize = max(2, min(default_popsize, run_budget))
        _x0_rng = np.random.default_rng(run_seed)
        x0 = _x0_rng.uniform(-sigma0 * 0.3, sigma0 * 0.3, d)
        opts = cma.CMAOptions()
        opts.set({'bounds': [[-1.0] * d, [1.0] * d], 'seed': int(run_seed % 2 ** 32), 'verbose': -9, 'popsize': _popsize, 'tolfun': 1e-06, 'tolx': 1e-06})
        es = cma.CMAEvolutionStrategy(x0, sigma0, opts)
        _best_metrics: DesignMetrics | None = None
        _best_params: dict[str, float] = {}
        _best_score: float = float('-inf')
        _best_fitness_score: float = float('-inf')
        _eval_count: int = 0
        _eval_history: list[tuple[dict[str, float], float]] = []
        _loop_stop_reason: str | None = None
        while not es.stop() and _eval_count < run_budget:
            solutions = es.ask()
            fitnesses: list[float] = []
            for x in solutions:
                if _eval_count >= run_budget:
                    fitnesses.append(-_best_score if _best_score != float('-inf') else 0.0)
                    continue
                x_clipped = np.clip(x, -1.0, 1.0)
                physical = _to_physical(x_clipped, ranges, param_names)
                traces = [backend.run_episode(artifact, physical, None, task_spec) for _ in range(n_samples_per_eval)]
                m = compute_metrics(traces, proxy, lambda_penalty=lambda_penalty, task_spec=task_spec, task_name=task_name, K_basin_runs=_K, current_iteration=base_iteration + _eval_count, total_iterations=total_iters)
                _eval_count += 1
                sc = m.fitness_score
                _eval_history.append((dict(physical), m.task_score))
                if sc > _best_score:
                    _best_score = sc
                    _best_metrics = m
                    _best_params = dict(physical)
                if m.fitness_score > _best_fitness_score:
                    _best_fitness_score = m.fitness_score
                fitnesses.append(-sc)
            try:
                es.tell(solutions, fitnesses)
            except ValueError:
                _loop_stop_reason = 'tell_error'
                break
        if _eval_count < 2 * _popsize and _eval_count < run_budget:
            extra_solutions = es.ask()
            extra_fitnesses: list[float] = []
            for x in extra_solutions:
                if _eval_count >= run_budget:
                    extra_fitnesses.append(-_best_score if _best_score != float('-inf') else 0.0)
                    continue
                x_clipped = np.clip(x, -1.0, 1.0)
                physical = _to_physical(x_clipped, ranges, param_names)
                traces = [backend.run_episode(artifact, physical, None, task_spec) for _ in range(n_samples_per_eval)]
                m = compute_metrics(traces, proxy, lambda_penalty=lambda_penalty, task_spec=task_spec, task_name=task_name, K_basin_runs=_K, current_iteration=base_iteration + _eval_count, total_iterations=total_iters)
                _eval_count += 1
                sc = m.fitness_score
                _eval_history.append((dict(physical), m.task_score))
                if sc > _best_score:
                    _best_score = sc
                    _best_metrics = m
                    _best_params = dict(physical)
                if m.fitness_score > _best_fitness_score:
                    _best_fitness_score = m.fitness_score
                extra_fitnesses.append(-sc)
            try:
                es.tell(extra_solutions, extra_fitnesses)
            except ValueError:
                if _eval_count < run_budget:
                    _loop_stop_reason = 'tell_error'
        if _best_metrics is None:
            traces = [backend.run_episode(artifact, _to_physical(x0, ranges, param_names), None, task_spec) for _ in range(n_samples_per_eval)]
            _best_metrics = compute_metrics(traces, proxy, lambda_penalty=lambda_penalty, task_spec=task_spec, task_name=task_name, K_basin_runs=_K, current_iteration=base_iteration + _eval_count, total_iterations=total_iters)
            _best_params = _to_physical(x0, ranges, param_names)
            _best_score = _best_metrics.fitness_score
            _best_fitness_score = _best_metrics.fitness_score
            _eval_count += 1
        lip_val = compute_lipschitz_from_pairs(_eval_history)
        if lip_val is not None:
            from dataclasses import replace as _dc_replace_inner
            _new_spo = dict(_best_metrics.skill_parameter_optimisation_scores)
            _new_spo['landscape_smoothness'] = lip_val
            _best_metrics = _dc_replace_inner(_best_metrics, skill_parameter_optimisation_scores=_new_spo)
        final_sigma = float(es.sigma)
        n_generations = int(es.result.iterations)
        stop_dict = es.stop()
        if _eval_count >= run_budget:
            stop_reason = 'budget_exhausted'
        elif stop_dict:
            stop_reason = list(stop_dict.keys())[0]
        else:
            stop_reason = _loop_stop_reason or 'completed'
        stagnated = stop_reason in {'tolfun', 'tolx', 'tolxup', 'tolupsigma', 'conditioncov'}
        best_x_norm = _to_normalised(_best_params, ranges, param_names)
        params_at_lower_bound: list[str] = []
        params_at_upper_bound: list[str] = []
        for (i, pname) in enumerate(param_names):
            if best_x_norm[i] < -1.0 + 0.0001:
                params_at_lower_bound.append(pname)
            if best_x_norm[i] > 1.0 - 0.0001:
                params_at_upper_bound.append(pname)
        run_diagnostics = {'best_score': float(_best_metrics.composite_score), 'best_fitness_score': float(_best_fitness_score), 'best_task_score': float(_best_metrics.task_score), 'final_sigma': final_sigma, 'stop_reason': stop_reason, 'n_generations': n_generations, 'stagnated': stagnated, 'allocated_candidate_evaluations': run_budget, 'consumed_candidate_evaluations': _eval_count, 'params_at_lower_bound': params_at_lower_bound, 'params_at_upper_bound': params_at_upper_bound, 'optimisation_signal_source': getattr(_best_metrics, 'optimisation_signal_source', 'fixed_subtasks'), **_semantic_randomised_result(_best_metrics, frozen_state)}
        return (_best_metrics, _best_params, _best_metrics.composite_score, run_diagnostics)
    run_results: list[tuple[DesignMetrics, dict[str, float], float, dict]] = []
    for k in range(_K):
        run_seed_k = int(seed) + k
        (frozen_state_k, configuration_fields) = _activate_run_configuration(k, run_seed_k)
        _base_iter = k * (budget // _K)
        (rm, rp, rs, rd) = _single_cma_run(run_seed_k, _per_run_budget, frozen_state_k, base_iteration=_base_iter, total_iters=budget)
        rd['run_index'] = k
        rd['seed'] = run_seed_k
        rd.update(configuration_fields)
        rd['best_params'] = dict(rp)
        run_results.append((rm, rp, rs, rd))
    best_run_idx = max(range(_K), key=lambda i: run_results[i][2])
    (best_metrics, best_params, best_score, _) = run_results[best_run_idx]
    all_run_scores = [rs for (_, _, rs, _) in run_results]
    all_diagnostics = [rd for (_, _, _, rd) in run_results]
    budget_accounting = _budget_accounting(budget, all_diagnostics)
    best_score_overall = max(all_run_scores)
    best_fitness_score_overall = max((rd.get('best_fitness_score', float('-inf')) for rd in all_diagnostics))
    best_task_score_overall = max((rd.get('best_task_score', float('-inf')) for rd in all_diagnostics))
    median_score = float(np.median(all_run_scores))
    k_run_variance = float(np.var(all_run_scores))
    stop_reasons = [rd['stop_reason'] for rd in all_diagnostics]
    from collections import Counter
    stop_reason_counts = Counter(stop_reasons)
    most_common_stop_reason = stop_reason_counts.most_common(1)[0][0]
    n_stagnated = sum((1 for rd in all_diagnostics if rd['stagnated']))
    majority_stagnated = n_stagnated > _K / 2
    mean_final_sigma = float(np.mean([rd['final_sigma'] for rd in all_diagnostics]))
    mean_n_generations = float(np.mean([rd['n_generations'] for rd in all_diagnostics]))
    params_at_lower = list(set((pname for rd in all_diagnostics for pname in rd['params_at_lower_bound'])))
    params_at_upper = list(set((pname for rd in all_diagnostics for pname in rd['params_at_upper_bound'])))
    randomised_config_results = [{'run_index': rd.get('run_index'), 'seed': rd.get('seed'), 'configuration_index': rd.get('configuration_index', rd.get('run_index')), 'configuration_seed': rd.get('configuration_seed', rd.get('seed')), 'configuration_sha256': rd.get('configuration_sha256'), 'realized_scene_sha256': rd.get('realized_scene_sha256'), 'realized_scene': rd.get('realized_scene'), 'configuration_bank_sha256': rd.get('configuration_bank_sha256'), 'randomised_task_state': rd.get('randomised_task_state', {}), 'episode_task_state': rd.get('episode_task_state', []), 'representative_task_state': rd.get('representative_task_state', {}), 'randomisation_debug': rd.get('randomisation_debug', {}), 'best_task_score': rd.get('best_task_score'), 'best_fitness_score': rd.get('best_fitness_score'), 'best_composite_score': rd.get('best_score'), 'best_params': rd.get('best_params', {}), 'stop_reason': rd.get('stop_reason'), 'stagnated': rd.get('stagnated'), 'allocated_candidate_evaluations': rd.get('allocated_candidate_evaluations'), 'consumed_candidate_evaluations': rd.get('consumed_candidate_evaluations')} for rd in all_diagnostics]
    posthoc_diagnostics = {'randomised_config_count': _K, 'randomised_config_results': randomised_config_results, **({'configuration_bank_sha256': randomized_config_bank.sha256} if randomized_config_bank is not None else {})}
    cma_diagnostics = {'best_score': best_score_overall, 'best_fitness_score': best_fitness_score_overall, 'best_task_score': best_task_score_overall, 'canonical_task_score': best_task_score_overall, 'search_fitness_score': best_fitness_score_overall, 'median_score': median_score, 'k_run_variance': k_run_variance, 'stagnated': majority_stagnated, 'stop_reason': most_common_stop_reason, 'n_generations_mean': mean_n_generations, 'params_at_lower_bound': params_at_lower, 'params_at_upper_bound': params_at_upper, 'final_sigma_mean': mean_final_sigma, 'optimisation_signal_source': getattr(best_metrics, 'optimisation_signal_source', 'fixed_subtasks'), 'randomised_config_count': _K, 'budget_accounting': budget_accounting, 'posthoc_diagnostics': posthoc_diagnostics}
    if _K > 1:
        n_converging = sum((1 for (m, _, _, _) in run_results if m.task_subscores.get('raw_task_score', m.task_score) > _expr_threshold))
        basin_fraction = float(n_converging) / float(_K)
        raw_task_score = float(np.mean([m.task_subscores.get('raw_task_score', m.task_score) for (m, _, _, _) in run_results]))
        mean_fitness_score = float(np.mean([m.fitness_score for (m, _, _, _) in run_results]))
        _bm = best_metrics
        mean_termination_fidelity = float(np.mean([m.termination_fidelity for (m, _, _, _) in run_results]))
        mean_force_compliance = float(np.mean([m.force_compliance if m.force_compliance is not None else 0.0 for (m, _, _, _) in run_results]))
        new_composite = mean_fitness_score + mean_termination_fidelity - _bm.complexity_penalty
        cma_diagnostics.update({'canonical_task_score': raw_task_score, 'search_fitness_score': mean_fitness_score, 'robust_task_score': raw_task_score, 'robust_fitness_score': mean_fitness_score, 'robust_composite_score': new_composite, 'aggregation': 'mean_of_config_specific_optimized_outcomes', 'configuration_count': _K})
        _new_sub = _mean_supported_mapping([result[0] for result in run_results], 'task_subscores')
        (_cma_opt, _cma_posthoc) = split_optimiser_posthoc_diagnostics(cma_diagnostics)
        _new_cma_diag = {**dict(_bm.skill_parameter_optimisation_scores), **_cma_opt}
        _new_cma_diag['basin_fraction'] = basin_fraction
        _new_cma_diag['optimisability_B'] = basin_fraction
        _new_cma_diag['raw_cma_task_score'] = _bm.task_score
        _new_cma_diag['K_basin_runs'] = float(_K)
        _new_cma_diag['n_converging_runs'] = float(n_converging)
        _new_cma_diag['expressivity_threshold'] = _expr_threshold
        _new_cma_diag['mean_termination_fidelity'] = mean_termination_fidelity
        _new_cma_diag['mean_force_compliance'] = mean_force_compliance
        _new_cma_diag['randomised_config_count'] = float(_K)
        _new_posthoc = {**dict(getattr(_bm, 'posthoc_diagnostics', {})), **_cma_posthoc}
        for k in ['basin_fraction', 'optimisability_B', 'raw_cma_expressivity', 'K_basin_runs', 'n_converging_runs', 'expressivity_threshold', 'mean_smoothness', 'landscape_smoothness']:
            _new_sub.pop(k, None)
        best_metrics = _dc_replace(_bm, task_score=raw_task_score, fitness_score=mean_fitness_score, termination_fidelity=mean_termination_fidelity, composite_score=new_composite, task_subscores=_new_sub, task_score_components=_mean_supported_mapping([result[0] for result in run_results], 'task_score_components'), optimiser_fitness_components=_mean_supported_mapping([result[0] for result in run_results], 'optimiser_fitness_components'), safety_diagnostics=_mean_supported_mapping([result[0] for result in run_results], 'safety_diagnostics'), termination_diagnostics=_mean_supported_mapping([result[0] for result in run_results], 'termination_diagnostics'), skill_parameter_optimisation_scores=_new_cma_diag, optimiser_diagnostics=_new_cma_diag, posthoc_diagnostics=_new_posthoc)
    else:
        cma_diagnostics.update({'robust_task_score': best_metrics.task_score, 'robust_fitness_score': best_metrics.fitness_score, 'robust_composite_score': best_metrics.composite_score, 'aggregation': 'single_config_optimized_outcome', 'configuration_count': 1})
        (_cma_opt, _cma_posthoc) = split_optimiser_posthoc_diagnostics(cma_diagnostics)
        _new_cma_diag = {**dict(best_metrics.skill_parameter_optimisation_scores), **_cma_opt}
        _new_posthoc = {**dict(getattr(best_metrics, 'posthoc_diagnostics', {})), **_cma_posthoc}
        best_metrics = _dc_replace(best_metrics, skill_parameter_optimisation_scores=_new_cma_diag, optimiser_diagnostics=_new_cma_diag, posthoc_diagnostics=_new_posthoc)
    return (best_metrics, best_params, cma_diagnostics)
