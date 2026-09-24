## Search State

- **Seed**: 4
- **Iteration**: 4 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 3 | approach → descend → push → push | linear_cartesian | linear_cartesian | impedance_motion | impedance_motion | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | time_limit | time_limit | 6 | 0.8067 | 1.00 | ✅ accepted |
| 2 | approach → descend → push | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | impedance_control | pose_tolerance | contact_detected | time_limit | 4 | 0.8104 | 0.71 | ✅ accepted |
| 1 | push → align → release | impedance_motion | linear_cartesian | linear_cartesian | position_control | position_control | position_control | time_limit | pose_tolerance | time_limit | 3 | 0.0400 | 0.22 | ✅ accepted |
| 0 | push → align → release | impedance_motion | linear_cartesian | linear_cartesian | position_control | position_control | position_control | time_limit | pose_tolerance | time_limit | 3 | 0.0400 | 0.22 | ✅ accepted |

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

## Current Skill (Q=0.807) — your mutation base

```yaml
skill: door_push
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: reach_handle
  anchor: fixture
  offset:
  - -0.4
  - -0.02
  - 0.35
  weight: 0.3
- id: push_door
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
    - 0.45
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_handle
- id: descend_to_handle
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: contact_detected
  target:
    source: yaml
    anchor: fixture
    entity: door_panel
    offset:
    - -0.4
    - -0.02
    - 0.35
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    descend_speed:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
- id: push_open
  type: push
  generator: impedance_motion
  control: position_control
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
      mode: replace_offset_projection
      sign: negative
    orientation:
      mode: keep_current
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.1
      - 0.5
      default: 0.3
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.06
      default: 0.04
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: force_limit_guard
    when: during_phase
    predicate: force_below
    threshold: 30.0
    on_failure: retry
  retries:
    max_attempts: 1
    strategy: reduce_speed
  subtask_id: push_door
- id: push_more
  type: push
  generator: impedance_motion
  control: position_control
  termination: time_limit
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
      mode: replace_offset_projection
      sign: negative
    orientation:
      mode: keep_current
  parameters:
    push_more_distance:
      type: scalar
      range:
      - 0.05
      - 0.4
      default: 0.2
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_more_speed:
      type: scalar
      range:
      - 0.01
      - 0.06
      default: 0.04
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: force_limit_guard_more
    when: during_phase
    predicate: force_below
    threshold: 30.0
    on_failure: retry
  retries:
    max_attempts: 1
    strategy: reduce_speed
  subtask_id: push_door

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_handle** (`approach`)
  - target: source=yaml, anchor=fixture, entity=door_panel, offset=[-0.4, -0.02, 0.45], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_handle** (`descend`)
  - target: source=yaml, anchor=fixture, entity=door_panel, offset=[-0.4, -0.02, 0.35], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (replace)
- **push_open** (`push`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_y, distance=0.3, mode=replace_offset_projection, sign=negative}
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=force_limit_guard, when=during_phase, predicate=force_below, on_failure=retry, threshold=30.0
  - retries: max_attempts=1, strategy=reduce_speed
- **push_more** (`push`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_y, distance=0.2, mode=replace_offset_projection, sign=negative}
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_more_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_more_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=force_limit_guard_more, when=during_phase, predicate=force_below, on_failure=retry, threshold=30.0
  - retries: max_attempts=1, strategy=reduce_speed

## Design Metrics

- **Composite score**: 0.807
- **task_score** (E): 1.000
- **fitness_score**: 1.000  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.167
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.360

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_handle | 1.00 | 0.67 | 0.2213 |
| descend_to_handle | 0.67 | 0.67 | 0.0606 |
| push_open | 1.00 | 0.67 | 0.1055 |
| push_more | 1.00 | 0.33 | 0.0827 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_handle | approach | 1.00 / step_budget | (0.100, 0.399, 0.350)→(0.100, 0.197, 0.440) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 0.67 / 0.667 | 5.716 | 32.142 |
| descend_to_handle | descend | 0.67 / step_budget | (0.100, 0.197, 0.440)→(0.100, 0.185, 0.381) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 0.67 / 2.000 | 10.110 | 10.719 |
| push_open | push | 1.00 / time_limit | (0.100, 0.185, 0.381)→(0.098, 0.088, 0.411) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 0.67 / 2.000 | 3.497 | 25.786 |
| push_more | push | 1.00 / time_limit | (0.098, 0.088, 0.411)→(0.100, 0.007, 0.420) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 0.33 / 0.333 | 3.463 | 25.442 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- hinge_angle_ratio: 1.000
- arc_quality: 1.000

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 1.000
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.640
- **K-run variance**: 0.0556
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.331


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.09615,"average_solve_count":208.0,"average_success_count":208.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_handle.approach_speed":0.03463,"descend_to_handle.descend_speed":0.02139,"push_more.push_more_distance":0.21358,"push_more.push_more_speed":0.05627,"push_open.push_distance":0.4628,"push_open.push_speed":0.03266},"optimized_scores":{"best_composite_score":1.14,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link7","contact_count":22.0,"contact_point_centroid":[0.16539,0.14471,0.46173],"force_p95":27.02911,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":27.75442,"mean_force":20.04241,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.10018,0.20202,0.43786]},{"body_a":"door_panel","body_b":"link7","contact_count":627.0,"contact_point_centroid":[0.17435,-0.02719,0.45304],"force_p95":17.94361,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":25.18858,"mean_force":10.63634,"phase_index":3.0,"phase_name":"push_more","phase_type":"push","tcp_position_centroid":[0.0997,0.01641,0.42803]},{"body_a":"door_panel","body_b":"link7","contact_count":827.0,"contact_point_centroid":[0.16553,0.07489,0.45491],"force_p95":17.6636,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":24.46695,"mean_force":13.1027,"phase_index":2.0,"phase_name":"push_open","phase_type":"push","tcp_position_centroid":[0.0997,0.13199,0.42981]},{"body_a":"world","body_b":"door_panel","contact_count":588.0,"contact_point_centroid":[0.30389,0.15949,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.1001,0.30247,0.39181]},{"body_a":"world","body_b":"door_panel","contact_count":64.0,"contact_point_centroid":[0.30522,0.15353,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"descend_to_handle","phase_type":"descend","tcp_position_centroid":[0.09993,0.19604,0.43637]},{"body_a":"world","body_b":"door_panel","contact_count":980.0,"contact_point_centroid":[0.31748,0.11995,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_open","phase_type":"push","tcp_position_centroid":[0.0997,0.1286,0.4298]},{"body_a":"world","body_b":"door_panel","contact_count":888.0,"contact_point_centroid":[0.34208,0.07717,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":3.0,"phase_name":"push_more","phase_type":"push","tcp_position_centroid":[0.0997,0.01509,0.42805]}],"total_contact_groups":7},"final_pose_error":0.11576,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.10152,-0.03252,0.42661],"hinge_angle":0.67981,"initial_hinge_angle":0.15466,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.15466,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":27.75442,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":554.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"approach_handle","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":610.0,"raw_peak_contact_force":27.75442,"subtask_id":"reach_handle","tcp_end":[0.10014,0.19702,0.44007],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.49245,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":68.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":22.79673,"phase_name":"descend_to_handle","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":64.0,"raw_peak_contact_force":0.0,"tcp_end":[0.0999,0.19505,0.43158],"tcp_start":[0.10014,0.19702,0.44007],"tcp_to_object_dist_end":0.48403,"terminated_normally":true,"termination_reason":"condition_met"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":5.39863,"phase_name":"push_open","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1807.0,"raw_peak_contact_force":24.46695,"subtask_id":"push_door","tcp_end":[0.09973,0.06535,0.42978],"tcp_start":[0.0999,0.19505,0.43158],"tcp_to_object_dist_end":0.44601,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"push_more","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1515.0,"raw_peak_contact_force":25.18858,"subtask_id":"push_door","tcp_end":[0.10152,-0.03252,0.42661],"tcp_start":[0.09973,0.06535,0.42978],"tcp_to_object_dist_end":0.43973,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.13408,"average_solve_count":179.0,"average_success_count":179.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_handle.approach_speed":0.07949,"descend_to_handle.descend_speed":0.04498,"push_more.push_more_distance":0.17452,"push_more.push_more_speed":0.04888,"push_open.push_distance":0.34116,"push_open.push_speed":0.04362},"optimized_scores":{"best_composite_score":0.64,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link6","contact_count":24.0,"contact_point_centroid":[0.10275,0.15375,0.53417],"force_p95":30.82606,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":34.44462,"mean_force":18.78682,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.10015,0.22079,0.42918]},{"body_a":"door_panel","body_b":"link7","contact_count":32.0,"contact_point_centroid":[0.16536,0.14857,0.45978],"force_p95":32.29579,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":32.49463,"mean_force":19.53412,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.1001,0.20597,0.43587]},{"body_a":"door_panel","body_b":"link7","contact_count":619.0,"contact_point_centroid":[0.16471,-0.00725,0.44484],"force_p95":25.13878,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":29.89342,"mean_force":11.72013,"phase_index":3.0,"phase_name":"push_more","phase_type":"push","tcp_position_centroid":[0.09721,0.04667,0.41601]},{"body_a":"door_panel","body_b":"link7","contact_count":622.0,"contact_point_centroid":[0.16447,0.07784,0.40264],"force_p95":20.92243,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":28.3656,"mean_force":12.9637,"phase_index":2.0,"phase_name":"push_open","phase_type":"push","tcp_position_centroid":[0.09907,0.13507,0.37686]},{"body_a":"door_panel","body_b":"link7","contact_count":178.0,"contact_point_centroid":[0.16508,0.13097,0.42041],"force_p95":15.3257,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":16.48714,"mean_force":13.13005,"phase_index":1.0,"phase_name":"descend_to_handle","phase_type":"descend","tcp_position_centroid":[0.0998,0.18836,0.39635]},{"body_a":"world","body_b":"door_panel","contact_count":572.0,"contact_point_centroid":[0.3023,0.16825,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.10009,0.30066,0.39262]},{"body_a":"world","body_b":"door_panel","contact_count":564.0,"contact_point_centroid":[0.30618,0.14974,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"descend_to_handle","phase_type":"descend","tcp_position_centroid":[0.0998,0.18822,0.3956]},{"body_a":"world","body_b":"door_panel","contact_count":920.0,"contact_point_centroid":[0.31551,0.12318,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_open","phase_type":"push","tcp_position_centroid":[0.09913,0.13624,0.37596]},{"body_a":"world","body_b":"door_panel","contact_count":776.0,"contact_point_centroid":[0.3354,0.08635,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":3.0,"phase_name":"push_more","phase_type":"push","tcp_position_centroid":[0.09733,0.04596,0.41593]}],"total_contact_groups":9},"final_pose_error":0.09285,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.10268,0.00476,0.41326],"hinge_angle":0.63649,"initial_hinge_angle":0.10647,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.10647,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":34.44462,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":521.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":17.14712,"phase_name":"approach_handle","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":628.0,"raw_peak_contact_force":34.44462,"subtask_id":"reach_handle","tcp_end":[0.10011,0.19717,0.43991],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.49236,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":597.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":7.53405,"phase_name":"descend_to_handle","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":742.0,"raw_peak_contact_force":16.48714,"tcp_end":[0.0998,0.18027,0.35495],"tcp_start":[0.10011,0.19717,0.43991],"tcp_to_object_dist_end":0.41042,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":5.09122,"phase_name":"push_open","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1542.0,"raw_peak_contact_force":28.3656,"subtask_id":"push_door","tcp_end":[0.09696,0.08676,0.4079],"tcp_start":[0.0998,0.18027,0.35495],"tcp_to_object_dist_end":0.42815,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"push_more","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1395.0,"raw_peak_contact_force":29.89342,"subtask_id":"push_door","tcp_end":[0.10268,0.00476,0.41326],"tcp_start":[0.09696,0.08676,0.4079],"tcp_to_object_dist_end":0.42585,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.69027,"average_solve_count":226.0,"average_success_count":226.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_handle.approach_speed":0.06268,"descend_to_handle.descend_speed":0.0275,"push_more.push_more_distance":0.21194,"push_more.push_more_speed":0.03326,"push_open.push_distance":0.23675,"push_open.push_speed":0.03615},"optimized_scores":{"best_composite_score":0.64,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link6","contact_count":93.0,"contact_point_centroid":[0.10129,0.17135,0.52541],"force_p95":32.43427,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":34.2283,"mean_force":20.9332,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.10001,0.24243,0.41901]},{"body_a":"door_panel","body_b":"link7","contact_count":31.0,"contact_point_centroid":[0.16529,0.14832,0.45975],"force_p95":30.79946,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":31.80649,"mean_force":20.26601,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.10002,0.20572,0.43585]},{"body_a":"door_panel","body_b":"link7","contact_count":670.0,"contact_point_centroid":[0.16469,0.08508,0.39678],"force_p95":17.69789,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":24.52508,"mean_force":12.52032,"phase_index":2.0,"phase_name":"push_open","phase_type":"push","tcp_position_centroid":[0.09937,0.14234,0.37191]},{"body_a":"door_panel","body_b":"link7","contact_count":744.0,"contact_point_centroid":[0.16237,0.02255,0.43894],"force_p95":12.78371,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":21.24394,"mean_force":11.08744,"phase_index":3.0,"phase_name":"push_more","phase_type":"push","tcp_position_centroid":[0.09684,0.07979,0.40961]},{"body_a":"door_panel","body_b":"link7","contact_count":196.0,"contact_point_centroid":[0.16505,0.13047,0.41866],"force_p95":14.54958,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":15.66949,"mean_force":13.00275,"phase_index":1.0,"phase_name":"descend_to_handle","phase_type":"descend","tcp_position_centroid":[0.09976,0.18787,0.39461]},{"body_a":"world","body_b":"door_panel","contact_count":524.0,"contact_point_centroid":[0.30078,0.18175,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.10004,0.29381,0.39564]},{"body_a":"world","body_b":"door_panel","contact_count":592.0,"contact_point_centroid":[0.30621,0.14962,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"descend_to_handle","phase_type":"descend","tcp_position_centroid":[0.09977,0.18799,0.39527]},{"body_a":"world","body_b":"door_panel","contact_count":892.0,"contact_point_centroid":[0.31415,0.12598,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_open","phase_type":"push","tcp_position_centroid":[0.0994,0.14249,0.37128]},{"body_a":"world","body_b":"door_panel","contact_count":760.0,"contact_point_centroid":[0.32793,0.09787,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":3.0,"phase_name":"push_more","phase_type":"push","tcp_position_centroid":[0.0968,0.07858,0.41005]}],"total_contact_groups":9},"final_pose_error":0.15043,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.0956,0.04837,0.41909],"hinge_angle":0.55226,"initial_hinge_angle":0.01332,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.01332,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":34.2283,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":538.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"approach_handle","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":648.0,"raw_peak_contact_force":34.2283,"subtask_id":"reach_handle","tcp_end":[0.10005,0.19689,0.43994],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.49227,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":639.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"descend_to_handle","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":788.0,"raw_peak_contact_force":15.66949,"tcp_end":[0.09976,0.18025,0.35497],"tcp_start":[0.10005,0.19689,0.43994],"tcp_to_object_dist_end":0.41042,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"push_open","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1562.0,"raw_peak_contact_force":24.52508,"subtask_id":"push_door","tcp_end":[0.09841,0.11184,0.39504],"tcp_start":[0.09976,0.18025,0.35497],"tcp_to_object_dist_end":0.4222,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":10.38787,"phase_name":"push_more","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1504.0,"raw_peak_contact_force":21.24394,"subtask_id":"push_door","tcp_end":[0.0956,0.04837,0.41909],"tcp_start":[0.09841,0.11184,0.39504],"tcp_to_object_dist_end":0.43256,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
```