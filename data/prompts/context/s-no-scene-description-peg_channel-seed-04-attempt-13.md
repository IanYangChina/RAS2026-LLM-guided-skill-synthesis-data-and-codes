## Search State

- **Seed**: 4
- **Iteration**: 14 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 13 | approach → descend → grasp → align → push | linear_cartesian | linear_cartesian | — | linear_cartesian | impedance_motion | position_control | position_control | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | force_exceeded | 9 | -0.3341 | 0.00 | ❌ rejected |
| 12 | approach → push | linear_cartesian | impedance_motion | position_control | admittance_control | pose_tolerance | force_exceeded | 6 | -0.1434 | 0.00 | ❌ rejected |
| 11 | push → align → release → insert | impedance_motion | linear_cartesian | linear_cartesian | impedance_motion | impedance_control | position_control | admittance_control | impedance_control | time_limit | pose_tolerance | pose_tolerance | force_exceeded | 6 | 0.3041 | 0.61 | ❌ rejected |
| 10 | push → align → release → insert | impedance_motion | linear_cartesian | linear_cartesian | impedance_motion | impedance_control | position_control | admittance_control | impedance_control | time_limit | pose_tolerance | pose_tolerance | force_exceeded | 6 | 0.3049 | 0.61 | ❌ rejected |
| 9 | approach → descend → push → retract | arc_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 5 | -0.3000 | 0.00 | ❌ rejected |

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

## Current Skill (Q=-0.334) — your mutation base

```yaml
skill: peg_channel
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

- **Composite score**: -0.334
- **task_score** (E): 0.004
- **fitness_score**: 0.206  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.540

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2362 |
| descend_1 | 1.00 | 1.00 | 0.0425 |
| grasp_1 | 1.00 | 1.00 | 0.0024 |
| align_1 | 1.00 | 1.00 | 0.0085 |
| push_1 | 0.00 | 1.00 | 0.0007 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.517, 0.088, 0.093) | (0.521, 0.084, 0.040)→(0.505, 0.084, 0.034) | 0.166→0.165 | 1.00 / 1.000 | 0.548 | 3.242 |
| descend_1 | descend | 1.00 / step_budget | (0.517, 0.088, 0.093)→(0.514, 0.087, 0.052) | (0.505, 0.084, 0.034)→(0.505, 0.085, 0.030) | 0.165→0.165 | 1.00 / 2.667 | 300.416 | 314.287 |
| grasp_1 | grasp | 1.00 / step_budget | (0.514, 0.087, 0.052)→(0.515, 0.087, 0.054) | (0.505, 0.085, 0.030)→(0.501, 0.085, 0.032) | 0.165→0.165 | 1.00 / 3.000 | 117.910 | 146.364 |
| align_1 | align | 1.00 / step_budget | (0.515, 0.087, 0.054)→(0.520, 0.083, 0.057) | (0.501, 0.085, 0.032)→(0.501, 0.084, 0.031) | 0.165→0.165 | 1.00 / 2.667 | 287.827 | 724.793 |
| push_1 | push | 0.00 / guard_failure | (0.520, 0.083, 0.057)→(0.521, 0.083, 0.058) | (0.501, 0.084, 0.031)→(0.501, 0.084, 0.031) | 0.165→0.165 | 1.00 / 3.000 | 424.319 | 424.319 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.013
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.013
- phase_score: 0.368
- phase_breakdown.approach_peg_score: 0.858
- phase_breakdown.push_through_channel_score: 0.053
- phase_breakdown.descend_peg_score: 0.823

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.226
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.013
- **Median Q (composite search score)**: -0.338
- **K-run variance**: 0.0002
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.315


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `424e8a040c59c1e1e42822c1022320b6050001458f7b9b4937cb9238911ce80b`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `72d2436204c0f1ee3bbdbdfe3e5489661153a48f95d8f0dc3b73e6ce1e1e081b`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.10784,"average_solve_count":102.0,"average_success_count":102.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.align_speed":0.01623,"align_1.pose_tol":0.01891,"approach_1.approach_speed":0.15441,"approach_1.pose_tol":0.01216,"descend_1.descend_speed":0.02828,"descend_1.pose_tol":0.0154,"push_1.push_distance":0.08813,"push_1.push_force_threshold":19.73325,"push_1.push_speed":0.05018},"optimized_scores":{"best_composite_score":-0.34983,"best_fitness_score":0.19017,"best_task_score":4e-05},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":11.0,"contact_point_centroid":[0.53773,0.08359,0.05998],"force_p95":897.05341,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":908.68267,"mean_force":708.09103,"phase_index":3.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.52768,0.07926,0.06145]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":1.0,"contact_point_centroid":[0.54324,0.08596,0.05998],"force_p95":534.54147,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":534.54147,"mean_force":534.54147,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.53661,0.07637,0.06278]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":539.0,"contact_point_centroid":[0.53056,0.08192,0.05991],"force_p95":352.78776,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":358.51878,"mean_force":330.4482,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51868,0.08289,0.06115]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":450.0,"contact_point_centroid":[0.53316,0.08158,0.05998],"force_p95":76.13555,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":77.32038,"mean_force":70.68581,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52132,0.08323,0.06098]},{"body_a":"peg","body_b":"channel_base_body","contact_count":918.0,"contact_point_centroid":[0.5058,0.08089,0.00937],"force_p95":0.55085,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.32595,"mean_force":0.56339,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51448,0.14152,0.19343]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":36.0,"contact_point_centroid":[0.5324,0.0809,0.02649],"force_p95":1.27622,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.70803,"mean_force":0.52144,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49973,0.19845,0.29711]},{"body_a":"peg","body_b":"channel_base_body","contact_count":698.0,"contact_point_centroid":[0.50602,0.08087,0.00938],"force_p95":0.55006,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55006,"mean_force":0.54676,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51968,0.08306,0.06491]},{"body_a":"peg","body_b":"channel_base_body","contact_count":450.0,"contact_point_centroid":[0.50597,0.08087,0.00938],"force_p95":0.55006,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55006,"mean_force":0.54677,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52132,0.08323,0.06098]},{"body_a":"peg","body_b":"channel_base_body","contact_count":20.0,"contact_point_centroid":[0.50518,0.07951,0.00938],"force_p95":0.55006,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55006,"mean_force":0.54682,"phase_index":3.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.52747,0.07925,0.06149]},{"body_a":"peg","body_b":"channel_base_body","contact_count":2.0,"contact_point_centroid":[0.4985,0.09395,0.00938],"force_p95":0.54982,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55006,"mean_force":0.54767,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.53632,0.07627,0.06272]}],"total_contact_groups":10},"final_pose_error":0.08852,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50598,0.08088,0.03378],"final_tcp_position":[0.53712,0.07655,0.06298],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53544,0.08091,0.04]},"peak_contact_force":908.68267,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":947.0,"n_steps_budget":990.0,"object_pos_end":[0.50599,0.08089,0.03378],"object_pos_start":[0.53544,0.08091,0.04],"object_to_goal_dist_end":0.16112,"object_to_goal_dist_start":0.16476,"object_z_max":0.04001,"peak_contact_force":0.55006,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":954.0,"raw_peak_contact_force":4.32595,"subtask_id":"approach_peg","tcp_end":[0.53044,0.08495,0.09293],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.06414,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":698.0,"n_steps_budget":1000.0,"object_pos_end":[0.50597,0.08086,0.03378],"object_pos_start":[0.50599,0.08089,0.03378],"object_to_goal_dist_end":0.16109,"object_to_goal_dist_start":0.16112,"object_z_max":0.03378,"peak_contact_force":328.97423,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1237.0,"raw_peak_contact_force":358.51878,"subtask_id":"descend_peg","tcp_end":[0.52095,0.0832,0.06088],"tcp_start":[0.53044,0.08495,0.09293],"tcp_to_object_dist_end":0.03106,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50596,0.08086,0.03378],"object_pos_start":[0.50597,0.08086,0.03378],"object_to_goal_dist_end":0.16109,"object_to_goal_dist_start":0.16109,"object_z_max":0.03378,"peak_contact_force":65.3089,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":900.0,"raw_peak_contact_force":77.32038,"tcp_end":[0.52149,0.08326,0.06098],"tcp_start":[0.52095,0.0832,0.06088],"tcp_to_object_dist_end":0.03141,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":20.0,"n_steps_budget":600.0,"object_pos_end":[0.50595,0.08088,0.03378],"object_pos_start":[0.50596,0.08086,0.03378],"object_to_goal_dist_end":0.16111,"object_to_goal_dist_start":0.16109,"object_z_max":0.03378,"peak_contact_force":0.0,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":31.0,"raw_peak_contact_force":908.68267,"tcp_end":[0.53603,0.07616,0.06267],"tcp_start":[0.52149,0.08326,0.06098],"tcp_to_object_dist_end":0.04198,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":2.0,"n_steps_budget":1000.0,"object_pos_end":[0.50598,0.08088,0.03378],"object_pos_start":[0.50595,0.08088,0.03378],"object_to_goal_dist_end":0.16112,"object_to_goal_dist_start":0.16111,"object_z_max":0.03378,"peak_contact_force":534.54147,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3.0,"raw_peak_contact_force":534.54147,"subtask_id":"push_through_channel","tcp_end":[0.53712,0.07655,0.06298],"tcp_start":[0.53603,0.07616,0.06267],"tcp_to_object_dist_end":0.04291,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `54762c1e743ba455eff3c9979c2b42f5642abe1893e28eae37dc231d7efcd4e4`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.81982,"average_solve_count":111.0,"average_success_count":111.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.align_speed":0.04203,"align_1.pose_tol":0.01042,"approach_1.approach_speed":0.14121,"approach_1.pose_tol":0.01042,"descend_1.descend_speed":0.02229,"descend_1.pose_tol":0.00702,"push_1.push_distance":0.09919,"push_1.push_force_threshold":22.38764,"push_1.push_speed":0.06274},"optimized_scores":{"best_composite_score":-0.33835,"best_fitness_score":0.20165,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":2,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":19.0,"contact_point_centroid":[0.52505,0.10819,0.05999],"force_p95":554.83119,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":609.9887,"mean_force":501.21568,"phase_index":3.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.51191,0.10768,0.05201]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":1.0,"contact_point_centroid":[0.52515,0.10935,0.05997],"force_p95":389.36957,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":389.36957,"mean_force":389.36957,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51201,0.10779,0.05473]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":456.0,"contact_point_centroid":[0.52506,0.10674,0.05999],"force_p95":276.44292,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":367.43859,"mean_force":219.57789,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.5121,0.10683,0.05228]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.50566,0.11796,0.05495],"force_p95":186.30419,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":186.30419,"mean_force":186.30419,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51201,0.10779,0.05473]},{"body_a":"peg","body_b":"channel_base_body","contact_count":715.0,"contact_point_centroid":[0.51871,0.10539,0.00852],"force_p95":168.66708,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":175.7679,"mean_force":97.44694,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51249,0.10658,0.05872]},{"body_a":"attachment","body_b":"peg","contact_count":546.0,"contact_point_centroid":[0.52337,0.10539,0.05406],"force_p95":169.37744,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":175.27984,"mean_force":127.01039,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51191,0.10665,0.05305]},{"body_a":"peg","body_b":"channel_base_body","contact_count":450.0,"contact_point_centroid":[0.50842,0.10565,0.0079],"force_p95":157.06262,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":166.12606,"mean_force":126.18837,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51193,0.10806,0.05077]},{"body_a":"attachment","body_b":"peg","contact_count":450.0,"contact_point_centroid":[0.51229,0.1053,0.05327],"force_p95":156.6003,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":165.63843,"mean_force":127.9784,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51193,0.10806,0.05077]},{"body_a":"attachment","body_b":"peg","contact_count":20.0,"contact_point_centroid":[0.50769,0.11255,0.05414],"force_p95":157.76692,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":162.49793,"mean_force":122.47439,"phase_index":3.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.5119,0.10766,0.05209]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.50324,0.11998,0.00794],"force_p95":147.12513,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":147.12513,"mean_force":147.12513,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51201,0.10779,0.05473]},{"body_a":"peg","body_b":"channel_base_body","contact_count":20.0,"contact_point_centroid":[0.49969,0.10693,0.00804],"force_p95":138.24975,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":138.62588,"mean_force":111.66827,"phase_index":3.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.5119,0.10766,0.05209]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":447.0,"contact_point_centroid":[0.52502,0.10795,0.06],"force_p95":107.11573,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":119.1116,"mean_force":62.11176,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51193,0.10806,0.05077]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":1.0,"contact_point_centroid":[0.4741,0.10672,0.01],"force_p95":61.7865,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":61.7865,"mean_force":61.7865,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51201,0.10779,0.05473]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":20.0,"contact_point_centroid":[0.47422,0.10713,0.02031],"force_p95":48.29368,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":57.21867,"mean_force":30.22394,"phase_index":3.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.5119,0.10766,0.05209]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":214.0,"contact_point_centroid":[0.47445,0.10724,0.01612],"force_p95":20.55289,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":26.16335,"mean_force":14.21038,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51196,0.10818,0.05105]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":45.0,"contact_point_centroid":[0.52504,0.10484,0.05741],"force_p95":4.15781,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":12.9104,"mean_force":1.42561,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.5121,0.10603,0.05513]}],"total_contact_groups":18},"final_pose_error":0.09934,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49126,0.1071,0.03111],"final_tcp_position":[0.51198,0.10794,0.05506],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.5244,0.10464,0.04]},"peak_contact_force":609.9887,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":973.0,"n_steps_budget":1000.0,"object_pos_end":[0.50599,0.10468,0.03384],"object_pos_start":[0.5244,0.10464,0.04],"object_to_goal_dist_end":0.18488,"object_to_goal_dist_start":0.18624,"object_z_max":0.04,"peak_contact_force":0.54963,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":978.0,"raw_peak_contact_force":3.33087,"subtask_id":"approach_peg","tcp_end":[0.51988,0.1076,0.09304],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.06088,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":715.0,"n_steps_budget":1000.0,"object_pos_end":[0.50154,0.10589,0.02974],"object_pos_start":[0.50599,0.10468,0.03384],"object_to_goal_dist_end":0.18617,"object_to_goal_dist_start":0.18488,"object_z_max":0.03388,"peak_contact_force":367.43859,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1762.0,"raw_peak_contact_force":367.43859,"subtask_id":"descend_peg","tcp_end":[0.51179,0.10741,0.04917],"tcp_start":[0.51988,0.1076,0.09304],"tcp_to_object_dist_end":0.02201,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.49158,0.10742,0.03111],"object_pos_start":[0.50154,0.10589,0.02974],"object_to_goal_dist_end":0.18782,"object_to_goal_dist_start":0.18617,"object_z_max":0.03111,"peak_contact_force":125.69477,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":1561.0,"raw_peak_contact_force":166.12606,"tcp_end":[0.51197,0.10822,0.0511],"tcp_start":[0.51179,0.10741,0.04917],"tcp_to_object_dist_end":0.02857,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":20.0,"n_steps_budget":600.0,"object_pos_end":[0.49131,0.10703,0.03112],"object_pos_start":[0.49158,0.10742,0.03111],"object_to_goal_dist_end":0.18744,"object_to_goal_dist_start":0.18782,"object_z_max":0.03115,"peak_contact_force":412.41663,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":79.0,"raw_peak_contact_force":609.9887,"tcp_end":[0.51201,0.10779,0.05473],"tcp_start":[0.51197,0.10822,0.0511],"tcp_to_object_dist_end":0.03142,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1.0,"n_steps_budget":990.0,"object_pos_end":[0.49126,0.1071,0.03111],"object_pos_start":[0.49131,0.10703,0.03112],"object_to_goal_dist_end":0.18751,"object_to_goal_dist_start":0.18744,"object_z_max":0.03112,"peak_contact_force":389.36957,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":4.0,"raw_peak_contact_force":389.36957,"subtask_id":"push_through_channel","tcp_end":[0.51198,0.10794,0.05506],"tcp_start":[0.51201,0.10779,0.05473],"tcp_to_object_dist_end":0.03168,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `b230a5798f38c3fb8968a6bc74f96ee85fe7026f3170cf8216fc868a1c5c570f`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.53521,"average_solve_count":71.0,"average_success_count":71.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.align_speed":0.03847,"align_1.pose_tol":0.00958,"approach_1.approach_speed":0.17565,"approach_1.pose_tol":0.01682,"descend_1.descend_speed":0.06681,"descend_1.pose_tol":0.01555,"push_1.push_distance":0.12384,"push_1.push_force_threshold":12.97853,"push_1.push_speed":0.04093},"optimized_scores":{"best_composite_score":-0.31405,"best_fitness_score":0.22595,"best_task_score":0.01326},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":19.0,"contact_point_centroid":[0.52535,0.06869,0.05995],"force_p95":627.87709,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":655.70874,"mean_force":502.71574,"phase_index":3.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.51244,0.06807,0.05123]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":1.0,"contact_point_centroid":[0.52553,0.06767,0.05989],"force_p95":349.04701,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":349.04701,"mean_force":349.04701,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51273,0.06608,0.05432]},{"body_a":"peg","body_b":"channel_base_body","contact_count":397.0,"contact_point_centroid":[0.51059,0.0678,0.0084],"force_p95":197.98723,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":216.90283,"mean_force":68.38403,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50109,0.07009,0.06381]},{"body_a":"attachment","body_b":"peg","contact_count":211.0,"contact_point_centroid":[0.51595,0.06842,0.05288],"force_p95":204.50128,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":214.027,"mean_force":127.40695,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50408,0.06929,0.05223]},{"body_a":"peg","body_b":"channel_base_body","contact_count":20.0,"contact_point_centroid":[0.51404,0.0677,0.00753],"force_p95":198.41456,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":201.64804,"mean_force":156.9428,"phase_index":3.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.51241,0.06814,0.05118]},{"body_a":"attachment","body_b":"peg","contact_count":20.0,"contact_point_centroid":[0.52165,0.07248,0.05231],"force_p95":197.98657,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":201.41686,"mean_force":156.46461,"phase_index":3.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.51241,0.06814,0.05118]},{"body_a":"peg","body_b":"channel_base_body","contact_count":450.0,"contact_point_centroid":[0.52346,0.06817,0.00758],"force_p95":188.8398,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":195.64451,"mean_force":167.43103,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51191,0.06964,0.04969]},{"body_a":"attachment","body_b":"peg","contact_count":450.0,"contact_point_centroid":[0.52377,0.06818,0.0518],"force_p95":188.31233,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":194.82087,"mean_force":166.76832,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51191,0.06964,0.04969]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":435.0,"contact_point_centroid":[0.52504,0.06952,0.06],"force_p95":85.21047,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":145.54768,"mean_force":78.56105,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51194,0.06965,0.04979]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.51845,0.07652,0.0528],"force_p95":145.17288,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":145.17288,"mean_force":145.17288,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51273,0.06608,0.05432]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.51939,0.05519,0.00719],"force_p95":145.15831,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":145.15831,"mean_force":145.15831,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51273,0.06608,0.05432]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":67.0,"contact_point_centroid":[0.52507,0.06692,0.04908],"force_p95":49.02782,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":65.25139,"mean_force":18.53405,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50825,0.0691,0.04794]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":44.0,"contact_point_centroid":[0.52508,0.06693,0.05184],"force_p95":18.29735,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":18.7648,"mean_force":5.07415,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51178,0.0693,0.04799]},{"body_a":"peg","body_b":"channel_base_body","contact_count":844.0,"contact_point_centroid":[0.50305,0.06743,0.00935],"force_p95":0.55313,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06903,"mean_force":0.55684,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49889,0.13643,0.19594]}],"total_contact_groups":14},"final_pose_error":0.12376,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50457,0.06534,0.02932],"final_tcp_position":[0.51264,0.066,0.05478],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"peak_contact_force":655.70874,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":860.0,"n_steps_budget":900.0,"object_pos_end":[0.50301,0.06748,0.0338],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14764,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"peak_contact_force":0.54498,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":844.0,"raw_peak_contact_force":2.06903,"subtask_id":"approach_peg","tcp_end":[0.49953,0.07266,0.09438],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.0609,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":397.0,"n_steps_budget":600.0,"object_pos_end":[0.50697,0.06688,0.02743],"object_pos_start":[0.50301,0.06748,0.0338],"object_to_goal_dist_end":0.14758,"object_to_goal_dist_start":0.14764,"object_z_max":0.0338,"peak_contact_force":204.83601,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":675.0,"raw_peak_contact_force":216.90283,"subtask_id":"descend_peg","tcp_end":[0.5104,0.06908,0.04619],"tcp_start":[0.49953,0.07266,0.09438],"tcp_to_object_dist_end":0.01919,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50588,0.06691,0.03067],"object_pos_start":[0.50697,0.06688,0.02743],"object_to_goal_dist_end":0.14732,"object_to_goal_dist_start":0.14758,"object_z_max":0.03067,"peak_contact_force":162.72743,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":1379.0,"raw_peak_contact_force":195.64451,"tcp_end":[0.51197,0.06978,0.05035],"tcp_start":[0.5104,0.06908,0.04619],"tcp_to_object_dist_end":0.0208,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":20.0,"n_steps_budget":600.0,"object_pos_end":[0.50477,0.06538,0.02943],"object_pos_start":[0.50588,0.06691,0.03067],"object_to_goal_dist_end":0.14584,"object_to_goal_dist_start":0.14732,"object_z_max":0.03067,"peak_contact_force":451.06407,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":59.0,"raw_peak_contact_force":655.70874,"tcp_end":[0.51273,0.06608,0.05432],"tcp_start":[0.51197,0.06978,0.05035],"tcp_to_object_dist_end":0.02615,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.50457,0.06534,0.02932],"object_pos_start":[0.50477,0.06538,0.02943],"object_to_goal_dist_end":0.1458,"object_to_goal_dist_start":0.14584,"object_z_max":0.02943,"peak_contact_force":349.04701,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3.0,"raw_peak_contact_force":349.04701,"subtask_id":"push_through_channel","tcp_end":[0.51264,0.066,0.05478],"tcp_start":[0.51273,0.06608,0.05432],"tcp_to_object_dist_end":0.02672,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```