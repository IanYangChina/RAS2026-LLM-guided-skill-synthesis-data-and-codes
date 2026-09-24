from __future__ import annotations
import math
import pathlib
from dataclasses import asdict, dataclass
from typing import Any
from dsl.grammar import ALLOWED_PHASE_TYPES, DSL_V2, MAX_PARAMS_PER_PHASE, MAX_PHASES, MIN_PHASES, V2_ALIGN_WITH_NAMES, V2_AXIS_NAMES, V2_AXIS_SIGNS, V2_BINDING_FRAMES, V2_BINDING_MODES, V2_ENTITY_FORBIDDEN_ANCHORS, V2_ENTITY_REQUIRED_ANCHORS, V2_GUARD_FAILURE_ACTIONS, V2_GUARD_PREDICATES, V2_GUARD_WHENS, V2_MIGRATION_TARGET_SOURCES, V2_OFFSET_AXIS_MODES, V2_ORIENTATION_MODES, V2_REJECTED_BINDING_PATHS, V2_RETRY_STRATEGIES, V2_SUPPORTED_BINDING_PATHS, V2_TARGET_ANCHORS, V2_TARGET_SOURCES, V2_XYZ_TARGET_FORBIDDEN_ANCHORS
from dsl.nodes import BindingConsumptionRecord, ControlMode, GeneratorType, ParameterConsumptionEntry, ParameterType, Phase, Skill, TerminationCond

@dataclass(frozen=True)
class ValidationError:
    message: str

def _is_finite(value: float) -> bool:
    return math.isfinite(float(value))

def _finite_vec(values: tuple[float, ...] | None) -> bool:
    return values is not None and all((_is_finite(v) for v in values))

def _non_zero_vec(values: tuple[float, ...] | None) -> bool:
    return _finite_vec(values) and math.sqrt(sum((float(v) ** 2 for v in values or ()))) > 0.0

def _base_validate(skill: Skill) -> list[ValidationError]:
    errors: list[ValidationError] = []
    num_phases = len(skill.phases)
    if num_phases < MIN_PHASES:
        errors.append(ValidationError(f"Skill '{skill.name}' has {num_phases} phase(s); minimum is {MIN_PHASES}."))
    if num_phases > MAX_PHASES:
        errors.append(ValidationError(f"Skill '{skill.name}' has {num_phases} phase(s); maximum is {MAX_PHASES}."))
    seen_phase_ids: set[str] = set()
    for phase in skill.phases:
        if phase.phase_id in seen_phase_ids:
            errors.append(ValidationError(f"Duplicate phase_id '{phase.phase_id}' in skill '{skill.name}'."))
        else:
            seen_phase_ids.add(phase.phase_id)
    for phase in skill.phases:
        if phase.phase_type not in ALLOWED_PHASE_TYPES:
            errors.append(ValidationError(f"Phase '{phase.phase_id}' in skill '{skill.name}' has unknown phase_type '{phase.phase_type}'; allowed types: {sorted((pt.value for pt in ALLOWED_PHASE_TYPES))}."))
    for phase in skill.phases:
        n_params = len(phase.parameters)
        if n_params > MAX_PARAMS_PER_PHASE:
            errors.append(ValidationError(f"Phase '{phase.phase_id}' in skill '{skill.name}' has {n_params} parameter(s); maximum per phase is {MAX_PARAMS_PER_PHASE}."))
    for phase in skill.phases:
        seen_param_names: set[str] = set()
        for (pname, _) in phase.parameters:
            if pname in seen_param_names:
                errors.append(ValidationError(f"Duplicate parameter name '{pname}' in phase '{phase.phase_id}' of skill '{skill.name}'."))
            else:
                seen_param_names.add(pname)
    for phase in skill.phases:
        for (pname, pparam) in phase.parameters:
            (lo, hi) = pparam.range
            if lo >= hi:
                errors.append(ValidationError(f"Parameter '{pname}' in phase '{phase.phase_id}' of skill '{skill.name}' has invalid range [{lo}, {hi}]: lower bound must be strictly less than upper bound."))
    for phase in skill.phases:
        if phase.generator is None and phase.end_effector_action is None:
            errors.append(ValidationError(f"Phase '{phase.phase_id}' in skill '{skill.name}' has neither a generator nor an end_effector_action — the phase does nothing."))
    return errors

def _validate_target(skill: Skill, phase: Phase, allow_migration: bool) -> list[ValidationError]:
    errors: list[ValidationError] = []
    target = phase.target
    if target is None:
        return [ValidationError(f"DSL v2 phase '{phase.phase_id}' must declare a target block.")]
    if target.source in V2_MIGRATION_TARGET_SOURCES and (not allow_migration):
        errors.append(ValidationError(f"Phase '{phase.phase_id}' uses target.source '{target.source}', which is migration/test-only for active DSL v2; use source: yaml."))
    elif target.source not in V2_TARGET_SOURCES and target.source not in V2_MIGRATION_TARGET_SOURCES:
        errors.append(ValidationError(f"Phase '{phase.phase_id}' has unsupported target.source '{target.source}'."))
    if target.anchor not in V2_TARGET_ANCHORS:
        errors.append(ValidationError(f"Phase '{phase.phase_id}' has unsupported target.anchor '{target.anchor}'."))
    if target.anchor in V2_ENTITY_FORBIDDEN_ANCHORS and target.entity is not None:
        errors.append(ValidationError(f"Phase '{phase.phase_id}' target anchor '{target.anchor}' forbids entity."))
    if target.anchor in V2_ENTITY_REQUIRED_ANCHORS and (not target.entity):
        errors.append(ValidationError(f"Phase '{phase.phase_id}' target anchor '{target.anchor}' requires entity."))
    if target.anchor in V2_XYZ_TARGET_FORBIDDEN_ANCHORS:
        errors.append(ValidationError(f"Phase '{phase.phase_id}' target anchor '{target.anchor}' is not valid as an XYZ motion target."))
    if not _finite_vec(target.offset):
        errors.append(ValidationError(f"Phase '{phase.phase_id}' target.offset must be finite."))
    if target.tolerance is not None and (not _is_finite(target.tolerance) or target.tolerance < 0.0):
        errors.append(ValidationError(f"Phase '{phase.phase_id}' target.tolerance must be finite and non-negative."))
    offset_axis = target.offset_along_axis
    if offset_axis is not None:
        if offset_axis.axis not in V2_AXIS_NAMES:
            errors.append(ValidationError(f"Phase '{phase.phase_id}' has unsupported offset_along_axis.axis '{offset_axis.axis}'."))
        if offset_axis.mode not in V2_OFFSET_AXIS_MODES:
            errors.append(ValidationError(f"Phase '{phase.phase_id}' has unsupported offset_along_axis.mode '{offset_axis.mode}'."))
        if offset_axis.sign not in V2_AXIS_SIGNS:
            errors.append(ValidationError(f"Phase '{phase.phase_id}' has unsupported offset_along_axis.sign '{offset_axis.sign}'."))
        if not _is_finite(offset_axis.distance):
            errors.append(ValidationError(f"Phase '{phase.phase_id}' offset_along_axis.distance must be finite."))
    orientation = target.orientation
    if orientation is not None:
        if orientation.mode not in V2_ORIENTATION_MODES:
            errors.append(ValidationError(f"Phase '{phase.phase_id}' has unsupported orientation mode '{orientation.mode}'."))
        if orientation.mode == 'quat':
            if not _non_zero_vec(orientation.quat):
                errors.append(ValidationError(f"Phase '{phase.phase_id}' orientation mode quat requires a non-zero finite quat."))
        if orientation.mode == 'align_axis':
            if not _non_zero_vec(orientation.axis):
                errors.append(ValidationError(f"Phase '{phase.phase_id}' orientation mode align_axis requires a non-zero finite axis."))
            if orientation.align_with not in V2_ALIGN_WITH_NAMES:
                errors.append(ValidationError(f"Phase '{phase.phase_id}' has unsupported align_axis align_with '{orientation.align_with}'."))
        if orientation.tolerance is not None and (not _is_finite(orientation.tolerance) or orientation.tolerance < 0.0):
            errors.append(ValidationError(f"Phase '{phase.phase_id}' orientation.tolerance must be finite and non-negative."))
    return errors

def _phase_has_force_limit_consumer(phase: Phase) -> bool:
    return phase.control in {ControlMode.IMPEDANCE_CONTROL, ControlMode.ADMITTANCE_CONTROL, ControlMode.FORCE_THRESHOLD_SWITCH, ControlMode.FORCE_CONTROL}

def _binding_consumer_error(phase: Phase, path: str) -> str | None:
    if path.startswith('guards.') and path.endswith('.threshold'):
        guard_id = path[len('guards.'):-len('.threshold')]
        if guard_id not in {guard.guard_id for guard in phase.guards}:
            return f"guard id '{guard_id}' does not exist in phase '{phase.phase_id}'"
        return None
    if path in V2_REJECTED_BINDING_PATHS:
        return f"path '{path}' is rejected or migration-only in active DSL v2"
    if path not in V2_SUPPORTED_BINDING_PATHS:
        return f"path '{path}' is not a Phase-3-supported binding path"
    if path == 'generator.arc_height' and phase.generator is not GeneratorType.ARC_CARTESIAN:
        return 'generator.arc_height requires generator arc_cartesian'
    if path == 'generator.speed' and phase.generator is None:
        return 'generator.speed requires a motion generator'
    if path == 'control.force_limit' and (not _phase_has_force_limit_consumer(phase)):
        return 'control.force_limit requires a force-aware control mode'
    if path == 'termination.pose_tolerance' and phase.termination is not TerminationCond.POSE_TOLERANCE:
        return 'termination.pose_tolerance requires termination pose_tolerance'
    if path == 'termination.force_threshold' and phase.termination is not TerminationCond.FORCE_EXCEEDED:
        return 'termination.force_threshold requires force_exceeded termination'
    if path == 'duration.max_time' and phase.termination is not TerminationCond.TIME_LIMIT:
        return 'duration.max_time requires termination time_limit'
    if path == 'end_effector.grip_width' and phase.end_effector_action is None:
        return 'end_effector.grip_width requires an end_effector_action'
    if path == 'target.offset_along_axis.distance' and (phase.target is None or phase.target.offset_along_axis is None):
        return 'target.offset_along_axis.distance requires target.offset_along_axis'
    if path.startswith('retry.offset.') and (phase.retries is None or phase.retries.strategy != 'offset_target'):
        return 'retry.offset.* requires retries.strategy offset_target'
    return None

def _validate_guards_and_retries(phase: Phase) -> list[ValidationError]:
    errors: list[ValidationError] = []
    seen_guard_ids: set[str] = set()
    has_retry_guard = False
    for guard in phase.guards:
        if guard.guard_id in seen_guard_ids:
            errors.append(ValidationError(f"Duplicate guard id '{guard.guard_id}' in phase '{phase.phase_id}'."))
        seen_guard_ids.add(guard.guard_id)
        if guard.when not in V2_GUARD_WHENS:
            errors.append(ValidationError(f"Guard '{guard.guard_id}' in phase '{phase.phase_id}' has unsupported when '{guard.when}'."))
        if guard.predicate not in V2_GUARD_PREDICATES:
            errors.append(ValidationError(f"Guard '{guard.guard_id}' in phase '{phase.phase_id}' has unsupported predicate '{guard.predicate}'."))
        if guard.on_failure not in V2_GUARD_FAILURE_ACTIONS:
            errors.append(ValidationError(f"Guard '{guard.guard_id}' in phase '{phase.phase_id}' has unsupported on_failure '{guard.on_failure}'."))
        if guard.threshold is not None and (not _is_finite(guard.threshold)):
            errors.append(ValidationError(f"Guard '{guard.guard_id}' in phase '{phase.phase_id}' threshold must be finite."))
        has_retry_guard = has_retry_guard or guard.on_failure == 'retry'
    retries = phase.retries
    if retries is None:
        if has_retry_guard:
            errors.append(ValidationError(f"Phase '{phase.phase_id}' has retry guard(s) but no retries block."))
        return errors
    if retries.max_attempts < 0 or retries.max_attempts > 3:
        errors.append(ValidationError(f"Phase '{phase.phase_id}' retries.max_attempts must be in [0, 3]."))
    if retries.strategy not in V2_RETRY_STRATEGIES:
        errors.append(ValidationError(f"Phase '{phase.phase_id}' has unsupported retry strategy '{retries.strategy}'."))
    if retries.strategy == 'offset_target' and (not _finite_vec(retries.offset)):
        errors.append(ValidationError(f"Phase '{phase.phase_id}' offset_target retries require finite offset."))
    if retries.strategy == 'reduce_speed':
        if phase.generator is None:
            errors.append(ValidationError(f"Phase '{phase.phase_id}' reduce_speed retry requires a motion generator."))
        elif not any((binding.path == 'generator.speed' for (_name, parameter) in phase.parameters for binding in parameter.binds_to)):
            errors.append(ValidationError(f"Phase '{phase.phase_id}' reduce_speed retry requires a bound generator.speed consumer."))
    if retries.reduce_speed_factor <= 0.0 or not _is_finite(retries.reduce_speed_factor):
        errors.append(ValidationError(f"Phase '{phase.phase_id}' reduce_speed_factor must be finite and positive."))
    if retries.increase_force_limit_factor != 1.25:
        errors.append(ValidationError(f"Phase '{phase.phase_id}' increase_force_limit_factor is not supported by active retry strategies."))
    return errors

def _validate_parameters(phase: Phase) -> list[ValidationError]:
    errors: list[ValidationError] = []
    for (pname, pparam) in phase.parameters:
        if (pparam.diagnostic_only or pparam.unused_allowed) and (not pparam.justification):
            errors.append(ValidationError(f"Parameter '{pname}' in phase '{phase.phase_id}' is diagnostic/unused but has no justification."))
        if pparam.binds_to:
            if pparam.diagnostic_only or pparam.unused_allowed:
                errors.append(ValidationError(f"Parameter '{pname}' in phase '{phase.phase_id}' declares binds_to and diagnostic_only/unused_allowed; choose one status."))
        elif not (pparam.diagnostic_only or pparam.unused_allowed):
            errors.append(ValidationError(f"Parameter '{pname}' in phase '{phase.phase_id}' has no supported binds_to path and is not diagnostic_only or unused_allowed."))
        for binding in pparam.binds_to:
            if binding.mode not in V2_BINDING_MODES:
                errors.append(ValidationError(f"Parameter '{pname}' in phase '{phase.phase_id}' has unsupported binding mode '{binding.mode}'."))
            if binding.mode == 'scale' and (pparam.range[0] <= 0.0 or pparam.range[1] <= 0.0):
                errors.append(ValidationError(f"Parameter '{pname}' in phase '{phase.phase_id}' uses scale mode with a non-positive range."))
            if pparam.type is ParameterType.VECTOR:
                if binding.frame not in V2_BINDING_FRAMES:
                    errors.append(ValidationError(f"Vector parameter '{pname}' in phase '{phase.phase_id}' binding requires frame world, anchor, or local."))
            elif binding.frame is not None and binding.frame not in V2_BINDING_FRAMES:
                errors.append(ValidationError(f"Parameter '{pname}' in phase '{phase.phase_id}' has unsupported binding frame '{binding.frame}'."))
            consumer_error = _binding_consumer_error(phase, binding.path)
            if consumer_error is not None:
                errors.append(ValidationError(f"Parameter '{pname}' in phase '{phase.phase_id}' binding error: {consumer_error}."))
    return errors

def _validate_v2(skill: Skill, allow_migration: bool) -> list[ValidationError]:
    errors: list[ValidationError] = []
    for phase in skill.phases:
        errors.extend(_validate_target(skill, phase, allow_migration=allow_migration))
        errors.extend(_validate_guards_and_retries(phase))
        errors.extend(_validate_parameters(phase))
    return errors

def validate(skill: Skill, *, allow_v2_migration: bool=False) -> list[ValidationError]:
    errors = _base_validate(skill)
    if skill.dsl_version == DSL_V2:
        errors.extend(_validate_v2(skill, allow_migration=allow_v2_migration))
    elif skill.dsl_version != 1:
        errors.append(ValidationError(f"Skill '{skill.name}' declares unsupported dsl_version {skill.dsl_version}; supported active version is 2 and missing version means v1 archive."))
    return errors

def parameter_consumption_report(skill: Skill, sampled_values: dict[str, Any] | None=None, *, as_entries: bool=False) -> dict[str, Any]:
    sampled_values = sampled_values or {}
    report: dict[str, Any] = {}
    for phase in skill.phases:
        for (pname, pparam) in phase.parameters:
            key = f'{phase.phase_id}.{pname}'
            if pparam.diagnostic_only:
                status = 'diagnostic_only'
            elif pparam.unused_allowed:
                status = 'unused_allowed'
            elif pparam.binds_to:
                status = 'consumed'
            elif skill.dsl_version == DSL_V2:
                status = 'rejected'
            else:
                status = 'legacy_implicit'
            entry = ParameterConsumptionEntry(status=status, type=pparam.type.name.lower(), sampled_value=sampled_values.get(key), bindings=tuple((BindingConsumptionRecord(path=b.path, mode=b.mode) for b in pparam.binds_to)), justification=pparam.justification)
            if as_entries:
                report[key] = entry
                continue
            entry_dict = asdict(entry)
            entry_dict['bindings'] = list(entry_dict['bindings'])
            report[key] = entry_dict
    return report

def validate_skill_yaml(path: str | pathlib.Path) -> bool:
    from dsl import serialiser
    path = pathlib.Path(path)
    if not path.exists():
        raise FileNotFoundError(f'Skill YAML not found: {path}')
    skill = serialiser.load_skill(path.read_text(encoding='utf-8'))
    errors = validate(skill)
    if errors:
        msg = '\n'.join((e.message for e in errors))
        raise ValueError(f"Validation errors in '{path}':\n{msg}")
    return True
