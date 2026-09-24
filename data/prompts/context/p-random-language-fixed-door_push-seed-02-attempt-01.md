## Search State

- **Seed**: 2
- **Iteration**: 2 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 1 | approach → align → contact → push | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 6 | 0.8728 | 0.98 | ✅ accepted |
| 0 | approach → align → align → pull → descend → release → grasp → push | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | — | — | impedance_motion | position_control | position_control | position_control | impedance_control | position_control | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | contact_detected | time_limit | grasp_success | pose_tolerance | 7 | -0.0589 | 0.47 | ✅ accepted |

**Proposal policy**: task_score is near-perfect (0.98). Preserve useful working parts and make only evidence-backed refinements. A HOLD is acceptable if you genuinely cannot find a better structure.

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

## Current Skill (Q=0.873) — your mutation base

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

- **Composite score**: 0.873
- **task_score** (E): 0.983
- **fitness_score**: 0.983  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.250
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.360

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 0.67 | 0.67 | 0.1920 |
| align_1 | 1.00 | 1.00 | 0.1205 |
| contact_1 | 1.00 | 1.00 | 0.0034 |
| push_1 | 1.00 | 0.33 | 0.1110 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 0.67 / step_budget | (0.100, 0.399, 0.350)→(0.102, 0.232, 0.443) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 0.67 / 1.667 | 4.603 | 26.675 |
| align_1 | align | 1.00 / step_budget | (0.102, 0.232, 0.443)→(0.113, 0.140, 0.369) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 3.667 | 14.096 | 33.381 |
| contact_1 | contact | 1.00 / force_exceeded | (0.113, 0.140, 0.369)→(0.114, 0.137, 0.370) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 5.000 | 28.693 | 26.573 |
| push_1 | push | 1.00 / step_budget | (0.114, 0.137, 0.370)→(0.160, 0.099, 0.451) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 0.33 / 1.667 | 2.463 | 25.332 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- hinge_angle_ratio: 1.000
- arc_quality: 1.000

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 1.000
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.890
- **K-run variance**: 0.0006
- **Stagnated**: no
- **Stop reason**: tolfun
- **Mean generations**: 7.3
- **Final σ (mean)**: 0.346


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.55245,"average_solve_count":143.0,"average_success_count":143.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":0.00167,"align_1.lateral_offset_y":0.00166,"approach_1.speed":0.07579,"contact_1.contact_force_threshold":10.69659,"push_1.push_distance":0.15547,"push_1.push_speed":0.04967},"optimized_scores":{"best_composite_score":0.89,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link6","contact_count":333.0,"contact_point_centroid":[0.10071,0.19264,0.54179],"force_p95":25.66134,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":39.65578,"mean_force":16.14598,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.09932,0.26713,0.43441]},{"body_a":"door_panel","body_b":"link7","contact_count":276.0,"contact_point_centroid":[0.16837,0.1173,0.41655],"force_p95":22.95173,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":29.97572,"mean_force":15.68557,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.10308,0.17467,0.39249]},{"body_a":"door_panel","body_b":"link6","contact_count":23.0,"contact_point_centroid":[0.10292,0.15192,0.54576],"force_p95":19.95318,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":26.60795,"mean_force":16.55255,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.09954,0.21803,0.44101]},{"body_a":"door_panel","body_b":"link7","contact_count":320.0,"contact_point_centroid":[0.20083,0.07625,0.44649],"force_p95":24.75704,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":26.19103,"mean_force":15.96246,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.13487,0.13327,0.42114]},{"body_a":"door_panel","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.17149,0.08866,0.3898],"force_p95":21.30044,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":22.00017,"mean_force":12.33435,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.10622,0.14604,0.3657]},{"body_a":"world","body_b":"door_panel","contact_count":1064.0,"contact_point_centroid":[0.30012,0.19831,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.09951,0.32092,0.4053]},{"body_a":"world","body_b":"door_panel","contact_count":544.0,"contact_point_centroid":[0.30747,0.1467,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.10236,0.18296,0.4015]},{"body_a":"world","body_b":"door_panel","contact_count":4.0,"contact_point_centroid":[0.31377,0.12639,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.1062,0.14615,0.36565]},{"body_a":"world","body_b":"door_panel","contact_count":728.0,"contact_point_centroid":[0.31949,0.11365,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.13585,0.13288,0.42307]}],"total_contact_groups":9},"final_pose_error":0.01,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.16207,0.12234,0.47487],"hinge_angle":0.46014,"initial_hinge_angle":-0.08321,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":-0.08321,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":39.65578,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":981.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1397.0,"raw_peak_contact_force":39.65578,"tcp_end":[0.09935,0.22236,0.44614],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.50829,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":485.0,"n_steps_budget":810.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":11.97116,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":843.0,"raw_peak_contact_force":29.97572,"tcp_end":[0.1062,0.14617,0.36565],"tcp_start":[0.09935,0.22236,0.44614],"tcp_to_object_dist_end":0.40786,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":5.0,"n_steps_budget":630.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":18.47737,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":7.0,"raw_peak_contact_force":22.00017,"tcp_end":[0.10631,0.14567,0.3659],"tcp_start":[0.1062,0.14617,0.36565],"tcp_to_object_dist_end":0.40792,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":778.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1048.0,"raw_peak_contact_force":26.19103,"tcp_end":[0.16207,0.12234,0.47487],"tcp_start":[0.10631,0.14567,0.3659],"tcp_to_object_dist_end":0.51647,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.21164,"average_solve_count":189.0,"average_success_count":189.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":0.00304,"align_1.lateral_offset_y":-0.00426,"approach_1.speed":0.05927,"contact_1.contact_force_threshold":19.15794,"push_1.push_distance":0.16173,"push_1.push_speed":0.03261},"optimized_scores":{"best_composite_score":0.89,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link6","contact_count":290.0,"contact_point_centroid":[0.10051,0.20666,0.54162],"force_p95":25.30648,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":40.36919,"mean_force":17.39812,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.10038,0.28479,0.43304]},{"body_a":"door_panel","body_b":"link6","contact_count":90.0,"contact_point_centroid":[0.10222,0.15902,0.53257],"force_p95":34.39987,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":36.88792,"mean_force":17.23645,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.10129,0.22818,0.42644]},{"body_a":"door_panel","body_b":"link7","contact_count":45.0,"contact_point_centroid":[0.17077,0.09682,0.38342],"force_p95":16.18845,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":32.94979,"mean_force":12.90325,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.10546,0.15406,0.35927]},{"body_a":"door_panel","body_b":"link7","contact_count":192.0,"contact_point_centroid":[0.16873,0.12445,0.40502],"force_p95":29.02437,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":30.13722,"mean_force":16.13967,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.10343,0.18177,0.38093]},{"body_a":"door_panel","body_b":"link7","contact_count":327.0,"contact_point_centroid":[0.20161,0.08213,0.4485],"force_p95":21.14848,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":22.64767,"mean_force":15.79063,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.13593,0.1392,0.42375]},{"body_a":"world","body_b":"door_panel","contact_count":872.0,"contact_point_centroid":[0.30003,0.20362,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.10014,0.33099,0.40461]},{"body_a":"world","body_b":"door_panel","contact_count":480.0,"contact_point_centroid":[0.3049,0.15714,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.1024,0.20388,0.40259]},{"body_a":"world","body_b":"door_panel","contact_count":44.0,"contact_point_centroid":[0.31195,0.13119,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.10525,0.15503,0.35909]},{"body_a":"world","body_b":"door_panel","contact_count":704.0,"contact_point_centroid":[0.31776,0.11728,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.13522,0.13945,0.42218]}],"total_contact_groups":9},"final_pose_error":0.00988,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.16187,0.13011,0.48024],"hinge_angle":0.43636,"initial_hinge_angle":-0.14464,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":-0.14464,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":40.36919,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":960.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":13.80799,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1162.0,"raw_peak_contact_force":40.36919,"tcp_end":[0.10078,0.24669,0.44543],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.51906,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":493.0,"n_steps_budget":870.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":7.22997,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":762.0,"raw_peak_contact_force":36.88792,"tcp_end":[0.1048,0.1574,0.359],"tcp_start":[0.10078,0.24669,0.44543],"tcp_to_object_dist_end":0.40576,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":53.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":29.12962,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":89.0,"raw_peak_contact_force":32.94979,"tcp_end":[0.10628,0.15059,0.36029],"tcp_start":[0.1048,0.1574,0.359],"tcp_to_object_dist_end":0.4047,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":851.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1031.0,"raw_peak_contact_force":22.64767,"tcp_end":[0.16187,0.13011,0.48024],"tcp_start":[0.10628,0.15059,0.36029],"tcp_to_object_dist_end":0.52322,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.20588,"average_solve_count":170.0,"average_success_count":170.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":0.01908,"align_1.lateral_offset_y":-0.0193,"approach_1.speed":0.02308,"contact_1.contact_force_threshold":25.38502,"push_1.push_distance":0.05874,"push_1.push_speed":0.03256},"optimized_scores":{"best_composite_score":0.83829,"best_fitness_score":0.94829,"best_task_score":0.94829},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link7","contact_count":356.0,"contact_point_centroid":[0.1833,0.0956,0.4136],"force_p95":26.75972,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":33.28008,"mean_force":16.18746,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.11781,0.15289,0.38887]},{"body_a":"door_panel","body_b":"link6","contact_count":22.0,"contact_point_centroid":[0.10483,0.13823,0.5302],"force_p95":23.00175,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":32.65902,"mean_force":15.20202,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.1076,0.20716,0.4238]},{"body_a":"door_panel","body_b":"link7","contact_count":317.0,"contact_point_centroid":[0.20947,0.02224,0.41991],"force_p95":23.1342,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":27.15794,"mean_force":15.32607,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.14333,0.07927,0.39157]},{"body_a":"door_panel","body_b":"link7","contact_count":8.0,"contact_point_centroid":[0.19457,0.05749,0.4104],"force_p95":24.01192,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":24.76861,"mean_force":14.30378,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.12838,0.11456,0.38218]},{"body_a":"world","body_b":"door_panel","contact_count":1056.0,"contact_point_centroid":[0.30379,0.16,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.10201,0.31764,0.39875]},{"body_a":"world","body_b":"door_panel","contact_count":548.0,"contact_point_centroid":[0.3123,0.13319,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.11606,0.16249,0.39525]},{"body_a":"world","body_b":"door_panel","contact_count":12.0,"contact_point_centroid":[0.32292,0.10651,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.12831,0.11482,0.38197]},{"body_a":"world","body_b":"door_panel","contact_count":288.0,"contact_point_centroid":[0.3355,0.08646,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.1441,0.07745,0.39193]}],"total_contact_groups":8},"final_pose_error":0.00985,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.15717,0.04599,0.39697],"hinge_angle":0.65156,"initial_hinge_angle":0.15466,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.15466,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":38.47315,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1056.0,"raw_peak_contact_force":0.0,"tcp_end":[0.10466,0.22576,0.43806],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.5038,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":619.0,"n_steps_budget":960.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":23.08707,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":926.0,"raw_peak_contact_force":33.28008,"tcp_end":[0.12814,0.11537,0.38155],"tcp_start":[0.10466,0.22576,0.43806],"tcp_to_object_dist_end":0.4187,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":17.0,"n_steps_budget":690.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":38.47315,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":20.0,"raw_peak_contact_force":24.76861,"tcp_end":[0.12868,0.11353,0.38301],"tcp_start":[0.12814,0.11537,0.38155],"tcp_to_object_dist_end":0.4197,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":379.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":7.38778,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":605.0,"raw_peak_contact_force":27.15794,"tcp_end":[0.15717,0.04599,0.39697],"tcp_start":[0.12868,0.11353,0.38301],"tcp_to_object_dist_end":0.42942,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```