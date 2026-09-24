## Search State

- **Seed**: 2
- **Iteration**: 8 / 15

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

## Current Skill (Q=1.170) — your mutation base

```yaml
skill: door_push
dsl_version: 2
subtasks:
- id: hinge_progress
  anchor: fixture
  target_entity: hinge
  metric: hinge_angle
phases:
- id: contact_handle
  type: contact
  generator: linear_cartesian
  control: force_threshold_switch
  termination: force_exceeded
  target:
    source: yaml
    anchor: body
    entity: door_panel
    offset:
    - -0.4
    - -0.02
    - 0.35
  parameters:
    force_threshold:
      type: scalar
      range:
      - 1.0
      - 20.0
      default: 5.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
  subtask_id: hinge_progress
- id: push_door
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: time_limit
  target:
    source: yaml
    anchor: fixture
    entity: door_panel
    offset:
    - -0.3364
    - -0.21732
    - 0.35
  parameters:
    max_push_time:
      type: scalar
      range:
      - 0.5
      - 8.0
      default: 4.0
      binds_to:
      - path: duration.max_time
        mode: replace
    push_target_x:
      type: scalar
      range:
      - -0.4364
      - -0.2364
      default: -0.3364
      binds_to:
      - path: target.offset.x
        mode: replace
    push_target_y:
      type: scalar
      range:
      - -0.31732
      - -0.11732
      default: -0.21732
      binds_to:
      - path: target.offset.y
        mode: replace
    speed:
      type: scalar
      range:
      - 0.01
      - 0.2
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: hinge_progress

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **contact_handle** (`contact`)
  - target: source=yaml, anchor=body, entity=door_panel, offset=[-0.4, -0.02, 0.35]
  - parameter_bindings:
    - force_threshold: status=consumed; consumers=termination.force_threshold (replace)
- **push_door** (`push`)
  - target: source=yaml, anchor=fixture, entity=door_panel, offset=[-0.3364, -0.21732, 0.35]
  - parameter_bindings:
    - max_push_time: status=consumed; consumers=duration.max_time (replace)
    - push_target_x: status=consumed; consumers=target.offset.x (replace)
    - push_target_y: status=consumed; consumers=target.offset.y (replace)
    - speed: status=consumed; consumers=generator.speed (replace)

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
| approach_handle | 0.33 | 1.00 | 0.2547 |
| contact_handle | 1.00 | 1.00 | 0.0001 |
| push_door | 1.00 | 1.00 | 0.1484 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_handle | approach | 0.33 / step_budget | (0.100, 0.399, 0.350)→(0.065, 0.158, 0.422) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 3.000 | 285.520 | 1764.348 |
| contact_handle | contact | 1.00 / force_exceeded | (0.065, 0.158, 0.422)→(0.065, 0.157, 0.422) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 1.667 | 245.829 | 89.637 |
| push_door | push | 1.00 / time_limit | (0.065, 0.157, 0.422)→(0.075, 0.010, 0.411) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 1.333 | 263.559 | 653.043 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- hinge_angle_ratio: 1.000
- arc_quality: 0.667

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 1.000
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 1.170
- **K-run variance**: 0.0000
- **Stagnated**: yes
  → Parameter optimiser converged to local optimum; structural change likely needed
- **Stop reason**: tolfun
- **Mean generations**: 2.0
- **Final σ (mean)**: 0.272


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":7.0,"average_solve_count":65.0,"average_success_count":65.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_handle.approach_speed":0.18337,"contact_handle.contact_speed":0.0931,"contact_handle.force_threshold":5.78619,"push_door.max_push_time":6.18436,"push_door.push_distance":0.28508,"push_door.push_speed":0.09839},"optimized_scores":{"best_composite_score":1.17,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link5","contact_count":151.0,"contact_point_centroid":[0.1025,0.24095,0.59125],"force_p95":741.665,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1579.43232,"mean_force":372.49673,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.06147,0.29789,0.41442]},{"body_a":"door_panel","body_b":"link4","contact_count":224.0,"contact_point_centroid":[0.11129,0.10696,0.60602],"force_p95":528.50853,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":635.42233,"mean_force":344.97094,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.04779,0.11841,0.40211]},{"body_a":"door_panel","body_b":"link4","contact_count":682.0,"contact_point_centroid":[0.10097,0.20163,0.61924],"force_p95":517.90017,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":574.47092,"mean_force":431.22719,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.05494,0.24656,0.42846]},{"body_a":"link1","body_b":"link7","contact_count":290.0,"contact_point_centroid":[0.05491,0.01597,0.35993],"force_p95":334.70119,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":434.97144,"mean_force":225.62547,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.06876,0.03349,0.41087]},{"body_a":"door_panel","body_b":"link7","contact_count":377.0,"contact_point_centroid":[0.10133,0.19326,0.41312],"force_p95":383.81745,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":419.6368,"mean_force":280.7237,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.05369,0.20863,0.42764]},{"body_a":"door_panel","body_b":"link7","contact_count":684.0,"contact_point_centroid":[0.13198,0.05651,0.40256],"force_p95":122.35571,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":282.74478,"mean_force":29.91719,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.05646,0.06813,0.40285]},{"body_a":"link2","body_b":"link7","contact_count":258.0,"contact_point_centroid":[0.02407,0.03892,0.36956],"force_p95":141.58589,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":181.7171,"mean_force":98.34349,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.05813,0.05809,0.40203]},{"body_a":"door_panel","body_b":"link4","contact_count":1.0,"contact_point_centroid":[0.10522,0.13668,0.60584],"force_p95":63.23283,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":63.23283,"mean_force":63.23283,"phase_index":1.0,"phase_name":"contact_handle","phase_type":"contact","tcp_position_centroid":[0.05972,0.15712,0.4237]},{"body_a":"door_panel","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.10505,0.13666,0.41186],"force_p95":29.98752,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":29.98752,"mean_force":29.98752,"phase_index":1.0,"phase_name":"contact_handle","phase_type":"contact","tcp_position_centroid":[0.05972,0.15712,0.4237]},{"body_a":"world","body_b":"door_panel","contact_count":696.0,"contact_point_centroid":[0.30044,0.2026,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.05842,0.26896,0.41832]},{"body_a":"world","body_b":"door_panel","contact_count":4.0,"contact_point_centroid":[0.3041,0.15847,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"contact_handle","phase_type":"contact","tcp_position_centroid":[0.05972,0.15712,0.4237]},{"body_a":"world","body_b":"door_panel","contact_count":952.0,"contact_point_centroid":[0.31737,0.12036,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.05564,0.07233,0.40271]}],"total_contact_groups":12},"final_pose_error":0.1458,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.07253,0.01699,0.4148],"hinge_angle":0.56064,"initial_hinge_angle":-0.08321,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":-0.08321,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":1579.43232,"phases":[{"contact_detected":true,"contact_event_count":6.0,"n_steps":782.0,"n_steps_budget":840.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.37818,"phase_name":"approach_handle","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1906.0,"raw_peak_contact_force":1579.43232,"subtask_id":"hinge_progress","tcp_end":[0.05972,0.15712,0.4237],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.45582,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":531.81025,"phase_name":"contact_handle","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":6.0,"raw_peak_contact_force":63.23283,"subtask_id":"hinge_progress","tcp_end":[0.05972,0.1571,0.42369],"tcp_start":[0.05972,0.15712,0.4237],"tcp_to_object_dist_end":0.45581,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":327.81931,"phase_name":"push_door","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2408.0,"raw_peak_contact_force":635.42233,"subtask_id":"hinge_progress","tcp_end":[0.07253,0.01699,0.4148],"tcp_start":[0.05972,0.1571,0.42369],"tcp_to_object_dist_end":0.42144,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":6.9661,"average_solve_count":59.0,"average_success_count":59.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_handle.approach_speed":0.23519,"contact_handle.contact_speed":0.12039,"contact_handle.force_threshold":5.16845,"push_door.max_push_time":5.73742,"push_door.push_distance":0.33774,"push_door.push_speed":0.07825},"optimized_scores":{"best_composite_score":1.17,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link5","contact_count":305.0,"contact_point_centroid":[0.10299,0.24641,0.60428],"force_p95":574.1442,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1463.47706,"mean_force":464.98389,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.06033,0.30704,0.41768]},{"body_a":"door_panel","body_b":"link4","contact_count":353.0,"contact_point_centroid":[0.11119,0.10762,0.60432],"force_p95":500.87631,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":605.69674,"mean_force":319.50026,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.04536,0.117,0.39946]},{"body_a":"door_panel","body_b":"link4","contact_count":340.0,"contact_point_centroid":[0.10082,0.18804,0.6123],"force_p95":538.84504,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":578.00285,"mean_force":430.96978,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.05395,0.2201,0.42965]},{"body_a":"door_panel","body_b":"link7","contact_count":282.0,"contact_point_centroid":[0.10122,0.19629,0.4126],"force_p95":425.4506,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":447.87884,"mean_force":314.92804,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.05362,0.21114,0.42709]},{"body_a":"door_panel","body_b":"link7","contact_count":631.0,"contact_point_centroid":[0.12462,0.07096,0.39915],"force_p95":132.66343,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":329.98256,"mean_force":31.83666,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.0512,0.07948,0.4002]},{"body_a":"link2","body_b":"link7","contact_count":461.0,"contact_point_centroid":[0.01427,0.04662,0.36615],"force_p95":135.02006,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":160.30781,"mean_force":108.8369,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.05477,0.06129,0.40127]},{"body_a":"door_panel","body_b":"link4","contact_count":1.0,"contact_point_centroid":[0.10432,0.14231,0.60526],"force_p95":72.21275,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":72.21275,"mean_force":72.21275,"phase_index":1.0,"phase_name":"contact_handle","phase_type":"contact","tcp_position_centroid":[0.05869,0.16177,0.4225]},{"body_a":"door_panel","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.10427,0.14214,0.41075],"force_p95":53.98471,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":53.98471,"mean_force":53.98471,"phase_index":1.0,"phase_name":"contact_handle","phase_type":"contact","tcp_position_centroid":[0.05869,0.16177,0.4225]},{"body_a":"world","body_b":"door_panel","contact_count":584.0,"contact_point_centroid":[0.30055,0.20277,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.05808,0.26404,0.42197]},{"body_a":"world","body_b":"door_panel","contact_count":956.0,"contact_point_centroid":[0.31336,0.12901,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.04968,0.086,0.39956]}],"total_contact_groups":10},"final_pose_error":0.22243,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.06233,0.04586,0.40771],"hinge_angle":0.44489,"initial_hinge_angle":-0.14464,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":-0.14464,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":1463.47706,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":631.0,"n_steps_budget":660.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":495.0546,"phase_name":"approach_handle","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1511.0,"raw_peak_contact_force":1463.47706,"subtask_id":"hinge_progress","tcp_end":[0.05869,0.16177,0.4225],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.45621,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":72.21275,"phase_name":"contact_handle","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2.0,"raw_peak_contact_force":72.21275,"subtask_id":"hinge_progress","tcp_end":[0.0587,0.16169,0.42249],"tcp_start":[0.05869,0.16177,0.4225],"tcp_to_object_dist_end":0.45617,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":115.95058,"phase_name":"push_door","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2401.0,"raw_peak_contact_force":605.69674,"subtask_id":"hinge_progress","tcp_end":[0.06233,0.04586,0.40771],"tcp_start":[0.0587,0.16169,0.42249],"tcp_to_object_dist_end":0.41499,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":6.95238,"average_solve_count":63.0,"average_success_count":63.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_handle.approach_speed":0.19251,"contact_handle.contact_speed":0.12098,"contact_handle.force_threshold":5.38619,"push_door.max_push_time":4.31725,"push_door.push_distance":0.33154,"push_door.push_speed":0.1572},"optimized_scores":{"best_composite_score":1.17,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link4","contact_count":714.0,"contact_point_centroid":[0.10853,0.12166,0.64264],"force_p95":776.55861,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2250.13469,"mean_force":611.86756,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.05387,0.2491,0.43167]},{"body_a":"door_panel","body_b":"link4","contact_count":205.0,"contact_point_centroid":[0.12728,0.05536,0.625],"force_p95":463.43001,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":718.00897,"mean_force":221.48113,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.06635,0.10786,0.39896]},{"body_a":"link1","body_b":"link7","contact_count":652.0,"contact_point_centroid":[0.06393,-0.00218,0.35769],"force_p95":436.87608,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":567.76055,"mean_force":333.3365,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.08104,0.01569,0.40653]},{"body_a":"door_panel","body_b":"link4","contact_count":1.0,"contact_point_centroid":[0.12051,0.0737,0.63928],"force_p95":133.46515,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":133.46515,"mean_force":133.46515,"phase_index":1.0,"phase_name":"contact_handle","phase_type":"contact","tcp_position_centroid":[0.07694,0.15367,0.41871]},{"body_a":"door_panel","body_b":"link6","contact_count":144.0,"contact_point_centroid":[0.24264,-0.03528,0.35246],"force_p95":37.3376,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":76.20243,"mean_force":25.23311,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.08555,-0.00578,0.41107]},{"body_a":"door_panel","body_b":"link7","contact_count":220.0,"contact_point_centroid":[0.16268,0.01673,0.40033],"force_p95":22.77702,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":36.72323,"mean_force":14.14222,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.07655,0.03979,0.40234]},{"body_a":"world","body_b":"door_panel","contact_count":740.0,"contact_point_centroid":[0.30509,0.15688,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.0568,0.26321,0.42538]},{"body_a":"world","body_b":"door_panel","contact_count":860.0,"contact_point_centroid":[0.33484,0.09145,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.07547,0.04622,0.40303]}],"total_contact_groups":8},"final_pose_error":0.1454,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.08961,-0.03326,0.41148],"hinge_angle":0.86503,"initial_hinge_angle":0.15466,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.15466,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":2250.13469,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":752.0,"n_steps_budget":810.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":361.12716,"phase_name":"approach_handle","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1454.0,"raw_peak_contact_force":2250.13469,"subtask_id":"hinge_progress","tcp_end":[0.07694,0.15367,0.41871],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.45261,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":133.46515,"phase_name":"contact_handle","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1.0,"raw_peak_contact_force":133.46515,"subtask_id":"hinge_progress","tcp_end":[0.07699,0.15361,0.41869],"tcp_start":[0.07694,0.15367,0.41871],"tcp_to_object_dist_end":0.45257,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":346.90843,"phase_name":"push_door","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2081.0,"raw_peak_contact_force":718.00897,"subtask_id":"hinge_progress","tcp_end":[0.08961,-0.03326,0.41148],"tcp_start":[0.07699,0.15361,0.41869],"tcp_to_object_dist_end":0.42244,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
```