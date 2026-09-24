## Search State

- **Seed**: 5
- **Iteration**: 7 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 6 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 7 | 0.6200 | 1.00 | ❌ rejected |
| 5 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 7 | 0.6200 | 1.00 | ❌ rejected |
| 4 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 6 | 0.6700 | 1.00 | ❌ rejected |
| 3 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 7 | -0.0520 | 0.33 | ❌ rejected |
| 2 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 7 | 0.7311 | 1.00 | ✅ accepted |

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

## Current Skill (Q=0.620) — your mutation base

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
  guards:
  - id: contact_force_guard
    when: during_phase
    predicate: force_below
    threshold: 30.0
    on_failure: abort
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
  guards:
  - id: push_force_guard
    when: during_phase
    predicate: force_below
    threshold: 30.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: reduce_speed
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
  - guards:
    - id=contact_force_guard, when=during_phase, predicate=force_below, on_failure=abort, threshold=30.0
- **push_1** (`push`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.2, mode=add_to_offset, sign=positive}, tolerance=0.05
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=world_x, tolerance=0.1
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_pose_tol: status=consumed; consumers=termination.pose_tolerance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=push_force_guard, when=during_phase, predicate=force_below, on_failure=retry, threshold=30.0
  - retries: max_attempts=2, strategy=reduce_speed

## Design Metrics

- **Composite score**: 0.620
- **task_score** (E): 1.000
- **fitness_score**: 1.000  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.380

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 0.00 | 1.00 | 0.3166 |
| contact_1 | 0.00 | 1.00 | 0.0001 |
| push_1 | 0.00 | 1.00 | 0.0001 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 0.00 / step_budget | (-0.129, 0.249, 0.314)→(0.065, 0.075, 0.135) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 1.333 | 387.492 | 1230.131 |
| contact_1 | descend | 0.00 / guard_failure | (0.065, 0.075, 0.135)→(0.065, 0.075, 0.135) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 1.333 | 61.622 | 61.622 |
| push_1 | push | 0.00 / guard_failure | (0.065, 0.075, 0.135)→(0.065, 0.075, 0.135) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 1.333 | 300.243 | 466.432 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- hinge_angle_ratio: 1.000
- arc_quality: 0.000

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 1.000
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.620
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.358


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":7.0,"average_failure_rate":0.14894,"average_mean_iterations":36.70213,"average_solve_count":47.0,"average_success_count":40.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.16142,"approach_1.approach_speed":0.42408,"contact_1.contact_force_threshold":23.78911,"contact_1.contact_speed":0.01334,"push_1.push_distance":0.2813,"push_1.push_pose_tol":0.05726,"push_1.push_speed":0.1194},"optimized_scores":{"best_composite_score":0.62,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link6","contact_count":13.0,"contact_point_centroid":[0.10637,0.14679,0.4398],"force_p95":987.8074,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1072.72944,"mean_force":518.47371,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.12136,0.24261,0.36224]},{"body_a":"link1","body_b":"link7","contact_count":127.0,"contact_point_centroid":[0.03865,0.03854,0.148],"force_p95":571.32099,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":684.53511,"mean_force":355.1857,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.05894,0.07617,0.13526]},{"body_a":"link0","body_b":"link7","contact_count":62.0,"contact_point_centroid":[0.04277,0.03492,0.13514],"force_p95":471.72786,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":487.13653,"mean_force":386.86644,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.06198,0.07563,0.13274]},{"body_a":"link0","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.04708,0.03086,0.12721],"force_p95":476.5371,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":476.61284,"mean_force":475.79543,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.06776,0.07176,0.1304]},{"body_a":"door_panel","body_b":"link4","contact_count":11.0,"contact_point_centroid":[0.23455,-0.09086,0.59973],"force_p95":234.94543,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":239.91579,"mean_force":168.13904,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.14353,0.03077,0.16266]},{"body_a":"door_panel","body_b":"link7","contact_count":34.0,"contact_point_centroid":[0.21344,0.08243,0.36723],"force_p95":130.98896,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":149.45757,"mean_force":98.57859,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.18896,0.16129,0.33565]},{"body_a":"link0","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.04703,0.03082,0.12724],"force_p95":53.41044,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":53.41044,"mean_force":53.41044,"phase_index":1.0,"phase_name":"contact_1","phase_type":"descend","tcp_position_centroid":[0.06756,0.07175,0.13031]},{"body_a":"world","body_b":"door_panel","contact_count":1060.0,"contact_point_centroid":[0.31493,0.15131,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.01057,0.25038,0.30374]},{"body_a":"world","body_b":"door_panel","contact_count":4.0,"contact_point_centroid":[0.42443,0.01456,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.06775,0.07176,0.1304]}],"total_contact_groups":9},"final_pose_error":0.12384,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.06804,0.0717,0.13052],"hinge_angle":1.13377,"initial_hinge_angle":0.10647,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.10647,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":1072.72944,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1078.0,"n_steps_budget":690.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":400.92079,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1307.0,"raw_peak_contact_force":1072.72944,"subtask_id":"tcp_contact","tcp_end":[0.06756,0.07175,0.13031],"tcp_start":[-0.12487,0.25136,0.29683],"tcp_to_object_dist_end":0.16338,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":53.41044,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1.0,"raw_peak_contact_force":53.41044,"tcp_end":[0.06765,0.07177,0.13035],"tcp_start":[0.06756,0.07175,0.13031],"tcp_to_object_dist_end":0.16345,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":3.0,"n_steps_budget":660.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":474.91796,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":7.0,"raw_peak_contact_force":476.61284,"subtask_id":"hinge_progress","tcp_end":[0.06804,0.0717,0.13052],"tcp_start":[0.06789,0.07174,0.13046],"tcp_to_object_dist_end":0.16373,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `fbf559b1c4ad02fb5807d56e72eb3a3daf90ab4647e10f958130a5b70ea34720`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":6.0,"average_failure_rate":0.13636,"average_mean_iterations":34.56818,"average_solve_count":44.0,"average_success_count":38.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.15184,"approach_1.approach_speed":0.5697,"contact_1.contact_force_threshold":20.59796,"contact_1.contact_speed":0.04006,"push_1.push_distance":0.23282,"push_1.push_pose_tol":0.06915,"push_1.push_speed":0.12631},"optimized_scores":{"best_composite_score":0.62,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link6","contact_count":14.0,"contact_point_centroid":[0.10428,0.176,0.42316],"force_p95":1303.87306,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1316.86873,"mean_force":778.47375,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.10809,0.25886,0.34317]},{"body_a":"link1","body_b":"link7","contact_count":46.0,"contact_point_centroid":[0.04287,0.03329,0.14845],"force_p95":687.53644,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":704.95454,"mean_force":454.96766,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.06269,0.06681,0.12694]},{"body_a":"link0","body_b":"link7","contact_count":70.0,"contact_point_centroid":[0.04624,0.03069,0.1348],"force_p95":627.91047,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":653.00383,"mean_force":531.7075,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.06525,0.06876,0.1206]},{"body_a":"door_panel","body_b":"link7","contact_count":57.0,"contact_point_centroid":[0.1765,0.14331,0.32807],"force_p95":207.19969,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":501.58639,"mean_force":90.12127,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.13238,0.21156,0.29618]},{"body_a":"link0","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.04679,0.03003,0.13366],"force_p95":425.55413,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":425.81129,"mean_force":422.94289,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.06893,0.06615,0.11904]},{"body_a":"door_panel","body_b":"link4","contact_count":21.0,"contact_point_centroid":[0.27462,-0.10759,0.50312],"force_p95":224.66122,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":225.68873,"mean_force":113.93791,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.11509,0.0595,0.1466]},{"body_a":"link0","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.0467,0.02998,0.13368],"force_p95":65.52787,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":65.52787,"mean_force":65.52787,"phase_index":1.0,"phase_name":"contact_1","phase_type":"descend","tcp_position_centroid":[0.06871,0.06607,0.11903]},{"body_a":"world","body_b":"door_panel","contact_count":844.0,"contact_point_centroid":[0.31072,0.16697,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[-0.00069,0.24616,0.30671]},{"body_a":"world","body_b":"door_panel","contact_count":4.0,"contact_point_centroid":[0.42555,0.01411,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.06894,0.06615,0.11905]}],"total_contact_groups":9},"final_pose_error":0.09044,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.06904,0.06622,0.11897],"hinge_angle":1.13978,"initial_hinge_angle":0.01332,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.01332,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":1316.86873,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":962.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":397.12308,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1052.0,"raw_peak_contact_force":1316.86873,"subtask_id":"tcp_contact","tcp_end":[0.06871,0.06607,0.11903],"tcp_start":[-0.14993,0.23582,0.29351],"tcp_to_object_dist_end":0.15249,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":65.52787,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1.0,"raw_peak_contact_force":65.52787,"tcp_end":[0.06884,0.06611,0.11906],"tcp_start":[0.06871,0.06607,0.11903],"tcp_to_object_dist_end":0.15259,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":3.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":425.81129,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":7.0,"raw_peak_contact_force":425.81129,"subtask_id":"hinge_progress","tcp_end":[0.06904,0.06622,0.11897],"tcp_start":[0.06901,0.06619,0.11902],"tcp_to_object_dist_end":0.15266,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `99847c10f6e36b39751f22a6e7e446b09a6cc2d5cdc4857751225dedfedfe952`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":5.0,"average_failure_rate":0.11364,"average_mean_iterations":30.93182,"average_solve_count":44.0,"average_success_count":39.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.15048,"approach_1.approach_speed":0.62162,"contact_1.contact_force_threshold":18.6772,"contact_1.contact_speed":0.0821,"push_1.push_distance":0.32116,"push_1.push_pose_tol":0.05825,"push_1.push_speed":0.08527},"optimized_scores":{"best_composite_score":0.62,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link6","contact_count":23.0,"contact_point_centroid":[0.10137,0.1799,0.44228],"force_p95":1085.82935,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1300.79342,"mean_force":488.67232,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[-0.00131,0.25715,0.41169]},{"body_a":"link0","body_b":"link7","contact_count":140.0,"contact_point_centroid":[0.0476,0.03193,0.11735],"force_p95":719.00854,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":806.40794,"mean_force":456.26305,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.05105,0.0911,0.15525]},{"body_a":"link1","body_b":"link7","contact_count":80.0,"contact_point_centroid":[0.04034,0.03704,0.17299],"force_p95":574.87953,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":647.0652,"mean_force":296.3387,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.05226,0.0884,0.15602]},{"body_a":"link1","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.04454,0.03219,0.17422],"force_p95":488.01733,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":496.87272,"mean_force":408.31887,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.05776,0.08663,0.15629]},{"body_a":"door_panel","body_b":"link7","contact_count":36.0,"contact_point_centroid":[0.19505,0.11813,0.34941],"force_p95":318.86515,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":424.67743,"mean_force":124.25752,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.16875,0.19855,0.32112]},{"body_a":"door_panel","body_b":"link4","contact_count":11.0,"contact_point_centroid":[0.21766,-0.07306,0.61073],"force_p95":287.57326,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":296.57517,"mean_force":199.39877,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.15248,0.05895,0.17201]},{"body_a":"link0","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.04894,0.03248,0.10965],"force_p95":235.78531,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":235.78531,"mean_force":235.78531,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.05769,0.0866,0.15626]},{"body_a":"link1","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.04448,0.03219,0.17414],"force_p95":65.92677,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":65.92677,"mean_force":65.92677,"phase_index":1.0,"phase_name":"contact_1","phase_type":"descend","tcp_position_centroid":[0.05762,0.08654,0.15614]},{"body_a":"world","body_b":"door_panel","contact_count":820.0,"contact_point_centroid":[0.31852,0.15511,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.0165,0.24593,0.31344]},{"body_a":"link0","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.04888,0.03244,0.10972],"force_p95":0.0,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"contact_1","phase_type":"descend","tcp_position_centroid":[0.05762,0.08654,0.15614]}],"total_contact_groups":10},"final_pose_error":0.13455,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.05795,0.08648,0.15624],"hinge_angle":1.14739,"initial_hinge_angle":0.04367,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.04367,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":1300.79342,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":992.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":364.43133,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1110.0,"raw_peak_contact_force":1300.79342,"subtask_id":"tcp_contact","tcp_end":[0.05762,0.08654,0.15614],"tcp_start":[-0.11083,0.2584,0.35309],"tcp_to_object_dist_end":0.18759,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":65.92677,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2.0,"raw_peak_contact_force":65.92677,"tcp_end":[0.05769,0.0866,0.15626],"tcp_start":[0.05762,0.08654,0.15614],"tcp_to_object_dist_end":0.18774,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":3.0,"n_steps_budget":990.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3.0,"raw_peak_contact_force":496.87272,"subtask_id":"hinge_progress","tcp_end":[0.05795,0.08648,0.15624],"tcp_start":[0.05801,0.08663,0.15634],"tcp_to_object_dist_end":0.18775,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```