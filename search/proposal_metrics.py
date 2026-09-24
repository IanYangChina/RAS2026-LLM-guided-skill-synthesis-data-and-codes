from __future__ import annotations
import datetime as _dt
import hashlib
import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal
from dsl import serialiser
from dsl.nodes import Skill
from dsl.validator import validate
from evaluation.task_spec import TaskSpec
from search.archive import SkillArchive, _NumpyEncoder
from search.structural_diff import classify_repair_types, structural_diff
Confidence = Literal['exact', 'recomputed', 'approximate', 'unavailable']
_RULE_SOURCE = 'rule_based_skill_structure'
_LARGE_IMPROVEMENT = 0.1
_DESTRUCTIVE_DROP = -0.05

@dataclass(frozen=True)
class SkillYamlDiagnostics:
    yaml_hash: str | None
    yaml_parse_status: str
    dsl_valid: bool | None
    validation_error: str | None
    n_phases: int | None
    n_params: int | None
    phase_types: tuple[str, ...]
    generator_types: tuple[str, ...]
    control_modes: tuple[str, ...]
    termination_conditions: tuple[str, ...]
    end_effector_actions: tuple[str, ...]
    critical_primitives: tuple[str, ...]
    confidence: Confidence
    semantic_valid: bool | None = None
    semantic_validity: dict[str, Any] | None = None
    critical_primitive_results: tuple[dict[str, Any], ...] = ()
    skill: Any | None = None

def _json_dumps(obj: Any, **kwargs: Any) -> str:
    return json.dumps(obj, cls=_NumpyEncoder, **kwargs)

def stable_yaml_hash(yaml_text: str | None) -> str | None:
    if yaml_text is None:
        return None
    return hashlib.sha256(yaml_text.strip().encode('utf-8')).hexdigest()

def skill_hash(skill: Skill | None) -> str | None:
    if skill is None:
        return None
    return SkillArchive._skill_hash(skill)

def _phase_type(phase: Any) -> str:
    return phase.phase_type.value

def _enum_name(value: Any) -> str | None:
    return getattr(value, 'name', '').lower() or None

def _skill_tokens(skill: Skill) -> dict[str, Any]:
    phases = tuple(skill.phases)
    phase_types = tuple((_phase_type(p) for p in phases))
    generator_types = tuple((_enum_name(p.generator) for p in phases if p.generator is not None))
    control_modes = tuple((_enum_name(p.control) for p in phases if p.control is not None))
    terminations = tuple((_enum_name(p.termination) for p in phases if p.termination is not None))
    actions = tuple((_enum_name(p.end_effector_action) for p in phases if p.end_effector_action is not None))
    ids = tuple((str(p.phase_id).lower() for p in phases))
    param_names = tuple((pname.lower() for p in phases for (pname, _param) in getattr(p, 'parameters', None) or ()))
    return {'phases': phases, 'phase_types': phase_types, 'generator_types': generator_types, 'control_modes': control_modes, 'termination_conditions': terminations, 'end_effector_actions': actions, 'phase_ids': ids, 'param_names': param_names}

def _has_ordered(indices_a: list[int], indices_b: list[int]) -> bool:
    return bool(indices_a and indices_b and (min(indices_a) < max(indices_b)))

def semantic_validity_for_task(skill: Skill | None, task: str | None) -> dict[str, Any]:
    if skill is None:
        return {'value': None, 'confidence': 'unavailable', 'source': _RULE_SOURCE, 'reason': 'skill unavailable'}
    if task is None:
        return {'value': None, 'confidence': 'unavailable', 'source': _RULE_SOURCE, 'reason': 'task unavailable'}
    t = _skill_tokens(skill)
    phase_types = t['phase_types']
    generators = set(t['generator_types'])
    controls = set(t['control_modes'])
    terms = set(t['termination_conditions'])
    actions = t['end_effector_actions']
    ids = t['phase_ids']
    params = set(t['param_names'])
    if task == 'obstacle_reach':
        has_clearance = bool({'arc_cartesian', 'bezier_curve'} & generators or {'lift', 'retract'} & set(phase_types) or any(('height' in p or 'clearance' in p or 'arc' in p for p in params)))
        has_reach_motion = bool({'approach', 'descend', 'retract'} & set(phase_types))
        value = has_clearance and has_reach_motion
        reason = 'clearance trajectory present' if value else 'missing clearance trajectory primitive'
    elif task == 'grasp_place':
        grasp_i = [i for (i, p) in enumerate(t['phases']) if _phase_type(p) == 'grasp' or _enum_name(p.end_effector_action) in {'close', 'force_grasp'}]
        release_i = [i for (i, p) in enumerate(t['phases']) if _phase_type(p) == 'release' or _enum_name(p.end_effector_action) == 'open']
        move_i = [i for (i, p) in enumerate(t['phases']) if _phase_type(p) in {'lift', 'retract'} or any((tok in str(p.phase_id).lower() for tok in ('lift', 'transport', 'place'))) or (p.generator is not None and _enum_name(p.generator) in {'arc_cartesian', 'bezier_curve'})]
        value = bool(grasp_i and release_i and move_i and (min(grasp_i) < max(move_i) < max(release_i)))
        reason = 'grasp-lift/transport-release ordering present' if value else 'missing grasp -> lift/transport -> release ordering'
    elif task == 'peg_channel':
        contact_i = [i for (i, p) in enumerate(t['phases']) if _phase_type(p) == 'contact' or _enum_name(p.control) in {'force_threshold_switch', 'force_control'} or _enum_name(p.termination) in {'contact_detected', 'force_exceeded'}]
        push_i = [i for (i, p) in enumerate(t['phases']) if _phase_type(p) == 'push' or 'push' in str(p.phase_id).lower() or any(('push' in pname or 'channel' in pname or 'depth' in pname for (pname, _) in p.parameters))]
        has_progress = bool(push_i and ('impedance_control' in controls or 'force_control' in controls or 'time_limit' in terms))
        value = _has_ordered(contact_i, push_i) and has_progress
        reason = 'contact/push/channel-progress pattern present' if value else 'missing ordered contact/push/channel-progress pattern'
    else:
        return {'value': None, 'confidence': 'unavailable', 'source': _RULE_SOURCE, 'reason': f'no semantic predicate registered for task {task!r}'}
    return {'value': bool(value), 'confidence': 'recomputed', 'source': _RULE_SOURCE, 'reason': reason}

def critical_primitive_results_for_task(skill: Skill | None, task: str | None) -> tuple[dict[str, Any], ...]:
    if skill is None or task is None:
        return ()
    t = _skill_tokens(skill)
    phase_set = set(t['phase_types'])
    gen_set = set(t['generator_types'])
    action_set = set(t['end_effector_actions'])
    control_set = set(t['control_modes'])
    term_set = set(t['termination_conditions'])
    ids = t['phase_ids']
    param_names = set(t['param_names'])
    specs: list[tuple[str, bool]] = []
    if task == 'obstacle_reach':
        specs = [('clearance_trajectory', bool({'arc_cartesian', 'bezier_curve'} & gen_set or {'lift', 'retract'} & phase_set)), ('approach_or_descend', bool({'approach', 'descend'} & phase_set))]
    elif task == 'grasp_place':
        specs = [('grasp_action', bool('grasp' in phase_set or {'close', 'force_grasp'} & action_set)), ('lift_or_transport', bool({'lift', 'retract'} & phase_set or any(('transport' in pid for pid in ids)))), ('release_action', bool('release' in phase_set or 'open' in action_set))]
    elif task == 'peg_channel':
        specs = [('contact_detection', bool('contact' in phase_set or {'contact_detected', 'force_exceeded'} & term_set)), ('push_phase', bool('push' in phase_set or any(('push' in pid for pid in ids)))), ('channel_progress_parameter', bool(any(('push' in p or 'depth' in p or 'channel' in p for p in param_names)))), ('force_or_impedance_control', bool({'force_threshold_switch', 'force_control', 'impedance_control'} & control_set))]
    return tuple(({'name': name, 'present': bool(present), 'confidence': 'recomputed', 'source': _RULE_SOURCE} for (name, present) in specs))

def critical_primitives_for_task(*, task: str | None, phase_types: tuple[str, ...], generator_types: tuple[str, ...], end_effector_actions: tuple[str, ...]) -> tuple[str, ...]:
    primitives: list[str] = []
    phase_set = set(phase_types)
    generator_set = set(generator_types)
    action_set = set(end_effector_actions)
    if 'arc_cartesian' in generator_set:
        primitives.append('arc_cartesian_generator')
    if 'contact' in phase_set:
        primitives.append('contact_phase')
    if 'push' in phase_set:
        primitives.append('push_phase')
    if 'grasp' in action_set or 'force_grasp' in action_set:
        primitives.append('grasp_action')
    if 'release' in action_set or 'open' in action_set:
        primitives.append('release_action')
    if task == 'obstacle_reach':
        if 'arc_cartesian' in generator_set:
            primitives.append('task_obstacle_arc')
        if 'retract' in phase_set:
            primitives.append('task_obstacle_retract')
    elif task == 'grasp_place':
        if 'grasp' in action_set or 'force_grasp' in action_set:
            primitives.append('task_grasp')
        if 'release' in action_set or 'open' in action_set:
            primitives.append('task_release')
        if {'lift', 'transport', 'retract'} & phase_set or 'arc_cartesian' in generator_set:
            primitives.append('task_lift_or_transport')
    elif task == 'peg_channel':
        if 'contact' in phase_set:
            primitives.append('task_channel_contact')
        if 'push' in phase_set:
            primitives.append('task_channel_push')
    return tuple(sorted(set(primitives)))

def valid_subtask_binding(skill: Skill | None, task_spec: TaskSpec | None, subtask_mode: str='fixed') -> dict[str, Any]:
    if skill is None:
        return {'value': None, 'confidence': 'unavailable', 'source': 'subtask_binding_check', 'reason': 'skill unavailable'}
    if subtask_mode == 'free':
        declared = {str(d.get('id')) for d in getattr(skill, 'skill_subtasks', None) or () if d.get('id')}
        missing_fields = [str(d.get('id', '<unknown>')) for d in getattr(skill, 'skill_subtasks', None) or () if 'anchor' not in d or 'target_entity' not in d]
        refs = {p.subtask_id for p in skill.phases if p.subtask_id}
        ok = not missing_fields and (not refs or refs <= declared)
        reason = 'free subtask bindings valid' if ok else f'invalid free subtask binding; missing_fields={missing_fields}; unknown_refs={sorted(refs - declared)}'
        return {'value': ok, 'confidence': 'recomputed', 'source': 'subtask_binding_check', 'reason': reason}
    if task_spec is None:
        return {'value': None, 'confidence': 'unavailable', 'source': 'subtask_binding_check', 'reason': 'task_spec unavailable'}
    allowed = {st.id for st in task_spec.subtasks or ()}
    refs = {p.subtask_id for p in skill.phases if p.subtask_id}
    ok = refs <= allowed
    reason = 'fixed subtask bindings valid' if ok else f'unknown fixed subtask refs={sorted(refs - allowed)}'
    return {'value': ok, 'confidence': 'recomputed', 'source': 'subtask_binding_check', 'reason': reason}

def analyse_skill_yaml(yaml_text: str | None, *, task: str | None=None) -> SkillYamlDiagnostics:
    yaml_hash = stable_yaml_hash(yaml_text)
    empty = dict(yaml_hash=yaml_hash, yaml_parse_status='unavailable', dsl_valid=None, validation_error='skill YAML was not stored', n_phases=None, n_params=None, phase_types=(), generator_types=(), control_modes=(), termination_conditions=(), end_effector_actions=(), critical_primitives=(), confidence='unavailable', semantic_valid=None, semantic_validity={'value': None, 'confidence': 'unavailable', 'source': _RULE_SOURCE, 'reason': 'skill YAML was not stored'}, critical_primitive_results=(), skill=None)
    if not yaml_text:
        return SkillYamlDiagnostics(**empty)
    try:
        skill = serialiser.load_skill(yaml_text)
    except Exception as exc:
        empty.update(yaml_parse_status='parse_error', dsl_valid=False, validation_error=str(exc), confidence='recomputed')
        return SkillYamlDiagnostics(**empty)
    errors = validate(skill)
    tokens = _skill_tokens(skill)
    semantic = semantic_validity_for_task(skill, task)
    primitive_results = critical_primitive_results_for_task(skill, task)
    return SkillYamlDiagnostics(yaml_hash=yaml_hash, yaml_parse_status='ok', dsl_valid=not errors, validation_error='\n'.join((error.message for error in errors)) or None, n_phases=len(skill.phases), n_params=skill.param_dim, phase_types=tokens['phase_types'], generator_types=tuple((x for x in tokens['generator_types'] if x)), control_modes=tuple((x for x in tokens['control_modes'] if x)), termination_conditions=tuple((x for x in tokens['termination_conditions'] if x)), end_effector_actions=tuple((x for x in tokens['end_effector_actions'] if x)), critical_primitives=critical_primitives_for_task(task=task, phase_types=tokens['phase_types'], generator_types=tuple((x for x in tokens['generator_types'] if x)), end_effector_actions=tuple((x for x in tokens['end_effector_actions'] if x))), confidence='recomputed', semantic_valid=semantic['value'], semantic_validity=semantic, critical_primitive_results=primitive_results, skill=skill)

def recompute_structural_diff(parent_yaml: str | None, child_yaml: str | None) -> tuple[dict[str, Any] | None, str | None]:
    parent = analyse_skill_yaml(parent_yaml)
    child = analyse_skill_yaml(child_yaml)
    if parent.skill is None:
        return (None, f'parent unavailable or invalid: {parent.validation_error}')
    if child.skill is None:
        return (None, f'child unavailable or invalid: {child.validation_error}')
    return (structural_diff(parent.skill, child.skill), None)

def _metric_value(metrics: Any, name: str) -> float | None:
    if metrics is None:
        return None
    if isinstance(metrics, dict):
        value = metrics.get(name)
    else:
        value = getattr(metrics, name, None)
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None

def proposal_delta_fields(parent_metrics: Any, candidate_metrics: Any) -> dict[str, Any]:
    parent_task = _metric_value(parent_metrics, 'task_score')
    cand_task = _metric_value(candidate_metrics, 'task_score')
    parent_comp = _metric_value(parent_metrics, 'composite_score')
    cand_comp = _metric_value(candidate_metrics, 'composite_score')
    delta_task = None if parent_task is None or cand_task is None else cand_task - parent_task
    delta_comp = None if parent_comp is None or cand_comp is None else cand_comp - parent_comp
    return {'delta_task_score': delta_task, 'delta_composite_score': delta_comp, 'improved': None if delta_task is None else delta_task > 0.0, 'large_improvement': None if delta_task is None else delta_task >= _LARGE_IMPROVEMENT, 'destructive': None if delta_task is None else delta_task <= _DESTRUCTIVE_DROP}

def build_evaluated_proposal_metrics(*, task: str | None, candidate_skill: Skill | None, parent_skill: Skill | None=None, candidate_yaml: str | None=None, parent_yaml: str | None=None, candidate_metrics: Any=None, parent_metrics: Any=None, task_spec: TaskSpec | None=None, subtask_mode: str='fixed', proposal_source: str | None=None, accepted_as_elite: bool | None=None, parse_status: str | None=None) -> dict[str, Any]:
    if candidate_yaml is None and candidate_skill is not None:
        candidate_yaml = serialiser.dump_skill(candidate_skill)
    if parent_yaml is None and parent_skill is not None:
        parent_yaml = serialiser.dump_skill(parent_skill)
    if candidate_skill is None and candidate_yaml:
        candidate_skill = analyse_skill_yaml(candidate_yaml, task=task).skill
    if parent_skill is None and parent_yaml:
        parent_skill = analyse_skill_yaml(parent_yaml, task=task).skill
    cand_diag = analyse_skill_yaml(candidate_yaml, task=task) if candidate_yaml else None
    semantic = semantic_validity_for_task(candidate_skill, task)
    critical_results = critical_primitive_results_for_task(candidate_skill, task)
    binding = valid_subtask_binding(candidate_skill, task_spec, subtask_mode)
    diff = structural_diff(parent_skill, candidate_skill) if parent_skill is not None and candidate_skill is not None else None
    repair_types = classify_repair_types(diff)
    deltas = proposal_delta_fields(parent_metrics, candidate_metrics)
    if deltas['destructive'] is True and 'destructive' not in repair_types:
        repair_types = (*repair_types, 'destructive')
    return {'proposal_source': proposal_source, 'parent_skill_hash': skill_hash(parent_skill), 'candidate_skill_hash': skill_hash(candidate_skill), 'parent_yaml_hash': stable_yaml_hash(parent_yaml), 'candidate_yaml_hash': stable_yaml_hash(candidate_yaml), **deltas, 'accepted_as_elite': accepted_as_elite, 'valid_yaml': None if candidate_yaml is None else cand_diag.yaml_parse_status == 'ok' if cand_diag else None, 'valid_dsl': cand_diag.dsl_valid if cand_diag else None, 'valid_subtask_binding': binding['value'], 'validity': {'yaml': None if candidate_yaml is None else cand_diag.yaml_parse_status == 'ok' if cand_diag else None, 'dsl': cand_diag.dsl_valid if cand_diag else None, 'subtask_binding': binding}, 'semantic_valid': semantic['value'], 'semantic_validity': semantic, 'critical_primitives': [r['name'] for r in critical_results if r['present']], 'critical_primitive_results': list(critical_results), 'repair_types': list(repair_types), 'repair_label': repair_types[0] if repair_types else None, 'structural_diff': diff, 'proposal_metrics_confidence': {'validity': 'recomputed' if candidate_yaml else 'unavailable', 'semantic_valid': semantic['confidence'], 'critical_primitives': 'recomputed' if critical_results else 'unavailable', 'repair_types': 'recomputed' if diff is not None else 'unavailable', 'delta': 'exact' if deltas['delta_task_score'] is not None or deltas['delta_composite_score'] is not None else 'unavailable'}, 'proposal_parse_status': parse_status}

def build_attempt_record(*, iteration: int | str, attempt_kind: str, proposal_source: str, task: str | None, candidate_yaml: str | None, parent_skill: Skill | None=None, parent_yaml: str | None=None, task_spec: TaskSpec | None=None, subtask_mode: str='fixed', condition: str | None=None, accepted: bool | None=None, parse_status: str | None=None, error: str | None=None, elapsed_s: float | None=None, extra: dict[str, Any] | None=None) -> dict[str, Any]:
    diag = analyse_skill_yaml(candidate_yaml, task=task)
    semantic = semantic_validity_for_task(diag.skill, task)
    binding = valid_subtask_binding(diag.skill, task_spec, subtask_mode) if diag.skill is not None else {'value': None, 'confidence': 'unavailable', 'source': 'subtask_binding_check', 'reason': 'skill unavailable'}
    record = {'timestamp_utc': _dt.datetime.utcnow().isoformat(), 'iteration': iteration, 'attempt_kind': attempt_kind, 'proposal_source': proposal_source, 'condition': condition, 'parent_skill_hash': skill_hash(parent_skill), 'parent_yaml_hash': stable_yaml_hash(parent_yaml), 'candidate_skill_hash': skill_hash(diag.skill), 'candidate_yaml_hash': diag.yaml_hash, 'yaml_parse_status': diag.yaml_parse_status, 'valid_yaml': diag.yaml_parse_status == 'ok' if candidate_yaml else None, 'valid_dsl': diag.dsl_valid, 'valid_subtask_binding': binding['value'], 'semantic_valid': semantic['value'], 'semantic_validity': semantic, 'critical_primitives': list(diag.critical_primitives), 'critical_primitive_results': list(diag.critical_primitive_results), 'parse_status': parse_status, 'accepted': accepted, 'error': error or diag.validation_error, 'elapsed_s': elapsed_s, 'confidence': {'validity': diag.confidence, 'semantic_valid': semantic['confidence'], 'critical_primitives': diag.confidence}}
    if extra:
        record.update(extra)
    return record

def append_jsonl(path: Path, record: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('a', encoding='utf-8') as fh:
        fh.write(_json_dumps(record, sort_keys=True) + '\n')
        fh.flush()
        os.fsync(fh.fileno())

def append_proposal_attempt(path: Path, record: dict[str, Any]) -> None:
    append_jsonl(path, record)
