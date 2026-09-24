from __future__ import annotations
import math
from dataclasses import dataclass, field
from typing import Any
import numpy as np
from dsl.nodes import Skill
from simulation.backend import EpisodeTrace
METRICS_SCHEMA_VERSION = 'metrics-schema-v1'
COMPOSITE_FORMULA_VERSION = 'composite-formula-v1'
POSTHOC_DIAGNOSTIC_KEYS: frozenset[str] = frozenset({'randomised_config_results', 'randomisation_debug', 'randomised_task_state', 'episode_task_state', 'representative_task_state', 'final_replay_task_subscores'})

def split_optimiser_posthoc_diagnostics(diagnostics: dict[str, Any] | None) -> tuple[dict[str, Any], dict[str, Any]]:
    optimiser: dict[str, Any] = {}
    posthoc: dict[str, Any] = {}
    if not diagnostics:
        return (optimiser, posthoc)
    for (key, value) in diagnostics.items():
        if key == 'posthoc_diagnostics' and isinstance(value, dict):
            posthoc.update(value)
        elif key in POSTHOC_DIAGNOSTIC_KEYS:
            posthoc[key] = value
        else:
            optimiser[key] = value
    return (optimiser, posthoc)

@dataclass(frozen=True)
class DesignMetrics:
    task_score: float
    termination_fidelity: float
    complexity_penalty: float
    composite_score: float
    LAMBDA: float = 0.05
    phase_completion_rate: float | None = None
    mean_phase_displacement: float | None = None
    force_compliance: float | None = None
    fitness_score: float = 0.0
    task_subscores: dict[str, float | str | None] = field(default_factory=dict, compare=False, hash=False)
    task_score_components: dict[str, float | str | None] = field(default_factory=dict, compare=False, hash=False)
    optimiser_fitness_components: dict[str, float | str | None] = field(default_factory=dict, compare=False, hash=False)
    safety_diagnostics: dict[str, float | str | None] = field(default_factory=dict, compare=False, hash=False)
    termination_diagnostics: dict[str, float | str | None] = field(default_factory=dict, compare=False, hash=False)
    randomised_task_state: dict[str, Any] = field(default_factory=dict, compare=False, hash=False)
    episode_task_state: list[dict[str, Any]] = field(default_factory=list, compare=False, hash=False)
    skill_parameter_optimisation_scores: dict[str, Any] = field(default_factory=dict, compare=False, hash=False)
    optimisation_signal_source: str = 'task_score_only'
    optimiser_diagnostics: dict[str, Any] = field(default_factory=dict, compare=False, hash=False)
    posthoc_diagnostics: dict[str, Any] = field(default_factory=dict, compare=False, hash=False)
    composite_formula_version: str = COMPOSITE_FORMULA_VERSION
    metrics_version: str = METRICS_SCHEMA_VERSION

    def to_dict(self) -> dict:
        (legacy_optimiser, legacy_posthoc) = split_optimiser_posthoc_diagnostics(self.skill_parameter_optimisation_scores)
        (explicit_optimiser, explicit_posthoc) = split_optimiser_posthoc_diagnostics(self.optimiser_diagnostics)
        optimiser_diagnostics = {**legacy_optimiser, **explicit_optimiser}
        posthoc_diagnostics = {**legacy_posthoc, **explicit_posthoc, **dict(self.posthoc_diagnostics)}
        d = {'task_score': self.task_score, 'canonical_task_score': self.task_score, 'fitness_score': self.fitness_score, 'search_fitness_score': self.fitness_score, 'termination_fidelity': self.termination_fidelity, 'force_compliance': self.force_compliance, 'complexity_penalty': self.complexity_penalty, 'composite_score': self.composite_score, 'composite_formula_version': self.composite_formula_version, 'LAMBDA': self.LAMBDA}
        for f in ('phase_completion_rate', 'mean_phase_displacement'):
            v = getattr(self, f)
            if v is not None:
                d[f] = v
        d['task_subscores'] = dict(self.task_subscores) if self.task_subscores else {}
        d['task_score_components'] = dict(self.task_score_components) if self.task_score_components else {}
        d['optimiser_fitness_components'] = dict(self.optimiser_fitness_components) if self.optimiser_fitness_components else {}
        d['safety_diagnostics'] = dict(self.safety_diagnostics) if self.safety_diagnostics else {}
        d['termination_diagnostics'] = dict(self.termination_diagnostics) if self.termination_diagnostics else {}
        d['randomised_task_state'] = dict(self.randomised_task_state) if self.randomised_task_state else {}
        d['episode_task_state'] = list(self.episode_task_state) if self.episode_task_state else []
        d['skill_parameter_optimisation_scores'] = dict(optimiser_diagnostics)
        d['optimiser_diagnostics'] = dict(optimiser_diagnostics)
        d['posthoc_diagnostics'] = dict(posthoc_diagnostics)
        d['optimisation_signal_source'] = self.optimisation_signal_source
        d['metrics_version'] = self.metrics_version
        return d
_FORCE_COMPLIANCE_FALLBACK_THRESHOLD: float = 15.0
_BASELINE_PHASES: int = 2
_LAMBDA_PHASES_START: float = 0.02
_LAMBDA_PHASES_END: float = 0.03
_PHASE_BLEND_TASKS: frozenset[str] = frozenset()
_PHASE_SCORING_TASKS: frozenset[str] = frozenset({'push_to_goal', 'peg_channel', 'grasp_place', 'peg_insert'})
_PHASE_SCORING_REQUIRED_PHASES: dict[str, frozenset[str]] = {'push_to_goal': frozenset({'approach', 'contact', 'push'}), 'peg_channel': frozenset({'approach', 'contact', 'push'}), 'grasp_place': frozenset({'descend', 'grasp', 'lift'}), 'peg_insert': frozenset({'align', 'approach', 'contact', 'insert'})}
_N_LIPSCHITZ_PAIRS: int = 30
_LIPSCHITZ_NORMALISER: float = 2.0

def _nanmean(values: list[float]) -> float | None:
    finite = [v for v in values if not v != v]
    return float(np.mean(finite)) if finite else None

def safe_task_subscores(sub: dict) -> dict:
    import math
    return {k: None if v is None or (isinstance(v, float) and (not math.isfinite(v))) else v for (k, v) in sub.items()}
safe_skill_design_scores = safe_task_subscores
safe_sub_scores = safe_task_subscores

def _lipschitz_smoothness_from_traces(per_trace_scores: list[float], traces: list[EpisodeTrace], n_pairs: int=_N_LIPSCHITZ_PAIRS) -> float:
    n = len(traces)
    if n < 2:
        return 1.0
    all_keys: list[str] | None = None
    param_matrix_rows: list[list[float]] = []
    for t in traces:
        if not t.parameter_values:
            param_matrix_rows.append([])
            continue
        keys = sorted(t.parameter_values.keys())
        if all_keys is None:
            all_keys = keys
        row = [float(t.parameter_values.get(k, 0.0)) for k in all_keys or keys]
        param_matrix_rows.append(row)
    if all_keys is None or not any(param_matrix_rows):
        return 1.0
    d = len(all_keys)
    param_arr = np.zeros((n, d), dtype=float)
    for (i, row) in enumerate(param_matrix_rows):
        if row:
            param_arr[i, :len(row)] = row[:d]
    p_min = param_arr.min(axis=0)
    p_max = param_arr.max(axis=0)
    p_range = p_max - p_min
    valid = p_range > 1e-09
    if not valid.any():
        return 1.0
    normed = np.where(valid[np.newaxis, :], (param_arr - p_min) / np.where(valid, p_range, 1.0), 0.0)
    scores = np.array(per_trace_scores, dtype=float)
    max_pairs = n * (n - 1) // 2
    if max_pairs <= n_pairs:
        pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]
    else:
        rng_lip = np.random.default_rng(0)
        seen: set[tuple[int, int]] = set()
        pairs = []
        while len(pairs) < n_pairs:
            ij = tuple(sorted(rng_lip.integers(0, n, size=2).tolist()))
            if ij[0] != ij[1] and ij not in seen:
                seen.add(ij)
                pairs.append(ij)
    lipschitz_vals: list[float] = []
    for (i, j) in pairs:
        d_theta = float(np.linalg.norm(normed[i] - normed[j]))
        if d_theta < 1e-09:
            continue
        d_score = abs(float(scores[i]) - float(scores[j]))
        lipschitz_vals.append(d_score / d_theta)
    if not lipschitz_vals:
        return 1.0
    mean_lip = float(np.mean(lipschitz_vals))
    return float(np.clip(1.0 - mean_lip / _LIPSCHITZ_NORMALISER, 0.0, 1.0))

def compute_lipschitz_from_pairs(pairs: list[tuple[dict[str, float], float]], n_pairs: int=_N_LIPSCHITZ_PAIRS) -> float | None:
    if len(pairs) < 2:
        return None
    all_keys_set: set[str] = set()
    for (param_dict, _) in pairs:
        all_keys_set.update(param_dict.keys())
    if not all_keys_set:
        return None
    all_keys = sorted(all_keys_set)
    n = len(pairs)
    d = len(all_keys)
    param_arr = np.zeros((n, d), dtype=float)
    scores = np.empty(n, dtype=float)
    for (idx, (param_dict, score)) in enumerate(pairs):
        for (k_idx, k) in enumerate(all_keys):
            param_arr[idx, k_idx] = float(param_dict.get(k, 0.0))
        scores[idx] = float(score)
    p_min = param_arr.min(axis=0)
    p_max = param_arr.max(axis=0)
    p_range = p_max - p_min
    valid = p_range > 1e-09
    if not valid.any():
        return None
    normed = np.where(valid[np.newaxis, :], (param_arr - p_min) / np.where(valid, p_range, 1.0), 0.0)
    max_pairs = n * (n - 1) // 2
    if max_pairs <= n_pairs:
        sampled_pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]
    else:
        rng = np.random.default_rng(seed=42)
        seen: set[tuple[int, int]] = set()
        sampled_pairs: list[tuple[int, int]] = []
        while len(sampled_pairs) < n_pairs:
            ij = tuple(sorted(rng.integers(0, n, size=2).tolist()))
            if ij[0] != ij[1] and ij not in seen:
                seen.add(ij)
                sampled_pairs.append(ij)
    lipschitz_vals: list[float] = []
    for (i, j) in sampled_pairs:
        d_theta = float(np.linalg.norm(normed[i] - normed[j]))
        if d_theta < 1e-09:
            continue
        d_score = abs(float(scores[i]) - float(scores[j]))
        lipschitz_vals.append(d_score / d_theta)
    if not lipschitz_vals:
        return None
    median_lip = float(np.median(lipschitz_vals))
    return 1.0 - float(np.clip(median_lip / _LIPSCHITZ_NORMALISER, 0.0, 1.0))

def _termination_reliability_from_traces(traces: list[EpisodeTrace]) -> float:
    n_condition_met: int = 0
    n_reactive: int = 0
    for t in traces:
        telemetry = t.metadata.get('phase_telemetry')
        if not telemetry:
            continue
        for phase in telemetry:
            reason = phase.get('termination_reason', 'step_budget')
            if reason == 'time_limit':
                continue
            n_reactive += 1
            if reason in ('condition_met', 'force_exceeded'):
                n_condition_met += 1
    if n_reactive == 0:
        return None
    return float(n_condition_met) / float(n_reactive)

def _get_phase_telem(phase_telemetry: list[dict] | None, phase_type_or_name: str) -> dict:
    for p in phase_telemetry or []:
        if p.get('phase_type') == phase_type_or_name or p.get('phase_name') == phase_type_or_name:
            return p
    return {}

def _as_vec3(value: Any) -> np.ndarray | None:
    if value is None:
        return None
    try:
        arr = np.asarray(value, dtype=float).reshape(-1)
    except (TypeError, ValueError):
        return None
    if arr.size < 3:
        return None
    return arr[:3].astype(float)

def _metadata_containers(metadata: dict | None) -> list[dict]:
    if not isinstance(metadata, dict):
        return []
    containers: list[dict] = []
    for key in ('episode_task_state', 'randomised_task_state', 'realised_task_state', 'task_state'):
        value = metadata.get(key)
        if isinstance(value, dict):
            containers.append(value)
    containers.append(metadata)
    return containers

def _metadata_vec(metadata: dict | None, keys: tuple[str, ...]) -> np.ndarray | None:
    for container in _metadata_containers(metadata):
        for key in keys:
            value = container.get(key)
            vec = _as_vec3(value)
            if vec is not None:
                return vec
    return None

def _resolve_object_initial(ep: EpisodeTrace, task_spec) -> np.ndarray | None:
    meta = ep.metadata or {}
    resolved = _metadata_vec(meta, ('actual_object_initial_position', 'object_initial_position', 'object_initial_pose', 'initial_object_position', 'actual_fixture_position', 'fixture_position', 'socket_position', 'peg_initial_position'))
    if resolved is not None:
        return resolved
    if task_spec is not None and getattr(task_spec, 'object_initial_pose', None) is not None:
        return np.array(task_spec.object_initial_pose[:3], dtype=float)
    return None

def _resolve_goal_position(ep: EpisodeTrace, task_spec, *, prefer_place: bool=False, infer_from_object_offset: bool=False) -> np.ndarray | None:
    meta = ep.metadata or {}
    keys = ('actual_place_goal_position', 'place_goal_position', 'target_object_position', 'actual_goal_object_position', 'goal_object_position', 'actual_goal_position') if prefer_place else ('actual_goal_object_position', 'goal_object_position', 'target_object_position', 'actual_goal_position', 'actual_goal_tcp_position', 'goal_tcp_position', 'actual_fixture_goal_position', 'fixture_goal_position')
    resolved = _metadata_vec(meta, keys)
    if resolved is not None:
        return resolved
    if infer_from_object_offset and task_spec is not None and (getattr(task_spec, 'object_initial_pose', None) is not None):
        actual_obj = _resolve_object_initial(ep, task_spec)
        if actual_obj is not None:
            static_obj = np.array(task_spec.object_initial_pose[:3], dtype=float)
            static_goal = None
            if prefer_place and getattr(task_spec, 'place_goal_position', None) is not None:
                static_goal = np.array(task_spec.place_goal_position[:3], dtype=float)
            elif getattr(task_spec, 'goal_object_position', None) is not None:
                static_goal = np.array(task_spec.goal_object_position[:3], dtype=float)
            elif getattr(task_spec, 'goal_tcp_position', None) is not None:
                static_goal = np.array(task_spec.goal_tcp_position[:3], dtype=float)
            if static_goal is not None:
                return actual_obj + (static_goal - static_obj)
    if task_spec is None:
        return None
    if prefer_place and getattr(task_spec, 'place_goal_position', None) is not None:
        return np.array(task_spec.place_goal_position[:3], dtype=float)
    for attr in ('goal_object_position', 'place_goal_position', 'goal_tcp_position'):
        value = getattr(task_spec, attr, None)
        if value is not None:
            return np.array(value[:3], dtype=float)
    return None

def _resolve_hinge_delta(ep: EpisodeTrace, task_spec) -> float | None:
    meta = ep.metadata or {}
    achieved = None
    for container in _metadata_containers(meta):
        for key in ('hinge_angle', 'final_hinge_angle', 'door_hinge_angle'):
            if key in container and container.get(key) is not None:
                achieved = float(container[key])
                break
        if achieved is not None:
            break
    if achieved is None:
        return None
    initial = None
    for container in _metadata_containers(meta):
        for key in ('initial_hinge_angle', 'hinge_initial_angle', 'door_initial_hinge_angle'):
            if key in container and container.get(key) is not None:
                initial = float(container[key])
                break
        if initial is not None:
            break
    if initial is None:
        initial = 0.0
    return achieved - initial

def _representative_task_state(traces: list[EpisodeTrace]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    episode_states: list[dict[str, Any]] = []
    for (idx, trace) in enumerate(traces):
        meta = trace.metadata or {}
        state: dict[str, Any] = {}
        for key in ('episode_task_state', 'randomised_task_state', 'realised_task_state', 'task_state'):
            if isinstance(meta.get(key), dict):
                state.update(meta[key])
        for key in ('actual_goal_position', 'actual_goal_object_position', 'actual_place_goal_position', 'object_initial_pose', 'actual_object_initial_position', 'initial_hinge_angle', 'hinge_angle'):
            if key in meta:
                state[key] = meta[key]
        if state:
            state.setdefault('episode_index', idx)
            episode_states.append(state)
    representative = dict(episode_states[0]) if episode_states else {}
    return (representative, episode_states)

def _sub_scores_push(episodes: list[EpisodeTrace], task_spec) -> dict[str, float | None]:
    keys = ['object_displacement_ratio', 'lateral_force_integral', 'approach_alignment', 'goal_progress']
    if not episodes:
        return {k: None for k in keys}
    odr_vals: list[float] = []
    for ep in episodes:
        final_obj = ep.metadata.get('final_object_position')
        if final_obj is None:
            odr_vals.append(float('nan'))
            continue
        final_obj = np.array(final_obj[:3], dtype=float)
        init_pos = _resolve_object_initial(ep, task_spec)
        if init_pos is None:
            odr_vals.append(float('nan'))
            continue
        actual_disp = float(np.linalg.norm(final_obj - init_pos))
        goal_pos = _resolve_goal_position(ep, task_spec)
        if goal_pos is not None:
            target_disp = float(np.linalg.norm(goal_pos - init_pos))
        else:
            odr_vals.append(float('nan'))
            continue
        if target_disp < 1e-09:
            odr_vals.append(float('nan'))
        else:
            odr_vals.append(float(np.clip(actual_disp / target_disp, 0.0, 1.0)))
    odr = _nanmean(odr_vals)
    lfi = None
    aa_vals: list[float] = []
    for ep in episodes:
        traj = ep.trajectory_positions
        if traj is None or len(traj) < 2:
            aa_vals.append(float('nan'))
            continue
        push_vec = traj[-1] - traj[0]
        push_norm = float(np.linalg.norm(push_vec))
        if push_norm < 1e-09:
            aa_vals.append(float('nan'))
            continue
        push_dir = push_vec / push_norm
        init_pos = _resolve_object_initial(ep, task_spec)
        goal_pos = _resolve_goal_position(ep, task_spec)
        if init_pos is None or goal_pos is None:
            aa_vals.append(float('nan'))
            continue
        goal_vec = goal_pos - init_pos
        goal_norm = float(np.linalg.norm(goal_vec))
        if goal_norm < 1e-09:
            aa_vals.append(float('nan'))
            continue
        goal_dir = goal_vec / goal_norm
        cosine = float(np.clip(np.dot(push_dir, goal_dir), -1.0, 1.0))
        aa_vals.append((cosine + 1.0) / 2.0)
    aa = _nanmean(aa_vals)
    gp_vals: list[float] = []
    for ep in episodes:
        final_obj = ep.metadata.get('final_object_position')
        if final_obj is None:
            gp_vals.append(float('nan'))
            continue
        final_obj_arr = np.array(final_obj[:3], dtype=float)
        goal_pos = _resolve_goal_position(ep, task_spec)
        if goal_pos is None:
            gp_vals.append(float('nan'))
            continue
        init_pos = _resolve_object_initial(ep, task_spec)
        if init_pos is None:
            gp_vals.append(float('nan'))
            continue
        dist_final_to_goal = float(np.linalg.norm(final_obj_arr - goal_pos))
        dist_init_to_goal = float(np.linalg.norm(init_pos - goal_pos))
        if dist_init_to_goal < 1e-09:
            gp_vals.append(1.0)
        else:
            gp = float(np.clip(1.0 - dist_final_to_goal / dist_init_to_goal, 0.0, 1.0))
            gp_vals.append(gp)
    goal_progress = _nanmean(gp_vals)
    return {'object_displacement_ratio': odr, 'lateral_force_integral': lfi, 'approach_alignment': aa, 'goal_progress': goal_progress}

def _sub_scores_obstacle_reach(episodes: list[EpisodeTrace], task_spec) -> dict[str, float | str | None]:
    keys = ['obstacle_clearance', 'path_efficiency', 'arc_smoothness', 'collision_factor', 'peak_obstacle_force', 'collision_location', 'final_tcp_distance', 'min_tcp_distance', 'tcp_proximity_score', 'goal_reached_rate']
    if not episodes:
        return {k: None for k in keys}
    oc_vals: list[float] = []
    for ep in episodes:
        traj = ep.trajectory_positions
        if traj is None or len(traj) == 0:
            oc_vals.append(float('nan'))
            continue
        obstacle_height = ep.metadata.get('obstacle_height')
        if obstacle_height is None and task_spec is not None:
            obstacle_height = getattr(task_spec, 'obstacle_height', None)
        if obstacle_height is None:
            oc_vals.append(float('nan'))
            continue
        threshold = float(obstacle_height) + 0.01
        z_vals = traj[:, 2]
        oc_vals.append(float(np.mean(z_vals > threshold)))
    oc = _nanmean(oc_vals)
    pe_vals: list[float] = []
    for ep in episodes:
        traj = ep.trajectory_positions
        if traj is None or len(traj) < 2:
            pe_vals.append(float('nan'))
            continue
        straight_dist = float(np.linalg.norm(traj[-1] - traj[0]))
        segments = traj[1:] - traj[:-1]
        path_length = float(np.sum(np.linalg.norm(segments, axis=1)))
        if path_length < 1e-09:
            pe_vals.append(float('nan'))
            continue
        pe_vals.append(float(np.clip(straight_dist / path_length, 0.0, 1.0)))
    pe = _nanmean(pe_vals)
    as_vals: list[float] = []
    for ep in episodes:
        traj = ep.trajectory_positions
        if traj is None or len(traj) < 3:
            as_vals.append(float('nan'))
            continue
        dirs = traj[1:] - traj[:-1]
        norms = np.linalg.norm(dirs, axis=1)
        valid_mask = norms > 1e-12
        if np.sum(valid_mask) < 2:
            as_vals.append(float('nan'))
            continue
        unit_dirs = dirs[valid_mask] / norms[valid_mask, np.newaxis]
        dots = np.einsum('ij,ij->i', unit_dirs[:-1], unit_dirs[1:])
        dots = np.clip(dots, -1.0, 1.0)
        angle_changes = np.arccos(dots)
        if len(angle_changes) == 0:
            as_vals.append(float('nan'))
            continue
        termination_fidelity = float(np.clip(1.0 - float(np.mean(np.abs(angle_changes))) / np.pi, 0.0, 1.0))
        as_vals.append(termination_fidelity)
    arc_s = _nanmean(as_vals)
    _tol = float(task_spec.goal_tolerance) if task_spec is not None else 0.02
    _sigma = float(task_spec.expressivity_sigma) if task_spec is not None else 0.1
    fd_vals: list[float] = []
    md_vals: list[float] = []
    tcp_prox_vals: list[float] = []
    gr_vals: list[float] = []
    for ep in episodes:
        tcp_positions: list = list(ep.metadata.get('tcp_positions', []) or [])
        ftcp = ep.metadata.get('final_tcp_position')
        if ftcp is not None:
            tcp_positions.append(list(ftcp)[:3])
        _goal = _resolve_goal_position(ep, task_spec)
        if not tcp_positions or _goal is None:
            fd_vals.append(float('nan'))
            md_vals.append(float('nan'))
            tcp_prox_vals.append(float('nan'))
            gr_vals.append(float('nan'))
            continue
        distances = [float(np.linalg.norm(np.array(p[:3], dtype=float) - _goal)) for p in tcp_positions]
        final_dist = distances[-1]
        fd_vals.append(final_dist)
        md_vals.append(min(distances))
        tcp_prox_vals.append(float(math.exp(-final_dist / _sigma)))
        gr_vals.append(1.0 if final_dist <= _tol else 0.0)
    final_tcp_distance = _nanmean(fd_vals)
    min_tcp_distance = _nanmean(md_vals)
    tcp_proximity_score = _nanmean(tcp_prox_vals)
    goal_reached_rate = _nanmean(gr_vals)
    _force_scale: float = float(getattr(task_spec, 'force_scale', 5.0)) if task_spec is not None else 5.0
    _has_obstacle = task_spec is not None and getattr(task_spec, 'obstacle_body_name', None) is not None
    cf_vals: list[float] = []
    pf_vals: list[float] = []
    for ep in episodes:
        peak_force = float(ep.metadata.get('peak_obstacle_force', 0.0))
        pf_vals.append(peak_force)
        cf_vals.append(math.exp(-peak_force / _force_scale))
    mean_collision_factor = float(np.mean(cf_vals)) if cf_vals else None
    mean_peak_force = float(np.mean(pf_vals)) if pf_vals else None
    collision_location: str | None = None
    if _has_obstacle:
        collision_location = str(task_spec.obstacle_body_name)
    _contact_counterbody: str | None = None
    _contact_countergeom: str | None = None
    _contact_obstacle_body: str | None = None
    _contact_obstacle_geom: str | None = None
    if pf_vals:
        _best_idx = max(range(len(pf_vals)), key=lambda i: pf_vals[i])
        _best_ep = episodes[_best_idx]
        _contact_counterbody = (_best_ep.metadata or {}).get('peak_obstacle_counterbody')
        _contact_countergeom = (_best_ep.metadata or {}).get('peak_obstacle_countergeom')
        _contact_obstacle_body = (_best_ep.metadata or {}).get('peak_obstacle_obstacle_body')
        _contact_obstacle_geom = (_best_ep.metadata or {}).get('peak_obstacle_obstacle_geom')
    return {'obstacle_clearance': oc, 'path_efficiency': pe, 'arc_smoothness': arc_s, 'collision_factor': mean_collision_factor, 'peak_obstacle_force': mean_peak_force, 'collision_location': collision_location, 'final_tcp_distance': final_tcp_distance, 'min_tcp_distance': min_tcp_distance, 'tcp_proximity_score': tcp_proximity_score, 'goal_reached_rate': goal_reached_rate, 'peak_obstacle_counterbody': _contact_counterbody, 'peak_obstacle_countergeom': _contact_countergeom, 'peak_obstacle_obstacle_body': _contact_obstacle_body, 'peak_obstacle_obstacle_geom': _contact_obstacle_geom}

def _get_hole_depth(task_spec) -> float:
    if getattr(task_spec, 'hole_depth', None) is not None:
        return float(task_spec.hole_depth)
    if getattr(task_spec, 'channel_length', None) is not None:
        return float(task_spec.channel_length)
    if task_spec is not None and getattr(task_spec, 'goal_tolerance', None) is not None:
        return float(task_spec.goal_tolerance)
    return 0.05

def _sub_scores_peg(episodes: list[EpisodeTrace], task_spec, task_name: str='') -> dict[str, float | None]:
    is_peg_insert = task_name.lower() == 'peg_insert'
    depth_key = 'distance_to_goal_ratio' if is_peg_insert else 'insertion_depth_ratio'
    keys = [depth_key, 'alignment_error', 'force_efficiency']
    if not episodes:
        return {k: None for k in keys}
    depth_vals: list[float] = []
    for ep in episodes:
        final_obj = ep.metadata.get('final_object_position')
        using_tcp_fallback = final_obj is None
        if using_tcp_fallback:
            final_obj = ep.metadata.get('final_tcp_position')
        if final_obj is None and (not using_tcp_fallback):
            depth_vals.append(float('nan'))
            continue
        if final_obj is not None:
            final_obj = np.array(final_obj[:3], dtype=float)
        if task_spec is None:
            depth_vals.append(float('nan'))
            continue
        if is_peg_insert:
            goal = _resolve_goal_position(ep, task_spec, infer_from_object_offset=True)
            if goal is None:
                depth_vals.append(float('nan'))
                continue
            tcp_positions = ep.metadata.get('tcp_positions', [])
            all_tcps: list = list(tcp_positions)
            ftcp = ep.metadata.get('final_tcp_position')
            if ftcp is not None:
                all_tcps.append(list(ftcp)[:3])
            elif final_obj is not None:
                all_tcps.append(final_obj.tolist())
            if not all_tcps:
                depth_vals.append(float('nan'))
                continue
            first_tcp = np.array(all_tcps[0][:3], dtype=float)
            initial_dist = float(np.linalg.norm(first_tcp - goal))
            if initial_dist < 1e-09:
                depth_vals.append(1.0)
                continue
            min_dist = float('inf')
            for tcp_pos in all_tcps:
                if tcp_pos is not None:
                    d = float(np.linalg.norm(np.array(tcp_pos[:3], dtype=float) - goal))
                    if d < min_dist:
                        min_dist = d
            dtg = float(np.clip(1.0 - min_dist / initial_dist, 0.0, 1.0))
            depth_vals.append(dtg)
        elif using_tcp_fallback:
            if task_spec.goal_tcp_position is None:
                depth_vals.append(float('nan'))
                continue
            init_pos = np.array(task_spec.goal_tcp_position[:3], dtype=float)
            if task_spec.channel_axis is not None:
                axis = np.array(task_spec.channel_axis, dtype=float)
            else:
                axis = np.array([0.0, -1.0, 0.0])
            axis_norm = float(np.linalg.norm(axis))
            if axis_norm < 1e-12:
                depth_vals.append(float('nan'))
                continue
            axis = axis / axis_norm
            hole_depth = _get_hole_depth(task_spec)
            if hole_depth < 1e-09:
                depth_vals.append(float('nan'))
                continue
            tcp_positions = ep.metadata.get('tcp_positions', [])
            all_tcps: list = list(tcp_positions)
            if final_obj is not None:
                all_tcps.append(final_obj.tolist())
            max_axial = 0.0
            for tcp_pos in all_tcps:
                if tcp_pos is not None:
                    delta = np.array(tcp_pos[:3], dtype=float) - init_pos
                    ap = float(np.dot(delta, axis))
                    if ap > max_axial:
                        max_axial = ap
            depth_vals.append(float(np.clip(max_axial / hole_depth, 0.0, 1.0)))
        else:
            init_pos = _resolve_object_initial(ep, task_spec)
            if init_pos is None:
                depth_vals.append(float('nan'))
                continue
            if task_spec.channel_axis is not None:
                axis = np.array(task_spec.channel_axis, dtype=float)
            else:
                axis = np.array([0.0, -1.0, 0.0])
            axis_norm = float(np.linalg.norm(axis))
            if axis_norm < 1e-12:
                depth_vals.append(float('nan'))
                continue
            axis = axis / axis_norm
            hole_depth = _get_hole_depth(task_spec)
            if hole_depth < 1e-09:
                depth_vals.append(float('nan'))
                continue
            assert final_obj is not None
            delta = final_obj - init_pos
            axial_progress = float(np.dot(delta, axis))
            depth_vals.append(float(np.clip(axial_progress / hole_depth, 0.0, 1.0)))
    depth_score = _nanmean(depth_vals)
    ae = None
    _MAX_INSERTION_FORCE: float = 50.0
    fe_vals: list[float] = [float(np.clip(1.0 - ep.peak_contact_force / _MAX_INSERTION_FORCE, 0.0, 1.0)) for ep in episodes]
    fe = _nanmean(fe_vals)
    return {depth_key: depth_score, 'alignment_error': ae, 'force_efficiency': fe}

def _sub_scores_grasp_place(episodes: list[EpisodeTrace], task_spec) -> dict[str, float | None]:
    keys = ['grasp_success_rate', 'place_accuracy', 'lift_clearance', 'transport_retention']
    if not episodes:
        return {k: None for k in keys}
    gsr_vals: list[float] = []
    for ep in episodes:
        if 'grasp_achieved' in ep.metadata:
            gsr_vals.append(float(bool(ep.metadata['grasp_achieved'])))
        else:
            gsr_vals.append(float(ep.success))
    gsr = float(np.mean(gsr_vals)) if gsr_vals else None
    pa_vals: list[float] = []
    for ep in episodes:
        final_obj = ep.metadata.get('final_object_position')
        if final_obj is None:
            pa_vals.append(float('nan'))
            continue
        final_obj = np.array(final_obj[:3], dtype=float)
        goal = _resolve_goal_position(ep, task_spec, prefer_place=True)
        if goal is None:
            pa_vals.append(float('nan'))
            continue
        if task_spec is None:
            pa_vals.append(float('nan'))
            continue
        tolerance = float(task_spec.goal_tolerance)
        if tolerance < 1e-09:
            pa_vals.append(float('nan'))
            continue
        error = float(np.linalg.norm(final_obj - goal))
        pa_vals.append(float(np.clip(1.0 - error / tolerance, 0.0, 1.0)))
    pa = _nanmean(pa_vals)
    _LIFT_Z_THRESHOLD: float = 0.11
    lc_vals: list[float] = []
    for ep in episodes:
        grasp_ok = bool(ep.metadata.get('grasp_achieved', True))
        _pt = ep.metadata.get('phase_telemetry')
        if not grasp_ok:
            _arc_phase_ng = _get_phase_telem(_pt, 'transport_arc')
            _arc_z_max_ng = _arc_phase_ng.get('object_z_max') if _arc_phase_ng else None
            if _arc_z_max_ng is not None:
                lc_vals.append(1.0 if float(_arc_z_max_ng) > _LIFT_Z_THRESHOLD else 0.0)
            else:
                lc_vals.append(0.0)
            continue
        _lift_phase = _get_phase_telem(_pt, 'lift')
        _lift_obj_end = _lift_phase.get('object_pos_end') if _lift_phase else None
        if _lift_obj_end is not None:
            lc_vals.append(1.0 if float(_lift_obj_end[2]) > _LIFT_Z_THRESHOLD else 0.0)
        else:
            _arc_phase = _get_phase_telem(_pt, 'transport_arc')
            _arc_z_max = _arc_phase.get('object_z_max') if _arc_phase else None
            if _arc_z_max is not None:
                lc_vals.append(1.0 if float(_arc_z_max) > _LIFT_Z_THRESHOLD else 0.0)
            else:
                obj_pos = ep.metadata.get('final_object_position')
                if obj_pos is not None:
                    lc_vals.append(1.0 if float(obj_pos[2]) > _LIFT_Z_THRESHOLD else 0.0)
    lc = float(np.mean(lc_vals)) if lc_vals else None
    _TRANSPORT_Z_THRESHOLD: float = 0.08
    tr_vals: list[float] = []
    for ep in episodes:
        _pt = (ep.metadata or {}).get('phase_telemetry', [])
        _tr_phase = _get_phase_telem(_pt, 'transport_hover')
        if not _tr_phase:
            _tr_phase = _get_phase_telem(_pt, 'approach_goal')
        if _tr_phase and _tr_phase.get('object_pos_end') is not None:
            _obj_z = float(_tr_phase['object_pos_end'][2])
            tr_vals.append(1.0 if _obj_z > _TRANSPORT_Z_THRESHOLD else 0.0)
        else:
            _arc_tr_phase = _get_phase_telem(_pt, 'transport_arc')
            _arc_tr_z_max = _arc_tr_phase.get('object_z_max') if _arc_tr_phase else None
            if _arc_tr_z_max is not None:
                tr_vals.append(1.0 if float(_arc_tr_z_max) > _TRANSPORT_Z_THRESHOLD else 0.0)
            else:
                tr_vals.append(float('nan'))
    tr = _nanmean(tr_vals)
    return {'grasp_success_rate': gsr, 'place_accuracy': pa, 'lift_clearance': lc, 'transport_retention': tr}

def _sub_scores_door_pull(episodes: list[EpisodeTrace], task_spec) -> dict[str, float | None]:
    keys = ['hinge_angle_ratio', 'arc_quality']
    if not episodes:
        return {k: None for k in keys}
    target_angle = float(task_spec.target_hinge_angle) if task_spec is not None and task_spec.target_hinge_angle is not None else 0.524
    har_vals: list[float] = []
    for ep in episodes:
        achieved_delta = _resolve_hinge_delta(ep, task_spec)
        if achieved_delta is not None:
            ratio = float(np.clip(achieved_delta / max(target_angle, 1e-09), 0.0, 1.0))
            har_vals.append(ratio)
            continue
        traj = ep.trajectory_positions
        if traj is None or len(traj) < 2:
            har_vals.append(float('nan'))
            continue
        if task_spec is not None and task_spec.arm_initial_tcp_position is not None:
            start_pos = np.array(task_spec.arm_initial_tcp_position[:3], dtype=float)
        else:
            start_pos = traj[0]
        end_pos = traj[-1]
        chord = float(np.linalg.norm(end_pos - start_pos))
        _DOOR_HANDLE_RADIUS = 0.4
        arc_angle_approx = chord / _DOOR_HANDLE_RADIUS
        ratio = float(np.clip(arc_angle_approx / max(target_angle, 1e-09), 0.0, 1.0))
        har_vals.append(ratio)
    har = _nanmean(har_vals)
    aq_vals: list[float] = []
    for ep in episodes:
        telemetry = ep.metadata.get('phase_telemetry')
        if not telemetry:
            aq_vals.append(float('nan'))
            continue
        rates = [1.0 if p['terminated_normally'] else 0.0 for p in telemetry]
        aq_vals.append(float(np.mean(rates)))
    aq = _nanmean(aq_vals)
    return {'hinge_angle_ratio': har, 'arc_quality': aq}

def _compute_subtask_scores(episode_trace: 'EpisodeTrace', task_spec, task_name: str='') -> dict[str, float]:
    subtasks = task_spec.subtasks
    if not subtasks:
        return {'phase_score': 0.0}
    telemetry = episode_trace.metadata.get('phase_telemetry') or []
    if not telemetry:
        return {'phase_score': 0.0}
    by_type: dict[str, list[dict]] = {}
    for _p in telemetry:
        _pt = _p.get('phase_type')
        if _pt is not None:
            by_type.setdefault(str(_pt).strip().lower(), []).append(_p)
        _pn = _p.get('phase_name')
        if _pn is not None:
            by_type.setdefault(str(_pn).strip().lower(), []).append(_p)
        _sid = _p.get('subtask_id')
        if _sid is not None:
            by_type.setdefault(str(_sid).strip().lower(), []).append(_p)
    _aliases = getattr(task_spec, 'phase_type_aliases', None)
    if not isinstance(_aliases, dict):
        _aliases = {}

    def _find_last(subtask_id: str) -> dict | None:
        candidates = by_type.get(subtask_id, [])
        if not candidates:
            for (alias_from, alias_to) in _aliases.items():
                if alias_to == subtask_id:
                    candidates = by_type.get(alias_from, [])
                    if candidates:
                        break
        return candidates[-1] if candidates else None
    sigma_dist = 0.05
    total_weight = sum((st.weight for st in subtasks))
    if total_weight < 1e-09:
        total_weight = 1.0
    scores: dict[str, float] = {}
    weighted_sum = 0.0
    for st in subtasks:
        phase = _find_last(st.id)
        score = 0.0
        if phase is not None:
            if st.metric == 'distance':
                tcp_end = phase.get('tcp_end')
                if tcp_end is not None:
                    target = _resolve_subtask_target_from_metadata(st, episode_trace, task_spec)
                    if target is not None:
                        dist = float(np.linalg.norm(np.array(tcp_end[:3], dtype=float) - target))
                        score = float(np.exp(-dist / sigma_dist))
                    else:
                        d = phase.get('tcp_to_object_dist_end')
                        if d is not None:
                            score = float(d < 0.05)
            elif st.metric == 'goal_progress':
                g_start = phase.get('object_to_goal_dist_start')
                g_end = phase.get('object_to_goal_dist_end')
                if g_start is not None and g_end is not None:
                    g_start_f = float(g_start)
                    if g_start_f > 1e-09:
                        push_delta = g_start_f - float(g_end)
                        score = float(np.clip(push_delta / g_start_f, 0.0, 1.0))
            elif st.metric == 'contact':
                score = float(bool(phase.get('contact_detected', False)))
            elif st.metric == 'hinge_angle':
                achieved = episode_trace.metadata.get('hinge_angle')
                target_angle = float(task_spec.target_hinge_angle) if getattr(task_spec, 'target_hinge_angle', None) is not None else 0.524
                if achieved is not None:
                    score = float(np.clip(float(achieved) / max(target_angle, 1e-09), 0.0, 1.0))
        normalised_weight = st.weight / total_weight
        weighted_sum += normalised_weight * score
        scores[f'{st.id}_score'] = score
    scores['phase_score'] = float(np.clip(weighted_sum, 0.0, 1.0))
    return scores

def _resolve_subtask_target_from_metadata(subtask: 'SubtaskSpec', episode_trace: 'EpisodeTrace', task_spec) -> 'np.ndarray | None':
    from evaluation.task_spec import SubtaskSpec
    offset = np.array(subtask.offset, dtype=float)
    if subtask.anchor == 'world':
        return offset
    elif subtask.anchor == 'object':
        obj_pos = _resolve_object_initial(episode_trace, task_spec)
        if obj_pos is None:
            return None
        return obj_pos + offset
    elif subtask.anchor == 'goal':
        goal = _resolve_goal_position(episode_trace, task_spec)
        if goal is None:
            return None
        return goal + offset
    elif subtask.anchor == 'fixture':
        fixture = _metadata_vec(episode_trace.metadata, ('fixture_position', 'actual_fixture_position', 'socket_position'))
        if fixture is not None:
            return fixture + offset
        fixture = getattr(task_spec, 'fixture_pose', None)
        if fixture is not None:
            return np.array(fixture[:3], dtype=float) + offset
        return offset
    return None

def _phase_scores_push_to_goal(episode_trace: 'EpisodeTrace', task_spec) -> dict[str, float]:
    telemetry = episode_trace.metadata.get('phase_telemetry') or []
    by_name: dict[str, dict] = {p['phase_name']: p for p in telemetry}
    by_type: dict[str, dict] = {}
    for _p in telemetry:
        _pt = _p.get('phase_type')
        if _pt is not None:
            by_type[str(_pt).strip().lower()] = _p

    def _lookup(key: str) -> dict | None:
        result = by_type.get(key) or by_name.get(key)
        if result is None:
            _aliases = getattr(task_spec, 'phase_type_aliases', None)
            if isinstance(_aliases, dict) and _aliases:
                for (_alias_from, _alias_to) in _aliases.items():
                    if _alias_to == key:
                        result = by_type.get(_alias_from) or by_name.get(_alias_from)
                        if result is not None:
                            break
        return result
    approach_phase = _lookup('approach')
    if approach_phase is not None and approach_phase.get('tcp_to_object_dist_end') is not None:
        approach_score = float(approach_phase['tcp_to_object_dist_end'] < 0.05)
    else:
        approach_score = 0.0
    contact_phase = _lookup('contact')
    if contact_phase is not None:
        obj_start = contact_phase.get('object_pos_start')
        obj_end = contact_phase.get('object_pos_end')
        if obj_start is not None and obj_end is not None:
            contact_delta = float(np.linalg.norm(np.array(obj_end, dtype=float) - np.array(obj_start, dtype=float)))
            contact_score = float(np.clip(contact_delta / 0.03, 0.0, 1.0))
        else:
            contact_score = 0.0
    else:
        contact_score = 0.0
    push_phase = _lookup('push')
    push_score = 0.0
    if push_phase is not None:
        g_start = push_phase.get('object_to_goal_dist_start')
        g_end = push_phase.get('object_to_goal_dist_end')
        if g_start is not None and g_end is not None:
            goal_dist_initial: float | None = None
            init_pos = _resolve_object_initial(episode_trace, task_spec)
            goal_pos = _resolve_goal_position(episode_trace, task_spec)
            if init_pos is not None and goal_pos is not None:
                goal_dist_initial = float(np.linalg.norm(init_pos - goal_pos))
            if goal_dist_initial is None or goal_dist_initial < 1e-09:
                goal_dist_initial = float(g_start) if float(g_start) > 1e-09 else 1.0
            push_delta = float(g_start) - float(g_end)
            push_score = float(np.clip(push_delta / goal_dist_initial, 0.0, 1.0))
    phase_score = float(0.2 * approach_score + 0.3 * contact_score + 0.5 * push_score)
    return {'approach_score': approach_score, 'contact_score': contact_score, 'push_score': push_score, 'phase_score': phase_score}

def _phase_scores_peg_channel(episode_trace: 'EpisodeTrace', task_spec) -> dict[str, float]:
    telemetry = episode_trace.metadata.get('phase_telemetry') or []
    by_name: dict[str, dict] = {p['phase_name']: p for p in telemetry}
    by_type: dict[str, dict] = {}
    for _p in telemetry:
        _pt = _p.get('phase_type')
        if _pt is not None:
            by_type[str(_pt).strip().lower()] = _p

    def _lookup(key: str) -> dict | None:
        result = by_type.get(key) or by_name.get(key)
        if result is None:
            _aliases = getattr(task_spec, 'phase_type_aliases', None)
            if isinstance(_aliases, dict) and _aliases:
                for (_alias_from, _alias_to) in _aliases.items():
                    if _alias_to == key:
                        result = by_type.get(_alias_from) or by_name.get(_alias_from)
                        if result is not None:
                            break
        return result
    approach_phase = _lookup('approach')
    if approach_phase is not None and approach_phase.get('tcp_to_object_dist_end') is not None:
        approach_score = float(approach_phase['tcp_to_object_dist_end'] < 0.05)
    else:
        approach_score = 0.0
    contact_phase = _lookup('contact')
    if contact_phase is not None:
        contact_score = float(bool(contact_phase.get('contact_detected', False)))
    else:
        contact_score = 0.0
    push_phase = _lookup('push')
    push_score = 0.0
    if push_phase is not None:
        obj_start = push_phase.get('object_pos_start')
        obj_end = push_phase.get('object_pos_end')
        if obj_start is not None and obj_end is not None:
            peg_y_start = float(np.array(obj_start, dtype=float)[1])
            peg_y_end = float(np.array(obj_end, dtype=float)[1])
            channel_length = float(task_spec.channel_length) if task_spec is not None and getattr(task_spec, 'channel_length', None) is not None else 0.18
            axial_progress = (peg_y_start - peg_y_end) / max(channel_length, 1e-09)
            push_score = float(np.clip(axial_progress, 0.0, 1.0))
    phase_score = float(0.2 * approach_score + 0.2 * contact_score + 0.6 * push_score)
    return {'approach_score': approach_score, 'contact_score': contact_score, 'push_score': push_score, 'phase_score': phase_score}

def _phase_scores_grasp_place(episode_trace: 'EpisodeTrace', task_spec) -> dict[str, float]:
    telemetry = episode_trace.metadata.get('phase_telemetry') or []
    by_name: dict[str, dict] = {p['phase_name']: p for p in telemetry}
    by_type: dict[str, dict] = {}
    for _p in telemetry:
        _pt = _p.get('phase_type')
        if _pt is not None:
            by_type[str(_pt).strip().lower()] = _p

    def _lookup(key: str) -> dict | None:
        result = by_type.get(key) or by_name.get(key)
        if result is None:
            _aliases = getattr(task_spec, 'phase_type_aliases', None)
            if isinstance(_aliases, dict) and _aliases:
                for (_alias_from, _alias_to) in _aliases.items():
                    if _alias_to == key:
                        result = by_type.get(_alias_from) or by_name.get(_alias_from)
                        if result is not None:
                            break
        return result
    descend_phase = _lookup('descend')
    if descend_phase is not None and descend_phase.get('tcp_to_object_dist_end') is not None:
        descend_score = float(descend_phase['tcp_to_object_dist_end'] < 0.04)
    else:
        descend_score = 0.0
    grasp_phase = _lookup('grasp')
    if grasp_phase is not None:
        grasp_score = float(bool(grasp_phase.get('contact_detected', False)))
    else:
        grasp_score = 0.0
    lift_phase = _lookup('lift')
    lift_score = 0.0
    if lift_phase is not None:
        obj_start = lift_phase.get('object_pos_start')
        obj_end = lift_phase.get('object_pos_end')
        if obj_start is not None and obj_end is not None:
            lift_delta = float(np.array(obj_end, dtype=float)[2] - np.array(obj_start, dtype=float)[2])
            lift_score = float(np.clip(lift_delta / 0.1, 0.0, 1.0))
    place_score = 0.0
    place_goal = _resolve_goal_position(episode_trace, task_spec, prefer_place=True)
    if task_spec is not None and place_goal is not None:
        sigma = float(task_spec.expressivity_sigma) if task_spec.expressivity_sigma else 0.05
        goal_tolerance = float(task_spec.goal_tolerance) if task_spec.goal_tolerance else 0.05
        obj_final = episode_trace.metadata.get('final_object_position')
        if obj_final is not None:
            dist = float(np.linalg.norm(np.array(obj_final[:3], dtype=float) - place_goal))
            place_score = 1.0 if dist <= goal_tolerance else float(np.exp(-dist / sigma))
    phase_score = float(0.1 * descend_score + 0.3 * grasp_score + 0.4 * lift_score + 0.2 * place_score)
    return {'descend_score': descend_score, 'grasp_score': grasp_score, 'lift_score': lift_score, 'place_score': place_score, 'phase_score': phase_score}

def _compute_phase_scores(episode_trace: 'EpisodeTrace', task_spec, task_name: str='') -> dict[str, float]:
    _subtasks = getattr(task_spec, 'subtasks', None)
    if task_spec is not None and isinstance(_subtasks, tuple) and (len(_subtasks) > 0):
        return _compute_subtask_scores(episode_trace, task_spec, task_name)
    name_lower = task_name.lower()
    if name_lower == 'push_to_goal':
        return _phase_scores_push_to_goal(episode_trace, task_spec)
    if name_lower == 'peg_channel':
        return _phase_scores_peg_channel(episode_trace, task_spec)
    if name_lower == 'grasp_place':
        return _phase_scores_grasp_place(episode_trace, task_spec)
    return {'phase_score': 0.0}

def compute_sub_scores(task_name: str, episode_results: list[EpisodeTrace], task_spec=None) -> dict[str, float | str | None]:
    _PUSH_TASKS = {'planar_push', 'push_to_goal'}
    _PEG_TASKS = {'peg_insert', 'peg_channel'}
    name_lower = task_name.lower()
    if name_lower in _PUSH_TASKS:
        return _sub_scores_push(episode_results, task_spec)
    if name_lower == 'obstacle_reach':
        return _sub_scores_obstacle_reach(episode_results, task_spec)
    if name_lower in _PEG_TASKS:
        return _sub_scores_peg(episode_results, task_spec, task_name=name_lower)
    if name_lower == 'grasp_place':
        return _sub_scores_grasp_place(episode_results, task_spec)
    if name_lower in {'door_pull', 'door_push'}:
        return _sub_scores_door_pull(episode_results, task_spec)
    return {}

def compute_metrics(traces: list[EpisodeTrace], skill: Skill, lambda_penalty: float=0.05, task_spec=None, task_name: str | None=None, current_iteration: int=0, total_iterations: int=50, K_basin_runs: int=1) -> DesignMetrics:
    if not traces:
        raise ValueError('traces must be non-empty; received an empty list')
    per_trace_scores: list[float] = []
    _grasp_place_fitness_scores: list[float] = []
    _task_score_components: dict[str, float | str | None] = {}
    if task_spec is not None and getattr(task_spec, 'peg_body_name', None) is not None:
        sigma_lateral = 0.02
        lateral_tolerance = 0.005
        axial_threshold = float(task_spec.channel_length) if getattr(task_spec, 'channel_length', None) is not None else float(task_spec.goal_tolerance)
        axis = np.array(task_spec.channel_axis, dtype=float) if task_spec.channel_axis is not None else np.array([0.0, -1.0, 0.0])
        axis_norm = float(np.linalg.norm(axis))
        axis = axis / axis_norm if axis_norm > 1e-12 else np.array([0.0, -1.0, 0.0])
        scores = []
        idr_vals: list[float] = []
        lateral_vals: list[float] = []
        lateral_ok_vals: list[float] = []
        for t in traces:
            peg_final_pos = t.metadata.get('final_object_position')
            if peg_final_pos is None:
                scores.append(0.0)
                continue
            peg_start = _resolve_object_initial(t, task_spec)
            if peg_start is None:
                scores.append(0.0)
                continue
            peg_final = np.array(peg_final_pos[:3], dtype=float)
            delta = peg_final - peg_start
            axial_progress = float(np.dot(delta, axis))
            axis_xy = axis.copy()
            axis_xy[2] = 0.0
            axis_xy_norm = float(np.linalg.norm(axis_xy))
            if axis_xy_norm > 1e-12:
                axis_xy = axis_xy / axis_xy_norm
                delta_xy = delta.copy()
                delta_xy[2] = 0.0
                axial_xy = float(np.dot(delta_xy, axis_xy))
                lateral_disp = float(np.linalg.norm(delta_xy - axial_xy * axis_xy))
            else:
                lateral_disp = 0.0
            idr = float(np.clip(axial_progress / axial_threshold, 0.0, 1.0))
            lateral_excess = max(0.0, lateral_disp - lateral_tolerance)
            lateral_ok = float(np.exp(-lateral_excess / sigma_lateral))
            raw_score = idr * lateral_ok
            scores.append(raw_score)
            idr_vals.append(idr)
            lateral_vals.append(lateral_disp)
            lateral_ok_vals.append(lateral_ok)
        per_trace_scores = list(scores)
        task_score = float(np.clip(np.mean(scores), 0.0, 1.0))
        _task_score_components = {'formula': 'axial_progress_ratio_times_horizontal_lateral_tolerance', 'axial_progress_ratio': _nanmean(idr_vals), 'horizontal_lateral_error_m': _nanmean(lateral_vals), 'lateral_tolerance_m': lateral_tolerance, 'lateral_alignment': _nanmean(lateral_ok_vals)}
    elif task_spec is not None and getattr(task_spec, 'grasp_target_body', None) is not None:
        sigma = float(task_spec.expressivity_sigma)
        goal_tolerance = float(task_spec.goal_tolerance)
        grasp_ref = np.array(task_spec.grasp_approach_position if getattr(task_spec, 'grasp_approach_position', None) is not None else task_spec.goal_tcp_position, dtype=float)
        scores: list[float] = []
        _grasp_place_fitness_scores: list[float] = []
        for t in traces:
            _pt = t.metadata.get('phase_telemetry')
            _grasp_pt = _get_phase_telem(_pt, 'grasp')
            _descend_pt = _get_phase_telem(_pt, 'descend')
            _grasp_dist = _grasp_pt.get('tcp_to_object_dist_end')
            _descend_dist = _descend_pt.get('tcp_to_object_dist_end')
            _tcp_obj_dist = _grasp_dist if _grasp_dist is not None else _descend_dist
            if _tcp_obj_dist is not None:
                s1 = float(np.exp(-float(_tcp_obj_dist) / sigma))
            else:
                final_tcp = t.metadata.get('final_tcp_position')
                if final_tcp is not None:
                    dist1 = float(np.linalg.norm(np.array(final_tcp, dtype=float) - grasp_ref))
                    s1 = float(np.exp(-dist1 / sigma))
                else:
                    s1 = float(t.success)
            place_goal = _resolve_goal_position(t, task_spec, prefer_place=True)
            _lift_pt = _get_phase_telem(_pt, 'lift')
            _transport_pt = _get_phase_telem(_pt, 'transport_to_place') or _get_phase_telem(_pt, 'transport') or _get_phase_telem(_pt, 'place_1') or _get_phase_telem(_pt, 'approach_goal')
            _lift_obj_end = _lift_pt.get('object_pos_end') if _lift_pt else None
            _arc_pt_for_s2 = _get_phase_telem(_pt, 'transport_arc')
            _arc_z_max_for_s2 = _arc_pt_for_s2.get('object_z_max') if _arc_pt_for_s2 else None
            _transport_obj_end = _transport_pt.get('object_pos_end') if _transport_pt else None
            if _lift_obj_end is not None:
                s2 = 1.0 if float(_lift_obj_end[2]) > 0.11 else 0.0
            elif _arc_z_max_for_s2 is not None:
                s2 = 1.0 if float(_arc_z_max_for_s2) > 0.11 else 0.0
            elif _transport_obj_end is not None:
                _init_obj_arr = np.array(task_spec.object_initial_pose[:3], dtype=float) if getattr(task_spec, 'object_initial_pose', None) is not None else None
                if _init_obj_arr is not None:
                    _moved = float(np.linalg.norm(np.array(_transport_obj_end[:3], dtype=float) - _init_obj_arr))
                    s2 = min(1.0, _moved / 0.05)
                else:
                    s2 = 1.0
            else:
                obj_pos = t.metadata.get('final_object_position')
                if obj_pos is not None:
                    s2 = 1.0 if float(obj_pos[2]) > 0.11 else 0.0
                else:
                    s2 = 0.0
            obj_pos = t.metadata.get('final_object_position')
            if place_goal is not None:
                if obj_pos is not None:
                    dist3 = float(np.linalg.norm(np.array(obj_pos, dtype=float) - place_goal))
                    s3 = 1.0 if dist3 <= goal_tolerance else float(np.exp(-dist3 / sigma))
                else:
                    s3 = 0.0
                score = s3
                fitness = 0.25 * s1 + 0.25 * s2 + 0.5 * s3
            else:
                score = 0.5 * s1 + 0.5 * s2
                fitness = score
            scores.append(score)
            _grasp_place_fitness_scores.append(fitness)
        per_trace_scores = list(scores)
        task_score = float(np.clip(np.mean(scores), 0.0, 1.0))
        _task_score_components = {'formula': 'final_object_to_realised_3d_target', 'object_target_proximity': task_score, 'goal_tolerance_m': goal_tolerance}
    elif task_spec is not None and task_spec.goal_object_position is not None:
        sigma = float(task_spec.expressivity_sigma)
        scores = []
        dist_final_vals: list[float] = []
        dist_init_vals: list[float] = []
        for t in traces:
            goal = _resolve_goal_position(t, task_spec)
            init_obj = _resolve_object_initial(t, task_spec)
            obj_pos = t.metadata.get('final_object_position')
            if obj_pos is not None and init_obj is not None and (goal is not None):
                dist_final = float(np.linalg.norm(np.array(obj_pos[:3], dtype=float) - goal))
                dist_init = float(np.linalg.norm(init_obj - goal))
                dist_final_vals.append(dist_final)
                dist_init_vals.append(dist_init)
                if dist_init > 1e-09:
                    gp = float(np.clip(1.0 - dist_final / dist_init, 0.0, 1.0))
                else:
                    gp = 1.0
                scores.append(gp)
            elif obj_pos is not None and goal is not None:
                dist = float(np.linalg.norm(np.array(obj_pos[:3], dtype=float) - goal))
                scores.append(float(np.exp(-dist / sigma)))
            else:
                final_tcp = t.metadata.get('final_tcp_position')
                if final_tcp is not None:
                    dist = float(np.linalg.norm(np.array(final_tcp, dtype=float) - goal))
                    scores.append(float(np.exp(-dist / sigma)))
                else:
                    scores.append(float(t.success))
        per_trace_scores = list(scores)
        task_score = float(np.clip(np.mean(scores), 0.0, 1.0))
        _task_score_components = {'formula': 'realised_object_goal_progress', 'goal_progress': task_score, 'mean_final_object_goal_distance_m': _nanmean(dist_final_vals), 'mean_initial_object_goal_distance_m': _nanmean(dist_init_vals)}
    elif task_spec is not None and getattr(task_spec, 'hinge_joint_name', None) is not None:
        target_angle = float(task_spec.target_hinge_angle) if getattr(task_spec, 'target_hinge_angle', None) is not None else 0.524
        scores = []
        for t in traces:
            achieved_delta = _resolve_hinge_delta(t, task_spec)
            if achieved_delta is not None:
                ratio = float(np.clip(achieved_delta / max(target_angle, 1e-09), 0.0, 1.0))
                scores.append(ratio)
            else:
                traj = t.trajectory_positions
                if traj is not None and len(traj) >= 2:
                    arm_start = getattr(task_spec, 'arm_initial_tcp_position', None)
                    start_pos = np.array(arm_start[:3], dtype=float) if arm_start is not None else traj[0]
                    chord = float(np.linalg.norm(traj[-1] - start_pos))
                    _DOOR_HANDLE_RADIUS = 0.4
                    arc_angle_approx = chord / _DOOR_HANDLE_RADIUS
                    ratio = float(np.clip(arc_angle_approx / max(target_angle, 1e-09), 0.0, 1.0))
                    scores.append(ratio)
                else:
                    scores.append(0.0)
        per_trace_scores = list(scores)
        task_score = float(np.clip(np.mean(scores), 0.0, 1.0))
        _task_score_components = {'formula': 'door_hinge_delta_ratio', 'hinge_angle_ratio': task_score, 'target_hinge_delta_rad': target_angle}
    elif task_spec is not None and (task_name or '').lower() == 'peg_insert':
        scores = []
        for t in traces:
            goal = _resolve_goal_position(t, task_spec, infer_from_object_offset=True)
            if goal is None:
                scores.append(float(t.success))
                continue
            tcp_positions = t.metadata.get('tcp_positions', [])
            final_tcp = t.metadata.get('final_tcp_position')
            all_tcps: list = list(tcp_positions)
            if final_tcp is not None:
                all_tcps.append(final_tcp)
            if all_tcps:
                first_tcp = np.array(all_tcps[0][:3], dtype=float)
                initial_dist = float(np.linalg.norm(first_tcp - goal))
                if initial_dist < 1e-09:
                    scores.append(1.0)
                    continue
                min_dist = float('inf')
                for tcp_pos in all_tcps:
                    if tcp_pos is not None:
                        d = float(np.linalg.norm(np.array(tcp_pos[:3], dtype=float) - goal))
                        if d < min_dist:
                            min_dist = d
                dtg = float(np.clip(1.0 - min_dist / initial_dist, 0.0, 1.0))
                scores.append(dtg)
            else:
                scores.append(float(t.success))
        per_trace_scores = list(scores)
        task_score = float(np.clip(np.mean(scores), 0.0, 1.0))
        _task_score_components = {'formula': 'min_tcp_distance_to_realised_fixture_goal_ratio', 'distance_to_goal_ratio': task_score}
    elif task_spec is not None:
        sigma = float(task_spec.expressivity_sigma)
        _force_scale: float = float(getattr(task_spec, 'force_scale', 5.0))
        scores = []
        tcp_prox_vals: list[float] = []
        collision_vals: list[float] = []
        for t in traces:
            goal = _resolve_goal_position(t, task_spec)
            final_tcp = t.metadata.get('final_tcp_position')
            if final_tcp is not None and goal is not None:
                dist = float(np.linalg.norm(np.array(final_tcp, dtype=float) - goal))
                tcp_proximity_score = float(np.exp(-dist / sigma))
            else:
                tcp_proximity_score = float(t.success)
            tcp_prox_vals.append(tcp_proximity_score)
            if task_spec.obstacle_body_name is not None:
                obstacle_contact_force = float(t.metadata.get('peak_obstacle_force', 0.0))
                collision_factor = math.exp(-obstacle_contact_force / _force_scale)
                collision_vals.append(collision_factor)
                scores.append(tcp_proximity_score * collision_factor)
            else:
                scores.append(tcp_proximity_score)
        per_trace_scores = list(scores)
        task_score = float(np.clip(np.mean(scores), 0.0, 1.0))
        _task_score_components = {'formula': 'tcp_goal_proximity_times_collision_factor' if task_spec.obstacle_body_name is not None else 'tcp_goal_proximity', 'tcp_proximity_score': _nanmean(tcp_prox_vals)}
        if collision_vals:
            _task_score_components['collision_factor'] = _nanmean(collision_vals)
    else:
        successes = np.array([float(t.success) for t in traces])
        per_trace_scores = [float(t.success) for t in traces]
        task_score = float(np.clip(np.mean(successes), 0.0, 1.0))
        _task_score_components = {'formula': 'mean_binary_success'}
    per_episode_rates: list[float] = []
    all_displacements: list[float] = []
    for t in traces:
        telemetry = t.metadata.get('phase_telemetry')
        if telemetry:
            rates = [1.0 if p['terminated_normally'] else 0.0 for p in telemetry]
            per_episode_rates.append(float(np.mean(rates)))
            disps = [float(np.linalg.norm(np.array(p['tcp_end']) - np.array(p['tcp_start']))) for p in telemetry]
            all_displacements.extend(disps)
    phase_completion_rate = float(np.mean(per_episode_rates)) if per_episode_rates else None
    mean_phase_displacement = float(np.mean(all_displacements)) if all_displacements else None
    raw_task_score = task_score
    _task_name_lower = (task_name or '').lower()
    _blend_applied = False
    if _task_name_lower in _PHASE_BLEND_TASKS and phase_completion_rate is not None:
        _alpha = 0.5
        task_score = float(np.clip(_alpha * raw_task_score + (1.0 - _alpha) * phase_completion_rate, 0.0, 1.0))
        _blend_applied = True
    _phase_score_applied: bool = False
    _phase_score_value: float = 0.0
    _phase_breakdown: dict = {}
    _has_phase_telemetry: bool = any((bool(t.metadata.get('phase_telemetry')) for t in traces))
    _telemetry_phase_names: set[str] = set()
    if _has_phase_telemetry:
        for t in traces:
            telemetry = t.metadata.get('phase_telemetry') or []
            for phase in telemetry:
                phase_name = str(phase.get('phase_name', '')).strip().lower()
                if phase_name:
                    _telemetry_phase_names.add(phase_name)
                _phase_type_val = phase.get('phase_type')
                if _phase_type_val is not None:
                    _pt_str = str(_phase_type_val).strip().lower()
                    if _pt_str:
                        _telemetry_phase_names.add(_pt_str)
    _phase_aliases = getattr(task_spec, 'phase_type_aliases', None)
    if task_spec is not None and isinstance(_phase_aliases, dict) and _phase_aliases:
        _alias_expansions: set[str] = set()
        for (_a, _canonical) in _phase_aliases.items():
            if _a in _telemetry_phase_names:
                _alias_expansions.add(_canonical)
        _telemetry_phase_names |= _alias_expansions
    _required_phase_names = _PHASE_SCORING_REQUIRED_PHASES.get(_task_name_lower, frozenset())
    _has_sufficient_required_phase_names = len(_telemetry_phase_names.intersection(_required_phase_names)) >= 2 if _required_phase_names else True
    if _task_name_lower in _PHASE_SCORING_TASKS and task_spec is not None and _has_phase_telemetry and _has_sufficient_required_phase_names:
        per_trace_phase_scores = [_compute_phase_scores(t, task_spec, _task_name_lower) for t in traces]
        _phase_score_value = float(np.clip(np.mean([ps['phase_score'] for ps in per_trace_phase_scores]), 0.0, 1.0))
        all_keys = set().union(*per_trace_phase_scores)
        _phase_breakdown = {k: float(np.mean([ps.get(k, 0.0) for ps in per_trace_phase_scores])) for k in all_keys if k != 'phase_score'}
        _phase_score_applied = True
    _tr = _termination_reliability_from_traces(traces)
    if _tr is not None:
        termination_fidelity = float(_tr)
    else:
        termination_fidelity = 0.0
    _force_limit_val: float = float(task_spec.force_limit) if task_spec is not None and hasattr(task_spec, 'force_limit') else _FORCE_COMPLIANCE_FALLBACK_THRESHOLD
    if traces:
        under_force_limit = [t.peak_contact_force < _force_limit_val for t in traces]
        force_compliance = float(np.clip(np.mean(under_force_limit), 0.0, 1.0))
    else:
        force_compliance = 0.0
    n_params = skill.param_dim
    n_phases = len(skill.phases)
    complexity_penalty = float(np.clip(lambda_penalty * n_params + _LAMBDA_PHASES_END * max(0, n_phases - _BASELINE_PHASES), 0.0, 1.0))
    task_subscores: dict[str, float | str | None] = {}
    if _blend_applied:
        task_subscores['raw_task_score'] = raw_task_score
    if task_name is not None:
        task_subscores.update(compute_sub_scores(task_name, traces, task_spec))
    if _phase_score_applied:
        task_subscores['terminal_score'] = raw_task_score
        task_subscores['phase_score'] = _phase_score_value
        for (k, v) in _phase_breakdown.items():
            task_subscores[f'phase_breakdown.{k}'] = float(v)
    _grasp_place_fitness_value: float | None = None
    if _grasp_place_fitness_scores:
        _grasp_place_fitness_value = float(np.clip(np.mean(_grasp_place_fitness_scores), 0.0, 1.0))
        task_subscores['grasp_place_fitness'] = _grasp_place_fitness_value
    if _task_name_lower == 'grasp_place' and _grasp_place_fitness_value is not None:
        fitness_score = _grasp_place_fitness_value
        optimiser_fitness_components: dict[str, float | str | None] = {'formula': '0.25*grasp_proximity + 0.25*lift + 0.50*object_target_proximity', 'grasp_place_fitness': _grasp_place_fitness_value, 'canonical_task_score': task_score}
    elif _task_name_lower in ('push_to_goal', 'peg_channel', 'peg_insert') and _phase_score_applied:
        fitness_score = float(np.clip(0.4 * raw_task_score + 0.6 * _phase_score_value, 0.0, 1.0))
        optimiser_fitness_components = {'formula': '0.4*canonical_task_score + 0.6*phase_score', 'canonical_task_score': raw_task_score, 'phase_score': _phase_score_value}
    else:
        fitness_score = task_score
        optimiser_fitness_components = {'formula': 'canonical_task_score', 'canonical_task_score': task_score}
    composite_score = fitness_score + termination_fidelity - complexity_penalty
    skill_parameter_optimisation_scores: dict[str, float] = {}
    if K_basin_runs > 1:
        skill_parameter_optimisation_scores['K_basin_runs'] = float(K_basin_runs)
    _has_subtasks = task_spec is not None and getattr(task_spec, 'subtasks', None) is not None
    _has_ptm = task_spec is not None and getattr(task_spec, 'phase_target_map', None) is not None
    _opt_signal = 'fixed_subtasks' if _has_subtasks or _has_ptm else 'task_score_only'
    (_randomised_state, _episode_states) = _representative_task_state(traces)
    safety_diagnostics: dict[str, float | str | None] = {'force_compliance': force_compliance, 'force_limit': _force_limit_val, 'mean_peak_contact_force': float(np.mean([t.peak_contact_force for t in traces])) if traces else 0.0, 'max_peak_contact_force': float(np.max([t.peak_contact_force for t in traces])) if traces else 0.0}
    if _task_name_lower == 'obstacle_reach':
        safety_diagnostics['mean_peak_obstacle_force'] = float(np.mean([float((t.metadata or {}).get('peak_obstacle_force', 0.0)) for t in traces]))
    termination_diagnostics: dict[str, float | str | None] = {'termination_fidelity': termination_fidelity, 'phase_completion_rate': phase_completion_rate, 'mean_phase_displacement': mean_phase_displacement}
    return DesignMetrics(task_score=task_score, termination_fidelity=termination_fidelity, complexity_penalty=complexity_penalty, composite_score=composite_score, LAMBDA=lambda_penalty, phase_completion_rate=phase_completion_rate, mean_phase_displacement=mean_phase_displacement, force_compliance=force_compliance, fitness_score=fitness_score, task_subscores=task_subscores, task_score_components=_task_score_components, optimiser_fitness_components=optimiser_fitness_components, safety_diagnostics=safety_diagnostics, termination_diagnostics=termination_diagnostics, randomised_task_state=_randomised_state, episode_task_state=_episode_states, skill_parameter_optimisation_scores=skill_parameter_optimisation_scores, optimiser_diagnostics=skill_parameter_optimisation_scores, optimisation_signal_source=_opt_signal, metrics_version=METRICS_SCHEMA_VERSION)
