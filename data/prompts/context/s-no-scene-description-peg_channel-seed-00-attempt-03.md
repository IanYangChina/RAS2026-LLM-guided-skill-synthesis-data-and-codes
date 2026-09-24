## Search State

- **Seed**: 0
- **Iteration**: 4 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 3 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 9 | -0.1659 | 0.01 | ❌ rejected |
| 2 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 10 | -0.2602 | 0.00 | ❌ rejected |
| 1 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 10 | -0.2420 | 0.01 | ❌ rejected |
| 0 | insert → approach → push → retract → lift → insert | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | linear_cartesian | impedance_motion | impedance_control | force_threshold_switch | impedance_control | position_control | position_control | admittance_control | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | 5 | 0.1857 | 0.74 | ✅ accepted |

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

## Current Skill (Q=-0.166) — your mutation base

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

- **Composite score**: -0.166
- **task_score** (E): 0.005
- **fitness_score**: 0.094  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
  → CMA-ES cannot optimise this structure (shaped reward also near zero)
- **Termination Fidelity** (C): 0.250
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.510

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1922 |
| contact_1 | 1.00 | 1.00 | 0.0859 |
| push_1 | 0.00 | 1.00 | 0.0001 |
| retract_1 | 1.00 | 1.00 | 0.1607 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.495, 0.088, 0.146) | (0.498, 0.080, 0.040)→(0.500, 0.081, 0.034) | 0.161→0.161 | 1.00 / 1.000 | 0.555 | 2.179 |
| contact_1 | contact | 1.00 / force_exceeded | (0.495, 0.088, 0.146)→(0.496, 0.081, 0.060) | (0.500, 0.081, 0.034)→(0.500, 0.080, 0.034) | 0.161→0.161 | 1.00 / 2.000 | 24.651 | 24.651 |
| push_1 | push | 0.00 / guard_failure | (0.495, 0.079, 0.060)→(0.495, 0.079, 0.060) | (0.500, 0.080, 0.034)→(0.499, 0.079, 0.034) | 0.161→0.160 | 1.00 / 2.000 | 37.262 | 48.526 |
| retract_1 | retract | 1.00 / step_budget | (0.495, 0.079, 0.060)→(0.497, -0.061, 0.139) | (0.499, 0.079, 0.034)→(0.499, 0.079, 0.034) | 0.159→0.160 | 1.00 / 1.000 | 0.561 | 35.366 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.007
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.006
- phase_score: 0.157
- phase_breakdown.reach_pre_contact_score: 0.200
- phase_breakdown.push_to_goal_score: 0.139

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.097
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.006
- **Median Q (composite search score)**: -0.164
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Parameters at upper bound**: retract_1.retract_height
- **Final σ (mean)**: 0.359


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.66129,"average_solve_count":124.0,"average_success_count":124.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.12122,"contact_1.descend_force_threshold":13.38885,"contact_1.descend_speed":0.06304,"push_1.push_distance":0.05614,"push_1.push_speed":0.03815,"push_1.push_tolerance":0.0225,"retract_1.retract_height":0.2,"retract_1.retract_speed":0.06958,"retract_1.retract_tolerance":0.02821},"optimized_scores":{"best_composite_score":-0.16326,"best_fitness_score":0.09674,"best_task_score":0.00631},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":17.0,"contact_point_centroid":[0.49852,0.04884,0.00931],"force_p95":43.72609,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":50.77672,"mean_force":29.3709,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50012,0.06141,0.05977]},{"body_a":"attachment","body_b":"peg","contact_count":17.0,"contact_point_centroid":[0.51197,0.06158,0.05842],"force_p95":43.26648,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":50.30535,"mean_force":28.91787,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50012,0.06141,0.05977]},{"body_a":"peg","body_b":"channel_base_body","contact_count":440.0,"contact_point_centroid":[0.5038,0.06164,0.00938],"force_p95":0.55003,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":41.73931,"mean_force":0.64039,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.5027,0.06561,0.10167]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.5123,0.06141,0.05871],"force_p95":41.07598,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":41.07598,"mean_force":41.07598,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50045,0.06209,0.06041]},{"body_a":"peg","body_b":"channel_base_body","contact_count":426.0,"contact_point_centroid":[0.50289,0.06047,0.00943],"force_p95":0.60831,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":36.80056,"mean_force":0.7433,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4973,0.01058,0.10946]},{"body_a":"attachment","body_b":"peg","contact_count":14.0,"contact_point_centroid":[0.51123,0.06058,0.05888],"force_p95":31.98744,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":36.40921,"mean_force":6.16252,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4994,0.05973,0.06021]},{"body_a":"peg","body_b":"channel_base_body","contact_count":637.0,"contact_point_centroid":[0.50362,0.06157,0.00935],"force_p95":0.58205,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.17216,"mean_force":0.55931,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50289,0.13258,0.21824]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":19.0,"contact_point_centroid":[0.52623,0.06158,0.03217],"force_p95":0.5921,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.62339,"mean_force":0.34148,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49971,0.19875,0.29868]}],"total_contact_groups":8},"final_pose_error":0.01969,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50306,0.06042,0.03422],"final_tcp_position":[0.49724,-0.06075,0.1369],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51096,0.06158,0.04]},"peak_contact_force":50.77672,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":660.0,"n_steps_budget":1000.0,"object_pos_end":[0.50376,0.0616,0.03378],"object_pos_start":[0.51096,0.06158,0.04],"object_to_goal_dist_end":0.14179,"object_to_goal_dist_start":0.14201,"object_z_max":0.04,"peak_contact_force":0.54549,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":656.0,"raw_peak_contact_force":2.17216,"subtask_id":"reach_pre_contact","tcp_end":[0.50726,0.06939,0.14467],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11122,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":440.0,"n_steps_budget":900.0,"object_pos_end":[0.50383,0.06158,0.0338],"object_pos_start":[0.50376,0.0616,0.03378],"object_to_goal_dist_end":0.14177,"object_to_goal_dist_start":0.14179,"object_z_max":0.03378,"peak_contact_force":41.73931,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":441.0,"raw_peak_contact_force":41.73931,"subtask_id":"reach_pre_contact","tcp_end":[0.5005,0.06208,0.06026],"tcp_start":[0.50726,0.06939,0.14467],"tcp_to_object_dist_end":0.02668,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":17.0,"n_steps_budget":930.0,"object_pos_end":[0.50337,0.06085,0.03399],"object_pos_start":[0.50383,0.06158,0.0338],"object_to_goal_dist_end":0.14102,"object_to_goal_dist_start":0.14177,"object_z_max":0.03402,"peak_contact_force":38.88414,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":34.0,"raw_peak_contact_force":50.77672,"subtask_id":"push_to_goal","tcp_end":[0.49994,0.06024,0.05955],"tcp_start":[0.49993,0.06033,0.05956],"tcp_to_object_dist_end":0.0258,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":426.0,"n_steps_budget":1000.0,"object_pos_end":[0.50306,0.06042,0.03422],"object_pos_start":[0.50341,0.06071,0.03404],"object_to_goal_dist_end":0.14057,"object_to_goal_dist_start":0.14088,"object_z_max":0.03483,"peak_contact_force":0.54158,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":440.0,"raw_peak_contact_force":36.80056,"subtask_id":"push_to_goal","tcp_end":[0.49724,-0.06075,0.1369],"tcp_start":[0.49994,0.06024,0.05955],"tcp_to_object_dist_end":0.15893,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `f24211f27d4adabdef509c8ed61621317fdbcaa86fc9ac888f85a717335bb714`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.77311,"average_solve_count":119.0,"average_success_count":119.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.09714,"contact_1.descend_force_threshold":11.6958,"contact_1.descend_speed":0.0794,"push_1.push_distance":0.08919,"push_1.push_speed":0.03869,"push_1.push_tolerance":0.01677,"retract_1.retract_height":0.19979,"retract_1.retract_speed":0.0965,"retract_1.retract_tolerance":0.04669},"optimized_scores":{"best_composite_score":-0.1705,"best_fitness_score":0.0895,"best_task_score":0.00454},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":18.0,"contact_point_centroid":[0.49423,0.10229,0.00934],"force_p95":42.2439,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":49.22826,"mean_force":30.30409,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49662,0.11514,0.05997]},{"body_a":"attachment","body_b":"peg","contact_count":18.0,"contact_point_centroid":[0.50846,0.11572,0.0586],"force_p95":41.78382,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":48.76596,"mean_force":29.81959,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49662,0.11514,0.05997]},{"body_a":"peg","body_b":"channel_base_body","contact_count":568.0,"contact_point_centroid":[0.49977,0.11504,0.00943],"force_p95":0.6187,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":35.40449,"mean_force":0.67094,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49512,0.04333,0.12505]},{"body_a":"attachment","body_b":"peg","contact_count":12.0,"contact_point_centroid":[0.50772,0.11477,0.05896],"force_p95":27.82927,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":35.00575,"mean_force":6.14498,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49595,0.11335,0.0603]},{"body_a":"peg","body_b":"channel_base_body","contact_count":448.0,"contact_point_centroid":[0.50093,0.11604,0.00942],"force_p95":0.61034,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":18.14119,"mean_force":0.5817,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49625,0.11853,0.10269]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.50879,0.11567,0.05891],"force_p95":17.60702,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":17.60702,"mean_force":17.60702,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49692,0.1159,0.06063]},{"body_a":"peg","body_b":"channel_base_body","contact_count":520.0,"contact_point_centroid":[0.50083,0.11598,0.00939],"force_p95":0.61438,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.92055,"mean_force":0.55822,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49819,0.16012,0.22106]}],"total_contact_groups":7},"final_pose_error":0.01982,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50023,0.11531,0.03385],"final_tcp_position":[0.49702,-0.06073,0.14354],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50095,0.11604,0.04]},"peak_contact_force":49.22826,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":536.0,"n_steps_budget":1000.0,"object_pos_end":[0.50101,0.11604,0.03386],"object_pos_start":[0.50095,0.11604,0.04],"object_to_goal_dist_end":0.19614,"object_to_goal_dist_start":0.19604,"object_z_max":0.04,"peak_contact_force":0.57046,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":520.0,"raw_peak_contact_force":1.92055,"subtask_id":"reach_pre_contact","tcp_end":[0.49796,0.12171,0.14734],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11367,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":448.0,"n_steps_budget":750.0,"object_pos_end":[0.50101,0.11598,0.03392],"object_pos_start":[0.50101,0.11604,0.03386],"object_to_goal_dist_end":0.19608,"object_to_goal_dist_start":0.19614,"object_z_max":0.03395,"peak_contact_force":18.14119,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":449.0,"raw_peak_contact_force":18.14119,"subtask_id":"reach_pre_contact","tcp_end":[0.49699,0.11591,0.06048],"tcp_start":[0.49796,0.12171,0.14734],"tcp_to_object_dist_end":0.02686,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":18.0,"n_steps_budget":1000.0,"object_pos_end":[0.50038,0.11505,0.03413],"object_pos_start":[0.50101,0.11598,0.03392],"object_to_goal_dist_end":0.19514,"object_to_goal_dist_start":0.19608,"object_z_max":0.03416,"peak_contact_force":37.40616,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":36.0,"raw_peak_contact_force":49.22826,"subtask_id":"push_to_goal","tcp_end":[0.49649,0.11383,0.05976],"tcp_start":[0.49648,0.11392,0.05977],"tcp_to_object_dist_end":0.02595,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":568.0,"n_steps_budget":1000.0,"object_pos_end":[0.50023,0.11531,0.03385],"object_pos_start":[0.50044,0.11491,0.03418],"object_to_goal_dist_end":0.19541,"object_to_goal_dist_start":0.195,"object_z_max":0.03476,"peak_contact_force":0.59873,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":580.0,"raw_peak_contact_force":35.40449,"subtask_id":"push_to_goal","tcp_end":[0.49702,-0.06073,0.14354],"tcp_start":[0.49649,0.11383,0.05976],"tcp_to_object_dist_end":0.20744,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `d098a7862ff18c9bbe982af3446a89a0fa6bcfa8790d7d955f65b2375d67a881`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.30732,"average_solve_count":205.0,"average_success_count":205.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.08145,"contact_1.descend_force_threshold":11.37527,"contact_1.descend_speed":0.07705,"push_1.push_distance":0.11005,"push_1.push_speed":0.06355,"push_1.push_tolerance":0.00608,"retract_1.retract_height":0.19875,"retract_1.retract_speed":0.02435,"retract_1.retract_tolerance":0.0267},"optimized_scores":{"best_composite_score":-0.16395,"best_fitness_score":0.09605,"best_task_score":0.00513},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":22.0,"contact_point_centroid":[0.48782,0.04885,0.00946],"force_p95":40.05947,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":45.57381,"mean_force":33.61655,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48951,0.06318,0.06029]},{"body_a":"attachment","body_b":"peg","contact_count":22.0,"contact_point_centroid":[0.50128,0.06444,0.05902],"force_p95":39.61522,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":45.12958,"mean_force":33.17022,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48951,0.06318,0.06029]},{"body_a":"peg","body_b":"channel_base_body","contact_count":464.0,"contact_point_centroid":[0.494,0.06197,0.00941],"force_p95":0.65453,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":33.89407,"mean_force":0.92227,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4905,0.01187,0.10998]},{"body_a":"attachment","body_b":"peg","contact_count":19.0,"contact_point_centroid":[0.50068,0.06294,0.05937],"force_p95":31.51741,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":33.47694,"mean_force":9.24214,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48897,0.06105,0.0606]},{"body_a":"peg","body_b":"channel_base_body","contact_count":528.0,"contact_point_centroid":[0.49504,0.06411,0.0094],"force_p95":0.55069,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":14.07181,"mean_force":0.57091,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48318,0.0679,0.10124]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.50157,0.06411,0.05908],"force_p95":13.59428,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":13.59428,"mean_force":13.59428,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48971,0.06443,0.06081]},{"body_a":"peg","body_b":"channel_base_body","contact_count":640.0,"contact_point_centroid":[0.49538,0.06379,0.00937],"force_p95":0.56787,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44546,"mean_force":0.55885,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48837,0.13365,0.2184]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":28.0,"contact_point_centroid":[0.47133,0.06388,0.03676],"force_p95":0.92436,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.16907,"mean_force":0.37063,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4993,0.1981,0.29759]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":13.0,"contact_point_centroid":[0.47482,0.06121,0.05938],"force_p95":0.6644,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.13258,"mean_force":0.13551,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48834,0.06024,0.0621]}],"total_contact_groups":9},"final_pose_error":0.01986,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49421,0.06264,0.03381],"final_tcp_position":[0.49583,-0.06075,0.13744],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"peak_contact_force":45.57381,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":667.0,"n_steps_budget":1000.0,"object_pos_end":[0.49532,0.06392,0.03396],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.14413,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"peak_contact_force":0.5491,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":668.0,"raw_peak_contact_force":2.44546,"subtask_id":"reach_pre_contact","tcp_end":[0.47911,0.07182,0.14543],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11292,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":528.0,"n_steps_budget":780.0,"object_pos_end":[0.49483,0.06375,0.03402],"object_pos_start":[0.49532,0.06392,0.03396],"object_to_goal_dist_end":0.14397,"object_to_goal_dist_start":0.14413,"object_z_max":0.03402,"peak_contact_force":14.07181,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":529.0,"raw_peak_contact_force":14.07181,"subtask_id":"reach_pre_contact","tcp_end":[0.48973,0.06442,0.06067],"tcp_start":[0.47911,0.07182,0.14543],"tcp_to_object_dist_end":0.02715,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":22.0,"n_steps_budget":1000.0,"object_pos_end":[0.49451,0.06226,0.03465],"object_pos_start":[0.49483,0.06375,0.03402],"object_to_goal_dist_end":0.14247,"object_to_goal_dist_start":0.14397,"object_z_max":0.03467,"peak_contact_force":35.49474,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":44.0,"raw_peak_contact_force":45.57381,"subtask_id":"push_to_goal","tcp_end":[0.48949,0.06148,0.06012],"tcp_start":[0.48948,0.06156,0.06014],"tcp_to_object_dist_end":0.02597,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":464.0,"n_steps_budget":1000.0,"object_pos_end":[0.49421,0.06264,0.03381],"object_pos_start":[0.49455,0.06213,0.03466],"object_to_goal_dist_end":0.14289,"object_to_goal_dist_start":0.14234,"object_z_max":0.03506,"peak_contact_force":0.54417,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":496.0,"raw_peak_contact_force":33.89407,"subtask_id":"push_to_goal","tcp_end":[0.49583,-0.06075,0.13744],"tcp_start":[0.48949,0.06148,0.06012],"tcp_to_object_dist_end":0.16114,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```