## Search State

- **Seed**: 4
- **Iteration**: 3 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 2 | grasp → approach → align → descend → insert | — | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | position_control | force_threshold_switch | impedance_control | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | force_exceeded | 8 | 0.0843 | 0.92 | ❌ rejected |
| 1 | grasp → approach → align → descend → insert → release | — | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | position_control | force_threshold_switch | admittance_control | position_control | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | force_exceeded | pose_tolerance | 7 | 0.1090 | 0.93 | ❌ rejected |
| 0 | push → align → release → insert | impedance_motion | linear_cartesian | linear_cartesian | impedance_motion | impedance_control | position_control | admittance_control | impedance_control | time_limit | pose_tolerance | pose_tolerance | force_exceeded | 6 | 0.1391 | 0.96 | ✅ accepted |

**Proposal policy**: task_score is near-perfect (0.92). Preserve useful working parts and make only evidence-backed refinements. A HOLD is acceptable if you genuinely cannot find a better structure.

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

## Current Skill (Q=0.084) — your mutation base

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

- **Composite score**: 0.084
- **task_score** (E): 0.921
- **fitness_score**: 0.374  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.200
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.490

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| grasp_1 | 1.00 | 0.00 | 0.0089 |
| approach_1 | 1.00 | 0.00 | 0.0614 |
| align_1 | 1.00 | 0.00 | 0.0149 |
| descend_1 | 1.00 | 1.00 | 0.1715 |
| insert_1 | 0.00 | 1.00 | 0.0001 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| grasp_1 | grasp | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.496, -0.000, 0.292) | (0.504, -0.000, 0.340)→(0.501, -0.000, 0.332) | 0.260→0.252 | 0.00 / 0.000 | 0.000 | 0.000 |
| approach_1 | approach | 1.00 / step_budget | (0.496, -0.000, 0.292)→(0.514, 0.004, 0.236) | (0.501, -0.000, 0.332)→(0.521, 0.004, 0.276) | 0.252→0.197 | 0.00 / 0.000 | 0.000 | 0.000 |
| align_1 | align | 1.00 / step_budget | (0.514, 0.004, 0.236)→(0.513, 0.007, 0.226) | (0.521, 0.004, 0.276)→(0.520, 0.007, 0.265) | 0.197→0.187 | 0.00 / 0.000 | 0.000 | 0.000 |
| descend_1 | descend | 1.00 / force_exceeded | (0.513, 0.007, 0.226)→(0.513, 0.006, 0.055) | (0.520, 0.007, 0.265)→(0.525, 0.006, 0.093) | 0.187→0.031 | 1.00 / 1.000 | 80.889 | 0.000 |
| insert_1 | insert | 0.00 / guard_failure | (0.513, 0.006, 0.055)→(0.513, 0.006, 0.054) | (0.525, 0.006, 0.093)→(0.525, 0.006, 0.092) | 0.031→0.031 | 1.00 / 1.000 | 82.336 | 82.336 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.977
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.977
- phase_score: 0.011
- phase_breakdown.insertion_score: 0.003
- phase_breakdown.approach_goal_score: 0.030

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.398
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.977
- **Median Q (composite search score)**: 0.073
- **K-run variance**: 0.0003
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Parameters at upper bound**: align_1.lateral_offset_y
- **Final σ (mean)**: 0.373


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.33333,"average_solve_count":78.0,"average_success_count":78.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":-0.01473,"align_1.lateral_offset_y":0.01164,"approach_1.approach_speed":0.09533,"descend_1.descend_distance":0.19933,"descend_1.force_threshold":11.60034,"grasp_1.pre_grasp_offset_z":0.11615,"insert_1.insertion_depth":0.04697,"insert_1.insertion_force":13.75601},"optimized_scores":{"best_composite_score":0.07248,"best_fitness_score":0.36248,"best_task_score":0.89272},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":1.0,"contact_point_centroid":[0.53747,0.00517,0.04991],"force_p95":93.62809,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":93.62809,"mean_force":93.62809,"phase_index":4.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.52312,0.00516,0.05419]}],"total_contact_groups":1},"final_pose_error":0.02476,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.53544,0.00091,0.025],"final_tcp_position":[0.52314,0.00515,0.05409],"realised_fixture_position":[0.53544,0.00091,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.53544,0.00091,0.08]},"peak_contact_force":93.62809,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50108,-3e-05,0.33212],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.25212,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.49623,-4e-05,0.29241],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":246.0,"n_steps_budget":600.0,"object_pos_end":[0.53226,0.00073,0.27421],"object_pos_start":[0.50108,-3e-05,0.33212],"object_to_goal_dist_end":0.19687,"object_to_goal_dist_start":0.25212,"object_z_max":0.33212,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach_goal","tcp_end":[0.52677,0.00071,0.23459],"tcp_start":[0.49623,-4e-05,0.29241],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":119.0,"n_steps_budget":600.0,"object_pos_end":[0.52616,0.0094,0.26576],"object_pos_start":[0.53226,0.00073,0.27421],"object_to_goal_dist_end":0.18783,"object_to_goal_dist_start":0.19687,"object_z_max":0.27421,"peak_contact_force":0.0,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach_goal","tcp_end":[0.51971,0.00937,0.22628],"tcp_start":[0.52677,0.00071,0.23459],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":864.0,"n_steps_budget":1000.0,"object_pos_end":[0.5348,0.00518,0.09245],"object_pos_start":[0.52616,0.0094,0.26576],"object_to_goal_dist_end":0.03732,"object_to_goal_dist_start":0.18783,"object_z_max":0.26576,"peak_contact_force":73.82042,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach_goal","tcp_end":[0.52312,0.00516,0.05419],"tcp_start":[0.51971,0.00937,0.22628],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.53482,0.00517,0.09235],"object_pos_start":[0.5348,0.00518,0.09245],"object_to_goal_dist_end":0.0373,"object_to_goal_dist_start":0.03732,"object_z_max":0.09245,"peak_contact_force":93.62809,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":1.0,"raw_peak_contact_force":93.62809,"subtask_id":"insertion","tcp_end":[0.52314,0.00515,0.05409],"tcp_start":[0.52312,0.00516,0.05419],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `82356f74d11e1888d903e80aabfa97b50f0a1f9374ab8997097863e47a04dcc6`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.32468,"average_solve_count":77.0,"average_success_count":77.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":-0.00653,"align_1.lateral_offset_y":-0.01488,"approach_1.approach_speed":0.09734,"descend_1.descend_distance":0.17335,"descend_1.force_threshold":17.07559,"grasp_1.pre_grasp_offset_z":0.08049,"insert_1.insertion_depth":0.06595,"insert_1.insertion_force":21.35255},"optimized_scores":{"best_composite_score":0.0728,"best_fitness_score":0.3628,"best_task_score":0.89296},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":1.0,"contact_point_centroid":[0.52994,0.01795,0.04994],"force_p95":78.9709,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":78.9709,"mean_force":78.9709,"phase_index":4.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.51567,0.01799,0.05449]}],"total_contact_groups":1},"final_pose_error":0.04184,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.5244,0.02464,0.025],"final_tcp_position":[0.51566,0.01799,0.05442],"realised_fixture_position":[0.5244,0.02464,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.5244,0.02464,0.08]},"peak_contact_force":89.87603,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50108,-3e-05,0.33212],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.25212,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.49623,-4e-05,0.29241],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":235.0,"n_steps_budget":600.0,"object_pos_end":[0.52337,0.02041,0.27474],"object_pos_start":[0.50108,-3e-05,0.33212],"object_to_goal_dist_end":0.1972,"object_to_goal_dist_start":0.25212,"object_z_max":0.33212,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach_goal","tcp_end":[0.51715,0.02039,0.23523],"tcp_start":[0.49623,-4e-05,0.29241],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":164.0,"n_steps_budget":600.0,"object_pos_end":[0.52187,0.01126,0.26509],"object_pos_start":[0.52337,0.02041,0.27474],"object_to_goal_dist_end":0.18672,"object_to_goal_dist_start":0.1972,"object_z_max":0.27474,"peak_contact_force":0.0,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach_goal","tcp_end":[0.51501,0.01123,0.22568],"tcp_start":[0.51715,0.02039,0.23523],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":853.0,"n_steps_budget":1000.0,"object_pos_end":[0.52795,0.01799,0.09256],"object_pos_start":[0.52187,0.01126,0.26509],"object_to_goal_dist_end":0.03553,"object_to_goal_dist_start":0.18672,"object_z_max":0.26509,"peak_contact_force":89.87603,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach_goal","tcp_end":[0.51567,0.01799,0.05449],"tcp_start":[0.51501,0.01123,0.22568],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.52794,0.01799,0.09249],"object_pos_start":[0.52795,0.01799,0.09256],"object_to_goal_dist_end":0.0355,"object_to_goal_dist_start":0.03553,"object_z_max":0.09256,"peak_contact_force":78.9709,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":1.0,"raw_peak_contact_force":78.9709,"subtask_id":"insertion","tcp_end":[0.51566,0.01799,0.05442],"tcp_start":[0.51567,0.01799,0.05449],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `4fedbe547233117d2a5522e0e6da389f32d172824e1a5c898bb2e8c1e5f99b78`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.20779,"average_solve_count":77.0,"average_success_count":77.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":0.00495,"align_1.lateral_offset_y":0.015,"approach_1.approach_speed":0.08493,"descend_1.descend_distance":0.18722,"descend_1.force_threshold":16.39106,"grasp_1.pre_grasp_offset_z":0.06519,"insert_1.insertion_depth":0.07473,"insert_1.insertion_force":10.80196},"optimized_scores":{"best_composite_score":0.10762,"best_fitness_score":0.39762,"best_task_score":0.97749},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":1.0,"contact_point_centroid":[0.51352,-0.00586,0.04996],"force_p95":74.40873,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":74.40873,"mean_force":74.40873,"phase_index":4.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49942,-0.00579,0.05502]}],"total_contact_groups":1},"final_pose_error":0.05028,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.50305,-0.01254,0.025],"final_tcp_position":[0.4994,-0.0058,0.05496],"realised_fixture_position":[0.50305,-0.01254,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.50305,-0.01254,0.08]},"peak_contact_force":78.9709,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50108,-3e-05,0.33212],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.25212,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.49623,-4e-05,0.29241],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":185.0,"n_steps_budget":600.0,"object_pos_end":[0.50662,-0.00984,0.27796],"object_pos_start":[0.50108,-3e-05,0.33212],"object_to_goal_dist_end":0.19831,"object_to_goal_dist_start":0.25212,"object_z_max":0.33212,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach_goal","tcp_end":[0.49911,-0.00982,0.23867],"tcp_start":[0.49623,-4e-05,0.29241],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":375.0,"n_steps_budget":600.0,"object_pos_end":[0.51188,0.00104,0.26519],"object_pos_start":[0.50662,-0.00984,0.27796],"object_to_goal_dist_end":0.18558,"object_to_goal_dist_start":0.19831,"object_z_max":0.27796,"peak_contact_force":0.0,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach_goal","tcp_end":[0.50416,0.001,0.22595],"tcp_start":[0.49911,-0.00982,0.23867],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":841.0,"n_steps_budget":1000.0,"object_pos_end":[0.51305,-0.00576,0.09263],"object_pos_start":[0.51188,0.00104,0.26519],"object_to_goal_dist_end":0.01905,"object_to_goal_dist_start":0.18558,"object_z_max":0.26519,"peak_contact_force":78.9709,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach_goal","tcp_end":[0.49942,-0.00579,0.05502],"tcp_start":[0.50416,0.001,0.22595],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.51303,-0.00577,0.09256],"object_pos_start":[0.51305,-0.00576,0.09263],"object_to_goal_dist_end":0.019,"object_to_goal_dist_start":0.01905,"object_z_max":0.09263,"peak_contact_force":74.40873,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":1.0,"raw_peak_contact_force":74.40873,"subtask_id":"insertion","tcp_end":[0.4994,-0.0058,0.05496],"tcp_start":[0.49942,-0.00579,0.05502],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
```