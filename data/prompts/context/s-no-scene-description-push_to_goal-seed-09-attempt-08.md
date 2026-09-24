## Search State

- **Seed**: 9
- **Iteration**: 9 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 8 | approach → push | linear_cartesian | linear_cartesian | position_control | impedance_control | pose_tolerance | time_limit | 6 | 0.3855 | 0.75 | ❌ rejected |
| 7 | approach → push | linear_cartesian | linear_cartesian | position_control | impedance_control | pose_tolerance | pose_tolerance | 7 | -0.2475 | 0.07 | ❌ rejected |
| 6 | approach → push | linear_cartesian | linear_cartesian | position_control | impedance_control | pose_tolerance | time_limit | 6 | 0.4207 | 0.79 | ✅ accepted |
| 5 | approach → push | linear_cartesian | linear_cartesian | position_control | impedance_control | pose_tolerance | time_limit | 7 | 0.2972 | 0.63 | ❌ rejected |
| 4 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | time_limit | 11 | -0.0215 | 0.60 | ❌ rejected |

**Proposal policy**: task_score is 0.75 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.386) — your mutation base

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

- **Composite score**: 0.386
- **task_score** (E): 0.746
- **fitness_score**: 0.686  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.300

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_from_behind | 1.00 | 1.00 | 0.1824 |
| push_to_goal_phase | 0.67 | 1.00 | 0.1387 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_from_behind | approach | 1.00 / step_budget | (0.528, 0.017, 0.220)→(0.529, 0.046, 0.045) | (0.518, -0.020, 0.025)→(0.518, -0.020, 0.025) | 0.139→0.139 | 1.00 / 4.000 | 0.245 | 0.245 |
| push_to_goal_phase | push | 0.67 / time_limit | (0.529, 0.046, 0.045)→(0.498, -0.082, 0.028) | (0.518, -0.020, 0.025)→(0.502, -0.117, 0.026) | 0.139→0.037 | 1.00 / 2.667 | 10.897 | 25.252 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.877
- lateral_force_integral: None
- approach_alignment: 0.641
- goal_progress: 0.875
- terminal_score: 0.875
- phase_score: 0.729
- phase_breakdown.reach_object_score: 0.143
- phase_breakdown.push_to_goal_score: 0.875

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.787
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.875
- **Median Q (composite search score)**: 0.471
- **K-run variance**: 0.0176
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.265


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.17219,"average_solve_count":151.0,"average_success_count":151.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_from_behind.approach_behind_distance":0.06417,"approach_from_behind.approach_speed":0.03944,"approach_from_behind.approach_tolerance":0.02258,"approach_from_behind.approach_z_offset":0.01696,"push_to_goal_phase.push_speed":0.10202,"push_to_goal_phase.push_time":6.69766},"optimized_scores":{"best_composite_score":0.47082,"best_fitness_score":0.77082,"best_task_score":0.83842},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":539.0,"contact_point_centroid":[0.53116,-0.05712,0.03732],"force_p95":20.56723,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":28.15079,"mean_force":6.3474,"phase_index":1.0,"phase_name":"push_to_goal_phase","phase_type":"push","tcp_position_centroid":[0.52932,-0.0452,0.03297]},{"body_a":"world","body_b":"push_box","contact_count":1881.0,"contact_point_centroid":[0.53288,-0.06697,-5e-05],"force_p95":8.23693,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":16.3758,"mean_force":2.12103,"phase_index":1.0,"phase_name":"push_to_goal_phase","phase_type":"push","tcp_position_centroid":[0.53691,-0.02273,0.03621]},{"body_a":"world","body_b":"push_box","contact_count":3828.0,"contact_point_centroid":[0.54443,-0.02558,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_from_behind","phase_type":"approach","tcp_position_centroid":[0.5282,0.0163,0.17341]}],"total_contact_groups":3},"final_pose_error":0.05206,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.51595,-0.13581,0.02492],"final_tcp_position":[0.51189,-0.09933,0.02623],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.54443,-0.02558,0.025]},"peak_contact_force":28.15079,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":957.0,"n_steps_budget":1000.0,"object_pos_end":[0.54443,-0.02558,0.02499],"object_pos_start":[0.54443,-0.02558,0.025],"object_to_goal_dist_end":0.13211,"object_to_goal_dist_start":0.13211,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_from_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3828.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_object","tcp_end":[0.55869,0.03287,0.04831],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.06453,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":843.0,"n_steps_budget":1000.0,"object_pos_end":[0.51595,-0.13581,0.02492],"object_pos_start":[0.54443,-0.02558,0.02499],"object_to_goal_dist_end":0.02135,"object_to_goal_dist_start":0.13211,"object_z_max":0.02535,"peak_contact_force":28.15079,"phase_name":"push_to_goal_phase","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2420.0,"raw_peak_contact_force":28.15079,"subtask_id":"push_to_goal","tcp_end":[0.51189,-0.09933,0.02623],"tcp_start":[0.55869,0.03287,0.04831],"tcp_to_object_dist_end":0.03673,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `e094d2c5a71c8b89ef1fa30d7ce553b9c4ed64cd3fbca90620c3ede94e719cec`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.16568,"average_solve_count":169.0,"average_success_count":169.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_from_behind.approach_behind_distance":0.10243,"approach_from_behind.approach_speed":0.02533,"approach_from_behind.approach_tolerance":0.00746,"approach_from_behind.approach_z_offset":0.01293,"push_to_goal_phase.push_speed":0.10424,"push_to_goal_phase.push_time":4.07954},"optimized_scores":{"best_composite_score":0.48741,"best_fitness_score":0.78741,"best_task_score":0.87523},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":509.0,"contact_point_centroid":[0.53885,-0.05976,0.02564],"force_p95":17.86768,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":22.72886,"mean_force":4.77414,"phase_index":1.0,"phase_name":"push_to_goal_phase","phase_type":"push","tcp_position_centroid":[0.54025,-0.04794,0.02502]},{"body_a":"world","body_b":"push_box","contact_count":2597.0,"contact_point_centroid":[0.54285,-0.06077,-3e-05],"force_p95":5.56121,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.13798,"mean_force":1.2121,"phase_index":1.0,"phase_name":"push_to_goal_phase","phase_type":"push","tcp_position_centroid":[0.55815,-0.00797,0.02731]},{"body_a":"world","body_b":"push_box","contact_count":4380.0,"contact_point_centroid":[0.55472,-0.03508,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_from_behind","phase_type":"approach","tcp_position_centroid":[0.54498,0.02776,0.16685]}],"total_contact_groups":3},"final_pose_error":0.05209,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50893,-0.13687,0.02516],"final_tcp_position":[0.51698,-0.10082,0.02241],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55472,-0.03508,0.025]},"peak_contact_force":22.72886,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1095.0,"n_steps_budget":1000.0,"object_pos_end":[0.55472,-0.03508,0.02499],"object_pos_start":[0.55472,-0.03508,0.025],"object_to_goal_dist_end":0.12728,"object_to_goal_dist_start":0.12728,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_from_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4380.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_object","tcp_end":[0.58985,0.05474,0.0363],"tcp_start":[0.58423,0.05094,0.05913],"tcp_to_object_dist_end":0.09711,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50893,-0.13687,0.02516],"object_pos_start":[0.55472,-0.03508,0.02499],"object_to_goal_dist_end":0.01588,"object_to_goal_dist_start":0.12728,"object_z_max":0.02527,"peak_contact_force":0.0,"phase_name":"push_to_goal_phase","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3106.0,"raw_peak_contact_force":22.72886,"subtask_id":"push_to_goal","tcp_end":[0.51698,-0.10082,0.02241],"tcp_start":[0.58985,0.05474,0.0363],"tcp_to_object_dist_end":0.03704,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `0fd7d18e656259f06515eb57b82afa0c0febd9395a43c1a5f926ddaec3767c64`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.77477,"average_solve_count":111.0,"average_success_count":111.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_from_behind.approach_behind_distance":0.05727,"approach_from_behind.approach_speed":0.07408,"approach_from_behind.approach_tolerance":0.02039,"approach_from_behind.approach_z_offset":0.01661,"push_to_goal_phase.push_speed":0.06309,"push_to_goal_phase.push_time":6.60555},"optimized_scores":{"best_composite_score":0.19839,"best_fitness_score":0.49839,"best_task_score":0.52545},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":697.0,"contact_point_centroid":[0.46085,-0.017,0.04897],"force_p95":14.81722,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":24.87746,"mean_force":6.33555,"phase_index":1.0,"phase_name":"push_to_goal_phase","phase_type":"push","tcp_position_centroid":[0.45228,-0.0054,0.03956]},{"body_a":"world","body_b":"push_box","contact_count":1860.0,"contact_point_centroid":[0.46673,-0.03684,-4e-05],"force_p95":7.94718,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":17.34067,"mean_force":2.77237,"phase_index":1.0,"phase_name":"push_to_goal_phase","phase_type":"push","tcp_position_centroid":[0.4466,0.01409,0.04246]},{"body_a":"world","body_b":"push_box","contact_count":3336.0,"contact_point_centroid":[0.45543,-9e-05,-1e-05],"force_p95":0.24527,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_from_behind","phase_type":"approach","tcp_position_centroid":[0.46866,0.02554,0.17494]}],"total_contact_groups":3},"final_pose_error":0.11094,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.48117,-0.07834,0.02929],"final_tcp_position":[0.46436,-0.04534,0.03412],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.45543,-9e-05,0.025]},"peak_contact_force":24.87746,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":834.0,"n_steps_budget":1000.0,"object_pos_end":[0.45543,-9e-05,0.02499],"object_pos_start":[0.45543,-9e-05,0.025],"object_to_goal_dist_end":0.1564,"object_to_goal_dist_start":0.1564,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_from_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3336.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_object","tcp_end":[0.43859,0.05158,0.05092],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.06021,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.48117,-0.07834,0.02929],"object_pos_start":[0.45543,-9e-05,0.02499],"object_to_goal_dist_end":0.07422,"object_to_goal_dist_start":0.1564,"object_z_max":0.0293,"peak_contact_force":4.53967,"phase_name":"push_to_goal_phase","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2557.0,"raw_peak_contact_force":24.87746,"subtask_id":"push_to_goal","tcp_end":[0.46436,-0.04534,0.03412],"tcp_start":[0.43859,0.05158,0.05092],"tcp_to_object_dist_end":0.03735,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
```