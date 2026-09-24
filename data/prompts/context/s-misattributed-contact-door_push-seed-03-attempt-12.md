## Search State

- **Seed**: 3
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | approach → descend → push | arc_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | pose_tolerance | force_exceeded | time_limit | 6 | 1.1700 | 1.00 | ❌ rejected |
| 11 | approach → descend → push | arc_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | pose_tolerance | force_exceeded | time_limit | 6 | 1.1700 | 1.00 | ❌ rejected |
| 10 | approach → descend → push | arc_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | pose_tolerance | force_exceeded | time_limit | 6 | 1.1700 | 1.00 | ❌ rejected |
| 9 | approach → descend → push | arc_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | pose_tolerance | force_exceeded | time_limit | 6 | 1.1700 | 1.00 | ✅ accepted |
| 8 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | pose_tolerance | force_exceeded | time_limit | 6 | 0.4115 | 0.41 | ❌ rejected |

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
- id: reach_handle
  anchor: fixture
  offset:
  - -0.4
  - -0.02
  - 0.35
  weight: 0.3
- id: push_door
  anchor: world
  target_entity: hinge
  metric: hinge_angle
  weight: 0.7
phases:
- id: approach_above_handle
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
    - 0.4
    tolerance: 0.03
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: world_z
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: generator.speed
        mode: replace
    arc_height:
      type: scalar
      range:
      - 0.05
      - 0.25
      default: 0.15
      binds_to:
      - path: generator.arc_height
        mode: replace
  subtask_id: reach_handle
- id: descend_to_handle
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
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    descend_force:
      type: scalar
      range:
      - 8.0
      - 25.0
      default: 15.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    descend_speed:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  retries:
    max_attempts: 1
    strategy: offset_target
    offset:
    - 0.0
    - 0.01
    - 0.0
  subtask_id: reach_handle
- id: push_door_open
  type: push
  generator: linear_cartesian
  control: admittance_control
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
    orientation:
      mode: keep_current
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.2
      - 0.6
      default: 0.4
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_time:
      type: scalar
      range:
      - 3.0
      - 10.0
      default: 6.0
      binds_to:
      - path: duration.max_time
        mode: replace
  retries:
    max_attempts: 1
    strategy: offset_target
    offset:
    - 0.0
    - 0.02
    - 0.0
  subtask_id: push_door

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_above_handle** (`approach`)
  - target: source=yaml, anchor=site, entity=door_handle, offset=[0.0, 0.0, 0.4], tolerance=0.03
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=world_z
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
    - arc_height: status=consumed; consumers=generator.arc_height (replace)
- **descend_to_handle** (`descend`)
  - target: source=yaml, anchor=site, entity=door_handle, offset=[0.0, 0.0, 0.0], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_force: status=consumed; consumers=termination.force_threshold (replace)
    - descend_speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=1, strategy=offset_target, offset=[0.0, 0.01, 0.0]
- **push_door_open** (`push`)
  - target: source=yaml, anchor=site, entity=door_handle, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_y, distance=0.3, mode=add_to_offset, sign=negative}
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_time: status=consumed; consumers=duration.max_time (replace)
  - retries: max_attempts=1, strategy=offset_target, offset=[0.0, 0.02, 0.0]

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
| approach_above_handle | 0.00 | 1.00 | 0.3376 |
| descend_to_handle | 1.00 | 1.00 | 0.0297 |
| push_door_open | 1.00 | 0.33 | 0.1627 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_above_handle | approach | 0.00 / step_budget | (0.100, 0.399, 0.350)→(0.092, 0.151, 0.574) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 2.333 | 112.054 | 243.101 |
| descend_to_handle | descend | 1.00 / force_exceeded | (0.092, 0.151, 0.574)→(0.096, 0.143, 0.546) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 2.000 | 8.812 | 161.598 |
| push_door_open | push | 1.00 / time_limit | (0.096, 0.143, 0.546)→(0.105, -0.001, 0.472) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 0.33 / 0.333 | 51.630 | 2053.077 |

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
- **Stagnated**: no
- **Stop reason**: tolflatfitness
- **Mean generations**: 7.7
- **Final σ (mean)**: 0.431


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":6.26667,"average_solve_count":75.0,"average_success_count":75.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above_handle.approach_speed":0.24382,"approach_above_handle.arc_height":0.14613,"descend_to_handle.descend_force":19.07171,"descend_to_handle.descend_speed":0.03672,"push_door_open.push_distance":0.37384,"push_door_open.push_time":7.74099},"optimized_scores":{"best_composite_score":1.17,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link5","contact_count":182.0,"contact_point_centroid":[0.10224,0.18505,0.68631],"force_p95":754.2145,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1516.72346,"mean_force":389.76011,"phase_index":0.0,"phase_name":"approach_above_handle","phase_type":"approach","tcp_position_centroid":[0.07673,0.30613,0.53019]},{"body_a":"door_panel","body_b":"link4","contact_count":724.0,"contact_point_centroid":[0.10254,0.24441,0.6594],"force_p95":709.31102,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":831.66695,"mean_force":621.67145,"phase_index":0.0,"phase_name":"approach_above_handle","phase_type":"approach","tcp_position_centroid":[0.05699,0.3816,0.50651]},{"body_a":"door_panel","body_b":"link5","contact_count":2.0,"contact_point_centroid":[0.10658,0.12855,0.7],"force_p95":653.62196,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":688.02312,"mean_force":344.01156,"phase_index":1.0,"phase_name":"descend_to_handle","phase_type":"descend","tcp_position_centroid":[0.08136,0.22541,0.58258]},{"body_a":"door_panel","body_b":"link5","contact_count":79.0,"contact_point_centroid":[0.1076,0.12254,0.69774],"force_p95":27.57328,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":427.65278,"mean_force":25.02423,"phase_index":2.0,"phase_name":"push_door_open","phase_type":"push","tcp_position_centroid":[0.08184,0.21406,0.57641]},{"body_a":"door_panel","body_b":"link7","contact_count":336.0,"contact_point_centroid":[0.17277,0.10036,0.53917],"force_p95":22.21166,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":31.74403,"mean_force":14.25073,"phase_index":2.0,"phase_name":"push_door_open","phase_type":"push","tcp_position_centroid":[0.08797,0.1091,0.52674]},{"body_a":"world","body_b":"door_panel","contact_count":976.0,"contact_point_centroid":[0.30119,0.21242,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_above_handle","phase_type":"approach","tcp_position_centroid":[0.06191,0.36402,0.51164]},{"body_a":"world","body_b":"door_panel","contact_count":972.0,"contact_point_centroid":[0.3083,0.14321,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_door_open","phase_type":"push","tcp_position_centroid":[0.08539,0.15434,0.54795]}],"total_contact_groups":7},"final_pose_error":0.3785,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.08986,0.07634,0.51136],"hinge_angle":0.38644,"initial_hinge_angle":-0.14464,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":-0.14464,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":1516.72346,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":294.94252,"phase_name":"approach_above_handle","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2.0,"raw_peak_contact_force":688.02312,"subtask_id":"reach_handle","tcp_end":[0.08131,0.22555,0.58251],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.62993,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":2.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":14.54565,"phase_name":"descend_to_handle","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1387.0,"raw_peak_contact_force":427.65278,"subtask_id":"reach_handle","tcp_end":[0.08137,0.22506,0.58277],"tcp_start":[0.08131,0.22555,0.58251],"tcp_to_object_dist_end":0.62999,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":154.89026,"phase_name":"push_door_open","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1882.0,"raw_peak_contact_force":1516.72346,"subtask_id":"push_door","tcp_end":[0.08986,0.07634,0.51136],"tcp_start":[0.08137,0.22506,0.58277],"tcp_to_object_dist_end":0.52478,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":6.41772,"average_solve_count":79.0,"average_success_count":79.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above_handle.approach_speed":0.27993,"approach_above_handle.arc_height":0.09293,"descend_to_handle.descend_force":13.36281,"descend_to_handle.descend_speed":0.10094,"push_door_open.push_distance":0.47412,"push_door_open.push_time":6.30796},"optimized_scores":{"best_composite_score":1.17,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link4","contact_count":532.0,"contact_point_centroid":[0.10108,0.17962,0.64095],"force_p95":874.75366,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2339.21823,"mean_force":656.93845,"phase_index":0.0,"phase_name":"approach_above_handle","phase_type":"approach","tcp_position_centroid":[0.03642,0.32731,0.44566]},{"body_a":"door_panel","body_b":"link5","contact_count":158.0,"contact_point_centroid":[0.11175,0.10732,0.6845],"force_p95":399.09245,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":510.78892,"mean_force":105.21769,"phase_index":0.0,"phase_name":"approach_above_handle","phase_type":"approach","tcp_position_centroid":[0.0854,0.19812,0.54712]},{"body_a":"door_panel","body_b":"link7","contact_count":725.0,"contact_point_centroid":[0.19369,0.02271,0.52242],"force_p95":16.67481,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":28.27696,"mean_force":13.52267,"phase_index":2.0,"phase_name":"push_door_open","phase_type":"push","tcp_position_centroid":[0.10622,0.03102,0.51405]},{"body_a":"door_panel","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.18739,0.09073,0.5556],"force_p95":14.22478,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":14.22478,"mean_force":14.22478,"phase_index":1.0,"phase_name":"descend_to_handle","phase_type":"descend","tcp_position_centroid":[0.102,0.09951,0.54825]},{"body_a":"world","body_b":"door_panel","contact_count":1004.0,"contact_point_centroid":[0.30386,0.17078,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_above_handle","phase_type":"approach","tcp_position_centroid":[0.058,0.27772,0.48081]},{"body_a":"world","body_b":"door_panel","contact_count":136.0,"contact_point_centroid":[0.31458,0.12438,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"descend_to_handle","phase_type":"descend","tcp_position_centroid":[0.10069,0.10197,0.55844]},{"body_a":"world","body_b":"door_panel","contact_count":892.0,"contact_point_centroid":[0.33283,0.09172,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_door_open","phase_type":"push","tcp_position_centroid":[0.10637,0.02904,0.51292]}],"total_contact_groups":7},"final_pose_error":0.40371,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.11273,-0.03859,0.46578],"hinge_angle":0.69284,"initial_hinge_angle":0.15466,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.15466,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":2339.21823,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":993.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":14.22478,"phase_name":"approach_above_handle","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":137.0,"raw_peak_contact_force":14.22478,"subtask_id":"reach_handle","tcp_end":[0.09928,0.10486,0.5695],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.58752,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":136.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"descend_to_handle","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1617.0,"raw_peak_contact_force":28.27696,"subtask_id":"reach_handle","tcp_end":[0.10202,0.09947,0.54809],"tcp_start":[0.09928,0.10486,0.5695],"tcp_to_object_dist_end":0.56631,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"push_door_open","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1694.0,"raw_peak_contact_force":2339.21823,"subtask_id":"push_door","tcp_end":[0.11273,-0.03859,0.46578],"tcp_start":[0.10202,0.09947,0.54809],"tcp_to_object_dist_end":0.48078,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":5.8764,"average_solve_count":89.0,"average_success_count":89.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above_handle.approach_speed":0.29616,"approach_above_handle.arc_height":0.08022,"descend_to_handle.descend_force":19.275,"descend_to_handle.descend_speed":0.08254,"push_door_open.push_distance":0.43085,"push_door_open.push_time":6.97288},"optimized_scores":{"best_composite_score":1.17,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link4","contact_count":458.0,"contact_point_centroid":[0.10051,0.20115,0.63439],"force_p95":787.23041,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2303.28804,"mean_force":615.55966,"phase_index":0.0,"phase_name":"approach_above_handle","phase_type":"approach","tcp_position_centroid":[0.03938,0.33331,0.43154]},{"body_a":"door_panel","body_b":"link5","contact_count":209.0,"contact_point_centroid":[0.10678,0.13777,0.67575],"force_p95":562.08123,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":621.47178,"mean_force":237.39812,"phase_index":0.0,"phase_name":"approach_above_handle","phase_type":"approach","tcp_position_centroid":[0.07722,0.21976,0.53274]},{"body_a":"door_panel","body_b":"link7","contact_count":734.0,"contact_point_centroid":[0.19451,0.02395,0.48806],"force_p95":20.03895,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":28.86338,"mean_force":14.12819,"phase_index":2.0,"phase_name":"push_door_open","phase_type":"push","tcp_position_centroid":[0.10702,0.03139,0.48016]},{"body_a":"door_panel","body_b":"link7","contact_count":46.0,"contact_point_centroid":[0.18744,0.09871,0.52591],"force_p95":20.64794,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":27.054,"mean_force":15.47864,"phase_index":1.0,"phase_name":"descend_to_handle","phase_type":"descend","tcp_position_centroid":[0.10201,0.10697,0.51839]},{"body_a":"world","body_b":"door_panel","contact_count":984.0,"contact_point_centroid":[0.30314,0.17822,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_above_handle","phase_type":"approach","tcp_position_centroid":[0.05936,0.28239,0.47186]},{"body_a":"world","body_b":"door_panel","contact_count":368.0,"contact_point_centroid":[0.31254,0.12959,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"descend_to_handle","phase_type":"descend","tcp_position_centroid":[0.09884,0.11383,0.54261]},{"body_a":"world","body_b":"door_panel","contact_count":880.0,"contact_point_centroid":[0.33401,0.09008,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_door_open","phase_type":"push","tcp_position_centroid":[0.10739,0.02442,0.47752]}],"total_contact_groups":7},"final_pose_error":0.34691,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.11243,-0.04171,0.43789],"hinge_angle":0.69655,"initial_hinge_angle":0.10647,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.10647,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":2303.28804,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":935.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":26.99501,"phase_name":"approach_above_handle","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":414.0,"raw_peak_contact_force":27.054,"subtask_id":"reach_handle","tcp_end":[0.09519,0.12183,0.57101],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.59157,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":437.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":11.8913,"phase_name":"descend_to_handle","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1614.0,"raw_peak_contact_force":28.86338,"subtask_id":"reach_handle","tcp_end":[0.10342,0.10391,0.50775],"tcp_start":[0.09519,0.12183,0.57101],"tcp_to_object_dist_end":0.52849,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"push_door_open","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1651.0,"raw_peak_contact_force":2303.28804,"subtask_id":"push_door","tcp_end":[0.11243,-0.04171,0.43789],"tcp_start":[0.10342,0.10391,0.50775],"tcp_to_object_dist_end":0.45401,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
```