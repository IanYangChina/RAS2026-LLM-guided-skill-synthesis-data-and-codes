## Search State

- **Seed**: 2
- **Iteration**: 15 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 14 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | time_limit | 7 | 1.0644 | 1.00 | ❌ rejected |
| 13 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | time_limit | 7 | 1.1200 | 1.00 | ❌ rejected |
| 12 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | time_limit | 7 | 1.1200 | 1.00 | ❌ rejected |
| 11 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | time_limit | 7 | 1.1200 | 1.00 | ❌ rejected |
| 10 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | time_limit | 7 | 1.1200 | 1.00 | ❌ rejected |

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
- Frozen realised-scene SHA-256: `6dd40fac67fc7b4cb952edf7b79ea329c0b46aa4cb26369fc447c16f02a37d6d`
- Frozen initial hinge angle: -0.083 rad
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
  frozen_initial_hinge_angle_rad: -0.0832
  frozen_fixtures: {'door_panel': [0.5, 0.2, 0.0]}
  door_hinge_axis: [0, 0, 1]
  goal_tolerance_m: 0.05
  force_limit_n: 30
  force_scale_n: 5
  target_hinge_angle_rad: 0.524
  realized_scene_sha256: 6dd40fac67fc7b4cb952edf7b79ea329c0b46aa4cb26369fc447c16f02a37d6d

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

## Current Skill (Q=1.064) — your mutation base

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
- id: approach_clearance
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
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: add
  subtask_id: reach_handle
- id: contact_handle
  type: descend
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
  parameters:
    contact_force:
      type: scalar
      range:
      - 5.0
      - 25.0
      default: 15.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    descend_speed:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: add
  guards:
  - id: contact_check
    when: during_phase
    predicate: contact_detected
    threshold: 1.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - -0.02
    - 0.0
  subtask_id: reach_handle
- id: push_door
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
    - 0.0
    offset_along_axis:
      distance: 0.3
      axis: world_y
      mode: add_to_offset
      sign: negative
    tolerance: 0.05
  parameters:
    force_guard_threshold:
      type: scalar
      range:
      - 30.0
      - 50.0
      default: 45.0
      binds_to:
      - path: guards.force_limit.threshold
        mode: replace
    max_time:
      type: scalar
      range:
      - 0.5
      - 3.0
      default: 2.0
      binds_to:
      - path: duration.max_time
        mode: replace
    push_distance:
      type: scalar
      range:
      - 0.05
      - 0.5
      default: 0.3
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: add
  guards:
  - id: force_limit
    when: during_phase
    predicate: force_below
    threshold: 45.0
    on_failure: abort
  retries:
    max_attempts: 1
    strategy: offset_target
    offset:
    - 0.0
    - -0.02
    - 0.0
  subtask_id: open_door

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_clearance** (`approach`)
  - target: source=yaml, anchor=site, entity=door_handle, offset=[0.0, 0.0, 0.1], tolerance=0.02
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (add)
- **contact_handle** (`descend`)
  - target: source=yaml, anchor=site, entity=door_handle, offset=[0.0, 0.0, 0.0]
  - parameter_bindings:
    - contact_force: status=consumed; consumers=termination.force_threshold (replace)
    - descend_speed: status=consumed; consumers=generator.speed (add)
  - guards:
    - id=contact_check, when=during_phase, predicate=contact_detected, on_failure=retry, threshold=1.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, -0.02, 0.0]
- **push_door** (`push`)
  - target: source=yaml, anchor=site, entity=door_handle, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_y, distance=0.3, mode=add_to_offset, sign=negative}, tolerance=0.05
  - parameter_bindings:
    - force_guard_threshold: status=consumed; consumers=guards.force_limit.threshold (replace)
    - max_time: status=consumed; consumers=duration.max_time (replace)
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (add)
  - guards:
    - id=force_limit, when=during_phase, predicate=force_below, on_failure=abort, threshold=45.0
  - retries: max_attempts=1, strategy=offset_target, offset=[0.0, -0.02, 0.0]

## Design Metrics

- **Composite score**: 1.064
- **task_score** (E): 1.000
- **fitness_score**: 1.000  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.444
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.380

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_clearance | 1.00 | 1.00 | 0.2133 |
| contact_handle | 1.00 | 0.33 | 0.0430 |
| push_door | 0.67 | 1.00 | 0.1314 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_clearance | approach | 1.00 / step_budget | (0.100, 0.399, 0.350)→(0.103, 0.207, 0.439) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 2.333 | 20.582 | 16.660 |
| contact_handle | descend | 1.00 / force_exceeded | (0.103, 0.207, 0.439)→(0.111, 0.176, 0.411) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 0.33 / 0.333 | 15.341 | 33.323 |
| push_door | push | 0.67 / time_limit | (0.111, 0.176, 0.411)→(0.116, 0.048, 0.388) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 2.333 | 15.494 | 40.344 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- hinge_angle_ratio: 1.000
- arc_quality: 1.000

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 1.000
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 1.120
- **K-run variance**: 0.0062
- **Stagnated**: no
- **Stop reason**: tolflatfitness
- **Mean generations**: 4.0
- **Final σ (mean)**: 0.266


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
{"anchors":[{"name":"fixture","value":[0.5,0.2,0.0]}],"axes":[{"name":"door_hinge_axis","value":[0.0,0.0,1.0]}],"door":{"hinge_axis":[0.0,0.0,1.0],"initial_hinge_angle":-0.08321,"panel":{"name":"door_panel","orientation":[0.99913,0.0,0.0,-0.04159],"position":[0.5,0.2,0.0]},"target_hinge_angle":0.524},"fixture_states":[],"fixtures":[{"name":"door_panel","orientation":[0.99913,0.0,0.0,-0.04159],"position":[0.5,0.2,0.0]}],"limits":[{"name":"goal_tolerance_m","value":0.05},{"name":"force_limit_n","value":30.0},{"name":"force_scale_n","value":5.0},{"name":"target_hinge_angle_rad","value":0.524}],"object_starts":[],"obstacles":[],"targets":[],"task_name":"door_push"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.85567,"average_solve_count":97.0,"average_success_count":97.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_clearance.approach_speed":0.08828,"contact_handle.contact_force":10.28989,"contact_handle.descend_speed":0.04994,"push_door.force_guard_threshold":44.88831,"push_door.max_time":1.31402,"push_door.push_distance":0.21368,"push_door.push_speed":0.07205},"optimized_scores":{"best_composite_score":1.12,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link7","contact_count":109.0,"contact_point_centroid":[0.1461,0.19536,0.46352],"force_p95":34.83187,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":35.69835,"mean_force":20.27036,"phase_index":0.0,"phase_name":"approach_clearance","phase_type":"approach","tcp_position_centroid":[0.09992,0.26008,0.42228]},{"body_a":"door_panel","body_b":"link7","contact_count":773.0,"contact_point_centroid":[0.13808,0.0942,0.46188],"force_p95":18.18303,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":26.59076,"mean_force":12.16877,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.10064,0.16211,0.41665]},{"body_a":"door_panel","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.14188,0.16083,0.47989],"force_p95":14.92306,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":15.0058,"mean_force":9.72808,"phase_index":1.0,"phase_name":"contact_handle","phase_type":"descend","tcp_position_centroid":[0.09984,0.2284,0.43748]},{"body_a":"door_panel","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.10132,0.23241,0.51614],"force_p95":0.0,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_clearance","phase_type":"approach","tcp_position_centroid":[0.09996,0.29034,0.40599]},{"body_a":"world","body_b":"door_panel","contact_count":496.0,"contact_point_centroid":[0.30002,0.20059,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_clearance","phase_type":"approach","tcp_position_centroid":[0.09989,0.31522,0.39265]},{"body_a":"world","body_b":"door_panel","contact_count":32.0,"contact_point_centroid":[0.30229,0.16819,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"contact_handle","phase_type":"descend","tcp_position_centroid":[0.09976,0.22867,0.43797]},{"body_a":"world","body_b":"door_panel","contact_count":932.0,"contact_point_centroid":[0.31247,0.13269,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.10073,0.15678,0.41514]}],"total_contact_groups":7},"final_pose_error":0.17484,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.10175,0.09077,0.39642],"hinge_angle":0.45429,"initial_hinge_angle":-0.08321,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":-0.08321,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":35.69835,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":454.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":14.17845,"phase_name":"approach_clearance","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":35.0,"raw_peak_contact_force":15.0058,"subtask_id":"reach_handle","tcp_end":[0.09994,0.22966,0.43876],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.50521,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":23.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"contact_handle","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1705.0,"raw_peak_contact_force":26.59076,"subtask_id":"reach_handle","tcp_end":[0.09979,0.22762,0.43668],"tcp_start":[0.09994,0.22966,0.43876],"tcp_to_object_dist_end":0.50245,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":15.52222,"phase_name":"push_door","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":606.0,"raw_peak_contact_force":35.69835,"subtask_id":"open_door","tcp_end":[0.10175,0.09077,0.39642],"tcp_start":[0.09979,0.22762,0.43668],"tcp_to_object_dist_end":0.41922,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `0106e02cd8847cdbc8cb80732350ffe717d1fc22c509bf8221b103cb157c8e2d`; realized-scene SHA-256: `a535d88ef07b74838c5ab0400d8932f8a62343284dc305f72bf16a3002d4504f`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"fixture","value":[0.5,0.2,0.0]}],"axes":[{"name":"door_hinge_axis","value":[0.0,0.0,1.0]}],"door":{"hinge_axis":[0.0,0.0,1.0],"initial_hinge_angle":-0.14464,"panel":{"name":"door_panel","orientation":[0.99739,0.0,0.0,-0.07225],"position":[0.5,0.2,0.0]},"target_hinge_angle":0.524},"fixture_states":[],"fixtures":[{"name":"door_panel","orientation":[0.99739,0.0,0.0,-0.07225],"position":[0.5,0.2,0.0]}],"limits":[{"name":"goal_tolerance_m","value":0.05},{"name":"force_limit_n","value":30.0},{"name":"force_scale_n","value":5.0},{"name":"target_hinge_angle_rad","value":0.524}],"object_starts":[],"obstacles":[],"targets":[],"task_name":"door_push"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.86747,"average_solve_count":83.0,"average_success_count":83.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_clearance.approach_speed":0.09442,"contact_handle.contact_force":8.82583,"contact_handle.descend_speed":0.0679,"push_door.force_guard_threshold":49.79783,"push_door.max_time":2.07482,"push_door.push_distance":0.39773,"push_door.push_speed":0.08198},"optimized_scores":{"best_composite_score":1.12,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link6","contact_count":16.0,"contact_point_centroid":[0.10165,0.23565,0.52035],"force_p95":46.98941,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":51.29202,"mean_force":26.71604,"phase_index":0.0,"phase_name":"approach_clearance","phase_type":"approach","tcp_position_centroid":[0.10086,0.29581,0.4113]},{"body_a":"door_panel","body_b":"link7","contact_count":72.0,"contact_point_centroid":[0.14803,0.20743,0.46591],"force_p95":34.83995,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":36.40131,"mean_force":19.29668,"phase_index":0.0,"phase_name":"approach_clearance","phase_type":"approach","tcp_position_centroid":[0.10108,0.27227,0.42592]},{"body_a":"door_panel","body_b":"link7","contact_count":818.0,"contact_point_centroid":[0.13853,0.11481,0.46675],"force_p95":17.31195,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":27.35424,"mean_force":12.31125,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.10093,0.18324,0.42213]},{"body_a":"door_panel","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.14594,0.18619,0.47802],"force_p95":11.91236,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":13.23596,"mean_force":4.41199,"phase_index":1.0,"phase_name":"contact_handle","phase_type":"descend","tcp_position_centroid":[0.10119,0.25293,0.43712]},{"body_a":"world","body_b":"door_panel","contact_count":376.0,"contact_point_centroid":[0.3,0.20514,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_clearance","phase_type":"approach","tcp_position_centroid":[0.10062,0.32221,0.39506]},{"body_a":"world","body_b":"door_panel","contact_count":36.0,"contact_point_centroid":[0.30056,0.18201,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"contact_handle","phase_type":"descend","tcp_position_centroid":[0.10113,0.25286,0.43716]},{"body_a":"world","body_b":"door_panel","contact_count":924.0,"contact_point_centroid":[0.30852,0.1457,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.10092,0.18354,0.4222]}],"total_contact_groups":7},"final_pose_error":0.35097,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.10094,0.1114,0.40947],"hinge_angle":0.40666,"initial_hinge_angle":-0.14464,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":-0.14464,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":51.29202,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":407.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":13.23596,"phase_name":"approach_clearance","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":39.0,"raw_peak_contact_force":13.23596,"subtask_id":"reach_handle","tcp_end":[0.1013,0.25353,0.43764],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.51582,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":20.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"contact_handle","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1742.0,"raw_peak_contact_force":27.35424,"subtask_id":"reach_handle","tcp_end":[0.10106,0.25174,0.43583],"tcp_start":[0.1013,0.25353,0.43764],"tcp_to_object_dist_end":0.51336,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":16.18172,"phase_name":"push_door","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":464.0,"raw_peak_contact_force":51.29202,"subtask_id":"open_door","tcp_end":[0.10094,0.1114,0.40947],"tcp_start":[0.10106,0.25174,0.43583],"tcp_to_object_dist_end":0.4362,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `7bc2b9dece282a8a9fabbafdd09525b72694e2e86202e4d7347d50b4ed50bf95`; realized-scene SHA-256: `93d761ce3dc4e78ce09d05c5eb184a7129267f8d2172dd2a5cd042d5ec0710b9`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"fixture","value":[0.5,0.2,0.0]}],"axes":[{"name":"door_hinge_axis","value":[0.0,0.0,1.0]}],"door":{"hinge_axis":[0.0,0.0,1.0],"initial_hinge_angle":0.15466,"panel":{"name":"door_panel","orientation":[0.99701,0.0,0.0,0.07725],"position":[0.5,0.2,0.0]},"target_hinge_angle":0.524},"fixture_states":[],"fixtures":[{"name":"door_panel","orientation":[0.99701,0.0,0.0,0.07725],"position":[0.5,0.2,0.0]}],"limits":[{"name":"goal_tolerance_m","value":0.05},{"name":"force_limit_n","value":30.0},{"name":"force_scale_n","value":5.0},{"name":"target_hinge_angle_rad","value":0.524}],"object_starts":[],"obstacles":[],"targets":[],"task_name":"door_push"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.71329,"average_solve_count":143.0,"average_success_count":143.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_clearance.approach_speed":0.08537,"contact_handle.contact_force":21.962,"contact_handle.descend_speed":0.0568,"push_door.force_guard_threshold":44.5957,"push_door.max_time":2.02171,"push_door.push_distance":0.31967,"push_door.push_speed":0.10636},"optimized_scores":{"best_composite_score":0.95333,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link6","contact_count":6.0,"contact_point_centroid":[0.24104,-0.04277,0.44899],"force_p95":38.50552,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":46.02389,"mean_force":20.65599,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.14503,-0.05896,0.35732]},{"body_a":"door_panel","body_b":"link7","contact_count":285.0,"contact_point_centroid":[0.20112,-0.04479,0.39125],"force_p95":19.52779,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":40.59605,"mean_force":13.5889,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.13786,0.0081,0.36187]},{"body_a":"door_panel","body_b":"link7","contact_count":130.0,"contact_point_centroid":[0.14184,0.1072,0.47264],"force_p95":31.35903,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":34.04214,"mean_force":18.21253,"phase_index":0.0,"phase_name":"approach_clearance","phase_type":"approach","tcp_position_centroid":[0.10663,0.17663,0.42753]},{"body_a":"door_panel","body_b":"link7","contact_count":629.0,"contact_point_centroid":[0.17132,0.02795,0.43046],"force_p95":17.62258,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":21.73754,"mean_force":13.41508,"phase_index":1.0,"phase_name":"contact_handle","phase_type":"descend","tcp_position_centroid":[0.11942,0.09003,0.3964]},{"body_a":"world","body_b":"door_panel","contact_count":660.0,"contact_point_centroid":[0.30549,0.15377,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_clearance","phase_type":"approach","tcp_position_centroid":[0.10361,0.27421,0.39252]},{"body_a":"world","body_b":"door_panel","contact_count":912.0,"contact_point_centroid":[0.32744,0.09948,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"contact_handle","phase_type":"descend","tcp_position_centroid":[0.11882,0.0924,0.39869]},{"body_a":"world","body_b":"door_panel","contact_count":492.0,"contact_point_centroid":[0.35259,0.0648,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.13855,0.003,0.36185]}],"total_contact_groups":7},"final_pose_error":0.30657,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.14511,-0.05948,0.35725],"hinge_angle":0.75453,"initial_hinge_angle":0.15466,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.15466,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":46.02389,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":644.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":34.3311,"phase_name":"approach_clearance","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1541.0,"raw_peak_contact_force":21.73754,"subtask_id":"reach_handle","tcp_end":[0.10788,0.1367,0.44203],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.4751,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":969.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":46.02389,"phase_name":"contact_handle","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":783.0,"raw_peak_contact_force":46.02389,"subtask_id":"reach_handle","tcp_end":[0.13148,0.04837,0.35902],"tcp_start":[0.10788,0.1367,0.44203],"tcp_to_object_dist_end":0.38538,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":636.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":14.77939,"phase_name":"push_door","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":790.0,"raw_peak_contact_force":34.04214,"subtask_id":"open_door","tcp_end":[0.14511,-0.05948,0.35725],"tcp_start":[0.13148,0.04837,0.35902],"tcp_to_object_dist_end":0.39015,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```