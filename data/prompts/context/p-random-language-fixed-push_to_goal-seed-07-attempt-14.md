## Search State

- **Seed**: 7
- **Iteration**: 15 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 14 | approach → approach → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | pose_tolerance | force_exceeded | pose_tolerance | 4 | 0.7803 | 0.81 | ❌ rejected |
| 13 | approach → approach → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | pose_tolerance | force_exceeded | pose_tolerance | 4 | 0.7719 | 0.80 | ❌ rejected |
| 12 | approach → approach → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | pose_tolerance | force_exceeded | pose_tolerance | 4 | 0.7793 | 0.82 | ✅ accepted |
| 11 | approach → approach → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | pose_tolerance | force_exceeded | pose_tolerance | 4 | 0.6893 | 0.71 | ✅ accepted |
| 10 | approach → approach → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | pose_tolerance | force_exceeded | pose_tolerance | 4 | 0.7982 | 0.68 | ❌ rejected |

**Proposal policy**: task_score is 0.81 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.780) — your mutation base

```yaml
skill: push_to_goal
dsl_version: 2
phases:
- id: descend_to_approach
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
    - 0.03
    tolerance: 0.02
    orientation:
      mode: none
  parameters:
    speed:
      type: scalar
      range:
      - 0.05
      - 0.25
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: scale
  retries:
    max_attempts: 1
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - 0.005
  subtask_id: approach
- id: approach_to_contact
  type: approach
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
    contact_force_threshold:
      type: scalar
      range:
      - 5.0
      - 25.0
      default: 15.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
  guards:
  - id: contact_guard
    when: after_phase
    predicate: contact_detected
    threshold: 1.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - -0.005
  subtask_id: contact
- id: push_toward_goal
  type: push
  generator: linear_cartesian
  control: admittance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.18
      axis: task_goal_direction
      mode: add_to_offset
      sign: positive
    tolerance: 0.015
    orientation:
      mode: none
  parameters:
    push_depth:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.18
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.15
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: scale
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.005
    - 0.0
    - 0.0
  subtask_id: push

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **descend_to_approach** (`approach`)
  - target: source=yaml, anchor=task_object, entity=push_box, offset=[0.0, 0.08, 0.03], tolerance=0.02
  - orientation: mode=none
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (scale)
  - retries: max_attempts=1, strategy=offset_target, offset=[0.0, 0.0, 0.005]
- **approach_to_contact** (`approach`)
  - target: source=yaml, anchor=task_object, entity=push_box, offset=[0.0, 0.03, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - contact_force_threshold: status=consumed; consumers=termination.force_threshold (replace)
  - guards:
    - id=contact_guard, when=after_phase, predicate=contact_detected, on_failure=retry, threshold=1.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, -0.005]
- **push_toward_goal** (`push`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.18, mode=add_to_offset, sign=positive}, tolerance=0.015
  - orientation: mode=none
  - parameter_bindings:
    - push_depth: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (scale)
  - retries: max_attempts=2, strategy=offset_target, offset=[0.005, 0.0, 0.0]

## Design Metrics

- **Composite score**: 0.780
- **task_score** (E): 0.814
- **fitness_score**: 0.788  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.222
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.230

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| descend_to_approach | 1.00 | 1.00 | 0.2527 |
| approach_to_contact | 0.67 | 1.00 | 0.0561 |
| push_toward_goal | 0.00 | 1.00 | 0.1915 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| descend_to_approach | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.508, 0.097, 0.071) | (0.513, 0.027, 0.025)→(0.513, 0.027, 0.025) | 0.180→0.180 | 1.00 / 4.000 | 0.245 | 0.245 |
| approach_to_contact | approach | 0.67 / force_exceeded | (0.508, 0.097, 0.071)→(0.508, 0.063, 0.027) | (0.513, 0.027, 0.025)→(0.513, 0.026, 0.025) | 0.180→0.179 | 1.00 / 4.000 | 9.523 | 14.017 |
| push_toward_goal | push | 0.00 / step_budget | (0.508, 0.063, 0.027)→(0.502, -0.127, 0.029) | (0.513, 0.026, 0.025)→(0.531, -0.154, 0.031) | 0.179→0.032 | 1.00 / 4.000 | 103.621 | 123.508 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 1.000
- lateral_force_integral: None
- approach_alignment: 0.711
- goal_progress: 0.852
- terminal_score: 0.852
- phase_score: 0.771
- phase_breakdown.approach_score: 0.415
- phase_breakdown.push_score: 0.912
- phase_breakdown.contact_score: 0.772

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.803
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.852
- **Median Q (composite search score)**: 0.905
- **K-run variance**: 0.0315
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.308


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.17391,"average_solve_count":207.0,"average_success_count":207.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_contact.contact_force_threshold":13.60194,"descend_to_approach.speed":0.18396,"push_toward_goal.push_depth":0.16181,"push_toward_goal.push_speed":0.06452},"optimized_scores":{"best_composite_score":0.90665,"best_fitness_score":0.80331,"best_task_score":0.85233},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":826.0,"contact_point_centroid":[0.53349,-0.06855,0.05701],"force_p95":92.29381,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":111.73859,"mean_force":56.6783,"phase_index":2.0,"phase_name":"push_toward_goal","phase_type":"push","tcp_position_centroid":[0.50226,-0.05515,0.02605]},{"body_a":"attachment","body_b":"push_box","contact_count":937.0,"contact_point_centroid":[0.51959,-0.04982,0.04864],"force_p95":87.91778,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":100.76315,"mean_force":45.60581,"phase_index":2.0,"phase_name":"push_toward_goal","phase_type":"push","tcp_position_centroid":[0.50267,-0.04153,0.02587]},{"body_a":"world","body_b":"push_box","contact_count":1683.0,"contact_point_centroid":[0.53001,-0.0939,-0.00017],"force_p95":60.04234,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":68.62963,"mean_force":37.89404,"phase_index":2.0,"phase_name":"push_toward_goal","phase_type":"push","tcp_position_centroid":[0.5027,-0.0464,0.02608]},{"body_a":"attachment","body_b":"push_box","contact_count":10.0,"contact_point_centroid":[0.50991,0.07247,0.02864],"force_p95":11.98186,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":12.11496,"mean_force":8.26296,"phase_index":1.0,"phase_name":"approach_to_contact","phase_type":"approach","tcp_position_centroid":[0.50986,0.08438,0.02855]},{"body_a":"world","body_b":"push_box","contact_count":1746.0,"contact_point_centroid":[0.51501,0.04769,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.279,"mean_force":0.29129,"phase_index":1.0,"phase_name":"approach_to_contact","phase_type":"approach","tcp_position_centroid":[0.50854,0.09931,0.04655]},{"body_a":"world","body_b":"push_box","contact_count":2184.0,"contact_point_centroid":[0.51501,0.04767,-1e-05],"force_p95":0.24529,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"descend_to_approach","phase_type":"approach","tcp_position_centroid":[0.50435,0.05677,0.18625]}],"total_contact_groups":6},"final_pose_error":0.18437,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.52765,-0.15736,0.03117],"final_tcp_position":[0.50196,-0.12756,0.02829],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.51501,0.04767,0.025]},"peak_contact_force":111.73859,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":546.0,"n_steps_budget":1000.0,"object_pos_end":[0.51501,0.04767,0.02499],"object_pos_start":[0.51501,0.04767,0.025],"object_to_goal_dist_end":0.19823,"object_to_goal_dist_start":0.19823,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"descend_to_approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2184.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.51038,0.11615,0.0705],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.08236,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":438.0,"n_steps_budget":600.0,"object_pos_end":[0.51505,0.04732,0.02492],"object_pos_start":[0.51501,0.04767,0.02499],"object_to_goal_dist_end":0.19789,"object_to_goal_dist_start":0.19823,"object_z_max":0.02502,"peak_contact_force":16.0,"phase_name":"approach_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1756.0,"raw_peak_contact_force":12.11496,"subtask_id":"contact","tcp_end":[0.5099,0.08411,0.02818],"tcp_start":[0.51038,0.11615,0.0705],"tcp_to_object_dist_end":0.03729,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52765,-0.15736,0.03117],"object_pos_start":[0.51505,0.04732,0.02492],"object_to_goal_dist_end":0.02927,"object_to_goal_dist_start":0.19789,"object_z_max":0.03125,"peak_contact_force":89.0735,"phase_name":"push_toward_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3446.0,"raw_peak_contact_force":111.73859,"subtask_id":"push","tcp_end":[0.50196,-0.12756,0.02829],"tcp_start":[0.5099,0.08411,0.02818],"tcp_to_object_dist_end":0.03946,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.29016,"average_solve_count":193.0,"average_success_count":193.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_contact.contact_force_threshold":9.66283,"descend_to_approach.speed":0.20339,"push_toward_goal.push_depth":0.14151,"push_toward_goal.push_speed":0.08901},"optimized_scores":{"best_composite_score":0.90499,"best_fitness_score":0.80166,"best_task_score":0.84734},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":759.0,"contact_point_centroid":[0.5263,-0.06443,0.05704],"force_p95":100.18455,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":119.72416,"mean_force":70.74014,"phase_index":2.0,"phase_name":"push_toward_goal","phase_type":"push","tcp_position_centroid":[0.49176,-0.05396,0.02765]},{"body_a":"attachment","body_b":"push_box","contact_count":912.0,"contact_point_centroid":[0.5058,-0.04216,0.048],"force_p95":99.65537,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":118.59693,"mean_force":53.30265,"phase_index":2.0,"phase_name":"push_toward_goal","phase_type":"push","tcp_position_centroid":[0.48902,-0.03461,0.02736]},{"body_a":"world","body_b":"push_box","contact_count":1772.0,"contact_point_centroid":[0.51848,-0.07705,-0.00019],"force_p95":66.98581,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":85.601,"mean_force":41.09792,"phase_index":2.0,"phase_name":"push_toward_goal","phase_type":"push","tcp_position_centroid":[0.48905,-0.03444,0.0274]},{"body_a":"attachment","body_b":"push_box","contact_count":1.0,"contact_point_centroid":[0.47499,0.08346,0.03002],"force_p95":10.75949,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":10.75949,"mean_force":10.75949,"phase_index":1.0,"phase_name":"approach_to_contact","phase_type":"approach","tcp_position_centroid":[0.47483,0.09544,0.02973]},{"body_a":"world","body_b":"push_box","contact_count":1424.0,"contact_point_centroid":[0.47924,0.05847,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.71522,"mean_force":0.25257,"phase_index":1.0,"phase_name":"approach_to_contact","phase_type":"approach","tcp_position_centroid":[0.47479,0.1104,0.04804]},{"body_a":"world","body_b":"push_box","contact_count":2220.0,"contact_point_centroid":[0.47924,0.05847,-1e-05],"force_p95":0.24529,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"descend_to_approach","phase_type":"approach","tcp_position_centroid":[0.48833,0.06183,0.18602]}],"total_contact_groups":6},"final_pose_error":0.16683,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.5313,-0.14987,0.03156],"final_tcp_position":[0.50201,-0.12447,0.02879],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47924,0.05847,0.025]},"peak_contact_force":119.72416,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":555.0,"n_steps_budget":1000.0,"object_pos_end":[0.47924,0.05847,0.02499],"object_pos_start":[0.47924,0.05847,0.025],"object_to_goal_dist_end":0.2095,"object_to_goal_dist_start":0.2095,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"descend_to_approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2220.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.47769,0.12623,0.07054],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.08166,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":356.0,"n_steps_budget":600.0,"object_pos_end":[0.47924,0.05847,0.02499],"object_pos_start":[0.47924,0.05847,0.02499],"object_to_goal_dist_end":0.2095,"object_to_goal_dist_start":0.2095,"object_z_max":0.02499,"peak_contact_force":10.75949,"phase_name":"approach_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1425.0,"raw_peak_contact_force":10.75949,"subtask_id":"contact","tcp_end":[0.47484,0.09537,0.02965],"tcp_start":[0.47769,0.12623,0.07054],"tcp_to_object_dist_end":0.03745,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5313,-0.14987,0.03156],"object_pos_start":[0.47924,0.05847,0.02499],"object_to_goal_dist_end":0.03198,"object_to_goal_dist_start":0.2095,"object_z_max":0.03161,"peak_contact_force":94.73647,"phase_name":"push_toward_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3443.0,"raw_peak_contact_force":119.72416,"subtask_id":"push","tcp_end":[0.50201,-0.12447,0.02879],"tcp_start":[0.47484,0.09537,0.02965],"tcp_to_object_dist_end":0.03887,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.03593,"average_solve_count":167.0,"average_success_count":167.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_contact.contact_force_threshold":23.20214,"descend_to_approach.speed":0.23623,"push_toward_goal.push_depth":0.18749,"push_toward_goal.push_speed":0.02791},"optimized_scores":{"best_composite_score":0.52923,"best_fitness_score":0.75923,"best_task_score":0.74111},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":931.0,"contact_point_centroid":[0.54938,-0.09058,0.05533],"force_p95":125.29259,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":139.06066,"mean_force":90.31645,"phase_index":2.0,"phase_name":"push_toward_goal","phase_type":"push","tcp_position_centroid":[0.51421,-0.07799,0.02557]},{"body_a":"world","body_b":"push_box","contact_count":1889.0,"contact_point_centroid":[0.54498,-0.12184,-0.00043],"force_p95":78.51128,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":85.75818,"mean_force":56.52403,"phase_index":2.0,"phase_name":"push_toward_goal","phase_type":"push","tcp_position_centroid":[0.5147,-0.07627,0.02549]},{"body_a":"attachment","body_b":"push_box","contact_count":962.0,"contact_point_centroid":[0.53541,-0.08327,0.05542],"force_p95":79.58437,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":81.95143,"mean_force":59.87197,"phase_index":2.0,"phase_name":"push_toward_goal","phase_type":"push","tcp_position_centroid":[0.51489,-0.07547,0.02543]},{"body_a":"attachment","body_b":"push_box","contact_count":47.0,"contact_point_centroid":[0.54565,-0.00215,0.04243],"force_p95":14.80927,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":19.17636,"mean_force":9.51432,"phase_index":1.0,"phase_name":"approach_to_contact","phase_type":"approach","tcp_position_centroid":[0.5392,0.00979,0.02506]},{"body_a":"world","body_b":"push_box","contact_count":2026.0,"contact_point_centroid":[0.54443,-0.02602,-1e-05],"force_p95":0.46716,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":13.13497,"mean_force":0.46747,"phase_index":1.0,"phase_name":"approach_to_contact","phase_type":"approach","tcp_position_centroid":[0.53633,0.02865,0.04568]},{"body_a":"world","body_b":"push_box","contact_count":1968.0,"contact_point_centroid":[0.54443,-0.02558,-1e-05],"force_p95":0.24529,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"descend_to_approach","phase_type":"approach","tcp_position_centroid":[0.51729,0.02385,0.18765]}],"total_contact_groups":6},"final_pose_error":0.2093,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.53346,-0.15373,0.03102],"final_tcp_position":[0.50246,-0.12777,0.02911],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.54443,-0.02558,0.025]},"peak_contact_force":139.06066,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":492.0,"n_steps_budget":1000.0,"object_pos_end":[0.54443,-0.02558,0.02499],"object_pos_start":[0.54443,-0.02558,0.025],"object_to_goal_dist_end":0.13211,"object_to_goal_dist_start":0.13211,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"descend_to_approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1968.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.53689,0.04903,0.07221],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.08862,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":524.0,"n_steps_budget":600.0,"object_pos_end":[0.54505,-0.02862,0.02508],"object_pos_start":[0.54443,-0.02558,0.02499],"object_to_goal_dist_end":0.12947,"object_to_goal_dist_start":0.13211,"object_z_max":0.02508,"peak_contact_force":1.8102,"phase_name":"approach_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2073.0,"raw_peak_contact_force":19.17636,"subtask_id":"contact","tcp_end":[0.53966,0.00822,0.02316],"tcp_start":[0.53689,0.04903,0.07221],"tcp_to_object_dist_end":0.03728,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53346,-0.15373,0.03102],"object_pos_start":[0.54505,-0.02862,0.02508],"object_to_goal_dist_end":0.0342,"object_to_goal_dist_start":0.12947,"object_z_max":0.03102,"peak_contact_force":127.05224,"phase_name":"push_toward_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3782.0,"raw_peak_contact_force":139.06066,"subtask_id":"push","tcp_end":[0.50246,-0.12777,0.02911],"tcp_start":[0.53966,0.00822,0.02316],"tcp_to_object_dist_end":0.04048,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```