## Search State

- **Seed**: 1
- **Iteration**: 14 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 13 | approach → push | linear_cartesian | linear_cartesian | position_control | impedance_control | pose_tolerance | time_limit | 4 | -0.0891 | 0.01 | ❌ rejected |
| 12 | rotate → align → push → align | impedance_motion | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | position_control | impedance_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 3 | 0.1527 | 0.31 | ❌ rejected |
| 11 | approach → push | linear_cartesian | linear_cartesian | position_control | impedance_control | pose_tolerance | pose_tolerance | 3 | -0.0274 | 0.00 | ❌ rejected |
| 10 | approach → push | linear_cartesian | linear_cartesian | position_control | impedance_control | pose_tolerance | time_limit | 4 | -0.0434 | 0.00 | ❌ rejected |
| 9 | approach → align → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 7 | -0.1096 | 0.00 | ❌ rejected |

**Proposal policy**: task_score is 0.01 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

- Task name: peg_channel
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Goal tolerance: 0.02 m
- Expressivity sigma: 1.0 m
- Expressivity threshold: 0.5
- Force limit: 40.0 N
- Peg body: `peg`
- Primary evaluation target: **insertion depth × lateral alignment (axial progress penalised by wall deviation)**

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

## Current Skill (Q=-0.089) — your mutation base

```yaml
skill: peg_channel
phases:
- id: rotate_1
  type: rotate
  generator: impedance_motion
  control: impedance_control
  termination: time_limit
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
  control: impedance_control
  termination: pose_tolerance
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.02
      - 0.2
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

```

## Design Metrics

- **Composite score**: -0.089
- **task_score** (E): 0.011
- **fitness_score**: 0.111  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.200

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach | 1.00 | 1.00 | 0.2348 |
| push | 0.00 | 1.00 | 0.0001 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.481, 0.105, 0.088) | (0.483, 0.080, 0.040)→(0.497, 0.080, 0.034) | 0.161→0.160 | 1.00 / 1.000 | 0.546 | 2.857 |
| push | push | 0.00 / guard_failure | (0.489, 0.053, 0.059)→(0.489, 0.053, 0.059) | (0.497, 0.080, 0.034)→(0.498, 0.077, 0.036) | 0.160→0.157 | 1.00 / 2.000 | 36.803 | 45.680 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.021
- alignment_error: None
- force_efficiency: 0.177
- terminal_score: 0.012
- phase_score: 0.182
- phase_breakdown.reach_contact_score: 0.823
- phase_breakdown.push_to_goal_score: 0.022

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.114
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.017
- **Median Q (composite search score)**: -0.088
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.358


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `a904e23429ae963dd2788b3e8d0575d9ce341e1daddfe013fbb1224c3e0c850e`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `6bee39a4c127c6d39ee1365e3969a50bb09484f7e2580b1a3dc4d8c4ae20213b`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.44286,"average_solve_count":70.0,"average_success_count":70.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_speed":0.11945,"push.push_offset_y":0.12761,"push.push_speed":0.04748,"push.push_timeout":5.07422},"optimized_scores":{"best_composite_score":-0.08819,"best_fitness_score":0.11181,"best_task_score":0.01697},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":661.0,"contact_point_centroid":[0.50136,0.11423,0.00943],"force_p95":27.76321,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":49.41995,"mean_force":3.48385,"phase_index":1.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.49495,0.11218,0.07046]},{"body_a":"attachment","body_b":"peg","contact_count":74.0,"contact_point_centroid":[0.50614,0.09716,0.0587],"force_p95":39.36304,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":48.96807,"mean_force":26.31777,"phase_index":1.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.49586,0.09132,0.05973]},{"body_a":"peg","body_b":"channel_base_body","contact_count":642.0,"contact_point_centroid":[0.50088,0.11601,0.00939],"force_p95":0.62166,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.92055,"mean_force":0.5554,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.49802,0.16884,0.19151]}],"total_contact_groups":3},"final_pose_error":0.04466,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50179,0.11332,0.03608],"final_tcp_position":[0.49687,0.08795,0.05888],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50095,0.11604,0.04]},"peak_contact_force":49.41995,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":658.0,"n_steps_budget":1000.0,"object_pos_end":[0.50093,0.11602,0.03388],"object_pos_start":[0.50095,0.11604,0.04],"object_to_goal_dist_end":0.19612,"object_to_goal_dist_start":0.19604,"object_z_max":0.04,"peak_contact_force":0.55126,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":642.0,"raw_peak_contact_force":1.92055,"subtask_id":"reach_contact","tcp_end":[0.49756,0.13906,0.08876],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.05961,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":661.0,"n_steps_budget":1000.0,"object_pos_end":[0.5018,0.11341,0.03604],"object_pos_start":[0.50093,0.11602,0.03388],"object_to_goal_dist_end":0.19346,"object_to_goal_dist_start":0.19612,"object_z_max":0.03606,"peak_contact_force":33.79364,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":735.0,"raw_peak_contact_force":49.41995,"subtask_id":"push_to_goal","tcp_end":[0.49687,0.08795,0.05888],"tcp_start":[0.49684,0.08802,0.05891],"tcp_to_object_dist_end":0.03456,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `8416ac3bebb4dbec2abbf751596843a33db171fd8d70765023f3b940d846bd0c`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.66667,"average_solve_count":57.0,"average_success_count":57.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_speed":0.22508,"push.push_offset_y":0.06444,"push.push_speed":0.04848,"push.push_timeout":2.61526},"optimized_scores":{"best_composite_score":-0.0856,"best_fitness_score":0.1144,"best_task_score":0.01231},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":780.0,"contact_point_centroid":[0.49586,0.06182,0.00942],"force_p95":28.88432,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":41.15635,"mean_force":3.69239,"phase_index":1.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.48146,0.05949,0.07016]},{"body_a":"attachment","body_b":"peg","contact_count":96.0,"contact_point_centroid":[0.4956,0.04288,0.05865],"force_p95":33.57372,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":40.71309,"mean_force":25.62597,"phase_index":1.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.48682,0.0349,0.05942]},{"body_a":"peg","body_b":"channel_base_body","contact_count":613.0,"contact_point_centroid":[0.49528,0.06388,0.00937],"force_p95":0.56981,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44546,"mean_force":0.55944,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.48826,0.14249,0.18814]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":28.0,"contact_point_centroid":[0.47133,0.06388,0.03676],"force_p95":0.92436,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.16907,"mean_force":0.37063,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.4993,0.19808,0.29647]}],"total_contact_groups":4},"final_pose_error":0.05142,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49683,0.06048,0.03675],"final_tcp_position":[0.48834,0.03098,0.05851],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"peak_contact_force":41.15635,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":640.0,"n_steps_budget":720.0,"object_pos_end":[0.49513,0.06365,0.03396],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.14386,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"peak_contact_force":0.54116,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":641.0,"raw_peak_contact_force":2.44546,"subtask_id":"reach_contact","tcp_end":[0.47874,0.08958,0.08762],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.06181,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":780.0,"n_steps_budget":1000.0,"object_pos_end":[0.49688,0.06056,0.03671],"object_pos_start":[0.49513,0.06365,0.03396],"object_to_goal_dist_end":0.14063,"object_to_goal_dist_start":0.14386,"object_z_max":0.03674,"peak_contact_force":38.23312,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":876.0,"raw_peak_contact_force":41.15635,"subtask_id":"push_to_goal","tcp_end":[0.48834,0.03098,0.05851],"tcp_start":[0.48835,0.03104,0.05854],"tcp_to_object_dist_end":0.03772,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `0188121de1b8142d5ff7a7406b62c43adf6da5520b986a997e46ef53b7d11bf9`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.85938,"average_solve_count":64.0,"average_success_count":64.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_speed":0.16096,"push.push_offset_y":0.08002,"push.push_speed":0.04373,"push.push_timeout":7.55922},"optimized_scores":{"best_composite_score":-0.09337,"best_fitness_score":0.10663,"best_task_score":0.00344},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":725.0,"contact_point_centroid":[0.49458,0.0574,0.00941],"force_p95":28.4304,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":46.46382,"mean_force":3.18919,"phase_index":1.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.47173,0.06128,0.07084]},{"body_a":"attachment","body_b":"peg","contact_count":68.0,"contact_point_centroid":[0.49141,0.04442,0.05888],"force_p95":36.66844,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":46.05336,"mean_force":28.2463,"phase_index":1.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.47985,0.04197,0.06008]},{"body_a":"peg","body_b":"channel_base_body","contact_count":660.0,"contact_point_centroid":[0.49439,0.05891,0.00936],"force_p95":0.56081,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.20518,"mean_force":0.56836,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.48143,0.14017,0.18839]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46807,0.05895,0.03796],"force_p95":1.19991,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.42382,"mean_force":0.50385,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.49895,0.19768,0.29568]}],"total_contact_groups":4},"final_pose_error":0.04845,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49565,0.05713,0.03503],"final_tcp_position":[0.48129,0.04016,0.05964],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.46685,0.05894,0.04]},"peak_contact_force":46.46382,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":689.0,"n_steps_budget":990.0,"object_pos_end":[0.4942,0.05908,0.03389],"object_pos_start":[0.46685,0.05894,0.04],"object_to_goal_dist_end":0.13934,"object_to_goal_dist_start":0.14284,"object_z_max":0.04001,"peak_contact_force":0.54648,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":695.0,"raw_peak_contact_force":4.20518,"subtask_id":"reach_contact","tcp_end":[0.46554,0.08494,0.08782],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.06632,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":725.0,"n_steps_budget":1000.0,"object_pos_end":[0.49568,0.05718,0.03504],"object_pos_start":[0.4942,0.05908,0.03389],"object_to_goal_dist_end":0.13734,"object_to_goal_dist_start":0.13934,"object_z_max":0.03504,"peak_contact_force":38.38284,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":793.0,"raw_peak_contact_force":46.46382,"subtask_id":"push_to_goal","tcp_end":[0.48129,0.04016,0.05964],"tcp_start":[0.4813,0.0402,0.05967],"tcp_to_object_dist_end":0.03319,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
```