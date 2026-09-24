from __future__ import annotations
from dataclasses import dataclass, field
from dsl.nodes import ControlMode

@dataclass
class ControlCommand:
    mode: ControlMode
    gains: dict[str, float] = field(default_factory=dict)
    metadata: dict = field(default_factory=dict)

class PositionController:
    mode = ControlMode.POSITION_CONTROL

    def command(self, target_position, state: dict) -> ControlCommand:
        return ControlCommand(mode=self.mode, gains={}, metadata={'target_position': target_position})

class ImpedanceController:
    mode = ControlMode.IMPEDANCE_CONTROL
    _DEFAULT_STIFFNESS: float = 500.0
    _DEFAULT_DAMPING: float = 50.0

    def command(self, target_position, state: dict) -> ControlCommand:
        return ControlCommand(mode=self.mode, gains={'stiffness': self._DEFAULT_STIFFNESS, 'damping': self._DEFAULT_DAMPING}, metadata={'target_position': target_position})

class AdmittanceController:
    mode = ControlMode.ADMITTANCE_CONTROL
    _DEFAULT_MASS: float = 1.0
    _DEFAULT_DAMPING: float = 20.0

    def command(self, target_position, state: dict) -> ControlCommand:
        contact_force = state.get('contact_force', 0.0)
        return ControlCommand(mode=self.mode, gains={'mass': self._DEFAULT_MASS, 'damping': self._DEFAULT_DAMPING}, metadata={'target_position': target_position, 'contact_force': contact_force})

class ForceThresholdSwitch:
    mode = ControlMode.FORCE_THRESHOLD_SWITCH
    _DEFAULT_THRESHOLD: float = 10.0

    def command(self, target_position, state: dict) -> ControlCommand:
        contact_force = state.get('contact_force', 0.0)
        return ControlCommand(mode=self.mode, gains={}, metadata={'target_position': target_position, 'threshold': self._DEFAULT_THRESHOLD, 'contact_force': contact_force})

class ForceController:
    mode = ControlMode.FORCE_CONTROL
    _ZERO_WRENCH: list[float] = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

    def command(self, target_position, state: dict) -> ControlCommand:
        target_wrench = state.get('target_wrench', self._ZERO_WRENCH)
        return ControlCommand(mode=self.mode, gains={}, metadata={'target_wrench': target_wrench})
_CONTROLLER_REGISTRY: dict[ControlMode, type] = {ControlMode.POSITION_CONTROL: PositionController, ControlMode.IMPEDANCE_CONTROL: ImpedanceController, ControlMode.ADMITTANCE_CONTROL: AdmittanceController, ControlMode.FORCE_THRESHOLD_SWITCH: ForceThresholdSwitch, ControlMode.FORCE_CONTROL: ForceController}

def make_controller(control_mode: ControlMode):
    cls = _CONTROLLER_REGISTRY.get(control_mode)
    if cls is None:
        raise ValueError(f'No controller registered for ControlMode.{control_mode.name}.')
    return cls()
