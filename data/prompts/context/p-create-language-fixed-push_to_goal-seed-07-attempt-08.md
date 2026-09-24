## Search State

- **Seed**: 7
- **Iteration**: 9 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 8 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 4 | 0.7944 | 0.81 | ❌ rejected |
| 7 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 4 | 0.7812 | 0.80 | ❌ rejected |
| 6 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 4 | 0.8167 | 0.86 | ✅ accepted |
| 5 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 5 | 0.2720 | 0.23 | ❌ rejected |
| 4 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 4 | 0.8056 | 0.86 | ✅ accepted |

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

## Current Skill (Q=0.794) — your mutation base

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

- **Composite score**: 0.794
- **task_score** (E): 0.813
- **fitness_score**: 0.804  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.250
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.260

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2800 |
| contact_1 | 1.00 | 1.00 | 0.0389 |
| push_1 | 1.00 | 1.00 | 0.1872 |
| retract_1 | 1.00 | 1.00 | 0.0804 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.508, 0.098, 0.042) | (0.513, 0.027, 0.025)→(0.513, 0.027, 0.025) | 0.180→0.180 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact_1 | contact | 1.00 / force_exceeded | (0.508, 0.098, 0.042)→(0.508, 0.064, 0.023) | (0.513, 0.027, 0.025)→(0.513, 0.027, 0.025) | 0.180→0.180 | 1.00 / 5.000 | 18.142 | 0.245 |
| push_1 | push | 1.00 / step_budget | (0.508, 0.064, 0.023)→(0.497, -0.121, 0.021) | (0.513, 0.027, 0.025)→(0.527, -0.141, 0.027) | 0.180→0.031 | 1.00 / 2.000 | 0.529 | 80.022 |
| retract_1 | retract | 1.00 / step_budget | (0.497, -0.121, 0.021)→(0.493, -0.120, 0.101) | (0.527, -0.141, 0.027)→(0.527, -0.144, 0.025) | 0.031→0.032 | 1.00 / 4.000 | 0.245 | 1.910 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 1.000
- lateral_force_integral: None
- approach_alignment: 0.754
- goal_progress: 0.929
- terminal_score: 0.929
- phase_score: 0.800
- phase_breakdown.push_score: 0.865
- phase_breakdown.approach_score: 0.674
- phase_breakdown.contact_score: 0.775

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.851
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.929
- **Median Q (composite search score)**: 0.776
- **K-run variance**: 0.0011
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.437


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.79433,"average_solve_count":141.0,"average_success_count":141.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"contact_1.contact_force":3.7599,"contact_1.contact_speed":0.04969,"push_1.push_depth":0.02759,"push_1.push_speed":0.11955},"optimized_scores":{"best_composite_score":0.76544,"best_fitness_score":0.77544,"best_task_score":0.75798},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":220.0,"contact_point_centroid":[0.51649,-0.02559,0.04962],"force_p95":75.07968,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":86.65162,"mean_force":21.55607,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50283,-0.01867,0.02095]},{"body_a":"world","body_b":"push_box","contact_count":355.0,"contact_point_centroid":[0.54444,-0.06807,-0.00013],"force_p95":68.61143,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":86.39956,"mean_force":23.75859,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50209,-0.03168,0.02094]},{"body_a":"push_box","body_b":"link7","contact_count":150.0,"contact_point_centroid":[0.53646,-0.05721,0.0546],"force_p95":60.10722,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":78.97294,"mean_force":31.19752,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50122,-0.05085,0.02108]},{"body_a":"attachment","body_b":"push_box","contact_count":5.0,"contact_point_centroid":[0.51406,-0.11909,0.04998],"force_p95":1.9538,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.98463,"mean_force":1.51897,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49545,-0.11981,0.02184]},{"body_a":"world","body_b":"push_box","contact_count":962.0,"contact_point_centroid":[0.53937,-0.12239,-2e-05],"force_p95":0.25519,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.91503,"mean_force":0.25215,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49389,-0.11804,0.06082]},{"body_a":"world","body_b":"push_box","contact_count":2264.0,"contact_point_centroid":[0.51501,0.04767,-1e-05],"force_p95":0.24528,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50452,0.05771,0.17082]},{"body_a":"world","body_b":"push_box","contact_count":1784.0,"contact_point_centroid":[0.51501,0.04767,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50852,0.10031,0.02977]}],"total_contact_groups":7},"final_pose_error":0.01995,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.5391,-0.12219,0.02499],"final_tcp_position":[0.49379,-0.1176,0.10105],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.51501,0.04767,0.025]},"peak_contact_force":86.65162,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":566.0,"n_steps_budget":1000.0,"object_pos_end":[0.51501,0.04767,0.02499],"object_pos_start":[0.51501,0.04767,0.025],"object_to_goal_dist_end":0.19823,"object_to_goal_dist_start":0.19823,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2264.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.51046,0.11714,0.04099],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07144,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":446.0,"n_steps_budget":600.0,"object_pos_end":[0.51501,0.04767,0.02499],"object_pos_start":[0.51501,0.04767,0.02499],"object_to_goal_dist_end":0.19823,"object_to_goal_dist_start":0.19823,"object_z_max":0.02499,"peak_contact_force":16.83177,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1784.0,"raw_peak_contact_force":0.24525,"subtask_id":"contact","tcp_end":[0.50996,0.08464,0.02308],"tcp_start":[0.51046,0.11714,0.04099],"tcp_to_object_dist_end":0.03736,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":345.0,"n_steps_budget":1000.0,"object_pos_end":[0.54096,-0.12215,0.02652],"object_pos_start":[0.51501,0.04767,0.02499],"object_to_goal_dist_end":0.04955,"object_to_goal_dist_start":0.19823,"object_z_max":0.03026,"peak_contact_force":0.4991,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":725.0,"raw_peak_contact_force":86.65162,"subtask_id":"push","tcp_end":[0.49702,-0.11823,0.02073],"tcp_start":[0.50996,0.08464,0.02308],"tcp_to_object_dist_end":0.04449,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":247.0,"n_steps_budget":630.0,"object_pos_end":[0.5391,-0.12219,0.02499],"object_pos_start":[0.54096,-0.12215,0.02652],"object_to_goal_dist_end":0.04798,"object_to_goal_dist_start":0.04955,"object_z_max":0.02652,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":967.0,"raw_peak_contact_force":1.98463,"tcp_end":[0.49379,-0.1176,0.10105],"tcp_start":[0.49702,-0.11823,0.02073],"tcp_to_object_dist_end":0.08865,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.69022,"average_solve_count":184.0,"average_success_count":184.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"contact_1.contact_force":4.26645,"contact_1.contact_speed":0.02591,"push_1.push_depth":0.02932,"push_1.push_speed":0.0714},"optimized_scores":{"best_composite_score":0.84137,"best_fitness_score":0.85137,"best_task_score":0.92878},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":318.0,"contact_point_centroid":[0.48682,-0.02063,0.0309],"force_p95":38.12451,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":68.77223,"mean_force":4.48126,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48438,-0.00886,0.02054]},{"body_a":"world","body_b":"push_box","contact_count":352.0,"contact_point_centroid":[0.48886,-0.05223,-8e-05],"force_p95":23.56518,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":34.29195,"mean_force":4.56895,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48457,-0.01021,0.02059]},{"body_a":"world","body_b":"push_box","contact_count":948.0,"contact_point_centroid":[0.50849,-0.16236,-2e-05],"force_p95":0.26085,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.38039,"mean_force":0.25958,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49372,-0.12032,0.06079]},{"body_a":"attachment","body_b":"push_box","contact_count":4.0,"contact_point_centroid":[0.50403,-0.13298,0.05003],"force_p95":0.55094,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.64816,"mean_force":0.16204,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49668,-0.12114,0.02011]},{"body_a":"world","body_b":"push_box","contact_count":2292.0,"contact_point_centroid":[0.47924,0.05847,-1e-05],"force_p95":0.24528,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48828,0.06282,0.17064]},{"body_a":"world","body_b":"push_box","contact_count":2784.0,"contact_point_centroid":[0.47924,0.05847,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.47462,0.10942,0.02978]}],"total_contact_groups":6},"final_pose_error":0.01996,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50839,-0.16234,0.02499],"final_tcp_position":[0.49365,-0.11996,0.10046],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47924,0.05847,0.025]},"peak_contact_force":68.77223,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":573.0,"n_steps_budget":1000.0,"object_pos_end":[0.47924,0.05847,0.02499],"object_pos_start":[0.47924,0.05847,0.025],"object_to_goal_dist_end":0.2095,"object_to_goal_dist_start":0.2095,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2292.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.47754,0.12727,0.04111],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07068,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":696.0,"n_steps_budget":1000.0,"object_pos_end":[0.47924,0.05847,0.02499],"object_pos_start":[0.47924,0.05847,0.02499],"object_to_goal_dist_end":0.2095,"object_to_goal_dist_start":0.2095,"object_z_max":0.02499,"peak_contact_force":16.20219,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2784.0,"raw_peak_contact_force":0.24525,"subtask_id":"contact","tcp_end":[0.475,0.09546,0.0238],"tcp_start":[0.47754,0.12727,0.04111],"tcp_to_object_dist_end":0.03725,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":374.0,"n_steps_budget":1000.0,"object_pos_end":[0.50749,-0.1571,0.02496],"object_pos_start":[0.47924,0.05847,0.02499],"object_to_goal_dist_end":0.01032,"object_to_goal_dist_start":0.2095,"object_z_max":0.02627,"peak_contact_force":0.00137,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":670.0,"raw_peak_contact_force":68.77223,"subtask_id":"push","tcp_end":[0.49688,-0.12061,0.02014],"tcp_start":[0.475,0.09546,0.0238],"tcp_to_object_dist_end":0.03831,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":247.0,"n_steps_budget":630.0,"object_pos_end":[0.50839,-0.16234,0.02499],"object_pos_start":[0.50749,-0.1571,0.02496],"object_to_goal_dist_end":0.01492,"object_to_goal_dist_start":0.01032,"object_z_max":0.02513,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":952.0,"raw_peak_contact_force":1.38039,"tcp_end":[0.49365,-0.11996,0.10046],"tcp_start":[0.49688,-0.12061,0.02014],"tcp_to_object_dist_end":0.0878,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.6963,"average_solve_count":135.0,"average_success_count":135.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"contact_1.contact_force":4.26571,"contact_1.contact_speed":0.03255,"push_1.push_depth":0.03346,"push_1.push_speed":0.13421},"optimized_scores":{"best_composite_score":0.77645,"best_fitness_score":0.78645,"best_task_score":0.75242},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":282.0,"contact_point_centroid":[0.55044,-0.10942,-0.00012],"force_p95":74.38096,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":84.64148,"mean_force":27.45667,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51321,-0.06569,0.02078]},{"body_a":"attachment","body_b":"push_box","contact_count":177.0,"contact_point_centroid":[0.52772,-0.07231,0.05144],"force_p95":56.0078,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":65.27792,"mean_force":21.44401,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51372,-0.06412,0.0208]},{"body_a":"push_box","body_b":"link7","contact_count":143.0,"contact_point_centroid":[0.54545,-0.08375,0.05411],"force_p95":55.2653,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":64.53076,"mean_force":30.8486,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50946,-0.07757,0.02079]},{"body_a":"world","body_b":"push_box","contact_count":897.0,"contact_point_centroid":[0.53413,-0.14697,-2e-05],"force_p95":0.3599,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.3657,"mean_force":0.27035,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4925,-0.1225,0.06449]},{"body_a":"attachment","body_b":"push_box","contact_count":15.0,"contact_point_centroid":[0.51152,-0.12507,0.05226],"force_p95":1.45386,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.60889,"mean_force":0.81677,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49362,-0.12383,0.02688]},{"body_a":"world","body_b":"push_box","contact_count":2080.0,"contact_point_centroid":[0.54443,-0.02558,-1e-05],"force_p95":0.24529,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51762,0.02423,0.17247]},{"body_a":"world","body_b":"push_box","contact_count":2960.0,"contact_point_centroid":[0.54443,-0.02558,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.53624,0.02943,0.02984]}],"total_contact_groups":7},"final_pose_error":0.01995,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.53256,-0.14692,0.02499],"final_tcp_position":[0.49253,-0.12216,0.10214],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.54443,-0.02558,0.025]},"peak_contact_force":84.64148,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":520.0,"n_steps_budget":1000.0,"object_pos_end":[0.54443,-0.02558,0.02499],"object_pos_start":[0.54443,-0.02558,0.025],"object_to_goal_dist_end":0.13211,"object_to_goal_dist_start":0.13211,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2080.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.53717,0.04944,0.04292],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07748,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":740.0,"n_steps_budget":960.0,"object_pos_end":[0.54443,-0.02558,0.02499],"object_pos_start":[0.54443,-0.02558,0.02499],"object_to_goal_dist_end":0.13211,"object_to_goal_dist_start":0.13211,"object_z_max":0.02499,"peak_contact_force":21.39067,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2960.0,"raw_peak_contact_force":0.24525,"subtask_id":"contact","tcp_end":[0.53889,0.0114,0.02236],"tcp_start":[0.53717,0.04944,0.04292],"tcp_to_object_dist_end":0.03748,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":243.0,"n_steps_budget":810.0,"object_pos_end":[0.53354,-0.14275,0.02852],"object_pos_start":[0.54443,-0.02558,0.02499],"object_to_goal_dist_end":0.03449,"object_to_goal_dist_start":0.13211,"object_z_max":0.02946,"peak_contact_force":1.0872,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":602.0,"raw_peak_contact_force":84.64148,"subtask_id":"push","tcp_end":[0.49575,-0.12282,0.02182],"tcp_start":[0.53889,0.0114,0.02236],"tcp_to_object_dist_end":0.04325,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":248.0,"n_steps_budget":630.0,"object_pos_end":[0.53256,-0.14692,0.02499],"object_pos_start":[0.53354,-0.14275,0.02852],"object_to_goal_dist_end":0.03271,"object_to_goal_dist_start":0.03449,"object_z_max":0.02852,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":912.0,"raw_peak_contact_force":2.3657,"tcp_end":[0.49253,-0.12216,0.10214],"tcp_start":[0.49575,-0.12282,0.02182],"tcp_to_object_dist_end":0.09038,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```