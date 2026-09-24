## Search State

- **Seed**: 9
- **Iteration**: 14 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 13 | approach → align → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 7 | 0.5776 | 0.93 | ✅ accepted |
| 12 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 6 | 0.7771 | 0.91 | ❌ rejected |
| 11 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 5 | 0.7326 | 0.93 | ✅ accepted |
| 10 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 6 | 0.7733 | 0.91 | ✅ accepted |
| 9 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 6 | 0.8635 | 0.89 | ✅ accepted |

**Proposal policy**: task_score is near-perfect (0.93). Preserve useful working parts and make only evidence-backed refinements. A HOLD is acceptable if you genuinely cannot find a better structure.

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
- Frozen realised-scene SHA-256: `8483aeff51d0063ec1cf7a724dac4352cd76049b8e216b9602c279ab004268b5`
- Frozen initial hinge angle: 0.129 rad
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
  frozen_initial_hinge_angle_rad: 0.1292
  frozen_fixtures: {'door_panel': [0.5, 0.2, 0.0]}
  door_hinge_axis: [0, 0, 1]
  goal_tolerance_m: 0.05
  force_limit_n: 30
  force_scale_n: 5
  target_hinge_angle_rad: 0.524
  realized_scene_sha256: 8483aeff51d0063ec1cf7a724dac4352cd76049b8e216b9602c279ab004268b5

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.934, which indicates the subtask decomposition is already effective.
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

## Current Skill (Q=0.578) — your mutation base

```yaml
skill: door_push
dsl_version: 2
subtasks:
- id: reach_handle
  offset:
  - 0.0
  - 0.0
  - 0.05
  weight: 0.3
- id: open_door
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
    anchor: task_goal
    offset:
    - 0.0
    - 0.2
    - 0.1
    tolerance: 0.03
    orientation:
      mode: keep_current
      tolerance: 0.2
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: generator.speed
        mode: add
  subtask_id: reach_handle
- id: align_to_handle
  type: align
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.1
    tolerance: 0.03
    orientation:
      mode: keep_current
      tolerance: 0.2
  parameters:
    align_speed:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: generator.speed
        mode: add
  subtask_id: reach_handle
- id: descend_to_contact
  type: descend
  generator: linear_cartesian
  control: force_threshold_switch
  termination: force_exceeded
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.0
    orientation:
      mode: keep_current
      tolerance: 0.2
  parameters:
    descend_force_threshold:
      type: scalar
      range:
      - 5.0
      - 20.0
      default: 10.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    descend_retry_offset_y:
      type: scalar
      range:
      - -0.02
      - 0.02
      default: -0.01
      binds_to:
      - path: retry.offset.y
        mode: replace
    descend_speed:
      type: scalar
      range:
      - 0.01
      - 0.08
      default: 0.04
      binds_to:
      - path: generator.speed
        mode: add
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - -0.01
    - 0.0
  subtask_id: reach_handle
- id: push_door
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
      distance: 0.2
      axis: world_y
      mode: add_to_offset
      sign: negative
    orientation:
      mode: keep_current
      tolerance: 0.2
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.05
      - 0.4
      default: 0.2
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
  subtask_id: open_door
- id: retract_to_goal
  type: retract
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: world
    offset:
    - 0.1
    - 0.18
    - 0.35
    tolerance: 0.03
    orientation:
      mode: keep_current
      tolerance: 0.2
  parameters:
    retract_speed:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: generator.speed
        mode: add
  subtask_id: reach_handle

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_handle** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.2, 0.1], tolerance=0.03
  - orientation: mode=keep_current, tolerance=0.2
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (add)
- **align_to_handle** (`align`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.1], tolerance=0.03
  - orientation: mode=keep_current, tolerance=0.2
  - parameter_bindings:
    - align_speed: status=consumed; consumers=generator.speed (add)
- **descend_to_contact** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current, tolerance=0.2
  - parameter_bindings:
    - descend_force_threshold: status=consumed; consumers=termination.force_threshold (replace)
    - descend_retry_offset_y: status=consumed; consumers=retry.offset.y (replace)
    - descend_speed: status=consumed; consumers=generator.speed (add)
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, -0.01, 0.0]
- **push_door** (`push`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_y, distance=0.2, mode=add_to_offset, sign=negative}
  - orientation: mode=keep_current, tolerance=0.2
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
- **retract_to_goal** (`retract`)
  - target: source=yaml, anchor=world, offset=[0.1, 0.18, 0.35], tolerance=0.03
  - orientation: mode=keep_current, tolerance=0.2
  - parameter_bindings:
    - retract_speed: status=consumed; consumers=generator.speed (add)

## Design Metrics

- **Composite score**: 0.578
- **task_score** (E): 0.934
- **fitness_score**: 0.934  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.083
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.440

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_handle | 1.00 | 0.00 | 0.0723 |
| align_to_handle | 1.00 | 1.00 | 0.1774 |
| descend_to_contact | 0.33 | 0.33 | 0.0652 |
| push_door | 1.00 | 0.33 | 0.1706 |
| retract_to_goal | 1.00 | 0.33 | 0.1378 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_handle | approach | 1.00 / step_budget | (0.100, 0.399, 0.350)→(0.101, 0.385, 0.421) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 0.00 / 0.000 | 0.000 | 0.000 |
| align_to_handle | align | 1.00 / step_budget | (0.101, 0.385, 0.421)→(0.101, 0.209, 0.445) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 2.000 | 5.561 | 30.776 |
| descend_to_contact | descend | 0.33 / step_budget | (0.101, 0.209, 0.445)→(0.100, 0.190, 0.383) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 0.33 / 0.333 | 4.126 | 16.748 |
| push_door | push | 1.00 / time_limit | (0.100, 0.190, 0.383)→(0.099, 0.026, 0.414) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 0.33 / 1.667 | 6.367 | 40.179 |
| retract_to_goal | retract | 1.00 / step_budget | (0.099, 0.026, 0.414)→(0.101, 0.156, 0.368) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 0.33 / 1.333 | 0.000 | 4.347 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- hinge_angle_ratio: 1.000
- arc_quality: 1.000

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 1.000
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.490
- **K-run variance**: 0.0275
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.419


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `d324a70682be50916187e25da5a0a59a7678607fbe49b53fdc39aa246f41ddf9`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"hinge_delta_deg":10.0,"object_xy_delta":[0.0,0.0]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `d82b7d31aa43f8d3a4479d5f34069ef44e70dc4ca62021414a1e013fa43805ad`; realized-scene SHA-256: `8483aeff51d0063ec1cf7a724dac4352cd76049b8e216b9602c279ab004268b5`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"fixture","value":[0.5,0.2,0.0]}],"axes":[{"name":"door_hinge_axis","value":[0.0,0.0,1.0]}],"door":{"hinge_axis":[0.0,0.0,1.0],"initial_hinge_angle":0.12924,"panel":{"name":"door_panel","orientation":[0.99791,0.0,0.0,0.06458],"position":[0.5,0.2,0.0]},"target_hinge_angle":0.524},"fixture_states":[],"fixtures":[{"name":"door_panel","orientation":[0.99791,0.0,0.0,0.06458],"position":[0.5,0.2,0.0]}],"limits":[{"name":"goal_tolerance_m","value":0.05},{"name":"force_limit_n","value":30.0},{"name":"force_scale_n","value":5.0},{"name":"target_hinge_angle_rad","value":0.524}],"object_starts":[],"obstacles":[],"targets":[],"task_name":"door_push"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.36196,"average_solve_count":163.0,"average_success_count":163.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_to_handle.align_speed":0.10213,"approach_handle.approach_speed":0.16417,"descend_to_contact.descend_force_threshold":19.98372,"descend_to_contact.descend_retry_offset_y":-0.01243,"descend_to_contact.descend_speed":0.04573,"push_door.push_distance":0.31878,"retract_to_goal.retract_speed":0.21855},"optimized_scores":{"best_composite_score":0.49013,"best_fitness_score":0.93013,"best_task_score":0.93013},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link7","contact_count":703.0,"contact_point_centroid":[0.16393,0.04693,0.4184],"force_p95":23.1977,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":43.76159,"mean_force":13.75827,"phase_index":3.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.09808,0.10286,0.39102]},{"body_a":"door_panel","body_b":"link7","contact_count":8.0,"contact_point_centroid":[0.16581,0.1554,0.46895],"force_p95":36.2762,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":36.75614,"mean_force":25.21453,"phase_index":1.0,"phase_name":"align_to_handle","phase_type":"align","tcp_position_centroid":[0.10076,0.21215,0.44446]},{"body_a":"door_panel","body_b":"link7","contact_count":243.0,"contact_point_centroid":[0.16526,0.13719,0.42251],"force_p95":16.31457,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":17.54117,"mean_force":13.44343,"phase_index":2.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.10011,0.19447,0.39785]},{"body_a":"door_panel","body_b":"link6","contact_count":8.0,"contact_point_centroid":[0.10358,0.14771,0.54964],"force_p95":0.03633,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0559,"mean_force":0.00699,"phase_index":1.0,"phase_name":"align_to_handle","phase_type":"align","tcp_position_centroid":[0.10076,0.21215,0.44446]},{"body_a":"world","body_b":"door_panel","contact_count":156.0,"contact_point_centroid":[0.30294,0.16438,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.10038,0.39229,0.38201]},{"body_a":"world","body_b":"door_panel","contact_count":288.0,"contact_point_centroid":[0.3029,0.1646,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"align_to_handle","phase_type":"align","tcp_position_centroid":[0.1006,0.30586,0.43087]},{"body_a":"world","body_b":"door_panel","contact_count":712.0,"contact_point_centroid":[0.30531,0.15338,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.10012,0.19463,0.39843]},{"body_a":"world","body_b":"door_panel","contact_count":912.0,"contact_point_centroid":[0.3213,0.11249,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":3.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.09841,0.10957,0.38713]},{"body_a":"world","body_b":"door_panel","contact_count":216.0,"contact_point_centroid":[0.34312,0.07555,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":4.0,"phase_name":"retract_to_goal","phase_type":"retract","tcp_position_centroid":[0.10051,0.08167,0.40007]}],"total_contact_groups":9},"final_pose_error":0.02979,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.10135,0.15486,0.36592],"hinge_angle":0.61663,"initial_hinge_angle":0.12924,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.12924,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":43.76159,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":131.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"approach_handle","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":156.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_handle","tcp_end":[0.1005,0.38489,0.42094],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.57917,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":275.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.48855,"phase_name":"align_to_handle","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":304.0,"raw_peak_contact_force":36.75614,"subtask_id":"reach_handle","tcp_end":[0.10077,0.20931,0.44488],"tcp_start":[0.1005,0.38489,0.42094],"tcp_to_object_dist_end":0.50188,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":652.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":955.0,"raw_peak_contact_force":17.54117,"subtask_id":"reach_handle","tcp_end":[0.0998,0.18104,0.35488],"tcp_start":[0.10077,0.20931,0.44488],"tcp_to_object_dist_end":0.4107,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"push_door","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1615.0,"raw_peak_contact_force":43.76159,"subtask_id":"open_door","tcp_end":[0.10019,0.00908,0.41408],"tcp_start":[0.0998,0.18104,0.35488],"tcp_to_object_dist_end":0.42612,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":276.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"retract_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":216.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_handle","tcp_end":[0.10135,0.15486,0.36592],"tcp_start":[0.10019,0.00908,0.41408],"tcp_to_object_dist_end":0.41006,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `1fec9e8e5c1fdb9e52be404e6e4e2b90974542a257bfa7ba08d11c8aa9beb00c`; realized-scene SHA-256: `0f1da74cddf6e66211f4104e2813e757573c0ccccbad31f53b6672ec96f686dd`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"fixture","value":[0.5,0.2,0.0]}],"axes":[{"name":"door_hinge_axis","value":[0.0,0.0,1.0]}],"door":{"hinge_axis":[0.0,0.0,1.0],"initial_hinge_angle":0.15917,"panel":{"name":"door_panel","orientation":[0.99683,0.0,0.0,0.0795],"position":[0.5,0.2,0.0]},"target_hinge_angle":0.524},"fixture_states":[],"fixtures":[{"name":"door_panel","orientation":[0.99683,0.0,0.0,0.0795],"position":[0.5,0.2,0.0]}],"limits":[{"name":"goal_tolerance_m","value":0.05},{"name":"force_limit_n","value":30.0},{"name":"force_scale_n","value":5.0},{"name":"target_hinge_angle_rad","value":0.524}],"object_starts":[],"obstacles":[],"targets":[],"task_name":"door_push"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.37888,"average_solve_count":161.0,"average_success_count":161.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_to_handle.align_speed":0.21139,"approach_handle.approach_speed":0.11132,"descend_to_contact.descend_force_threshold":17.56101,"descend_to_contact.descend_retry_offset_y":-0.00078,"descend_to_contact.descend_speed":0.03254,"push_door.push_distance":0.34378,"retract_to_goal.retract_speed":0.18637},"optimized_scores":{"best_composite_score":0.43278,"best_fitness_score":0.87278,"best_task_score":0.87278},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link7","contact_count":702.0,"contact_point_centroid":[0.16386,0.04752,0.41824],"force_p95":24.34595,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":43.75045,"mean_force":13.81143,"phase_index":3.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.09808,0.10349,0.39081]},{"body_a":"door_panel","body_b":"link7","contact_count":218.0,"contact_point_centroid":[0.16521,0.13545,0.41755],"force_p95":16.06222,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":16.48835,"mean_force":13.57658,"phase_index":2.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.10013,0.19278,0.39279]},{"body_a":"world","body_b":"door_panel","contact_count":156.0,"contact_point_centroid":[0.3041,0.15851,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.10036,0.39264,0.38012]},{"body_a":"world","body_b":"door_panel","contact_count":296.0,"contact_point_centroid":[0.30404,0.15878,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"align_to_handle","phase_type":"align","tcp_position_centroid":[0.10076,0.30298,0.43155]},{"body_a":"world","body_b":"door_panel","contact_count":692.0,"contact_point_centroid":[0.30531,0.15331,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.10019,0.19487,0.3997]},{"body_a":"world","body_b":"door_panel","contact_count":864.0,"contact_point_centroid":[0.32276,0.1099,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":3.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.09815,0.10298,0.39002]},{"body_a":"world","body_b":"door_panel","contact_count":284.0,"contact_point_centroid":[0.34314,0.07552,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":4.0,"phase_name":"retract_to_goal","phase_type":"retract","tcp_position_centroid":[0.10046,0.07572,0.40204]}],"total_contact_groups":7},"final_pose_error":0.02996,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.10132,0.15466,0.36594],"hinge_angle":0.61651,"initial_hinge_angle":0.15917,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.15917,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":43.75045,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":131.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"approach_handle","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":156.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_handle","tcp_end":[0.1005,0.38489,0.42094],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.57917,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":253.0,"n_steps_budget":630.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"align_to_handle","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":296.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_handle","tcp_end":[0.10089,0.20918,0.44533],"tcp_start":[0.1005,0.38489,0.42094],"tcp_to_object_dist_end":0.50225,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":659.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":910.0,"raw_peak_contact_force":16.48835,"subtask_id":"reach_handle","tcp_end":[0.09981,0.18102,0.35487],"tcp_start":[0.10089,0.20918,0.44533],"tcp_to_object_dist_end":0.41069,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"push_door","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1566.0,"raw_peak_contact_force":43.75045,"subtask_id":"open_door","tcp_end":[0.1002,0.00911,0.4141],"tcp_start":[0.09981,0.18102,0.35487],"tcp_to_object_dist_end":0.42615,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":278.0,"n_steps_budget":630.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"retract_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":284.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_handle","tcp_end":[0.10132,0.15466,0.36594],"tcp_start":[0.1002,0.00911,0.4141],"tcp_to_object_dist_end":0.40999,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `3715cb43c8f8f3084ca346701c1c33fec8eb1e50d1b8785cdad3bdd48e46f29f`; realized-scene SHA-256: `a85e6d1e7f42d6b7853e30231dc3bdf8d0b19eb5c068167ff162abd11c92b77d`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"fixture","value":[0.5,0.2,0.0]}],"axes":[{"name":"door_hinge_axis","value":[0.0,0.0,1.0]}],"door":{"hinge_axis":[0.0,0.0,1.0],"initial_hinge_angle":-0.12965,"panel":{"name":"door_panel","orientation":[0.9979,0.0,0.0,-0.06478],"position":[0.5,0.2,0.0]},"target_hinge_angle":0.524},"fixture_states":[],"fixtures":[{"name":"door_panel","orientation":[0.9979,0.0,0.0,-0.06478],"position":[0.5,0.2,0.0]}],"limits":[{"name":"goal_tolerance_m","value":0.05},{"name":"force_limit_n","value":30.0},{"name":"force_scale_n","value":5.0},{"name":"target_hinge_angle_rad","value":0.524}],"object_starts":[],"obstacles":[],"targets":[],"task_name":"door_push"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.37719,"average_solve_count":114.0,"average_success_count":114.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_to_handle.align_speed":0.14399,"approach_handle.approach_speed":0.22103,"descend_to_contact.descend_force_threshold":11.88926,"descend_to_contact.descend_retry_offset_y":-0.00592,"descend_to_contact.descend_speed":0.03416,"push_door.push_distance":0.15166,"retract_to_goal.retract_speed":0.20458},"optimized_scores":{"best_composite_score":0.81,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link6","contact_count":129.0,"contact_point_centroid":[0.10105,0.19488,0.54429],"force_p95":39.91815,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":55.57122,"mean_force":21.90254,"phase_index":1.0,"phase_name":"align_to_handle","phase_type":"align","tcp_position_centroid":[0.10039,0.26899,0.43588]},{"body_a":"door_panel","body_b":"link7","contact_count":731.0,"contact_point_centroid":[0.16506,0.07911,0.43516],"force_p95":20.92415,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":33.02495,"mean_force":13.68609,"phase_index":3.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.09972,0.13624,0.40921]},{"body_a":"door_panel","body_b":"link7","contact_count":8.0,"contact_point_centroid":[0.16569,0.15489,0.46912],"force_p95":27.12726,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":29.80048,"mean_force":18.36113,"phase_index":1.0,"phase_name":"align_to_handle","phase_type":"align","tcp_position_centroid":[0.1006,0.21179,0.44453]},{"body_a":"door_panel","body_b":"link7","contact_count":12.0,"contact_point_centroid":[0.16541,0.15074,0.46772],"force_p95":16.0619,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":16.21438,"mean_force":8.80288,"phase_index":2.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.10032,0.20787,0.44308]},{"body_a":"door_panel","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.16217,0.00323,0.44284],"force_p95":12.38873,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":13.04077,"mean_force":6.52038,"phase_index":4.0,"phase_name":"retract_to_goal","phase_type":"retract","tcp_position_centroid":[0.09753,0.06106,0.41272]},{"body_a":"world","body_b":"door_panel","contact_count":136.0,"contact_point_centroid":[0.30005,0.21094,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.1004,0.39177,0.38436]},{"body_a":"world","body_b":"door_panel","contact_count":228.0,"contact_point_centroid":[0.30039,0.19626,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"align_to_handle","phase_type":"align","tcp_position_centroid":[0.1004,0.3022,0.43142]},{"body_a":"world","body_b":"door_panel","contact_count":56.0,"contact_point_centroid":[0.30365,0.16069,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.10025,0.20764,0.44251]},{"body_a":"world","body_b":"door_panel","contact_count":912.0,"contact_point_centroid":[0.31692,0.12189,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":3.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.09966,0.1319,0.40832]},{"body_a":"world","body_b":"door_panel","contact_count":176.0,"contact_point_centroid":[0.33215,0.09079,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":4.0,"phase_name":"retract_to_goal","phase_type":"retract","tcp_position_centroid":[0.09865,0.10748,0.39852]}],"total_contact_groups":10},"final_pose_error":0.02997,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.10027,0.15945,0.37181],"hinge_angle":0.52445,"initial_hinge_angle":-0.12965,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":-0.12965,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":55.57122,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":131.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"approach_handle","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":136.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_handle","tcp_end":[0.1005,0.38489,0.42094],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.57917,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":267.0,"n_steps_budget":900.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":16.19395,"phase_name":"align_to_handle","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":365.0,"raw_peak_contact_force":55.57122,"subtask_id":"reach_handle","tcp_end":[0.1006,0.20898,0.44497],"tcp_start":[0.1005,0.38489,0.42094],"tcp_to_object_dist_end":0.50179,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":50.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":12.3782,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":68.0,"raw_peak_contact_force":16.21438,"subtask_id":"reach_handle","tcp_end":[0.10024,0.20672,0.4389],"tcp_start":[0.1006,0.20898,0.44497],"tcp_to_object_dist_end":0.49539,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":19.09992,"phase_name":"push_door","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1643.0,"raw_peak_contact_force":33.02495,"subtask_id":"open_door","tcp_end":[0.09755,0.06107,0.41268],"tcp_start":[0.10024,0.20672,0.4389],"tcp_to_object_dist_end":0.42843,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":191.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"retract_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":178.0,"raw_peak_contact_force":13.04077,"subtask_id":"reach_handle","tcp_end":[0.10027,0.15945,0.37181],"tcp_start":[0.09755,0.06107,0.41268],"tcp_to_object_dist_end":0.41679,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```