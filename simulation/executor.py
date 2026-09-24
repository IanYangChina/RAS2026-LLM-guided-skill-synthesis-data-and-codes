from __future__ import annotations
import logging
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Callable, Optional
import mujoco
import numpy as np
from primitives.generators import Trajectory
from simulation.ik import get_tcp_pose, solve_ik
if TYPE_CHECKING:
    from primitives.control import ControlCommand
    from dsl.nodes import ControlMode
logger = logging.getLogger(__name__)

@dataclass
class StepRecord:
    time: float
    qpos: np.ndarray
    qvel: np.ndarray
    tcp_pos: np.ndarray
    tcp_quat: np.ndarray
    ctrl: np.ndarray
    contact_forces: list

@dataclass
class IKStatistics:
    solve_count: int = 0
    success_count: int = 0
    failure_count: int = 0
    _iteration_total: int = 0

    def record(self, *, success: bool, iterations: int) -> None:
        self.solve_count += 1
        self._iteration_total += int(iterations)
        if success:
            self.success_count += 1
        else:
            self.failure_count += 1

    def to_dict(self) -> dict[str, int | float]:
        mean_iterations = self._iteration_total / self.solve_count if self.solve_count else 0.0
        return {'solve_count': self.solve_count, 'success_count': self.success_count, 'failure_count': self.failure_count, 'mean_iterations': mean_iterations}

def execute_trajectory(model: mujoco.MjModel, data: mujoco.MjData, trajectory: Trajectory, site_name: str='attachment_site', kp: float=100.0, kd: float=10.0, dt_sim: Optional[float]=None, max_steps_per_waypoint: int=200, max_total_steps: Optional[int]=None, pos_tol: float=0.005, step_callback: Callable[[mujoco.MjModel, mujoco.MjData], None] | None=None, cmd: Optional['ControlCommand']=None, termination_hook=None, ik_statistics: IKStatistics | None=None) -> list:
    from primitives.control import ControlCommand as _ControlCommand
    from dsl.nodes import ControlMode as _ControlMode
    kp_eff: float = kp
    kd_eff: float = kd
    if cmd is not None:
        if cmd.mode == _ControlMode.IMPEDANCE_CONTROL:
            stiffness = cmd.gains.get('stiffness', 500.0)
            damping = cmd.gains.get('damping', 50.0)
            kp_eff = kp * (stiffness / 500.0)
            kd_eff = kd * (damping / 50.0)
        elif cmd.mode == _ControlMode.ADMITTANCE_CONTROL:
            kp_eff = kp * 0.3
            kd_eff = kd * 2.0
        elif cmd.mode == _ControlMode.FORCE_CONTROL:
            kp_eff = kp * 0.05
            kd_eff = kd * 1.0
    logger.debug('execute_trajectory: mode=%s  kp_eff=%.3f  kd_eff=%.3f', cmd.mode.name if cmd is not None else 'None', kp_eff, kd_eff)
    if dt_sim is not None:
        model.opt.timestep = float(dt_sim)
    (n_waypoints, _) = trajectory.positions.shape
    if n_waypoints == 0:
        return []
    orientations = trajectory.metadata.get('orientations', None)
    axis_alignment = trajectory.metadata.get('axis_alignment', None)
    records: list[StepRecord] = []
    prev_ik_q: np.ndarray | None = None
    total_steps = 0
    _n_arm_act: int
    if model.nu > 0:
        _n_arm_act = sum((1 for i in range(model.nu) if model.actuator_trntype[i] != mujoco.mjtTrn.mjTRN_TENDON))
    else:
        _n_arm_act = 0
    for i in range(n_waypoints):
        waypoint_pos = np.asarray(trajectory.positions[i], dtype=float)
        if trajectory.frame == 'world':
            target_quat = None
            if orientations is not None:
                target_quat = np.asarray(orientations[i], dtype=float)
            local_axis = None
            target_axis = None
            if target_quat is None and axis_alignment is not None:
                local_axis = np.asarray(axis_alignment['local_axis'], dtype=float)
                target_axis = np.asarray(axis_alignment['target_axis'], dtype=float)
            saved_qpos = data.qpos.copy()
            if prev_ik_q is not None:
                nq_seed = min(len(prev_ik_q), model.nq)
                data.qpos[:nq_seed] = prev_ik_q[:nq_seed]
                mujoco.mj_forward(model, data)
            ik_result = solve_ik(model, data, target_pos=waypoint_pos, target_quat=target_quat, site_name=site_name, local_axis=local_axis, target_axis=target_axis)
            if ik_statistics is not None:
                ik_statistics.record(success=ik_result.success, iterations=ik_result.iterations)
            data.qpos[:] = saved_qpos
            mujoco.mj_forward(model, data)
            if not ik_result.success:
                logger.warning('IK failed for waypoint %d (pos=%s): error_pos=%.4f m. Skipping waypoint.', i, waypoint_pos, ik_result.error_pos)
                continue
            q_target = ik_result.q
            prev_ik_q = q_target.copy()
            logger.debug('Waypoint %d/%d: IK %s in %d iter, pos_err=%.4f m', i, n_waypoints, 'OK' if ik_result.success else 'FAILED', ik_result.iterations, ik_result.error_pos)
        else:
            q_target = np.asarray(waypoint_pos, dtype=float)
        for _ in range(max_steps_per_waypoint):
            if max_total_steps is not None and total_steps >= max_total_steps:
                return records
            n_ctrl = _n_arm_act if _n_arm_act > 0 else model.nu if model.nu > 0 else model.nq
            ctrl_raw = q_target[:n_ctrl].copy()
            if model.nu > 0:
                n_clip = min(_n_arm_act, ctrl_raw.shape[0])
                ctrl_clipped = ctrl_raw[:n_clip].copy()
                lo = model.actuator_ctrlrange[:n_clip, 0]
                hi = model.actuator_ctrlrange[:n_clip, 1]
                active = hi > lo
                ctrl_clipped = np.where(active, np.clip(ctrl_clipped, lo, hi), ctrl_clipped)
                data.ctrl[:n_clip] = ctrl_clipped
            mujoco.mj_step(model, data)
            if step_callback is not None:
                step_callback(model, data)
            (tcp_pos, tcp_quat) = get_tcp_pose(model, data, site_name=site_name)
            contact_forces: list[float] = []
            for c in range(data.ncon):
                force_buf = np.zeros(6)
                mujoco.mj_contactForce(model, data, c, force_buf)
                contact_forces.append(float(np.linalg.norm(force_buf[:3])))
            records.append(StepRecord(time=float(data.time), qpos=data.qpos[:model.nq].copy(), qvel=data.qvel[:model.nv].copy(), tcp_pos=tcp_pos, tcp_quat=tcp_quat, ctrl=data.ctrl[:model.nu].copy(), contact_forces=contact_forces))
            total_steps += 1
            if termination_hook is not None and termination_hook():
                return records
            if trajectory.frame == 'world':
                dist = float(np.linalg.norm(tcp_pos - waypoint_pos))
            else:
                dist = float(np.linalg.norm(data.qpos[:model.nq] - q_target[:model.nq]))
            if dist < pos_tol:
                break
    return records

def records_to_arrays(records: list) -> dict:
    return {'time': np.array([r.time for r in records]), 'qpos': np.stack([r.qpos for r in records]), 'qvel': np.stack([r.qvel for r in records]), 'tcp_pos': np.stack([r.tcp_pos for r in records]), 'tcp_quat': np.stack([r.tcp_quat for r in records]), 'ctrl': np.stack([r.ctrl for r in records])}
