## Search State

- **Seed**: 3
- **Iteration**: 7 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 6 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 10 | 0.2144 | 0.69 | ✅ accepted |
| 5 | approach → contact → push → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 11 | 0.0471 | 0.69 | ✅ accepted |
| 4 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 9 | 0.1189 | 0.63 | ✅ accepted |
| 3 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 7 | 0.2059 | 0.28 | ❌ rejected |
| 2 | approach → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | pose_tolerance | time_limit | pose_tolerance | 5 | -0.2463 | 0.03 | ❌ rejected |

**Proposal policy**: task_score is 0.69 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
- task_score stagnant: change coupled targets, parameters, terminations, phase types, controls, subtasks, or ordering when evidence shows they need to change together.
A HOLD wastes an iteration when task_score is below 0.9.

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
- Frozen realised-scene SHA-256: `a535d88ef07b74838c5ab0400d8932f8a62343284dc305f72bf16a3002d4504f`
- Frozen initial hinge angle: -0.145 rad
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
  frozen_initial_hinge_angle_rad: -0.1446
  frozen_fixtures: {'door_panel': [0.5, 0.2, 0.0]}
  door_hinge_axis: [0, 0, 1]
  goal_tolerance_m: 0.05
  force_limit_n: 30
  force_scale_n: 5
  target_hinge_angle_rad: 0.524
  realized_scene_sha256: a535d88ef07b74838c5ab0400d8932f8a62343284dc305f72bf16a3002d4504f

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

## Current Skill (Q=0.214) — your mutation base

```yaml
skill: door_push
dsl_version: 2
subtasks:
- id: approach_handle
  anchor: fixture
  offset:
  - -0.4
  - -0.02
  - 0.35
  weight: 0.2
- id: push_to_goal
  anchor: world
  target_entity: hinge
  metric: hinge_angle
  weight: 0.8
phases:
- id: approach_handle
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
    tolerance: 0.02
    orientation:
      mode: keep_current
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
    tolerance:
      type: scalar
      range:
      - 0.005
      - 0.03
      default: 0.02
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat
  subtask_id: approach_handle
- id: contact_handle
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
    - 0.0
    orientation:
      mode: keep_current
  parameters:
    force_threshold:
      type: scalar
      range:
      - 5.0
      - 20.0
      default: 10.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    speed:
      type: scalar
      range:
      - 0.005
      - 0.05
      default: 0.01
      binds_to:
      - path: generator.speed
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat
  subtask_id: approach_handle
- id: push_door
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: time_limit
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.3
      axis: world_y
      mode: add_to_offset
      sign: negative
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: world_z
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.2
      - 0.5
      default: 0.3
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_force_limit:
      type: scalar
      range:
      - 15.0
      - 30.0
      default: 30.0
      binds_to:
      - path: guards.push_force_guard.threshold
        mode: replace
    speed:
      type: scalar
      range:
      - 0.01
      - 0.2
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
    timeout:
      type: scalar
      range:
      - 5.0
      - 15.0
      default: 10.0
      binds_to:
      - path: duration.max_time
        mode: replace
  guards:
  - id: push_force_guard
    when: during_phase
    predicate: force_below
    threshold: 30.0
    on_failure: retry
  retries:
    max_attempts: 1
    strategy: reduce_speed
  subtask_id: push_to_goal
- id: retract
  type: retract
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: world
    offset:
    - 0.0
    - 0.3
    - 0.35
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
    tol:
      type: scalar
      range:
      - 0.005
      - 0.03
      default: 0.02
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_handle** (`approach`)
  - target: source=yaml, anchor=site, entity=door_handle, offset=[0.0, 0.0, 0.1], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
    - tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
  - retries: max_attempts=0, strategy=repeat
- **contact_handle** (`contact`)
  - target: source=yaml, anchor=site, entity=door_handle, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - force_threshold: status=consumed; consumers=termination.force_threshold (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=0, strategy=repeat
- **push_door** (`push`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_y, distance=0.3, mode=add_to_offset, sign=negative}
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=world_z
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_force_limit: status=consumed; consumers=guards.push_force_guard.threshold (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
    - timeout: status=consumed; consumers=duration.max_time (replace)
  - guards:
    - id=push_force_guard, when=during_phase, predicate=force_below, on_failure=retry, threshold=30.0
  - retries: max_attempts=1, strategy=reduce_speed
- **retract** (`retract`)
  - target: source=yaml, anchor=world, offset=[0.0, 0.3, 0.35], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
    - tol: status=consumed; consumers=termination.pose_tolerance (replace)
  - retries: max_attempts=0, strategy=repeat

## Design Metrics

- **Composite score**: 0.214
- **task_score** (E): 0.691
- **fitness_score**: 0.691  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.083
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.560

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_handle | 1.00 | 1.00 | 0.2364 |
| contact_handle | 1.00 | 1.00 | 0.0595 |
| push_door | 0.00 | 1.00 | 0.0020 |
| retract | 1.00 | 0.00 | 0.2272 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_handle | approach | 1.00 / step_budget | (0.100, 0.399, 0.350)→(0.104, 0.182, 0.440) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 1.000 | 6.510 | 31.103 |
| contact_handle | contact | 1.00 / step_budget | (0.104, 0.182, 0.440)→(0.115, 0.135, 0.405) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 1.000 | 12.003 | 20.456 |
| push_door | push | 0.00 / guard_failure | (0.119, 0.094, 0.391)→(0.119, 0.094, 0.392) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 1.000 | 27.307 | 238.258 |
| retract | retract | 1.00 / step_budget | (0.119, 0.094, 0.392)→(0.010, 0.283, 0.351) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 0.00 / 0.000 | 0.000 | 231.870 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- hinge_angle_ratio: 0.857
- arc_quality: 0.750

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.857
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.857
- **Median Q (composite search score)**: 0.213
- **K-run variance**: 0.0044
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.313


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `bba62da7f52483738d4dc6e46310e5298b0e0489aa689b981e86db9abdda203f`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"hinge_delta_deg":10.0,"object_xy_delta":[0.0,0.0]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `789e053c0bcbffe7b16f252cc6b64c92268fc5193521b308e129f45c08e7a265`; realized-scene SHA-256: `a535d88ef07b74838c5ab0400d8932f8a62343284dc305f72bf16a3002d4504f`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"fixture","value":[0.5,0.2,0.0]}],"axes":[{"name":"door_hinge_axis","value":[0.0,0.0,1.0]}],"door":{"hinge_axis":[0.0,0.0,1.0],"initial_hinge_angle":-0.14464,"panel":{"name":"door_panel","orientation":[0.99739,0.0,0.0,-0.07225],"position":[0.5,0.2,0.0]},"target_hinge_angle":0.524},"fixture_states":[],"fixtures":[{"name":"door_panel","orientation":[0.99739,0.0,0.0,-0.07225],"position":[0.5,0.2,0.0]}],"limits":[{"name":"goal_tolerance_m","value":0.05},{"name":"force_limit_n","value":30.0},{"name":"force_scale_n","value":5.0},{"name":"target_hinge_angle_rad","value":0.524}],"object_starts":[],"obstacles":[],"targets":[],"task_name":"door_push"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.32877,"average_solve_count":146.0,"average_success_count":146.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_handle.speed":0.04033,"approach_handle.tolerance":0.01578,"contact_handle.force_threshold":16.35294,"contact_handle.speed":0.03689,"push_door.push_distance":0.31929,"push_door.push_force_limit":18.41083,"push_door.speed":0.17565,"push_door.timeout":9.59339,"retract.speed":0.09868,"retract.tol":0.02157},"optimized_scores":{"best_composite_score":0.21301,"best_fitness_score":0.52301,"best_task_score":0.52301},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.17763,0.17481,0.32094],"force_p95":77.34982,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":78.0734,"mean_force":70.83753,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.09519,0.19196,0.32081]},{"body_a":"door_panel","body_b":"link7","contact_count":10.0,"contact_point_centroid":[0.17462,0.16788,0.30657],"force_p95":56.38782,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":56.88248,"mean_force":32.3986,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.09205,0.18621,0.32114]},{"body_a":"door_panel","body_b":"link6","contact_count":110.0,"contact_point_centroid":[0.10053,0.20977,0.52445],"force_p95":32.6817,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":35.43924,"mean_force":24.4858,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.10076,0.28896,0.41535]},{"body_a":"door_panel","body_b":"link6","contact_count":56.0,"contact_point_centroid":[0.10085,0.17429,0.53773],"force_p95":22.13771,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":22.75487,"mean_force":14.75401,"phase_index":1.0,"phase_name":"contact_handle","phase_type":"contact","tcp_position_centroid":[0.10073,0.24642,0.43056]},{"body_a":"world","body_b":"door_panel","contact_count":388.0,"contact_point_centroid":[0.30004,0.20284,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.10056,0.32597,0.39255]},{"body_a":"world","body_b":"door_panel","contact_count":148.0,"contact_point_centroid":[0.30101,0.17765,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"contact_handle","phase_type":"contact","tcp_position_centroid":[0.10076,0.24779,0.43204]},{"body_a":"door_panel","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.10113,0.17003,0.53228],"force_p95":0.0,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.10069,0.24116,0.42533]},{"body_a":"world","body_b":"door_panel","contact_count":92.0,"contact_point_centroid":[0.30134,0.17482,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.1035,0.22683,0.3653]},{"body_a":"world","body_b":"door_panel","contact_count":364.0,"contact_point_centroid":[0.30297,0.16425,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.05781,0.22727,0.33088]}],"total_contact_groups":9},"final_pose_error":0.01973,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.01185,0.28517,0.34461],"hinge_angle":0.12942,"initial_hinge_angle":-0.14464,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":-0.14464,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":78.0734,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":438.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":19.53103,"phase_name":"approach_handle","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":498.0,"raw_peak_contact_force":35.43924,"subtask_id":"approach_handle","tcp_end":[0.10105,0.25325,0.4377],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.51568,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":125.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":21.33722,"phase_name":"contact_handle","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":204.0,"raw_peak_contact_force":22.75487,"subtask_id":"approach_handle","tcp_end":[0.10069,0.24116,0.42533],"tcp_start":[0.10105,0.25325,0.4377],"tcp_to_object_dist_end":0.4992,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":75.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":78.0734,"phase_name":"push_door","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":95.0,"raw_peak_contact_force":78.0734,"subtask_id":"push_to_goal","tcp_end":[0.09428,0.19007,0.32086],"tcp_start":[0.0949,0.19131,0.32083],"tcp_to_object_dist_end":0.38466,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":341.0,"n_steps_budget":930.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":374.0,"raw_peak_contact_force":56.88248,"tcp_end":[0.01185,0.28517,0.34461],"tcp_start":[0.09428,0.19007,0.32086],"tcp_to_object_dist_end":0.44746,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `5a9939150766bec2b15bab1845f15dc59243da82175f4d23a01f9499c42cbd2f`; realized-scene SHA-256: `93d761ce3dc4e78ce09d05c5eb184a7129267f8d2172dd2a5cd042d5ec0710b9`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"fixture","value":[0.5,0.2,0.0]}],"axes":[{"name":"door_hinge_axis","value":[0.0,0.0,1.0]}],"door":{"hinge_axis":[0.0,0.0,1.0],"initial_hinge_angle":0.15466,"panel":{"name":"door_panel","orientation":[0.99701,0.0,0.0,0.07725],"position":[0.5,0.2,0.0]},"target_hinge_angle":0.524},"fixture_states":[],"fixtures":[{"name":"door_panel","orientation":[0.99701,0.0,0.0,0.07725],"position":[0.5,0.2,0.0]}],"limits":[{"name":"goal_tolerance_m","value":0.05},{"name":"force_limit_n","value":30.0},{"name":"force_scale_n","value":5.0},{"name":"target_hinge_angle_rad","value":0.524}],"object_starts":[],"obstacles":[],"targets":[],"task_name":"door_push"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":17.0,"average_failure_rate":0.05923,"average_mean_iterations":14.96167,"average_solve_count":287.0,"average_success_count":270.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_handle.speed":0.04953,"approach_handle.tolerance":0.02158,"contact_handle.force_threshold":19.89002,"contact_handle.speed":0.02332,"push_door.push_distance":0.36532,"push_door.push_force_limit":17.64553,"push_door.speed":0.18734,"push_door.timeout":8.14395,"retract.speed":0.10266,"retract.tol":0.0112},"optimized_scores":{"best_composite_score":0.29664,"best_fitness_score":0.85664,"best_task_score":0.85664},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"link2","body_b":"link5","contact_count":15.0,"contact_point_centroid":[-0.00781,0.09371,0.37129],"force_p95":194.92609,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":200.06997,"mean_force":139.32335,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.13681,0.01926,0.44138]},{"body_a":"door_panel","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.20764,0.02477,0.41278],"force_p95":139.48936,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":139.74335,"mean_force":92.31559,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.12885,0.04336,0.41773]},{"body_a":"door_panel","body_b":"link7","contact_count":10.0,"contact_point_centroid":[0.22052,0.01822,0.42006],"force_p95":81.29602,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":85.55073,"mean_force":37.27448,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.13479,0.02173,0.43745]},{"body_a":"door_panel","body_b":"link7","contact_count":138.0,"contact_point_centroid":[0.17175,0.1151,0.45243],"force_p95":27.58943,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":28.8702,"mean_force":19.51498,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.10648,0.17255,0.42863]},{"body_a":"door_panel","body_b":"link6","contact_count":8.0,"contact_point_centroid":[0.10482,0.13872,0.52223],"force_p95":17.76679,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":27.33352,"mean_force":3.41669,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.10563,0.20615,0.41686]},{"body_a":"door_panel","body_b":"link7","contact_count":706.0,"contact_point_centroid":[0.18463,0.03871,0.43169],"force_p95":16.71127,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":19.59219,"mean_force":11.99602,"phase_index":1.0,"phase_name":"contact_handle","phase_type":"contact","tcp_position_centroid":[0.11816,0.09569,0.40509]},{"body_a":"world","body_b":"door_panel","contact_count":680.0,"contact_point_centroid":[0.3053,0.15448,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.10352,0.27605,0.3917]},{"body_a":"world","body_b":"door_panel","contact_count":884.0,"contact_point_centroid":[0.32603,0.1015,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"contact_handle","phase_type":"contact","tcp_position_centroid":[0.11744,0.0981,0.40657]},{"body_a":"world","body_b":"door_panel","contact_count":44.0,"contact_point_centroid":[0.33316,0.08926,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.11916,0.05227,0.39124]},{"body_a":"world","body_b":"door_panel","contact_count":580.0,"contact_point_centroid":[0.34229,0.0766,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.07502,0.14448,0.39657]}],"total_contact_groups":10},"final_pose_error":0.01999,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.0079,0.28218,0.35442],"hinge_angle":0.60353,"initial_hinge_angle":0.15466,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.15466,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":304.49766,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":679.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"approach_handle","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":826.0,"raw_peak_contact_force":28.8702,"subtask_id":"approach_handle","tcp_end":[0.10746,0.13658,0.44148],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.47445,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":8.61071,"phase_name":"contact_handle","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1590.0,"raw_peak_contact_force":19.59219,"subtask_id":"approach_handle","tcp_end":[0.12539,0.07369,0.3967],"tcp_start":[0.10746,0.13658,0.44148],"tcp_to_object_dist_end":0.42252,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":84.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":3.38882,"phase_name":"push_door","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":47.0,"raw_peak_contact_force":139.74335,"subtask_id":"push_to_goal","tcp_end":[0.13165,0.02619,0.43118],"tcp_start":[0.13095,0.02748,0.42923],"tcp_to_object_dist_end":0.45159,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":751.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":605.0,"raw_peak_contact_force":200.06997,"tcp_end":[0.0079,0.28218,0.35442],"tcp_start":[0.13165,0.02619,0.43118],"tcp_to_object_dist_end":0.4531,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `2f40317e91cda9d20f75f9f44171fa9a28a4706ede195f831595653d78bddc9d`; realized-scene SHA-256: `f3bd2e80ef0506fd6b5cd5a4fd1b44e0782b3c0a174abf2e2d5dfa29f59ee618`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"fixture","value":[0.5,0.2,0.0]}],"axes":[{"name":"door_hinge_axis","value":[0.0,0.0,1.0]}],"door":{"hinge_axis":[0.0,0.0,1.0],"initial_hinge_angle":0.10647,"panel":{"name":"door_panel","orientation":[0.99858,0.0,0.0,0.05321],"position":[0.5,0.2,0.0]},"target_hinge_angle":0.524},"fixture_states":[],"fixtures":[{"name":"door_panel","orientation":[0.99858,0.0,0.0,0.05321],"position":[0.5,0.2,0.0]}],"limits":[{"name":"goal_tolerance_m","value":0.05},{"name":"force_limit_n","value":30.0},{"name":"force_scale_n","value":5.0},{"name":"target_hinge_angle_rad","value":0.524}],"object_starts":[],"obstacles":[],"targets":[],"task_name":"door_push"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":12.0,"average_failure_rate":0.04494,"average_mean_iterations":12.12734,"average_solve_count":267.0,"average_success_count":255.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_handle.speed":0.03577,"approach_handle.tolerance":0.00585,"contact_handle.force_threshold":19.47966,"contact_handle.speed":0.00856,"push_door.push_distance":0.21876,"push_door.push_force_limit":21.16454,"push_door.speed":0.1854,"push_door.timeout":8.22311,"retract.speed":0.14337,"retract.tol":0.02759},"optimized_scores":{"best_composite_score":0.13341,"best_fitness_score":0.69341,"best_task_score":0.69341},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"link2","body_b":"link5","contact_count":2.0,"contact_point_centroid":[-0.0276,0.09333,0.35881],"force_p95":494.13525,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":496.95597,"mean_force":468.74874,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.13096,0.06381,0.42084]},{"body_a":"link2","body_b":"link5","contact_count":8.0,"contact_point_centroid":[-0.02425,0.08991,0.35995],"force_p95":393.89791,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":438.65889,"mean_force":180.52194,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.13258,0.06885,0.42797]},{"body_a":"door_panel","body_b":"link7","contact_count":108.0,"contact_point_centroid":[0.169,0.12516,0.4544],"force_p95":27.15278,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":28.99896,"mean_force":19.24944,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.10373,0.18258,0.43057]},{"body_a":"door_panel","body_b":"link6","contact_count":39.0,"contact_point_centroid":[0.1032,0.1503,0.52243],"force_p95":25.29004,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":28.364,"mean_force":17.18843,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.10317,0.21903,0.41671]},{"body_a":"door_panel","body_b":"link7","contact_count":656.0,"contact_point_centroid":[0.17913,0.05679,0.4288],"force_p95":16.50598,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":19.02086,"mean_force":11.95608,"phase_index":1.0,"phase_name":"contact_handle","phase_type":"contact","tcp_position_centroid":[0.11297,0.11387,0.40289]},{"body_a":"world","body_b":"door_panel","contact_count":680.0,"contact_point_centroid":[0.30328,0.16408,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.10203,0.28245,0.39238]},{"body_a":"world","body_b":"door_panel","contact_count":984.0,"contact_point_centroid":[0.32095,0.11111,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"contact_handle","phase_type":"contact","tcp_position_centroid":[0.11229,0.11682,0.40535]},{"body_a":"door_panel","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.18556,0.03413,0.42],"force_p95":0.0,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.1192,0.09123,0.39226]},{"body_a":"world","body_b":"door_panel","contact_count":112.0,"contact_point_centroid":[0.32768,0.09799,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.11483,0.07248,0.37655]},{"body_a":"world","body_b":"door_panel","contact_count":580.0,"contact_point_centroid":[0.3269,0.09932,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.07556,0.16737,0.39209]}],"total_contact_groups":10},"final_pose_error":0.01968,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.00907,0.28304,0.35419],"hinge_angle":0.46981,"initial_hinge_angle":0.10647,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.10647,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":496.95597,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":643.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"approach_handle","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":827.0,"raw_peak_contact_force":28.99896,"subtask_id":"approach_handle","tcp_end":[0.10419,0.15511,0.44112],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.47906,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":6.06159,"phase_name":"contact_handle","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1640.0,"raw_peak_contact_force":19.02086,"subtask_id":"approach_handle","tcp_end":[0.1192,0.09123,0.39226],"tcp_start":[0.10419,0.15511,0.44112],"tcp_to_object_dist_end":0.42,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":96.0,"n_steps_budget":750.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.45858,"phase_name":"push_door","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":115.0,"raw_peak_contact_force":496.95597,"subtask_id":"push_to_goal","tcp_end":[0.13145,0.06565,0.4235],"tcp_start":[0.13116,0.06442,0.42173],"tcp_to_object_dist_end":0.44826,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":608.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":588.0,"raw_peak_contact_force":438.65889,"tcp_end":[0.00907,0.28304,0.35419],"tcp_start":[0.13145,0.06565,0.4235],"tcp_to_object_dist_end":0.45348,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```