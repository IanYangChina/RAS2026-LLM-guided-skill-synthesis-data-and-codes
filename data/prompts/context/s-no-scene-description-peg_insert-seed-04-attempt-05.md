## Search State

- **Seed**: 4
- **Iteration**: 6 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 5 | approach → align → descend → insert | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | force_exceeded | 9 | -0.0908 | 0.85 | ❌ rejected |
| 4 | push → align → release → insert | impedance_motion | linear_cartesian | linear_cartesian | impedance_motion | impedance_control | position_control | admittance_control | impedance_control | time_limit | pose_tolerance | pose_tolerance | force_exceeded | 6 | 0.1390 | 0.96 | ❌ rejected |
| 3 | push → align → release → insert | impedance_motion | linear_cartesian | — | impedance_motion | impedance_control | position_control | position_control | impedance_control | time_limit | pose_tolerance | pose_tolerance | force_exceeded | 6 | 0.6859 | 0.95 | ❌ rejected |
| 2 | grasp → approach → align → descend → insert | — | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | position_control | force_threshold_switch | impedance_control | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | force_exceeded | 8 | 0.0843 | 0.92 | ❌ rejected |
| 1 | grasp → approach → align → descend → insert → release | — | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | position_control | force_threshold_switch | admittance_control | position_control | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | force_exceeded | pose_tolerance | 7 | 0.1090 | 0.93 | ❌ rejected |

**Proposal policy**: task_score is 0.85 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

- Task name: peg_insert
- Goal tolerance: 0.02 m
- Expressivity sigma: 0.15 m
- Expressivity threshold: 0.3
- Force limit: 40.0 N
- Primary evaluation target: **insertion depth ratio (axial progress into hole)**

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
| `fixture` | offset from fixture pose | approach/contact targets near fixture |

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

## Current Skill (Q=-0.091) — your mutation base

```yaml
skill: peg_insert
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

- **Composite score**: -0.091
- **task_score** (E): 0.852
- **fitness_score**: 0.419  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.510

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 0.33 | 1.00 | 0.1033 |
| align_1 | 0.00 | 1.00 | 0.0319 |
| descend_1 | 0.00 | 0.33 | 0.0002 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 0.33 / step_budget | (0.500, -0.000, 0.301)→(0.473, 0.003, 0.201) | (0.504, -0.000, 0.340)→(0.507, 0.003, 0.180) | 0.260→0.101 | 1.00 / 1.000 | 266.187 | 1079.897 |
| align_1 | align | 0.00 / step_budget | (0.473, 0.003, 0.201)→(0.490, 0.007, 0.179) | (0.507, 0.003, 0.180)→(0.525, 0.010, 0.160) | 0.101→0.088 | 1.00 / 1.000 | 305.775 | 1004.195 |
| descend_1 | descend | 0.00 / guard_failure | (0.490, 0.007, 0.179)→(0.490, 0.007, 0.179) | (0.525, 0.010, 0.160)→(0.525, 0.009, 0.160) | 0.088→0.088 | 0.33 / 0.333 | 75.267 | 241.375 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.854
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.854
- phase_score: 0.156
- phase_breakdown.reach_goal_score: 0.156

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.435
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.854
- **Median Q (composite search score)**: -0.095
- **K-run variance**: 0.0001
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.268


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `1c06d48834291abac995c6cc1d2cd84f840e8dd85a042a042b29bb3e8b43f340`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `a5dd99a2832e295b96a2d483dc6e44525a65c5240d3c756ec4d63dfbfe5237b3`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":6.0,"average_failure_rate":0.09524,"average_mean_iterations":26.57143,"average_solve_count":63.0,"average_success_count":57.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.align_offset_z":0.02807,"align_1.lateral_offset_x":-0.0029,"align_1.lateral_offset_y":0.00821,"approach_1.approach_height":0.10216,"approach_1.approach_speed":0.06941,"descend_1.descend_force":3.74477,"descend_1.descend_speed":0.04785,"insert_1.insertion_depth":0.09133,"insert_1.insertion_force":5.09977},"optimized_scores":{"best_composite_score":-0.09541,"best_fitness_score":0.41459,"best_task_score":0.85119},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link7","contact_count":43.0,"contact_point_centroid":[0.56839,0.00219,0.07766],"force_p95":693.25679,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1184.02261,"mean_force":125.31297,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.44343,-0.00019,0.1071]},{"body_a":"peg_socket","body_b":"link6","contact_count":473.0,"contact_point_centroid":[0.59534,-0.00057,0.07981],"force_p95":351.50659,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":847.41316,"mean_force":260.99621,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.47207,0.0032,0.20391]},{"body_a":"peg_socket","body_b":"link6","contact_count":894.0,"contact_point_centroid":[0.59487,-0.00278,0.07977],"force_p95":279.34305,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":533.54919,"mean_force":233.10303,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.45861,0.00019,0.16882]},{"body_a":"peg_socket","body_b":"link7","contact_count":11.0,"contact_point_centroid":[0.53656,0.03133,0.07956],"force_p95":307.73106,"geom_a":"socket_collar_y1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":335.13706,"mean_force":197.40834,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4421,-6e-05,0.09047]},{"body_a":"peg_socket","body_b":"link7","contact_count":28.0,"contact_point_centroid":[0.53859,-0.02962,0.07688],"force_p95":225.2783,"geom_a":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":280.15208,"mean_force":26.90974,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.44272,-0.00016,0.09848]},{"body_a":"peg_socket","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.5954,0.01237,0.07991],"force_p95":225.80121,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":225.80121,"mean_force":225.80121,"phase_index":2.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49411,0.00148,0.18447]},{"body_a":"attachment","body_b":"peg_socket","contact_count":7.0,"contact_point_centroid":[0.47552,-1e-05,0.07973],"force_p95":0.0,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.44597,-1e-05,0.08708]}],"total_contact_groups":7},"final_pose_error":0.11225,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.53544,0.00091,0.025],"final_tcp_position":[0.49417,0.00142,0.18439],"realised_fixture_position":[0.53544,0.00091,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.53544,0.00091,0.08]},"peak_contact_force":1184.02261,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51752,0.00111,0.18925],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.11065,"object_to_goal_dist_start":0.26034,"object_z_max":0.34456,"peak_contact_force":226.40952,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":983.0,"raw_peak_contact_force":1184.02261,"subtask_id":"reach_goal","tcp_end":[0.485,0.00117,0.21255],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":512.0,"n_steps_budget":750.0,"object_pos_end":[0.52925,0.00407,0.16555],"object_pos_start":[0.51752,0.00111,0.18925],"object_to_goal_dist_end":0.0905,"object_to_goal_dist_start":0.11065,"object_z_max":0.1956,"peak_contact_force":251.6999,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":473.0,"raw_peak_contact_force":847.41316,"subtask_id":"reach_goal","tcp_end":[0.49411,0.00148,0.18447],"tcp_start":[0.485,0.00117,0.21255],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.52934,0.00408,0.16552],"object_pos_start":[0.52925,0.00407,0.16555],"object_to_goal_dist_end":0.09051,"object_to_goal_dist_start":0.0905,"object_z_max":0.16555,"peak_contact_force":225.80121,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1.0,"raw_peak_contact_force":225.80121,"subtask_id":"reach_goal","tcp_end":[0.49417,0.00142,0.18439],"tcp_start":[0.49411,0.00148,0.18447],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `82356f74d11e1888d903e80aabfa97b50f0a1f9374ab8997097863e47a04dcc6`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":1.0,"average_failure_rate":0.01887,"average_mean_iterations":11.92453,"average_solve_count":53.0,"average_success_count":52.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.align_offset_z":0.03124,"align_1.lateral_offset_x":-0.00743,"align_1.lateral_offset_y":-0.00185,"approach_1.approach_height":0.1235,"approach_1.approach_speed":0.0726,"descend_1.descend_force":3.86189,"descend_1.descend_speed":0.03996,"insert_1.insertion_depth":0.05474,"insert_1.insertion_force":18.56227},"optimized_scores":{"best_composite_score":-0.10212,"best_fitness_score":0.40788,"best_task_score":0.84957},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":7.0,"contact_point_centroid":[0.4647,0.003,0.07931],"force_p95":929.23735,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":973.36711,"mean_force":257.09072,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.45325,0.00298,0.09072]},{"body_a":"peg_socket","body_b":"link7","contact_count":56.0,"contact_point_centroid":[0.58426,0.03439,0.07985],"force_p95":764.25696,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":907.12499,"mean_force":381.3927,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49141,0.02902,0.18197]},{"body_a":"peg_socket","body_b":"link6","contact_count":469.0,"contact_point_centroid":[0.58431,0.0159,0.07984],"force_p95":330.45278,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":839.04082,"mean_force":260.45331,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.46393,0.0193,0.20098]},{"body_a":"peg_socket","body_b":"link7","contact_count":30.0,"contact_point_centroid":[0.54429,-0.00575,0.07766],"force_p95":689.83696,"geom_a":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":789.86348,"mean_force":241.05304,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.44824,0.00326,0.10251]},{"body_a":"peg_socket","body_b":"link7","contact_count":31.0,"contact_point_centroid":[0.55477,0.00245,0.078],"force_p95":233.86826,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":419.57094,"mean_force":174.70928,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.44826,0.00328,0.10312]},{"body_a":"peg_socket","body_b":"link6","contact_count":678.0,"contact_point_centroid":[0.58435,0.00646,0.07985],"force_p95":287.92953,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":345.58495,"mean_force":249.7128,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.45344,0.00912,0.16781]},{"body_a":"peg_socket","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.58439,0.05161,0.07998],"force_p95":146.05502,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":146.05502,"mean_force":146.05502,"phase_index":2.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.48657,0.0361,0.18156]}],"total_contact_groups":7},"final_pose_error":0.10921,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.5244,0.02464,0.025],"final_tcp_position":[0.48647,0.03613,0.18176],"realised_fixture_position":[0.5244,0.02464,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.5244,0.02464,0.08]},"peak_contact_force":973.36711,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":813.0,"n_steps_budget":900.0,"object_pos_end":[0.50147,0.0156,0.17911],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.10034,"object_to_goal_dist_start":0.26034,"object_z_max":0.34454,"peak_contact_force":267.39352,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":746.0,"raw_peak_contact_force":973.36711,"subtask_id":"reach_goal","tcp_end":[0.46695,0.0159,0.19932],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":572.0,"n_steps_budget":660.0,"object_pos_end":[0.52169,0.04078,0.16299],"object_pos_start":[0.50147,0.0156,0.17911],"object_to_goal_dist_end":0.09498,"object_to_goal_dist_start":0.10034,"object_z_max":0.19346,"peak_contact_force":406.24018,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":525.0,"raw_peak_contact_force":907.12499,"subtask_id":"reach_goal","tcp_end":[0.48657,0.0361,0.18156],"tcp_start":[0.46695,0.0159,0.19932],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.52157,0.04099,0.16321],"object_pos_start":[0.52169,0.04078,0.16299],"object_to_goal_dist_end":0.09524,"object_to_goal_dist_start":0.09498,"object_z_max":0.16299,"peak_contact_force":0.0,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1.0,"raw_peak_contact_force":146.05502,"subtask_id":"reach_goal","tcp_end":[0.48647,0.03613,0.18176],"tcp_start":[0.48657,0.0361,0.18156],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `4fedbe547233117d2a5522e0e6da389f32d172824e1a5c898bb2e8c1e5f99b78`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":8.15094,"average_solve_count":53.0,"average_success_count":53.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.align_offset_z":0.01569,"align_1.lateral_offset_x":-0.00732,"align_1.lateral_offset_y":0.00624,"approach_1.approach_height":0.08127,"approach_1.approach_speed":0.09971,"descend_1.descend_force":2.15269,"descend_1.descend_speed":0.01969,"insert_1.insertion_depth":0.1181,"insert_1.insertion_force":11.71914},"optimized_scores":{"best_composite_score":-0.07494,"best_fitness_score":0.43506,"best_task_score":0.85395},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link7","contact_count":65.0,"contact_point_centroid":[0.56297,-0.0141,0.0799],"force_p95":604.8416,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1258.04666,"mean_force":389.80643,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.48769,-0.01564,0.18167]},{"body_a":"attachment","body_b":"peg_socket","contact_count":12.0,"contact_point_centroid":[0.46114,-0.00183,0.07866],"force_p95":1033.53191,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1082.30032,"mean_force":314.39041,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.45636,-0.00175,0.09153]},{"body_a":"peg_socket","body_b":"link6","contact_count":232.0,"contact_point_centroid":[0.56298,-0.00776,0.07984],"force_p95":309.39336,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":897.89364,"mean_force":286.96764,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.45904,-0.00664,0.18185]},{"body_a":"peg_socket","body_b":"link7","contact_count":488.0,"contact_point_centroid":[0.56211,-0.00109,0.0798],"force_p95":320.57215,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":748.20378,"mean_force":271.51502,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4558,-0.00372,0.15801]},{"body_a":"peg_socket","body_b":"link6","contact_count":493.0,"contact_point_centroid":[0.563,-0.00847,0.07992],"force_p95":308.22991,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":411.36716,"mean_force":279.36741,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.46571,-0.00909,0.19524]},{"body_a":"peg_socket","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.56304,-0.01551,0.07997],"force_p95":352.27006,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":352.27006,"mean_force":352.27006,"phase_index":2.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49068,-0.01523,0.17126]}],"total_contact_groups":6},"final_pose_error":0.09207,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.50305,-0.01254,0.025],"final_tcp_position":[0.49074,-0.01546,0.1712],"realised_fixture_position":[0.50305,-0.01254,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.50305,-0.01254,0.08]},"peak_contact_force":1258.04666,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":813.0,"n_steps_budget":900.0,"object_pos_end":[0.50055,-0.00747,0.17131],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.09161,"object_to_goal_dist_start":0.26034,"object_z_max":0.34453,"peak_contact_force":304.75883,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":732.0,"raw_peak_contact_force":1082.30032,"subtask_id":"reach_goal","tcp_end":[0.4667,-0.00777,0.19262],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":602.0,"n_steps_budget":660.0,"object_pos_end":[0.52549,-0.01631,0.15159],"object_pos_start":[0.50055,-0.00747,0.17131],"object_to_goal_dist_end":0.07773,"object_to_goal_dist_start":0.09161,"object_z_max":0.1826,"peak_contact_force":259.38361,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":558.0,"raw_peak_contact_force":1258.04666,"subtask_id":"reach_goal","tcp_end":[0.49068,-0.01523,0.17126],"tcp_start":[0.4667,-0.00777,0.19262],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.52559,-0.01662,0.1516],"object_pos_start":[0.52549,-0.01631,0.15159],"object_to_goal_dist_end":0.07783,"object_to_goal_dist_start":0.07773,"object_z_max":0.15159,"peak_contact_force":0.0,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1.0,"raw_peak_contact_force":352.27006,"subtask_id":"reach_goal","tcp_end":[0.49074,-0.01546,0.1712],"tcp_start":[0.49068,-0.01523,0.17126],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
```