## Search State

- **Seed**: 8
- **Iteration**: 11 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 10 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | time_limit | 6 | 0.4114 | 0.77 | ✅ accepted |
| 9 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | time_limit | 6 | 0.4401 | 0.73 | ✅ accepted |
| 8 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | time_limit | 6 | 0.7008 | 0.57 | ❌ rejected |
| 7 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | time_limit | 6 | 0.5426 | 0.59 | ✅ accepted |
| 6 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | time_limit | 6 | -0.1776 | 0.00 | ✅ accepted |

**Proposal policy**: task_score is 0.77 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.411) — your mutation base

```yaml
skill: push_to_goal
dsl_version: 2
subtasks:
- id: reach_object
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.1
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
    - 0.0
    - 0.02
    offset_along_axis:
      distance: 0.15
      axis: task_goal_direction
      mode: replace_offset_projection
      sign: negative
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
      distance: 0.15
      axis: task_goal_direction
      mode: replace_offset_projection
      sign: positive
  parameters:
    force_threshold:
      type: scalar
      range:
      - 1.0
      - 25.0
      default: 8.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.04
      binds_to:
      - path: generator.speed
        mode: replace
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
      distance: 0.4
      axis: task_goal_direction
      mode: replace_offset_projection
      sign: positive
  parameters:
    max_time:
      type: scalar
      range:
      - 1.0
      - 5.0
      default: 3.0
      binds_to:
      - path: duration.max_time
        mode: replace
    push_distance:
      type: scalar
      range:
      - 0.2
      - 0.6
      default: 0.4
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
  guards:
  - id: contact_guard
    when: during_phase
    predicate: contact_detected
    threshold: 0.5
    on_failure: retry
  retries:
    max_attempts: 1
    strategy: offset_target
    offset:
    - 0.0
    - -0.02
    - 0.0
  subtask_id: push_to_goal

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.02], offset_along_axis={axis=task_goal_direction, distance=0.15, mode=replace_offset_projection, sign=negative}
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
- **contact_1** (`contact`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.15, mode=replace_offset_projection, sign=positive}
  - parameter_bindings:
    - force_threshold: status=consumed; consumers=termination.force_threshold (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **push_1** (`push`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.4, mode=replace_offset_projection, sign=positive}
  - parameter_bindings:
    - max_time: status=consumed; consumers=duration.max_time (replace)
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=contact_guard, when=during_phase, predicate=contact_detected, on_failure=retry, threshold=0.5
  - retries: max_attempts=1, strategy=offset_target, offset=[0.0, -0.02, 0.0]

## Design Metrics

- **Composite score**: 0.411
- **task_score** (E): 0.768
- **fitness_score**: 0.575  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.167
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.330

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2970 |
| contact_1 | 0.33 | 1.00 | 0.0933 |
| push_1 | 1.00 | 1.00 | 0.2088 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.553, 0.133, 0.052) | (0.526, -0.001, 0.025)→(0.526, -0.001, 0.025) | 0.156→0.156 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact_1 | contact | 0.33 / step_budget | (0.553, 0.133, 0.052)→(0.529, 0.046, 0.046) | (0.526, -0.001, 0.025)→(0.526, -0.001, 0.025) | 0.156→0.156 | 1.00 / 4.333 | 9.570 | 0.245 |
| push_1 | push | 1.00 / time_limit | (0.529, 0.046, 0.046)→(0.490, -0.152, 0.043) | (0.526, -0.001, 0.025)→(0.513, -0.129, 0.031) | 0.156→0.033 | 1.00 / 2.333 | 15.516 | 67.765 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.855
- lateral_force_integral: None
- approach_alignment: 0.734
- goal_progress: 0.758
- terminal_score: 0.758
- phase_score: 0.486
- phase_breakdown.reach_object_score: 0.039
- phase_breakdown.push_to_goal_score: 0.678

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.598
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.912
- **Median Q (composite search score)**: 0.268
- **K-run variance**: 0.0633
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Parameters at upper bound**: approach_1.speed
- **Final σ (mean)**: 0.305


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.38462,"average_solve_count":91.0,"average_success_count":91.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.39999,"contact_1.force_threshold":1.03722,"contact_1.speed":0.06036,"push_1.max_time":1.26244,"push_1.push_distance":0.43581,"push_1.push_speed":0.16614},"optimized_scores":{"best_composite_score":0.26762,"best_fitness_score":0.59762,"best_task_score":0.91229},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":851.0,"contact_point_centroid":[0.49077,-0.04547,0.04851],"force_p95":120.3708,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":154.9653,"mean_force":69.20866,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48352,-0.04201,0.05138]},{"body_a":"world","body_b":"push_box","contact_count":1565.0,"contact_point_centroid":[0.49681,-0.05509,-0.00035],"force_p95":112.38318,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":151.66172,"mean_force":38.221,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48189,-0.02802,0.0512]},{"body_a":"world","body_b":"push_box","contact_count":2260.0,"contact_point_centroid":[0.47924,0.05847,-1e-05],"force_p95":0.24528,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48199,0.09198,0.18237]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.47924,0.05847,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.46474,0.14386,0.05218]}],"total_contact_groups":4},"final_pose_error":0.17359,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.48754,-0.13863,0.0323],"final_tcp_position":[0.49688,-0.16637,0.05163],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47924,0.05847,0.025]},"peak_contact_force":154.9653,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":565.0,"n_steps_budget":600.0,"object_pos_end":[0.47924,0.05847,0.02499],"object_pos_start":[0.47924,0.05847,0.025],"object_to_goal_dist_end":0.2095,"object_to_goal_dist_start":0.2095,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2260.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_object","tcp_end":[0.46363,0.19312,0.05666],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.1392,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47924,0.05847,0.02499],"object_pos_start":[0.47924,0.05847,0.02499],"object_to_goal_dist_end":0.2095,"object_to_goal_dist_start":0.2095,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.46948,0.09443,0.0521],"tcp_start":[0.46363,0.19312,0.05666],"tcp_to_object_dist_end":0.04608,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.48754,-0.13863,0.0323],"object_pos_start":[0.47924,0.05847,0.02499],"object_to_goal_dist_end":0.01838,"object_to_goal_dist_start":0.2095,"object_z_max":0.03449,"peak_contact_force":42.50823,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2416.0,"raw_peak_contact_force":154.9653,"subtask_id":"push_to_goal","tcp_end":[0.49688,-0.16637,0.05163],"tcp_start":[0.46948,0.09443,0.0521],"tcp_to_object_dist_end":0.03508,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `021f3e69028f16fb65e79b302b37775f7324e143e034cbac30fdb04ffcd99d24`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.78571,"average_solve_count":98.0,"average_success_count":98.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.25081,"contact_1.force_threshold":21.35062,"contact_1.speed":0.04334,"push_1.max_time":3.90172,"push_1.push_distance":0.53515,"push_1.push_speed":0.11848},"optimized_scores":{"best_composite_score":0.20145,"best_fitness_score":0.53145,"best_task_score":0.63277},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":572.0,"contact_point_centroid":[0.53065,-0.06939,0.0557],"force_p95":16.8263,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":20.85628,"mean_force":5.24884,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51668,-0.06176,0.04067]},{"body_a":"world","body_b":"push_box","contact_count":1906.0,"contact_point_centroid":[0.54948,-0.06803,-5e-05],"force_p95":8.65185,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":13.32201,"mean_force":2.01189,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52751,-0.03262,0.04102]},{"body_a":"world","body_b":"push_box","contact_count":2808.0,"contact_point_centroid":[0.54443,-0.02558,-1e-05],"force_p95":0.24527,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.54128,0.0531,0.17719]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.54443,-0.02558,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.56959,0.0739,0.0458]}],"total_contact_groups":4},"final_pose_error":0.34248,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.52354,-0.10783,0.02964],"final_tcp_position":[0.48872,-0.13975,0.04078],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.54443,-0.02558,0.025]},"peak_contact_force":20.85628,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":702.0,"n_steps_budget":750.0,"object_pos_end":[0.54443,-0.02558,0.02499],"object_pos_start":[0.54443,-0.02558,0.025],"object_to_goal_dist_end":0.13211,"object_to_goal_dist_start":0.13211,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2808.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_object","tcp_end":[0.5861,0.10886,0.05183],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.14329,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54443,-0.02558,0.02499],"object_pos_start":[0.54443,-0.02558,0.02499],"object_to_goal_dist_end":0.13211,"object_to_goal_dist_start":0.13211,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.55741,0.04038,0.04582],"tcp_start":[0.5861,0.10886,0.05183],"tcp_to_object_dist_end":0.07038,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52354,-0.10783,0.02964],"object_pos_start":[0.54443,-0.02558,0.02499],"object_to_goal_dist_end":0.04852,"object_to_goal_dist_start":0.13211,"object_z_max":0.03259,"peak_contact_force":0.75679,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2478.0,"raw_peak_contact_force":20.85628,"subtask_id":"push_to_goal","tcp_end":[0.48872,-0.13975,0.04078],"tcp_start":[0.55741,0.04038,0.04582],"tcp_to_object_dist_end":0.04853,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `886824c4c8b8334954c1de9b3100fb0acfdd4a04855e7e82a07b72c52723cc86`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.24272,"average_solve_count":103.0,"average_success_count":103.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.17298,"contact_1.force_threshold":8.16669,"contact_1.speed":0.07604,"push_1.max_time":4.70584,"push_1.push_distance":0.33618,"push_1.push_speed":0.10486},"optimized_scores":{"best_composite_score":0.7651,"best_fitness_score":0.5951,"best_task_score":0.75832},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":1670.0,"contact_point_centroid":[0.54832,-0.10855,-7e-05],"force_p95":20.38954,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":27.47404,"mean_force":4.88664,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52176,-0.07284,0.03645]},{"body_a":"push_box","body_b":"link7","contact_count":198.0,"contact_point_centroid":[0.53983,-0.10451,0.06294],"force_p95":22.17242,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":24.10981,"mean_force":15.14513,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49967,-0.11938,0.03687]},{"body_a":"attachment","body_b":"push_box","contact_count":787.0,"contact_point_centroid":[0.53347,-0.08353,0.05202],"force_p95":15.53329,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":24.03984,"mean_force":5.74606,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52107,-0.07409,0.03634]},{"body_a":"world","body_b":"push_box","contact_count":3824.0,"contact_point_centroid":[0.55472,-0.03508,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.555,0.04841,0.17094]},{"body_a":"world","body_b":"push_box","contact_count":3376.0,"contact_point_centroid":[0.55472,-0.03508,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.58418,0.04918,0.04103]}],"total_contact_groups":5},"final_pose_error":0.16519,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.52835,-0.1404,0.03209],"final_tcp_position":[0.48423,-0.15086,0.03632],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55472,-0.03508,0.025]},"peak_contact_force":28.2184,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":956.0,"n_steps_budget":1000.0,"object_pos_end":[0.55472,-0.03508,0.02499],"object_pos_start":[0.55472,-0.03508,0.025],"object_to_goal_dist_end":0.12728,"object_to_goal_dist_start":0.12728,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3824.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_object","tcp_end":[0.61052,0.09601,0.0472],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.14419,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":844.0,"n_steps_budget":1000.0,"object_pos_end":[0.55472,-0.03508,0.02499],"object_pos_start":[0.55472,-0.03508,0.02499],"object_to_goal_dist_end":0.12728,"object_to_goal_dist_start":0.12728,"object_z_max":0.02499,"peak_contact_force":28.2184,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":3376.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.56138,0.00192,0.04114],"tcp_start":[0.61052,0.09601,0.0472],"tcp_to_object_dist_end":0.04091,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52835,-0.1404,0.03209],"object_pos_start":[0.55472,-0.03508,0.02499],"object_to_goal_dist_end":0.03076,"object_to_goal_dist_start":0.12728,"object_z_max":0.03249,"peak_contact_force":3.2819,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2655.0,"raw_peak_contact_force":27.47404,"subtask_id":"push_to_goal","tcp_end":[0.48423,-0.15086,0.03632],"tcp_start":[0.56138,0.00192,0.04114],"tcp_to_object_dist_end":0.04554,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
```