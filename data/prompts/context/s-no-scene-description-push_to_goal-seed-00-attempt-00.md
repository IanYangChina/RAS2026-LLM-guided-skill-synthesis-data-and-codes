## Search State

- **Seed**: 0
- **Iteration**: 1 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 0 | insert → approach → push → retract → lift → insert | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | linear_cartesian | impedance_motion | impedance_control | force_threshold_switch | impedance_control | position_control | position_control | admittance_control | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | 5 | 0.2321 | 0.79 | ✅ accepted |

**Proposal policy**: task_score is 0.79 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

- Task name: push_to_goal
- Goal tolerance: 0.02 m
- Expressivity sigma: 1.0 m
- Expressivity threshold: 0.8
- Force limit: 25.0 N
- Primary evaluation target: **object displacement ratio toward goal_object_position**

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
| `fixture` | offset from fixture pose | targets near fixture |

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

## Current Skill (Q=0.232) — your mutation base

```yaml
skill: push_to_goal
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

- **Composite score**: 0.232
- **task_score** (E): 0.795
- **fitness_score**: 0.602  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.370

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| insert_1 | 0.00 | 1.00 | 0.1849 |
| approach_1 | 1.00 | 1.00 | 0.1925 |
| push_1 | 0.33 | 1.00 | 0.1675 |
| retract_1 | 0.00 | 1.00 | 0.1213 |
| lift_1 | 0.00 | 1.00 | 0.1592 |
| insert_2 | 0.00 | 1.00 | 0.1663 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| insert_1 | insert | 0.00 / step_budget | (0.500, -0.000, 0.301)→(0.497, -0.086, 0.137) | (0.496, 0.001, 0.025)→(0.496, 0.001, 0.025) | 0.152→0.152 | 1.00 / 4.000 | 0.245 | 0.245 |
| approach_1 | approach | 1.00 / step_budget | (0.497, -0.086, 0.137)→(0.494, 0.071, 0.030) | (0.496, 0.001, 0.025)→(0.497, 0.010, 0.028) | 0.152→0.161 | 1.00 / 4.000 | 13.603 | 60.704 |
| push_1 | push | 0.33 / step_budget | (0.494, 0.071, 0.030)→(0.496, -0.096, 0.023) | (0.497, 0.010, 0.028)→(0.494, -0.134, 0.029) | 0.161→0.034 | 1.00 / 4.333 | 28.096 | 58.968 |
| retract_1 | retract | 0.00 / step_budget | (0.496, -0.096, 0.023)→(0.494, -0.001, 0.098) | (0.494, -0.134, 0.029)→(0.494, -0.129, 0.025) | 0.034→0.037 | 1.00 / 4.000 | 0.245 | 23.032 |
| lift_1 | lift | 0.00 / step_budget | (0.494, -0.001, 0.098)→(0.420, -0.073, 0.219) | (0.494, -0.129, 0.025)→(0.494, -0.129, 0.025) | 0.037→0.037 | 1.00 / 4.000 | 0.245 | 0.245 |
| insert_2 | insert | 0.00 / step_budget | (0.420, -0.073, 0.219)→(0.475, -0.128, 0.073) | (0.494, -0.129, 0.025)→(0.494, -0.129, 0.025) | 0.037→0.037 | 1.00 / 4.000 | 0.245 | 0.245 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 1.000
- lateral_force_integral: None
- approach_alignment: 0.758
- goal_progress: 0.900
- terminal_score: 0.900
- phase_score: 0.637
- phase_breakdown.approach_score: 0.820
- phase_breakdown.push_score: 0.947
- phase_breakdown.contact_score: 0.000

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.743
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.904
- **Median Q (composite search score)**: 0.319
- **K-run variance**: 0.0264
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.490


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `1efc9b29f7d131941a1bd842274a029ca5b2a2ff6a8656033ab118e32e2fae7d`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.06,0.06]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `6150c547b3cd2920ed4582689733d59ef61d18dc295ccd2a0d2317d1cf4e7764`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.71967,"average_solve_count":239.0,"average_success_count":239.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"lift_1.speed":0.09917,"push_1.push_distance":0.14276,"push_1.push_speed":0.09812,"retract_1.retract_height":0.051,"retract_1.speed":0.04017},"optimized_scores":{"best_composite_score":0.37266,"best_fitness_score":0.74266,"best_task_score":0.9005},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":1926.0,"contact_point_centroid":[0.52019,-0.08385,-0.00011],"force_p95":45.19043,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":71.29552,"mean_force":17.24596,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50488,-0.03066,0.02262]},{"body_a":"attachment","body_b":"push_box","contact_count":773.0,"contact_point_centroid":[0.51987,-0.0734,0.04863],"force_p95":55.73435,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":68.88324,"mean_force":30.19368,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50364,-0.06279,0.02269]},{"body_a":"push_box","body_b":"link7","contact_count":745.0,"contact_point_centroid":[0.53144,-0.0828,0.05453],"force_p95":46.21473,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":54.77563,"mean_force":28.29657,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50371,-0.0632,0.02277]},{"body_a":"push_box","body_b":"link7","contact_count":10.0,"contact_point_centroid":[0.52696,-0.14925,0.05515],"force_p95":33.78356,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":34.84993,"mean_force":16.45571,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50088,-0.1253,0.02254]},{"body_a":"attachment","body_b":"push_box","contact_count":39.0,"contact_point_centroid":[0.51807,-0.13343,0.05326],"force_p95":24.4594,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":26.82608,"mean_force":3.97336,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49959,-0.12266,0.02362]},{"body_a":"world","body_b":"push_box","contact_count":3849.0,"contact_point_centroid":[0.50497,-0.16178,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":14.83041,"mean_force":0.27447,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49712,-0.0777,0.05948]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.51644,-0.02763,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49729,-0.0436,0.21555]},{"body_a":"world","body_b":"push_box","contact_count":2704.0,"contact_point_centroid":[0.51644,-0.02763,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50252,-0.02032,0.07916]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.50488,-0.16128,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.45478,-0.06246,0.15776]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.50488,-0.16128,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":5.0,"phase_name":"insert_2","phase_type":"insert","tcp_position_centroid":[0.44367,-0.11361,0.14924]}],"total_contact_groups":10},"final_pose_error":0.05774,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50488,-0.16128,0.02499],"final_tcp_position":[0.47401,-0.13421,0.07408],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.51644,-0.02763,0.025]},"peak_contact_force":71.29552,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51644,-0.02763,0.02499],"object_pos_start":[0.51644,-0.02763,0.025],"object_to_goal_dist_end":0.12347,"object_to_goal_dist_start":0.12347,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.4966,-0.08596,0.13695],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.12779,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":676.0,"n_steps_budget":1000.0,"object_pos_end":[0.51644,-0.02763,0.02499],"object_pos_start":[0.51644,-0.02763,0.02499],"object_to_goal_dist_end":0.12347,"object_to_goal_dist_start":0.12347,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2704.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.51104,0.04412,0.02621],"tcp_start":[0.4966,-0.08596,0.13695],"tcp_to_object_dist_end":0.07196,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50703,-0.16409,0.02905],"object_pos_start":[0.51644,-0.02763,0.02499],"object_to_goal_dist_end":0.01626,"object_to_goal_dist_start":0.12347,"object_z_max":0.03041,"peak_contact_force":40.37602,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3444.0,"raw_peak_contact_force":71.29552,"tcp_end":[0.50118,-0.12532,0.02256],"tcp_start":[0.51104,0.04412,0.02621],"tcp_to_object_dist_end":0.03974,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50488,-0.16128,0.02499],"object_pos_start":[0.50703,-0.16409,0.02905],"object_to_goal_dist_end":0.01229,"object_to_goal_dist_start":0.01626,"object_z_max":0.0291,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3898.0,"raw_peak_contact_force":34.84993,"tcp_end":[0.49707,-0.03083,0.09288],"tcp_start":[0.50118,-0.12532,0.02256],"tcp_to_object_dist_end":0.14726,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50488,-0.16128,0.02499],"object_pos_start":[0.50488,-0.16128,0.02499],"object_to_goal_dist_end":0.01229,"object_to_goal_dist_start":0.01229,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.41627,-0.09385,0.22599],"tcp_start":[0.49707,-0.03083,0.09288],"tcp_to_object_dist_end":0.22978,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50488,-0.16128,0.02499],"object_pos_start":[0.50488,-0.16128,0.02499],"object_to_goal_dist_end":0.01229,"object_to_goal_dist_start":0.01229,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"insert_2","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.47401,-0.13421,0.07408],"tcp_start":[0.41627,-0.09385,0.22599],"tcp_to_object_dist_end":0.06399,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `88c86884172a74f1f27b08fda534b767baf4d8d60d3fd4d782dec9555f4aae87`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.71318,"average_solve_count":258.0,"average_success_count":258.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"lift_1.speed":0.05301,"push_1.push_distance":0.19889,"push_1.push_speed":0.09977,"retract_1.retract_height":0.05591,"retract_1.speed":0.06887},"optimized_scores":{"best_composite_score":0.00451,"best_fitness_score":0.37451,"best_task_score":0.57965},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":286.0,"contact_point_centroid":[0.51033,0.08541,0.04646],"force_p95":154.66051,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":181.6215,"mean_force":112.54583,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50235,0.09183,0.04903]},{"body_a":"world","body_b":"push_box","contact_count":3422.0,"contact_point_centroid":[0.50174,0.05825,-9e-05],"force_p95":81.58625,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":164.76933,"mean_force":9.73416,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49612,0.00715,0.08615]},{"body_a":"attachment","body_b":"push_box","contact_count":994.0,"contact_point_centroid":[0.50365,0.03318,0.03087],"force_p95":73.10428,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":78.1582,"mean_force":53.15394,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50161,0.04446,0.03149]},{"body_a":"world","body_b":"push_box","contact_count":1912.0,"contact_point_centroid":[0.4965,-0.00213,-0.00016],"force_p95":57.13712,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":68.61458,"mean_force":39.22613,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50165,0.04727,0.03166]},{"body_a":"push_box","body_b":"link7","contact_count":1000.0,"contact_point_centroid":[0.52164,0.0097,0.06806],"force_p95":31.01093,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":53.8641,"mean_force":28.08153,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50161,0.04492,0.03151]},{"body_a":"push_box","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.52838,0.09012,0.06853],"force_p95":39.95326,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":40.31824,"mean_force":36.49581,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50206,0.12188,0.0353]},{"body_a":"world","body_b":"push_box","contact_count":3763.0,"contact_point_centroid":[0.48488,-0.06663,-1e-05],"force_p95":0.27325,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":29.91113,"mean_force":0.28359,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4957,0.00716,0.07179]},{"body_a":"push_box","body_b":"link7","contact_count":13.0,"contact_point_centroid":[0.50905,-0.07649,0.06713],"force_p95":27.97249,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":29.57283,"mean_force":7.15211,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4989,-0.03984,0.02578]},{"body_a":"attachment","body_b":"push_box","contact_count":43.0,"contact_point_centroid":[0.49485,-0.04567,0.03148],"force_p95":2.83721,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.30788,"mean_force":0.94019,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49674,-0.03416,0.03053]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.50142,0.05406,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49729,-0.0436,0.21555]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.48528,-0.0655,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4612,0.00994,0.15816]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.48528,-0.0655,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":5.0,"phase_name":"insert_2","phase_type":"insert","tcp_position_centroid":[0.45148,-0.07516,0.14112]}],"total_contact_groups":12},"final_pose_error":0.06309,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.48528,-0.0655,0.02499],"final_tcp_position":[0.47634,-0.11663,0.07303],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50142,0.05406,0.025]},"peak_contact_force":181.6215,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50142,0.05406,0.02499],"object_pos_start":[0.50142,0.05406,0.025],"object_to_goal_dist_end":0.20406,"object_to_goal_dist_start":0.20406,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.4966,-0.08596,0.13695],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.17934,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50341,0.08175,0.03419],"object_pos_start":[0.50142,0.05406,0.02499],"object_to_goal_dist_end":0.23196,"object_to_goal_dist_start":0.20406,"object_z_max":0.03486,"peak_contact_force":40.31824,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3711.0,"raw_peak_contact_force":181.6215,"tcp_end":[0.50193,0.12221,0.03486],"tcp_start":[0.4966,-0.08596,0.13695],"tcp_to_object_dist_end":0.04049,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.48273,-0.07945,0.03355],"object_pos_start":[0.50341,0.08175,0.03419],"object_to_goal_dist_end":0.07314,"object_to_goal_dist_start":0.23196,"object_z_max":0.03432,"peak_contact_force":33.25693,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3906.0,"raw_peak_contact_force":78.1582,"tcp_end":[0.49928,-0.03972,0.02564],"tcp_start":[0.50193,0.12221,0.03486],"tcp_to_object_dist_end":0.04376,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.48528,-0.0655,0.02499],"object_pos_start":[0.48273,-0.07945,0.03355],"object_to_goal_dist_end":0.08578,"object_to_goal_dist_start":0.07314,"object_z_max":0.03359,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3819.0,"raw_peak_contact_force":29.91113,"tcp_end":[0.49612,0.05498,0.10952],"tcp_start":[0.49928,-0.03972,0.02564],"tcp_to_object_dist_end":0.14757,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.48528,-0.0655,0.02499],"object_pos_start":[0.48528,-0.0655,0.02499],"object_to_goal_dist_end":0.08578,"object_to_goal_dist_start":0.08578,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.42951,-0.0347,0.211],"tcp_start":[0.49612,0.05498,0.10952],"tcp_to_object_dist_end":0.19662,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.48528,-0.0655,0.02499],"object_pos_start":[0.48528,-0.0655,0.02499],"object_to_goal_dist_end":0.08578,"object_to_goal_dist_start":0.08578,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"insert_2","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.47634,-0.11663,0.07303],"tcp_start":[0.42951,-0.0347,0.211],"tcp_to_object_dist_end":0.07073,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `a3cdbd735282928b0caf1de02aaaeed7f0a3d0a10908989412c558d20f3517fa`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.72727,"average_solve_count":253.0,"average_success_count":253.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"lift_1.speed":0.07087,"push_1.push_distance":0.165,"push_1.push_speed":0.09234,"retract_1.retract_height":0.08642,"retract_1.speed":0.03824},"optimized_scores":{"best_composite_score":0.31928,"best_fitness_score":0.68928,"best_task_score":0.90419},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":728.0,"contact_point_centroid":[0.48314,-0.06761,0.03094],"force_p95":18.00643,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":27.45013,"mean_force":4.23311,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47846,-0.05562,0.02185]},{"body_a":"world","body_b":"push_box","contact_count":2035.0,"contact_point_centroid":[0.477,-0.0745,-3e-05],"force_p95":7.05814,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":18.53708,"mean_force":1.81,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47496,-0.0268,0.02258]},{"body_a":"attachment","body_b":"push_box","contact_count":5.0,"contact_point_centroid":[0.50136,-0.13501,0.05006],"force_p95":3.69709,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.33587,"mean_force":1.46842,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48725,-0.12287,0.02079]},{"body_a":"world","body_b":"push_box","contact_count":3963.0,"contact_point_centroid":[0.49276,-0.16003,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.86325,"mean_force":0.24899,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48572,-0.07599,0.05787]},{"body_a":"push_box","body_b":"link7","contact_count":14.0,"contact_point_centroid":[0.51751,-0.12818,0.05023],"force_p95":2.0728,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.21854,"mean_force":0.86826,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48621,-0.114,0.02098]},{"body_a":"push_box","body_b":"link7","contact_count":5.0,"contact_point_centroid":[0.51791,-0.14119,0.05019],"force_p95":0.47163,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.55248,"mean_force":0.14014,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48678,-0.12267,0.0208]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.47139,-0.02418,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49729,-0.0436,0.21555]},{"body_a":"world","body_b":"push_box","contact_count":2520.0,"contact_point_centroid":[0.47139,-0.02418,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48142,-0.0196,0.08025]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.49272,-0.15999,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.45013,-0.05835,0.15424]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.49272,-0.15999,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":5.0,"phase_name":"insert_2","phase_type":"insert","tcp_position_centroid":[0.44318,-0.1107,0.14518]}],"total_contact_groups":10},"final_pose_error":0.05675,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.49272,-0.15999,0.02499],"final_tcp_position":[0.47378,-0.13298,0.07237],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47139,-0.02418,0.025]},"peak_contact_force":27.45013,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47139,-0.02418,0.02499],"object_pos_start":[0.47139,-0.02418,0.025],"object_to_goal_dist_end":0.12903,"object_to_goal_dist_start":0.12903,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.4966,-0.08596,0.13695],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.13033,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":630.0,"n_steps_budget":1000.0,"object_pos_end":[0.47139,-0.02418,0.02499],"object_pos_start":[0.47139,-0.02418,0.02499],"object_to_goal_dist_end":0.12903,"object_to_goal_dist_start":0.12903,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2520.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.46892,0.04665,0.02746],"tcp_start":[0.4966,-0.08596,0.13695],"tcp_to_object_dist_end":0.07092,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.493,-0.15963,0.02498],"object_pos_start":[0.47139,-0.02418,0.02499],"object_to_goal_dist_end":0.01191,"object_to_goal_dist_start":0.12903,"object_z_max":0.02534,"peak_contact_force":10.65586,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2777.0,"raw_peak_contact_force":27.45013,"tcp_end":[0.48734,-0.12277,0.02084],"tcp_start":[0.46892,0.04665,0.02746],"tcp_to_object_dist_end":0.03753,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49272,-0.15999,0.02499],"object_pos_start":[0.493,-0.15963,0.02498],"object_to_goal_dist_end":0.01236,"object_to_goal_dist_start":0.01191,"object_z_max":0.02512,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3973.0,"raw_peak_contact_force":4.33587,"tcp_end":[0.48808,-0.02751,0.09288],"tcp_start":[0.48734,-0.12277,0.02084],"tcp_to_object_dist_end":0.14894,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49272,-0.15999,0.02499],"object_pos_start":[0.49272,-0.15999,0.02499],"object_to_goal_dist_end":0.01236,"object_to_goal_dist_start":0.01236,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.41553,-0.08927,0.21961],"tcp_start":[0.48808,-0.02751,0.09288],"tcp_to_object_dist_end":0.22099,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49272,-0.15999,0.02499],"object_pos_start":[0.49272,-0.15999,0.02499],"object_to_goal_dist_end":0.01236,"object_to_goal_dist_start":0.01236,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"insert_2","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.47378,-0.13298,0.07237],"tcp_start":[0.41553,-0.08927,0.21961],"tcp_to_object_dist_end":0.05773,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```