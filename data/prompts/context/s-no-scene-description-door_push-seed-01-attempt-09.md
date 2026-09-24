## Search State

- **Seed**: 1
- **Iteration**: 10 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 9 | approach → align → push | arc_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | time_limit | 5 | 0.7200 | 1.00 | ✅ accepted |
| 8 | approach → align → push | arc_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.6200 | 1.00 | ❌ rejected |
| 7 | approach → align → push | arc_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.4322 | 0.81 | ❌ rejected |
| 6 | approach → align → push | arc_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.6200 | 1.00 | ✅ accepted |
| 5 | rotate → align → push | arc_cartesian | linear_cartesian | impedance_motion | impedance_control | position_control | position_control | time_limit | pose_tolerance | time_limit | 3 | 0.3605 | 0.54 | ❌ rejected |

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

## Current Skill (Q=0.720) — your mutation base

```yaml
skill: door_push
dsl_version: 2
subtasks:
- id: reach_door
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.1
  weight: 0.3
- id: open_door
  anchor: object
  target_entity: hinge
  metric: hinge_angle
  weight: 0.7
phases:
- id: approach
  type: approach
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.1
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.01
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_door
- id: align_contact
  type: align
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    lateral_offset_x:
      type: scalar
      range:
      - -0.01
      - 0.01
      default: 0.0
      binds_to:
      - path: target.offset.x
        mode: add
  subtask_id: reach_door
- id: push_door
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: time_limit
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.3
      axis: world_y
      mode: add_to_offset
      sign: negative
    tolerance: 0.05
    orientation:
      mode: none
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.1
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
    push_time:
      type: scalar
      range:
      - 1.0
      - 5.0
      default: 2.0
      binds_to:
      - path: duration.max_time
        mode: replace
  subtask_id: open_door

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.1], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **align_contact** (`align`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - lateral_offset_x: status=consumed; consumers=target.offset.x (add)
- **push_door** (`push`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_y, distance=0.3, mode=add_to_offset, sign=negative}, tolerance=0.05
  - orientation: mode=none
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
    - push_time: status=consumed; consumers=duration.max_time (replace)

## Design Metrics

- **Composite score**: 0.720
- **task_score** (E): 1.000
- **fitness_score**: 1.000  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.280

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach | 1.00 | 1.00 | 0.2256 |
| align_contact | 1.00 | 0.00 | 0.0883 |
| push_door | 1.00 | 1.00 | 0.1031 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach | approach | 1.00 / step_budget | (0.100, 0.399, 0.350)→(0.100, 0.195, 0.447) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 1.000 | 4.349 | 46.051 |
| align_contact | align | 1.00 / step_budget | (0.100, 0.195, 0.447)→(0.098, 0.181, 0.360) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 0.00 / 0.000 | 0.000 | 23.549 |
| push_door | push | 1.00 / time_limit | (0.098, 0.181, 0.360)→(0.100, 0.078, 0.366) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 3.333 | 8.448 | 27.365 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- hinge_angle_ratio: 1.000
- arc_quality: 1.000

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 1.000
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.720
- **K-run variance**: 0.0000
- **Stagnated**: yes
  → Parameter optimiser converged to local optimum; structural change likely needed
- **Stop reason**: tolfun
- **Mean generations**: 4.3
- **Final σ (mean)**: 0.359


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `083132501f1ba139cf05fa7994a1ee954b157d46058e9396ba8b78c93b367725`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"hinge_delta_deg":10.0,"object_xy_delta":[0.0,0.0]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `a0caaf91521131af8da2ca1e0ce4fb631dc10b8d496fc3757eb1acd97f543da3`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.11224,"average_solve_count":98.0,"average_success_count":98.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_contact.lateral_offset_x":-0.00394,"approach.approach_speed":0.12548,"push_door.push_distance":0.31993,"push_door.push_speed":0.0722,"push_door.push_time":2.3567},"optimized_scores":{"best_composite_score":0.72,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link6","contact_count":210.0,"contact_point_centroid":[0.10118,0.17327,0.54394],"force_p95":20.84357,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":36.79075,"mean_force":14.72095,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.09961,0.24429,0.43769]},{"body_a":"door_panel","body_b":"link7","contact_count":766.0,"contact_point_centroid":[0.15678,0.05928,0.39219],"force_p95":17.91746,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":29.23434,"mean_force":12.78151,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.09743,0.12127,0.36313]},{"body_a":"door_panel","body_b":"link7","contact_count":63.0,"contact_point_centroid":[0.16508,0.14749,0.46942],"force_p95":22.08971,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":26.75055,"mean_force":14.51062,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.09977,0.20484,0.44559]},{"body_a":"door_panel","body_b":"link7","contact_count":62.0,"contact_point_centroid":[0.16326,0.13048,0.42578],"force_p95":21.67931,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":23.47576,"mean_force":15.84771,"phase_index":1.0,"phase_name":"align_contact","phase_type":"align","tcp_position_centroid":[0.09789,0.18782,0.40184]},{"body_a":"world","body_b":"door_panel","contact_count":1040.0,"contact_point_centroid":[0.30056,0.18452,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.0997,0.31022,0.40619]},{"body_a":"world","body_b":"door_panel","contact_count":320.0,"contact_point_centroid":[0.30614,0.14988,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"align_contact","phase_type":"align","tcp_position_centroid":[0.09796,0.18811,0.40354]},{"body_a":"world","body_b":"door_panel","contact_count":924.0,"contact_point_centroid":[0.32014,0.11384,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.09757,0.11674,0.3637]}],"total_contact_groups":7},"final_pose_error":0.20078,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.09973,0.05998,0.36865],"hinge_angle":0.53381,"initial_hinge_angle":0.00413,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.00413,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":36.79075,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1313.0,"raw_peak_contact_force":36.79075,"subtask_id":"reach_door","tcp_end":[0.09981,0.19529,0.44675],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.49768,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":326.0,"n_steps_budget":630.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"align_contact","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":382.0,"raw_peak_contact_force":23.47576,"subtask_id":"reach_door","tcp_end":[0.09628,0.18097,0.35979],"tcp_start":[0.09981,0.19529,0.44675],"tcp_to_object_dist_end":0.41408,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":11.14238,"phase_name":"push_door","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1690.0,"raw_peak_contact_force":29.23434,"subtask_id":"open_door","tcp_end":[0.09973,0.05998,0.36865],"tcp_start":[0.09628,0.18097,0.35979],"tcp_to_object_dist_end":0.38658,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `5bc49f053da41ee2995fb91d1adc375d35d8209a2f6f497df40da3fd7dd59d69`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.18367,"average_solve_count":98.0,"average_success_count":98.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_contact.lateral_offset_x":-0.00086,"approach.approach_speed":0.14851,"push_door.push_distance":0.27458,"push_door.push_speed":0.01536,"push_door.push_time":2.86828},"optimized_scores":{"best_composite_score":0.72,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link6","contact_count":314.0,"contact_point_centroid":[0.10091,0.18966,0.53821],"force_p95":23.34867,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":54.18359,"mean_force":16.3808,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.09959,0.26373,0.43101]},{"body_a":"door_panel","body_b":"link7","contact_count":91.0,"contact_point_centroid":[0.16507,0.14483,0.46986],"force_p95":19.24643,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":31.63944,"mean_force":13.85632,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.09976,0.20219,0.44602]},{"body_a":"door_panel","body_b":"link7","contact_count":770.0,"contact_point_centroid":[0.15972,0.06777,0.38926],"force_p95":19.04525,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":25.66173,"mean_force":12.56014,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.09935,0.12929,0.36138]},{"body_a":"door_panel","body_b":"link7","contact_count":49.0,"contact_point_centroid":[0.16461,0.12705,0.42398],"force_p95":19.00345,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":22.14781,"mean_force":15.35194,"phase_index":1.0,"phase_name":"align_contact","phase_type":"align","tcp_position_centroid":[0.09927,0.18443,0.40003]},{"body_a":"world","body_b":"door_panel","contact_count":1020.0,"contact_point_centroid":[0.3006,0.19331,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.0997,0.30466,0.40843]},{"body_a":"world","body_b":"door_panel","contact_count":312.0,"contact_point_centroid":[0.30669,0.14776,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"align_contact","phase_type":"align","tcp_position_centroid":[0.09929,0.18456,0.40125]},{"body_a":"world","body_b":"door_panel","contact_count":800.0,"contact_point_centroid":[0.3174,0.1189,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.09934,0.12949,0.36136]}],"total_contact_groups":7},"final_pose_error":0.18449,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.10018,0.08934,0.36452],"hinge_angle":0.47108,"initial_hinge_angle":-0.08321,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":-0.08321,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":54.18359,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":940.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":13.04739,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1425.0,"raw_peak_contact_force":54.18359,"subtask_id":"reach_door","tcp_end":[0.09981,0.18958,0.44744],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.49609,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":326.0,"n_steps_budget":630.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"align_contact","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":361.0,"raw_peak_contact_force":22.14781,"subtask_id":"reach_door","tcp_end":[0.09901,0.18029,0.35984],"tcp_start":[0.09981,0.18958,0.44744],"tcp_to_object_dist_end":0.41447,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":14.20088,"phase_name":"push_door","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1570.0,"raw_peak_contact_force":25.66173,"subtask_id":"open_door","tcp_end":[0.10018,0.08934,0.36452],"tcp_start":[0.09901,0.18029,0.35984],"tcp_to_object_dist_end":0.38845,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `36664242b94803fac749fdbd125449f5f6a464dcd4b70b6714af07046570273f`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.89524,"average_solve_count":105.0,"average_success_count":105.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_contact.lateral_offset_x":-0.00124,"approach.approach_speed":0.11422,"push_door.push_distance":0.30336,"push_door.push_speed":0.02944,"push_door.push_time":3.39786},"optimized_scores":{"best_composite_score":0.72,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link6","contact_count":372.0,"contact_point_centroid":[0.10098,0.19265,0.5368],"force_p95":24.75581,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":47.17918,"mean_force":16.50706,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.09953,0.26719,0.42941]},{"body_a":"door_panel","body_b":"link7","contact_count":766.0,"contact_point_centroid":[0.15932,0.0676,0.38961],"force_p95":19.07653,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":27.19852,"mean_force":12.59971,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.09905,0.12917,0.36155]},{"body_a":"door_panel","body_b":"link7","contact_count":44.0,"contact_point_centroid":[0.16511,0.15092,0.46897],"force_p95":21.34584,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":26.93747,"mean_force":14.53897,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.09971,0.20818,0.44516]},{"body_a":"door_panel","body_b":"link7","contact_count":84.0,"contact_point_centroid":[0.16446,0.13412,0.42651],"force_p95":21.47049,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":25.02402,"mean_force":16.19583,"phase_index":1.0,"phase_name":"align_contact","phase_type":"align","tcp_position_centroid":[0.09909,0.19145,0.40256]},{"body_a":"world","body_b":"door_panel","contact_count":916.0,"contact_point_centroid":[0.30049,0.19605,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.09962,0.30679,0.40799]},{"body_a":"world","body_b":"door_panel","contact_count":308.0,"contact_point_centroid":[0.30552,0.15239,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"align_contact","phase_type":"align","tcp_position_centroid":[0.09916,0.19281,0.40853]},{"body_a":"world","body_b":"door_panel","contact_count":984.0,"contact_point_centroid":[0.31717,0.11953,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.09902,0.13056,0.36126]}],"total_contact_groups":7},"final_pose_error":0.20896,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.10005,0.08503,0.36538],"hinge_angle":0.4809,"initial_hinge_angle":-0.14464,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":-0.14464,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":47.17918,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1332.0,"raw_peak_contact_force":47.17918,"subtask_id":"reach_door","tcp_end":[0.09976,0.20141,0.44608],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.49951,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":327.0,"n_steps_budget":630.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"align_contact","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":392.0,"raw_peak_contact_force":25.02402,"subtask_id":"reach_door","tcp_end":[0.09863,0.18173,0.35977],"tcp_start":[0.09976,0.20141,0.44608],"tcp_to_object_dist_end":0.41496,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"push_door","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1750.0,"raw_peak_contact_force":27.19852,"subtask_id":"open_door","tcp_end":[0.10005,0.08503,0.36538],"tcp_start":[0.09863,0.18173,0.35977],"tcp_to_object_dist_end":0.38825,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
```