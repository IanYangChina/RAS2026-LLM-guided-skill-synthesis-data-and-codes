## Search State

- **Seed**: 5
- **Iteration**: 15 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 14 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 7 | 0.9533 | 1.00 | ❌ rejected |
| 13 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 7 | 0.9533 | 1.00 | ❌ rejected |
| 12 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 7 | 0.0708 | 0.12 | ❌ rejected |
| 11 | approach → descend → push | arc_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 8 | 0.3403 | 0.44 | ❌ rejected |
| 10 | approach → descend → push | arc_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 8 | -0.0368 | 0.06 | ❌ rejected |

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
| approach_1 | 0.00 | 0.67 | 0.2485 |
| contact_1 | 1.00 | 1.00 | 0.0035 |
| push_1 | 0.00 | 0.00 | 0.2878 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 0.00 / step_budget | (-0.112, 0.255, 0.277)→(0.054, 0.164, 0.250) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 0.67 / 2.333 | 287.159 | 1171.688 |
| contact_1 | descend | 1.00 / force_exceeded | (0.054, 0.164, 0.250)→(0.055, 0.161, 0.250) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 2.333 | 104.367 | 92.580 |
| push_1 | push | 0.00 / step_budget | (0.055, 0.161, 0.250)→(-0.006, 0.090, 0.241) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 0.00 / 0.000 | 0.000 | 866.674 |

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
- **Final σ (mean)**: 0.272


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":6.0,"average_failure_rate":0.06818,"average_mean_iterations":22.43182,"average_solve_count":88.0,"average_success_count":82.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.13516,"approach_1.approach_speed":0.75432,"contact_1.contact_force_threshold":13.88757,"contact_1.contact_speed":0.04094,"push_1.push_distance":0.22174,"push_1.push_pose_tol":0.04312,"push_1.push_speed":0.09002},"optimized_scores":{"best_composite_score":0.95333,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"link1","body_b":"link5","contact_count":89.0,"contact_point_centroid":[0.01271,0.11859,0.35484],"force_p95":1138.20617,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1772.83346,"mean_force":338.86727,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[-0.0663,0.30842,0.28826]},{"body_a":"door_panel","body_b":"link6","contact_count":33.0,"contact_point_centroid":[0.22244,0.1379,0.27696],"force_p95":1477.77509,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1645.4907,"mean_force":558.76173,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.10172,0.25555,0.24323]},{"body_a":"door_panel","body_b":"link6","contact_count":169.0,"contact_point_centroid":[0.10178,0.2275,0.35529],"force_p95":1010.32079,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1616.67607,"mean_force":627.81308,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[-0.0495,0.31961,0.3162]},{"body_a":"door_panel","body_b":"link5","contact_count":425.0,"contact_point_centroid":[0.10995,0.20268,0.31666],"force_p95":1258.67375,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1302.76204,"mean_force":381.78396,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[-0.0116,0.33565,0.29866]},{"body_a":"door_panel","body_b":"link5","contact_count":81.0,"contact_point_centroid":[0.10457,0.15667,0.5406],"force_p95":919.03451,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1052.43737,"mean_force":412.82616,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[-0.07464,0.28154,0.33851]},{"body_a":"link1","body_b":"link5","contact_count":16.0,"contact_point_centroid":[0.04375,0.11605,0.3546],"force_p95":579.09886,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":656.83944,"mean_force":275.87223,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.0423,0.28306,0.32578]},{"body_a":"link1","body_b":"link5","contact_count":3.0,"contact_point_centroid":[0.00928,0.1233,0.34608],"force_p95":187.30755,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":203.56969,"mean_force":90.57446,"phase_index":1.0,"phase_name":"contact_1","phase_type":"descend","tcp_position_centroid":[-0.0668,0.29496,0.2484]},{"body_a":"door_panel","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.10342,0.25204,0.30882],"force_p95":113.75472,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":113.75472,"mean_force":113.75472,"phase_index":1.0,"phase_name":"contact_1","phase_type":"descend","tcp_position_centroid":[-0.06673,0.29515,0.24878]},{"body_a":"world","body_b":"door_panel","contact_count":1060.0,"contact_point_centroid":[0.30174,0.17592,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[-0.03236,0.27973,0.30418]},{"body_a":"world","body_b":"door_panel","contact_count":4.0,"contact_point_centroid":[0.30039,0.21604,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"contact_1","phase_type":"descend","tcp_position_centroid":[-0.0668,0.29494,0.24837]},{"body_a":"world","body_b":"door_panel","contact_count":876.0,"contact_point_centroid":[0.32046,0.17037,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[-0.02888,0.27176,0.27165]}],"total_contact_groups":11},"final_pose_error":0.31498,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[-0.24383,0.19844,0.20177],"hinge_angle":1.19767,"initial_hinge_angle":0.10647,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.10647,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":1772.83346,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":962.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":473.80731,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1399.0,"raw_peak_contact_force":1772.83346,"subtask_id":"tcp_contact","tcp_end":[-0.06673,0.29515,0.24878],"tcp_start":[-0.14775,0.2353,0.27017],"tcp_to_object_dist_end":0.39174,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":206.99711,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8.0,"raw_peak_contact_force":203.56969,"tcp_end":[-0.06689,0.29466,0.24777],"tcp_start":[-0.06673,0.29515,0.24878],"tcp_to_object_dist_end":0.39075,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1350.0,"raw_peak_contact_force":1645.4907,"subtask_id":"hinge_progress","tcp_end":[-0.24383,0.19844,0.20177],"tcp_start":[-0.06689,0.29466,0.24777],"tcp_to_object_dist_end":0.37356,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `fbf559b1c4ad02fb5807d56e72eb3a3daf90ab4647e10f958130a5b70ea34720`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":24.0,"average_failure_rate":0.3871,"average_mean_iterations":84.91935,"average_solve_count":62.0,"average_success_count":38.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.13703,"approach_1.approach_speed":0.78473,"contact_1.contact_force_threshold":9.21666,"contact_1.contact_speed":0.03899,"push_1.push_distance":0.31691,"push_1.push_pose_tol":0.05291,"push_1.push_speed":0.16249},"optimized_scores":{"best_composite_score":0.95333,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link5","contact_count":41.0,"contact_point_centroid":[0.10195,0.15863,0.54595],"force_p95":988.91091,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1012.20864,"mean_force":482.93921,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[-0.04054,0.27627,0.29915]},{"body_a":"door_panel","body_b":"link6","contact_count":128.0,"contact_point_centroid":[0.10835,0.16543,0.36821],"force_p95":535.12855,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":627.38045,"mean_force":366.15997,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[-0.02069,0.26608,0.30318]},{"body_a":"door_panel","body_b":"link6","contact_count":5.0,"contact_point_centroid":[0.23404,0.04059,0.51468],"force_p95":67.84477,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":68.29351,"mean_force":51.00878,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.15404,0.13872,0.38425]},{"body_a":"door_panel","body_b":"link7","contact_count":15.0,"contact_point_centroid":[0.1194,0.19331,0.29561],"force_p95":16.04094,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":16.18122,"mean_force":13.67901,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.05682,0.25058,0.27318]},{"body_a":"world","body_b":"door_panel","contact_count":724.0,"contact_point_centroid":[0.30121,0.18132,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.00535,0.27986,0.30209]},{"body_a":"world","body_b":"door_panel","contact_count":76.0,"contact_point_centroid":[0.33814,0.0821,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.00074,0.13831,0.27432]}],"total_contact_groups":6},"final_pose_error":0.21666,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[-0.11203,0.0638,0.20288],"hinge_angle":0.57962,"initial_hinge_angle":0.01332,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.01332,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":1012.20864,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":812.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":908.0,"raw_peak_contact_force":1012.20864,"subtask_id":"tcp_contact","tcp_end":[0.14928,0.15219,0.3836],"tcp_start":[-0.07563,0.2612,0.24235],"tcp_to_object_dist_end":0.43885,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":62.58017,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.15256,0.14359,0.38375],"tcp_start":[0.14928,0.15219,0.3836],"tcp_to_object_dist_end":0.43721,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":94.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":81.0,"raw_peak_contact_force":68.29351,"subtask_id":"hinge_progress","tcp_end":[-0.11203,0.0638,0.20288],"tcp_start":[0.15256,0.14359,0.38375],"tcp_to_object_dist_end":0.24037,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `99847c10f6e36b39751f22a6e7e446b09a6cc2d5cdc4857751225dedfedfe952`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":6.0,"average_failure_rate":0.07895,"average_mean_iterations":23.75,"average_solve_count":76.0,"average_success_count":70.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.14393,"approach_1.approach_speed":0.7209,"contact_1.contact_force_threshold":23.73789,"contact_1.contact_speed":0.05065,"push_1.push_distance":0.34226,"push_1.push_pose_tol":0.05487,"push_1.push_speed":0.12472},"optimized_scores":{"best_composite_score":0.95333,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"link0","body_b":"link7","contact_count":413.0,"contact_point_centroid":[0.0564,0.00831,0.11737],"force_p95":591.69351,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":886.23722,"mean_force":372.1751,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.078,0.03187,0.0956]},{"body_a":"world","body_b":"link5","contact_count":127.0,"contact_point_centroid":[0.22073,0.0039,-0.00061],"force_p95":570.49443,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":793.73025,"mean_force":255.20928,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.07261,0.0368,0.09387]},{"body_a":"link1","body_b":"link7","contact_count":78.0,"contact_point_centroid":[0.0482,0.02558,0.14744],"force_p95":698.60124,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":730.02129,"mean_force":386.40175,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.07386,0.05609,0.12718]},{"body_a":"door_panel","body_b":"link4","contact_count":8.0,"contact_point_centroid":[0.35329,-0.13871,0.34348],"force_p95":666.13986,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":698.60503,"mean_force":319.5791,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.07631,0.03787,0.10059]},{"body_a":"link0","body_b":"link7","contact_count":37.0,"contact_point_centroid":[0.052,0.01724,0.13826],"force_p95":611.27698,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":618.75309,"mean_force":489.52909,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.07785,0.04935,0.12072]},{"body_a":"door_panel","body_b":"link7","contact_count":39.0,"contact_point_centroid":[0.17586,0.08803,0.34815],"force_p95":155.44857,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":244.96332,"mean_force":93.04995,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.16624,0.17265,0.33824]},{"body_a":"door_panel","body_b":"link4","contact_count":20.0,"contact_point_centroid":[0.2618,-0.11083,0.52764],"force_p95":214.40044,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":217.20113,"mean_force":108.34086,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.11793,0.05259,0.15716]},{"body_a":"link0","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.05411,0.01313,0.13409],"force_p95":74.16983,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":74.16983,"mean_force":74.16983,"phase_index":1.0,"phase_name":"contact_1","phase_type":"descend","tcp_position_centroid":[0.08052,0.04609,0.11834]},{"body_a":"world","body_b":"door_panel","contact_count":852.0,"contact_point_centroid":[0.31708,0.15565,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.01576,0.24525,0.3043]},{"body_a":"world","body_b":"door_panel","contact_count":4.0,"contact_point_centroid":[0.42022,0.01633,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"contact_1","phase_type":"descend","tcp_position_centroid":[0.08052,0.04609,0.11834]},{"body_a":"world","body_b":"door_panel","contact_count":420.0,"contact_point_centroid":[0.43652,0.01012,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.18072,0.0505,0.17626]}],"total_contact_groups":11},"final_pose_error":0.29111,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.33677,0.00857,0.31751],"hinge_angle":1.18391,"initial_hinge_angle":0.04367,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.04367,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":886.23722,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":962.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":387.66895,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1026.0,"raw_peak_contact_force":730.02129,"subtask_id":"tcp_contact","tcp_end":[0.08052,0.04609,0.11834],"tcp_start":[-0.11186,0.26743,0.31907],"tcp_to_object_dist_end":0.15037,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":43.52232,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5.0,"raw_peak_contact_force":74.16983,"tcp_end":[0.08061,0.04604,0.11831],"tcp_start":[0.08052,0.04609,0.11834],"tcp_to_object_dist_end":0.15038,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":818.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":968.0,"raw_peak_contact_force":886.23722,"subtask_id":"hinge_progress","tcp_end":[0.33677,0.00857,0.31751],"tcp_start":[0.08061,0.04604,0.11831],"tcp_to_object_dist_end":0.46293,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```