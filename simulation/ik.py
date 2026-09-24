from __future__ import annotations
from dataclasses import dataclass
import mujoco
import numpy as np

@dataclass
class IKResult:
    success: bool
    q: np.ndarray
    error_pos: float
    error_rot: float
    iterations: int

def _get_site_id(model: mujoco.MjModel, site_name: str) -> int:
    site_id = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_SITE, site_name)
    if site_id == -1:
        available = [mujoco.mj_id2name(model, mujoco.mjtObj.mjOBJ_SITE, i) for i in range(model.nsite)]
        raise ValueError(f'Site {site_name!r} not found in model.  Available sites: {available}')
    return site_id

def _quat_error(target_quat: np.ndarray, current_quat: np.ndarray) -> np.ndarray:
    q_inv = current_quat.copy()
    q_inv[1:] *= -1.0
    q_diff = np.zeros(4)
    mujoco.mju_mulQuat(q_diff, target_quat, q_inv)
    if q_diff[0] < 0.0:
        q_diff = -q_diff
    return 2.0 * q_diff[1:]

def _normalise_vec(vec: np.ndarray, *, name: str) -> np.ndarray:
    arr = np.asarray(vec, dtype=float)
    norm = float(np.linalg.norm(arr))
    if arr.shape != (3,) or norm < 1e-12 or (not np.all(np.isfinite(arr))):
        raise ValueError(f'{name} must be a finite non-zero 3-vector.')
    return arr / norm

def _axis_alignment_error(current_axis: np.ndarray, target_axis: np.ndarray) -> tuple[np.ndarray, float]:
    current = _normalise_vec(current_axis, name='current_axis')
    target = _normalise_vec(target_axis, name='target_axis')
    cross = np.cross(current, target)
    cross_norm = float(np.linalg.norm(cross))
    dot = float(np.clip(np.dot(current, target), -1.0, 1.0))
    angle = float(np.arctan2(cross_norm, dot))
    if angle <= 1e-12:
        return (np.zeros(3, dtype=float), 0.0)
    if cross_norm <= 1e-12:
        basis = min(np.eye(3), key=lambda vec: abs(float(np.dot(vec, current))))
        cross = np.cross(current, basis)
        cross_norm = float(np.linalg.norm(cross))
    return (cross / max(cross_norm, 1e-12) * angle, angle)

def _clip_to_joint_limits(model: mujoco.MjModel, qpos: np.ndarray) -> np.ndarray:
    q = qpos.copy()
    for i in range(model.njnt):
        if model.jnt_limited[i]:
            (lo, hi) = model.jnt_range[i]
            addr = model.jnt_qposadr[i]
            q[addr] = float(np.clip(q[addr], lo, hi))
    return q

def get_tcp_pose(model: mujoco.MjModel, data: mujoco.MjData, site_name: str='attachment_site') -> tuple[np.ndarray, np.ndarray]:
    site_id = _get_site_id(model, site_name)
    mujoco.mj_fwdPosition(model, data)
    pos = data.site_xpos[site_id].copy()
    quat = np.zeros(4)
    mujoco.mju_mat2Quat(quat, data.site_xmat[site_id])
    return (pos, quat)

def solve_ik(model: mujoco.MjModel, data: mujoco.MjData, target_pos: np.ndarray, target_quat: np.ndarray | None, site_name: str='attachment_site', max_iter: int=200, pos_tol: float=0.001, rot_tol: float=0.01, step_size: float=0.5, damping: float=0.0001, local_axis: np.ndarray | None=None, target_axis: np.ndarray | None=None) -> IKResult:
    site_id = _get_site_id(model, site_name)
    target_pos = np.asarray(target_pos, dtype=float)
    if target_quat is not None:
        target_quat = np.asarray(target_quat, dtype=float)
        norm = np.linalg.norm(target_quat)
        if norm < 1e-12:
            raise ValueError('target_quat has near-zero norm.')
        target_quat = target_quat / norm
    if (local_axis is None) != (target_axis is None):
        raise ValueError('local_axis and target_axis must be provided together.')
    axis_constraint = target_quat is None and local_axis is not None and (target_axis is not None)
    if axis_constraint:
        local_axis = _normalise_vec(local_axis, name='local_axis')
        target_axis = _normalise_vec(target_axis, name='target_axis')
    nv = model.nv
    nq = model.nq
    data.qpos[:] = _clip_to_joint_limits(model, data.qpos)
    jacp = np.zeros((3, nv))
    jacr = np.zeros((3, nv))
    err_pos = np.inf
    err_rot = 0.0
    iteration = 0
    for iteration in range(1, max_iter + 1):
        mujoco.mj_fwdPosition(model, data)
        current_pos = data.site_xpos[site_id]
        err_pos_vec = target_pos - current_pos
        err_pos = float(np.linalg.norm(err_pos_vec))
        if target_quat is not None:
            current_quat = np.zeros(4)
            mujoco.mju_mat2Quat(current_quat, data.site_xmat[site_id])
            err_rot_vec = _quat_error(target_quat, current_quat)
            err_rot = float(np.linalg.norm(err_rot_vec))
        elif axis_constraint:
            site_rot = np.asarray(data.site_xmat[site_id], dtype=float).reshape(3, 3)
            current_axis = site_rot @ local_axis
            (err_rot_vec, err_rot) = _axis_alignment_error(current_axis, target_axis)
        else:
            err_rot = 0.0
        pos_ok = err_pos < pos_tol
        rot_ok = target_quat is None and (not axis_constraint) or err_rot < rot_tol
        if pos_ok and rot_ok:
            break
        mujoco.mj_jacSite(model, data, jacp, jacr, site_id)
        if target_quat is not None or axis_constraint:
            err = np.concatenate([err_pos_vec, err_rot_vec])
            J = np.vstack([jacp, jacr])
        else:
            err = err_pos_vec
            J = jacp
        n_rows = J.shape[0]
        A = J @ J.T + damping * np.eye(n_rows)
        dq = J.T @ np.linalg.solve(A, err)
        mujoco.mj_integratePos(model, data.qpos, dq, step_size)
    mujoco.mj_fwdPosition(model, data)
    current_pos = data.site_xpos[site_id]
    err_pos = float(np.linalg.norm(target_pos - current_pos))
    if target_quat is not None:
        current_quat = np.zeros(4)
        mujoco.mju_mat2Quat(current_quat, data.site_xmat[site_id])
        err_rot = float(np.linalg.norm(_quat_error(target_quat, current_quat)))
    elif axis_constraint:
        site_rot = np.asarray(data.site_xmat[site_id], dtype=float).reshape(3, 3)
        current_axis = site_rot @ local_axis
        (_, err_rot) = _axis_alignment_error(current_axis, target_axis)
    else:
        err_rot = 0.0
    pos_ok = err_pos < pos_tol
    rot_ok = target_quat is None and (not axis_constraint) or err_rot < rot_tol
    success = bool(pos_ok and rot_ok)
    return IKResult(success=success, q=data.qpos[:nq].copy(), error_pos=err_pos, error_rot=err_rot, iterations=iteration)
