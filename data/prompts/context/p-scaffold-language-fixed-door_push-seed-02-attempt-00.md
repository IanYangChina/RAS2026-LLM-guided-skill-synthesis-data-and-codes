## Search State

- **Seed**: 2
- **Iteration**: 1 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 0 | approach → contact → push → retract | linear_cartesian | impedance_motion | linear_cartesian | arc_cartesian | position_control | admittance_control | position_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 3 | 0.2353 | 0.45 | ✅ accepted |

**Proposal policy**: task_score is 0.45 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.235) — your mutation base

```yaml
skill: door_push
phases:
- id: approach_1
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.05
      - 0.3
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
- id: contact_1
  type: contact
  generator: impedance_motion
  control: admittance_control
  termination: contact_detected
- id: push_1
  type: push
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.02
      - 0.2
- id: retract_1
  type: retract
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance

```

## Design Metrics

- **Composite score**: 0.235
- **task_score** (E): 0.445
- **fitness_score**: 0.445  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.210

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2095 |
| contact_1 | 0.67 | 0.67 | 0.0052 |
| push_1 | 1.00 | 1.00 | 0.0011 |
| retract_1 | 1.00 | 0.00 | 0.0009 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.100, 0.399, 0.350)→(0.100, 0.190, 0.349) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 2.333 | 5.821 | 28.617 |
| contact_1 | contact | 0.67 / step_budget | (0.100, 0.190, 0.349)→(0.100, 0.185, 0.348) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 0.67 / 0.667 | 3.899 | 14.482 |
| push_1 | push | 1.00 / step_budget | (0.100, 0.185, 0.348)→(0.100, 0.184, 0.348) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 3.667 | 8.781 | 12.458 |
| retract_1 | retract | 1.00 / step_budget | (0.100, 0.184, 0.348)→(0.100, 0.183, 0.348) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 0.00 / 0.000 | 0.000 | 12.556 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- hinge_angle_ratio: 0.675
- arc_quality: 1.000

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.675
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.675
- **Median Q (composite search score)**: 0.348
- **K-run variance**: 0.0607
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 10.0
- **Final σ (mean)**: 0.415


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.44785,"average_solve_count":163.0,"average_success_count":163.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.12493,"approach_1.speed":0.04313,"push_1.push_distance":0.1036},"optimized_scores":{"best_composite_score":0.34752,"best_fitness_score":0.55752,"best_task_score":0.55752},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link6","contact_count":69.0,"contact_point_centroid":[0.10095,0.22676,0.47113],"force_p95":23.5851,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":25.32898,"mean_force":14.01915,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.09948,0.28406,0.3478]},{"body_a":"door_panel","body_b":"link7","contact_count":323.0,"contact_point_centroid":[0.14993,0.17635,0.39508],"force_p95":20.32487,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":21.36791,"mean_force":13.28585,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.09968,0.23387,0.34818]},{"body_a":"door_panel","body_b":"link7","contact_count":37.0,"contact_point_centroid":[0.146,0.12914,0.39959],"force_p95":13.91604,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":14.31401,"mean_force":11.67403,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.09978,0.18705,0.3482]},{"body_a":"door_panel","body_b":"link7","contact_count":8.0,"contact_point_centroid":[0.14556,0.12518,0.39925],"force_p95":12.62069,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":12.66055,"mean_force":9.54101,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.09963,0.183,0.34765]},{"body_a":"door_panel","body_b":"link7","contact_count":6.0,"contact_point_centroid":[0.14573,0.12596,0.39929],"force_p95":12.53077,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":12.56666,"mean_force":11.61474,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.0997,0.18379,0.34789]},{"body_a":"world","body_b":"door_panel","contact_count":1012.0,"contact_point_centroid":[0.30044,0.19574,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.09961,0.29943,0.34794]},{"body_a":"world","body_b":"door_panel","contact_count":68.0,"contact_point_centroid":[0.30586,0.15091,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.09978,0.18696,0.34818]},{"body_a":"world","body_b":"door_panel","contact_count":28.0,"contact_point_centroid":[0.30624,0.14943,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.09973,0.18425,0.34803]},{"body_a":"world","body_b":"door_panel","contact_count":24.0,"contact_point_centroid":[0.30635,0.14902,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.09966,0.18332,0.34775]}],"total_contact_groups":9},"final_pose_error":0.00361,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.09961,0.1827,0.34763],"hinge_angle":0.20893,"initial_hinge_angle":-0.08321,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":-0.08321,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":25.32898,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":920.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1404.0,"raw_peak_contact_force":25.32898,"tcp_end":[0.09986,0.18973,0.34855],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.40922,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":51.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":105.0,"raw_peak_contact_force":14.31401,"tcp_end":[0.09976,0.18457,0.3482],"tcp_start":[0.09986,0.18973,0.34855],"tcp_to_object_dist_end":0.40652,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":20.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":4.80718,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":34.0,"raw_peak_contact_force":12.56666,"tcp_end":[0.09969,0.18353,0.34788],"tcp_start":[0.09976,0.18457,0.3482],"tcp_to_object_dist_end":0.40577,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":20.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":32.0,"raw_peak_contact_force":12.66055,"tcp_end":[0.09961,0.1827,0.34763],"tcp_start":[0.09969,0.18353,0.34788],"tcp_to_object_dist_end":0.40516,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.61468,"average_solve_count":109.0,"average_success_count":109.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.05688,"approach_1.speed":0.09221,"push_1.push_distance":0.04566},"optimized_scores":{"best_composite_score":0.46479,"best_fitness_score":0.67479,"best_task_score":0.67479},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link6","contact_count":90.0,"contact_point_centroid":[0.10127,0.23061,0.47079],"force_p95":31.85622,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":36.63122,"mean_force":14.6594,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.09941,0.28932,0.34779]},{"body_a":"door_panel","body_b":"link7","contact_count":311.0,"contact_point_centroid":[0.14982,0.17493,0.39527],"force_p95":24.55351,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":28.56834,"mean_force":13.10545,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.09967,0.23244,0.34822]},{"body_a":"door_panel","body_b":"link7","contact_count":36.0,"contact_point_centroid":[0.14598,0.12917,0.39959],"force_p95":14.04482,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":14.67585,"mean_force":11.59886,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.09977,0.18707,0.3482]},{"body_a":"door_panel","body_b":"link7","contact_count":8.0,"contact_point_centroid":[0.14555,0.12531,0.39932],"force_p95":12.53486,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":12.58686,"mean_force":9.86416,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.09964,0.18317,0.3477]},{"body_a":"door_panel","body_b":"link7","contact_count":10.0,"contact_point_centroid":[0.14565,0.12621,0.3996],"force_p95":12.47746,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":12.51682,"mean_force":9.04013,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.09971,0.18412,0.34798]},{"body_a":"world","body_b":"door_panel","contact_count":788.0,"contact_point_centroid":[0.3008,0.19378,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.0996,0.28935,0.34801]},{"body_a":"world","body_b":"door_panel","contact_count":60.0,"contact_point_centroid":[0.30587,0.15088,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.09977,0.18695,0.34819]},{"body_a":"world","body_b":"door_panel","contact_count":16.0,"contact_point_centroid":[0.30627,0.14933,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.0997,0.18392,0.34793]},{"body_a":"world","body_b":"door_panel","contact_count":32.0,"contact_point_centroid":[0.30635,0.149,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.09965,0.18327,0.34773]}],"total_contact_groups":9},"final_pose_error":0.00362,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.09961,0.18273,0.34765],"hinge_angle":0.20895,"initial_hinge_angle":-0.14464,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":-0.14464,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":36.63122,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":830.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":12.68102,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1189.0,"raw_peak_contact_force":36.63122,"tcp_end":[0.09985,0.18977,0.34856],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.40924,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":51.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":96.0,"raw_peak_contact_force":14.67585,"tcp_end":[0.09975,0.18459,0.34821],"tcp_start":[0.09985,0.18977,0.34856],"tcp_to_object_dist_end":0.40653,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":20.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":10.91588,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":26.0,"raw_peak_contact_force":12.51682,"tcp_end":[0.09969,0.18356,0.3479],"tcp_start":[0.09975,0.18459,0.34821],"tcp_to_object_dist_end":0.40579,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":20.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":40.0,"raw_peak_contact_force":12.58686,"tcp_end":[0.09961,0.18273,0.34765],"tcp_start":[0.09969,0.18356,0.3479],"tcp_to_object_dist_end":0.40518,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.53968,"average_solve_count":126.0,"average_success_count":126.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.22698,"approach_1.speed":0.06796,"push_1.push_distance":0.11989},"optimized_scores":{"best_composite_score":-0.10649,"best_fitness_score":0.10351,"best_task_score":0.10351},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link7","contact_count":56.0,"contact_point_centroid":[0.14709,0.14014,0.39886],"force_p95":21.54389,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":23.89196,"mean_force":13.87727,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.09979,0.1979,0.34841]},{"body_a":"door_panel","body_b":"link7","contact_count":36.0,"contact_point_centroid":[0.14596,0.12922,0.39952],"force_p95":14.0396,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":14.45557,"mean_force":11.59181,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.09971,0.18713,0.34816]},{"body_a":"door_panel","body_b":"link7","contact_count":8.0,"contact_point_centroid":[0.14543,0.1252,0.39945],"force_p95":12.25944,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":12.42086,"mean_force":9.67377,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.09959,0.18308,0.34764]},{"body_a":"door_panel","body_b":"link7","contact_count":10.0,"contact_point_centroid":[0.14569,0.12625,0.39945],"force_p95":12.28487,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":12.29012,"mean_force":8.04597,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.09967,0.18413,0.34797]},{"body_a":"world","body_b":"door_panel","contact_count":900.0,"contact_point_centroid":[0.30386,0.15964,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.09966,0.29699,0.34805]},{"body_a":"world","body_b":"door_panel","contact_count":48.0,"contact_point_centroid":[0.30592,0.15069,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.09971,0.18654,0.34818]},{"body_a":"world","body_b":"door_panel","contact_count":28.0,"contact_point_centroid":[0.30623,0.14947,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.09967,0.1842,0.34796]},{"body_a":"world","body_b":"door_panel","contact_count":20.0,"contact_point_centroid":[0.30635,0.14901,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.0996,0.18324,0.34767]}],"total_contact_groups":8},"final_pose_error":0.00363,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.09958,0.1827,0.34761],"hinge_angle":0.20889,"initial_hinge_angle":0.15466,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.15466,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":23.89196,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":869.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":4.78226,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":956.0,"raw_peak_contact_force":23.89196,"tcp_end":[0.09979,0.18987,0.34852],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.40924,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":52.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":11.69807,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":84.0,"raw_peak_contact_force":14.45557,"tcp_end":[0.09971,0.18456,0.34818],"tcp_start":[0.09979,0.18987,0.34852],"tcp_to_object_dist_end":0.40648,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":20.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":10.6205,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":38.0,"raw_peak_contact_force":12.29012,"tcp_end":[0.09965,0.18353,0.34786],"tcp_start":[0.09971,0.18456,0.34818],"tcp_to_object_dist_end":0.40574,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":20.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":28.0,"raw_peak_contact_force":12.42086,"tcp_end":[0.09958,0.1827,0.34761],"tcp_start":[0.09965,0.18353,0.34786],"tcp_to_object_dist_end":0.40513,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```