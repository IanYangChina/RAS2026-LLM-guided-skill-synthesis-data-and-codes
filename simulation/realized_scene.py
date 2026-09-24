from __future__ import annotations
from dataclasses import dataclass, replace
import hashlib
import json
import math
from typing import Any, Mapping, TypeAlias
Vector3: TypeAlias = tuple[float, float, float]
Quaternion: TypeAlias = tuple[float, float, float, float]

def _vector3(value: Any) -> Vector3:
    values = tuple((float(v) for v in value))
    if len(values) != 3 or not all((math.isfinite(v) for v in values)):
        raise ValueError('scene coordinates must be three finite floats')
    return tuple((0.0 if v == 0.0 else v for v in values))

def _quaternion(value: Any | None) -> Quaternion | None:
    if value is None:
        return None
    values = tuple((float(v) for v in value))
    if len(values) != 4 or not all((math.isfinite(v) for v in values)):
        raise ValueError('scene orientations must be four finite floats')
    return tuple((0.0 if v == 0.0 else v for v in values))

@dataclass(frozen=True)
class ScenePose:
    name: str
    position: Vector3
    orientation: Quaternion | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, 'position', _vector3(self.position))
        object.__setattr__(self, 'orientation', _quaternion(self.orientation))

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {'name': self.name, 'position': list(self.position)}
        if self.orientation is not None:
            result['orientation'] = list(self.orientation)
        return result

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> 'ScenePose':
        return cls(str(value['name']), value['position'], value.get('orientation'))

@dataclass(frozen=True)
class NamedVector:
    name: str
    value: Vector3

    def __post_init__(self) -> None:
        object.__setattr__(self, 'value', _vector3(self.value))

    def to_dict(self) -> dict[str, Any]:
        return {'name': self.name, 'value': list(self.value)}

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> 'NamedVector':
        return cls(str(value['name']), value['value'])

@dataclass(frozen=True)
class NamedScalar:
    name: str
    value: float

    def __post_init__(self) -> None:
        value = float(self.value)
        if not math.isfinite(value):
            raise ValueError('scene scalar values must be finite')
        object.__setattr__(self, 'value', 0.0 if value == 0.0 else value)

    def to_dict(self) -> dict[str, Any]:
        return {'name': self.name, 'value': self.value}

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> 'NamedScalar':
        return cls(str(value['name']), value['value'])

@dataclass(frozen=True)
class FixtureState:
    name: str
    state: str

    def to_dict(self) -> dict[str, str]:
        return {'name': self.name, 'state': self.state}

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> 'FixtureState':
        return cls(str(value['name']), str(value['state']))

@dataclass(frozen=True)
class DoorState:
    panel: ScenePose
    hinge_axis: Vector3
    initial_hinge_angle: float
    target_hinge_angle: float | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, 'hinge_axis', _vector3(self.hinge_axis))
        object.__setattr__(self, 'initial_hinge_angle', float(self.initial_hinge_angle))
        if self.target_hinge_angle is not None:
            object.__setattr__(self, 'target_hinge_angle', float(self.target_hinge_angle))

    def to_dict(self) -> dict[str, Any]:
        result = {'panel': self.panel.to_dict(), 'hinge_axis': list(self.hinge_axis), 'initial_hinge_angle': self.initial_hinge_angle}
        if self.target_hinge_angle is not None:
            result['target_hinge_angle'] = self.target_hinge_angle
        return result

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> 'DoorState':
        return cls(panel=ScenePose.from_dict(value['panel']), hinge_axis=value['hinge_axis'], initial_hinge_angle=value['initial_hinge_angle'], target_hinge_angle=value.get('target_hinge_angle'))

@dataclass(frozen=True)
class RealizedSceneSnapshot:
    task_name: str
    object_starts: tuple[ScenePose, ...] = ()
    targets: tuple[ScenePose, ...] = ()
    obstacles: tuple[ScenePose, ...] = ()
    fixtures: tuple[ScenePose, ...] = ()
    fixture_states: tuple[FixtureState, ...] = ()
    axes: tuple[NamedVector, ...] = ()
    limits: tuple[NamedScalar, ...] = ()
    anchors: tuple[NamedVector, ...] = ()
    door: DoorState | None = None
    schema_version: str = 'skill-synthesis-realized-scene-schema-v1'

    def __post_init__(self) -> None:
        for name in ('object_starts', 'targets', 'obstacles', 'fixtures', 'fixture_states', 'axes', 'limits', 'anchors'):
            object.__setattr__(self, name, tuple(getattr(self, name)))

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {'schema_version': self.schema_version, 'task_name': self.task_name, 'object_starts': [item.to_dict() for item in self.object_starts], 'targets': [item.to_dict() for item in self.targets], 'obstacles': [item.to_dict() for item in self.obstacles], 'fixtures': [item.to_dict() for item in self.fixtures], 'fixture_states': [item.to_dict() for item in self.fixture_states], 'axes': [item.to_dict() for item in self.axes], 'limits': [item.to_dict() for item in self.limits], 'anchors': [item.to_dict() for item in self.anchors]}
        if self.door is not None:
            result['door'] = self.door.to_dict()
        return result

    def canonical_json(self) -> str:
        return json.dumps(self.to_dict(), sort_keys=True, separators=(',', ':'), allow_nan=False)

    @property
    def sha256(self) -> str:
        return hashlib.sha256(self.canonical_json().encode('utf-8')).hexdigest()

    def position(self, category: str, name: str) -> Vector3 | None:
        for pose in getattr(self, category):
            if pose.name == name:
                return pose.position
        return None

    def first_position(self, category: str) -> Vector3 | None:
        poses = getattr(self, category)
        return poses[0].position if poses else None

    def anchor(self, name: str) -> Vector3 | None:
        for item in self.anchors:
            if item.name == name:
                return item.value
        return None

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> 'RealizedSceneSnapshot':
        return cls(task_name=str(value['task_name']), object_starts=tuple((ScenePose.from_dict(item) for item in value.get('object_starts', ()))), targets=tuple((ScenePose.from_dict(item) for item in value.get('targets', ()))), obstacles=tuple((ScenePose.from_dict(item) for item in value.get('obstacles', ()))), fixtures=tuple((ScenePose.from_dict(item) for item in value.get('fixtures', ()))), fixture_states=tuple((FixtureState.from_dict(item) for item in value.get('fixture_states', ()))), axes=tuple((NamedVector.from_dict(item) for item in value.get('axes', ()))), limits=tuple((NamedScalar.from_dict(item) for item in value.get('limits', ()))), anchors=tuple((NamedVector.from_dict(item) for item in value.get('anchors', ()))), door=DoorState.from_dict(value['door']) if value.get('door') else None, schema_version=str(value.get('schema_version', 'skill-synthesis-realized-scene-schema-v1')))

def coerce_realized_scene(value: RealizedSceneSnapshot | Mapping[str, Any] | None) -> RealizedSceneSnapshot | None:
    if value is None or isinstance(value, RealizedSceneSnapshot):
        return value
    return RealizedSceneSnapshot.from_dict(value)
REALIZED_SCENE_SCHEMA_VERSION = 'skill-synthesis-realized-scene-schema-v1'

def canonical_realized_scene_json(snapshot: RealizedSceneSnapshot | Mapping[str, Any]) -> str:
    return coerce_realized_scene(snapshot).canonical_json()

def realized_scene_snapshot_hash(snapshot: RealizedSceneSnapshot | Mapping[str, Any]) -> str:
    return coerce_realized_scene(snapshot).sha256

@dataclass(frozen=True)
class RealizedSceneConfiguration:
    config_index: int
    seed: int
    snapshot: RealizedSceneSnapshot
    backend_state_json: str
    schema_version: str = 'skill-synthesis-randomized-config-v1'

    def __post_init__(self) -> None:
        state = json.loads(self.backend_state_json)
        canonical_state = json.dumps(state, sort_keys=True, separators=(',', ':'), allow_nan=False)
        object.__setattr__(self, 'backend_state_json', canonical_state)

    @property
    def backend_state(self) -> dict[str, Any]:
        return json.loads(self.backend_state_json)

    def _payload(self) -> dict[str, Any]:
        return {'schema_version': self.schema_version, 'config_index': self.config_index, 'seed': self.seed, 'realized_scene': self.snapshot.to_dict(), 'realized_scene_sha256': self.snapshot.sha256, 'backend_state': self.backend_state}

    @property
    def sha256(self) -> str:
        canonical = json.dumps(self._payload(), sort_keys=True, separators=(',', ':'), allow_nan=False)
        return hashlib.sha256(canonical.encode('utf-8')).hexdigest()

    def to_dict(self) -> dict[str, Any]:
        return {**self._payload(), 'configuration_sha256': self.sha256}

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> 'RealizedSceneConfiguration':
        snapshot = coerce_realized_scene(value['realized_scene'])
        if snapshot is None:
            raise ValueError('randomized configuration lacks a realized scene')
        configuration = cls(config_index=int(value['config_index']), seed=int(value['seed']), snapshot=snapshot, backend_state_json=json.dumps(value['backend_state']), schema_version=str(value.get('schema_version', 'skill-synthesis-randomized-config-v1')))
        if value.get('realized_scene_sha256') != snapshot.sha256:
            raise ValueError('randomized configuration realized-scene hash mismatch')
        if value.get('configuration_sha256') != configuration.sha256:
            raise ValueError('randomized configuration hash mismatch')
        return configuration

@dataclass(frozen=True)
class RealizedSceneConfigBank:
    task_name: str
    outer_seed: int
    configurations: tuple[RealizedSceneConfiguration, ...]
    schema_version: str = 'skill-synthesis-randomized-config-bank-v1'

    def __post_init__(self) -> None:
        object.__setattr__(self, 'configurations', tuple(self.configurations))
        if not self.configurations:
            raise ValueError('randomized configuration bank must not be empty')
        for (index, configuration) in enumerate(self.configurations):
            if configuration.config_index != index:
                raise ValueError('randomized configuration bank indices must be contiguous')
            if configuration.snapshot.task_name != self.task_name:
                raise ValueError('randomized configuration bank task mismatch')

    def _payload(self) -> dict[str, Any]:
        return {'schema_version': self.schema_version, 'task_name': self.task_name, 'outer_seed': self.outer_seed, 'k_runs': len(self.configurations), 'configurations': [configuration.to_dict() for configuration in self.configurations]}

    @property
    def sha256(self) -> str:
        return hashlib.sha256(self.canonical_json().encode('utf-8')).hexdigest()

    def to_dict(self) -> dict[str, Any]:
        return {**self._payload(), 'configuration_bank_sha256': self.sha256}

    def canonical_json(self) -> str:
        return json.dumps(self._payload(), sort_keys=True, separators=(',', ':'), allow_nan=False)

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> 'RealizedSceneConfigBank':
        bank = cls(task_name=str(value['task_name']), outer_seed=int(value['outer_seed']), configurations=tuple((RealizedSceneConfiguration.from_dict(item) for item in value['configurations'])), schema_version=str(value.get('schema_version', 'skill-synthesis-randomized-config-bank-v1')))
        if int(value.get('k_runs', -1)) != len(bank.configurations):
            raise ValueError('randomized configuration bank size mismatch')
        if value.get('configuration_bank_sha256') != bank.sha256:
            raise ValueError('randomized configuration bank hash mismatch')
        return bank

def _jsonable_randomisation_state(backend: Any) -> dict[str, Any]:
    body_deltas = getattr(backend, '_rand_frozen_body_deltas', None) or {}
    qpos_delta = getattr(backend, '_rand_frozen_qpos_delta', None)
    return {'body_deltas': {str(body_id): [float(component) for component in delta] for (body_id, delta) in sorted(body_deltas.items(), key=lambda item: int(item[0]))}, 'qpos_delta': [float(component) for component in qpos_delta] if qpos_delta is not None else None, 'scene_frozen': bool(getattr(backend, '_rand_scene_frozen', False))}

def activate_realized_scene_configuration(backend: Any, configuration: RealizedSceneConfiguration) -> None:
    import numpy as np
    state = configuration.backend_state
    backend._rand_frozen_body_deltas = {int(body_id): tuple((float(component) for component in delta)) for (body_id, delta) in state['body_deltas'].items()}
    qpos_delta = state.get('qpos_delta')
    backend._rand_frozen_qpos_delta = np.asarray(qpos_delta, dtype=float) if qpos_delta is not None else None
    backend._rand_scene_frozen = bool(state.get('scene_frozen', True))
    snapshots = getattr(backend, '_realized_scene_snapshots', None)
    if isinstance(snapshots, dict):
        snapshots.clear()

def materialize_realized_scene_config_bank(backend: Any, task_name: str, task_spec: Any, *, outer_seed: int, k_runs: int) -> RealizedSceneConfigBank:
    import numpy as np
    if k_runs < 1:
        raise ValueError('k_runs must be positive')
    configurations: list[RealizedSceneConfiguration] = []
    for index in range(k_runs):
        config_seed = int(outer_seed) + index
        if hasattr(backend, '_rand_config'):
            backend._rand_rng = np.random.default_rng(config_seed % 2 ** 32)
        for attr in ('_rand_frozen_body_deltas', '_rand_frozen_qpos_delta'):
            if hasattr(backend, attr):
                delattr(backend, attr)
        backend.unfreeze_scene_randomisation()
        backend.freeze_scene_randomisation()
        snapshot = backend.realized_scene_snapshot(task_name, task_spec)
        state_json = json.dumps(_jsonable_randomisation_state(backend), sort_keys=True, separators=(',', ':'), allow_nan=False)
        configurations.append(RealizedSceneConfiguration(config_index=index, seed=config_seed, snapshot=snapshot, backend_state_json=state_json))
    bank = RealizedSceneConfigBank(task_name, int(outer_seed), tuple(configurations))
    randomisation_enabled = bool((getattr(backend, '_rand_config', None) or {}).get('enabled', False))
    if randomisation_enabled and len({item.snapshot.sha256 for item in configurations}) != k_runs:
        raise RuntimeError('randomized configuration bank contains duplicate realized scenes')
    activate_realized_scene_configuration(backend, bank.configurations[0])
    return bank

def _position(value: Any) -> Vector3 | None:
    if value is None:
        return None
    try:
        return _vector3(value)
    except (TypeError, ValueError):
        return None

def _number(value: Any) -> float | None:
    try:
        value = float(value)
    except (TypeError, ValueError):
        return None
    return value if math.isfinite(value) else None

def _first_position(state: Mapping[str, Any], *keys: str) -> Vector3 | None:
    for key in keys:
        value = _position(state.get(key))
        if value is not None:
            return value
    return None

def _first_number(state: Mapping[str, Any], *keys: str) -> float | None:
    for key in keys:
        value = _number(state.get(key))
        if value is not None:
            return value
    return None

def _scene_poses(state: Mapping[str, Any], category: str) -> list[ScenePose]:
    value = state.get(category)
    if not isinstance(value, (list, tuple)):
        return []
    poses: list[ScenePose] = []
    for item in value:
        if not isinstance(item, Mapping):
            continue
        try:
            poses.append(ScenePose.from_dict(item))
        except (KeyError, TypeError, ValueError):
            continue
    return poses

def build_realized_scene_snapshot(task_name: str, task_spec: Any, realised_task_state: Mapping[str, Any]) -> RealizedSceneSnapshot:
    state = dict(realised_task_state)
    for key in ('realized_scene_snapshot', 'realised_scene_snapshot'):
        payload = state.get(key)
        if isinstance(payload, Mapping):
            try:
                return RealizedSceneSnapshot.from_dict(payload)
            except (KeyError, TypeError, ValueError):
                pass
    task = str(task_name).lower()
    object_start = _first_position(state, 'actual_object_initial_position', 'realised_object_initial_position', 'object_initial_position', 'object_initial_pose')
    target_keys = (('socket_entry_position', 'socket_hole_position') if task == 'peg_insert' else ()) + ('goal_marker_position', 'actual_goal_object_position', 'actual_place_goal_position', 'actual_goal_position', 'realised_goal_position', 'goal_object_position', 'place_goal_position', 'goal_position')
    if task == 'peg_channel':
        target_keys = ('goal_marker_position', 'actual_goal_object_position')
    target = _first_position(state, *target_keys)
    socket = _first_position(state, 'socket_position', 'realised_fixture_position', 'actual_fixture_position', 'fixture_position')
    initial_hinge = _first_number(state, 'realised_initial_hinge_angle', 'initial_hinge_angle', 'hinge_angle_initial', 'hinge_initial_angle')
    door_panel = _first_position(state, 'realised_door_panel_position', 'actual_door_panel_position', 'door_panel_position')
    axes: list[NamedVector] = []
    axis = _position(getattr(task_spec, 'channel_axis', None))
    if axis is not None:
        axes.append(NamedVector('channel_axis', axis))
    limits: list[NamedScalar] = []
    for (name, value) in (('channel_length_m', getattr(task_spec, 'channel_length', None)), ('hole_depth_m', getattr(task_spec, 'hole_depth', None)), ('goal_tolerance_m', getattr(task_spec, 'goal_tolerance', None)), ('force_limit_n', getattr(task_spec, 'force_limit', None))):
        number = _number(value)
        if number is not None:
            limits.append(NamedScalar(name, number))
    object_starts = _scene_poses(state, 'object_starts')
    targets = _scene_poses(state, 'targets')
    obstacles = _scene_poses(state, 'obstacles')
    fixtures = _scene_poses(state, 'fixtures')
    if not object_starts and object_start is not None:
        object_starts.append(ScenePose('manipulated_object', object_start))
    if not targets and target is not None:
        targets.append(ScenePose('socket_entry' if task == 'peg_insert' else 'task_target', target))
    obstacle = _first_position(state, 'actual_obstacle_position', 'realised_obstacle_position', 'obstacle_position')
    if obstacle is not None:
        obstacles.append(ScenePose('task_obstacle', obstacle))
    door = None
    anchors: list[NamedVector] = []
    if socket is not None and (not any((pose.name == 'peg_socket' for pose in fixtures))):
        fixtures.append(ScenePose('peg_socket', socket))
    channel = _first_position(state, 'channel_position', 'realised_channel_position')
    if channel is not None and (not any((pose.name == 'channel_structure' for pose in fixtures))):
        fixtures.append(ScenePose('channel_structure', channel))
    for (name, key) in (('channel_left_wall', 'channel_left_wall_position'), ('channel_right_wall', 'channel_right_wall_position')):
        position = _first_position(state, key)
        if position is not None and (not any((pose.name == name for pose in fixtures))):
            fixtures.append(ScenePose(name, position))
    if task in {'door_push', 'door_pull'}:
        door = DoorState(panel=ScenePose('door_panel', door_panel or (0.0, 0.0, 0.0)), hinge_axis=(0.0, 0.0, 1.0), initial_hinge_angle=initial_hinge or 0.0, target_hinge_angle=_number(getattr(task_spec, 'target_hinge_angle', None)))
        if not any((pose.name == 'door_panel' for pose in fixtures)):
            fixtures.append(door.panel)
        anchors.append(NamedVector('fixture', door.panel.position))
    if task == 'peg_insert':
        socket_entry = _first_position(state, 'socket_entry_position', 'socket_hole_position')
        if socket_entry is not None and (not targets):
            targets.append(ScenePose('socket_entry', socket_entry))
    if task == 'peg_channel' and (not targets) and (object_start is not None):
        axis = next((item.value for item in axes if item.name == 'channel_axis'), None)
        length = next((item.value for item in limits if item.name == 'channel_length_m'), None)
        if axis is not None and length is not None:
            targets.append(ScenePose('channel_exit', tuple((object_start[index] + axis[index] * length for index in range(3)))))
    fixture = next((pose.position for pose in fixtures if pose.name == 'peg_socket'), None)
    if fixture is None and fixtures:
        fixture = fixtures[0].position
    if fixture is not None and (not any((item.name == 'fixture' for item in anchors))):
        anchors.append(NamedVector('fixture', fixture))
    if object_starts and (not any((item.name == 'object' for item in anchors))):
        anchors.append(NamedVector('object', object_starts[0].position))
    if task == 'peg_insert':
        peg = object_starts[0].position if object_starts else None
        if peg is not None and (not any((item.name == 'task_object' for item in anchors))):
            anchors.append(NamedVector('task_object', peg))
        if fixture is not None:
            for name in ('target', 'socket'):
                if not any((item.name == name for item in anchors)):
                    anchors.append(NamedVector(name, fixture))
    if task == 'peg_insert' and fixture is not None and (not any((item.name == 'goal' for item in anchors))):
        anchors.append(NamedVector('goal', fixture))
    elif targets and (not any((item.name == 'goal' for item in anchors))):
        anchors.append(NamedVector('goal', targets[0].position))
    return RealizedSceneSnapshot(task_name=task_name, object_starts=tuple(object_starts), targets=tuple(targets), obstacles=tuple(obstacles), fixtures=tuple(fixtures), fixture_states=(FixtureState('peg_socket', 'static_frozen'),) if any((pose.name == 'peg_socket' for pose in fixtures)) else (), axes=tuple(axes), limits=tuple(limits), anchors=tuple(anchors), door=door)

def _state_from_trace(trace: Any) -> Mapping[str, Any] | None:
    if isinstance(trace, Mapping):
        metadata = trace.get('metadata')
        containers = [trace, metadata] if isinstance(metadata, Mapping) else [trace]
    else:
        metadata = getattr(trace, 'metadata', None)
        containers = [metadata] if isinstance(metadata, Mapping) else []
    for container in containers:
        for key in ('realised_task_state', 'randomised_task_state', 'episode_task_state', 'task_state'):
            value = container.get(key)
            if isinstance(value, Mapping):
                merged = dict(value)
                for direct_key in ('actual_goal_position', 'realised_goal_position', 'actual_object_initial_position', 'realised_object_initial_position', 'realised_fixture_position', 'realised_door_panel_position', 'initial_hinge_angle', 'realised_initial_hinge_angle', 'actual_obstacle_position', 'realised_obstacle_position', 'socket_entry_position', 'channel_position', 'channel_left_wall_position', 'channel_right_wall_position', 'realized_scene_snapshot', 'realised_scene_snapshot'):
                    if direct_key in container:
                        merged[direct_key] = container[direct_key]
                return merged
    return None

def realized_scene_snapshot_from_evaluation(task_name: str, task_spec: Any, *, realized_scene_snapshot: RealizedSceneSnapshot | Mapping[str, Any] | None=None, randomised_task_state: Mapping[str, Any] | None=None, metrics: Any=None, traces: list[Any] | None=None, cma_diagnostics: Mapping[str, Any] | None=None) -> RealizedSceneSnapshot | None:
    snapshot = coerce_realized_scene(realized_scene_snapshot)
    if snapshot is not None:
        return snapshot
    candidates: list[Mapping[str, Any]] = []
    if isinstance(randomised_task_state, Mapping):
        candidates.append(randomised_task_state)
    if metrics is not None:
        value = getattr(metrics, 'randomised_task_state', None)
        if isinstance(value, Mapping):
            candidates.append(value)
        for value in getattr(metrics, 'episode_task_state', []) or []:
            if isinstance(value, Mapping):
                candidates.append(value)
    if isinstance(cma_diagnostics, Mapping):
        posthoc = cma_diagnostics.get('posthoc_diagnostics', cma_diagnostics)
        if isinstance(posthoc, Mapping):
            for result in posthoc.get('randomised_config_results', []) or []:
                if isinstance(result, Mapping):
                    value = result.get('representative_task_state') or result.get('randomised_task_state')
                    if isinstance(value, Mapping):
                        candidates.append(value)
    for trace in traces or []:
        value = _state_from_trace(trace)
        if value is not None:
            candidates.append(value)
    for state in candidates:
        if state:
            return build_realized_scene_snapshot(task_name, task_spec, state)
    return None

def apply_realized_scene_to_task_spec(task_spec: Any, snapshot: RealizedSceneSnapshot | Mapping[str, Any] | None) -> Any:
    scene = coerce_realized_scene(snapshot)
    if scene is None or task_spec is None:
        return task_spec
    object_start = scene.position('object_starts', 'manipulated_object') or scene.first_position('object_starts')
    target = scene.position('targets', 'task_target') or scene.first_position('targets')
    socket = scene.position('fixtures', 'peg_socket')
    fixture = socket or scene.first_position('fixtures')
    fixture_anchor = scene.anchor('fixture')
    updates: dict[str, Any] = {}
    task = scene.task_name.lower()
    if object_start is not None:
        updates['object_initial_pose'] = object_start
    if target is not None:
        if task not in {'door_push', 'door_pull'}:
            updates['goal_object_position'] = target
        if task == 'grasp_place':
            updates['place_goal_position'] = target
    if socket is not None:
        updates['fixture_pose'] = socket
    elif fixture is not None:
        updates['fixture_pose'] = fixture
    elif fixture_anchor is not None:
        updates['fixture_pose'] = fixture_anchor
    if task == 'peg_insert' and fixture is not None:
        updates['goal_object_position'] = fixture
    obstacle = scene.first_position('obstacles')
    if obstacle is not None:
        updates['obstacle_position'] = obstacle
    for axis in scene.axes:
        if axis.name in {'channel_axis', 'insertion_axis'}:
            updates['channel_axis'] = axis.value
    for limit in scene.limits:
        field = {'channel_length_m': 'channel_length', 'hole_depth_m': 'hole_depth', 'goal_tolerance_m': 'goal_tolerance', 'force_limit_n': 'force_limit'}.get(limit.name)
        if field is not None:
            updates[field] = limit.value
    if scene.door is not None:
        updates['initial_hinge_angle'] = scene.door.initial_hinge_angle
    try:
        return replace(task_spec, **updates)
    except TypeError:
        return task_spec

def apply_realized_scene_to_entities(entities: Mapping[str, Any] | None, snapshot: RealizedSceneSnapshot | Mapping[str, Any] | None) -> dict[str, Any] | None:
    scene = coerce_realized_scene(snapshot)
    if scene is None:
        return json.loads(json.dumps(entities)) if entities is not None else None
    result = json.loads(json.dumps(entities)) if entities is not None else {'robot': {}, 'objects': [], 'task_landmarks': {}}
    original_landmarks = result.get('task_landmarks', {})
    if not isinstance(original_landmarks, Mapping):
        original_landmarks = {}
    landmarks: dict[str, Any] = {str(key): value for (key, value) in original_landmarks.items() if any((token in str(key).lower() for token in ('random', 'range', 'distribution')))}
    result['task_landmarks'] = landmarks
    object_start = scene.position('object_starts', 'manipulated_object') or scene.first_position('object_starts')
    target = scene.position('targets', 'task_target') or scene.first_position('targets')
    socket = scene.position('fixtures', 'peg_socket')
    fixture = socket or scene.first_position('fixtures')
    if object_start is not None:
        value = list(object_start)
        landmarks['frozen_object_start'] = value
    if target is not None:
        value = list(target)
        landmarks['frozen_task_target'] = value
    obstacle = scene.first_position('obstacles')
    if obstacle is not None:
        landmarks['frozen_obstacle_position'] = list(obstacle)
    if socket is not None:
        landmarks['frozen_socket_position'] = list(socket)
        landmarks['socket_state'] = 'static_frozen'
    elif fixture is not None:
        landmarks['frozen_fixture_position'] = list(fixture)
    if scene.door is not None:
        landmarks['frozen_initial_hinge_angle_rad'] = scene.door.initial_hinge_angle
    for (key, poses) in (('frozen_object_starts', scene.object_starts), ('frozen_targets', scene.targets), ('frozen_obstacles', scene.obstacles), ('frozen_fixtures', scene.fixtures)):
        if poses:
            landmarks[key] = {pose.name: list(pose.position) for pose in poses}
    for axis in scene.axes:
        landmarks[axis.name] = list(axis.value)
    for limit in scene.limits:
        landmarks[limit.name] = limit.value
    landmarks['realized_scene_sha256'] = scene.sha256
    return result
