from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass, field
import math
from typing import Any
import numpy as np

def _vector_to_list(value: tuple[float, ...] | list[float] | np.ndarray | None) -> list[float] | None:
    if value is None:
        return None
    arr = np.asarray(value, dtype=float).reshape(-1)
    if not np.all(np.isfinite(arr)):
        return None
    return [float(x) for x in arr]

def finite_contact_force(value: object) -> float | None:
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return None
    return numeric if math.isfinite(numeric) else None

def _contact_force_sort_key(value: object) -> float:
    force = finite_contact_force(value)
    return -force if force is not None else float('inf')

def sanitise_diagnostic_value(value: Any) -> Any:
    if isinstance(value, np.ndarray):
        return sanitise_diagnostic_value(value.tolist())
    if isinstance(value, np.floating):
        return finite_contact_force(value)
    if isinstance(value, float):
        return value if math.isfinite(value) else None
    if isinstance(value, dict):
        return {key: sanitise_diagnostic_value(item) for (key, item) in value.items()}
    if isinstance(value, list):
        return [sanitise_diagnostic_value(item) for item in value]
    if isinstance(value, tuple):
        return tuple((sanitise_diagnostic_value(item) for item in value))
    return value

def apply_binding_mode(base_value: float, sampled_value: float, mode: str) -> float:
    if mode == 'replace':
        return float(sampled_value)
    if mode == 'scale':
        return float(base_value) * float(sampled_value)
    return float(base_value) + float(sampled_value)

def summarise_target_resolution_sources(phase_rows: list[dict]) -> dict[str, int]:
    summary: dict[str, int] = {}
    for row in phase_rows:
        target = row.get('target') if isinstance(row, dict) else None
        if not isinstance(target, dict):
            continue
        source = str(target.get('source', 'unknown'))
        summary[source] = summary.get(source, 0) + 1
    return summary

@dataclass
class ContactEvent:
    time: float
    force: float
    in_contact: bool
    episode_index: int | None = None
    phase_index: int | None = None
    phase_name: str | None = None
    phase_type: str | None = None
    sim_step: int | None = None
    body_a: str | None = None
    geom_a: str | None = None
    body_b: str | None = None
    geom_b: str | None = None
    contact_point: tuple[float, float, float] | None = None
    contact_normal: tuple[float, float, float] | None = None
    contact_distance: float | None = None
    tcp_position: tuple[float, float, float] | None = None
    involves_obstacle: bool | None = None
    involves_robot_link: bool | None = None
    involves_task_object: bool | None = None

    def to_dict(self) -> dict:
        data = asdict(self)
        data['time'] = finite_contact_force(self.time)
        data['force'] = finite_contact_force(self.force)
        data['contact_point'] = _vector_to_list(self.contact_point)
        data['contact_normal'] = _vector_to_list(self.contact_normal)
        data['tcp_position'] = _vector_to_list(self.tcp_position)
        return data

    def pair_key(self) -> tuple:
        pair_a = (self.body_a, self.geom_a)
        pair_b = (self.body_b, self.geom_b)
        ordered = tuple(sorted((pair_a, pair_b), key=lambda item: (item[0] or '', item[1] or '')))
        return (self.phase_index, self.phase_name, self.phase_type, *ordered)

@dataclass
class EpisodeTrace:
    skill_name: str
    parameter_values: dict[str, float]
    success: bool
    duration: float
    final_pose_error: float
    peak_contact_force: float
    trajectory_positions: np.ndarray
    contact_history: list[ContactEvent] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)

def select_contact_events_for_storage(events: list[ContactEvent], *, max_events: int, top_force_events: int=8, top_obstacle_events: int=8) -> list[ContactEvent]:
    if max_events <= 0 or not events:
        return []
    indexed = list(enumerate(events))
    priority: dict[int, tuple[int, float, float, int]] = {}
    top_force = sorted(indexed, key=lambda item: (_contact_force_sort_key(item[1].force), item[1].time, item[0]))[:min(top_force_events, max_events)]
    for (rank, (idx, event)) in enumerate(top_force):
        priority[idx] = min(priority.get(idx, (10 ** 9, 0.0, 0.0, idx)), (rank, _contact_force_sort_key(event.force), event.time, idx))
    obstacle_candidates = [item for item in indexed if bool(item[1].involves_obstacle)]
    top_obstacle = sorted(obstacle_candidates, key=lambda item: (_contact_force_sort_key(item[1].force), item[1].time, item[0]))[:min(top_obstacle_events, max_events)]
    for (rank, (idx, event)) in enumerate(top_obstacle):
        priority[idx] = min(priority.get(idx, (10 ** 9, 0.0, 0.0, idx)), (rank, _contact_force_sort_key(event.force), event.time, idx))
    selected = {idx for idx in sorted(priority, key=lambda i: priority[i])[:max_events]}
    if len(selected) < max_events:
        for (idx, _event) in indexed:
            selected.add(idx)
            if len(selected) >= max_events:
                break
    return [events[idx] for idx in sorted(selected, key=lambda i: (events[i].time, _contact_force_sort_key(events[i].force), i))]

def summarise_contact_events(events: list[ContactEvent]) -> list[dict]:
    if not events:
        return []
    grouped: dict[tuple, list[ContactEvent]] = {}
    for event in events:
        grouped.setdefault(event.pair_key(), []).append(event)
    summary_rows: list[dict] = []
    for key in sorted(grouped, key=lambda item: tuple(('' if v is None else str(v) for v in item))):
        group = grouped[key]
        forces = [force for event in group if (force := finite_contact_force(event.force)) is not None]
        points = [point for event in group if (point := _vector_to_list(event.contact_point)) is not None]
        tcp_points = [point for event in group if (point := _vector_to_list(event.tcp_position)) is not None]
        distances = [distance for event in group if (distance := finite_contact_force(event.contact_distance)) is not None]
        row = {'phase_index': group[0].phase_index, 'phase_name': group[0].phase_name, 'phase_type': group[0].phase_type, 'body_a': group[0].body_a, 'geom_a': group[0].geom_a, 'body_b': group[0].body_b, 'geom_b': group[0].geom_b, 'contact_count': len(group), 'first_time': float(min((event.time for event in group))), 'last_time': float(max((event.time for event in group))), 'first_step': min((event.sim_step for event in group if event.sim_step is not None), default=None), 'max_force': float(np.max(forces)) if forces else None, 'mean_force': float(np.mean(forces)) if forces else None, 'force_p95': float(np.percentile(forces, 95)) if forces else None, 'contact_point_centroid': _vector_to_list(np.mean(np.array(points, dtype=float), axis=0)) if points else None, 'tcp_position_centroid': _vector_to_list(np.mean(np.array(tcp_points, dtype=float), axis=0)) if tcp_points else None, 'min_contact_distance': float(min(distances)) if distances else None, 'max_contact_distance': float(max(distances)) if distances else None, 'involves_obstacle': any((bool(event.involves_obstacle) for event in group)), 'involves_robot_link': any((bool(event.involves_robot_link) for event in group)), 'involves_task_object': any((bool(event.involves_task_object) for event in group))}
        summary_rows.append(row)
    return summary_rows

class SimulatorBackend(ABC):

    @abstractmethod
    def run_episode(self, artifact, parameter_values: dict[str, float], scene_config: dict | None=None, task_spec=None) -> EpisodeTrace:
        ...

    @abstractmethod
    def is_available(self) -> bool:
        ...

    @property
    @abstractmethod
    def name(self) -> str:
        ...

    def freeze_scene_randomisation(self) -> None:
        """Fix the scene perturbation for all subsequent episodes (no-op base)."""

    def unfreeze_scene_randomisation(self) -> None:
        """Re-enable per-episode randomisation (no-op base)."""
