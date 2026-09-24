from __future__ import annotations
from dataclasses import dataclass
from typing import Literal
AnchorFrame = Literal['world', 'object', 'goal', 'fixture']

@dataclass(frozen=True)
class SubtaskSpec:
    id: str
    target_entity: str
    metric: str
    anchor: AnchorFrame
    offset: tuple[float, float, float] = (0.0, 0.0, 0.0)
    param_offset_key: str | None = None
    weight: float = 1.0

@dataclass(frozen=True)
class PhaseTargetSpec:
    anchor: AnchorFrame
    offset: tuple[float, float, float]
    tolerance: float = 0.01

@dataclass(frozen=True)
class TaskSpec:
    goal_tcp_position: tuple[float, float, float]
    object_initial_pose: tuple[float, float, float] | None = None
    goal_object_position: tuple[float, float, float] | None = None
    fixture_pose: tuple[float, float, float] | None = None
    initial_hinge_angle: float | None = None
    perturbation_range: float = 0.02
    goal_tolerance: float = 0.05
    expressivity_sigma: float = 0.15
    expressivity_threshold: float = 0.3
    force_limit: float = 15.0
    hole_depth: float | None = None
    min_phases: int = 1
    grasp_target_body: str | None = None
    grasp_approach_position: tuple[float, float, float] | None = None
    place_goal_position: tuple[float, float, float] | None = None
    obstacle_body_name: str | None = None
    obstacle_height: float | None = None
    force_scale: float = 5.0
    obstacle_position: tuple[float, float, float] | None = None
    arm_initial_tcp_position: tuple[float, float, float] | None = None
    hinge_body_name: str | None = None
    hinge_joint_name: str | None = None
    target_hinge_angle: float | None = None
    door_handle_site: str | None = None
    channel_axis: tuple[float, float, float] | None = None
    channel_wall_bodies: tuple[str, str] | None = None
    peg_body_name: str | None = None
    channel_length: float | None = None
    phase_target_map: dict | None = None
    phase_type_aliases: dict[str, str] | None = None
    subtasks: tuple[SubtaskSpec, ...] | None = None
    open_settle_mode: str = 'static_hold'
    open_settle_retract_z: float = 0.05
