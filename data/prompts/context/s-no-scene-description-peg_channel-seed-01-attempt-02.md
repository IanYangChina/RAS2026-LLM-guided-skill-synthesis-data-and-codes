## Search State

- **Seed**: 1
- **Iteration**: 3 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 2 | approach → align → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 4 | 0.1072 | 0.00 | ❌ rejected |
| 1 | rotate → align → push → align | impedance_motion | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | position_control | impedance_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 3 | 0.1706 | 0.42 | ✅ accepted |
| 0 | rotate → align → push → align | impedance_motion | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | position_control | impedance_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 3 | 0.1472 | 0.30 | ✅ accepted |

**Proposal policy**: task_score is 0.00 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.107) — your mutation base

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

- **Composite score**: 0.107
- **task_score** (E): 0.000
- **fitness_score**: 0.284  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.083
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.260

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_peg | 1.00 | 1.00 | 0.1932 |
| align_peg | 1.00 | 1.00 | 0.0959 |
| push_channel | 0.33 | 1.00 | 0.0001 |
| retract_up | 1.00 | 1.00 | 0.0407 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_peg | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.481, 0.087, 0.146) | (0.483, 0.080, 0.040)→(0.497, 0.080, 0.034) | 0.161→0.160 | 1.00 / 1.000 | 0.540 | 2.857 |
| align_peg | align | 1.00 / step_budget | (0.481, 0.087, 0.146)→(0.490, 0.081, 0.051) | (0.497, 0.080, 0.034)→(0.499, 0.080, 0.029) | 0.160→0.160 | 1.00 / 2.333 | 251.919 | 385.423 |
| push_channel | push | 0.33 / guard_failure | (0.490, 0.081, 0.051)→(0.490, 0.081, 0.051) | (0.499, 0.080, 0.029)→(0.499, 0.080, 0.029) | 0.160→0.160 | 1.00 / 2.333 | 74.240 | 72.917 |
| retract_up | retract | 1.00 / step_budget | (0.480, 0.061, 0.059)→(0.477, 0.060, 0.100) | (0.495, 0.059, 0.033)→(0.495, 0.059, 0.034) | 0.139→0.139 | 1.00 / 1.000 | 0.535 | 60.883 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.002
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.001
- phase_score: 0.434
- phase_breakdown.approach_above_score: 0.820
- phase_breakdown.push_channel_score: 0.000
- phase_breakdown.align_lateral_score: 0.627

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.306
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.001
- **Median Q (composite search score)**: 0.046
- **K-run variance**: 0.0103
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.298


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.85714,"average_solve_count":63.0,"average_success_count":63.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_peg.lateral_offset_x":-0.00597,"push_channel.force_threshold":24.59996,"push_channel.lateral_retry_x":0.00471,"push_channel.push_distance":0.11261},"optimized_scores":{"best_composite_score":0.04614,"best_fitness_score":0.30614,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":366.0,"contact_point_centroid":[0.50289,0.11616,0.00888],"force_p95":188.55813,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":213.87409,"mean_force":34.30636,"phase_index":1.0,"phase_name":"align_peg","phase_type":"align","tcp_position_centroid":[0.49469,0.11862,0.09077]},{"body_a":"attachment","body_b":"peg","contact_count":94.0,"contact_point_centroid":[0.50758,0.11654,0.05256],"force_p95":206.24597,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":213.32152,"mean_force":131.46909,"phase_index":1.0,"phase_name":"align_peg","phase_type":"align","tcp_position_centroid":[0.4957,0.11715,0.05209]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.49909,0.0989,0.00553],"force_p95":100.84029,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":100.84029,"mean_force":100.84029,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49914,0.11751,0.04586]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.51102,0.11676,0.04772],"force_p95":100.02226,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":100.02226,"mean_force":100.02226,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49914,0.11751,0.04586]},{"body_a":"peg","body_b":"channel_base_body","contact_count":518.0,"contact_point_centroid":[0.5009,0.11598,0.00938],"force_p95":0.60602,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.92055,"mean_force":0.55888,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49818,0.16018,0.22117]}],"total_contact_groups":5},"final_pose_error":0.30985,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50368,0.11629,0.02605],"final_tcp_position":[0.49917,0.11754,0.04583],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50095,0.11604,0.04]},"peak_contact_force":213.87409,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":534.0,"n_steps_budget":1000.0,"object_pos_end":[0.50091,0.11602,0.03385],"object_pos_start":[0.50095,0.11604,0.04],"object_to_goal_dist_end":0.19612,"object_to_goal_dist_start":0.19604,"object_z_max":0.04,"peak_contact_force":0.52535,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":518.0,"raw_peak_contact_force":1.92055,"subtask_id":"approach_above","tcp_end":[0.49796,0.12182,0.14756],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11389,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":366.0,"n_steps_budget":720.0,"object_pos_end":[0.50369,0.11628,0.02606],"object_pos_start":[0.50091,0.11602,0.03385],"object_to_goal_dist_end":0.1968,"object_to_goal_dist_start":0.19612,"object_z_max":0.03397,"peak_contact_force":213.87409,"phase_name":"align_peg","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":460.0,"raw_peak_contact_force":213.87409,"subtask_id":"align_lateral","tcp_end":[0.49914,0.11751,0.04586],"tcp_start":[0.49796,0.12182,0.14756],"tcp_to_object_dist_end":0.02035,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.50368,0.11629,0.02605],"object_pos_start":[0.50369,0.11628,0.02606],"object_to_goal_dist_end":0.19682,"object_to_goal_dist_start":0.1968,"object_z_max":0.02606,"peak_contact_force":100.84029,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2.0,"raw_peak_contact_force":100.84029,"subtask_id":"push_channel","tcp_end":[0.49917,0.11754,0.04583],"tcp_start":[0.49914,0.11751,0.04586],"tcp_to_object_dist_end":0.02032,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `8416ac3bebb4dbec2abbf751596843a33db171fd8d70765023f3b940d846bd0c`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.86957,"average_solve_count":69.0,"average_success_count":69.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_peg.lateral_offset_x":-0.00426,"push_channel.force_threshold":31.64732,"push_channel.lateral_retry_x":0.00058,"push_channel.push_distance":0.10082},"optimized_scores":{"best_composite_score":0.02497,"best_fitness_score":0.28497,"best_task_score":0.00085},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_right_wall","contact_count":62.0,"contact_point_centroid":[0.47497,0.06132,0.05982],"force_p95":437.88397,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":474.52266,"mean_force":359.84973,"phase_index":1.0,"phase_name":"align_peg","phase_type":"align","tcp_position_centroid":[0.48596,0.06538,0.058]},{"body_a":"peg","body_b":"channel_base_body","contact_count":391.0,"contact_point_centroid":[0.49683,0.06367,0.00917],"force_p95":151.43116,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":179.53482,"mean_force":22.5229,"phase_index":1.0,"phase_name":"align_peg","phase_type":"align","tcp_position_centroid":[0.48238,0.06775,0.09029]},{"body_a":"attachment","body_b":"peg","contact_count":107.0,"contact_point_centroid":[0.49889,0.06497,0.0559],"force_p95":163.47301,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":178.91881,"mean_force":80.3633,"phase_index":1.0,"phase_name":"align_peg","phase_type":"align","tcp_position_centroid":[0.48703,0.06541,0.05646]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.51124,0.05163,0.0061],"force_p95":90.52336,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":90.52336,"mean_force":90.52336,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49159,0.06522,0.04865]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.50347,0.06484,0.04961],"force_p95":89.75158,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":89.75158,"mean_force":89.75158,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49159,0.06522,0.04865]},{"body_a":"peg","body_b":"channel_base_body","contact_count":628.0,"contact_point_centroid":[0.49541,0.06398,0.00937],"force_p95":0.56804,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44546,"mean_force":0.5591,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.48848,0.13352,0.21827]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":28.0,"contact_point_centroid":[0.47133,0.06388,0.03676],"force_p95":0.92436,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.16907,"mean_force":0.37063,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49929,0.19795,0.2974]}],"total_contact_groups":7},"final_pose_error":0.24583,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49808,0.06363,0.02713],"final_tcp_position":[0.4916,0.06523,0.04855],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"peak_contact_force":474.52266,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":655.0,"n_steps_budget":1000.0,"object_pos_end":[0.49487,0.0639,0.03396],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.14412,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"peak_contact_force":0.5469,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":656.0,"raw_peak_contact_force":2.44546,"subtask_id":"approach_above","tcp_end":[0.47922,0.07181,0.14546],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11287,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":391.0,"n_steps_budget":720.0,"object_pos_end":[0.49814,0.06363,0.02724],"object_pos_start":[0.49487,0.0639,0.03396],"object_to_goal_dist_end":0.1442,"object_to_goal_dist_start":0.14412,"object_z_max":0.034,"peak_contact_force":156.84983,"phase_name":"align_peg","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":560.0,"raw_peak_contact_force":474.52266,"subtask_id":"align_lateral","tcp_end":[0.49159,0.06522,0.04865],"tcp_start":[0.47922,0.07181,0.14546],"tcp_to_object_dist_end":0.02244,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.49808,0.06363,0.02713],"object_pos_start":[0.49814,0.06363,0.02724],"object_to_goal_dist_end":0.14422,"object_to_goal_dist_start":0.1442,"object_z_max":0.02724,"peak_contact_force":90.52336,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2.0,"raw_peak_contact_force":90.52336,"subtask_id":"push_channel","tcp_end":[0.4916,0.06523,0.04855],"tcp_start":[0.49159,0.06522,0.04865],"tcp_to_object_dist_end":0.02244,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `0188121de1b8142d5ff7a7406b62c43adf6da5520b986a997e46ef53b7d11bf9`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.65934,"average_solve_count":91.0,"average_success_count":91.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_peg.lateral_offset_x":-0.00998,"push_channel.force_threshold":21.02056,"push_channel.lateral_retry_x":-0.00291,"push_channel.push_distance":0.06457},"optimized_scores":{"best_composite_score":0.25055,"best_fitness_score":0.26055,"best_task_score":0.00052},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_right_wall","contact_count":114.0,"contact_point_centroid":[0.47498,0.05135,0.05987],"force_p95":455.67893,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":467.87078,"mean_force":391.67438,"phase_index":1.0,"phase_name":"align_peg","phase_type":"align","tcp_position_centroid":[0.47866,0.06076,0.05919]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":4.0,"contact_point_centroid":[0.475,0.07052,0.05999],"force_p95":59.6373,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":60.88342,"mean_force":44.6351,"phase_index":3.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.48032,0.06074,0.05903]},{"body_a":"peg","body_b":"channel_base_body","contact_count":411.0,"contact_point_centroid":[0.4943,0.05946,0.00937],"force_p95":38.463,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":51.44857,"mean_force":9.70782,"phase_index":1.0,"phase_name":"align_peg","phase_type":"align","tcp_position_centroid":[0.47237,0.06299,0.09053]},{"body_a":"attachment","body_b":"peg","contact_count":116.0,"contact_point_centroid":[0.49046,0.0605,0.05798],"force_p95":39.64633,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":51.07921,"mean_force":32.54717,"phase_index":1.0,"phase_name":"align_peg","phase_type":"align","tcp_position_centroid":[0.47861,0.06076,0.0592]},{"body_a":"peg","body_b":"channel_base_body","contact_count":2.0,"contact_point_centroid":[0.49561,0.06098,0.00916],"force_p95":27.32973,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":27.38738,"mean_force":26.81094,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.48029,0.06078,0.05905]},{"body_a":"attachment","body_b":"peg","contact_count":2.0,"contact_point_centroid":[0.4921,0.06084,0.05762],"force_p95":27.00371,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":27.07362,"mean_force":26.3745,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.48029,0.06078,0.05905]},{"body_a":"peg","body_b":"channel_base_body","contact_count":368.0,"contact_point_centroid":[0.49383,0.05862,0.00942],"force_p95":0.65667,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":26.1016,"mean_force":0.9057,"phase_index":3.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.47736,0.06037,0.0794]},{"body_a":"attachment","body_b":"peg","contact_count":30.0,"contact_point_centroid":[0.49147,0.06068,0.05871],"force_p95":23.68922,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":25.48226,"mean_force":4.48681,"phase_index":3.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.47967,0.06062,0.06039]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":1.0,"contact_point_centroid":[0.475,0.07092,0.05999],"force_p95":14.53823,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":14.53823,"mean_force":14.53823,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.48025,0.06078,0.05904]},{"body_a":"peg","body_b":"channel_base_body","contact_count":640.0,"contact_point_centroid":[0.49432,0.05889,0.00936],"force_p95":0.56138,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.20518,"mean_force":0.56906,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.48165,0.13095,0.21815]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46807,0.05895,0.03796],"force_p95":1.19991,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.42382,"mean_force":0.50385,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49889,0.1973,0.29651]}],"total_contact_groups":11},"final_pose_error":0.00999,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49536,0.05868,0.03377],"final_tcp_position":[0.47699,0.06034,0.09962],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.46685,0.05894,0.04]},"peak_contact_force":467.87078,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":669.0,"n_steps_budget":1000.0,"object_pos_end":[0.49426,0.05894,0.03388],"object_pos_start":[0.46685,0.05894,0.04],"object_to_goal_dist_end":0.13919,"object_to_goal_dist_start":0.14284,"object_z_max":0.04001,"peak_contact_force":0.54863,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":675.0,"raw_peak_contact_force":4.20518,"subtask_id":"approach_above","tcp_end":[0.46605,0.06714,0.14559],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.1155,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":411.0,"n_steps_budget":720.0,"object_pos_end":[0.49541,0.05874,0.03331],"object_pos_start":[0.49426,0.05894,0.03388],"object_to_goal_dist_end":0.13898,"object_to_goal_dist_start":0.13919,"object_z_max":0.03392,"peak_contact_force":385.03243,"phase_name":"align_peg","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":641.0,"raw_peak_contact_force":467.87078,"subtask_id":"align_lateral","tcp_end":[0.48025,0.06078,0.05904],"tcp_start":[0.46605,0.06714,0.14559],"tcp_to_object_dist_end":0.02993,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":2.0,"n_steps_budget":1000.0,"object_pos_end":[0.49538,0.05874,0.0333],"object_pos_start":[0.49541,0.05874,0.03331],"object_to_goal_dist_end":0.13898,"object_to_goal_dist_start":0.13898,"object_z_max":0.03332,"peak_contact_force":31.35562,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":5.0,"raw_peak_contact_force":27.38738,"subtask_id":"push_channel","tcp_end":[0.48031,0.06076,0.05903],"tcp_start":[0.48025,0.06078,0.05904],"tcp_to_object_dist_end":0.02989,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":368.0,"n_steps_budget":600.0,"object_pos_end":[0.49536,0.05868,0.03377],"object_pos_start":[0.49538,0.05874,0.0333],"object_to_goal_dist_end":0.13889,"object_to_goal_dist_start":0.13898,"object_z_max":0.03508,"peak_contact_force":0.53452,"phase_name":"retract_up","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":402.0,"raw_peak_contact_force":60.88342,"tcp_end":[0.47699,0.06034,0.09962],"tcp_start":[0.48031,0.06076,0.05903],"tcp_to_object_dist_end":0.06839,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```