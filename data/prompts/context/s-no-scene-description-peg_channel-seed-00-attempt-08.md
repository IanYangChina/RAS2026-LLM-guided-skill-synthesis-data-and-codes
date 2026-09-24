## Search State

- **Seed**: 0
- **Iteration**: 9 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 8 | approach → push → lift | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | 4 | -0.2249 | 0.00 | ❌ rejected |
| 7 | approach → push | linear_cartesian | impedance_motion | position_control | admittance_control | pose_tolerance | pose_tolerance | 3 | -0.0823 | 0.00 | ❌ rejected |
| 6 | insert → approach → push → retract → lift → insert | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | linear_cartesian | impedance_motion | impedance_control | force_threshold_switch | impedance_control | position_control | position_control | admittance_control | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | 5 | 0.1593 | 0.72 | ❌ rejected |
| 5 | insert → approach → push → retract → lift → insert | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | linear_cartesian | impedance_motion | impedance_control | force_threshold_switch | impedance_control | position_control | position_control | admittance_control | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | 5 | 0.1644 | 0.77 | ✅ accepted |
| 4 | insert → approach → push → retract → lift → insert | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | linear_cartesian | impedance_motion | impedance_control | force_threshold_switch | impedance_control | position_control | position_control | admittance_control | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | 5 | 0.2691 | 0.74 | ❌ rejected |

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

## Current Skill (Q=-0.225) — your mutation base

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

- **Composite score**: -0.225
- **task_score** (E): 0.001
- **fitness_score**: 0.005  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
  → CMA-ES cannot optimise this structure (shaped reward also near zero)
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.230

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_entrance | 0.00 | 0.67 | 0.0001 |
| push_through_channel | 0.33 | 0.67 | 0.3080 |
| lift_out | 1.00 | 1.00 | 0.0804 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_entrance | approach | 0.00 / guard_failure | (0.500, 0.200, 0.300)→(0.500, 0.199, 0.300) | (0.498, 0.080, 0.040)→(0.498, 0.080, 0.040) | 0.161→0.161 | 0.67 / 0.667 | 0.500 | 0.597 |
| push_through_channel | push | 0.33 / step_budget | (0.500, 0.199, 0.300)→(0.500, -0.063, 0.139) | (0.498, 0.080, 0.040)→(0.500, 0.080, 0.036) | 0.161→0.161 | 0.67 / 0.667 | 0.361 | 1.539 |
| lift_out | lift | 1.00 / step_budget | (0.500, -0.063, 0.139)→(0.497, -0.062, 0.219) | (0.500, 0.080, 0.036)→(0.500, 0.080, 0.034) | 0.161→0.161 | 1.00 / 1.000 | 0.547 | 1.010 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.002
- alignment_error: None
- force_efficiency: 0.951
- terminal_score: 0.001
- phase_score: 0.010
- phase_breakdown.traverse_channel_score: 0.008
- phase_breakdown.reach_entrance_score: 0.015

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.007
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.001
- **Median Q (composite search score)**: -0.225
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.3
- **Final σ (mean)**: 0.327


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.90604,"average_solve_count":149.0,"average_success_count":149.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_entrance.approach_speed":0.06123,"lift_out.lift_speed":0.06202,"push_through_channel.push_distance":0.17018,"push_through_channel.push_speed":0.04346},"optimized_scores":{"best_composite_score":-0.22644,"best_fitness_score":0.00356,"best_task_score":0.00034},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":980.0,"contact_point_centroid":[0.50371,0.06156,0.00936],"force_p95":0.58368,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.17216,"mean_force":0.55479,"phase_index":1.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49174,-0.00537,0.17686]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":3.0,"contact_point_centroid":[0.52696,0.06158,0.02249],"force_p95":0.61991,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.62339,"mean_force":0.57851,"phase_index":0.0,"phase_name":"approach_entrance","phase_type":"approach","tcp_position_centroid":[0.49984,0.19956,0.30027]},{"body_a":"peg","body_b":"channel_base_body","contact_count":272.0,"contact_point_centroid":[0.50377,0.06159,0.00939],"force_p95":0.55248,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55492,"mean_force":0.54639,"phase_index":2.0,"phase_name":"lift_out","phase_type":"lift","tcp_position_centroid":[0.48269,-0.19728,0.10293]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52609,0.06158,0.03398],"force_p95":0.49689,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.5079,"mean_force":0.29704,"phase_index":1.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49956,0.19812,0.29875]}],"total_contact_groups":4},"final_pose_error":0.01975,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.5037,0.06152,0.03384],"final_tcp_position":[0.48267,-0.19703,0.14481],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51096,0.06158,0.04]},"peak_contact_force":2.17216,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.51091,0.06158,0.03998],"object_pos_start":[0.51096,0.06158,0.04],"object_to_goal_dist_end":0.142,"object_to_goal_dist_start":0.14201,"object_z_max":0.04,"peak_contact_force":0.52352,"phase_name":"approach_entrance","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3.0,"raw_peak_contact_force":0.62339,"subtask_id":"reach_entrance","tcp_end":[0.49987,0.19942,0.30016],"tcp_start":[0.49986,0.19952,0.30023],"tcp_to_object_dist_end":0.29464,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5037,0.06153,0.03383],"object_pos_start":[0.51073,0.06158,0.03993],"object_to_goal_dist_end":0.14172,"object_to_goal_dist_start":0.14199,"object_z_max":0.03993,"peak_contact_force":0.5414,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":996.0,"raw_peak_contact_force":2.17216,"subtask_id":"traverse_channel","tcp_end":[0.48547,-0.19806,0.06433],"tcp_start":[0.49987,0.19942,0.30016],"tcp_to_object_dist_end":0.26201,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":272.0,"n_steps_budget":1000.0,"object_pos_end":[0.5037,0.06152,0.03384],"object_pos_start":[0.5037,0.06153,0.03383],"object_to_goal_dist_end":0.1417,"object_to_goal_dist_start":0.14172,"object_z_max":0.03384,"peak_contact_force":0.5444,"phase_name":"lift_out","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":272.0,"raw_peak_contact_force":0.55492,"tcp_end":[0.48267,-0.19703,0.14481],"tcp_start":[0.48547,-0.19806,0.06433],"tcp_to_object_dist_end":0.28214,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `f24211f27d4adabdef509c8ed61621317fdbcaa86fc9ac888f85a717335bb714`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.26087,"average_solve_count":46.0,"average_success_count":46.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_entrance.approach_speed":0.05289,"lift_out.lift_speed":0.05062,"push_through_channel.push_distance":0.14904,"push_through_channel.push_speed":0.02972},"optimized_scores":{"best_composite_score":-0.22502,"best_fitness_score":0.00498,"best_task_score":0.00029},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":270.0,"contact_point_centroid":[0.50097,0.11607,0.00932],"force_p95":0.73748,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.92055,"mean_force":0.57504,"phase_index":2.0,"phase_name":"lift_out","phase_type":"lift","tcp_position_centroid":[0.49873,0.19887,0.34009]}],"total_contact_groups":1},"final_pose_error":0.01988,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50096,0.11599,0.03394],"final_tcp_position":[0.49892,0.19892,0.38014],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50095,0.11604,0.04]},"peak_contact_force":1.92055,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.50095,0.11604,0.03996],"object_pos_start":[0.50095,0.11604,0.04],"object_to_goal_dist_end":0.19604,"object_to_goal_dist_start":0.19604,"object_z_max":0.04,"peak_contact_force":0.0,"phase_name":"approach_entrance","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_entrance","tcp_end":[0.49987,0.19942,0.30016],"tcp_start":[0.49986,0.19952,0.30023],"tcp_to_object_dist_end":0.27323,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":2.0,"n_steps_budget":1000.0,"object_pos_end":[0.50095,0.11604,0.03961],"object_pos_start":[0.50095,0.11604,0.03976],"object_to_goal_dist_end":0.19604,"object_to_goal_dist_start":0.19604,"object_z_max":0.03976,"peak_contact_force":0.0,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"traverse_channel","tcp_end":[0.49981,0.1994,0.29999],"tcp_start":[0.49982,0.19941,0.30007],"tcp_to_object_dist_end":0.27341,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":281.0,"n_steps_budget":1000.0,"object_pos_end":[0.50096,0.11599,0.03394],"object_pos_start":[0.50095,0.11604,0.03941],"object_to_goal_dist_end":0.19609,"object_to_goal_dist_start":0.19604,"object_z_max":0.03941,"peak_contact_force":0.55402,"phase_name":"lift_out","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":270.0,"raw_peak_contact_force":1.92055,"tcp_end":[0.49892,0.19892,0.38014],"tcp_start":[0.49981,0.1994,0.29999],"tcp_to_object_dist_end":0.35599,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `d098a7862ff18c9bbe982af3446a89a0fa6bcfa8790d7d955f65b2375d67a881`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.0625,"average_solve_count":144.0,"average_success_count":144.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_entrance.approach_speed":0.03804,"lift_out.lift_speed":0.08828,"push_through_channel.push_distance":0.14134,"push_through_channel.push_speed":0.01661},"optimized_scores":{"best_composite_score":-0.22331,"best_fitness_score":0.00669,"best_task_score":0.00115},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":976.0,"contact_point_centroid":[0.49523,0.06393,0.00938],"force_p95":0.55692,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44546,"mean_force":0.55422,"phase_index":1.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50622,-0.0017,0.17054]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":3.0,"contact_point_centroid":[0.46898,0.06387,0.0289],"force_p95":1.14974,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.16907,"mean_force":0.99124,"phase_index":0.0,"phase_name":"approach_entrance","phase_type":"approach","tcp_position_centroid":[0.49984,0.19956,0.30027]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":25.0,"contact_point_centroid":[0.47162,0.06388,0.0377],"force_p95":0.7346,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.81305,"mean_force":0.29616,"phase_index":1.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49963,0.19665,0.29742]},{"body_a":"peg","body_b":"channel_base_body","contact_count":270.0,"contact_point_centroid":[0.49502,0.06369,0.0094],"force_p95":0.55078,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55315,"mean_force":0.54514,"phase_index":2.0,"phase_name":"lift_out","phase_type":"lift","tcp_position_centroid":[0.51043,-0.18903,0.09121]}],"total_contact_groups":4},"final_pose_error":0.01974,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49514,0.06359,0.03402],"final_tcp_position":[0.51048,-0.1888,0.13325],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"peak_contact_force":2.44546,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.481,0.06388,0.03996],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.14513,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"peak_contact_force":0.97578,"phase_name":"approach_entrance","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3.0,"raw_peak_contact_force":1.16907,"subtask_id":"reach_entrance","tcp_end":[0.49987,0.19942,0.30016],"tcp_start":[0.49986,0.19952,0.30023],"tcp_to_object_dist_end":0.29399,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49493,0.06364,0.03401],"object_pos_start":[0.48131,0.06388,0.03994],"object_to_goal_dist_end":0.14386,"object_to_goal_dist_start":0.14509,"object_z_max":0.03995,"peak_contact_force":0.54301,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1001.0,"raw_peak_contact_force":2.44546,"subtask_id":"traverse_channel","tcp_end":[0.51357,-0.18983,0.05272],"tcp_start":[0.49987,0.19942,0.30016],"tcp_to_object_dist_end":0.25484,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":270.0,"n_steps_budget":720.0,"object_pos_end":[0.49514,0.06359,0.03402],"object_pos_start":[0.49493,0.06364,0.03401],"object_to_goal_dist_end":0.14379,"object_to_goal_dist_start":0.14386,"object_z_max":0.03402,"peak_contact_force":0.54161,"phase_name":"lift_out","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":270.0,"raw_peak_contact_force":0.55315,"tcp_end":[0.51048,-0.1888,0.13325],"tcp_start":[0.51357,-0.18983,0.05272],"tcp_to_object_dist_end":0.27163,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```