from __future__ import annotations
from dsl.nodes import TerminationCond

class TimeLimit:
    cond = TerminationCond.TIME_LIMIT

    def __init__(self, max_time: float=5.0) -> None:
        if max_time <= 0.0:
            raise ValueError(f'max_time must be positive, got {max_time}.')
        self.max_time = float(max_time)

    def is_met(self, state: dict) -> bool:
        return float(state.get('elapsed_time', 0.0)) >= self.max_time

class PoseTolerance:
    cond = TerminationCond.POSE_TOLERANCE

    def __init__(self, tol: float=0.01) -> None:
        if tol < 0.0:
            raise ValueError(f'tol must be non-negative, got {tol}.')
        self.tol = float(tol)

    def is_met(self, state: dict) -> bool:
        return float(state.get('pose_error', float('inf'))) <= self.tol

class ForceExceeded:
    cond = TerminationCond.FORCE_EXCEEDED

    def __init__(self, threshold: float=10.0) -> None:
        if threshold < 0.0:
            raise ValueError(f'threshold must be non-negative, got {threshold}.')
        self.threshold = float(threshold)

    def is_met(self, state: dict) -> bool:
        return float(state.get('contact_force', 0.0)) >= self.threshold

class ContactLost:
    cond = TerminationCond.CONTACT_LOST

    def is_met(self, state: dict) -> bool:
        return not state.get('in_contact', True)

class ContactDetectedCondition:
    cond = TerminationCond.CONTACT_DETECTED

    def is_met(self, state: dict) -> bool:
        return bool(state.get('contact_detected', False))

class GraspSuccessCondition:
    cond = TerminationCond.GRASP_SUCCESS

    def is_met(self, state: dict) -> bool:
        return bool(state.get('grasp_success', False))
_TERMINATION_REGISTRY: dict[TerminationCond, type] = {TerminationCond.TIME_LIMIT: TimeLimit, TerminationCond.POSE_TOLERANCE: PoseTolerance, TerminationCond.FORCE_EXCEEDED: ForceExceeded, TerminationCond.CONTACT_LOST: ContactLost, TerminationCond.CONTACT_DETECTED: ContactDetectedCondition, TerminationCond.GRASP_SUCCESS: GraspSuccessCondition}

def make_termination(cond: TerminationCond, **kwargs):
    cls = _TERMINATION_REGISTRY.get(cond)
    if cls is None:
        raise ValueError(f'No termination condition registered for TerminationCond.{cond.name}.')
    return cls(**kwargs)
