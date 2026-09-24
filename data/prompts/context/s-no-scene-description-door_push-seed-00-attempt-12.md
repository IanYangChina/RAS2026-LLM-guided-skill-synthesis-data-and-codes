## Search State

- **Seed**: 0
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | approach → align → push | arc_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 13 | 0.3200 | 1.00 | ✅ accepted |
| 11 | approach → align → push | arc_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 13 | 0.3099 | 0.99 | ✅ accepted |
| 10 | approach → align → push | arc_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | contact_detected | force_exceeded | 11 | 0.2489 | 0.83 | ✅ accepted |
| 9 | approach → align → push | arc_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 7 | -0.1713 | 0.21 | ❌ rejected |
| 8 | approach → push | arc_cartesian | linear_cartesian | position_control | impedance_control | pose_tolerance | pose_tolerance | 5 | 0.2161 | 0.47 | ❌ rejected |

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

## Current Skill (Q=0.320) — your mutation base

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
  target_entity: hinge
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

- **Composite score**: 0.320
- **task_score** (E): 1.000
- **fitness_score**: 1.000  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.680

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_to_handle | 0.00 | 1.00 | 0.2494 |
| align_to_door | 0.00 | 1.00 | 0.1611 |
| push_door_open | 0.67 | 0.33 | 0.1362 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_to_handle | approach | 0.00 / step_budget | (0.100, 0.399, 0.350)→(0.048, 0.191, 0.472) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 1.000 | 6.925 | 29.842 |
| align_to_door | align | 0.00 / step_budget | (0.048, 0.191, 0.472)→(0.137, 0.080, 0.411) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 1.000 | 7.898 | 70.448 |
| push_door_open | push | 0.67 / step_budget | (0.137, 0.080, 0.411)→(0.178, 0.148, 0.521) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 0.33 / 0.333 | 46.587 | 205.375 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- hinge_angle_ratio: 1.000
- arc_quality: 0.333

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 1.000
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.320
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.346


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.09302,"average_solve_count":258.0,"average_success_count":258.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_to_door.align_speed":0.03441,"align_to_door.align_x_offset":0.03718,"align_to_door.align_y_offset":-0.11948,"align_to_door.align_z_offset":-0.03647,"align_to_door.tolerance":0.06508,"approach_to_handle.approach_height":0.26352,"approach_to_handle.approach_x_offset":-0.00476,"approach_to_handle.approach_y_offset":-0.01639,"approach_to_handle.arc_height":0.11767,"approach_to_handle.speed":0.11275,"push_door_open.push_distance":0.17296,"push_door_open.push_speed":0.03292,"push_door_open.tolerance":0.02847},"optimized_scores":{"best_composite_score":0.32,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link7","contact_count":684.0,"contact_point_centroid":[0.18911,0.03719,0.43469],"force_p95":25.94587,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":31.91593,"mean_force":13.86976,"phase_index":1.0,"phase_name":"align_to_door","phase_type":"align","tcp_position_centroid":[0.12555,0.0961,0.40507]},{"body_a":"door_panel","body_b":"link7","contact_count":196.0,"contact_point_centroid":[0.11753,0.15549,0.44851],"force_p95":14.43007,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":28.04079,"mean_force":12.67871,"phase_index":0.0,"phase_name":"approach_to_handle","phase_type":"approach","tcp_position_centroid":[0.05324,0.21304,0.42479]},{"body_a":"door_panel","body_b":"link7","contact_count":4.0,"contact_point_centroid":[0.21303,0.00831,0.44115],"force_p95":19.06788,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":19.76582,"mean_force":8.71968,"phase_index":2.0,"phase_name":"push_door_open","phase_type":"push","tcp_position_centroid":[0.15162,0.06869,0.40935]},{"body_a":"world","body_b":"door_panel","contact_count":932.0,"contact_point_centroid":[0.30119,0.17722,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_to_handle","phase_type":"approach","tcp_position_centroid":[0.07392,0.2954,0.40335]},{"body_a":"world","body_b":"door_panel","contact_count":808.0,"contact_point_centroid":[0.32763,0.09977,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"align_to_door","phase_type":"align","tcp_position_centroid":[0.12345,0.09837,0.40515]},{"body_a":"world","body_b":"door_panel","contact_count":216.0,"contact_point_centroid":[0.33895,0.08099,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_door_open","phase_type":"push","tcp_position_centroid":[0.16913,0.10017,0.47104]}],"total_contact_groups":6},"final_pose_error":0.02799,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.18734,0.13293,0.53431],"hinge_angle":0.58273,"initial_hinge_angle":0.04781,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.04781,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":31.91593,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"approach_to_handle","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1128.0,"raw_peak_contact_force":28.04079,"subtask_id":"reach_handle","tcp_end":[0.04603,0.18434,0.42316],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.46386,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":893.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":10.50759,"phase_name":"align_to_door","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":1492.0,"raw_peak_contact_force":31.91593,"subtask_id":"reach_handle","tcp_end":[0.15162,0.06869,0.40936],"tcp_start":[0.04603,0.18434,0.42316],"tcp_to_object_dist_end":0.44191,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":285.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"push_door_open","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":220.0,"raw_peak_contact_force":19.76582,"subtask_id":"push_complete","tcp_end":[0.18734,0.13293,0.53431],"tcp_start":[0.15162,0.06869,0.40936],"tcp_to_object_dist_end":0.58159,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `7a748efd829eb09daaf6b07ec36a2131763f35cca8c1f058f1a757467a8ce067`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.90141,"average_solve_count":213.0,"average_success_count":213.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_to_door.align_speed":0.03758,"align_to_door.align_x_offset":0.02562,"align_to_door.align_y_offset":-0.10906,"align_to_door.align_z_offset":-0.01893,"align_to_door.tolerance":0.05253,"approach_to_handle.approach_height":0.36491,"approach_to_handle.approach_x_offset":0.00522,"approach_to_handle.approach_y_offset":0.00137,"approach_to_handle.arc_height":0.16743,"approach_to_handle.speed":0.14391,"push_door_open.push_distance":0.08747,"push_door_open.push_speed":0.03147,"push_door_open.tolerance":0.01531},"optimized_scores":{"best_composite_score":0.32,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link7","contact_count":406.0,"contact_point_centroid":[0.17887,0.03383,0.44157],"force_p95":32.78218,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":142.16891,"mean_force":15.4003,"phase_index":1.0,"phase_name":"align_to_door","phase_type":"align","tcp_position_centroid":[0.11443,0.09251,0.41337]},{"body_a":"door_panel","body_b":"link7","contact_count":233.0,"contact_point_centroid":[0.11942,0.15439,0.54393],"force_p95":21.37501,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":35.44626,"mean_force":14.07184,"phase_index":0.0,"phase_name":"approach_to_handle","phase_type":"approach","tcp_position_centroid":[0.05532,0.21189,0.52015]},{"body_a":"door_panel","body_b":"link7","contact_count":4.0,"contact_point_centroid":[0.19742,0.0164,0.43605],"force_p95":18.84191,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":19.43444,"mean_force":8.72967,"phase_index":2.0,"phase_name":"push_door_open","phase_type":"push","tcp_position_centroid":[0.13449,0.07635,0.40652]},{"body_a":"world","body_b":"door_panel","contact_count":1100.0,"contact_point_centroid":[0.30099,0.18217,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_to_handle","phase_type":"approach","tcp_position_centroid":[0.07753,0.30467,0.46508]},{"body_a":"world","body_b":"door_panel","contact_count":552.0,"contact_point_centroid":[0.32541,0.10372,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"align_to_door","phase_type":"align","tcp_position_centroid":[0.10676,0.09963,0.42301]},{"body_a":"world","body_b":"door_panel","contact_count":220.0,"contact_point_centroid":[0.33399,0.08801,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_door_open","phase_type":"push","tcp_position_centroid":[0.14294,0.09177,0.43592]}],"total_contact_groups":6},"final_pose_error":0.0151,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.15236,0.10874,0.46872],"hinge_angle":0.53994,"initial_hinge_angle":0.00413,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.00413,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":142.16891,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":9.96525,"phase_name":"approach_to_handle","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1333.0,"raw_peak_contact_force":35.44626,"subtask_id":"reach_handle","tcp_end":[0.04327,0.16159,0.51932],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.5456,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":613.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":9.80974,"phase_name":"align_to_door","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":958.0,"raw_peak_contact_force":142.16891,"subtask_id":"reach_handle","tcp_end":[0.1345,0.07633,0.40653],"tcp_start":[0.04327,0.16159,0.51932],"tcp_to_object_dist_end":0.43495,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":278.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"push_door_open","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":224.0,"raw_peak_contact_force":19.43444,"subtask_id":"push_complete","tcp_end":[0.15236,0.10874,0.46872],"tcp_start":[0.1345,0.07633,0.40653],"tcp_to_object_dist_end":0.50471,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `8f682501979e58f93da2583f25150788eff90e19c055477d4547c33e5c9d7ff1`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.93939,"average_solve_count":231.0,"average_success_count":231.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_to_door.align_speed":0.04816,"align_to_door.align_x_offset":0.01981,"align_to_door.align_y_offset":-0.10907,"align_to_door.align_z_offset":-0.05745,"align_to_door.tolerance":0.05343,"approach_to_handle.approach_height":0.33543,"approach_to_handle.approach_x_offset":-0.00296,"approach_to_handle.approach_y_offset":0.00997,"approach_to_handle.arc_height":0.13328,"approach_to_handle.speed":0.10502,"push_door_open.push_distance":0.31501,"push_door_open.push_speed":0.05988,"push_door_open.tolerance":0.02825},"optimized_scores":{"best_composite_score":0.32,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_frame","body_b":"link6","contact_count":607.0,"contact_point_centroid":[0.16731,0.2011,0.75015],"force_p95":336.71588,"geom_a":"door_frame_top_beam","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":576.92541,"mean_force":277.98687,"phase_index":2.0,"phase_name":"push_door_open","phase_type":"push","tcp_position_centroid":[0.18225,0.18972,0.56129]},{"body_a":"door_panel","body_b":"link7","contact_count":697.0,"contact_point_centroid":[0.17084,0.06572,0.43369],"force_p95":30.80113,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":37.25899,"mean_force":14.16345,"phase_index":1.0,"phase_name":"align_to_door","phase_type":"align","tcp_position_centroid":[0.10627,0.12376,0.40509]},{"body_a":"door_panel","body_b":"link7","contact_count":245.0,"contact_point_centroid":[0.12442,0.19954,0.48967],"force_p95":16.21355,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":26.03941,"mean_force":11.97667,"phase_index":0.0,"phase_name":"approach_to_handle","phase_type":"approach","tcp_position_centroid":[0.0624,0.25726,0.46641]},{"body_a":"door_panel","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.18641,0.03606,0.45022],"force_p95":12.15396,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":13.5044,"mean_force":4.50147,"phase_index":2.0,"phase_name":"push_door_open","phase_type":"push","tcp_position_centroid":[0.12413,0.09543,0.41819]},{"body_a":"world","body_b":"door_panel","contact_count":1096.0,"contact_point_centroid":[0.29995,0.20223,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_to_handle","phase_type":"approach","tcp_position_centroid":[0.08089,0.32696,0.42313]},{"body_a":"world","body_b":"door_panel","contact_count":904.0,"contact_point_centroid":[0.31886,0.11661,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"align_to_door","phase_type":"align","tcp_position_centroid":[0.10509,0.12617,0.40715]},{"body_a":"world","body_b":"door_panel","contact_count":936.0,"contact_point_centroid":[0.32637,0.10025,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_door_open","phase_type":"push","tcp_position_centroid":[0.16896,0.16952,0.53593]}],"total_contact_groups":7},"final_pose_error":0.13292,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.19342,0.20186,0.56125],"hinge_angle":0.46029,"initial_hinge_angle":-0.08321,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":-0.08321,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":576.92541,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":10.81005,"phase_name":"approach_to_handle","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1341.0,"raw_peak_contact_force":26.03941,"subtask_id":"reach_handle","tcp_end":[0.05417,0.22579,0.47307],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.52698,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":3.37601,"phase_name":"align_to_door","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":1601.0,"raw_peak_contact_force":37.25899,"subtask_id":"reach_handle","tcp_end":[0.12412,0.09544,0.41818],"tcp_start":[0.05417,0.22579,0.47307],"tcp_to_object_dist_end":0.44653,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":139.76248,"phase_name":"push_door_open","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1546.0,"raw_peak_contact_force":576.92541,"subtask_id":"push_complete","tcp_end":[0.19342,0.20186,0.56125],"tcp_start":[0.12412,0.09544,0.41818],"tcp_to_object_dist_end":0.62702,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```