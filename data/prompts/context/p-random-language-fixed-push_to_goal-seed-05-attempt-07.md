## Search State

- **Seed**: 5
- **Iteration**: 8 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 7 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | time_limit | 5 | 0.7838 | 0.66 | ✅ accepted |
| 6 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | time_limit | 5 | 0.6178 | 0.47 | ✅ accepted |
| 5 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | position_control | pose_tolerance | force_exceeded | force_exceeded | 5 | 0.6188 | 0.23 | ❌ rejected |
| 4 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | position_control | pose_tolerance | force_exceeded | force_exceeded | 5 | 0.6317 | 0.28 | ✅ accepted |
| 3 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | time_limit | 4 | 0.4640 | 0.18 | ✅ accepted |

**Proposal policy**: task_score is 0.66 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `b2a76c5d1121259d09d3db2c62740fd8fe93dd873d8f379ba1928ff319a7d266`
- Frozen object start: [0.5366003508494456, 0.03695289476837925, 0.025]
- Frozen task target: [0.5, -0.15, 0.025]
- Goal object position: (0.5, -0.15, 0.025)
- Object initial pose: (0.5366003508494456, 0.03695289476837925, 0.025)
- Goal tolerance: 0.02 m
- Expressivity sigma: 1.0 m
- Expressivity threshold: 0.8
- Force limit: 25.0 N
- Robot initial TCP position: (0.5, 0.0, 0.3)
- Phase navigation guidance: the task `phase_target_map` may provide internal predefined TCP waypoint aliases / semantic phase ids. These names are not DSL phase types and are intentionally not enumerated here to avoid confusing ids with types. Phase `id` may be semantic, but phase `type` must be exactly one of the DSL enum values listed in the prompt.
- Primary evaluation target: **object displacement ratio toward goal_object_position**

## Scene Entities

robot:
  model: panda_pusher
  tcp_site: attachment_site
  gripper: null
  tcp_initial_world: [0.5, 0, 0.3]
objects:
  - name: push_box
    role: manipulated_object
    dynamics: free
    geometry: box
    dimensions_m: [0.05, 0.05, 0.05]
    mass_kg: 0.1
  - name: goal_marker
    role: target_marker
    dynamics: static
    geometry: point
task_landmarks:
  frozen_object_start: [0.5366, 0.037, 0.025]
  frozen_task_target: [0.5, -0.15, 0.025]
  frozen_object_starts: {'push_box': [0.5366003508494456, 0.03695289476837925, 0.025]}
  frozen_targets: {'task_goal': [0.5, -0.15, 0.025]}
  push_direction: [-0.0366, -0.187, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 25
  force_scale_n: 5
  realized_scene_sha256: b2a76c5d1121259d09d3db2c62740fd8fe93dd873d8f379ba1928ff319a7d266

## Subtask Layer

**Mode**: fixed (subtask targets are defined by the task configuration)

Available subtask IDs for phase binding:
| Subtask ID | Anchor | Target offset (m) | Metric | CMA-ES offset param |
|---|---|---|---|---|
| approach | object | (0.00, 0.08, 0.00) | distance | — |
| contact | object | (0.00, 0.03, 0.00) | distance | — |
| push | goal | (0.00, 0.03, 0.00) | distance | push_depth |

Annotate phases with `subtask_id: <id>` to bind them to a subtask target.
- A phase bound to a subtask receives a navigation waypoint computed from that subtask's anchor and offset.
- Only the **last phase** bound to a given subtask is used for subtask scoring.
- Phases without `subtask_id` are not scored against subtasks but still execute normally.

## Current Skill (Q=0.784) — your mutation base

```yaml
skill: push_to_goal
dsl_version: 2
subtasks:
- id: approach
  anchor: object
  offset:
  - 0.0
  - 0.08
  - 0.0
  weight: 0.0
- id: contact
  anchor: object
  offset:
  - 0.0
  - 0.03
  - 0.0
  weight: 0.0
- id: push
  target_entity: object
  metric: goal_progress
  offset:
  - 0.0
  - 0.03
  - 0.0
  weight: 0.0
phases:
- id: approach
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
      distance: 0.1
      axis: task_goal_direction
      mode: add_to_offset
      sign: negative
    tolerance: 0.01
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
- id: contact
  type: contact
  generator: linear_cartesian
  control: force_threshold_switch
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
      sign: negative
  parameters:
    contact_force_threshold:
      type: scalar
      range:
      - 1.0
      - 15.0
      default: 6.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
  guards:
  - id: contact_force_guard
    when: during_phase
    predicate: force_below
    threshold: 30.0
    on_failure: abort
- id: push
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: time_limit
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.03
    - 0.0
    offset_along_axis:
      distance: 0.25
      axis: task_goal_direction
      mode: add_to_offset
      sign: positive
  parameters:
    push_depth:
      type: scalar
      range:
      - 0.05
      - 0.5
      default: 0.25
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.04
      binds_to:
      - path: generator.speed
        mode: replace
    push_timeout:
      type: scalar
      range:
      - 0.5
      - 10.0
      default: 5.0
      binds_to:
      - path: duration.max_time
        mode: replace
  guards:
  - id: push_force_guard
    when: during_phase
    predicate: force_below
    threshold: 30.0
    on_failure: abort
  retries:
    max_attempts: 2
    strategy: reduce_speed
  subtask_id: push

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.1, mode=add_to_offset, sign=negative}, tolerance=0.01
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **contact** (`contact`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.03, mode=add_to_offset, sign=negative}
  - parameter_bindings:
    - contact_force_threshold: status=consumed; consumers=termination.force_threshold (replace)
  - guards:
    - id=contact_force_guard, when=during_phase, predicate=force_below, on_failure=abort, threshold=30.0
- **push** (`push`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.03, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.25, mode=add_to_offset, sign=positive}
  - parameter_bindings:
    - push_depth: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
    - push_timeout: status=consumed; consumers=duration.max_time (replace)
  - guards:
    - id=push_force_guard, when=during_phase, predicate=force_below, on_failure=abort, threshold=30.0
  - retries: max_attempts=2, strategy=reduce_speed

## Design Metrics

- **Composite score**: 0.784
- **task_score** (E): 0.665
- **fitness_score**: 0.619  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.444
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.280

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach | 1.00 | 1.00 | 0.2772 |
| contact | 1.00 | 1.00 | 0.0555 |
| push | 0.67 | 1.00 | 0.1287 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.522, 0.107, 0.048) | (0.519, 0.022, 0.025)→(0.519, 0.022, 0.025) | 0.173→0.173 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact | contact | 1.00 / force_exceeded | (0.522, 0.107, 0.048)→(0.517, 0.059, 0.023) | (0.519, 0.022, 0.025)→(0.519, 0.022, 0.025) | 0.173→0.173 | 1.00 / 5.000 | 20.957 | 0.245 |
| push | push | 0.67 / time_limit | (0.517, 0.059, 0.023)→(0.497, -0.068, 0.019) | (0.519, 0.022, 0.025)→(0.502, -0.105, 0.025) | 0.173→0.045 | 1.00 / 2.667 | 5.393 | 30.845 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.964
- lateral_force_integral: None
- approach_alignment: 0.673
- goal_progress: 0.964
- terminal_score: 0.964
- phase_score: 0.694
- phase_breakdown.approach_score: 0.612
- phase_breakdown.contact_score: 0.781
- phase_breakdown.push_score: 0.674

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.802
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.967
- **Median Q (composite search score)**: 1.008
- **K-run variance**: 0.1066
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.415


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `7ff7a4e3a1b03e3d7ba3d0b298d1ee8847b5344eb55f2aa0aaf582e7a98ab8ac`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.06,0.06]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `028a6956ebe09ab7c7952341570355f52da12e46fb22d3462091c70c024324ff`; realized-scene SHA-256: `b2a76c5d1121259d09d3db2c62740fd8fe93dd873d8f379ba1928ff319a7d266`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5366,0.03695,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.0366,-0.18695,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.5366,0.03695,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.83065,"average_solve_count":124.0,"average_success_count":124.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_speed":0.08706,"contact.contact_force_threshold":5.04051,"push.push_depth":0.4752,"push.push_speed":0.05646,"push.push_timeout":4.67038},"optimized_scores":{"best_composite_score":1.02178,"best_fitness_score":0.80178,"best_task_score":0.96416},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":866.0,"contact_point_centroid":[0.52159,-0.02615,0.02846],"force_p95":19.47648,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":29.22864,"mean_force":4.64204,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.51703,-0.01429,0.01814]},{"body_a":"push_box","body_b":"link7","contact_count":113.0,"contact_point_centroid":[0.53671,-0.06419,0.05023],"force_p95":10.92349,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":17.45764,"mean_force":2.07236,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.50997,-0.04913,0.01809]},{"body_a":"world","body_b":"push_box","contact_count":1612.0,"contact_point_centroid":[0.51697,-0.05768,-6e-05],"force_p95":8.31532,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":15.61652,"mean_force":2.87563,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.51685,-0.0153,0.01817]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.5366,0.03695,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.52207,0.06016,0.17203]},{"body_a":"world","body_b":"push_box","contact_count":1920.0,"contact_point_centroid":[0.5366,0.03695,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact","phase_type":"contact","tcp_position_centroid":[0.5405,0.09683,0.03263]}],"total_contact_groups":5},"final_pose_error":0.48837,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50128,-0.14329,0.02504],"final_tcp_position":[0.49881,-0.1064,0.01846],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.5366,0.03695,0.025]},"peak_contact_force":29.22864,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5366,0.03695,0.02499],"object_pos_start":[0.5366,0.03695,0.025],"object_to_goal_dist_end":0.1905,"object_to_goal_dist_start":0.1905,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.54604,0.12035,0.04738],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.08687,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":480.0,"n_steps_budget":600.0,"object_pos_end":[0.5366,0.03695,0.02499],"object_pos_start":[0.5366,0.03695,0.02499],"object_to_goal_dist_end":0.1905,"object_to_goal_dist_start":0.1905,"object_z_max":0.02499,"peak_contact_force":16.30049,"phase_name":"contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1920.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.53845,0.07396,0.02268],"tcp_start":[0.54604,0.12035,0.04738],"tcp_to_object_dist_end":0.03713,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50128,-0.14329,0.02504],"object_pos_start":[0.5366,0.03695,0.02499],"object_to_goal_dist_end":0.00683,"object_to_goal_dist_start":0.1905,"object_z_max":0.02551,"peak_contact_force":1.65692,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2591.0,"raw_peak_contact_force":29.22864,"subtask_id":"push","tcp_end":[0.49881,-0.1064,0.01846],"tcp_start":[0.53845,0.07396,0.02268],"tcp_to_object_dist_end":0.03756,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `1c6409cc6d884b90ecc3937d36e5ea87cc4ef513b6f301a9da66b4e84390f805`; realized-scene SHA-256: `5f9daa62d5a7a2b8a7116f2dfbb5f9857bb0d5d4b297d304a4e76a9a270e7ec7`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50458,-0.01881,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.00458,-0.13119,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.50458,-0.01881,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.68571,"average_solve_count":70.0,"average_success_count":70.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_speed":0.13837,"contact.contact_force_threshold":14.72322,"push.push_depth":0.07254,"push.push_speed":0.05911,"push.push_timeout":8.94764},"optimized_scores":{"best_composite_score":0.32207,"best_fitness_score":0.26874,"best_task_score":0.06313},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":269.0,"contact_point_centroid":[0.51071,-0.02532,-8e-05],"force_p95":28.28168,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":34.25784,"mean_force":10.11981,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.4994,0.01437,0.019]},{"body_a":"push_box","body_b":"link7","contact_count":82.0,"contact_point_centroid":[0.52799,-0.00655,0.04967],"force_p95":26.28989,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":28.0483,"mean_force":22.09777,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.49905,0.0131,0.01862]},{"body_a":"attachment","body_b":"push_box","contact_count":105.0,"contact_point_centroid":[0.5098,0.00234,0.03976],"force_p95":19.46459,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":21.78725,"mean_force":13.11216,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.49936,0.01401,0.01895]},{"body_a":"world","body_b":"push_box","contact_count":3472.0,"contact_point_centroid":[0.50458,-0.01881,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.50093,0.03812,0.16557]},{"body_a":"world","body_b":"push_box","contact_count":2080.0,"contact_point_centroid":[0.50458,-0.01881,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact","phase_type":"contact","tcp_position_centroid":[0.50054,0.04785,0.02472]}],"total_contact_groups":5},"final_pose_error":0.20246,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50273,-0.02705,0.02515],"final_tcp_position":[0.49868,0.00985,0.01832],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50458,-0.01881,0.025]},"peak_contact_force":34.25784,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":868.0,"n_steps_budget":1000.0,"object_pos_end":[0.50458,-0.01881,0.02499],"object_pos_start":[0.50458,-0.01881,0.025],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3472.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.50359,0.07678,0.03262],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.0959,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":520.0,"n_steps_budget":600.0,"object_pos_end":[0.50458,-0.01881,0.02499],"object_pos_start":[0.50458,-0.01881,0.02499],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.02499,"peak_contact_force":26.13506,"phase_name":"contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2080.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.50107,0.01809,0.02084],"tcp_start":[0.50359,0.07678,0.03262],"tcp_to_object_dist_end":0.03729,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":105.0,"n_steps_budget":1000.0,"object_pos_end":[0.50273,-0.02705,0.02515],"object_pos_start":[0.50458,-0.01881,0.02499],"object_to_goal_dist_end":0.12299,"object_to_goal_dist_start":0.13127,"object_z_max":0.02519,"peak_contact_force":0.00212,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":456.0,"raw_peak_contact_force":34.25784,"subtask_id":"push","tcp_end":[0.49868,0.00985,0.01832],"tcp_start":[0.50107,0.01809,0.02084],"tcp_to_object_dist_end":0.03774,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `f52ec1899e2888770a8b6b3ae605718303ef4b10e72cfd7d20ce53303721b2b0`; realized-scene SHA-256: `c8d09cd43835becf8e5eb4413394fad8627e4bf404e9e7726e9f380b60e09752`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.51501,0.04767,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.01501,-0.19767,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.51501,0.04767,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.2236,"average_solve_count":161.0,"average_success_count":161.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_speed":0.03908,"contact.contact_force_threshold":13.78453,"push.push_depth":0.49953,"push.push_speed":0.05875,"push.push_timeout":3.47207},"optimized_scores":{"best_composite_score":1.00765,"best_fitness_score":0.78765,"best_task_score":0.96655},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":806.0,"contact_point_centroid":[0.51246,-0.02123,0.04215],"force_p95":23.07034,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":29.04839,"mean_force":6.23023,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.502,-0.0095,0.02141]},{"body_a":"world","body_b":"push_box","contact_count":1250.0,"contact_point_centroid":[0.51006,-0.05909,-8e-05],"force_p95":14.09535,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":19.82034,"mean_force":4.77783,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.50242,-0.00447,0.02149]},{"body_a":"push_box","body_b":"link7","contact_count":201.0,"contact_point_centroid":[0.53203,-0.04212,0.05096],"force_p95":12.12688,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":19.69046,"mean_force":2.49362,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.5007,-0.02533,0.02119]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.51501,0.04767,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.50662,0.06162,0.17985]},{"body_a":"world","body_b":"push_box","contact_count":1816.0,"contact_point_centroid":[0.51501,0.04767,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact","phase_type":"contact","tcp_position_centroid":[0.5123,0.10326,0.04184]}],"total_contact_groups":5},"final_pose_error":0.51233,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.5018,-0.14362,0.02491],"final_tcp_position":[0.49486,-0.10682,0.02099],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.51501,0.04767,0.025]},"peak_contact_force":29.04839,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51501,0.04767,0.02499],"object_pos_start":[0.51501,0.04767,0.025],"object_to_goal_dist_end":0.19823,"object_to_goal_dist_start":0.19823,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.51517,0.12349,0.06265],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.08466,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":454.0,"n_steps_budget":600.0,"object_pos_end":[0.51501,0.04767,0.02499],"object_pos_start":[0.51501,0.04767,0.02499],"object_to_goal_dist_end":0.19823,"object_to_goal_dist_start":0.19823,"object_z_max":0.02499,"peak_contact_force":20.43469,"phase_name":"contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1816.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.51261,0.08463,0.0261],"tcp_start":[0.51517,0.12349,0.06265],"tcp_to_object_dist_end":0.03706,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5018,-0.14362,0.02491],"object_pos_start":[0.51501,0.04767,0.02499],"object_to_goal_dist_end":0.00663,"object_to_goal_dist_start":0.19823,"object_z_max":0.02631,"peak_contact_force":14.51851,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2257.0,"raw_peak_contact_force":29.04839,"subtask_id":"push","tcp_end":[0.49486,-0.10682,0.02099],"tcp_start":[0.51261,0.08463,0.0261],"tcp_to_object_dist_end":0.03765,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
```