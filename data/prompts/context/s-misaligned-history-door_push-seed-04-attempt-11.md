## Search State

- **Seed**: 4
- **Iteration**: 12 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 11 | approach → contact → push | arc_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | time_limit | 7 | 1.1200 | 1.00 | ❌ rejected |
| 10 | approach → contact → push | arc_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | time_limit | 7 | 1.1200 | 1.00 | ❌ rejected |
| 9 | approach → contact → push | arc_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | time_limit | 7 | 1.1200 | 1.00 | ❌ rejected |
| 8 | approach → contact → push | arc_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | time_limit | 7 | 1.1200 | 1.00 | ❌ rejected |
| 7 | approach → contact → push | arc_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | time_limit | 7 | 1.1200 | 1.00 | ❌ rejected |

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

## Current Skill (Q=1.120) — your mutation base

```yaml
skill: door_push
dsl_version: 2
subtasks:
- id: approach_handle_sub
  anchor: fixture
  offset:
  - -0.4
  - -0.02
  - 0.35
  weight: 0.2
- id: push_door_sub
  anchor: fixture
  target_entity: hinge
  metric: hinge_angle
  weight: 0.8
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
    - -0.05
    - 0.0
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    approach_offset_y:
      type: scalar
      range:
      - -0.08
      - -0.02
      default: -0.05
      binds_to:
      - path: target.offset.y
        mode: replace
    approach_tolerance:
      type: scalar
      range:
      - 0.005
      - 0.05
      default: 0.02
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
    arc_height:
      type: scalar
      range:
      - 0.03
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.arc_height
        mode: replace
  subtask_id: approach_handle_sub
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
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    contact_force:
      type: scalar
      range:
      - 3.0
      - 10.0
      default: 5.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
  subtask_id: approach_handle_sub
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
      distance: 0.25
      axis: world_y
      mode: add_to_offset
      sign: negative
    tolerance: 0.05
    orientation:
      mode: keep_current
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.15
      - 0.4
      default: 0.25
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_duration:
      type: scalar
      range:
      - 3.0
      - 8.0
      default: 5.0
      binds_to:
      - path: duration.max_time
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.05
      - 0.15
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: push_door_sub

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_handle** (`approach`)
  - target: source=yaml, anchor=site, entity=door_handle, offset=[0.0, -0.05, 0.0], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_offset_y: status=consumed; consumers=target.offset.y (replace)
    - approach_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
    - arc_height: status=consumed; consumers=generator.arc_height (replace)
- **contact_handle** (`contact`)
  - target: source=yaml, anchor=site, entity=door_handle, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - contact_force: status=consumed; consumers=termination.force_threshold (replace)
- **push_door** (`push`)
  - target: source=yaml, anchor=site, entity=door_handle, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_y, distance=0.25, mode=add_to_offset, sign=negative}, tolerance=0.05
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_duration: status=consumed; consumers=duration.max_time (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: 1.120
- **task_score** (E): 1.000
- **fitness_score**: 1.000  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.500
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.380

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_handle | 0.33 | 1.00 | 0.2950 |
| contact_handle | 1.00 | 1.00 | 0.0006 |
| push_door | 1.00 | 0.33 | 0.1642 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_handle | approach | 0.33 / step_budget | (0.100, 0.399, 0.350)→(0.103, 0.108, 0.395) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 2.333 | 9.688 | 38.045 |
| contact_handle | contact | 1.00 / force_exceeded | (0.103, 0.108, 0.395)→(0.104, 0.107, 0.395) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 1.000 | 22.606 | 24.225 |
| push_door | push | 1.00 / time_limit | (0.104, 0.107, 0.395)→(0.124, -0.054, 0.408) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 0.33 / 1.667 | 5.314 | 38.695 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- hinge_angle_ratio: 1.000
- arc_quality: 0.667

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 1.000
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 1.120
- **K-run variance**: 0.0000
- **Stagnated**: yes
  → Parameter optimiser converged to local optimum; structural change likely needed
- **Stop reason**: tolfun
- **Mean generations**: 2.0
- **Final σ (mean)**: 0.287


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.69159,"average_solve_count":107.0,"average_success_count":107.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_handle.approach_offset_y":-0.05177,"approach_handle.approach_tolerance":0.03107,"approach_handle.arc_height":0.06238,"contact_handle.contact_force":5.68636,"push_door.push_distance":0.28545,"push_door.push_duration":4.01806,"push_door.push_speed":0.08553},"optimized_scores":{"best_composite_score":1.12,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link7","contact_count":325.0,"contact_point_centroid":[0.17205,0.0709,0.4249],"force_p95":32.02808,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":38.58805,"mean_force":16.79696,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.10646,0.12827,0.3988]},{"body_a":"door_panel","body_b":"link7","contact_count":666.0,"contact_point_centroid":[0.18649,-0.03641,0.4444],"force_p95":22.92808,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":35.71388,"mean_force":12.83418,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.11617,0.01182,0.41689]},{"body_a":"door_panel","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.17152,0.01995,0.43956],"force_p95":17.33322,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":18.24549,"mean_force":9.12274,"phase_index":1.0,"phase_name":"contact_handle","phase_type":"contact","tcp_position_centroid":[0.10674,0.07801,0.4102]},{"body_a":"door_panel","body_b":"link6","contact_count":6.0,"contact_point_centroid":[0.10476,0.13878,0.51387],"force_p95":0.0,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.10474,0.2057,0.40867]},{"body_a":"world","body_b":"door_panel","contact_count":884.0,"contact_point_centroid":[0.3104,0.14082,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.10407,0.23079,0.39182]},{"body_a":"world","body_b":"door_panel","contact_count":4.0,"contact_point_centroid":[0.32943,0.09509,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"contact_handle","phase_type":"contact","tcp_position_centroid":[0.10671,0.07804,0.41019]},{"body_a":"world","body_b":"door_panel","contact_count":848.0,"contact_point_centroid":[0.34847,0.07023,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.11736,0.00464,0.41638]}],"total_contact_groups":7},"final_pose_error":0.233,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.12874,-0.07166,0.40757],"hinge_angle":0.78744,"initial_hinge_angle":0.15466,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.15466,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":38.58805,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":916.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":13.00188,"phase_name":"approach_handle","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1215.0,"raw_peak_contact_force":38.58805,"subtask_id":"approach_handle_sub","tcp_end":[0.1067,0.07812,0.41013],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.43092,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":4.0,"n_steps_budget":750.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":18.24549,"phase_name":"contact_handle","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":6.0,"raw_peak_contact_force":18.24549,"subtask_id":"approach_handle_sub","tcp_end":[0.10684,0.0778,0.41033],"tcp_start":[0.1067,0.07812,0.41013],"tcp_to_object_dist_end":0.43109,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"push_door","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1514.0,"raw_peak_contact_force":35.71388,"subtask_id":"push_door_sub","tcp_end":[0.12874,-0.07166,0.40757],"tcp_start":[0.10684,0.0778,0.41033],"tcp_to_object_dist_end":0.43338,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.90291,"average_solve_count":103.0,"average_success_count":103.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_handle.approach_offset_y":-0.04849,"approach_handle.approach_tolerance":0.0169,"approach_handle.arc_height":0.0562,"contact_handle.contact_force":6.47394,"push_door.push_distance":0.2314,"push_door.push_duration":4.8187,"push_door.push_speed":0.09004},"optimized_scores":{"best_composite_score":1.12,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link7","contact_count":703.0,"contact_point_centroid":[0.18156,-0.02,0.44331],"force_p95":23.31098,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":38.38629,"mean_force":12.91912,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.11278,0.03134,0.41543]},{"body_a":"door_panel","body_b":"link7","contact_count":274.0,"contact_point_centroid":[0.16921,0.0871,0.41635],"force_p95":27.68986,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":37.4319,"mean_force":16.40136,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.10367,0.14444,0.391]},{"body_a":"door_panel","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.16933,0.04649,0.42816],"force_p95":28.02336,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":29.49827,"mean_force":14.74913,"phase_index":1.0,"phase_name":"contact_handle","phase_type":"contact","tcp_position_centroid":[0.10359,0.10396,0.3997]},{"body_a":"door_panel","body_b":"link6","contact_count":41.0,"contact_point_centroid":[0.10322,0.15038,0.50801],"force_p95":15.60175,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":19.16385,"mean_force":8.90026,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.10269,0.21865,0.40246]},{"body_a":"world","body_b":"door_panel","contact_count":900.0,"contact_point_centroid":[0.30783,0.14979,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.10237,0.23698,0.38854]},{"body_a":"world","body_b":"door_panel","contact_count":8.0,"contact_point_centroid":[0.32301,0.10634,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"contact_handle","phase_type":"contact","tcp_position_centroid":[0.10391,0.10331,0.40022]},{"body_a":"world","body_b":"door_panel","contact_count":724.0,"contact_point_centroid":[0.34164,0.07906,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.11289,0.03104,0.41528]}],"total_contact_groups":7},"final_pose_error":0.17127,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.1264,-0.05907,0.40854],"hinge_angle":0.77072,"initial_hinge_angle":0.10647,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.10647,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":38.38629,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":827.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":12.21541,"phase_name":"approach_handle","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1215.0,"raw_peak_contact_force":37.4319,"subtask_id":"approach_handle_sub","tcp_end":[0.10358,0.10399,0.39966],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.42576,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":9.0,"n_steps_budget":720.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":24.64054,"phase_name":"contact_handle","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":10.0,"raw_peak_contact_force":29.49827,"subtask_id":"approach_handle_sub","tcp_end":[0.10399,0.10314,0.40034],"tcp_start":[0.10358,0.10399,0.39966],"tcp_to_object_dist_end":0.42629,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"push_door","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1427.0,"raw_peak_contact_force":38.38629,"subtask_id":"push_door_sub","tcp_end":[0.1264,-0.05907,0.40854],"tcp_start":[0.10399,0.10314,0.40034],"tcp_to_object_dist_end":0.4317,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.88421,"average_solve_count":95.0,"average_success_count":95.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_handle.approach_offset_y":-0.04565,"approach_handle.approach_tolerance":0.01361,"approach_handle.arc_height":0.07191,"contact_handle.contact_force":7.61949,"push_door.push_distance":0.30748,"push_door.push_duration":6.86365,"push_door.push_speed":0.09768},"optimized_scores":{"best_composite_score":1.12,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link7","contact_count":727.0,"contact_point_centroid":[0.17287,0.00842,0.43479],"force_p95":23.58649,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":41.98343,"mean_force":13.15132,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.10506,0.06203,0.40724]},{"body_a":"door_panel","body_b":"link7","contact_count":180.0,"contact_point_centroid":[0.16534,0.11056,0.41209],"force_p95":36.62191,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":38.1139,"mean_force":17.04746,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.10016,0.16805,0.38813]},{"body_a":"door_panel","body_b":"link6","contact_count":106.0,"contact_point_centroid":[0.10136,0.17116,0.52287],"force_p95":23.25577,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":34.10463,"mean_force":12.56701,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.1002,0.24214,0.41658]},{"body_a":"door_panel","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.16534,0.08417,0.39937],"force_p95":23.68601,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":24.93264,"mean_force":12.46632,"phase_index":1.0,"phase_name":"contact_handle","phase_type":"contact","tcp_position_centroid":[0.10016,0.14171,0.3754]},{"body_a":"world","body_b":"door_panel","contact_count":712.0,"contact_point_centroid":[0.30395,0.16712,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.10018,0.2576,0.39521]},{"body_a":"world","body_b":"door_panel","contact_count":8.0,"contact_point_centroid":[0.31426,0.12515,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"contact_handle","phase_type":"contact","tcp_position_centroid":[0.10014,0.14175,0.3754]},{"body_a":"world","body_b":"door_panel","contact_count":908.0,"contact_point_centroid":[0.33184,0.09363,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.10464,0.06687,0.40618]}],"total_contact_groups":7},"final_pose_error":0.23327,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.11569,-0.03233,0.40937],"hinge_angle":0.71529,"initial_hinge_angle":0.01332,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.01332,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":41.98343,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":713.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":3.84538,"phase_name":"approach_handle","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":998.0,"raw_peak_contact_force":38.1139,"subtask_id":"approach_handle_sub","tcp_end":[0.10014,0.14176,0.37541],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.41359,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":4.0,"n_steps_budget":630.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":24.93264,"phase_name":"contact_handle","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":10.0,"raw_peak_contact_force":24.93264,"subtask_id":"approach_handle_sub","tcp_end":[0.10025,0.14139,0.37542],"tcp_start":[0.10014,0.14176,0.37541],"tcp_to_object_dist_end":0.4135,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":15.94079,"phase_name":"push_door","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1635.0,"raw_peak_contact_force":41.98343,"subtask_id":"push_door_sub","tcp_end":[0.11569,-0.03233,0.40937],"tcp_start":[0.10025,0.14139,0.37542],"tcp_to_object_dist_end":0.42663,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
```