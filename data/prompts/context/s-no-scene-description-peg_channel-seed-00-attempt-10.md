## Search State

- **Seed**: 0
- **Iteration**: 11 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 10 | approach → push | linear_cartesian | linear_cartesian | position_control | impedance_control | pose_tolerance | force_exceeded | 6 | -0.0724 | 0.11 | ❌ rejected |
| 9 | approach → push → lift | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.0311 | 0.23 | ❌ rejected |
| 8 | approach → push → lift | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | 4 | -0.2249 | 0.00 | ❌ rejected |
| 7 | approach → push | linear_cartesian | impedance_motion | position_control | admittance_control | pose_tolerance | pose_tolerance | 3 | -0.0823 | 0.00 | ❌ rejected |
| 6 | insert → approach → push → retract → lift → insert | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | linear_cartesian | impedance_motion | impedance_control | force_threshold_switch | impedance_control | position_control | position_control | admittance_control | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | 5 | 0.1593 | 0.72 | ❌ rejected |

**Proposal policy**: task_score is 0.11 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.072) — your mutation base

```yaml
skill: peg_channel
phases:
- id: insert_1
  type: insert
  generator: linear_cartesian
  control: impedance_control
  termination: force_exceeded
- id: approach_1
  type: approach
  generator: linear_cartesian
  control: force_threshold_switch
  termination: pose_tolerance
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
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
- id: retract_1
  type: retract
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    retract_height:
      type: scalar
      range:
      - 0.05
      - 0.2
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
- id: lift_1
  type: lift
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
- id: insert_2
  type: insert
  generator: impedance_motion
  control: admittance_control
  termination: force_exceeded

```

## Design Metrics

- **Composite score**: -0.072
- **task_score** (E): 0.106
- **fitness_score**: 0.228  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.300

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_peg | 1.00 | 1.00 | 0.2439 |
| push_through_channel | 0.33 | 1.00 | 0.0347 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_peg | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.494, 0.129, 0.068) | (0.498, 0.080, 0.040)→(0.500, 0.081, 0.034) | 0.161→0.161 | 1.00 / 1.000 | 0.548 | 2.179 |
| push_through_channel | push | 0.33 / guard_failure | (0.494, 0.129, 0.068)→(0.497, 0.099, 0.060) | (0.500, 0.081, 0.034)→(0.500, 0.064, 0.031) | 0.161→0.144 | 1.00 / 1.667 | 413.281 | 415.158 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.317
- alignment_error: None
- force_efficiency: 0.842
- terminal_score: 0.317
- phase_score: 0.422
- phase_breakdown.traverse_channel_score: 0.256
- phase_breakdown.reach_entrance_score: 0.811

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.380
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.317
- **Median Q (composite search score)**: -0.148
- **K-run variance**: 0.0117
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Parameters at upper bound**: push_through_channel.wiggle_offset
- **Final σ (mean)**: 0.250


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `d6915c31707ac435a9367b840736087e39a7a48adfeb36a4f94b6b3ae57cce94`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `19172182883d287409b73cab43749e937e65f1ca1d4501d52b4a913a881aad36`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.98462,"average_solve_count":65.0,"average_success_count":65.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_speed":0.08621,"approach_peg.approach_y_offset":0.04661,"push_through_channel.push_distance":0.15082,"push_through_channel.push_force_threshold":28.40718,"push_through_channel.push_speed":0.05594,"push_through_channel.wiggle_offset":0.01},"optimized_scores":{"best_composite_score":-0.14927,"best_fitness_score":0.15073,"best_task_score":0.0002},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":1.0,"contact_point_centroid":[0.52542,0.10368,0.05982],"force_p95":842.54324,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":842.54324,"mean_force":842.54324,"phase_index":1.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.51341,0.10349,0.06107]},{"body_a":"peg","body_b":"channel_base_body","contact_count":757.0,"contact_point_centroid":[0.50365,0.06162,0.00935],"force_p95":0.59646,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.17216,"mean_force":0.55727,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.50252,0.15493,0.17983]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":19.0,"contact_point_centroid":[0.52623,0.06158,0.03217],"force_p95":0.5921,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.62339,"mean_force":0.34148,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49969,0.19916,0.29851]},{"body_a":"peg","body_b":"channel_base_body","contact_count":10.0,"contact_point_centroid":[0.50669,0.05993,0.00938],"force_p95":0.55555,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55748,"mean_force":0.54722,"phase_index":1.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50976,0.10835,0.06503]}],"total_contact_groups":4},"final_pose_error":0.14215,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50375,0.06155,0.03379],"final_tcp_position":[0.51379,0.10266,0.06011],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51096,0.06158,0.04]},"peak_contact_force":842.54324,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":780.0,"n_steps_budget":1000.0,"object_pos_end":[0.50379,0.06157,0.03379],"object_pos_start":[0.51096,0.06158,0.04],"object_to_goal_dist_end":0.14176,"object_to_goal_dist_start":0.14201,"object_z_max":0.04,"peak_contact_force":0.5465,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":776.0,"raw_peak_contact_force":2.17216,"subtask_id":"reach_entrance","tcp_end":[0.5066,0.1123,0.06776],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.06111,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":10.0,"n_steps_budget":1000.0,"object_pos_end":[0.50375,0.06155,0.03379],"object_pos_start":[0.50379,0.06157,0.03379],"object_to_goal_dist_end":0.14173,"object_to_goal_dist_start":0.14176,"object_z_max":0.03379,"peak_contact_force":842.54324,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":11.0,"raw_peak_contact_force":842.54324,"subtask_id":"traverse_channel","tcp_end":[0.51379,0.10266,0.06011],"tcp_start":[0.5066,0.1123,0.06776],"tcp_to_object_dist_end":0.04984,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `f24211f27d4adabdef509c8ed61621317fdbcaa86fc9ac888f85a717335bb714`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.02548,"average_solve_count":157.0,"average_success_count":157.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_speed":0.02808,"approach_peg.approach_y_offset":0.04491,"push_through_channel.push_distance":0.17146,"push_through_channel.push_force_threshold":39.00708,"push_through_channel.push_speed":0.04059,"push_through_channel.wiggle_offset":0.00654},"optimized_scores":{"best_composite_score":0.08033,"best_fitness_score":0.38033,"best_task_score":0.3172},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":993.0,"contact_point_centroid":[0.50157,0.10244,0.00973],"force_p95":3.46337,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.9016,"mean_force":1.66045,"phase_index":1.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49239,0.12517,0.06028]},{"body_a":"attachment","body_b":"peg","contact_count":507.0,"contact_point_centroid":[0.49902,0.11483,0.05512],"force_p95":3.98176,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":7.5213,"mean_force":2.30701,"phase_index":1.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49418,0.11487,0.06606]},{"body_a":"peg","body_b":"channel_base_body","contact_count":757.0,"contact_point_centroid":[0.50094,0.11597,0.00939],"force_p95":0.60823,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.92055,"mean_force":0.55405,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49775,0.18051,0.18213]}],"total_contact_groups":3},"final_pose_error":0.10219,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50228,0.06529,0.02669],"final_tcp_position":[0.49403,0.09262,0.06683],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50095,0.11604,0.04]},"peak_contact_force":7.9016,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":773.0,"n_steps_budget":1000.0,"object_pos_end":[0.50098,0.11604,0.0338],"object_pos_start":[0.50095,0.11604,0.04],"object_to_goal_dist_end":0.19614,"object_to_goal_dist_start":0.19604,"object_z_max":0.04,"peak_contact_force":0.55827,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":757.0,"raw_peak_contact_force":1.92055,"subtask_id":"reach_entrance","tcp_end":[0.49723,0.16211,0.06901],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.0581,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50228,0.06529,0.02669],"object_pos_start":[0.50098,0.11604,0.0338],"object_to_goal_dist_end":0.14591,"object_to_goal_dist_start":0.19614,"object_z_max":0.04068,"peak_contact_force":2.27104,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1500.0,"raw_peak_contact_force":7.9016,"subtask_id":"traverse_channel","tcp_end":[0.49403,0.09262,0.06683],"tcp_start":[0.49723,0.16211,0.06901],"tcp_to_object_dist_end":0.04926,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `d098a7862ff18c9bbe982af3446a89a0fa6bcfa8790d7d955f65b2375d67a881`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.36667,"average_solve_count":90.0,"average_success_count":90.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_speed":0.06112,"approach_peg.approach_y_offset":0.04374,"push_through_channel.push_distance":0.16371,"push_through_channel.push_force_threshold":25.05999,"push_through_channel.push_speed":0.06365,"push_through_channel.wiggle_offset":0.00385},"optimized_scores":{"best_composite_score":-0.14838,"best_fitness_score":0.15162,"best_task_score":0.00059},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_right_wall","contact_count":1.0,"contact_point_centroid":[0.47433,0.10212,0.05952],"force_p95":395.02852,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":395.02852,"mean_force":395.02852,"phase_index":1.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.48431,0.10146,0.05404]},{"body_a":"peg","body_b":"channel_base_body","contact_count":779.0,"contact_point_centroid":[0.49541,0.06387,0.00938],"force_p95":0.56399,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44546,"mean_force":0.55646,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.48808,0.15455,0.17977]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":28.0,"contact_point_centroid":[0.47133,0.06388,0.03676],"force_p95":0.92436,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.16907,"mean_force":0.37063,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49933,0.1988,0.29735]},{"body_a":"peg","body_b":"channel_base_body","contact_count":15.0,"contact_point_centroid":[0.48767,0.06107,0.0094],"force_p95":0.54897,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54976,"mean_force":0.54486,"phase_index":1.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.48223,0.10637,0.06288]}],"total_contact_groups":4},"final_pose_error":0.1544,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49531,0.06373,0.03399],"final_tcp_position":[0.48434,0.10108,0.05242],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"peak_contact_force":395.02852,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":806.0,"n_steps_budget":1000.0,"object_pos_end":[0.4951,0.06413,0.03399],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.14434,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"peak_contact_force":0.53816,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":807.0,"raw_peak_contact_force":2.44546,"subtask_id":"reach_entrance","tcp_end":[0.47833,0.11184,0.06843],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.06119,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":15.0,"n_steps_budget":1000.0,"object_pos_end":[0.49531,0.06373,0.03399],"object_pos_start":[0.4951,0.06413,0.03399],"object_to_goal_dist_end":0.14393,"object_to_goal_dist_start":0.14434,"object_z_max":0.03399,"peak_contact_force":395.02852,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":16.0,"raw_peak_contact_force":395.02852,"subtask_id":"traverse_channel","tcp_end":[0.48434,0.10108,0.05242],"tcp_start":[0.47833,0.11184,0.06843],"tcp_to_object_dist_end":0.04307,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```