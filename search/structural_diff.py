from __future__ import annotations
from typing import Any
from dsl.nodes import Skill

def _enum_name(value: Any) -> str:
    return getattr(value, 'name', str(value)).lower() if value is not None else 'None'

def _phase_type(phase: Any) -> str:
    return phase.phase_type.value

def _param_map(skill: Skill) -> dict[str, Any]:
    return {f'{ph.phase_id}.{pname}': pparam for ph in skill.phases for (pname, pparam) in ph.parameters}

def _subtasks_summary(skill: Skill) -> tuple[tuple, ...] | None:
    subtasks = getattr(skill, 'skill_subtasks', None)
    if subtasks is None:
        return None
    return tuple(sorted((tuple(sorted(d.items())) for d in subtasks)))

def structural_diff(parent: Skill, child: Skill) -> dict:
    parent_params = set(parent.flat_param_names())
    child_params = set(child.flat_param_names())
    params_added = sorted(child_params - parent_params)
    params_removed = sorted(parent_params - child_params)
    parent_param_map = _param_map(parent)
    child_param_map = _param_map(child)
    parameter_type_changes = []
    parameter_range_changes = []
    for name in sorted(parent_params & child_params):
        pp = parent_param_map[name]
        cp = child_param_map[name]
        if pp.type != cp.type:
            parameter_type_changes.append(f'{name}: {_enum_name(pp.type)} -> {_enum_name(cp.type)}')
        if tuple(pp.range) != tuple(cp.range):
            parameter_range_changes.append(f'{name}: {tuple(pp.range)} -> {tuple(cp.range)}')
    parent_phases = {p.phase_id: p for p in parent.phases}
    child_phases = {p.phase_id: p for p in child.phases}
    phases_added = [n for n in child_phases if n not in parent_phases]
    phases_removed = [n for n in parent_phases if n not in child_phases]
    parent_order = {p.phase_id: i for (i, p) in enumerate(parent.phases)}
    child_order = {p.phase_id: i for (i, p) in enumerate(child.phases)}
    phase_reorderings = [f'{pid}: {parent_order[pid]} -> {child_order[pid]}' for pid in parent_order if pid in child_order and parent_order[pid] != child_order[pid]]
    phase_type_changes = []
    generator_changes = []
    control_changes = []
    termination_changes = []
    end_effector_action_changes = []
    subtask_binding_changes = []
    for (name, cp) in child_phases.items():
        if name in parent_phases:
            pp = parent_phases[name]
            if cp.phase_type != pp.phase_type:
                phase_type_changes.append(f'{name}: {_phase_type(pp)} -> {_phase_type(cp)}')
            if cp.generator != pp.generator:
                generator_changes.append(f'{name}: {_enum_name(pp.generator)} -> {_enum_name(cp.generator)}')
            if cp.control != pp.control:
                control_changes.append(f'{name}: {_enum_name(pp.control)} -> {_enum_name(cp.control)}')
            if cp.termination != pp.termination:
                termination_changes.append(f'{name}: {_enum_name(pp.termination)} -> {_enum_name(cp.termination)}')
            if cp.end_effector_action != pp.end_effector_action:
                end_effector_action_changes.append(f'{name}: {_enum_name(pp.end_effector_action)} -> {_enum_name(cp.end_effector_action)}')
            if getattr(cp, 'subtask_id', None) != getattr(pp, 'subtask_id', None):
                subtask_binding_changes.append(f"{name}: {getattr(pp, 'subtask_id', None)} -> {getattr(cp, 'subtask_id', None)}")
    skill_type_changed = parent.skill_type != child.skill_type
    skill_type_change = f'{_enum_name(parent.skill_type)} -> {_enum_name(child.skill_type)}' if skill_type_changed else None
    skill_subtasks_changed = _subtasks_summary(parent) != _subtasks_summary(child)
    subtask_changes = list(subtask_binding_changes)
    if skill_subtasks_changed:
        subtask_changes.append('skill_subtasks changed')
    changes = []
    if params_added:
        changes.append(f"+param({','.join(params_added)})")
    if params_removed:
        changes.append(f"-param({','.join(params_removed)})")
    for c in parameter_type_changes:
        changes.append(f'param_type({c})')
    for c in parameter_range_changes:
        changes.append(f'param_range({c})')
    if phases_added:
        changes.append(f"+phase({','.join(phases_added)})")
    if phases_removed:
        changes.append(f"-phase({','.join(phases_removed)})")
    for c in phase_reorderings:
        changes.append(f'phase_order({c})')
    for c in phase_type_changes:
        changes.append(f'phase_type({c})')
    for c in generator_changes:
        changes.append(f'gen({c})')
    for c in control_changes:
        changes.append(f'ctrl({c})')
    for c in termination_changes:
        changes.append(f'term({c})')
    for c in end_effector_action_changes:
        changes.append(f'ee({c})')
    if skill_type_change:
        changes.append(f'skill_type({skill_type_change})')
    for c in subtask_changes:
        changes.append(f'subtask({c})')
    summary = '; '.join(changes) if changes else 'identity (no structural change)'
    return {'params_added': params_added, 'params_removed': params_removed, 'phases_added': phases_added, 'phases_removed': phases_removed, 'generator_changes': generator_changes, 'control_changes': control_changes, 'termination_changes': termination_changes, 'n_params': child.param_dim, 'n_phases': len(child.phases), 'summary': summary, 'phase_type_changes': phase_type_changes, 'phase_reorderings': phase_reorderings, 'skill_type_changed': skill_type_changed, 'skill_type_change': skill_type_change, 'parameter_type_changes': parameter_type_changes, 'parameter_range_changes': parameter_range_changes, 'subtask_changes': subtask_changes, 'subtask_binding_changes': subtask_binding_changes, 'skill_subtasks_changed': skill_subtasks_changed, 'end_effector_action_changes': end_effector_action_changes}

def classify_repair_types(diff: dict | None) -> tuple[str, ...]:
    if diff is None:
        return ('unknown',)
    labels: list[str] = []
    if diff.get('generator_changes'):
        labels.append('trajectory repair')
    if diff.get('phases_added'):
        labels.append('phase insertion repair')
    if diff.get('phases_removed'):
        labels.append('phase removal repair')
    if diff.get('phase_reorderings'):
        labels.append('phase order repair')
    if diff.get('phase_type_changes'):
        labels.append('phase type repair')
    if diff.get('control_changes'):
        labels.append('control repair')
    if diff.get('termination_changes'):
        labels.append('termination repair')
    if diff.get('params_added') or diff.get('params_removed') or diff.get('parameter_type_changes') or diff.get('parameter_range_changes'):
        labels.append('parameter repair')
    if diff.get('subtask_changes'):
        labels.append('subtask repair')
    if diff.get('skill_type_changed') or diff.get('end_effector_action_changes'):
        labels.append('mode repair')
    if not labels and diff.get('summary') == 'identity (no structural change)':
        labels.append('unknown')
    elif not labels:
        labels.append('unknown')
    return tuple(labels)
