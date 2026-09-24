## Search State

- **Seed**: 9
- **Iteration**: 8 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 7 | approach → push | linear_cartesian | linear_cartesian | position_control | impedance_control | pose_tolerance | pose_tolerance | 7 | -0.2475 | 0.07 | ❌ rejected |
| 6 | approach → push | linear_cartesian | linear_cartesian | position_control | impedance_control | pose_tolerance | time_limit | 6 | 0.4207 | 0.79 | ✅ accepted |
| 5 | approach → push | linear_cartesian | linear_cartesian | position_control | impedance_control | pose_tolerance | time_limit | 7 | 0.2972 | 0.63 | ❌ rejected |
| 4 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | time_limit | 11 | -0.0215 | 0.60 | ❌ rejected |
| 3 | approach → push | linear_cartesian | linear_cartesian | position_control | impedance_control | pose_tolerance | time_limit | 6 | 0.1459 | 0.48 | ❌ rejected |

**Proposal policy**: task_score is 0.07 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.247) — your mutation base

```yaml
skill: push_to_goal
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: reach_object
  anchor: object
  weight: 0.2
- id: push_to_goal
  target_entity: object
  metric: goal_progress
  weight: 0.8
phases:
- id: approach_from_behind
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
    - 0.025
    offset_along_axis:
      distance: 0.1
      axis: task_goal_direction
      mode: replace_offset_projection
      sign: negative
    tolerance: 0.01
    orientation:
      mode: none
  parameters:
    approach_behind_distance:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    approach_speed:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
    approach_tolerance:
      type: scalar
      range:
      - 0.005
      - 0.03
      default: 0.01
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
    approach_z_offset:
      type: scalar
      range:
      - 0.0
      - 0.04
      default: 0.025
      binds_to:
      - path: target.offset.z
        mode: replace
  guards:
  - id: approach_pose_check
    when: after_phase
    predicate: pose_within_tolerance
    threshold: 0.02
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - -0.005
  subtask_id: reach_object
- id: push_to_goal_phase
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: time_limit
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.0
    orientation:
      mode: none
  parameters:
    push_speed:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
    push_time:
      type: scalar
      range:
      - 1.0
      - 10.0
      default: 5.0
      binds_to:
      - path: duration.max_time
        mode: replace
  guards:
  - id: force_limit
    when: during_phase
    predicate: force_below
    threshold: 25.0
    on_failure: abort
  subtask_id: push_to_goal

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_from_behind** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.025], offset_along_axis={axis=task_goal_direction, distance=0.1, mode=replace_offset_projection, sign=negative}, tolerance=0.01
  - orientation: mode=none
  - parameter_bindings:
    - approach_behind_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - approach_speed: status=consumed; consumers=generator.speed (replace)
    - approach_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
    - approach_z_offset: status=consumed; consumers=target.offset.z (replace)
  - guards:
    - id=approach_pose_check, when=after_phase, predicate=pose_within_tolerance, on_failure=retry, threshold=0.02
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, -0.005]
- **push_to_goal_phase** (`push`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0]
  - orientation: mode=none
  - parameter_bindings:
    - push_speed: status=consumed; consumers=generator.speed (replace)
    - push_time: status=consumed; consumers=duration.max_time (replace)
  - guards:
    - id=force_limit, when=during_phase, predicate=force_below, on_failure=abort, threshold=25.0

## Design Metrics

- **Composite score**: -0.247
- **task_score** (E): 0.066
- **fitness_score**: 0.103  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.350

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_from_behind | 1.00 | 1.00 | 0.2643 |
| push_to_goal_phase | 0.00 | 1.00 | 0.0103 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_from_behind | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.525, 0.014, 0.043) | (0.518, -0.020, 0.025)→(0.519, -0.024, 0.025) | 0.139→0.136 | 1.00 / 2.667 | 5.245 | 221.461 |
| push_to_goal_phase | push | 0.00 / guard_failure | (0.525, 0.014, 0.043)→(0.521, 0.006, 0.040) | (0.519, -0.024, 0.025)→(0.518, -0.031, 0.025) | 0.136→0.130 | 1.00 / 4.667 | 40.513 | 40.513 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.122
- lateral_force_integral: None
- approach_alignment: 0.478
- goal_progress: 0.121
- terminal_score: 0.121
- phase_score: 0.182
- phase_breakdown.reach_object_score: 0.423
- phase_breakdown.push_to_goal_score: 0.121

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.157
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.121
- **Median Q (composite search score)**: -0.265
- **K-run variance**: 0.0016
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.340


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `327b95871eb659cd41b4cf66bc0b4dfb3b240662e8501854b46ee2b8b86a04c5`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.06,0.06]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `5ffd2bb280d1d50ec9ffd23c1ed75abf73d645c1d10372a9b5bb6e9fac6e0bf8`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.90323,"average_solve_count":62.0,"average_success_count":62.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_from_behind.approach_behind_distance":0.03641,"approach_from_behind.approach_speed":0.10755,"approach_from_behind.approach_tolerance":0.0207,"approach_from_behind.approach_z_offset":0.01281,"push_to_goal_phase.push_distance":0.27844,"push_to_goal_phase.push_speed":0.08241,"push_to_goal_phase.push_tolerance":0.02744},"optimized_scores":{"best_composite_score":-0.19263,"best_fitness_score":0.15737,"best_task_score":0.12095},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":37.0,"contact_point_centroid":[0.55736,-0.00045,0.04833],"force_p95":150.0856,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":170.49155,"mean_force":118.29805,"phase_index":0.0,"phase_name":"approach_from_behind","phase_type":"approach","tcp_position_centroid":[0.55092,0.00881,0.04956]},{"body_a":"world","body_b":"push_box","contact_count":3404.0,"contact_point_centroid":[0.54474,-0.02537,-1e-05],"force_p95":0.24531,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":143.64909,"mean_force":1.54439,"phase_index":0.0,"phase_name":"approach_from_behind","phase_type":"approach","tcp_position_centroid":[0.52387,0.00405,0.17186]},{"body_a":"attachment","body_b":"push_box","contact_count":20.0,"contact_point_centroid":[0.55026,-0.00838,0.04615],"force_p95":20.19598,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":34.99511,"mean_force":5.65173,"phase_index":1.0,"phase_name":"push_to_goal_phase","phase_type":"push","tcp_position_centroid":[0.54985,0.00341,0.04468]},{"body_a":"world","body_b":"push_box","contact_count":47.0,"contact_point_centroid":[0.53522,-0.04172,-0.00029],"force_p95":11.23099,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":18.02288,"mean_force":2.95545,"phase_index":1.0,"phase_name":"push_to_goal_phase","phase_type":"push","tcp_position_centroid":[0.55058,0.00444,0.04516]}],"total_contact_groups":4},"final_pose_error":0.29934,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.54106,-0.04137,0.02455],"final_tcp_position":[0.54619,-0.00453,0.04276],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.54443,-0.02558,0.025]},"peak_contact_force":170.49155,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":861.0,"n_steps_budget":1000.0,"object_pos_end":[0.5455,-0.02593,0.02464],"object_pos_start":[0.54443,-0.02558,0.025],"object_to_goal_dist_end":0.13216,"object_to_goal_dist_start":0.13211,"object_z_max":0.025,"peak_contact_force":14.39685,"phase_name":"approach_from_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3441.0,"raw_peak_contact_force":170.49155,"subtask_id":"reach_object","tcp_end":[0.55388,0.00993,0.04731],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.04324,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":42.0,"n_steps_budget":1000.0,"object_pos_end":[0.54106,-0.04137,0.02455],"object_pos_start":[0.5455,-0.02593,0.02464],"object_to_goal_dist_end":0.11613,"object_to_goal_dist_start":0.13216,"object_z_max":0.02661,"peak_contact_force":34.99511,"phase_name":"push_to_goal_phase","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":67.0,"raw_peak_contact_force":34.99511,"subtask_id":"push_to_goal","tcp_end":[0.54619,-0.00453,0.04276],"tcp_start":[0.55388,0.00993,0.04731],"tcp_to_object_dist_end":0.04142,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `e094d2c5a71c8b89ef1fa30d7ce553b9c4ed64cd3fbca90620c3ede94e719cec`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.89286,"average_solve_count":56.0,"average_success_count":56.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_from_behind.approach_behind_distance":0.03701,"approach_from_behind.approach_speed":0.11722,"approach_from_behind.approach_tolerance":0.01901,"approach_from_behind.approach_z_offset":0.00736,"push_to_goal_phase.push_distance":0.18263,"push_to_goal_phase.push_speed":0.09432,"push_to_goal_phase.push_tolerance":0.02833},"optimized_scores":{"best_composite_score":-0.28498,"best_fitness_score":0.06502,"best_task_score":0.02827},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":48.0,"contact_point_centroid":[0.57001,-0.00992,0.0482],"force_p95":181.60558,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":209.47322,"mean_force":116.72502,"phase_index":0.0,"phase_name":"approach_from_behind","phase_type":"approach","tcp_position_centroid":[0.56363,-0.00063,0.04897]},{"body_a":"world","body_b":"push_box","contact_count":3472.0,"contact_point_centroid":[0.55515,-0.03501,-2e-05],"force_p95":0.24532,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":187.62418,"mean_force":1.87488,"phase_index":0.0,"phase_name":"approach_from_behind","phase_type":"approach","tcp_position_centroid":[0.53003,-0.00079,0.17081]},{"body_a":"attachment","body_b":"push_box","contact_count":2.0,"contact_point_centroid":[0.56219,-0.01643,0.03902],"force_p95":40.33405,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":41.33577,"mean_force":31.31866,"phase_index":1.0,"phase_name":"push_to_goal_phase","phase_type":"push","tcp_position_centroid":[0.56311,-0.00457,0.03873]},{"body_a":"world","body_b":"push_box","contact_count":58.0,"contact_point_centroid":[0.56068,-0.04474,-0.00017],"force_p95":7.66563,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":16.54926,"mean_force":1.42696,"phase_index":1.0,"phase_name":"push_to_goal_phase","phase_type":"push","tcp_position_centroid":[0.56502,-0.00199,0.03976]}],"total_contact_groups":4},"final_pose_error":0.21696,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.5593,-0.04145,0.0248],"final_tcp_position":[0.56277,-0.00514,0.03858],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55472,-0.03508,0.025]},"peak_contact_force":209.47322,"phases":[{"contact_detected":true,"contact_event_count":3.0,"n_steps":896.0,"n_steps_budget":1000.0,"object_pos_end":[0.55837,-0.04079,0.02496],"object_pos_start":[0.55472,-0.03508,0.025],"object_to_goal_dist_end":0.12383,"object_to_goal_dist_start":0.12728,"object_z_max":0.02519,"peak_contact_force":0.65449,"phase_name":"approach_from_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3520.0,"raw_peak_contact_force":209.47322,"subtask_id":"reach_object","tcp_end":[0.56725,-3e-05,0.04145],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.04486,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":19.0,"n_steps_budget":1000.0,"object_pos_end":[0.5593,-0.04145,0.0248],"object_pos_start":[0.55837,-0.04079,0.02496],"object_to_goal_dist_end":0.12369,"object_to_goal_dist_start":0.12383,"object_z_max":0.02496,"peak_contact_force":41.33577,"phase_name":"push_to_goal_phase","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":60.0,"raw_peak_contact_force":41.33577,"subtask_id":"push_to_goal","tcp_end":[0.56277,-0.00514,0.03858],"tcp_start":[0.56725,-3e-05,0.04145],"tcp_to_object_dist_end":0.039,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `0fd7d18e656259f06515eb57b82afa0c0febd9395a43c1a5f926ddaec3767c64`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.90625,"average_solve_count":64.0,"average_success_count":64.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_from_behind.approach_behind_distance":0.03243,"approach_from_behind.approach_speed":0.1009,"approach_from_behind.approach_tolerance":0.01566,"approach_from_behind.approach_z_offset":0.00256,"push_to_goal_phase.push_distance":0.26465,"push_to_goal_phase.push_speed":0.09944,"push_to_goal_phase.push_tolerance":0.0156},"optimized_scores":{"best_composite_score":-0.26479,"best_fitness_score":0.08521,"best_task_score":0.04824},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":104.0,"contact_point_centroid":[0.46146,0.02571,0.04625],"force_p95":275.89241,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":284.41962,"mean_force":213.12658,"phase_index":0.0,"phase_name":"approach_from_behind","phase_type":"approach","tcp_position_centroid":[0.45265,0.03011,0.04973]},{"body_a":"world","body_b":"push_box","contact_count":3415.0,"contact_point_centroid":[0.45608,0.00047,-6e-05],"force_p95":56.21203,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":204.34906,"mean_force":6.76951,"phase_index":0.0,"phase_name":"approach_from_behind","phase_type":"approach","tcp_position_centroid":[0.47184,0.01497,0.16547]},{"body_a":"attachment","body_b":"push_box","contact_count":1.0,"contact_point_centroid":[0.45314,0.01582,0.03888],"force_p95":45.20746,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":45.20746,"mean_force":45.20746,"phase_index":1.0,"phase_name":"push_to_goal_phase","phase_type":"push","tcp_position_centroid":[0.45339,0.02773,0.03857]},{"body_a":"world","body_b":"push_box","contact_count":15.0,"contact_point_centroid":[0.45027,-0.02895,-0.00025],"force_p95":18.92203,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":19.94447,"mean_force":3.87093,"phase_index":1.0,"phase_name":"push_to_goal_phase","phase_type":"push","tcp_position_centroid":[0.45325,0.02976,0.0392]}],"total_contact_groups":4},"final_pose_error":0.29663,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.45244,-0.00895,0.02458],"final_tcp_position":[0.45348,0.02735,0.03851],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.45543,-9e-05,0.025]},"peak_contact_force":284.41962,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":884.0,"n_steps_budget":1000.0,"object_pos_end":[0.45368,-0.00563,0.02661],"object_pos_start":[0.45543,-9e-05,0.025],"object_to_goal_dist_end":0.15163,"object_to_goal_dist_start":0.1564,"object_z_max":0.02643,"peak_contact_force":0.68254,"phase_name":"approach_from_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3519.0,"raw_peak_contact_force":284.41962,"subtask_id":"reach_object","tcp_end":[0.45356,0.03337,0.04095],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.04155,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":20.0,"n_steps_budget":1000.0,"object_pos_end":[0.45244,-0.00895,0.02458],"object_pos_start":[0.45368,-0.00563,0.02661],"object_to_goal_dist_end":0.14885,"object_to_goal_dist_start":0.15163,"object_z_max":0.02718,"peak_contact_force":45.20746,"phase_name":"push_to_goal_phase","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":16.0,"raw_peak_contact_force":45.20746,"subtask_id":"push_to_goal","tcp_end":[0.45348,0.02735,0.03851],"tcp_start":[0.45356,0.03337,0.04095],"tcp_to_object_dist_end":0.03889,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```