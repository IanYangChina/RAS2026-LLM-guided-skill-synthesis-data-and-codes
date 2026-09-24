## Search State

- **Seed**: 2
- **Iteration**: 4 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 3 | approach → descend → push | arc_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | time_limit | 5 | 0.1901 | 0.47 | ❌ rejected |
| 2 | approach → descend → push | arc_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | time_limit | 5 | 0.1918 | 0.47 | ✅ accepted |
| 1 | approach → align → align → pull → descend → release → grasp → push | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | — | — | impedance_motion | position_control | position_control | position_control | impedance_control | position_control | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | contact_detected | time_limit | grasp_success | pose_tolerance | 7 | -0.0589 | 0.47 | ✅ accepted |
| 0 | approach → align → align → pull → descend → release → grasp → push | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | — | — | impedance_motion | position_control | position_control | position_control | impedance_control | position_control | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | contact_detected | time_limit | grasp_success | pose_tolerance | 7 | -0.0589 | 0.47 | ✅ accepted |

**Proposal policy**: task_score is 0.47 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `6dd40fac67fc7b4cb952edf7b79ea329c0b46aa4cb26369fc447c16f02a37d6d`
- Frozen initial hinge angle: 0.524 rad
- target_hinge_angle: -0.083 rad (task success = realised hinge-angle delta ratio; not TCP proximity)
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
  frozen_initial_hinge_angle_rad: -0.0832
  frozen_fixtures: {'door_panel': [0.5, 0.2, 0.0]}
  door_hinge_axis: [0, 0, 1]
  goal_tolerance_m: 0.05
  force_limit_n: 30
  force_scale_n: 5
  target_hinge_angle_rad: -0.083
  realized_scene_sha256: 6dd40fac67fc7b4cb952edf7b79ea329c0b46aa4cb26369fc447c16f02a37d6d

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

## Current Skill (Q=0.190) — your mutation base

```yaml
skill: door_push
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: reach_handle
  weight: 0.3
- id: push_door
  target_entity: hinge
  metric: hinge_angle
  weight: 0.7
phases:
- id: approach_to_handle
  type: approach
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.12
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
  retries:
    max_attempts: 1
    strategy: reduce_speed
  subtask_id: reach_handle
- id: descend_to_handle
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.02
    tolerance: 0.005
    orientation:
      mode: keep_current
  parameters:
    descend_speed:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: contact_early
    when: during_phase
    predicate: force_below
    threshold: 30.0
    on_failure: continue
  retries:
    max_attempts: 1
    strategy: reduce_speed
  subtask_id: reach_handle
- id: push_door_closed
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: time_limit
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.3
      axis: world_y
      mode: replace_offset_projection
      sign: negative
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - -1.0
      - 0.0
      align_with: world_y
      tolerance: 0.15
  parameters:
    max_push_time:
      type: scalar
      range:
      - 1.0
      - 5.0
      default: 3.0
      binds_to:
      - path: duration.max_time
        mode: replace
    push_distance:
      type: scalar
      range:
      - 0.1
      - 0.4
      default: 0.3
      binds_to:
      - path: target.offset_along_axis.distance
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
  - id: force_below_limit
    when: during_phase
    predicate: force_below
    threshold: 30.0
    on_failure: continue
  - id: hinge_reached
    when: during_phase
    predicate: hinge_delta_reached
    threshold: 0.1
    on_failure: continue
  retries:
    max_attempts: 1
    strategy: reduce_speed
  subtask_id: push_door

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_to_handle** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.12], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=1, strategy=reduce_speed
- **descend_to_handle** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.02], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=contact_early, when=during_phase, predicate=force_below, on_failure=continue, threshold=30.0
  - retries: max_attempts=1, strategy=reduce_speed
- **push_door_closed** (`push`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_y, distance=0.3, mode=replace_offset_projection, sign=negative}
  - orientation: mode=align_axis, axis=[0.0, -1.0, 0.0], align_with=world_y, tolerance=0.15
  - parameter_bindings:
    - max_push_time: status=consumed; consumers=duration.max_time (replace)
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=force_below_limit, when=during_phase, predicate=force_below, on_failure=continue, threshold=30.0
    - id=hinge_reached, when=during_phase, predicate=hinge_delta_reached, on_failure=continue, threshold=0.1
  - retries: max_attempts=1, strategy=reduce_speed

## Design Metrics

- **Composite score**: 0.190
- **task_score** (E): 0.470
- **fitness_score**: 0.470  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.280

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_to_handle | 1.00 | 0.33 | 0.2105 |
| descend_to_handle | 1.00 | 0.33 | 0.0940 |
| push_door_closed | 0.00 | 0.00 | 0.0000 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_to_handle | approach | 1.00 / step_budget | (0.100, 0.399, 0.350)→(0.100, 0.220, 0.460) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 0.33 / 0.333 | 3.640 | 29.944 |
| descend_to_handle | descend | 1.00 / step_budget | (0.100, 0.220, 0.460)→(0.100, 0.182, 0.375) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 0.33 / 0.333 | 0.000 | 20.104 |
| push_door_closed | push | 0.00 / guard_failure | (0.100, 0.182, 0.375)→(0.100, 0.182, 0.375) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 0.00 / 0.000 | 0.000 | 0.000 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- hinge_angle_ratio: 0.699
- arc_quality: 0.667

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.699
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.699
- **Median Q (composite search score)**: 0.302
- **K-run variance**: 0.0604
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.357


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `7dec7b9d265217827596e50fcdf4f13e307fabe21fe4cab198e2a5d141ff1ba8`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"hinge_delta_deg":10.0,"object_xy_delta":[0.0,0.0]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `2703841599a88ffb6fe3c9276875d1c87ae4a75b7467b1c48183ebe23e97d755`; realized-scene SHA-256: `6dd40fac67fc7b4cb952edf7b79ea329c0b46aa4cb26369fc447c16f02a37d6d`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"fixture","value":[0.5,0.2,0.0]}],"axes":[{"name":"door_hinge_axis","value":[0.0,0.0,1.0]}],"door":{"hinge_axis":[0.0,0.0,1.0],"initial_hinge_angle":0.524,"panel":{"name":"door_panel","orientation":[0.99913,0.0,0.0,-0.04159],"position":[0.5,0.2,0.0]},"target_hinge_angle":-0.08321},"fixture_states":[],"fixtures":[{"name":"door_panel","orientation":[0.99913,0.0,0.0,-0.04159],"position":[0.5,0.2,0.0]}],"limits":[{"name":"goal_tolerance_m","value":0.05},{"name":"force_limit_n","value":30.0},{"name":"force_scale_n","value":5.0},{"name":"target_hinge_angle_rad","value":0.524}],"object_starts":[],"obstacles":[],"targets":[],"task_name":"door_push"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.26087,"average_solve_count":115.0,"average_success_count":115.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_handle.approach_speed":0.09916,"descend_to_handle.descend_speed":0.02974,"push_door_closed.max_push_time":3.45525,"push_door_closed.push_distance":0.35235,"push_door_closed.push_speed":0.03115},"optimized_scores":{"best_composite_score":0.30203,"best_fitness_score":0.58203,"best_task_score":0.58203},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link6","contact_count":319.0,"contact_point_centroid":[0.10072,0.1927,0.55085],"force_p95":25.82133,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":43.58994,"mean_force":16.8429,"phase_index":0.0,"phase_name":"approach_to_handle","phase_type":"approach","tcp_position_centroid":[0.09956,0.26736,0.44343]},{"body_a":"door_panel","body_b":"link6","contact_count":30.0,"contact_point_centroid":[0.10286,0.15226,0.55887],"force_p95":18.79811,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":22.81612,"mean_force":13.69149,"phase_index":1.0,"phase_name":"descend_to_handle","phase_type":"descend","tcp_position_centroid":[0.0995,0.21825,0.45407]},{"body_a":"door_panel","body_b":"link7","contact_count":261.0,"contact_point_centroid":[0.16485,0.14089,0.43415],"force_p95":16.63997,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":17.6656,"mean_force":13.77369,"phase_index":1.0,"phase_name":"descend_to_handle","phase_type":"descend","tcp_position_centroid":[0.09955,0.19824,0.41008]},{"body_a":"world","body_b":"door_panel","contact_count":1036.0,"contact_point_centroid":[0.30006,0.1992,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_to_handle","phase_type":"approach","tcp_position_centroid":[0.09966,0.32363,0.4089]},{"body_a":"world","body_b":"door_panel","contact_count":636.0,"contact_point_centroid":[0.30451,0.15707,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"descend_to_handle","phase_type":"descend","tcp_position_centroid":[0.09954,0.20126,0.4167]}],"total_contact_groups":5},"final_pose_error":0.35352,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.09968,0.18187,0.37448],"hinge_angle":0.22177,"initial_hinge_angle":-0.08321,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":-0.08321,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":43.58994,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":10.92108,"phase_name":"approach_to_handle","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1355.0,"raw_peak_contact_force":43.58994,"subtask_id":"reach_handle","tcp_end":[0.09969,0.22092,0.46007],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.52001,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":674.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"descend_to_handle","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":927.0,"raw_peak_contact_force":22.81612,"subtask_id":"reach_handle","tcp_end":[0.09971,0.18192,0.37448],"tcp_start":[0.09969,0.22092,0.46007],"tcp_to_object_dist_end":0.42811,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"push_door_closed","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"push_door","tcp_end":[0.09968,0.18187,0.37448],"tcp_start":[0.09971,0.18192,0.37448],"tcp_to_object_dist_end":0.42808,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `0106e02cd8847cdbc8cb80732350ffe717d1fc22c509bf8221b103cb157c8e2d`; realized-scene SHA-256: `a535d88ef07b74838c5ab0400d8932f8a62343284dc305f72bf16a3002d4504f`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"fixture","value":[0.5,0.2,0.0]}],"axes":[{"name":"door_hinge_axis","value":[0.0,0.0,1.0]}],"door":{"hinge_axis":[0.0,0.0,1.0],"initial_hinge_angle":0.524,"panel":{"name":"door_panel","orientation":[0.99739,0.0,0.0,-0.07225],"position":[0.5,0.2,0.0]},"target_hinge_angle":-0.14464},"fixture_states":[],"fixtures":[{"name":"door_panel","orientation":[0.99739,0.0,0.0,-0.07225],"position":[0.5,0.2,0.0]}],"limits":[{"name":"goal_tolerance_m","value":0.05},{"name":"force_limit_n","value":30.0},{"name":"force_scale_n","value":5.0},{"name":"target_hinge_angle_rad","value":0.524}],"object_starts":[],"obstacles":[],"targets":[],"task_name":"door_push"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.43396,"average_solve_count":106.0,"average_success_count":106.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_handle.approach_speed":0.09829,"descend_to_handle.descend_speed":0.03453,"push_door_closed.max_push_time":2.86544,"push_door_closed.push_distance":0.41103,"push_door_closed.push_speed":0.06726},"optimized_scores":{"best_composite_score":0.41913,"best_fitness_score":0.69913,"best_task_score":0.69913},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link6","contact_count":341.0,"contact_point_centroid":[0.1008,0.19585,0.54917],"force_p95":29.43761,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":46.24279,"mean_force":17.39868,"phase_index":0.0,"phase_name":"approach_to_handle","phase_type":"approach","tcp_position_centroid":[0.09953,0.27097,0.4416]},{"body_a":"door_panel","body_b":"link6","contact_count":28.0,"contact_point_centroid":[0.10294,0.15166,0.55644],"force_p95":19.54824,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":20.28926,"mean_force":14.27517,"phase_index":1.0,"phase_name":"descend_to_handle","phase_type":"descend","tcp_position_centroid":[0.09946,0.21742,0.45162]},{"body_a":"door_panel","body_b":"link7","contact_count":266.0,"contact_point_centroid":[0.16485,0.14116,0.43446],"force_p95":16.70471,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":17.38924,"mean_force":13.64164,"phase_index":1.0,"phase_name":"descend_to_handle","phase_type":"descend","tcp_position_centroid":[0.09954,0.19851,0.41039]},{"body_a":"world","body_b":"door_panel","contact_count":1020.0,"contact_point_centroid":[0.30024,0.19869,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_to_handle","phase_type":"approach","tcp_position_centroid":[0.09962,0.31311,0.41533]},{"body_a":"world","body_b":"door_panel","contact_count":704.0,"contact_point_centroid":[0.30442,0.15747,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"descend_to_handle","phase_type":"descend","tcp_position_centroid":[0.09953,0.20199,0.41799]}],"total_contact_groups":5},"final_pose_error":0.41209,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.09968,0.1819,0.37449],"hinge_angle":0.22171,"initial_hinge_angle":-0.14464,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":-0.14464,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":46.24279,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"approach_to_handle","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1361.0,"raw_peak_contact_force":46.24279,"subtask_id":"reach_handle","tcp_end":[0.09968,0.22115,0.45999],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.52003,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":660.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"descend_to_handle","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":998.0,"raw_peak_contact_force":20.28926,"subtask_id":"reach_handle","tcp_end":[0.09971,0.18194,0.3745],"tcp_start":[0.09968,0.22115,0.45999],"tcp_to_object_dist_end":0.42812,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"push_door_closed","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"push_door","tcp_end":[0.09968,0.1819,0.37449],"tcp_start":[0.09971,0.18194,0.3745],"tcp_to_object_dist_end":0.4281,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `7bc2b9dece282a8a9fabbafdd09525b72694e2e86202e4d7347d50b4ed50bf95`; realized-scene SHA-256: `93d761ce3dc4e78ce09d05c5eb184a7129267f8d2172dd2a5cd042d5ec0710b9`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"fixture","value":[0.5,0.2,0.0]}],"axes":[{"name":"door_hinge_axis","value":[0.0,0.0,1.0]}],"door":{"hinge_axis":[0.0,0.0,1.0],"initial_hinge_angle":0.524,"panel":{"name":"door_panel","orientation":[0.99701,0.0,0.0,0.07725],"position":[0.5,0.2,0.0]},"target_hinge_angle":0.15466},"fixture_states":[],"fixtures":[{"name":"door_panel","orientation":[0.99701,0.0,0.0,0.07725],"position":[0.5,0.2,0.0]}],"limits":[{"name":"goal_tolerance_m","value":0.05},{"name":"force_limit_n","value":30.0},{"name":"force_scale_n","value":5.0},{"name":"target_hinge_angle_rad","value":0.524}],"object_starts":[],"obstacles":[],"targets":[],"task_name":"door_push"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.20168,"average_solve_count":119.0,"average_success_count":119.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_handle.approach_speed":0.09807,"descend_to_handle.descend_speed":0.02844,"push_door_closed.max_push_time":1.37778,"push_door_closed.push_distance":0.31128,"push_door_closed.push_speed":0.03631},"optimized_scores":{"best_composite_score":-0.15072,"best_fitness_score":0.12928,"best_task_score":0.12928},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link7","contact_count":216.0,"contact_point_centroid":[0.16491,0.13708,0.42881],"force_p95":16.6759,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":17.20675,"mean_force":13.74062,"phase_index":1.0,"phase_name":"descend_to_handle","phase_type":"descend","tcp_position_centroid":[0.09965,0.1945,0.40478]},{"body_a":"world","body_b":"door_panel","contact_count":1056.0,"contact_point_centroid":[0.30379,0.16,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_to_handle","phase_type":"approach","tcp_position_centroid":[0.09978,0.31641,0.41259]},{"body_a":"world","body_b":"door_panel","contact_count":564.0,"contact_point_centroid":[0.3049,0.1552,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"descend_to_handle","phase_type":"descend","tcp_position_centroid":[0.09966,0.19937,0.41636]},{"body_a":"door_panel","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.16499,0.1243,0.39859],"force_p95":0.0,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_door_closed","phase_type":"push","tcp_position_centroid":[0.09972,0.18173,0.37456]}],"total_contact_groups":4},"final_pose_error":0.31255,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.0997,0.1817,0.37457],"hinge_angle":0.2224,"initial_hinge_angle":0.15466,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.15466,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":17.20675,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"approach_to_handle","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1056.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_handle","tcp_end":[0.09986,0.2181,0.46109],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.51976,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":670.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"descend_to_handle","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":780.0,"raw_peak_contact_force":17.20675,"subtask_id":"reach_handle","tcp_end":[0.09972,0.18173,0.37456],"tcp_start":[0.09986,0.2181,0.46109],"tcp_to_object_dist_end":0.4281,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"push_door_closed","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1.0,"raw_peak_contact_force":0.0,"subtask_id":"push_door","tcp_end":[0.0997,0.1817,0.37457],"tcp_start":[0.09972,0.18173,0.37456],"tcp_to_object_dist_end":0.42808,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```