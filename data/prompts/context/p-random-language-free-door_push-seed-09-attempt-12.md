## Search State

- **Seed**: 9
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 6 | 0.7771 | 0.91 | ❌ rejected |
| 11 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 5 | 0.7326 | 0.93 | ✅ accepted |
| 10 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 6 | 0.7733 | 0.91 | ✅ accepted |
| 9 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 6 | 0.8635 | 0.89 | ✅ accepted |
| 8 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | time_limit | 6 | 0.9460 | 0.78 | ❌ rejected |

**Proposal policy**: task_score is near-perfect (0.91). Preserve useful working parts and make only evidence-backed refinements. A HOLD is acceptable if you genuinely cannot find a better structure.

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

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.931, which indicates the subtask decomposition is already effective.
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

## Current Skill (Q=0.777) — your mutation base

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
    - 0.0
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
    descend_speed:
      type: scalar
      range:
      - 0.01
      - 0.08
      default: 0.04
      binds_to:
      - path: generator.speed
        mode: add
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
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.1], tolerance=0.03
  - orientation: mode=keep_current, tolerance=0.2
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (add)
- **descend_to_contact** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current, tolerance=0.2
  - parameter_bindings:
    - descend_force_threshold: status=consumed; consumers=termination.force_threshold (replace)
    - descend_speed: status=consumed; consumers=generator.speed (add)
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

- **Composite score**: 0.777
- **task_score** (E): 0.915
- **fitness_score**: 0.915  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.222
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.360

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_handle | 1.00 | 0.33 | 0.2112 |
| descend_to_contact | 1.00 | 1.00 | 0.0461 |
| push_door | 1.00 | 0.67 | 0.1695 |
| retract_to_goal | 1.00 | 0.00 | 0.1369 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_handle | approach | 1.00 / step_budget | (0.100, 0.399, 0.350)→(0.101, 0.207, 0.437) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 0.33 / 0.333 | 6.351 | 47.465 |
| descend_to_contact | descend | 1.00 / force_exceeded | (0.101, 0.207, 0.437)→(0.100, 0.193, 0.393) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 3.667 | 15.694 | 18.179 |
| push_door | push | 1.00 / time_limit | (0.100, 0.193, 0.393)→(0.099, 0.027, 0.414) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 0.67 / 3.333 | 10.475 | 37.837 |
| retract_to_goal | retract | 1.00 / step_budget | (0.099, 0.027, 0.414)→(0.101, 0.156, 0.368) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 0.00 / 0.000 | 0.000 | 3.640 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- hinge_angle_ratio: 1.000
- arc_quality: 1.000

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 1.000
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.785
- **K-run variance**: 0.0268
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.324


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.97701,"average_solve_count":174.0,"average_success_count":174.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_handle.approach_speed":0.15395,"descend_to_contact.descend_force_threshold":16.52439,"descend_to_contact.descend_retry_offset_y":-0.01229,"descend_to_contact.descend_speed":0.02178,"push_door.push_distance":0.35889,"retract_to_goal.retract_speed":0.25436},"optimized_scores":{"best_composite_score":0.57274,"best_fitness_score":0.93274,"best_task_score":0.93274},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link7","contact_count":12.0,"contact_point_centroid":[0.16604,0.15394,0.45888],"force_p95":41.97522,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":51.21232,"mean_force":23.66476,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.10096,0.2112,0.43467]},{"body_a":"door_panel","body_b":"link7","contact_count":702.0,"contact_point_centroid":[0.16392,0.04626,0.4193],"force_p95":22.09655,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":43.69647,"mean_force":13.77907,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.09802,0.10231,0.39205]},{"body_a":"door_panel","body_b":"link6","contact_count":7.0,"contact_point_centroid":[0.10359,0.14797,0.53843],"force_p95":25.45469,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":26.08785,"mean_force":7.15216,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.10098,0.21334,0.43375]},{"body_a":"door_panel","body_b":"link7","contact_count":226.0,"contact_point_centroid":[0.16531,0.13501,0.4157],"force_p95":15.32396,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":16.61832,"mean_force":13.39248,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.10018,0.19245,0.39133]},{"body_a":"world","body_b":"door_panel","contact_count":356.0,"contact_point_centroid":[0.30294,0.1644,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.10071,0.30911,0.3896]},{"body_a":"world","body_b":"door_panel","contact_count":712.0,"contact_point_centroid":[0.30533,0.15326,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.10025,0.19471,0.39872]},{"body_a":"world","body_b":"door_panel","contact_count":912.0,"contact_point_centroid":[0.32232,0.11043,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.0982,0.10494,0.39071]},{"body_a":"world","body_b":"door_panel","contact_count":292.0,"contact_point_centroid":[0.34333,0.07528,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":3.0,"phase_name":"retract_to_goal","phase_type":"retract","tcp_position_centroid":[0.1006,0.07605,0.4019]}],"total_contact_groups":8},"final_pose_error":0.02964,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.10136,0.15515,0.3661],"hinge_angle":0.618,"initial_hinge_angle":0.12924,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.12924,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":51.21232,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":317.0,"n_steps_budget":990.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"approach_handle","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":375.0,"raw_peak_contact_force":51.21232,"subtask_id":"reach_handle","tcp_end":[0.10093,0.20678,0.43664],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.49355,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":641.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":12.18552,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":938.0,"raw_peak_contact_force":16.61832,"subtask_id":"reach_handle","tcp_end":[0.09982,0.18104,0.35487],"tcp_start":[0.10093,0.20678,0.43664],"tcp_to_object_dist_end":0.4107,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"push_door","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1614.0,"raw_peak_contact_force":43.69647,"subtask_id":"open_door","tcp_end":[0.1004,0.00882,0.41395],"tcp_start":[0.09982,0.18104,0.35487],"tcp_to_object_dist_end":0.42605,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":278.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"retract_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":292.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_handle","tcp_end":[0.10136,0.15515,0.3661],"tcp_start":[0.1004,0.00882,0.41395],"tcp_to_object_dist_end":0.41033,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.75,"average_solve_count":100.0,"average_success_count":100.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_handle.approach_speed":0.18359,"descend_to_contact.descend_force_threshold":16.68393,"descend_to_contact.descend_retry_offset_y":-0.00784,"descend_to_contact.descend_speed":0.06967,"push_door.push_distance":0.36638,"retract_to_goal.retract_speed":0.18566},"optimized_scores":{"best_composite_score":0.78525,"best_fitness_score":0.81192,"best_task_score":0.81192},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link7","contact_count":746.0,"contact_point_centroid":[0.16525,0.05976,0.42186],"force_p95":21.79969,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":37.58819,"mean_force":13.66825,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.0996,0.11672,0.39553]},{"body_a":"door_panel","body_b":"link7","contact_count":91.0,"contact_point_centroid":[0.16565,0.14189,0.43762],"force_p95":17.41788,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":21.26618,"mean_force":13.67652,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.10045,0.19925,0.41328]},{"body_a":"world","body_b":"door_panel","contact_count":384.0,"contact_point_centroid":[0.30407,0.15864,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.10076,0.30497,0.39143]},{"body_a":"world","body_b":"door_panel","contact_count":256.0,"contact_point_centroid":[0.30458,0.15632,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.10048,0.20013,0.41621]},{"body_a":"world","body_b":"door_panel","contact_count":908.0,"contact_point_centroid":[0.32164,0.11194,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.09949,0.10956,0.39635]},{"body_a":"door_panel","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.16784,-0.02286,0.4426],"force_p95":0.0,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":3.0,"phase_name":"retract_to_goal","phase_type":"retract","tcp_position_centroid":[0.09777,0.02727,0.41609]},{"body_a":"world","body_b":"door_panel","contact_count":232.0,"contact_point_centroid":[0.33916,0.08072,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":3.0,"phase_name":"retract_to_goal","phase_type":"retract","tcp_position_centroid":[0.09872,0.09426,0.40096]}],"total_contact_groups":7},"final_pose_error":0.02982,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.10045,0.15792,0.37003],"hinge_angle":0.58462,"initial_hinge_angle":0.15917,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.15917,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":37.58819,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":312.0,"n_steps_budget":840.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"approach_handle","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":384.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_handle","tcp_end":[0.10098,0.20681,0.43698],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.49389,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":285.0,"n_steps_budget":840.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":18.58857,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":347.0,"raw_peak_contact_force":21.26618,"subtask_id":"reach_handle","tcp_end":[0.10025,0.19365,0.39518],"tcp_start":[0.10098,0.20681,0.43698],"tcp_to_object_dist_end":0.45136,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":17.65102,"phase_name":"push_door","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1654.0,"raw_peak_contact_force":37.58819,"subtask_id":"open_door","tcp_end":[0.09777,0.02727,0.41609],"tcp_start":[0.10025,0.19365,0.39518],"tcp_to_object_dist_end":0.42829,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":260.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"retract_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":233.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_handle","tcp_end":[0.10045,0.15792,0.37003],"tcp_start":[0.09777,0.02727,0.41609],"tcp_to_object_dist_end":0.41467,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.47778,"average_solve_count":90.0,"average_success_count":90.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_handle.approach_speed":0.20438,"descend_to_contact.descend_force_threshold":12.74905,"descend_to_contact.descend_retry_offset_y":-0.013,"descend_to_contact.descend_speed":0.05253,"push_door.push_distance":0.26667,"retract_to_goal.retract_speed":0.14354},"optimized_scores":{"best_composite_score":0.97333,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link6","contact_count":121.0,"contact_point_centroid":[0.10111,0.19279,0.51608],"force_p95":52.39336,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":91.18156,"mean_force":28.74095,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.10065,0.2679,0.40805]},{"body_a":"door_panel","body_b":"link7","contact_count":785.0,"contact_point_centroid":[0.16566,0.0711,0.43545],"force_p95":19.5344,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":32.22772,"mean_force":13.33847,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.10004,0.12823,0.4097]},{"body_a":"door_panel","body_b":"link7","contact_count":11.0,"contact_point_centroid":[0.16594,0.15275,0.45932],"force_p95":26.83704,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":27.48832,"mean_force":19.57863,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.10079,0.20978,0.43509]},{"body_a":"door_panel","body_b":"link7","contact_count":8.0,"contact_point_centroid":[0.16562,0.14732,0.45697],"force_p95":16.53284,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":16.6533,"mean_force":9.16754,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.10052,0.20473,0.43267]},{"body_a":"door_panel","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.16435,-0.01184,0.43999],"force_p95":10.37258,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":10.91851,"mean_force":5.45925,"phase_index":3.0,"phase_name":"retract_to_goal","phase_type":"retract","tcp_position_centroid":[0.09888,0.04568,0.41106]},{"body_a":"world","body_b":"door_panel","contact_count":320.0,"contact_point_centroid":[0.30051,0.19524,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.1006,0.30281,0.39203]},{"body_a":"world","body_b":"door_panel","contact_count":80.0,"contact_point_centroid":[0.30406,0.15869,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.10043,0.2048,0.43348]},{"body_a":"world","body_b":"door_panel","contact_count":1004.0,"contact_point_centroid":[0.31744,0.12116,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.10005,0.13017,0.41005]},{"body_a":"world","body_b":"door_panel","contact_count":216.0,"contact_point_centroid":[0.33607,0.08499,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":3.0,"phase_name":"retract_to_goal","phase_type":"retract","tcp_position_centroid":[0.09996,0.09787,0.39664]}],"total_contact_groups":9},"final_pose_error":0.02991,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.10109,0.15543,0.36701],"hinge_angle":0.55904,"initial_hinge_angle":-0.12965,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":-0.12965,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":91.18156,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":311.0,"n_steps_budget":750.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":19.05353,"phase_name":"approach_handle","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":452.0,"raw_peak_contact_force":91.18156,"subtask_id":"reach_handle","tcp_end":[0.10077,0.20634,0.43668],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.49338,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":64.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":16.30914,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":88.0,"raw_peak_contact_force":16.6533,"subtask_id":"reach_handle","tcp_end":[0.10042,0.20347,0.42846],"tcp_start":[0.10077,0.20634,0.43668],"tcp_to_object_dist_end":0.48483,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":13.77543,"phase_name":"push_door","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1789.0,"raw_peak_contact_force":32.22772,"subtask_id":"open_door","tcp_end":[0.0989,0.04569,0.41103],"tcp_start":[0.10042,0.20347,0.42846],"tcp_to_object_dist_end":0.42523,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":204.0,"n_steps_budget":660.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"retract_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":218.0,"raw_peak_contact_force":10.91851,"subtask_id":"reach_handle","tcp_end":[0.10109,0.15543,0.36701],"tcp_start":[0.0989,0.04569,0.41103],"tcp_to_object_dist_end":0.41119,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```