## Search State

- **Seed**: 7
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | time_limit | force_exceeded | pose_tolerance | 6 | 1.1700 | 1.00 | ❌ rejected |
| 11 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | time_limit | force_exceeded | pose_tolerance | 6 | 1.1700 | 1.00 | ✅ accepted |
| 10 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 6 | 0.8922 | 1.00 | ❌ rejected |
| 9 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 5 | 1.0533 | 1.00 | ✅ accepted |
| 8 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 7 | 0.6200 | 1.00 | ✅ accepted |

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

## Current Skill (Q=1.170) — your mutation base

```yaml
skill: door_push
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: reach_door
  anchor: object
  offset:
  - 0.0
  - -0.2
  - 0.15
  weight: 0.3
- id: push_open
  metric: goal_progress
  weight: 0.7
phases:
- id: approach_door
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: time_limit
  target:
    source: yaml
    anchor: task_object
    entity: door_panel
    offset:
    - 0.0
    - -0.2
    - 0.15
    tolerance: 0.05
    orientation:
      mode: none
  parameters:
    app_duration:
      type: scalar
      range:
      - 500.0
      - 2000.0
      default: 1000
      binds_to:
      - path: duration.max_time
        mode: replace
    app_speed:
      type: scalar
      range:
      - 0.01
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
    app_y:
      type: scalar
      range:
      - -0.35
      - -0.05
      default: -0.2
      binds_to:
      - path: target.offset.y
        mode: replace
  subtask_id: reach_door
- id: contact_door
  type: contact
  generator: linear_cartesian
  control: force_threshold_switch
  termination: force_exceeded
  target:
    source: yaml
    anchor: task_object
    entity: door_panel
    offset:
    - 0.0
    - -0.08
    - 0.05
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    contact_force:
      type: scalar
      range:
      - 3.0
      - 10.0
      default: 6.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
  subtask_id: reach_door
- id: push_door
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: door_panel
    offset:
    - 0.0
    - -0.08
    - 0.05
    offset_along_axis:
      distance: 0.3
      axis: world_x
      mode: add_to_offset
      sign: positive
    tolerance: 0.03
    orientation:
      mode: keep_current
  parameters:
    push_dist:
      type: scalar
      range:
      - 0.05
      - 0.5
      default: 0.3
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: push_open

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_door** (`approach`)
  - target: source=yaml, anchor=task_object, entity=door_panel, offset=[0.0, -0.2, 0.15], tolerance=0.05
  - orientation: mode=none
  - parameter_bindings:
    - app_duration: status=consumed; consumers=duration.max_time (replace)
    - app_speed: status=consumed; consumers=generator.speed (replace)
    - app_y: status=consumed; consumers=target.offset.y (replace)
- **contact_door** (`contact`)
  - target: source=yaml, anchor=task_object, entity=door_panel, offset=[0.0, -0.08, 0.05], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - contact_force: status=consumed; consumers=termination.force_threshold (replace)
- **push_door** (`push`)
  - target: source=yaml, anchor=task_object, entity=door_panel, offset=[0.0, -0.08, 0.05], offset_along_axis={axis=world_x, distance=0.3, mode=add_to_offset, sign=positive}, tolerance=0.03
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_dist: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: 1.170
- **task_score** (E): 1.000
- **fitness_score**: 1.000  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.500
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.330

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_door | 1.00 | 0.33 | 0.1775 |
| contact_door | 1.00 | 1.00 | 0.0147 |
| push_door | 0.33 | 1.00 | 0.3544 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_door | approach | 1.00 / time_limit | (0.100, 0.399, 0.350)→(0.072, 0.233, 0.293) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 0.33 / 0.333 | 0.000 | 7.361 |
| contact_door | contact | 1.00 / force_exceeded | (0.072, 0.233, 0.293)→(0.069, 0.222, 0.284) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 1.000 | 13.229 | 13.298 |
| push_door | push | 0.33 / step_budget | (0.069, 0.222, 0.284)→(0.291, 0.005, 0.114) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 1.000 | 16.512 | 58.826 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- hinge_angle_ratio: 1.000
- arc_quality: 1.000

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 1.000
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 1.170
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: tolflatfitness
- **Mean generations**: 3.3
- **Final σ (mean)**: 0.297


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `2fa9c04e562df03eff32cc7f63abe386d265bbd85d42dcee2df7f90a42e2de0a`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"hinge_delta_deg":10.0,"object_xy_delta":[0.0,0.0]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `fb31b2d7951f101afe3533d0babe40d387e4396f53837e61e543f2cfc46b7e19`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.98742,"average_solve_count":159.0,"average_success_count":159.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_door.app_duration":1239.04949,"approach_door.app_speed":0.08333,"approach_door.app_y":-0.20107,"contact_door.contact_force":4.97125,"push_door.push_dist":0.37233,"push_door.push_speed":0.04417},"optimized_scores":{"best_composite_score":1.17,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link7","contact_count":472.0,"contact_point_centroid":[0.29023,0.04645,0.21186],"force_p95":59.57472,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":68.30362,"mean_force":37.09422,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.22019,0.07998,0.17355]},{"body_a":"door_panel","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.13028,0.18453,0.33912],"force_p95":13.905,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":13.905,"mean_force":13.905,"phase_index":1.0,"phase_name":"contact_door","phase_type":"contact","tcp_position_centroid":[0.07186,0.23106,0.29262]},{"body_a":"world","body_b":"door_panel","contact_count":920.0,"contact_point_centroid":[0.30061,0.18148,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_door","phase_type":"approach","tcp_position_centroid":[0.08609,0.31698,0.32107]},{"body_a":"world","body_b":"door_panel","contact_count":16.0,"contact_point_centroid":[0.30059,0.18168,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"contact_door","phase_type":"contact","tcp_position_centroid":[0.07198,0.23154,0.293]},{"body_a":"world","body_b":"door_panel","contact_count":596.0,"contact_point_centroid":[0.34959,0.08818,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.20371,0.09723,0.18721]}],"total_contact_groups":5},"final_pose_error":0.02974,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.3538,-0.06021,0.06223],"hinge_angle":1.36549,"initial_hinge_angle":0.04367,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.04367,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":68.30362,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"approach_door","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":920.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_door","tcp_end":[0.07205,0.23187,0.29323],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.38071,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":7.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":13.905,"phase_name":"contact_door","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":17.0,"raw_peak_contact_force":13.905,"subtask_id":"reach_door","tcp_end":[0.07184,0.23092,0.29249],"tcp_start":[0.07205,0.23187,0.29323],"tcp_to_object_dist_end":0.37952,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":764.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":29.78142,"phase_name":"push_door","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1068.0,"raw_peak_contact_force":68.30362,"subtask_id":"push_open","tcp_end":[0.3538,-0.06021,0.06223],"tcp_start":[0.07184,0.23092,0.29249],"tcp_to_object_dist_end":0.36424,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `2fe1c8aab50c64fd16f940100e2036790f2ea8f75271c649e6989441e8f9191e`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.75,"average_solve_count":104.0,"average_success_count":104.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_door.app_duration":1431.69086,"approach_door.app_speed":0.07645,"approach_door.app_y":-0.18757,"contact_door.contact_force":6.94099,"push_door.push_dist":0.29316,"push_door.push_speed":0.04487},"optimized_scores":{"best_composite_score":1.17,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link7","contact_count":696.0,"contact_point_centroid":[0.23013,0.09317,0.26552],"force_p95":33.29473,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":44.86272,"mean_force":18.29358,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.17112,0.14032,0.21711]},{"body_a":"door_panel","body_b":"link7","contact_count":194.0,"contact_point_centroid":[0.13349,0.20552,0.34403],"force_p95":15.60957,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":22.0842,"mean_force":11.61339,"phase_index":0.0,"phase_name":"approach_door","phase_type":"approach","tcp_position_centroid":[0.07502,0.25377,0.29951]},{"body_a":"door_panel","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.13059,0.18879,0.33928],"force_p95":13.54411,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":13.565,"mean_force":8.9737,"phase_index":1.0,"phase_name":"contact_door","phase_type":"contact","tcp_position_centroid":[0.0719,0.23545,0.29323]},{"body_a":"world","body_b":"door_panel","contact_count":1064.0,"contact_point_centroid":[0.2998,0.19989,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_door","phase_type":"approach","tcp_position_centroid":[0.08579,0.31714,0.32057]},{"body_a":"world","body_b":"door_panel","contact_count":8.0,"contact_point_centroid":[0.3004,0.18389,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"contact_door","phase_type":"contact","tcp_position_centroid":[0.07188,0.23538,0.29318]},{"body_a":"world","body_b":"door_panel","contact_count":948.0,"contact_point_centroid":[0.3195,0.11814,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.16791,0.1432,0.21936]}],"total_contact_groups":6},"final_pose_error":0.22333,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.21267,0.08541,0.17663],"hinge_angle":0.61501,"initial_hinge_angle":-0.0604,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":-0.0604,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":44.86272,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"approach_door","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1258.0,"raw_peak_contact_force":22.0842,"subtask_id":"reach_door","tcp_end":[0.07199,0.2359,0.29359],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.38344,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":7.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":13.35611,"phase_name":"contact_door","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":11.0,"raw_peak_contact_force":13.565,"subtask_id":"reach_door","tcp_end":[0.07179,0.235,0.29287],"tcp_start":[0.07199,0.2359,0.29359],"tcp_to_object_dist_end":0.3823,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":19.75359,"phase_name":"push_door","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1644.0,"raw_peak_contact_force":44.86272,"subtask_id":"push_open","tcp_end":[0.21267,0.08541,0.17663],"tcp_start":[0.07179,0.235,0.29287],"tcp_to_object_dist_end":0.28935,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `356d1c9659b48b76a1cff255b134bf18d0729848f67621b991467785bdaaef44`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.43151,"average_solve_count":146.0,"average_success_count":146.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_door.app_duration":1382.18687,"approach_door.app_speed":0.07687,"approach_door.app_y":-0.19903,"contact_door.contact_force":5.97065,"push_door.push_dist":0.38433,"push_door.push_speed":0.04745},"optimized_scores":{"best_composite_score":1.17,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link7","contact_count":638.0,"contact_point_centroid":[0.25095,0.07056,0.24317],"force_p95":47.77961,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":63.31103,"mean_force":25.80049,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.18784,0.11311,0.19791]},{"body_a":"door_panel","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.12319,0.15379,0.31459],"force_p95":12.42529,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":12.42529,"mean_force":12.42529,"phase_index":1.0,"phase_name":"contact_door","phase_type":"contact","tcp_position_centroid":[0.06471,0.20018,0.268]},{"body_a":"world","body_b":"door_panel","contact_count":1100.0,"contact_point_centroid":[0.30285,0.16488,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_door","phase_type":"approach","tcp_position_centroid":[0.0862,0.31792,0.32131]},{"body_a":"world","body_b":"door_panel","contact_count":268.0,"contact_point_centroid":[0.30273,0.16561,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"contact_door","phase_type":"contact","tcp_position_centroid":[0.06838,0.2163,0.28051]},{"body_a":"world","body_b":"door_panel","contact_count":880.0,"contact_point_centroid":[0.32815,0.10686,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.17656,0.12419,0.20647]}],"total_contact_groups":5},"final_pose_error":0.11671,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.30674,-0.01009,0.10209],"hinge_angle":1.12653,"initial_hinge_angle":0.12924,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.12924,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":63.31103,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"approach_door","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1100.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_door","tcp_end":[0.07205,0.23244,0.29323],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.38106,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":239.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":12.42529,"phase_name":"contact_door","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":269.0,"raw_peak_contact_force":12.42529,"subtask_id":"reach_door","tcp_end":[0.06468,0.20004,0.26789],"tcp_start":[0.07205,0.23244,0.29323],"tcp_to_object_dist_end":0.34053,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"push_door","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1518.0,"raw_peak_contact_force":63.31103,"subtask_id":"push_open","tcp_end":[0.30674,-0.01009,0.10209],"tcp_start":[0.06468,0.20004,0.26789],"tcp_to_object_dist_end":0.32344,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```