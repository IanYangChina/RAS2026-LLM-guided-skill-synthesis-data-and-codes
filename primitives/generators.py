from __future__ import annotations
from dataclasses import dataclass, field
import numpy as np
from dsl.nodes import GeneratorType
N_STEPS: int = 20

@dataclass
class Trajectory:
    times: np.ndarray
    positions: np.ndarray
    frame: str = 'world'
    metadata: dict = field(default_factory=dict)

def _linspace_traj(start: np.ndarray, end: np.ndarray, duration: float, n: int=N_STEPS, frame: str='world', metadata: dict | None=None) -> Trajectory:
    t_norm = np.linspace(0.0, 1.0, n)
    positions = start[np.newaxis, :] + t_norm[:, np.newaxis] * (end - start)[np.newaxis, :]
    times = np.linspace(0.0, duration, n)
    return Trajectory(times=times, positions=positions, frame=frame, metadata=metadata if metadata is not None else {})

def _chord_duration(start: np.ndarray, end: np.ndarray, speed: float) -> float:
    dist = float(np.linalg.norm(end - start))
    return dist / speed if speed > 0.0 and dist > 0.0 else 1.0

def _state_waypoint_count(state: dict, default: int=N_STEPS) -> int:
    raw = state.get('n_waypoints', default)
    try:
        value = int(raw)
    except (TypeError, ValueError):
        value = default
    return max(1, value)

class LinearCartesianGenerator:
    generator_type = GeneratorType.LINEAR_CARTESIAN

    def generate(self, params: dict[str, float], state: dict) -> Trajectory:
        start = np.asarray(state['start'], dtype=float)
        end = np.asarray(state['end'], dtype=float)
        speed = float(params.get('push_speed', params.get('speed', params.get('reach_speed', 0.1))))
        duration = _chord_duration(start, end, speed)
        n = _state_waypoint_count(state)
        return _linspace_traj(start, end, duration, n=n)

class ArcCartesianGenerator:
    generator_type = GeneratorType.ARC_CARTESIAN

    def generate(self, params: dict[str, float], state: dict) -> Trajectory:
        start = np.asarray(state['start'], dtype=float)
        end = np.asarray(state['end'], dtype=float)
        speed = float(params.get('speed', params.get('reach_speed', 0.1)))
        if 'arc_angle' in params:
            arc_angle = float(params['arc_angle'])
        elif 'arc_height' in params:
            chord_len = float(np.linalg.norm(end - start))
            h = float(params['arc_height'])
            if chord_len > 1e-06 and h > 1e-06:
                r = (chord_len ** 2 / 4.0 + h ** 2) / (2.0 * h)
                half_angle = np.arcsin(min(chord_len / (2.0 * r), 1.0))
                arc_angle = 2.0 * half_angle
            else:
                arc_angle = float(np.pi / 4.0)
        elif 'arc_angle_override' in state:
            arc_angle = float(state['arc_angle_override'])
        else:
            arc_angle = float(np.pi / 4.0)
        chord = end - start
        chord_len = float(np.linalg.norm(chord))
        half_angle = arc_angle / 2.0
        if chord_len < 1e-09 or abs(np.sin(half_angle)) < 1e-09:
            duration = _chord_duration(start, end, speed)
            return _linspace_traj(start, end, duration, n=_state_waypoint_count(state))
        radius = chord_len / (2.0 * abs(np.sin(half_angle)))
        chord_unit = chord / chord_len
        ref = np.array([0.0, 0.0, 1.0])
        if abs(np.dot(chord_unit, ref)) > 0.9:
            ref = np.array([0.0, 1.0, 0.0])
        perp = ref - np.dot(ref, chord_unit) * chord_unit
        perp /= np.linalg.norm(perp)
        midpoint = (start + end) / 2.0
        h = radius * np.cos(half_angle)
        center = midpoint - h * perp
        v_start = start - center
        v_end = end - center
        arc_normal_raw = np.cross(v_start, v_end)
        arc_normal_len = float(np.linalg.norm(arc_normal_raw))
        if arc_normal_len < 1e-09:
            v_start_unit_tmp = v_start / (float(np.linalg.norm(v_start)) + 1e-15)
            arc_normal = np.cross(v_start_unit_tmp, perp)
            n_len = float(np.linalg.norm(arc_normal))
            arc_normal = arc_normal / n_len if n_len > 1e-09 else perp.copy()
        else:
            arc_normal = arc_normal_raw / arc_normal_len
        v_start_unit = v_start / (float(np.linalg.norm(v_start)) + 1e-15)
        perp_in_plane = np.cross(arc_normal, v_start_unit)
        n = _state_waypoint_count(state)
        theta = np.linspace(0.0, arc_angle, n)
        positions = center[np.newaxis, :] + radius * (np.cos(theta)[:, np.newaxis] * v_start_unit[np.newaxis, :] + np.sin(theta)[:, np.newaxis] * perp_in_plane[np.newaxis, :])
        arc_length = abs(radius * arc_angle)
        duration = arc_length / speed if speed > 0.0 else 1.0
        times = np.linspace(0.0, duration, n)
        return Trajectory(times=times, positions=positions, frame='world')

class BezierCurveGenerator:
    generator_type = GeneratorType.BEZIER_CURVE

    def generate(self, params: dict[str, float], state: dict) -> Trajectory:
        start = np.asarray(state['start'], dtype=float)
        end = np.asarray(state['end'], dtype=float)
        speed = float(params.get('speed', params.get('reach_speed', 0.1)))
        ctrl1_raw = params.get('ctrl1', None)
        ctrl2_raw = params.get('ctrl2', None)
        chord = end - start
        chord_len = float(np.linalg.norm(chord))
        chord_unit = chord / chord_len if chord_len > 1e-09 else np.zeros_like(chord)
        if ctrl1_raw is None or ctrl2_raw is None:
            bz_height_raw = params.get('bezier_height', params.get('ctrl_height', None))
            if bz_height_raw is not None:
                bz_height = float(bz_height_raw)
                p1 = start + chord / 3.0 + np.array([0.0, 0.0, bz_height])
                p2 = start + 2.0 * chord / 3.0 + np.array([0.0, 0.0, bz_height])
            else:
                p1 = start + chord / 3.0
                p2 = start + 2.0 * chord / 3.0
        else:
            ctrl1 = np.asarray(ctrl1_raw, dtype=float)
            ctrl2 = np.asarray(ctrl2_raw, dtype=float)
            if ctrl1.ndim == 0:
                ctrl1 = float(ctrl1) * chord_unit
            if ctrl2.ndim == 0:
                ctrl2 = float(ctrl2) * chord_unit
            p1 = start + ctrl1
            p2 = end + ctrl2
        n = _state_waypoint_count(state)
        t = np.linspace(0.0, 1.0, n)
        b = ((1.0 - t) ** 3)[:, np.newaxis] * start[np.newaxis, :] + (3.0 * (1.0 - t) ** 2 * t)[:, np.newaxis] * p1[np.newaxis, :] + (3.0 * (1.0 - t) * t ** 2)[:, np.newaxis] * p2[np.newaxis, :] + (t ** 3)[:, np.newaxis] * end[np.newaxis, :]
        duration = _chord_duration(start, end, speed)
        times = np.linspace(0.0, duration, n)
        return Trajectory(times=times, positions=b, frame='world')

class JointInterpolationGenerator:
    generator_type = GeneratorType.JOINT_INTERPOLATION

    def generate(self, params: dict[str, float], state: dict) -> Trajectory:
        q_start = np.asarray(state['q_start'], dtype=float)
        q_end = np.asarray(state['q_end'], dtype=float)
        speed = float(params.get('speed', 1.0))
        delta = q_end - q_start
        max_disp = float(np.max(np.abs(delta))) if delta.size > 0 else 0.0
        duration = max_disp / speed if speed > 0.0 and max_disp > 0.0 else 1.0
        n = _state_waypoint_count(state)
        tau = np.linspace(0.0, 1.0, n)
        smooth_tau = 3.0 * tau ** 2 - 2.0 * tau ** 3
        positions = q_start[np.newaxis, :] + smooth_tau[:, np.newaxis] * delta[np.newaxis, :]
        times = np.linspace(0.0, duration, n)
        return Trajectory(times=times, positions=positions, frame='joint')

class ImpedanceMotionGenerator:
    generator_type = GeneratorType.IMPEDANCE_MOTION

    def generate(self, params: dict[str, float], state: dict) -> Trajectory:
        start = np.asarray(state['start'], dtype=float)
        end = np.asarray(state['end'], dtype=float)
        speed = float(params.get('push_speed', params.get('speed', params.get('reach_speed', 0.1))))
        stiffness = float(params.get('contact_force', 5.0)) * 25.0
        duration = _chord_duration(start, end, speed)
        return _linspace_traj(start, end, duration, n=_state_waypoint_count(state), metadata={'compliance': True, 'stiffness': stiffness})
_GENERATOR_REGISTRY: dict[GeneratorType, type] = {GeneratorType.LINEAR_CARTESIAN: LinearCartesianGenerator, GeneratorType.ARC_CARTESIAN: ArcCartesianGenerator, GeneratorType.BEZIER_CURVE: BezierCurveGenerator, GeneratorType.JOINT_INTERPOLATION: JointInterpolationGenerator, GeneratorType.IMPEDANCE_MOTION: ImpedanceMotionGenerator}

def make_generator(generator_type: GeneratorType):
    cls = _GENERATOR_REGISTRY.get(generator_type)
    if cls is None:
        raise ValueError(f'No generator registered for GeneratorType.{generator_type.name}.')
    return cls()
