## Search State

- **Seed**: 7
- **Iteration**: 7 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 6 | approach → descend → grasp → push → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | — | linear_cartesian | position_control | impedance_control | position_control | admittance_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | time_limit | pose_tolerance | 5 | -0.3038 | 0.00 | ❌ rejected |
| 5 | descend → insert → grasp → approach → align | linear_cartesian | impedance_motion | — | linear_cartesian | linear_cartesian | admittance_control | admittance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 5 | -0.1315 | 0.26 | ❌ rejected |
| 4 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | pose_tolerance | force_exceeded | force_exceeded | 4 | 0.2393 | 0.00 | ❌ rejected |
| 3 | approach → descend → align → insert | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | admittance_control | position_control | admittance_control | pose_tolerance | force_exceeded | pose_tolerance | force_exceeded | 6 | 0.0319 | 0.02 | ❌ rejected |
| 2 | descend → insert → grasp → approach → align | linear_cartesian | impedance_motion | — | linear_cartesian | linear_cartesian | admittance_control | admittance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 5 | -0.1314 | 0.26 | ✅ accepted |

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

## Current Skill (Q=-0.304) — your mutation base

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

- **Composite score**: -0.304
- **task_score** (E): 0.000
- **fitness_score**: 0.066  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
  → CMA-ES cannot optimise this structure (shaped reward also near zero)
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.370

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1830 |
| descend_1 | 1.00 | 1.00 | 0.0025 |
| grasp_1 | 1.00 | 1.00 | 0.0054 |
| push_1 | 0.00 | 1.00 | 0.0006 |
| release_1 | 1.00 | 1.00 | 0.0030 |
| retract_1 | 1.00 | 1.00 | 0.0409 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.505, 0.104, 0.146) | (0.509, 0.098, 0.040)→(0.502, 0.098, 0.034) | 0.179→0.178 | 1.00 / 1.000 | 0.521 | 2.732 |
| descend_1 | descend | 1.00 / step_budget | (0.510, 0.101, 0.041)→(0.510, 0.103, 0.042) | (0.502, 0.098, 0.034)→(0.505, 0.099, 0.030) | 0.178→0.179 | 1.00 / 3.000 | 144.663 | 336.569 |
| grasp_1 | grasp | 1.00 / step_budget | (0.510, 0.103, 0.042)→(0.508, 0.103, 0.041) | (0.483, 0.121, 0.025)→(0.502, 0.169, 0.025) | 0.202→0.250 | 1.00 / 3.000 | 115.300 | 138.987 |
| push_1 | push | 0.00 / guard_failure | (0.510, 0.101, 0.040)→(0.511, 0.100, 0.040) | (0.502, 0.169, 0.025)→(0.503, 0.170, 0.025) | 0.250→0.251 | 1.00 / 2.667 | 581.728 | 846.626 |
| release_1 | release | 1.00 / step_budget | (0.511, 0.100, 0.040)→(0.511, 0.103, 0.041) | (0.503, 0.170, 0.025)→(0.511, 0.191, 0.025) | 0.251→0.273 | 1.00 / 3.000 | 94.937 | 222.823 |
| retract_1 | retract | 1.00 / step_budget | (0.511, 0.103, 0.041)→(0.508, 0.102, 0.082) | (0.511, 0.191, 0.025)→(0.529, 0.247, 0.021) | 0.273→0.331 | 1.00 / 1.333 | 0.621 | 113.698 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.000
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.000
- phase_score: 0.130
- phase_breakdown.reach_peg_score: 0.432
- phase_breakdown.insert_peg_score: 0.000

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.078
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.000
- **Median Q (composite search score)**: -0.297
- **K-run variance**: 0.0002
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.242


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.80455,"average_solve_count":220.0,"average_success_count":220.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.05317,"descend_1.descend_speed":0.0293,"push_1.push_distance":0.09711,"push_1.push_force_limit":15.93791,"retract_1.retract_speed":0.03718},"optimized_scores":{"best_composite_score":-0.29226,"best_fitness_score":0.07774,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":8,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":3.0,"contact_point_centroid":[0.52501,0.11916,0.04893],"force_p95":549.3376,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":550.571,"mean_force":538.15538,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51303,0.11917,0.04877]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":1486.0,"contact_point_centroid":[0.52504,0.11565,0.05927],"force_p95":254.33506,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":383.92479,"mean_force":137.4448,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51206,0.11588,0.04664]},{"body_a":"attachment","body_b":"peg","contact_count":1959.0,"contact_point_centroid":[0.51442,0.11141,0.05067],"force_p95":223.8469,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":237.39803,"mean_force":186.16543,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.5113,0.11558,0.0476]},{"body_a":"peg","body_b":"channel_base_body","contact_count":2447.0,"contact_point_centroid":[0.51107,0.11169,0.00761],"force_p95":221.78364,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":228.43794,"mean_force":148.37836,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.5095,0.11543,0.05861]},{"body_a":"peg","body_b":"channel_base_body","contact_count":450.0,"contact_point_centroid":[0.50364,0.11125,0.00748],"force_p95":200.01164,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":207.46126,"mean_force":178.68647,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51306,0.11899,0.04819]},{"body_a":"attachment","body_b":"peg","contact_count":450.0,"contact_point_centroid":[0.5043,0.11084,0.05136],"force_p95":198.9204,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":207.02025,"mean_force":177.80568,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51306,0.11899,0.04819]},{"body_a":"attachment","body_b":"peg","contact_count":200.0,"contact_point_centroid":[0.50357,0.11462,0.05304],"force_p95":152.86128,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":185.30397,"mean_force":139.46423,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.51322,0.12166,0.05054]},{"body_a":"attachment","body_b":"peg","contact_count":3.0,"contact_point_centroid":[0.50344,0.11197,0.05183],"force_p95":183.20735,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":183.85672,"mean_force":177.07269,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51303,0.11917,0.04877]},{"body_a":"peg","body_b":"channel_base_body","contact_count":3.0,"contact_point_centroid":[0.50108,0.11067,0.00764],"force_p95":182.27073,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":182.58811,"mean_force":178.94548,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51303,0.11917,0.04877]},{"body_a":"peg","body_b":"channel_base_body","contact_count":200.0,"contact_point_centroid":[0.5029,0.11559,0.00794],"force_p95":153.33905,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":179.22125,"mean_force":139.78809,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.51322,0.12166,0.05054]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":447.0,"contact_point_centroid":[0.52503,0.11899,0.04835],"force_p95":99.58519,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":140.45833,"mean_force":79.83912,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51306,0.119,0.04819]},{"body_a":"peg","body_b":"channel_base_body","contact_count":104.0,"contact_point_centroid":[0.49165,0.1179,0.00926],"force_p95":75.36464,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":130.10966,"mean_force":20.5112,"phase_index":5.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.51217,0.12179,0.05791]},{"body_a":"attachment","body_b":"peg","contact_count":63.0,"contact_point_centroid":[0.50271,0.11549,0.05643],"force_p95":79.2627,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":129.63241,"mean_force":31.08746,"phase_index":5.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.5128,0.12195,0.05542]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":187.0,"contact_point_centroid":[0.52505,0.11999,0.05074],"force_p95":72.98191,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":110.66765,"mean_force":54.616,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.51324,0.12173,0.05062]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":918.0,"contact_point_centroid":[0.47453,0.11782,0.01273],"force_p95":25.87974,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":56.51944,"mean_force":12.62824,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51233,0.11702,0.04618]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":10.0,"contact_point_centroid":[0.52506,0.11999,0.05153],"force_p95":51.36738,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":54.85662,"mean_force":28.91014,"phase_index":5.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.5133,0.122,0.05141]}],"total_contact_groups":24},"final_pose_error":0.00993,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49474,0.17059,0.01413],"final_tcp_position":[0.50998,0.1212,0.09187],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":550.571,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":597.0,"n_steps_budget":1000.0,"object_pos_end":[0.50369,0.11173,0.03397],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.19186,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":0.53235,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":591.0,"raw_peak_contact_force":2.06328,"subtask_id":"reach_peg","tcp_end":[0.50625,0.11762,0.1469],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11312,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":2447.0,"n_steps_budget":1000.0,"object_pos_end":[0.5066,0.11215,0.02954],"object_pos_start":[0.50369,0.11173,0.03397],"object_to_goal_dist_end":0.19254,"object_to_goal_dist_start":0.19186,"object_z_max":0.03402,"peak_contact_force":215.201,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":6958.0,"raw_peak_contact_force":383.92479,"subtask_id":"reach_peg","tcp_end":[0.51308,0.11843,0.046],"tcp_start":[0.5117,0.11566,0.04416],"tcp_to_object_dist_end":0.01877,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.49195,0.12583,0.03034],"object_pos_start":[0.49268,0.12267,0.02918],"object_to_goal_dist_end":0.20621,"object_to_goal_dist_start":0.20309,"object_z_max":0.03034,"peak_contact_force":173.27293,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":1761.0,"raw_peak_contact_force":207.46126,"subtask_id":"reach_peg","tcp_end":[0.51305,0.1192,0.04879],"tcp_start":[0.51308,0.11843,0.046],"tcp_to_object_dist_end":0.0288,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":3.0,"n_steps_budget":630.0,"object_pos_end":[0.49194,0.12582,0.03034],"object_pos_start":[0.49195,0.12583,0.03034],"object_to_goal_dist_end":0.2062,"object_to_goal_dist_start":0.20621,"object_z_max":0.03035,"peak_contact_force":0.0,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":12.0,"raw_peak_contact_force":550.571,"subtask_id":"insert_peg","tcp_end":[0.51297,0.11908,0.04871],"tcp_start":[0.513,0.11913,0.04874],"tcp_to_object_dist_end":0.02873,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.49107,0.12851,0.0313],"object_pos_start":[0.49193,0.12578,0.03036],"object_to_goal_dist_end":0.20888,"object_to_goal_dist_start":0.20616,"object_z_max":0.03131,"peak_contact_force":137.06321,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":595.0,"raw_peak_contact_force":185.30397,"tcp_end":[0.51335,0.12199,0.05118],"tcp_start":[0.51297,0.11908,0.04871],"tcp_to_object_dist_end":0.03056,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":400.0,"n_steps_budget":840.0,"object_pos_end":[0.49474,0.17059,0.01413],"object_pos_start":[0.49107,0.12851,0.0313],"object_to_goal_dist_end":0.25198,"object_to_goal_dist_start":0.20888,"object_z_max":0.03429,"peak_contact_force":0.6837,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":553.0,"raw_peak_contact_force":130.10966,"tcp_end":[0.50998,0.1212,0.09187],"tcp_start":[0.51335,0.12199,0.05118],"tcp_to_object_dist_end":0.09336,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `3ca2e925d364d2c0fe81fb71ee31d40f947a20e349a0720e1c44a2dd2bc628da`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.89109,"average_solve_count":202.0,"average_success_count":202.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.06343,"descend_1.descend_speed":0.02408,"push_1.push_distance":0.08639,"push_1.push_force_limit":12.69978,"retract_1.retract_speed":0.05472},"optimized_scores":{"best_composite_score":-0.32229,"best_fitness_score":0.04771,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.53745,0.11999,0.05966],"force_p95":1383.61095,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1396.40683,"mean_force":1272.37996,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50362,0.11583,0.02258]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":192.0,"contact_point_centroid":[0.54027,0.12,0.05994],"force_p95":99.27363,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":276.02812,"mean_force":82.65894,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.50679,0.11417,0.02302]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1712.0,"contact_point_centroid":[0.50664,0.1192,0.00821],"force_p95":218.97874,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":231.46365,"mean_force":105.80194,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49979,0.12238,0.06713]},{"body_a":"attachment","body_b":"peg","contact_count":1125.0,"contact_point_centroid":[0.51342,0.11901,0.05163],"force_p95":222.94835,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":228.62637,"mean_force":160.38972,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.5071,0.12264,0.04908]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":448.0,"contact_point_centroid":[0.52502,0.11999,0.06],"force_p95":62.76377,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":131.82393,"mean_force":40.25301,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.5127,0.12399,0.04681]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":131.0,"contact_point_centroid":[0.47488,0.11992,0.0142],"force_p95":47.55211,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":81.37385,"mean_force":13.97321,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51286,0.12517,0.04421]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":4.0,"contact_point_centroid":[0.54031,0.12,0.05998],"force_p95":69.35753,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":71.92238,"mean_force":50.83578,"phase_index":5.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50686,0.11454,0.02306]},{"body_a":"peg","body_b":"world","contact_count":1.0,"contact_point_centroid":[0.44433,0.17951,-0.00042],"force_p95":4.11927,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.11927,"mean_force":4.11927,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50533,0.12199,0.03305]},{"body_a":"peg","body_b":"world","contact_count":450.0,"contact_point_centroid":[0.49291,0.23868,-0.002],"force_p95":0.73358,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.4938,"mean_force":0.63295,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49961,0.12061,0.02601]},{"body_a":"peg","body_b":"channel_base_body","contact_count":527.0,"contact_point_centroid":[0.49627,0.11915,0.00943],"force_p95":0.61228,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.55418,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49113,0.16103,0.22024]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49945,0.19881,0.29797]},{"body_a":"peg","body_b":"world","contact_count":8.0,"contact_point_centroid":[0.52278,0.3082,-0.00198],"force_p95":0.72631,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.72645,"mean_force":0.60622,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50116,0.11809,0.02365]},{"body_a":"peg","body_b":"world","contact_count":200.0,"contact_point_centroid":[0.53584,0.33936,-0.00198],"force_p95":0.72644,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.72645,"mean_force":0.60622,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.50682,0.11411,0.02304]},{"body_a":"peg","body_b":"world","contact_count":429.0,"contact_point_centroid":[0.57456,0.43239,-0.00198],"force_p95":0.72641,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.72643,"mean_force":0.60629,"phase_index":5.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50354,0.11372,0.04361]}],"total_contact_groups":14},"final_pose_error":0.00996,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.60071,0.49519,0.0141],"final_tcp_position":[0.50323,0.11365,0.06383],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":1396.40683,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":552.0,"n_steps_budget":1000.0,"object_pos_end":[0.49601,0.11914,0.03411],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.19926,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.48518,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":551.0,"raw_peak_contact_force":2.24822,"subtask_id":"reach_peg","tcp_end":[0.48428,0.12455,0.1478],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11442,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1738.0,"n_steps_budget":1000.0,"object_pos_end":[0.5027,0.12033,0.02948],"object_pos_start":[0.49601,0.11914,0.03411],"object_to_goal_dist_end":0.20062,"object_to_goal_dist_start":0.19926,"object_z_max":0.03412,"peak_contact_force":4.11927,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3417.0,"raw_peak_contact_force":231.46365,"subtask_id":"reach_peg","tcp_end":[0.50521,0.12196,0.03291],"tcp_start":[0.50546,0.12204,0.0332],"tcp_to_object_dist_end":0.00454,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.52228,0.30715,0.0141],"object_pos_start":[0.46368,0.16654,0.01749],"object_to_goal_dist_end":0.38866,"object_to_goal_dist_start":0.25022,"object_z_max":0.01749,"peak_contact_force":0.63708,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":450.0,"raw_peak_contact_force":3.4938,"subtask_id":"reach_peg","tcp_end":[0.49863,0.12037,0.0248],"tcp_start":[0.50521,0.12196,0.03291],"tcp_to_object_dist_end":0.18857,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":8.0,"n_steps_budget":600.0,"object_pos_end":[0.52311,0.30893,0.01411],"object_pos_start":[0.52228,0.30715,0.0141],"object_to_goal_dist_end":0.39047,"object_to_goal_dist_start":0.38866,"object_z_max":0.01411,"peak_contact_force":1152.28497,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":11.0,"raw_peak_contact_force":1396.40683,"subtask_id":"insert_peg","tcp_end":[0.50545,0.11378,0.02221],"tcp_start":[0.50462,0.11478,0.02229],"tcp_to_object_dist_end":0.19611,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54833,0.36935,0.0141],"object_pos_start":[0.52329,0.30956,0.0141],"object_to_goal_dist_end":0.45268,"object_to_goal_dist_start":0.39111,"object_z_max":0.01411,"peak_contact_force":71.54432,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":392.0,"raw_peak_contact_force":276.02812,"tcp_end":[0.50687,0.11455,0.02306],"tcp_start":[0.50545,0.11378,0.02221],"tcp_to_object_dist_end":0.2583,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":429.0,"n_steps_budget":600.0,"object_pos_end":[0.60071,0.49519,0.0141],"object_pos_start":[0.54833,0.36935,0.0141],"object_to_goal_dist_end":0.58451,"object_to_goal_dist_start":0.45268,"object_z_max":0.0141,"peak_contact_force":0.63743,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":433.0,"raw_peak_contact_force":71.92238,"tcp_end":[0.50323,0.11365,0.06383],"tcp_start":[0.50687,0.11455,0.02306],"tcp_to_object_dist_end":0.39692,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `f85f1938a541e3d507519c8f918b8ca98f1f9baf6ab2f6f3ba2c32478e079e47`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.10471,"average_solve_count":191.0,"average_success_count":191.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.06425,"descend_1.descend_speed":0.03842,"push_1.push_distance":0.10825,"push_1.push_force_limit":6.90468,"retract_1.retract_speed":0.06494},"optimized_scores":{"best_composite_score":-0.29672,"best_fitness_score":0.07328,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":7,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":2.0,"contact_point_centroid":[0.52508,0.06898,0.04869],"force_p95":587.35743,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":592.89944,"mean_force":537.47935,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51316,0.06899,0.04859]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":1566.0,"contact_point_centroid":[0.52505,0.06588,0.05956],"force_p95":284.02113,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":394.31828,"mean_force":159.43788,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51208,0.06604,0.04781]},{"body_a":"attachment","body_b":"peg","contact_count":1887.0,"contact_point_centroid":[0.51537,0.06328,0.05116],"force_p95":214.29622,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":225.7873,"mean_force":178.88756,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51194,0.06609,0.0482]},{"body_a":"peg","body_b":"channel_base_body","contact_count":2307.0,"contact_point_centroid":[0.51251,0.0633,0.0077],"force_p95":213.95401,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":216.79865,"mean_force":145.4817,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51255,0.06633,0.05798]},{"body_a":"peg","body_b":"channel_base_body","contact_count":3.0,"contact_point_centroid":[0.50245,0.06034,0.00761],"force_p95":215.21565,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":216.68328,"mean_force":198.24323,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51311,0.06902,0.0486]},{"body_a":"attachment","body_b":"peg","contact_count":3.0,"contact_point_centroid":[0.50447,0.06071,0.05178],"force_p95":215.45677,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":216.43124,"mean_force":184.11697,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51311,0.06902,0.0486]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":191.0,"contact_point_centroid":[0.52506,0.07131,0.04973],"force_p95":83.1265,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":207.13777,"mean_force":63.17302,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.51311,0.07131,0.04964]},{"body_a":"attachment","body_b":"peg","contact_count":450.0,"contact_point_centroid":[0.505,0.06017,0.0514],"force_p95":199.39541,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":206.00551,"mean_force":178.3481,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51306,0.06903,0.04806]},{"body_a":"peg","body_b":"channel_base_body","contact_count":450.0,"contact_point_centroid":[0.50456,0.0604,0.00751],"force_p95":200.03613,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":205.96689,"mean_force":179.24234,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51306,0.06903,0.04806]},{"body_a":"attachment","body_b":"peg","contact_count":200.0,"contact_point_centroid":[0.50456,0.06386,0.05244],"force_p95":163.38167,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":189.23602,"mean_force":151.17086,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.5131,0.07126,0.04959]},{"body_a":"peg","body_b":"channel_base_body","contact_count":200.0,"contact_point_centroid":[0.5046,0.06341,0.0077],"force_p95":162.46491,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":188.96058,"mean_force":151.9976,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.5131,0.07126,0.04959]},{"body_a":"peg","body_b":"channel_base_body","contact_count":372.0,"contact_point_centroid":[0.4939,0.07398,0.00932],"force_p95":50.18188,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":139.0617,"mean_force":6.15735,"phase_index":5.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.51034,0.07104,0.0719]},{"body_a":"attachment","body_b":"peg","contact_count":63.0,"contact_point_centroid":[0.50464,0.06243,0.05619],"force_p95":72.62294,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":138.7689,"mean_force":31.64118,"phase_index":5.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.51264,0.07135,0.05492]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":447.0,"contact_point_centroid":[0.52503,0.06903,0.04817],"force_p95":94.89653,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":115.33952,"mean_force":78.57054,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51306,0.06903,0.04807]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":2.0,"contact_point_centroid":[0.475,0.07448,0.01],"force_p95":58.45572,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":61.12983,"mean_force":34.38873,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51302,0.06911,0.04863]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":886.0,"contact_point_centroid":[0.47452,0.06895,0.01248],"force_p95":30.24318,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":50.75748,"mean_force":13.3081,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51227,0.06718,0.04636]}],"total_contact_groups":23},"final_pose_error":0.00997,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.493,0.07605,0.03378],"final_tcp_position":[0.50964,0.07094,0.09078],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.52962,0.06295,0.04]},"peak_contact_force":592.89944,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":737.0,"n_steps_budget":1000.0,"object_pos_end":[0.50602,0.06295,0.03381],"object_pos_start":[0.52962,0.06295,0.04],"object_to_goal_dist_end":0.14321,"object_to_goal_dist_start":0.14598,"object_z_max":0.04001,"peak_contact_force":0.54588,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":743.0,"raw_peak_contact_force":3.88411,"subtask_id":"reach_peg","tcp_end":[0.52476,0.07046,0.14411],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11213,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":2307.0,"n_steps_budget":1000.0,"object_pos_end":[0.50663,0.06305,0.03031],"object_pos_start":[0.50602,0.06295,0.03381],"object_to_goal_dist_end":0.14353,"object_to_goal_dist_start":0.14321,"object_z_max":0.03381,"peak_contact_force":214.6699,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":6783.0,"raw_peak_contact_force":394.31828,"subtask_id":"reach_peg","tcp_end":[0.513,0.06869,0.04594],"tcp_start":[0.51169,0.06572,0.04489],"tcp_to_object_dist_end":0.0178,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.49301,0.07446,0.03028],"object_pos_start":[0.49298,0.07256,0.02943],"object_to_goal_dist_end":0.15493,"object_to_goal_dist_start":0.15309,"object_z_max":0.03028,"peak_contact_force":171.99076,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":1714.0,"raw_peak_contact_force":206.00551,"subtask_id":"reach_peg","tcp_end":[0.51304,0.06913,0.04865],"tcp_start":[0.513,0.06869,0.04594],"tcp_to_object_dist_end":0.02769,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":3.0,"n_steps_budget":690.0,"object_pos_end":[0.493,0.07444,0.03027],"object_pos_start":[0.49301,0.07446,0.03028],"object_to_goal_dist_end":0.1549,"object_to_goal_dist_start":0.15493,"object_z_max":0.03035,"peak_contact_force":592.89944,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":10.0,"raw_peak_contact_force":592.89944,"subtask_id":"insert_peg","tcp_end":[0.51345,0.06858,0.04844],"tcp_start":[0.51328,0.06884,0.04854],"tcp_to_object_dist_end":0.02798,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.49302,0.07597,0.03094],"object_pos_start":[0.49327,0.07419,0.03041],"object_to_goal_dist_end":0.15639,"object_to_goal_dist_start":0.15463,"object_z_max":0.03096,"peak_contact_force":76.20321,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":740.0,"raw_peak_contact_force":207.13777,"tcp_end":[0.51302,0.07143,0.05015],"tcp_start":[0.51345,0.06858,0.04844],"tcp_to_object_dist_end":0.02811,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":372.0,"n_steps_budget":600.0,"object_pos_end":[0.493,0.07605,0.03378],"object_pos_start":[0.49302,0.07597,0.03094],"object_to_goal_dist_end":0.15633,"object_to_goal_dist_start":0.15639,"object_z_max":0.03436,"peak_contact_force":0.54232,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":602.0,"raw_peak_contact_force":139.0617,"tcp_end":[0.50964,0.07094,0.09078],"tcp_start":[0.51302,0.07143,0.05015],"tcp_to_object_dist_end":0.0596,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```