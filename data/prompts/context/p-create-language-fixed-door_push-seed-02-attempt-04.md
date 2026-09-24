## Search State

- **Seed**: 2
- **Iteration**: 5 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 4 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | pose_tolerance | force_exceeded | time_limit | time_limit | 9 | 0.9900 | 1.00 | ❌ rejected |
| 3 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | pose_tolerance | force_exceeded | time_limit | time_limit | 9 | 0.9900 | 1.00 | ❌ rejected |
| 2 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | pose_tolerance | force_exceeded | time_limit | time_limit | 9 | 0.9900 | 1.00 | ❌ rejected |
| 1 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | pose_tolerance | force_exceeded | time_limit | time_limit | 9 | 0.9900 | 1.00 | ✅ accepted |
| 0 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | 0.8900 | 1.00 | ✅ accepted |

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

## Current Skill (Q=0.990) — your mutation base

```yaml
skill: door_push
dsl_version: 2
phases:
- id: approach_1
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
    - 0.15
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
    approach_speed:
      type: scalar
      range:
      - 0.01
      - 0.2
      default: 0.05
      binds_to:
      - path: generator.speed
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
    contact_force:
      type: scalar
      range:
      - 1.0
      - 20.0
      default: 5.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    speed:
      type: scalar
      range:
      - 0.005
      - 0.05
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
- id: push_1
  type: push
  generator: linear_cartesian
  control: position_control
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
    orientation:
      mode: keep_current
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.15
      - 0.3
      default: 0.25
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_duration:
      type: scalar
      range:
      - 0.5
      - 3.0
      default: 2.0
      binds_to:
      - path: duration.max_time
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
- id: retract_1
  type: retract
  generator: linear_cartesian
  control: position_control
  termination: time_limit
  target:
    source: yaml
    anchor: site
    entity: door_handle
    offset:
    - 0.0
    - 0.0
    - 0.2
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    retract_duration:
      type: scalar
      range:
      - 0.5
      - 3.0
      default: 1.5
      binds_to:
      - path: duration.max_time
        mode: replace
    retract_height:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.2
      binds_to:
      - path: target.offset.z
        mode: replace

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=site, entity=door_handle, offset=[0.0, 0.0, 0.15], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **contact_1** (`contact`)
  - target: source=yaml, anchor=site, entity=door_handle, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - contact_force: status=consumed; consumers=termination.force_threshold (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **push_1** (`push`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_y, distance=0.25, mode=add_to_offset, sign=negative}
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_duration: status=consumed; consumers=duration.max_time (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
- **retract_1** (`retract`)
  - target: source=yaml, anchor=site, entity=door_handle, offset=[0.0, 0.0, 0.2], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - retract_duration: status=consumed; consumers=duration.max_time (replace)
    - retract_height: status=consumed; consumers=target.offset.z (replace)

## Design Metrics

- **Composite score**: 0.990
- **task_score** (E): 1.000
- **fitness_score**: 1.000  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.500
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.510

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 0.33 | 1.00 | 0.2133 |
| contact_1 | 1.00 | 1.00 | 0.0013 |
| push_1 | 1.00 | 1.00 | 0.1181 |
| retract_1 | 1.00 | 0.67 | 0.1194 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 0.33 / step_budget | (0.100, 0.399, 0.350)→(0.102, 0.242, 0.490) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 4.667 | 11.058 | 46.933 |
| contact_1 | contact | 1.00 / force_exceeded | (0.102, 0.242, 0.490)→(0.102, 0.242, 0.489) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 3.667 | 14.273 | 11.202 |
| push_1 | push | 1.00 / time_limit | (0.102, 0.242, 0.489)→(0.101, 0.124, 0.487) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 1.000 | 12.112 | 29.238 |
| retract_1 | retract | 1.00 / time_limit | (0.101, 0.124, 0.487)→(0.136, 0.041, 0.562) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 0.67 / 2.000 | 1.511 | 27.120 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- hinge_angle_ratio: 1.000
- arc_quality: 1.000

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 1.000
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.990
- **K-run variance**: 0.0000
- **Stagnated**: yes
  → Parameter optimiser converged to local optimum; structural change likely needed
- **Stop reason**: tolfun
- **Mean generations**: 2.0
- **Final σ (mean)**: 0.288


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.81081,"average_solve_count":111.0,"average_success_count":111.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.16417,"approach_1.approach_speed":0.1231,"contact_1.contact_force":10.8969,"contact_1.speed":0.02092,"push_1.push_distance":0.17563,"push_1.push_duration":2.12235,"push_1.push_speed":0.07163,"retract_1.retract_duration":1.14393,"retract_1.retract_height":0.24052},"optimized_scores":{"best_composite_score":0.99,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link6","contact_count":239.0,"contact_point_centroid":[0.10042,0.2005,0.5629],"force_p95":30.3313,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":54.58519,"mean_force":18.55086,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.09939,0.27652,0.45508]},{"body_a":"door_panel","body_b":"link7","contact_count":553.0,"contact_point_centroid":[0.18409,0.01894,0.5591],"force_p95":20.27612,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":27.55371,"mean_force":14.29802,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.11718,0.07552,0.53235]},{"body_a":"door_panel","body_b":"link7","contact_count":707.0,"contact_point_centroid":[0.16443,0.1107,0.50882],"force_p95":16.49614,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":24.54043,"mean_force":12.91373,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.09913,0.16804,0.4848]},{"body_a":"door_panel","body_b":"link6","contact_count":164.0,"contact_point_centroid":[0.10203,0.16022,0.59049],"force_p95":8.61925,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":17.19579,"mean_force":7.24566,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.09911,0.22738,0.48506]},{"body_a":"world","body_b":"door_panel","contact_count":1060.0,"contact_point_centroid":[0.29998,0.19963,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.09953,0.32164,0.41519]},{"body_a":"world","body_b":"door_panel","contact_count":28.0,"contact_point_centroid":[0.30135,0.1747,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.09939,0.23944,0.48766]},{"body_a":"world","body_b":"door_panel","contact_count":920.0,"contact_point_centroid":[0.30814,0.14597,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.09913,0.18068,0.48484]},{"body_a":"world","body_b":"door_panel","contact_count":748.0,"contact_point_centroid":[0.33194,0.09216,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.11728,0.07531,0.53259]}],"total_contact_groups":8},"final_pose_error":0.00835,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.1363,0.03202,0.5837],"hinge_angle":0.64789,"initial_hinge_angle":-0.08321,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":-0.08321,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":54.58519,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1299.0,"raw_peak_contact_force":54.58519,"tcp_end":[0.0994,0.23967,0.48791],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.55261,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":14.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":17.89232,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":28.0,"raw_peak_contact_force":0.0,"tcp_end":[0.09936,0.23895,0.48677],"tcp_start":[0.0994,0.23967,0.48791],"tcp_to_object_dist_end":0.55129,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":11.41217,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1791.0,"raw_peak_contact_force":24.54043,"tcp_end":[0.09912,0.11759,0.48489],"tcp_start":[0.09936,0.23895,0.48677],"tcp_to_object_dist_end":0.50869,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":842.0,"n_steps_budget":900.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1301.0,"raw_peak_contact_force":27.55371,"tcp_end":[0.1363,0.03202,0.5837],"tcp_start":[0.09912,0.11759,0.48489],"tcp_to_object_dist_end":0.60026,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.47414,"average_solve_count":116.0,"average_success_count":116.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.24121,"approach_1.approach_speed":0.09851,"contact_1.contact_force":11.06496,"contact_1.speed":0.02914,"push_1.push_distance":0.20455,"push_1.push_duration":1.83482,"push_1.push_speed":0.05098,"retract_1.retract_duration":1.16423,"retract_1.retract_height":0.21985},"optimized_scores":{"best_composite_score":0.99,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link6","contact_count":113.0,"contact_point_centroid":[0.10095,0.22638,0.59328],"force_p95":29.21317,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":51.73636,"mean_force":20.54265,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.10026,0.30722,0.484]},{"body_a":"door_panel","body_b":"link6","contact_count":627.0,"contact_point_centroid":[0.10091,0.18062,0.61066],"force_p95":10.9235,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":27.54212,"mean_force":7.37674,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.09989,0.25248,0.50343]},{"body_a":"door_panel","body_b":"link7","contact_count":497.0,"contact_point_centroid":[0.17113,0.08922,0.55624],"force_p95":16.42773,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":26.74518,"mean_force":14.01237,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.10548,0.14627,0.53193]},{"body_a":"door_panel","body_b":"link6","contact_count":2.0,"contact_point_centroid":[0.1002,0.21258,0.61528],"force_p95":20.62098,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":20.84002,"mean_force":18.6497,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.10033,0.29153,0.50645]},{"body_a":"door_panel","body_b":"link7","contact_count":237.0,"contact_point_centroid":[0.1654,0.144,0.52754],"force_p95":14.9787,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":17.29627,"mean_force":12.43871,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.1,0.20122,0.50353]},{"body_a":"world","body_b":"door_panel","contact_count":992.0,"contact_point_centroid":[0.29994,0.20772,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.10011,0.3418,0.43197]},{"body_a":"world","body_b":"door_panel","contact_count":24.0,"contact_point_centroid":[0.29978,0.19629,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.10033,0.29171,0.50686]},{"body_a":"world","body_b":"door_panel","contact_count":916.0,"contact_point_centroid":[0.30192,0.17387,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.09992,0.23821,0.50345]},{"body_a":"world","body_b":"door_panel","contact_count":636.0,"contact_point_centroid":[0.31335,0.12873,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.10502,0.14951,0.52949]}],"total_contact_groups":9},"final_pose_error":0.00806,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.11148,0.10377,0.56383],"hinge_angle":0.44339,"initial_hinge_angle":-0.14464,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":-0.14464,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":51.73636,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":18.39215,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1105.0,"raw_peak_contact_force":51.73636,"tcp_end":[0.10038,0.29193,0.50713],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.5937,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":16.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":16.45939,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":26.0,"raw_peak_contact_force":20.84002,"tcp_end":[0.10026,0.29107,0.50562],"tcp_start":[0.10038,0.29193,0.50713],"tcp_to_object_dist_end":0.59197,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":12.142,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1780.0,"raw_peak_contact_force":27.54212,"tcp_end":[0.10002,0.18713,0.50359],"tcp_start":[0.10026,0.29107,0.50562],"tcp_to_object_dist_end":0.54647,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":662.0,"n_steps_budget":720.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":4.53395,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1133.0,"raw_peak_contact_force":26.74518,"tcp_end":[0.11148,0.10377,0.56383],"tcp_start":[0.10002,0.18713,0.50359],"tcp_to_object_dist_end":0.58404,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.9619,"average_solve_count":105.0,"average_success_count":105.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.17453,"approach_1.approach_speed":0.14443,"contact_1.contact_force":4.64107,"contact_1.speed":0.01931,"push_1.push_distance":0.17832,"push_1.push_duration":2.62921,"push_1.push_speed":0.07782,"retract_1.retract_duration":2.54811,"retract_1.retract_height":0.19596},"optimized_scores":{"best_composite_score":0.99,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link7","contact_count":803.0,"contact_point_centroid":[0.17116,0.07471,0.49669],"force_p95":17.91952,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":35.63002,"mean_force":13.45676,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.1052,0.13179,0.47172]},{"body_a":"door_panel","body_b":"link7","contact_count":48.0,"contact_point_centroid":[0.17066,0.1448,0.4937],"force_p95":18.9871,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":34.47763,"mean_force":15.12626,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.10531,0.2022,0.46994]},{"body_a":"door_panel","body_b":"link7","contact_count":576.0,"contact_point_centroid":[0.19977,-0.03002,0.53128],"force_p95":16.04516,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":27.06085,"mean_force":13.94446,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.13252,0.02644,0.50447]},{"body_a":"door_panel","body_b":"link6","contact_count":11.0,"contact_point_centroid":[0.10454,0.1403,0.57193],"force_p95":15.85317,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":16.02355,"mean_force":7.25267,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.10521,0.2077,0.46662]},{"body_a":"door_panel","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.17081,0.13767,0.4978],"force_p95":11.48925,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":12.76584,"mean_force":4.25528,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.10547,0.19509,0.47405]},{"body_a":"world","body_b":"door_panel","contact_count":1068.0,"contact_point_centroid":[0.30383,0.1598,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.10265,0.29644,0.4112]},{"body_a":"world","body_b":"door_panel","contact_count":16.0,"contact_point_centroid":[0.30536,0.15293,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.10548,0.19508,0.47407]},{"body_a":"world","body_b":"door_panel","contact_count":960.0,"contact_point_centroid":[0.31711,0.12079,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.10521,0.13249,0.47174]},{"body_a":"world","body_b":"door_panel","contact_count":600.0,"contact_point_centroid":[0.34693,0.07169,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.13125,0.02825,0.50286]}],"total_contact_groups":9},"final_pose_error":0.00833,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.16089,-0.01391,0.53996],"hinge_angle":0.78287,"initial_hinge_angle":0.15466,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.15466,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":35.63002,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":14.78212,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1127.0,"raw_peak_contact_force":34.47763,"tcp_end":[0.10548,0.19526,0.47422],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.52358,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":10.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":8.46864,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":19.0,"raw_peak_contact_force":12.76584,"tcp_end":[0.10546,0.19473,0.47354],"tcp_start":[0.10548,0.19526,0.47422],"tcp_to_object_dist_end":0.52276,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":12.7826,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1763.0,"raw_peak_contact_force":35.63002,"tcp_end":[0.10517,0.0658,0.47173],"tcp_start":[0.10546,0.19473,0.47354],"tcp_to_object_dist_end":0.48777,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":752.0,"n_steps_budget":810.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1176.0,"raw_peak_contact_force":27.06085,"tcp_end":[0.16089,-0.01391,0.53996],"tcp_start":[0.10517,0.0658,0.47173],"tcp_to_object_dist_end":0.56359,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
```