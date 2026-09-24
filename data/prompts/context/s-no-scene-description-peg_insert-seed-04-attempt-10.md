## Search State

- **Seed**: 4
- **Iteration**: 11 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 10 | approach → grasp → lift → approach → align → insert → release | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | — | position_control | position_control | impedance_control | position_control | position_control | impedance_control | position_control | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 8 | -0.0341 | 0.88 | ❌ rejected |
| 9 | push → align → release → insert | linear_cartesian | linear_cartesian | — | impedance_motion | position_control | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | time_limit | force_exceeded | 6 | 0.1595 | 0.86 | ❌ rejected |
| 8 | push → align → release → insert | impedance_motion | linear_cartesian | linear_cartesian | impedance_motion | impedance_control | position_control | admittance_control | impedance_control | time_limit | pose_tolerance | pose_tolerance | force_exceeded | 6 | 0.1391 | 0.96 | ❌ rejected |
| 7 | push → align → release → insert | impedance_motion | linear_cartesian | linear_cartesian | impedance_motion | impedance_control | position_control | admittance_control | impedance_control | time_limit | pose_tolerance | pose_tolerance | force_exceeded | 6 | 0.6608 | 0.91 | ❌ rejected |
| 6 | push → align → release → insert | impedance_motion | linear_cartesian | linear_cartesian | impedance_motion | impedance_control | position_control | admittance_control | impedance_control | time_limit | pose_tolerance | pose_tolerance | force_exceeded | 6 | 0.1391 | 0.96 | ❌ rejected |

**Proposal policy**: task_score is 0.88 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.034) — your mutation base

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

- **Composite score**: -0.034
- **task_score** (E): 0.884
- **fitness_score**: 0.516  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.550

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_peg | 1.00 | 0.00 | 0.1400 |
| grasp_peg | 1.00 | 0.00 | 0.0082 |
| lift_peg | 1.00 | 0.00 | 0.0793 |
| approach_hole | 0.00 | 0.33 | 0.2817 |
| align_hole | 0.33 | 0.67 | 0.0217 |
| insert_peg | 0.00 | 0.67 | 0.0016 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_peg | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.503, -0.000, 0.440) | (0.504, -0.000, 0.340)→(0.508, -0.000, 0.480) | 0.260→0.400 | 0.00 / 0.000 | 0.000 | 0.000 |
| grasp_peg | grasp | 1.00 / step_budget | (0.503, -0.000, 0.440)→(0.502, -0.000, 0.432) | (0.508, -0.000, 0.480)→(0.507, -0.000, 0.472) | 0.400→0.392 | 0.00 / 0.000 | 0.000 | 0.000 |
| lift_peg | lift | 1.00 / step_budget | (0.502, -0.000, 0.432)→(0.502, -0.000, 0.512) | (0.507, -0.000, 0.472)→(0.508, -0.000, 0.551) | 0.392→0.471 | 0.00 / 0.000 | 0.000 | 0.000 |
| approach_hole | approach | 0.00 / step_budget | (0.502, -0.000, 0.512)→(0.434, 0.002, 0.243) | (0.508, -0.000, 0.551)→(0.464, 0.002, 0.220) | 0.471→0.148 | 0.33 / 0.333 | 65.934 | 8825.711 |
| align_hole | align | 0.33 / step_budget | (0.434, 0.002, 0.243)→(0.451, 0.005, 0.231) | (0.464, 0.002, 0.220)→(0.481, 0.005, 0.208) | 0.148→0.136 | 0.67 / 1.000 | 311.702 | 2558.105 |
| insert_peg | insert | 0.00 / guard_failure | (0.451, 0.005, 0.231)→(0.452, 0.005, 0.229) | (0.481, 0.005, 0.208)→(0.482, 0.005, 0.207) | 0.136→0.135 | 0.67 / 0.667 | 199.561 | 244.707 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.906
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.906
- phase_score: 0.486
- phase_breakdown.above_peg_score: 0.672
- phase_breakdown.above_hole_score: 0.216
- phase_breakdown.inserted_score: 0.574

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.654
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.931
- **Median Q (composite search score)**: -0.078
- **K-run variance**: 0.0100
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.281


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":6.93233,"average_solve_count":133.0,"average_success_count":133.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_hole.lateral_offset_x":0.00499,"align_hole.lateral_offset_y":0.00718,"approach_hole.approach_speed":0.05389,"approach_peg.approach_speed":0.09615,"insert_peg.insertion_depth":0.05655,"insert_peg.insertion_force_threshold":24.65435,"lift_peg.lift_height":0.09128,"release_peg.release_duration":0.62775},"optimized_scores":{"best_composite_score":-0.12916,"best_fitness_score":0.42084,"best_task_score":0.81624},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link7","contact_count":356.0,"contact_point_centroid":[0.59534,0.00133,0.07937],"force_p95":318.31187,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":2119.78556,"mean_force":258.57053,"phase_index":3.0,"phase_name":"approach_hole","phase_type":"approach","tcp_position_centroid":[0.49013,0.0002,0.1485]},{"body_a":"peg_socket","body_b":"link6","contact_count":707.0,"contact_point_centroid":[0.53809,-0.02913,0.07994],"force_p95":422.26304,"geom_a":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1618.68403,"mean_force":367.53358,"phase_index":4.0,"phase_name":"align_hole","phase_type":"align","tcp_position_centroid":[0.41219,0.00172,0.3022]},{"body_a":"peg_socket","body_b":"link6","contact_count":719.0,"contact_point_centroid":[0.54001,0.03094,0.07996],"force_p95":433.92284,"geom_a":"socket_collar_y1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1581.58631,"mean_force":380.81873,"phase_index":4.0,"phase_name":"align_hole","phase_type":"align","tcp_position_centroid":[0.41212,0.00173,0.30224]},{"body_a":"peg_socket","body_b":"link6","contact_count":18.0,"contact_point_centroid":[0.56586,0.01133,0.07912],"force_p95":1096.00371,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1164.50502,"mean_force":842.9768,"phase_index":4.0,"phase_name":"align_hole","phase_type":"align","tcp_position_centroid":[0.42095,0.00301,0.29777]},{"body_a":"peg_socket","body_b":"link6","contact_count":275.0,"contact_point_centroid":[0.50534,-0.00057,0.07989],"force_p95":257.41186,"geom_a":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":308.12414,"mean_force":230.49001,"phase_index":4.0,"phase_name":"align_hole","phase_type":"align","tcp_position_centroid":[0.40399,0.00095,0.30382]},{"body_a":"peg_socket","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.56585,0.01161,0.07916],"force_p95":274.64301,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":274.64301,"mean_force":274.64301,"phase_index":5.0,"phase_name":"insert_peg","phase_type":"insert","tcp_position_centroid":[0.42156,0.00319,0.29804]}],"total_contact_groups":6},"final_pose_error":0.29737,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.53544,0.00091,0.025],"final_tcp_position":[0.42148,0.00315,0.29811],"realised_fixture_position":[0.53544,0.00091,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.53544,0.00091,0.08]},"peak_contact_force":2119.78556,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":434.0,"n_steps_budget":1000.0,"object_pos_end":[0.5076,-2e-05,0.48033],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.40041,"object_to_goal_dist_start":0.26034,"object_z_max":0.48004,"peak_contact_force":0.0,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"above_peg","tcp_end":[0.50301,-4e-05,0.4406],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50693,-6e-05,0.47211],"object_pos_start":[0.5076,-2e-05,0.48033],"object_to_goal_dist_end":0.39217,"object_to_goal_dist_start":0.40041,"object_z_max":0.48051,"peak_contact_force":0.0,"phase_name":"grasp_peg","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.50163,-0.0001,0.43247],"tcp_start":[0.50301,-4e-05,0.4406],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":222.0,"n_steps_budget":600.0,"object_pos_end":[0.50754,-0.0001,0.54357],"object_pos_start":[0.50693,-6e-05,0.47211],"object_to_goal_dist_end":0.46363,"object_to_goal_dist_start":0.39217,"object_z_max":0.54327,"peak_contact_force":0.0,"phase_name":"lift_peg","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.50177,-0.00014,0.50399],"tcp_start":[0.50163,-0.0001,0.43247],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.44023,9e-05,0.27528],"object_pos_start":[0.50754,-0.0001,0.54357],"object_to_goal_dist_end":0.20422,"object_to_goal_dist_start":0.46363,"object_z_max":0.59953,"peak_contact_force":0.0,"phase_name":"approach_hole","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":356.0,"raw_peak_contact_force":2119.78556,"subtask_id":"above_hole","tcp_end":[0.4164,9e-05,0.3074],"tcp_start":[0.50177,-0.00014,0.50399],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.445,0.00285,0.26562],"object_pos_start":[0.44023,9e-05,0.27528],"object_to_goal_dist_end":0.19362,"object_to_goal_dist_start":0.20422,"object_z_max":0.27528,"peak_contact_force":706.31839,"phase_name":"align_hole","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":1719.0,"raw_peak_contact_force":1618.68403,"subtask_id":"above_hole","tcp_end":[0.42156,0.00319,0.29804],"tcp_start":[0.4164,9e-05,0.3074],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.44492,0.00281,0.2657],"object_pos_start":[0.445,0.00285,0.26562],"object_to_goal_dist_end":0.19372,"object_to_goal_dist_start":0.19362,"object_z_max":0.26562,"peak_contact_force":274.64301,"phase_name":"insert_peg","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":1.0,"raw_peak_contact_force":274.64301,"subtask_id":"inserted","tcp_end":[0.42148,0.00315,0.29811],"tcp_start":[0.42156,0.00319,0.29804],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `82356f74d11e1888d903e80aabfa97b50f0a1f9374ab8997097863e47a04dcc6`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":6.92029,"average_solve_count":138.0,"average_success_count":138.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_hole.lateral_offset_x":-0.0007,"align_hole.lateral_offset_y":-0.01099,"approach_hole.approach_speed":0.04847,"approach_peg.approach_speed":0.0878,"insert_peg.insertion_depth":0.06769,"insert_peg.insertion_force_threshold":16.90304,"lift_peg.lift_height":0.0925,"release_peg.release_duration":0.46467},"optimized_scores":{"best_composite_score":-0.07752,"best_fitness_score":0.47248,"best_task_score":0.93062},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link7","contact_count":549.0,"contact_point_centroid":[0.58364,0.02011,0.07759],"force_p95":303.69828,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":2218.70339,"mean_force":258.12501,"phase_index":3.0,"phase_name":"approach_hole","phase_type":"approach","tcp_position_centroid":[0.502,0.00154,0.09797]},{"body_a":"peg_socket","body_b":"link6","contact_count":508.0,"contact_point_centroid":[0.5547,0.01322,0.07992],"force_p95":690.29065,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1358.21132,"mean_force":690.5649,"phase_index":4.0,"phase_name":"align_hole","phase_type":"align","tcp_position_centroid":[0.42074,0.01182,0.30302]},{"body_a":"peg_socket","body_b":"link6","contact_count":474.0,"contact_point_centroid":[0.53047,-0.00538,0.07984],"force_p95":539.17278,"geom_a":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":700.00784,"mean_force":299.98187,"phase_index":4.0,"phase_name":"align_hole","phase_type":"align","tcp_position_centroid":[0.39892,0.00779,0.30359]},{"body_a":"peg_socket","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.58433,0.01482,0.0799],"force_p95":324.04071,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":324.04071,"mean_force":324.04071,"phase_index":5.0,"phase_name":"insert_peg","phase_type":"insert","tcp_position_centroid":[0.44734,0.013,0.28551]},{"body_a":"attachment","body_b":"peg_socket","contact_count":18.0,"contact_point_centroid":[0.49077,0.0035,0.07993],"force_p95":163.40532,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":165.01936,"mean_force":135.77309,"phase_index":3.0,"phase_name":"approach_hole","phase_type":"approach","tcp_position_centroid":[0.48747,0.00347,0.09449]}],"total_contact_groups":5},"final_pose_error":0.28376,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.5244,0.02464,0.025],"final_tcp_position":[0.44718,0.01302,0.28512],"realised_fixture_position":[0.5244,0.02464,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.5244,0.02464,0.08]},"peak_contact_force":2218.70339,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":438.0,"n_steps_budget":1000.0,"object_pos_end":[0.50756,-2e-05,0.48009],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.40016,"object_to_goal_dist_start":0.26034,"object_z_max":0.47978,"peak_contact_force":0.0,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"above_peg","tcp_end":[0.50297,-4e-05,0.44035],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50689,-6e-05,0.47187],"object_pos_start":[0.50756,-2e-05,0.48009],"object_to_goal_dist_end":0.39193,"object_to_goal_dist_start":0.40016,"object_z_max":0.48027,"peak_contact_force":0.0,"phase_name":"grasp_peg","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.50158,-0.0001,0.43223],"tcp_start":[0.50297,-4e-05,0.44035],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":225.0,"n_steps_budget":600.0,"object_pos_end":[0.50751,-0.0001,0.54435],"object_pos_start":[0.50689,-6e-05,0.47187],"object_to_goal_dist_end":0.46442,"object_to_goal_dist_start":0.39193,"object_z_max":0.54405,"peak_contact_force":0.0,"phase_name":"lift_peg","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.50173,-0.00014,0.50477],"tcp_start":[0.50158,-0.0001,0.43223],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.43708,0.00655,0.27648],"object_pos_start":[0.50751,-0.0001,0.54435],"object_to_goal_dist_end":0.20641,"object_to_goal_dist_start":0.46442,"object_z_max":0.60045,"peak_contact_force":0.0,"phase_name":"approach_hole","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":567.0,"raw_peak_contact_force":2218.70339,"subtask_id":"above_hole","tcp_end":[0.41337,0.00626,0.3087],"tcp_start":[0.50173,-0.00014,0.50477],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47248,0.01328,0.25966],"object_pos_start":[0.43708,0.00655,0.27648],"object_to_goal_dist_end":0.18224,"object_to_goal_dist_start":0.20641,"object_z_max":0.27702,"peak_contact_force":0.0,"phase_name":"align_hole","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":982.0,"raw_peak_contact_force":1358.21132,"subtask_id":"above_hole","tcp_end":[0.44556,0.01287,0.28925],"tcp_start":[0.41337,0.00626,0.3087],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":7.0,"n_steps_budget":1000.0,"object_pos_end":[0.47425,0.01343,0.25568],"object_pos_start":[0.47248,0.01328,0.25966],"object_to_goal_dist_end":0.17806,"object_to_goal_dist_start":0.18224,"object_z_max":0.25966,"peak_contact_force":324.04071,"phase_name":"insert_peg","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":1.0,"raw_peak_contact_force":324.04071,"subtask_id":"inserted","tcp_end":[0.44718,0.01302,0.28512],"tcp_start":[0.44556,0.01287,0.28925],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `4fedbe547233117d2a5522e0e6da389f32d172824e1a5c898bb2e8c1e5f99b78`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":6.2446,"average_solve_count":139.0,"average_success_count":139.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_hole.lateral_offset_x":-0.00808,"align_hole.lateral_offset_y":0.0012,"approach_hole.approach_speed":0.04664,"approach_peg.approach_speed":0.06044,"insert_peg.insertion_depth":0.06825,"insert_peg.insertion_force_threshold":12.49608,"lift_peg.lift_height":0.11364,"release_peg.release_duration":0.48528},"optimized_scores":{"best_composite_score":0.10429,"best_fitness_score":0.65429,"best_task_score":0.90634},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":35.0,"contact_point_centroid":[0.56146,0.00329,0.07547],"force_p95":21030.69725,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":22138.64257,"mean_force":6889.21053,"phase_index":3.0,"phase_name":"approach_hole","phase_type":"approach","tcp_position_centroid":[0.48767,0.0024,0.09833]},{"body_a":"peg_socket","body_b":"link7","contact_count":829.0,"contact_point_centroid":[0.56277,0.00356,0.06985],"force_p95":186.2432,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":17582.39666,"mean_force":369.15407,"phase_index":3.0,"phase_name":"approach_hole","phase_type":"approach","tcp_position_centroid":[0.48809,0.00281,0.11243]},{"body_a":"peg_socket","body_b":"link7","contact_count":16.0,"contact_point_centroid":[0.56056,0.00486,0.0488],"force_p95":7290.10543,"geom_a":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":7564.86847,"mean_force":1659.79126,"phase_index":3.0,"phase_name":"approach_hole","phase_type":"approach","tcp_position_centroid":[0.48458,0.00275,0.09597]},{"body_a":"attachment","body_b":"peg_socket","contact_count":6.0,"contact_point_centroid":[0.53304,0.01761,0.07996],"force_p95":4799.46094,"geom_a":"peg_tip","geom_b":"socket_collar_y1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":4840.26455,"mean_force":4209.56686,"phase_index":3.0,"phase_name":"approach_hole","phase_type":"approach","tcp_position_centroid":[0.48363,0.00292,0.09514]},{"body_a":"attachment","body_b":"peg_socket","contact_count":363.0,"contact_point_centroid":[0.56273,-0.00254,0.0798],"force_p95":2602.23698,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":4697.41864,"mean_force":402.93978,"phase_index":4.0,"phase_name":"align_hole","phase_type":"align","tcp_position_centroid":[0.48601,-0.00157,0.1022]},{"body_a":"peg_socket","body_b":"link7","contact_count":401.0,"contact_point_centroid":[0.56284,-0.00701,0.06486],"force_p95":2135.19664,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":4479.10229,"mean_force":465.4085,"phase_index":4.0,"phase_name":"align_hole","phase_type":"align","tcp_position_centroid":[0.4857,-0.00153,0.10247]},{"body_a":"attachment","body_b":"peg_socket","contact_count":1.0,"contact_point_centroid":[0.56305,-0.00276,0.07997],"force_p95":135.43747,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":135.43747,"mean_force":135.43747,"phase_index":5.0,"phase_name":"insert_peg","phase_type":"insert","tcp_position_centroid":[0.48722,-0.00148,0.10453]},{"body_a":"peg_socket","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.56301,-0.00734,0.06457],"force_p95":0.0,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0,"mean_force":0.0,"phase_index":5.0,"phase_name":"insert_peg","phase_type":"insert","tcp_position_centroid":[0.48722,-0.00148,0.10453]}],"total_contact_groups":8},"final_pose_error":0.09486,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.50305,-0.01254,0.025],"final_tcp_position":[0.48736,-0.00151,0.10465],"realised_fixture_position":[0.50305,-0.01254,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.50305,-0.01254,0.08]},"peak_contact_force":22138.64257,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":463.0,"n_steps_budget":1000.0,"object_pos_end":[0.50752,-2e-05,0.48016],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.40024,"object_to_goal_dist_start":0.26034,"object_z_max":0.47987,"peak_contact_force":0.0,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"above_peg","tcp_end":[0.50292,-4e-05,0.44043],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50685,-6e-05,0.47194],"object_pos_start":[0.50752,-2e-05,0.48016],"object_to_goal_dist_end":0.392,"object_to_goal_dist_start":0.40024,"object_z_max":0.48033,"peak_contact_force":0.0,"phase_name":"grasp_peg","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.50153,-0.0001,0.43229],"tcp_start":[0.50292,-4e-05,0.44043],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":289.0,"n_steps_budget":720.0,"object_pos_end":[0.50771,-0.0001,0.56579],"object_pos_start":[0.50685,-6e-05,0.47194],"object_to_goal_dist_end":0.48585,"object_to_goal_dist_start":0.392,"object_z_max":0.56549,"peak_contact_force":0.0,"phase_name":"lift_peg","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.50193,-0.00015,0.52621],"tcp_start":[0.50153,-0.0001,0.43229],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51319,-0.00031,0.10954],"object_pos_start":[0.50771,-0.0001,0.56579],"object_to_goal_dist_end":0.03235,"object_to_goal_dist_start":0.48585,"object_z_max":0.61899,"peak_contact_force":197.8021,"phase_name":"approach_hole","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":886.0,"raw_peak_contact_force":22138.64257,"subtask_id":"above_hole","tcp_end":[0.47325,-0.00016,0.1116],"tcp_start":[0.50193,-0.00015,0.52621],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":426.0,"n_steps_budget":600.0,"object_pos_end":[0.5269,-0.00214,0.09957],"object_pos_start":[0.51319,-0.00031,0.10954],"object_to_goal_dist_end":0.03334,"object_to_goal_dist_start":0.03235,"object_z_max":0.10954,"peak_contact_force":228.78722,"phase_name":"align_hole","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":764.0,"raw_peak_contact_force":4697.41864,"subtask_id":"above_hole","tcp_end":[0.48722,-0.00148,0.10453],"tcp_start":[0.47325,-0.00016,0.1116],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.52704,-0.00216,0.09968],"object_pos_start":[0.5269,-0.00214,0.09957],"object_to_goal_dist_end":0.03351,"object_to_goal_dist_start":0.03334,"object_z_max":0.09957,"peak_contact_force":0.0,"phase_name":"insert_peg","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":2.0,"raw_peak_contact_force":135.43747,"subtask_id":"inserted","tcp_end":[0.48736,-0.00151,0.10465],"tcp_start":[0.48722,-0.00148,0.10453],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
```