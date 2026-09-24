## Search State

- **Seed**: 4
- **Iteration**: 9 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 8 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | time_limit | time_limit | 7 | 1.0900 | 1.00 | ❌ rejected |
| 7 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | time_limit | time_limit | 7 | 1.0900 | 1.00 | ❌ rejected |
| 6 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | time_limit | time_limit | 8 | 0.6230 | 0.86 | ❌ rejected |
| 5 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | time_limit | time_limit | 7 | 1.0900 | 1.00 | ❌ rejected |
| 4 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | time_limit | time_limit | 7 | 1.0900 | 1.00 | ❌ rejected |

**Proposal policy**: task_score is near-perfect (1.00). Preserve useful working parts and make only evidence-backed refinements. A HOLD is acceptable if you genuinely cannot find a better structure.

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
- Frozen realised-scene SHA-256: `93d761ce3dc4e78ce09d05c5eb184a7129267f8d2172dd2a5cd042d5ec0710b9`
- Frozen initial hinge angle: 0.155 rad
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
  frozen_initial_hinge_angle_rad: 0.1547
  frozen_fixtures: {'door_panel': [0.5, 0.2, 0.0]}
  door_hinge_axis: [0, 0, 1]
  goal_tolerance_m: 0.05
  force_limit_n: 30
  force_scale_n: 5
  target_hinge_angle_rad: 0.524
  realized_scene_sha256: 93d761ce3dc4e78ce09d05c5eb184a7129267f8d2172dd2a5cd042d5ec0710b9

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

## Current Skill (Q=1.090) — your mutation base

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
- id: push_door
  anchor: fixture
  target_entity: hinge
  metric: hinge_angle
  weight: 0.7
phases:
- id: approach_1
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: site
    entity: door_handle
    offset:
    - 0.0
    - 0.0
    - 0.1
    tolerance: 0.01
    orientation:
      mode: none
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_handle
- id: contact_1
  type: contact
  generator: linear_cartesian
  control: force_threshold_switch
  termination: force_exceeded
  target:
    source: yaml
    anchor: site
    entity: door_handle
    offset:
    - 0.0
    - 0.0
    - -0.005
    tolerance: 0.005
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: world_y
      tolerance: 0.05
  parameters:
    contact_force:
      type: scalar
      range:
      - 1.0
      - 20.0
      default: 10.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
  subtask_id: reach_handle
- id: push_1
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: time_limit
  target:
    source: yaml
    anchor: site
    entity: door_handle
    offset:
    - 0.0
    - 0.0
    - -0.005
    offset_along_axis:
      distance: 0.15
      axis: world_y
      mode: add_to_offset
      sign: negative
    tolerance: 0.02
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: world_y
      tolerance: 0.1
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.02
      - 0.3
      default: 0.15
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_max_time:
      type: scalar
      range:
      - 5.0
      - 20.0
      default: 10.0
      binds_to:
      - path: duration.max_time
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: door_progress_check
    when: after_phase
    predicate: hinge_delta_reached
    threshold: 0.5
    on_failure: retry
  retries:
    max_attempts: 1
    strategy: offset_target
    offset:
    - 0.0
    - -0.01
    - 0.0
  subtask_id: push_door
- id: retract_1
  type: retract
  generator: linear_cartesian
  control: position_control
  termination: time_limit
  target:
    source: yaml
    anchor: world
    offset:
    - 0.1
    - 0.4
    - 0.35
    tolerance: 0.05
    orientation:
      mode: none
  parameters:
    retract_max_time:
      type: scalar
      range:
      - 5.0
      - 20.0
      default: 10.0
      binds_to:
      - path: duration.max_time
        mode: replace
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=site, entity=door_handle, offset=[0.0, 0.0, 0.1], tolerance=0.01
  - orientation: mode=none
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
- **contact_1** (`contact`)
  - target: source=yaml, anchor=site, entity=door_handle, offset=[0.0, 0.0, -0.005], tolerance=0.005
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=world_y, tolerance=0.05
  - parameter_bindings:
    - contact_force: status=consumed; consumers=termination.force_threshold (replace)
- **push_1** (`push`)
  - target: source=yaml, anchor=site, entity=door_handle, offset=[0.0, 0.0, -0.005], offset_along_axis={axis=world_y, distance=0.15, mode=add_to_offset, sign=negative}, tolerance=0.02
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=world_y, tolerance=0.1
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_max_time: status=consumed; consumers=duration.max_time (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=door_progress_check, when=after_phase, predicate=hinge_delta_reached, on_failure=retry, threshold=0.5
  - retries: max_attempts=1, strategy=offset_target, offset=[0.0, -0.01, 0.0]
- **retract_1** (`retract`)
  - target: source=yaml, anchor=world, offset=[0.1, 0.4, 0.35], tolerance=0.05
  - orientation: mode=none
  - parameter_bindings:
    - retract_max_time: status=consumed; consumers=duration.max_time (replace)
    - speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: 1.090
- **task_score** (E): 1.000
- **fitness_score**: 1.000  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.500
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.410

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 0.33 | 1.00 | 0.2121 |
| contact_1 | 1.00 | 1.00 | 0.0024 |
| push_1 | 1.00 | 0.67 | 0.1793 |
| retract_1 | 1.00 | 0.00 | 0.0971 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 0.33 / step_budget | (0.100, 0.399, 0.350)→(0.103, 0.201, 0.426) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 4.667 | 5.303 | 26.066 |
| contact_1 | contact | 1.00 / force_exceeded | (0.103, 0.201, 0.426)→(0.103, 0.199, 0.425) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 2.333 | 59.276 | 67.749 |
| push_1 | push | 1.00 / time_limit | (0.103, 0.199, 0.425)→(0.119, 0.032, 0.384) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 0.67 / 1.667 | 0.063 | 869.699 |
| retract_1 | retract | 1.00 / time_limit | (0.119, 0.032, 0.384)→(0.117, 0.125, 0.377) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 0.00 / 0.000 | 0.000 | 242.878 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- hinge_angle_ratio: 1.000
- arc_quality: 0.750

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 1.000
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 1.090
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: tolflatfitness
- **Mean generations**: 3.7
- **Final σ (mean)**: 0.294


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `6e4aa099e94fbceab0cbffcfa0782e5dc3f2f920fda4dd08a29a8751703a4594`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"hinge_delta_deg":10.0,"object_xy_delta":[0.0,0.0]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `1d4a12af4ca966b9ae057d85a80c022f8f485e56fbc5d1e540c4eac6bafb8e2f`; realized-scene SHA-256: `93d761ce3dc4e78ce09d05c5eb184a7129267f8d2172dd2a5cd042d5ec0710b9`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"fixture","value":[0.5,0.2,0.0]}],"axes":[{"name":"door_hinge_axis","value":[0.0,0.0,1.0]}],"door":{"hinge_axis":[0.0,0.0,1.0],"initial_hinge_angle":0.15466,"panel":{"name":"door_panel","orientation":[0.99701,0.0,0.0,0.07725],"position":[0.5,0.2,0.0]},"target_hinge_angle":0.524},"fixture_states":[],"fixtures":[{"name":"door_panel","orientation":[0.99701,0.0,0.0,0.07725],"position":[0.5,0.2,0.0]}],"limits":[{"name":"goal_tolerance_m","value":0.05},{"name":"force_limit_n","value":30.0},{"name":"force_scale_n","value":5.0},{"name":"target_hinge_angle_rad","value":0.524}],"object_starts":[],"obstacles":[],"targets":[],"task_name":"door_push"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":34.0,"average_failure_rate":0.18182,"average_mean_iterations":40.77005,"average_solve_count":187.0,"average_success_count":153.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.05937,"contact_1.contact_force":9.32187,"push_1.push_distance":0.16235,"push_1.push_max_time":8.24031,"push_1.push_speed":0.06395,"retract_1.retract_max_time":8.68298,"retract_1.speed":0.05645},"optimized_scores":{"best_composite_score":1.09,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link6","contact_count":51.0,"contact_point_centroid":[0.13481,0.04682,0.57154],"force_p95":1443.24988,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1618.07761,"mean_force":278.59144,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.08393,0.17233,0.5273]},{"body_a":"door_panel","body_b":"link7","contact_count":11.0,"contact_point_centroid":[0.21536,0.02164,0.52964],"force_p95":147.64049,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":149.95942,"mean_force":103.1513,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.15116,0.08034,0.52208]},{"body_a":"door_panel","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.14491,0.13302,0.46318],"force_p95":62.81201,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":63.43989,"mean_force":57.1611,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.10534,0.20038,0.41818]},{"body_a":"door_panel","body_b":"link7","contact_count":51.0,"contact_point_centroid":[0.14576,0.14076,0.46096],"force_p95":23.41981,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":24.82389,"mean_force":13.70594,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.10518,0.20747,0.41595]},{"body_a":"world","body_b":"door_panel","contact_count":1072.0,"contact_point_centroid":[0.30383,0.1598,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.10254,0.29875,0.38331]},{"body_a":"world","body_b":"door_panel","contact_count":8.0,"contact_point_centroid":[0.30529,0.15323,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.10535,0.2006,0.41827]},{"body_a":"world","body_b":"door_panel","contact_count":824.0,"contact_point_centroid":[0.35374,0.0722,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.06814,0.01218,0.46457]},{"body_a":"world","body_b":"door_panel","contact_count":640.0,"contact_point_centroid":[0.37249,0.04561,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.07382,-0.08164,0.36795]}],"total_contact_groups":8},"final_pose_error":0.44257,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.09903,-0.04179,0.37621],"hinge_angle":0.8119,"initial_hinge_angle":0.15466,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.15466,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":1618.07761,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":5.28893,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1123.0,"raw_peak_contact_force":24.82389,"subtask_id":"reach_handle","tcp_end":[0.10536,0.20076,0.41829],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.47579,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":4.0,"n_steps_budget":750.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":63.43989,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":10.0,"raw_peak_contact_force":63.43989,"subtask_id":"reach_handle","tcp_end":[0.1052,0.19879,0.41734],"tcp_start":[0.10536,0.20076,0.41829],"tcp_to_object_dist_end":0.47408,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":886.0,"raw_peak_contact_force":1618.07761,"subtask_id":"push_door","tcp_end":[0.07379,-0.11517,0.36473],"tcp_start":[0.1052,0.19879,0.41734],"tcp_to_object_dist_end":0.38953,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":640.0,"raw_peak_contact_force":0.0,"tcp_end":[0.09903,-0.04179,0.37621],"tcp_start":[0.07379,-0.11517,0.36473],"tcp_to_object_dist_end":0.39126,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `74b09c110110eedfa033ccf01fd9064bfaa53943493bfa1a44417e7ed7258576`; realized-scene SHA-256: `f3bd2e80ef0506fd6b5cd5a4fd1b44e0782b3c0a174abf2e2d5dfa29f59ee618`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"fixture","value":[0.5,0.2,0.0]}],"axes":[{"name":"door_hinge_axis","value":[0.0,0.0,1.0]}],"door":{"hinge_axis":[0.0,0.0,1.0],"initial_hinge_angle":0.10647,"panel":{"name":"door_panel","orientation":[0.99858,0.0,0.0,0.05321],"position":[0.5,0.2,0.0]},"target_hinge_angle":0.524},"fixture_states":[],"fixtures":[{"name":"door_panel","orientation":[0.99858,0.0,0.0,0.05321],"position":[0.5,0.2,0.0]}],"limits":[{"name":"goal_tolerance_m","value":0.05},{"name":"force_limit_n","value":30.0},{"name":"force_scale_n","value":5.0},{"name":"target_hinge_angle_rad","value":0.524}],"object_starts":[],"obstacles":[],"targets":[],"task_name":"door_push"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.2515,"average_solve_count":167.0,"average_success_count":167.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.04834,"contact_1.contact_force":13.25582,"push_1.push_distance":0.16597,"push_1.push_max_time":13.19455,"push_1.push_speed":0.06973,"retract_1.retract_max_time":14.30053,"retract_1.speed":0.07415},"optimized_scores":{"best_composite_score":1.09,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"link1","body_b":"link6","contact_count":267.0,"contact_point_centroid":[0.10843,0.00147,0.37778],"force_p95":424.90445,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":619.56443,"mean_force":364.17889,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.14605,0.10649,0.39056]},{"body_a":"door_panel","body_b":"link5","contact_count":583.0,"contact_point_centroid":[0.18947,-0.04848,0.52985],"force_p95":237.89937,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":387.92423,"mean_force":115.60576,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.14822,0.14343,0.44804]},{"body_a":"door_panel","body_b":"link6","contact_count":126.0,"contact_point_centroid":[0.16727,0.02651,0.51897],"force_p95":300.76749,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":328.51005,"mean_force":119.14521,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.12211,0.18548,0.50695]},{"body_a":"link1","body_b":"link6","contact_count":755.0,"contact_point_centroid":[0.11813,0.00237,0.36677],"force_p95":253.65117,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":259.2552,"mean_force":160.79108,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.15631,0.12544,0.37843]},{"body_a":"door_panel","body_b":"link7","contact_count":13.0,"contact_point_centroid":[0.14534,0.12699,0.45635],"force_p95":68.95787,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":81.91124,"mean_force":39.0061,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.0996,0.19614,0.42095]},{"body_a":"door_panel","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.14336,0.13878,0.4659],"force_p95":58.04059,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":58.04059,"mean_force":58.04059,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.10305,0.2059,0.4212]},{"body_a":"door_panel","body_b":"link5","contact_count":161.0,"contact_point_centroid":[0.26199,-0.1214,0.43795],"force_p95":37.07485,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":55.9815,"mean_force":23.54905,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.15288,0.14061,0.37652]},{"body_a":"door_panel","body_b":"link7","contact_count":90.0,"contact_point_centroid":[0.14496,0.15174,0.46145],"force_p95":22.27798,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":23.70546,"mean_force":14.33486,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.10289,0.2178,0.41688]},{"body_a":"world","body_b":"door_panel","contact_count":1096.0,"contact_point_centroid":[0.30224,0.1686,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.10132,0.30467,0.38357]},{"body_a":"world","body_b":"door_panel","contact_count":4.0,"contact_point_centroid":[0.30454,0.15647,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.10307,0.20623,0.42127]},{"body_a":"world","body_b":"door_panel","contact_count":716.0,"contact_point_centroid":[0.34549,0.07619,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.13359,0.15375,0.46199]},{"body_a":"world","body_b":"door_panel","contact_count":624.0,"contact_point_centroid":[0.38927,0.03319,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.15266,0.14153,0.37655]}],"total_contact_groups":12},"final_pose_error":0.20251,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.13898,0.20232,0.37036],"hinge_angle":0.96521,"initial_hinge_angle":0.10647,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.10647,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":619.56443,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1186.0,"raw_peak_contact_force":23.70546,"subtask_id":"reach_handle","tcp_end":[0.10307,0.20623,0.42127],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.48024,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":2.0,"n_steps_budget":780.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":32.62252,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":5.0,"raw_peak_contact_force":58.04059,"subtask_id":"reach_handle","tcp_end":[0.10302,0.20545,0.42101],"tcp_start":[0.10307,0.20623,0.42127],"tcp_to_object_dist_end":0.47966,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.18968,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1705.0,"raw_peak_contact_force":619.56443,"subtask_id":"push_door","tcp_end":[0.16351,0.08414,0.38373],"tcp_start":[0.10302,0.20545,0.42101],"tcp_to_object_dist_end":0.42552,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1540.0,"raw_peak_contact_force":259.2552,"tcp_end":[0.13898,0.20232,0.37036],"tcp_start":[0.16351,0.08414,0.38373],"tcp_to_object_dist_end":0.44432,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `19b9b4f2c5af25040a197573455096dd2f805f94d78c64c4126be8f0525fbcc6`; realized-scene SHA-256: `dc4259a01269d1a689f775747b3c927cb1b450b657cf3ca07d50da9e3593da80`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"fixture","value":[0.5,0.2,0.0]}],"axes":[{"name":"door_hinge_axis","value":[0.0,0.0,1.0]}],"door":{"hinge_axis":[0.0,0.0,1.0],"initial_hinge_angle":0.01332,"panel":{"name":"door_panel","orientation":[0.99998,0.0,0.0,0.00666],"position":[0.5,0.2,0.0]},"target_hinge_angle":0.524},"fixture_states":[],"fixtures":[{"name":"door_panel","orientation":[0.99998,0.0,0.0,0.00666],"position":[0.5,0.2,0.0]}],"limits":[{"name":"goal_tolerance_m","value":0.05},{"name":"force_limit_n","value":30.0},{"name":"force_scale_n","value":5.0},{"name":"target_hinge_angle_rad","value":0.524}],"object_starts":[],"obstacles":[],"targets":[],"task_name":"door_push"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.68276,"average_solve_count":145.0,"average_success_count":145.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.07862,"contact_1.contact_force":10.4879,"push_1.push_distance":0.17242,"push_1.push_max_time":12.8234,"push_1.push_speed":0.02909,"retract_1.retract_max_time":12.89083,"retract_1.speed":0.03686},"optimized_scores":{"best_composite_score":1.09,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link5","contact_count":498.0,"contact_point_centroid":[0.21554,-0.08074,0.48178],"force_p95":338.29169,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":469.37874,"mean_force":189.4926,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.11859,0.15567,0.39797]},{"body_a":"door_panel","body_b":"link6","contact_count":117.0,"contact_point_centroid":[0.15655,0.00925,0.51951],"force_p95":263.81413,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":371.45511,"mean_force":46.54978,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.1127,0.17533,0.5114]},{"body_a":"door_panel","body_b":"link5","contact_count":390.0,"contact_point_centroid":[0.17576,-0.03347,0.546],"force_p95":233.60323,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":342.22803,"mean_force":152.07562,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.13362,0.13989,0.44791]},{"body_a":"door_panel","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.13849,0.12659,0.48025],"force_p95":79.72439,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":81.76683,"mean_force":64.08094,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.10009,0.19571,0.43698]},{"body_a":"door_panel","body_b":"link7","contact_count":11.0,"contact_point_centroid":[0.14152,0.11432,0.46987],"force_p95":51.91462,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":65.82085,"mean_force":33.46177,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.09673,0.18563,0.43594]},{"body_a":"door_panel","body_b":"link7","contact_count":239.0,"contact_point_centroid":[0.14309,0.16175,0.46718],"force_p95":26.68622,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":29.66761,"mean_force":14.14465,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.10005,0.22786,0.42365]},{"body_a":"world","body_b":"door_panel","contact_count":960.0,"contact_point_centroid":[0.30094,0.18115,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.09989,0.29573,0.39337]},{"body_a":"world","body_b":"door_panel","contact_count":8.0,"contact_point_centroid":[0.30597,0.15048,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.1001,0.19588,0.4371]},{"body_a":"world","body_b":"door_panel","contact_count":792.0,"contact_point_centroid":[0.3367,0.08605,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.12486,0.15689,0.47478]},{"body_a":"world","body_b":"door_panel","contact_count":728.0,"contact_point_centroid":[0.36788,0.04975,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.11745,0.16712,0.39532]}],"total_contact_groups":10},"final_pose_error":0.18903,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.11335,0.21475,0.38516],"hinge_angle":0.86987,"initial_hinge_angle":0.01332,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.01332,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":469.37874,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":10.62153,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1199.0,"raw_peak_contact_force":29.66761,"subtask_id":"reach_handle","tcp_end":[0.10014,0.19678,0.43762],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.49016,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":6.0,"n_steps_budget":840.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":81.76683,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":11.0,"raw_peak_contact_force":81.76683,"subtask_id":"reach_handle","tcp_end":[0.09996,0.19342,0.43522],"tcp_start":[0.10014,0.19678,0.43762],"tcp_to_object_dist_end":0.48664,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1310.0,"raw_peak_contact_force":371.45511,"subtask_id":"push_door","tcp_end":[0.12109,0.12568,0.40421],"tcp_start":[0.09996,0.19342,0.43522],"tcp_to_object_dist_end":0.44027,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1226.0,"raw_peak_contact_force":469.37874,"tcp_end":[0.11335,0.21475,0.38516],"tcp_start":[0.12109,0.12568,0.40421],"tcp_to_object_dist_end":0.45532,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
```