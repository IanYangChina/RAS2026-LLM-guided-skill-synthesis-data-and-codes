## Search State

- **Seed**: 1
- **Iteration**: 14 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 13 | contact → push → retract | impedance_motion | linear_cartesian | arc_cartesian | force_threshold_switch | position_control | position_control | force_exceeded | pose_tolerance | pose_tolerance | 4 | 1.1033 | 1.00 | ❌ rejected |
| 12 | contact → push → retract | impedance_motion | linear_cartesian | arc_cartesian | force_threshold_switch | position_control | position_control | force_exceeded | pose_tolerance | pose_tolerance | 4 | 0.9922 | 1.00 | ❌ rejected |
| 11 | contact → push → retract | impedance_motion | linear_cartesian | arc_cartesian | force_threshold_switch | position_control | position_control | force_exceeded | pose_tolerance | pose_tolerance | 4 | 0.8811 | 1.00 | ❌ rejected |
| 10 | contact → push → retract | impedance_motion | linear_cartesian | arc_cartesian | force_threshold_switch | position_control | position_control | force_exceeded | pose_tolerance | pose_tolerance | 4 | 1.1033 | 1.00 | ✅ accepted |
| 9 | contact → push → retract | impedance_motion | linear_cartesian | arc_cartesian | force_threshold_switch | position_control | position_control | force_exceeded | time_limit | pose_tolerance | 6 | 0.8367 | 1.00 | ✅ accepted |

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
- Frozen realised-scene SHA-256: `02510fe55caa23c78bf987721ef5c6c19c6d55c0df3e224216ba39f61ecd9c91`
- Frozen initial hinge angle: 0.004 rad
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
  frozen_initial_hinge_angle_rad: 0.0041
  frozen_fixtures: {'door_panel': [0.5, 0.2, 0.0]}
  door_hinge_axis: [0, 0, 1]
  goal_tolerance_m: 0.05
  force_limit_n: 30
  force_scale_n: 5
  target_hinge_angle_rad: 0.524
  realized_scene_sha256: 02510fe55caa23c78bf987721ef5c6c19c6d55c0df3e224216ba39f61ecd9c91

## Current Skill (Q=1.103) — your mutation base

```yaml
skill: door_push
dsl_version: 2
phases:
- id: approach_contact
  type: contact
  generator: impedance_motion
  control: force_threshold_switch
  termination: force_exceeded
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - -0.01
    - 0.0
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    contact_force_threshold:
      type: scalar
      range:
      - 5.0
      - 30.0
      default: 15.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat
- id: push_1
  type: push
  generator: linear_cartesian
  control: position_control
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
      mode: add_to_offset
      sign: positive
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.1
      - 0.3
      default: 0.2
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat
- id: retract_1
  type: retract
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.1
    - -0.1
    - 0.15
    tolerance: 0.05
    orientation:
      mode: keep_current
  parameters:
    retract_arc_height:
      type: scalar
      range:
      - 0.1
      - 0.5
      default: 0.3
      binds_to:
      - path: generator.arc_height
        mode: replace
    retract_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_contact** (`contact`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, -0.01, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - contact_force_threshold: status=consumed; consumers=termination.force_threshold (replace)
  - retries: max_attempts=0, strategy=repeat
- **push_1** (`push`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_y, distance=0.2, mode=add_to_offset, sign=positive}, tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
  - retries: max_attempts=0, strategy=repeat
- **retract_1** (`retract`)
  - target: source=yaml, anchor=task_goal, offset=[0.1, -0.1, 0.15], tolerance=0.05
  - orientation: mode=keep_current
  - parameter_bindings:
    - retract_arc_height: status=consumed; consumers=generator.arc_height (replace)
    - retract_speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=0, strategy=repeat

## Design Metrics

- **Composite score**: 1.103
- **task_score** (E): 1.000
- **fitness_score**: 1.000  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.333
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.230

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_contact | 1.00 | 1.00 | 0.1151 |
| push_1 | 1.00 | 0.33 | 0.1691 |
| retract_1 | 1.00 | 1.00 | 0.3980 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_contact | contact | 1.00 / force_exceeded | (0.100, 0.399, 0.350)→(0.100, 0.284, 0.348) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 2.333 | 26.701 | 14.195 |
| push_1 | push | 1.00 / step_budget | (0.100, 0.284, 0.348)→(0.099, 0.453, 0.345) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 0.33 / 1.333 | 0.000 | 3.003 |
| retract_1 | retract | 1.00 / step_budget | (0.099, 0.453, 0.345)→(0.191, 0.115, 0.533) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 2.333 | 15.313 | 527.321 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- hinge_angle_ratio: 1.000
- arc_quality: 1.000

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 1.000
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 1.103
- **K-run variance**: 0.0000
- **Stagnated**: yes
  → Parameter optimiser converged to local optimum; structural change likely needed
- **Stop reason**: tolfun
- **Mean generations**: 5.0
- **Final σ (mean)**: 0.424


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `083132501f1ba139cf05fa7994a1ee954b157d46058e9396ba8b78c93b367725`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"hinge_delta_deg":10.0,"object_xy_delta":[0.0,0.0]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `a0caaf91521131af8da2ca1e0ce4fb631dc10b8d496fc3757eb1acd97f543da3`; realized-scene SHA-256: `02510fe55caa23c78bf987721ef5c6c19c6d55c0df3e224216ba39f61ecd9c91`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"fixture","value":[0.5,0.2,0.0]}],"axes":[{"name":"door_hinge_axis","value":[0.0,0.0,1.0]}],"door":{"hinge_axis":[0.0,0.0,1.0],"initial_hinge_angle":0.00413,"panel":{"name":"door_panel","orientation":[1.0,0.0,0.0,0.00206],"position":[0.5,0.2,0.0]},"target_hinge_angle":0.524},"fixture_states":[],"fixtures":[{"name":"door_panel","orientation":[1.0,0.0,0.0,0.00206],"position":[0.5,0.2,0.0]}],"limits":[{"name":"goal_tolerance_m","value":0.05},{"name":"force_limit_n","value":30.0},{"name":"force_scale_n","value":5.0},{"name":"target_hinge_angle_rad","value":0.524}],"object_starts":[],"obstacles":[],"targets":[],"task_name":"door_push"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.95312,"average_solve_count":192.0,"average_success_count":192.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_contact.contact_force_threshold":18.32763,"push_1.push_distance":0.19737,"retract_1.retract_arc_height":0.22635,"retract_1.retract_speed":0.05511},"optimized_scores":{"best_composite_score":1.10333,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_frame","body_b":"link6","contact_count":368.0,"contact_point_centroid":[0.11132,0.22492,0.75013],"force_p95":344.28184,"geom_a":"door_frame_top_beam","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":567.56601,"mean_force":300.81331,"phase_index":2.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.14251,0.25195,0.57295]},{"body_a":"door_panel","body_b":"link7","contact_count":89.0,"contact_point_centroid":[0.23544,0.11604,0.58756],"force_p95":57.30365,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":60.12895,"mean_force":41.89301,"phase_index":2.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.16808,0.16895,0.55996]},{"body_a":"door_panel","body_b":"link6","contact_count":113.0,"contact_point_centroid":[0.10214,0.16499,0.69803],"force_p95":31.72133,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":36.16873,"mean_force":14.04955,"phase_index":2.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.144,0.23475,0.56995]},{"body_a":"door_panel","body_b":"link6","contact_count":87.0,"contact_point_centroid":[0.10016,0.19178,0.45579],"force_p95":16.48691,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":21.22237,"mean_force":8.07737,"phase_index":0.0,"phase_name":"approach_contact","phase_type":"contact","tcp_position_centroid":[0.09962,0.26798,0.34796]},{"body_a":"world","body_b":"door_panel","contact_count":900.0,"contact_point_centroid":[0.30006,0.18889,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_contact","phase_type":"contact","tcp_position_centroid":[0.09959,0.33225,0.34777]},{"body_a":"door_panel","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.1003,0.18484,0.45543],"force_p95":0.0,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.09959,0.25969,0.34802]},{"body_a":"world","body_b":"door_panel","contact_count":516.0,"contact_point_centroid":[0.30057,0.18191,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.09926,0.34275,0.34605]},{"body_a":"world","body_b":"door_panel","contact_count":924.0,"contact_point_centroid":[0.30269,0.17302,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.13333,0.30119,0.53374]}],"total_contact_groups":8},"final_pose_error":0.04928,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.19047,0.11384,0.53453],"hinge_angle":0.529,"initial_hinge_angle":0.00413,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.00413,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":567.56601,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":844.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":20.55654,"phase_name":"approach_contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":987.0,"raw_peak_contact_force":21.22237,"tcp_end":[0.09959,0.25969,0.34802],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.44551,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":448.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":517.0,"raw_peak_contact_force":0.0,"tcp_end":[0.09887,0.43732,0.34511],"tcp_start":[0.09959,0.25969,0.34802],"tcp_to_object_dist_end":0.5658,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":830.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":45.9389,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1494.0,"raw_peak_contact_force":567.56601,"tcp_end":[0.19047,0.11384,0.53453],"tcp_start":[0.09887,0.43732,0.34511],"tcp_to_object_dist_end":0.57876,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `5bc49f053da41ee2995fb91d1adc375d35d8209a2f6f497df40da3fd7dd59d69`; realized-scene SHA-256: `6dd40fac67fc7b4cb952edf7b79ea329c0b46aa4cb26369fc447c16f02a37d6d`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"fixture","value":[0.5,0.2,0.0]}],"axes":[{"name":"door_hinge_axis","value":[0.0,0.0,1.0]}],"door":{"hinge_axis":[0.0,0.0,1.0],"initial_hinge_angle":-0.08321,"panel":{"name":"door_panel","orientation":[0.99913,0.0,0.0,-0.04159],"position":[0.5,0.2,0.0]},"target_hinge_angle":0.524},"fixture_states":[],"fixtures":[{"name":"door_panel","orientation":[0.99913,0.0,0.0,-0.04159],"position":[0.5,0.2,0.0]}],"limits":[{"name":"goal_tolerance_m","value":0.05},{"name":"force_limit_n","value":30.0},{"name":"force_scale_n","value":5.0},{"name":"target_hinge_angle_rad","value":0.524}],"object_starts":[],"obstacles":[],"targets":[],"task_name":"door_push"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.95361,"average_solve_count":194.0,"average_success_count":194.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_contact.contact_force_threshold":16.76244,"push_1.push_distance":0.21586,"retract_1.retract_arc_height":0.28504,"retract_1.retract_speed":0.04454},"optimized_scores":{"best_composite_score":1.10333,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_frame","body_b":"link6","contact_count":79.0,"contact_point_centroid":[0.1323,0.22496,0.75014],"force_p95":371.8467,"geom_a":"door_frame_top_beam","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":451.83266,"mean_force":319.38579,"phase_index":2.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.15572,0.24701,0.57089]},{"body_a":"door_panel","body_b":"link7","contact_count":74.0,"contact_point_centroid":[0.24465,0.11011,0.58037],"force_p95":57.01565,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":59.22831,"mean_force":44.96611,"phase_index":2.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.17826,0.16575,0.55451]},{"body_a":"door_panel","body_b":"link6","contact_count":68.0,"contact_point_centroid":[0.11481,0.16449,0.69377],"force_p95":33.91474,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":36.54719,"mean_force":20.66124,"phase_index":2.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.15639,0.24228,0.56991]},{"body_a":"door_panel","body_b":"link6","contact_count":242.0,"contact_point_centroid":[0.10043,0.21303,0.45687],"force_p95":10.30026,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":21.36125,"mean_force":7.56516,"phase_index":0.0,"phase_name":"approach_contact","phase_type":"contact","tcp_position_centroid":[0.09954,0.29317,0.34787]},{"body_a":"world","body_b":"door_panel","contact_count":856.0,"contact_point_centroid":[0.29986,0.20314,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_contact","phase_type":"contact","tcp_position_centroid":[0.09955,0.33655,0.34776]},{"body_a":"door_panel","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.10007,0.19312,0.45594],"force_p95":0.0,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.09957,0.26969,0.34799]},{"body_a":"world","body_b":"door_panel","contact_count":500.0,"contact_point_centroid":[0.30024,0.186,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.09913,0.3678,0.34577]},{"body_a":"world","body_b":"door_panel","contact_count":568.0,"contact_point_centroid":[0.30371,0.17137,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.13729,0.32534,0.51535]}],"total_contact_groups":8},"final_pose_error":0.04936,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.19191,0.11701,0.53164],"hinge_angle":0.52293,"initial_hinge_angle":-0.08321,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":-0.08321,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":451.83266,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":784.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":21.36125,"phase_name":"approach_contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1098.0,"raw_peak_contact_force":21.36125,"tcp_end":[0.09957,0.26969,0.34799],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.45138,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":495.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":501.0,"raw_peak_contact_force":0.0,"tcp_end":[0.09876,0.46599,0.345],"tcp_start":[0.09957,0.26969,0.34799],"tcp_to_object_dist_end":0.58816,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":542.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":789.0,"raw_peak_contact_force":451.83266,"tcp_end":[0.19191,0.11701,0.53164],"tcp_start":[0.09876,0.46599,0.345],"tcp_to_object_dist_end":0.5772,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `36664242b94803fac749fdbd125449f5f6a464dcd4b70b6714af07046570273f`; realized-scene SHA-256: `a535d88ef07b74838c5ab0400d8932f8a62343284dc305f72bf16a3002d4504f`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"fixture","value":[0.5,0.2,0.0]}],"axes":[{"name":"door_hinge_axis","value":[0.0,0.0,1.0]}],"door":{"hinge_axis":[0.0,0.0,1.0],"initial_hinge_angle":-0.14464,"panel":{"name":"door_panel","orientation":[0.99739,0.0,0.0,-0.07225],"position":[0.5,0.2,0.0]},"target_hinge_angle":0.524},"fixture_states":[],"fixtures":[{"name":"door_panel","orientation":[0.99739,0.0,0.0,-0.07225],"position":[0.5,0.2,0.0]}],"limits":[{"name":"goal_tolerance_m","value":0.05},{"name":"force_limit_n","value":30.0},{"name":"force_scale_n","value":5.0},{"name":"target_hinge_angle_rad","value":0.524}],"object_starts":[],"obstacles":[],"targets":[],"task_name":"door_push"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.94706,"average_solve_count":170.0,"average_success_count":170.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_contact.contact_force_threshold":18.13037,"push_1.push_distance":0.1529,"retract_1.retract_arc_height":0.24972,"retract_1.retract_speed":0.05466},"optimized_scores":{"best_composite_score":1.10333,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_frame","body_b":"link6","contact_count":353.0,"contact_point_centroid":[0.11147,0.22495,0.75009],"force_p95":345.4677,"geom_a":"door_frame_top_beam","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":562.56332,"mean_force":298.28247,"phase_index":2.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.14411,0.25138,0.57272]},{"body_a":"door_panel","body_b":"link7","contact_count":82.0,"contact_point_centroid":[0.23893,0.1139,0.58585],"force_p95":59.08669,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":61.41908,"mean_force":43.91697,"phase_index":2.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.17164,0.16719,0.55839]},{"body_a":"door_panel","body_b":"link6","contact_count":264.0,"contact_point_centroid":[0.10203,0.18508,0.69828],"force_p95":29.92778,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":32.68353,"mean_force":13.74548,"phase_index":2.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.14298,0.25989,0.57398]},{"body_a":"door_panel","body_b":"link6","contact_count":3.0,"contact_point_centroid":[0.10197,0.23932,0.45905],"force_p95":8.1092,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":9.01022,"mean_force":3.00341,"phase_index":1.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.09956,0.32334,0.34765]},{"body_a":"world","body_b":"door_panel","contact_count":416.0,"contact_point_centroid":[0.30001,0.21014,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_contact","phase_type":"contact","tcp_position_centroid":[0.09956,0.36046,0.34772]},{"body_a":"world","body_b":"door_panel","contact_count":364.0,"contact_point_centroid":[0.29998,0.20956,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.09905,0.39269,0.34538]},{"body_a":"world","body_b":"door_panel","contact_count":812.0,"contact_point_centroid":[0.30244,0.18447,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.13546,0.30363,0.53367]}],"total_contact_groups":7},"final_pose_error":0.04901,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.19118,0.11456,0.53362],"hinge_angle":0.52785,"initial_hinge_angle":-0.14464,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":-0.14464,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":562.56332,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":459.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":38.18469,"phase_name":"approach_contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":416.0,"raw_peak_contact_force":0.0,"tcp_end":[0.09957,0.32332,0.34764],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.48508,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":336.0,"n_steps_budget":960.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":367.0,"raw_peak_contact_force":9.01022,"tcp_end":[0.09878,0.45664,0.34467],"tcp_start":[0.09957,0.32332,0.34764],"tcp_to_object_dist_end":0.58058,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":827.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1511.0,"raw_peak_contact_force":562.56332,"tcp_end":[0.19118,0.11456,0.53362],"tcp_start":[0.09878,0.45664,0.34467],"tcp_to_object_dist_end":0.57829,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```