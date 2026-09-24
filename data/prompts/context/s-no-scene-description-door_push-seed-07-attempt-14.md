## Search State

- **Seed**: 7
- **Iteration**: 15 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 14 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | time_limit | force_exceeded | pose_tolerance | 6 | 1.1700 | 1.00 | ❌ rejected |
| 13 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | time_limit | force_exceeded | pose_tolerance | 6 | 0.8860 | 0.72 | ❌ rejected |
| 12 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | time_limit | force_exceeded | pose_tolerance | 6 | 1.1700 | 1.00 | ❌ rejected |
| 11 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | time_limit | force_exceeded | pose_tolerance | 6 | 1.1700 | 1.00 | ✅ accepted |
| 10 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 6 | 0.8922 | 1.00 | ❌ rejected |

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
| approach_door | 1.00 | 0.33 | 0.1807 |
| contact_door | 1.00 | 1.00 | 0.0110 |
| push_door | 0.33 | 1.00 | 0.3193 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_door | approach | 1.00 / time_limit | (0.100, 0.399, 0.350)→(0.071, 0.231, 0.291) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 0.33 / 0.333 | 3.543 | 7.202 |
| contact_door | contact | 1.00 / force_exceeded | (0.071, 0.231, 0.291)→(0.069, 0.223, 0.284) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 3.667 | 10.183 | 5.614 |
| push_door | push | 0.33 / step_budget | (0.069, 0.223, 0.284)→(0.262, 0.024, 0.127) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 1.000 | 15.833 | 52.205 |

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
- **Stagnated**: yes
  → Parameter optimiser converged to local optimum; structural change likely needed
- **Stop reason**: tolfun
- **Mean generations**: 4.0
- **Final σ (mean)**: 0.303


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.29193,"average_solve_count":161.0,"average_success_count":161.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_door.app_duration":1276.25892,"approach_door.app_speed":0.10364,"approach_door.app_y":-0.14745,"contact_door.contact_force":4.92152,"push_door.push_dist":0.33061,"push_door.push_speed":0.03579},"optimized_scores":{"best_composite_score":1.17,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link7","contact_count":604.0,"contact_point_centroid":[0.26209,0.05655,0.22264],"force_p95":45.09955,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":57.60268,"mean_force":28.03003,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.19586,0.09557,0.1806]},{"body_a":"world","body_b":"door_panel","contact_count":920.0,"contact_point_centroid":[0.30061,0.18148,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_door","phase_type":"approach","tcp_position_centroid":[0.08536,0.32025,0.31962]},{"body_a":"world","body_b":"door_panel","contact_count":60.0,"contact_point_centroid":[0.30059,0.18169,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"contact_door","phase_type":"contact","tcp_position_centroid":[0.06989,0.23556,0.28778]},{"body_a":"world","body_b":"door_panel","contact_count":884.0,"contact_point_centroid":[0.33773,0.10126,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.18178,0.11145,0.19266]}],"total_contact_groups":4},"final_pose_error":0.0297,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.31397,-0.05909,0.06297],"hinge_angle":1.22476,"initial_hinge_angle":0.04367,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.04367,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":57.60268,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"approach_door","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":920.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_door","tcp_end":[0.07059,0.23877,0.29032],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.38247,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":61.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":6.94322,"phase_name":"contact_door","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":60.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_door","tcp_end":[0.06878,0.23053,0.28386],"tcp_start":[0.07059,0.23877,0.29032],"tcp_to_object_dist_end":0.37209,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":945.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":28.64856,"phase_name":"push_door","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1488.0,"raw_peak_contact_force":57.60268,"subtask_id":"push_open","tcp_end":[0.31397,-0.05909,0.06297],"tcp_start":[0.06878,0.23053,0.28386],"tcp_to_object_dist_end":0.32563,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `2fe1c8aab50c64fd16f940100e2036790f2ea8f75271c649e6989441e8f9191e`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.96078,"average_solve_count":102.0,"average_success_count":102.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_door.app_duration":1211.2681,"approach_door.app_speed":0.05815,"approach_door.app_y":-0.16243,"contact_door.contact_force":6.34521,"push_door.push_dist":0.2402,"push_door.push_speed":0.04542},"optimized_scores":{"best_composite_score":1.17,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link7","contact_count":596.0,"contact_point_centroid":[0.21163,0.11563,0.27662],"force_p95":27.91767,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":44.15346,"mean_force":17.47212,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.15249,0.16344,0.22897]},{"body_a":"door_panel","body_b":"link7","contact_count":179.0,"contact_point_centroid":[0.13304,0.20746,0.34223],"force_p95":15.06007,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":21.60596,"mean_force":11.40898,"phase_index":0.0,"phase_name":"approach_door","phase_type":"approach","tcp_position_centroid":[0.07422,0.25546,0.2979]},{"body_a":"door_panel","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.13055,0.19291,0.33785],"force_p95":16.00076,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":16.8429,"mean_force":8.42145,"phase_index":1.0,"phase_name":"contact_door","phase_type":"contact","tcp_position_centroid":[0.07139,0.23951,0.29231]},{"body_a":"world","body_b":"door_panel","contact_count":1028.0,"contact_point_centroid":[0.29978,0.20059,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_door","phase_type":"approach","tcp_position_centroid":[0.08588,0.32114,0.32073]},{"body_a":"world","body_b":"door_panel","contact_count":8.0,"contact_point_centroid":[0.30023,0.18616,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"contact_door","phase_type":"contact","tcp_position_centroid":[0.0714,0.23952,0.29234]},{"body_a":"world","body_b":"door_panel","contact_count":988.0,"contact_point_centroid":[0.31027,0.13925,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.14041,0.17068,0.23526]}],"total_contact_groups":6},"final_pose_error":0.25885,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.20391,0.12747,0.20049],"hinge_angle":0.46916,"initial_hinge_angle":-0.0604,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":-0.0604,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":44.15346,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":10.63035,"phase_name":"approach_door","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1207.0,"raw_peak_contact_force":21.60596,"subtask_id":"reach_door","tcp_end":[0.07141,0.23962,0.29241],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.38474,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":4.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":16.8429,"phase_name":"contact_door","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":10.0,"raw_peak_contact_force":16.8429,"subtask_id":"reach_door","tcp_end":[0.07135,0.23926,0.29209],"tcp_start":[0.07141,0.23962,0.29241],"tcp_to_object_dist_end":0.38426,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":18.85073,"phase_name":"push_door","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1584.0,"raw_peak_contact_force":44.15346,"subtask_id":"push_open","tcp_end":[0.20391,0.12747,0.20049],"tcp_start":[0.07135,0.23926,0.29209],"tcp_to_object_dist_end":0.31309,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `356d1c9659b48b76a1cff255b134bf18d0729848f67621b991467785bdaaef44`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.51471,"average_solve_count":136.0,"average_success_count":136.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_door.app_duration":1370.82106,"approach_door.app_speed":0.11915,"approach_door.app_y":-0.21324,"contact_door.contact_force":6.20893,"push_door.push_dist":0.35147,"push_door.push_speed":0.05659},"optimized_scores":{"best_composite_score":1.17,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link7","contact_count":617.0,"contact_point_centroid":[0.23668,0.07377,0.25436],"force_p95":43.4248,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":54.85966,"mean_force":23.1948,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.17565,0.11691,0.20632]},{"body_a":"world","body_b":"door_panel","contact_count":1096.0,"contact_point_centroid":[0.30285,0.16488,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_door","phase_type":"approach","tcp_position_centroid":[0.08524,0.31007,0.31941]},{"body_a":"world","body_b":"door_panel","contact_count":144.0,"contact_point_centroid":[0.30274,0.16555,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"contact_door","phase_type":"contact","tcp_position_centroid":[0.06796,0.20682,0.28205]},{"body_a":"world","body_b":"door_panel","contact_count":844.0,"contact_point_centroid":[0.32593,0.10861,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.16927,0.12309,0.21133]}],"total_contact_groups":4},"final_pose_error":0.13568,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.26809,0.0041,0.11621],"hinge_angle":0.96718,"initial_hinge_angle":0.12924,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.12924,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":54.85966,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"approach_door","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1096.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_door","tcp_end":[0.06993,0.21535,0.28902],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.36715,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":125.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":6.76243,"phase_name":"contact_door","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":144.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_door","tcp_end":[0.06607,0.1987,0.27546],"tcp_start":[0.06993,0.21535,0.28902],"tcp_to_object_dist_end":0.34601,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"push_door","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1461.0,"raw_peak_contact_force":54.85966,"subtask_id":"push_open","tcp_end":[0.26809,0.0041,0.11621],"tcp_start":[0.06607,0.1987,0.27546],"tcp_to_object_dist_end":0.29223,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```