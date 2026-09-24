## Search State

- **Seed**: 0
- **Iteration**: 12 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 11 | approach → align → push | arc_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 13 | 0.3099 | 0.99 | ✅ accepted |
| 10 | approach → align → push | arc_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | contact_detected | force_exceeded | 11 | 0.2489 | 0.83 | ✅ accepted |
| 9 | approach → align → push | arc_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 7 | -0.1713 | 0.21 | ❌ rejected |
| 8 | approach → push | arc_cartesian | linear_cartesian | position_control | impedance_control | pose_tolerance | pose_tolerance | 5 | 0.2161 | 0.47 | ❌ rejected |
| 7 | approach → push | arc_cartesian | linear_cartesian | position_control | impedance_control | pose_tolerance | force_exceeded | 5 | 0.5434 | 0.46 | ❌ rejected |

**Proposal policy**: task_score is near-perfect (0.99). Preserve useful working parts and make only evidence-backed refinements. A HOLD is acceptable if you genuinely cannot find a better structure.

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

## Current Skill (Q=0.310) — your mutation base

```yaml
skill: door_push
dsl_version: 2
subtasks:
- id: reach_handle
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.35
  weight: 0.3
- id: push_complete
  weight: 0.7
phases:
- id: approach_to_handle
  type: approach
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.25
    orientation:
      mode: keep_current
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.15
      - 0.45
      default: 0.25
      binds_to:
      - path: target.offset.z
        mode: replace
    approach_x_offset:
      type: scalar
      range:
      - -0.05
      - 0.05
      default: 0.0
      binds_to:
      - path: target.offset.x
        mode: replace
    approach_y_offset:
      type: scalar
      range:
      - -0.05
      - 0.05
      default: 0.0
      binds_to:
      - path: target.offset.y
        mode: replace
    arc_height:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.arc_height
        mode: replace
    speed:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.06
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_handle
- id: align_to_door
  type: align
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - -0.05
    - -0.1
    orientation:
      mode: keep_current
  parameters:
    align_speed:
      type: scalar
      range:
      - 0.01
      - 0.08
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
    align_x_offset:
      type: scalar
      range:
      - -0.05
      - 0.05
      default: 0.0
      binds_to:
      - path: target.offset.x
        mode: replace
    align_y_offset:
      type: scalar
      range:
      - -0.12
      - 0.0
      default: -0.05
      binds_to:
      - path: target.offset.y
        mode: replace
    align_z_offset:
      type: scalar
      range:
      - -0.2
      - 0.0
      default: -0.1
      binds_to:
      - path: target.offset.z
        mode: replace
    tolerance:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  subtask_id: reach_handle
- id: push_door_open
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.25
      axis: task_goal_direction
      mode: add_to_offset
      sign: positive
    orientation:
      mode: keep_current
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.05
      - 0.5
      default: 0.25
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.08
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
    tolerance:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.02
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.01
    - 0.0
  subtask_id: push_complete

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_to_handle** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.25]
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
    - approach_x_offset: status=consumed; consumers=target.offset.x (replace)
    - approach_y_offset: status=consumed; consumers=target.offset.y (replace)
    - arc_height: status=consumed; consumers=generator.arc_height (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **align_to_door** (`align`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, -0.05, -0.1]
  - orientation: mode=keep_current
  - parameter_bindings:
    - align_speed: status=consumed; consumers=generator.speed (replace)
    - align_x_offset: status=consumed; consumers=target.offset.x (replace)
    - align_y_offset: status=consumed; consumers=target.offset.y (replace)
    - align_z_offset: status=consumed; consumers=target.offset.z (replace)
    - tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
- **push_door_open** (`push`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.25, mode=add_to_offset, sign=positive}
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
    - tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.01, 0.0]

## Design Metrics

- **Composite score**: 0.310
- **task_score** (E): 0.990
- **fitness_score**: 0.990  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.680

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_to_handle | 0.00 | 1.00 | 0.2361 |
| align_to_door | 0.00 | 1.00 | 0.1490 |
| push_door_open | 0.67 | 0.33 | 0.1454 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_to_handle | approach | 0.00 / step_budget | (0.100, 0.399, 0.350)→(0.054, 0.191, 0.449) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 2.333 | 26.498 | 27.827 |
| align_to_door | align | 0.00 / step_budget | (0.054, 0.191, 0.449)→(0.131, 0.073, 0.414) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 2.333 | 11.374 | 38.083 |
| push_door_open | push | 0.67 / step_budget | (0.131, 0.073, 0.414)→(0.172, 0.145, 0.534) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 0.33 / 0.333 | 0.226 | 194.555 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- hinge_angle_ratio: 1.000
- arc_quality: 0.333

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 1.000
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.320
- **K-run variance**: 0.0002
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.331


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `275c70960dc683bb9d0f514db4e615bd3a6644bf8e38d8dd2bfa731bf179f097`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"hinge_delta_deg":10.0,"object_xy_delta":[0.0,0.0]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `35996939e2e1630dea7cedb55906290b2cb0393492844f540c2c9d9496e5416e`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.98462,"average_solve_count":195.0,"average_success_count":195.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_to_door.align_speed":0.0572,"align_to_door.align_x_offset":0.03398,"align_to_door.align_y_offset":-0.11952,"align_to_door.align_z_offset":-0.01533,"align_to_door.tolerance":0.04668,"approach_to_handle.approach_height":0.40774,"approach_to_handle.approach_x_offset":0.00173,"approach_to_handle.approach_y_offset":-0.01135,"approach_to_handle.arc_height":0.07726,"approach_to_handle.speed":0.13812,"push_door_open.push_distance":0.34807,"push_door_open.push_speed":0.06123,"push_door_open.tolerance":0.02336},"optimized_scores":{"best_composite_score":0.28966,"best_fitness_score":0.96966,"best_task_score":0.96966},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_frame","body_b":"link6","contact_count":517.0,"contact_point_centroid":[0.1948,0.18581,0.75014],"force_p95":374.21201,"geom_a":"door_frame_top_beam","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":548.86366,"mean_force":273.14601,"phase_index":2.0,"phase_name":"push_door_open","phase_type":"push","tcp_position_centroid":[0.19893,0.1651,0.56169]},{"body_a":"door_panel","body_b":"link7","contact_count":418.0,"contact_point_centroid":[0.18147,0.03655,0.43444],"force_p95":30.27682,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":33.99616,"mean_force":16.03043,"phase_index":1.0,"phase_name":"align_to_door","phase_type":"align","tcp_position_centroid":[0.117,0.09495,0.40623]},{"body_a":"door_panel","body_b":"link7","contact_count":196.0,"contact_point_centroid":[0.11988,0.15563,0.47513],"force_p95":18.47198,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":23.94945,"mean_force":12.51564,"phase_index":0.0,"phase_name":"approach_to_handle","phase_type":"approach","tcp_position_centroid":[0.05558,0.21315,0.45142]},{"body_a":"door_panel","body_b":"link7","contact_count":5.0,"contact_point_centroid":[0.20501,0.0065,0.43626],"force_p95":17.40284,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":17.84503,"mean_force":11.91338,"phase_index":2.0,"phase_name":"push_door_open","phase_type":"push","tcp_position_centroid":[0.14213,0.06605,0.40601]},{"body_a":"world","body_b":"door_panel","contact_count":960.0,"contact_point_centroid":[0.30129,0.17657,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_to_handle","phase_type":"approach","tcp_position_centroid":[0.07422,0.29116,0.41879]},{"body_a":"world","body_b":"door_panel","contact_count":488.0,"contact_point_centroid":[0.32648,0.10238,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"align_to_door","phase_type":"align","tcp_position_centroid":[0.11359,0.0991,0.4079]},{"body_a":"world","body_b":"door_panel","contact_count":904.0,"contact_point_centroid":[0.33694,0.08377,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_door_open","phase_type":"push","tcp_position_centroid":[0.18379,0.13929,0.52774]}],"total_contact_groups":7},"final_pose_error":0.15184,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.20697,0.177,0.562],"hinge_angle":0.55591,"initial_hinge_angle":0.04781,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.04781,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":548.86366,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":13.12223,"phase_name":"approach_to_handle","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1156.0,"raw_peak_contact_force":23.94945,"subtask_id":"reach_handle","tcp_end":[0.0481,0.18175,0.45583],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.49308,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":531.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":13.10802,"phase_name":"align_to_door","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":906.0,"raw_peak_contact_force":33.99616,"subtask_id":"reach_handle","tcp_end":[0.14215,0.06605,0.40602],"tcp_start":[0.0481,0.18175,0.45583],"tcp_to_object_dist_end":0.43522,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.6777,"phase_name":"push_door_open","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1426.0,"raw_peak_contact_force":548.86366,"subtask_id":"push_complete","tcp_end":[0.20697,0.177,0.562],"tcp_start":[0.14215,0.06605,0.40602],"tcp_to_object_dist_end":0.62451,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `7a748efd829eb09daaf6b07ec36a2131763f35cca8c1f058f1a757467a8ce067`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.09302,"average_solve_count":258.0,"average_success_count":258.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_to_door.align_speed":0.03441,"align_to_door.align_x_offset":0.03718,"align_to_door.align_y_offset":-0.11948,"align_to_door.align_z_offset":-0.03647,"align_to_door.tolerance":0.06508,"approach_to_handle.approach_height":0.26352,"approach_to_handle.approach_x_offset":-0.00476,"approach_to_handle.approach_y_offset":-0.01639,"approach_to_handle.arc_height":0.11767,"approach_to_handle.speed":0.11275,"push_door_open.push_distance":0.17296,"push_door_open.push_speed":0.03292,"push_door_open.tolerance":0.02847},"optimized_scores":{"best_composite_score":0.32,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link7","contact_count":691.0,"contact_point_centroid":[0.18913,0.03723,0.43465],"force_p95":25.90846,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":31.93392,"mean_force":13.86018,"phase_index":1.0,"phase_name":"align_to_door","phase_type":"align","tcp_position_centroid":[0.12556,0.09613,0.40503]},{"body_a":"door_panel","body_b":"link7","contact_count":257.0,"contact_point_centroid":[0.11916,0.16415,0.44806],"force_p95":13.80931,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":28.14392,"mean_force":12.53291,"phase_index":0.0,"phase_name":"approach_to_handle","phase_type":"approach","tcp_position_centroid":[0.05543,0.22174,0.42444]},{"body_a":"door_panel","body_b":"link7","contact_count":4.0,"contact_point_centroid":[0.21302,0.00833,0.44116],"force_p95":19.06496,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":19.76273,"mean_force":8.71841,"phase_index":2.0,"phase_name":"push_door_open","phase_type":"push","tcp_position_centroid":[0.15161,0.06871,0.40936]},{"body_a":"world","body_b":"door_panel","contact_count":1036.0,"contact_point_centroid":[0.30055,0.18485,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_to_handle","phase_type":"approach","tcp_position_centroid":[0.07663,0.3062,0.39938]},{"body_a":"world","body_b":"door_panel","contact_count":788.0,"contact_point_centroid":[0.32726,0.10071,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"align_to_door","phase_type":"align","tcp_position_centroid":[0.1221,0.09987,0.4053]},{"body_a":"world","body_b":"door_panel","contact_count":236.0,"contact_point_centroid":[0.33896,0.08098,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_door_open","phase_type":"push","tcp_position_centroid":[0.16879,0.09958,0.46995]}],"total_contact_groups":6},"final_pose_error":0.02799,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.18733,0.13295,0.53431],"hinge_angle":0.58266,"initial_hinge_angle":0.00413,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.00413,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":53.75717,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":53.75717,"phase_name":"approach_to_handle","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1293.0,"raw_peak_contact_force":28.14392,"subtask_id":"reach_handle","tcp_end":[0.04607,0.18449,0.42319],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.46395,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":893.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":10.52482,"phase_name":"align_to_door","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":1479.0,"raw_peak_contact_force":31.93392,"subtask_id":"reach_handle","tcp_end":[0.15161,0.0687,0.40937],"tcp_start":[0.04607,0.18449,0.42319],"tcp_to_object_dist_end":0.44191,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":285.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"push_door_open","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":240.0,"raw_peak_contact_force":19.76273,"subtask_id":"push_complete","tcp_end":[0.18733,0.13295,0.53431],"tcp_start":[0.15161,0.0687,0.40937],"tcp_to_object_dist_end":0.5816,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `8f682501979e58f93da2583f25150788eff90e19c055477d4547c33e5c9d7ff1`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.12755,"average_solve_count":196.0,"average_success_count":196.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_to_door.align_speed":0.0529,"align_to_door.align_x_offset":0.00706,"align_to_door.align_y_offset":-0.11232,"align_to_door.align_z_offset":-0.05718,"align_to_door.tolerance":0.06828,"approach_to_handle.approach_height":0.31023,"approach_to_handle.approach_x_offset":0.03394,"approach_to_handle.approach_y_offset":0.01722,"approach_to_handle.arc_height":0.13892,"approach_to_handle.speed":0.10836,"push_door_open.push_distance":0.12172,"push_door_open.push_speed":0.03437,"push_door_open.tolerance":0.03314},"optimized_scores":{"best_composite_score":0.32,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link7","contact_count":539.0,"contact_point_centroid":[0.15888,0.05714,0.44199],"force_p95":28.58515,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":48.318,"mean_force":13.92704,"phase_index":1.0,"phase_name":"align_to_door","phase_type":"align","tcp_position_centroid":[0.09446,0.11533,0.41312]},{"body_a":"door_panel","body_b":"link7","contact_count":286.0,"contact_point_centroid":[0.13619,0.1887,0.48642],"force_p95":14.42309,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":31.38787,"mean_force":12.70209,"phase_index":0.0,"phase_name":"approach_to_handle","phase_type":"approach","tcp_position_centroid":[0.07341,0.24635,0.46302]},{"body_a":"door_panel","body_b":"link6","contact_count":18.0,"contact_point_centroid":[0.10123,0.23092,0.55589],"force_p95":25.24394,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":26.17876,"mean_force":18.89817,"phase_index":0.0,"phase_name":"approach_to_handle","phase_type":"approach","tcp_position_centroid":[0.08034,0.28644,0.45321]},{"body_a":"door_panel","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.162,0.02534,0.45986],"force_p95":14.28613,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":15.03804,"mean_force":7.51902,"phase_index":2.0,"phase_name":"push_door_open","phase_type":"push","tcp_position_centroid":[0.09998,0.08505,0.42789]},{"body_a":"world","body_b":"door_panel","contact_count":1064.0,"contact_point_centroid":[0.30009,0.20029,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_to_handle","phase_type":"approach","tcp_position_centroid":[0.08641,0.32107,0.42285]},{"body_a":"world","body_b":"door_panel","contact_count":704.0,"contact_point_centroid":[0.3201,0.11315,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"align_to_door","phase_type":"align","tcp_position_centroid":[0.09479,0.11404,0.41432]},{"body_a":"world","body_b":"door_panel","contact_count":172.0,"contact_point_centroid":[0.32684,0.09943,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_door_open","phase_type":"push","tcp_position_centroid":[0.11023,0.10418,0.4663]}],"total_contact_groups":7},"final_pose_error":0.03257,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.12109,0.12406,0.50525],"hinge_angle":0.47462,"initial_hinge_angle":-0.08321,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":-0.08321,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":48.318,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":12.61413,"phase_name":"approach_to_handle","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1368.0,"raw_peak_contact_force":31.38787,"subtask_id":"reach_handle","tcp_end":[0.06675,0.20701,0.4672],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.51535,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":806.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":10.4896,"phase_name":"align_to_door","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":1243.0,"raw_peak_contact_force":48.318,"subtask_id":"reach_handle","tcp_end":[0.09999,0.08505,0.42788],"tcp_start":[0.06675,0.20701,0.4672],"tcp_to_object_dist_end":0.44756,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":156.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"push_door_open","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":174.0,"raw_peak_contact_force":15.03804,"subtask_id":"push_complete","tcp_end":[0.12109,0.12406,0.50525],"tcp_start":[0.09999,0.08505,0.42788],"tcp_to_object_dist_end":0.53416,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```