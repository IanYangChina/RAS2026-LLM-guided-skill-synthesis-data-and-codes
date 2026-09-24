## Search State

- **Seed**: 7
- **Iteration**: 15 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 14 | approach → align → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | admittance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 7 | -0.2374 | 0.10 | ❌ rejected |
| 13 | descend → insert → grasp → approach → align | linear_cartesian | impedance_motion | — | linear_cartesian | linear_cartesian | admittance_control | admittance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 5 | -0.1315 | 0.26 | ❌ rejected |
| 12 | approach → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | position_control | admittance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | 5 | -0.1797 | 0.00 | ❌ rejected |
| 11 | approach → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | position_control | admittance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | 4 | -0.0423 | 0.01 | ❌ rejected |
| 10 | descend → insert → grasp → approach → align | linear_cartesian | impedance_motion | — | linear_cartesian | linear_cartesian | admittance_control | admittance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 5 | -0.1314 | 0.26 | ❌ rejected |

**Proposal policy**: task_score is 0.10 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.237) — your mutation base

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

- **Composite score**: -0.237
- **task_score** (E): 0.104
- **fitness_score**: 0.173  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.410

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_entrance | 1.00 | 1.00 | 0.1805 |
| align_entrance | 1.00 | 1.00 | 0.0992 |
| push_channel | 0.00 | 1.00 | 0.0001 |
| retract_tcp | 1.00 | 1.00 | 0.0644 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_entrance | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.497, 0.094, 0.154) | (0.509, 0.098, 0.040)→(0.502, 0.098, 0.034) | 0.179→0.178 | 1.00 / 1.000 | 0.537 | 2.732 |
| align_entrance | align | 1.00 / step_budget | (0.497, 0.094, 0.154)→(0.502, 0.080, 0.056) | (0.502, 0.098, 0.034)→(0.502, 0.083, 0.031) | 0.178→0.164 | 1.00 / 3.000 | 215.341 | 292.279 |
| push_channel | push | 0.00 / guard_failure | (0.502, 0.080, 0.056)→(0.502, 0.080, 0.056) | (0.502, 0.083, 0.031)→(0.502, 0.083, 0.031) | 0.164→0.164 | 1.00 / 2.667 | 76.669 | 174.876 |
| retract_tcp | retract | 1.00 / step_budget | (0.502, 0.080, 0.056)→(0.498, 0.079, 0.120) | (0.502, 0.083, 0.031)→(0.500, 0.071, 0.031) | 0.163→0.151 | 1.00 / 1.000 | 0.603 | 165.381 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.125
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.112
- phase_score: 0.226
- phase_breakdown.push_through_score: 0.000
- phase_breakdown.reach_entrance_score: 0.754

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.180
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.112
- **Median Q (composite search score)**: -0.232
- **K-run variance**: 0.0001
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.267


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.26974,"average_solve_count":152.0,"average_success_count":152.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_entrance.align_lateral_x":-0.00149,"align_entrance.align_lateral_y":-0.01213,"approach_entrance.approach_speed":0.03901,"push_channel.push_force_threshold":22.10181,"push_channel.retry_offset_x":0.00946,"push_channel.retry_offset_y":-0.00114,"push_channel.retry_offset_z":-3e-05},"optimized_scores":{"best_composite_score":-0.23152,"best_fitness_score":0.17848,"best_task_score":0.10225},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_right_wall","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.47272,0.11997,0.06],"force_p95":253.46564,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":257.88237,"mean_force":213.7151,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50273,0.08017,0.05314]},{"body_a":"peg","body_b":"channel_base_body","contact_count":498.0,"contact_point_centroid":[0.50093,0.10024,0.00882],"force_p95":128.35999,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":246.98476,"mean_force":41.7379,"phase_index":1.0,"phase_name":"align_entrance","phase_type":"align","tcp_position_centroid":[0.49334,0.08556,0.08651]},{"body_a":"attachment","body_b":"peg","contact_count":190.0,"contact_point_centroid":[0.50042,0.09439,0.05573],"force_p95":150.66276,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":246.41307,"mean_force":93.64954,"phase_index":1.0,"phase_name":"align_entrance","phase_type":"align","tcp_position_centroid":[0.50008,0.07999,0.0652]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":150.0,"contact_point_centroid":[0.47108,0.11995,0.06],"force_p95":196.32196,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":207.50059,"mean_force":129.21572,"phase_index":1.0,"phase_name":"align_entrance","phase_type":"align","tcp_position_centroid":[0.50007,0.07994,0.06524]},{"body_a":"peg","body_b":"channel_base_body","contact_count":3.0,"contact_point_centroid":[0.50545,0.08884,0.00585],"force_p95":195.55134,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":198.12093,"mean_force":155.92825,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50273,0.08021,0.05315]},{"body_a":"attachment","body_b":"peg","contact_count":3.0,"contact_point_centroid":[0.50274,0.08025,0.04644],"force_p95":194.98066,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":197.54748,"mean_force":155.34202,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50273,0.08021,0.05315]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":11.0,"contact_point_centroid":[0.47263,0.11999,0.06],"force_p95":186.83887,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":188.39007,"mean_force":101.93267,"phase_index":3.0,"phase_name":"retract_tcp","phase_type":"retract","tcp_position_centroid":[0.50181,0.08018,0.06499]},{"body_a":"world","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.50193,0.14278,-0.00027],"force_p95":140.78309,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":149.05978,"mean_force":87.53789,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50273,0.08021,0.05315]},{"body_a":"world","body_b":"link7","contact_count":5.0,"contact_point_centroid":[0.50189,0.14267,-0.00015],"force_p95":129.17159,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":138.71202,"mean_force":82.61625,"phase_index":1.0,"phase_name":"align_entrance","phase_type":"align","tcp_position_centroid":[0.5027,0.08008,0.05337]},{"body_a":"peg","body_b":"channel_base_body","contact_count":194.0,"contact_point_centroid":[0.50058,0.09457,0.00893],"force_p95":49.4165,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":134.99533,"mean_force":9.26644,"phase_index":3.0,"phase_name":"retract_tcp","phase_type":"retract","tcp_position_centroid":[0.50015,0.0798,0.08648]},{"body_a":"attachment","body_b":"peg","contact_count":51.0,"contact_point_centroid":[0.50226,0.09201,0.05269],"force_p95":132.79495,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":134.9173,"mean_force":33.24617,"phase_index":3.0,"phase_name":"retract_tcp","phase_type":"retract","tcp_position_centroid":[0.50226,0.08034,0.06157]},{"body_a":"peg","body_b":"link7","contact_count":51.0,"contact_point_centroid":[0.50147,0.12516,0.05731],"force_p95":70.61386,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":78.89728,"mean_force":53.65011,"phase_index":1.0,"phase_name":"align_entrance","phase_type":"align","tcp_position_centroid":[0.49493,0.08074,0.09142]},{"body_a":"world","body_b":"link7","contact_count":5.0,"contact_point_centroid":[0.50203,0.14293,-0.00016],"force_p95":67.23349,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":69.09379,"mean_force":36.41664,"phase_index":3.0,"phase_name":"retract_tcp","phase_type":"retract","tcp_position_centroid":[0.50282,0.08039,0.0534]},{"body_a":"peg","body_b":"channel_base_body","contact_count":354.0,"contact_point_centroid":[0.50348,0.1116,0.00937],"force_p95":0.63173,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06328,"mean_force":0.56549,"phase_index":0.0,"phase_name":"approach_entrance","phase_type":"approach","tcp_position_centroid":[0.49805,0.1453,0.22356]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52601,0.11178,0.02875],"force_p95":0.50724,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54079,"mean_force":0.34334,"phase_index":0.0,"phase_name":"approach_entrance","phase_type":"approach","tcp_position_centroid":[0.49965,0.19911,0.29914]}],"total_contact_groups":15},"final_pose_error":0.01979,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.5036,0.09422,0.03382],"final_tcp_position":[0.49836,0.07921,0.1203],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":257.88237,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":376.0,"n_steps_budget":1000.0,"object_pos_end":[0.50372,0.11176,0.03381],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.1919,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":0.53247,"phase_name":"approach_entrance","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":370.0,"raw_peak_contact_force":2.06328,"subtask_id":"reach_entrance","tcp_end":[0.49745,0.09369,0.15417],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.12188,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":498.0,"n_steps_budget":750.0,"object_pos_end":[0.5047,0.09488,0.02677],"object_pos_start":[0.50372,0.11176,0.03381],"object_to_goal_dist_end":0.17545,"object_to_goal_dist_start":0.1919,"object_z_max":0.03843,"peak_contact_force":245.76704,"phase_name":"align_entrance","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":894.0,"raw_peak_contact_force":246.98476,"subtask_id":"reach_entrance","tcp_end":[0.50275,0.08014,0.05315],"tcp_start":[0.49745,0.09369,0.15417],"tcp_to_object_dist_end":0.03029,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.50467,0.09491,0.02674],"object_pos_start":[0.5047,0.09488,0.02677],"object_to_goal_dist_end":0.17548,"object_to_goal_dist_start":0.17545,"object_z_max":0.02677,"peak_contact_force":97.23878,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":11.0,"raw_peak_contact_force":257.88237,"subtask_id":"push_through","tcp_end":[0.50276,0.08035,0.0532],"tcp_start":[0.50274,0.08029,0.05316],"tcp_to_object_dist_end":0.03026,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":194.0,"n_steps_budget":600.0,"object_pos_end":[0.5036,0.09422,0.03382],"object_pos_start":[0.50464,0.09498,0.0267],"object_to_goal_dist_end":0.17437,"object_to_goal_dist_start":0.17555,"object_z_max":0.03387,"peak_contact_force":0.54998,"phase_name":"retract_tcp","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":261.0,"raw_peak_contact_force":188.39007,"tcp_end":[0.49836,0.07921,0.1203],"tcp_start":[0.50276,0.08035,0.0532],"tcp_to_object_dist_end":0.08792,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `3ca2e925d364d2c0fe81fb71ee31d40f947a20e349a0720e1c44a2dd2bc628da`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.22619,"average_solve_count":168.0,"average_success_count":168.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_entrance.align_lateral_x":-0.00107,"align_entrance.align_lateral_y":-0.00922,"approach_entrance.approach_speed":0.03319,"push_channel.push_force_threshold":25.93415,"push_channel.retry_offset_x":0.00589,"push_channel.retry_offset_y":-0.00281,"push_channel.retry_offset_z":-0.00211},"optimized_scores":{"best_composite_score":-0.22953,"best_fitness_score":0.18047,"best_task_score":0.11154},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"link7","contact_count":19.0,"contact_point_centroid":[0.50052,0.14238,-0.00031],"force_p95":229.12827,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":321.29026,"mean_force":160.57841,"phase_index":1.0,"phase_name":"align_entrance","phase_type":"align","tcp_position_centroid":[0.50123,0.0801,0.05341]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":102.0,"contact_point_centroid":[0.46976,0.11996,0.05889],"force_p95":177.36342,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":215.9969,"mean_force":106.06684,"phase_index":1.0,"phase_name":"align_entrance","phase_type":"align","tcp_position_centroid":[0.49929,0.0799,0.06231]},{"body_a":"peg","body_b":"channel_base_body","contact_count":482.0,"contact_point_centroid":[0.49697,0.10646,0.00872],"force_p95":147.13336,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":215.34679,"mean_force":41.05471,"phase_index":1.0,"phase_name":"align_entrance","phase_type":"align","tcp_position_centroid":[0.49299,0.08637,0.08683]},{"body_a":"attachment","body_b":"peg","contact_count":157.0,"contact_point_centroid":[0.49914,0.09946,0.05307],"force_p95":173.34006,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":214.83153,"mean_force":96.54814,"phase_index":1.0,"phase_name":"align_entrance","phase_type":"align","tcp_position_centroid":[0.49936,0.07995,0.062]},{"body_a":"peg","body_b":"channel_base_body","contact_count":191.0,"contact_point_centroid":[0.49526,0.09953,0.00894],"force_p95":60.09353,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":164.32578,"mean_force":8.41846,"phase_index":3.0,"phase_name":"retract_tcp","phase_type":"retract","tcp_position_centroid":[0.49929,0.0798,0.08699]},{"body_a":"attachment","body_b":"peg","contact_count":48.0,"contact_point_centroid":[0.50063,0.11012,0.05284],"force_p95":65.92244,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":163.73327,"mean_force":31.40982,"phase_index":3.0,"phase_name":"retract_tcp","phase_type":"retract","tcp_position_centroid":[0.50098,0.08048,0.06221]},{"body_a":"peg","body_b":"channel_base_body","contact_count":3.0,"contact_point_centroid":[0.49716,0.11168,0.00617],"force_p95":148.34371,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":149.696,"mean_force":135.8641,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50142,0.08008,0.05417]},{"body_a":"attachment","body_b":"peg","contact_count":3.0,"contact_point_centroid":[0.50122,0.11679,0.04712],"force_p95":147.83066,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":149.18374,"mean_force":135.40616,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50142,0.08008,0.05417]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":11.0,"contact_point_centroid":[0.475,0.11999,0.05134],"force_p95":119.73746,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":120.20172,"mean_force":60.57211,"phase_index":3.0,"phase_name":"retract_tcp","phase_type":"retract","tcp_position_centroid":[0.50033,0.08013,0.06801]},{"body_a":"peg","body_b":"link7","contact_count":75.0,"contact_point_centroid":[0.49497,0.12966,0.05684],"force_p95":82.33779,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":84.56744,"mean_force":58.45582,"phase_index":1.0,"phase_name":"align_entrance","phase_type":"align","tcp_position_centroid":[0.49546,0.08302,0.09321]},{"body_a":"world","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.501,0.14203,-0.00012],"force_p95":29.77086,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":32.00876,"mean_force":13.87952,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50142,0.08008,0.05417]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":5.0,"contact_point_centroid":[0.525,0.11997,0.05269],"force_p95":20.94294,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":21.13393,"mean_force":8.26259,"phase_index":1.0,"phase_name":"align_entrance","phase_type":"align","tcp_position_centroid":[0.50055,0.0796,0.05572]},{"body_a":"world","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.5011,0.14191,-1e-05],"force_p95":9.06462,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":9.06462,"mean_force":9.06462,"phase_index":3.0,"phase_name":"retract_tcp","phase_type":"retract","tcp_position_centroid":[0.50148,0.08003,0.05447]},{"body_a":"peg","body_b":"channel_base_body","contact_count":352.0,"contact_point_centroid":[0.49637,0.11906,0.00939],"force_p95":0.6347,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.56383,"phase_index":0.0,"phase_name":"approach_entrance","phase_type":"approach","tcp_position_centroid":[0.49804,0.14495,0.22307]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"approach_entrance","phase_type":"approach","tcp_position_centroid":[0.49955,0.19848,0.29798]}],"total_contact_groups":15},"final_pose_error":0.0199,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49351,0.09891,0.0338],"final_tcp_position":[0.49812,0.07917,0.12021],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":321.29026,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":377.0,"n_steps_budget":1000.0,"object_pos_end":[0.49606,0.11931,0.03381],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.19945,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.53352,"phase_name":"approach_entrance","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":376.0,"raw_peak_contact_force":2.24822,"subtask_id":"reach_entrance","tcp_end":[0.49744,0.09369,0.15416],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.12306,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":482.0,"n_steps_budget":750.0,"object_pos_end":[0.49493,0.10001,0.02739],"object_pos_start":[0.49606,0.11931,0.03381],"object_to_goal_dist_end":0.18052,"object_to_goal_dist_start":0.19945,"object_z_max":0.03631,"peak_contact_force":168.98271,"phase_name":"align_entrance","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":840.0,"raw_peak_contact_force":321.29026,"subtask_id":"reach_entrance","tcp_end":[0.50141,0.08009,0.05403],"tcp_start":[0.49744,0.09369,0.15416],"tcp_to_object_dist_end":0.03389,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.49489,0.09997,0.02746],"object_pos_start":[0.49493,0.10001,0.02739],"object_to_goal_dist_end":0.18048,"object_to_goal_dist_start":0.18052,"object_z_max":0.02754,"peak_contact_force":132.41168,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":9.0,"raw_peak_contact_force":149.696,"subtask_id":"push_through","tcp_end":[0.50148,0.08003,0.05447],"tcp_start":[0.50143,0.08006,0.05431],"tcp_to_object_dist_end":0.03421,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":191.0,"n_steps_budget":600.0,"object_pos_end":[0.49351,0.09891,0.0338],"object_pos_start":[0.49489,0.09987,0.02761],"object_to_goal_dist_end":0.17913,"object_to_goal_dist_start":0.18037,"object_z_max":0.03385,"peak_contact_force":0.54064,"phase_name":"retract_tcp","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":251.0,"raw_peak_contact_force":164.32578,"tcp_end":[0.49812,0.07917,0.12021],"tcp_start":[0.50148,0.08003,0.05447],"tcp_to_object_dist_end":0.08876,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `f85f1938a541e3d507519c8f918b8ca98f1f9baf6ab2f6f3ba2c32478e079e47`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.67273,"average_solve_count":110.0,"average_success_count":110.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_entrance.align_lateral_x":-0.00138,"align_entrance.align_lateral_y":-0.01933,"approach_entrance.approach_speed":0.06606,"push_channel.push_force_threshold":21.67576,"push_channel.retry_offset_x":-0.00141,"push_channel.retry_offset_y":-0.00571,"push_channel.retry_offset_z":-0.00223},"optimized_scores":{"best_composite_score":-0.25104,"best_fitness_score":0.15896,"best_task_score":0.0985},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":165.0,"contact_point_centroid":[0.52502,0.11995,0.05945],"force_p95":304.27283,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":308.56273,"mean_force":275.61432,"phase_index":1.0,"phase_name":"align_entrance","phase_type":"align","tcp_position_centroid":[0.50024,0.07983,0.07944]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":88.0,"contact_point_centroid":[0.47498,0.11994,0.05774],"force_p95":265.02456,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":277.13096,"mean_force":180.59712,"phase_index":1.0,"phase_name":"align_entrance","phase_type":"align","tcp_position_centroid":[0.49872,0.07769,0.08035]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":18.0,"contact_point_centroid":[0.475,0.12,0.05122],"force_p95":108.85957,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":143.42613,"mean_force":58.64761,"phase_index":3.0,"phase_name":"retract_tcp","phase_type":"retract","tcp_position_centroid":[0.49979,0.08043,0.06944]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.475,0.11998,0.04561],"force_p95":115.33729,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":117.04907,"mean_force":99.93127,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50169,0.0803,0.06071]},{"body_a":"peg","body_b":"channel_base_body","contact_count":520.0,"contact_point_centroid":[0.50607,0.0624,0.00938],"force_p95":0.55277,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":64.92251,"mean_force":0.86939,"phase_index":1.0,"phase_name":"align_entrance","phase_type":"align","tcp_position_centroid":[0.49372,0.08406,0.09102]},{"body_a":"attachment","body_b":"peg","contact_count":8.0,"contact_point_centroid":[0.50385,0.08041,0.05781],"force_p95":57.86908,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":64.43903,"mean_force":21.38598,"phase_index":1.0,"phase_name":"align_entrance","phase_type":"align","tcp_position_centroid":[0.50078,0.08044,0.06906]},{"body_a":"peg","body_b":"channel_base_body","contact_count":337.0,"contact_point_centroid":[0.50553,0.06305,0.00934],"force_p95":0.60188,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.88411,"mean_force":0.58671,"phase_index":0.0,"phase_name":"approach_entrance","phase_type":"approach","tcp_position_centroid":[0.49799,0.14403,0.22181]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":34.0,"contact_point_centroid":[0.53102,0.06295,0.03156],"force_p95":1.1362,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.98455,"mean_force":0.48262,"phase_index":0.0,"phase_name":"approach_entrance","phase_type":"approach","tcp_position_centroid":[0.49949,0.19675,0.29528]},{"body_a":"peg","body_b":"channel_base_body","contact_count":173.0,"contact_point_centroid":[0.50531,0.03234,0.00898],"force_p95":1.08225,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.86649,"mean_force":0.58184,"phase_index":3.0,"phase_name":"retract_tcp","phase_type":"retract","tcp_position_centroid":[0.49895,0.07993,0.08901]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":1.0,"contact_point_centroid":[0.52501,0.03974,0.06],"force_p95":0.38946,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.38946,"mean_force":0.38946,"phase_index":3.0,"phase_name":"retract_tcp","phase_type":"retract","tcp_position_centroid":[0.5004,0.08043,0.06249]},{"body_a":"peg","body_b":"channel_base_body","contact_count":3.0,"contact_point_centroid":[0.50672,0.04534,0.00965],"force_p95":0.35642,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.35682,"mean_force":0.35306,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50169,0.08032,0.06059]}],"total_contact_groups":11},"final_pose_error":0.01979,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50406,0.0189,0.02408],"final_tcp_position":[0.49811,0.07924,0.12031],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.52962,0.06295,0.04]},"peak_contact_force":308.56273,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":365.0,"n_steps_budget":1000.0,"object_pos_end":[0.50603,0.06301,0.03381],"object_pos_start":[0.52962,0.06295,0.04],"object_to_goal_dist_end":0.14327,"object_to_goal_dist_start":0.14598,"object_z_max":0.04001,"peak_contact_force":0.54453,"phase_name":"approach_entrance","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":371.0,"raw_peak_contact_force":3.88411,"subtask_id":"reach_entrance","tcp_end":[0.4974,0.09366,0.15411],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.12445,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":520.0,"n_steps_budget":750.0,"object_pos_end":[0.50632,0.05525,0.03838],"object_pos_start":[0.50603,0.06301,0.03381],"object_to_goal_dist_end":0.13541,"object_to_goal_dist_start":0.14327,"object_z_max":0.03817,"peak_contact_force":231.27197,"phase_name":"align_entrance","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":781.0,"raw_peak_contact_force":308.56273,"subtask_id":"reach_entrance","tcp_end":[0.50168,0.08029,0.06085],"tcp_start":[0.4974,0.09366,0.15411],"tcp_to_object_dist_end":0.03396,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.50633,0.0549,0.03858],"object_pos_start":[0.50632,0.05525,0.03838],"object_to_goal_dist_end":0.13505,"object_to_goal_dist_start":0.13541,"object_z_max":0.03876,"peak_contact_force":0.35682,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":5.0,"raw_peak_contact_force":117.04907,"subtask_id":"push_through","tcp_end":[0.50166,0.08039,0.06019],"tcp_start":[0.5017,0.08037,0.06035],"tcp_to_object_dist_end":0.03375,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":185.0,"n_steps_budget":600.0,"object_pos_end":[0.50406,0.0189,0.02408],"object_pos_start":[0.50637,0.05421,0.03894],"object_to_goal_dist_end":0.10026,"object_to_goal_dist_start":0.13436,"object_z_max":0.04081,"peak_contact_force":0.71797,"phase_name":"retract_tcp","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":192.0,"raw_peak_contact_force":143.42613,"tcp_end":[0.49811,0.07924,0.12031],"tcp_start":[0.50166,0.08039,0.06019],"tcp_to_object_dist_end":0.11374,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```