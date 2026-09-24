## Search State

- **Seed**: 1
- **Iteration**: 11 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 10 | approach → push | linear_cartesian | linear_cartesian | position_control | impedance_control | pose_tolerance | time_limit | 4 | -0.0434 | 0.00 | ❌ rejected |
| 9 | approach → align → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 7 | -0.1096 | 0.00 | ❌ rejected |
| 8 | approach → rotate → contact → push | linear_cartesian | impedance_motion | linear_cartesian | linear_cartesian | position_control | impedance_control | force_threshold_switch | admittance_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 5 | 0.0551 | 0.00 | ❌ rejected |
| 7 | rotate → align → push → align | impedance_motion | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | position_control | impedance_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 3 | 0.1659 | 0.40 | ❌ rejected |
| 6 | rotate → align → push → align | impedance_motion | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | position_control | impedance_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 3 | 0.1659 | 0.40 | ❌ rejected |

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

## Current Skill (Q=-0.043) — your mutation base

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

- **Composite score**: -0.043
- **task_score** (E): 0.000
- **fitness_score**: 0.157  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.200

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_entry | 1.00 | 1.00 | 0.1911 |
| push_through_channel | 0.00 | 1.00 | 0.0001 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_entry | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.497, 0.088, 0.145) | (0.483, 0.080, 0.040)→(0.497, 0.080, 0.034) | 0.161→0.160 | 1.00 / 1.000 | 0.531 | 2.857 |
| push_through_channel | push | 0.00 / guard_failure | (0.497, 0.086, 0.144)→(0.497, 0.086, 0.143) | (0.497, 0.080, 0.034)→(0.497, 0.080, 0.034) | 0.160→0.160 | 1.00 / 2.000 | 27.344 | 54.194 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.001
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.001
- phase_score: 0.261
- phase_breakdown.reach_entry_score: 0.822
- phase_breakdown.traverse_channel_score: 0.020

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.157
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.001
- **Median Q (composite search score)**: -0.044
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.344


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.79545,"average_solve_count":44.0,"average_success_count":44.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_entry.approach_speed":0.11477,"push_through_channel.force_threshold":23.71071,"push_through_channel.max_time":8.23738,"push_through_channel.push_speed":0.01417},"optimized_scores":{"best_composite_score":-0.04352,"best_fitness_score":0.15648,"best_task_score":0.00022},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.52503,0.02207,0.05991],"force_p95":62.21353,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":62.86685,"mean_force":46.45744,"phase_index":1.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49678,0.08647,0.14355]},{"body_a":"peg","body_b":"channel_base_body","contact_count":614.0,"contact_point_centroid":[0.50086,0.11604,0.00938],"force_p95":0.61569,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.92055,"mean_force":0.55678,"phase_index":0.0,"phase_name":"approach_entry","phase_type":"approach","tcp_position_centroid":[0.48805,0.13614,0.2074]},{"body_a":"peg","body_b":"channel_base_body","contact_count":16.0,"contact_point_centroid":[0.50315,0.11493,0.00944],"force_p95":0.59543,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.61461,"mean_force":0.53921,"phase_index":1.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49707,0.08701,0.1444]}],"total_contact_groups":3},"final_pose_error":0.19588,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50098,0.116,0.03391],"final_tcp_position":[0.49674,0.08635,0.14338],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50095,0.11604,0.04]},"peak_contact_force":62.86685,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":630.0,"n_steps_budget":1000.0,"object_pos_end":[0.50095,0.11604,0.03388],"object_pos_start":[0.50095,0.11604,0.04],"object_to_goal_dist_end":0.19614,"object_to_goal_dist_start":0.19604,"object_z_max":0.04,"peak_contact_force":0.49725,"phase_name":"approach_entry","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":614.0,"raw_peak_contact_force":1.92055,"subtask_id":"reach_entry","tcp_end":[0.49742,0.08767,0.14548],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11521,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":16.0,"n_steps_budget":1000.0,"object_pos_end":[0.501,0.11601,0.03391],"object_pos_start":[0.50095,0.11604,0.03388],"object_to_goal_dist_end":0.19611,"object_to_goal_dist_start":0.19614,"object_z_max":0.03391,"peak_contact_force":20.17178,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":19.0,"raw_peak_contact_force":62.86685,"subtask_id":"traverse_channel","tcp_end":[0.49674,0.08635,0.14338],"tcp_start":[0.49678,0.0864,0.14345],"tcp_to_object_dist_end":0.1135,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `8416ac3bebb4dbec2abbf751596843a33db171fd8d70765023f3b940d846bd0c`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.87234,"average_solve_count":47.0,"average_success_count":47.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_entry.approach_speed":0.10183,"push_through_channel.force_threshold":22.09377,"push_through_channel.max_time":6.81127,"push_through_channel.push_speed":0.05568},"optimized_scores":{"best_composite_score":-0.04325,"best_fitness_score":0.15675,"best_task_score":0.00092},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.52502,0.02207,0.05994],"force_p95":54.95019,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":55.56952,"mean_force":40.8872,"phase_index":1.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49689,0.08645,0.14367]},{"body_a":"peg","body_b":"channel_base_body","contact_count":620.0,"contact_point_centroid":[0.49543,0.0638,0.00937],"force_p95":0.56835,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44546,"mean_force":0.55929,"phase_index":0.0,"phase_name":"approach_entry","phase_type":"approach","tcp_position_centroid":[0.48833,0.13608,0.20722]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":28.0,"contact_point_centroid":[0.47133,0.06388,0.03676],"force_p95":0.92436,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.16907,"mean_force":0.37063,"phase_index":0.0,"phase_name":"approach_entry","phase_type":"approach","tcp_position_centroid":[0.49282,0.18419,0.28087]},{"body_a":"peg","body_b":"channel_base_body","contact_count":14.0,"contact_point_centroid":[0.48865,0.06814,0.0094],"force_p95":0.54946,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.5516,"mean_force":0.54538,"phase_index":1.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49713,0.087,0.14448]}],"total_contact_groups":4},"final_pose_error":0.1959,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.4951,0.06365,0.03396],"final_tcp_position":[0.49684,0.08631,0.14349],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"peak_contact_force":55.56952,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":647.0,"n_steps_budget":1000.0,"object_pos_end":[0.49527,0.06401,0.03396],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.14422,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"peak_contact_force":0.54509,"phase_name":"approach_entry","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":648.0,"raw_peak_contact_force":2.44546,"subtask_id":"reach_entry","tcp_end":[0.49742,0.08767,0.14548],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11403,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":14.0,"n_steps_budget":1000.0,"object_pos_end":[0.49497,0.06368,0.03396],"object_pos_start":[0.49527,0.06401,0.03396],"object_to_goal_dist_end":0.14389,"object_to_goal_dist_start":0.14422,"object_z_max":0.03396,"peak_contact_force":17.7159,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":17.0,"raw_peak_contact_force":55.56952,"subtask_id":"traverse_channel","tcp_end":[0.49684,0.08631,0.14349],"tcp_start":[0.49689,0.08636,0.14356],"tcp_to_object_dist_end":0.11185,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `0188121de1b8142d5ff7a7406b62c43adf6da5520b986a997e46ef53b7d11bf9`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.88679,"average_solve_count":53.0,"average_success_count":53.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_entry.approach_speed":0.08775,"push_through_channel.force_threshold":22.16484,"push_through_channel.max_time":8.64609,"push_through_channel.push_speed":0.04809},"optimized_scores":{"best_composite_score":-0.04354,"best_fitness_score":0.15646,"best_task_score":0.00019},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.52503,0.02209,0.05992],"force_p95":43.75725,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":44.14519,"mean_force":38.38399,"phase_index":1.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49684,0.08647,0.14362]},{"body_a":"peg","body_b":"channel_base_body","contact_count":623.0,"contact_point_centroid":[0.49432,0.05889,0.00936],"force_p95":0.56252,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.20518,"mean_force":0.56968,"phase_index":0.0,"phase_name":"approach_entry","phase_type":"approach","tcp_position_centroid":[0.48844,0.13561,0.2066]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46807,0.05895,0.03796],"force_p95":1.19991,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.42382,"mean_force":0.50385,"phase_index":0.0,"phase_name":"approach_entry","phase_type":"approach","tcp_position_centroid":[0.48953,0.17772,0.27358]},{"body_a":"peg","body_b":"channel_base_body","contact_count":15.0,"contact_point_centroid":[0.49249,0.06032,0.00939],"force_p95":0.54997,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55025,"mean_force":0.54589,"phase_index":1.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.4971,0.087,0.14443]}],"total_contact_groups":4},"final_pose_error":0.19594,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49421,0.05885,0.03388],"final_tcp_position":[0.49681,0.08637,0.14346],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.46685,0.05894,0.04]},"peak_contact_force":44.14519,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":652.0,"n_steps_budget":1000.0,"object_pos_end":[0.49426,0.05893,0.03388],"object_pos_start":[0.46685,0.05894,0.04],"object_to_goal_dist_end":0.13919,"object_to_goal_dist_start":0.14284,"object_z_max":0.04001,"peak_contact_force":0.55061,"phase_name":"approach_entry","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":658.0,"raw_peak_contact_force":4.20518,"subtask_id":"reach_entry","tcp_end":[0.49742,0.08767,0.14548],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11528,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":15.0,"n_steps_budget":1000.0,"object_pos_end":[0.49411,0.05882,0.03388],"object_pos_start":[0.49426,0.05893,0.03388],"object_to_goal_dist_end":0.13908,"object_to_goal_dist_start":0.13919,"object_z_max":0.03388,"peak_contact_force":44.14519,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":18.0,"raw_peak_contact_force":44.14519,"subtask_id":"traverse_channel","tcp_end":[0.49681,0.08637,0.14346],"tcp_start":[0.49684,0.0864,0.14351],"tcp_to_object_dist_end":0.11302,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```