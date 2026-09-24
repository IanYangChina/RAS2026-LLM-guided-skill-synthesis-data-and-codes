from __future__ import annotations
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any
from enum import Enum, auto

class ParameterType(Enum):
    SCALAR = auto()
    ANGLE = auto()
    VECTOR = auto()
    FRAME = auto()
    CATEGORICAL = auto()

class PhaseType(Enum):
    APPROACH = 'approach'
    ALIGN = 'align'
    DESCEND = 'descend'
    CONTACT = 'contact'
    PUSH = 'push'
    PULL = 'pull'
    INSERT = 'insert'
    LIFT = 'lift'
    RETRACT = 'retract'
    ROTATE = 'rotate'
    GRASP = 'grasp'
    RELEASE = 'release'

class GeneratorType(Enum):
    LINEAR_CARTESIAN = auto()
    ARC_CARTESIAN = auto()
    BEZIER_CURVE = auto()
    JOINT_INTERPOLATION = auto()
    IMPEDANCE_MOTION = auto()

class ControlMode(Enum):
    POSITION_CONTROL = auto()
    IMPEDANCE_CONTROL = auto()
    ADMITTANCE_CONTROL = auto()
    FORCE_THRESHOLD_SWITCH = auto()
    FORCE_CONTROL = auto()

class SkillType(Enum):
    ARM = auto()
    GRIPPER = auto()
    ARM_GRIPPER = auto()

class EndEffectorAction(Enum):
    OPEN = auto()
    CLOSE = auto()
    PARTIAL = auto()
    FORCE_GRASP = auto()

class TerminationCond(Enum):
    TIME_LIMIT = auto()
    POSE_TOLERANCE = auto()
    FORCE_EXCEEDED = auto()
    CONTACT_LOST = auto()
    CONTACT_DETECTED = auto()
    GRASP_SUCCESS = auto()

@dataclass(frozen=True)
class OffsetAlongAxis:
    distance: float
    axis: str
    mode: str = 'add_to_offset'
    sign: str = 'positive'

@dataclass(frozen=True)
class OrientationTarget:
    mode: str = 'none'
    quat: tuple[float, float, float, float] | None = None
    axis: tuple[float, float, float] | None = None
    align_with: str | None = None
    tolerance: float | None = None

@dataclass(frozen=True)
class PhaseTarget:
    source: str
    anchor: str
    offset: tuple[float, float, float]
    entity: str | None = None
    offset_along_axis: OffsetAlongAxis | None = None
    tolerance: float | None = None
    orientation: OrientationTarget | None = None

@dataclass(frozen=True)
class ParameterBinding:
    path: str
    mode: str = 'add'
    frame: str | None = None

@dataclass(frozen=True)
class Guard:
    guard_id: str
    when: str
    predicate: str
    args: tuple[tuple[str, Any], ...] = ()
    threshold: float | None = None
    on_failure: str = 'abort'

@dataclass(frozen=True)
class RetryPolicy:
    max_attempts: int = 0
    strategy: str = 'repeat'
    offset: tuple[float, float, float] | None = None
    reduce_speed_factor: float = 0.5
    increase_force_limit_factor: float = 1.25

@dataclass(frozen=True)
class BindingConsumptionRecord:
    path: str
    mode: str
    before: Any | None = None
    after: Any | None = None

@dataclass(frozen=True)
class ParameterConsumptionEntry:
    status: str
    type: str
    sampled_value: Any | None = None
    bindings: tuple[BindingConsumptionRecord, ...] = ()
    justification: str | None = None

@dataclass(frozen=True)
class ParameterDef:
    name: str
    type: ParameterType
    range: tuple[float, float]
    default: float | str | tuple[float, ...] | None = None
    binds_to: tuple[ParameterBinding, ...] = ()
    diagnostic_only: bool = False
    unused_allowed: bool = False
    justification: str | None = None

    def normalize(self, value: float) -> float:
        (lo, hi) = self.range
        return 2.0 * (value - lo) / (hi - lo) - 1.0

    def denormalize(self, norm_value: float) -> float:
        (lo, hi) = self.range
        return lo + (norm_value + 1.0) * 0.5 * (hi - lo)

@dataclass(frozen=True)
class PhaseParameter:
    type: ParameterType
    range: tuple[float, float]
    default: float | str | tuple[float, ...] | None = None
    binds_to: tuple[ParameterBinding, ...] = ()
    diagnostic_only: bool = False
    unused_allowed: bool = False
    justification: str | None = None

    def normalize(self, value: float) -> float:
        (lo, hi) = self.range
        return 2.0 * (value - lo) / (hi - lo) - 1.0

    def denormalize(self, norm_value: float) -> float:
        (lo, hi) = self.range
        return lo + (norm_value + 1.0) * 0.5 * (hi - lo)

@dataclass(frozen=True)
class Phase:
    phase_id: str
    phase_type: PhaseType
    generator: GeneratorType | None = None
    control: ControlMode = ControlMode.POSITION_CONTROL
    termination: TerminationCond = TerminationCond.POSE_TOLERANCE
    end_effector_action: EndEffectorAction | None = None
    parameters: tuple[tuple[str, PhaseParameter], ...] = ()
    subtask_id: str | None = None
    target: PhaseTarget | None = None
    guards: tuple[Guard, ...] = ()
    retries: RetryPolicy | None = None

@dataclass(frozen=True)
class Skill:
    name: str
    phases: tuple[Phase, ...]
    skill_type: SkillType = SkillType.ARM
    skill_subtasks: tuple[dict, ...] | None = None
    dsl_version: int = 1

    @property
    def param_dim(self) -> int:
        return sum((len(ph.parameters) for ph in self.phases))

    def flat_param_names(self) -> tuple[str, ...]:
        return tuple((f'{ph.phase_id}.{pname}' for ph in self.phases for (pname, _) in ph.parameters))

    def normalize_params(self, values: dict[str, float]) -> list[float]:
        result: list[float] = []
        for ph in self.phases:
            for (pname, pparam) in ph.parameters:
                key = f'{ph.phase_id}.{pname}'
                result.append(pparam.normalize(values[key]))
        return result

    def denormalize_params(self, norm_vec: Sequence[float]) -> dict[str, float]:
        result: dict[str, float] = {}
        i = 0
        for ph in self.phases:
            for (pname, pparam) in ph.parameters:
                key = f'{ph.phase_id}.{pname}'
                result[key] = pparam.denormalize(norm_vec[i])
                i += 1
        return result

    def phase_local_params(self, phase_id: str, flat_params: dict[str, float]) -> dict[str, float]:
        prefix = phase_id + '.'
        return {k[len(prefix):]: v for (k, v) in flat_params.items() if k.startswith(prefix)}
