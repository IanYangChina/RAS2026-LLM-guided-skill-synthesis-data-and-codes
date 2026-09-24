## Search State

- **Seed**: 8
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | approach → approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 7 | 0.5538 | 0.77 | ❌ rejected |
| 11 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | time_limit | 6 | 0.5100 | 0.77 | ✅ accepted |
| 10 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | time_limit | 6 | 0.4114 | 0.77 | ✅ accepted |
| 9 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | time_limit | 6 | 0.4401 | 0.73 | ✅ accepted |
| 8 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | time_limit | 6 | 0.7008 | 0.57 | ❌ rejected |

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

## Current Skill (Q=0.554) — your mutation base

```yaml
skill: push_to_goal
dsl_version: 2
subtasks:
- id: reach_object
  anchor: object
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
    - 0.0
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
  retries:
    max_attempts: 1
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - -0.01
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
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.15, mode=replace_offset_projection, sign=negative}
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
- **contact_1** (`contact`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.15, mode=replace_offset_projection, sign=positive}
  - parameter_bindings:
    - force_threshold: status=consumed; consumers=termination.force_threshold (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=1, strategy=offset_target, offset=[0.0, 0.0, -0.01]
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

- **Composite score**: 0.554
- **task_score** (E): 0.768
- **fitness_score**: 0.631  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.333
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.410

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.3099 |
| align_1 | 1.00 | 1.00 | 0.0822 |
| contact_1 | 1.00 | 1.00 | 0.0143 |
| push_1 | 1.00 | 1.00 | 0.1838 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.552, 0.132, 0.036) | (0.526, -0.001, 0.025)→(0.526, -0.001, 0.025) | 0.156→0.156 | 1.00 / 4.000 | 0.245 | 0.245 |
| align_1 | approach | 1.00 / step_budget | (0.552, 0.132, 0.036)→(0.534, 0.055, 0.020) | (0.526, -0.001, 0.025)→(0.526, -0.001, 0.025) | 0.156→0.156 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact_1 | contact | 1.00 / force_exceeded | (0.534, 0.055, 0.020)→(0.527, 0.043, 0.016) | (0.526, -0.001, 0.025)→(0.526, -0.001, 0.025) | 0.156→0.156 | 1.00 / 5.000 | 25310.531 | 0.245 |
| push_1 | push | 1.00 / time_limit | (0.527, 0.043, 0.016)→(0.498, -0.133, 0.014) | (0.526, -0.001, 0.025)→(0.476, -0.129, 0.025) | 0.156→0.044 | 1.00 / 4.000 | 38.820 | 71.760 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 1.000
- lateral_force_integral: None
- approach_alignment: 0.684
- goal_progress: 0.923
- terminal_score: 0.923
- phase_score: 0.484
- phase_breakdown.reach_object_score: 0.316
- phase_breakdown.push_to_goal_score: 0.556

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.660
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.923
- **Median Q (composite search score)**: 0.579
- **K-run variance**: 0.0015
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.379


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.75,"average_solve_count":76.0,"average_success_count":76.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.speed":0.24394,"approach_1.speed":0.39254,"contact_1.force_threshold":8.16497,"contact_1.speed":0.07754,"push_1.max_time":1.50533,"push_1.push_distance":0.27742,"push_1.push_speed":0.17389},"optimized_scores":{"best_composite_score":0.49949,"best_fitness_score":0.57616,"best_task_score":0.49259},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":187.0,"contact_point_centroid":[0.50115,0.07098,0.04971],"force_p95":64.16745,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":73.11753,"mean_force":40.58285,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4697,0.09404,0.0195]},{"body_a":"world","body_b":"push_box","contact_count":2638.0,"contact_point_centroid":[0.45064,-0.03135,-5e-05],"force_p95":17.93994,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":49.88031,"mean_force":3.80083,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47979,-0.03088,0.01692]},{"body_a":"attachment","body_b":"push_box","contact_count":263.0,"contact_point_centroid":[0.4742,0.01856,0.02109],"force_p95":27.98187,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":47.82898,"mean_force":7.01125,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47359,0.02999,0.0169]},{"body_a":"world","body_b":"push_box","contact_count":2268.0,"contact_point_centroid":[0.47924,0.05847,-1e-05],"force_p95":0.24528,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48206,0.09168,0.17387]},{"body_a":"world","body_b":"push_box","contact_count":1432.0,"contact_point_centroid":[0.47924,0.05847,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"align_1","phase_type":"approach","tcp_position_centroid":[0.46478,0.15428,0.02796]},{"body_a":"world","body_b":"push_box","contact_count":48.0,"contact_point_centroid":[0.47924,0.05847,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.46892,0.11535,0.02132]}],"total_contact_groups":6},"final_pose_error":0.01383,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.43597,-0.06514,0.02499],"final_tcp_position":[0.49079,-0.14988,0.01573],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47924,0.05847,0.025]},"peak_contact_force":75893.53664,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":567.0,"n_steps_budget":600.0,"object_pos_end":[0.47924,0.05847,0.02499],"object_pos_start":[0.47924,0.05847,0.025],"object_to_goal_dist_end":0.2095,"object_to_goal_dist_start":0.2095,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2268.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_object","tcp_end":[0.46365,0.19312,0.03802],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.13617,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":358.0,"n_steps_budget":600.0,"object_pos_end":[0.47924,0.05847,0.02499],"object_pos_start":[0.47924,0.05847,0.02499],"object_to_goal_dist_end":0.2095,"object_to_goal_dist_start":0.2095,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1432.0,"raw_peak_contact_force":0.24525,"subtask_id":"reach_object","tcp_end":[0.46913,0.11611,0.02169],"tcp_start":[0.46365,0.19312,0.03802],"tcp_to_object_dist_end":0.05861,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":12.0,"n_steps_budget":660.0,"object_pos_end":[0.47924,0.05847,0.02499],"object_pos_start":[0.47924,0.05847,0.02499],"object_to_goal_dist_end":0.2095,"object_to_goal_dist_start":0.2095,"object_z_max":0.02499,"peak_contact_force":75893.53664,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":48.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.46855,0.11445,0.02082],"tcp_start":[0.46913,0.11611,0.02169],"tcp_to_object_dist_end":0.05714,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":961.0,"n_steps_budget":990.0,"object_pos_end":[0.43597,-0.06514,0.02499],"object_pos_start":[0.47924,0.05847,0.02499],"object_to_goal_dist_end":0.10631,"object_to_goal_dist_start":0.2095,"object_z_max":0.0257,"peak_contact_force":0.24525,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3088.0,"raw_peak_contact_force":73.11753,"subtask_id":"push_to_goal","tcp_end":[0.49079,-0.14988,0.01573],"tcp_start":[0.46855,0.11445,0.02082],"tcp_to_object_dist_end":0.10135,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `021f3e69028f16fb65e79b302b37775f7324e143e034cbac30fdb04ffcd99d24`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.11765,"average_solve_count":85.0,"average_success_count":85.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.speed":0.38896,"approach_1.speed":0.30935,"contact_1.force_threshold":6.69849,"contact_1.speed":0.08751,"push_1.max_time":1.81024,"push_1.push_distance":0.40964,"push_1.push_speed":0.09296},"optimized_scores":{"best_composite_score":0.583,"best_fitness_score":0.65967,"best_task_score":0.92346},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":1000.0,"contact_point_centroid":[0.54731,-0.07364,0.05054],"force_p95":72.30026,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":76.19038,"mean_force":62.57894,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52618,-0.05051,0.01484]},{"body_a":"world","body_b":"push_box","contact_count":2131.0,"contact_point_centroid":[0.52961,-0.10298,-0.00016],"force_p95":51.92191,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":73.5993,"mean_force":35.93114,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52758,-0.04649,0.01477]},{"body_a":"attachment","body_b":"push_box","contact_count":960.0,"contact_point_centroid":[0.5414,-0.06421,0.04963],"force_p95":49.78228,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":57.1316,"mean_force":42.52523,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52526,-0.05311,0.01488]},{"body_a":"world","body_b":"push_box","contact_count":2480.0,"contact_point_centroid":[0.54443,-0.02558,-1e-05],"force_p95":0.24528,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.54053,0.0519,0.17111]},{"body_a":"world","body_b":"push_box","contact_count":1480.0,"contact_point_centroid":[0.54443,-0.02558,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"align_1","phase_type":"approach","tcp_position_centroid":[0.57041,0.06852,0.02484]},{"body_a":"world","body_b":"push_box","contact_count":520.0,"contact_point_centroid":[0.54443,-0.02558,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.55346,0.02194,0.01613]}],"total_contact_groups":6},"final_pose_error":0.26546,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.49903,-0.16002,0.02597],"final_tcp_position":[0.50172,-0.12241,0.01503],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.54443,-0.02558,0.025]},"peak_contact_force":76.19038,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":620.0,"n_steps_budget":660.0,"object_pos_end":[0.54443,-0.02558,0.02499],"object_pos_start":[0.54443,-0.02558,0.025],"object_to_goal_dist_end":0.13211,"object_to_goal_dist_start":0.13211,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2480.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_object","tcp_end":[0.58539,0.10802,0.035],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.1401,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":370.0,"n_steps_budget":600.0,"object_pos_end":[0.54443,-0.02558,0.02499],"object_pos_start":[0.54443,-0.02558,0.02499],"object_to_goal_dist_end":0.13211,"object_to_goal_dist_start":0.13211,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1480.0,"raw_peak_contact_force":0.24525,"subtask_id":"reach_object","tcp_end":[0.55914,0.02982,0.01992],"tcp_start":[0.58539,0.10802,0.035],"tcp_to_object_dist_end":0.05754,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":130.0,"n_steps_budget":600.0,"object_pos_end":[0.54443,-0.02558,0.02499],"object_pos_start":[0.54443,-0.02558,0.02499],"object_to_goal_dist_end":0.13211,"object_to_goal_dist_start":0.13211,"object_z_max":0.02499,"peak_contact_force":18.45957,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":520.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.54914,0.01375,0.01444],"tcp_start":[0.55914,0.02982,0.01992],"tcp_to_object_dist_end":0.04099,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49903,-0.16002,0.02597],"object_pos_start":[0.54443,-0.02558,0.02499],"object_to_goal_dist_end":0.01011,"object_to_goal_dist_start":0.13211,"object_z_max":0.02624,"peak_contact_force":66.07525,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":4091.0,"raw_peak_contact_force":76.19038,"subtask_id":"push_to_goal","tcp_end":[0.50172,-0.12241,0.01503],"tcp_start":[0.54914,0.01375,0.01444],"tcp_to_object_dist_end":0.03926,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `886824c4c8b8334954c1de9b3100fb0acfdd4a04855e7e82a07b72c52723cc86`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.12644,"average_solve_count":87.0,"average_success_count":87.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.speed":0.26862,"approach_1.speed":0.30863,"contact_1.force_threshold":1.38805,"contact_1.speed":0.05715,"push_1.max_time":1.60834,"push_1.push_distance":0.36422,"push_1.push_speed":0.08965},"optimized_scores":{"best_composite_score":0.57906,"best_fitness_score":0.65572,"best_task_score":0.88919},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":993.0,"contact_point_centroid":[0.55058,-0.08307,0.04961],"force_p95":57.96923,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":65.9728,"mean_force":49.41332,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.53214,-0.05901,0.01286]},{"body_a":"world","body_b":"push_box","contact_count":2282.0,"contact_point_centroid":[0.5292,-0.11096,-8e-05],"force_p95":41.917,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":59.2688,"mean_force":25.82548,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.53191,-0.05955,0.01281]},{"body_a":"attachment","body_b":"push_box","contact_count":994.0,"contact_point_centroid":[0.5454,-0.07023,0.0451],"force_p95":37.08237,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":46.11251,"mean_force":30.29234,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.53217,-0.05895,0.01286]},{"body_a":"world","body_b":"push_box","contact_count":2480.0,"contact_point_centroid":[0.55472,-0.03508,-1e-05],"force_p95":0.24528,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.55165,0.04508,0.17084]},{"body_a":"world","body_b":"push_box","contact_count":1460.0,"contact_point_centroid":[0.55472,-0.03508,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"align_1","phase_type":"approach","tcp_position_centroid":[0.58965,0.05569,0.02426]},{"body_a":"world","body_b":"push_box","contact_count":716.0,"contact_point_centroid":[0.55472,-0.03508,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.56752,0.0098,0.01509]}],"total_contact_groups":6},"final_pose_error":0.2223,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.49197,-0.1616,0.02511],"final_tcp_position":[0.50043,-0.12574,0.01226],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55472,-0.03508,0.025]},"peak_contact_force":65.9728,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":620.0,"n_steps_budget":660.0,"object_pos_end":[0.55472,-0.03508,0.02499],"object_pos_start":[0.55472,-0.03508,0.025],"object_to_goal_dist_end":0.12728,"object_to_goal_dist_start":0.12728,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2480.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_object","tcp_end":[0.60819,0.09373,0.03448],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.13979,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":365.0,"n_steps_budget":600.0,"object_pos_end":[0.55472,-0.03508,0.02499],"object_pos_start":[0.55472,-0.03508,0.02499],"object_to_goal_dist_end":0.12728,"object_to_goal_dist_start":0.12728,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1460.0,"raw_peak_contact_force":0.24525,"subtask_id":"reach_object","tcp_end":[0.57487,0.01825,0.01958],"tcp_start":[0.60819,0.09373,0.03448],"tcp_to_object_dist_end":0.05726,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":179.0,"n_steps_budget":870.0,"object_pos_end":[0.55472,-0.03508,0.02499],"object_pos_start":[0.55472,-0.03508,0.02499],"object_to_goal_dist_end":0.12728,"object_to_goal_dist_start":0.12728,"object_z_max":0.02499,"peak_contact_force":19.59796,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":716.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.56256,0.00187,0.01362],"tcp_start":[0.57487,0.01825,0.01958],"tcp_to_object_dist_end":0.03944,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49197,-0.1616,0.02511],"object_pos_start":[0.55472,-0.03508,0.02499],"object_to_goal_dist_end":0.0141,"object_to_goal_dist_start":0.12728,"object_z_max":0.02538,"peak_contact_force":50.14013,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":4269.0,"raw_peak_contact_force":65.9728,"subtask_id":"push_to_goal","tcp_end":[0.50043,-0.12574,0.01226],"tcp_start":[0.56256,0.00187,0.01362],"tcp_to_object_dist_end":0.03901,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
```