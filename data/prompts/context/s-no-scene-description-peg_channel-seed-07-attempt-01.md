## Search State

- **Seed**: 7
- **Iteration**: 2 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 1 | approach → descend → grasp → align → push → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | admittance_control | position_control | position_control | admittance_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | force_exceeded | pose_tolerance | 5 | -0.0266 | 0.22 | ❌ rejected |
| 0 | descend → insert → grasp → approach → align | linear_cartesian | impedance_motion | — | linear_cartesian | linear_cartesian | admittance_control | admittance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 5 | -0.1315 | 0.26 | ✅ accepted |

**Proposal policy**: task_score is 0.22 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.027) — your mutation base

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

- **Composite score**: -0.027
- **task_score** (E): 0.218
- **fitness_score**: 0.143  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.200
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.370

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_above | 1.00 | 1.00 | 0.2001 |
| descend_contact | 1.00 | 1.00 | 0.0643 |
| grasp_peg | 1.00 | 1.00 | 0.0037 |
| align_entry | 1.00 | 1.00 | 0.1691 |
| push_through | 0.00 | 1.00 | 0.0001 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_above | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.505, 0.104, 0.127) | (0.509, 0.098, 0.040)→(0.502, 0.098, 0.034) | 0.179→0.178 | 1.00 / 1.000 | 0.530 | 2.732 |
| descend_contact | descend | 1.00 / force_exceeded | (0.505, 0.104, 0.127)→(0.499, 0.099, 0.063) | (0.502, 0.098, 0.034)→(0.502, 0.098, 0.034) | 0.178→0.178 | 1.00 / 2.000 | 27.844 | 27.844 |
| grasp_peg | grasp | 1.00 / step_budget | (0.499, 0.099, 0.063)→(0.497, 0.098, 0.060) | (0.502, 0.098, 0.034)→(0.500, 0.098, 0.032) | 0.178→0.178 | 1.00 / 2.000 | 50.575 | 60.166 |
| align_entry | align | 1.00 / step_budget | (0.497, 0.098, 0.060)→(0.496, -0.069, 0.037) | (0.500, 0.098, 0.032)→(0.502, 0.049, 0.024) | 0.178→0.130 | 1.00 / 1.667 | 59.018 | 133.558 |
| push_through | push | 0.00 / guard_failure | (0.496, -0.069, 0.037)→(0.496, -0.069, 0.037) | (0.502, 0.049, 0.024)→(0.502, 0.049, 0.024) | 0.130→0.130 | 1.00 / 2.000 | 51.923 | 51.923 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.311
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.311
- phase_score: 0.095
- phase_breakdown.push_progress_score: 0.000
- phase_breakdown.reach_peg_score: 0.318

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.182
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.311
- **Median Q (composite search score)**: -0.016
- **K-run variance**: 0.0013
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.366


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.87097,"average_solve_count":93.0,"average_success_count":93.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_entry.lateral_x":-0.00979,"approach_above.speed":0.12143,"descend_contact.force_threshold":17.40672,"push_through.force_limit":21.93339,"push_through.push_speed":0.01897},"optimized_scores":{"best_composite_score":0.01155,"best_fitness_score":0.18155,"best_task_score":0.31073},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_base_body","body_b":"link7","contact_count":30.0,"contact_point_centroid":[0.53159,-0.1,0.06499],"force_p95":112.15145,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":130.16863,"mean_force":94.20051,"phase_index":3.0,"phase_name":"align_entry","phase_type":"align","tcp_position_centroid":[0.48857,-0.06622,0.03782]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":40.0,"contact_point_centroid":[0.53294,-0.05684,0.06],"force_p95":72.40477,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":103.29303,"mean_force":53.18247,"phase_index":3.0,"phase_name":"align_entry","phase_type":"align","tcp_position_centroid":[0.4877,-0.06028,0.03776]},{"body_a":"peg","body_b":"channel_base_body","contact_count":914.0,"contact_point_centroid":[0.50146,0.07336,0.00857],"force_p95":93.86627,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":96.88655,"mean_force":27.63692,"phase_index":3.0,"phase_name":"align_entry","phase_type":"align","tcp_position_centroid":[0.49279,0.01949,0.04811]},{"body_a":"attachment","body_b":"peg","contact_count":364.0,"contact_point_centroid":[0.50655,0.08318,0.05498],"force_p95":94.54962,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":96.33011,"mean_force":68.06265,"phase_index":3.0,"phase_name":"align_entry","phase_type":"align","tcp_position_centroid":[0.49824,0.07809,0.05743]},{"body_a":"peg","body_b":"channel_base_body","contact_count":450.0,"contact_point_centroid":[0.50705,0.11171,0.00877],"force_p95":58.7679,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":59.96089,"mean_force":47.46663,"phase_index":2.0,"phase_name":"grasp_peg","phase_type":"grasp","tcp_position_centroid":[0.49878,0.11211,0.06062]},{"body_a":"attachment","body_b":"peg","contact_count":450.0,"contact_point_centroid":[0.50975,0.11227,0.05666],"force_p95":58.26307,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":59.4521,"mean_force":46.96516,"phase_index":2.0,"phase_name":"grasp_peg","phase_type":"grasp","tcp_position_centroid":[0.49878,0.11211,0.06062]},{"body_a":"channel_base_body","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.53201,-0.1,0.06499],"force_p95":53.45186,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":53.45186,"mean_force":53.45186,"phase_index":4.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.48901,-0.06747,0.03796]},{"body_a":"peg","body_b":"channel_base_body","contact_count":303.0,"contact_point_centroid":[0.50364,0.11171,0.00941],"force_p95":0.59852,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":29.75089,"mean_force":0.64021,"phase_index":1.0,"phase_name":"descend_contact","phase_type":"descend","tcp_position_centroid":[0.50218,0.11453,0.09459]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.51154,0.11271,0.05889],"force_p95":29.32591,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":29.32591,"mean_force":29.32591,"phase_index":1.0,"phase_name":"descend_contact","phase_type":"descend","tcp_position_centroid":[0.50054,0.11252,0.06367]},{"body_a":"peg","body_b":"channel_base_body","contact_count":566.0,"contact_point_centroid":[0.50355,0.11162,0.00938],"force_p95":0.61623,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06328,"mean_force":0.55794,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.50227,0.15738,0.2101]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.50649,0.08708,0.00806],"force_p95":0.57974,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57974,"mean_force":0.57974,"phase_index":4.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.48901,-0.06747,0.03796]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52601,0.11178,0.02875],"force_p95":0.50724,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54079,"mean_force":0.34334,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.49972,0.1992,0.29893]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":4.0,"contact_point_centroid":[0.47498,0.03897,0.03127],"force_p95":0.51307,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.52084,"mean_force":0.46194,"phase_index":3.0,"phase_name":"align_entry","phase_type":"align","tcp_position_centroid":[0.49154,0.02787,0.0472]}],"total_contact_groups":13},"final_pose_error":0.19996,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50621,0.06206,0.02412],"final_tcp_position":[0.48904,-0.0675,0.03797],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":130.16863,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":588.0,"n_steps_budget":1000.0,"object_pos_end":[0.50365,0.11176,0.0338],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.1919,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":0.56051,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":582.0,"raw_peak_contact_force":2.06328,"subtask_id":"reach_peg","tcp_end":[0.50605,0.11707,0.12723],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.09361,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":303.0,"n_steps_budget":600.0,"object_pos_end":[0.50374,0.11171,0.03389],"object_pos_start":[0.50365,0.11176,0.0338],"object_to_goal_dist_end":0.19185,"object_to_goal_dist_start":0.1919,"object_z_max":0.03392,"peak_contact_force":29.75089,"phase_name":"descend_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":304.0,"raw_peak_contact_force":29.75089,"subtask_id":"reach_peg","tcp_end":[0.50054,0.11252,0.06346],"tcp_start":[0.50605,0.11707,0.12723],"tcp_to_object_dist_end":0.02976,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50113,0.11129,0.03234],"object_pos_start":[0.50374,0.11171,0.03389],"object_to_goal_dist_end":0.19145,"object_to_goal_dist_start":0.19185,"object_z_max":0.03389,"peak_contact_force":35.19239,"phase_name":"grasp_peg","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":900.0,"raw_peak_contact_force":59.96089,"tcp_end":[0.49859,0.11208,0.0603],"tcp_start":[0.50054,0.11252,0.06346],"tcp_to_object_dist_end":0.02809,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":918.0,"n_steps_budget":1000.0,"object_pos_end":[0.50618,0.06208,0.02412],"object_pos_start":[0.50113,0.11129,0.03234],"object_to_goal_dist_end":0.1431,"object_to_goal_dist_start":0.19145,"object_z_max":0.03986,"peak_contact_force":95.05037,"phase_name":"align_entry","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":1352.0,"raw_peak_contact_force":130.16863,"tcp_end":[0.48901,-0.06747,0.03796],"tcp_start":[0.49859,0.11208,0.0603],"tcp_to_object_dist_end":0.13141,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.50621,0.06206,0.02412],"object_pos_start":[0.50618,0.06208,0.02412],"object_to_goal_dist_end":0.14308,"object_to_goal_dist_start":0.1431,"object_z_max":0.02412,"peak_contact_force":53.45186,"phase_name":"push_through","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2.0,"raw_peak_contact_force":53.45186,"subtask_id":"push_progress","tcp_end":[0.48904,-0.0675,0.03797],"tcp_start":[0.48901,-0.06747,0.03796],"tcp_to_object_dist_end":0.13143,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `3ca2e925d364d2c0fe81fb71ee31d40f947a20e349a0720e1c44a2dd2bc628da`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.86667,"average_solve_count":90.0,"average_success_count":90.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_entry.lateral_x":0.00331,"approach_above.speed":0.13606,"descend_contact.force_threshold":21.25961,"push_through.force_limit":26.61667,"push_through.push_speed":0.03911},"optimized_scores":{"best_composite_score":-0.01562,"best_fitness_score":0.15438,"best_task_score":0.24036},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_base_body","body_b":"link7","contact_count":33.0,"contact_point_centroid":[0.54151,-0.1,0.06499],"force_p95":126.34336,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":130.33629,"mean_force":80.2022,"phase_index":3.0,"phase_name":"align_entry","phase_type":"align","tcp_position_centroid":[0.49908,-0.06768,0.03679]},{"body_a":"peg","body_b":"channel_base_body","contact_count":980.0,"contact_point_centroid":[0.49962,0.0799,0.00851],"force_p95":96.46321,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":100.06335,"mean_force":26.24775,"phase_index":3.0,"phase_name":"align_entry","phase_type":"align","tcp_position_centroid":[0.49267,0.02159,0.04768]},{"body_a":"attachment","body_b":"peg","contact_count":362.0,"contact_point_centroid":[0.49865,0.09022,0.0549],"force_p95":97.32098,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":99.47988,"mean_force":69.2313,"phase_index":3.0,"phase_name":"align_entry","phase_type":"align","tcp_position_centroid":[0.49036,0.08534,0.05751]},{"body_a":"peg","body_b":"channel_base_body","contact_count":450.0,"contact_point_centroid":[0.49531,0.11931,0.00868],"force_p95":58.23983,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":62.28144,"mean_force":45.85784,"phase_index":2.0,"phase_name":"grasp_peg","phase_type":"grasp","tcp_position_centroid":[0.48674,0.11913,0.06077]},{"body_a":"attachment","body_b":"peg","contact_count":450.0,"contact_point_centroid":[0.49759,0.11949,0.05651],"force_p95":57.70426,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":61.70846,"mean_force":45.34535,"phase_index":2.0,"phase_name":"grasp_peg","phase_type":"grasp","tcp_position_centroid":[0.48674,0.11913,0.06077]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":5.0,"contact_point_centroid":[0.54264,-0.06111,0.06],"force_p95":53.47313,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":54.50446,"mean_force":45.88147,"phase_index":3.0,"phase_name":"align_entry","phase_type":"align","tcp_position_centroid":[0.49798,-0.06457,0.03662]},{"body_a":"channel_base_body","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.54239,-0.1,0.06498],"force_p95":47.08715,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":47.08715,"mean_force":47.08715,"phase_index":4.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49999,-0.06956,0.03698]},{"body_a":"peg","body_b":"channel_base_body","contact_count":368.0,"contact_point_centroid":[0.49589,0.11911,0.00945],"force_p95":0.60268,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":22.43225,"mean_force":0.64117,"phase_index":1.0,"phase_name":"descend_contact","phase_type":"descend","tcp_position_centroid":[0.4851,0.12145,0.09406]},{"body_a":"attachment","body_b":"peg","contact_count":2.0,"contact_point_centroid":[0.49948,0.11984,0.05886],"force_p95":21.61813,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":21.95194,"mean_force":18.61384,"phase_index":1.0,"phase_name":"descend_contact","phase_type":"descend","tcp_position_centroid":[0.48859,0.11959,0.06382]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":33.0,"contact_point_centroid":[0.47499,0.10643,0.0224],"force_p95":8.44178,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.06163,"mean_force":5.25995,"phase_index":3.0,"phase_name":"align_entry","phase_type":"align","tcp_position_centroid":[0.49175,0.05683,0.05342]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":8.0,"contact_point_centroid":[0.52504,0.04535,0.02439],"force_p95":5.73094,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.54667,"mean_force":1.38055,"phase_index":3.0,"phase_name":"align_entry","phase_type":"align","tcp_position_centroid":[0.49312,-0.0075,0.04261]},{"body_a":"peg","body_b":"channel_base_body","contact_count":531.0,"contact_point_centroid":[0.49636,0.11917,0.00938],"force_p95":0.62132,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.55777,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.49102,0.16069,0.21008]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.4994,0.19878,0.29767]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.49718,0.04436,0.008],"force_p95":0.63682,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.63682,"mean_force":0.63682,"phase_index":4.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49999,-0.06956,0.03698]}],"total_contact_groups":14},"final_pose_error":0.19996,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49629,0.06928,0.0241],"final_tcp_position":[0.50002,-0.06961,0.03699],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":130.33629,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":556.0,"n_steps_budget":930.0,"object_pos_end":[0.49601,0.11902,0.03381],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.19916,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.48455,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":555.0,"raw_peak_contact_force":2.24822,"subtask_id":"reach_peg","tcp_end":[0.48398,0.12399,0.12812],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.0952,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":368.0,"n_steps_budget":600.0,"object_pos_end":[0.49608,0.11905,0.03393],"object_pos_start":[0.49601,0.11902,0.03381],"object_to_goal_dist_end":0.19919,"object_to_goal_dist_start":0.19916,"object_z_max":0.03403,"peak_contact_force":22.43225,"phase_name":"descend_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":370.0,"raw_peak_contact_force":22.43225,"subtask_id":"reach_peg","tcp_end":[0.48863,0.11958,0.06363],"tcp_start":[0.48398,0.12399,0.12812],"tcp_to_object_dist_end":0.03062,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.49335,0.11883,0.03213],"object_pos_start":[0.49608,0.11905,0.03393],"object_to_goal_dist_end":0.1991,"object_to_goal_dist_start":0.19919,"object_z_max":0.03393,"peak_contact_force":59.5073,"phase_name":"grasp_peg","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":900.0,"raw_peak_contact_force":62.28144,"tcp_end":[0.4865,0.11911,0.0604],"tcp_start":[0.48863,0.11958,0.06363],"tcp_to_object_dist_end":0.02909,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":985.0,"n_steps_budget":1000.0,"object_pos_end":[0.49631,0.06928,0.02409],"object_pos_start":[0.49335,0.11883,0.03213],"object_to_goal_dist_end":0.15017,"object_to_goal_dist_start":0.1991,"object_z_max":0.03984,"peak_contact_force":82.00486,"phase_name":"align_entry","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":1421.0,"raw_peak_contact_force":130.33629,"tcp_end":[0.49999,-0.06956,0.03698],"tcp_start":[0.4865,0.11911,0.0604],"tcp_to_object_dist_end":0.13949,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.49629,0.06928,0.0241],"object_pos_start":[0.49631,0.06928,0.02409],"object_to_goal_dist_end":0.15018,"object_to_goal_dist_start":0.15017,"object_z_max":0.02409,"peak_contact_force":47.08715,"phase_name":"push_through","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2.0,"raw_peak_contact_force":47.08715,"subtask_id":"push_progress","tcp_end":[0.50002,-0.06961,0.03699],"tcp_start":[0.49999,-0.06956,0.03698],"tcp_to_object_dist_end":0.13954,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `f85f1938a541e3d507519c8f918b8ca98f1f9baf6ab2f6f3ba2c32478e079e47`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.8427,"average_solve_count":89.0,"average_success_count":89.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_entry.lateral_x":-0.00014,"approach_above.speed":0.12175,"descend_contact.force_threshold":14.24273,"push_through.force_limit":17.51545,"push_through.push_speed":0.03361},"optimized_scores":{"best_composite_score":-0.07565,"best_fitness_score":0.09435,"best_task_score":0.10193},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_base_body","body_b":"link7","contact_count":35.0,"contact_point_centroid":[0.53941,-0.10001,0.06497],"force_p95":139.90639,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":140.17052,"mean_force":83.83847,"phase_index":3.0,"phase_name":"align_entry","phase_type":"align","tcp_position_centroid":[0.49688,-0.06743,0.03719]},{"body_a":"peg","body_b":"channel_base_body","contact_count":680.0,"contact_point_centroid":[0.50446,0.03061,0.00871],"force_p95":97.37818,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":101.66266,"mean_force":39.07355,"phase_index":3.0,"phase_name":"align_entry","phase_type":"align","tcp_position_centroid":[0.50236,-0.00243,0.04944]},{"body_a":"attachment","body_b":"peg","contact_count":377.0,"contact_point_centroid":[0.51388,0.03531,0.0544],"force_p95":97.73671,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":101.45335,"mean_force":69.53205,"phase_index":3.0,"phase_name":"align_entry","phase_type":"align","tcp_position_centroid":[0.50606,0.02977,0.05646]},{"body_a":"peg","body_b":"channel_base_body","contact_count":450.0,"contact_point_centroid":[0.51574,0.06411,0.00885],"force_p95":57.50217,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":58.25568,"mean_force":48.98712,"phase_index":2.0,"phase_name":"grasp_peg","phase_type":"grasp","tcp_position_centroid":[0.50619,0.0643,0.06069]},{"body_a":"attachment","body_b":"peg","contact_count":450.0,"contact_point_centroid":[0.51717,0.06432,0.05678],"force_p95":56.99285,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":57.74502,"mean_force":48.48398,"phase_index":2.0,"phase_name":"grasp_peg","phase_type":"grasp","tcp_position_centroid":[0.50619,0.0643,0.06069]},{"body_a":"channel_base_body","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.54007,-0.1,0.06499],"force_p95":55.23097,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":55.23097,"mean_force":55.23097,"phase_index":4.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49756,-0.06897,0.03739]},{"body_a":"peg","body_b":"channel_base_body","contact_count":268.0,"contact_point_centroid":[0.50586,0.063,0.00938],"force_p95":0.55267,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":31.34765,"mean_force":0.6615,"phase_index":1.0,"phase_name":"descend_contact","phase_type":"descend","tcp_position_centroid":[0.51547,0.06724,0.09394]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.51883,0.06451,0.05876],"force_p95":30.91183,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":30.91183,"mean_force":30.91183,"phase_index":1.0,"phase_name":"descend_contact","phase_type":"descend","tcp_position_centroid":[0.50782,0.06462,0.06351]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":65.0,"contact_point_centroid":[0.525,0.04443,0.05808],"force_p95":10.09296,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":11.60411,"mean_force":7.05176,"phase_index":3.0,"phase_name":"align_entry","phase_type":"align","tcp_position_centroid":[0.50768,0.03293,0.05835]},{"body_a":"peg","body_b":"channel_base_body","contact_count":689.0,"contact_point_centroid":[0.50582,0.06301,0.00936],"force_p95":0.55986,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.88411,"mean_force":0.5662,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.51183,0.13256,0.20752]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":34.0,"contact_point_centroid":[0.53102,0.06295,0.03156],"force_p95":1.1362,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.98455,"mean_force":0.48262,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.49982,0.19767,0.29658]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":6.0,"contact_point_centroid":[0.47499,0.03953,0.02766],"force_p95":0.6347,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.66352,"mean_force":0.44505,"phase_index":3.0,"phase_name":"align_entry","phase_type":"align","tcp_position_centroid":[0.49894,-0.0207,0.04406]},{"body_a":"peg","body_b":"channel_base_body","contact_count":2.0,"contact_point_centroid":[0.50167,0.0408,0.0079],"force_p95":0.62176,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.62545,"mean_force":0.58849,"phase_index":4.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49756,-0.06896,0.0374]}],"total_contact_groups":13},"final_pose_error":0.19995,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50345,0.01596,0.02401],"final_tcp_position":[0.49756,-0.06899,0.03738],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.52962,0.06295,0.04]},"peak_contact_force":140.17052,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":717.0,"n_steps_budget":1000.0,"object_pos_end":[0.50601,0.06294,0.03381],"object_pos_start":[0.52962,0.06295,0.04],"object_to_goal_dist_end":0.1432,"object_to_goal_dist_start":0.14598,"object_z_max":0.04001,"peak_contact_force":0.54633,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":723.0,"raw_peak_contact_force":3.88411,"subtask_id":"reach_peg","tcp_end":[0.52456,0.07008,0.12468],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.09302,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":268.0,"n_steps_budget":600.0,"object_pos_end":[0.50604,0.063,0.0338],"object_pos_start":[0.50601,0.06294,0.03381],"object_to_goal_dist_end":0.14326,"object_to_goal_dist_start":0.1432,"object_z_max":0.03381,"peak_contact_force":31.34765,"phase_name":"descend_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":269.0,"raw_peak_contact_force":31.34765,"subtask_id":"reach_peg","tcp_end":[0.50777,0.06459,0.06329],"tcp_start":[0.52456,0.07008,0.12468],"tcp_to_object_dist_end":0.02958,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50499,0.06254,0.03257],"object_pos_start":[0.50604,0.063,0.0338],"object_to_goal_dist_end":0.14282,"object_to_goal_dist_start":0.14326,"object_z_max":0.0338,"peak_contact_force":57.02598,"phase_name":"grasp_peg","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":900.0,"raw_peak_contact_force":58.25568,"tcp_end":[0.50606,0.06427,0.06042],"tcp_start":[0.50777,0.06459,0.06329],"tcp_to_object_dist_end":0.02792,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":685.0,"n_steps_budget":930.0,"object_pos_end":[0.50338,0.01601,0.02399],"object_pos_start":[0.50499,0.06254,0.03257],"object_to_goal_dist_end":0.09739,"object_to_goal_dist_start":0.14282,"object_z_max":0.03972,"peak_contact_force":0.0,"phase_name":"align_entry","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":1163.0,"raw_peak_contact_force":140.17052,"tcp_end":[0.49756,-0.06894,0.0374],"tcp_start":[0.50606,0.06427,0.06042],"tcp_to_object_dist_end":0.0862,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":2.0,"n_steps_budget":1000.0,"object_pos_end":[0.50345,0.01596,0.02401],"object_pos_start":[0.50338,0.01601,0.02399],"object_to_goal_dist_end":0.09734,"object_to_goal_dist_start":0.09739,"object_z_max":0.024,"peak_contact_force":55.23097,"phase_name":"push_through","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3.0,"raw_peak_contact_force":55.23097,"subtask_id":"push_progress","tcp_end":[0.49756,-0.06899,0.03738],"tcp_start":[0.49756,-0.06894,0.0374],"tcp_to_object_dist_end":0.08619,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```