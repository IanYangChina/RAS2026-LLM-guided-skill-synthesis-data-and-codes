## Search State

- **Seed**: 7
- **Iteration**: 12 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 11 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 4 | 0.7770 | 0.78 | ❌ rejected |
| 10 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 4 | 0.4219 | 0.42 | ❌ rejected |
| 9 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 4 | 0.4320 | 0.46 | ❌ rejected |
| 8 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 4 | 0.7944 | 0.81 | ✅ accepted |
| 7 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 4 | 0.7812 | 0.80 | ❌ rejected |

**Proposal policy**: task_score is 0.78 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `c8d09cd43835becf8e5eb4413394fad8627e4bf404e9e7726e9f380b60e09752`
- Frozen object start: [0.51501145599256, 0.047665656116349056, 0.025]
- Frozen task target: [0.5, -0.15, 0.025]
- Goal object position: (0.5, -0.15, 0.025)
- Object initial pose: (0.51501145599256, 0.047665656116349056, 0.025)
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
  frozen_object_start: [0.515, 0.0477, 0.025]
  frozen_task_target: [0.5, -0.15, 0.025]
  frozen_object_starts: {'push_box': [0.51501145599256, 0.047665656116349056, 0.025]}
  frozen_targets: {'task_goal': [0.5, -0.15, 0.025]}
  push_direction: [-0.015, -0.1977, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 25
  force_scale_n: 5
  realized_scene_sha256: c8d09cd43835becf8e5eb4413394fad8627e4bf404e9e7726e9f380b60e09752

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

## Current Skill (Q=0.777) — your mutation base

```yaml
skill: push_to_goal
dsl_version: 2
phases:
- id: approach_1
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: push_box
    offset:
    - 0.0
    - 0.08
    - 0.0
    tolerance: 0.02
    orientation:
      mode: keep_current
  subtask_id: approach
- id: contact_1
  type: contact
  generator: linear_cartesian
  control: force_threshold_switch
  termination: force_exceeded
  target:
    source: yaml
    anchor: task_object
    entity: push_box
    offset:
    - 0.0
    - 0.03
    - 0.0
    orientation:
      mode: keep_current
  parameters:
    contact_force:
      type: scalar
      range:
      - 1.0
      - 10.0
      default: 5.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    contact_speed:
      type: scalar
      range:
      - 0.005
      - 0.05
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: contact
- id: push_1
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    entity: goal_marker
    offset:
    - 0.0
    - 0.03
    - 0.0
    offset_along_axis:
      distance: 0.05
      axis: task_goal_direction
      mode: add_to_offset
      sign: positive
    tolerance: 0.03
    orientation:
      mode: keep_current
  parameters:
    push_depth:
      type: scalar
      range:
      - 0.0
      - 0.15
      default: 0.05
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.2
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: push
- id: retract_1
  type: retract
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.1
    tolerance: 0.02
    orientation:
      mode: keep_current

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, entity=push_box, offset=[0.0, 0.08, 0.0], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings: none
- **contact_1** (`contact`)
  - target: source=yaml, anchor=task_object, entity=push_box, offset=[0.0, 0.03, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - contact_force: status=consumed; consumers=termination.force_threshold (replace)
    - contact_speed: status=consumed; consumers=generator.speed (replace)
- **push_1** (`push`)
  - target: source=yaml, anchor=task_goal, entity=goal_marker, offset=[0.0, 0.03, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.05, mode=add_to_offset, sign=positive}, tolerance=0.03
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_depth: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
- **retract_1** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.1], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.777
- **task_score** (E): 0.779
- **fitness_score**: 0.787  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.250
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.260

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2800 |
| contact_1 | 1.00 | 1.00 | 0.0389 |
| push_1 | 1.00 | 0.67 | 0.1874 |
| retract_1 | 1.00 | 1.00 | 0.0804 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.508, 0.098, 0.042) | (0.513, 0.027, 0.025)→(0.513, 0.027, 0.025) | 0.180→0.180 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact_1 | contact | 1.00 / force_exceeded | (0.508, 0.098, 0.042)→(0.508, 0.064, 0.023) | (0.513, 0.027, 0.025)→(0.513, 0.027, 0.025) | 0.180→0.180 | 1.00 / 5.000 | 16.379 | 0.245 |
| push_1 | push | 1.00 / step_budget | (0.508, 0.064, 0.023)→(0.496, -0.121, 0.020) | (0.513, 0.027, 0.025)→(0.529, -0.140, 0.026) | 0.180→0.035 | 0.67 / 1.667 | 0.404 | 64.872 |
| retract_1 | retract | 1.00 / step_budget | (0.496, -0.121, 0.020)→(0.493, -0.120, 0.101) | (0.529, -0.140, 0.026)→(0.530, -0.143, 0.025) | 0.035→0.036 | 1.00 / 4.000 | 0.245 | 1.652 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 1.000
- lateral_force_integral: None
- approach_alignment: 0.761
- goal_progress: 0.913
- terminal_score: 0.913
- phase_score: 0.814
- phase_breakdown.contact_score: 0.775
- phase_breakdown.push_score: 0.893
- phase_breakdown.approach_score: 0.674

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.854
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.913
- **Median Q (composite search score)**: 0.762
- **K-run variance**: 0.0025
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.240


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `75e2389a1a667086aa2b9c0de482ff37adf5571150b90a83772692baadf8b52e`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.06,0.06]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `154c216c563de6b8ee153943e5b668ca6d0c7dfd9253696b060f91a67dca06ec`; realized-scene SHA-256: `c8d09cd43835becf8e5eb4413394fad8627e4bf404e9e7726e9f380b60e09752`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.51501,0.04767,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.01501,-0.19767,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.51501,0.04767,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.61143,"average_solve_count":175.0,"average_success_count":175.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"contact_1.contact_force":7.29421,"contact_1.contact_speed":0.02258,"push_1.push_depth":0.02517,"push_1.push_speed":0.08204},"optimized_scores":{"best_composite_score":0.76239,"best_fitness_score":0.77239,"best_task_score":0.77901},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":142.0,"contact_point_centroid":[0.51161,0.00719,0.04243],"force_p95":24.89195,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":49.141,"mean_force":5.99043,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50411,0.01844,0.02015]},{"body_a":"world","body_b":"push_box","contact_count":281.0,"contact_point_centroid":[0.52981,-0.06846,-0.0001],"force_p95":17.1654,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":30.13123,"mean_force":3.99707,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50167,-0.02365,0.02004]},{"body_a":"push_box","body_b":"link7","contact_count":25.0,"contact_point_centroid":[0.53854,-0.02708,0.05234],"force_p95":15.3699,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":17.1565,"mean_force":2.68782,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50144,-0.02011,0.01937]},{"body_a":"world","body_b":"push_box","contact_count":959.0,"contact_point_centroid":[0.54154,-0.13567,-7e-05],"force_p95":0.31078,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.15833,"mean_force":0.26378,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49328,-0.11591,0.06022]},{"body_a":"world","body_b":"push_box","contact_count":2264.0,"contact_point_centroid":[0.51501,0.04767,-1e-05],"force_p95":0.24528,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50452,0.05771,0.17082]},{"body_a":"world","body_b":"push_box","contact_count":3388.0,"contact_point_centroid":[0.51501,0.04767,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50846,0.09946,0.02928]}],"total_contact_groups":6},"final_pose_error":0.01993,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.5415,-0.13597,0.02499],"final_tcp_position":[0.49316,-0.11548,0.10028],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.51501,0.04767,0.025]},"peak_contact_force":49.141,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":566.0,"n_steps_budget":1000.0,"object_pos_end":[0.51501,0.04767,0.02499],"object_pos_start":[0.51501,0.04767,0.025],"object_to_goal_dist_end":0.19823,"object_to_goal_dist_start":0.19823,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2264.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.51046,0.11714,0.04099],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07144,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":847.0,"n_steps_budget":1000.0,"object_pos_end":[0.51501,0.04767,0.02499],"object_pos_start":[0.51501,0.04767,0.02499],"object_to_goal_dist_end":0.19823,"object_to_goal_dist_start":0.19823,"object_z_max":0.02499,"peak_contact_force":14.78623,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":3388.0,"raw_peak_contact_force":0.24525,"subtask_id":"contact","tcp_end":[0.50996,0.08464,0.02308],"tcp_start":[0.51046,0.11714,0.04099],"tcp_to_object_dist_end":0.03737,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":336.0,"n_steps_budget":1000.0,"object_pos_end":[0.5409,-0.13219,0.02708],"object_pos_start":[0.51501,0.04767,0.02499],"object_to_goal_dist_end":0.04465,"object_to_goal_dist_start":0.19823,"object_z_max":0.02752,"peak_contact_force":0.83654,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":448.0,"raw_peak_contact_force":49.141,"subtask_id":"push","tcp_end":[0.49639,-0.1161,0.01994],"tcp_start":[0.50996,0.08464,0.02308],"tcp_to_object_dist_end":0.04786,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":247.0,"n_steps_budget":630.0,"object_pos_end":[0.5415,-0.13597,0.02499],"object_pos_start":[0.5409,-0.13219,0.02708],"object_to_goal_dist_end":0.04381,"object_to_goal_dist_start":0.04465,"object_z_max":0.02708,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":959.0,"raw_peak_contact_force":2.15833,"tcp_end":[0.49316,-0.11548,0.10028],"tcp_start":[0.49639,-0.1161,0.01994],"tcp_to_object_dist_end":0.09179,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `4d55d9375783bea830660bf0a13dfc76a97a0d4f5645e7ebcc1ef7143776d0b7`; realized-scene SHA-256: `f3b8ea82cefd9504be10e2d47c49094a836a703404c06bdee3b01a27a59bf7be`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.47924,0.05847,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[0.02076,-0.20847,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.47924,0.05847,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.76,"average_solve_count":150.0,"average_success_count":150.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"contact_1.contact_force":8.12729,"contact_1.contact_speed":0.03287,"push_1.push_depth":0.03343,"push_1.push_speed":0.12473},"optimized_scores":{"best_composite_score":0.84374,"best_fitness_score":0.85374,"best_task_score":0.91317},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":261.0,"contact_point_centroid":[0.48837,-0.0236,0.03404],"force_p95":30.48688,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":62.56126,"mean_force":4.34667,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48476,-0.0118,0.02056]},{"body_a":"world","body_b":"push_box","contact_count":254.0,"contact_point_centroid":[0.49281,-0.05781,-4e-05],"force_p95":24.88773,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":32.9704,"mean_force":5.11903,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48408,-0.00519,0.02068]},{"body_a":"world","body_b":"push_box","contact_count":918.0,"contact_point_centroid":[0.50909,-0.16628,-4e-05],"force_p95":0.4647,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.3798,"mean_force":0.27609,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49407,-0.12428,0.06187]},{"body_a":"world","body_b":"push_box","contact_count":2292.0,"contact_point_centroid":[0.47924,0.05847,-1e-05],"force_p95":0.24528,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48828,0.06282,0.17064]},{"body_a":"world","body_b":"push_box","contact_count":2232.0,"contact_point_centroid":[0.47924,0.05847,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.47465,0.10974,0.02995]}],"total_contact_groups":5},"final_pose_error":0.01999,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50933,-0.16562,0.02499],"final_tcp_position":[0.49403,-0.12394,0.10037],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47924,0.05847,0.025]},"peak_contact_force":62.56126,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":573.0,"n_steps_budget":1000.0,"object_pos_end":[0.47924,0.05847,0.02499],"object_pos_start":[0.47924,0.05847,0.025],"object_to_goal_dist_end":0.2095,"object_to_goal_dist_start":0.2095,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2292.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.47754,0.12727,0.04111],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07068,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":558.0,"n_steps_budget":810.0,"object_pos_end":[0.47924,0.05847,0.02499],"object_pos_start":[0.47924,0.05847,0.02499],"object_to_goal_dist_end":0.2095,"object_to_goal_dist_start":0.2095,"object_z_max":0.02499,"peak_contact_force":19.68868,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2232.0,"raw_peak_contact_force":0.24525,"subtask_id":"contact","tcp_end":[0.475,0.09542,0.02378],"tcp_start":[0.47754,0.12727,0.04111],"tcp_to_object_dist_end":0.03721,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":367.0,"n_steps_budget":1000.0,"object_pos_end":[0.50677,-0.16114,0.02587],"object_pos_start":[0.47924,0.05847,0.02499],"object_to_goal_dist_end":0.01307,"object_to_goal_dist_start":0.2095,"object_z_max":0.0262,"peak_contact_force":0.0,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":515.0,"raw_peak_contact_force":62.56126,"subtask_id":"push","tcp_end":[0.49727,-0.12461,0.02009],"tcp_start":[0.475,0.09542,0.02378],"tcp_to_object_dist_end":0.03818,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":247.0,"n_steps_budget":630.0,"object_pos_end":[0.50933,-0.16562,0.02499],"object_pos_start":[0.50677,-0.16114,0.02587],"object_to_goal_dist_end":0.01819,"object_to_goal_dist_start":0.01307,"object_z_max":0.02587,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":918.0,"raw_peak_contact_force":2.3798,"tcp_end":[0.49403,-0.12394,0.10037],"tcp_start":[0.49727,-0.12461,0.02009],"tcp_to_object_dist_end":0.08748,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `0a9238470f4497c7aa88b149b7cee960f9853513db10bf496723f5ea1d3a6043`; realized-scene SHA-256: `2cf7387f3e8baf02f18930263090d6f78777bdbc147b7fa30c178332e76b547b`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.54443,-0.02558,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.04443,-0.12442,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.54443,-0.02558,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.29545,"average_solve_count":176.0,"average_success_count":176.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"contact_1.contact_force":5.23073,"contact_1.contact_speed":0.02685,"push_1.push_depth":0.03234,"push_1.push_speed":0.05539},"optimized_scores":{"best_composite_score":0.72496,"best_fitness_score":0.73496,"best_task_score":0.64395},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":340.0,"contact_point_centroid":[0.55435,-0.09793,-0.00014],"force_p95":63.6647,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":82.91403,"mean_force":21.69194,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51444,-0.06152,0.02081]},{"body_a":"push_box","body_b":"link7","contact_count":128.0,"contact_point_centroid":[0.55002,-0.07066,0.05385],"force_p95":63.19153,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":69.52377,"mean_force":37.72715,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51305,-0.06569,0.0207]},{"body_a":"attachment","body_b":"push_box","contact_count":169.0,"contact_point_centroid":[0.53213,-0.05585,0.05082],"force_p95":39.73924,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":54.5325,"mean_force":16.15504,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51884,-0.0471,0.02057]},{"body_a":"world","body_b":"push_box","contact_count":988.0,"contact_point_centroid":[0.54067,-0.12636,-4e-05],"force_p95":0.25247,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.41855,"mean_force":0.24668,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49215,-0.12134,0.05979]},{"body_a":"world","body_b":"push_box","contact_count":2080.0,"contact_point_centroid":[0.54443,-0.02558,-1e-05],"force_p95":0.24529,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51762,0.02423,0.17247]},{"body_a":"world","body_b":"push_box","contact_count":3592.0,"contact_point_centroid":[0.54443,-0.02558,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.53616,0.02967,0.0299]}],"total_contact_groups":6},"final_pose_error":0.01994,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.54067,-0.12636,0.02499],"final_tcp_position":[0.49204,-0.12087,0.10106],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.54443,-0.02558,0.025]},"peak_contact_force":82.91403,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":520.0,"n_steps_budget":1000.0,"object_pos_end":[0.54443,-0.02558,0.02499],"object_pos_start":[0.54443,-0.02558,0.025],"object_to_goal_dist_end":0.13211,"object_to_goal_dist_start":0.13211,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2080.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.53717,0.04944,0.04292],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07748,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":898.0,"n_steps_budget":1000.0,"object_pos_end":[0.54443,-0.02558,0.02499],"object_pos_start":[0.54443,-0.02558,0.02499],"object_to_goal_dist_end":0.13211,"object_to_goal_dist_start":0.13211,"object_z_max":0.02499,"peak_contact_force":14.66088,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":3592.0,"raw_peak_contact_force":0.24525,"subtask_id":"contact","tcp_end":[0.53888,0.0114,0.02236],"tcp_start":[0.53717,0.04944,0.04292],"tcp_to_object_dist_end":0.03749,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":258.0,"n_steps_budget":1000.0,"object_pos_end":[0.53991,-0.1262,0.02422],"object_pos_start":[0.54443,-0.02558,0.02499],"object_to_goal_dist_end":0.04648,"object_to_goal_dist_start":0.13211,"object_z_max":0.02907,"peak_contact_force":0.37672,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":637.0,"raw_peak_contact_force":82.91403,"subtask_id":"push","tcp_end":[0.49526,-0.12152,0.02072],"tcp_start":[0.53888,0.0114,0.02236],"tcp_to_object_dist_end":0.04504,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":247.0,"n_steps_budget":630.0,"object_pos_end":[0.54067,-0.12636,0.02499],"object_pos_start":[0.53991,-0.1262,0.02422],"object_to_goal_dist_end":0.04704,"object_to_goal_dist_start":0.04648,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":988.0,"raw_peak_contact_force":0.41855,"tcp_end":[0.49204,-0.12087,0.10106],"tcp_start":[0.49526,-0.12152,0.02072],"tcp_to_object_dist_end":0.09045,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```