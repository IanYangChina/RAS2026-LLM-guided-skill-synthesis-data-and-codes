## Search State

- **Seed**: 0
- **Iteration**: 10 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 9 | approach → push → lift | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.0311 | 0.23 | ❌ rejected |
| 8 | approach → push → lift | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | 4 | -0.2249 | 0.00 | ❌ rejected |
| 7 | approach → push | linear_cartesian | impedance_motion | position_control | admittance_control | pose_tolerance | pose_tolerance | 3 | -0.0823 | 0.00 | ❌ rejected |
| 6 | insert → approach → push → retract → lift → insert | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | linear_cartesian | impedance_motion | impedance_control | force_threshold_switch | impedance_control | position_control | position_control | admittance_control | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | 5 | 0.1593 | 0.72 | ❌ rejected |
| 5 | insert → approach → push → retract → lift → insert | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | linear_cartesian | impedance_motion | impedance_control | force_threshold_switch | impedance_control | position_control | position_control | admittance_control | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | 5 | 0.1644 | 0.77 | ✅ accepted |

**Proposal policy**: task_score is 0.23 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.031) — your mutation base

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

- **Composite score**: 0.031
- **task_score** (E): 0.226
- **fitness_score**: 0.311  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.280

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_to_peg_side | 1.00 | 1.00 | 0.2491 |
| push_through_channel | 0.67 | 1.00 | 0.0702 |
| lift_out | 1.00 | 1.00 | 0.0805 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_to_peg_side | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.494, 0.145, 0.059) | (0.498, 0.080, 0.040)→(0.500, 0.080, 0.034) | 0.161→0.161 | 1.00 / 1.000 | 0.536 | 2.179 |
| push_through_channel | push | 0.67 / step_budget | (0.494, 0.145, 0.059)→(0.493, 0.075, 0.055) | (0.500, 0.080, 0.034)→(0.498, 0.041, 0.027) | 0.161→0.122 | 1.00 / 1.333 | 21.249 | 42.300 |
| lift_out | lift | 1.00 / step_budget | (0.500, 0.048, 0.054)→(0.497, 0.048, 0.134) | (0.499, 0.030, 0.024)→(0.500, 0.032, 0.024) | 0.111→0.113 | 1.00 / 1.500 | 1.402 | 7.750 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.357
- alignment_error: None
- force_efficiency: 0.319
- terminal_score: 0.326
- phase_score: 0.500
- phase_breakdown.traverse_channel_score: 0.426
- phase_breakdown.reach_entrance_score: 0.673

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.430
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.351
- **Median Q (composite search score)**: 0.100
- **K-run variance**: 0.0182
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.288


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.43158,"average_solve_count":190.0,"average_success_count":190.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_peg_side.approach_speed":0.07295,"lift_out.lift_speed":0.06629,"push_through_channel.max_push_force":34.24275,"push_through_channel.push_distance":0.14373,"push_through_channel.push_speed":0.0356},"optimized_scores":{"best_composite_score":0.15041,"best_fitness_score":0.43041,"best_task_score":0.32637},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":79.0,"contact_point_centroid":[0.50348,0.04906,0.00925],"force_p95":6.83258,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":34.07008,"mean_force":2.33617,"phase_index":1.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50443,0.10062,0.05477]},{"body_a":"attachment","body_b":"peg","contact_count":19.0,"contact_point_centroid":[0.50664,0.05539,0.0533],"force_p95":32.50817,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":33.91294,"mean_force":7.00923,"phase_index":1.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50444,0.06686,0.05378]},{"body_a":"peg","body_b":"channel_base_body","contact_count":265.0,"contact_point_centroid":[0.49984,0.00263,0.00809],"force_p95":0.73813,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.36367,"mean_force":0.71663,"phase_index":2.0,"phase_name":"lift_out","phase_type":"lift","tcp_position_centroid":[0.50178,0.03238,0.09237]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":12.0,"contact_point_centroid":[0.47489,0.02542,0.02559],"force_p95":6.83497,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.94248,"mean_force":3.02219,"phase_index":2.0,"phase_name":"lift_out","phase_type":"lift","tcp_position_centroid":[0.50326,0.02976,0.05625]},{"body_a":"peg","body_b":"channel_base_body","contact_count":468.0,"contact_point_centroid":[0.5036,0.06155,0.00934],"force_p95":0.58545,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.17216,"mean_force":0.56376,"phase_index":0.0,"phase_name":"approach_to_peg_side","phase_type":"approach","tcp_position_centroid":[0.50271,0.16272,0.17468]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":19.0,"contact_point_centroid":[0.52623,0.06158,0.03217],"force_p95":0.5921,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.62339,"mean_force":0.34148,"phase_index":0.0,"phase_name":"approach_to_peg_side","phase_type":"approach","tcp_position_centroid":[0.49979,0.19914,0.29795]}],"total_contact_groups":6},"final_pose_error":0.01988,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50414,0.00439,0.0241],"final_tcp_position":[0.50148,0.03315,0.13383],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51096,0.06158,0.04]},"peak_contact_force":34.07008,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":491.0,"n_steps_budget":1000.0,"object_pos_end":[0.50374,0.06159,0.03378],"object_pos_start":[0.51096,0.06158,0.04],"object_to_goal_dist_end":0.14177,"object_to_goal_dist_start":0.14201,"object_z_max":0.04,"peak_contact_force":0.54805,"phase_name":"approach_to_peg_side","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":487.0,"raw_peak_contact_force":2.17216,"subtask_id":"reach_entrance","tcp_end":[0.50657,0.12779,0.0583],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.07066,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":114.0,"n_steps_budget":1000.0,"object_pos_end":[0.49784,0.00035,0.02695],"object_pos_start":[0.50374,0.06159,0.03378],"object_to_goal_dist_end":0.08143,"object_to_goal_dist_start":0.14177,"object_z_max":0.04439,"peak_contact_force":0.95387,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":98.0,"raw_peak_contact_force":34.07008,"subtask_id":"traverse_channel","tcp_end":[0.50464,0.03343,0.05346],"tcp_start":[0.50657,0.12779,0.0583],"tcp_to_object_dist_end":0.04294,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":265.0,"n_steps_budget":960.0,"object_pos_end":[0.50414,0.00439,0.0241],"object_pos_start":[0.49784,0.00035,0.02695],"object_to_goal_dist_end":0.08597,"object_to_goal_dist_start":0.08143,"object_z_max":0.02695,"peak_contact_force":2.2154,"phase_name":"lift_out","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":277.0,"raw_peak_contact_force":7.36367,"tcp_end":[0.50148,0.03315,0.13383],"tcp_start":[0.50464,0.03343,0.05346],"tcp_to_object_dist_end":0.11348,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `f24211f27d4adabdef509c8ed61621317fdbcaa86fc9ac888f85a717335bb714`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.45679,"average_solve_count":162.0,"average_success_count":162.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_peg_side.approach_speed":0.09353,"lift_out.lift_speed":0.0845,"push_through_channel.max_push_force":35.76254,"push_through_channel.push_distance":0.16398,"push_through_channel.push_speed":0.04156},"optimized_scores":{"best_composite_score":0.10023,"best_fitness_score":0.38023,"best_task_score":0.35149},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":21.0,"contact_point_centroid":[0.50216,0.11001,0.05326],"force_p95":28.42674,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":30.57661,"mean_force":5.73316,"phase_index":1.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49544,0.11906,0.0547]},{"body_a":"peg","body_b":"channel_base_body","contact_count":90.0,"contact_point_centroid":[0.5015,0.0942,0.00863],"force_p95":11.75967,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":30.48163,"mean_force":2.04352,"phase_index":1.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49545,0.13334,0.05535]},{"body_a":"peg","body_b":"channel_base_body","contact_count":254.0,"contact_point_centroid":[0.49606,0.06018,0.00803],"force_p95":0.77966,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.1354,"mean_force":0.68248,"phase_index":2.0,"phase_name":"lift_out","phase_type":"lift","tcp_position_centroid":[0.49297,0.06116,0.09334]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":11.0,"contact_point_centroid":[0.47498,0.03701,0.0244],"force_p95":7.76102,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.84884,"mean_force":2.35208,"phase_index":2.0,"phase_name":"lift_out","phase_type":"lift","tcp_position_centroid":[0.49283,0.06114,0.08299]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":3.0,"contact_point_centroid":[0.52514,0.0692,0.05629],"force_p95":2.57148,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.60717,"mean_force":2.23444,"phase_index":1.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49547,0.12035,0.05471]},{"body_a":"peg","body_b":"channel_base_body","contact_count":443.0,"contact_point_centroid":[0.50096,0.11597,0.00938],"force_p95":0.62324,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.92055,"mean_force":0.56111,"phase_index":0.0,"phase_name":"approach_to_peg_side","phase_type":"approach","tcp_position_centroid":[0.49818,0.18806,0.17678]}],"total_contact_groups":6},"final_pose_error":0.01974,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49621,0.0598,0.02422],"final_tcp_position":[0.49267,0.06194,0.13483],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50095,0.11604,0.04]},"peak_contact_force":30.57661,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":459.0,"n_steps_budget":1000.0,"object_pos_end":[0.50094,0.11603,0.03393],"object_pos_start":[0.50095,0.11604,0.04],"object_to_goal_dist_end":0.19613,"object_to_goal_dist_start":0.19604,"object_z_max":0.04,"peak_contact_force":0.5128,"phase_name":"approach_to_peg_side","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":443.0,"raw_peak_contact_force":1.92055,"subtask_id":"reach_entrance","tcp_end":[0.49756,0.17714,0.0592],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.06621,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":130.0,"n_steps_budget":1000.0,"object_pos_end":[0.49994,0.05989,0.02156],"object_pos_start":[0.50094,0.11603,0.03393],"object_to_goal_dist_end":0.1411,"object_to_goal_dist_start":0.19613,"object_z_max":0.04426,"peak_contact_force":0.53998,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":114.0,"raw_peak_contact_force":30.57661,"subtask_id":"traverse_channel","tcp_end":[0.4958,0.06238,0.05431],"tcp_start":[0.49756,0.17714,0.0592],"tcp_to_object_dist_end":0.0331,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":254.0,"n_steps_budget":750.0,"object_pos_end":[0.49621,0.0598,0.02422],"object_pos_start":[0.49994,0.05989,0.02156],"object_to_goal_dist_end":0.14074,"object_to_goal_dist_start":0.1411,"object_z_max":0.02478,"peak_contact_force":0.58772,"phase_name":"lift_out","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":265.0,"raw_peak_contact_force":8.1354,"tcp_end":[0.49267,0.06194,0.13483],"tcp_start":[0.4958,0.06238,0.05431],"tcp_to_object_dist_end":0.11069,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `d098a7862ff18c9bbe982af3446a89a0fa6bcfa8790d7d955f65b2375d67a881`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.54878,"average_solve_count":82.0,"average_success_count":82.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_peg_side.approach_speed":0.06984,"lift_out.lift_speed":0.03465,"push_through_channel.max_push_force":29.13711,"push_through_channel.push_distance":0.10193,"push_through_channel.push_speed":0.01755},"optimized_scores":{"best_composite_score":-0.15743,"best_fitness_score":0.12257,"best_task_score":0.00065},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_right_wall","contact_count":1.0,"contact_point_centroid":[0.47497,0.12,0.05993],"force_p95":62.25331,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":62.25331,"mean_force":62.25331,"phase_index":1.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.47893,0.12952,0.05771]},{"body_a":"peg","body_b":"channel_base_body","contact_count":463.0,"contact_point_centroid":[0.4955,0.06402,0.00937],"force_p95":0.59674,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44546,"mean_force":0.56388,"phase_index":0.0,"phase_name":"approach_to_peg_side","phase_type":"approach","tcp_position_centroid":[0.48871,0.16342,0.1737]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":28.0,"contact_point_centroid":[0.47133,0.06388,0.03676],"force_p95":0.92436,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.16907,"mean_force":0.37063,"phase_index":0.0,"phase_name":"approach_to_peg_side","phase_type":"approach","tcp_position_centroid":[0.49933,0.19861,0.29591]},{"body_a":"peg","body_b":"channel_base_body","contact_count":3.0,"contact_point_centroid":[0.47854,0.05859,0.0094],"force_p95":0.54878,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54911,"mean_force":0.54672,"phase_index":1.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.47914,0.12966,0.05811]}],"total_contact_groups":4},"final_pose_error":0.10155,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49498,0.06372,0.03394],"final_tcp_position":[0.47876,0.12942,0.05741],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"peak_contact_force":62.25331,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":490.0,"n_steps_budget":1000.0,"object_pos_end":[0.4949,0.06387,0.03394],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.14409,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"peak_contact_force":0.54565,"phase_name":"approach_to_peg_side","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":491.0,"raw_peak_contact_force":2.44546,"subtask_id":"reach_entrance","tcp_end":[0.47933,0.1298,0.05853],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.07206,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.49498,0.06372,0.03394],"object_pos_start":[0.4949,0.06387,0.03394],"object_to_goal_dist_end":0.14393,"object_to_goal_dist_start":0.14409,"object_z_max":0.03394,"peak_contact_force":62.25331,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":4.0,"raw_peak_contact_force":62.25331,"subtask_id":"traverse_channel","tcp_end":[0.47876,0.12942,0.05741],"tcp_start":[0.47933,0.1298,0.05853],"tcp_to_object_dist_end":0.07163,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```