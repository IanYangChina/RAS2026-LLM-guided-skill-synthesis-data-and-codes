## Search State

- **Seed**: 3
- **Iteration**: 7 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 6 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | pose_tolerance | force_exceeded | time_limit | 7 | 0.3554 | 0.88 | ✅ accepted |
| 5 | approach → align → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | admittance_control | pose_tolerance | pose_tolerance | time_limit | 4 | -0.0820 | 0.00 | ❌ rejected |
| 4 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | pose_tolerance | force_exceeded | time_limit | 5 | 0.5559 | 0.39 | ❌ rejected |
| 3 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | pose_tolerance | force_exceeded | time_limit | 5 | 0.5565 | 0.39 | ✅ accepted |
| 2 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | pose_tolerance | force_exceeded | time_limit | 5 | 0.5559 | 0.39 | ✅ accepted |

**Proposal policy**: task_score is 0.88 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.355) — your mutation base

```yaml
skill: push_to_goal
dsl_version: 2
subtasks:
- id: approach_object
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.15
  weight: 0.3
- id: push_progress
  target_entity: object
  metric: goal_progress
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
    - 0.15
    offset_along_axis:
      distance: 0.05
      axis: task_goal_direction
      mode: add_to_offset
      sign: negative
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.05
      - 0.5
      default: 0.2
      binds_to:
      - path: generator.speed
        mode: replace
    behind_offset:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
  guards:
  - id: no_obstacle
    when: before_phase
    predicate: force_below
    threshold: 5.0
    on_failure: abort
  subtask_id: approach_object
- id: descend_to_push
  type: descend
  generator: linear_cartesian
  control: force_threshold_switch
  termination: force_exceeded
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.025
    offset_along_axis:
      distance: 0.05
      axis: task_goal_direction
      mode: add_to_offset
      sign: negative
    tolerance: 0.02
  parameters:
    descend_force_threshold:
      type: scalar
      range:
      - 0.5
      - 5.0
      default: 1.5
      binds_to:
      - path: termination.force_threshold
        mode: replace
    descend_speed:
      type: scalar
      range:
      - 0.01
      - 0.2
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: contact_obtained
    when: after_phase
    predicate: contact_detected
    threshold: 0.0
    on_failure: retry
  retries:
    max_attempts: 1
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - 0.005
  subtask_id: approach_object
- id: push_1
  type: push
  generator: linear_cartesian
  control: admittance_control
  termination: time_limit
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.2
      axis: task_goal_direction
      mode: add_to_offset
      sign: positive
    tolerance: 0.03
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.1
      - 0.3
      default: 0.2
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.02
      - 0.3
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
    push_timeout:
      type: scalar
      range:
      - 2.0
      - 10.0
      default: 5.0
      binds_to:
      - path: duration.max_time
        mode: replace
  guards:
  - id: contact_maintained
    when: during_phase
    predicate: contact_detected
    threshold: 0.0
    on_failure: abort
  subtask_id: push_progress

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.15], offset_along_axis={axis=task_goal_direction, distance=0.05, mode=add_to_offset, sign=negative}, tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
    - behind_offset: status=consumed; consumers=target.offset_along_axis.distance (replace)
  - guards:
    - id=no_obstacle, when=before_phase, predicate=force_below, on_failure=abort, threshold=5.0
- **descend_to_push** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.025], offset_along_axis={axis=task_goal_direction, distance=0.05, mode=add_to_offset, sign=negative}, tolerance=0.02
  - parameter_bindings:
    - descend_force_threshold: status=consumed; consumers=termination.force_threshold (replace)
    - descend_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=contact_obtained, when=after_phase, predicate=contact_detected, on_failure=retry, threshold=0.0
  - retries: max_attempts=1, strategy=offset_target, offset=[0.0, 0.0, 0.005]
- **push_1** (`push`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.2, mode=add_to_offset, sign=positive}, tolerance=0.03
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
    - push_timeout: status=consumed; consumers=duration.max_time (replace)
  - guards:
    - id=contact_maintained, when=during_phase, predicate=contact_detected, on_failure=abort, threshold=0.0

## Design Metrics

- **Composite score**: 0.355
- **task_score** (E): 0.881
- **fitness_score**: 0.735  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.380

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1400 |
| descend_to_push | 0.00 | 1.00 | 0.1359 |
| push_1 | 1.00 | 0.67 | 0.1908 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.516, 0.053, 0.188) | (0.513, 0.002, 0.025)→(0.513, 0.002, 0.025) | 0.160→0.160 | 1.00 / 4.000 | 0.245 | 0.245 |
| descend_to_push | descend | 0.00 / step_budget | (0.516, 0.053, 0.188)→(0.512, 0.049, 0.053) | (0.513, 0.002, 0.025)→(0.513, 0.002, 0.025) | 0.160→0.160 | 1.00 / 4.000 | 0.245 | 0.245 |
| push_1 | push | 1.00 / time_limit | (0.512, 0.049, 0.053)→(0.492, -0.132, 0.035) | (0.513, 0.002, 0.025)→(0.513, -0.142, 0.027) | 0.160→0.019 | 0.67 / 1.000 | 0.271 | 47.514 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.958
- lateral_force_integral: None
- approach_alignment: 0.671
- goal_progress: 0.953
- terminal_score: 0.953
- phase_score: 0.688
- phase_breakdown.push_progress_score: 0.953
- phase_breakdown.approach_object_score: 0.070

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.794
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.953
- **Median Q (composite search score)**: 0.336
- **K-run variance**: 0.0018
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.286


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `01fea9f27a58d64b0f9b0ff0cae1096a52b0da1ad311c77058a75ddb9aab77d2`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.06,0.06]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `c53c9bf1992485fcf877d50f4ee23d3483b4b9e63e5a19adda2461c26d89c46e`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.99435,"average_solve_count":177.0,"average_success_count":177.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.1459,"approach_1.behind_offset":0.04452,"descend_to_push.descend_force_threshold":2.02559,"descend_to_push.descend_speed":0.01715,"push_1.push_distance":0.23906,"push_1.push_speed":0.08515,"push_1.push_timeout":3.7366},"optimized_scores":{"best_composite_score":0.31625,"best_fitness_score":0.69625,"best_task_score":0.83319},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":627.0,"contact_point_centroid":[0.45806,-0.06153,0.05005],"force_p95":19.29034,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":45.60783,"mean_force":8.20344,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.45242,-0.05048,0.04519]},{"body_a":"world","body_b":"push_box","contact_count":2143.0,"contact_point_centroid":[0.47864,-0.08375,-6e-05],"force_p95":10.70292,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":20.85539,"mean_force":2.76294,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.45109,-0.04694,0.04569]},{"body_a":"world","body_b":"push_box","contact_count":904.0,"contact_point_centroid":[0.45028,-0.03158,-0.0],"force_p95":0.24532,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.47212,0.00374,0.24731]},{"body_a":"world","body_b":"push_box","contact_count":3504.0,"contact_point_centroid":[0.45028,-0.03158,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"descend_to_push","phase_type":"descend","tcp_position_centroid":[0.43407,0.0109,0.12158]}],"total_contact_groups":4},"final_pose_error":0.2817,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.51451,-0.13424,0.02504],"final_tcp_position":[0.47908,-0.11301,0.03982],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.45028,-0.03158,0.025]},"peak_contact_force":45.60783,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":226.0,"n_steps_budget":630.0,"object_pos_end":[0.45028,-0.03158,0.02499],"object_pos_start":[0.45028,-0.03158,0.025],"object_to_goal_dist_end":0.12843,"object_to_goal_dist_start":0.12843,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":904.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach_object","tcp_end":[0.44253,0.00785,0.1921],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.17187,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":876.0,"n_steps_budget":1000.0,"object_pos_end":[0.45028,-0.03158,0.02499],"object_pos_start":[0.45028,-0.03158,0.02499],"object_to_goal_dist_end":0.12843,"object_to_goal_dist_start":0.12843,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"descend_to_push","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3504.0,"raw_peak_contact_force":0.24525,"subtask_id":"approach_object","tcp_end":[0.42801,0.01401,0.05392],"tcp_start":[0.44253,0.00785,0.1921],"tcp_to_object_dist_end":0.05841,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51451,-0.13424,0.02504],"object_pos_start":[0.45028,-0.03158,0.02499],"object_to_goal_dist_end":0.02142,"object_to_goal_dist_start":0.12843,"object_z_max":0.02544,"peak_contact_force":0.0,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2770.0,"raw_peak_contact_force":45.60783,"subtask_id":"push_progress","tcp_end":[0.47908,-0.11301,0.03982],"tcp_start":[0.42801,0.01401,0.05392],"tcp_to_object_dist_end":0.04386,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `234a0edc218dcf63b67654ddcfd8b0f12da84040687f62c4c4845001a50f549a`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.11236,"average_solve_count":89.0,"average_success_count":89.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.4518,"approach_1.behind_offset":0.06699,"descend_to_push.descend_force_threshold":1.50156,"descend_to_push.descend_speed":0.08807,"push_1.push_distance":0.23085,"push_1.push_speed":0.10088,"push_1.push_timeout":9.45807},"optimized_scores":{"best_composite_score":0.41396,"best_fitness_score":0.79396,"best_task_score":0.9528},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":637.0,"contact_point_centroid":[0.53275,-0.04218,0.0418],"force_p95":17.88144,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":24.43163,"mean_force":6.63553,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.534,-0.03036,0.04116]},{"body_a":"world","body_b":"push_box","contact_count":2003.0,"contact_point_centroid":[0.52866,-0.06625,-7e-05],"force_p95":8.41944,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":11.82002,"mean_force":2.44107,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.53638,-0.02415,0.04189]},{"body_a":"world","body_b":"push_box","contact_count":1108.0,"contact_point_centroid":[0.55317,0.00136,-1e-05],"force_p95":0.24532,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.5301,0.02684,0.24383]},{"body_a":"world","body_b":"push_box","contact_count":2600.0,"contact_point_centroid":[0.55317,0.00136,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"descend_to_push","phase_type":"descend","tcp_position_centroid":[0.56252,0.05174,0.11611]}],"total_contact_groups":4},"final_pose_error":0.27493,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.49913,-0.14248,0.02516],"final_tcp_position":[0.50804,-0.10645,0.0365],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55317,0.00136,0.025]},"peak_contact_force":24.43163,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":277.0,"n_steps_budget":600.0,"object_pos_end":[0.55317,0.00136,0.02499],"object_pos_start":[0.55317,0.00136,0.025],"object_to_goal_dist_end":0.16043,"object_to_goal_dist_start":0.16043,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1108.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach_object","tcp_end":[0.56257,0.05527,0.18673],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.17075,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":650.0,"n_steps_budget":990.0,"object_pos_end":[0.55317,0.00136,0.02499],"object_pos_start":[0.55317,0.00136,0.02499],"object_to_goal_dist_end":0.16043,"object_to_goal_dist_start":0.16043,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"descend_to_push","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2600.0,"raw_peak_contact_force":0.24525,"subtask_id":"approach_object","tcp_end":[0.565,0.04846,0.05152],"tcp_start":[0.56257,0.05527,0.18673],"tcp_to_object_dist_end":0.05534,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49913,-0.14248,0.02516],"object_pos_start":[0.55317,0.00136,0.02499],"object_to_goal_dist_end":0.00757,"object_to_goal_dist_start":0.16043,"object_z_max":0.02558,"peak_contact_force":0.81261,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2640.0,"raw_peak_contact_force":24.43163,"subtask_id":"push_progress","tcp_end":[0.50804,-0.10645,0.0365],"tcp_start":[0.565,0.04846,0.05152],"tcp_to_object_dist_end":0.0388,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `107d1233d3b0a09f0fa34aa18231b315c9a1d92237bb254399d486ed8004836a`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.50575,"average_solve_count":87.0,"average_success_count":87.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.31309,"approach_1.behind_offset":0.07415,"descend_to_push.descend_force_threshold":2.4478,"descend_to_push.descend_speed":0.08809,"push_1.push_distance":0.154,"push_1.push_speed":0.17031,"push_1.push_timeout":5.1231},"optimized_scores":{"best_composite_score":0.33592,"best_fitness_score":0.71592,"best_task_score":0.85748},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":1509.0,"contact_point_centroid":[0.54569,-0.06569,-0.0001],"force_p95":41.5185,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":72.5017,"mean_force":10.39805,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51679,-0.0326,0.03978]},{"body_a":"push_box","body_b":"link7","contact_count":305.0,"contact_point_centroid":[0.53673,-0.11116,0.06101],"force_p95":40.18886,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":54.36842,"mean_force":26.40422,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49925,-0.12965,0.03332]},{"body_a":"attachment","body_b":"push_box","contact_count":658.0,"contact_point_centroid":[0.52643,-0.06491,0.0554],"force_p95":28.74313,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":37.12542,"mean_force":11.64586,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51183,-0.05812,0.03766]},{"body_a":"world","body_b":"push_box","contact_count":1212.0,"contact_point_centroid":[0.5366,0.03695,-1e-05],"force_p95":0.24531,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.52021,0.04666,0.24262]},{"body_a":"world","body_b":"push_box","contact_count":2544.0,"contact_point_centroid":[0.5366,0.03695,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"descend_to_push","phase_type":"descend","tcp_position_centroid":[0.54067,0.09052,0.11641]}],"total_contact_groups":5},"final_pose_error":0.12551,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.52617,-0.14956,0.03221],"final_tcp_position":[0.48986,-0.17721,0.02938],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.5366,0.03695,0.025]},"peak_contact_force":72.5017,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":303.0,"n_steps_budget":600.0,"object_pos_end":[0.5366,0.03695,0.02499],"object_pos_start":[0.5366,0.03695,0.025],"object_to_goal_dist_end":0.1905,"object_to_goal_dist_start":0.1905,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1212.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach_object","tcp_end":[0.54209,0.09547,0.18521],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.17066,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":636.0,"n_steps_budget":960.0,"object_pos_end":[0.5366,0.03695,0.02499],"object_pos_start":[0.5366,0.03695,0.02499],"object_to_goal_dist_end":0.1905,"object_to_goal_dist_start":0.1905,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"descend_to_push","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2544.0,"raw_peak_contact_force":0.24525,"subtask_id":"approach_object","tcp_end":[0.54178,0.08587,0.05225],"tcp_start":[0.54209,0.09547,0.18521],"tcp_to_object_dist_end":0.05624,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52617,-0.14956,0.03221],"object_pos_start":[0.5366,0.03695,0.02499],"object_to_goal_dist_end":0.02715,"object_to_goal_dist_start":0.1905,"object_z_max":0.03324,"peak_contact_force":0.0,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2472.0,"raw_peak_contact_force":72.5017,"subtask_id":"push_progress","tcp_end":[0.48986,-0.17721,0.02938],"tcp_start":[0.54178,0.08587,0.05225],"tcp_to_object_dist_end":0.04573,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
```