## Search State

- **Seed**: 4
- **Iteration**: 2 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 1 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 5 | 0.8711 | 0.82 | ✅ accepted |
| 0 | push → align → release | impedance_motion | linear_cartesian | linear_cartesian | position_control | position_control | position_control | time_limit | pose_tolerance | time_limit | 3 | 0.0400 | 0.22 | ✅ accepted |

**Proposal policy**: task_score is 0.82 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
- task_score stagnant: change coupled targets, parameters, terminations, phase types, controls, subtasks, or ordering when evidence shows they need to change together.
A HOLD wastes an iteration when task_score is below 0.9.

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

## Current Skill (Q=0.871) — your mutation base

```yaml
skill: door_push
dsl_version: 2
skill_type: arm_gripper
phases:
- id: approach_1
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
    - 0.05
    tolerance: 0.01
    orientation:
      mode: keep_current
      tolerance: 0.1
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
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
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.01
    orientation:
      mode: keep_current
      tolerance: 0.1
  parameters:
    contact_force_threshold:
      type: scalar
      range:
      - 3.0
      - 15.0
      default: 5.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    contact_speed:
      type: scalar
      range:
      - 0.005
      - 0.05
      default: 0.01
      binds_to:
      - path: generator.speed
        mode: replace
- id: push_1
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.15
      axis: world_y
      mode: add_to_offset
      sign: negative
    tolerance: 0.01
    orientation:
      mode: keep_current
      tolerance: 0.1
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.05
      - 0.25
      default: 0.15
      binds_to:
      - path: target.offset_along_axis.distance
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
  guards:
  - id: force_limit
    when: during_phase
    predicate: force_below
    threshold: 25.0
    on_failure: abort

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.05], tolerance=0.01
  - orientation: mode=keep_current, tolerance=0.1
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **contact_1** (`contact`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - orientation: mode=keep_current, tolerance=0.1
  - parameter_bindings:
    - contact_force_threshold: status=consumed; consumers=termination.force_threshold (replace)
    - contact_speed: status=consumed; consumers=generator.speed (replace)
- **push_1** (`push`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_y, distance=0.15, mode=add_to_offset, sign=negative}, tolerance=0.01
  - orientation: mode=keep_current, tolerance=0.1
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=force_limit, when=during_phase, predicate=force_below, on_failure=abort, threshold=25.0

## Design Metrics

- **Composite score**: 0.871
- **task_score** (E): 0.818
- **fitness_score**: 0.818  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.333
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.280

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2152 |
| contact_1 | 1.00 | 1.00 | 0.0018 |
| push_1 | 0.00 | 0.67 | 0.1251 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.100, 0.399, 0.350)→(0.100, 0.189, 0.396) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 3.667 | 7.786 | 29.411 |
| contact_1 | contact | 1.00 / force_exceeded | (0.100, 0.189, 0.396)→(0.100, 0.188, 0.394) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 2.333 | 18.241 | 16.294 |
| push_1 | push | 0.00 / step_budget | (0.100, 0.188, 0.394)→(0.097, 0.065, 0.412) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 0.67 / 3.000 | 3.880 | 24.207 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- hinge_angle_ratio: 0.978
- arc_quality: 0.667

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.978
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.978
- **Median Q (composite search score)**: 0.856
- **K-run variance**: 0.0156
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.261


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.84211,"average_solve_count":133.0,"average_success_count":133.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.06709,"contact_1.contact_force_threshold":9.43904,"contact_1.contact_speed":0.02511,"push_1.push_distance":0.14624,"push_1.push_speed":0.04996},"optimized_scores":{"best_composite_score":0.72658,"best_fitness_score":0.67325,"best_task_score":0.67325},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link7","contact_count":72.0,"contact_point_centroid":[0.16506,0.14107,0.41725],"force_p95":25.32214,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":29.2921,"mean_force":14.60228,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.09981,0.19848,0.39344]},{"body_a":"door_panel","body_b":"link7","contact_count":720.0,"contact_point_centroid":[0.16443,0.0583,0.41968],"force_p95":20.72227,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":25.10758,"mean_force":12.65475,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.09888,0.11565,0.39301]},{"body_a":"door_panel","body_b":"link7","contact_count":5.0,"contact_point_centroid":[0.16497,0.13061,0.41694],"force_p95":16.35551,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":16.43652,"mean_force":11.21845,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.0997,0.18809,0.39311]},{"body_a":"world","body_b":"door_panel","contact_count":1044.0,"contact_point_centroid":[0.30392,0.15939,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.09975,0.29083,0.37235]},{"body_a":"world","body_b":"door_panel","contact_count":28.0,"contact_point_centroid":[0.30622,0.1495,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.09968,0.18796,0.39265]},{"body_a":"world","body_b":"door_panel","contact_count":912.0,"contact_point_centroid":[0.31993,0.11371,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.09895,0.11578,0.39223]}],"total_contact_groups":6},"final_pose_error":0.07264,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.09671,0.06979,0.41299],"hinge_angle":0.50744,"initial_hinge_angle":0.15466,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.15466,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":29.2921,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":953.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":12.78236,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1116.0,"raw_peak_contact_force":29.2921,"tcp_end":[0.09977,0.18879,0.3956],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.44955,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":41.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":22.27622,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":33.0,"raw_peak_contact_force":16.43652,"tcp_end":[0.09965,0.18745,0.39051],"tcp_start":[0.09977,0.18879,0.3956],"tcp_to_object_dist_end":0.44449,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":991.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1632.0,"raw_peak_contact_force":25.10758,"tcp_end":[0.09671,0.06979,0.41299],"tcp_start":[0.09965,0.18745,0.39051],"tcp_to_object_dist_end":0.42987,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.0,"average_solve_count":131.0,"average_success_count":131.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.07058,"contact_1.contact_force_threshold":12.56688,"contact_1.contact_speed":0.01737,"push_1.push_distance":0.24772,"push_1.push_speed":0.01129},"optimized_scores":{"best_composite_score":0.85584,"best_fitness_score":0.8025,"best_task_score":0.8025},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link7","contact_count":84.0,"contact_point_centroid":[0.16504,0.14396,0.41654],"force_p95":28.0724,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":28.32728,"mean_force":14.47974,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.09977,0.20138,0.39272]},{"body_a":"door_panel","body_b":"link6","contact_count":52.0,"contact_point_centroid":[0.10281,0.15317,0.49335],"force_p95":26.41181,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":27.83996,"mean_force":12.27513,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.09978,0.22029,0.38843]},{"body_a":"door_panel","body_b":"link7","contact_count":725.0,"contact_point_centroid":[0.16503,0.05284,0.42225],"force_p95":20.60971,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":23.80006,"mean_force":12.85205,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.09923,0.11014,0.39569]},{"body_a":"door_panel","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.16505,0.13153,0.41942],"force_p95":14.68746,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":16.3194,"mean_force":5.4398,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.0998,0.18893,0.39564]},{"body_a":"world","body_b":"door_panel","contact_count":1036.0,"contact_point_centroid":[0.30235,0.16802,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.09974,0.2951,0.37134]},{"body_a":"world","body_b":"door_panel","contact_count":8.0,"contact_point_centroid":[0.30604,0.15022,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.0998,0.18894,0.39564]},{"body_a":"world","body_b":"door_panel","contact_count":980.0,"contact_point_centroid":[0.32119,0.11156,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.09927,0.11074,0.39502]}],"total_contact_groups":7},"final_pose_error":0.14324,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.09786,0.06179,0.41116],"hinge_angle":0.52698,"initial_hinge_angle":0.10647,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.10647,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":28.32728,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":924.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":5.28691,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1172.0,"raw_peak_contact_force":28.32728,"tcp_end":[0.09981,0.18898,0.39563],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.44966,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":16.3194,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":11.0,"raw_peak_contact_force":16.3194,"tcp_end":[0.09978,0.18887,0.39562],"tcp_start":[0.09981,0.18898,0.39563],"tcp_to_object_dist_end":0.4496,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1705.0,"raw_peak_contact_force":23.80006,"tcp_end":[0.09786,0.06179,0.41116],"tcp_start":[0.09978,0.18887,0.39562],"tcp_to_object_dist_end":0.42714,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.97692,"average_solve_count":130.0,"average_success_count":130.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.07063,"contact_1.contact_force_threshold":7.17616,"contact_1.contact_speed":0.01333,"push_1.push_distance":0.24282,"push_1.push_speed":0.04405},"optimized_scores":{"best_composite_score":1.03103,"best_fitness_score":0.9777,"best_task_score":0.9777},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link6","contact_count":186.0,"contact_point_centroid":[0.10133,0.17119,0.48953],"force_p95":27.83917,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":30.6134,"mean_force":14.3219,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.09966,0.24237,0.38321]},{"body_a":"door_panel","body_b":"link7","contact_count":84.0,"contact_point_centroid":[0.16503,0.14398,0.41651],"force_p95":28.08417,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":28.37225,"mean_force":14.5131,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.09976,0.20139,0.39269]},{"body_a":"door_panel","body_b":"link7","contact_count":720.0,"contact_point_centroid":[0.16502,0.05311,0.42219],"force_p95":20.98635,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":23.71376,"mean_force":12.84317,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.09922,0.11041,0.39562]},{"body_a":"door_panel","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.16505,0.13153,0.41941],"force_p95":14.51437,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":16.12707,"mean_force":5.37569,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.0998,0.18894,0.39563]},{"body_a":"world","body_b":"door_panel","contact_count":976.0,"contact_point_centroid":[0.30105,0.17998,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.0997,0.2884,0.37278]},{"body_a":"world","body_b":"door_panel","contact_count":4.0,"contact_point_centroid":[0.30602,0.15029,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.0998,0.18898,0.39562]},{"body_a":"world","body_b":"door_panel","contact_count":964.0,"contact_point_centroid":[0.32162,0.11092,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.09917,0.10903,0.39641]}],"total_contact_groups":7},"final_pose_error":0.13929,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.09783,0.06234,0.41111],"hinge_angle":0.52564,"initial_hinge_angle":0.01332,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.01332,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":30.6134,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":926.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":5.28964,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1246.0,"raw_peak_contact_force":30.6134,"tcp_end":[0.0998,0.18898,0.39562],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.44965,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":16.12707,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":7.0,"raw_peak_contact_force":16.12707,"tcp_end":[0.09978,0.18888,0.39561],"tcp_start":[0.0998,0.18898,0.39562],"tcp_to_object_dist_end":0.44959,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":11.64103,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1684.0,"raw_peak_contact_force":23.71376,"tcp_end":[0.09783,0.06234,0.41111],"tcp_start":[0.09978,0.18888,0.39561],"tcp_to_object_dist_end":0.42716,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```