from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional
from dsl.nodes import ControlMode, EndEffectorAction, Guard, ParameterConsumptionEntry, Phase, PhaseTarget, RetryPolicy, Skill
from dsl.validator import parameter_consumption_report, validate
from primitives.control import ControlCommand, make_controller
from primitives.generators import Trajectory, make_generator
from primitives.termination import make_termination

@dataclass(frozen=True)
class PhaseArtifact:
    phase_name: str
    phase_id: str
    phase_type: str
    generator: object
    controller: object
    termination: object
    end_effector_action: Optional[EndEffectorAction] = None
    subtask_id: Optional[str] = None
    target: PhaseTarget | None = None
    parameter_bindings: dict[str, ParameterConsumptionEntry] = field(default_factory=dict)
    guards: tuple[Guard, ...] = ()
    retries: RetryPolicy | None = None
    dsl_version: int = 1

@dataclass(frozen=True)
class ControllerArtifact:
    skill_name: str
    parameter_names: tuple[str, ...]
    parameter_ranges: dict[str, tuple[float, float]]
    phases: tuple[PhaseArtifact, ...]
    dsl_version: int = 1
    parameter_consumption_report: dict[str, ParameterConsumptionEntry] = field(default_factory=dict)
    parameter_defaults: dict[str, float | str | tuple[float, ...]] = field(default_factory=dict)

    def run_phase(self, phase_idx: int, params: dict[str, float], state: dict) -> tuple[Trajectory | None, ControlCommand]:
        if phase_idx < 0 or phase_idx >= len(self.phases):
            raise IndexError(f"phase_idx {phase_idx} is out of range for skill '{self.skill_name}' which has {len(self.phases)} phase(s).")
        pa: PhaseArtifact = self.phases[phase_idx]
        prefix = pa.phase_id + '.'
        local_params = {k[len(prefix):]: v for (k, v) in params.items() if k.startswith(prefix)}
        if not local_params and params:
            local_params = params
        if pa.generator is None:
            traj = None
            target_position = None
        else:
            traj = pa.generator.generate(local_params, state)
            target_position = traj.positions[-1]
        cmd: ControlCommand = pa.controller.command(target_position, state)
        if traj is not None and cmd.mode == ControlMode.IMPEDANCE_CONTROL and ('stiffness' in traj.metadata):
            cmd.gains['stiffness'] = float(traj.metadata['stiffness'])
        return (traj, cmd)

def _phase_parameter_bindings(phase: Phase, report: dict[str, ParameterConsumptionEntry]) -> dict[str, ParameterConsumptionEntry]:
    return {pname: report[f'{phase.phase_id}.{pname}'] for (pname, _) in phase.parameters if f'{phase.phase_id}.{pname}' in report}

def _make_phase_termination(phase: Phase) -> object:
    kwargs: dict[str, float] = {}
    if phase.target is not None and phase.target.tolerance is not None and (phase.termination is not None) and (phase.termination.name == 'POSE_TOLERANCE'):
        kwargs['tol'] = float(phase.target.tolerance)
    return make_termination(phase.termination, **kwargs)

def compile(skill: Skill) -> ControllerArtifact:
    errors = validate(skill)
    if errors:
        msg = '\n'.join((error.message for error in errors))
        raise ValueError(f"Cannot compile invalid skill '{skill.name}':\n{msg}")
    flat_consumption_report = parameter_consumption_report(skill, as_entries=True)
    phases: tuple[PhaseArtifact, ...] = tuple((PhaseArtifact(phase_name=ph.phase_id, phase_id=ph.phase_id, phase_type=ph.phase_type.value, generator=make_generator(ph.generator) if ph.generator is not None else None, controller=make_controller(ph.control), termination=_make_phase_termination(ph), end_effector_action=ph.end_effector_action, subtask_id=ph.subtask_id, target=ph.target, parameter_bindings=_phase_parameter_bindings(ph, flat_consumption_report), guards=ph.guards, retries=ph.retries, dsl_version=skill.dsl_version) for ph in skill.phases))
    flat_names: list[str] = []
    flat_ranges: dict[str, tuple[float, float]] = {}
    flat_defaults: dict[str, float | str | tuple[float, ...]] = {}
    for ph in skill.phases:
        for (pname, pparam) in ph.parameters:
            key = f'{ph.phase_id}.{pname}'
            flat_names.append(key)
            flat_ranges[key] = pparam.range
            if pparam.default is not None:
                flat_defaults[key] = pparam.default
    return ControllerArtifact(skill_name=skill.name, parameter_names=tuple(flat_names), parameter_ranges=flat_ranges, phases=phases, parameter_defaults=flat_defaults, dsl_version=skill.dsl_version, parameter_consumption_report=flat_consumption_report)
