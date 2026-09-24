## Search State

- **Seed**: 4
- **Iteration**: 12 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 11 | push → align → release → insert | impedance_motion | linear_cartesian | linear_cartesian | impedance_motion | impedance_control | position_control | admittance_control | impedance_control | time_limit | pose_tolerance | pose_tolerance | force_exceeded | 6 | 0.4171 | 0.80 | ✅ accepted |
| 10 | push → align → release → insert | impedance_motion | linear_cartesian | linear_cartesian | impedance_motion | impedance_control | position_control | admittance_control | impedance_control | time_limit | pose_tolerance | pose_tolerance | force_exceeded | 6 | 0.4187 | 0.80 | ❌ rejected |
| 9 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | 6 | -0.2283 | 0.00 | ❌ rejected |
| 8 | approach → descend → push | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | admittance_control | pose_tolerance | pose_tolerance | force_exceeded | 8 | -0.3614 | 0.00 | ❌ rejected |
| 7 | approach → descend → align → push | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | position_control | admittance_control | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | 8 | -0.3071 | 0.04 | ❌ rejected |

**Proposal policy**: task_score is 0.80 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

- Task name: push_to_goal
- Goal tolerance: 0.02 m
- Expressivity sigma: 1.0 m
- Expressivity threshold: 0.8
- Force limit: 25.0 N
- Primary evaluation target: **object displacement ratio toward goal_object_position**

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
| `object` | offset from object initial position | approach/contact targets near object start |
| `goal` | offset from task goal position | final destination targets |
| `fixture` | offset from fixture pose | targets near fixture |

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

## Current Skill (Q=0.417) — your mutation base

```yaml
skill: push_to_goal
skill_type: arm_gripper
phases:
- id: push_1
  type: push
  generator: impedance_motion
  control: impedance_control
  termination: time_limit
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.02
      - 0.2
    push_speed:
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
    lateral_offset_x:
      type: scalar
      range:
      - -0.01
      - 0.01
    lateral_offset_y:
      type: scalar
      range:
      - -0.01
      - 0.01
- id: release_1
  type: release
  generator: linear_cartesian
  control: admittance_control
  termination: pose_tolerance
  end_effector_action: open
- id: insert_1
  type: insert
  generator: impedance_motion
  control: impedance_control
  termination: force_exceeded
  parameters:
    insertion_depth:
      type: scalar
      range:
      - 0.01
      - 0.15
    insertion_force:
      type: scalar
      range:
      - 1.0
      - 20.0

```

## Design Metrics

- **Composite score**: 0.417
- **task_score** (E): 0.802
- **fitness_score**: 0.444  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.333
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.360

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| push_1 | 1.00 | 1.00 | 0.1840 |
| align_1 | 1.00 | 1.00 | 0.1756 |
| release_1 | 0.33 | 1.00 | 0.1669 |
| insert_1 | 1.00 | 1.00 | 0.0000 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| push_1 | push | 1.00 / time_limit | (0.500, -0.000, 0.301)→(0.497, -0.059, 0.128) | (0.531, 0.007, 0.025)→(0.531, 0.007, 0.025) | 0.161→0.161 | 1.00 / 4.000 | 0.245 | 0.245 |
| align_1 | align | 1.00 / step_budget | (0.497, -0.059, 0.128)→(0.527, 0.079, 0.028) | (0.531, 0.007, 0.025)→(0.533, 0.016, 0.028) | 0.161→0.171 | 1.00 / 3.667 | 24.544 | 60.410 |
| release_1 | release | 0.33 / step_budget | (0.527, 0.079, 0.028)→(0.506, -0.086, 0.021) | (0.533, 0.016, 0.028)→(0.522, -0.130, 0.026) | 0.171→0.034 | 1.00 / 3.667 | 17.937 | 103.516 |
| insert_1 | insert | 1.00 / force_exceeded | (0.506, -0.086, 0.021)→(0.505, -0.086, 0.021) | (0.522, -0.130, 0.026)→(0.522, -0.130, 0.026) | 0.034→0.034 | 1.00 / 3.667 | 34.905 | 34.905 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 1.000
- lateral_force_integral: None
- approach_alignment: 0.691
- goal_progress: 0.934
- terminal_score: 0.934
- phase_score: 0.202
- phase_breakdown.approach_score: 0.821
- phase_breakdown.contact_score: 0.000
- phase_breakdown.push_score: 0.076

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.495
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.934
- **Median Q (composite search score)**: 0.414
- **K-run variance**: 0.0016
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.245


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `8d5a7e825d9524a0954b44a69bda19e1d764760f64bb1262d03aec3c389fadbb`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.06,0.06]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `c4094dd933e0897d422d7ea261a82b80810f7dec183b19c1da5b940157e7d0c4`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.6791,"average_solve_count":134.0,"average_success_count":134.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":-0.00276,"align_1.lateral_offset_y":0.00291,"insert_1.insertion_depth":0.10745,"insert_1.insertion_force":7.04967,"push_1.push_distance":0.05692,"push_1.push_speed":0.0651},"optimized_scores":{"best_composite_score":0.41351,"best_fitness_score":0.44017,"best_task_score":0.79216},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":1075.0,"contact_point_centroid":[0.55965,-0.05038,0.05049],"force_p95":58.99872,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":75.40865,"mean_force":34.97015,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.52238,-0.02962,0.02156]},{"body_a":"world","body_b":"push_box","contact_count":2121.0,"contact_point_centroid":[0.55402,-0.05526,-0.00017],"force_p95":53.5278,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":73.09999,"mean_force":21.35534,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.5269,-0.00679,0.02127]},{"body_a":"attachment","body_b":"push_box","contact_count":860.0,"contact_point_centroid":[0.52859,-0.0561,0.03841],"force_p95":45.35848,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":55.68715,"mean_force":16.92432,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.51945,-0.04516,0.02195]},{"body_a":"world","body_b":"push_box","contact_count":1.0,"contact_point_centroid":[0.56084,-0.13576,-0.00035],"force_p95":43.7163,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":43.7163,"mean_force":43.7163,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.51047,-0.09087,0.02208]},{"body_a":"push_box","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.54571,-0.11306,0.05105],"force_p95":42.30268,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":42.30268,"mean_force":42.30268,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.51047,-0.09087,0.02208]},{"body_a":"attachment","body_b":"push_box","contact_count":1.0,"contact_point_centroid":[0.53159,-0.10012,0.0528],"force_p95":19.62554,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":19.62554,"mean_force":19.62554,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.51047,-0.09087,0.02208]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.55317,0.00136,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49721,-0.01837,0.20462]},{"body_a":"world","body_b":"push_box","contact_count":2844.0,"contact_point_centroid":[0.55317,0.00136,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.52043,0.02065,0.06489]}],"total_contact_groups":8},"final_pose_error":0.06013,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.52744,-0.13111,0.02643],"final_tcp_position":[0.51045,-0.09086,0.02205],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55317,0.00136,0.025]},"peak_contact_force":75.40865,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.55317,0.00136,0.02499],"object_pos_start":[0.55317,0.00136,0.025],"object_to_goal_dist_end":0.16043,"object_to_goal_dist_start":0.16043,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.49643,-0.03676,0.11267],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.11118,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":711.0,"n_steps_budget":990.0,"object_pos_end":[0.55317,0.00136,0.02499],"object_pos_start":[0.55317,0.00136,0.02499],"object_to_goal_dist_end":0.16043,"object_to_goal_dist_start":0.16043,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":2844.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.54584,0.07484,0.02355],"tcp_start":[0.49643,-0.03676,0.11267],"tcp_to_object_dist_end":0.07386,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52745,-0.1311,0.02647],"object_pos_start":[0.55317,0.00136,0.02499],"object_to_goal_dist_end":0.03335,"object_to_goal_dist_start":0.16043,"object_z_max":0.02926,"peak_contact_force":30.92602,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":4056.0,"raw_peak_contact_force":75.40865,"tcp_end":[0.51047,-0.09087,0.02208],"tcp_start":[0.54584,0.07484,0.02355],"tcp_to_object_dist_end":0.04389,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.52744,-0.13111,0.02643],"object_pos_start":[0.52745,-0.1311,0.02647],"object_to_goal_dist_end":0.03334,"object_to_goal_dist_start":0.03335,"object_z_max":0.02647,"peak_contact_force":43.7163,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":3.0,"raw_peak_contact_force":43.7163,"tcp_end":[0.51045,-0.09086,0.02205],"tcp_start":[0.51047,-0.09087,0.02208],"tcp_to_object_dist_end":0.04391,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `452b4d03bf1b69f7d6475210c4cc0fbd85197208ecbf5594cd2cfcf54c82bcbb`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.90476,"average_solve_count":126.0,"average_success_count":126.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":-0.00508,"align_1.lateral_offset_y":0.00553,"insert_1.insertion_depth":0.12737,"insert_1.insertion_force":10.57301,"push_1.push_distance":0.19467,"push_1.push_speed":0.09957},"optimized_scores":{"best_composite_score":0.36938,"best_fitness_score":0.39605,"best_task_score":0.67858},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":218.0,"contact_point_centroid":[0.53602,0.07124,0.04597],"force_p95":149.89217,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":180.73938,"mean_force":97.26162,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.52882,0.07865,0.04797]},{"body_a":"attachment","body_b":"push_box","contact_count":916.0,"contact_point_centroid":[0.53346,0.02979,0.03469],"force_p95":153.28602,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":162.12837,"mean_force":115.21034,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.52938,0.04003,0.03543]},{"body_a":"world","body_b":"push_box","contact_count":3394.0,"contact_point_centroid":[0.53703,0.04022,-6e-05],"force_p95":54.87534,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":146.99392,"mean_force":7.17575,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.51048,-0.00184,0.08828]},{"body_a":"world","body_b":"push_box","contact_count":2429.0,"contact_point_centroid":[0.53759,-0.02309,-0.00041],"force_p95":102.65848,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":113.9548,"mean_force":58.76087,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.52578,0.02349,0.03296]},{"body_a":"push_box","body_b":"link7","contact_count":1049.0,"contact_point_centroid":[0.56128,-0.00084,0.06722],"force_p95":72.61095,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":83.93471,"mean_force":46.07241,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.52795,0.03479,0.03426]},{"body_a":"push_box","body_b":"link7","contact_count":34.0,"contact_point_centroid":[0.56736,0.07314,0.06719],"force_p95":76.62263,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":76.67988,"mean_force":63.96951,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.53389,0.1062,0.03436]},{"body_a":"push_box","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.55323,-0.07275,0.04971],"force_p95":31.71185,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":31.71185,"mean_force":31.71185,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.50981,-0.04962,0.02244]},{"body_a":"world","body_b":"push_box","contact_count":3.0,"contact_point_centroid":[0.54258,-0.0908,-5e-05],"force_p95":21.12127,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":22.79879,"mean_force":10.96199,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.50981,-0.04962,0.02244]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.5366,0.03695,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4973,-0.04473,0.21749]}],"total_contact_groups":9},"final_pose_error":0.1009,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.53526,-0.09994,0.02494],"final_tcp_position":[0.50981,-0.04962,0.02243],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.5366,0.03695,0.025]},"peak_contact_force":180.73938,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5366,0.03695,0.02499],"object_pos_start":[0.5366,0.03695,0.025],"object_to_goal_dist_end":0.1905,"object_to_goal_dist_start":0.1905,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.49667,-0.08809,0.14099],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.17517,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":968.0,"n_steps_budget":1000.0,"object_pos_end":[0.54238,0.06677,0.03283],"object_pos_start":[0.5366,0.03695,0.02499],"object_to_goal_dist_end":0.22101,"object_to_goal_dist_start":0.1905,"object_z_max":0.0349,"peak_contact_force":73.1406,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":3646.0,"raw_peak_contact_force":180.73938,"tcp_end":[0.53508,0.1101,0.03205],"tcp_start":[0.49667,-0.08809,0.14099],"tcp_to_object_dist_end":0.04395,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53526,-0.09994,0.02494],"object_pos_start":[0.54238,0.06677,0.03283],"object_to_goal_dist_end":0.06123,"object_to_goal_dist_start":0.22101,"object_z_max":0.03449,"peak_contact_force":6.26602,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":4394.0,"raw_peak_contact_force":162.12837,"tcp_end":[0.50981,-0.04962,0.02244],"tcp_start":[0.53508,0.1101,0.03205],"tcp_to_object_dist_end":0.05645,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1.0,"n_steps_budget":660.0,"object_pos_end":[0.53526,-0.09994,0.02494],"object_pos_start":[0.53526,-0.09994,0.02494],"object_to_goal_dist_end":0.06123,"object_to_goal_dist_start":0.06123,"object_z_max":0.02494,"peak_contact_force":31.71185,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":4.0,"raw_peak_contact_force":31.71185,"tcp_end":[0.50981,-0.04962,0.02243],"tcp_start":[0.50981,-0.04962,0.02244],"tcp_to_object_dist_end":0.05645,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `e3aaa9b30183e782395a479a1824f41a69a2557638e862a63e7a5368dd2a464a`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.41379,"average_solve_count":145.0,"average_success_count":145.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":-0.00219,"align_1.lateral_offset_y":0.00199,"insert_1.insertion_depth":0.07782,"insert_1.insertion_force":8.10726,"push_1.push_distance":0.06654,"push_1.push_speed":0.04996},"optimized_scores":{"best_composite_score":0.46841,"best_fitness_score":0.49508,"best_task_score":0.93426},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":957.0,"contact_point_centroid":[0.51534,-0.07217,0.04941],"force_p95":57.36651,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":73.01226,"mean_force":29.22779,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49811,-0.06164,0.0229]},{"body_a":"world","body_b":"push_box","contact_count":2286.0,"contact_point_centroid":[0.51237,-0.08916,-0.0001],"force_p95":44.55015,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":66.01919,"mean_force":17.09653,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49768,-0.03438,0.02304]},{"body_a":"push_box","body_b":"link7","contact_count":890.0,"contact_point_centroid":[0.52535,-0.08711,0.0549],"force_p95":47.57859,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":57.27486,"mean_force":28.65972,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49828,-0.06689,0.02296]},{"body_a":"push_box","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.52259,-0.14315,0.05124],"force_p95":29.28655,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":29.28655,"mean_force":29.28655,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49625,-0.11621,0.01892]},{"body_a":"world","body_b":"push_box","contact_count":2.0,"contact_point_centroid":[0.51054,-0.18021,-0.00013],"force_p95":22.51693,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":23.28575,"mean_force":15.5975,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49625,-0.11621,0.01892]},{"body_a":"attachment","body_b":"push_box","contact_count":1.0,"contact_point_centroid":[0.51636,-0.12736,0.05245],"force_p95":13.71355,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":13.71355,"mean_force":13.71355,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49625,-0.11621,0.01892]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.50458,-0.01881,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49726,-0.02553,0.21328]},{"body_a":"world","body_b":"push_box","contact_count":2212.0,"contact_point_centroid":[0.50458,-0.01881,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49685,0.00092,0.07694]}],"total_contact_groups":8},"final_pose_error":0.03455,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50181,-0.15836,0.02611],"final_tcp_position":[0.49623,-0.1162,0.0189],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50458,-0.01881,0.025]},"peak_contact_force":73.01226,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50458,-0.01881,0.02499],"object_pos_start":[0.50458,-0.01881,0.025],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.49653,-0.05101,0.13026],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.11038,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":553.0,"n_steps_budget":960.0,"object_pos_end":[0.50458,-0.01881,0.02499],"object_pos_start":[0.50458,-0.01881,0.02499],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":2212.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.49982,0.05289,0.0274],"tcp_start":[0.49653,-0.05101,0.13026],"tcp_to_object_dist_end":0.07189,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50182,-0.15836,0.02613],"object_pos_start":[0.50458,-0.01881,0.02499],"object_to_goal_dist_end":0.00863,"object_to_goal_dist_start":0.13127,"object_z_max":0.02986,"peak_contact_force":16.61792,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":4133.0,"raw_peak_contact_force":73.01226,"tcp_end":[0.49625,-0.11621,0.01892],"tcp_start":[0.49982,0.05289,0.0274],"tcp_to_object_dist_end":0.04312,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.50181,-0.15836,0.02611],"object_pos_start":[0.50182,-0.15836,0.02613],"object_to_goal_dist_end":0.00863,"object_to_goal_dist_start":0.00863,"object_z_max":0.02613,"peak_contact_force":29.28655,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":4.0,"raw_peak_contact_force":29.28655,"tcp_end":[0.49623,-0.1162,0.0189],"tcp_start":[0.49625,-0.11621,0.01892],"tcp_to_object_dist_end":0.04314,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":true}]}
```