## Search State

- **Seed**: 8
- **Iteration**: 12 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 11 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | time_limit | 7 | 1.1200 | 1.00 | ✅ accepted |
| 10 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | time_limit | 8 | 1.0700 | 1.00 | ❌ rejected |
| 9 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | time_limit | 8 | 1.0700 | 1.00 | ❌ rejected |
| 8 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | time_limit | 8 | 1.0700 | 1.00 | ❌ rejected |
| 7 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | time_limit | 8 | 1.0578 | 0.99 | ❌ rejected |

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
- Frozen realised-scene SHA-256: `03ad88d640dcd23384857b752dfa12af63a722a6c6b9379a358f8168d1c71e09`
- Frozen initial hinge angle: -0.060 rad
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
  frozen_initial_hinge_angle_rad: -0.0604
  frozen_fixtures: {'door_panel': [0.5, 0.2, 0.0]}
  door_hinge_axis: [0, 0, 1]
  goal_tolerance_m: 0.05
  force_limit_n: 30
  force_scale_n: 5
  target_hinge_angle_rad: 0.524
  realized_scene_sha256: 03ad88d640dcd23384857b752dfa12af63a722a6c6b9379a358f8168d1c71e09

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
- id: approach_door
  anchor: fixture
  offset:
  - -0.45
  - -0.02
  - 0.35
  weight: 0.2
- id: open_door
  anchor: fixture
  target_entity: hinge
  metric: hinge_angle
  weight: 0.8
phases:
- id: pre_approach
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
    tolerance: 0.015
    orientation:
      mode: keep_current
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.05
      - 0.15
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: replace
    approach_speed:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.2
      binds_to:
      - path: generator.speed
        mode: replace
  retries:
    max_attempts: 1
    strategy: repeat
  subtask_id: approach_door
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
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    contact_threshold:
      type: scalar
      range:
      - 2.0
      - 10.0
      default: 5.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - 0.005
  subtask_id: approach_door
- id: push_open
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
      distance: 0.25
      axis: world_y
      mode: add_to_offset
      sign: negative
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    force_guard_threshold:
      type: scalar
      range:
      - 25.0
      - 30.0
      default: 28.0
      binds_to:
      - path: guards.force_limit_check.threshold
        mode: replace
    max_time:
      type: scalar
      range:
      - 3.0
      - 8.0
      default: 5.0
      binds_to:
      - path: duration.max_time
        mode: replace
    push_distance:
      type: scalar
      range:
      - 0.15
      - 0.4
      default: 0.25
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.05
      - 0.25
      default: 0.12
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: force_limit_check
    when: during_phase
    predicate: force_below
    threshold: 28.0
    on_failure: abort
  retries:
    max_attempts: 2
    strategy: reduce_speed
  subtask_id: open_door

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **pre_approach** (`approach`)
  - target: source=yaml, anchor=site, entity=door_handle, offset=[0.0, 0.0, 0.1], tolerance=0.015
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
    - approach_speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=1, strategy=repeat
- **descend_to_handle** (`descend`)
  - target: source=yaml, anchor=site, entity=door_handle, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - contact_threshold: status=consumed; consumers=termination.force_threshold (replace)
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, 0.005]
- **push_open** (`push`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_y, distance=0.25, mode=add_to_offset, sign=negative}, tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - force_guard_threshold: status=consumed; consumers=guards.force_limit_check.threshold (replace)
    - max_time: status=consumed; consumers=duration.max_time (replace)
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=force_limit_check, when=during_phase, predicate=force_below, on_failure=abort, threshold=28.0
  - retries: max_attempts=2, strategy=reduce_speed

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
| pre_approach | 1.00 | 1.00 | 0.2575 |
| descend_to_handle | 1.00 | 1.00 | 0.0016 |
| push_open | 1.00 | 0.67 | 0.1637 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| pre_approach | approach | 1.00 / step_budget | (0.100, 0.399, 0.350)→(0.104, 0.163, 0.449) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 2.333 | 5.833 | 48.651 |
| descend_to_handle | descend | 1.00 / force_exceeded | (0.104, 0.163, 0.449)→(0.104, 0.161, 0.448) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 2.333 | 15.349 | 15.349 |
| push_open | push | 1.00 / time_limit | (0.104, 0.161, 0.448)→(0.104, -0.002, 0.447) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 0.67 / 0.667 | 3.546 | 27.189 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- hinge_angle_ratio: 1.000
- arc_quality: 1.000

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 1.000
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 1.120
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.367


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `ea6bae111f14debb91f5aac35e1b236c8a3b6c6e55761aa2eab002718511c500`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"hinge_delta_deg":10.0,"object_xy_delta":[0.0,0.0]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `4672b672dcc6ffecf2b710096d1b05b46bb79ca3304db4877275d5463822e477`; realized-scene SHA-256: `03ad88d640dcd23384857b752dfa12af63a722a6c6b9379a358f8168d1c71e09`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"fixture","value":[0.5,0.2,0.0]}],"axes":[{"name":"door_hinge_axis","value":[0.0,0.0,1.0]}],"door":{"hinge_axis":[0.0,0.0,1.0],"initial_hinge_angle":-0.0604,"panel":{"name":"door_panel","orientation":[0.99954,0.0,0.0,-0.03019],"position":[0.5,0.2,0.0]},"target_hinge_angle":0.524},"fixture_states":[],"fixtures":[{"name":"door_panel","orientation":[0.99954,0.0,0.0,-0.03019],"position":[0.5,0.2,0.0]}],"limits":[{"name":"goal_tolerance_m","value":0.05},{"name":"force_limit_n","value":30.0},{"name":"force_scale_n","value":5.0},{"name":"target_hinge_angle_rad","value":0.524}],"object_starts":[],"obstacles":[],"targets":[],"task_name":"door_push"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.26866,"average_solve_count":67.0,"average_success_count":67.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"descend_to_handle.contact_threshold":7.58449,"pre_approach.approach_height":0.09256,"pre_approach.approach_speed":0.16021,"push_open.force_guard_threshold":27.75149,"push_open.max_time":6.54909,"push_open.push_distance":0.20272,"push_open.push_speed":0.1032},"optimized_scores":{"best_composite_score":1.12,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link6","contact_count":178.0,"contact_point_centroid":[0.1008,0.18746,0.52002],"force_p95":30.56658,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":68.83123,"mean_force":19.31103,"phase_index":0.0,"phase_name":"pre_approach","phase_type":"approach","tcp_position_centroid":[0.09947,0.26122,0.41284]},{"body_a":"door_panel","body_b":"link7","contact_count":822.0,"contact_point_centroid":[0.16505,0.07815,0.45663],"force_p95":18.37461,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":26.92141,"mean_force":13.54569,"phase_index":2.0,"phase_name":"push_open","phase_type":"push","tcp_position_centroid":[0.09917,0.13518,0.43143]},{"body_a":"door_panel","body_b":"link6","contact_count":2.0,"contact_point_centroid":[0.10314,0.15009,0.53766],"force_p95":16.09427,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":16.22857,"mean_force":14.88565,"phase_index":2.0,"phase_name":"push_open","phase_type":"push","tcp_position_centroid":[0.09933,0.21533,0.43313]},{"body_a":"door_panel","body_b":"link6","contact_count":2.0,"contact_point_centroid":[0.10308,0.15047,0.53832],"force_p95":15.15725,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":15.955,"mean_force":7.9775,"phase_index":1.0,"phase_name":"descend_to_handle","phase_type":"descend","tcp_position_centroid":[0.09939,0.21602,0.4338]},{"body_a":"world","body_b":"door_panel","contact_count":552.0,"contact_point_centroid":[0.30026,0.19249,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"pre_approach","phase_type":"approach","tcp_position_centroid":[0.09965,0.30573,0.39184]},{"body_a":"world","body_b":"door_panel","contact_count":12.0,"contact_point_centroid":[0.30279,0.16527,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"descend_to_handle","phase_type":"descend","tcp_position_centroid":[0.09933,0.21607,0.43395]},{"body_a":"world","body_b":"door_panel","contact_count":988.0,"contact_point_centroid":[0.31581,0.12581,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_open","phase_type":"push","tcp_position_centroid":[0.09918,0.13899,0.43146]}],"total_contact_groups":7},"final_pose_error":0.03551,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.09922,0.04809,0.4314],"hinge_angle":0.5582,"initial_hinge_angle":-0.0604,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":-0.0604,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":68.83123,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":559.0,"n_steps_budget":840.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"pre_approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":730.0,"raw_peak_contact_force":68.83123,"subtask_id":"approach_door","tcp_end":[0.09944,0.21657,0.43431],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.49539,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":11.0,"n_steps_budget":780.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":15.955,"phase_name":"descend_to_handle","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":14.0,"raw_peak_contact_force":15.955,"subtask_id":"approach_door","tcp_end":[0.09933,0.21535,0.43315],"tcp_start":[0.09944,0.21657,0.43431],"tcp_to_object_dist_end":0.49382,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"push_open","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1812.0,"raw_peak_contact_force":26.92141,"subtask_id":"open_door","tcp_end":[0.09922,0.04809,0.4314],"tcp_start":[0.09933,0.21535,0.43315],"tcp_to_object_dist_end":0.44526,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `6091bac9443f311cc90f1388d6700bb5b9c315c724ba8069ca061d7c4a07c1f1`; realized-scene SHA-256: `8483aeff51d0063ec1cf7a724dac4352cd76049b8e216b9602c279ab004268b5`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"fixture","value":[0.5,0.2,0.0]}],"axes":[{"name":"door_hinge_axis","value":[0.0,0.0,1.0]}],"door":{"hinge_axis":[0.0,0.0,1.0],"initial_hinge_angle":0.12924,"panel":{"name":"door_panel","orientation":[0.99791,0.0,0.0,0.06458],"position":[0.5,0.2,0.0]},"target_hinge_angle":0.524},"fixture_states":[],"fixtures":[{"name":"door_panel","orientation":[0.99791,0.0,0.0,0.06458],"position":[0.5,0.2,0.0]}],"limits":[{"name":"goal_tolerance_m","value":0.05},{"name":"force_limit_n","value":30.0},{"name":"force_scale_n","value":5.0},{"name":"target_hinge_angle_rad","value":0.524}],"object_starts":[],"obstacles":[],"targets":[],"task_name":"door_push"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.31944,"average_solve_count":72.0,"average_success_count":72.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"descend_to_handle.contact_threshold":6.24353,"pre_approach.approach_height":0.08399,"pre_approach.approach_speed":0.1791,"push_open.force_guard_threshold":29.97768,"push_open.max_time":4.46238,"push_open.push_distance":0.38051,"push_open.push_speed":0.10164},"optimized_scores":{"best_composite_score":1.12,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link6","contact_count":28.0,"contact_point_centroid":[0.10382,0.14512,0.51125],"force_p95":31.40368,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":39.35713,"mean_force":16.16033,"phase_index":0.0,"phase_name":"pre_approach","phase_type":"approach","tcp_position_centroid":[0.10413,0.21339,0.40566]},{"body_a":"door_panel","body_b":"link7","contact_count":169.0,"contact_point_centroid":[0.1702,0.11746,0.44133],"force_p95":22.11997,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":34.09069,"mean_force":15.91072,"phase_index":0.0,"phase_name":"pre_approach","phase_type":"approach","tcp_position_centroid":[0.10491,0.17484,0.41752]},{"body_a":"door_panel","body_b":"link7","contact_count":724.0,"contact_point_centroid":[0.17451,0.01071,0.45122],"force_p95":20.08091,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":28.77309,"mean_force":13.54349,"phase_index":2.0,"phase_name":"push_open","phase_type":"push","tcp_position_centroid":[0.10558,0.06387,0.42525]},{"body_a":"door_panel","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.17098,0.0842,0.45115],"force_p95":16.41536,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":17.27932,"mean_force":8.63966,"phase_index":1.0,"phase_name":"descend_to_handle","phase_type":"descend","tcp_position_centroid":[0.10567,0.14165,0.4274]},{"body_a":"world","body_b":"door_panel","contact_count":716.0,"contact_point_centroid":[0.30424,0.15937,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"pre_approach","phase_type":"approach","tcp_position_centroid":[0.10255,0.28082,0.38459]},{"body_a":"world","body_b":"door_panel","contact_count":4.0,"contact_point_centroid":[0.31475,0.12395,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"descend_to_handle","phase_type":"descend","tcp_position_centroid":[0.10571,0.14119,0.42705]},{"body_a":"world","body_b":"door_panel","contact_count":920.0,"contact_point_centroid":[0.33244,0.09221,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_open","phase_type":"push","tcp_position_centroid":[0.10558,0.06399,0.42527]}],"total_contact_groups":7},"final_pose_error":0.21347,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.10561,-0.02599,0.42539],"hinge_angle":0.68287,"initial_hinge_angle":0.12924,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.12924,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":39.35713,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":713.0,"n_steps_budget":990.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":12.57391,"phase_name":"pre_approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":913.0,"raw_peak_contact_force":39.35713,"subtask_id":"approach_door","tcp_end":[0.10562,0.14212,0.42774],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.46295,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":9.0,"n_steps_budget":780.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":17.27932,"phase_name":"descend_to_handle","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":6.0,"raw_peak_contact_force":17.27932,"subtask_id":"approach_door","tcp_end":[0.10574,0.14105,0.42691],"tcp_start":[0.10562,0.14212,0.42774],"tcp_to_object_dist_end":0.46188,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"push_open","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1644.0,"raw_peak_contact_force":28.77309,"subtask_id":"open_door","tcp_end":[0.10561,-0.02599,0.42539],"tcp_start":[0.10574,0.14105,0.42691],"tcp_to_object_dist_end":0.43907,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `3d62b54ff2d8b84e841b6e4711bcf5c00d2771c3332b770c71c3a72dad860645`; realized-scene SHA-256: `0f1da74cddf6e66211f4104e2813e757573c0ccccbad31f53b6672ec96f686dd`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"fixture","value":[0.5,0.2,0.0]}],"axes":[{"name":"door_hinge_axis","value":[0.0,0.0,1.0]}],"door":{"hinge_axis":[0.0,0.0,1.0],"initial_hinge_angle":0.15917,"panel":{"name":"door_panel","orientation":[0.99683,0.0,0.0,0.0795],"position":[0.5,0.2,0.0]},"target_hinge_angle":0.524},"fixture_states":[],"fixtures":[{"name":"door_panel","orientation":[0.99683,0.0,0.0,0.0795],"position":[0.5,0.2,0.0]}],"limits":[{"name":"goal_tolerance_m","value":0.05},{"name":"force_limit_n","value":30.0},{"name":"force_scale_n","value":5.0},{"name":"target_hinge_angle_rad","value":0.524}],"object_starts":[],"obstacles":[],"targets":[],"task_name":"door_push"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.37975,"average_solve_count":79.0,"average_success_count":79.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"descend_to_handle.contact_threshold":6.04979,"pre_approach.approach_height":0.14472,"pre_approach.approach_speed":0.16558,"push_open.force_guard_threshold":26.16997,"push_open.max_time":6.42298,"push_open.push_distance":0.25221,"push_open.push_speed":0.09617},"optimized_scores":{"best_composite_score":1.12,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link7","contact_count":198.0,"contact_point_centroid":[0.17203,0.11026,0.4901],"force_p95":29.11635,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":37.76474,"mean_force":17.44139,"phase_index":0.0,"phase_name":"pre_approach","phase_type":"approach","tcp_position_centroid":[0.10666,0.16762,0.46637]},{"body_a":"door_panel","body_b":"link7","contact_count":726.0,"contact_point_centroid":[0.17715,0.00123,0.50922],"force_p95":18.72656,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":25.87339,"mean_force":13.01496,"phase_index":2.0,"phase_name":"push_open","phase_type":"push","tcp_position_centroid":[0.10766,0.05375,0.48314]},{"body_a":"door_panel","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.17321,0.07109,0.50928],"force_p95":12.17285,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":12.81352,"mean_force":6.40676,"phase_index":1.0,"phase_name":"descend_to_handle","phase_type":"descend","tcp_position_centroid":[0.10782,0.12853,0.48561]},{"body_a":"door_panel","body_b":"link6","contact_count":5.0,"contact_point_centroid":[0.10492,0.1377,0.55271],"force_p95":0.0,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"pre_approach","phase_type":"approach","tcp_position_centroid":[0.10568,0.20487,0.44746]},{"body_a":"world","body_b":"door_panel","contact_count":924.0,"contact_point_centroid":[0.30589,0.15234,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"pre_approach","phase_type":"approach","tcp_position_centroid":[0.10379,0.26699,0.41538]},{"body_a":"world","body_b":"door_panel","contact_count":12.0,"contact_point_centroid":[0.31761,0.11733,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"descend_to_handle","phase_type":"descend","tcp_position_centroid":[0.10777,0.1287,0.4859]},{"body_a":"world","body_b":"door_panel","contact_count":928.0,"contact_point_centroid":[0.33498,0.08809,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_open","phase_type":"push","tcp_position_centroid":[0.10766,0.05453,0.48314]}],"total_contact_groups":7},"final_pose_error":0.09545,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.10766,-0.0288,0.48325],"hinge_angle":0.69113,"initial_hinge_angle":0.15917,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.15917,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":37.76474,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":850.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":4.92593,"phase_name":"pre_approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1127.0,"raw_peak_contact_force":37.76474,"subtask_id":"approach_door","tcp_end":[0.10774,0.129,0.48628],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.51451,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":12.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":12.81352,"phase_name":"descend_to_handle","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":14.0,"raw_peak_contact_force":12.81352,"subtask_id":"approach_door","tcp_end":[0.10791,0.12796,0.48478],"tcp_start":[0.10774,0.129,0.48628],"tcp_to_object_dist_end":0.51286,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":10.63872,"phase_name":"push_open","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1654.0,"raw_peak_contact_force":25.87339,"subtask_id":"open_door","tcp_end":[0.10766,-0.0288,0.48325],"tcp_start":[0.10791,0.12796,0.48478],"tcp_to_object_dist_end":0.49594,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
```