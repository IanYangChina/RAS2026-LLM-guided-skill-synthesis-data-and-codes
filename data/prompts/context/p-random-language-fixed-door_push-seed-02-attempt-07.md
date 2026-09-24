## Search State

- **Seed**: 2
- **Iteration**: 8 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 7 | approach → align → contact → push | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | time_limit | pose_tolerance | force_exceeded | time_limit | 8 | 0.9636 | 0.92 | ❌ rejected |
| 6 | approach → align → contact → push | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 6 | 0.8492 | 0.96 | ❌ rejected |
| 5 | approach → align → contact → push | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | time_limit | time_limit | force_exceeded | time_limit | 6 | 1.6018 | 0.96 | ❌ rejected |
| 4 | approach → align → contact → push | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 6 | 0.8655 | 0.98 | ❌ rejected |
| 3 | approach → align → contact → push | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 6 | 0.8705 | 0.98 | ❌ rejected |

**Proposal policy**: task_score is near-perfect (0.92). Preserve useful working parts and make only evidence-backed refinements. A HOLD is acceptable if you genuinely cannot find a better structure.

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

## Current Skill (Q=0.964) — your mutation base

```yaml
skill: door_push
dsl_version: 2
skill_type: arm_gripper
phases:
- id: approach_1
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
    - 0.1
    orientation:
      mode: keep_current
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
- id: align_1
  type: align
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
    - 0.0
    orientation:
      mode: keep_current
  parameters:
    lateral_offset_x:
      type: scalar
      range:
      - -0.02
      - 0.02
      default: 0.0
      binds_to:
      - path: target.offset.x
        mode: replace
    lateral_offset_y:
      type: scalar
      range:
      - -0.02
      - 0.02
      default: 0.0
      binds_to:
      - path: target.offset.y
        mode: replace
- id: contact_1
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
    orientation:
      mode: keep_current
  parameters:
    contact_force_threshold:
      type: scalar
      range:
      - 5.0
      - 30.0
      default: 10.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
- id: push_1
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: site
    entity: door_handle
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.15
      axis: task_goal_direction
      mode: add_to_offset
      sign: positive
    orientation:
      mode: keep_current
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: force_guard
    when: during_phase
    predicate: force_below
    threshold: 30.0
    on_failure: abort

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=site, entity=door_handle, offset=[0.0, 0.0, 0.1]
  - orientation: mode=keep_current
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
- **align_1** (`align`)
  - target: source=yaml, anchor=site, entity=door_handle, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - lateral_offset_x: status=consumed; consumers=target.offset.x (replace)
    - lateral_offset_y: status=consumed; consumers=target.offset.y (replace)
- **contact_1** (`contact`)
  - target: source=yaml, anchor=site, entity=door_handle, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - contact_force_threshold: status=consumed; consumers=termination.force_threshold (replace)
- **push_1** (`push`)
  - target: source=yaml, anchor=site, entity=door_handle, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.15, mode=add_to_offset, sign=positive}
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=force_guard, when=during_phase, predicate=force_below, on_failure=abort, threshold=30.0

## Design Metrics

- **Composite score**: 0.964
- **task_score** (E): 0.924
- **fitness_score**: 0.924  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.500
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.460

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 0.33 | 0.1095 |
| align_1 | 1.00 | 1.00 | 0.1650 |
| contact_1 | 1.00 | 1.00 | 0.0260 |
| push_1 | 1.00 | 1.00 | 0.0781 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / time_limit | (0.100, 0.399, 0.350)→(0.100, 0.324, 0.429) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 0.33 / 1.667 | 6.115 | 12.369 |
| align_1 | align | 1.00 / step_budget | (0.100, 0.324, 0.429)→(0.113, 0.182, 0.365) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 1.000 | 4.534 | 37.929 |
| contact_1 | contact | 1.00 / force_exceeded | (0.113, 0.182, 0.365)→(0.112, 0.157, 0.366) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 2.333 | 33.962 | 30.751 |
| push_1 | push | 1.00 / time_limit | (0.112, 0.157, 0.366)→(0.137, 0.091, 0.395) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 2.333 | 1.798 | 25.588 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- hinge_angle_ratio: 1.000
- arc_quality: 1.000

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 1.000
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.936
- **K-run variance**: 0.0030
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Parameters at lower bound**: push_1.push_max_time
- **Parameters at upper bound**: approach_1.speed
- **Final σ (mean)**: 0.389


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.26357,"average_solve_count":129.0,"average_success_count":129.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":0.0176,"align_1.lateral_offset_y":0.0182,"approach_1.approach_max_time":3.25756,"approach_1.speed":0.1,"contact_1.contact_force_threshold":17.3794,"push_1.push_distance":0.05733,"push_1.push_max_time":2.00016,"push_1.push_speed":0.02792},"optimized_scores":{"best_composite_score":0.91508,"best_fitness_score":0.87508,"best_task_score":0.87508},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link6","contact_count":202.0,"contact_point_centroid":[0.10171,0.16966,0.52013],"force_p95":33.22347,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":42.3809,"mean_force":18.8361,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.10724,0.24623,0.41087]},{"body_a":"door_panel","body_b":"link6","contact_count":127.0,"contact_point_centroid":[0.10056,0.21964,0.56512],"force_p95":24.79475,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":37.10779,"mean_force":18.01766,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.09933,0.29868,0.45639]},{"body_a":"door_panel","body_b":"link7","contact_count":694.0,"contact_point_centroid":[0.1844,0.10636,0.39881],"force_p95":18.24359,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":23.89808,"mean_force":13.29448,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.11897,0.16344,0.37449]},{"body_a":"door_panel","body_b":"link7","contact_count":8.0,"contact_point_centroid":[0.17963,0.13956,0.3795],"force_p95":20.2256,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":23.68393,"mean_force":14.39645,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.11426,0.19666,0.35527]},{"body_a":"door_panel","body_b":"link6","contact_count":69.0,"contact_point_centroid":[0.1061,0.13052,0.46514],"force_p95":8.61263,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":17.40914,"mean_force":7.59201,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.1148,0.20318,0.3563]},{"body_a":"world","body_b":"door_panel","contact_count":1120.0,"contact_point_centroid":[0.29984,0.2052,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.09956,0.34793,0.41017]},{"body_a":"world","body_b":"door_panel","contact_count":388.0,"contact_point_centroid":[0.30147,0.17583,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.10678,0.24829,0.41391]},{"body_a":"world","body_b":"door_panel","contact_count":72.0,"contact_point_centroid":[0.30483,0.1552,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.11475,0.20255,0.3562]},{"body_a":"world","body_b":"door_panel","contact_count":1108.0,"contact_point_centroid":[0.31116,0.13422,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.11882,0.16439,0.37388]}],"total_contact_groups":9},"final_pose_error":0.00639,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.12373,0.13452,0.39414],"hinge_angle":0.37533,"initial_hinge_angle":-0.08321,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":-0.08321,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":42.3809,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":18.3437,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1247.0,"raw_peak_contact_force":37.10779,"tcp_end":[0.09926,0.28329,0.4663],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.55456,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":489.0,"n_steps_budget":900.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":590.0,"raw_peak_contact_force":42.3809,"tcp_end":[0.11547,0.21012,0.3579],"tcp_start":[0.09926,0.28329,0.4663],"tcp_to_object_dist_end":0.43079,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":92.0,"n_steps_budget":630.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":23.68393,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":149.0,"raw_peak_contact_force":23.68393,"tcp_end":[0.1142,0.19608,0.35521],"tcp_start":[0.11547,0.21012,0.3579],"tcp_to_object_dist_end":0.4215,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1802.0,"raw_peak_contact_force":23.89808,"tcp_end":[0.12373,0.13452,0.39414],"tcp_start":[0.1142,0.19608,0.35521],"tcp_to_object_dist_end":0.43446,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.336,"average_solve_count":125.0,"average_success_count":125.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":0.01443,"align_1.lateral_offset_y":-0.01262,"approach_1.approach_max_time":6.66471,"approach_1.speed":0.03561,"contact_1.contact_force_threshold":24.37359,"push_1.push_distance":0.05173,"push_1.push_max_time":6.50953,"push_1.push_speed":0.04793},"optimized_scores":{"best_composite_score":1.04,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link6","contact_count":339.0,"contact_point_centroid":[0.10121,0.18873,0.4825],"force_p95":27.86895,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":36.33537,"mean_force":15.09988,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.10793,0.26988,0.36992]},{"body_a":"door_panel","body_b":"link7","contact_count":252.0,"contact_point_centroid":[0.17591,0.11968,0.37456],"force_p95":19.98405,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":31.37186,"mean_force":13.99359,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.11051,0.1768,0.35028]},{"body_a":"door_panel","body_b":"link7","contact_count":638.0,"contact_point_centroid":[0.18995,0.05978,0.40063],"force_p95":23.67516,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":25.75436,"mean_force":13.66124,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.1236,0.11641,0.37453]},{"body_a":"door_panel","body_b":"link6","contact_count":77.0,"contact_point_centroid":[0.10529,0.13539,0.4592],"force_p95":8.27326,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":17.91655,"mean_force":7.498,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.11237,0.20716,0.35092]},{"body_a":"world","body_b":"door_panel","contact_count":976.0,"contact_point_centroid":[0.29999,0.20977,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.09969,0.38146,0.37721]},{"body_a":"world","body_b":"door_panel","contact_count":588.0,"contact_point_centroid":[0.30065,0.19055,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.10628,0.28844,0.3761]},{"body_a":"world","body_b":"door_panel","contact_count":368.0,"contact_point_centroid":[0.30709,0.14732,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.11113,0.18677,0.35051]},{"body_a":"world","body_b":"door_panel","contact_count":840.0,"contact_point_centroid":[0.32219,0.10878,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.12353,0.11661,0.37446]}],"total_contact_groups":8},"final_pose_error":0.00505,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.13601,0.08485,0.39054],"hinge_angle":0.52384,"initial_hinge_angle":-0.14464,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":-0.14464,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":41.00383,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":976.0,"raw_peak_contact_force":0.0,"tcp_end":[0.09984,0.36457,0.40284],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.55242,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":606.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":927.0,"raw_peak_contact_force":36.33537,"tcp_end":[0.11304,0.2154,0.35212],"tcp_start":[0.09984,0.36457,0.40284],"tcp_to_object_dist_end":0.42797,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":398.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":41.00383,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":697.0,"raw_peak_contact_force":31.37186,"tcp_end":[0.10919,0.1533,0.35535],"tcp_start":[0.11304,0.2154,0.35212],"tcp_to_object_dist_end":0.40211,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":881.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":1.98911,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1478.0,"raw_peak_contact_force":25.75436,"tcp_end":[0.13601,0.08485,0.39054],"tcp_start":[0.10919,0.1533,0.35535],"tcp_to_object_dist_end":0.42216,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.81818,"average_solve_count":121.0,"average_success_count":121.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":0.00359,"align_1.lateral_offset_y":-0.01593,"approach_1.approach_max_time":6.48783,"approach_1.speed":0.06057,"contact_1.contact_force_threshold":18.73384,"push_1.push_distance":0.05354,"push_1.push_max_time":8.0167,"push_1.push_speed":0.04947},"optimized_scores":{"best_composite_score":0.93564,"best_fitness_score":0.89564,"best_task_score":0.89564},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.17779,0.06484,0.41374],"force_p95":35.33817,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":37.19807,"mean_force":18.59904,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.1114,0.12171,0.38556]},{"body_a":"door_panel","body_b":"link7","contact_count":326.0,"contact_point_centroid":[0.17408,0.10254,0.39651],"force_p95":23.08537,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":35.0698,"mean_force":15.24027,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.10873,0.1598,0.37216]},{"body_a":"door_panel","body_b":"link6","contact_count":23.0,"contact_point_centroid":[0.10458,0.14005,0.48689],"force_p95":20.01015,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":27.1458,"mean_force":12.33188,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.10629,0.20846,0.38049]},{"body_a":"door_panel","body_b":"link7","contact_count":731.0,"contact_point_centroid":[0.19785,0.02983,0.42406],"force_p95":18.90591,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":27.11226,"mean_force":13.36835,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.13168,0.08668,0.3955]},{"body_a":"world","body_b":"door_panel","contact_count":1056.0,"contact_point_centroid":[0.30379,0.16,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.10059,0.36279,0.38379]},{"body_a":"world","body_b":"door_panel","contact_count":868.0,"contact_point_centroid":[0.30802,0.146,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.10646,0.20954,0.38466]},{"body_a":"world","body_b":"door_panel","contact_count":764.0,"contact_point_centroid":[0.33106,0.09322,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.13183,0.08642,0.39557]}],"total_contact_groups":7},"final_pose_error":0.00499,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.15092,0.05289,0.39948],"hinge_angle":0.62397,"initial_hinge_angle":0.15466,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.15466,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":37.19807,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1056.0,"raw_peak_contact_force":0.0,"tcp_end":[0.1017,0.32414,0.41778],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.53847,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":921.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":13.60133,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":1217.0,"raw_peak_contact_force":35.0698,"tcp_end":[0.1114,0.12174,0.38553],"tcp_start":[0.1017,0.32414,0.41778],"tcp_to_object_dist_end":0.41936,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":10.0,"n_steps_budget":660.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":37.19807,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2.0,"raw_peak_contact_force":37.19807,"tcp_end":[0.11179,0.12076,0.38646],"tcp_start":[0.1114,0.12174,0.38553],"tcp_to_object_dist_end":0.42004,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":934.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":3.4034,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1495.0,"raw_peak_contact_force":27.11226,"tcp_end":[0.15092,0.05289,0.39948],"tcp_start":[0.11179,0.12076,0.38646],"tcp_to_object_dist_end":0.4303,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
```