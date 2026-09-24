## Search State

- **Seed**: 1
- **Iteration**: 4 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 3 | approach → push | linear_cartesian | linear_cartesian | position_control | impedance_control | pose_tolerance | time_limit | 5 | 0.2741 | 0.52 | ❌ rejected |
| 2 | approach → push | arc_cartesian | linear_cartesian | force_threshold_switch | impedance_control | force_exceeded | time_limit | 5 | -0.2493 | 0.00 | ❌ rejected |
| 1 | approach → push | arc_cartesian | linear_cartesian | position_control | impedance_control | pose_tolerance | time_limit | 4 | -0.2000 | 0.00 | ❌ rejected |
| 0 | rotate → align → push | arc_cartesian | linear_cartesian | impedance_motion | impedance_control | position_control | position_control | time_limit | pose_tolerance | time_limit | 3 | 0.3605 | 0.54 | ✅ accepted |

**Proposal policy**: task_score is 0.52 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.274) — your mutation base

```yaml
skill: door_push
phases:
- id: rotate_1
  type: rotate
  generator: arc_cartesian
  control: impedance_control
  termination: time_limit
  parameters:
    yaw_angle:
      type: angle
      range:
      - 0.1
      - 1.57
- id: align_1
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
- id: push_1
  type: push
  generator: impedance_motion
  control: position_control
  termination: time_limit
  parameters:
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.1

```

## Design Metrics

- **Composite score**: 0.274
- **task_score** (E): 0.524
- **fitness_score**: 0.524  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.250

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_handle | 1.00 | 1.00 | 0.2095 |
| push_handle | 0.00 | 0.67 | 0.0001 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_handle | approach | 1.00 / step_budget | (0.100, 0.399, 0.350)→(0.100, 0.190, 0.349) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 2.333 | 10.319 | 29.630 |
| push_handle | push | 0.00 / guard_failure | (0.100, 0.190, 0.349)→(0.100, 0.190, 0.349) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 0.67 / 3.000 | 0.000 | 0.000 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- hinge_angle_ratio: 0.658
- arc_quality: 0.500

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.658
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.658
- **Median Q (composite search score)**: 0.291
- **K-run variance**: 0.0135
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.303


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.87755,"average_solve_count":49.0,"average_success_count":49.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_handle.approach_speed":0.09402,"push_handle.force_threshold":9.98866,"push_handle.push_distance":0.37503,"push_handle.push_duration":2.86843,"push_handle.push_speed":0.04094},"optimized_scores":{"best_composite_score":0.12398,"best_fitness_score":0.37398,"best_task_score":0.37398},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link7","contact_count":78.0,"contact_point_centroid":[0.1651,0.14337,0.37234],"force_p95":20.71957,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":25.19188,"mean_force":14.78815,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.09985,0.20077,0.34847]},{"body_a":"door_panel","body_b":"link6","contact_count":206.0,"contact_point_centroid":[0.10123,0.17343,0.45473],"force_p95":17.72664,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":21.01531,"mean_force":8.99398,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.09972,0.24557,0.34819]},{"body_a":"world","body_b":"door_panel","contact_count":856.0,"contact_point_centroid":[0.30077,0.18287,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.09968,0.30043,0.34802]},{"body_a":"door_panel","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.16514,0.13223,0.37241],"force_p95":0.0,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"push_handle","phase_type":"push","tcp_position_centroid":[0.09988,0.1897,0.34855]}],"total_contact_groups":4},"final_pose_error":0.67505,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.09986,0.18962,0.34854],"hinge_angle":0.20009,"initial_hinge_angle":0.00413,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.00413,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":25.19188,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":824.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":13.15904,"phase_name":"approach_handle","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1140.0,"raw_peak_contact_force":25.19188,"subtask_id":"reach_handle","tcp_end":[0.09988,0.1897,0.34855],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.40921,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"push_handle","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1.0,"raw_peak_contact_force":0.0,"subtask_id":"push_door","tcp_end":[0.09986,0.18962,0.34854],"tcp_start":[0.09988,0.1897,0.34855],"tcp_to_object_dist_end":0.40916,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.72414,"average_solve_count":29.0,"average_success_count":29.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_handle.approach_speed":0.16578,"push_handle.force_threshold":11.77371,"push_handle.push_distance":0.40534,"push_handle.push_duration":6.96755,"push_handle.push_speed":0.07995},"optimized_scores":{"best_composite_score":0.29077,"best_fitness_score":0.54077,"best_task_score":0.54077},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link6","contact_count":322.0,"contact_point_centroid":[0.101,0.19004,0.4558],"force_p95":23.06418,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":40.72421,"mean_force":9.49977,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.09965,0.26533,0.34829]},{"body_a":"door_panel","body_b":"link7","contact_count":70.0,"contact_point_centroid":[0.1652,0.14344,0.37258],"force_p95":23.30917,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":33.60066,"mean_force":15.20127,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.09992,0.20074,0.34867]},{"body_a":"world","body_b":"door_panel","contact_count":748.0,"contact_point_centroid":[0.30069,0.19159,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.09967,0.2982,0.34819]},{"body_a":"door_panel","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.16523,0.13225,0.37258],"force_p95":0.0,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"push_handle","phase_type":"push","tcp_position_centroid":[0.09996,0.18971,0.34869]}],"total_contact_groups":4},"final_pose_error":0.70536,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.09994,0.18963,0.34868],"hinge_angle":0.20015,"initial_hinge_angle":-0.08321,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":-0.08321,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":40.72421,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":728.0,"n_steps_budget":840.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":13.19132,"phase_name":"approach_handle","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1140.0,"raw_peak_contact_force":40.72421,"subtask_id":"reach_handle","tcp_end":[0.09996,0.18971,0.34869],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.40935,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"push_handle","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1.0,"raw_peak_contact_force":0.0,"subtask_id":"push_door","tcp_end":[0.09994,0.18963,0.34868],"tcp_start":[0.09996,0.18971,0.34869],"tcp_to_object_dist_end":0.40929,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.42254,"average_solve_count":71.0,"average_success_count":71.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_handle.approach_speed":0.06366,"push_handle.force_threshold":12.15522,"push_handle.push_distance":0.42788,"push_handle.push_duration":7.10466,"push_handle.push_speed":0.07056},"optimized_scores":{"best_composite_score":0.40751,"best_fitness_score":0.65751,"best_task_score":0.65751},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link7","contact_count":81.0,"contact_point_centroid":[0.1651,0.14352,0.37229],"force_p95":21.20485,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":22.97428,"mean_force":14.6603,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.09985,0.20097,0.34843]},{"body_a":"door_panel","body_b":"link6","contact_count":396.0,"contact_point_centroid":[0.10103,0.19307,0.45584],"force_p95":13.3928,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":15.9773,"mean_force":8.19654,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.09965,0.26912,0.34804]},{"body_a":"world","body_b":"door_panel","contact_count":780.0,"contact_point_centroid":[0.3008,0.19229,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.09965,0.29572,0.34801]},{"body_a":"door_panel","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.16513,0.13229,0.37236],"force_p95":0.0,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"push_handle","phase_type":"push","tcp_position_centroid":[0.09987,0.18976,0.34851]},{"body_a":"world","body_b":"door_panel","contact_count":4.0,"contact_point_centroid":[0.30594,0.15058,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"push_handle","phase_type":"push","tcp_position_centroid":[0.09987,0.18976,0.34851]}],"total_contact_groups":5},"final_pose_error":0.72789,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.09985,0.18967,0.3485],"hinge_angle":0.1999,"initial_hinge_angle":-0.14464,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":-0.14464,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":22.97428,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":878.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":4.60534,"phase_name":"approach_handle","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1257.0,"raw_peak_contact_force":22.97428,"subtask_id":"reach_handle","tcp_end":[0.09987,0.18976,0.34851],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.4092,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"push_handle","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":5.0,"raw_peak_contact_force":0.0,"subtask_id":"push_door","tcp_end":[0.09985,0.18967,0.3485],"tcp_start":[0.09987,0.18976,0.34851],"tcp_to_object_dist_end":0.40915,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```