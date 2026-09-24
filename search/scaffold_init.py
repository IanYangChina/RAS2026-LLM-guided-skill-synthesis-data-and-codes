from __future__ import annotations
import random
import warnings
from typing import NamedTuple
from dsl.nodes import ControlMode, EndEffectorAction, GeneratorType, ParameterType, Phase, PhaseParameter, PhaseType, Skill, SkillType, TerminationCond
from dsl.validator import validate

class _PhaseConfig(NamedTuple):
    generators: list[GeneratorType | None]
    controls: list[ControlMode]
    terminations: list[TerminationCond]
    ee_action: EndEffectorAction | None = None
_PHASE_CONFIGS: dict[PhaseType, _PhaseConfig] = {PhaseType.APPROACH: _PhaseConfig(generators=[GeneratorType.LINEAR_CARTESIAN, GeneratorType.ARC_CARTESIAN], controls=[ControlMode.POSITION_CONTROL, ControlMode.FORCE_THRESHOLD_SWITCH], terminations=[TerminationCond.POSE_TOLERANCE]), PhaseType.ALIGN: _PhaseConfig(generators=[GeneratorType.LINEAR_CARTESIAN], controls=[ControlMode.POSITION_CONTROL], terminations=[TerminationCond.POSE_TOLERANCE]), PhaseType.DESCEND: _PhaseConfig(generators=[GeneratorType.LINEAR_CARTESIAN], controls=[ControlMode.POSITION_CONTROL, ControlMode.ADMITTANCE_CONTROL], terminations=[TerminationCond.POSE_TOLERANCE, TerminationCond.CONTACT_DETECTED]), PhaseType.CONTACT: _PhaseConfig(generators=[GeneratorType.LINEAR_CARTESIAN, GeneratorType.IMPEDANCE_MOTION], controls=[ControlMode.IMPEDANCE_CONTROL, ControlMode.ADMITTANCE_CONTROL, ControlMode.FORCE_THRESHOLD_SWITCH], terminations=[TerminationCond.CONTACT_DETECTED, TerminationCond.FORCE_EXCEEDED]), PhaseType.PUSH: _PhaseConfig(generators=[GeneratorType.LINEAR_CARTESIAN, GeneratorType.IMPEDANCE_MOTION], controls=[ControlMode.IMPEDANCE_CONTROL, ControlMode.POSITION_CONTROL], terminations=[TerminationCond.TIME_LIMIT, TerminationCond.POSE_TOLERANCE]), PhaseType.PULL: _PhaseConfig(generators=[GeneratorType.ARC_CARTESIAN, GeneratorType.LINEAR_CARTESIAN], controls=[ControlMode.IMPEDANCE_CONTROL], terminations=[TerminationCond.TIME_LIMIT, TerminationCond.POSE_TOLERANCE]), PhaseType.INSERT: _PhaseConfig(generators=[GeneratorType.IMPEDANCE_MOTION, GeneratorType.LINEAR_CARTESIAN], controls=[ControlMode.ADMITTANCE_CONTROL, ControlMode.IMPEDANCE_CONTROL], terminations=[TerminationCond.POSE_TOLERANCE, TerminationCond.FORCE_EXCEEDED]), PhaseType.LIFT: _PhaseConfig(generators=[GeneratorType.LINEAR_CARTESIAN], controls=[ControlMode.POSITION_CONTROL], terminations=[TerminationCond.POSE_TOLERANCE]), PhaseType.RETRACT: _PhaseConfig(generators=[GeneratorType.LINEAR_CARTESIAN, GeneratorType.ARC_CARTESIAN], controls=[ControlMode.POSITION_CONTROL], terminations=[TerminationCond.POSE_TOLERANCE]), PhaseType.ROTATE: _PhaseConfig(generators=[GeneratorType.ARC_CARTESIAN, GeneratorType.IMPEDANCE_MOTION], controls=[ControlMode.POSITION_CONTROL, ControlMode.IMPEDANCE_CONTROL], terminations=[TerminationCond.POSE_TOLERANCE, TerminationCond.TIME_LIMIT]), PhaseType.GRASP: _PhaseConfig(generators=[None], controls=[ControlMode.POSITION_CONTROL], terminations=[TerminationCond.TIME_LIMIT, TerminationCond.GRASP_SUCCESS], ee_action=EndEffectorAction.FORCE_GRASP), PhaseType.RELEASE: _PhaseConfig(generators=[GeneratorType.LINEAR_CARTESIAN, None], controls=[ControlMode.POSITION_CONTROL, ControlMode.ADMITTANCE_CONTROL], terminations=[TerminationCond.POSE_TOLERANCE, TerminationCond.TIME_LIMIT], ee_action=EndEffectorAction.OPEN)}

class _ParamEntry(NamedTuple):
    name: str
    lo: float
    hi: float
    param_type: ParameterType = ParameterType.SCALAR
_PARAM_SCHEMA: dict[PhaseType, list[_ParamEntry]] = {PhaseType.APPROACH: [_ParamEntry('approach_height', 0.05, 0.3), _ParamEntry('speed', 0.01, 0.1)], PhaseType.ALIGN: [_ParamEntry('lateral_offset_x', -0.01, 0.01), _ParamEntry('lateral_offset_y', -0.01, 0.01)], PhaseType.DESCEND: [_ParamEntry('depth', 0.01, 0.1)], PhaseType.CONTACT: [_ParamEntry('contact_force', 1.0, 20.0), _ParamEntry('speed', 0.005, 0.05)], PhaseType.PUSH: [_ParamEntry('push_distance', 0.02, 0.2), _ParamEntry('push_speed', 0.01, 0.1), _ParamEntry('push_depth', 0.01, 0.1)], PhaseType.PULL: [_ParamEntry('pull_angle', 0.1, 1.2, ParameterType.ANGLE), _ParamEntry('pull_distance', 0.02, 0.2)], PhaseType.INSERT: [_ParamEntry('insertion_depth', 0.01, 0.15), _ParamEntry('insertion_force', 1.0, 20.0)], PhaseType.LIFT: [_ParamEntry('lift_height', 0.05, 0.3), _ParamEntry('speed', 0.01, 0.1)], PhaseType.RETRACT: [_ParamEntry('retract_height', 0.05, 0.2), _ParamEntry('speed', 0.01, 0.1)], PhaseType.ROTATE: [_ParamEntry('yaw_angle', 0.1, 1.57, ParameterType.ANGLE)], PhaseType.GRASP: [_ParamEntry('grip_force', 5.0, 30.0)], PhaseType.RELEASE: []}
_TASK_PARAM_OVERRIDES: dict[tuple[str, PhaseType], list[_ParamEntry]] = {('obstacle_reach', PhaseType.APPROACH): [_ParamEntry('arc_height', 0.32, 0.5), _ParamEntry('approach_distance', 0.1, 0.3), _ParamEntry('reach_speed', 0.01, 0.1)], ('obstacle_reach_baseline', PhaseType.APPROACH): [_ParamEntry('arc_height', 0.32, 0.5), _ParamEntry('approach_distance', 0.1, 0.3), _ParamEntry('reach_speed', 0.01, 0.1)]}
_TASK_PHASE_SEQUENCES: dict[str, list[PhaseType]] = {'push_to_goal': [PhaseType.APPROACH, PhaseType.CONTACT, PhaseType.PUSH, PhaseType.RETRACT], 'peg_insert': [PhaseType.ALIGN, PhaseType.APPROACH, PhaseType.CONTACT, PhaseType.INSERT, PhaseType.RETRACT], 'peg_channel': [PhaseType.ALIGN, PhaseType.APPROACH, PhaseType.CONTACT, PhaseType.PUSH, PhaseType.RETRACT], 'grasp_place': [PhaseType.APPROACH, PhaseType.DESCEND, PhaseType.GRASP, PhaseType.LIFT, PhaseType.RELEASE], 'door_pull': [PhaseType.APPROACH, PhaseType.GRASP, PhaseType.PULL, PhaseType.RETRACT], 'door_push': [PhaseType.APPROACH, PhaseType.CONTACT, PhaseType.PUSH, PhaseType.RETRACT], 'obstacle_reach': [PhaseType.APPROACH, PhaseType.DESCEND], 'obstacle_reach_baseline': [PhaseType.APPROACH, PhaseType.DESCEND]}
_DEFAULT_PHASE_SEQUENCE: list[PhaseType] = [PhaseType.APPROACH, PhaseType.CONTACT, PhaseType.RETRACT]
_PRIMARY_MOTION_PHASE: dict[str, PhaseType] = {'push_to_goal': PhaseType.PUSH, 'peg_insert': PhaseType.INSERT, 'peg_channel': PhaseType.PUSH, 'grasp_place': PhaseType.GRASP, 'door_pull': PhaseType.PULL, 'door_push': PhaseType.PUSH, 'obstacle_reach': PhaseType.APPROACH, 'obstacle_reach_baseline': PhaseType.APPROACH}
_DEFAULT_PRIMARY_PHASE: PhaseType = PhaseType.CONTACT

def _gripper_skill_type(sequence: list[PhaseType]) -> SkillType:
    gripper_phases = {PhaseType.GRASP, PhaseType.RELEASE}
    return SkillType.ARM_GRIPPER if any((pt in gripper_phases for pt in sequence)) else SkillType.ARM

class ScaffoldInitialiser:

    def __init__(self, task_name: str, rng: random.Random | None=None) -> None:
        self._task_name: str = task_name
        self._rng: random.Random = rng if rng is not None else random.Random()
        if task_name not in _TASK_PHASE_SEQUENCES:
            warnings.warn(f"ScaffoldInitialiser: unknown task '{task_name}'; using default [approach, contact, retract] skeleton.", UserWarning, stacklevel=2)
        self._sequence: list[PhaseType] = _TASK_PHASE_SEQUENCES.get(task_name, _DEFAULT_PHASE_SEQUENCE)
        self._primary_phase: PhaseType = _PRIMARY_MOTION_PHASE.get(task_name, _DEFAULT_PRIMARY_PHASE)

    def sample(self) -> Skill:
        for attempt in range(10):
            try:
                skill = self._build_skill()
                errors = validate(skill)
                if not errors:
                    return skill
                warnings.warn(f'ScaffoldInitialiser: attempt {attempt + 1} produced invalid skill: {[e.message for e in errors]}; resampling.', UserWarning, stacklevel=2)
            except Exception as exc:
                warnings.warn(f'ScaffoldInitialiser: attempt {attempt + 1} raised {type(exc).__name__}: {exc}; resampling.', UserWarning, stacklevel=2)
        raise RuntimeError(f"ScaffoldInitialiser: could not produce a valid skill for task '{self._task_name}' after 10 attempts.")

    def _build_skill(self) -> Skill:
        phases = self._sample_phases()
        skill_type = _gripper_skill_type(self._sequence)
        return Skill(name=self._task_name, phases=tuple(phases), skill_type=skill_type)

    def _sample_phases(self) -> list[Phase]:
        type_counts: dict[PhaseType, int] = {}
        phase_ids: list[str] = []
        for pt in self._sequence:
            type_counts[pt] = type_counts.get(pt, 0) + 1
            phase_ids.append(f'{pt.value}_{type_counts[pt]}')
        phases: list[Phase] = []
        for (phase_id, phase_type) in zip(phase_ids, self._sequence):
            phases.append(self._sample_phase(phase_id, phase_type))
        return phases

    def _sample_phase(self, phase_id: str, phase_type: PhaseType) -> Phase:
        cfg = _PHASE_CONFIGS[phase_type]
        generator: GeneratorType | None = self._rng.choice(cfg.generators)
        if generator is None and cfg.ee_action is None:
            non_none = [g for g in cfg.generators if g is not None]
            generator = non_none[0] if non_none else GeneratorType.LINEAR_CARTESIAN
        control: ControlMode = self._rng.choice(cfg.controls)
        termination: TerminationCond = self._rng.choice(cfg.terminations)
        ee_action: EndEffectorAction | None = cfg.ee_action
        parameters = self._sample_parameters(phase_type)
        return Phase(phase_id=phase_id, phase_type=phase_type, generator=generator, control=control, termination=termination, end_effector_action=ee_action, parameters=parameters)

    def _sample_parameters(self, phase_type: PhaseType) -> tuple[tuple[str, PhaseParameter], ...]:
        schema = _TASK_PARAM_OVERRIDES.get((self._task_name, phase_type), _PARAM_SCHEMA.get(phase_type, []))
        if not schema:
            return ()
        selected: list[tuple[str, PhaseParameter]] = []
        for entry in schema:
            if entry.lo >= entry.hi:
                continue
            if self._rng.random() < 0.5:
                selected.append((entry.name, PhaseParameter(type=entry.param_type, range=(entry.lo, entry.hi))))
        if phase_type == self._primary_phase and (not selected):
            first = next((e for e in schema if e.lo < e.hi), None)
            if first is not None:
                selected.append((first.name, PhaseParameter(type=first.param_type, range=(first.lo, first.hi))))
        selected.sort(key=lambda t: t[0])
        return tuple(selected)

def sample_scaffold_skill(task_name: str, rng: random.Random | None=None) -> Skill:
    return ScaffoldInitialiser(task_name, rng).sample()
_ALL_PHASE_TYPES: list[PhaseType] = list(_PHASE_CONFIGS.keys())

class GrammarUniformInitialiser:
    _MIN_PHASES: int = 1
    _MAX_PHASES: int = 8

    def __init__(self, task_name: str, rng: random.Random | None=None, min_phases: int=1) -> None:
        self._task_name: str = task_name
        self._rng: random.Random = rng if rng is not None else random.Random()
        self._actual_min_phases: int = max(self._MIN_PHASES, min_phases)

    def sample(self) -> Skill:
        for attempt in range(10):
            try:
                skill = self._build_skill()
                errors = validate(skill)
                if not errors:
                    return skill
                warnings.warn(f'GrammarUniformInitialiser: attempt {attempt + 1} produced invalid skill: {[e.message for e in errors]}; resampling.', UserWarning, stacklevel=2)
            except Exception as exc:
                warnings.warn(f'GrammarUniformInitialiser: attempt {attempt + 1} raised {type(exc).__name__}: {exc}; resampling.', UserWarning, stacklevel=2)
        raise RuntimeError(f"GrammarUniformInitialiser: could not produce a valid skill for task '{self._task_name}' after 10 attempts.")

    def _build_skill(self) -> Skill:
        n_phases = self._rng.randint(self._actual_min_phases, self._MAX_PHASES)
        phase_types: list[PhaseType] = [self._rng.choice(_ALL_PHASE_TYPES) for _ in range(n_phases)]
        type_counts: dict[PhaseType, int] = {}
        phase_ids: list[str] = []
        for pt in phase_types:
            type_counts[pt] = type_counts.get(pt, 0) + 1
            phase_ids.append(f'{pt.value}_{type_counts[pt]}')
        phases: list[Phase] = [self._sample_phase(phase_id, phase_type) for (phase_id, phase_type) in zip(phase_ids, phase_types)]
        skill_type = _gripper_skill_type(phase_types)
        return Skill(name=self._task_name, phases=tuple(phases), skill_type=skill_type)

    def _sample_phase(self, phase_id: str, phase_type: PhaseType) -> Phase:
        cfg = _PHASE_CONFIGS[phase_type]
        generator: GeneratorType | None = self._rng.choice(cfg.generators)
        if generator is None and cfg.ee_action is None:
            non_none = [g for g in cfg.generators if g is not None]
            generator = non_none[0] if non_none else GeneratorType.LINEAR_CARTESIAN
        control: ControlMode = self._rng.choice(cfg.controls)
        termination: TerminationCond = self._rng.choice(cfg.terminations)
        ee_action: EndEffectorAction | None = cfg.ee_action
        parameters = self._sample_parameters(phase_type)
        return Phase(phase_id=phase_id, phase_type=phase_type, generator=generator, control=control, termination=termination, end_effector_action=ee_action, parameters=parameters)

    def _sample_parameters(self, phase_type: PhaseType) -> tuple[tuple[str, PhaseParameter], ...]:
        schema = _PARAM_SCHEMA.get(phase_type, [])
        if not schema:
            return ()
        selected: list[tuple[str, PhaseParameter]] = []
        for entry in schema:
            if entry.lo >= entry.hi:
                continue
            if self._rng.random() < 0.5:
                selected.append((entry.name, PhaseParameter(type=entry.param_type, range=(entry.lo, entry.hi))))
        selected.sort(key=lambda t: t[0])
        return tuple(selected)

def sample_grammar_uniform_skill(task_name: str, rng: random.Random | None=None, min_phases: int=1) -> Skill:
    return GrammarUniformInitialiser(task_name, rng, min_phases=min_phases).sample()
