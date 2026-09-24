## Search State

- **Seed**: 7
- **Iteration**: 9 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 8 | approach → approach → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | pose_tolerance | force_exceeded | pose_tolerance | 4 | 0.7812 | 0.62 | ❌ rejected |
| 7 | approach → approach → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | pose_tolerance | force_exceeded | pose_tolerance | 3 | 0.9102 | 0.81 | ✅ accepted |
| 6 | approach → approach → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | pose_tolerance | force_exceeded | pose_tolerance | 3 | 0.7131 | 0.63 | ✅ accepted |
| 5 | approach → approach → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | pose_tolerance | force_exceeded | pose_tolerance | 4 | 0.4717 | 0.36 | ❌ rejected |
| 4 | approach → approach → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | pose_tolerance | force_exceeded | pose_tolerance | 4 | 0.7828 | 0.62 | ✅ accepted |

**Proposal policy**: task_score is 0.62 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.781) — your mutation base

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
    - 0.05
    tolerance: 0.01
    orientation:
      mode: keep_current
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
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.15
      axis: task_goal_direction
      mode: add_to_offset
      sign: positive
    tolerance: 0.005
    orientation:
      mode: keep_current
  parameters:
    push_depth:
      type: scalar
      range:
      - 0.05
      - 0.25
      default: 0.15
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
  - target: source=yaml, anchor=task_object, entity=push_box, offset=[0.0, 0.08, 0.05], tolerance=0.01
  - orientation: mode=keep_current
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
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.15, mode=add_to_offset, sign=positive}, tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_depth: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (scale)
  - retries: max_attempts=2, strategy=offset_target, offset=[0.005, 0.0, 0.0]

## Design Metrics

- **Composite score**: 0.781
- **task_score** (E): 0.618
- **fitness_score**: 0.678  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.333
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.230

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| descend_to_approach | 1.00 | 1.00 | 0.2453 |
| approach_to_contact | 1.00 | 1.00 | 0.0636 |
| push_toward_goal | 1.00 | 1.00 | 0.1883 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| descend_to_approach | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.509, 0.101, 0.081) | (0.513, 0.027, 0.025)→(0.513, 0.027, 0.025) | 0.180→0.180 | 1.00 / 4.000 | 0.245 | 0.245 |
| approach_to_contact | approach | 1.00 / force_exceeded | (0.509, 0.101, 0.081)→(0.508, 0.064, 0.030) | (0.513, 0.027, 0.025)→(0.513, 0.027, 0.025) | 0.180→0.180 | 1.00 / 5.000 | 25315.704 | 0.245 |
| push_toward_goal | push | 1.00 / step_budget | (0.508, 0.064, 0.030)→(0.491, -0.121, 0.025) | (0.513, 0.027, 0.025)→(0.533, -0.096, 0.026) | 0.180→0.065 | 1.00 / 3.667 | 2.701 | 27.011 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.882
- lateral_force_integral: None
- approach_alignment: 0.701
- goal_progress: 0.781
- terminal_score: 0.781
- phase_score: 0.740
- phase_breakdown.approach_score: 0.418
- phase_breakdown.push_score: 0.858
- phase_breakdown.contact_score: 0.757

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.756
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.781
- **Median Q (composite search score)**: 0.775
- **K-run variance**: 0.0038
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.404


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.29932,"average_solve_count":147.0,"average_success_count":147.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_contact.contact_force_threshold":18.55395,"descend_to_approach.speed":0.23754,"push_toward_goal.push_depth":0.21682,"push_toward_goal.push_speed":0.13029},"optimized_scores":{"best_composite_score":0.77517,"best_fitness_score":0.67184,"best_task_score":0.60528},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":750.0,"contact_point_centroid":[0.51057,-0.01502,0.04431],"force_p95":17.08475,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":26.16726,"mean_force":3.95437,"phase_index":2.0,"phase_name":"push_toward_goal","phase_type":"push","tcp_position_centroid":[0.49939,-0.0075,0.02545]},{"body_a":"world","body_b":"push_box","contact_count":1471.0,"contact_point_centroid":[0.53795,-0.0412,-6e-05],"force_p95":9.19513,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":14.17768,"mean_force":2.5088,"phase_index":2.0,"phase_name":"push_toward_goal","phase_type":"push","tcp_position_centroid":[0.49819,-0.02369,0.02548]},{"body_a":"world","body_b":"push_box","contact_count":3744.0,"contact_point_centroid":[0.51501,0.04767,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"descend_to_approach","phase_type":"approach","tcp_position_centroid":[0.50439,0.06025,0.1888]},{"body_a":"world","body_b":"push_box","contact_count":1712.0,"contact_point_centroid":[0.51501,0.04767,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"approach_to_contact","phase_type":"approach","tcp_position_centroid":[0.50905,0.10185,0.05246]}],"total_contact_groups":4},"final_pose_error":0.01266,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.52477,-0.07578,0.02492],"final_tcp_position":[0.49055,-0.12032,0.02504],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.51501,0.04767,0.025]},"peak_contact_force":75893.53664,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":936.0,"n_steps_budget":1000.0,"object_pos_end":[0.51501,0.04767,0.02499],"object_pos_start":[0.51501,0.04767,0.025],"object_to_goal_dist_end":0.19823,"object_to_goal_dist_start":0.19823,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"descend_to_approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3744.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.51072,0.12079,0.08055],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.09193,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":428.0,"n_steps_budget":600.0,"object_pos_end":[0.51501,0.04767,0.02499],"object_pos_start":[0.51501,0.04767,0.02499],"object_to_goal_dist_end":0.19823,"object_to_goal_dist_start":0.19823,"object_z_max":0.02499,"peak_contact_force":75893.53664,"phase_name":"approach_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1712.0,"raw_peak_contact_force":0.24525,"subtask_id":"contact","tcp_end":[0.51013,0.08461,0.02985],"tcp_start":[0.51072,0.12079,0.08055],"tcp_to_object_dist_end":0.03758,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52477,-0.07578,0.02492],"object_pos_start":[0.51501,0.04767,0.02499],"object_to_goal_dist_end":0.07825,"object_to_goal_dist_start":0.19823,"object_z_max":0.02984,"peak_contact_force":0.24644,"phase_name":"push_toward_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2221.0,"raw_peak_contact_force":26.16726,"subtask_id":"push","tcp_end":[0.49055,-0.12032,0.02504],"tcp_start":[0.51013,0.08461,0.02985],"tcp_to_object_dist_end":0.05617,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.29605,"average_solve_count":152.0,"average_success_count":152.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_contact.contact_force_threshold":10.84697,"descend_to_approach.speed":0.23503,"push_toward_goal.push_depth":0.23317,"push_toward_goal.push_speed":0.13806},"optimized_scores":{"best_composite_score":0.85971,"best_fitness_score":0.75637,"best_task_score":0.78115},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":769.0,"contact_point_centroid":[0.48992,-0.01938,0.04094],"force_p95":21.64632,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":34.47191,"mean_force":4.97286,"phase_index":2.0,"phase_name":"push_toward_goal","phase_type":"push","tcp_position_centroid":[0.482,-0.00968,0.02666]},{"body_a":"world","body_b":"push_box","contact_count":1306.0,"contact_point_centroid":[0.50919,-0.04424,-6e-05],"force_p95":12.04073,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":24.81316,"mean_force":3.42229,"phase_index":2.0,"phase_name":"push_toward_goal","phase_type":"push","tcp_position_centroid":[0.48154,-0.0042,0.02676]},{"body_a":"world","body_b":"push_box","contact_count":3768.0,"contact_point_centroid":[0.47924,0.05847,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"descend_to_approach","phase_type":"approach","tcp_position_centroid":[0.48747,0.06538,0.18906]},{"body_a":"world","body_b":"push_box","contact_count":1524.0,"contact_point_centroid":[0.47924,0.05847,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"approach_to_contact","phase_type":"approach","tcp_position_centroid":[0.47461,0.11306,0.05442]}],"total_contact_groups":4},"final_pose_error":0.01597,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.53279,-0.11827,0.02956],"final_tcp_position":[0.49293,-0.12229,0.02596],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47924,0.05847,0.025]},"peak_contact_force":34.47191,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":942.0,"n_steps_budget":1000.0,"object_pos_end":[0.47924,0.05847,0.02499],"object_pos_start":[0.47924,0.05847,0.025],"object_to_goal_dist_end":0.2095,"object_to_goal_dist_start":0.2095,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"descend_to_approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3768.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.47684,0.131,0.08117],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.09177,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":381.0,"n_steps_budget":600.0,"object_pos_end":[0.47924,0.05847,0.02499],"object_pos_start":[0.47924,0.05847,0.02499],"object_to_goal_dist_end":0.2095,"object_to_goal_dist_start":0.2095,"object_z_max":0.02499,"peak_contact_force":27.76193,"phase_name":"approach_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1524.0,"raw_peak_contact_force":0.24525,"subtask_id":"contact","tcp_end":[0.47503,0.09543,0.03077],"tcp_start":[0.47684,0.131,0.08117],"tcp_to_object_dist_end":0.03764,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53279,-0.11827,0.02956],"object_pos_start":[0.47924,0.05847,0.02499],"object_to_goal_dist_end":0.04585,"object_to_goal_dist_start":0.2095,"object_z_max":0.02985,"peak_contact_force":7.61251,"phase_name":"push_toward_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2075.0,"raw_peak_contact_force":34.47191,"subtask_id":"push","tcp_end":[0.49293,-0.12229,0.02596],"tcp_start":[0.47503,0.09543,0.03077],"tcp_to_object_dist_end":0.04022,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.25714,"average_solve_count":175.0,"average_success_count":175.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_contact.contact_force_threshold":12.68651,"descend_to_approach.speed":0.18438,"push_toward_goal.push_depth":0.16111,"push_toward_goal.push_speed":0.08572},"optimized_scores":{"best_composite_score":0.70873,"best_fitness_score":0.6054,"best_task_score":0.46758},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":648.0,"contact_point_centroid":[0.52893,-0.04641,0.04734],"force_p95":12.83477,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":20.39502,"mean_force":3.53333,"phase_index":2.0,"phase_name":"push_toward_goal","phase_type":"push","tcp_position_centroid":[0.51803,-0.03658,0.02356]},{"body_a":"world","body_b":"push_box","contact_count":2070.0,"contact_point_centroid":[0.55094,-0.08399,-3e-05],"force_p95":6.87504,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":11.26136,"mean_force":1.5382,"phase_index":2.0,"phase_name":"push_toward_goal","phase_type":"push","tcp_position_centroid":[0.50719,-0.06676,0.02359]},{"body_a":"push_box","body_b":"link7","contact_count":29.0,"contact_point_centroid":[0.54829,-0.04495,0.05616],"force_p95":7.75701,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":8.32226,"mean_force":4.86822,"phase_index":2.0,"phase_name":"push_toward_goal","phase_type":"push","tcp_position_centroid":[0.51134,-0.05457,0.02333]},{"body_a":"world","body_b":"push_box","contact_count":3320.0,"contact_point_centroid":[0.54443,-0.02558,-1e-05],"force_p95":0.24527,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"descend_to_approach","phase_type":"approach","tcp_position_centroid":[0.51801,0.02524,0.19042]},{"body_a":"world","body_b":"push_box","contact_count":1892.0,"contact_point_centroid":[0.54443,-0.02558,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"approach_to_contact","phase_type":"approach","tcp_position_centroid":[0.53721,0.03092,0.05267]}],"total_contact_groups":5},"final_pose_error":0.02168,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.5429,-0.09425,0.02499],"final_tcp_position":[0.48819,-0.11941,0.02349],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.54443,-0.02558,0.025]},"peak_contact_force":25.81413,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":830.0,"n_steps_budget":1000.0,"object_pos_end":[0.54443,-0.02558,0.02499],"object_pos_start":[0.54443,-0.02558,0.025],"object_to_goal_dist_end":0.13211,"object_to_goal_dist_start":0.13211,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"descend_to_approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3320.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.5383,0.05104,0.08188],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.09563,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":473.0,"n_steps_budget":600.0,"object_pos_end":[0.54443,-0.02558,0.02499],"object_pos_start":[0.54443,-0.02558,0.02499],"object_to_goal_dist_end":0.13211,"object_to_goal_dist_start":0.13211,"object_z_max":0.02499,"peak_contact_force":25.81413,"phase_name":"approach_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1892.0,"raw_peak_contact_force":0.24525,"subtask_id":"contact","tcp_end":[0.53921,0.01141,0.02826],"tcp_start":[0.5383,0.05104,0.08188],"tcp_to_object_dist_end":0.03751,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5429,-0.09425,0.02499],"object_pos_start":[0.54443,-0.02558,0.02499],"object_to_goal_dist_end":0.07034,"object_to_goal_dist_start":0.13211,"object_z_max":0.0284,"peak_contact_force":0.24525,"phase_name":"push_toward_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2747.0,"raw_peak_contact_force":20.39502,"subtask_id":"push","tcp_end":[0.48819,-0.11941,0.02349],"tcp_start":[0.53921,0.01141,0.02826],"tcp_to_object_dist_end":0.06023,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```