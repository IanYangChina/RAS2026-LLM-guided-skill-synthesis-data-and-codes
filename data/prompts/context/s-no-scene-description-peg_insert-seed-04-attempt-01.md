## Search State

- **Seed**: 4
- **Iteration**: 2 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 1 | grasp → approach → align → descend → insert → release | — | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | position_control | force_threshold_switch | admittance_control | position_control | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | force_exceeded | pose_tolerance | 7 | 0.1090 | 0.93 | ❌ rejected |
| 0 | push → align → release → insert | impedance_motion | linear_cartesian | linear_cartesian | impedance_motion | impedance_control | position_control | admittance_control | impedance_control | time_limit | pose_tolerance | pose_tolerance | force_exceeded | 6 | 0.1391 | 0.96 | ✅ accepted |

**Proposal policy**: task_score is near-perfect (0.93). Preserve useful working parts and make only evidence-backed refinements. A HOLD is acceptable if you genuinely cannot find a better structure.

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

## Current Skill (Q=0.109) — your mutation base

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

- **Composite score**: 0.109
- **task_score** (E): 0.928
- **fitness_score**: 0.379  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.200
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.470

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| grasp_1 | 1.00 | 0.00 | 0.0089 |
| approach_1 | 1.00 | 0.00 | 0.0614 |
| align_1 | 1.00 | 0.00 | 0.0047 |
| descend_1 | 0.67 | 1.00 | 0.1723 |
| insert_1 | 0.00 | 1.00 | 0.0001 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| grasp_1 | grasp | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.496, -0.000, 0.292) | (0.504, -0.000, 0.340)→(0.501, -0.000, 0.332) | 0.260→0.252 | 0.00 / 0.000 | 0.000 | 0.000 |
| approach_1 | approach | 1.00 / step_budget | (0.496, -0.000, 0.292)→(0.514, 0.004, 0.236) | (0.501, -0.000, 0.332)→(0.515, 0.004, 0.276) | 0.252→0.198 | 0.00 / 0.000 | 0.000 | 0.000 |
| align_1 | align | 1.00 / step_budget | (0.514, 0.004, 0.236)→(0.516, 0.005, 0.232) | (0.515, 0.004, 0.276)→(0.516, 0.005, 0.272) | 0.198→0.193 | 0.00 / 0.000 | 0.000 | 0.000 |
| descend_1 | descend | 0.67 / force_exceeded | (0.516, 0.005, 0.232)→(0.509, 0.003, 0.060) | (0.516, 0.005, 0.272)→(0.510, 0.003, 0.100) | 0.193→0.026 | 1.00 / 1.000 | 1347.467 | 30.151 |
| insert_1 | insert | 0.00 / guard_failure | (0.508, -0.004, 0.065)→(0.508, -0.004, 0.065) | (0.509, -0.004, 0.105)→(0.509, -0.004, 0.105) | 0.028→0.028 | 1.00 / 1.000 | 77.283 | 77.283 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.963
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.963
- phase_score: 0.013
- phase_breakdown.insertion_score: 0.006
- phase_breakdown.approach_goal_score: 0.027

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.393
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.963
- **Median Q (composite search score)**: 0.105
- **K-run variance**: 0.0001
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.466


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.0,"average_solve_count":100.0,"average_success_count":100.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.align_offset_x":-0.00623,"align_1.align_offset_y":-0.00118,"approach_1.approach_speed":0.03343,"descend_1.descend_distance":0.11912,"descend_1.force_threshold":10.87137,"insert_1.insertion_depth":0.06244,"insert_1.insertion_force":9.29463},"optimized_scores":{"best_composite_score":0.10476,"best_fitness_score":0.37476,"best_task_score":0.91279},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":1.0,"contact_point_centroid":[0.50544,0.003,0.07997],"force_p95":76.53362,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":76.53362,"mean_force":76.53362,"phase_index":4.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.51853,0.0005,0.07979]}],"total_contact_groups":1},"final_pose_error":0.05692,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.53544,0.00091,0.025],"final_tcp_position":[0.51851,0.0005,0.0797],"realised_fixture_position":[0.53544,0.00091,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.53544,0.00091,0.08]},"peak_contact_force":3892.30136,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50108,-3e-05,0.33212],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.25212,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.49623,-4e-05,0.29241],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":268.0,"n_steps_budget":1000.0,"object_pos_end":[0.52714,0.00073,0.27475],"object_pos_start":[0.50108,-3e-05,0.33212],"object_to_goal_dist_end":0.19663,"object_to_goal_dist_start":0.25212,"object_z_max":0.33212,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach_goal","tcp_end":[0.52665,0.00073,0.23475],"tcp_start":[0.49623,-4e-05,0.29241],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":20.0,"n_steps_budget":600.0,"object_pos_end":[0.52655,0.00061,0.2722],"object_pos_start":[0.52714,0.00073,0.27475],"object_to_goal_dist_end":0.19403,"object_to_goal_dist_start":0.19663,"object_z_max":0.27475,"peak_contact_force":0.0,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach_goal","tcp_end":[0.52602,0.00061,0.23221],"tcp_start":[0.52665,0.00073,0.23475],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":711.0,"n_steps_budget":1000.0,"object_pos_end":[0.519,0.00051,0.11979],"object_pos_start":[0.52655,0.00061,0.2722],"object_to_goal_dist_end":0.0441,"object_to_goal_dist_start":0.19403,"object_z_max":0.2722,"peak_contact_force":3892.30136,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach_goal","tcp_end":[0.51853,0.0005,0.07979],"tcp_start":[0.52602,0.00061,0.23221],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.51898,0.0005,0.11969],"object_pos_start":[0.519,0.00051,0.11979],"object_to_goal_dist_end":0.044,"object_to_goal_dist_start":0.0441,"object_z_max":0.11979,"peak_contact_force":76.53362,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":1.0,"raw_peak_contact_force":76.53362,"subtask_id":"insertion","tcp_end":[0.51851,0.0005,0.0797],"tcp_start":[0.51853,0.0005,0.07979],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `82356f74d11e1888d903e80aabfa97b50f0a1f9374ab8997097863e47a04dcc6`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.4557,"average_solve_count":79.0,"average_success_count":79.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.align_offset_x":0.00176,"align_1.align_offset_y":-0.00582,"approach_1.approach_speed":0.12504,"descend_1.descend_distance":0.11995,"descend_1.force_threshold":16.05147,"insert_1.insertion_depth":0.0653,"insert_1.insertion_force":22.4565},"optimized_scores":{"best_composite_score":0.09938,"best_fitness_score":0.36938,"best_task_score":0.9084},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":1.0,"contact_point_centroid":[0.52586,0.01536,0.04998],"force_p95":90.45415,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":90.45415,"mean_force":90.45415,"phase_index":3.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51088,0.01477,0.05013]}],"total_contact_groups":1},"final_pose_error":0.0888,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.5244,0.02464,0.025],"final_tcp_position":[0.51088,0.01477,0.04997],"realised_fixture_position":[0.5244,0.02464,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.5244,0.02464,0.08]},"peak_contact_force":90.45415,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50108,-3e-05,0.33212],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.25212,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.49623,-4e-05,0.29241],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":233.0,"n_steps_budget":600.0,"object_pos_end":[0.51779,0.02045,0.27528],"object_pos_start":[0.50108,-3e-05,0.33212],"object_to_goal_dist_end":0.19715,"object_to_goal_dist_start":0.25212,"object_z_max":0.33212,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach_goal","tcp_end":[0.51729,0.02043,0.23528],"tcp_start":[0.49623,-4e-05,0.29241],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":20.0,"n_steps_budget":600.0,"object_pos_end":[0.51824,0.02039,0.27269],"object_pos_start":[0.51779,0.02045,0.27528],"object_to_goal_dist_end":0.19462,"object_to_goal_dist_start":0.19715,"object_z_max":0.27528,"peak_contact_force":0.0,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach_goal","tcp_end":[0.51774,0.02036,0.23269],"tcp_start":[0.51729,0.02043,0.23528],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":878.0,"n_steps_budget":1000.0,"object_pos_end":[0.51133,0.01478,0.08997],"object_pos_start":[0.51824,0.02039,0.27269],"object_to_goal_dist_end":0.02112,"object_to_goal_dist_start":0.19462,"object_z_max":0.27269,"peak_contact_force":90.45415,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1.0,"raw_peak_contact_force":90.45415,"subtask_id":"approach_goal","tcp_end":[0.51088,0.01477,0.04997],"tcp_start":[0.51774,0.02036,0.23269],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `4fedbe547233117d2a5522e0e6da389f32d172824e1a5c898bb2e8c1e5f99b78`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.20238,"average_solve_count":84.0,"average_success_count":84.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.align_offset_x":0.00997,"align_1.align_offset_y":0.00848,"approach_1.approach_speed":0.05729,"descend_1.descend_distance":0.11999,"descend_1.force_threshold":15.94125,"insert_1.insertion_depth":0.02101,"insert_1.insertion_force":13.69514},"optimized_scores":{"best_composite_score":0.1228,"best_fitness_score":0.3928,"best_task_score":0.96312},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":1.0,"contact_point_centroid":[0.51281,-0.00781,0.04998],"force_p95":78.03244,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":78.03244,"mean_force":78.03244,"phase_index":4.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49781,-0.00774,0.05012]}],"total_contact_groups":1},"final_pose_error":0.01756,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.50305,-0.01254,0.025],"final_tcp_position":[0.4978,-0.00775,0.05002],"realised_fixture_position":[0.50305,-0.01254,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.50305,-0.01254,0.08]},"peak_contact_force":78.03244,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50108,-3e-05,0.33212],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.25212,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.49623,-4e-05,0.29241],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":187.0,"n_steps_budget":720.0,"object_pos_end":[0.49962,-0.00981,0.27852],"object_pos_start":[0.50108,-3e-05,0.33212],"object_to_goal_dist_end":0.19876,"object_to_goal_dist_start":0.25212,"object_z_max":0.33212,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach_goal","tcp_end":[0.49903,-0.00981,0.23852],"tcp_start":[0.49623,-4e-05,0.29241],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":51.0,"n_steps_budget":600.0,"object_pos_end":[0.50422,-0.00727,0.27134],"object_pos_start":[0.49962,-0.00981,0.27852],"object_to_goal_dist_end":0.19153,"object_to_goal_dist_start":0.19876,"object_z_max":0.27852,"peak_contact_force":0.0,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach_goal","tcp_end":[0.5037,-0.00727,0.23135],"tcp_start":[0.49903,-0.00981,0.23852],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":892.0,"n_steps_budget":1000.0,"object_pos_end":[0.49825,-0.00774,0.09012],"object_pos_start":[0.50422,-0.00727,0.27134],"object_to_goal_dist_end":0.01286,"object_to_goal_dist_start":0.19153,"object_z_max":0.27134,"peak_contact_force":59.64482,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach_goal","tcp_end":[0.49781,-0.00774,0.05012],"tcp_start":[0.5037,-0.00727,0.23135],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.49824,-0.00775,0.09001],"object_pos_start":[0.49825,-0.00774,0.09012],"object_to_goal_dist_end":0.01278,"object_to_goal_dist_start":0.01286,"object_z_max":0.09012,"peak_contact_force":78.03244,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":1.0,"raw_peak_contact_force":78.03244,"subtask_id":"insertion","tcp_end":[0.4978,-0.00775,0.05002],"tcp_start":[0.49781,-0.00774,0.05012],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
```