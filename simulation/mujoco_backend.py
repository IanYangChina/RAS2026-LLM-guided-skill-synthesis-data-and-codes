from __future__ import annotations
import logging
import math
import os
import uuid
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Concatenate, Optional, ParamSpec, TypeVar, cast
import numpy as np
try:
    import mujoco
except ImportError:
    mujoco = None
from dsl.nodes import EndEffectorAction
from primitives.termination import TimeLimit
from simulation.backend import ContactEvent, EpisodeTrace, SimulatorBackend, apply_binding_mode, finite_contact_force, sanitise_diagnostic_value, select_contact_events_for_storage, summarise_target_resolution_sources, summarise_contact_events
from simulation.scene import SceneConfig, build_scene
from simulation.realized_scene import DoorState, FixtureState, NamedScalar, NamedVector, RealizedSceneSnapshot, ScenePose
logger = logging.getLogger(__name__)
P = ParamSpec('P')
R = TypeVar('R')

def _finite_peak_contact_force(events: list[ContactEvent]) -> float | None:
    forces = [force for event in events if (force := finite_contact_force(event.force)) is not None]
    if forces:
        return max(forces)
    return 0.0 if not events else None

def _mj_id2name_or_none(model, obj_type: int, obj_id: int) -> str | None:
    if mujoco is None:
        return None
    try:
        name = mujoco.mj_id2name(model, obj_type, obj_id)
        return str(name) if name else None
    except Exception:
        return None

def _guard_result_template(guard_cfg: dict[str, Any]) -> dict[str, Any]:
    return {'id': guard_cfg.get('guard_id'), 'predicate': guard_cfg.get('predicate'), 'when': guard_cfg.get('when'), 'threshold': guard_cfg.get('threshold'), 'on_failure': guard_cfg.get('on_failure'), 'outcome': 'skipped', 'observed_value': None}

def _restore_cached_model_body_pos(method: Callable[Concatenate['MuJoCoBackend', P], R]) -> Callable[Concatenate['MuJoCoBackend', P], R]:

    @wraps(method)
    def wrapped(self: 'MuJoCoBackend', *args: P.args, **kwargs: P.kwargs) -> R:
        if not self.is_available():
            return method(self, *args, **kwargs)
        model = self._get_model()
        body_pos_before = model.body_pos.copy()
        try:
            return method(self, *args, **kwargs)
        finally:
            model.body_pos[:] = body_pos_before
    return cast(Callable[Concatenate['MuJoCoBackend', P], R], wrapped)

class MuJoCoBackend(SimulatorBackend):
    _model_cache: dict = {}
    MAX_STEPS_PER_PHASE: int = 1000
    CONTACT_DETECTED_ONLINE_FORCE_MIN: float = 1.0
    CONTACT_DETECTED_ONLINE_FORCE_MAX: float = 100.0
    MAX_STORED_CONTACT_EVENTS: int = 32
    PRIORITY_FORCE_CONTACT_EVENTS: int = 8
    PRIORITY_OBSTACLE_CONTACT_EVENTS: int = 8

    def __init__(self, scene_config: Optional[SceneConfig]=None, site_name: str='attachment_site', render: bool=False, render_dir: str | Path='artifacts/renders', render_width: int=640, render_height: int=480, _model_override=None) -> None:
        self.scene_config: SceneConfig = scene_config if scene_config is not None else SceneConfig(robot='panda', gripper=None, object_xml=None)
        self.site_name = site_name
        self.render = render
        self.render_dir = Path(render_dir)
        self.render_width = render_width
        self.render_height = render_height
        self._model_override = _model_override
        self._ee_site_id: int | None = None
        self._rand_config: dict | None = None
        self._rand_rng: np.random.Generator | None = None
        self._realized_scene_snapshots: dict[str, RealizedSceneSnapshot] = {}

    @property
    def name(self) -> str:
        return 'mujoco'

    def is_available(self) -> bool:
        try:
            import mujoco
            return True
        except Exception:
            return False

    @_restore_cached_model_body_pos
    def run_episode(self, artifact, parameter_values: dict[str, float], scene_config: dict | None=None, task_spec=None, step_callback: Callable[[Any, Any], None] | None=None, phase_callback: Callable[[str, Any, Any], None] | None=None) -> EpisodeTrace:
        if not self.is_available():
            raise RuntimeError('MuJoCo is not installed. Install with: pip install mujoco>=3.0')
        import mujoco
        from simulation.executor import IKStatistics, execute_trajectory
        from simulation.ik import get_tcp_pose
        model = self._get_model()
        self._ee_site_id = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_SITE, self.site_name)
        if self._ee_site_id < 0:
            self._ee_site_id = None
        data = mujoco.MjData(model)
        if task_spec is not None and task_spec.object_initial_pose is not None:
            _peg_body = getattr(task_spec, 'peg_body_name', None)
            self._reset_object_pose(model, data, task_spec.object_initial_pose, preferred_body_name=_peg_body)
        if task_spec is not None and task_spec.arm_initial_tcp_position is not None:
            self._reset_arm_pose(model, data, task_spec.arm_initial_tcp_position)
        mujoco.mj_forward(model, data)
        _rand_cfg = getattr(self, '_rand_config', None)
        _rand_rng = getattr(self, '_rand_rng', None)
        if getattr(self, '_rand_scene_frozen', False):
            _frozen_body = getattr(self, '_rand_frozen_body_deltas', None) or {}
            _frozen_qpos = getattr(self, '_rand_frozen_qpos_delta', None)
            for (body_id, (dx, dy, dz)) in _frozen_body.items():
                model.body_pos[body_id, 0] += dx
                model.body_pos[body_id, 1] += dy
                model.body_pos[body_id, 2] += dz
            if _frozen_qpos is not None:
                data.qpos[:] += _frozen_qpos
            mujoco.mj_forward(model, data)
        elif _rand_cfg is not None and _rand_rng is not None:
            self.apply_randomisation(model, data, _rand_cfg, _rand_rng)
            mujoco.mj_forward(model, data)
        _initial_hinge_angle: float | None = None
        _hinge_joint_id = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_JOINT, 'door_hinge')
        if _hinge_joint_id >= 0:
            _hinge_qpos_addr = int(model.jnt_qposadr[_hinge_joint_id])
            _initial_hinge_angle = float(data.qpos[_hinge_qpos_addr])
        _realised_goal_pos = self._get_goal_body_pos(model, task_spec)
        try:
            _realised_object_initial_pos = self._get_object_position(model, data, task_spec)
        except Exception:
            _realised_object_initial_pos = None
        _realised_fixture_pos = self._get_named_body_pos(model, data, 'peg_socket')
        _realised_door_panel_pos = self._get_named_body_pos(model, data, 'door_panel')
        _realised_obstacle_pos = self._get_named_body_pos(model, data, 'obstacle_block')
        _realised_channel_pos = self._get_named_body_pos(model, data, 'peg_channel_body')
        _realised_left_wall_pos = self._get_named_body_pos(model, data, 'channel_left_wall')
        _realised_right_wall_pos = self._get_named_body_pos(model, data, 'channel_right_wall')
        _realised_socket_entry_pos = self._get_named_site_pos(model, data, 'socket_hole')
        _realised_goal_marker_pos = self._get_named_body_pos(model, data, 'goal_marker')
        run_id: str = uuid.uuid4().hex[:8]
        frame_idx: int = 0
        all_step_records: list = []
        ik_statistics = IKStatistics()
        all_contact_events: list[ContactEvent] = []
        all_contact_events_raw: list[ContactEvent] = []
        last_traj = None
        contact_label_sets = self._infer_contact_label_sets(model, task_spec)
        phase_telemetry: list[dict] = []
        episode_parameter_bindings: list[dict] = []
        episode_guard_outcomes: list[dict] = []
        episode_obstacle_peak_force: float = 0.0
        episode_obstacle_peak_time: float | None = None
        episode_obstacle_peak_phase: str | None = None
        episode_obstacle_peak_obstacle_body: str | None = None
        episode_obstacle_peak_obstacle_geom: str | None = None
        episode_obstacle_peak_counterbody: str | None = None
        episode_obstacle_peak_countergeom: str | None = None
        _grasp_achieved_flag: bool | None = None
        _episode_goal_pos: np.ndarray | None = None
        if _realised_goal_pos is not None:
            _episode_goal_pos = np.array(_realised_goal_pos[:3], dtype=float)
        elif task_spec is not None:
            _goal_raw = getattr(task_spec, 'goal_object_position', None)
            if _goal_raw is None:
                _goal_raw = getattr(task_spec, 'goal_tcp_position', None)
            if _goal_raw is not None:
                _episode_goal_pos = np.array(_goal_raw[:3], dtype=float)
        n_phases = len(artifact.phases)
        abort_episode = False
        for phase_idx in range(n_phases):
            phase_artifact = artifact.phases[phase_idx]
            phase_name: str = getattr(phase_artifact, 'phase_name', f'phase_{phase_idx}')
            _phase_name_key = phase_name.strip().lower() if phase_name else ''
            _phase_id = getattr(phase_artifact, 'phase_id', phase_name)
            _prefix = _phase_id + '.'
            _local = {k[len(_prefix):]: v for (k, v) in parameter_values.items() if k.startswith(_prefix)}
            phase_params = _local if _local else parameter_values
            if 'push_speed' in phase_params and _phase_name_key not in ('push', 'contact'):
                phase_params = dict(phase_params)
                phase_params.pop('push_speed', None)
            _term = getattr(phase_artifact, 'termination', None)
            if isinstance(_term, TimeLimit) and 'max_duration' in phase_params:
                _term.max_time = float(phase_params['max_duration'])
            state = self._build_phase_state(phase_idx, n_phases, phase_params, artifact, model, data, task_spec=task_spec)
            state['initial_hinge_angle'] = _initial_hinge_angle
            target_trace = state.get('resolved_target_metadata', {'resolved_position': np.asarray(state['end'], dtype=float).tolist(), 'resolved_orientation': None, 'resolved_axis_alignment': None, 'orientation_status': 'legacy', 'source': 'v1_compat', 'anchor': None, 'entity': None, 'base_offset': None, 'offset_along_axis': None})
            run_phase_params = dict(parameter_values)
            binding_records: list[dict] = []
            termination_restores: list[tuple[Any, str, float]] = []
            guard_runtime: list[dict] = []
            retry_runtime: dict[str, Any] | None = None
            if target_trace.get('source') != 'v1_compat':
                (prepared_target_trace, run_phase_params, binding_records, termination_restores, guard_runtime, retry_runtime) = self._prepare_v2_phase_execution(artifact=artifact, phase_idx=phase_idx, params=parameter_values, base_state=state, model=model, data=data, task_spec=task_spec)
                if prepared_target_trace is not None:
                    target_trace = prepared_target_trace
                    state['resolved_target_metadata'] = prepared_target_trace
                    state['end'] = np.asarray(prepared_target_trace['resolved_position'], dtype=float)
                    if prepared_target_trace.get('resolved_orientation') is not None:
                        state['target_orientation'] = np.asarray(prepared_target_trace['resolved_orientation'], dtype=float)
                    if prepared_target_trace.get('resolved_axis_alignment') is not None:
                        state['target_axis_alignment'] = prepared_target_trace['resolved_axis_alignment']
            tcp_start = np.array(state['start'], dtype=float)
            if task_spec is not None and getattr(task_spec, 'grasp_target_body', None) is not None:
                _phase_type_for_wps = getattr(phase_artifact, 'phase_type', '')
                if _phase_type_for_wps in ('approach', 'descend'):
                    state = {**state, 'min_steps_per_wp': 60}
            _obj_pos_start: 'np.ndarray | None' = None
            if task_spec is not None:
                try:
                    _obj_pos_start = self._get_object_position(model, data, task_spec)
                except Exception:
                    _obj_pos_start = None
            _phase_obj_z_max_acc: 'list[float | None]' = [None]
            phase_contact_start_idx: int = len(all_contact_events_raw)
            phase_obstacle_peak_force: float = 0.0
            phase_obstacle_peak_time: float | None = None
            phase_obstacle_peak_obstacle_body: str | None = None
            phase_obstacle_peak_obstacle_geom: str | None = None
            phase_obstacle_peak_counterbody: str | None = None
            phase_obstacle_peak_countergeom: str | None = None

            def _track_obstacle_peak_step(_m, _d) -> None:
                nonlocal episode_obstacle_peak_force
                for _contact_idx in range(_d.ncon):
                    all_contact_events_raw.append(self._build_contact_event(_m, _d, _contact_idx, phase_index=phase_idx, phase_name=phase_name, phase_type=getattr(phase_artifact, 'phase_type', None), task_spec=task_spec, episode_index=None, contact_label_sets=contact_label_sets))
                nonlocal episode_obstacle_peak_time
                nonlocal episode_obstacle_peak_phase
                nonlocal episode_obstacle_peak_obstacle_body
                nonlocal episode_obstacle_peak_obstacle_geom
                nonlocal episode_obstacle_peak_counterbody
                nonlocal episode_obstacle_peak_countergeom
                nonlocal phase_obstacle_peak_force
                nonlocal phase_obstacle_peak_time
                nonlocal phase_obstacle_peak_obstacle_body
                nonlocal phase_obstacle_peak_obstacle_geom
                nonlocal phase_obstacle_peak_counterbody
                nonlocal phase_obstacle_peak_countergeom
                _updated_peak = self._update_obstacle_peak_from_contacts(model=_m, data=_d, obstacle_body_name=getattr(task_spec, 'obstacle_body_name', None) if task_spec is not None else None, phase_name=phase_name, current_peak_force=phase_obstacle_peak_force, current_peak_time=phase_obstacle_peak_time, current_peak_phase=phase_name, current_peak_obstacle_body=phase_obstacle_peak_obstacle_body, current_peak_obstacle_geom=phase_obstacle_peak_obstacle_geom, current_peak_counterbody=phase_obstacle_peak_counterbody, current_peak_countergeom=phase_obstacle_peak_countergeom)
                (phase_obstacle_peak_force, phase_obstacle_peak_time, _phase_peak_phase, phase_obstacle_peak_obstacle_body, phase_obstacle_peak_obstacle_geom, phase_obstacle_peak_counterbody, phase_obstacle_peak_countergeom) = _updated_peak
                if phase_obstacle_peak_force > episode_obstacle_peak_force:
                    episode_obstacle_peak_force = phase_obstacle_peak_force
                    episode_obstacle_peak_time = phase_obstacle_peak_time
                    episode_obstacle_peak_phase = _phase_peak_phase
                    episode_obstacle_peak_obstacle_body = phase_obstacle_peak_obstacle_body
                    episode_obstacle_peak_obstacle_geom = phase_obstacle_peak_obstacle_geom
                    episode_obstacle_peak_counterbody = phase_obstacle_peak_counterbody
                    episode_obstacle_peak_countergeom = phase_obstacle_peak_countergeom
            if task_spec is not None:
                _z_outer_cb = step_callback

                def _z_tracking_step_cb(_m, _d, _acc=_phase_obj_z_max_acc, _self=self, _ts=task_spec, _outer=_z_outer_cb):
                    try:
                        _z = float(_self._get_object_position(_m, _d, _ts)[2])
                        if _acc[0] is None or _z > _acc[0]:
                            _acc[0] = _z
                    except Exception:
                        pass
                    _track_obstacle_peak_step(_m, _d)
                    if _outer is not None:
                        _outer(_m, _d)
                _active_step_cb = _z_tracking_step_cb
            else:
                _phase_outer_cb = step_callback

                def _phase_step_cb(_m, _d, _outer=_phase_outer_cb):
                    _track_obstacle_peak_step(_m, _d)
                    if _outer is not None:
                        _outer(_m, _d)
                _active_step_cb = _phase_step_cb
            before_phase_guard_results = [self._evaluate_phase_guard(guard_cfg, model=model, data=data, task_spec=task_spec, state=state) for guard_cfg in guard_runtime if guard_cfg.get('when') == 'before_phase']
            during_phase_guard_cfgs = [guard_cfg for guard_cfg in guard_runtime if guard_cfg.get('when') == 'during_phase']
            during_phase_guard_results = [_guard_result_template(guard_cfg) for guard_cfg in during_phase_guard_cfgs]
            guard_stop_state: dict[str, Any] = {'triggered': False, 'action': None}

            def _evaluate_during_phase_guards() -> None:
                nonlocal during_phase_guard_results
                if not during_phase_guard_cfgs or guard_stop_state['triggered']:
                    return
                try:
                    (tcp_current, _) = get_tcp_pose(model, data, site_name=self.site_name)
                except Exception:
                    tcp_current = None
                phase_contacts_now = all_contact_events_raw[phase_contact_start_idx:]
                for (idx, guard_cfg) in enumerate(during_phase_guard_cfgs):
                    result = self._evaluate_phase_guard(guard_cfg, model=model, data=data, task_spec=task_spec, state=state, tcp_end=tcp_current, phase_contacts=phase_contacts_now)
                    during_phase_guard_results[idx] = result
                    if result['outcome'] == 'fail':
                        guard_stop_state['triggered'] = True
                        guard_stop_state['action'] = result.get('on_failure')
                        break
            _base_step_cb = _active_step_cb

            def _guarded_step_cb(_m, _d, _outer=_base_step_cb):
                if _outer is not None:
                    _outer(_m, _d)
                _evaluate_during_phase_guards()
            _active_step_cb = _guarded_step_cb
            while retry_runtime is not None:
                failed_before_guard = self._first_failed_guard(before_phase_guard_results)
                if failed_before_guard is None or failed_before_guard.get('on_failure') != 'retry' or retry_runtime['attempts'] >= retry_runtime['max_attempts']:
                    break
                previous_retry_runtime = retry_runtime
                retry_runtime['attempts'] += 1
                retry_runtime['executed'] = True
                retry_runtime['last_failed_guards'] = [failed_before_guard['id']]
                (run_phase_params, retry_offset) = self._apply_retry_strategy(phase_id=_phase_id, retry_runtime=retry_runtime, run_phase_params=run_phase_params)
                retry_state = self._build_phase_state(phase_idx, n_phases, phase_params, artifact, model, data, task_spec=task_spec)
                retry_state['initial_hinge_angle'] = _initial_hinge_angle
                (prepared_target_trace, run_phase_params, retry_binding_records, retry_restores, guard_runtime, retry_runtime) = self._prepare_v2_phase_execution(artifact=artifact, phase_idx=phase_idx, params=run_phase_params, base_state=retry_state, model=model, data=data, task_spec=task_spec, retry_offset=retry_offset, retry_attempt=retry_runtime['attempts'], preserve_generator_speed=True)
                retry_runtime = self._carry_retry_runtime_state(previous_retry_runtime, retry_runtime)
                binding_records.extend(retry_binding_records)
                termination_restores.extend(retry_restores)
                if prepared_target_trace is not None:
                    target_trace = prepared_target_trace
                    retry_state['resolved_target_metadata'] = prepared_target_trace
                    retry_state['end'] = np.asarray(prepared_target_trace['resolved_position'], dtype=float)
                    if prepared_target_trace.get('resolved_orientation') is not None:
                        retry_state['target_orientation'] = np.asarray(prepared_target_trace['resolved_orientation'], dtype=float)
                    if prepared_target_trace.get('resolved_axis_alignment') is not None:
                        retry_state['target_axis_alignment'] = prepared_target_trace['resolved_axis_alignment']
                state = retry_state
                before_phase_guard_results = [self._evaluate_phase_guard(guard_cfg, model=model, data=data, task_spec=task_spec, state=state) for guard_cfg in guard_runtime if guard_cfg.get('when') == 'before_phase']
                during_phase_guard_cfgs = [guard_cfg for guard_cfg in guard_runtime if guard_cfg.get('when') == 'during_phase']
                during_phase_guard_results = [_guard_result_template(guard_cfg) for guard_cfg in during_phase_guard_cfgs]
                guard_stop_state = {'triggered': False, 'action': None}
            phase_guard_action = self._first_failed_guard(before_phase_guard_results)
            skip_motion_execution = phase_guard_action is not None and phase_guard_action.get('on_failure') in {'abort', 'continue'}
            phase_control_action = phase_guard_action.get('on_failure') if phase_guard_action is not None else None
            try:
                if skip_motion_execution:
                    (traj, cmd) = (None, None)
                else:
                    _phase_prefix = f'{_phase_id}.'
                    local_run_phase_params = {key[len(_phase_prefix):]: value for (key, value) in run_phase_params.items() if key.startswith(_phase_prefix)}
                    if not local_run_phase_params:
                        local_run_phase_params = dict(phase_params)
                    state['n_waypoints'] = max(int(state.get('n_waypoints', 20) or 20), self._estimate_phase_waypoint_count(state, local_run_phase_params))
                    (traj, cmd) = artifact.run_phase(phase_idx, run_phase_params, state)
            except Exception as exc:
                for (target_obj, attr_name, previous) in reversed(termination_restores):
                    setattr(target_obj, attr_name, previous)
                logger.warning('Phase %d/%d run_phase raised %s: %s — phase skipped.', phase_idx, n_phases, type(exc).__name__, exc)
                continue
            if traj is not None:
                if state.get('target_orientation') is not None:
                    traj.metadata['orientations'] = np.repeat(np.asarray(state['target_orientation'], dtype=float)[np.newaxis, :], traj.positions.shape[0], axis=0)
                if state.get('target_axis_alignment') is not None:
                    traj.metadata['axis_alignment'] = state['target_axis_alignment']
                last_traj = traj
                workspace_dist = float(np.linalg.norm(np.array(state['end']) - tcp_start))
                n_waypoints = max(1, traj.positions.shape[0])
                _min_spwp = int(state.get('min_steps_per_wp', 30))
                phase_budget = min(self.MAX_STEPS_PER_PHASE, max(200 + int(500 * workspace_dist), _min_spwp * n_waypoints))
                n_wps = traj.positions.shape[0] if traj.positions.shape[0] > 0 else 1
                steps_per_wp = max(1, _min_spwp, phase_budget // n_wps)
                n_steps_budget: int = phase_budget
                _phase_artifact_for_hook = phase_artifact
                _phase_target_for_hook = np.array(state['end'], dtype=float)
                _initial_ncon: int = int(data.ncon)
                _initial_finger_contact: bool = self._check_finger_contact(model, data)
                _online_fired: list[bool] = [False]

                def _termination_hook(_pa=_phase_artifact_for_hook, _pt=_phase_target_for_hook, _fired=_online_fired, _init_ncon=_initial_ncon, _init_finger_contact=_initial_finger_contact) -> bool:
                    if guard_stop_state['triggered']:
                        return True
                    if self._check_termination_online(model, data, _pa, task_spec, phase_target=_pt, initial_ncon=_init_ncon, initial_finger_contact=_init_finger_contact):
                        _fired[0] = True
                        return True
                    return False
                records = self._execute_trajectory_compat(execute_trajectory, model, data, traj, self.site_name, max_steps_per_waypoint=steps_per_wp, max_total_steps=phase_budget, step_callback=_active_step_cb, cmd=cmd, termination_hook=_termination_hook, pos_tol=float(getattr(phase_artifact.termination, 'tol', 0.005)), ik_statistics=ik_statistics)
                all_step_records.extend(records)
                n_steps: int = len(records)
                from dsl.nodes import TerminationCond as _TC
                _cond_val = getattr(getattr(_phase_artifact_for_hook, 'termination', None), 'cond', None)
                if guard_stop_state['triggered']:
                    termination_reason = 'guard_failure'
                elif _online_fired[0]:
                    if _cond_val == _TC.FORCE_EXCEEDED:
                        termination_reason: str = 'force_exceeded'
                    else:
                        termination_reason = 'condition_met'
                elif _cond_val == _TC.TIME_LIMIT:
                    termination_reason = 'time_limit'
                else:
                    termination_reason = 'step_budget'
            elif skip_motion_execution:
                n_steps = 0
                n_steps_budget = 0
                termination_reason = 'guard_failure'
            else:
                _gp_n_arm = sum((1 for _ai in range(model.nu) if model.actuator_trntype[_ai] != mujoco.mjtTrn.mjTRN_TENDON)) if model.nu > 0 else 0
                _gp_q_target = data.qpos[:_gp_n_arm].copy()
                _gp_arm_lo = model.actuator_ctrlrange[:_gp_n_arm, 0]
                _gp_arm_hi = model.actuator_ctrlrange[:_gp_n_arm, 1]
                _gp_arm_active = _gp_arm_hi > _gp_arm_lo
                for _ in range(50):
                    if _gp_n_arm > 0:
                        data.ctrl[:_gp_n_arm] = np.where(_gp_arm_active, np.clip(_gp_q_target, _gp_arm_lo, _gp_arm_hi), data.ctrl[:_gp_n_arm])
                    mujoco.mj_step(model, data)
                    if _active_step_cb is not None:
                        _active_step_cb(model, data)
                    if guard_stop_state['triggered']:
                        break
                n_steps = 50 if not guard_stop_state['triggered'] else 0
                n_steps_budget = 50
                termination_reason = 'guard_failure' if guard_stop_state['triggered'] else 'step_budget'
            for (target_obj, attr_name, previous) in reversed(termination_restores):
                setattr(target_obj, attr_name, previous)
            _phase_artifact = phase_artifact
            _ee_action = getattr(_phase_artifact, 'end_effector_action', None)
            if _ee_action is not None and phase_control_action not in {'abort', 'continue', 'retry'}:
                if _ee_action in (EndEffectorAction.CLOSE, EndEffectorAction.FORCE_GRASP):
                    _n_arm = sum((1 for _ai in range(model.nu) if model.actuator_trntype[_ai] != mujoco.mjtTrn.mjTRN_TENDON)) if model.nu > 0 else 0
                    _settle_q_target = data.qpos[:_n_arm].copy()
                    _settle_arm_lo = model.actuator_ctrlrange[:_n_arm, 0]
                    _settle_arm_hi = model.actuator_ctrlrange[:_n_arm, 1]
                    _settle_arm_active = _settle_arm_hi > _settle_arm_lo
                    _grip_acts: 'list[tuple[int, float, float]]' = [(_ai, float(data.ctrl[_ai]), float(model.actuator_ctrlrange[_ai, 0])) for _ai in range(model.nu) if model.actuator_trntype[_ai] == mujoco.mjtTrn.mjTRN_TENDON]
                    _N_SETTLE = 200
                    _N_POST_SETTLE = 200
                    if _ee_action == EndEffectorAction.CLOSE:
                        for _si in range(_N_SETTLE):
                            if _n_arm > 0:
                                data.ctrl[:_n_arm] = np.where(_settle_arm_active, np.clip(_settle_q_target, _settle_arm_lo, _settle_arm_hi), data.ctrl[:_n_arm])
                            _t = _si / float(_N_SETTLE - 1)
                            for (_gai, _g_open, _g_lo) in _grip_acts:
                                data.ctrl[_gai] = float(_g_open * (1.0 - _t) + _g_lo * _t)
                            mujoco.mj_step(model, data)
                            if _active_step_cb is not None:
                                _active_step_cb(model, data)
                        for (_gai, _g_open, _g_lo) in _grip_acts:
                            data.ctrl[_gai] = _g_lo
                        for _psi in range(_N_POST_SETTLE):
                            if _n_arm > 0:
                                data.ctrl[:_n_arm] = np.where(_settle_arm_active, np.clip(_settle_q_target, _settle_arm_lo, _settle_arm_hi), data.ctrl[:_n_arm])
                            for (_gai, _g_open, _g_lo) in _grip_acts:
                                data.ctrl[_gai] = _g_lo
                            mujoco.mj_step(model, data)
                            if _active_step_cb is not None:
                                _active_step_cb(model, data)
                    else:
                        _frozen_ctrl: 'dict[int, float]' = {}
                        for _si in range(_N_SETTLE):
                            if _n_arm > 0:
                                data.ctrl[:_n_arm] = np.where(_settle_arm_active, np.clip(_settle_q_target, _settle_arm_lo, _settle_arm_hi), data.ctrl[:_n_arm])
                            _t = _si / float(_N_SETTLE - 1)
                            for (_gai, _g_open, _g_lo) in _grip_acts:
                                data.ctrl[_gai] = float(_g_open * (1.0 - _t) + _g_lo * _t)
                            mujoco.mj_step(model, data)
                            if _active_step_cb is not None:
                                _active_step_cb(model, data)
                            if not _frozen_ctrl and self._check_bilateral_contact(model, data, force_threshold=3.0):
                                _frozen_ctrl = {_gai: float(data.ctrl[_gai]) for (_gai, _, _) in _grip_acts}
                                break
                        for (_gai, _g_open, _g_lo) in _grip_acts:
                            data.ctrl[_gai] = _frozen_ctrl[_gai] if _frozen_ctrl else _g_lo
                        for _psi in range(_N_POST_SETTLE):
                            if _n_arm > 0:
                                data.ctrl[:_n_arm] = np.where(_settle_arm_active, np.clip(_settle_q_target, _settle_arm_lo, _settle_arm_hi), data.ctrl[:_n_arm])
                            for (_gai, _g_open, _g_lo) in _grip_acts:
                                data.ctrl[_gai] = _frozen_ctrl[_gai] if _frozen_ctrl else _g_lo
                            mujoco.mj_step(model, data)
                            if _active_step_cb is not None:
                                _active_step_cb(model, data)
                    mujoco.mj_forward(model, data)
                    if not _grasp_achieved_flag:
                        _grasp_achieved_flag = self._check_finger_contact(model, data)
                elif _ee_action == EndEffectorAction.OPEN:
                    self.open_gripper(model, data)
                    _OPEN_SETTLE_STEPS = 150
                    _phase_is_release = getattr(phase_artifact, 'phase_type', '') == 'release'
                    _open_settle_mode: str = getattr(task_spec, 'open_settle_mode', 'static_hold') if task_spec is not None and _phase_is_release else 'static_hold'
                    _retreat_settle_done = False
                    if _open_settle_mode == 'retreat_up':
                        try:
                            from simulation.ik import get_tcp_pose as _os_get_tcp, solve_ik as _os_solve_ik
                            _n_arm_os: int = sum((1 for _ai in range(model.nu) if model.actuator_trntype[_ai] != mujoco.mjtTrn.mjTRN_TENDON)) if model.nu > 0 else 0
                            _os_arm_lo = model.actuator_ctrlrange[:_n_arm_os, 0]
                            _os_arm_hi = model.actuator_ctrlrange[:_n_arm_os, 1]
                            _os_arm_active = _os_arm_hi > _os_arm_lo
                            (_os_tcp_cur, _) = _os_get_tcp(model, data, site_name=self.site_name)
                            _os_retract_z = float(getattr(task_spec, 'open_settle_retract_z', 0.05))
                            _os_tcp_tgt = _os_tcp_cur + np.array([0.0, 0.0, _os_retract_z])
                            _os_q_backup = data.qpos.copy()
                            _os_ik_res = _os_solve_ik(model, data, _os_tcp_tgt, target_quat=None)
                            if _os_ik_res.success:
                                _os_q_end = data.qpos[:_n_arm_os].copy()
                            else:
                                _os_q_end = None
                            data.qpos[:] = _os_q_backup
                            mujoco.mj_forward(model, data)
                            if _os_q_end is not None:
                                _os_q_start = _os_q_backup[:_n_arm_os].copy()
                                for _osi in range(_OPEN_SETTLE_STEPS):
                                    _os_alpha = _osi / float(_OPEN_SETTLE_STEPS - 1)
                                    _os_q_interp = (1.0 - _os_alpha) * _os_q_start + _os_alpha * _os_q_end
                                    if _n_arm_os > 0:
                                        data.ctrl[:_n_arm_os] = np.where(_os_arm_active, np.clip(_os_q_interp, _os_arm_lo, _os_arm_hi), data.ctrl[:_n_arm_os])
                                    mujoco.mj_step(model, data)
                                    if _active_step_cb is not None:
                                        _active_step_cb(model, data)
                                _retreat_settle_done = True
                        except (ImportError, ValueError, RuntimeError, AttributeError):
                            pass
                    if not _retreat_settle_done:
                        _sh_n_arm: int = sum((1 for _ai in range(model.nu) if model.actuator_trntype[_ai] != mujoco.mjtTrn.mjTRN_TENDON)) if model.nu > 0 else 0
                        if _sh_n_arm > 0:
                            _sh_arm_lo = model.actuator_ctrlrange[:_sh_n_arm, 0]
                            _sh_arm_hi = model.actuator_ctrlrange[:_sh_n_arm, 1]
                            _sh_arm_active = _sh_arm_hi > _sh_arm_lo
                            _sh_q_hold = data.qpos[:_sh_n_arm].copy()
                        for _ in range(_OPEN_SETTLE_STEPS):
                            if _sh_n_arm > 0:
                                data.ctrl[:_sh_n_arm] = np.where(_sh_arm_active, np.clip(_sh_q_hold, _sh_arm_lo, _sh_arm_hi), data.ctrl[:_sh_n_arm])
                            mujoco.mj_step(model, data)
                            if _active_step_cb is not None:
                                _active_step_cb(model, data)
            try:
                (tcp_end, _) = get_tcp_pose(model, data, site_name=self.site_name)
            except Exception:
                tcp_end = np.zeros(3)
            _obj_pos_end: 'np.ndarray | None' = None
            if task_spec is not None:
                try:
                    _obj_pos_end = self._get_object_position(model, data, task_spec)
                except Exception:
                    _obj_pos_end = None
            phase_end_contacts = self._collect_contacts(model, data, phase_index=phase_idx, phase_name=phase_name, phase_type=getattr(phase_artifact, 'phase_type', None), task_spec=task_spec, contact_label_sets=contact_label_sets)
            all_contact_events.extend(phase_end_contacts)
            raw_phase_contacts = all_contact_events_raw[phase_contact_start_idx:]
            phase_contacts = phase_end_contacts
            phase_peak_force = _finite_peak_contact_force(phase_contacts)
            raw_phase_peak_force = _finite_peak_contact_force(raw_phase_contacts)
            if traj is not None:
                if guard_stop_state['triggered']:
                    terminated_normally = False
                elif _online_fired[0]:
                    terminated_normally: bool = True
                else:
                    terminated_normally = self._check_termination_condition(phase_artifact, model, data, tcp_start, tcp_end, state, phase_contacts, phase_peak_force if phase_peak_force is not None else 0.0, task_spec=task_spec)
            else:
                terminated_normally = not skip_motion_execution and (not guard_stop_state['triggered'])
            for (idx, guard_cfg) in enumerate(during_phase_guard_cfgs):
                if during_phase_guard_results[idx].get('outcome') != 'skipped':
                    continue
                during_phase_guard_results[idx] = self._evaluate_phase_guard(guard_cfg, model=model, data=data, task_spec=task_spec, state=state, tcp_end=tcp_end, phase_contacts=raw_phase_contacts if raw_phase_contacts else phase_contacts)
            after_phase_guard_results = []
            if phase_control_action not in {'abort', 'continue', 'retry'}:
                after_phase_guard_results = [self._evaluate_phase_guard(guard_cfg, model=model, data=data, task_spec=task_spec, state=state, tcp_end=tcp_end, phase_contacts=phase_contacts) for guard_cfg in guard_runtime if guard_cfg.get('when') == 'after_phase']
            guard_results = before_phase_guard_results + during_phase_guard_results + after_phase_guard_results
            phase_guard_action = self._first_failed_guard(guard_results)
            if phase_guard_action is not None:
                phase_control_action = phase_guard_action.get('on_failure')
            if retry_runtime is not None:
                retry_runtime['outcomes'] = [{'guard_id': row['id'], 'when': row['when'], 'outcome': row['outcome'], 'would_retry': row['outcome'] == 'fail' and row.get('on_failure') == 'retry' and (retry_runtime['attempts'] < retry_runtime['max_attempts'])} for row in guard_results]
                while retry_runtime['attempts'] < retry_runtime['max_attempts'] and any((row['outcome'] == 'fail' and row.get('on_failure') == 'retry' for row in guard_results)):
                    retry_runtime['attempts'] += 1
                    retry_runtime['executed'] = True
                    retry_runtime['last_failed_guards'] = [row['id'] for row in guard_results if row['outcome'] == 'fail' and row.get('on_failure') == 'retry']
                    (run_phase_params, retry_offset) = self._apply_retry_strategy(phase_id=_phase_id, retry_runtime=retry_runtime, run_phase_params=run_phase_params)
                    retry_state = self._build_phase_state(phase_idx, n_phases, phase_params, artifact, model, data, task_spec=task_spec)
                    retry_state['initial_hinge_angle'] = _initial_hinge_angle
                    (prepared_target_trace, run_phase_params, retry_binding_records, retry_restores, _retry_guard_runtime, _) = self._prepare_v2_phase_execution(artifact=artifact, phase_idx=phase_idx, params=run_phase_params, base_state=retry_state, model=model, data=data, task_spec=task_spec, retry_offset=retry_offset, retry_attempt=retry_runtime['attempts'], preserve_generator_speed=True)
                    guard_runtime = _retry_guard_runtime
                    before_phase_guard_results = [self._evaluate_phase_guard(guard_cfg, model=model, data=data, task_spec=task_spec, state=retry_state) for guard_cfg in guard_runtime if guard_cfg.get('when') == 'before_phase']
                    during_phase_guard_cfgs = [guard_cfg for guard_cfg in guard_runtime if guard_cfg.get('when') == 'during_phase']
                    during_phase_guard_results = [_guard_result_template(guard_cfg) for guard_cfg in during_phase_guard_cfgs]
                    guard_stop_state = {'triggered': False, 'action': None}
                    phase_guard_action = self._first_failed_guard(before_phase_guard_results)
                    if phase_guard_action is not None and phase_guard_action.get('on_failure') == 'retry':
                        guard_results = before_phase_guard_results + during_phase_guard_results
                        retry_runtime['outcomes'] = [{'guard_id': row['id'], 'when': row['when'], 'outcome': row['outcome'], 'would_retry': retry_runtime['attempts'] < retry_runtime['max_attempts']} for row in guard_results]
                        continue
                    if prepared_target_trace is not None:
                        target_trace = prepared_target_trace
                        retry_state['resolved_target_metadata'] = prepared_target_trace
                        retry_state['end'] = np.asarray(prepared_target_trace['resolved_position'], dtype=float)
                        if prepared_target_trace.get('resolved_orientation') is not None:
                            retry_state['target_orientation'] = np.asarray(prepared_target_trace['resolved_orientation'], dtype=float)
                        if prepared_target_trace.get('resolved_axis_alignment') is not None:
                            retry_state['target_axis_alignment'] = prepared_target_trace['resolved_axis_alignment']
                    tcp_start = np.array(retry_state['start'], dtype=float)
                    try:
                        (retry_traj, retry_cmd) = artifact.run_phase(phase_idx, run_phase_params, retry_state)
                    finally:
                        for (target_obj, attr_name, previous) in reversed(retry_restores):
                            setattr(target_obj, attr_name, previous)
                    if retry_traj is not None:
                        if retry_state.get('target_orientation') is not None:
                            retry_traj.metadata['orientations'] = np.repeat(np.asarray(retry_state['target_orientation'], dtype=float)[np.newaxis, :], retry_traj.positions.shape[0], axis=0)
                        if retry_state.get('target_axis_alignment') is not None:
                            retry_traj.metadata['axis_alignment'] = retry_state['target_axis_alignment']
                        _retry_target_for_hook = np.array(retry_state['end'], dtype=float)
                        _retry_initial_ncon = int(data.ncon)
                        _retry_initial_finger_contact = self._check_finger_contact(model, data)
                        _online_fired = [False]

                        def _termination_hook(_pa=phase_artifact, _pt=_retry_target_for_hook, _fired=_online_fired, _init_ncon=_retry_initial_ncon, _init_finger_contact=_retry_initial_finger_contact) -> bool:
                            if guard_stop_state['triggered']:
                                return True
                            if self._check_termination_online(model, data, _pa, task_spec, phase_target=_pt, initial_ncon=_init_ncon, initial_finger_contact=_init_finger_contact):
                                _fired[0] = True
                                return True
                            return False
                        retry_records = self._execute_trajectory_compat(execute_trajectory, model, data, retry_traj, self.site_name, max_steps_per_waypoint=max(1, int(retry_state.get('min_steps_per_wp', 30)), n_steps_budget // max(1, retry_traj.positions.shape[0])), max_total_steps=n_steps_budget, step_callback=_active_step_cb, cmd=retry_cmd, termination_hook=_termination_hook, pos_tol=float(getattr(phase_artifact.termination, 'tol', 0.005)), ik_statistics=ik_statistics)
                        all_step_records.extend(retry_records)
                        n_steps += len(retry_records)
                    else:
                        retry_ee_action = getattr(phase_artifact, 'end_effector_action', None)
                        if retry_ee_action in (EndEffectorAction.CLOSE, EndEffectorAction.FORCE_GRASP):
                            self.close_gripper(model, data)
                        elif retry_ee_action == EndEffectorAction.OPEN:
                            self.open_gripper(model, data)
                        for _ in range(50):
                            mujoco.mj_step(model, data)
                            if _active_step_cb is not None:
                                _active_step_cb(model, data)
                        n_steps += 50
                    target_trace = retry_state.get('resolved_target_metadata', target_trace)
                    state = retry_state
                    try:
                        (tcp_end, _) = get_tcp_pose(model, data, site_name=self.site_name)
                    except Exception:
                        tcp_end = np.zeros(3)
                    phase_end_contacts = self._collect_contacts(model, data, phase_index=phase_idx, phase_name=phase_name, phase_type=getattr(phase_artifact, 'phase_type', None), task_spec=task_spec, contact_label_sets=contact_label_sets)
                    all_contact_events.extend(phase_end_contacts)
                    phase_contacts = phase_end_contacts
                    raw_phase_contacts = all_contact_events_raw[phase_contact_start_idx:]
                    phase_peak_force = _finite_peak_contact_force(phase_contacts)
                    raw_phase_peak_force = _finite_peak_contact_force(raw_phase_contacts)
                    binding_records.extend(retry_binding_records)
                    for (idx, guard_cfg) in enumerate(during_phase_guard_cfgs):
                        if during_phase_guard_results[idx].get('outcome') != 'skipped':
                            continue
                        during_phase_guard_results[idx] = self._evaluate_phase_guard(guard_cfg, model=model, data=data, task_spec=task_spec, state=state, tcp_end=tcp_end, phase_contacts=raw_phase_contacts if raw_phase_contacts else phase_contacts)
                    after_phase_guard_results = []
                    if not guard_stop_state['triggered']:
                        after_phase_guard_results = [self._evaluate_phase_guard(guard_cfg, model=model, data=data, task_spec=task_spec, state=state, tcp_end=tcp_end, phase_contacts=phase_contacts) for guard_cfg in guard_runtime if guard_cfg.get('when') == 'after_phase']
                    guard_results = before_phase_guard_results + during_phase_guard_results + after_phase_guard_results
                    retry_runtime['outcomes'] = [{'guard_id': row['id'], 'when': row['when'], 'outcome': row['outcome'], 'would_retry': row['outcome'] == 'fail' and row.get('on_failure') == 'retry' and (retry_runtime['attempts'] < retry_runtime['max_attempts'])} for row in guard_results]
            episode_parameter_bindings.extend(binding_records)
            episode_guard_outcomes.extend(guard_results)
            phase_telemetry.append({'phase_name': phase_name, 'phase_type': getattr(phase_artifact, 'phase_type', None), 'tcp_start': tcp_start.tolist(), 'tcp_end': tcp_end.tolist(), 'terminated_normally': terminated_normally, 'termination_reason': termination_reason, 'n_steps': n_steps, 'n_steps_budget': n_steps_budget, 'object_pos_start': _obj_pos_start.tolist() if _obj_pos_start is not None else None, 'object_pos_end': _obj_pos_end.tolist() if _obj_pos_end is not None else None, 'tcp_to_object_dist_end': float(np.linalg.norm(tcp_end - _obj_pos_end)) if _obj_pos_end is not None else None, 'object_to_goal_dist_start': float(np.linalg.norm(_obj_pos_start - _episode_goal_pos)) if _obj_pos_start is not None and _episode_goal_pos is not None else None, 'object_to_goal_dist_end': float(np.linalg.norm(_obj_pos_end - _episode_goal_pos)) if _obj_pos_end is not None and _episode_goal_pos is not None else None, 'contact_detected': len(phase_contacts) > 0, 'contact_event_count': len(phase_contacts), 'peak_contact_force': phase_peak_force, 'raw_contact_detected': len(raw_phase_contacts) > 0, 'raw_contact_event_count': len(raw_phase_contacts), 'raw_peak_contact_force': raw_phase_peak_force, 'phase_peak_obstacle_force': phase_obstacle_peak_force, 'phase_peak_obstacle_time': phase_obstacle_peak_time, 'phase_peak_obstacle_body': phase_obstacle_peak_obstacle_body, 'phase_peak_obstacle_geom': phase_obstacle_peak_obstacle_geom, 'phase_peak_obstacle_counterbody': phase_obstacle_peak_counterbody, 'phase_peak_obstacle_countergeom': phase_obstacle_peak_countergeom, 'object_z_max': _phase_obj_z_max_acc[0], 'subtask_id': getattr(phase_artifact, 'subtask_id', None), 'target': target_trace, 'parameter_bindings': binding_records, 'guards': guard_results, 'retries': retry_runtime})
            if self.render:
                try:
                    self._render_frame(model, data, run_id, frame_idx)
                    frame_idx += 1
                except Exception as exc:
                    logger.warning('Render frame %d failed: %s', frame_idx, exc)
            if phase_callback is not None:
                try:
                    phase_callback(phase_name, model, data)
                except Exception as exc:
                    logger.warning('phase_callback for %s raised %s: %s', phase_name, type(exc).__name__, exc)
            if phase_control_action == 'abort':
                abort_episode = True
            if abort_episode:
                break
        if all_step_records:
            tcp_positions = [r.tcp_pos for r in all_step_records]
            trajectory_positions: np.ndarray = np.stack(tcp_positions)
            joint_positions: list = [r.qpos for r in all_step_records]
            final_tcp = all_step_records[-1].tcp_pos
            if last_traj is not None and last_traj.positions.shape[0] > 0:
                last_target = np.asarray(last_traj.positions[-1], dtype=float)
                if last_target.shape[0] == 3:
                    final_pose_error = float(np.linalg.norm(final_tcp - last_target))
                else:
                    final_pose_error = float(np.linalg.norm(data.qpos[:model.nq] - last_target[:model.nq]))
            else:
                final_pose_error = 0.0
            success = bool(len(all_contact_events) > 0 and final_pose_error < 0.1)
        else:
            trajectory_positions = np.zeros((0, 3))
            joint_positions = []
            final_pose_error = 0.0
            final_tcp = np.zeros(3)
            success = False
        phase_end_peak_force = _finite_peak_contact_force(all_contact_events)
        raw_peak_force = _finite_peak_contact_force(all_contact_events_raw)
        peak_force = max((value for value in (phase_end_peak_force, raw_peak_force) if value is not None)) if phase_end_peak_force is not None or raw_peak_force is not None else 0.0
        stored_contact_events = select_contact_events_for_storage(all_contact_events_raw, max_events=self.MAX_STORED_CONTACT_EVENTS, top_force_events=self.PRIORITY_FORCE_CONTACT_EVENTS, top_obstacle_events=self.PRIORITY_OBSTACLE_CONTACT_EVENTS)
        _hinge_id = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_JOINT, 'door_hinge')
        _hinge_qpos_addr = int(model.jnt_qposadr[_hinge_id]) if _hinge_id >= 0 else -1
        _hinge_angle = float(data.qpos[_hinge_qpos_addr]) if _hinge_qpos_addr >= 0 else None
        metadata: dict = {'backend': self.name, 'run_id': run_id, 'joint_positions': joint_positions, 'tcp_positions': [r.tcp_pos for r in all_step_records], 'render': self.render, 'final_tcp_position': final_tcp.tolist(), 'phase_telemetry': phase_telemetry, 'peak_obstacle_force': episode_obstacle_peak_force, 'peak_obstacle_time': episode_obstacle_peak_time, 'peak_obstacle_phase': episode_obstacle_peak_phase, 'peak_obstacle_body': episode_obstacle_peak_obstacle_body, 'peak_obstacle_geom': episode_obstacle_peak_obstacle_geom, 'peak_obstacle_obstacle_body': episode_obstacle_peak_obstacle_body, 'peak_obstacle_obstacle_geom': episode_obstacle_peak_obstacle_geom, 'peak_obstacle_counterbody': episode_obstacle_peak_counterbody, 'peak_obstacle_countergeom': episode_obstacle_peak_countergeom, 'hinge_angle': _hinge_angle, 'contact_events': [event.to_dict() for event in stored_contact_events], 'contact_event_summary': summarise_contact_events(all_contact_events_raw), 'phase_end_peak_contact_force': phase_end_peak_force, 'raw_peak_contact_force': raw_peak_force, 'contact_event_retention': {'total_events': len(all_contact_events_raw), 'stored_events': len(stored_contact_events), 'max_events': self.MAX_STORED_CONTACT_EVENTS, 'priority_force_events': self.PRIORITY_FORCE_CONTACT_EVENTS, 'priority_obstacle_events': self.PRIORITY_OBSTACLE_CONTACT_EVENTS}, 'parameter_consumption': episode_parameter_bindings, 'guard_outcomes': episode_guard_outcomes, 'target_resolution_summary': summarise_target_resolution_sources(phase_telemetry), 'ik_statistics': ik_statistics.to_dict()}
        if _realised_goal_pos is not None:
            metadata['actual_goal_position'] = _realised_goal_pos.tolist()
            metadata['realised_goal_position'] = _realised_goal_pos.tolist()
        if _realised_object_initial_pos is not None:
            metadata['realised_object_initial_position'] = _realised_object_initial_pos.tolist()
        if _realised_fixture_pos is not None:
            metadata['realised_fixture_position'] = _realised_fixture_pos.tolist()
        if _realised_door_panel_pos is not None:
            metadata['realised_door_panel_position'] = _realised_door_panel_pos.tolist()
        if _realised_obstacle_pos is not None:
            metadata['actual_obstacle_position'] = _realised_obstacle_pos.tolist()
            metadata['realised_obstacle_position'] = _realised_obstacle_pos.tolist()
        if _realised_socket_entry_pos is not None:
            metadata['socket_entry_position'] = _realised_socket_entry_pos.tolist()
        if _realised_goal_marker_pos is not None:
            metadata['goal_marker_position'] = _realised_goal_marker_pos.tolist()
        if _initial_hinge_angle is not None:
            metadata['initial_hinge_angle'] = _initial_hinge_angle
            metadata['realised_initial_hinge_angle'] = _initial_hinge_angle
        realised_task_state: dict[str, Any] = {}
        if _realised_goal_pos is not None:
            realised_task_state['goal_position'] = _realised_goal_pos.tolist()
        if _realised_object_initial_pos is not None:
            realised_task_state['object_initial_position'] = _realised_object_initial_pos.tolist()
        if _realised_fixture_pos is not None:
            realised_task_state['fixture_position'] = _realised_fixture_pos.tolist()
        if _realised_door_panel_pos is not None:
            realised_task_state['door_panel_position'] = _realised_door_panel_pos.tolist()
        if _realised_obstacle_pos is not None:
            realised_task_state['obstacle_position'] = _realised_obstacle_pos.tolist()
        if _realised_socket_entry_pos is not None:
            realised_task_state['socket_entry_position'] = _realised_socket_entry_pos.tolist()
        if _realised_goal_marker_pos is not None:
            realised_task_state['goal_marker_position'] = _realised_goal_marker_pos.tolist()
        if _realised_channel_pos is not None:
            realised_task_state['channel_position'] = _realised_channel_pos.tolist()
        if _realised_left_wall_pos is not None:
            realised_task_state['channel_left_wall_position'] = _realised_left_wall_pos.tolist()
        if _realised_right_wall_pos is not None:
            realised_task_state['channel_right_wall_position'] = _realised_right_wall_pos.tolist()
        if _initial_hinge_angle is not None:
            realised_task_state['hinge_angle_initial'] = _initial_hinge_angle
        if realised_task_state:
            metadata['realised_task_state'] = realised_task_state
        if _grasp_achieved_flag is not None:
            metadata['grasp_achieved'] = _grasp_achieved_flag
        _peg_body_name = getattr(task_spec, 'peg_body_name', None) if task_spec is not None else None
        _obj_body_candidates = ([_peg_body_name] if _peg_body_name else []) + ['push_box', 'grasp_target', 'peg_socket']
        for _obj_body in _obj_body_candidates:
            body_id = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_BODY, _obj_body)
            if body_id >= 0:
                metadata['final_object_position'] = data.xpos[body_id].copy().tolist()
                break
        metadata = sanitise_diagnostic_value(metadata)
        episode_trace = EpisodeTrace(skill_name=artifact.skill_name, parameter_values=parameter_values, success=success, duration=float(data.time), final_pose_error=final_pose_error, peak_contact_force=peak_force, trajectory_positions=trajectory_positions, contact_history=all_contact_events, metadata=metadata)
        return episode_trace

    @staticmethod
    def _update_obstacle_peak_from_contacts(model, data, obstacle_body_name: str | None, phase_name: str | None, current_peak_force: float, current_peak_time: float | None, current_peak_phase: str | None, current_peak_obstacle_body: str | None, current_peak_obstacle_geom: str | None, current_peak_counterbody: str | None, current_peak_countergeom: str | None) -> tuple[float, float | None, str | None, str | None, str | None, str | None, str | None]:
        if mujoco is None or obstacle_body_name is None:
            return (current_peak_force, current_peak_time, current_peak_phase, current_peak_obstacle_body, current_peak_obstacle_geom, current_peak_counterbody, current_peak_countergeom)
        obstacle_id = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_BODY, obstacle_body_name)
        if obstacle_id < 0:
            return (current_peak_force, current_peak_time, current_peak_phase, current_peak_obstacle_body, current_peak_obstacle_geom, current_peak_counterbody, current_peak_countergeom)
        peak_force = current_peak_force
        peak_time = current_peak_time
        peak_phase = current_peak_phase
        peak_obstacle_body = current_peak_obstacle_body
        peak_obstacle_geom = current_peak_obstacle_geom
        peak_counterbody = current_peak_counterbody
        peak_countergeom = current_peak_countergeom
        for c_idx in range(data.ncon):
            contact = data.contact[c_idx]
            b1 = model.geom_bodyid[contact.geom1]
            b2 = model.geom_bodyid[contact.geom2]
            if obstacle_id not in (b1, b2):
                continue
            force_buf = np.zeros(6)
            mujoco.mj_contactForce(model, data, c_idx, force_buf)
            f_mag = finite_contact_force(np.linalg.norm(force_buf[:3]))
            if f_mag is None:
                continue
            if f_mag <= peak_force:
                continue
            peak_force = f_mag
            peak_time = float(data.time)
            peak_phase = phase_name
            geom1_name = _mj_id2name_or_none(model, mujoco.mjtObj.mjOBJ_GEOM, contact.geom1)
            geom2_name = _mj_id2name_or_none(model, mujoco.mjtObj.mjOBJ_GEOM, contact.geom2)
            body1_name = _mj_id2name_or_none(model, mujoco.mjtObj.mjOBJ_BODY, b1)
            body2_name = _mj_id2name_or_none(model, mujoco.mjtObj.mjOBJ_BODY, b2)
            if b1 == obstacle_id:
                peak_obstacle_body = body1_name
                peak_obstacle_geom = geom1_name
                peak_counterbody = body2_name
                peak_countergeom = geom2_name
            else:
                peak_obstacle_body = body2_name
                peak_obstacle_geom = geom2_name
                peak_counterbody = body1_name
                peak_countergeom = geom1_name
        return (peak_force, peak_time, peak_phase, peak_obstacle_body, peak_obstacle_geom, peak_counterbody, peak_countergeom)

    def _infer_contact_label_sets(self, model, task_spec=None) -> dict[str, set[str]]:
        obstacle_bodies: set[str] = set()
        task_object_bodies: set[str] = set()
        robot_bodies: set[str] = set()

        def _body_exists(name: str) -> bool:
            return mujoco is not None and _mj_id2name_or_none(model, mujoco.mjtObj.mjOBJ_BODY, mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_BODY, name)) == name

        def _add_body_name(name: str | None) -> None:
            if name and _body_exists(str(name)):
                task_object_bodies.add(str(name))
        if task_spec is not None:
            _obstacle = getattr(task_spec, 'obstacle_body_name', None)
            if _obstacle:
                obstacle_bodies.add(str(_obstacle))
            for _attr in ('grasp_target_body', 'peg_body_name', 'push_object_body', 'hinge_body_name'):
                _add_body_name(getattr(task_spec, _attr, None))
            _hinge_joint = getattr(task_spec, 'hinge_joint_name', None)
            if _hinge_joint and mujoco is not None:
                _joint_id = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_JOINT, str(_hinge_joint))
                if _joint_id >= 0:
                    _body_id = int(model.jnt_bodyid[_joint_id])
                    _add_body_name(_mj_id2name_or_none(model, mujoco.mjtObj.mjOBJ_BODY, _body_id))
            _door_handle_site = getattr(task_spec, 'door_handle_site', None)
            if _door_handle_site and mujoco is not None:
                _site_id = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_SITE, str(_door_handle_site))
                if _site_id >= 0:
                    _body_id = int(model.site_bodyid[_site_id])
                    _add_body_name(_mj_id2name_or_none(model, mujoco.mjtObj.mjOBJ_BODY, _body_id))
            if getattr(task_spec, 'object_initial_pose', None) is not None or getattr(task_spec, 'goal_object_position', None) is not None:
                _add_body_name('push_box')
            if getattr(task_spec, 'hinge_body_name', None) is not None:
                for _candidate in ('door_panel', 'door_body', 'door'):
                    _add_body_name(_candidate)
        if task_spec is None and 'push_box' in [_mj_id2name_or_none(model, mujoco.mjtObj.mjOBJ_BODY, i) for i in range(getattr(model, 'nbody', 0))]:
            task_object_bodies.add('push_box')
        ee_site_id = getattr(self, '_ee_site_id', None)
        if mujoco is not None and ee_site_id is not None and (ee_site_id >= 0):
            try:
                ee_body_id = int(model.site_bodyid[ee_site_id])
                robot_root_id = ee_body_id
                while robot_root_id > 0 and int(model.body_parentid[robot_root_id]) > 0:
                    robot_root_id = int(model.body_parentid[robot_root_id])
                for body_id in range(1, int(model.nbody)):
                    cur = body_id
                    while cur > 0:
                        if cur == robot_root_id:
                            name = _mj_id2name_or_none(model, mujoco.mjtObj.mjOBJ_BODY, body_id)
                            if name:
                                robot_bodies.add(name)
                            break
                        cur = int(model.body_parentid[cur])
            except Exception:
                robot_bodies = set()
        return {'obstacle_bodies': obstacle_bodies, 'task_object_bodies': task_object_bodies, 'robot_bodies': robot_bodies}

    def _build_contact_event(self, model, data, contact_index: int, *, phase_index: int | None, phase_name: str | None, phase_type: str | None, task_spec=None, episode_index: int | None=None, contact_label_sets: dict[str, set[str]] | None=None) -> ContactEvent:
        import mujoco
        contact = data.contact[contact_index]
        force_buf = np.zeros(6)
        mujoco.mj_contactForce(model, data, contact_index, force_buf)
        body_a_id = int(model.geom_bodyid[contact.geom1])
        body_b_id = int(model.geom_bodyid[contact.geom2])
        body_a = _mj_id2name_or_none(model, mujoco.mjtObj.mjOBJ_BODY, body_a_id)
        body_b = _mj_id2name_or_none(model, mujoco.mjtObj.mjOBJ_BODY, body_b_id)
        geom_a = _mj_id2name_or_none(model, mujoco.mjtObj.mjOBJ_GEOM, int(contact.geom1))
        geom_b = _mj_id2name_or_none(model, mujoco.mjtObj.mjOBJ_GEOM, int(contact.geom2))
        tcp_position = self._get_tcp_position(model, data)
        label_sets = contact_label_sets or {}
        obstacle_bodies = label_sets.get('obstacle_bodies', set())
        task_object_bodies = label_sets.get('task_object_bodies', set())
        robot_bodies = label_sets.get('robot_bodies', set())
        contact_normal = None
        try:
            contact_normal = tuple((float(x) for x in np.asarray(contact.frame, dtype=float)[:3]))
        except Exception:
            contact_normal = None
        contact_point = None
        try:
            contact_point = tuple((float(x) for x in np.asarray(contact.pos, dtype=float)[:3]))
        except Exception:
            contact_point = None
        sim_step = None
        try:
            sim_step = int(round(float(data.time) / float(model.opt.timestep)))
        except Exception:
            sim_step = None
        return ContactEvent(time=float(data.time), force=float(np.linalg.norm(force_buf[:3])), in_contact=True, episode_index=episode_index, phase_index=phase_index, phase_name=phase_name, phase_type=phase_type, sim_step=sim_step, body_a=body_a, geom_a=geom_a, body_b=body_b, geom_b=geom_b, contact_point=contact_point, contact_normal=contact_normal, contact_distance=float(contact.dist) if hasattr(contact, 'dist') and np.isfinite(float(contact.dist)) else None, tcp_position=tuple((float(x) for x in tcp_position[:3])) if tcp_position is not None else None, involves_obstacle=body_a in obstacle_bodies or body_b in obstacle_bodies if obstacle_bodies else False, involves_robot_link=body_a in robot_bodies or body_b in robot_bodies if robot_bodies else False, involves_task_object=body_a in task_object_bodies or body_b in task_object_bodies if task_object_bodies else False)

    @staticmethod
    def apply_randomisation(model, data, rand_config: dict, rng: np.random.Generator) -> dict[int, tuple[float, float, float]]:
        body_pos_deltas: dict[int, tuple[float, float, float]] = {}
        if not rand_config or not rand_config.get('enabled', False):
            return body_pos_deltas
        import mujoco

        def _find_body_id(candidates: list[str]) -> tuple[int, str] | tuple[None, None]:
            for name in candidates:
                if not name:
                    continue
                try:
                    body_id = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_BODY, name)
                except Exception:
                    continue
                if body_id >= 0:
                    return (body_id, name)
            return (None, None)

        def _record_body_delta(body_id: int, dx: float, dy: float, dz: float=0.0) -> None:
            (prev_dx, prev_dy, prev_dz) = body_pos_deltas.get(body_id, (0.0, 0.0, 0.0))
            body_pos_deltas[body_id] = (prev_dx + dx, prev_dy + dy, prev_dz + dz)

        def _maybe_shift_body(delta_key: str, candidates: list[str], *, force_body_pos: bool=False) -> None:
            delta = rand_config.get(delta_key)
            if delta is None:
                return
            try:
                dx_range = float(delta[0])
                dy_range = float(delta[1])
            except Exception:
                return
            (body_id, body_name) = _find_body_id(candidates)
            if body_id is None:
                logger.debug('Randomisation skipped: no body match for %s candidates %s', delta_key, candidates)
                return
            dx = rng.uniform(-dx_range, dx_range)
            dy = rng.uniform(-dy_range, dy_range)
            joint_adr = int(model.body_jntadr[body_id])
            use_qpos = False
            if not force_body_pos and joint_adr >= 0:
                joint_type = int(model.jnt_type[joint_adr])
                use_qpos = joint_type == mujoco.mjtJoint.mjJNT_FREE
            if use_qpos:
                qpos_addr = int(model.jnt_qposadr[joint_adr])
                data.qpos[qpos_addr] += dx
                data.qpos[qpos_addr + 1] += dy
                logger.debug('Randomisation applied to %s (body=%s via qpos): Δx=%.4f, Δy=%.4f', delta_key, body_name, dx, dy)
            else:
                model.body_pos[body_id, 0] += dx
                model.body_pos[body_id, 1] += dy
                _record_body_delta(body_id, dx, dy)
                logger.debug('Randomisation applied to %s (body=%s via body_pos): Δx=%.4f, Δy=%.4f', delta_key, body_name, dx, dy)
        object_candidates = ['peg_socket', 'peg', 'push_box', 'grasp_target', 'peg_channel_body', 'object', 'box']
        goal_candidates = ['goal_marker', 'goal', 'target_marker_0', 'target_marker']
        _maybe_shift_body('object_xy_delta', object_candidates)
        _maybe_shift_body('goal_xy_delta', goal_candidates, force_body_pos=True)
        _goal_z_delta = rand_config.get('goal_z_delta')
        if _goal_z_delta is not None:
            try:
                _goal_z_range = float(_goal_z_delta)
            except Exception:
                _goal_z_range = 0.0
            if _goal_z_range > 0.0:
                (_goal_body_id, _goal_body_name) = _find_body_id(goal_candidates)
                if _goal_body_id is not None:
                    dz = rng.uniform(0.0, _goal_z_range)
                    model.body_pos[_goal_body_id, 2] += dz
                    _record_body_delta(_goal_body_id, 0.0, 0.0, dz)
                    logger.debug('Randomisation applied to goal_z_delta (body=%s via body_pos): Δz=%.4f', _goal_body_name, dz)
                else:
                    logger.debug('Randomisation skipped: no body match for goal_z_delta candidates %s', goal_candidates)
        hinge_delta_deg = rand_config.get('hinge_delta_deg')
        if hinge_delta_deg:
            try:
                delta_rad = float(hinge_delta_deg) * (np.pi / 180.0)
            except Exception:
                delta_rad = 0.0
            if delta_rad <= 0.0:
                return body_pos_deltas
            joint_candidates = ['hinge', 'door_hinge', 'door_joint']
            joint_id = None
            joint_name = None
            for name in joint_candidates:
                try:
                    jid = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_JOINT, name)
                except Exception:
                    continue
                if jid >= 0:
                    joint_id = jid
                    joint_name = name
                    break
            if joint_id is None:
                logger.debug('Randomisation skipped: no hinge joint found')
                return body_pos_deltas
            qpos_addr = int(model.jnt_qposadr[joint_id])
            delta_angle = rng.uniform(-delta_rad, delta_rad)
            data.qpos[qpos_addr] += delta_angle
            logger.debug('Randomisation applied to hinge %s: Δθ=%.4f rad', joint_name, delta_angle)
        return body_pos_deltas

    def freeze_scene_randomisation(self) -> None:
        _rand_cfg = getattr(self, '_rand_config', None)
        _rand_rng = getattr(self, '_rand_rng', None)
        if getattr(self, '_rand_frozen_body_deltas', None) is not None or getattr(self, '_rand_frozen_qpos_delta', None) is not None:
            self._rand_scene_frozen = True
            return
        if _rand_cfg is None or _rand_rng is None:
            return
        try:
            import mujoco as _mujoco
        except ImportError:
            return
        model = self._get_model()
        data = _mujoco.MjData(model)
        qpos_before = data.qpos.copy()
        body_pos_before = model.body_pos.copy()
        try:
            body_pos_deltas = self.apply_randomisation(model, data, _rand_cfg, _rand_rng)
            qpos_delta = data.qpos - qpos_before
            self._rand_frozen_body_deltas: dict = body_pos_deltas
            self._rand_frozen_qpos_delta: np.ndarray = qpos_delta
        finally:
            model.body_pos[:] = body_pos_before
        self._rand_scene_frozen = True
        self._realized_scene_snapshots.clear()

    def unfreeze_scene_randomisation(self) -> None:
        self._rand_scene_frozen = False
        self._realized_scene_snapshots.clear()

    def realized_scene_snapshot(self, task_name: str, task_spec) -> RealizedSceneSnapshot:
        cached = self._realized_scene_snapshots.get(task_name)
        if cached is not None:
            return cached
        if not self.is_available():
            raise RuntimeError('MuJoCo is required to capture a realized scene snapshot')
        import mujoco as _mujoco
        model = self._get_model()
        data = _mujoco.MjData(model)
        if task_spec is not None and getattr(task_spec, 'object_initial_pose', None) is not None:
            self._reset_object_pose(model, data, task_spec.object_initial_pose, preferred_body_name=getattr(task_spec, 'peg_body_name', None))
        if task_spec is not None and getattr(task_spec, 'arm_initial_tcp_position', None) is not None:
            self._reset_arm_pose(model, data, task_spec.arm_initial_tcp_position)
        _mujoco.mj_forward(model, data)
        body_deltas = getattr(self, '_rand_frozen_body_deltas', None) or {}
        qpos_delta = getattr(self, '_rand_frozen_qpos_delta', None)
        if not getattr(self, '_rand_scene_frozen', False) and (getattr(self, '_rand_config', None) or {}).get('enabled', False):
            raise RuntimeError('freeze_scene_randomisation() before requesting a realized scene snapshot')
        body_pos_before = model.body_pos.copy()
        try:
            for (body_id, (dx, dy, dz)) in body_deltas.items():
                model.body_pos[body_id, :3] += (dx, dy, dz)
            if qpos_delta is not None:
                data.qpos[:] += qpos_delta
            _mujoco.mj_forward(model, data)
            snapshot = self._snapshot_from_state(task_name, task_spec, model, data)
        finally:
            model.body_pos[:] = body_pos_before
        self._realized_scene_snapshots[task_name] = snapshot
        return snapshot

    @staticmethod
    def _snapshot_from_state(task_name: str, task_spec, model, data) -> RealizedSceneSnapshot:
        import mujoco as _mujoco

        def body_pose(name: str) -> ScenePose | None:
            body_id = _mujoco.mj_name2id(model, _mujoco.mjtObj.mjOBJ_BODY, name)
            if body_id < 0:
                return None
            orientation = data.xquat[body_id] if hasattr(data, 'xquat') else None
            return ScenePose(name, data.xpos[body_id, :3], orientation)

        def site_pose(name: str) -> ScenePose | None:
            site_id = _mujoco.mj_name2id(model, _mujoco.mjtObj.mjOBJ_SITE, name)
            if site_id < 0:
                return None
            return ScenePose(name, data.site_xpos[site_id, :3])

        def geom_pose(name: str) -> ScenePose | None:
            geom_id = _mujoco.mj_name2id(model, _mujoco.mjtObj.mjOBJ_GEOM, name)
            if geom_id < 0:
                return None
            return ScenePose(name, data.geom_xpos[geom_id, :3])

        def first_body(*names: str) -> ScenePose | None:
            return next((pose for name in names if (pose := body_pose(name)) is not None), None)

        def scalar(name: str, value: Any) -> NamedScalar | None:
            return NamedScalar(name, value) if value is not None else None
        task = task_name.lower()
        objects: list[ScenePose] = []
        targets: list[ScenePose] = []
        obstacles: list[ScenePose] = []
        fixtures: list[ScenePose] = []
        axes: list[NamedVector] = []
        limits: list[NamedScalar] = []
        anchors: list[NamedVector] = []
        door: DoorState | None = None
        for (name, value) in (('goal_tolerance_m', getattr(task_spec, 'goal_tolerance', None)), ('force_limit_n', getattr(task_spec, 'force_limit', None)), ('hole_depth_m', getattr(task_spec, 'hole_depth', None)), ('channel_length_m', getattr(task_spec, 'channel_length', None)), ('obstacle_height_m', getattr(task_spec, 'obstacle_height', None)), ('force_scale_n', getattr(task_spec, 'force_scale', None))):
            item = scalar(name, value)
            if item is not None:
                limits.append(item)
        goal_body = first_body('goal_marker', 'goal', 'target_marker_0', 'target_marker')
        if task == 'push_to_goal':
            obj = first_body('push_box')
            if obj is not None:
                objects.append(obj)
                anchors.append(NamedVector('object', obj.position))
            if goal_body is not None:
                targets.append(ScenePose('task_goal', goal_body.position, goal_body.orientation))
                anchors.append(NamedVector('goal', goal_body.position))
            if obj is not None and goal_body is not None:
                axes.append(NamedVector('push_direction', np.asarray(goal_body.position) - np.asarray(obj.position)))
        elif task == 'peg_insert':
            peg = geom_pose('peg_tip') or first_body('peg', 'attachment')
            if peg is not None:
                objects.append(ScenePose('peg', peg.position, peg.orientation))
                anchors.extend((NamedVector('object', peg.position), NamedVector('task_object', peg.position)))
            socket = first_body('peg_socket')
            if socket is not None:
                fixtures.append(ScenePose('peg_socket', socket.position, socket.orientation))
                anchors.extend((NamedVector('fixture', socket.position), NamedVector('target', socket.position), NamedVector('socket', socket.position)))
            entry = site_pose('socket_hole') or socket
            if entry is not None:
                targets.append(ScenePose('socket_entry', entry.position, entry.orientation))
                anchors.append(NamedVector('goal', socket.position if socket is not None else entry.position))
            axis = getattr(task_spec, 'channel_axis', None)
            if axis is not None:
                axes.append(NamedVector('insertion_axis', axis))
        elif task == 'peg_channel':
            peg = first_body('peg')
            if peg is not None:
                objects.append(peg)
                anchors.append(NamedVector('object', peg.position))
            channel = first_body('peg_channel_body', 'channel_structure')
            if channel is not None:
                fixtures.append(channel)
                anchors.append(NamedVector('fixture', channel.position))
            for wall in ('channel_left_wall', 'channel_right_wall'):
                pose = body_pose(wall)
                if pose is not None:
                    fixtures.append(pose)
            axis = getattr(task_spec, 'channel_axis', None)
            length = getattr(task_spec, 'channel_length', None)
            if axis is not None:
                axes.append(NamedVector('channel_axis', axis))
                if peg is not None and length is not None:
                    exit_pos = np.asarray(peg.position) + np.asarray(axis, dtype=float) * float(length)
                    targets.append(ScenePose('channel_exit', exit_pos))
                    anchors.append(NamedVector('goal', exit_pos))
        elif task in ('door_push', 'door_pull'):
            panel = first_body('door_panel')
            if panel is not None:
                fixtures.append(panel)
                anchors.append(NamedVector('fixture', panel.position))
                hinge_id = _mujoco.mj_name2id(model, _mujoco.mjtObj.mjOBJ_JOINT, 'door_hinge')
                angle = float(data.qpos[int(model.jnt_qposadr[hinge_id])]) if hinge_id >= 0 else 0.0
                target_angle = getattr(task_spec, 'target_hinge_angle', None)
                door = DoorState(panel, (0.0, 0.0, 1.0), angle, target_angle)
                axes.append(NamedVector('door_hinge_axis', (0.0, 0.0, 1.0)))
                if target_angle is not None:
                    limits.append(NamedScalar('target_hinge_angle_rad', target_angle))
        elif task == 'grasp_place':
            obj = first_body('grasp_target')
            if obj is not None:
                objects.append(obj)
                anchors.append(NamedVector('object', obj.position))
            if goal_body is not None:
                targets.append(ScenePose('place_target', goal_body.position, goal_body.orientation))
                anchors.append(NamedVector('goal', goal_body.position))
        elif task == 'obstacle_reach':
            obstacle = first_body('obstacle_block')
            if obstacle is not None:
                obstacles.append(obstacle)
                anchors.append(NamedVector('fixture', obstacle.position))
            if goal_body is not None:
                targets.append(ScenePose('task_goal', goal_body.position, goal_body.orientation))
                anchors.append(NamedVector('goal', goal_body.position))
        return RealizedSceneSnapshot(task_name=task_name, object_starts=tuple(objects), targets=tuple(targets), obstacles=tuple(obstacles), fixtures=tuple(fixtures), fixture_states=(FixtureState('peg_socket', 'static_frozen'),) if any((pose.name == 'peg_socket' for pose in fixtures)) else (), axes=tuple(axes), limits=tuple(limits), anchors=tuple(anchors), door=door)

    @staticmethod
    def _get_goal_body_pos(model, task_spec) -> 'np.ndarray | None':
        import mujoco as _mj
        _goal_candidates = ['goal_marker', 'goal', 'target_marker_0', 'target_marker']
        for _name in _goal_candidates:
            _bid = _mj.mj_name2id(model, _mj.mjtObj.mjOBJ_BODY, _name)
            if _bid >= 0:
                return model.body_pos[_bid, :3].copy()
        if task_spec is not None:
            _goal = getattr(task_spec, 'goal_object_position', None)
            if _goal is None:
                _goal = getattr(task_spec, 'place_goal_position', None)
            if _goal is None:
                _goal = getattr(task_spec, 'goal_tcp_position', None)
            if _goal is not None:
                return np.array(_goal[:3], dtype=float)
        return None

    @staticmethod
    def _get_named_body_pos(model, data, body_name: str) -> 'np.ndarray | None':
        import mujoco as _mj
        try:
            _bid = _mj.mj_name2id(model, _mj.mjtObj.mjOBJ_BODY, body_name)
        except Exception:
            return None
        if _bid < 0:
            return None
        return data.xpos[_bid].copy()

    @staticmethod
    def _get_named_site_pos(model, data, site_name: str) -> 'np.ndarray | None':
        import mujoco as _mj
        try:
            site_id = _mj.mj_name2id(model, _mj.mjtObj.mjOBJ_SITE, site_name)
        except Exception:
            return None
        if site_id < 0:
            return None
        return data.site_xpos[site_id].copy()

    def open_gripper(self, model, data, width: float=0.08) -> None:
        import mujoco as _mj
        from simulation.scene import GRIPPER_ACTUATOR_NAMES
        gripper = self.scene_config.gripper
        if gripper is None or gripper not in GRIPPER_ACTUATOR_NAMES:
            return
        width = float(max(0.0, min(0.08, width)))
        actuator_names = GRIPPER_ACTUATOR_NAMES[gripper]
        for act_name in actuator_names:
            act_id = _mj.mj_name2id(model, _mj.mjtObj.mjOBJ_ACTUATOR, act_name)
            if act_id < 0:
                continue
            ctrl_val = width / 0.04 * 255.0
            (lo, hi) = model.actuator_ctrlrange[act_id]
            data.ctrl[act_id] = float(max(lo, min(hi, ctrl_val)))
        _mj.mj_forward(model, data)

    def close_gripper(self, model, data, force: float=20.0) -> None:
        import mujoco as _mj
        from simulation.scene import GRIPPER_ACTUATOR_NAMES
        gripper = self.scene_config.gripper
        if gripper is None or gripper not in GRIPPER_ACTUATOR_NAMES:
            return
        actuator_names = GRIPPER_ACTUATOR_NAMES[gripper]
        for act_name in actuator_names:
            act_id = _mj.mj_name2id(model, _mj.mjtObj.mjOBJ_ACTUATOR, act_name)
            if act_id < 0:
                continue
            (lo, _hi) = model.actuator_ctrlrange[act_id]
            data.ctrl[act_id] = float(lo)
        _mj.mj_forward(model, data)

    def _get_model(self):
        if self._model_override is not None:
            return self._model_override

        def _normalise_markers(markers) -> tuple[tuple[Any, ...], ...]:
            if not markers:
                return ()
            return tuple((tuple(marker) for marker in markers))
        cache_key = (self.scene_config.robot, self.scene_config.gripper, self.scene_config.object_xml, _normalise_markers(self.scene_config.target_markers), _normalise_markers(self.scene_config.tcp_markers))
        if cache_key not in MuJoCoBackend._model_cache:
            MuJoCoBackend._model_cache[cache_key] = build_scene(self.scene_config)
        return MuJoCoBackend._model_cache[cache_key]

    def _build_state(self, model, data, task_spec=None) -> dict:
        from simulation.ik import get_tcp_pose
        try:
            (tcp_pos, _tcp_quat) = get_tcp_pose(model, data, site_name=self.site_name)
        except Exception:
            tcp_pos = np.zeros(3)
            _tcp_quat = np.array([1.0, 0.0, 0.0, 0.0], dtype=float)
        if task_spec is not None:
            end_pos = np.array(task_spec.goal_tcp_position, dtype=float)
        else:
            end_pos = tcp_pos + np.array([0.05, 0.0, 0.0])
        nq = model.nq
        q_start = data.qpos[:nq].copy()
        q_end = q_start.copy()
        if nq > 0:
            q_end[0] = q_end[0] + 0.05
        return {'start': tcp_pos.copy(), 'end': end_pos, 'start_quat': np.asarray(_tcp_quat, dtype=float).copy(), 'q_start': q_start, 'q_end': q_end, 'elapsed_time': float(data.time), 'pose_error': 0.0, 'contact_force': 0.0, 'in_contact': bool(data.ncon > 0)}

    def _get_tcp_position(self, model, data) -> 'np.ndarray | None':
        site_id = getattr(self, '_ee_site_id', None)
        if site_id is not None and site_id >= 0:
            try:
                return np.array(data.site_xpos[site_id], dtype=float)
            except Exception:
                pass
        try:
            from simulation.ik import get_tcp_pose
            (tcp_pos, _) = get_tcp_pose(model, data, site_name=self.site_name)
            return np.array(tcp_pos, dtype=float)
        except Exception:
            return None

    @staticmethod
    def _get_optional_field(container: Any, name: str, default: Any=None) -> Any:
        if container is None:
            return default
        if isinstance(container, dict):
            return container.get(name, default)
        return getattr(container, name, default)

    def _get_phase_runtime_config(self, artifact, phase_idx: int) -> dict[str, Any]:
        phase_artifact = artifact.phases[phase_idx]
        runtime_meta = self._get_optional_field(artifact, 'phase_runtime_metadata', {}) or {}
        phase_id = self._get_optional_field(phase_artifact, 'phase_id', f'phase_{phase_idx}')
        phase_meta = runtime_meta.get(phase_id, {}) if isinstance(runtime_meta, dict) else {}
        return {'dsl_version': self._get_optional_field(phase_artifact, 'dsl_version', self._get_optional_field(artifact, 'dsl_version', 1)), 'target': self._get_optional_field(phase_artifact, 'target', self._get_optional_field(phase_meta, 'target')), 'guards': tuple(self._get_optional_field(phase_artifact, 'guards', self._get_optional_field(phase_meta, 'guards', ())) or ()), 'retries': self._get_optional_field(phase_artifact, 'retries', self._get_optional_field(phase_meta, 'retries')), 'parameters': tuple(self._get_optional_field(phase_artifact, 'parameters', self._get_optional_field(phase_meta, 'parameters', ())) or ()), 'parameter_bindings': self._get_optional_field(phase_artifact, 'parameter_bindings', self._get_optional_field(phase_meta, 'parameter_bindings', {})) or {}}

    @staticmethod
    def _estimate_phase_waypoint_count(state: dict[str, Any], local_params: dict[str, float]) -> int:
        start = np.asarray(state.get('start', (0.0, 0.0, 0.0)), dtype=float)
        end = np.asarray(state.get('end', start), dtype=float)
        distance = float(np.linalg.norm(end - start))
        speed = float(local_params.get('push_speed', local_params.get('speed', local_params.get('reach_speed', 0.1))))
        if not np.isfinite(speed) or speed <= 1e-06:
            speed = 0.1
        duration = distance / speed if distance > 1e-09 else 0.0
        return int(np.clip(math.ceil(duration / 0.05) + 1, 20, 120))

    @staticmethod
    def _first_failed_guard(guard_results: list[dict[str, Any]]) -> dict[str, Any] | None:
        for row in guard_results:
            if row.get('outcome') == 'fail':
                return row
        return None

    @staticmethod
    def _execute_trajectory_compat(execute_trajectory_fn, model, data, traj, site_name: str, *, max_steps_per_waypoint: int, max_total_steps: int, step_callback, cmd, termination_hook, pos_tol: float, ik_statistics) -> list:
        execute_kwargs = {'max_steps_per_waypoint': max_steps_per_waypoint, 'max_total_steps': max_total_steps, 'step_callback': step_callback, 'cmd': cmd, 'termination_hook': termination_hook, 'pos_tol': pos_tol, 'ik_statistics': ik_statistics}
        while True:
            try:
                return execute_trajectory_fn(model, data, traj, site_name, **execute_kwargs)
            except TypeError as exc:
                unsupported = next((name for name in ('max_total_steps', 'pos_tol', 'ik_statistics') if name in str(exc) and name in execute_kwargs), None)
                if unsupported is None:
                    raise
                execute_kwargs.pop(unsupported)

    def _iter_phase_parameter_bindings(self, phase_config: dict[str, Any]) -> list[tuple[str, Any]]:
        bindings: list[tuple[str, Any]] = []
        compiled_bindings = phase_config.get('parameter_bindings', {}) or {}
        if isinstance(compiled_bindings, dict) and compiled_bindings:
            for (param_name, entry) in compiled_bindings.items():
                for binding in tuple(self._get_optional_field(entry, 'bindings', ()) or ()):
                    bindings.append((str(param_name), binding))
            return bindings
        for (param_name, param_def) in phase_config.get('parameters', ()):
            for binding in tuple(self._get_optional_field(param_def, 'binds_to', ()) or ()):
                bindings.append((param_name, binding))
        return bindings

    @staticmethod
    def _normalise_quat(quat: Any) -> np.ndarray | None:
        if quat is None:
            return None
        arr = np.asarray(quat, dtype=float).reshape(-1)
        if arr.shape[0] != 4 or not np.all(np.isfinite(arr)):
            return None
        norm = float(np.linalg.norm(arr))
        if norm <= 1e-12:
            return None
        return arr / norm

    def _resolve_semantic_axis(self, axis_name: str | None, model, data, task_spec) -> np.ndarray | None:
        if not axis_name:
            return None
        key = str(axis_name).strip().lower()
        if key == 'world_x':
            return np.array([1.0, 0.0, 0.0], dtype=float)
        if key == 'world_y':
            return np.array([0.0, 1.0, 0.0], dtype=float)
        if key == 'world_z':
            return np.array([0.0, 0.0, 1.0], dtype=float)
        if key == 'task_goal_direction' and task_spec is not None:
            obj = self._get_object_position(model, data, task_spec)
            goal = self._get_goal_body_pos(model, task_spec)
            if goal is None and getattr(task_spec, 'goal_tcp_position', None) is not None:
                goal = np.array(task_spec.goal_tcp_position, dtype=float)
            if goal is None:
                return None
            axis = np.asarray(goal, dtype=float) - np.asarray(obj, dtype=float)
        elif task_spec is not None and key in {'channel_axis', 'insertion_axis'}:
            axis = self._get_optional_field(task_spec, key, None)
            if axis is None and key == 'insertion_axis':
                axis = self._get_optional_field(task_spec, 'channel_axis', None)
            if axis is None:
                return None
            axis = np.asarray(axis, dtype=float)
        else:
            return None
        norm = float(np.linalg.norm(axis))
        if norm <= 1e-12 or not np.all(np.isfinite(axis)):
            return None
        return np.asarray(axis, dtype=float) / norm

    def _resolve_v2_anchor_position(self, *, anchor: str, entity: str | None, base_state: dict[str, Any], model, data, task_spec) -> np.ndarray:
        anchor_key = str(anchor).strip().lower()
        if anchor_key == 'world':
            return np.zeros(3, dtype=float)
        if anchor_key == 'current_tcp':
            return np.asarray(base_state['start'], dtype=float)
        if anchor_key == 'task_object' and task_spec is not None:
            return np.asarray(self._get_object_position(model, data, task_spec), dtype=float)
        if anchor_key == 'task_object':
            raise ValueError("Unresolved DSL v2 anchor 'task_object': task_spec is required.")
        if anchor_key == 'task_goal':
            socket_site_id = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_SITE, 'socket_hole')
            if socket_site_id >= 0:
                return np.array(data.site_xpos[socket_site_id], dtype=float)
            goal = self._get_goal_body_pos(model, task_spec)
            if goal is None and task_spec is not None:
                goal = np.array(task_spec.goal_tcp_position, dtype=float)
            if goal is None:
                raise ValueError("Unresolved DSL v2 anchor 'task_goal'.")
            return np.asarray(goal, dtype=float)
        if anchor_key == 'fixture':
            if entity:
                body_id = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_BODY, entity)
                if body_id >= 0:
                    return np.array(data.xpos[body_id], dtype=float)
                site_id = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_SITE, entity)
                if site_id >= 0:
                    return np.array(data.site_xpos[site_id], dtype=float)
                raise ValueError(f"Unresolved DSL v2 fixture entity '{entity}'.")
            fixture = getattr(task_spec, 'fixture_pose', None) if task_spec is not None else None
            if fixture is not None:
                return np.array(fixture[:3], dtype=float)
            socket_id = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_BODY, 'peg_socket')
            if socket_id >= 0:
                return np.array(data.xpos[socket_id], dtype=float)
            raise ValueError("Unresolved DSL v2 anchor 'fixture'.")
        if anchor_key == 'body' and entity:
            body_id = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_BODY, entity)
            if body_id >= 0:
                return np.array(data.xpos[body_id], dtype=float)
            raise ValueError(f"Unresolved DSL v2 body entity '{entity}'.")
        if anchor_key == 'site' and entity:
            site_id = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_SITE, entity)
            if site_id >= 0:
                return np.array(data.site_xpos[site_id], dtype=float)
            raise ValueError(f"Unresolved DSL v2 site entity '{entity}'.")
        raise ValueError(f"Unresolved DSL v2 anchor '{anchor}'.")

    def _resolve_v2_orientation(self, orientation, base_state: dict[str, Any], model, data, task_spec) -> tuple[np.ndarray | None, str, dict[str, Any] | None]:
        if orientation is None:
            return (None, 'absent', None)
        mode = str(self._get_optional_field(orientation, 'mode', 'none'))
        if mode == 'none':
            return (None, 'none', None)
        if mode == 'keep_current':
            return (self._normalise_quat(base_state.get('start_quat')), 'executed', None)
        if mode == 'quat':
            quat = self._normalise_quat(self._get_optional_field(orientation, 'quat', None))
            return (quat, 'executed' if quat is not None else 'invalid', None)
        if mode == 'align_axis':
            align_with = self._get_optional_field(orientation, 'align_with', None)
            semantic_axis = self._resolve_semantic_axis(align_with, model, data, task_spec)
            if semantic_axis is None:
                raise ValueError(f"Unresolved DSL v2 orientation semantic axis '{align_with}'.")
            local_axis = np.asarray(self._get_optional_field(orientation, 'axis', None), dtype=float)
            local_norm = float(np.linalg.norm(local_axis))
            target_norm = float(np.linalg.norm(semantic_axis))
            if local_norm <= 1e-12 or not np.all(np.isfinite(local_axis)):
                raise ValueError('DSL v2 align_axis requires a finite non-zero local axis.')
            if target_norm <= 1e-12 or not np.all(np.isfinite(semantic_axis)):
                raise ValueError('DSL v2 align_axis requires a finite non-zero semantic axis.')
            return (None, 'axis_only', {'local_axis': (local_axis / local_norm).tolist(), 'target_axis': (semantic_axis / target_norm).tolist(), 'align_with': align_with, 'tolerance': self._get_optional_field(orientation, 'tolerance', None)})
        return (None, 'unsupported', None)

    def validate_v2_runtime_references(self, artifact, task_spec=None) -> None:
        model = self._get_model()
        data = mujoco.MjData(model)
        mujoco.mj_forward(model, data)
        base_state = {'start': np.zeros(3, dtype=float), 'start_quat': np.array([1.0, 0.0, 0.0, 0.0], dtype=float)}
        for phase in artifact.phases:
            if int(getattr(phase, 'dsl_version', 1) or 1) < 2:
                continue
            target = getattr(phase, 'target', None)
            if target is None:
                continue
            self._resolve_v2_anchor_position(anchor=str(self._get_optional_field(target, 'anchor', 'world')), entity=self._get_optional_field(target, 'entity', None), base_state=base_state, model=model, data=data, task_spec=task_spec)
            offset_along_axis = self._get_optional_field(target, 'offset_along_axis', None)
            if offset_along_axis is not None and self._resolve_semantic_axis(self._get_optional_field(offset_along_axis, 'axis', None), model, data, task_spec) is None:
                raise ValueError(f"Unresolved DSL v2 offset_along_axis semantic axis '{self._get_optional_field(offset_along_axis, 'axis', None)}'.")
            self._resolve_v2_orientation(self._get_optional_field(target, 'orientation', None), base_state, model, data, task_spec)

    def _prepare_v2_phase_execution(self, *, artifact, phase_idx: int, params: dict[str, float], base_state: dict[str, Any], model, data, task_spec, apply_termination_bindings: bool=True, retry_offset: np.ndarray | None=None, retry_attempt: int=0, preserve_generator_speed: bool=False) -> tuple[dict[str, Any] | None, dict[str, float], list[dict], list[tuple[Any, str, float]], list[dict], dict | None]:
        phase_config = self._get_phase_runtime_config(artifact, phase_idx)
        if int(phase_config.get('dsl_version', 1) or 1) < 2:
            return (None, dict(params), [], [], [], None)
        target = phase_config.get('target')
        if target is None:
            return (None, dict(params), [], [], [], None)
        phase_artifact = artifact.phases[phase_idx]
        phase_id = self._get_optional_field(phase_artifact, 'phase_id', f'phase_{phase_idx}')
        phase_params = dict(params)
        binding_records: list[dict] = []
        termination_restores: list[tuple[Any, str, float]] = []
        target_offset = np.array(self._get_optional_field(target, 'offset', (0.0, 0.0, 0.0)), dtype=float)
        offset_along_axis = self._get_optional_field(target, 'offset_along_axis', None)
        axis_distance = float(self._get_optional_field(offset_along_axis, 'distance', 0.0)) if offset_along_axis is not None else 0.0
        guard_runtime: list[dict] = []
        for guard in phase_config.get('guards', ()):
            guard_runtime.append({'guard_id': self._get_optional_field(guard, 'guard_id', 'guard'), 'when': self._get_optional_field(guard, 'when', 'after_phase'), 'predicate': self._get_optional_field(guard, 'predicate', 'unknown'), 'args': dict(self._get_optional_field(guard, 'args', ()) or ()), 'threshold': self._get_optional_field(guard, 'threshold', None), 'on_failure': self._get_optional_field(guard, 'on_failure', 'abort')})
        guard_lookup = {row['guard_id']: row for row in guard_runtime}
        retry_spec = phase_config.get('retries')
        retry_runtime = None
        if retry_spec is not None:
            retry_runtime = {'attempts': 0, 'max_attempts': int(self._get_optional_field(retry_spec, 'max_attempts', 0) or 0), 'strategy': self._get_optional_field(retry_spec, 'strategy', 'repeat'), 'reduce_speed_factor': float(self._get_optional_field(retry_spec, 'reduce_speed_factor', 0.5)), 'offset': list(self._get_optional_field(retry_spec, 'offset', (0.0, 0.0, 0.0)) or (0.0, 0.0, 0.0)), 'outcomes': [], 'executed': False}
        for (param_name, binding) in self._iter_phase_parameter_bindings(phase_config):
            flat_key = f'{phase_id}.{param_name}'
            if flat_key in phase_params:
                sampled_value = float(phase_params[flat_key])
                record_parameter = flat_key
            elif param_name in phase_params:
                sampled_value = float(phase_params[param_name])
                record_parameter = flat_key
            else:
                continue
            path = str(self._get_optional_field(binding, 'path', ''))
            mode = str(self._get_optional_field(binding, 'mode', 'add'))
            record = {'parameter': record_parameter, 'path': path, 'mode': mode, 'value': sampled_value, 'before': None, 'after': None, 'applied': False}
            if path.startswith('target.offset.') and path.rsplit('.', 1)[-1] in {'x', 'y', 'z'}:
                idx = {'x': 0, 'y': 1, 'z': 2}[path.rsplit('.', 1)[-1]]
                before = float(target_offset[idx])
                after = apply_binding_mode(before, sampled_value, mode)
                target_offset[idx] = after
                record['before'] = before
                record['after'] = after
                record['applied'] = True
            elif path == 'target.offset_along_axis.distance':
                before = float(axis_distance)
                after = apply_binding_mode(before, sampled_value, mode)
                axis_distance = after
                record['before'] = before
                record['after'] = after
                record['applied'] = True
            elif path in {'generator.speed', 'generator.arc_height', 'end_effector.grip_width'}:
                alias = path.split('.', 1)[1]
                concrete_key = f'{phase_id}.{alias}'
                if path == 'generator.speed' and preserve_generator_speed and (concrete_key in phase_params):
                    continue
                before = phase_params.get(f'{phase_id}.{alias}')
                base = float(before) if before is not None else 0.0
                after = apply_binding_mode(base, sampled_value, mode)
                phase_params[concrete_key] = after
                record['before'] = before
                record['after'] = after
                record['applied'] = True
            elif path.startswith('guards.') and path.endswith('.threshold'):
                guard_id = path[len('guards.'):-len('.threshold')]
                if guard_id in guard_lookup:
                    before = guard_lookup[guard_id]['threshold']
                    base = float(before) if before is not None else 0.0
                    after = apply_binding_mode(base, sampled_value, mode)
                    guard_lookup[guard_id]['threshold'] = after
                    record['before'] = before
                    record['after'] = after
                    record['applied'] = True
            elif path.startswith('retry.offset.') and retry_runtime is not None:
                axis_name = path.rsplit('.', 1)[-1]
                if axis_name in {'x', 'y', 'z'}:
                    idx = {'x': 0, 'y': 1, 'z': 2}[axis_name]
                    before = float(retry_runtime['offset'][idx])
                    after = apply_binding_mode(before, sampled_value, mode)
                    retry_runtime['offset'][idx] = after
                    record['before'] = before
                    record['after'] = after
                    record['applied'] = True
            elif path in {'termination.pose_tolerance', 'termination.force_threshold', 'duration.max_time'}:
                attr_name = {'termination.pose_tolerance': 'tol', 'termination.force_threshold': 'threshold', 'duration.max_time': 'max_time'}[path]
                if hasattr(phase_artifact.termination, attr_name):
                    before = float(getattr(phase_artifact.termination, attr_name))
                    after = apply_binding_mode(before, sampled_value, mode)
                    record['before'] = before
                    record['after'] = after
                    if apply_termination_bindings:
                        termination_restores.append((phase_artifact.termination, attr_name, before))
                        setattr(phase_artifact.termination, attr_name, after)
                        record['applied'] = True
                    else:
                        record['applied'] = False
            binding_records.append(record)
        anchor_pos = self._resolve_v2_anchor_position(anchor=str(self._get_optional_field(target, 'anchor', 'world')), entity=self._get_optional_field(target, 'entity', None), base_state=base_state, model=model, data=data, task_spec=task_spec)
        resolved_target = anchor_pos + target_offset
        resolved_axis = None
        if offset_along_axis is not None:
            resolved_axis = self._resolve_semantic_axis(self._get_optional_field(offset_along_axis, 'axis', None), model, data, task_spec)
            if resolved_axis is None:
                raise ValueError(f"Unresolved DSL v2 offset_along_axis semantic axis '{self._get_optional_field(offset_along_axis, 'axis', None)}'.")
            if str(self._get_optional_field(offset_along_axis, 'sign', 'positive')) == 'negative':
                resolved_axis = -resolved_axis
            axis_component = resolved_axis * axis_distance
            if str(self._get_optional_field(offset_along_axis, 'mode', 'add_to_offset')) == 'replace_offset_projection':
                resolved_target = resolved_target - np.dot(target_offset, resolved_axis) * resolved_axis
            resolved_target = resolved_target + axis_component
        if retry_offset is not None:
            resolved_target = resolved_target + np.asarray(retry_offset, dtype=float)
        (resolved_orientation, orientation_status, axis_alignment) = self._resolve_v2_orientation(self._get_optional_field(target, 'orientation', None), base_state, model, data, task_spec)
        target_trace = {'resolved_position': resolved_target.tolist(), 'resolved_orientation': resolved_orientation.tolist() if resolved_orientation is not None else None, 'resolved_axis_alignment': axis_alignment, 'orientation_status': orientation_status, 'source': 'retry_adjusted' if retry_offset is not None and np.linalg.norm(retry_offset) > 0.0 else str(self._get_optional_field(target, 'source', 'yaml')), 'anchor': self._get_optional_field(target, 'anchor', None), 'entity': self._get_optional_field(target, 'entity', None), 'base_offset': np.asarray(target_offset, dtype=float).tolist(), 'offset_along_axis': None, 'retry_attempt': int(retry_attempt), 'tolerance': self._get_optional_field(target, 'tolerance', None)}
        if self._get_optional_field(target, 'tolerance', None) is not None and hasattr(phase_artifact.termination, 'tol'):
            before = float(getattr(phase_artifact.termination, 'tol'))
            after = float(self._get_optional_field(target, 'tolerance', before))
            if apply_termination_bindings:
                termination_restores.append((phase_artifact.termination, 'tol', before))
                setattr(phase_artifact.termination, 'tol', after)
        if offset_along_axis is not None:
            target_trace['offset_along_axis'] = {'axis': self._get_optional_field(offset_along_axis, 'axis', None), 'resolved_axis': resolved_axis.tolist() if resolved_axis is not None else None, 'distance': float(axis_distance), 'sign': self._get_optional_field(offset_along_axis, 'sign', 'positive'), 'mode': self._get_optional_field(offset_along_axis, 'mode', 'add_to_offset')}
        runtime_state = dict(base_state)
        runtime_state['end'] = resolved_target
        runtime_state['resolved_target_metadata'] = target_trace
        if resolved_orientation is not None:
            runtime_state['target_orientation'] = resolved_orientation.copy()
        if axis_alignment is not None:
            runtime_state['target_axis_alignment'] = axis_alignment
        return (target_trace, phase_params, binding_records, termination_restores, guard_runtime, retry_runtime)

    def _apply_retry_strategy(self, *, phase_id: str, retry_runtime: dict[str, Any], run_phase_params: dict[str, float]) -> tuple[dict[str, float], np.ndarray | None]:
        strategy = str(retry_runtime.get('strategy', 'repeat'))
        updated_params = dict(run_phase_params)
        retry_offset: np.ndarray | None = None
        if strategy == 'repeat':
            return (updated_params, None)
        if strategy == 'offset_target':
            retry_offset = np.asarray(retry_runtime.get('offset', (0.0, 0.0, 0.0)), dtype=float)
            return (updated_params, retry_offset)
        if strategy == 'reduce_speed':
            speed_keys = [f'{phase_id}.speed', 'speed']
            for key in speed_keys:
                if key in updated_params:
                    updated_params[key] = float(updated_params[key]) * float(retry_runtime.get('reduce_speed_factor', 0.5))
                    return (updated_params, None)
            raise ValueError(f"DSL v2 retry strategy 'reduce_speed' requires a bound generator.speed consumer in phase '{phase_id}'.")
        raise ValueError(f"Unsupported DSL v2 retry strategy '{strategy}'.")

    @staticmethod
    def _carry_retry_runtime_state(previous: dict[str, Any] | None, current: dict[str, Any] | None) -> dict[str, Any] | None:
        if previous is None or current is None:
            return current
        carried = dict(current)
        carried['attempts'] = int(previous.get('attempts', 0))
        carried['executed'] = bool(previous.get('executed', False)) or bool(current.get('executed', False))
        for key in ('last_failed_guards', 'outcomes'):
            if key in previous:
                carried[key] = previous[key]
        return carried

    def _evaluate_phase_guard(self, guard_cfg: dict[str, Any], *, model, data, task_spec, state: dict[str, Any], tcp_end: np.ndarray | None=None, phase_contacts: list[ContactEvent] | None=None) -> dict:
        outcome = {'id': guard_cfg.get('guard_id'), 'predicate': guard_cfg.get('predicate'), 'when': guard_cfg.get('when'), 'threshold': guard_cfg.get('threshold'), 'on_failure': guard_cfg.get('on_failure'), 'outcome': 'skipped', 'observed_value': None}
        predicate = str(guard_cfg.get('predicate', ''))
        threshold = guard_cfg.get('threshold')
        args = dict(guard_cfg.get('args', {}) or {})
        contacts = self._filter_guard_contacts(phase_contacts or [], args)
        if predicate == 'force_below':
            if contacts:
                observed = max((float(event.force) for event in contacts))
            else:
                observed = 0.0
            outcome['observed_value'] = observed
            if threshold is not None:
                outcome['outcome'] = 'pass' if observed <= float(threshold) else 'fail'
        elif predicate == 'contact_detected':
            observed = len(contacts) > 0
            outcome['observed_value'] = observed
            outcome['outcome'] = 'pass' if observed else 'fail'
        elif predicate == 'bilateral_grasp':
            observed = bool(self._check_finger_contact(model, data))
            outcome['observed_value'] = observed
            outcome['outcome'] = 'pass' if observed else 'fail'
        elif predicate == 'object_lifted' and task_spec is not None:
            obj = self._get_object_position(model, data, task_spec)
            initial = self._get_optional_field(task_spec, 'object_initial_pose', None)
            if initial is not None:
                observed = float(obj[2] - float(initial[2]))
                outcome['observed_value'] = observed
                outcome['outcome'] = 'pass' if threshold is not None and observed >= float(threshold) else 'fail'
        elif predicate == 'hinge_delta_reached':
            joint_name = str(args.get('joint', 'door_hinge'))
            hinge_id = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_JOINT, joint_name)
            initial_angle = self._get_optional_field(state, 'initial_hinge_angle', None)
            if hinge_id >= 0 and initial_angle is not None:
                qpos_addr = int(model.jnt_qposadr[hinge_id])
                observed = float(data.qpos[qpos_addr] - float(initial_angle))
                outcome['observed_value'] = observed
                outcome['outcome'] = 'pass' if threshold is not None and observed >= float(threshold) else 'fail'
        elif predicate == 'pose_within_tolerance' and tcp_end is not None:
            observed = float(np.linalg.norm(np.asarray(state['end'], dtype=float) - np.asarray(tcp_end, dtype=float)))
            target_tol = self._get_optional_field(self._get_optional_field(state, 'resolved_target_metadata', {}), 'tolerance', None)
            tol = float(threshold if threshold is not None else target_tol if target_tol is not None else 0.01)
            outcome['observed_value'] = observed
            outcome['outcome'] = 'pass' if observed <= tol else 'fail'
        return outcome

    @staticmethod
    def _filter_guard_contacts(contacts: list[ContactEvent], args: dict[str, Any]) -> list[ContactEvent]:
        scope = str(args.get('scope', 'all_contacts'))
        body = args.get('body')
        geom = args.get('geom')
        if scope == 'task_obstacle':
            contacts = [event for event in contacts if event.involves_obstacle]
        elif scope == 'task_object':
            contacts = [event for event in contacts if event.involves_task_object]
        elif scope == 'robot_link':
            contacts = [event for event in contacts if event.involves_robot_link]
        elif scope in {'all_contacts', 'body_contact'}:
            pass
        if body is None and geom is None:
            return contacts
        body_name = str(body) if body is not None else None
        geom_name = str(geom) if geom is not None else None

        def _matches(event: ContactEvent) -> bool:
            if body_name is not None and body_name not in {event.body_a, event.body_b}:
                return False
            if geom_name is not None and geom_name not in {event.geom_a, event.geom_b}:
                return False
            return True
        return [event for event in contacts if _matches(event)]

    def _build_phase_state(self, phase_idx: int, n_phases: int, params: dict, artifact, model, data, task_spec=None) -> dict:
        base_state = self._build_state(model, data, task_spec=task_spec)
        phase_config = self._get_phase_runtime_config(artifact, phase_idx)
        if int(phase_config.get('dsl_version', 1) or 1) >= 2 and phase_config.get('target') is not None:
            (target_trace, _phase_params, _binding_records, _restores, _guards, _retry) = self._prepare_v2_phase_execution(artifact=artifact, phase_idx=phase_idx, params=params, base_state=base_state, model=model, data=data, task_spec=task_spec, apply_termination_bindings=False)
            if target_trace is not None:
                v2_state = dict(base_state)
                v2_state['end'] = np.asarray(target_trace['resolved_position'], dtype=float)
                v2_state['resolved_target_metadata'] = target_trace
                if target_trace.get('resolved_orientation') is not None:
                    v2_state['target_orientation'] = np.asarray(target_trace['resolved_orientation'], dtype=float)
                if target_trace.get('resolved_axis_alignment') is not None:
                    v2_state['target_axis_alignment'] = target_trace['resolved_axis_alignment']
                return v2_state
        if task_spec is not None and isinstance(getattr(task_spec, 'subtasks', None), tuple) and (len(task_spec.subtasks) > 0):
            _st_phase_artifact = artifact.phases[phase_idx]
            _st_subtask_id = getattr(_st_phase_artifact, 'subtask_id', None)
            if _st_subtask_id is not None:
                _st_spec = None
                for _st in task_spec.subtasks:
                    if _st.id == _st_subtask_id:
                        _st_spec = _st
                        break
                if _st_spec is not None:
                    _st_state = dict(base_state)
                    _st_offset = np.array(_st_spec.offset, dtype=float)
                    if _st_spec.anchor == 'world':
                        _st_target = _st_offset.copy()
                    elif _st_spec.anchor == 'object':
                        _st_obj_pos = self._get_object_position(model, data, task_spec)
                        _st_target = _st_obj_pos + _st_offset
                    elif _st_spec.anchor == 'goal':
                        _st_goal_pos = self._get_goal_body_pos(model, task_spec)
                        if _st_goal_pos is None:
                            _st_goal_pos = np.zeros(3, dtype=float)
                        _st_target = _st_goal_pos + _st_offset
                    elif _st_spec.anchor == 'fixture':
                        _fixture = getattr(task_spec, 'fixture_pose', None)
                        if _fixture is not None:
                            _st_target = np.array(_fixture[:3], dtype=float) + _st_offset
                        else:
                            _st_target = _st_offset.copy()
                    else:
                        _st_target = _st_offset.copy()
                    if _st_spec.param_offset_key is not None:
                        _pok = _st_spec.param_offset_key
                        _pok_lookup = _pok
                        if _pok_lookup not in params and _pok == 'push_depth' and ('push_distance' in params):
                            _pok_lookup = 'push_distance'
                        if _pok_lookup in params:
                            _pok_val = float(params[_pok_lookup])
                            _st_target_adj = list(_st_target)
                            if _pok == 'push_depth':
                                _st_obj_for_depth = self._get_object_position(model, data, task_spec)
                                _st_target_adj[1] = float(_st_obj_for_depth[1]) - _pok_val
                            elif _pok == 'approach_height':
                                _st_target_adj[2] = _pok_val
                            elif _pok == 'grasp_x_offset':
                                _st_obj_for_gx = self._get_object_position(model, data, task_spec)
                                _st_target_adj[0] = float(_st_obj_for_gx[0]) + _pok_val
                            elif _pok == 'grasp_z_offset':
                                _st_target_adj[2] += _pok_val
                            elif _pok == 'lift_height':
                                _st_lift_obj = self._get_object_position(model, data, task_spec)
                                _st_target_adj[2] = float(_st_lift_obj[2]) + _pok_val
                            elif _pok == 'place_height':
                                _st_target_adj[2] = _pok_val
                            else:
                                _st_target_adj[1] += _pok_val
                            _st_target = np.array(_st_target_adj, dtype=float)
                    _st_state['end'] = _st_target
                    return _st_state
        if task_spec is not None and getattr(task_spec, 'phase_target_map', None) is not None:
            _ptm_phase_artifact = artifact.phases[phase_idx]
            _ptm_phase_id = getattr(_ptm_phase_artifact, 'phase_name', f'phase_{phase_idx}')
            _ptm_phase_type = getattr(_ptm_phase_artifact, 'phase_type', None)
            if _ptm_phase_id in task_spec.phase_target_map:
                _ptm_phase_name = _ptm_phase_id
            elif _ptm_phase_type is not None:
                _ptm_phase_name = _ptm_phase_type
            else:
                _ptm_phase_name = _ptm_phase_id
            if _ptm_phase_name not in task_spec.phase_target_map and getattr(task_spec, 'phase_type_aliases', None):
                _ptm_phase_name = task_spec.phase_type_aliases.get(_ptm_phase_name, _ptm_phase_name)
            if _ptm_phase_name in task_spec.phase_target_map:
                _ptm_spec = task_spec.phase_target_map[_ptm_phase_name]
                _ptm_state = dict(base_state)
                _ptm_state['end'] = self._resolve_phase_target(_ptm_spec, model, data, task_spec)
                _push_depth_key = None
                if _ptm_phase_name == 'push':
                    if 'push_depth' in params:
                        _push_depth_key = 'push_depth'
                    elif 'push_distance' in params:
                        _push_depth_key = 'push_distance'
                if _push_depth_key is not None:
                    _push_depth = float(params[_push_depth_key])
                    _ptm_target_adj = list(_ptm_state['end'])
                    _obj_pos_for_depth = self._get_object_position(model, data, task_spec)
                    _ptm_target_adj[1] = float(_obj_pos_for_depth[1]) - float(_push_depth)
                    _ptm_state['end'] = np.array(_ptm_target_adj, dtype=float)
                _is_grasp_task = task_spec is not None and getattr(task_spec, 'grasp_target_body', None) is not None
                if _is_grasp_task:
                    if _ptm_phase_name == 'approach' and 'approach_height' in params:
                        _ptm_target_adj = list(_ptm_state['end'])
                        _ptm_target_adj[2] = float(params['approach_height'])
                        _ptm_state['end'] = np.array(_ptm_target_adj, dtype=float)
                    if _ptm_phase_name in ('descend', 'grasp') and 'grasp_x_offset' in params:
                        _ptm_target_adj = list(_ptm_state['end'])
                        _object_pos_for_gx = self._get_object_position(model, data, task_spec)
                        _ptm_target_adj[0] = float(_object_pos_for_gx[0]) + float(params['grasp_x_offset'])
                        _ptm_state['end'] = np.array(_ptm_target_adj, dtype=float)
                    if _ptm_phase_name == 'descend' and 'grasp_z_offset' in params:
                        _ptm_target_adj = list(_ptm_state['end'])
                        _ptm_target_adj[2] += float(params['grasp_z_offset'])
                        _ptm_state['end'] = np.array(_ptm_target_adj, dtype=float)
                    if _ptm_phase_name == 'lift' and 'lift_height' in params:
                        _object_pos = self._get_object_position(model, data, task_spec)
                        _ptm_target_adj = list(_ptm_state['end'])
                        _ptm_target_adj[2] = float(_object_pos[2]) + float(params['lift_height'])
                        _ptm_state['end'] = np.array(_ptm_target_adj, dtype=float)
                    if _ptm_phase_name == 'place' and 'place_height' in params:
                        _ptm_target_adj = list(_ptm_state['end'])
                        _ptm_target_adj[2] = float(params['place_height'])
                        _ptm_state['end'] = np.array(_ptm_target_adj, dtype=float)
                    if _ptm_phase_name == 'approach_goal' and 'approach_height' in params:
                        _ag_goal_pos = self._get_goal_body_pos(model, task_spec)
                        if _ag_goal_pos is not None:
                            _ptm_target_adj = list(_ptm_state['end'])
                            _ptm_target_adj[2] = float(_ag_goal_pos[2]) + float(params['approach_height'])
                            _ptm_state['end'] = np.array(_ptm_target_adj, dtype=float)
                    if _ptm_phase_name == 'transport_hover' and 'approach_height' in params:
                        _th_goal_pos = self._get_goal_body_pos(model, task_spec)
                        if _th_goal_pos is not None:
                            _ptm_target_adj = list(_ptm_state['end'])
                            _ptm_target_adj[2] = float(_th_goal_pos[2]) + float(params['approach_height'])
                            _ptm_state['end'] = np.array(_ptm_target_adj, dtype=float)
                    if _ptm_phase_name == 'place_1' and 'depth' in params:
                        _p1_goal_pos = self._get_goal_body_pos(model, task_spec)
                        if _p1_goal_pos is not None:
                            _ptm_target_adj = list(_ptm_state['end'])
                            _ptm_target_adj[2] = float(_p1_goal_pos[2]) + float(params['depth'])
                            _ptm_state['end'] = np.array(_ptm_target_adj, dtype=float)
                    if _ptm_phase_name == 'preplace_descend' and 'depth' in params:
                        _ppd_goal_pos = self._get_goal_body_pos(model, task_spec)
                        if _ppd_goal_pos is not None:
                            _ptm_target_adj = list(_ptm_state['end'])
                            _ptm_target_adj[2] = float(_ppd_goal_pos[2]) + float(params['depth'])
                            _ptm_state['end'] = np.array(_ptm_target_adj, dtype=float)
                return _ptm_state
        if task_spec is None or n_phases == 1 or phase_idx == n_phases - 1:
            return base_state
        goal = np.array(task_spec.goal_tcp_position, dtype=float)
        obstacle_height = float(task_spec.obstacle_height) if task_spec.obstacle_height is not None else 0.3
        obstacle_pos = np.array(task_spec.obstacle_position, dtype=float) if task_spec.obstacle_position is not None else np.array([0.5, goal[1], 0.0])
        arc_height = float(params.get('arc_height', 0.2))
        approach_dist = float(params.get('approach_distance', 0.15))
        safe_height = max(arc_height, obstacle_height + 0.05)
        phase = artifact.phases[phase_idx]
        from dsl.nodes import GeneratorType
        gen_type = getattr(getattr(phase, 'generator', None), 'generator_type', None)
        if gen_type is None:
            _gen_attr = getattr(phase, 'generator', None)
            if isinstance(_gen_attr, GeneratorType):
                gen_type = _gen_attr
        if gen_type == GeneratorType.ARC_CARTESIAN:
            arc_end = np.array([goal[0], goal[1], safe_height])
            new_state = dict(base_state)
            new_state['end'] = arc_end
            new_state['arc_angle_override'] = float(params.get('arc_angle', np.pi / 2.0))
            return new_state
        _phase_type_str = getattr(artifact.phases[phase_idx], 'phase_type', None)
        if _phase_type_str is None:
            _phase_type_str = getattr(artifact.phases[phase_idx], 'phase_name', f'phase_{phase_idx}')
        if _phase_type_str == 'lift':
            approach_x = min(obstacle_pos[0] - 0.05, goal[0] - approach_dist)
            approach_target = np.array([approach_x, goal[1], safe_height])
            new_state = dict(base_state)
            new_state['end'] = approach_target
            return new_state
        return base_state

    def _get_object_position(self, model, data, task_spec) -> 'np.ndarray':
        import mujoco as _mj
        _peg_body = getattr(task_spec, 'peg_body_name', None)
        candidates = ([_peg_body] if _peg_body else []) + ['push_box', 'grasp_target']
        peg_geom_id = _mj.mj_name2id(model, _mj.mjtObj.mjOBJ_GEOM, 'peg_tip')
        if peg_geom_id >= 0:
            return data.geom_xpos[peg_geom_id].copy()
        if getattr(self.scene_config, 'robot', None) == 'panda_peg':
            candidates = ['attachment', 'peg'] + candidates
        for _cand in candidates:
            body_id = _mj.mj_name2id(model, _mj.mjtObj.mjOBJ_BODY, _cand)
            if body_id >= 0:
                return data.xpos[body_id].copy()
        _init = getattr(task_spec, 'object_initial_pose', None)
        if _init is not None:
            return np.array(_init[:3], dtype=float)
        try:
            from evaluation.metrics import _PHASE_SCORING_TASKS
        except Exception:
            _PHASE_SCORING_TASKS = frozenset()
        _task_name = str(getattr(task_spec, 'task_name', None) or getattr(task_spec, 'name', None) or '').strip().lower()
        if not _task_name:
            if getattr(task_spec, 'grasp_target_body', None):
                _task_name = 'grasp_place'
            elif getattr(task_spec, 'peg_body_name', None):
                _task_name = 'peg_channel'
            elif getattr(task_spec, 'goal_object_position', None) is not None:
                _task_name = 'push_to_goal'
        if _task_name in _PHASE_SCORING_TASKS:
            logger.warning('_get_object_position fallback reached origin: no known object body found and task_spec.object_initial_pose is None (task=%s).', _task_name)
        return np.zeros(3)

    def _resolve_phase_target(self, spec, model, data, task_spec) -> 'np.ndarray':
        from evaluation.task_spec import PhaseTargetSpec
        if isinstance(spec, (tuple, list, np.ndarray)):
            return np.array(spec, dtype=float)
        if not isinstance(spec, PhaseTargetSpec):
            return np.array(spec, dtype=float)
        offset = np.array(spec.offset, dtype=float)
        if spec.anchor == 'world':
            return offset
        elif spec.anchor == 'object':
            obj_pos = self._get_object_position(model, data, task_spec)
            return obj_pos + offset
        elif spec.anchor == 'goal':
            _goal_pos = self._get_goal_body_pos(model, task_spec)
            if _goal_pos is None:
                _goal_pos = np.zeros(3, dtype=float)
            return _goal_pos + offset
        elif spec.anchor == 'fixture':
            fixture = getattr(task_spec, 'fixture_pose', None)
            if fixture is not None:
                return np.array(fixture[:3], dtype=float) + offset
            return offset
        return offset

    def _reset_object_pose(self, model, data, pos: tuple[float, float, float], preferred_body_name: str | None=None) -> None:
        import mujoco
        body_id = -1
        candidates = ([preferred_body_name] if preferred_body_name else []) + ['push_box', 'grasp_target']
        for _candidate in candidates:
            body_id = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_BODY, _candidate)
            if body_id >= 0:
                break
        if body_id < 0:
            return
        joint_id = model.body_jntadr[body_id]
        if joint_id < 0:
            return
        qadr = model.jnt_qposadr[joint_id]
        data.qpos[qadr:qadr + 3] = pos
        data.qpos[qadr + 3:qadr + 7] = [1, 0, 0, 0]
        mujoco.mj_forward(model, data)

    def _check_finger_contact(self, model, data, object_body_names: tuple=('grasp_target',), finger_body_names: tuple=('left_finger', 'right_finger'), force_threshold: float=0.05) -> bool:
        import mujoco as _mj
        object_body_ids: set = set()
        for name in object_body_names:
            bid = _mj.mj_name2id(model, _mj.mjtObj.mjOBJ_BODY, name)
            if bid >= 0:
                object_body_ids.add(bid)
        finger_body_ids: set = set()
        for name in finger_body_names:
            bid = _mj.mj_name2id(model, _mj.mjtObj.mjOBJ_BODY, name)
            if bid >= 0:
                finger_body_ids.add(bid)
        if not object_body_ids or not finger_body_ids:
            return False
        for c_idx in range(data.ncon):
            contact = data.contact[c_idx]
            b1 = model.geom_bodyid[contact.geom1]
            b2 = model.geom_bodyid[contact.geom2]
            if b1 in finger_body_ids and b2 in object_body_ids or (b2 in finger_body_ids and b1 in object_body_ids):
                force_buf = np.zeros(6)
                _mj.mj_contactForce(model, data, c_idx, force_buf)
                f_mag = float(np.linalg.norm(force_buf[:3]))
                if f_mag > force_threshold:
                    return True
        return False

    def _check_bilateral_contact(self, model, data, object_body_names: tuple=('grasp_target',), left_finger_name: str='left_finger', right_finger_name: str='right_finger', force_threshold: float=0.5) -> bool:
        import mujoco as _mj
        object_body_ids: set = set()
        for name in object_body_names:
            bid = _mj.mj_name2id(model, _mj.mjtObj.mjOBJ_BODY, name)
            if bid >= 0:
                object_body_ids.add(bid)
        if not object_body_ids:
            return False
        left_bid = _mj.mj_name2id(model, _mj.mjtObj.mjOBJ_BODY, left_finger_name)
        right_bid = _mj.mj_name2id(model, _mj.mjtObj.mjOBJ_BODY, right_finger_name)
        if left_bid < 0 or right_bid < 0:
            return False
        left_contact = False
        right_contact = False
        for c_idx in range(data.ncon):
            if left_contact and right_contact:
                break
            contact = data.contact[c_idx]
            b1 = model.geom_bodyid[contact.geom1]
            b2 = model.geom_bodyid[contact.geom2]
            involves_object = b1 in object_body_ids or b2 in object_body_ids
            if not involves_object:
                continue
            involves_left = b1 == left_bid or b2 == left_bid
            involves_right = b1 == right_bid or b2 == right_bid
            if not (involves_left or involves_right):
                continue
            force_buf = np.zeros(6)
            _mj.mj_contactForce(model, data, c_idx, force_buf)
            f_mag = float(np.linalg.norm(force_buf[:3]))
            if f_mag > force_threshold:
                if involves_left:
                    left_contact = True
                if involves_right:
                    right_contact = True
        return left_contact and right_contact

    def _reset_arm_pose(self, model, data, tcp_position: tuple[float, float, float]) -> None:
        import mujoco as _mujoco
        from simulation.ik import solve_ik
        NATURAL_ARM_SEED_QPOS = np.array([0.0, -0.3, 0.0, -2.2, 0.0, 2.0, 0.785])
        target = np.array(tcp_position, dtype=float)
        q_backup = data.qpos.copy()
        data.qpos[:7] = NATURAL_ARM_SEED_QPOS
        if model.nu > 7:
            data.qpos[7:9] = [0.04, 0.04]
            self.open_gripper(model, data)
        _mujoco.mj_forward(model, data)
        result = solve_ik(model, data, target, target_quat=None)
        if result.success:
            _mujoco.mj_forward(model, data)
        else:
            data.qpos[:] = q_backup
            _mujoco.mj_forward(model, data)

    def _check_termination_online(self, model, data, phase_artifact, task_spec=None, phase_target=None, initial_ncon: int=0, initial_finger_contact: bool=False) -> bool:
        from dsl.nodes import TerminationCond
        try:
            cond = phase_artifact.termination.cond
        except AttributeError:
            return False
        if cond == TerminationCond.TIME_LIMIT:
            return False
        elif cond == TerminationCond.CONTACT_DETECTED:
            _relevant_body_name = None
            if task_spec is not None:
                for _attr in ('grasp_target_body', 'peg_body_name', 'push_object_body'):
                    _body_name = getattr(task_spec, _attr, None)
                    if _body_name:
                        _relevant_body_name = _body_name
                        break
            import mujoco as _mj_cd
            _has_fingers = _mj_cd.mj_name2id(model, _mj_cd.mjtObj.mjOBJ_BODY, 'left_finger') >= 0 or _mj_cd.mj_name2id(model, _mj_cd.mjtObj.mjOBJ_BODY, 'right_finger') >= 0
            if _has_fingers:
                if initial_finger_contact:
                    return False
                if not self._check_finger_contact(model, data, force_threshold=self.CONTACT_DETECTED_ONLINE_FORCE_MIN):
                    return False
            else:
                if initial_ncon != 0:
                    return False
                if not self._any_relevant_contact(model, data, _relevant_body_name):
                    return False
            peak_force = self._peak_contact_force_live(model, data)
            return self.CONTACT_DETECTED_ONLINE_FORCE_MIN <= peak_force <= self.CONTACT_DETECTED_ONLINE_FORCE_MAX
        elif cond == TerminationCond.FORCE_EXCEEDED:
            threshold = getattr(phase_artifact.termination, 'threshold', 10.0)
            return self._peak_contact_force_live(model, data) > threshold
        elif cond == TerminationCond.POSE_TOLERANCE:
            return False
        elif cond == TerminationCond.CONTACT_LOST:
            return False
        elif cond == TerminationCond.GRASP_SUCCESS:
            if phase_target is None:
                return False
            tcp_pos = self._get_tcp_position(model, data)
            if tcp_pos is None:
                return False
            tol = getattr(task_spec, 'goal_tolerance', 0.05) if task_spec is not None else 0.05
            return bool(np.linalg.norm(tcp_pos - np.asarray(phase_target, dtype=float)) < tol)
        return False

    def _any_relevant_contact(self, model, data, relevant_body_name: str | None=None) -> bool:
        if data.ncon <= 0:
            return False
        if not relevant_body_name:
            return True
        import mujoco as _mj
        _body_id = _mj.mj_name2id(model, _mj.mjtObj.mjOBJ_BODY, relevant_body_name)
        if _body_id < 0:
            logger.warning("Relevant contact body '%s' not found in model; falling back to any-contact check.", relevant_body_name)
            return True
        for c in range(data.ncon):
            _contact = data.contact[c]
            _geom1_body = int(model.geom_bodyid[_contact.geom1])
            _geom2_body = int(model.geom_bodyid[_contact.geom2])
            if _geom1_body == _body_id or _geom2_body == _body_id:
                return True
        return False

    def _peak_contact_force_live(self, model, data) -> float:
        import mujoco as _mj
        peak = 0.0
        for c in range(data.ncon):
            force_buf = np.zeros(6)
            _mj.mj_contactForce(model, data, c, force_buf)
            force = finite_contact_force(np.linalg.norm(force_buf[:3]))
            if force is not None:
                peak = max(peak, force)
        return peak

    def _check_termination_condition(self, phase, model, data, tcp_start: np.ndarray, tcp_end: np.ndarray, phase_state: dict, contact_events: list, peak_force: float, task_spec=None) -> bool:
        from dsl.nodes import TerminationCond
        try:
            cond = phase.termination.cond
        except AttributeError:
            return True
        if cond == TerminationCond.TIME_LIMIT:
            return True
        elif cond == TerminationCond.POSE_TOLERANCE:
            target = np.array(phase_state['end'], dtype=float)
            dist = float(np.linalg.norm(tcp_end - target))
            return dist < 0.05
        elif cond == TerminationCond.FORCE_EXCEEDED:
            return peak_force > 2.0
        elif cond == TerminationCond.CONTACT_DETECTED:
            return len(contact_events) > 0
        elif cond == TerminationCond.CONTACT_LOST:
            return data.ncon == 0
        elif cond == TerminationCond.GRASP_SUCCESS:
            _phase_state = phase_state or {}
            target = _phase_state.get('end')
            if target is None:
                return False
            tcp_pos = self._get_tcp_position(model, data)
            if tcp_pos is None:
                return False
            tol = getattr(task_spec, 'goal_tolerance', 0.05) if task_spec is not None else 0.05
            return bool(np.linalg.norm(tcp_pos - np.array(target, dtype=float)) < tol)
        return True

    def _collect_contacts(self, model, data, *, phase_index: int | None=None, phase_name: str | None=None, phase_type: str | None=None, task_spec=None, episode_index: int | None=None, contact_label_sets: dict[str, set[str]] | None=None) -> list[ContactEvent]:
        return [self._build_contact_event(model, data, c, phase_index=phase_index, phase_name=phase_name, phase_type=phase_type, task_spec=task_spec, episode_index=episode_index, contact_label_sets=contact_label_sets) for c in range(data.ncon)]

    def _render_frame(self, model, data, run_id: str, frame_idx: int) -> None:
        import mujoco
        from PIL import Image
        frame_dir = self.render_dir / run_id
        frame_dir.mkdir(parents=True, exist_ok=True)
        with mujoco.Renderer(model, self.render_height, self.render_width) as renderer:
            renderer.update_scene(data)
            pixels = renderer.render()
        img = Image.fromarray(pixels)
        img.save(frame_dir / f'frame_{frame_idx:04d}.png')

    def capture_phase_keyframes(self, phase_name: str, out_dir: Path, cameras: list[dict] | None=None, width: int=480, height: int=360, *, model=None, data=None) -> dict[str, Path]:
        import mujoco
        from PIL import Image
        if cameras is None:
            cameras = [{'name': 'overview', 'azimuth': 45.0, 'elevation': -20.0, 'distance': 2.2, 'lookat': [0.5, 0.0, 0.15]}, {'name': 'side', 'azimuth': 90.0, 'elevation': -15.0, 'distance': 2.0, 'lookat': [0.5, 0.0, 0.15]}]
        if model is None or data is None:
            model = self._get_model()
            data = mujoco.MjData(model)
            mujoco.mj_forward(model, data)
        out_root = Path(out_dir)
        phase_token = (phase_name or 'phase').strip()
        if not phase_token:
            phase_token = 'phase'
        safe_phase = phase_token.replace(' ', '_')
        phase_dir = out_root / 'keyframes' / safe_phase
        phase_dir.mkdir(parents=True, exist_ok=True)
        results: dict[str, Path] = {}
        with mujoco.Renderer(model, height, width) as renderer:
            for cam_cfg in cameras:
                if isinstance(cam_cfg, str):
                    logger.warning("capture_phase_keyframes: string camera name '%s' not supported; pass a dict config instead. Skipping.", cam_cfg)
                    continue
                cam_name = cam_cfg['name']
                cam = mujoco.MjvCamera()
                cam.type = mujoco.mjtCamera.mjCAMERA_FREE
                cam.azimuth = float(cam_cfg['azimuth'])
                cam.elevation = float(cam_cfg['elevation'])
                cam.distance = float(cam_cfg['distance'])
                cam.lookat[:] = cam_cfg['lookat']
                renderer.update_scene(data, camera=cam)
                pixels = renderer.render()
                out_path = phase_dir / f'{cam_name}.png'
                Image.fromarray(pixels).save(out_path)
                results[cam_name] = out_path
        return results
