from __future__ import annotations
import random
from dataclasses import replace as dc_replace
from typing import List
from dsl.nodes import ControlMode, GeneratorType, ParameterType, Phase, PhaseParameter, PhaseType, Skill, TerminationCond
from dsl.grammar import ALLOWED_PHASE_TYPES, MAX_PARAMS_PER_PHASE, MIN_PHASES, MAX_PHASES

def _rng(rng: random.Random | None) -> random.Random:
    return rng if rng is not None else random.Random()

def _unique_param_name(existing_names: frozenset[str], rng: random.Random) -> str:
    i = 0
    while True:
        candidate = f'param_{i}'
        if candidate not in existing_names:
            return candidate
        i += 1

def _unique_phase_id(phase_type: PhaseType, used_ids: frozenset[str]) -> str:
    n = 1
    while True:
        candidate = f'{phase_type.value}_{n}'
        if candidate not in used_ids:
            return candidate
        n += 1

def _pick_different(choices: list, current, rng: random.Random):
    alternatives = [c for c in choices if c != current]
    return rng.choice(alternatives)

def _rebuild_phase(phase: Phase, **kwargs) -> Phase:
    return dc_replace(phase, **kwargs)

def _rebuild_skill(skill: Skill, new_phases: tuple[Phase, ...]) -> Skill:
    return dc_replace(skill, phases=new_phases)

def add_parameter(skill: Skill, rng: random.Random | None=None, phase_idx: int | None=None) -> Skill:
    r = _rng(rng)
    if phase_idx is not None and 0 <= phase_idx < len(skill.phases):
        idx = phase_idx
    else:
        idx = r.randrange(len(skill.phases))
    target_phase = skill.phases[idx]
    if len(target_phase.parameters) >= MAX_PARAMS_PER_PHASE:
        return skill
    existing_names: frozenset[str] = frozenset((pname for (pname, _) in target_phase.parameters))
    new_name = _unique_param_name(existing_names, r)
    a = r.uniform(-1.0, 1.0)
    b = r.uniform(-1.0, 1.0)
    while a == b:
        b = r.uniform(-1.0, 1.0)
    (lo, hi) = (a, b) if a < b else (b, a)
    new_pparam = PhaseParameter(type=ParameterType.SCALAR, range=(lo, hi))
    new_phase = _rebuild_phase(target_phase, parameters=target_phase.parameters + ((new_name, new_pparam),))
    new_phases = skill.phases[:idx] + (new_phase,) + skill.phases[idx + 1:]
    return _rebuild_skill(skill, new_phases)

def remove_parameter(skill: Skill, rng: random.Random | None=None, phase_idx: int | None=None) -> Skill:
    r = _rng(rng)
    phases_with_params = [i for (i, ph) in enumerate(skill.phases) if len(ph.parameters) >= 1]
    if not phases_with_params:
        return skill
    if phase_idx is not None and phase_idx in phases_with_params:
        idx = phase_idx
    else:
        idx = r.choice(phases_with_params)
    target_phase = skill.phases[idx]
    param_idx = r.randrange(len(target_phase.parameters))
    new_phase_params = target_phase.parameters[:param_idx] + target_phase.parameters[param_idx + 1:]
    new_phase = _rebuild_phase(target_phase, parameters=new_phase_params)
    new_phases = skill.phases[:idx] + (new_phase,) + skill.phases[idx + 1:]
    return _rebuild_skill(skill, new_phases)

def insert_phase(skill: Skill, rng: random.Random | None=None, target_phase_idx: int | None=None) -> Skill:
    r = _rng(rng)
    if len(skill.phases) >= MAX_PHASES:
        return skill
    phase_type = r.choice(list(ALLOWED_PHASE_TYPES))
    used_ids: frozenset[str] = frozenset((ph.phase_id for ph in skill.phases))
    new_phase_id = _unique_phase_id(phase_type, used_ids)
    new_phase = Phase(phase_id=new_phase_id, phase_type=phase_type, generator=GeneratorType.LINEAR_CARTESIAN, control=ControlMode.POSITION_CONTROL, termination=TerminationCond.POSE_TOLERANCE, parameters=())
    if target_phase_idx is not None and 0 <= target_phase_idx <= len(skill.phases):
        insert_idx = target_phase_idx
    else:
        insert_idx = r.randint(0, len(skill.phases))
    new_phases = skill.phases[:insert_idx] + (new_phase,) + skill.phases[insert_idx:]
    return _rebuild_skill(skill, new_phases)

def remove_phase(skill: Skill, rng: random.Random | None=None, target_phase_idx: int | None=None) -> Skill:
    r = _rng(rng)
    if len(skill.phases) <= MIN_PHASES:
        return skill
    if target_phase_idx is not None and 0 <= target_phase_idx < len(skill.phases):
        idx = target_phase_idx
    else:
        idx = r.randrange(len(skill.phases))
    new_phases = skill.phases[:idx] + skill.phases[idx + 1:]
    return _rebuild_skill(skill, new_phases)

def swap_generator(skill: Skill, rng: random.Random | None=None, target_phase_idx: int | None=None) -> Skill:
    r = _rng(rng)
    all_generators = list(GeneratorType)
    if target_phase_idx is not None and 0 <= target_phase_idx < len(skill.phases):
        idx = target_phase_idx
    else:
        idx = r.randrange(len(skill.phases))
    old_phase = skill.phases[idx]
    new_generator = _pick_different(all_generators, old_phase.generator, r)
    new_phase = _rebuild_phase(old_phase, generator=new_generator)
    new_phases = skill.phases[:idx] + (new_phase,) + skill.phases[idx + 1:]
    return _rebuild_skill(skill, new_phases)

def change_control_mode(skill: Skill, rng: random.Random | None=None, target_phase_idx: int | None=None) -> Skill:
    r = _rng(rng)
    all_modes = list(ControlMode)
    if target_phase_idx is not None and 0 <= target_phase_idx < len(skill.phases):
        idx = target_phase_idx
    else:
        idx = r.randrange(len(skill.phases))
    old_phase = skill.phases[idx]
    new_mode = _pick_different(all_modes, old_phase.control, r)
    new_phase = _rebuild_phase(old_phase, control=new_mode)
    new_phases = skill.phases[:idx] + (new_phase,) + skill.phases[idx + 1:]
    return _rebuild_skill(skill, new_phases)

def change_termination(skill: Skill, rng: random.Random | None=None, target_phase_idx: int | None=None) -> Skill:
    r = _rng(rng)
    all_terms = list(TerminationCond)
    if target_phase_idx is not None and 0 <= target_phase_idx < len(skill.phases):
        idx = target_phase_idx
    else:
        idx = r.randrange(len(skill.phases))
    old_phase = skill.phases[idx]
    new_term = _pick_different(all_terms, old_phase.termination, r)
    new_phase = _rebuild_phase(old_phase, termination=new_term)
    new_phases = skill.phases[:idx] + (new_phase,) + skill.phases[idx + 1:]
    return _rebuild_skill(skill, new_phases)

def _find_param(skill: Skill, param_name: str | None, rng: random.Random) -> tuple[int, str, PhaseParameter] | None:
    all_params: list[tuple[int, str, PhaseParameter]] = [(pi, pname, pparam) for (pi, ph) in enumerate(skill.phases) for (pname, pparam) in ph.parameters]
    if not all_params:
        return None
    if param_name is None:
        return rng.choice(all_params)
    if '.' in param_name:
        (target_pid, target_pname) = param_name.split('.', 1)
        for (pi, ph) in enumerate(skill.phases):
            if ph.phase_id == target_pid:
                for (pname, pparam) in ph.parameters:
                    if pname == target_pname:
                        return (pi, pname, pparam)
    else:
        for (pi, pname, pparam) in all_params:
            if pname == param_name:
                return (pi, pname, pparam)
    return None

def _replace_phase_param(skill: Skill, phase_idx: int, param_name: str, new_pparam: PhaseParameter) -> Skill:
    target_phase = skill.phases[phase_idx]
    new_phase_params = tuple(((pn, new_pparam if pn == param_name else pp) for (pn, pp) in target_phase.parameters))
    new_phase = _rebuild_phase(target_phase, parameters=new_phase_params)
    new_phases = skill.phases[:phase_idx] + (new_phase,) + skill.phases[phase_idx + 1:]
    return _rebuild_skill(skill, new_phases)

def expand_param_range(skill: Skill, rng: random.Random | None=None, param_name: str | None=None, target_phase_idx: int | None=None, factor: float=0.2) -> Skill:
    r = _rng(rng)
    found = _find_param(skill, param_name, r)
    if found is None:
        return skill
    (pi, pname, pparam) = found
    (lo, hi) = pparam.range
    width = hi - lo
    new_lo = lo - factor * width
    new_hi = hi + factor * width
    new_pparam = dc_replace(pparam, range=(new_lo, new_hi))
    return _replace_phase_param(skill, pi, pname, new_pparam)

def shrink_param_range(skill: Skill, rng: random.Random | None=None, param_name: str | None=None, target_phase_idx: int | None=None, factor: float=0.2) -> Skill:
    r = _rng(rng)
    found = _find_param(skill, param_name, r)
    if found is None:
        return skill
    (pi, pname, pparam) = found
    (lo, hi) = pparam.range
    centre = (lo + hi) / 2.0
    half_width = (hi - lo) / 2.0
    new_half_width = (1.0 - factor) * half_width
    MIN_WIDTH = 1e-06
    if 2.0 * new_half_width < MIN_WIDTH:
        return skill
    new_lo = centre - new_half_width
    new_hi = centre + new_half_width
    new_pparam = dc_replace(pparam, range=(new_lo, new_hi))
    return _replace_phase_param(skill, pi, pname, new_pparam)

def shift_param_range(skill: Skill, rng: random.Random | None=None, param_name: str | None=None, target_phase_idx: int | None=None, fraction: float=0.1) -> Skill:
    r = _rng(rng)
    found = _find_param(skill, param_name, r)
    if found is None:
        return skill
    (pi, pname, pparam) = found
    (lo, hi) = pparam.range
    width = hi - lo
    direction = r.choice([-1, +1])
    delta = direction * fraction * width
    new_lo = lo + delta
    new_hi = hi + delta
    new_pparam = dc_replace(pparam, range=(new_lo, new_hi))
    return _replace_phase_param(skill, pi, pname, new_pparam)
ALL_OPERATORS = [add_parameter, remove_parameter, insert_phase, remove_phase, swap_generator, change_control_mode, change_termination, expand_param_range, shrink_param_range, shift_param_range]

def random_mutation(skill: Skill, rng: random.Random | None=None) -> Skill:
    r = _rng(rng)
    operator = r.choice(ALL_OPERATORS)
    return operator(skill, r)
