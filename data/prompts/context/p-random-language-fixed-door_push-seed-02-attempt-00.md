## Search State

- **Seed**: 2
- **Iteration**: 1 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 0 | approach → align → align → pull → descend → release → grasp → push | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | — | — | impedance_motion | position_control | position_control | position_control | impedance_control | position_control | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | contact_detected | time_limit | grasp_success | pose_tolerance | 7 | -0.0589 | 0.47 | ✅ accepted |

**Proposal policy**: task_score is 0.47 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.059) — your mutation base

```yaml
skill: door_push
skill_type: arm_gripper
phases:
- id: approach_1
  type: approach
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
- id: align_1
  type: align
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    lateral_offset_y:
      type: scalar
      range:
      - -0.01
      - 0.01
- id: align_2
  type: align
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    lateral_offset_x:
      type: scalar
      range:
      - -0.01
      - 0.01
- id: pull_1
  type: pull
  generator: linear_cartesian
  control: impedance_control
  termination: time_limit
  parameters:
    pull_distance:
      type: scalar
      range:
      - 0.02
      - 0.2
- id: descend_1
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: contact_detected
  parameters:
    depth:
      type: scalar
      range:
      - 0.01
      - 0.1
- id: release_1
  type: release
  control: position_control
  termination: time_limit
  end_effector_action: open
- id: grasp_1
  type: grasp
  control: position_control
  termination: grasp_success
  end_effector_action: force_grasp
  parameters:
    grip_force:
      type: scalar
      range:
      - 5.0
      - 30.0
- id: push_1
  type: push
  generator: impedance_motion
  control: impedance_control
  termination: pose_tolerance
  parameters:
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.1

```

## Design Metrics

- **Composite score**: -0.059
- **task_score** (E): 0.471
- **fitness_score**: 0.471  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.530

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 0.67 | 0.2116 |
| align_1 | 1.00 | 0.33 | 0.0022 |
| align_2 | 1.00 | 0.67 | 0.0017 |
| pull_1 | 1.00 | 1.00 | 0.0014 |
| descend_1 | 0.67 | 0.67 | 0.0012 |
| release_1 | 1.00 | 1.00 | 0.0034 |
| grasp_1 | 1.00 | 1.00 | 0.0034 |
| push_1 | 1.00 | 0.33 | 0.0003 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.100, 0.399, 0.350)→(0.100, 0.188, 0.356) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 0.67 / 0.667 | 4.379 | 27.660 |
| align_1 | align | 1.00 / step_budget | (0.100, 0.188, 0.356)→(0.100, 0.186, 0.354) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 0.33 / 1.333 | 0.000 | 14.800 |
| align_2 | align | 1.00 / step_budget | (0.100, 0.186, 0.354)→(0.100, 0.185, 0.353) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 0.67 / 0.667 | 4.516 | 14.244 |
| pull_1 | pull | 1.00 / time_limit | (0.100, 0.185, 0.353)→(0.100, 0.184, 0.352) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 3.667 | 8.765 | 13.427 |
| descend_1 | descend | 0.67 / step_budget | (0.100, 0.184, 0.352)→(0.100, 0.183, 0.352) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 0.67 / 0.667 | 8.611 | 12.908 |
| release_1 | release | 1.00 / step_budget | (0.100, 0.183, 0.352)→(0.099, 0.181, 0.349) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 1.000 | 0.775 | 10.924 |
| grasp_1 | grasp | 1.00 / step_budget | (0.099, 0.181, 0.349)→(0.099, 0.179, 0.346) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 2.333 | 0.687 | 12.650 |
| push_1 | push | 1.00 / step_budget | (0.099, 0.179, 0.346)→(0.099, 0.179, 0.346) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 0.33 / 1.667 | 2.060 | 12.794 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- hinge_angle_ratio: 0.700
- arc_quality: 0.875

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.700
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.700
- **Median Q (composite search score)**: 0.053
- **K-run variance**: 0.0606
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.303


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.38854,"average_solve_count":157.0,"average_success_count":157.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_y":0.00335,"align_2.lateral_offset_x":-0.00311,"approach_1.speed":0.07896,"descend_1.depth":0.05553,"grasp_1.grip_force":7.27732,"pull_1.pull_distance":0.10112,"push_1.push_speed":0.05951},"optimized_scores":{"best_composite_score":0.05342,"best_fitness_score":0.58342,"best_task_score":0.58342},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link7","contact_count":350.0,"contact_point_centroid":[0.14728,0.17925,0.42692],"force_p95":21.6502,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":25.53396,"mean_force":13.79029,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.09973,0.24055,0.38208]},{"body_a":"door_panel","body_b":"link6","contact_count":15.0,"contact_point_centroid":[0.10132,0.23125,0.5052],"force_p95":16.96971,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":21.60991,"mean_force":11.03649,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.09968,0.28822,0.3927]},{"body_a":"door_panel","body_b":"link7","contact_count":6.0,"contact_point_centroid":[0.14472,0.12642,0.40473],"force_p95":15.09322,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":15.10496,"mean_force":14.8384,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.09975,0.18654,0.35479]},{"body_a":"door_panel","body_b":"link7","contact_count":5.0,"contact_point_centroid":[0.14463,0.12512,0.40359],"force_p95":14.50341,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":14.55863,"mean_force":13.82369,"phase_index":2.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.0997,0.18513,0.35349]},{"body_a":"door_panel","body_b":"link7","contact_count":9.0,"contact_point_centroid":[0.14457,0.12432,0.4029],"force_p95":13.53803,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":13.53951,"mean_force":11.19331,"phase_index":3.0,"phase_name":"pull_1","phase_type":"pull","tcp_position_centroid":[0.09966,0.18426,0.35269]},{"body_a":"door_panel","body_b":"link7","contact_count":8.0,"contact_point_centroid":[0.14448,0.12339,0.40209],"force_p95":12.90291,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":12.91061,"mean_force":10.3988,"phase_index":4.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.09959,0.18325,0.35175]},{"body_a":"door_panel","body_b":"link7","contact_count":9.0,"contact_point_centroid":[0.14349,0.11954,0.39717],"force_p95":12.31183,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":12.79442,"mean_force":8.34739,"phase_index":7.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.09859,0.17871,0.346]},{"body_a":"door_panel","body_b":"link7","contact_count":403.0,"contact_point_centroid":[0.14358,0.11991,0.39764],"force_p95":5.0739,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":12.62049,"mean_force":1.77105,"phase_index":6.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.09868,0.17914,0.34654]},{"body_a":"door_panel","body_b":"link7","contact_count":149.0,"contact_point_centroid":[0.14411,0.12187,0.40024],"force_p95":5.32393,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":11.90445,"mean_force":2.9416,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.09923,0.18148,0.34958]},{"body_a":"world","body_b":"door_panel","contact_count":1044.0,"contact_point_centroid":[0.30064,0.19448,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.09971,0.30318,0.37863]},{"body_a":"world","body_b":"door_panel","contact_count":12.0,"contact_point_centroid":[0.30614,0.14982,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.09977,0.18696,0.35517]},{"body_a":"world","body_b":"door_panel","contact_count":16.0,"contact_point_centroid":[0.30632,0.14912,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.09972,0.18563,0.35394]},{"body_a":"world","body_b":"door_panel","contact_count":20.0,"contact_point_centroid":[0.30643,0.14869,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":3.0,"phase_name":"pull_1","phase_type":"pull","tcp_position_centroid":[0.09968,0.18465,0.35304]},{"body_a":"world","body_b":"door_panel","contact_count":28.0,"contact_point_centroid":[0.30658,0.14814,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":4.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.0996,0.18345,0.35192]},{"body_a":"world","body_b":"door_panel","contact_count":208.0,"contact_point_centroid":[0.30679,0.14739,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.09926,0.18159,0.34972]},{"body_a":"world","body_b":"door_panel","contact_count":464.0,"contact_point_centroid":[0.30705,0.14642,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":6.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.09869,0.17919,0.34661]}],"total_contact_groups":17},"final_pose_error":0.00442,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.09868,0.17855,0.34604],"hinge_angle":0.2225,"initial_hinge_angle":-0.08321,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":-0.08321,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":25.53396,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":971.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1409.0,"raw_peak_contact_force":25.53396,"tcp_end":[0.0998,0.18776,0.35596],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.41464,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":20.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":18.0,"raw_peak_contact_force":15.10496,"tcp_end":[0.09974,0.18613,0.35447],"tcp_start":[0.0998,0.18776,0.35596],"tcp_to_object_dist_end":0.4126,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":20.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":13.54706,"phase_name":"align_2","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":21.0,"raw_peak_contact_force":14.55863,"tcp_end":[0.09969,0.18485,0.35327],"tcp_start":[0.09974,0.18613,0.35447],"tcp_to_object_dist_end":0.41098,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":20.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":12.68837,"phase_name":"pull_1","phase_peak_obstacle_force":0.0,"phase_type":"pull","raw_contact_event_count":29.0,"raw_peak_contact_force":13.53951,"tcp_end":[0.09964,0.18382,0.35231],"tcp_start":[0.09969,0.18485,0.35327],"tcp_to_object_dist_end":0.40969,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":20.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":12.91061,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":36.0,"raw_peak_contact_force":12.91061,"tcp_end":[0.09958,0.18294,0.3515],"tcp_start":[0.09964,0.18382,0.35231],"tcp_to_object_dist_end":0.40858,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":1.00467,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":357.0,"raw_peak_contact_force":11.90445,"tcp_end":[0.09911,0.18093,0.34885],"tcp_start":[0.09958,0.18294,0.3515],"tcp_to_object_dist_end":0.40528,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.68591,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":867.0,"raw_peak_contact_force":12.62049,"tcp_end":[0.09862,0.17885,0.34617],"tcp_start":[0.09911,0.18093,0.34885],"tcp_to_object_dist_end":0.40193,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":20.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":21.0,"raw_peak_contact_force":12.79442,"tcp_end":[0.09868,0.17855,0.34604],"tcp_start":[0.09862,0.17885,0.34617],"tcp_to_object_dist_end":0.4017,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.425,"average_solve_count":160.0,"average_success_count":160.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_y":-0.00636,"align_2.lateral_offset_x":-0.00108,"approach_1.speed":0.07483,"descend_1.depth":0.04666,"grasp_1.grip_force":22.67642,"pull_1.pull_distance":0.04958,"push_1.push_speed":0.02902},"optimized_scores":{"best_composite_score":0.17036,"best_fitness_score":0.70036,"best_task_score":0.70036},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link6","contact_count":42.0,"contact_point_centroid":[0.10167,0.23569,0.50468],"force_p95":27.83183,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":33.78813,"mean_force":15.65294,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.09959,0.29387,0.39247]},{"body_a":"door_panel","body_b":"link7","contact_count":341.0,"contact_point_centroid":[0.14723,0.17855,0.42664],"force_p95":21.3565,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":28.18001,"mean_force":14.04487,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.09972,0.23988,0.38173]},{"body_a":"door_panel","body_b":"link7","contact_count":9.0,"contact_point_centroid":[0.14475,0.12688,0.40514],"force_p95":14.58858,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":14.68195,"mean_force":11.02125,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.09977,0.18705,0.35527]},{"body_a":"door_panel","body_b":"link7","contact_count":6.0,"contact_point_centroid":[0.14466,0.12546,0.40389],"force_p95":13.86305,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":13.90509,"mean_force":13.12348,"phase_index":2.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.09971,0.18552,0.35384]},{"body_a":"door_panel","body_b":"link7","contact_count":13.0,"contact_point_centroid":[0.14459,0.12452,0.40309],"force_p95":13.03953,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":13.18024,"mean_force":10.03759,"phase_index":3.0,"phase_name":"pull_1","phase_type":"pull","tcp_position_centroid":[0.09966,0.18449,0.3529]},{"body_a":"door_panel","body_b":"link7","contact_count":16.0,"contact_point_centroid":[0.1445,0.1236,0.4023],"force_p95":12.38743,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":12.88989,"mean_force":7.79614,"phase_index":4.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.0996,0.18349,0.35198]},{"body_a":"door_panel","body_b":"link7","contact_count":10.0,"contact_point_centroid":[0.14349,0.11957,0.39722],"force_p95":12.1841,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":12.7943,"mean_force":7.61135,"phase_index":7.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.0986,0.17873,0.34604]},{"body_a":"door_panel","body_b":"link7","contact_count":402.0,"contact_point_centroid":[0.14357,0.11994,0.39768],"force_p95":5.34799,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":12.6663,"mean_force":1.7733,"phase_index":6.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.09868,0.17917,0.34658]},{"body_a":"door_panel","body_b":"link7","contact_count":149.0,"contact_point_centroid":[0.14411,0.12191,0.40028],"force_p95":5.44648,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":11.90356,"mean_force":2.96476,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.09923,0.18151,0.34962]},{"body_a":"world","body_b":"door_panel","contact_count":976.0,"contact_point_centroid":[0.30084,0.19456,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.0997,0.2949,0.37927]},{"body_a":"world","body_b":"door_panel","contact_count":12.0,"contact_point_centroid":[0.30615,0.14977,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.09976,0.18684,0.35507]},{"body_a":"world","body_b":"door_panel","contact_count":20.0,"contact_point_centroid":[0.30628,0.14927,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.09973,0.18582,0.35414]},{"body_a":"world","body_b":"door_panel","contact_count":12.0,"contact_point_centroid":[0.30645,0.14865,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":3.0,"phase_name":"pull_1","phase_type":"pull","tcp_position_centroid":[0.09966,0.18444,0.35286]},{"body_a":"world","body_b":"door_panel","contact_count":16.0,"contact_point_centroid":[0.30656,0.14823,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":4.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.09961,0.18353,0.35203]},{"body_a":"world","body_b":"door_panel","contact_count":212.0,"contact_point_centroid":[0.30679,0.14736,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.09922,0.1815,0.3496]},{"body_a":"world","body_b":"door_panel","contact_count":508.0,"contact_point_centroid":[0.30705,0.14642,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":6.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.09868,0.17918,0.34659]}],"total_contact_groups":17},"final_pose_error":0.00438,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.09867,0.17858,0.34607],"hinge_angle":0.22235,"initial_hinge_angle":-0.14464,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":-0.14464,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":33.78813,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":976.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":13.13715,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1359.0,"raw_peak_contact_force":33.78813,"tcp_end":[0.0998,0.18778,0.35599],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.41467,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":20.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":21.0,"raw_peak_contact_force":14.68195,"tcp_end":[0.09974,0.18616,0.3545],"tcp_start":[0.0998,0.18778,0.35599],"tcp_to_object_dist_end":0.41264,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":20.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"align_2","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":26.0,"raw_peak_contact_force":13.90509,"tcp_end":[0.09969,0.18487,0.35331],"tcp_start":[0.09974,0.18616,0.3545],"tcp_to_object_dist_end":0.41102,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":20.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":6.76552,"phase_name":"pull_1","phase_peak_obstacle_force":0.0,"phase_type":"pull","raw_contact_event_count":25.0,"raw_peak_contact_force":13.18024,"tcp_end":[0.09964,0.18383,0.35234],"tcp_start":[0.09969,0.18487,0.35331],"tcp_to_object_dist_end":0.40971,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":20.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":32.0,"raw_peak_contact_force":12.88989,"tcp_end":[0.09958,0.18298,0.35155],"tcp_start":[0.09964,0.18383,0.35234],"tcp_to_object_dist_end":0.40863,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":1.31956,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":361.0,"raw_peak_contact_force":11.90356,"tcp_end":[0.0991,0.18096,0.3489],"tcp_start":[0.09958,0.18298,0.35155],"tcp_to_object_dist_end":0.40534,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.68786,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":910.0,"raw_peak_contact_force":12.6663,"tcp_end":[0.09862,0.17888,0.34621],"tcp_start":[0.0991,0.18096,0.3489],"tcp_to_object_dist_end":0.40198,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":20.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":6.18007,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":50.0,"raw_peak_contact_force":12.7943,"tcp_end":[0.09867,0.17858,0.34607],"tcp_start":[0.09862,0.17888,0.34621],"tcp_to_object_dist_end":0.40174,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.36774,"average_solve_count":155.0,"average_success_count":155.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_y":-0.00974,"align_2.lateral_offset_x":0.00541,"approach_1.speed":0.08229,"descend_1.depth":0.08663,"grasp_1.grip_force":13.89522,"pull_1.pull_distance":0.07093,"push_1.push_speed":0.05419},"optimized_scores":{"best_composite_score":-0.40061,"best_fitness_score":0.12939,"best_task_score":0.12939},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link7","contact_count":65.0,"contact_point_centroid":[0.14514,0.13763,0.41275],"force_p95":22.71937,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":23.65928,"mean_force":15.25922,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.09981,0.19832,0.36391]},{"body_a":"door_panel","body_b":"link7","contact_count":7.0,"contact_point_centroid":[0.14476,0.12684,0.40503],"force_p95":14.61223,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":14.61308,"mean_force":12.2783,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.09977,0.187,0.35515]},{"body_a":"door_panel","body_b":"link7","contact_count":9.0,"contact_point_centroid":[0.14466,0.12538,0.40378],"force_p95":14.0925,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":14.26896,"mean_force":12.98768,"phase_index":2.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.09971,0.18544,0.35372]},{"body_a":"door_panel","body_b":"link7","contact_count":7.0,"contact_point_centroid":[0.14455,0.1242,0.40275],"force_p95":13.56116,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":13.56199,"mean_force":12.79107,"phase_index":3.0,"phase_name":"pull_1","phase_type":"pull","tcp_position_centroid":[0.09964,0.18412,0.35252]},{"body_a":"door_panel","body_b":"link7","contact_count":8.0,"contact_point_centroid":[0.14447,0.12341,0.40208],"force_p95":12.91499,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":12.92235,"mean_force":10.40905,"phase_index":4.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.09959,0.18327,0.35174]},{"body_a":"door_panel","body_b":"link7","contact_count":9.0,"contact_point_centroid":[0.14349,0.11956,0.39717],"force_p95":12.31976,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":12.79444,"mean_force":8.40271,"phase_index":7.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.09859,0.17873,0.346]},{"body_a":"door_panel","body_b":"link7","contact_count":403.0,"contact_point_centroid":[0.14358,0.11993,0.39764],"force_p95":5.17439,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":12.66265,"mean_force":1.76791,"phase_index":6.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.09868,0.17916,0.34654]},{"body_a":"door_panel","body_b":"link7","contact_count":151.0,"contact_point_centroid":[0.14411,0.12189,0.40024],"force_p95":5.32489,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":8.96394,"mean_force":2.93448,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.09923,0.18151,0.34958]},{"body_a":"world","body_b":"door_panel","contact_count":992.0,"contact_point_centroid":[0.3039,0.15947,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.09974,0.30057,0.37729]},{"body_a":"world","body_b":"door_panel","contact_count":12.0,"contact_point_centroid":[0.30613,0.14985,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.09978,0.18708,0.35522]},{"body_a":"world","body_b":"door_panel","contact_count":20.0,"contact_point_centroid":[0.30631,0.14917,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.09972,0.18557,0.35385]},{"body_a":"world","body_b":"door_panel","contact_count":4.0,"contact_point_centroid":[0.30644,0.14869,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":3.0,"phase_name":"pull_1","phase_type":"pull","tcp_position_centroid":[0.09968,0.18472,0.35308]},{"body_a":"world","body_b":"door_panel","contact_count":8.0,"contact_point_centroid":[0.30655,0.14825,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":4.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.09961,0.18357,0.35203]},{"body_a":"world","body_b":"door_panel","contact_count":232.0,"contact_point_centroid":[0.30679,0.14736,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.09923,0.18152,0.34959]},{"body_a":"world","body_b":"door_panel","contact_count":432.0,"contact_point_centroid":[0.30705,0.14641,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":6.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.09868,0.17918,0.34656]},{"body_a":"world","body_b":"door_panel","contact_count":16.0,"contact_point_centroid":[0.30711,0.1462,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":7.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.0986,0.1787,0.346]}],"total_contact_groups":16},"final_pose_error":0.00442,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.09868,0.17857,0.34604],"hinge_angle":0.22246,"initial_hinge_angle":0.15466,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.15466,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":23.65928,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":954.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1057.0,"raw_peak_contact_force":23.65928,"tcp_end":[0.09981,0.18778,0.35592],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.41461,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":20.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":19.0,"raw_peak_contact_force":14.61308,"tcp_end":[0.09975,0.18615,0.35443],"tcp_start":[0.09981,0.18778,0.35592],"tcp_to_object_dist_end":0.41258,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":20.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"align_2","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":29.0,"raw_peak_contact_force":14.26896,"tcp_end":[0.0997,0.18489,0.35327],"tcp_start":[0.09975,0.18615,0.35443],"tcp_to_object_dist_end":0.411,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":20.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":6.84227,"phase_name":"pull_1","phase_peak_obstacle_force":0.0,"phase_type":"pull","raw_contact_event_count":11.0,"raw_peak_contact_force":13.56199,"tcp_end":[0.09964,0.18384,0.35231],"tcp_start":[0.0997,0.18489,0.35327],"tcp_to_object_dist_end":0.40969,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":20.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":12.92235,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":16.0,"raw_peak_contact_force":12.92235,"tcp_end":[0.09958,0.18296,0.35149],"tcp_start":[0.09964,0.18384,0.35231],"tcp_to_object_dist_end":0.40858,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":383.0,"raw_peak_contact_force":8.96394,"tcp_end":[0.0991,0.18095,0.34885],"tcp_start":[0.09958,0.18296,0.35149],"tcp_to_object_dist_end":0.40529,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.68607,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":835.0,"raw_peak_contact_force":12.66265,"tcp_end":[0.09862,0.17887,0.34617],"tcp_start":[0.0991,0.18095,0.34885],"tcp_to_object_dist_end":0.40193,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":20.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":25.0,"raw_peak_contact_force":12.79444,"tcp_end":[0.09868,0.17857,0.34604],"tcp_start":[0.09862,0.17887,0.34617],"tcp_to_object_dist_end":0.4017,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```