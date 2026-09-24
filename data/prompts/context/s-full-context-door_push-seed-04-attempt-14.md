## Search State

- **Seed**: 4
- **Iteration**: 15 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 14 | approach → descend → push → push | linear_cartesian | linear_cartesian | impedance_motion | impedance_motion | position_control | position_control | impedance_control | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | 0.8400 | 1.00 | ❌ rejected |
| 13 | approach → descend → push → push → approach | linear_cartesian | linear_cartesian | impedance_motion | impedance_motion | linear_cartesian | position_control | position_control | impedance_control | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.7019 | 0.99 | ❌ rejected |
| 12 | approach → descend → push → push | linear_cartesian | linear_cartesian | impedance_motion | impedance_motion | position_control | position_control | impedance_control | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | 0.8400 | 1.00 | ❌ rejected |
| 11 | approach → descend → push → push | linear_cartesian | linear_cartesian | impedance_motion | impedance_motion | position_control | position_control | impedance_control | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | 0.8400 | 1.00 | ✅ accepted |
| 10 | approach → descend → push | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | position_control | time_limit | time_limit | time_limit | 4 | 0.5294 | 0.76 | ❌ rejected |

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

## Current Skill (Q=0.840) — your mutation base

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
  termination: force_exceeded
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
    contact_force_threshold:
      type: scalar
      range:
      - 3.0
      - 10.0
      default: 5.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    descend_speed:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
- id: push_primary
  type: push
  generator: impedance_motion
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.4
      axis: world_y
      mode: replace_offset_projection
      sign: negative
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.2
      - 0.5
      default: 0.4
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.02
      - 0.08
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: force_guard_primary
    when: during_phase
    predicate: force_below
    threshold: 30.0
    on_failure: retry
  retries:
    max_attempts: 1
    strategy: reduce_speed
  subtask_id: push_door
- id: push_secondary
  type: push
  generator: impedance_motion
  control: impedance_control
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
      mode: replace_offset_projection
      sign: negative
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    push_extra_distance:
      type: scalar
      range:
      - 0.1
      - 0.4
      default: 0.2
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_extra_speed:
      type: scalar
      range:
      - 0.02
      - 0.08
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: force_guard_secondary
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
    - contact_force_threshold: status=consumed; consumers=termination.force_threshold (replace)
    - descend_speed: status=consumed; consumers=generator.speed (replace)
- **push_primary** (`push`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_y, distance=0.4, mode=replace_offset_projection, sign=negative}, tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=force_guard_primary, when=during_phase, predicate=force_below, on_failure=retry, threshold=30.0
  - retries: max_attempts=1, strategy=reduce_speed
- **push_secondary** (`push`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_y, distance=0.2, mode=replace_offset_projection, sign=negative}, tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_extra_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_extra_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=force_guard_secondary, when=during_phase, predicate=force_below, on_failure=retry, threshold=30.0
  - retries: max_attempts=1, strategy=reduce_speed

## Design Metrics

- **Composite score**: 0.840
- **task_score** (E): 1.000
- **fitness_score**: 1.000  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.250
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.410

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_handle | 1.00 | 1.00 | 0.2214 |
| descend_to_handle | 1.00 | 1.00 | 0.0049 |
| push_primary | 0.33 | 0.33 | 0.2098 |
| push_secondary | 0.00 | 0.33 | 0.1217 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_handle | approach | 1.00 / step_budget | (0.100, 0.399, 0.350)→(0.100, 0.197, 0.440) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 1.000 | 5.603 | 33.797 |
| descend_to_handle | descend | 1.00 / force_exceeded | (0.100, 0.197, 0.440)→(0.100, 0.196, 0.435) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 2.333 | 12.698 | 9.862 |
| push_primary | push | 0.33 / step_budget | (0.100, 0.196, 0.435)→(0.100, -0.014, 0.434) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 0.33 / 1.333 | 0.000 | 25.001 |
| push_secondary | push | 0.00 / step_budget | (0.100, -0.014, 0.434)→(0.104, -0.136, 0.430) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 0.33 / 1.333 | 0.000 | 24.089 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- hinge_angle_ratio: 1.000
- arc_quality: 0.500

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 1.000
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.840
- **K-run variance**: 0.0000
- **Stagnated**: yes
  → Parameter optimiser converged to local optimum; structural change likely needed
- **Stop reason**: tolfun
- **Mean generations**: 4.0
- **Final σ (mean)**: 0.278


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.22066,"average_solve_count":213.0,"average_success_count":213.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_handle.approach_speed":0.06023,"descend_to_handle.contact_force_threshold":8.9367,"descend_to_handle.descend_speed":0.0284,"push_primary.push_distance":0.34596,"push_primary.push_speed":0.05652,"push_secondary.push_extra_distance":0.27978,"push_secondary.push_extra_speed":0.05986},"optimized_scores":{"best_composite_score":0.84,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link7","contact_count":20.0,"contact_point_centroid":[0.16538,0.1452,0.46151],"force_p95":28.59689,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":32.83456,"mean_force":20.49871,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.10017,0.20249,0.43764]},{"body_a":"door_panel","body_b":"link7","contact_count":692.0,"contact_point_centroid":[0.16781,0.03979,0.45904],"force_p95":24.52195,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":26.14827,"mean_force":14.06531,"phase_index":2.0,"phase_name":"push_primary","phase_type":"push","tcp_position_centroid":[0.09982,0.0939,0.43354]},{"body_a":"door_panel","body_b":"link7","contact_count":181.0,"contact_point_centroid":[0.19115,-0.05408,0.44636],"force_p95":20.53796,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":23.63004,"mean_force":11.42539,"phase_index":3.0,"phase_name":"push_secondary","phase_type":"push","tcp_position_centroid":[0.10221,-0.03993,0.43062]},{"body_a":"door_panel","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.16528,0.13909,0.46241],"force_p95":13.28621,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":14.76246,"mean_force":4.92082,"phase_index":1.0,"phase_name":"descend_to_handle","phase_type":"descend","tcp_position_centroid":[0.10003,0.19656,0.43852]},{"body_a":"world","body_b":"door_panel","contact_count":572.0,"contact_point_centroid":[0.30389,0.15951,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.1001,0.30272,0.39174]},{"body_a":"world","body_b":"door_panel","contact_count":36.0,"contact_point_centroid":[0.30512,0.15396,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"descend_to_handle","phase_type":"descend","tcp_position_centroid":[0.09993,0.19635,0.43789]},{"body_a":"world","body_b":"door_panel","contact_count":928.0,"contact_point_centroid":[0.32597,0.10518,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_primary","phase_type":"push","tcp_position_centroid":[0.09982,0.09033,0.43356]},{"body_a":"world","body_b":"door_panel","contact_count":872.0,"contact_point_centroid":[0.35306,0.06398,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":3.0,"phase_name":"push_secondary","phase_type":"push","tcp_position_centroid":[0.10438,-0.0794,0.42911]}],"total_contact_groups":8},"final_pose_error":0.15742,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.10351,-0.13737,0.42981],"hinge_angle":0.68946,"initial_hinge_angle":0.15466,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.15466,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":32.83456,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":546.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"approach_handle","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":592.0,"raw_peak_contact_force":32.83456,"subtask_id":"reach_handle","tcp_end":[0.10013,0.197,0.44007],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.49244,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":40.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":14.76246,"phase_name":"descend_to_handle","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":39.0,"raw_peak_contact_force":14.76246,"tcp_end":[0.09991,0.19578,0.43518],"tcp_start":[0.10013,0.197,0.44007],"tcp_to_object_dist_end":0.48754,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"push_primary","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1620.0,"raw_peak_contact_force":26.14827,"subtask_id":"push_door","tcp_end":[0.09981,-0.01492,0.43365],"tcp_start":[0.09991,0.19578,0.43518],"tcp_to_object_dist_end":0.44524,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"push_secondary","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1053.0,"raw_peak_contact_force":23.63004,"subtask_id":"push_door","tcp_end":[0.10351,-0.13737,0.42981],"tcp_start":[0.09981,-0.01492,0.43365],"tcp_to_object_dist_end":0.46295,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.3907,"average_solve_count":215.0,"average_success_count":215.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_handle.approach_speed":0.06208,"descend_to_handle.contact_force_threshold":6.41081,"descend_to_handle.descend_speed":0.02572,"push_primary.push_distance":0.31994,"push_primary.push_speed":0.04355,"push_secondary.push_extra_distance":0.24492,"push_secondary.push_extra_speed":0.06084},"optimized_scores":{"best_composite_score":0.84,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link6","contact_count":26.0,"contact_point_centroid":[0.10278,0.15349,0.53426],"force_p95":28.84722,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":31.99122,"mean_force":18.67936,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.10013,0.22048,0.4293]},{"body_a":"door_panel","body_b":"link7","contact_count":31.0,"contact_point_centroid":[0.16533,0.14839,0.45979],"force_p95":29.92817,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":31.57831,"mean_force":19.9006,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.10007,0.20582,0.4359]},{"body_a":"door_panel","body_b":"link7","contact_count":686.0,"contact_point_centroid":[0.16776,0.04019,0.46003],"force_p95":23.99003,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":25.27999,"mean_force":14.28396,"phase_index":2.0,"phase_name":"push_primary","phase_type":"push","tcp_position_centroid":[0.09976,0.09429,0.43457]},{"body_a":"door_panel","body_b":"link7","contact_count":189.0,"contact_point_centroid":[0.19074,-0.05358,0.44783],"force_p95":18.58686,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":23.71809,"mean_force":10.56702,"phase_index":3.0,"phase_name":"push_secondary","phase_type":"push","tcp_position_centroid":[0.10192,-0.03914,0.43185]},{"body_a":"world","body_b":"door_panel","contact_count":576.0,"contact_point_centroid":[0.30232,0.16816,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.10008,0.3023,0.39186]},{"body_a":"door_panel","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.16529,0.1395,0.46385],"force_p95":0.0,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"descend_to_handle","phase_type":"descend","tcp_position_centroid":[0.10003,0.19692,0.43998]},{"body_a":"world","body_b":"door_panel","contact_count":40.0,"contact_point_centroid":[0.30508,0.15409,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"descend_to_handle","phase_type":"descend","tcp_position_centroid":[0.09988,0.19645,0.4383]},{"body_a":"world","body_b":"door_panel","contact_count":820.0,"contact_point_centroid":[0.32467,0.10718,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_primary","phase_type":"push","tcp_position_centroid":[0.09977,0.09637,0.43457]},{"body_a":"world","body_b":"door_panel","contact_count":876.0,"contact_point_centroid":[0.35296,0.06409,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":3.0,"phase_name":"push_secondary","phase_type":"push","tcp_position_centroid":[0.1043,-0.07565,0.43026]}],"total_contact_groups":9},"final_pose_error":0.12102,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.10355,-0.13819,0.43087],"hinge_angle":0.68871,"initial_hinge_angle":0.10647,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.10647,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":31.99122,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":537.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"approach_handle","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":633.0,"raw_peak_contact_force":31.99122,"subtask_id":"reach_handle","tcp_end":[0.10006,0.19699,0.43993],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.4923,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":32.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":8.50632,"phase_name":"descend_to_handle","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":42.0,"raw_peak_contact_force":0.0,"tcp_end":[0.09986,0.19601,0.43621],"tcp_start":[0.10006,0.19699,0.43993],"tcp_to_object_dist_end":0.48853,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"push_primary","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1506.0,"raw_peak_contact_force":25.27999,"subtask_id":"push_door","tcp_end":[0.09976,-0.01417,0.4347],"tcp_start":[0.09986,0.19601,0.43621],"tcp_to_object_dist_end":0.44622,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"push_secondary","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1065.0,"raw_peak_contact_force":23.71809,"subtask_id":"push_door","tcp_end":[0.10355,-0.13819,0.43087],"tcp_start":[0.09976,-0.01417,0.4347],"tcp_to_object_dist_end":0.46419,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.41026,"average_solve_count":234.0,"average_success_count":234.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_handle.approach_speed":0.06902,"descend_to_handle.contact_force_threshold":6.68118,"descend_to_handle.descend_speed":0.03078,"push_primary.push_distance":0.24516,"push_primary.push_speed":0.03975,"push_secondary.push_extra_distance":0.26362,"push_secondary.push_extra_speed":0.05629},"optimized_scores":{"best_composite_score":0.84,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link6","contact_count":93.0,"contact_point_centroid":[0.10134,0.17108,0.52557],"force_p95":33.03095,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":36.56528,"mean_force":20.3496,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.10002,0.24204,0.4192]},{"body_a":"door_panel","body_b":"link7","contact_count":35.0,"contact_point_centroid":[0.16529,0.14834,0.45976],"force_p95":29.30911,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":32.96315,"mean_force":19.12157,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.10002,0.20573,0.43586]},{"body_a":"door_panel","body_b":"link7","contact_count":197.0,"contact_point_centroid":[0.19112,-0.05405,0.4451],"force_p95":18.42898,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":24.91806,"mean_force":10.31746,"phase_index":3.0,"phase_name":"push_secondary","phase_type":"push","tcp_position_centroid":[0.10225,-0.03973,0.42951]},{"body_a":"door_panel","body_b":"link7","contact_count":659.0,"contact_point_centroid":[0.16745,0.04395,0.45803],"force_p95":22.38206,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":23.57388,"mean_force":14.49822,"phase_index":2.0,"phase_name":"push_primary","phase_type":"push","tcp_position_centroid":[0.09972,0.09845,0.43259]},{"body_a":"door_panel","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.16521,0.13908,0.46197],"force_p95":13.34252,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":14.82503,"mean_force":4.94168,"phase_index":1.0,"phase_name":"descend_to_handle","phase_type":"descend","tcp_position_centroid":[0.09993,0.1965,0.43807]},{"body_a":"world","body_b":"door_panel","contact_count":524.0,"contact_point_centroid":[0.30087,0.18124,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.10005,0.29211,0.39642]},{"body_a":"world","body_b":"door_panel","contact_count":28.0,"contact_point_centroid":[0.30511,0.15396,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"descend_to_handle","phase_type":"descend","tcp_position_centroid":[0.09985,0.19624,0.43716]},{"body_a":"world","body_b":"door_panel","contact_count":1016.0,"contact_point_centroid":[0.32664,0.10374,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_primary","phase_type":"push","tcp_position_centroid":[0.09972,0.08706,0.43258]},{"body_a":"world","body_b":"door_panel","contact_count":804.0,"contact_point_centroid":[0.35337,0.06364,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":3.0,"phase_name":"push_secondary","phase_type":"push","tcp_position_centroid":[0.10459,-0.07733,0.42786]}],"total_contact_groups":9},"final_pose_error":0.14543,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.10372,-0.13107,0.42859],"hinge_angle":0.69092,"initial_hinge_angle":0.01332,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.01332,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":36.56528,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":532.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":16.80951,"phase_name":"approach_handle","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":652.0,"raw_peak_contact_force":36.56528,"subtask_id":"reach_handle","tcp_end":[0.10003,0.197,0.43989],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.49226,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":44.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":14.82503,"phase_name":"descend_to_handle","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":31.0,"raw_peak_contact_force":14.82503,"tcp_end":[0.09981,0.19562,0.4342],"tcp_start":[0.10003,0.197,0.43989],"tcp_to_object_dist_end":0.48658,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"push_primary","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1675.0,"raw_peak_contact_force":23.57388,"subtask_id":"push_door","tcp_end":[0.09975,-0.01276,0.43272],"tcp_start":[0.09981,0.19562,0.4342],"tcp_to_object_dist_end":0.44425,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"push_secondary","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1001.0,"raw_peak_contact_force":24.91806,"subtask_id":"push_door","tcp_end":[0.10372,-0.13107,0.42859],"tcp_start":[0.09975,-0.01276,0.43272],"tcp_to_object_dist_end":0.46003,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```