from __future__ import annotations
from typing import Any
import yaml
from dsl.nodes import ControlMode, EndEffectorAction, GeneratorType, Guard, OffsetAlongAxis, OrientationTarget, ParameterBinding, ParameterType, Phase, PhaseParameter, PhaseTarget, PhaseType, RetryPolicy, Skill, SkillType, TerminationCond
_PARAM_TYPE_MAP: dict[str, ParameterType] = {m.name.lower(): m for m in ParameterType}
_GENERATOR_MAP: dict[str, GeneratorType] = {m.name.lower(): m for m in GeneratorType}
_CONTROL_MAP: dict[str, ControlMode] = {m.name.lower(): m for m in ControlMode}
_TERMINATION_MAP: dict[str, TerminationCond] = {m.name.lower(): m for m in TerminationCond}
_EE_ACTION_MAP: dict[str, EndEffectorAction] = {m.name.lower(): m for m in EndEffectorAction}
_SKILL_TYPE_MAP: dict[str, SkillType] = {m.name.lower(): m for m in SkillType}
_PHASE_TYPE_MAP: dict[str, PhaseType] = {pt.value: pt for pt in PhaseType}

def _require(mapping: dict[str, Any], key: str, context: str) -> Any:
    if key not in mapping:
        raise ValueError(f"Missing required field '{key}' in {context}.")
    return mapping[key]

def _lookup(table: dict[str, Any], raw: str, field: str, context: str) -> Any:
    normalised = str(raw).strip().lower()
    if normalised not in table:
        raise ValueError(f"Unknown value '{raw}' for field '{field}' in {context}. Allowed values: {sorted(table.keys())}.")
    return table[normalised]

def _as_float_tuple(raw: Any, length: int, context: str) -> tuple[float, ...]:
    if not isinstance(raw, (list, tuple)) or len(raw) != length:
        raise ValueError(f'{context} must be a {length}-element numeric list, got {raw!r}.')
    try:
        return tuple((float(v) for v in raw))
    except (TypeError, ValueError) as exc:
        raise ValueError(f'{context} must contain only numeric values: {exc}') from exc

def _normalise_default(raw: Any, context: str) -> float | str | tuple[float, ...] | None:
    if raw is None or isinstance(raw, (str, int, float)):
        return raw
    if isinstance(raw, (list, tuple)):
        try:
            return tuple((float(v) for v in raw))
        except (TypeError, ValueError) as exc:
            raise ValueError(f'Default in {context} must be scalar, string, or numeric list: {exc}') from exc
    raise ValueError(f'Default in {context} must be scalar, string, or numeric list.')

def _freeze_args(raw: Any, context: str) -> tuple[tuple[str, Any], ...]:
    if raw is None:
        return ()
    if not isinstance(raw, dict):
        raise ValueError(f"'args' in {context} must be a YAML mapping.")
    return tuple(sorted(((str(k), v) for (k, v) in raw.items())))

def _parse_binding(raw: Any, context: str) -> ParameterBinding:
    if not isinstance(raw, dict):
        raise ValueError(f'Binding at {context} must be a YAML mapping.')
    return ParameterBinding(path=str(_require(raw, 'path', context)), mode=str(raw.get('mode', 'add')), frame=str(raw['frame']) if raw.get('frame') is not None else None)

def _parse_phase_parameters(raw_params: Any, phase_ctx: str) -> tuple[tuple[str, PhaseParameter], ...]:
    if not isinstance(raw_params, dict):
        raise ValueError(f"'parameters' in {phase_ctx} must be a YAML mapping, got {type(raw_params).__name__}.")
    result: list[tuple[str, PhaseParameter]] = []
    for (pname, pdata) in raw_params.items():
        pctx = f'{phase_ctx}.parameters.{pname}'
        if not isinstance(pdata, dict):
            raise ValueError(f'Parameter definition at {pctx} must be a YAML mapping, got {type(pdata).__name__}.')
        param_type: ParameterType = _lookup(_PARAM_TYPE_MAP, _require(pdata, 'type', pctx), 'type', pctx)
        raw_range = _require(pdata, 'range', pctx)
        if not isinstance(raw_range, (list, tuple)) or len(raw_range) != 2:
            raise ValueError(f"Field 'range' in {pctx} must be a two-element list, got {raw_range!r}.")
        try:
            (lo, hi) = (float(raw_range[0]), float(raw_range[1]))
        except (TypeError, ValueError) as exc:
            raise ValueError(f"Both elements of 'range' in {pctx} must be numeric: {exc}") from exc
        raw_bindings = pdata.get('binds_to')
        if raw_bindings is None:
            bindings: tuple[ParameterBinding, ...] = ()
        else:
            if not isinstance(raw_bindings, list):
                raise ValueError(f"'binds_to' in {pctx} must be a YAML sequence.")
            bindings = tuple((_parse_binding(b, f'{pctx}.binds_to[{i}]') for (i, b) in enumerate(raw_bindings)))
        result.append((str(pname), PhaseParameter(type=param_type, range=(lo, hi), default=_normalise_default(pdata.get('default'), pctx), binds_to=bindings, diagnostic_only=bool(pdata.get('diagnostic_only', False)), unused_allowed=bool(pdata.get('unused_allowed', False)), justification=str(pdata['justification']) if pdata.get('justification') is not None else None)))
    return tuple(sorted(result, key=lambda t: t[0]))

def _parse_offset_along_axis(raw: Any, context: str) -> OffsetAlongAxis:
    if not isinstance(raw, dict):
        raise ValueError(f'{context} must be a YAML mapping.')
    return OffsetAlongAxis(distance=float(_require(raw, 'distance', context)), axis=str(_require(raw, 'axis', context)), mode=str(raw.get('mode', 'add_to_offset')), sign=str(raw.get('sign', 'positive')))

def _parse_orientation(raw: Any, context: str) -> OrientationTarget:
    if not isinstance(raw, dict):
        raise ValueError(f'{context} must be a YAML mapping.')
    quat = raw.get('quat')
    axis = raw.get('axis')
    return OrientationTarget(mode=str(raw.get('mode', 'none')), quat=_as_float_tuple(quat, 4, f'{context}.quat') if quat is not None else None, axis=_as_float_tuple(axis, 3, f'{context}.axis') if axis is not None else None, align_with=str(raw['align_with']) if raw.get('align_with') is not None else None, tolerance=float(raw['tolerance']) if raw.get('tolerance') is not None else None)

def _parse_target(raw: Any, context: str) -> PhaseTarget:
    if not isinstance(raw, dict):
        raise ValueError(f'{context} must be a YAML mapping.')
    offset_axis = raw.get('offset_along_axis')
    orientation = raw.get('orientation')
    return PhaseTarget(source=str(_require(raw, 'source', context)), anchor=str(_require(raw, 'anchor', context)), entity=str(raw['entity']) if raw.get('entity') is not None else None, offset=_as_float_tuple(raw.get('offset', [0.0, 0.0, 0.0]), 3, f'{context}.offset'), offset_along_axis=_parse_offset_along_axis(offset_axis, f'{context}.offset_along_axis') if offset_axis is not None else None, tolerance=float(raw['tolerance']) if raw.get('tolerance') is not None else None, orientation=_parse_orientation(orientation, f'{context}.orientation') if orientation is not None else None)

def _parse_guard(raw: Any, context: str) -> Guard:
    if not isinstance(raw, dict):
        raise ValueError(f'{context} must be a YAML mapping.')
    return Guard(guard_id=str(_require(raw, 'id', context)), when=str(_require(raw, 'when', context)), predicate=str(_require(raw, 'predicate', context)), args=_freeze_args(raw.get('args'), context), threshold=float(raw['threshold']) if raw.get('threshold') is not None else None, on_failure=str(raw.get('on_failure', 'abort')))

def _parse_retries(raw: Any, context: str) -> RetryPolicy:
    if not isinstance(raw, dict):
        raise ValueError(f'{context} must be a YAML mapping.')
    raw_offset = raw.get('offset')
    return RetryPolicy(max_attempts=int(raw.get('max_attempts', 0)), strategy=str(raw.get('strategy', 'repeat')), offset=_as_float_tuple(raw_offset, 3, f'{context}.offset') if raw_offset is not None else None, reduce_speed_factor=float(raw.get('reduce_speed_factor', 0.5)), increase_force_limit_factor=float(raw.get('increase_force_limit_factor', 1.25)))

def _parse_phase(raw: Any, index: int) -> Phase:
    ctx = f'phase[{index}]'
    if not isinstance(raw, dict):
        raise ValueError(f'{ctx} must be a YAML mapping, got {type(raw).__name__}.')
    phase_id: str = str(_require(raw, 'id', ctx))
    phase_type: PhaseType = _lookup(_PHASE_TYPE_MAP, _require(raw, 'type', ctx), 'type', ctx)
    raw_generator = raw.get('generator')
    if raw_generator is None:
        generator: GeneratorType | None = None
    else:
        generator = _lookup(_GENERATOR_MAP, raw_generator, 'generator', ctx)
    control: ControlMode = _lookup(_CONTROL_MAP, _require(raw, 'control', ctx), 'control', ctx)
    termination: TerminationCond = _lookup(_TERMINATION_MAP, _require(raw, 'termination', ctx), 'termination', ctx)
    raw_ee = raw.get('end_effector_action')
    if raw_ee is None:
        end_effector_action: EndEffectorAction | None = None
    else:
        end_effector_action = _lookup(_EE_ACTION_MAP, raw_ee, 'end_effector_action', ctx)
    raw_phase_params = raw.get('parameters')
    if raw_phase_params is None:
        parameters: tuple[tuple[str, PhaseParameter], ...] = ()
    else:
        parameters = _parse_phase_parameters(raw_phase_params, ctx)
    raw_subtask_id = raw.get('subtask_id')
    subtask_id: str | None = str(raw_subtask_id) if raw_subtask_id is not None else None
    target = _parse_target(raw['target'], f'{ctx}.target') if raw.get('target') is not None else None
    raw_guards = raw.get('guards')
    if raw_guards is None:
        guards: tuple[Guard, ...] = ()
    else:
        if not isinstance(raw_guards, list):
            raise ValueError(f"'guards' in {ctx} must be a YAML sequence.")
        guards = tuple((_parse_guard(g, f'{ctx}.guards[{i}]') for (i, g) in enumerate(raw_guards)))
    retries = _parse_retries(raw['retries'], f'{ctx}.retries') if raw.get('retries') is not None else None
    return Phase(phase_id=phase_id, phase_type=phase_type, generator=generator, control=control, termination=termination, end_effector_action=end_effector_action, parameters=parameters, subtask_id=subtask_id, target=target, guards=guards, retries=retries)

def load_skill(yaml_str: str) -> Skill:
    try:
        doc: Any = yaml.safe_load(yaml_str)
    except yaml.YAMLError as exc:
        raise ValueError(f'YAML parse error: {exc}') from exc
    if not isinstance(doc, dict):
        raise ValueError(f'Top-level YAML document must be a mapping, got {type(doc).__name__}.')
    raw_dsl_version = doc.get('dsl_version', 1)
    try:
        dsl_version = int(raw_dsl_version)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"'dsl_version' must be an integer, got {raw_dsl_version!r}.") from exc
    skill_name: str = str(_require(doc, 'skill', 'top-level document'))
    raw_phases = _require(doc, 'phases', 'top-level document')
    if not isinstance(raw_phases, list):
        raise ValueError(f"'phases' must be a YAML sequence, got {type(raw_phases).__name__}.")
    phases: tuple[Phase, ...] = tuple((_parse_phase(ph, i) for (i, ph) in enumerate(raw_phases)))
    raw_skill_type = doc.get('skill_type')
    if raw_skill_type is None:
        skill_type: SkillType = SkillType.ARM
    else:
        skill_type = _lookup(_SKILL_TYPE_MAP, raw_skill_type, 'skill_type', 'top-level document')
    skill_subtasks: tuple[dict, ...] | None = None
    raw_subtasks = doc.get('subtasks')
    if raw_subtasks is not None:
        if not isinstance(raw_subtasks, list):
            raise ValueError(f"'subtasks' must be a YAML sequence, got {type(raw_subtasks).__name__}.")
        parsed: list[dict] = []
        for (idx, raw_st) in enumerate(raw_subtasks):
            st_ctx = f'subtasks[{idx}]'
            if not isinstance(raw_st, dict):
                raise ValueError(f'{st_ctx} must be a YAML mapping.')
            st_id = raw_st.get('id')
            if not isinstance(st_id, str) or not st_id.strip():
                raise ValueError(f"'id' in {st_ctx} must be a non-empty string.")
            entry: dict = {'id': st_id.strip(), 'target_entity': str(raw_st.get('target_entity', raw_st.get('entity', 'tcp'))), 'metric': str(raw_st.get('metric', 'distance')), 'anchor': str(raw_st.get('anchor', 'goal')), 'offset': [float(v) for v in raw_st.get('offset', [0.0, 0.0, 0.0])], 'param_offset_key': raw_st.get('param_offset_key'), 'weight': float(raw_st.get('weight', 1.0))}
            if raw_st.get('entity') is not None:
                entry['entity'] = str(raw_st['entity'])
            parsed.append(entry)
        skill_subtasks = tuple(parsed)
    return Skill(name=skill_name, phases=phases, skill_type=skill_type, skill_subtasks=skill_subtasks, dsl_version=dsl_version)

def _maybe_list(value: Any) -> Any:
    return list(value) if isinstance(value, tuple) else value

def _dump_orientation(orientation: OrientationTarget) -> dict[str, Any]:
    out: dict[str, Any] = {'mode': orientation.mode}
    if orientation.quat is not None:
        out['quat'] = list(orientation.quat)
    if orientation.axis is not None:
        out['axis'] = list(orientation.axis)
    if orientation.align_with is not None:
        out['align_with'] = orientation.align_with
    if orientation.tolerance is not None:
        out['tolerance'] = orientation.tolerance
    return out

def _dump_target(target: PhaseTarget) -> dict[str, Any]:
    out: dict[str, Any] = {'source': target.source, 'anchor': target.anchor}
    if target.entity is not None:
        out['entity'] = target.entity
    out['offset'] = list(target.offset)
    if target.offset_along_axis is not None:
        out['offset_along_axis'] = {'distance': target.offset_along_axis.distance, 'axis': target.offset_along_axis.axis, 'mode': target.offset_along_axis.mode, 'sign': target.offset_along_axis.sign}
    if target.tolerance is not None:
        out['tolerance'] = target.tolerance
    if target.orientation is not None:
        out['orientation'] = _dump_orientation(target.orientation)
    return out

def _dump_guard(guard: Guard) -> dict[str, Any]:
    out: dict[str, Any] = {'id': guard.guard_id, 'when': guard.when, 'predicate': guard.predicate}
    if guard.args:
        out['args'] = dict(guard.args)
    if guard.threshold is not None:
        out['threshold'] = guard.threshold
    out['on_failure'] = guard.on_failure
    return out

def _dump_retries(retries: RetryPolicy) -> dict[str, Any]:
    out: dict[str, Any] = {'max_attempts': retries.max_attempts, 'strategy': retries.strategy}
    if retries.offset is not None:
        out['offset'] = list(retries.offset)
    if retries.reduce_speed_factor != 0.5:
        out['reduce_speed_factor'] = retries.reduce_speed_factor
    return out

def _dump_parameter(param: PhaseParameter) -> dict[str, Any]:
    out: dict[str, Any] = {'type': param.type.name.lower(), 'range': list(param.range)}
    if param.default is not None:
        out['default'] = _maybe_list(param.default)
    if param.binds_to:
        out['binds_to'] = [{**{'path': binding.path, 'mode': binding.mode}, **({'frame': binding.frame} if binding.frame is not None else {})} for binding in param.binds_to]
    if param.diagnostic_only:
        out['diagnostic_only'] = True
    if param.unused_allowed:
        out['unused_allowed'] = True
    if param.justification is not None:
        out['justification'] = param.justification
    return out

def dump_skill(skill: Skill) -> str:
    doc: dict[str, Any] = {'skill': skill.name}
    if skill.dsl_version != 1:
        doc['dsl_version'] = skill.dsl_version
    if skill.skill_type is not SkillType.ARM:
        doc['skill_type'] = skill.skill_type.name.lower()
    if skill.skill_subtasks:
        _DEFAULT_OFFSET = [0.0, 0.0, 0.0]
        subtasks_list = []
        for st in skill.skill_subtasks:
            st_dict: dict[str, Any] = {'id': st['id']}
            if st.get('anchor', 'goal') != 'goal':
                st_dict['anchor'] = st['anchor']
            if st.get('target_entity', 'tcp') != 'tcp':
                st_dict['target_entity'] = st['target_entity']
            if st.get('entity') is not None:
                st_dict['entity'] = st['entity']
            if st.get('metric', 'distance') != 'distance':
                st_dict['metric'] = st['metric']
            if st.get('offset', _DEFAULT_OFFSET) != _DEFAULT_OFFSET:
                st_dict['offset'] = st['offset']
            if st.get('param_offset_key') is not None:
                st_dict['param_offset_key'] = st['param_offset_key']
            if st.get('weight', 1.0) != 1.0:
                st_dict['weight'] = st['weight']
            subtasks_list.append(st_dict)
        doc['subtasks'] = subtasks_list
    phases_list = []
    for ph in skill.phases:
        phase_dict: dict[str, Any] = {'id': ph.phase_id, 'type': ph.phase_type.value}
        if ph.generator is not None:
            phase_dict['generator'] = ph.generator.name.lower()
        phase_dict['control'] = ph.control.name.lower()
        phase_dict['termination'] = ph.termination.name.lower()
        if ph.end_effector_action is not None:
            phase_dict['end_effector_action'] = ph.end_effector_action.name.lower()
        if ph.target is not None:
            phase_dict['target'] = _dump_target(ph.target)
        if ph.parameters:
            phase_dict['parameters'] = {pname: _dump_parameter(pparam) for (pname, pparam) in sorted(ph.parameters, key=lambda t: t[0])}
        if ph.guards:
            phase_dict['guards'] = [_dump_guard(guard) for guard in ph.guards]
        if ph.retries is not None:
            phase_dict['retries'] = _dump_retries(ph.retries)
        if ph.subtask_id is not None:
            phase_dict['subtask_id'] = ph.subtask_id
        phases_list.append(phase_dict)
    doc['phases'] = phases_list
    return yaml.dump(doc, default_flow_style=False, sort_keys=False)
