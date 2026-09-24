## Search State

- **Seed**: 2
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | approach → descend → push | arc_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | force_exceeded | time_limit | 6 | 1.1700 | 1.00 | ❌ rejected |
| 11 | approach → descend → push | arc_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | force_exceeded | time_limit | 6 | 1.1700 | 1.00 | ❌ rejected |
| 10 | approach → descend → push | arc_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | force_exceeded | time_limit | 6 | 1.1406 | 0.97 | ❌ rejected |
| 9 | approach → descend → push | arc_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | force_exceeded | time_limit | 6 | 1.1700 | 1.00 | ✅ accepted |
| 8 | approach → descend → push | arc_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 6 | 0.8963 | 0.89 | ❌ rejected |

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

## Parent Skill (Best Known, Q=1.170)

```yaml
skill: door_push
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: reach_handle
  anchor: fixture
  weight: 0.3
- id: push_door
  target_entity: hinge
  metric: hinge_angle
  weight: 0.7
phases:
- id: approach_handle
  type: approach
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: site
    entity: door_handle
    offset:
    - 0.0
    - 0.0
    - 0.14
    tolerance: 0.02
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
    arc_height:
      type: scalar
      range:
      - 0.02
      - 0.12
      default: 0.06
      binds_to:
      - path: generator.arc_height
        mode: replace
  guards:
  - id: contact_guard
    when: during_phase
    predicate: force_below
    threshold: 30.0
    on_failure: continue
  retries:
    max_attempts: 1
    strategy: reduce_speed
  subtask_id: reach_handle
- id: descend_to_handle
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: force_exceeded
  target:
    source: yaml
    anchor: site
    entity: door_handle
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.01
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
  - id: contact_detected
    when: after_phase
    predicate: contact_detected
    threshold: 0.0
    on_failure: retry
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
    anchor: site
    entity: door_handle
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.35
      axis: task_goal_direction
      mode: replace_offset_projection
      sign: positive
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: world_y
      tolerance: 0.15
  parameters:
    max_push_time:
      type: scalar
      range:
      - 2.0
      - 8.0
      default: 4.0
      binds_to:
      - path: duration.max_time
        mode: replace
    push_distance:
      type: scalar
      range:
      - 0.15
      - 0.5
      default: 0.35
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
  retries:
    max_attempts: 1
    strategy: reduce_speed
  subtask_id: push_door

```

## Last Evaluated Skill (Q=1.170)

```yaml
skill: door_push
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: reach_handle
  anchor: fixture
  weight: 0.3
- id: push_door
  target_entity: hinge
  metric: hinge_angle
  weight: 0.7
phases:
- id: approach_handle
  type: approach
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: site
    entity: door_handle
    offset:
    - 0.0
    - 0.0
    - 0.14
    tolerance: 0.03
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
    arc_height:
      type: scalar
      range:
      - 0.02
      - 0.12
      default: 0.06
      binds_to:
      - path: generator.arc_height
        mode: replace
  guards:
  - id: contact_guard
    when: during_phase
    predicate: force_below
    threshold: 100.0
    on_failure: continue
  retries:
    max_attempts: 1
    strategy: reduce_speed
  subtask_id: reach_handle
- id: descend_to_handle
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: force_exceeded
  target:
    source: yaml
    anchor: site
    entity: door_handle
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.01
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
  - id: contact_detected
    when: after_phase
    predicate: contact_detected
    threshold: 0.0
    on_failure: retry
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
    anchor: site
    entity: door_handle
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.35
      axis: task_goal_direction
      mode: replace_offset_projection
      sign: positive
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: world_y
      tolerance: 0.15
  parameters:
    max_push_time:
      type: scalar
      range:
      - 2.0
      - 8.0
      default: 4.0
      binds_to:
      - path: duration.max_time
        mode: replace
    push_distance:
      type: scalar
      range:
      - 0.15
      - 0.5
      default: 0.35
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
  retries:
    max_attempts: 1
    strategy: reduce_speed
  subtask_id: push_door

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_handle** (`approach`)
  - target: source=yaml, anchor=site, entity=door_handle, offset=[0.0, 0.0, 0.14], tolerance=0.03
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
    - arc_height: status=consumed; consumers=generator.arc_height (replace)
  - guards:
    - id=contact_guard, when=during_phase, predicate=force_below, on_failure=continue, threshold=100.0
  - retries: max_attempts=1, strategy=reduce_speed
- **descend_to_handle** (`descend`)
  - target: source=yaml, anchor=site, entity=door_handle, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=contact_detected, when=after_phase, predicate=contact_detected, on_failure=retry, threshold=0.0
  - retries: max_attempts=1, strategy=reduce_speed
- **push_door_closed** (`push`)
  - target: source=yaml, anchor=site, entity=door_handle, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.35, mode=replace_offset_projection, sign=positive}
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=world_y, tolerance=0.15
  - parameter_bindings:
    - max_push_time: status=consumed; consumers=duration.max_time (replace)
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=1, strategy=reduce_speed

## Design Metrics

- **Composite score**: 1.170
- **task_score** (E): 1.000
- **fitness_score**: 1.000  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.500
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.330

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_handle | 1.00 | 1.00 | 0.2287 |
| descend_to_handle | 1.00 | 1.00 | 0.0050 |
| push_door_closed | 1.00 | 0.67 | 0.0564 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_handle | approach | 1.00 / step_budget | (0.100, 0.399, 0.350)→(0.103, 0.217, 0.487) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 2.333 | 18.578 | 51.530 |
| descend_to_handle | descend | 1.00 / force_exceeded | (0.103, 0.217, 0.487)→(0.103, 0.214, 0.483) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 1.000 | 19.066 | 9.534 |
| push_door_closed | push | 1.00 / time_limit | (0.103, 0.214, 0.483)→(0.151, 0.195, 0.503) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 0.67 / 2.000 | 4.941 | 171.421 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- hinge_angle_ratio: 1.000
- arc_quality: 1.000

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 1.000
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 1.170
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.349


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.0,"average_solve_count":112.0,"average_success_count":112.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_handle.approach_speed":0.05787,"approach_handle.arc_height":0.02542,"descend_to_handle.descend_speed":0.02869,"push_door_closed.max_push_time":2.60157,"push_door_closed.push_distance":0.16326,"push_door_closed.push_speed":0.04931},"optimized_scores":{"best_composite_score":1.17,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link6","contact_count":297.0,"contact_point_centroid":[0.14355,0.05796,0.50937],"force_p95":53.27003,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":95.8971,"mean_force":18.883,"phase_index":2.0,"phase_name":"push_door_closed","phase_type":"push","tcp_position_centroid":[0.11728,0.23202,0.48293]},{"body_a":"door_panel","body_b":"link6","contact_count":83.0,"contact_point_centroid":[0.10047,0.20115,0.5705],"force_p95":44.30963,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":55.72407,"mean_force":29.29468,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.10016,0.27747,0.46233]},{"body_a":"world","body_b":"door_panel","contact_count":372.0,"contact_point_centroid":[0.29991,0.20234,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.10045,0.33368,0.41925]},{"body_a":"door_panel","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.1011,0.17031,0.58521],"force_p95":0.0,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"descend_to_handle","phase_type":"descend","tcp_position_centroid":[0.10003,0.24068,0.47895]},{"body_a":"world","body_b":"door_panel","contact_count":52.0,"contact_point_centroid":[0.30142,0.17422,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"descend_to_handle","phase_type":"descend","tcp_position_centroid":[0.09976,0.23929,0.47769]},{"body_a":"world","body_b":"door_panel","contact_count":512.0,"contact_point_centroid":[0.31756,0.11959,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_door_closed","phase_type":"push","tcp_position_centroid":[0.11336,0.2342,0.48315]}],"total_contact_groups":6},"final_pose_error":0.00526,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.13945,0.22148,0.48703],"hinge_angle":0.44254,"initial_hinge_angle":-0.08321,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":-0.08321,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":95.8971,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":364.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":19.56098,"phase_name":"approach_handle","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":455.0,"raw_peak_contact_force":55.72407,"subtask_id":"reach_handle","tcp_end":[0.10003,0.24068,0.47895],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.54528,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":45.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":28.5959,"phase_name":"descend_to_handle","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":53.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_handle","tcp_end":[0.0998,0.23752,0.47433],"tcp_start":[0.10003,0.24068,0.47895],"tcp_to_object_dist_end":0.53978,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":560.0,"n_steps_budget":630.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":10.02549,"phase_name":"push_door_closed","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":809.0,"raw_peak_contact_force":95.8971,"subtask_id":"push_door","tcp_end":[0.13945,0.22148,0.48703],"tcp_start":[0.0998,0.23752,0.47433],"tcp_to_object_dist_end":0.5529,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.68235,"average_solve_count":85.0,"average_success_count":85.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_handle.approach_speed":0.07643,"approach_handle.arc_height":0.03064,"descend_to_handle.descend_speed":0.03276,"push_door_closed.max_push_time":6.26388,"push_door_closed.push_distance":0.17078,"push_door_closed.push_speed":0.08796},"optimized_scores":{"best_composite_score":1.17,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link6","contact_count":299.0,"contact_point_centroid":[0.14543,0.08048,0.51234],"force_p95":55.35934,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":103.71952,"mean_force":18.91723,"phase_index":2.0,"phase_name":"push_door_closed","phase_type":"push","tcp_position_centroid":[0.11859,0.25498,0.48706]},{"body_a":"door_panel","body_b":"link6","contact_count":62.0,"contact_point_centroid":[0.10061,0.21474,0.57581],"force_p95":56.5116,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":66.0101,"mean_force":32.54601,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.10115,0.29419,0.46649]},{"body_a":"door_panel","body_b":"link6","contact_count":4.0,"contact_point_centroid":[0.10019,0.18812,0.58386],"force_p95":15.23101,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":15.24608,"mean_force":11.23893,"phase_index":1.0,"phase_name":"descend_to_handle","phase_type":"descend","tcp_position_centroid":[0.10104,0.2628,0.4758]},{"body_a":"world","body_b":"door_panel","contact_count":300.0,"contact_point_centroid":[0.29998,0.20633,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.10096,0.34219,0.4242]},{"body_a":"world","body_b":"door_panel","contact_count":44.0,"contact_point_centroid":[0.30039,0.184,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"descend_to_handle","phase_type":"descend","tcp_position_centroid":[0.101,0.2636,0.47755]},{"body_a":"world","body_b":"door_panel","contact_count":480.0,"contact_point_centroid":[0.3127,0.13201,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_door_closed","phase_type":"push","tcp_position_centroid":[0.1114,0.25868,0.48598]}],"total_contact_groups":6},"final_pose_error":0.00588,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.13913,0.24433,0.49281],"hinge_angle":0.38766,"initial_hinge_angle":-0.14464,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":-0.14464,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":103.71952,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":329.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":20.98647,"phase_name":"approach_handle","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":362.0,"raw_peak_contact_force":66.0101,"subtask_id":"reach_handle","tcp_end":[0.1013,0.26525,0.47922],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.55702,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":45.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":15.24608,"phase_name":"descend_to_handle","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":48.0,"raw_peak_contact_force":15.24608,"subtask_id":"reach_handle","tcp_end":[0.10094,0.26184,0.47442],"tcp_start":[0.1013,0.26525,0.47922],"tcp_to_object_dist_end":0.5512,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":533.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":4.79647,"phase_name":"push_door_closed","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":779.0,"raw_peak_contact_force":103.71952,"subtask_id":"push_door","tcp_end":[0.13913,0.24433,0.49281],"tcp_start":[0.10094,0.26184,0.47442],"tcp_to_object_dist_end":0.56738,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.17197,"average_solve_count":157.0,"average_success_count":157.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_handle.approach_speed":0.01029,"approach_handle.arc_height":0.09044,"descend_to_handle.descend_speed":0.01801,"push_door_closed.max_push_time":5.04944,"push_door_closed.push_distance":0.18027,"push_door_closed.push_speed":0.04798},"optimized_scores":{"best_composite_score":1.17,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link6","contact_count":516.0,"contact_point_centroid":[0.17327,-0.0278,0.54978],"force_p95":172.86364,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":314.64712,"mean_force":97.78295,"phase_index":2.0,"phase_name":"push_door_closed","phase_type":"push","tcp_position_centroid":[0.13563,0.11813,0.55522]},{"body_a":"door_panel","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.17279,0.08579,0.52],"force_p95":74.48254,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":75.73363,"mean_force":63.22272,"phase_index":2.0,"phase_name":"push_door_closed","phase_type":"push","tcp_position_centroid":[0.10721,0.14315,0.49679]},{"body_a":"door_panel","body_b":"link7","contact_count":82.0,"contact_point_centroid":[0.17165,0.12126,0.53549],"force_p95":29.80644,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":32.85682,"mean_force":22.09042,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.10654,0.17858,0.51148]},{"body_a":"door_panel","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.17235,0.08744,0.52525],"force_p95":12.01925,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":13.35473,"mean_force":4.45158,"phase_index":1.0,"phase_name":"descend_to_handle","phase_type":"descend","tcp_position_centroid":[0.10728,0.14505,0.50121]},{"body_a":"door_panel","body_b":"link6","contact_count":9.0,"contact_point_centroid":[0.10498,0.138,0.62103],"force_p95":0.0,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.10594,0.20445,0.51591]},{"body_a":"world","body_b":"door_panel","contact_count":628.0,"contact_point_centroid":[0.305,0.15545,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.10325,0.29945,0.4587]},{"body_a":"world","body_b":"door_panel","contact_count":36.0,"contact_point_centroid":[0.31425,0.12519,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"descend_to_handle","phase_type":"descend","tcp_position_centroid":[0.10725,0.14464,0.50081]},{"body_a":"world","body_b":"door_panel","contact_count":716.0,"contact_point_centroid":[0.34074,0.08075,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_door_closed","phase_type":"push","tcp_position_centroid":[0.13387,0.12211,0.54605]}],"total_contact_groups":8},"final_pose_error":0.02746,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.17519,0.11898,0.53051],"hinge_angle":0.71234,"initial_hinge_angle":0.15466,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.15466,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":314.64712,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":583.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":15.18592,"phase_name":"approach_handle","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":719.0,"raw_peak_contact_force":32.85682,"subtask_id":"reach_handle","tcp_end":[0.10727,0.14579,0.50219],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.53381,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":26.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":13.35473,"phase_name":"descend_to_handle","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":39.0,"raw_peak_contact_force":13.35473,"subtask_id":"reach_handle","tcp_end":[0.10736,0.14386,0.49928],"tcp_start":[0.10727,0.14579,0.50219],"tcp_to_object_dist_end":0.53056,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":842.0,"n_steps_budget":900.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"push_door_closed","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1234.0,"raw_peak_contact_force":314.64712,"subtask_id":"push_door","tcp_end":[0.17519,0.11898,0.53051],"tcp_start":[0.10736,0.14386,0.49928],"tcp_to_object_dist_end":0.57121,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
```