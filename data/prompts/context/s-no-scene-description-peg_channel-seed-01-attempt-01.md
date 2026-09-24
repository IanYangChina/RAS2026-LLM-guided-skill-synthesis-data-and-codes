## Search State

- **Seed**: 1
- **Iteration**: 2 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 1 | rotate → align → push → align | impedance_motion | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | position_control | impedance_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 3 | 0.1706 | 0.42 | ✅ accepted |
| 0 | rotate → align → push → align | impedance_motion | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | position_control | impedance_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 3 | 0.1472 | 0.30 | ✅ accepted |

**Proposal policy**: task_score is 0.42 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.171) — your mutation base

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

- **Composite score**: 0.171
- **task_score** (E): 0.418
- **fitness_score**: 0.381  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.210

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| rotate_1 | 1.00 | 1.00 | 0.1730 |
| align_1 | 1.00 | 1.00 | 0.1462 |
| push_1 | 0.33 | 1.00 | 0.1270 |
| align_2 | 1.00 | 1.00 | 0.0070 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| rotate_1 | rotate | 1.00 / time_limit | (0.500, 0.200, 0.300)→(0.497, 0.075, 0.180) | (0.483, 0.080, 0.040)→(0.497, 0.080, 0.034) | 0.161→0.160 | 1.00 / 1.000 | 0.560 | 2.857 |
| align_1 | align | 1.00 / step_budget | (0.497, 0.075, 0.180)→(0.494, 0.118, 0.043) | (0.497, 0.080, 0.034)→(0.497, 0.084, 0.033) | 0.160→0.164 | 1.00 / 1.667 | 34.709 | 43.847 |
| push_1 | push | 0.33 / step_budget | (0.494, 0.118, 0.043)→(0.496, -0.009, 0.039) | (0.497, 0.084, 0.033)→(0.506, -0.024, 0.024) | 0.164→0.068 | 1.00 / 2.667 | 51.094 | 212.914 |
| align_2 | align | 1.00 / step_budget | (0.496, -0.009, 0.039)→(0.500, -0.005, 0.039) | (0.506, -0.024, 0.024)→(0.495, -0.026, 0.028) | 0.068→0.062 | 1.00 / 4.000 | 1431.968 | 307.950 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.868
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.633
- phase_score: 0.448
- phase_breakdown.approach_score: 0.036
- phase_breakdown.push_score: 0.735
- phase_breakdown.contact_score: 0.000

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.522
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.633
- **Median Q (composite search score)**: 0.221
- **K-run variance**: 0.0197
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 10.0
- **Final σ (mean)**: 0.447


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.25,"average_solve_count":112.0,"average_success_count":112.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":0.00481,"align_2.lateral_offset_x":-0.00289,"push_1.push_distance":0.02294},"optimized_scores":{"best_composite_score":-0.02071,"best_fitness_score":0.18929,"best_task_score":0.32613},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":430.0,"contact_point_centroid":[0.50813,0.11607,0.00741],"force_p95":194.33533,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":195.791,"mean_force":133.35057,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50317,0.14301,0.04702]},{"body_a":"attachment","body_b":"peg","contact_count":411.0,"contact_point_centroid":[0.50972,0.13595,0.04678],"force_p95":193.9225,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":195.37153,"mean_force":143.95586,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50307,0.14412,0.04705]},{"body_a":"attachment","body_b":"peg","contact_count":109.0,"contact_point_centroid":[0.50657,0.13982,0.05102],"force_p95":119.53343,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":130.43451,"mean_force":83.80714,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49846,0.14657,0.05326]},{"body_a":"peg","body_b":"channel_base_body","contact_count":563.0,"contact_point_centroid":[0.50214,0.1166,0.00925],"force_p95":94.17839,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":117.99062,"mean_force":15.43742,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49609,0.11288,0.10781]},{"body_a":"peg","body_b":"world","contact_count":173.0,"contact_point_centroid":[0.50199,0.12513,-0.00017],"force_p95":20.0452,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":48.74864,"mean_force":14.06837,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50046,0.15431,0.04476]},{"body_a":"peg","body_b":"world","contact_count":28.0,"contact_point_centroid":[0.50222,0.12719,-0.0003],"force_p95":37.33342,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":39.90411,"mean_force":28.00895,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49992,0.15488,0.04587]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":8.0,"contact_point_centroid":[0.47452,0.086,0.0568],"force_p95":2.87743,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.08939,"mean_force":1.50684,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50637,0.12011,0.04784]},{"body_a":"peg","body_b":"channel_base_body","contact_count":984.0,"contact_point_centroid":[0.50098,0.11602,0.0094],"force_p95":0.60736,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.92055,"mean_force":0.55146,"phase_index":0.0,"phase_name":"rotate_1","phase_type":"rotate","tcp_position_centroid":[0.49749,0.13563,0.23636]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":7.0,"contact_point_centroid":[0.52518,0.05145,0.04909],"force_p95":1.80284,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.90201,"mean_force":1.13968,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.50103,0.11404,0.04121]},{"body_a":"peg","body_b":"channel_base_body","contact_count":18.0,"contact_point_centroid":[0.49927,0.08052,0.00989],"force_p95":0.91956,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.01643,"mean_force":0.57487,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.50094,0.11406,0.04109]}],"total_contact_groups":10},"final_pose_error":0.00126,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50088,0.06386,0.03599],"final_tcp_position":[0.50016,0.11375,0.03995],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50095,0.11604,0.04]},"peak_contact_force":195.791,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50092,0.11601,0.03383],"object_pos_start":[0.50095,0.11604,0.04],"object_to_goal_dist_end":0.19611,"object_to_goal_dist_start":0.19604,"object_z_max":0.04,"peak_contact_force":0.58045,"phase_name":"rotate_1","phase_peak_obstacle_force":0.0,"phase_type":"rotate","raw_contact_event_count":984.0,"raw_peak_contact_force":1.92055,"tcp_end":[0.49696,0.07528,0.18003],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.15182,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":563.0,"n_steps_budget":1000.0,"object_pos_end":[0.50228,0.12805,0.02979],"object_pos_start":[0.50092,0.11601,0.03383],"object_to_goal_dist_end":0.20832,"object_to_goal_dist_start":0.19611,"object_z_max":0.0342,"peak_contact_force":103.03901,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":700.0,"raw_peak_contact_force":130.43451,"tcp_end":[0.50029,0.1577,0.04359],"tcp_start":[0.49696,0.07528,0.18003],"tcp_to_object_dist_end":0.03276,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":443.0,"n_steps_budget":600.0,"object_pos_end":[0.50123,0.07322,0.03957],"object_pos_start":[0.50228,0.12805,0.02979],"object_to_goal_dist_end":0.15323,"object_to_goal_dist_start":0.20832,"object_z_max":0.04125,"peak_contact_force":0.86996,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1022.0,"raw_peak_contact_force":195.791,"tcp_end":[0.50163,0.11464,0.04204],"tcp_start":[0.50029,0.1577,0.04359],"tcp_to_object_dist_end":0.04149,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":20.0,"n_steps_budget":600.0,"object_pos_end":[0.50088,0.06386,0.03599],"object_pos_start":[0.50123,0.07322,0.03957],"object_to_goal_dist_end":0.14391,"object_to_goal_dist_start":0.15323,"object_z_max":0.03957,"peak_contact_force":0.83802,"phase_name":"align_2","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":25.0,"raw_peak_contact_force":1.90201,"tcp_end":[0.50016,0.11375,0.03995],"tcp_start":[0.50163,0.11464,0.04204],"tcp_to_object_dist_end":0.05006,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `8416ac3bebb4dbec2abbf751596843a33db171fd8d70765023f3b940d846bd0c`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.75397,"average_solve_count":126.0,"average_success_count":126.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":0.00717,"align_2.lateral_offset_x":-0.00668,"push_1.push_distance":0.19992},"optimized_scores":{"best_composite_score":0.31181,"best_fitness_score":0.52181,"best_task_score":0.63281},"replay_outcomes":[{"contacts":{"omitted_contact_groups":3,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":229.0,"contact_point_centroid":[0.5251,-0.06251,0.05995],"force_p95":526.46155,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":589.31535,"mean_force":249.49904,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.5004,-0.06223,0.03815]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":381.0,"contact_point_centroid":[0.54424,-0.05984,0.05995],"force_p95":386.98282,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":470.42573,"mean_force":248.49592,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.49886,-0.06318,0.03795]},{"body_a":"channel_base_body","body_b":"link7","contact_count":190.0,"contact_point_centroid":[0.53819,-0.1,0.06498],"force_p95":270.73528,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":295.41197,"mean_force":168.18617,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.49516,-0.06543,0.03771]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":334.0,"contact_point_centroid":[0.53464,-0.01375,0.05999],"force_p95":164.53658,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":226.06596,"mean_force":100.95418,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4893,-0.00929,0.03818]},{"body_a":"attachment","body_b":"peg","contact_count":429.0,"contact_point_centroid":[0.50212,-0.07153,0.03665],"force_p95":151.37493,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":165.51899,"mean_force":66.96239,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.49808,-0.06367,0.03794]},{"body_a":"peg","body_b":"channel_base_body","contact_count":455.0,"contact_point_centroid":[0.49773,-0.07266,0.00622],"force_p95":140.65225,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":154.80744,"mean_force":57.35152,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.49798,-0.06373,0.03793]},{"body_a":"attachment","body_b":"peg","contact_count":922.0,"contact_point_centroid":[0.49762,0.00632,0.03584],"force_p95":121.12916,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":137.94502,"mean_force":70.21664,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48929,0.01181,0.03808]},{"body_a":"peg","body_b":"channel_base_body","contact_count":971.0,"contact_point_centroid":[0.50848,-0.0067,0.00927],"force_p95":91.38564,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":119.60626,"mean_force":42.43435,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48929,0.01601,0.03819]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":838.0,"contact_point_centroid":[0.52621,-0.00762,0.027],"force_p95":96.81748,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":106.62139,"mean_force":59.13423,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48937,0.00534,0.03807]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":112.0,"contact_point_centroid":[0.52556,-0.07101,0.01728],"force_p95":67.71959,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":101.12608,"mean_force":41.99602,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.49416,-0.06605,0.03767]},{"body_a":"channel_base_body","body_b":"link7","contact_count":4.0,"contact_point_centroid":[0.53487,-0.1,0.06499],"force_p95":93.47082,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":95.35319,"mean_force":73.93136,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49182,-0.06612,0.03783]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":272.0,"contact_point_centroid":[0.47466,-0.0606,0.02323],"force_p95":33.30114,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":50.48508,"mean_force":23.08176,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.5,-0.06251,0.03808]},{"body_a":"peg","body_b":"world","contact_count":31.0,"contact_point_centroid":[0.51037,-0.06854,-0.00051],"force_p95":15.73937,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":30.49101,"mean_force":1.99902,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49095,-0.06246,0.03793]},{"body_a":"peg","body_b":"link7","contact_count":369.0,"contact_point_centroid":[0.52003,0.00919,0.06779],"force_p95":24.87257,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":29.93994,"mean_force":12.26204,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48936,0.03407,0.03791]},{"body_a":"peg","body_b":"channel_base_body","contact_count":97.0,"contact_point_centroid":[0.48428,-0.10004,0.01856],"force_p95":14.48772,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":19.89707,"mean_force":6.78938,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.49871,-0.06323,0.03806]},{"body_a":"peg","body_b":"world","contact_count":178.0,"contact_point_centroid":[0.50574,-0.06605,-0.00082],"force_p95":9.87639,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":16.82378,"mean_force":1.42291,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.49492,-0.06557,0.0377]}],"total_contact_groups":19},"final_pose_error":0.03758,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49224,-0.07495,0.02452],"final_tcp_position":[0.50001,-0.06184,0.03921],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"peak_contact_force":4071.80599,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49482,0.06382,0.03401],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.14404,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"peak_contact_force":0.55002,"phase_name":"rotate_1","phase_peak_obstacle_force":0.0,"phase_type":"rotate","raw_contact_event_count":1001.0,"raw_peak_contact_force":2.44546,"tcp_end":[0.49696,0.07528,0.18003],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.14649,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":447.0,"n_steps_budget":930.0,"object_pos_end":[0.49519,0.06359,0.03403],"object_pos_start":[0.49482,0.06382,0.03401],"object_to_goal_dist_end":0.14379,"object_to_goal_dist_start":0.14404,"object_z_max":0.03403,"peak_contact_force":0.54085,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":447.0,"raw_peak_contact_force":0.55403,"tcp_end":[0.4911,0.10042,0.04259],"tcp_start":[0.49696,0.07528,0.18003],"tcp_to_object_dist_end":0.03803,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50954,-0.07373,0.01617],"object_pos_start":[0.49519,0.06359,0.03403],"object_to_goal_dist_end":0.02643,"object_to_goal_dist_start":0.14379,"object_z_max":0.03987,"peak_contact_force":71.02636,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3469.0,"raw_peak_contact_force":226.06596,"tcp_end":[0.49215,-0.06688,0.03791],"tcp_start":[0.4911,0.10042,0.04259],"tcp_to_object_dist_end":0.02867,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":455.0,"n_steps_budget":600.0,"object_pos_end":[0.49224,-0.07495,0.02452],"object_pos_start":[0.50954,-0.07373,0.01617],"object_to_goal_dist_end":0.01803,"object_to_goal_dist_start":0.02643,"object_z_max":0.02451,"peak_contact_force":4071.80599,"phase_name":"align_2","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":2343.0,"raw_peak_contact_force":589.31535,"tcp_end":[0.50001,-0.06184,0.03921],"tcp_start":[0.49215,-0.06688,0.03791],"tcp_to_object_dist_end":0.02116,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `0188121de1b8142d5ff7a7406b62c43adf6da5520b986a997e46ef53b7d11bf9`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.75397,"average_solve_count":126.0,"average_success_count":126.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":0.00573,"align_2.lateral_offset_x":-0.0024,"push_1.push_distance":0.19495},"optimized_scores":{"best_composite_score":0.2208,"best_fitness_score":0.4308,"best_task_score":0.29643},"replay_outcomes":[{"contacts":{"omitted_contact_groups":2,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":352.0,"contact_point_centroid":[0.52506,-0.06797,0.05997],"force_p95":274.11829,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":332.63337,"mean_force":217.42425,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.5008,-0.06782,0.03738]},{"body_a":"channel_base_body","body_b":"link7","contact_count":437.0,"contact_point_centroid":[0.54316,-0.10001,0.06495],"force_p95":277.94049,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":285.85238,"mean_force":209.23931,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.5004,-0.06846,0.0374]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":318.0,"contact_point_centroid":[0.53437,-0.00837,0.05999],"force_p95":161.48107,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":216.88418,"mean_force":96.97813,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48903,-0.00386,0.03816]},{"body_a":"peg","body_b":"channel_base_body","contact_count":965.0,"contact_point_centroid":[0.50747,-0.01043,0.00889],"force_p95":93.91088,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":136.89659,"mean_force":42.0519,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48928,0.01049,0.0382]},{"body_a":"attachment","body_b":"peg","contact_count":441.0,"contact_point_centroid":[0.50217,-0.07056,0.03701],"force_p95":101.34923,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":134.80976,"mean_force":51.86716,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.50022,-0.0687,0.03744]},{"body_a":"attachment","body_b":"peg","contact_count":873.0,"contact_point_centroid":[0.49778,-0.00099,0.03506],"force_p95":119.50487,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":133.07062,"mean_force":71.20228,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48937,0.00381,0.0381]},{"body_a":"peg","body_b":"channel_base_body","contact_count":465.0,"contact_point_centroid":[0.49575,-0.06914,0.00634],"force_p95":101.20471,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":126.61787,"mean_force":50.71641,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.50024,-0.06868,0.03743]},{"body_a":"channel_base_body","body_b":"link7","contact_count":5.0,"contact_point_centroid":[0.53726,-0.1,0.06499],"force_p95":118.96009,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":125.13329,"mean_force":77.53978,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49445,-0.07291,0.0383]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":847.0,"contact_point_centroid":[0.52611,-0.00969,0.02369],"force_p95":96.69263,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":105.20028,"mean_force":55.67135,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48941,0.00105,0.03807]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":15.0,"contact_point_centroid":[0.54584,-0.06389,0.06],"force_p95":55.27288,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":57.45925,"mean_force":51.75782,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.50034,-0.06719,0.03828]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":315.0,"contact_point_centroid":[0.47429,-0.08046,0.0226],"force_p95":40.49317,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":43.30609,"mean_force":25.62038,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.50074,-0.06775,0.03746]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":21.0,"contact_point_centroid":[0.52502,-0.04739,0.01627],"force_p95":41.54399,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":42.60908,"mean_force":28.41554,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.49649,-0.07361,0.03817]},{"body_a":"peg","body_b":"world","contact_count":94.0,"contact_point_centroid":[0.50882,-0.06794,-0.00068],"force_p95":18.59755,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":22.891,"mean_force":1.8302,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49261,-0.06513,0.03793]},{"body_a":"peg","body_b":"link7","contact_count":181.0,"contact_point_centroid":[0.5169,0.00747,0.06919],"force_p95":9.81502,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":20.20971,"mean_force":6.79674,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48898,0.03442,0.03796]},{"body_a":"peg","body_b":"world","contact_count":110.0,"contact_point_centroid":[0.50583,-0.07158,-0.00103],"force_p95":7.36136,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.42969,"mean_force":1.02235,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.49845,-0.07145,0.03758]},{"body_a":"peg","body_b":"channel_base_body","contact_count":971.0,"contact_point_centroid":[0.49432,0.05896,0.00937],"force_p95":0.55417,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.20518,"mean_force":0.56118,"phase_index":0.0,"phase_name":"rotate_1","phase_type":"rotate","tcp_position_centroid":[0.49747,0.13481,0.23556]}],"total_contact_groups":18},"final_pose_error":0.04126,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49151,-0.06776,0.02264],"final_tcp_position":[0.50035,-0.06717,0.03834],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.46685,0.05894,0.04]},"peak_contact_force":332.63337,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49409,0.05914,0.03393],"object_pos_start":[0.46685,0.05894,0.04],"object_to_goal_dist_end":0.1394,"object_to_goal_dist_start":0.14284,"object_z_max":0.04001,"peak_contact_force":0.54973,"phase_name":"rotate_1","phase_peak_obstacle_force":0.0,"phase_type":"rotate","raw_contact_event_count":1006.0,"raw_peak_contact_force":4.20518,"tcp_end":[0.49696,0.07528,0.18003],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.14702,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":443.0,"n_steps_budget":930.0,"object_pos_end":[0.49439,0.05889,0.034],"object_pos_start":[0.49409,0.05914,0.03393],"object_to_goal_dist_end":0.13914,"object_to_goal_dist_start":0.1394,"object_z_max":0.034,"peak_contact_force":0.54579,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":443.0,"raw_peak_contact_force":0.55295,"tcp_end":[0.49044,0.0962,0.04256],"tcp_start":[0.49696,0.07528,0.18003],"tcp_to_object_dist_end":0.03848,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50692,-0.07259,0.0168],"object_pos_start":[0.49439,0.05889,0.034],"object_to_goal_dist_end":0.02531,"object_to_goal_dist_start":0.13914,"object_z_max":0.04011,"peak_contact_force":81.38699,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3283.0,"raw_peak_contact_force":216.88418,"tcp_end":[0.49496,-0.07428,0.03851],"tcp_start":[0.49044,0.0962,0.04256],"tcp_to_object_dist_end":0.02484,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":6.0,"n_steps":465.0,"n_steps_budget":600.0,"object_pos_end":[0.49151,-0.06776,0.02264],"object_pos_start":[0.50692,-0.07259,0.0168],"object_to_goal_dist_end":0.02287,"object_to_goal_dist_start":0.02531,"object_z_max":0.02384,"peak_contact_force":223.25966,"phase_name":"align_2","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":2156.0,"raw_peak_contact_force":332.63337,"tcp_end":[0.50035,-0.06717,0.03834],"tcp_start":[0.49496,-0.07428,0.03851],"tcp_to_object_dist_end":0.01803,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```