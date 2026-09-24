## Search State

- **Seed**: 7
- **Iteration**: 8 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 7 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 9 | -0.2220 | 0.00 | ❌ rejected |
| 6 | approach → descend → grasp → push → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | — | linear_cartesian | position_control | impedance_control | position_control | admittance_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | time_limit | pose_tolerance | 5 | -0.3038 | 0.00 | ❌ rejected |
| 5 | descend → insert → grasp → approach → align | linear_cartesian | impedance_motion | — | linear_cartesian | linear_cartesian | admittance_control | admittance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 5 | -0.1315 | 0.26 | ❌ rejected |
| 4 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | pose_tolerance | force_exceeded | force_exceeded | 4 | 0.2393 | 0.00 | ❌ rejected |
| 3 | approach → descend → align → insert | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | admittance_control | position_control | admittance_control | pose_tolerance | force_exceeded | pose_tolerance | force_exceeded | 6 | 0.0319 | 0.02 | ❌ rejected |

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

## Current Skill (Q=-0.222) — your mutation base

```yaml
skill: peg_channel
skill_type: arm_gripper
phases:
- id: descend_1
  type: descend
  generator: linear_cartesian
  control: admittance_control
  termination: pose_tolerance
- id: insert_1
  type: insert
  generator: impedance_motion
  control: admittance_control
  termination: pose_tolerance
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
- id: grasp_1
  type: grasp
  control: position_control
  termination: time_limit
  end_effector_action: force_grasp
- id: approach_1
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    speed:
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

```

## Design Metrics

- **Composite score**: -0.222
- **task_score** (E): 0.004
- **fitness_score**: 0.038  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
  → CMA-ES cannot optimise this structure (shaped reward also near zero)
- **Termination Fidelity** (C): 0.250
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.510

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_peg | 1.00 | 1.00 | 0.1725 |
| descend_contact | 1.00 | 1.00 | 0.0962 |
| push_channel | 0.00 | 1.00 | 0.0014 |
| retract_lift | 1.00 | 1.00 | 0.0805 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_peg | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.505, 0.110, 0.155) | (0.509, 0.098, 0.040)→(0.502, 0.098, 0.034) | 0.179→0.178 | 1.00 / 1.000 | 0.537 | 2.732 |
| descend_contact | descend | 1.00 / force_exceeded | (0.505, 0.110, 0.155)→(0.499, 0.099, 0.060) | (0.502, 0.098, 0.034)→(0.502, 0.098, 0.034) | 0.178→0.178 | 1.00 / 2.000 | 19.305 | 19.305 |
| push_channel | push | 0.00 / guard_failure | (0.500, 0.097, 0.060)→(0.502, 0.097, 0.059) | (0.502, 0.098, 0.034)→(0.502, 0.098, 0.034) | 0.178→0.178 | 1.00 / 2.333 | 266.809 | 266.809 |
| retract_lift | retract | 1.00 / step_budget | (0.502, 0.097, 0.059)→(0.499, 0.096, 0.140) | (0.503, 0.097, 0.034)→(0.502, 0.097, 0.034) | 0.177→0.177 | 1.00 / 1.000 | 0.545 | 77.169 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.006
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.006
- phase_score: 0.061
- phase_breakdown.push_peg_score: 0.002
- phase_breakdown.reach_peg_score: 0.201

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.039
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.006
- **Median Q (composite search score)**: -0.221
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.252


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `474e87cb3f7f98c9c8d99c8760356b7c026b70b97898f68d5a6c39ba94bca956`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `a79e5fd8fc80d9ecadd30a274b12d8d7e7d0841df5ca68ae512c46dc86b114e6`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.84689,"average_solve_count":209.0,"average_success_count":209.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_speed":0.04387,"descend_contact.contact_force_threshold":19.87367,"descend_contact.descend_speed":0.02402,"push_channel.lateral_offset_x":-0.00117,"push_channel.lateral_offset_y":-0.00148,"push_channel.push_distance":0.11889,"push_channel.push_force_limit":20.79742,"push_channel.push_speed":0.01909,"retract_lift.retract_speed":0.06054},"optimized_scores":{"best_composite_score":-0.22074,"best_fitness_score":0.03926,"best_task_score":0.00594},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":4.0,"contact_point_centroid":[0.51109,0.10544,0.00927],"force_p95":219.23868,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":224.79378,"mean_force":141.94445,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50102,0.11163,0.05998]},{"body_a":"attachment","body_b":"peg","contact_count":4.0,"contact_point_centroid":[0.51283,0.11237,0.05849],"force_p95":217.88921,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":223.45528,"mean_force":140.91127,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50102,0.11163,0.05998]},{"body_a":"attachment","body_b":"peg","contact_count":17.0,"contact_point_centroid":[0.51465,0.11519,0.05825],"force_p95":36.01926,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":79.41843,"mean_force":9.07016,"phase_index":3.0,"phase_name":"retract_lift","phase_type":"retract","tcp_position_centroid":[0.5042,0.10986,0.05916]},{"body_a":"peg","body_b":"channel_base_body","contact_count":273.0,"contact_point_centroid":[0.50463,0.11055,0.00939],"force_p95":0.78688,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":78.53955,"mean_force":1.08393,"phase_index":3.0,"phase_name":"retract_lift","phase_type":"retract","tcp_position_centroid":[0.50101,0.10961,0.09775]},{"body_a":"peg","body_b":"channel_base_body","contact_count":540.0,"contact_point_centroid":[0.50367,0.11173,0.00941],"force_p95":0.60004,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":25.69427,"mean_force":0.59081,"phase_index":1.0,"phase_name":"descend_contact","phase_type":"descend","tcp_position_centroid":[0.50198,0.11711,0.10681]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.51216,0.11171,0.05883],"force_p95":25.19344,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":25.19344,"mean_force":25.19344,"phase_index":1.0,"phase_name":"descend_contact","phase_type":"descend","tcp_position_centroid":[0.5003,0.11219,0.06056]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":8.0,"contact_point_centroid":[0.52541,0.10969,0.05786],"force_p95":7.1264,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.76946,"mean_force":1.49841,"phase_index":3.0,"phase_name":"retract_lift","phase_type":"retract","tcp_position_centroid":[0.50488,0.10975,0.05871]},{"body_a":"peg","body_b":"channel_base_body","contact_count":314.0,"contact_point_centroid":[0.5035,0.11158,0.00936],"force_p95":0.65628,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06328,"mean_force":0.56819,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.50255,0.15999,0.22433]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52601,0.11178,0.02875],"force_p95":0.50724,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54079,"mean_force":0.34334,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49974,0.19918,0.29901]}],"total_contact_groups":9},"final_pose_error":0.01972,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50407,0.11078,0.0338],"final_tcp_position":[0.50049,0.10956,0.13981],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":224.79378,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":336.0,"n_steps_budget":1000.0,"object_pos_end":[0.50372,0.11179,0.03393],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.19192,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":0.53304,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":330.0,"raw_peak_contact_force":2.06328,"subtask_id":"reach_peg","tcp_end":[0.50616,0.1226,0.15585],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.12242,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":540.0,"n_steps_budget":1000.0,"object_pos_end":[0.50372,0.11175,0.03386],"object_pos_start":[0.50372,0.11179,0.03393],"object_to_goal_dist_end":0.19189,"object_to_goal_dist_start":0.19192,"object_z_max":0.03397,"peak_contact_force":25.69427,"phase_name":"descend_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":541.0,"raw_peak_contact_force":25.69427,"subtask_id":"reach_peg","tcp_end":[0.5003,0.11217,0.0604],"tcp_start":[0.50616,0.1226,0.15585],"tcp_to_object_dist_end":0.02676,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":4.0,"n_steps_budget":1000.0,"object_pos_end":[0.50412,0.11143,0.03379],"object_pos_start":[0.50372,0.11175,0.03386],"object_to_goal_dist_end":0.19158,"object_to_goal_dist_start":0.19189,"object_z_max":0.03392,"peak_contact_force":224.79378,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":8.0,"raw_peak_contact_force":224.79378,"subtask_id":"push_peg","tcp_end":[0.50334,0.11022,0.05931],"tcp_start":[0.50207,0.11093,0.05956],"tcp_to_object_dist_end":0.02556,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":273.0,"n_steps_budget":1000.0,"object_pos_end":[0.50407,0.11078,0.0338],"object_pos_start":[0.50518,0.11082,0.03416],"object_to_goal_dist_end":0.19093,"object_to_goal_dist_start":0.19098,"object_z_max":0.03449,"peak_contact_force":0.57352,"phase_name":"retract_lift","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":298.0,"raw_peak_contact_force":79.41843,"tcp_end":[0.50049,0.10956,0.13981],"tcp_start":[0.50334,0.11022,0.05931],"tcp_to_object_dist_end":0.10608,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `3ca2e925d364d2c0fe81fb71ee31d40f947a20e349a0720e1c44a2dd2bc628da`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.52941,"average_solve_count":255.0,"average_success_count":255.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_speed":0.06774,"descend_contact.contact_force_threshold":7.60932,"descend_contact.descend_speed":0.02678,"push_channel.lateral_offset_x":0.00093,"push_channel.lateral_offset_y":0.00692,"push_channel.push_distance":0.09918,"push_channel.push_force_limit":20.7795,"push_channel.push_speed":0.02633,"retract_lift.retract_speed":0.01203},"optimized_scores":{"best_composite_score":-0.22118,"best_fitness_score":0.03882,"best_task_score":0.00423},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":4.0,"contact_point_centroid":[0.50066,0.10972,0.00928],"force_p95":224.07506,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":229.66851,"mean_force":140.07742,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49201,0.11884,0.05999]},{"body_a":"attachment","body_b":"peg","contact_count":4.0,"contact_point_centroid":[0.50383,0.11958,0.05851],"force_p95":222.78041,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":228.38609,"mean_force":139.07792,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49201,0.11884,0.05999]},{"body_a":"attachment","body_b":"peg","contact_count":26.0,"contact_point_centroid":[0.50641,0.1205,0.05829],"force_p95":20.19006,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":71.03164,"mean_force":7.59018,"phase_index":3.0,"phase_name":"retract_lift","phase_type":"retract","tcp_position_centroid":[0.49527,0.11704,0.05925]},{"body_a":"peg","body_b":"channel_base_body","contact_count":295.0,"contact_point_centroid":[0.49753,0.11794,0.0094],"force_p95":0.84178,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":70.8067,"mean_force":1.19717,"phase_index":3.0,"phase_name":"retract_lift","phase_type":"retract","tcp_position_centroid":[0.4921,0.1168,0.09664]},{"body_a":"peg","body_b":"channel_base_body","contact_count":632.0,"contact_point_centroid":[0.49607,0.11902,0.00942],"force_p95":0.61563,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":13.68263,"mean_force":0.56288,"phase_index":1.0,"phase_name":"descend_contact","phase_type":"descend","tcp_position_centroid":[0.48719,0.12398,0.10676]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.50311,0.11896,0.05882],"force_p95":13.14804,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":13.14804,"mean_force":13.14804,"phase_index":1.0,"phase_name":"descend_contact","phase_type":"descend","tcp_position_centroid":[0.49124,0.11936,0.06049]},{"body_a":"peg","body_b":"channel_base_body","contact_count":291.0,"contact_point_centroid":[0.49642,0.11918,0.00939],"force_p95":0.6429,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.56775,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49199,0.1629,0.22388]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49946,0.1984,0.29708]}],"total_contact_groups":8},"final_pose_error":0.01995,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49658,0.1181,0.03401],"final_tcp_position":[0.49153,0.11679,0.13963],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":229.66851,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":316.0,"n_steps_budget":1000.0,"object_pos_end":[0.49602,0.11911,0.03392],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.19924,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.53143,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":315.0,"raw_peak_contact_force":2.24822,"subtask_id":"reach_peg","tcp_end":[0.48569,0.12932,0.15708],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.12402,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":632.0,"n_steps_budget":1000.0,"object_pos_end":[0.49595,0.11899,0.03387],"object_pos_start":[0.49602,0.11911,0.03392],"object_to_goal_dist_end":0.19912,"object_to_goal_dist_start":0.19924,"object_z_max":0.03407,"peak_contact_force":13.68263,"phase_name":"descend_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":633.0,"raw_peak_contact_force":13.68263,"subtask_id":"reach_peg","tcp_end":[0.49126,0.11935,0.06037],"tcp_start":[0.48569,0.12932,0.15708],"tcp_to_object_dist_end":0.02691,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":4.0,"n_steps_budget":1000.0,"object_pos_end":[0.49634,0.11868,0.03377],"object_pos_start":[0.49595,0.11899,0.03387],"object_to_goal_dist_end":0.19882,"object_to_goal_dist_start":0.19912,"object_z_max":0.03388,"peak_contact_force":229.66851,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":8.0,"raw_peak_contact_force":229.66851,"subtask_id":"push_peg","tcp_end":[0.49439,0.1175,0.05936],"tcp_start":[0.4931,0.11817,0.0596],"tcp_to_object_dist_end":0.02569,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":295.0,"n_steps_budget":1000.0,"object_pos_end":[0.49658,0.1181,0.03401],"object_pos_start":[0.4974,0.11811,0.03409],"object_to_goal_dist_end":0.19822,"object_to_goal_dist_start":0.19822,"object_z_max":0.03445,"peak_contact_force":0.5209,"phase_name":"retract_lift","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":321.0,"raw_peak_contact_force":71.03164,"tcp_end":[0.49153,0.11679,0.13963],"tcp_start":[0.49439,0.1175,0.05936],"tcp_to_object_dist_end":0.10575,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `f85f1938a541e3d507519c8f918b8ca98f1f9baf6ab2f6f3ba2c32478e079e47`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.92896,"average_solve_count":183.0,"average_success_count":183.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_speed":0.05984,"descend_contact.contact_force_threshold":16.63703,"descend_contact.descend_speed":0.0291,"push_channel.lateral_offset_x":-0.00433,"push_channel.lateral_offset_y":-0.00805,"push_channel.push_distance":0.12725,"push_channel.push_force_limit":22.97824,"push_channel.push_speed":0.02711,"retract_lift.retract_speed":0.05755},"optimized_scores":{"best_composite_score":-0.22417,"best_fitness_score":0.03583,"best_task_score":0.00257},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":4.0,"contact_point_centroid":[0.51675,0.06408,0.05843],"force_p95":321.50098,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":345.96329,"mean_force":173.13815,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50495,0.06349,0.05994]},{"body_a":"peg","body_b":"channel_base_body","contact_count":4.0,"contact_point_centroid":[0.51752,0.06022,0.00924],"force_p95":241.03914,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":251.04305,"mean_force":150.19689,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50495,0.06349,0.05994]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":1.0,"contact_point_centroid":[0.5253,0.06179,0.05828],"force_p95":146.86092,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":146.86092,"mean_force":146.86092,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50588,0.06265,0.05952]},{"body_a":"attachment","body_b":"peg","contact_count":18.0,"contact_point_centroid":[0.51854,0.06397,0.05784],"force_p95":45.18083,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":81.05688,"mean_force":9.1143,"phase_index":3.0,"phase_name":"retract_lift","phase_type":"retract","tcp_position_centroid":[0.50712,0.0614,0.05905]},{"body_a":"peg","body_b":"channel_base_body","contact_count":273.0,"contact_point_centroid":[0.50618,0.06232,0.00935],"force_p95":0.78985,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":75.35974,"mean_force":1.08762,"phase_index":3.0,"phase_name":"retract_lift","phase_type":"retract","tcp_position_centroid":[0.50439,0.06144,0.09751]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":23.0,"contact_point_centroid":[0.52528,0.06173,0.0584],"force_p95":18.16599,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":21.87711,"mean_force":2.72048,"phase_index":3.0,"phase_name":"retract_lift","phase_type":"retract","tcp_position_centroid":[0.50575,0.0614,0.07075]},{"body_a":"peg","body_b":"channel_base_body","contact_count":476.0,"contact_point_centroid":[0.50588,0.06292,0.00938],"force_p95":0.55144,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":18.53717,"mean_force":0.58437,"phase_index":1.0,"phase_name":"descend_contact","phase_type":"descend","tcp_position_centroid":[0.51298,0.07072,0.10557]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.5162,0.06344,0.0588],"force_p95":18.09418,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":18.09418,"mean_force":18.09418,"phase_index":1.0,"phase_name":"descend_contact","phase_type":"descend","tcp_position_centroid":[0.50435,0.06416,0.06054]},{"body_a":"peg","body_b":"channel_base_body","contact_count":379.0,"contact_point_centroid":[0.50568,0.06304,0.00934],"force_p95":0.58572,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.88411,"mean_force":0.58225,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.51169,0.1357,0.22102]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":34.0,"contact_point_centroid":[0.53102,0.06295,0.03156],"force_p95":1.1362,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.98455,"mean_force":0.48262,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.50015,0.1967,0.29569]}],"total_contact_groups":10},"final_pose_error":0.01975,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50627,0.06192,0.0341],"final_tcp_position":[0.50399,0.06146,0.13971],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.52962,0.06295,0.04]},"peak_contact_force":345.96329,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":407.0,"n_steps_budget":1000.0,"object_pos_end":[0.50601,0.06295,0.0338],"object_pos_start":[0.52962,0.06295,0.04],"object_to_goal_dist_end":0.14321,"object_to_goal_dist_start":0.14598,"object_z_max":0.04001,"peak_contact_force":0.54716,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":413.0,"raw_peak_contact_force":3.88411,"subtask_id":"reach_peg","tcp_end":[0.52368,0.07749,0.15233],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.12071,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":476.0,"n_steps_budget":1000.0,"object_pos_end":[0.50598,0.06304,0.0338],"object_pos_start":[0.50601,0.06295,0.0338],"object_to_goal_dist_end":0.1433,"object_to_goal_dist_start":0.14321,"object_z_max":0.03381,"peak_contact_force":18.53717,"phase_name":"descend_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":477.0,"raw_peak_contact_force":18.53717,"subtask_id":"reach_peg","tcp_end":[0.50433,0.06413,0.06036],"tcp_start":[0.52368,0.07749,0.15233],"tcp_to_object_dist_end":0.02664,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":4.0,"n_steps_budget":1000.0,"object_pos_end":[0.50638,0.0627,0.03375],"object_pos_start":[0.50598,0.06304,0.0338],"object_to_goal_dist_end":0.14298,"object_to_goal_dist_start":0.1433,"object_z_max":0.03389,"peak_contact_force":345.96329,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":9.0,"raw_peak_contact_force":345.96329,"subtask_id":"push_peg","tcp_end":[0.50689,0.06186,0.05924],"tcp_start":[0.50588,0.06265,0.05952],"tcp_to_object_dist_end":0.02552,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":273.0,"n_steps_budget":1000.0,"object_pos_end":[0.50627,0.06192,0.0341],"object_pos_start":[0.50717,0.06208,0.03398],"object_to_goal_dist_end":0.14218,"object_to_goal_dist_start":0.14239,"object_z_max":0.03416,"peak_contact_force":0.54046,"phase_name":"retract_lift","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":314.0,"raw_peak_contact_force":81.05688,"tcp_end":[0.50399,0.06146,0.13971],"tcp_start":[0.50689,0.06186,0.05924],"tcp_to_object_dist_end":0.10564,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```