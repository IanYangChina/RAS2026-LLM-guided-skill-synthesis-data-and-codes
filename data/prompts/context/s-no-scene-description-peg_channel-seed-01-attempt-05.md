## Search State

- **Seed**: 1
- **Iteration**: 6 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 5 | approach → align → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 5 | -0.1614 | 0.09 | ❌ rejected |
| 4 | rotate → align → push → align | impedance_motion | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | position_control | impedance_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 3 | 0.1680 | 0.40 | ❌ rejected |
| 3 | approach → align → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 5 | -0.1615 | 0.00 | ❌ rejected |
| 2 | approach → align → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 4 | 0.1072 | 0.00 | ❌ rejected |
| 1 | rotate → align → push → align | impedance_motion | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | position_control | impedance_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 3 | 0.1706 | 0.42 | ✅ accepted |

**Proposal policy**: task_score is 0.09 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- **task_score** (E): 0.089
- **fitness_score**: 0.119  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.280

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2312 |
| align_1 | 0.67 | 1.00 | 0.0344 |
| push_1 | 0.00 | 1.00 | 0.0170 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.482, 0.088, 0.100) | (0.483, 0.080, 0.040)→(0.497, 0.080, 0.034) | 0.161→0.160 | 1.00 / 1.667 | 175.671 | 180.354 |
| align_1 | align | 0.67 / step_budget | (0.482, 0.088, 0.100)→(0.487, 0.090, 0.069) | (0.497, 0.080, 0.034)→(0.498, 0.063, 0.031) | 0.160→0.143 | 1.00 / 2.333 | 272.020 | 323.537 |
| push_1 | push | 0.00 / step_budget | (0.487, 0.090, 0.069)→(0.492, 0.087, 0.059) | (0.498, 0.063, 0.031)→(0.499, 0.059, 0.030) | 0.143→0.140 | 1.00 / 3.000 | 226.106 | 351.953 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.275
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.166
- phase_score: 0.116
- phase_breakdown.push_channel_score: 0.034
- phase_breakdown.pre_contact_score: 0.442

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.136
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.166
- **Median Q (composite search score)**: -0.152
- **K-run variance**: 0.0004
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.461


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.44203,"average_solve_count":138.0,"average_success_count":138.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.align_speed":0.02501,"align_1.lateral_offset_x":-0.00548,"approach_1.approach_speed":0.10503,"push_1.push_distance":0.15472,"push_1.push_speed":0.09105},"optimized_scores":{"best_composite_score":-0.15179,"best_fitness_score":0.12821,"best_task_score":0.09942},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":153.0,"contact_point_centroid":[0.49599,0.29542,-4e-05],"force_p95":308.63349,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":323.07302,"mean_force":223.41363,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49088,0.10745,0.06777]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":864.0,"contact_point_centroid":[0.46147,0.1199,0.05951],"force_p95":246.23017,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":294.54483,"mean_force":213.54119,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49538,0.08379,0.06671]},{"body_a":"world","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.49656,0.29563,-4e-05],"force_p95":159.68046,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":159.68046,"mean_force":159.68046,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49103,0.10792,0.06848]},{"body_a":"peg","body_b":"channel_base_body","contact_count":826.0,"contact_point_centroid":[0.49621,0.11922,0.00805],"force_p95":125.71077,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":129.90022,"mean_force":84.2815,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49469,0.11321,0.06776]},{"body_a":"attachment","body_b":"peg","contact_count":676.0,"contact_point_centroid":[0.495,0.12393,0.05309],"force_p95":125.45006,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":129.26073,"mean_force":102.32657,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49446,0.11212,0.06401]},{"body_a":"attachment","body_b":"peg","contact_count":1000.0,"contact_point_centroid":[0.495,0.08838,0.05617],"force_p95":92.6826,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":103.39708,"mean_force":72.37525,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49481,0.08511,0.06684]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.49694,0.0876,0.0088],"force_p95":92.03565,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":98.52677,"mean_force":72.30697,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49481,0.08511,0.06684]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":887.0,"contact_point_centroid":[0.52519,0.09488,0.01568],"force_p95":10.22876,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":19.23824,"mean_force":3.90807,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49529,0.08375,0.06672]},{"body_a":"peg","body_b":"channel_base_body","contact_count":680.0,"contact_point_centroid":[0.50095,0.11599,0.00939],"force_p95":0.61516,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.92055,"mean_force":0.55495,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4954,0.16615,0.1963]}],"total_contact_groups":9},"final_pose_error":0.32415,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50747,0.09887,0.0323],"final_tcp_position":[0.49943,0.08885,0.06642],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50095,0.11604,0.04]},"peak_contact_force":323.07302,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":696.0,"n_steps_budget":1000.0,"object_pos_end":[0.50092,0.1162,0.03383],"object_pos_start":[0.50095,0.11604,0.04],"object_to_goal_dist_end":0.1963,"object_to_goal_dist_start":0.19604,"object_z_max":0.04,"peak_contact_force":0.58031,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":680.0,"raw_peak_contact_force":1.92055,"subtask_id":"pre_contact","tcp_end":[0.49818,0.11996,0.09871],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.06505,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":826.0,"n_steps_budget":1000.0,"object_pos_end":[0.5049,0.10902,0.0337],"object_pos_start":[0.50092,0.1162,0.03383],"object_to_goal_dist_end":0.18919,"object_to_goal_dist_start":0.1963,"object_z_max":0.03393,"peak_contact_force":296.9874,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":1655.0,"raw_peak_contact_force":323.07302,"subtask_id":"pre_contact","tcp_end":[0.49103,0.10792,0.06848],"tcp_start":[0.49818,0.11996,0.09871],"tcp_to_object_dist_end":0.03746,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50747,0.09887,0.0323],"object_pos_start":[0.5049,0.10902,0.0337],"object_to_goal_dist_end":0.17919,"object_to_goal_dist_start":0.18919,"object_z_max":0.03385,"peak_contact_force":205.60756,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3752.0,"raw_peak_contact_force":294.54483,"subtask_id":"push_channel","tcp_end":[0.49943,0.08885,0.06642],"tcp_start":[0.49103,0.10792,0.06848],"tcp_to_object_dist_end":0.03646,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `8416ac3bebb4dbec2abbf751596843a33db171fd8d70765023f3b940d846bd0c`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.10526,"average_solve_count":95.0,"average_success_count":95.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.align_speed":0.0603,"align_1.lateral_offset_x":-0.00133,"approach_1.approach_speed":0.15418,"push_1.push_distance":0.24491,"push_1.push_speed":0.07653},"optimized_scores":{"best_composite_score":-0.1441,"best_fitness_score":0.1359,"best_task_score":0.16634},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_right_wall","body_b":"link7","contact_count":987.0,"contact_point_centroid":[0.46109,0.11994,0.05898],"force_p95":228.21483,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":413.27919,"mean_force":211.42697,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49415,0.08438,0.04816]},{"body_a":"world","body_b":"link7","contact_count":123.0,"contact_point_centroid":[0.49454,0.14323,-0.00013],"force_p95":383.35678,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":393.44379,"mean_force":353.61492,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49273,0.0811,0.0539]},{"body_a":"world","body_b":"link7","contact_count":17.0,"contact_point_centroid":[0.49502,0.14181,-3e-05],"force_p95":323.89977,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":328.35785,"mean_force":196.71412,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49267,0.08062,0.05515]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":493.0,"contact_point_centroid":[0.46643,0.11996,0.05999],"force_p95":199.85871,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":237.32107,"mean_force":156.72965,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.48757,0.07882,0.07661]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":20.0,"contact_point_centroid":[0.47495,0.11965,0.05974],"force_p95":233.63243,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":233.70688,"mean_force":206.45838,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48007,0.07216,0.09929]},{"body_a":"attachment","body_b":"peg","contact_count":40.0,"contact_point_centroid":[0.4897,0.08037,0.05827],"force_p95":78.23,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":89.93533,"mean_force":41.69361,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.4888,0.08011,0.06947]},{"body_a":"peg","body_b":"channel_base_body","contact_count":643.0,"contact_point_centroid":[0.49534,0.04985,0.00908],"force_p95":19.09674,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":89.86166,"mean_force":3.15193,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.48833,0.07919,0.0734]},{"body_a":"peg","body_b":"channel_base_body","contact_count":683.0,"contact_point_centroid":[0.49534,0.06379,0.00938],"force_p95":0.56622,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44546,"mean_force":0.55801,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48574,0.13798,0.18857]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":28.0,"contact_point_centroid":[0.47133,0.06388,0.03676],"force_p95":0.92436,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.16907,"mean_force":0.37063,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50391,0.21522,0.29278]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.49496,0.01989,0.00804],"force_p95":0.72551,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.94138,"mean_force":0.60557,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49413,0.08434,0.04825]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":2.0,"contact_point_centroid":[0.475,0.04461,0.02416],"force_p95":0.38451,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.38532,"mean_force":0.37718,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49409,0.08335,0.04928]}],"total_contact_groups":11},"final_pose_error":0.41261,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49597,0.0199,0.0241],"final_tcp_position":[0.49513,0.08909,0.04243],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"peak_contact_force":413.27919,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":710.0,"n_steps_budget":1000.0,"object_pos_end":[0.49534,0.06387,0.03397],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.14407,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"peak_contact_force":231.68785,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":731.0,"raw_peak_contact_force":233.70688,"subtask_id":"pre_contact","tcp_end":[0.48075,0.07279,0.09872],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.06697,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":656.0,"n_steps_budget":720.0,"object_pos_end":[0.49596,0.01996,0.02414],"object_pos_start":[0.49534,0.06387,0.03397],"object_to_goal_dist_end":0.10129,"object_to_goal_dist_start":0.14407,"object_z_max":0.0408,"peak_contact_force":371.2383,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":1299.0,"raw_peak_contact_force":393.44379,"subtask_id":"pre_contact","tcp_end":[0.49273,0.08207,0.05545],"tcp_start":[0.48075,0.07279,0.09872],"tcp_to_object_dist_end":0.06963,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49597,0.0199,0.0241],"object_pos_start":[0.49596,0.01996,0.02414],"object_to_goal_dist_end":0.10124,"object_to_goal_dist_start":0.10129,"object_z_max":0.02446,"peak_contact_force":226.34403,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2006.0,"raw_peak_contact_force":413.27919,"subtask_id":"push_channel","tcp_end":[0.49513,0.08909,0.04243],"tcp_start":[0.49273,0.08207,0.05545],"tcp_to_object_dist_end":0.07159,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `0188121de1b8142d5ff7a7406b62c43adf6da5520b986a997e46ef53b7d11bf9`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.47748,"average_solve_count":111.0,"average_success_count":111.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.align_speed":0.01001,"align_1.lateral_offset_x":-0.00755,"approach_1.approach_speed":0.17895,"push_1.push_distance":0.26399,"push_1.push_speed":0.05081},"optimized_scores":{"best_composite_score":-0.18843,"best_fitness_score":0.09157,"best_task_score":0.00059},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_right_wall","body_b":"link7","contact_count":999.0,"contact_point_centroid":[0.45254,0.11995,0.05999],"force_p95":275.5578,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":348.03397,"mean_force":228.18633,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47927,0.0809,0.07595]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":28.0,"contact_point_centroid":[0.46458,0.11961,0.05972],"force_p95":305.32666,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":305.43323,"mean_force":288.02401,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.46756,0.06988,0.10282]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":971.0,"contact_point_centroid":[0.46655,0.11995,0.05997],"force_p95":239.21988,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":254.09319,"mean_force":172.27609,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.47257,0.07703,0.09291]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":150.0,"contact_point_centroid":[0.47498,0.08357,0.05996],"force_p95":193.02478,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":202.13502,"mean_force":141.73758,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48189,0.08287,0.0697]},{"body_a":"peg","body_b":"channel_base_body","contact_count":657.0,"contact_point_centroid":[0.49431,0.05889,0.00936],"force_p95":0.56089,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.20518,"mean_force":0.56846,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.47863,0.13446,0.18664]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46807,0.05895,0.03796],"force_p95":1.19991,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.42382,"mean_force":0.50385,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50214,0.22036,0.287]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.49413,0.05893,0.0094],"force_p95":0.55049,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55392,"mean_force":0.5456,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.47255,0.07699,0.09296]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.49406,0.05901,0.00941],"force_p95":0.55051,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55316,"mean_force":0.54505,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47926,0.0809,0.07596]}],"total_contact_groups":8},"final_pose_error":0.42836,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49422,0.05865,0.03405],"final_tcp_position":[0.4827,0.08354,0.06916],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.46685,0.05894,0.04]},"peak_contact_force":348.03397,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":686.0,"n_steps_budget":900.0,"object_pos_end":[0.49426,0.05895,0.03389],"object_pos_start":[0.46685,0.05894,0.04],"object_to_goal_dist_end":0.1392,"object_to_goal_dist_start":0.14284,"object_z_max":0.04001,"peak_contact_force":294.74362,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":720.0,"raw_peak_contact_force":305.43323,"subtask_id":"pre_contact","tcp_end":[0.46782,0.07058,0.10293],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.07484,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49442,0.05896,0.03403],"object_pos_start":[0.49426,0.05895,0.03389],"object_to_goal_dist_end":0.1392,"object_to_goal_dist_start":0.1392,"object_z_max":0.03403,"peak_contact_force":147.83295,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":1971.0,"raw_peak_contact_force":254.09319,"subtask_id":"pre_contact","tcp_end":[0.47588,0.07965,0.08204],"tcp_start":[0.46782,0.07058,0.10293],"tcp_to_object_dist_end":0.05547,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49422,0.05865,0.03405],"object_pos_start":[0.49442,0.05896,0.03403],"object_to_goal_dist_end":0.1389,"object_to_goal_dist_start":0.1392,"object_z_max":0.03405,"peak_contact_force":246.36775,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2149.0,"raw_peak_contact_force":348.03397,"subtask_id":"push_channel","tcp_end":[0.4827,0.08354,0.06916],"tcp_start":[0.47588,0.07965,0.08204],"tcp_to_object_dist_end":0.04455,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```