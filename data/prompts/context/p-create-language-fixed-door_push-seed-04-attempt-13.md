## Search State

- **Seed**: 4
- **Iteration**: 14 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 13 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | time_limit | force_exceeded | time_limit | 7 | 1.6200 | 1.00 | ❌ rejected |
| 12 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | time_limit | force_exceeded | time_limit | 7 | 1.6200 | 1.00 | ❌ rejected |
| 11 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | time_limit | force_exceeded | time_limit | 7 | 1.6200 | 1.00 | ✅ accepted |
| 10 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | time_limit | 6 | 1.1700 | 1.00 | ❌ rejected |
| 9 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | time_limit | 6 | 1.1700 | 1.00 | ✅ accepted |

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

## Current Skill (Q=1.620) — your mutation base

```yaml
skill: door_push
dsl_version: 2
phases:
- id: approach_1
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: time_limit
  target:
    source: yaml
    anchor: site
    entity: door_handle
    offset:
    - 0.0
    - -0.02
    - 0.0
    tolerance: 0.05
    orientation:
      mode: keep_current
  parameters:
    approach_offset_y:
      type: scalar
      range:
      - -0.05
      - 0.0
      default: -0.02
      binds_to:
      - path: target.offset.y
        mode: replace
    approach_speed:
      type: scalar
      range:
      - 0.01
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
    approach_time_limit:
      type: scalar
      range:
      - 2.0
      - 10.0
      default: 5.0
      binds_to:
      - path: duration.max_time
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
- id: push_1
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: time_limit
  target:
    source: yaml
    anchor: world
    offset:
    - 0.1
    - 0.18
    - 0.35
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
      - 0.02
      - 0.35
      default: 0.25
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
    push_time_limit:
      type: scalar
      range:
      - 5.0
      - 30.0
      default: 15.0
      binds_to:
      - path: duration.max_time
        mode: replace

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=site, entity=door_handle, offset=[0.0, -0.02, 0.0], tolerance=0.05
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_offset_y: status=consumed; consumers=target.offset.y (replace)
    - approach_speed: status=consumed; consumers=generator.speed (replace)
    - approach_time_limit: status=consumed; consumers=duration.max_time (replace)
- **contact_1** (`contact`)
  - target: source=yaml, anchor=site, entity=door_handle, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - contact_force: status=consumed; consumers=termination.force_threshold (replace)
- **push_1** (`push`)
  - target: source=yaml, anchor=world, offset=[0.1, 0.18, 0.35], offset_along_axis={axis=world_y, distance=0.25, mode=add_to_offset, sign=negative}, tolerance=0.05
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
    - push_time_limit: status=consumed; consumers=duration.max_time (replace)

## Design Metrics

- **Composite score**: 1.620
- **task_score** (E): 1.000
- **fitness_score**: 1.000  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 1.000
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.380

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 0.33 | 0.1933 |
| contact_1 | 1.00 | 1.00 | 0.0244 |
| push_1 | 1.00 | 0.33 | 0.2197 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / time_limit | (0.100, 0.399, 0.350)→(0.102, 0.206, 0.358) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 0.33 / 0.333 | 10.817 | 25.311 |
| contact_1 | contact | 1.00 / force_exceeded | (0.102, 0.206, 0.358)→(0.103, 0.182, 0.358) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 1.333 | 17.883 | 23.992 |
| push_1 | push | 1.00 / time_limit | (0.103, 0.182, 0.358)→(0.102, -0.031, 0.407) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 0.33 / 1.333 | 0.000 | 48.788 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- hinge_angle_ratio: 1.000
- arc_quality: 1.000

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 1.000
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 1.620
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: tolflatfitness
- **Mean generations**: 3.0
- **Final σ (mean)**: 0.367


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.30097,"average_solve_count":103.0,"average_success_count":103.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_offset_y":-0.02138,"approach_1.approach_speed":0.04635,"approach_1.approach_time_limit":6.79027,"contact_1.contact_force":13.53862,"push_1.push_distance":0.22788,"push_1.push_speed":0.15682,"push_1.push_time_limit":16.91948},"optimized_scores":{"best_composite_score":1.62,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link7","contact_count":674.0,"contact_point_centroid":[0.17043,0.04454,0.41294],"force_p95":28.3679,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":50.79519,"mean_force":14.66375,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.10173,0.09623,0.38737]},{"body_a":"door_panel","body_b":"link7","contact_count":14.0,"contact_point_centroid":[0.16981,0.14997,0.37094],"force_p95":19.06342,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":30.92583,"mean_force":12.97255,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.10451,0.20726,0.34689]},{"body_a":"door_panel","body_b":"link6","contact_count":26.0,"contact_point_centroid":[0.10451,0.14079,0.45271],"force_p95":8.71084,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":8.88694,"mean_force":4.00286,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.10448,0.20819,0.34685]},{"body_a":"world","body_b":"door_panel","contact_count":1060.0,"contact_point_centroid":[0.30379,0.16,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.10113,0.33791,0.34774]},{"body_a":"world","body_b":"door_panel","contact_count":368.0,"contact_point_centroid":[0.3036,0.16094,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.10348,0.24198,0.34648]},{"body_a":"door_panel","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.10469,0.13898,0.4527],"force_p95":0.0,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.10452,0.20623,0.34693]},{"body_a":"world","body_b":"door_panel","contact_count":852.0,"contact_point_centroid":[0.32474,0.10972,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.10219,0.09614,0.38504]}],"total_contact_groups":7},"final_pose_error":0.05347,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.10364,-0.06145,0.40159],"hinge_angle":0.71234,"initial_hinge_angle":0.15466,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.15466,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":50.79519,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1060.0,"raw_peak_contact_force":0.0,"tcp_end":[0.1028,0.27576,0.34783],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.45563,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":423.0,"n_steps_budget":960.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":30.92583,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":408.0,"raw_peak_contact_force":30.92583,"tcp_end":[0.10452,0.20623,0.34693],"tcp_start":[0.1028,0.27576,0.34783],"tcp_to_object_dist_end":0.41691,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":982.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1527.0,"raw_peak_contact_force":50.79519,"tcp_end":[0.10364,-0.06145,0.40159],"tcp_start":[0.10452,0.20623,0.34693],"tcp_to_object_dist_end":0.41928,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":5.60294,"average_solve_count":68.0,"average_success_count":68.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_offset_y":-0.02486,"approach_1.approach_speed":0.17114,"approach_1.approach_time_limit":5.68032,"contact_1.contact_force":10.24395,"push_1.push_distance":0.22087,"push_1.push_speed":0.12386,"push_1.push_time_limit":21.60827},"optimized_scores":{"best_composite_score":1.62,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link7","contact_count":550.0,"contact_point_centroid":[0.17126,0.00567,0.43675],"force_p95":22.50073,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":50.13134,"mean_force":13.97405,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.10167,0.05644,0.40979]},{"body_a":"door_panel","body_b":"link7","contact_count":222.0,"contact_point_centroid":[0.16881,0.11617,0.37853],"force_p95":30.01663,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":43.48185,"mean_force":16.27057,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.10353,0.17354,0.35461]},{"body_a":"door_panel","body_b":"link6","contact_count":73.0,"contact_point_centroid":[0.10331,0.14984,0.45399],"force_p95":17.96903,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":24.05945,"mean_force":8.17856,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.10261,0.2185,0.34842]},{"body_a":"door_panel","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.1699,0.07823,0.40392],"force_p95":13.13879,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":13.13879,"mean_force":13.13879,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.10475,0.13562,0.37961]},{"body_a":"world","body_b":"door_panel","contact_count":1112.0,"contact_point_centroid":[0.30425,0.16061,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.10182,0.26816,0.35064]},{"body_a":"world","body_b":"door_panel","contact_count":16.0,"contact_point_centroid":[0.3157,0.12167,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.10446,0.13641,0.37892]},{"body_a":"world","body_b":"door_panel","contact_count":732.0,"contact_point_centroid":[0.33529,0.08827,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.10192,0.04722,0.40959]}],"total_contact_groups":7},"final_pose_error":0.05486,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.10366,-0.05786,0.40203],"hinge_angle":0.71107,"initial_hinge_angle":0.10647,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.10647,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":50.13134,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1407.0,"raw_peak_contact_force":43.48185,"tcp_end":[0.10436,0.13694,0.37834],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.41568,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":14.0,"n_steps_budget":660.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":13.13879,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":17.0,"raw_peak_contact_force":13.13879,"tcp_end":[0.10478,0.13553,0.37969],"tcp_start":[0.10436,0.13694,0.37834],"tcp_to_object_dist_end":0.41655,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":871.0,"n_steps_budget":900.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1282.0,"raw_peak_contact_force":50.13134,"tcp_end":[0.10366,-0.05786,0.40203],"tcp_start":[0.10478,0.13553,0.37969],"tcp_to_object_dist_end":0.41919,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.96,"average_solve_count":75.0,"average_success_count":75.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_offset_y":-0.021,"approach_1.approach_speed":0.11948,"approach_1.approach_time_limit":4.08211,"contact_1.contact_force":5.33482,"push_1.push_distance":0.1925,"push_1.push_speed":0.10871,"push_1.push_time_limit":14.32204},"optimized_scores":{"best_composite_score":1.62,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link7","contact_count":722.0,"contact_point_centroid":[0.16357,0.06822,0.40954],"force_p95":20.40569,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":45.43782,"mean_force":13.96552,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.09808,0.12511,0.38283]},{"body_a":"door_panel","body_b":"link7","contact_count":25.0,"contact_point_centroid":[0.16529,0.1518,0.37227],"force_p95":14.22644,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":32.45244,"mean_force":14.03973,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.1,0.20905,0.34842]},{"body_a":"door_panel","body_b":"link7","contact_count":4.0,"contact_point_centroid":[0.16534,0.14898,0.37228],"force_p95":25.16142,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":27.91053,"mean_force":10.12352,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.10001,0.20632,0.34842]},{"body_a":"door_panel","body_b":"link6","contact_count":270.0,"contact_point_centroid":[0.10137,0.17082,0.45461],"force_p95":17.73537,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":20.98938,"mean_force":8.20573,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.09986,0.24254,0.34827]},{"body_a":"world","body_b":"door_panel","contact_count":984.0,"contact_point_centroid":[0.30067,0.18254,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.09974,0.30137,0.34807]},{"body_a":"world","body_b":"door_panel","contact_count":20.0,"contact_point_centroid":[0.30384,0.15971,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.10001,0.20604,0.3484]},{"body_a":"world","body_b":"door_panel","contact_count":996.0,"contact_point_centroid":[0.31818,0.1198,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.09823,0.1255,0.38189]}],"total_contact_groups":7},"final_pose_error":0.07846,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.0973,0.0269,0.41779],"hinge_angle":0.59054,"initial_hinge_angle":0.01332,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.01332,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":45.43782,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":32.45244,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1279.0,"raw_peak_contact_force":32.45244,"tcp_end":[0.10002,0.20679,0.34846],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.41736,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":11.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":9.58315,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":24.0,"raw_peak_contact_force":27.91053,"tcp_end":[0.10006,0.20504,0.34822],"tcp_start":[0.10002,0.20679,0.34846],"tcp_to_object_dist_end":0.41631,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1718.0,"raw_peak_contact_force":45.43782,"tcp_end":[0.0973,0.0269,0.41779],"tcp_start":[0.10006,0.20504,0.34822],"tcp_to_object_dist_end":0.42982,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
```