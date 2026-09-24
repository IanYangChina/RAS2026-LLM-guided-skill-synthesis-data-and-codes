## Search State

- **Seed**: 1
- **Iteration**: 4 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 3 | approach → align → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 5 | -0.1615 | 0.00 | ❌ rejected |
| 2 | approach → align → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 4 | 0.1072 | 0.00 | ❌ rejected |
| 1 | rotate → align → push → align | impedance_motion | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | position_control | impedance_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 3 | 0.1706 | 0.42 | ✅ accepted |
| 0 | rotate → align → push → align | impedance_motion | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | position_control | impedance_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 3 | 0.1472 | 0.30 | ✅ accepted |

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

## Current Skill (Q=-0.161) — your mutation base

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

- **Composite score**: -0.161
- **task_score** (E): 0.001
- **fitness_score**: 0.149  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.310

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_above | 1.00 | 1.00 | 0.1934 |
| align_lateral | 1.00 | 1.00 | 0.1009 |
| push_channel | 0.00 | 1.00 | 0.0001 |
| retract_up | 1.00 | 1.00 | 0.0408 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_above | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.481, 0.087, 0.146) | (0.483, 0.080, 0.040)→(0.497, 0.080, 0.034) | 0.161→0.160 | 1.00 / 1.000 | 0.566 | 2.857 |
| align_lateral | align | 1.00 / step_budget | (0.481, 0.087, 0.146)→(0.499, 0.081, 0.047) | (0.497, 0.080, 0.034)→(0.501, 0.079, 0.028) | 0.160→0.160 | 1.00 / 2.000 | 179.849 | 402.742 |
| push_channel | push | 0.00 / guard_failure | (0.499, 0.081, 0.047)→(0.500, 0.081, 0.047) | (0.501, 0.079, 0.028)→(0.501, 0.079, 0.027) | 0.160→0.160 | 1.00 / 2.000 | 104.154 | 106.321 |
| retract_up | retract | 1.00 / step_budget | (0.500, 0.081, 0.047)→(0.496, 0.081, 0.088) | (0.501, 0.079, 0.027)→(0.500, 0.079, 0.034) | 0.160→0.160 | 1.00 / 1.000 | 0.579 | 134.833 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.006
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.003
- phase_score: 0.247
- phase_breakdown.approach_above_score: 0.822
- phase_breakdown.push_progress_score: 0.000

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.149
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.003
- **Median Q (composite search score)**: -0.162
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.209


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.10366,"average_solve_count":164.0,"average_success_count":164.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_lateral.lateral_offset_x":0.00233,"align_lateral.lateral_offset_y":0.00042,"approach_above.approach_speed":0.0312,"push_channel.lateral_retry_x":-0.00199,"retract_up.retract_speed":0.05567},"optimized_scores":{"best_composite_score":-0.16188,"best_fitness_score":0.14812,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":369.0,"contact_point_centroid":[0.50559,0.11661,0.00906],"force_p95":199.47554,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":203.19039,"mean_force":40.93971,"phase_index":1.0,"phase_name":"align_lateral","phase_type":"align","tcp_position_centroid":[0.49882,0.11874,0.08945]},{"body_a":"attachment","body_b":"peg","contact_count":99.0,"contact_point_centroid":[0.51549,0.11755,0.0538],"force_p95":200.15793,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":202.64886,"mean_force":150.61254,"phase_index":1.0,"phase_name":"align_lateral","phase_type":"align","tcp_position_centroid":[0.50358,0.11774,0.05297]},{"body_a":"peg","body_b":"channel_base_body","contact_count":354.0,"contact_point_centroid":[0.5065,0.11697,0.00929],"force_p95":64.37217,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":141.20526,"mean_force":8.63987,"phase_index":3.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.50759,0.11823,0.07099]},{"body_a":"attachment","body_b":"peg","contact_count":73.0,"contact_point_centroid":[0.52206,0.11807,0.05555],"force_p95":92.05165,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":140.55562,"mean_force":39.33568,"phase_index":3.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.51014,0.11871,0.05512]},{"body_a":"peg","body_b":"channel_base_body","contact_count":3.0,"contact_point_centroid":[0.5232,0.11928,0.00736],"force_p95":134.2181,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":135.21017,"mean_force":122.01309,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50983,0.11871,0.04838]},{"body_a":"attachment","body_b":"peg","contact_count":3.0,"contact_point_centroid":[0.52178,0.11775,0.05088],"force_p95":133.55535,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":134.53979,"mean_force":121.5314,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50983,0.11871,0.04838]},{"body_a":"peg","body_b":"channel_base_body","contact_count":573.0,"contact_point_centroid":[0.50099,0.116,0.00938],"force_p95":0.60731,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.92055,"mean_force":0.55771,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.4981,0.16024,0.22129]}],"total_contact_groups":7},"final_pose_error":0.00999,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50481,0.11711,0.03396],"final_tcp_position":[0.50661,0.11804,0.08908],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50095,0.11604,0.04]},"peak_contact_force":203.19039,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":589.0,"n_steps_budget":1000.0,"object_pos_end":[0.50092,0.11605,0.03386],"object_pos_start":[0.50095,0.11604,0.04],"object_to_goal_dist_end":0.19615,"object_to_goal_dist_start":0.19604,"object_z_max":0.04,"peak_contact_force":0.60541,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":573.0,"raw_peak_contact_force":1.92055,"subtask_id":"approach_above","tcp_end":[0.49791,0.1217,0.14732],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11365,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":369.0,"n_steps_budget":720.0,"object_pos_end":[0.50586,0.11697,0.03007],"object_pos_start":[0.50092,0.11605,0.03386],"object_to_goal_dist_end":0.19731,"object_to_goal_dist_start":0.19615,"object_z_max":0.03398,"peak_contact_force":196.40781,"phase_name":"align_lateral","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":468.0,"raw_peak_contact_force":203.19039,"tcp_end":[0.50973,0.11869,0.04836],"tcp_start":[0.49791,0.1217,0.14732],"tcp_to_object_dist_end":0.01877,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.50585,0.117,0.03007],"object_pos_start":[0.50586,0.11697,0.03007],"object_to_goal_dist_end":0.19734,"object_to_goal_dist_start":0.19731,"object_z_max":0.03007,"peak_contact_force":135.21017,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":6.0,"raw_peak_contact_force":135.21017,"subtask_id":"push_progress","tcp_end":[0.50999,0.11873,0.04846],"tcp_start":[0.50991,0.11873,0.0484],"tcp_to_object_dist_end":0.01893,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":354.0,"n_steps_budget":600.0,"object_pos_end":[0.50481,0.11711,0.03396],"object_pos_start":[0.50581,0.11703,0.03008],"object_to_goal_dist_end":0.19726,"object_to_goal_dist_start":0.19736,"object_z_max":0.03435,"peak_contact_force":0.56144,"phase_name":"retract_up","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":427.0,"raw_peak_contact_force":141.20526,"tcp_end":[0.50661,0.11804,0.08908],"tcp_start":[0.50999,0.11873,0.04846],"tcp_to_object_dist_end":0.05516,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `8416ac3bebb4dbec2abbf751596843a33db171fd8d70765023f3b940d846bd0c`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.10897,"average_solve_count":156.0,"average_success_count":156.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_lateral.lateral_offset_x":-0.00366,"align_lateral.lateral_offset_y":-0.00113,"approach_above.approach_speed":0.04207,"push_channel.lateral_retry_x":0.00271,"retract_up.retract_speed":0.03888},"optimized_scores":{"best_composite_score":-0.16085,"best_fitness_score":0.14915,"best_task_score":0.00307},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_right_wall","contact_count":14.0,"contact_point_centroid":[0.4749,0.06623,0.05954],"force_p95":490.48981,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":516.98095,"mean_force":243.39826,"phase_index":1.0,"phase_name":"align_lateral","phase_type":"align","tcp_position_centroid":[0.48588,0.065,0.05768]},{"body_a":"peg","body_b":"channel_base_body","contact_count":388.0,"contact_point_centroid":[0.4974,0.06379,0.00885],"force_p95":166.602,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":233.68814,"mean_force":34.09081,"phase_index":1.0,"phase_name":"align_lateral","phase_type":"align","tcp_position_centroid":[0.4833,0.0666,0.08888]},{"body_a":"attachment","body_b":"peg","contact_count":106.0,"contact_point_centroid":[0.50158,0.06486,0.05288],"force_p95":192.36297,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":232.89302,"mean_force":122.78988,"phase_index":1.0,"phase_name":"align_lateral","phase_type":"align","tcp_position_centroid":[0.48969,0.06481,0.05257]},{"body_a":"peg","body_b":"channel_base_body","contact_count":323.0,"contact_point_centroid":[0.49779,0.06319,0.00895],"force_p95":89.07436,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":152.74414,"mean_force":12.9936,"phase_index":3.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.49278,0.06407,0.06822]},{"body_a":"attachment","body_b":"peg","contact_count":92.0,"contact_point_centroid":[0.50698,0.06409,0.05406],"force_p95":109.94626,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":152.18348,"mean_force":43.77072,"phase_index":3.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.49507,0.06426,0.05404]},{"body_a":"peg","body_b":"channel_base_body","contact_count":3.0,"contact_point_centroid":[0.49575,0.06786,0.00523],"force_p95":98.42869,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":98.89975,"mean_force":93.06894,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49479,0.06431,0.0456]},{"body_a":"attachment","body_b":"peg","contact_count":3.0,"contact_point_centroid":[0.50668,0.06423,0.04731],"force_p95":97.71709,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":98.20744,"mean_force":92.19038,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49479,0.06431,0.0456]},{"body_a":"peg","body_b":"channel_base_body","contact_count":692.0,"contact_point_centroid":[0.49541,0.06395,0.00938],"force_p95":0.56578,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44546,"mean_force":0.55784,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.48842,0.13376,0.21854]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":28.0,"contact_point_centroid":[0.47133,0.06388,0.03676],"force_p95":0.92436,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.16907,"mean_force":0.37063,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.49927,0.19829,0.29781]}],"total_contact_groups":9},"final_pose_error":0.00994,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49808,0.06298,0.03377],"final_tcp_position":[0.49151,0.06396,0.08624],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"peak_contact_force":516.98095,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":719.0,"n_steps_budget":1000.0,"object_pos_end":[0.4949,0.06401,0.03397],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.14422,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"peak_contact_force":0.54727,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":720.0,"raw_peak_contact_force":2.44546,"subtask_id":"approach_above","tcp_end":[0.47916,0.07183,0.14547],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11287,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":388.0,"n_steps_budget":720.0,"object_pos_end":[0.49938,0.0628,0.02556],"object_pos_start":[0.4949,0.06401,0.03397],"object_to_goal_dist_end":0.14353,"object_to_goal_dist_start":0.14422,"object_z_max":0.03401,"peak_contact_force":161.9962,"phase_name":"align_lateral","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":508.0,"raw_peak_contact_force":516.98095,"tcp_end":[0.49478,0.0643,0.04564],"tcp_start":[0.47916,0.07183,0.14547],"tcp_to_object_dist_end":0.02065,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.49933,0.06283,0.0255],"object_pos_start":[0.49938,0.0628,0.02556],"object_to_goal_dist_end":0.14356,"object_to_goal_dist_start":0.14353,"object_z_max":0.02556,"peak_contact_force":94.18922,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":6.0,"raw_peak_contact_force":98.89975,"subtask_id":"push_progress","tcp_end":[0.49486,0.0643,0.04559],"tcp_start":[0.4948,0.06432,0.04557],"tcp_to_object_dist_end":0.02063,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":323.0,"n_steps_budget":810.0,"object_pos_end":[0.49808,0.06298,0.03377],"object_pos_start":[0.49929,0.06283,0.02551],"object_to_goal_dist_end":0.14313,"object_to_goal_dist_start":0.14357,"object_z_max":0.03456,"peak_contact_force":0.55395,"phase_name":"retract_up","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":415.0,"raw_peak_contact_force":152.74414,"tcp_end":[0.49151,0.06396,0.08624],"tcp_start":[0.49486,0.0643,0.04559],"tcp_to_object_dist_end":0.05288,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `0188121de1b8142d5ff7a7406b62c43adf6da5520b986a997e46ef53b7d11bf9`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.69072,"average_solve_count":97.0,"average_success_count":97.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_lateral.lateral_offset_x":-0.00104,"align_lateral.lateral_offset_y":0.0006,"approach_above.approach_speed":0.09059,"push_channel.lateral_retry_x":0.00316,"retract_up.retract_speed":0.08552},"optimized_scores":{"best_composite_score":-0.16166,"best_fitness_score":0.14834,"best_task_score":0.00132},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_right_wall","contact_count":67.0,"contact_point_centroid":[0.47497,0.06562,0.05984],"force_p95":458.77729,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":488.05334,"mean_force":385.32793,"phase_index":1.0,"phase_name":"align_lateral","phase_type":"align","tcp_position_centroid":[0.4851,0.06147,0.05813]},{"body_a":"peg","body_b":"channel_base_body","contact_count":432.0,"contact_point_centroid":[0.49677,0.0595,0.00913],"force_p95":155.41072,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":199.49819,"mean_force":24.95053,"phase_index":1.0,"phase_name":"align_lateral","phase_type":"align","tcp_position_centroid":[0.47699,0.06212,0.08952]},{"body_a":"attachment","body_b":"peg","contact_count":122.0,"contact_point_centroid":[0.49886,0.06186,0.05567],"force_p95":183.48025,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":198.69042,"mean_force":86.46153,"phase_index":1.0,"phase_name":"align_lateral","phase_type":"align","tcp_position_centroid":[0.48702,0.0614,0.05619]},{"body_a":"peg","body_b":"channel_base_body","contact_count":330.0,"contact_point_centroid":[0.49757,0.05886,0.00903],"force_p95":72.61376,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":110.55001,"mean_force":9.92716,"phase_index":3.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.4915,0.0607,0.06987]},{"body_a":"attachment","body_b":"peg","contact_count":81.0,"contact_point_centroid":[0.50559,0.06114,0.05448],"force_p95":93.45399,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":109.86576,"mean_force":38.28353,"phase_index":3.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.49371,0.06085,0.05471]},{"body_a":"peg","body_b":"channel_base_body","contact_count":3.0,"contact_point_centroid":[0.49304,0.05749,0.00587],"force_p95":84.67386,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":84.85299,"mean_force":80.93136,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49375,0.061,0.04772]},{"body_a":"attachment","body_b":"peg","contact_count":3.0,"contact_point_centroid":[0.50562,0.06143,0.04894],"force_p95":83.66828,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":83.83404,"mean_force":80.09183,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49375,0.061,0.04772]},{"body_a":"peg","body_b":"channel_base_body","contact_count":648.0,"contact_point_centroid":[0.49437,0.05903,0.00936],"force_p95":0.56113,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.20518,"mean_force":0.56877,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.48167,0.13098,0.21818]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46807,0.05895,0.03796],"force_p95":1.19991,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.42382,"mean_force":0.50385,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.49892,0.19741,0.29664]}],"total_contact_groups":9},"final_pose_error":0.00998,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.4978,0.05817,0.03376],"final_tcp_position":[0.49046,0.06063,0.08828],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.46685,0.05894,0.04]},"peak_contact_force":488.05334,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":677.0,"n_steps_budget":1000.0,"object_pos_end":[0.49399,0.059,0.03389],"object_pos_start":[0.46685,0.05894,0.04],"object_to_goal_dist_end":0.13926,"object_to_goal_dist_start":0.14284,"object_z_max":0.04001,"peak_contact_force":0.54535,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":683.0,"raw_peak_contact_force":4.20518,"subtask_id":"approach_above","tcp_end":[0.46605,0.06707,0.14552],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11536,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":432.0,"n_steps_budget":750.0,"object_pos_end":[0.49911,0.05809,0.02688],"object_pos_start":[0.49399,0.059,0.03389],"object_to_goal_dist_end":0.13871,"object_to_goal_dist_start":0.13926,"object_z_max":0.03393,"peak_contact_force":181.14215,"phase_name":"align_lateral","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":621.0,"raw_peak_contact_force":488.05334,"tcp_end":[0.49374,0.06103,0.04778],"tcp_start":[0.46605,0.06707,0.14552],"tcp_to_object_dist_end":0.02178,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.49906,0.05808,0.02679],"object_pos_start":[0.49911,0.05809,0.02688],"object_to_goal_dist_end":0.13872,"object_to_goal_dist_start":0.13871,"object_z_max":0.02688,"peak_contact_force":83.06161,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":6.0,"raw_peak_contact_force":84.85299,"subtask_id":"push_progress","tcp_end":[0.49381,0.06096,0.04768],"tcp_start":[0.49377,0.06098,0.04768],"tcp_to_object_dist_end":0.02173,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":330.0,"n_steps_budget":600.0,"object_pos_end":[0.4978,0.05817,0.03376],"object_pos_start":[0.49897,0.05809,0.02673],"object_to_goal_dist_end":0.13833,"object_to_goal_dist_start":0.13873,"object_z_max":0.03433,"peak_contact_force":0.6207,"phase_name":"retract_up","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":411.0,"raw_peak_contact_force":110.55001,"tcp_end":[0.49046,0.06063,0.08828],"tcp_start":[0.49381,0.06096,0.04768],"tcp_to_object_dist_end":0.05507,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```