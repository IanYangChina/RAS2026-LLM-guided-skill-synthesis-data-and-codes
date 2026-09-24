## Search State

- **Seed**: 8
- **Iteration**: 15 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 14 | approach → contact → push | arc_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | time_limit | 7 | 1.1200 | 1.00 | ❌ rejected |
| 13 | approach → contact → push | arc_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | time_limit | 7 | 1.1200 | 1.00 | ✅ accepted |
| 12 | approach → align → contact → push | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 9 | -0.1404 | 0.12 | ❌ rejected |
| 11 | approach → align → contact → push | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 8 | 0.2523 | 0.55 | ❌ rejected |
| 10 | approach → contact → push | arc_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | time_limit | 8 | 0.0749 | 0.17 | ❌ rejected |

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

## Current Skill (Q=1.120) — your mutation base

```yaml
skill: door_push
dsl_version: 2
subtasks:
- id: approach_door
  anchor: object
  offset:
  - 0.0
  - -0.15
  - 0.15
  weight: 0.3
- id: push_hinge
  anchor: fixture
  target_entity: hinge
  metric: hinge_angle
  weight: 0.7
phases:
- id: approach_1
  type: approach
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - -0.15
    - 0.15
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.1
      - 0.5
      default: 0.3
      binds_to:
      - path: generator.speed
        mode: replace
    arc_height:
      type: scalar
      range:
      - 0.05
      - 0.25
      default: 0.1
      binds_to:
      - path: generator.arc_height
        mode: replace
  subtask_id: approach_door
- id: contact_1
  type: contact
  generator: linear_cartesian
  control: force_threshold_switch
  termination: force_exceeded
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - -0.15
    - 0.0
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    contact_force_threshold:
      type: scalar
      range:
      - 3.0
      - 20.0
      default: 10.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    contact_speed:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: approach_door
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
      distance: 0.3
      axis: task_goal_direction
      mode: add_to_offset
      sign: positive
    orientation:
      mode: keep_current
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.1
      - 0.6
      default: 0.3
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_max_time:
      type: scalar
      range:
      - 3.0
      - 10.0
      default: 6.0
      binds_to:
      - path: duration.max_time
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
  - id: contact_maintained
    when: during_phase
    predicate: contact_detected
    threshold: 1.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - 0.0
  subtask_id: push_hinge

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, -0.15, 0.15], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
    - arc_height: status=consumed; consumers=generator.arc_height (replace)
- **contact_1** (`contact`)
  - target: source=yaml, anchor=task_object, offset=[0.0, -0.15, 0.0], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - contact_force_threshold: status=consumed; consumers=termination.force_threshold (replace)
    - contact_speed: status=consumed; consumers=generator.speed (replace)
- **push_1** (`push`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.3, mode=add_to_offset, sign=positive}
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_max_time: status=consumed; consumers=duration.max_time (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=contact_maintained, when=during_phase, predicate=contact_detected, on_failure=retry, threshold=1.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, 0.0]

## Design Metrics

- **Composite score**: 1.120
- **task_score** (E): 1.000
- **fitness_score**: 1.000  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.500
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.380

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 0.00 | 1.00 | 0.4531 |
| contact_1 | 1.00 | 1.00 | 0.0003 |
| push_1 | 1.00 | 0.00 | 0.2765 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 0.00 / step_budget | (0.100, 0.399, 0.350)→(0.033, -0.044, 0.417) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 2.333 | 239.283 | 1228.848 |
| contact_1 | contact | 1.00 / force_exceeded | (0.033, -0.044, 0.417)→(0.033, -0.044, 0.417) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 5.000 | 240.252 | 64.486 |
| push_1 | push | 1.00 / time_limit | (0.033, -0.044, 0.417)→(0.101, 0.079, 0.655) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 0.00 / 0.000 | 0.000 | 239.031 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- hinge_angle_ratio: 1.000
- arc_quality: 0.667

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 1.000
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 1.120
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.3
- **Final σ (mean)**: 0.254


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `ea6bae111f14debb91f5aac35e1b236c8a3b6c6e55761aa2eab002718511c500`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"hinge_delta_deg":10.0,"object_xy_delta":[0.0,0.0]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `4672b672dcc6ffecf2b710096d1b05b46bb79ca3304db4877275d5463822e477`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":6.13235,"average_solve_count":68.0,"average_success_count":68.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.28967,"approach_1.arc_height":0.10069,"contact_1.contact_force_threshold":13.6291,"contact_1.contact_speed":0.08213,"push_1.push_distance":0.31133,"push_1.push_max_time":5.75481,"push_1.push_speed":0.21737},"optimized_scores":{"best_composite_score":1.12,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link6","contact_count":172.0,"contact_point_centroid":[0.13947,0.03602,0.51922],"force_p95":1117.17459,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1307.88892,"mean_force":564.85669,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.02398,-0.00633,0.39963]},{"body_a":"link1","body_b":"link7","contact_count":266.0,"contact_point_centroid":[0.04537,0.00042,0.37645],"force_p95":435.72473,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":612.81039,"mean_force":276.07989,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.02207,-0.00368,0.39878]},{"body_a":"link2","body_b":"link7","contact_count":42.0,"contact_point_centroid":[0.01179,0.02884,0.37821],"force_p95":219.923,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":315.14006,"mean_force":28.294,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.01572,0.00475,0.39599]},{"body_a":"link1","body_b":"link7","contact_count":11.0,"contact_point_centroid":[0.0858,-0.06591,0.36666],"force_p95":70.92729,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":73.66825,"mean_force":49.49754,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.03308,-0.03285,0.41533]},{"body_a":"door_panel","body_b":"link7","contact_count":235.0,"contact_point_centroid":[0.12868,0.15001,0.39744],"force_p95":29.86721,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":45.71425,"mean_force":16.74845,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.06312,0.20447,0.37378]},{"body_a":"link1","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.08591,-0.06573,0.36638],"force_p95":33.92556,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":33.92556,"mean_force":33.92556,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.03287,-0.03249,0.41433]},{"body_a":"door_panel","body_b":"link6","contact_count":15.0,"contact_point_centroid":[0.18917,-0.05176,0.62993],"force_p95":28.46405,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":29.63442,"mean_force":20.92306,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.06944,0.03233,0.54182]},{"body_a":"world","body_b":"door_panel","contact_count":1060.0,"contact_point_centroid":[0.31029,0.14784,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.04754,0.139,0.38432]},{"body_a":"world","body_b":"door_panel","contact_count":648.0,"contact_point_centroid":[0.35101,0.0662,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.06753,0.02897,0.53509]}],"total_contact_groups":9},"final_pose_error":0.01467,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.10646,0.09871,0.67008],"hinge_angle":0.67328,"initial_hinge_angle":-0.0604,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":-0.0604,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":1307.88892,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":361.46809,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1775.0,"raw_peak_contact_force":1307.88892,"subtask_id":"approach_door","tcp_end":[0.03287,-0.03249,0.41433],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.4169,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":372.07649,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1.0,"raw_peak_contact_force":33.92556,"subtask_id":"approach_door","tcp_end":[0.03291,-0.03281,0.41452],"tcp_start":[0.03287,-0.03249,0.41433],"tcp_to_object_dist_end":0.41712,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":871.0,"n_steps_budget":900.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":674.0,"raw_peak_contact_force":73.66825,"subtask_id":"push_hinge","tcp_end":[0.10646,0.09871,0.67008],"tcp_start":[0.03291,-0.03281,0.41452],"tcp_to_object_dist_end":0.68563,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `6091bac9443f311cc90f1388d6700bb5b9c315c724ba8069ca061d7c4a07c1f1`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":5.76389,"average_solve_count":72.0,"average_success_count":72.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.3174,"approach_1.arc_height":0.11585,"contact_1.contact_force_threshold":14.54094,"contact_1.contact_speed":0.08941,"push_1.push_distance":0.41157,"push_1.push_max_time":8.78961,"push_1.push_speed":0.14775},"optimized_scores":{"best_composite_score":1.12,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link6","contact_count":139.0,"contact_point_centroid":[0.14096,0.03042,0.5186],"force_p95":1133.27096,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1232.99144,"mean_force":573.60896,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.02909,-0.00751,0.39763]},{"body_a":"link1","body_b":"link7","contact_count":282.0,"contact_point_centroid":[0.05,-0.00658,0.37535],"force_p95":420.24692,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":666.84533,"mean_force":258.32722,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.02781,-0.00963,0.39918]},{"body_a":"door_panel","body_b":"link6","contact_count":49.0,"contact_point_centroid":[0.20055,-0.06516,0.52679],"force_p95":119.54351,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":415.46208,"mean_force":66.98751,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.04095,-0.03584,0.44289]},{"body_a":"link1","body_b":"link7","contact_count":14.0,"contact_point_centroid":[0.07995,-0.07872,0.36535],"force_p95":165.62669,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":180.61222,"mean_force":106.76436,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.03375,-0.04923,0.41574]},{"body_a":"link1","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.0791,-0.07936,0.36513],"force_p95":128.78895,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":128.78895,"mean_force":128.78895,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.0331,-0.05062,0.41615]},{"body_a":"door_panel","body_b":"link7","contact_count":152.0,"contact_point_centroid":[0.12309,0.1055,0.41013],"force_p95":29.48227,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":68.73611,"mean_force":16.59516,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.05302,0.15429,0.38688]},{"body_a":"link2","body_b":"link7","contact_count":28.0,"contact_point_centroid":[0.01689,0.02516,0.37865],"force_p95":1.79761,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":8.08235,"mean_force":0.38743,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.02169,0.00086,0.39597]},{"body_a":"world","body_b":"door_panel","contact_count":1052.0,"contact_point_centroid":[0.31189,0.13806,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.05376,0.1509,0.38593]},{"body_a":"world","body_b":"door_panel","contact_count":716.0,"contact_point_centroid":[0.35689,0.05994,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.06127,0.00052,0.51362]}],"total_contact_groups":9},"final_pose_error":0.17717,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.09118,0.05384,0.61782],"hinge_angle":0.71506,"initial_hinge_angle":0.12924,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.12924,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":1232.99144,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":353.17546,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1653.0,"raw_peak_contact_force":1232.99144,"subtask_id":"approach_door","tcp_end":[0.0331,-0.05062,0.41615],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.42052,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":317.93672,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1.0,"raw_peak_contact_force":128.78895,"subtask_id":"approach_door","tcp_end":[0.03323,-0.05008,0.41587],"tcp_start":[0.0331,-0.05062,0.41615],"tcp_to_object_dist_end":0.42019,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":779.0,"raw_peak_contact_force":415.46208,"subtask_id":"push_hinge","tcp_end":[0.09118,0.05384,0.61782],"tcp_start":[0.03323,-0.05008,0.41587],"tcp_to_object_dist_end":0.62683,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `3d62b54ff2d8b84e841b6e4711bcf5c00d2771c3332b770c71c3a72dad860645`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":6.13699,"average_solve_count":73.0,"average_success_count":73.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.31163,"approach_1.arc_height":0.0995,"contact_1.contact_force_threshold":12.17425,"contact_1.contact_speed":0.09831,"push_1.push_distance":0.49459,"push_1.push_max_time":7.55355,"push_1.push_speed":0.18732},"optimized_scores":{"best_composite_score":1.12,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link6","contact_count":167.0,"contact_point_centroid":[0.14086,0.03334,0.51991],"force_p95":1119.55085,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1145.66391,"mean_force":522.93338,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.02423,-0.00728,0.40007]},{"body_a":"link1","body_b":"link7","contact_count":288.0,"contact_point_centroid":[0.04961,-0.00746,0.37536],"force_p95":393.61414,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":640.16599,"mean_force":265.46096,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.02333,-0.00796,0.40092]},{"body_a":"link2","body_b":"link7","contact_count":40.0,"contact_point_centroid":[0.01139,0.02912,0.37823],"force_p95":237.63804,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":350.32358,"mean_force":33.7706,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.01572,0.00505,0.39596]},{"body_a":"door_panel","body_b":"link6","contact_count":54.0,"contact_point_centroid":[0.19928,-0.06371,0.52516],"force_p95":169.02656,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":227.96181,"mean_force":88.15389,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.03938,-0.03519,0.44604]},{"body_a":"link1","body_b":"link7","contact_count":7.0,"contact_point_centroid":[0.07895,-0.07226,0.36721],"force_p95":160.41593,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":168.06394,"mean_force":83.88638,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.0323,-0.04811,0.4209]},{"body_a":"door_panel","body_b":"link7","contact_count":100.0,"contact_point_centroid":[0.12164,0.1109,0.40005],"force_p95":30.55066,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":47.54607,"mean_force":17.15439,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.05327,0.16256,0.37639]},{"body_a":"link1","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.07887,-0.07247,0.36704],"force_p95":30.74405,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":30.74405,"mean_force":30.74405,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.03222,-0.04821,0.42052]},{"body_a":"world","body_b":"door_panel","contact_count":1004.0,"contact_point_centroid":[0.31122,0.13894,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.05269,0.16152,0.38151]},{"body_a":"world","body_b":"door_panel","contact_count":4.0,"contact_point_centroid":[0.35453,0.06238,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.03222,-0.04821,0.42052]},{"body_a":"world","body_b":"door_panel","contact_count":744.0,"contact_point_centroid":[0.35723,0.0596,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.06934,0.01815,0.54987]}],"total_contact_groups":10},"final_pose_error":0.19609,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.10624,0.08396,0.67771],"hinge_angle":0.71473,"initial_hinge_angle":0.15917,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.15917,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":1145.66391,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":3.20642,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1599.0,"raw_peak_contact_force":1145.66391,"subtask_id":"approach_door","tcp_end":[0.03222,-0.04821,0.42052],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.4245,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":30.74405,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":5.0,"raw_peak_contact_force":30.74405,"subtask_id":"approach_door","tcp_end":[0.03221,-0.04826,0.42054],"tcp_start":[0.03222,-0.04821,0.42052],"tcp_to_object_dist_end":0.42452,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":805.0,"raw_peak_contact_force":227.96181,"subtask_id":"push_hinge","tcp_end":[0.10624,0.08396,0.67771],"tcp_start":[0.03221,-0.04826,0.42054],"tcp_to_object_dist_end":0.69111,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
```