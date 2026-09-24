## Search State

- **Seed**: 5
- **Iteration**: 11 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 10 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | pose_tolerance | force_exceeded | contact_lost | 5 | 0.6125 | 0.43 | ❌ rejected |
| 9 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | time_limit | 6 | 0.7273 | 0.42 | ❌ rejected |
| 8 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 5 | 0.6803 | 0.31 | ❌ rejected |
| 7 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | pose_tolerance | force_exceeded | contact_lost | 5 | 0.6092 | 0.43 | ✅ accepted |
| 6 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | pose_tolerance | time_limit | time_limit | 4 | 0.3879 | 0.40 | ❌ rejected |

**Proposal policy**: task_score is 0.43 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.613) — your mutation base

```yaml
skill: push_to_goal
dsl_version: 2
subtasks:
- id: contact_object
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.04
  weight: 0.3
- id: move_to_goal
  target_entity: object
  weight: 0.7
phases:
- id: approach_pre_contact
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
    - 0.04
    offset_along_axis:
      distance: 0.07
      axis: task_goal_direction
      mode: add_to_offset
      sign: negative
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: contact_object
- id: contact_approach
  type: contact
  generator: linear_cartesian
  control: impedance_control
  termination: force_exceeded
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.03
      axis: task_goal_direction
      mode: add_to_offset
      sign: positive
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    contact_force_threshold:
      type: scalar
      range:
      - 5.0
      - 25.0
      default: 15.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    contact_speed:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: contact_object
- id: push_to_goal
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: contact_lost
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.5
      axis: task_goal_direction
      mode: add_to_offset
      sign: positive
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.1
      - 0.8
      default: 0.5
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  retries:
    max_attempts: 1
    strategy: reduce_speed
  subtask_id: move_to_goal

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_pre_contact** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.04], offset_along_axis={axis=task_goal_direction, distance=0.07, mode=add_to_offset, sign=negative}, tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **contact_approach** (`contact`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.03, mode=add_to_offset, sign=positive}, tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - contact_force_threshold: status=consumed; consumers=termination.force_threshold (replace)
    - contact_speed: status=consumed; consumers=generator.speed (replace)
- **push_to_goal** (`push`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.5, mode=add_to_offset, sign=positive}, tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=1, strategy=reduce_speed

## Design Metrics

- **Composite score**: 0.613
- **task_score** (E): 0.432
- **fitness_score**: 0.559  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.333
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.280

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_pre_contact | 1.00 | 1.00 | 0.2476 |
| contact_approach | 1.00 | 1.00 | 0.0370 |
| push_to_goal | 0.00 | 1.00 | 0.2037 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_pre_contact | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.521, 0.086, 0.072) | (0.519, 0.022, 0.025)→(0.519, 0.022, 0.025) | 0.173→0.173 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact_approach | contact | 1.00 / force_exceeded | (0.521, 0.086, 0.072)→(0.515, 0.056, 0.052) | (0.519, 0.022, 0.025)→(0.519, 0.022, 0.025) | 0.173→0.173 | 1.00 / 5.000 | 75893.537 | 0.245 |
| push_to_goal | push | 0.00 / step_budget | (0.515, 0.056, 0.052)→(0.492, -0.146, 0.039) | (0.519, 0.022, 0.025)→(0.511, -0.051, 0.025) | 0.173→0.100 | 1.00 / 4.000 | 0.245 | 121.789 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.524
- lateral_force_integral: None
- approach_alignment: 0.745
- goal_progress: 0.524
- terminal_score: 0.524
- phase_score: 0.668
- phase_breakdown.move_to_goal_score: 0.744
- phase_breakdown.contact_object_score: 0.489

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.610
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.524
- **Median Q (composite search score)**: 0.599
- **K-run variance**: 0.0014
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.633


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `7ff7a4e3a1b03e3d7ba3d0b298d1ee8847b5344eb55f2aa0aaf582e7a98ab8ac`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.06,0.06]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `028a6956ebe09ab7c7952341570355f52da12e46fb22d3462091c70c024324ff`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.2695,"average_solve_count":141.0,"average_success_count":141.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_pre_contact.approach_speed":0.06046,"contact_approach.contact_force_threshold":18.16603,"contact_approach.contact_speed":0.04404,"push_to_goal.push_distance":0.79816,"push_to_goal.push_speed":0.06355},"optimized_scores":{"best_composite_score":0.59938,"best_fitness_score":0.54604,"best_task_score":0.40684},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":606.0,"contact_point_centroid":[0.53488,0.01768,0.04957],"force_p95":112.24362,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":117.90359,"mean_force":72.90502,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.52631,0.0145,0.05072]},{"body_a":"world","body_b":"push_box","contact_count":3052.0,"contact_point_centroid":[0.52953,-0.01033,-0.00014],"force_p95":56.41564,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":72.96875,"mean_force":14.78867,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.51459,-0.03486,0.0462]},{"body_a":"world","body_b":"push_box","contact_count":3828.0,"contact_point_centroid":[0.5366,0.03695,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_pre_contact","phase_type":"approach","tcp_position_centroid":[0.52094,0.04985,0.18378]},{"body_a":"world","body_b":"push_box","contact_count":1520.0,"contact_point_centroid":[0.5366,0.03695,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_approach","phase_type":"contact","tcp_position_centroid":[0.53821,0.08469,0.05823]}],"total_contact_groups":4},"final_pose_error":0.60881,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.52409,-0.0396,0.02499],"final_tcp_position":[0.491,-0.14731,0.03932],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.5366,0.03695,0.025]},"peak_contact_force":75893.53664,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":957.0,"n_steps_budget":1000.0,"object_pos_end":[0.5366,0.03695,0.02499],"object_pos_start":[0.5366,0.03695,0.025],"object_to_goal_dist_end":0.1905,"object_to_goal_dist_start":0.1905,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_pre_contact","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3828.0,"raw_peak_contact_force":0.24534,"subtask_id":"contact_object","tcp_end":[0.54387,0.09995,0.07039],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07799,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":380.0,"n_steps_budget":1000.0,"object_pos_end":[0.5366,0.03695,0.02499],"object_pos_start":[0.5366,0.03695,0.02499],"object_to_goal_dist_end":0.1905,"object_to_goal_dist_start":0.1905,"object_z_max":0.02499,"peak_contact_force":75893.53664,"phase_name":"contact_approach","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1520.0,"raw_peak_contact_force":0.24525,"subtask_id":"contact_object","tcp_end":[0.53588,0.07182,0.05136],"tcp_start":[0.54387,0.09995,0.07039],"tcp_to_object_dist_end":0.04372,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52409,-0.0396,0.02499],"object_pos_start":[0.5366,0.03695,0.02499],"object_to_goal_dist_end":0.113,"object_to_goal_dist_start":0.1905,"object_z_max":0.03514,"peak_contact_force":0.24525,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3658.0,"raw_peak_contact_force":117.90359,"subtask_id":"move_to_goal","tcp_end":[0.491,-0.14731,0.03932],"tcp_start":[0.53588,0.07182,0.05136],"tcp_to_object_dist_end":0.11358,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `1c6409cc6d884b90ecc3937d36e5ea87cc4ef513b6f301a9da66b4e84390f805`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.47761,"average_solve_count":134.0,"average_success_count":134.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_pre_contact.approach_speed":0.08161,"contact_approach.contact_force_threshold":13.70274,"contact_approach.contact_speed":0.02273,"push_to_goal.push_distance":0.42264,"push_to_goal.push_speed":0.09998},"optimized_scores":{"best_composite_score":0.66339,"best_fitness_score":0.61006,"best_task_score":0.52357},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":762.0,"contact_point_centroid":[0.50893,-0.04026,0.04821],"force_p95":118.2079,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":126.57045,"mean_force":79.63223,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.49987,-0.04417,0.04931]},{"body_a":"world","body_b":"push_box","contact_count":2874.0,"contact_point_centroid":[0.5042,-0.05167,-0.00022],"force_p95":72.16149,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":91.4224,"mean_force":21.44209,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.49795,-0.05853,0.04684]},{"body_a":"world","body_b":"push_box","contact_count":3024.0,"contact_point_centroid":[0.50458,-0.01881,-1e-05],"force_p95":0.24527,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_pre_contact","phase_type":"approach","tcp_position_centroid":[0.50063,0.02364,0.1865]},{"body_a":"world","body_b":"push_box","contact_count":3440.0,"contact_point_centroid":[0.50458,-0.01881,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_approach","phase_type":"contact","tcp_position_centroid":[0.49947,0.02879,0.0595]}],"total_contact_groups":4},"final_pose_error":0.29338,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50037,-0.08746,0.02499],"final_tcp_position":[0.49204,-0.14807,0.03728],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50458,-0.01881,0.025]},"peak_contact_force":75893.53664,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":756.0,"n_steps_budget":1000.0,"object_pos_end":[0.50458,-0.01881,0.02499],"object_pos_start":[0.50458,-0.01881,0.025],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_pre_contact","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3024.0,"raw_peak_contact_force":0.24534,"subtask_id":"contact_object","tcp_end":[0.50302,0.0479,0.07345],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.08246,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":860.0,"n_steps_budget":1000.0,"object_pos_end":[0.50458,-0.01881,0.02499],"object_pos_start":[0.50458,-0.01881,0.02499],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.02499,"peak_contact_force":75893.53664,"phase_name":"contact_approach","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":3440.0,"raw_peak_contact_force":0.24525,"subtask_id":"contact_object","tcp_end":[0.4993,0.01403,0.05186],"tcp_start":[0.50302,0.0479,0.07345],"tcp_to_object_dist_end":0.04276,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50037,-0.08746,0.02499],"object_pos_start":[0.50458,-0.01881,0.02499],"object_to_goal_dist_end":0.06254,"object_to_goal_dist_start":0.13127,"object_z_max":0.03533,"peak_contact_force":0.24525,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3636.0,"raw_peak_contact_force":126.57045,"subtask_id":"move_to_goal","tcp_end":[0.49204,-0.14807,0.03728],"tcp_start":[0.4993,0.01403,0.05186],"tcp_to_object_dist_end":0.0624,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `f52ec1899e2888770a8b6b3ae605718303ef4b10e72cfd7d20ce53303721b2b0`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.15476,"average_solve_count":168.0,"average_success_count":168.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_pre_contact.approach_speed":0.05039,"contact_approach.contact_force_threshold":11.08375,"contact_approach.contact_speed":0.02767,"push_to_goal.push_distance":0.79995,"push_to_goal.push_speed":0.06944},"optimized_scores":{"best_composite_score":0.57476,"best_fitness_score":0.52142,"best_task_score":0.366},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":578.0,"contact_point_centroid":[0.51694,0.02966,0.04957],"force_p95":114.57186,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":120.89405,"mean_force":73.83565,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.50821,0.02618,0.05073]},{"body_a":"world","body_b":"push_box","contact_count":3081.0,"contact_point_centroid":[0.51217,0.00127,-0.00014],"force_p95":55.31961,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":75.41136,"mean_force":14.15739,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.50195,-0.02849,0.04613]},{"body_a":"world","body_b":"push_box","contact_count":3784.0,"contact_point_centroid":[0.51501,0.04767,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_pre_contact","phase_type":"approach","tcp_position_centroid":[0.50687,0.05543,0.18402]},{"body_a":"world","body_b":"push_box","contact_count":2364.0,"contact_point_centroid":[0.51501,0.04767,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_approach","phase_type":"contact","tcp_position_centroid":[0.51155,0.09421,0.05819]}],"total_contact_groups":4},"final_pose_error":0.60993,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50925,-0.02466,0.02499],"final_tcp_position":[0.49185,-0.14138,0.03955],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.51501,0.04767,0.025]},"peak_contact_force":75893.53664,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":946.0,"n_steps_budget":1000.0,"object_pos_end":[0.51501,0.04767,0.02499],"object_pos_start":[0.51501,0.04767,0.025],"object_to_goal_dist_end":0.19823,"object_to_goal_dist_start":0.19823,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_pre_contact","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3784.0,"raw_peak_contact_force":0.24534,"subtask_id":"contact_object","tcp_end":[0.51568,0.11114,0.07091],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07835,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":591.0,"n_steps_budget":1000.0,"object_pos_end":[0.51501,0.04767,0.02499],"object_pos_start":[0.51501,0.04767,0.02499],"object_to_goal_dist_end":0.19823,"object_to_goal_dist_start":0.19823,"object_z_max":0.02499,"peak_contact_force":75893.53664,"phase_name":"contact_approach","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2364.0,"raw_peak_contact_force":0.24525,"subtask_id":"contact_object","tcp_end":[0.51082,0.08154,0.05163],"tcp_start":[0.51568,0.11114,0.07091],"tcp_to_object_dist_end":0.0433,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50925,-0.02466,0.02499],"object_pos_start":[0.51501,0.04767,0.02499],"object_to_goal_dist_end":0.12568,"object_to_goal_dist_start":0.19823,"object_z_max":0.03518,"peak_contact_force":0.24525,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3659.0,"raw_peak_contact_force":120.89405,"subtask_id":"move_to_goal","tcp_end":[0.49185,-0.14138,0.03955],"tcp_start":[0.51082,0.08154,0.05163],"tcp_to_object_dist_end":0.11891,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```