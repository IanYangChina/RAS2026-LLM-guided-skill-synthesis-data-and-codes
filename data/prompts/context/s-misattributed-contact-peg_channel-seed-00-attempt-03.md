## Search State

- **Seed**: 0
- **Iteration**: 4 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 3 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | 0.2736 | 0.29 | ❌ rejected |
| 2 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | 0.2378 | 0.42 | ❌ rejected |
| 1 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | -0.0520 | 0.00 | ❌ rejected |
| 0 | insert → approach → push → retract → lift → insert | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | linear_cartesian | impedance_motion | impedance_control | force_threshold_switch | impedance_control | position_control | position_control | admittance_control | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | 5 | 0.1883 | 0.75 | ✅ accepted |

**Proposal policy**: task_score is 0.29 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `cd60c08f71f9d10bc11dd62c79067fee574cade1f8d1192fc945700528a8d454`
- Frozen object start: [0.5109569349857164, 0.061582937101109625, 0.04]
- Frozen task target: [0.5109569349857164, -0.09841706289889038, 0.04]
- Goal object position: (0.5109569349857164, -0.09841706289889038, 0.04)
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Object initial pose: (0.5109569349857164, 0.061582937101109625, 0.04)
- Goal tolerance: 0.02 m
- Expressivity sigma: 1.0 m
- Expressivity threshold: 0.5
- Force limit: 40.0 N
- Peg body: `peg`
- Channel axis: `(0.0, -1.0, 0.0)` — use `impedance_control` to absorb lateral wall forces
- Robot initial TCP position: (0.5, 0.2, 0.3)
- Phase navigation guidance: the task `phase_target_map` may provide internal predefined TCP waypoint aliases / semantic phase ids. These names are not DSL phase types and are intentionally not enumerated here to avoid confusing ids with types. Phase `id` may be semantic, but phase `type` must be exactly one of the DSL enum values listed in the prompt.
- Primary evaluation target: **insertion depth × lateral alignment (axial progress penalised by wall deviation)**

## Scene Entities

robot:
  model: panda_pusher
  tcp_site: attachment_site
  gripper: null
  tcp_initial_world: [0.5, 0.2, 0.3]
objects:
  - name: peg
    role: manipulated_object
    dynamics: free
    geometry: cylinder
    radius_m: 0.018
    half_length_m: 0.025
  - name: channel_structure
    role: fixture
    dynamics: static
    geometry: two_parallel_walls
    inner_gap_m: 0.05
    wall_thickness_m: 0.03
    wall_height_m: 0.05
task_landmarks:
  frozen_object_start: [0.511, 0.0616, 0.04]
  frozen_task_target: [0.511, -0.0984, 0.04]
  frozen_fixture_position: [0.54, 0, 0.035]
  frozen_object_starts: {'peg': [0.5109569349857164, 0.061582937101109625, 0.04]}
  frozen_targets: {'channel_exit': [0.5109569349857164, -0.09841706289889038, 0.04]}
  frozen_fixtures: {'channel_left_wall': [0.54, 0.0, 0.035], 'channel_right_wall': [0.46, 0.0, 0.035]}
  channel_axis: [0, -1, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  channel_length_m: 0.16
  force_scale_n: 5
  realized_scene_sha256: cd60c08f71f9d10bc11dd62c79067fee574cade1f8d1192fc945700528a8d454

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
| `object` | offset from object initial position (0.5109569349857164, 0.061582937101109625, 0.04) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5109569349857164, -0.09841706289889038, 0.04) | final destination targets |
| `fixture` | offset from fixture pose (0.54, 0.0, 0.035) | approach/contact targets near fixture |

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

## Current Skill (Q=0.274) — your mutation base

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

- **Composite score**: 0.274
- **task_score** (E): 0.291
- **fitness_score**: 0.434  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.250
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.410

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1922 |
| descend_1 | 1.00 | 1.00 | 0.0829 |
| push_1 | 0.00 | 1.00 | 0.1673 |
| retract_1 | 0.33 | 1.00 | 0.1346 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.495, 0.088, 0.146) | (0.498, 0.080, 0.040)→(0.500, 0.081, 0.034) | 0.161→0.161 | 1.00 / 2.000 | 30.850 | 30.850 |
| descend_1 | descend | 1.00 / force_exceeded | (0.495, 0.088, 0.146)→(0.495, 0.082, 0.063) | (0.500, 0.081, 0.034)→(0.500, 0.080, 0.034) | 0.161→0.161 | 1.00 / 1.667 | 116.903 | 150.849 |
| push_1 | push | 0.00 / step_budget | (0.495, 0.082, 0.063)→(0.494, -0.084, 0.048) | (0.500, 0.080, 0.034)→(0.501, 0.029, 0.024) | 0.161→0.111 | 1.00 / 1.000 | 0.672 | 43.186 |
| retract_1 | retract | 0.33 / step_budget | (0.494, -0.084, 0.048)→(0.491, -0.066, 0.180) | (0.501, 0.029, 0.024)→(0.501, 0.028, 0.024) | 0.111→0.110 | 1.00 / 1.000 | 0.560 | 2.179 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.324
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.324
- phase_score: 0.541
- phase_breakdown.reach_goal_score: 0.349
- phase_breakdown.reach_descend_score: 0.604
- phase_breakdown.reach_approach_score: 0.820

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.454
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.324
- **Median Q (composite search score)**: 0.266
- **K-run variance**: 0.0002
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.324


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `d6915c31707ac435a9367b840736087e39a7a48adfeb36a4f94b6b3ae57cce94`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `19172182883d287409b73cab43749e937e65f1ca1d4501d52b4a913a881aad36`; realized-scene SHA-256: `cd60c08f71f9d10bc11dd62c79067fee574cade1f8d1192fc945700528a8d454`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.51096,0.06158,0.04]},{"name":"goal","value":[0.51096,-0.09842,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.51096,0.06158,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.51096,-0.09842,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.72727,"average_solve_count":154.0,"average_success_count":154.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.06064,"descend_1.force_threshold":24.67308,"descend_1.speed":0.03609,"push_1.push_distance":0.08559,"push_1.push_speed":0.03229,"retract_1.retract_height":0.18466,"retract_1.speed":0.035},"optimized_scores":{"best_composite_score":0.29439,"best_fitness_score":0.45439,"best_task_score":0.324},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_base_body","contact_count":175.0,"contact_point_centroid":[0.50488,-0.1001,0.065],"force_p95":202.6051,"geom_a":"pusher_tip","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":212.54668,"mean_force":148.59207,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4972,-0.08797,0.04855]},{"body_a":"peg","body_b":"channel_base_body","contact_count":996.0,"contact_point_centroid":[0.49974,0.02242,0.00867],"force_p95":67.20891,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":69.77537,"mean_force":17.58056,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49828,-0.02694,0.05419]},{"body_a":"attachment","body_b":"peg","contact_count":368.0,"contact_point_centroid":[0.50855,0.03505,0.05737],"force_p95":67.79297,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":69.24449,"mean_force":46.12899,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50061,0.02907,0.0601]},{"body_a":"attachment","body_b":"channel_base_body","contact_count":2.0,"contact_point_centroid":[0.50554,-0.10002,0.065],"force_p95":56.79711,"geom_a":"pusher_tip","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":57.56897,"mean_force":49.85032,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49757,-0.08777,0.04808]},{"body_a":"peg","body_b":"channel_base_body","contact_count":405.0,"contact_point_centroid":[0.50383,0.06151,0.00938],"force_p95":0.55168,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":35.32524,"mean_force":0.7972,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50283,0.06633,0.10303]},{"body_a":"attachment","body_b":"peg","contact_count":4.0,"contact_point_centroid":[0.51188,0.06366,0.05864],"force_p95":33.1165,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":34.88848,"mean_force":25.46593,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50094,0.06355,0.06344]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50144,0.01107,0.00808],"force_p95":0.64396,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.53742,"mean_force":0.67084,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49419,-0.0698,0.10455]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":17.0,"contact_point_centroid":[0.525,-0.01422,0.02446],"force_p95":8.89405,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.01422,"mean_force":4.21018,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49444,-0.06016,0.15934]},{"body_a":"peg","body_b":"channel_base_body","contact_count":636.0,"contact_point_centroid":[0.50361,0.06161,0.00935],"force_p95":0.59088,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.17216,"mean_force":0.55918,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50281,0.13265,0.21828]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":19.0,"contact_point_centroid":[0.52623,0.06158,0.03217],"force_p95":0.5921,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.62339,"mean_force":0.34148,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49966,0.19875,0.29867]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":2.0,"contact_point_centroid":[0.475,0.03541,0.02419],"force_p95":0.38422,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.38648,"mean_force":0.36387,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4969,-0.08781,0.04877]}],"total_contact_groups":11},"final_pose_error":0.17213,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50668,0.00974,0.02479],"final_tcp_position":[0.4945,-0.05993,0.16291],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51096,0.06158,0.04]},"peak_contact_force":212.54668,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":659.0,"n_steps_budget":1000.0,"object_pos_end":[0.50379,0.06159,0.03378],"object_pos_start":[0.51096,0.06158,0.04],"object_to_goal_dist_end":0.14178,"object_to_goal_dist_start":0.14201,"object_z_max":0.04,"peak_contact_force":35.32524,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":409.0,"raw_peak_contact_force":35.32524,"subtask_id":"reach_approach","tcp_end":[0.50711,0.06946,0.14461],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11115,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":405.0,"n_steps_budget":960.0,"object_pos_end":[0.50376,0.06154,0.03375],"object_pos_start":[0.50379,0.06159,0.03378],"object_to_goal_dist_end":0.14173,"object_to_goal_dist_start":0.14178,"object_z_max":0.03378,"peak_contact_force":201.28984,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1541.0,"raw_peak_contact_force":212.54668,"subtask_id":"reach_descend","tcp_end":[0.50097,0.06354,0.06303],"tcp_start":[0.50711,0.06946,0.14461],"tcp_to_object_dist_end":0.02948,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49538,0.01084,0.02431],"object_pos_start":[0.50376,0.06154,0.03375],"object_to_goal_dist_end":0.09231,"object_to_goal_dist_start":0.14173,"object_z_max":0.04024,"peak_contact_force":0.64543,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1019.0,"raw_peak_contact_force":57.56897,"subtask_id":"reach_goal","tcp_end":[0.49758,-0.08778,0.04809],"tcp_start":[0.50097,0.06354,0.06303],"tcp_to_object_dist_end":0.10148,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50668,0.00974,0.02479],"object_pos_start":[0.49538,0.01084,0.02431],"object_to_goal_dist_end":0.09127,"object_to_goal_dist_start":0.09231,"object_z_max":0.0248,"peak_contact_force":0.5519,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":655.0,"raw_peak_contact_force":2.17216,"tcp_end":[0.4945,-0.05993,0.16291],"tcp_start":[0.49758,-0.08778,0.04809],"tcp_to_object_dist_end":0.15518,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `f24211f27d4adabdef509c8ed61621317fdbcaa86fc9ac888f85a717335bb714`; realized-scene SHA-256: `9fd07833843a6ee28e14c5e2ce05f86547005983f45e63c41c77b8dac2024c0a`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50095,0.11604,0.04]},{"name":"goal","value":[0.50095,-0.04396,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.50095,0.11604,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.50095,-0.04396,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.33937,"average_solve_count":221.0,"average_success_count":221.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.0194,"descend_1.force_threshold":10.33359,"descend_1.speed":0.02361,"push_1.push_distance":0.11182,"push_1.push_speed":0.03691,"retract_1.retract_height":0.09753,"retract_1.speed":0.06025},"optimized_scores":{"best_composite_score":0.26579,"best_fitness_score":0.42579,"best_task_score":0.32184},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":996.0,"contact_point_centroid":[0.50019,0.07663,0.00861],"force_p95":64.26882,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":66.6609,"mean_force":15.12957,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49425,0.01726,0.05487]},{"body_a":"attachment","body_b":"peg","contact_count":328.0,"contact_point_centroid":[0.50399,0.09058,0.05794],"force_p95":65.02895,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":66.14253,"mean_force":44.28522,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49604,0.08431,0.06076]},{"body_a":"peg","body_b":"channel_base_body","contact_count":476.0,"contact_point_centroid":[0.501,0.11597,0.00943],"force_p95":0.60887,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":20.53195,"mean_force":0.62219,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49569,0.119,0.10396]},{"body_a":"attachment","body_b":"peg","contact_count":2.0,"contact_point_centroid":[0.50712,0.11714,0.05877],"force_p95":19.96559,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":20.0499,"mean_force":19.2068,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49616,0.11689,0.06357]},{"body_a":"peg","body_b":"channel_base_body","contact_count":958.0,"contact_point_centroid":[0.50493,0.0662,0.00813],"force_p95":7.18544,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.88899,"mean_force":1.04796,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49074,-0.06351,0.13838]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":95.0,"contact_point_centroid":[0.52506,0.05844,0.02523],"force_p95":8.98837,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.37573,"mean_force":4.77578,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49102,-0.06319,0.19587]},{"body_a":"peg","body_b":"channel_base_body","contact_count":569.0,"contact_point_centroid":[0.50093,0.11602,0.00938],"force_p95":0.60733,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.92055,"mean_force":0.55781,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49805,0.16032,0.2214]}],"total_contact_groups":7},"final_pose_error":0.01312,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50333,0.06454,0.02413],"final_tcp_position":[0.49135,-0.07391,0.23375],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50095,0.11604,0.04]},"peak_contact_force":66.6609,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":585.0,"n_steps_budget":1000.0,"object_pos_end":[0.50099,0.116,0.03387],"object_pos_start":[0.50095,0.11604,0.04],"object_to_goal_dist_end":0.1961,"object_to_goal_dist_start":0.19604,"object_z_max":0.04,"peak_contact_force":20.53195,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":478.0,"raw_peak_contact_force":20.53195,"subtask_id":"reach_approach","tcp_end":[0.49779,0.12174,0.14729],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11361,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":476.0,"n_steps_budget":1000.0,"object_pos_end":[0.50088,0.116,0.03382],"object_pos_start":[0.50099,0.116,0.03387],"object_to_goal_dist_end":0.1961,"object_to_goal_dist_start":0.1961,"object_z_max":0.03403,"peak_contact_force":0.72551,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1324.0,"raw_peak_contact_force":66.6609,"subtask_id":"reach_descend","tcp_end":[0.49619,0.11689,0.06334],"tcp_start":[0.49779,0.12174,0.14729],"tcp_to_object_dist_end":0.0299,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50157,0.06651,0.02409],"object_pos_start":[0.50088,0.116,0.03382],"object_to_goal_dist_end":0.14738,"object_to_goal_dist_start":0.1961,"object_z_max":0.04028,"peak_contact_force":0.68314,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1053.0,"raw_peak_contact_force":9.88899,"subtask_id":"reach_goal","tcp_end":[0.49375,-0.07703,0.04874],"tcp_start":[0.49619,0.11689,0.06334],"tcp_to_object_dist_end":0.14585,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":958.0,"n_steps_budget":1000.0,"object_pos_end":[0.50333,0.06454,0.02413],"object_pos_start":[0.50157,0.06651,0.02409],"object_to_goal_dist_end":0.14545,"object_to_goal_dist_start":0.14738,"object_z_max":0.02605,"peak_contact_force":0.58317,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":569.0,"raw_peak_contact_force":1.92055,"tcp_end":[0.49135,-0.07391,0.23375],"tcp_start":[0.49375,-0.07703,0.04874],"tcp_to_object_dist_end":0.2515,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `d098a7862ff18c9bbe982af3446a89a0fa6bcfa8790d7d955f65b2375d67a881`; realized-scene SHA-256: `2a92d231da5879af7af8916eb4c7dff00148227e84220c4d9643d9841dc77ee7`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.48093,0.06388,0.04]},{"name":"goal","value":[0.48093,-0.09612,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.48093,0.06388,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.48093,-0.09612,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.17935,"average_solve_count":184.0,"average_success_count":184.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.05152,"descend_1.force_threshold":25.49122,"descend_1.speed":0.03012,"push_1.push_distance":0.02716,"push_1.push_speed":0.01785,"retract_1.retract_height":0.16775,"retract_1.speed":0.01928},"optimized_scores":{"best_composite_score":0.26052,"best_fitness_score":0.42052,"best_task_score":0.22636},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_base_body","contact_count":114.0,"contact_point_centroid":[0.49813,-0.10013,0.065],"force_p95":151.49835,"geom_a":"pusher_tip","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":173.34018,"mean_force":117.25147,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48948,-0.08798,0.04721]},{"body_a":"peg","body_b":"channel_base_body","contact_count":996.0,"contact_point_centroid":[0.50046,0.02278,0.00872],"force_p95":73.73025,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":76.22328,"mean_force":21.26105,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48781,-0.02098,0.05405]},{"body_a":"attachment","body_b":"peg","contact_count":407.0,"contact_point_centroid":[0.49639,0.03545,0.05677],"force_p95":74.20376,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":75.68978,"mean_force":50.70186,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4878,0.03078,0.06003]},{"body_a":"attachment","body_b":"channel_base_body","contact_count":7.0,"contact_point_centroid":[0.49906,-0.10018,0.065],"force_p95":61.67194,"geom_a":"pusher_tip","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":62.10069,"mean_force":50.16985,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49023,-0.08807,0.04675]},{"body_a":"peg","body_b":"channel_base_body","contact_count":556.0,"contact_point_centroid":[0.4949,0.06382,0.0094],"force_p95":0.551,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":36.69244,"mean_force":0.96916,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.48147,0.06866,0.10203]},{"body_a":"attachment","body_b":"peg","contact_count":9.0,"contact_point_centroid":[0.4972,0.0664,0.05878],"force_p95":34.90983,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":36.25007,"mean_force":26.27549,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.48643,0.06601,0.06384]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.49967,0.01028,0.00805],"force_p95":0.6834,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.68234,"mean_force":0.61464,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48684,-0.07213,0.09467]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":4.0,"contact_point_centroid":[0.47499,0.03517,0.02414],"force_p95":7.91432,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.23629,"mean_force":2.59002,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48696,-0.06332,0.13874]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":6.0,"contact_point_centroid":[0.52501,-0.01438,0.02422],"force_p95":6.9401,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.11448,"mean_force":1.82677,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4884,-0.07503,0.04852]},{"body_a":"peg","body_b":"channel_base_body","contact_count":621.0,"contact_point_centroid":[0.49545,0.06382,0.00937],"force_p95":0.56814,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44546,"mean_force":0.55926,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48838,0.13362,0.21832]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":28.0,"contact_point_centroid":[0.47133,0.06388,0.03676],"force_p95":0.92436,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.16907,"mean_force":0.37063,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4992,0.19793,0.29738]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":2.0,"contact_point_centroid":[0.47499,0.0023,0.05068],"force_p95":0.74518,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.75196,"mean_force":0.68419,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48655,-0.00838,0.05431]}],"total_contact_groups":12},"final_pose_error":0.17253,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49371,0.01043,0.02418],"final_tcp_position":[0.48701,-0.06282,0.14391],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"peak_contact_force":173.34018,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":648.0,"n_steps_budget":1000.0,"object_pos_end":[0.49523,0.06406,0.03396],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.14426,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"peak_contact_force":36.69244,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":565.0,"raw_peak_contact_force":36.69244,"subtask_id":"reach_approach","tcp_end":[0.47905,0.07193,0.14543],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11292,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":556.0,"n_steps_budget":1000.0,"object_pos_end":[0.49509,0.06361,0.03387],"object_pos_start":[0.49523,0.06406,0.03396],"object_to_goal_dist_end":0.14383,"object_to_goal_dist_start":0.14426,"object_z_max":0.03402,"peak_contact_force":148.69295,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1525.0,"raw_peak_contact_force":173.34018,"subtask_id":"reach_descend","tcp_end":[0.48667,0.06608,0.06329],"tcp_start":[0.47905,0.07193,0.14543],"tcp_to_object_dist_end":0.0307,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50586,0.0104,0.02413],"object_pos_start":[0.49509,0.06361,0.03387],"object_to_goal_dist_end":0.09197,"object_to_goal_dist_start":0.14383,"object_z_max":0.04029,"peak_contact_force":0.68756,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1011.0,"raw_peak_contact_force":62.10069,"subtask_id":"reach_goal","tcp_end":[0.49027,-0.08825,0.04677],"tcp_start":[0.48667,0.06608,0.06329],"tcp_to_object_dist_end":0.10241,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49371,0.01043,0.02418],"object_pos_start":[0.50586,0.0104,0.02413],"object_to_goal_dist_end":0.09202,"object_to_goal_dist_start":0.09197,"object_z_max":0.0244,"peak_contact_force":0.54427,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":649.0,"raw_peak_contact_force":2.44546,"tcp_end":[0.48701,-0.06282,0.14391],"tcp_start":[0.49027,-0.08825,0.04677],"tcp_to_object_dist_end":0.14052,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```