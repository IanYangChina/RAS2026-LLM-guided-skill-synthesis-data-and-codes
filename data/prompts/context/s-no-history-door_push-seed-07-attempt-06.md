## Search State

- **Seed**: 7
- **Iteration**: 7 / 15

## Optimisation Objective

Your goal is to **maximise task_score first, then composite score Q**:

> **Primary objective: task_score** — the fraction of episodes where the robot successfully completes the task. This is the most important metric. **Never propose a simpler or shorter skill if it reduces task_score.**

> **Q = fitness_score + termination_fidelity − complexity_penalty**

- `fitness_score`: shaped task reward (includes phase progress for contact-rich tasks)
- `termination_fidelity`: fraction of phases that terminated by designed condition (not timeout)
- `complexity_penalty`: cost for over-parameterised or over-phased designs

**Warning**: Do not reduce phases or parameters to lower complexity if doing so reduces task_score. Structure complexity is only penalised when it adds no performance gain.

# Proposal Context

## Task Specification

- Task name: door_push
- Frozen realised-scene SHA-256: `82ce57ad272540c243cfe7c86f1faba3a732bddf0a834ea70613e69de7a6ff57`
- Frozen initial hinge angle: 0.044 rad
- target_hinge_angle: 0.524 rad (task success = realised hinge-angle delta ratio; not TCP proximity)
- Goal tolerance: 0.05 m
- Expressivity sigma: 0.15 m
- Expressivity threshold: 0.3
- Force limit: 30.0 N
- Robot initial TCP position: (0.1, 0.4, 0.35)
- Primary evaluation target: **hinge angle delta ratio (realised hinge motion / target_hinge_angle)**

## Scene Entities

robot:
  model: panda_full
  tcp_site: attachment_site
  gripper: null
  tcp_initial_world: [0.1, 0.4, 0.35]
objects:
  - name: door_panel
    role: fixture
    dynamics: hinged
    geometry: box
    dimensions_m: [0.4, 0.02, 0.7]
    hinge_axis: Z
    hinge_joint_name: door_hinge
  - name: door_handle
    role: grasp_site
    dynamics: hinged_with_panel
    geometry: site
    body_frame_offset_m: [-0.4, -0.02, 0.35]
  - name: door_frame
    role: fixture
    dynamics: static
    geometry: box
task_landmarks:
  frozen_fixture_position: [0.5, 0.2, 0]
  frozen_initial_hinge_angle_rad: 0.0437
  frozen_fixtures: {'door_panel': [0.5, 0.2, 0.0]}
  door_hinge_axis: [0, 0, 1]
  goal_tolerance_m: 0.05
  force_limit_n: 30
  force_scale_n: 5
  target_hinge_angle_rad: 0.524
  realized_scene_sha256: 82ce57ad272540c243cfe7c86f1faba3a732bddf0a834ea70613e69de7a6ff57

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 1.000, which indicates the subtask decomposition is already effective.
> Preserve the current subtask decomposition unless the evidence shows a subtask change is necessary. Prefer refining phases, parameters, control modes, or termination conditions first.
> Unnecessary subtask redesign when performance is already high often causes regression.

## Subtask Layer

**Mode**: free (you define subtask targets; use `subtasks:` block in your YAML)

Define subtasks in a `subtasks:` block **before** `phases:`. Each subtask specifies an intermediate optimisation target.

**Required fields** — always include both, never omit:
- `anchor` (**required**): fixture | goal | object | world
- `target_entity` (**required**): hinge | object | tcp

Subtask anchors are separate from phase `target.anchor` vocabulary: subtasks use `world | object | goal | fixture`, while phase targets use `world | task_goal | task_object | fixture | body | site | current_tcp`.

Optional fields:
- `metric`: contact | distance | goal_progress | hinge_angle (default: distance)
- `offset`: [x, y, z] in metres relative to anchor (default: [0, 0, 0])
- `param_offset_key`: CMA-ES parameter added to offset at runtime (optional)
- `weight`: scoring weight [0.1, 1.0] (default: 1.0)

**Anchor resolution for this task** — choose anchor so the resolved position is meaningful:
| Anchor | Resolves to | Best used for |
|--------|-------------|---------------|
| `world` | absolute world-frame coordinate | fixed reference points not tied to objects |
| `object` | offset from object initial position | approach/contact targets near object |
| `goal` | offset from task goal position | final destination targets |
| `fixture` | offset from fixture pose (0.5, 0.2, 0.0) | approach/contact targets near fixture |

Annotate each phase with `subtask_id: <id>` to bind it to a subtask.
Only the **last phase** bound to a given subtask contributes to subtask scoring.

Example (two subtasks — one near object start, one at goal):
```yaml
subtasks:
  - id: reach_pre_contact
    anchor: object         # resolved to object initial position (see table above)
    target_entity: tcp     # score TCP distance to this target
    metric: distance
    offset: [0.0, 0.0, 0.10]  # 10 cm above object start position
    weight: 0.3
  - id: reach_goal
    anchor: goal           # resolved to task goal position (see table above)
    target_entity: tcp
    metric: distance
    offset: [0.0, 0.0, 0.0]
    weight: 0.7
phases:
  - id: approach_1
    type: approach
    subtask_id: reach_pre_contact
    ...
  - id: push_1
    type: push
    subtask_id: reach_goal
    ...
```

## Current Skill (Q=0.826) — your mutation base

```yaml
skill: door_push
dsl_version: 2
subtasks:
- id: reach_handle
  anchor: fixture
  offset:
  - -0.4
  - -0.02
  - 0.35
  weight: 0.3
- id: open_door
  anchor: fixture
  target_entity: hinge
  metric: hinge_angle
  weight: 0.7
phases:
- id: approach_handle
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: fixture
    entity: door_panel
    offset:
    - -0.4
    - -0.02
    - 0.35
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.15
      default: 0.06
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_handle
- id: push_door
  type: push
  generator: impedance_motion
  control: admittance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.2
      axis: world_y
      mode: add_to_offset
      sign: negative
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.1
      - 0.3
      default: 0.2
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: contact_maintained
    when: during_phase
    predicate: contact_detected
    threshold: 1.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.005
    - 0.0
  subtask_id: open_door

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_handle** (`approach`)
  - target: source=yaml, anchor=fixture, entity=door_panel, offset=[-0.4, -0.02, 0.35], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
- **push_door** (`push`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_y, distance=0.2, mode=add_to_offset, sign=negative}, tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=contact_maintained, when=during_phase, predicate=contact_detected, on_failure=retry, threshold=1.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.005, 0.0]

## Design Metrics

- **Composite score**: 0.826
- **task_score** (E): 0.976
- **fitness_score**: 0.976  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.150

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_handle | 1.00 | 1.00 | 0.1996 |
| push_door | 0.00 | 1.00 | 0.1679 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_handle | approach | 1.00 / step_budget | (0.100, 0.399, 0.350)→(0.100, 0.200, 0.349) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 2.333 | 12.563 | 33.208 |
| push_door | push | 0.00 / step_budget | (0.100, 0.200, 0.349)→(0.097, 0.046, 0.416) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 3.333 | 11.966 | 36.839 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- hinge_angle_ratio: 1.000
- arc_quality: 0.500

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 1.000
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.850
- **K-run variance**: 0.0011
- **Stagnated**: yes
  → Parameter optimiser converged to local optimum; structural change likely needed
- **Stop reason**: tolfun
- **Mean generations**: 8.7
- **Final σ (mean)**: 0.308


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `2fa9c04e562df03eff32cc7f63abe386d265bbd85d42dcee2df7f90a42e2de0a`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"hinge_delta_deg":10.0,"object_xy_delta":[0.0,0.0]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `fb31b2d7951f101afe3533d0babe40d387e4396f53837e61e543f2cfc46b7e19`; realized-scene SHA-256: `82ce57ad272540c243cfe7c86f1faba3a732bddf0a834ea70613e69de7a6ff57`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"fixture","value":[0.5,0.2,0.0]}],"axes":[{"name":"door_hinge_axis","value":[0.0,0.0,1.0]}],"door":{"hinge_axis":[0.0,0.0,1.0],"initial_hinge_angle":0.04367,"panel":{"name":"door_panel","orientation":[0.99976,0.0,0.0,0.02183],"position":[0.5,0.2,0.0]},"target_hinge_angle":0.524},"fixture_states":[],"fixtures":[{"name":"door_panel","orientation":[0.99976,0.0,0.0,0.02183],"position":[0.5,0.2,0.0]}],"limits":[{"name":"goal_tolerance_m","value":0.05},{"name":"force_limit_n","value":30.0},{"name":"force_scale_n","value":5.0},{"name":"target_hinge_angle_rad","value":0.524}],"object_starts":[],"obstacles":[],"targets":[],"task_name":"door_push"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.91111,"average_solve_count":90.0,"average_success_count":90.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_handle.speed":0.09126,"push_door.push_distance":0.21021,"push_door.push_speed":0.08655},"optimized_scores":{"best_composite_score":0.85,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link7","contact_count":680.0,"contact_point_centroid":[0.16297,0.0608,0.41561],"force_p95":25.45721,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":36.93978,"mean_force":14.08017,"phase_index":1.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.09785,0.1181,0.38827]},{"body_a":"door_panel","body_b":"link7","contact_count":25.0,"contact_point_centroid":[0.16531,0.14857,0.37308],"force_p95":21.96675,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":26.84294,"mean_force":16.70653,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.10014,0.20597,0.34901]},{"body_a":"door_panel","body_b":"link6","contact_count":80.0,"contact_point_centroid":[0.10175,0.16536,0.4548],"force_p95":19.70594,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":22.45318,"mean_force":10.91807,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.10004,0.23558,0.3487]},{"body_a":"world","body_b":"door_panel","contact_count":412.0,"contact_point_centroid":[0.30104,0.17819,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.0999,0.29866,0.34841]},{"body_a":"world","body_b":"door_panel","contact_count":884.0,"contact_point_centroid":[0.31921,0.11617,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.09801,0.11932,0.388]}],"total_contact_groups":5},"final_pose_error":0.0859,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.09538,0.03802,0.41984],"hinge_angle":0.56807,"initial_hinge_angle":0.04367,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.04367,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":36.93978,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":436.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":15.30495,"phase_name":"approach_handle","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":517.0,"raw_peak_contact_force":26.84294,"subtask_id":"reach_handle","tcp_end":[0.10017,0.19973,0.34911],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.41449,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":35.89863,"phase_name":"push_door","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1564.0,"raw_peak_contact_force":36.93978,"subtask_id":"open_door","tcp_end":[0.09538,0.03802,0.41984],"tcp_start":[0.10017,0.19973,0.34911],"tcp_to_object_dist_end":0.43221,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `2fe1c8aab50c64fd16f940100e2036790f2ea8f75271c649e6989441e8f9191e`; realized-scene SHA-256: `03ad88d640dcd23384857b752dfa12af63a722a6c6b9379a358f8168d1c71e09`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"fixture","value":[0.5,0.2,0.0]}],"axes":[{"name":"door_hinge_axis","value":[0.0,0.0,1.0]}],"door":{"hinge_axis":[0.0,0.0,1.0],"initial_hinge_angle":-0.0604,"panel":{"name":"door_panel","orientation":[0.99954,0.0,0.0,-0.03019],"position":[0.5,0.2,0.0]},"target_hinge_angle":0.524},"fixture_states":[],"fixtures":[{"name":"door_panel","orientation":[0.99954,0.0,0.0,-0.03019],"position":[0.5,0.2,0.0]}],"limits":[{"name":"goal_tolerance_m","value":0.05},{"name":"force_limit_n","value":30.0},{"name":"force_scale_n","value":5.0},{"name":"target_hinge_angle_rad","value":0.524}],"object_starts":[],"obstacles":[],"targets":[],"task_name":"door_push"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.66667,"average_solve_count":84.0,"average_success_count":84.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_handle.speed":0.11675,"push_door.push_distance":0.19987,"push_door.push_speed":0.05899},"optimized_scores":{"best_composite_score":0.85,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link7","contact_count":25.0,"contact_point_centroid":[0.16535,0.14891,0.37351],"force_p95":28.99227,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":35.30447,"mean_force":18.21754,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.10013,0.2062,0.34942]},{"body_a":"door_panel","body_b":"link7","contact_count":612.0,"contact_point_centroid":[0.16422,0.07994,0.40473],"force_p95":22.76645,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":29.32127,"mean_force":13.42002,"phase_index":1.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.09888,0.13717,0.37856]},{"body_a":"door_panel","body_b":"link6","contact_count":175.0,"contact_point_centroid":[0.10102,0.18517,0.45609],"force_p95":20.49645,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":23.08418,"mean_force":10.72481,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.0999,0.25955,0.34871]},{"body_a":"world","body_b":"door_panel","contact_count":408.0,"contact_point_centroid":[0.30044,0.19114,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.09985,0.30237,0.34854]},{"body_a":"world","body_b":"door_panel","contact_count":940.0,"contact_point_centroid":[0.31562,0.12332,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.09888,0.13605,0.37879]}],"total_contact_groups":5},"final_pose_error":0.1059,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.09577,0.08552,0.41141],"hinge_angle":0.46939,"initial_hinge_angle":-0.0604,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":-0.0604,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":35.30447,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":428.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":15.44425,"phase_name":"approach_handle","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":608.0,"raw_peak_contact_force":35.30447,"subtask_id":"reach_handle","tcp_end":[0.10017,0.19961,0.34948],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.41474,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"push_door","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1552.0,"raw_peak_contact_force":29.32127,"subtask_id":"open_door","tcp_end":[0.09577,0.08552,0.41141],"tcp_start":[0.10017,0.19961,0.34948],"tcp_to_object_dist_end":0.43098,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `356d1c9659b48b76a1cff255b134bf18d0729848f67621b991467785bdaaef44`; realized-scene SHA-256: `8483aeff51d0063ec1cf7a724dac4352cd76049b8e216b9602c279ab004268b5`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"fixture","value":[0.5,0.2,0.0]}],"axes":[{"name":"door_hinge_axis","value":[0.0,0.0,1.0]}],"door":{"hinge_axis":[0.0,0.0,1.0],"initial_hinge_angle":0.12924,"panel":{"name":"door_panel","orientation":[0.99791,0.0,0.0,0.06458],"position":[0.5,0.2,0.0]},"target_hinge_angle":0.524},"fixture_states":[],"fixtures":[{"name":"door_panel","orientation":[0.99791,0.0,0.0,0.06458],"position":[0.5,0.2,0.0]}],"limits":[{"name":"goal_tolerance_m","value":0.05},{"name":"force_limit_n","value":30.0},{"name":"force_scale_n","value":5.0},{"name":"target_hinge_angle_rad","value":0.524}],"object_starts":[],"obstacles":[],"targets":[],"task_name":"door_push"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":5.15584,"average_solve_count":77.0,"average_success_count":77.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_handle.speed":0.12014,"push_door.push_distance":0.26429,"push_door.push_speed":0.1},"optimized_scores":{"best_composite_score":0.77848,"best_fitness_score":0.92848,"best_task_score":0.92848},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link7","contact_count":705.0,"contact_point_centroid":[0.16367,0.05235,0.41809],"force_p95":24.64514,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":44.25535,"mean_force":14.08451,"phase_index":1.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.09795,0.10872,0.39084]},{"body_a":"door_panel","body_b":"link7","contact_count":28.0,"contact_point_centroid":[0.16538,0.15011,0.37345],"force_p95":29.20314,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":37.47593,"mean_force":18.74667,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.10021,0.20729,0.34935]},{"body_a":"door_panel","body_b":"link6","contact_count":14.0,"contact_point_centroid":[0.10368,0.14746,0.45378],"force_p95":11.96467,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":12.25453,"mean_force":3.27668,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.10018,0.2129,0.34925]},{"body_a":"world","body_b":"door_panel","contact_count":468.0,"contact_point_centroid":[0.30298,0.16423,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.0999,0.30648,0.34856]},{"body_a":"world","body_b":"door_panel","contact_count":912.0,"contact_point_centroid":[0.32029,0.11531,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.09826,0.11532,0.38726]}],"total_contact_groups":5},"final_pose_error":0.1023,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.09972,0.01357,0.41531],"hinge_angle":0.61576,"initial_hinge_angle":0.12924,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.12924,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":44.25535,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":426.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":6.93899,"phase_name":"approach_handle","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":510.0,"raw_peak_contact_force":37.47593,"subtask_id":"reach_handle","tcp_end":[0.10024,0.19957,0.34947],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.41474,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.00044,"phase_name":"push_door","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1617.0,"raw_peak_contact_force":44.25535,"subtask_id":"open_door","tcp_end":[0.09972,0.01357,0.41531],"tcp_start":[0.10024,0.19957,0.34947],"tcp_to_object_dist_end":0.42733,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```