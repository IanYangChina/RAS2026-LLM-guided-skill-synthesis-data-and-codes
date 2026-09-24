from __future__ import annotations
from dataclasses import dataclass
from simulation.backend import EpisodeTrace

@dataclass(frozen=True)
class FeasibilityReport:
    reachable: bool
    collision_free: bool
    within_force_limits: bool
    contact_valid: bool
    overall: bool

def check_feasibility(trace: EpisodeTrace, force_limit: float=20.0, pose_error_limit: float=0.05) -> FeasibilityReport:
    reachable: bool = trace.final_pose_error < pose_error_limit
    collision: bool = bool(trace.metadata.get('collision', False))
    collision_free: bool = not collision
    within_force_limits: bool = trace.peak_contact_force < force_limit
    contact_valid: bool = len(trace.contact_history) > 0
    overall: bool = reachable and collision_free and within_force_limits and contact_valid
    return FeasibilityReport(reachable=reachable, collision_free=collision_free, within_force_limits=within_force_limits, contact_valid=contact_valid, overall=overall)
