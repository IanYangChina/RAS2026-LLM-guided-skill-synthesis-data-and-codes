## Search State

- **Seed**: 7
- **Iteration**: 15 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 14 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 5 | 0.7500 | 0.88 | ❌ rejected |
| 13 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 4 | 0.8359 | 0.91 | ✅ accepted |
| 12 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 4 | 0.6345 | 0.78 | ❌ rejected |
| 11 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 4 | 0.7770 | 0.78 | ❌ rejected |
| 10 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 4 | 0.4219 | 0.42 | ❌ rejected |

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

## Current Skill (Q=0.750) — your mutation base

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
      mode: none
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
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.01
      axis: task_goal_direction
      mode: replace_offset_projection
      sign: positive
    orientation:
      mode: none
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
    tolerance: 0.05
    orientation:
      mode: none
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
  - orientation: mode=none
  - parameter_bindings: none
- **contact_1** (`contact`)
  - target: source=yaml, anchor=task_object, entity=push_box, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.01, mode=replace_offset_projection, sign=positive}
  - orientation: mode=none
  - parameter_bindings:
    - contact_force: status=consumed; consumers=termination.force_threshold (replace)
    - contact_speed: status=consumed; consumers=generator.speed (replace)
- **push_1** (`push`)
  - target: source=yaml, anchor=task_goal, entity=goal_marker, offset=[0.0, 0.03, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.05, mode=add_to_offset, sign=positive}, tolerance=0.05
  - orientation: mode=none
  - parameter_bindings:
    - push_depth: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
- **retract_1** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.1], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.750
- **task_score** (E): 0.878
- **fitness_score**: 0.838  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.222
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.310

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2803 |
| contact_1 | 0.67 | 1.00 | 0.0344 |
| push_1 | 1.00 | 1.00 | 0.1940 |
| retract_1 | 1.00 | 1.00 | 0.0806 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.508, 0.098, 0.041) | (0.513, 0.027, 0.025)→(0.513, 0.027, 0.025) | 0.180→0.180 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact_1 | contact | 0.67 / force_exceeded | (0.508, 0.098, 0.041)→(0.505, 0.066, 0.030) | (0.513, 0.027, 0.025)→(0.513, 0.027, 0.025) | 0.180→0.180 | 1.00 / 4.667 | 11.111 | 0.245 |
| push_1 | push | 1.00 / time_limit | (0.505, 0.066, 0.030)→(0.499, -0.126, 0.028) | (0.513, 0.027, 0.025)→(0.523, -0.153, 0.031) | 0.180→0.028 | 1.00 / 3.667 | 95.717 | 124.600 |
| retract_1 | retract | 1.00 / step_budget | (0.499, -0.126, 0.028)→(0.496, -0.126, 0.108) | (0.523, -0.153, 0.031)→(0.516, -0.152, 0.025) | 0.028→0.020 | 1.00 / 4.000 | 0.245 | 69.957 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 1.000
- lateral_force_integral: None
- approach_alignment: 0.776
- goal_progress: 0.920
- terminal_score: 0.920
- phase_score: 0.815
- phase_breakdown.contact_score: 0.745
- phase_breakdown.push_score: 0.913
- phase_breakdown.approach_score: 0.675

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.869
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.936
- **Median Q (composite search score)**: 0.811
- **K-run variance**: 0.0191
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.537


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.57333,"average_solve_count":150.0,"average_success_count":150.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"contact_1.contact_force":1.7669,"contact_1.contact_speed":0.02288,"push_1.push_depth":0.10758,"push_1.push_max_time":1.77718,"push_1.push_speed":0.14107},"optimized_scores":{"best_composite_score":0.88021,"best_fitness_score":0.85688,"best_task_score":0.92026},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":859.0,"contact_point_centroid":[0.51626,-0.03626,0.04752],"force_p95":105.14347,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":140.72934,"mean_force":40.08789,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50118,-0.02668,0.02587]},{"body_a":"push_box","body_b":"link7","contact_count":620.0,"contact_point_centroid":[0.53355,-0.07015,0.05594],"force_p95":108.88119,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":134.73895,"mean_force":57.66214,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50065,-0.0559,0.02619]},{"body_a":"push_box","body_b":"link7","contact_count":15.0,"contact_point_centroid":[0.54046,-0.13897,0.05688],"force_p95":104.29724,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":111.08609,"mean_force":37.98366,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50087,-0.1282,0.02964]},{"body_a":"world","body_b":"push_box","contact_count":1698.0,"contact_point_centroid":[0.52326,-0.07274,-0.00015],"force_p95":68.78364,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":86.89924,"mean_force":30.90344,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50133,-0.02416,0.02595]},{"body_a":"attachment","body_b":"push_box","contact_count":41.0,"contact_point_centroid":[0.51497,-0.13325,0.05047],"force_p95":68.123,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":81.84562,"mean_force":11.05886,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4997,-0.12785,0.03989]},{"body_a":"world","body_b":"push_box","contact_count":728.0,"contact_point_centroid":[0.52194,-0.15776,-9e-05],"force_p95":0.90766,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":40.01514,"mean_force":0.64646,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4983,-0.12726,0.07566]},{"body_a":"world","body_b":"push_box","contact_count":2264.0,"contact_point_centroid":[0.51501,0.04767,-1e-05],"force_p95":0.24528,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50439,0.05756,0.1711]},{"body_a":"world","body_b":"push_box","contact_count":3172.0,"contact_point_centroid":[0.51501,0.04767,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50705,0.09953,0.03253]}],"total_contact_groups":8},"final_pose_error":0.01974,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.51542,-0.15347,0.02499],"final_tcp_position":[0.49817,-0.12713,0.10887],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.51501,0.04767,0.025]},"peak_contact_force":140.72934,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":566.0,"n_steps_budget":1000.0,"object_pos_end":[0.51501,0.04767,0.02499],"object_pos_start":[0.51501,0.04767,0.025],"object_to_goal_dist_end":0.19823,"object_to_goal_dist_start":0.19823,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2264.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.51029,0.1171,0.04089],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07138,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":793.0,"n_steps_budget":1000.0,"object_pos_end":[0.51501,0.04767,0.02499],"object_pos_start":[0.51501,0.04767,0.02499],"object_to_goal_dist_end":0.19823,"object_to_goal_dist_start":0.19823,"object_z_max":0.02499,"peak_contact_force":12.53118,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":3172.0,"raw_peak_contact_force":0.24525,"subtask_id":"contact","tcp_end":[0.50759,0.08464,0.02935],"tcp_start":[0.51029,0.1171,0.04089],"tcp_to_object_dist_end":0.03797,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52534,-0.15746,0.0316],"object_pos_start":[0.51501,0.04767,0.02499],"object_to_goal_dist_end":0.02723,"object_to_goal_dist_start":0.19823,"object_z_max":0.03158,"peak_contact_force":104.3544,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3177.0,"raw_peak_contact_force":140.72934,"subtask_id":"push","tcp_end":[0.50147,-0.12777,0.02833],"tcp_start":[0.50759,0.08464,0.02935],"tcp_to_object_dist_end":0.03823,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":250.0,"n_steps_budget":630.0,"object_pos_end":[0.51542,-0.15347,0.02499],"object_pos_start":[0.52534,-0.15746,0.0316],"object_to_goal_dist_end":0.01581,"object_to_goal_dist_start":0.02723,"object_z_max":0.03299,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":784.0,"raw_peak_contact_force":111.08609,"tcp_end":[0.49817,-0.12713,0.10887],"tcp_start":[0.50147,-0.12777,0.02833],"tcp_to_object_dist_end":0.0896,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.51553,"average_solve_count":161.0,"average_success_count":161.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"contact_1.contact_force":6.89023,"contact_1.contact_speed":0.0137,"push_1.push_depth":0.07424,"push_1.push_max_time":3.68377,"push_1.push_speed":0.14497},"optimized_scores":{"best_composite_score":0.55881,"best_fitness_score":0.86881,"best_task_score":0.93561},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":856.0,"contact_point_centroid":[0.5012,-0.02864,0.04701],"force_p95":75.83851,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":101.28543,"mean_force":31.53061,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48603,-0.01857,0.02576]},{"body_a":"world","body_b":"push_box","contact_count":1471.0,"contact_point_centroid":[0.5028,-0.05519,-0.00012],"force_p95":59.57688,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":90.27728,"mean_force":23.33525,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4844,-0.0038,0.02624]},{"body_a":"push_box","body_b":"link7","contact_count":574.0,"contact_point_centroid":[0.52051,-0.07266,0.05624],"force_p95":54.85779,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":85.85215,"mean_force":30.80837,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49112,-0.05505,0.02559]},{"body_a":"push_box","body_b":"link7","contact_count":4.0,"contact_point_centroid":[0.52847,-0.15093,0.05482],"force_p95":25.84429,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":28.08406,"mean_force":14.08832,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4991,-0.1251,0.02365]},{"body_a":"attachment","body_b":"push_box","contact_count":32.0,"contact_point_centroid":[0.51238,-0.13488,0.05176],"force_p95":9.97749,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":22.40976,"mean_force":2.14856,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49714,-0.12499,0.03285]},{"body_a":"world","body_b":"push_box","contact_count":823.0,"contact_point_centroid":[0.507,-0.16587,-3e-05],"force_p95":0.70644,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.74838,"mean_force":0.32049,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4959,-0.12433,0.06949]},{"body_a":"world","body_b":"push_box","contact_count":2296.0,"contact_point_centroid":[0.47924,0.05847,-1e-05],"force_p95":0.24528,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48814,0.06269,0.17079]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.47924,0.05847,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.47391,0.11232,0.03354]}],"total_contact_groups":8},"final_pose_error":0.01974,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50559,-0.16228,0.02499],"final_tcp_position":[0.49592,-0.12419,0.10423],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47924,0.05847,0.025]},"peak_contact_force":101.28543,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":574.0,"n_steps_budget":1000.0,"object_pos_end":[0.47924,0.05847,0.02499],"object_pos_start":[0.47924,0.05847,0.025],"object_to_goal_dist_end":0.2095,"object_to_goal_dist_start":0.2095,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2296.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.47734,0.12723,0.04092],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.0706,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47924,0.05847,0.02499],"object_pos_start":[0.47924,0.05847,0.02499],"object_to_goal_dist_end":0.2095,"object_to_goal_dist_start":0.2095,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24525,"subtask_id":"contact","tcp_end":[0.47417,0.10102,0.03112],"tcp_start":[0.47734,0.12723,0.04092],"tcp_to_object_dist_end":0.04329,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50698,-0.1642,0.03006],"object_pos_start":[0.47924,0.05847,0.02499],"object_to_goal_dist_end":0.01661,"object_to_goal_dist_start":0.2095,"object_z_max":0.03086,"peak_contact_force":54.14386,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2901.0,"raw_peak_contact_force":101.28543,"subtask_id":"push","tcp_end":[0.49926,-0.12482,0.02368],"tcp_start":[0.47417,0.10102,0.03112],"tcp_to_object_dist_end":0.04063,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":252.0,"n_steps_budget":630.0,"object_pos_end":[0.50559,-0.16228,0.02499],"object_pos_start":[0.50698,-0.1642,0.03006],"object_to_goal_dist_end":0.01349,"object_to_goal_dist_start":0.01661,"object_z_max":0.03006,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":859.0,"raw_peak_contact_force":28.08406,"tcp_end":[0.49592,-0.12419,0.10423],"tcp_start":[0.49926,-0.12482,0.02368],"tcp_to_object_dist_end":0.08845,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.72727,"average_solve_count":143.0,"average_success_count":143.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"contact_1.contact_force":6.3697,"contact_1.contact_speed":0.03276,"push_1.push_depth":0.09103,"push_1.push_max_time":2.86743,"push_1.push_speed":0.09318},"optimized_scores":{"best_composite_score":0.81087,"best_fitness_score":0.78753,"best_task_score":0.7771},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":818.0,"contact_point_centroid":[0.55214,-0.07354,0.05575],"force_p95":127.91262,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":131.78413,"mean_force":82.72029,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51181,-0.0671,0.02861]},{"body_a":"world","body_b":"push_box","contact_count":1946.0,"contact_point_centroid":[0.54814,-0.09725,-0.00035],"force_p95":99.97687,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":111.7883,"mean_force":46.3747,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51439,-0.05645,0.0281]},{"body_a":"attachment","body_b":"push_box","contact_count":952.0,"contact_point_centroid":[0.53301,-0.0655,0.0544],"force_p95":83.218,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":85.8405,"mean_force":45.02874,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51405,-0.05775,0.02814]},{"body_a":"world","body_b":"push_box","contact_count":808.0,"contact_point_centroid":[0.5329,-0.14042,-7e-05],"force_p95":0.80486,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":70.70175,"mean_force":0.51486,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49423,-0.12529,0.07651]},{"body_a":"push_box","body_b":"link7","contact_count":17.0,"contact_point_centroid":[0.54057,-0.12102,0.05678],"force_p95":54.62543,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":70.03581,"mean_force":12.42102,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49659,-0.12609,0.03185]},{"body_a":"attachment","body_b":"push_box","contact_count":27.0,"contact_point_centroid":[0.51858,-0.12632,0.06056],"force_p95":27.20125,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":52.55849,"mean_force":6.39692,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49578,-0.12584,0.03872]},{"body_a":"world","body_b":"push_box","contact_count":2084.0,"contact_point_centroid":[0.54443,-0.02558,-1e-05],"force_p95":0.24529,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51752,0.02421,0.1725]},{"body_a":"world","body_b":"push_box","contact_count":2804.0,"contact_point_centroid":[0.54443,-0.02558,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.53379,0.03002,0.03321]}],"total_contact_groups":8},"final_pose_error":0.01985,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.52795,-0.14073,0.02499],"final_tcp_position":[0.49417,-0.12519,0.11099],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.54443,-0.02558,0.025]},"peak_contact_force":131.78413,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":521.0,"n_steps_budget":1000.0,"object_pos_end":[0.54443,-0.02558,0.02499],"object_pos_start":[0.54443,-0.02558,0.025],"object_to_goal_dist_end":0.13211,"object_to_goal_dist_start":0.13211,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2084.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.53708,0.0495,0.04248],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07744,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":701.0,"n_steps_budget":1000.0,"object_pos_end":[0.54443,-0.02558,0.02499],"object_pos_start":[0.54443,-0.02558,0.02499],"object_to_goal_dist_end":0.13211,"object_to_goal_dist_start":0.13211,"object_z_max":0.02499,"peak_contact_force":20.55742,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2804.0,"raw_peak_contact_force":0.24525,"subtask_id":"contact","tcp_end":[0.53443,0.0114,0.02908],"tcp_start":[0.53708,0.0495,0.04248],"tcp_to_object_dist_end":0.03852,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53722,-0.13868,0.03094],"object_pos_start":[0.54443,-0.02558,0.02499],"object_to_goal_dist_end":0.03936,"object_to_goal_dist_start":0.13211,"object_z_max":0.03142,"peak_contact_force":128.65184,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3716.0,"raw_peak_contact_force":131.78413,"subtask_id":"push","tcp_end":[0.49747,-0.12584,0.03055],"tcp_start":[0.53443,0.0114,0.02908],"tcp_to_object_dist_end":0.04178,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":252.0,"n_steps_budget":660.0,"object_pos_end":[0.52795,-0.14073,0.02499],"object_pos_start":[0.53722,-0.13868,0.03094],"object_to_goal_dist_end":0.02945,"object_to_goal_dist_start":0.03936,"object_z_max":0.03239,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":852.0,"raw_peak_contact_force":70.70175,"tcp_end":[0.49417,-0.12519,0.11099],"tcp_start":[0.49747,-0.12584,0.03055],"tcp_to_object_dist_end":0.0937,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```