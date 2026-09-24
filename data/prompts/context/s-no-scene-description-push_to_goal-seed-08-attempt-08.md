## Search State

- **Seed**: 8
- **Iteration**: 9 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 8 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | time_limit | 6 | 0.7008 | 0.57 | ❌ rejected |
| 7 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | time_limit | 6 | 0.5426 | 0.59 | ✅ accepted |
| 6 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | time_limit | 6 | -0.1776 | 0.00 | ✅ accepted |
| 5 | pull → insert → descend → contact | arc_cartesian | impedance_motion | linear_cartesian | linear_cartesian | impedance_control | impedance_control | position_control | impedance_control | time_limit | pose_tolerance | contact_detected | force_exceeded | 5 | -0.3100 | 0.00 | ❌ rejected |
| 4 | pull → insert → descend → contact | arc_cartesian | impedance_motion | linear_cartesian | linear_cartesian | impedance_control | impedance_control | position_control | impedance_control | time_limit | pose_tolerance | contact_detected | force_exceeded | 5 | -0.3100 | 0.00 | ❌ rejected |

**Proposal policy**: task_score is 0.57 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.701) — your mutation base

```yaml
skill: push_to_goal
dsl_version: 2
subtasks:
- id: reach_object
  anchor: object
  offset:
  - 0.0
  - 0.08
  - 0.01
  weight: 0.3
- id: push_to_goal
  target_entity: object
  weight: 0.7
phases:
- id: approach_1
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.08
    - 0.01
  parameters:
    speed:
      type: scalar
      range:
      - 0.1
      - 0.4
      default: 0.25
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_object
- id: contact_1
  type: contact
  generator: linear_cartesian
  control: force_threshold_switch
  termination: force_exceeded
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.08
      axis: task_goal_direction
      mode: replace_offset_projection
      sign: positive
  parameters:
    force_threshold:
      type: scalar
      range:
      - 1.0
      - 15.0
      default: 5.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_object
- id: push_1
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: time_limit
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.3
      axis: task_goal_direction
      mode: replace_offset_projection
      sign: positive
  parameters:
    max_time:
      type: scalar
      range:
      - 1.0
      - 10.0
      default: 5.0
      binds_to:
      - path: duration.max_time
        mode: replace
    push_distance:
      type: scalar
      range:
      - 0.1
      - 0.5
      default: 0.3
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: push_to_goal

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.08, 0.01]
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
- **contact_1** (`contact`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.08, mode=replace_offset_projection, sign=positive}
  - parameter_bindings:
    - force_threshold: status=consumed; consumers=termination.force_threshold (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **push_1** (`push`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.3, mode=replace_offset_projection, sign=positive}
  - parameter_bindings:
    - max_time: status=consumed; consumers=duration.max_time (replace)
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: 0.701
- **task_score** (E): 0.569
- **fitness_score**: 0.531  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.500
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.330

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2742 |
| contact_1 | 1.00 | 1.00 | 0.0425 |
| push_1 | 1.00 | 1.00 | 0.1863 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.521, 0.075, 0.042) | (0.526, -0.001, 0.025)→(0.526, -0.001, 0.025) | 0.156→0.156 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact_1 | contact | 1.00 / force_exceeded | (0.521, 0.075, 0.042)→(0.507, 0.036, 0.037) | (0.526, -0.001, 0.025)→(0.526, -0.001, 0.025) | 0.156→0.156 | 1.00 / 5.000 | 14.909 | 0.245 |
| push_1 | push | 1.00 / time_limit | (0.507, 0.036, 0.037)→(0.471, -0.141, 0.033) | (0.526, -0.001, 0.025)→(0.522, -0.115, 0.027) | 0.156→0.060 | 1.00 / 3.000 | 0.185 | 70.177 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 1.000
- lateral_force_integral: None
- approach_alignment: 0.742
- goal_progress: 0.829
- terminal_score: 0.829
- phase_score: 0.722
- phase_breakdown.reach_object_score: 0.421
- phase_breakdown.push_to_goal_score: 0.851

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.765
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.829
- **Median Q (composite search score)**: 0.678
- **K-run variance**: 0.0333
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.309


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `8267fcc1127ab3c529e380fe6aea430def9956719b146bd9818eb52355cb895d`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.06,0.06]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `33d626702a3717cebb1eda35e1cb80c1c9d108c246efccd193577b9105813420`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.375,"average_solve_count":80.0,"average_success_count":80.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.2118,"contact_1.force_threshold":8.96046,"contact_1.speed":0.04109,"push_1.max_time":5.53725,"push_1.push_distance":0.25896,"push_1.push_speed":0.18274},"optimized_scores":{"best_composite_score":0.93489,"best_fitness_score":0.76489,"best_task_score":0.8289},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":608.0,"contact_point_centroid":[0.4912,-0.02927,0.04382],"force_p95":40.66867,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":102.48285,"mean_force":9.21074,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4836,-0.01784,0.0329]},{"body_a":"world","body_b":"push_box","contact_count":991.0,"contact_point_centroid":[0.50047,-0.06631,-0.00011],"force_p95":22.14997,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":62.17148,"mean_force":6.49106,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48342,-0.01513,0.03301]},{"body_a":"push_box","body_b":"link7","contact_count":31.0,"contact_point_centroid":[0.53618,-0.13316,0.05813],"force_p95":33.33548,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":34.19648,"mean_force":10.4207,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49492,-0.12823,0.03261]},{"body_a":"world","body_b":"push_box","contact_count":3312.0,"contact_point_centroid":[0.47924,0.05847,-1e-05],"force_p95":0.24527,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48735,0.06555,0.16963]},{"body_a":"world","body_b":"push_box","contact_count":2012.0,"contact_point_centroid":[0.47924,0.05847,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.47435,0.11276,0.0375]}],"total_contact_groups":5},"final_pose_error":0.01438,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.52016,-0.17916,0.03034],"final_tcp_position":[0.49675,-0.14948,0.03236],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47924,0.05847,0.025]},"peak_contact_force":102.48285,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":828.0,"n_steps_budget":900.0,"object_pos_end":[0.47924,0.05847,0.02499],"object_pos_start":[0.47924,0.05847,0.025],"object_to_goal_dist_end":0.2095,"object_to_goal_dist_start":0.2095,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3312.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_object","tcp_end":[0.47626,0.13148,0.04178],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07497,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":503.0,"n_steps_budget":1000.0,"object_pos_end":[0.47924,0.05847,0.02499],"object_pos_start":[0.47924,0.05847,0.02499],"object_to_goal_dist_end":0.2095,"object_to_goal_dist_start":0.2095,"object_z_max":0.02499,"peak_contact_force":10.41752,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2012.0,"raw_peak_contact_force":0.24525,"subtask_id":"reach_object","tcp_end":[0.47572,0.09545,0.03711],"tcp_start":[0.47626,0.13148,0.04178],"tcp_to_object_dist_end":0.03907,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":871.0,"n_steps_budget":900.0,"object_pos_end":[0.52016,-0.17916,0.03034],"object_pos_start":[0.47924,0.05847,0.02499],"object_to_goal_dist_end":0.03585,"object_to_goal_dist_start":0.2095,"object_z_max":0.03121,"peak_contact_force":0.0,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1630.0,"raw_peak_contact_force":102.48285,"subtask_id":"push_to_goal","tcp_end":[0.49675,-0.14948,0.03236],"tcp_start":[0.47572,0.09545,0.03711],"tcp_to_object_dist_end":0.03785,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `021f3e69028f16fb65e79b302b37775f7324e143e034cbac30fdb04ffcd99d24`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.78205,"average_solve_count":78.0,"average_success_count":78.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.24617,"contact_1.force_threshold":8.51873,"contact_1.speed":0.02769,"push_1.max_time":3.3142,"push_1.push_distance":0.1724,"push_1.push_speed":0.19022},"optimized_scores":{"best_composite_score":0.67816,"best_fitness_score":0.50816,"best_task_score":0.64011},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":1039.0,"contact_point_centroid":[0.53939,-0.07485,-0.00022],"force_p95":74.9459,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":89.75055,"mean_force":21.55033,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49274,-0.05662,0.03611]},{"body_a":"push_box","body_b":"link7","contact_count":306.0,"contact_point_centroid":[0.53361,-0.05277,0.06094],"force_p95":76.09633,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":85.90912,"mean_force":50.41181,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49091,-0.06289,0.03675]},{"body_a":"attachment","body_b":"push_box","contact_count":443.0,"contact_point_centroid":[0.51488,-0.05471,0.05803],"force_p95":28.57169,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":36.2594,"mean_force":16.11119,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49632,-0.04714,0.03642]},{"body_a":"world","body_b":"push_box","contact_count":2680.0,"contact_point_centroid":[0.54443,-0.02558,-1e-05],"force_p95":0.24528,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51774,0.02493,0.17297]},{"body_a":"world","body_b":"push_box","contact_count":3412.0,"contact_point_centroid":[0.54443,-0.02558,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.5263,0.02999,0.03864]}],"total_contact_groups":5},"final_pose_error":0.01236,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.49995,-0.10245,0.02474],"final_tcp_position":[0.46168,-0.13938,0.03415],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.54443,-0.02558,0.025]},"peak_contact_force":89.75055,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":670.0,"n_steps_budget":720.0,"object_pos_end":[0.54443,-0.02558,0.02499],"object_pos_start":[0.54443,-0.02558,0.025],"object_to_goal_dist_end":0.13211,"object_to_goal_dist_start":0.13211,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2680.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_object","tcp_end":[0.5378,0.05099,0.04379],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07913,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":853.0,"n_steps_budget":1000.0,"object_pos_end":[0.54443,-0.02558,0.02499],"object_pos_start":[0.54443,-0.02558,0.02499],"object_to_goal_dist_end":0.13211,"object_to_goal_dist_start":0.13211,"object_z_max":0.02499,"peak_contact_force":19.23661,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":3412.0,"raw_peak_contact_force":0.24525,"subtask_id":"reach_object","tcp_end":[0.51945,0.01142,0.0385],"tcp_start":[0.5378,0.05099,0.04379],"tcp_to_object_dist_end":0.04664,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":571.0,"n_steps_budget":600.0,"object_pos_end":[0.49995,-0.10245,0.02474],"object_pos_start":[0.54443,-0.02558,0.02499],"object_to_goal_dist_end":0.04755,"object_to_goal_dist_start":0.13211,"object_z_max":0.03423,"peak_contact_force":0.31117,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1788.0,"raw_peak_contact_force":89.75055,"subtask_id":"push_to_goal","tcp_end":[0.46168,-0.13938,0.03415],"tcp_start":[0.51945,0.01142,0.0385],"tcp_to_object_dist_end":0.054,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `886824c4c8b8334954c1de9b3100fb0acfdd4a04855e7e82a07b72c52723cc86`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.28916,"average_solve_count":83.0,"average_success_count":83.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.17103,"contact_1.force_threshold":9.47808,"contact_1.speed":0.08964,"push_1.max_time":9.19005,"push_1.push_distance":0.15967,"push_1.push_speed":0.09199},"optimized_scores":{"best_composite_score":0.48948,"best_fitness_score":0.31948,"best_task_score":0.23881},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":361.0,"contact_point_centroid":[0.52256,-0.03517,0.0521],"force_p95":14.63909,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":18.29841,"mean_force":7.76114,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50787,-0.02499,0.03238]},{"body_a":"world","body_b":"push_box","contact_count":3020.0,"contact_point_centroid":[0.54731,-0.06458,-3e-05],"force_p95":10.61591,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":18.06397,"mean_force":1.36697,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48258,-0.07712,0.03194]},{"body_a":"push_box","body_b":"link7","contact_count":32.0,"contact_point_centroid":[0.55114,-0.0242,0.05589],"force_p95":17.30186,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":17.32956,"mean_force":12.85416,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50699,-0.02584,0.03185]},{"body_a":"world","body_b":"push_box","contact_count":3172.0,"contact_point_centroid":[0.55472,-0.03508,-1e-05],"force_p95":0.24527,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.52299,0.02104,0.17028]},{"body_a":"world","body_b":"push_box","contact_count":1320.0,"contact_point_centroid":[0.55472,-0.03508,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.53478,0.02256,0.03703]}],"total_contact_groups":5},"final_pose_error":0.01024,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.54561,-0.06452,0.02499],"final_tcp_position":[0.45575,-0.1331,0.03198],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55472,-0.03508,0.025]},"peak_contact_force":18.29841,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":793.0,"n_steps_budget":1000.0,"object_pos_end":[0.55472,-0.03508,0.02499],"object_pos_start":[0.55472,-0.03508,0.025],"object_to_goal_dist_end":0.12728,"object_to_goal_dist_start":0.12728,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3172.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_object","tcp_end":[0.54792,0.04241,0.04185],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07959,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":330.0,"n_steps_budget":600.0,"object_pos_end":[0.55472,-0.03508,0.02499],"object_pos_start":[0.55472,-0.03508,0.02499],"object_to_goal_dist_end":0.12728,"object_to_goal_dist_start":0.12728,"object_z_max":0.02499,"peak_contact_force":15.07139,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1320.0,"raw_peak_contact_force":0.24525,"subtask_id":"reach_object","tcp_end":[0.5244,0.00186,0.03646],"tcp_start":[0.54792,0.04241,0.04185],"tcp_to_object_dist_end":0.04914,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54561,-0.06452,0.02499],"object_pos_start":[0.55472,-0.03508,0.02499],"object_to_goal_dist_end":0.09689,"object_to_goal_dist_start":0.12728,"object_z_max":0.02805,"peak_contact_force":0.24525,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3413.0,"raw_peak_contact_force":18.29841,"subtask_id":"push_to_goal","tcp_end":[0.45575,-0.1331,0.03198],"tcp_start":[0.5244,0.00186,0.03646],"tcp_to_object_dist_end":0.11326,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
```