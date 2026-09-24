## Search State

- **Seed**: 5
- **Iteration**: 9 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 8 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 7 | 0.9533 | 1.00 | ❌ rejected |
| 7 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 7 | 0.9533 | 1.00 | ✅ accepted |
| 6 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 7 | 0.6200 | 1.00 | ❌ rejected |
| 5 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 7 | 0.6200 | 1.00 | ❌ rejected |
| 4 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 6 | 0.6700 | 1.00 | ❌ rejected |

**Proposal policy**: task_score is near-perfect (1.00). Preserve useful working parts and make only evidence-backed refinements. A HOLD is acceptable if you genuinely cannot find a better structure.

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

- Task name: door_push
- target_hinge_angle: 0.524 rad (task success = realised hinge-angle delta ratio; not TCP proximity)
- Goal tolerance: 0.05 m
- Expressivity sigma: 0.15 m
- Expressivity threshold: 0.3
- Force limit: 30.0 N
- Primary evaluation target: **hinge angle delta ratio (realised hinge motion / target_hinge_angle)**

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
| `object` | offset from object initial position | approach/contact targets near object |
| `goal` | offset from task goal position | final destination targets |
| `fixture` | offset from fixture pose | approach/contact targets near fixture |

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

## Current Skill (Q=0.953) — your mutation base

```yaml
skill: door_push
dsl_version: 2
subtasks:
- id: tcp_contact
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.1
  weight: 0.3
- id: hinge_progress
  target_entity: hinge
  metric: hinge_angle
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
    - 0.1
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: replace
    approach_speed:
      type: scalar
      range:
      - 0.1
      - 1.0
      default: 0.5
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: approach_pose_guard
    when: after_phase
    predicate: pose_within_tolerance
    threshold: 0.02
    on_failure: retry
  retries:
    max_attempts: 1
    strategy: reduce_speed
  subtask_id: tcp_contact
- id: contact_1
  type: descend
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
    orientation:
      mode: keep_current
  parameters:
    contact_force_threshold:
      type: scalar
      range:
      - 5.0
      - 30.0
      default: 10.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    contact_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
- id: push_1
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.2
      axis: task_goal_direction
      mode: add_to_offset
      sign: positive
    tolerance: 0.05
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: world_x
      tolerance: 0.1
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.1
      - 0.5
      default: 0.2
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_pose_tol:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.02
      - 0.2
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: hinge_progress

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.1], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
    - approach_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=approach_pose_guard, when=after_phase, predicate=pose_within_tolerance, on_failure=retry, threshold=0.02
  - retries: max_attempts=1, strategy=reduce_speed
- **contact_1** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - contact_force_threshold: status=consumed; consumers=termination.force_threshold (replace)
    - contact_speed: status=consumed; consumers=generator.speed (replace)
- **push_1** (`push`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.2, mode=add_to_offset, sign=positive}, tolerance=0.05
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=world_x, tolerance=0.1
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_pose_tol: status=consumed; consumers=termination.pose_tolerance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: 0.953
- **task_score** (E): 1.000
- **fitness_score**: 1.000  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.333
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.380

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 0.00 | 0.67 | 0.3500 |
| contact_1 | 1.00 | 1.00 | 0.0054 |
| push_1 | 0.67 | 0.33 | 0.0457 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 0.00 / step_budget | (-0.114, 0.261, 0.332)→(0.057, 0.031, 0.142) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 0.67 / 1.333 | 248.967 | 2102.233 |
| contact_1 | descend | 1.00 / force_exceeded | (0.057, 0.031, 0.142)→(0.054, 0.032, 0.138) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 1.667 | 48.103 | 48.103 |
| push_1 | push | 0.67 / step_budget | (0.054, 0.032, 0.138)→(0.052, 0.018, 0.135) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 0.33 / 1.000 | 188.535 | 620.649 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- hinge_angle_ratio: 1.000
- arc_quality: 0.333

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 1.000
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.953
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.314


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `e036e59174e9f4dc4d090dc26b64c24f51b2862ad33098baa3e34b1ab5217b2c`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"hinge_delta_deg":10.0,"object_xy_delta":[0.0,0.0]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `121441f93055d9c3a0317d86ccf3c4d50a1368e9262fdd196bc29f47a537ab6f`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":6.0,"average_failure_rate":0.06667,"average_mean_iterations":20.63333,"average_solve_count":90.0,"average_success_count":84.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.1493,"approach_1.approach_speed":0.7784,"contact_1.contact_force_threshold":14.27958,"contact_1.contact_speed":0.04242,"push_1.push_distance":0.20908,"push_1.push_pose_tol":0.06622,"push_1.push_speed":0.10527},"optimized_scores":{"best_composite_score":0.95333,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":20.0,"contact_point_centroid":[0.02886,0.42348,-0.00792],"force_p95":3962.66172,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":4448.43348,"mean_force":820.47498,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.16149,0.43031,0.05952]},{"body_a":"world","body_b":"link5","contact_count":11.0,"contact_point_centroid":[0.0162,0.46052,-0.0025],"force_p95":1979.1503,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":2152.16684,"mean_force":988.91869,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.15671,0.43262,0.06599]},{"body_a":"link0","body_b":"link6","contact_count":829.0,"contact_point_centroid":[0.05016,-0.03437,0.08914],"force_p95":591.47228,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1199.03691,"mean_force":566.55839,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[-0.00294,-0.12911,0.08827]},{"body_a":"door_panel","body_b":"link7","contact_count":26.0,"contact_point_centroid":[0.42694,0.13952,0.06134],"force_p95":1047.17875,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1169.92506,"mean_force":391.04274,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.35816,0.16354,0.02312]},{"body_a":"door_frame","body_b":"link5","contact_count":12.0,"contact_point_centroid":[0.47688,0.2139,0.13932],"force_p95":1123.2603,"geom_a":"door_frame_hinge_post","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1157.10094,"mean_force":577.53412,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.36012,0.14626,0.02301]},{"body_a":"world","body_b":"link5","contact_count":801.0,"contact_point_centroid":[0.15765,-0.13266,-4e-05],"force_p95":139.0929,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":951.26735,"mean_force":122.46187,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[-0.00304,-0.12926,0.08804]},{"body_a":"door_panel","body_b":"link5","contact_count":4.0,"contact_point_centroid":[0.44674,0.12178,0.12836],"force_p95":873.09506,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":894.53153,"mean_force":703.10157,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.32191,0.08724,0.01999]},{"body_a":"link0","body_b":"link7","contact_count":21.0,"contact_point_centroid":[0.02608,-0.05498,0.10982],"force_p95":694.88649,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":706.74748,"mean_force":521.2772,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.04092,-0.09671,0.09964]},{"body_a":"door_panel","body_b":"link6","contact_count":17.0,"contact_point_centroid":[0.20507,0.14396,0.31089],"force_p95":118.58762,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":122.29737,"mean_force":59.40469,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.12794,0.23288,0.26602]},{"body_a":"link0","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.0358,-0.04467,0.12447],"force_p95":14.61855,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":14.61855,"mean_force":14.61855,"phase_index":1.0,"phase_name":"contact_1","phase_type":"descend","tcp_position_centroid":[0.05792,-0.08339,0.1037]},{"body_a":"door_panel","body_b":"link4","contact_count":646.0,"contact_point_centroid":[0.37589,-0.02401,0.40737],"force_p95":6.77863,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":8.88015,"mean_force":5.41829,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[-0.00333,-0.12927,0.0867]},{"body_a":"world","body_b":"door_panel","contact_count":1012.0,"contact_point_centroid":[0.30791,0.15759,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.0349,0.27654,0.30176]},{"body_a":"world","body_b":"door_panel","contact_count":144.0,"contact_point_centroid":[0.41477,0.0188,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"contact_1","phase_type":"descend","tcp_position_centroid":[0.0604,-0.08511,0.10972]},{"body_a":"world","body_b":"door_panel","contact_count":548.0,"contact_point_centroid":[0.412,0.02012,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[-0.00129,-0.12783,0.08858]}],"total_contact_groups":14},"final_pose_error":0.24925,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[-0.00394,-0.12967,0.08217],"hinge_angle":1.06507,"initial_hinge_angle":0.10647,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.10647,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":4448.43348,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":962.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1102.0,"raw_peak_contact_force":4448.43348,"subtask_id":"tcp_contact","tcp_end":[0.06626,-0.08751,0.11649],"tcp_start":[-0.0962,0.27451,0.32021],"tcp_to_object_dist_end":0.16006,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":261.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":14.61855,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":145.0,"raw_peak_contact_force":14.61855,"tcp_end":[0.0579,-0.08337,0.10367],"tcp_start":[0.06626,-0.08751,0.11649],"tcp_to_object_dist_end":0.14509,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":879.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":565.60382,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2845.0,"raw_peak_contact_force":1199.03691,"subtask_id":"hinge_progress","tcp_end":[-0.00394,-0.12967,0.08217],"tcp_start":[0.0579,-0.08337,0.10367],"tcp_to_object_dist_end":0.15357,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `fbf559b1c4ad02fb5807d56e72eb3a3daf90ab4647e10f958130a5b70ea34720`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":5.0,"average_failure_rate":0.08197,"average_mean_iterations":25.18033,"average_solve_count":61.0,"average_success_count":56.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.15115,"approach_1.approach_speed":0.6412,"contact_1.contact_force_threshold":5.01038,"contact_1.contact_speed":0.06798,"push_1.push_distance":0.18967,"push_1.push_pose_tol":0.05824,"push_1.push_speed":0.05443},"optimized_scores":{"best_composite_score":0.95333,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link6","contact_count":25.0,"contact_point_centroid":[0.1018,0.18228,0.44289],"force_p95":944.03445,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1123.87869,"mean_force":433.39782,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.01957,0.26028,0.39906]},{"body_a":"link0","body_b":"link7","contact_count":128.0,"contact_point_centroid":[0.04756,0.03319,0.11318],"force_p95":712.32343,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":782.50575,"mean_force":457.35627,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.04904,0.09271,0.15662]},{"body_a":"link1","body_b":"link7","contact_count":83.0,"contact_point_centroid":[0.04043,0.03711,0.17555],"force_p95":609.02525,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":682.95685,"mean_force":319.78881,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.05086,0.09041,0.15775]},{"body_a":"door_panel","body_b":"link7","contact_count":57.0,"contact_point_centroid":[0.17223,0.14859,0.33093],"force_p95":201.70982,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":419.10404,"mean_force":86.32905,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.13054,0.21933,0.30235]},{"body_a":"link1","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.04461,0.03205,0.17689],"force_p95":312.08766,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":334.3761,"mean_force":185.42437,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.0567,0.08843,0.15819]},{"body_a":"door_panel","body_b":"link4","contact_count":11.0,"contact_point_centroid":[0.21686,-0.07066,0.61039],"force_p95":284.885,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":294.93862,"mean_force":201.991,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.15715,0.06643,0.17183]},{"body_a":"link0","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.04927,0.03278,0.10584],"force_p95":218.60462,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":218.60462,"mean_force":218.60462,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.05655,0.08838,0.1581]},{"body_a":"link1","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.04452,0.03207,0.17678],"force_p95":68.0367,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":68.0367,"mean_force":68.0367,"phase_index":1.0,"phase_name":"contact_1","phase_type":"descend","tcp_position_centroid":[0.05647,0.08831,0.15799]},{"body_a":"world","body_b":"door_panel","contact_count":872.0,"contact_point_centroid":[0.3175,0.15866,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.0199,0.24488,0.31139]},{"body_a":"link0","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.0492,0.03273,0.10591],"force_p95":0.0,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"contact_1","phase_type":"descend","tcp_position_centroid":[0.05647,0.08831,0.15799]},{"body_a":"world","body_b":"door_panel","contact_count":8.0,"contact_point_centroid":[0.4266,0.01369,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.05847,0.08882,0.15964]}],"total_contact_groups":11},"final_pose_error":0.04008,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.08612,0.09048,0.16692],"hinge_angle":1.14477,"initial_hinge_angle":0.01332,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.01332,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":1123.87869,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":992.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":383.64421,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1176.0,"raw_peak_contact_force":1123.87869,"subtask_id":"tcp_contact","tcp_end":[0.05647,0.08831,0.15799],"tcp_start":[-0.111,0.25872,0.3506],"tcp_to_object_dist_end":0.1896,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":68.0367,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2.0,"raw_peak_contact_force":68.0367,"tcp_end":[0.05655,0.08838,0.1581],"tcp_start":[0.05647,0.08831,0.15799],"tcp_to_object_dist_end":0.18975,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":20.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":12.0,"raw_peak_contact_force":334.3761,"subtask_id":"hinge_progress","tcp_end":[0.08612,0.09048,0.16692],"tcp_start":[0.05655,0.08838,0.1581],"tcp_to_object_dist_end":0.20849,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `99847c10f6e36b39751f22a6e7e446b09a6cc2d5cdc4857751225dedfedfe952`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":5.0,"average_failure_rate":0.08197,"average_mean_iterations":25.2459,"average_solve_count":61.0,"average_success_count":56.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.16127,"approach_1.approach_speed":0.74972,"contact_1.contact_force_threshold":10.35577,"contact_1.contact_speed":0.03109,"push_1.push_distance":0.21557,"push_1.push_pose_tol":0.02927,"push_1.push_speed":0.11968},"optimized_scores":{"best_composite_score":0.95333,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link6","contact_count":54.0,"contact_point_centroid":[0.1019,0.16931,0.45946],"force_p95":686.33704,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":734.38572,"mean_force":351.31033,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.00313,0.26461,0.38222]},{"body_a":"link0","body_b":"link7","contact_count":120.0,"contact_point_centroid":[0.03933,0.04191,0.11768],"force_p95":647.52297,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":684.07626,"mean_force":390.19276,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.0394,0.09538,0.14904]},{"body_a":"link1","body_b":"link7","contact_count":82.0,"contact_point_centroid":[0.03573,0.04158,0.16843],"force_p95":571.52139,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":603.70909,"mean_force":289.83187,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.04148,0.09439,0.1511]},{"body_a":"link1","body_b":"link7","contact_count":8.0,"contact_point_centroid":[0.04035,0.0372,0.16976],"force_p95":273.12996,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":328.5341,"mean_force":102.03896,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.04967,0.09234,0.15217]},{"body_a":"door_panel","body_b":"link4","contact_count":13.0,"contact_point_centroid":[0.2302,-0.0655,0.58805],"force_p95":274.51247,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":299.01531,"mean_force":196.29951,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.15923,0.09583,0.14983]},{"body_a":"door_panel","body_b":"link7","contact_count":17.0,"contact_point_centroid":[0.2473,0.12296,0.28582],"force_p95":225.85759,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":240.33863,"mean_force":169.2177,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.19259,0.18477,0.24544]},{"body_a":"link0","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.05028,0.03369,0.0943],"force_p95":208.29957,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":219.26271,"mean_force":109.63135,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.0491,0.09243,0.15166]},{"body_a":"link1","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.03998,0.03764,0.16926],"force_p95":61.655,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":61.655,"mean_force":61.655,"phase_index":1.0,"phase_name":"contact_1","phase_type":"descend","tcp_position_centroid":[0.04895,0.09233,0.15152]},{"body_a":"world","body_b":"door_panel","contact_count":868.0,"contact_point_centroid":[0.31701,0.15658,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.01088,0.24536,0.30792]},{"body_a":"link0","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.05019,0.03363,0.09439],"force_p95":0.0,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"contact_1","phase_type":"descend","tcp_position_centroid":[0.04895,0.09233,0.15152]}],"total_contact_groups":10},"final_pose_error":0.03581,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.07447,0.09402,0.15712],"hinge_angle":1.14231,"initial_hinge_angle":0.04367,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.04367,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":734.38572,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":976.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":363.25716,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1154.0,"raw_peak_contact_force":734.38572,"subtask_id":"tcp_contact","tcp_end":[0.04895,0.09233,0.15152],"tcp_start":[-0.1334,0.24894,0.32581],"tcp_to_object_dist_end":0.18406,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":61.655,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2.0,"raw_peak_contact_force":61.655,"tcp_end":[0.04903,0.0924,0.15163],"tcp_start":[0.04895,0.09233,0.15152],"tcp_to_object_dist_end":0.18421,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":20.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":10.0,"raw_peak_contact_force":328.5341,"subtask_id":"hinge_progress","tcp_end":[0.07447,0.09402,0.15712],"tcp_start":[0.04903,0.0924,0.15163],"tcp_to_object_dist_end":0.19766,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```