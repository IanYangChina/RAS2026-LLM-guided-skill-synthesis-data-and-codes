from __future__ import annotations
from typing import Any

def _pos(t: tuple | list | None) -> list[float] | None:
    if t is None:
        return None
    return [float(v) for v in t]

def _getattr_safe(obj: Any, name: str, default: Any=None) -> Any:
    return getattr(obj, name, default)

def _robot_entry(task_spec: Any, sim_config: dict) -> dict:
    gripper = sim_config.get('gripper') or None
    robot_model = sim_config.get('robot', 'panda_full')
    if gripper == 'franka_hand':
        robot_model = 'panda_full'
    initial_tcp = _pos(_getattr_safe(task_spec, 'arm_initial_tcp_position'))
    entry: dict = {'model': robot_model, 'tcp_site': 'attachment_site', 'gripper': gripper}
    if initial_tcp is not None:
        entry['tcp_initial_world'] = initial_tcp
    return entry

def _build_push_to_goal(task_spec: Any) -> tuple[list[dict], dict]:
    objects: list[dict] = [{'name': 'push_box', 'role': 'manipulated_object', 'dynamics': 'free', 'geometry': 'box', 'dimensions_m': [0.05, 0.05, 0.05], 'mass_kg': 0.1}, {'name': 'goal_marker', 'role': 'target_marker', 'dynamics': 'static', 'geometry': 'point'}]
    obj_init = _pos(_getattr_safe(task_spec, 'object_initial_pose'))
    goal_obj = _pos(_getattr_safe(task_spec, 'goal_object_position'))
    landmarks: dict = {}
    if obj_init is not None:
        landmarks['object_initial_position'] = obj_init
    if goal_obj is not None:
        landmarks['goal_object_position'] = goal_obj
    if obj_init and goal_obj:
        landmarks['push_displacement_m'] = [round(goal_obj[i] - obj_init[i], 4) for i in range(3)]
    return (objects, landmarks)

def _build_peg_insert(task_spec: Any) -> tuple[list[dict], dict]:
    objects: list[dict] = [{'name': 'peg_socket', 'role': 'fixture', 'dynamics': 'static', 'geometry': 'box_with_hole', 'base_dimensions_m': [0.12, 0.12, 0.05], 'hole_entry_height_m': 0.08}, {'name': 'peg', 'role': 'manipulated_object', 'dynamics': 'free', 'geometry': 'cylinder', 'note': 'peg is a fixed end-effector attachment on the panda_peg arm'}]
    hole_depth = _getattr_safe(task_spec, 'hole_depth')
    channel_axis = _pos(_getattr_safe(task_spec, 'channel_axis'))
    fixture_pose = _pos(_getattr_safe(task_spec, 'fixture_pose'))
    obj_init = _pos(_getattr_safe(task_spec, 'object_initial_pose'))
    goal_tcp = _pos(_getattr_safe(task_spec, 'goal_tcp_position'))
    landmarks: dict = {}
    if hole_depth is not None:
        landmarks['hole_depth_m'] = float(hole_depth)
    landmarks['hole_entry_world_z_m'] = 0.08
    if channel_axis is not None:
        landmarks['insertion_axis'] = channel_axis
    if fixture_pose is not None:
        landmarks['frozen_socket_position'] = fixture_pose
        landmarks['socket_state'] = 'static_frozen'
    elif obj_init is not None:
        landmarks['peg_initial_position'] = obj_init
    if goal_tcp is not None:
        landmarks['hole_entry_goal_world'] = goal_tcp
    return (objects, landmarks)

def _build_peg_channel(task_spec: Any) -> tuple[list[dict], dict]:
    objects: list[dict] = [{'name': 'peg', 'role': 'manipulated_object', 'dynamics': 'free', 'geometry': 'cylinder', 'radius_m': 0.018, 'half_length_m': 0.025}, {'name': 'channel_structure', 'role': 'fixture', 'dynamics': 'static', 'geometry': 'two_parallel_walls', 'inner_gap_m': 0.05, 'wall_thickness_m': 0.03, 'wall_height_m': 0.05}]
    channel_axis = _pos(_getattr_safe(task_spec, 'channel_axis'))
    channel_length = _getattr_safe(task_spec, 'channel_length')
    obj_init = _pos(_getattr_safe(task_spec, 'object_initial_pose'))
    goal_tcp = _pos(_getattr_safe(task_spec, 'goal_tcp_position'))
    wall_bodies = _getattr_safe(task_spec, 'channel_wall_bodies')
    landmarks: dict = {}
    if channel_axis is not None:
        landmarks['channel_axis'] = channel_axis
    if channel_length is not None:
        landmarks['channel_length_m'] = float(channel_length)
    if obj_init is not None:
        landmarks['peg_initial_position'] = obj_init
    if goal_tcp is not None:
        landmarks['channel_exit_goal'] = goal_tcp
    if wall_bodies is not None:
        landmarks['channel_wall_bodies'] = list(wall_bodies)
    return (objects, landmarks)

def _build_door_push(task_spec: Any) -> tuple[list[dict], dict]:
    objects: list[dict] = [{'name': 'door_panel', 'role': 'fixture', 'dynamics': 'hinged', 'geometry': 'box', 'dimensions_m': [0.4, 0.02, 0.7], 'hinge_axis': 'Z', 'hinge_joint_name': 'door_hinge'}, {'name': 'door_handle', 'role': 'grasp_site', 'dynamics': 'hinged_with_panel', 'geometry': 'site', 'body_frame_offset_m': [-0.4, -0.02, 0.35]}, {'name': 'door_frame', 'role': 'fixture', 'dynamics': 'static', 'geometry': 'box'}]
    target_angle = _getattr_safe(task_spec, 'target_hinge_angle')
    hinge_body = _getattr_safe(task_spec, 'hinge_body_name')
    hinge_joint = _getattr_safe(task_spec, 'hinge_joint_name')
    handle_site = _getattr_safe(task_spec, 'door_handle_site')
    goal_tcp = _pos(_getattr_safe(task_spec, 'goal_tcp_position'))
    landmarks: dict = {}
    if hinge_body is not None:
        landmarks['hinge_body'] = str(hinge_body)
    if hinge_joint is not None:
        landmarks['hinge_joint'] = str(hinge_joint)
    if target_angle is not None:
        landmarks['target_hinge_angle_rad'] = float(target_angle)
        landmarks['target_hinge_angle_deg'] = round(float(target_angle) * 180.0 / 3.14159265, 2)
        landmarks['goal_type'] = 'door_hinge_angle'
    if handle_site is not None:
        landmarks['handle_site'] = str(handle_site)
    if goal_tcp is not None:
        landmarks['goal_tcp_position_placeholder'] = goal_tcp
    return (objects, landmarks)

def _build_grasp_place(task_spec: Any) -> tuple[list[dict], dict]:
    objects: list[dict] = [{'name': 'grasp_target', 'role': 'manipulated_object', 'dynamics': 'free', 'geometry': 'box', 'dimensions_m': [0.04, 0.04, 0.06], 'mass_kg': 0.05}, {'name': 'placement_surface', 'role': 'goal_area', 'dynamics': 'static', 'geometry': 'point'}]
    obj_init = _pos(_getattr_safe(task_spec, 'object_initial_pose'))
    place_goal = _pos(_getattr_safe(task_spec, 'place_goal_position'))
    grasp_approach = _pos(_getattr_safe(task_spec, 'grasp_approach_position'))
    grasp_body = _getattr_safe(task_spec, 'grasp_target_body')
    landmarks: dict = {}
    if obj_init is not None:
        landmarks['object_initial_position'] = obj_init
    if grasp_approach is not None:
        landmarks['grasp_approach_position'] = grasp_approach
    if place_goal is not None:
        landmarks['place_goal_position'] = place_goal
    if grasp_body is not None:
        landmarks['grasp_target_body'] = str(grasp_body)
    if obj_init and place_goal:
        landmarks['transport_displacement_m'] = [round(place_goal[i] - obj_init[i], 4) for i in range(3)]
    return (objects, landmarks)

def _build_obstacle_reach(task_spec: Any) -> tuple[list[dict], dict]:
    obs_height = _getattr_safe(task_spec, 'obstacle_height')
    objects: list[dict] = [{'name': 'obstacle_block', 'role': 'obstacle', 'dynamics': 'static', 'geometry': 'box', 'dimensions_m': [0.08, 0.3, round(float(obs_height), 4) if obs_height is not None else 0.3]}, {'name': 'goal_marker', 'role': 'target_marker', 'dynamics': 'static', 'geometry': 'point'}]
    obs_pos = _pos(_getattr_safe(task_spec, 'obstacle_position'))
    obs_body = _getattr_safe(task_spec, 'obstacle_body_name')
    goal_tcp = _pos(_getattr_safe(task_spec, 'goal_tcp_position'))
    landmarks: dict = {}
    if obs_body is not None:
        landmarks['obstacle_body'] = str(obs_body)
    if obs_pos is not None:
        landmarks['obstacle_position'] = obs_pos
    if obs_height is not None:
        landmarks['obstacle_height_m'] = float(obs_height)
    if goal_tcp is not None:
        landmarks['goal_tcp_position'] = goal_tcp
    if obs_pos and goal_tcp:
        landmarks['goal_beyond_obstacle'] = goal_tcp[0] > obs_pos[0]
    return (objects, landmarks)
_TASK_BUILDERS = {'push_to_goal': _build_push_to_goal, 'peg_insert': _build_peg_insert, 'peg_channel': _build_peg_channel, 'door_push': _build_door_push, 'door_pull': _build_door_push, 'grasp_place': _build_grasp_place, 'obstacle_reach': _build_obstacle_reach}

def get_scene_entities(task_name: str, task_spec: Any, sim_config: dict, realized_scene_snapshot: dict | None=None) -> dict:
    robot = _robot_entry(task_spec, sim_config)
    builder = _TASK_BUILDERS.get(task_name)
    if builder is not None:
        (objects, landmarks) = builder(task_spec)
    else:
        objects = []
        landmarks = {}
    entities = {'robot': robot, 'objects': objects, 'task_landmarks': landmarks}
    if realized_scene_snapshot is not None:
        from simulation.realized_scene import apply_realized_scene_to_entities
        return apply_realized_scene_to_entities(entities, realized_scene_snapshot) or entities
    return entities

def format_scene_entities_block(entities: dict) -> str:
    lines: list[str] = []
    robot = entities.get('robot', {})
    lines.append('robot:')
    for (key, val) in robot.items():
        lines.append(f'  {key}: {_fmt_value(val)}')
    objects = entities.get('objects', [])
    lines.append('objects:')
    for obj in objects:
        items = list(obj.items())
        if items:
            (first_key, first_val) = items[0]
            lines.append(f'  - {first_key}: {_fmt_value(first_val)}')
            for (key, val) in items[1:]:
                lines.append(f'    {key}: {_fmt_value(val)}')
    landmarks = entities.get('task_landmarks', {})
    if landmarks:
        lines.append('task_landmarks:')
        for (key, val) in landmarks.items():
            lines.append(f'  {key}: {_fmt_value(val)}')
    return '\n'.join(lines)

def _fmt_value(val: Any) -> str:
    if isinstance(val, list):
        return '[' + ', '.join((_fmt_scalar(v) for v in val)) + ']'
    if isinstance(val, bool):
        return 'true' if val else 'false'
    if isinstance(val, float):
        return _fmt_scalar(val)
    if isinstance(val, int):
        return str(val)
    if val is None:
        return 'null'
    return str(val)

def _fmt_scalar(v: Any) -> str:
    if isinstance(v, float):
        s = f'{v:.4f}'.rstrip('0').rstrip('.')
        return s if s else '0'
    return str(v)
if __name__ == '__main__':
    import sys
    from pathlib import Path as _Path
    _repo_root = str(_Path(__file__).resolve().parent.parent)
    if _repo_root not in sys.path:
        sys.path.insert(0, _repo_root)
    try:
        from scripts.task_configs import TASK_CONFIGS, SIM_CONFIGS
        from evaluation.task_spec import TaskSpec
    except ImportError as exc:
        print(f'[scene_info smoke-test] Import error: {exc}', file=sys.stderr)
        print('Make sure you run this from the repository root:', file=sys.stderr)
        print('  conda run -n robot-skill-synthesis python simulation/scene_info.py', file=sys.stderr)
        sys.exit(1)
    TASKS = ['push_to_goal', 'peg_insert', 'peg_channel', 'door_push', 'grasp_place', 'obstacle_reach']
    for task_name in TASKS:
        print(f"\n{'=' * 60}")
        print(f'Task: {task_name}')
        print('=' * 60)
        task_cfg = TASK_CONFIGS[task_name]
        task_spec = TaskSpec(**task_cfg['task_spec'])
        sim_config = SIM_CONFIGS[task_name]
        entities = get_scene_entities(task_name, task_spec, sim_config)
        block = format_scene_entities_block(entities)
        print('## Scene Entities')
        print(block)
