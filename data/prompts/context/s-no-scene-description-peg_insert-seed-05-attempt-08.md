## Search State

- **Seed**: 5
- **Iteration**: 9 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 8 | grasp → approach → insert → release → retract | — | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | impedance_control | position_control | position_control | grasp_success | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 5 | 0.2855 | 0.86 | ❌ rejected |
| 7 | approach → insert → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | impedance_control | position_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 5 | 0.4161 | 0.89 | ❌ rejected |
| 6 | push → release → pull → release → release → grasp → retract | linear_cartesian | — | arc_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | impedance_control | admittance_control | position_control | position_control | position_control | time_limit | time_limit | time_limit | pose_tolerance | time_limit | time_limit | pose_tolerance | 3 | 0.6642 | 0.96 | ❌ rejected |
| 5 | approach → insert → retract | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | 5 | 0.4773 | 0.86 | ❌ rejected |
| 4 | push → insert → retract | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | 5 | 0.9106 | 0.86 | ❌ rejected |

**Proposal policy**: task_score is 0.86 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.286) — your mutation base

```yaml
skill: peg_insert
skill_type: arm_gripper
phases:
- id: push_1
  type: push
  generator: linear_cartesian
  control: position_control
  termination: time_limit
  parameters:
    push_depth:
      type: scalar
      range:
      - 0.01
      - 0.1
- id: release_1
  type: release
  control: position_control
  termination: time_limit
  end_effector_action: open
- id: pull_1
  type: pull
  generator: arc_cartesian
  control: impedance_control
  termination: time_limit
  parameters:
    pull_distance:
      type: scalar
      range:
      - 0.02
      - 0.2
- id: release_2
  type: release
  generator: linear_cartesian
  control: admittance_control
  termination: pose_tolerance
  end_effector_action: open
- id: release_3
  type: release
  generator: linear_cartesian
  control: position_control
  termination: time_limit
  end_effector_action: open
- id: grasp_1
  type: grasp
  control: position_control
  termination: time_limit
  end_effector_action: force_grasp
- id: retract_1
  type: retract
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1

```

## Design Metrics

- **Composite score**: 0.286
- **task_score** (E): 0.860
- **fitness_score**: 0.426  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.200
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.340

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| grasp_1 | 1.00 | 0.00 | 0.0000 |
| approach_1 | 0.33 | 1.00 | 0.1045 |
| insert_1 | 1.00 | 1.00 | 0.0001 |
| release_1 | 1.00 | 1.00 | 0.0005 |
| retract_1 | 1.00 | 0.00 | 0.0478 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| grasp_1 | grasp | 1.00 / step_budget | (0.496, -0.000, 0.292)→(0.496, -0.000, 0.292) | (0.504, -0.000, 0.340)→(0.501, -0.000, 0.332) | 0.260→0.252 | 0.00 / 0.000 | 0.000 | 0.000 |
| approach_1 | approach | 0.33 / step_budget | (0.496, -0.000, 0.292)→(0.466, 0.008, 0.194) | (0.501, -0.000, 0.332)→(0.501, 0.009, 0.174) | 0.252→0.095 | 1.00 / 1.000 | 301.237 | 1096.232 |
| insert_1 | insert | 1.00 / force_exceeded | (0.466, 0.008, 0.194)→(0.466, 0.008, 0.194) | (0.501, 0.009, 0.174)→(0.501, 0.009, 0.174) | 0.095→0.095 | 1.00 / 1.000 | 331.517 | 331.517 |
| release_1 | release | 1.00 / step_budget | (0.466, 0.008, 0.194)→(0.467, 0.008, 0.194) | (0.501, 0.009, 0.174)→(0.501, 0.009, 0.174) | 0.095→0.095 | 1.00 / 1.000 | 65.515 | 274.998 |
| retract_1 | retract | 1.00 / step_budget | (0.467, 0.008, 0.194)→(0.508, 0.020, 0.210) | (0.501, 0.009, 0.174)→(0.543, 0.020, 0.190) | 0.095→0.122 | 0.00 / 0.000 | 0.000 | 93.911 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.860
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.860
- phase_score: 0.152
- phase_breakdown.retract_above_hole_score: 0.585
- phase_breakdown.insertion_progress_score: 0.000
- phase_breakdown.reach_above_hole_score: 0.176

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.435
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.868
- **Median Q (composite search score)**: 0.281
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.258


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `5e5af3f51d5f63e3a348998ea00f94a7255959965642a40069d0a7b5ef8ede34`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `cc7f64fba434a86728ba6288ab9746a03660fc43702ba486c544717f06e4937d`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":6.8913,"average_solve_count":46.0,"average_success_count":46.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.10206,"insert_1.insertion_depth":0.17958,"insert_1.insertion_force_threshold":25.29627,"release_1.release_duration":0.45093,"retract_1.retract_speed":0.07239},"optimized_scores":{"best_composite_score":0.27967,"best_fitness_score":0.41967,"best_task_score":0.86761},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":15.0,"contact_point_centroid":[0.46771,0.00294,0.07798],"force_p95":1056.67491,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1100.54806,"mean_force":257.99564,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.46237,0.0029,0.08992]},{"body_a":"peg_socket","body_b":"link7","contact_count":187.0,"contact_point_centroid":[0.57855,0.00907,0.07959],"force_p95":387.11418,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":700.50032,"mean_force":259.09867,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.46366,0.00506,0.1387]},{"body_a":"peg_socket","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.58429,0.01475,0.07981],"force_p95":348.73667,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":348.73667,"mean_force":348.73667,"phase_index":2.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.47554,0.01641,0.19535]},{"body_a":"peg_socket","body_b":"link6","contact_count":385.0,"contact_point_centroid":[0.58434,0.0105,0.07981],"force_p95":301.98498,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":346.6976,"mean_force":255.22116,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.46158,0.01109,0.17099]},{"body_a":"peg_socket","body_b":"link6","contact_count":199.0,"contact_point_centroid":[0.58439,0.01461,0.07998],"force_p95":90.86576,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":337.60879,"mean_force":70.25914,"phase_index":3.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.47587,0.01629,0.19606]},{"body_a":"peg_socket","body_b":"link6","contact_count":3.0,"contact_point_centroid":[0.58439,0.0146,0.07999],"force_p95":68.56958,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":70.28247,"mean_force":51.06635,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.47596,0.01628,0.19608]},{"body_a":"peg_socket","body_b":"link7","contact_count":14.0,"contact_point_centroid":[0.55414,-0.00542,0.07966],"force_p95":0.0,"geom_a":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.45987,0.0029,0.0955]}],"total_contact_groups":7},"final_pose_error":0.015,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.5244,0.02464,0.025],"final_tcp_position":[0.52085,0.03118,0.21697],"realised_fixture_position":[0.5244,0.02464,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.5244,0.02464,0.08]},"peak_contact_force":1100.54806,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.50108,-3e-05,0.33212],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.25212,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.49623,-4e-05,0.29241],"tcp_start":[0.49623,-4e-05,0.29241],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":663.0,"n_steps_budget":750.0,"object_pos_end":[0.50992,0.01676,0.17492],"object_pos_start":[0.50108,-3e-05,0.33211],"object_to_goal_dist_end":0.0969,"object_to_goal_dist_start":0.25212,"object_z_max":0.3362,"peak_contact_force":319.74227,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":601.0,"raw_peak_contact_force":1100.54806,"subtask_id":"reach_above_hole","tcp_end":[0.47554,0.01641,0.19535],"tcp_start":[0.49623,-4e-05,0.29241],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.50998,0.01676,0.17499],"object_pos_start":[0.50992,0.01676,0.17492],"object_to_goal_dist_end":0.09698,"object_to_goal_dist_start":0.0969,"object_z_max":0.17492,"peak_contact_force":348.73667,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":1.0,"raw_peak_contact_force":348.73667,"subtask_id":"insertion_progress","tcp_end":[0.47561,0.0164,0.19547],"tcp_start":[0.47554,0.01641,0.19535],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51028,0.01664,0.17554],"object_pos_start":[0.50998,0.01676,0.17499],"object_to_goal_dist_end":0.09752,"object_to_goal_dist_start":0.09698,"object_z_max":0.17568,"peak_contact_force":65.10515,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":199.0,"raw_peak_contact_force":337.60879,"tcp_end":[0.47595,0.01628,0.19606],"tcp_start":[0.47561,0.0164,0.19547],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":465.0,"n_steps_budget":600.0,"object_pos_end":[0.55503,0.03014,0.19622],"object_pos_start":[0.51028,0.01664,0.17554],"object_to_goal_dist_end":0.13208,"object_to_goal_dist_start":0.09752,"object_z_max":0.19614,"peak_contact_force":0.0,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3.0,"raw_peak_contact_force":70.28247,"subtask_id":"retract_above_hole","tcp_end":[0.52085,0.03118,0.21697],"tcp_start":[0.47595,0.01628,0.19606],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `619899a8ac3451ebc6b92c72992387b20e095386c555898a9ee2a3180ddd0ca3`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":6.48276,"average_solve_count":58.0,"average_success_count":58.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.06355,"insert_1.insertion_depth":0.15496,"insert_1.insertion_force_threshold":32.98419,"release_1.release_duration":0.58215,"retract_1.retract_speed":0.08169},"optimized_scores":{"best_composite_score":0.28149,"best_fitness_score":0.42149,"best_task_score":0.85141},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":15.0,"contact_point_centroid":[0.46115,-0.00251,0.07815],"force_p95":1041.02045,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1088.76236,"mean_force":254.76476,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4563,-0.00248,0.09048]},{"body_a":"peg_socket","body_b":"link7","contact_count":517.0,"contact_point_centroid":[0.56218,-0.00101,0.07983],"force_p95":317.86349,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":697.43823,"mean_force":270.83886,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.45425,-0.00475,0.15754]},{"body_a":"peg_socket","body_b":"link6","contact_count":384.0,"contact_point_centroid":[0.56301,-0.00798,0.07989],"force_p95":289.64783,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":666.696,"mean_force":269.88426,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.45093,-0.0092,0.17452]},{"body_a":"peg_socket","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.56302,-0.00888,0.07994],"force_p95":327.25399,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":327.25399,"mean_force":327.25399,"phase_index":2.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.45863,-0.01181,0.18821]},{"body_a":"peg_socket","body_b":"link6","contact_count":197.0,"contact_point_centroid":[0.56304,-0.00884,0.07997],"force_p95":68.1878,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":166.69,"mean_force":67.58093,"phase_index":3.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.45891,-0.01174,0.18833]},{"body_a":"peg_socket","body_b":"link6","contact_count":3.0,"contact_point_centroid":[0.56305,-0.00886,0.07999],"force_p95":96.03668,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":100.82739,"mean_force":57.46023,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.45902,-0.01173,0.18838]}],"total_contact_groups":6},"final_pose_error":0.01722,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.50305,-0.01254,0.025],"final_tcp_position":[0.49839,-0.01265,0.21342],"realised_fixture_position":[0.50305,-0.01254,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.50305,-0.01254,0.08]},"peak_contact_force":1088.76236,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.50108,-3e-05,0.33212],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.25212,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.49623,-4e-05,0.29241],"tcp_start":[0.49623,-4e-05,0.29241],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":994.0,"n_steps_budget":1000.0,"object_pos_end":[0.49359,-0.01057,0.16881],"object_pos_start":[0.50108,-3e-05,0.33211],"object_to_goal_dist_end":0.08966,"object_to_goal_dist_start":0.25212,"object_z_max":0.33599,"peak_contact_force":289.24815,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":916.0,"raw_peak_contact_force":1088.76236,"subtask_id":"reach_above_hole","tcp_end":[0.45863,-0.01181,0.18821],"tcp_start":[0.49623,-4e-05,0.29241],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.49362,-0.01054,0.16889],"object_pos_start":[0.49359,-0.01057,0.16881],"object_to_goal_dist_end":0.08974,"object_to_goal_dist_start":0.08966,"object_z_max":0.16881,"peak_contact_force":327.25399,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":1.0,"raw_peak_contact_force":327.25399,"subtask_id":"insertion_progress","tcp_end":[0.45867,-0.01178,0.18831],"tcp_start":[0.45863,-0.01181,0.18821],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.49394,-0.01049,0.16891],"object_pos_start":[0.49362,-0.01054,0.16889],"object_to_goal_dist_end":0.08973,"object_to_goal_dist_start":0.08974,"object_z_max":0.16895,"peak_contact_force":66.0889,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":197.0,"raw_peak_contact_force":166.69,"tcp_end":[0.45901,-0.01173,0.18836],"tcp_start":[0.45867,-0.01178,0.18831],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":476.0,"n_steps_budget":600.0,"object_pos_end":[0.53373,-0.01123,0.19475],"object_pos_start":[0.49394,-0.01049,0.16891],"object_to_goal_dist_end":0.12013,"object_to_goal_dist_start":0.08973,"object_z_max":0.19682,"peak_contact_force":0.0,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3.0,"raw_peak_contact_force":100.82739,"subtask_id":"retract_above_hole","tcp_end":[0.49839,-0.01265,0.21342],"tcp_start":[0.45901,-0.01173,0.18836],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `09a021eaed2a28b8f97b40a956e668b0df532c8dfcbc8d48b91f00ceefb0c83a`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":6.65217,"average_solve_count":46.0,"average_success_count":46.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.10052,"insert_1.insertion_depth":0.16153,"insert_1.insertion_force_threshold":34.72156,"release_1.release_duration":0.65485,"retract_1.retract_speed":0.10418},"optimized_scores":{"best_composite_score":0.29546,"best_fitness_score":0.43546,"best_task_score":0.8604},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":15.0,"contact_point_centroid":[0.46437,0.00409,0.07787],"force_p95":1054.32967,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1099.38647,"mean_force":257.56848,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.45948,0.00399,0.08989]},{"body_a":"peg_socket","body_b":"link7","contact_count":240.0,"contact_point_centroid":[0.56768,0.01225,0.07964],"force_p95":353.84469,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":705.48559,"mean_force":288.07177,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.45998,0.00805,0.14887]},{"body_a":"peg_socket","body_b":"link6","contact_count":313.0,"contact_point_centroid":[0.56993,0.01745,0.07981],"force_p95":306.86634,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":337.3911,"mean_force":267.92391,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4543,0.01687,0.17892]},{"body_a":"peg_socket","body_b":"link6","contact_count":198.0,"contact_point_centroid":[0.56999,0.02225,0.07998],"force_p95":67.72784,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":320.69414,"mean_force":68.00145,"phase_index":3.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.46462,0.02006,0.19827]},{"body_a":"peg_socket","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.56995,0.02276,0.07991],"force_p95":318.55995,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":318.55995,"mean_force":318.55995,"phase_index":2.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.4643,0.02052,0.19812]},{"body_a":"peg_socket","body_b":"link6","contact_count":3.0,"contact_point_centroid":[0.57,0.02222,0.07999],"force_p95":104.8807,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":110.62343,"mean_force":62.67334,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.46473,0.02005,0.19829]},{"body_a":"attachment","body_b":"peg_socket","contact_count":5.0,"contact_point_centroid":[0.48005,0.00176,0.07989],"force_p95":0.0,"geom_a":"peg_tip","geom_b":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.46057,0.00398,0.08819]}],"total_contact_groups":7},"final_pose_error":0.0334,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.51001,0.03178,0.025],"final_tcp_position":[0.50379,0.0422,0.19889],"realised_fixture_position":[0.51001,0.03178,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.51001,0.03178,0.08]},"peak_contact_force":1099.38647,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.50108,-3e-05,0.33212],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.25212,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.49623,-4e-05,0.29241],"tcp_start":[0.49623,-4e-05,0.29241],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":663.0,"n_steps_budget":750.0,"object_pos_end":[0.49817,0.02114,0.17684],"object_pos_start":[0.50108,-3e-05,0.33211],"object_to_goal_dist_end":0.09914,"object_to_goal_dist_start":0.25212,"object_z_max":0.33614,"peak_contact_force":294.72074,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":573.0,"raw_peak_contact_force":1099.38647,"subtask_id":"reach_above_hole","tcp_end":[0.4643,0.02052,0.19812],"tcp_start":[0.49623,-4e-05,0.29241],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.49823,0.02106,0.17691],"object_pos_start":[0.49817,0.02114,0.17684],"object_to_goal_dist_end":0.09919,"object_to_goal_dist_start":0.09914,"object_z_max":0.17684,"peak_contact_force":318.55995,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":1.0,"raw_peak_contact_force":318.55995,"subtask_id":"insertion_progress","tcp_end":[0.46437,0.02041,0.1982],"tcp_start":[0.4643,0.02052,0.19812],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.49856,0.02067,0.17696],"object_pos_start":[0.49823,0.02106,0.17691],"object_to_goal_dist_end":0.09915,"object_to_goal_dist_start":0.09919,"object_z_max":0.17703,"peak_contact_force":65.34954,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":198.0,"raw_peak_contact_force":320.69414,"tcp_end":[0.46472,0.02005,0.19828],"tcp_start":[0.46437,0.02041,0.1982],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":448.0,"n_steps_budget":600.0,"object_pos_end":[0.53913,0.04025,0.18024],"object_pos_start":[0.49856,0.02067,0.17696],"object_to_goal_dist_end":0.11489,"object_to_goal_dist_start":0.09915,"object_z_max":0.18746,"peak_contact_force":0.0,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3.0,"raw_peak_contact_force":110.62343,"subtask_id":"retract_above_hole","tcp_end":[0.50379,0.0422,0.19889],"tcp_start":[0.46472,0.02005,0.19828],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```