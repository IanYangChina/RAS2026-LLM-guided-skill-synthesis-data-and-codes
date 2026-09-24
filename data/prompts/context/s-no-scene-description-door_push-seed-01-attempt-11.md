## Search State

- **Seed**: 1
- **Iteration**: 12 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 11 | approach → align → push | arc_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | time_limit | time_limit | time_limit | 7 | 0.6200 | 1.00 | ❌ rejected |
| 10 | approach → align → push | arc_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | time_limit | 5 | 0.7200 | 1.00 | ❌ rejected |
| 9 | approach → align → push | arc_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | time_limit | 5 | 0.7200 | 1.00 | ✅ accepted |
| 8 | approach → align → push | arc_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.6200 | 1.00 | ❌ rejected |
| 7 | approach → align → push | arc_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.4322 | 0.81 | ❌ rejected |

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
| approach | 1.00 | 1.00 | 0.2017 |
| align_contact | 1.00 | 0.67 | 0.1009 |
| push_door | 1.00 | 0.33 | 0.1148 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach | approach | 1.00 / time_limit | (0.100, 0.399, 0.350)→(0.100, 0.220, 0.441) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 2.333 | 12.147 | 47.247 |
| align_contact | align | 1.00 / time_limit | (0.100, 0.220, 0.441)→(0.099, 0.181, 0.354) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 0.67 / 0.667 | 4.312 | 27.840 |
| push_door | push | 1.00 / time_limit | (0.099, 0.181, 0.354)→(0.102, 0.067, 0.364) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 0.33 / 1.667 | 4.327 | 29.418 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- hinge_angle_ratio: 1.000
- arc_quality: 1.000

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 1.000
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.620
- **K-run variance**: 0.0000
- **Stagnated**: yes
  → Parameter optimiser converged to local optimum; structural change likely needed
- **Stop reason**: tolfun
- **Mean generations**: 3.0
- **Final σ (mean)**: 0.312


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.46739,"average_solve_count":92.0,"average_success_count":92.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_contact.align_time":2.2642,"align_contact.lateral_offset_x":-0.00233,"approach.approach_speed":0.13881,"approach.approach_time":3.35203,"push_door.push_distance":0.2877,"push_door.push_speed":0.08308,"push_door.push_time":1.17283},"optimized_scores":{"best_composite_score":0.62,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link6","contact_count":217.0,"contact_point_centroid":[0.10118,0.1733,0.54394],"force_p95":20.21502,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":37.32002,"mean_force":14.15835,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.09963,0.24435,0.4377]},{"body_a":"door_panel","body_b":"link7","contact_count":752.0,"contact_point_centroid":[0.15809,0.05381,0.39061],"force_p95":18.56821,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":30.87715,"mean_force":13.01153,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.09897,0.11583,0.36127]},{"body_a":"door_panel","body_b":"link7","contact_count":59.0,"contact_point_centroid":[0.16502,0.15017,0.46925],"force_p95":19.29232,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":30.50601,"mean_force":13.77943,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.0997,0.20756,0.44542]},{"body_a":"door_panel","body_b":"link7","contact_count":155.0,"contact_point_centroid":[0.16381,0.13187,0.42201],"force_p95":17.8505,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":23.56061,"mean_force":13.79879,"phase_index":1.0,"phase_name":"align_contact","phase_type":"align","tcp_position_centroid":[0.09848,0.18925,0.39804]},{"body_a":"world","body_b":"door_panel","contact_count":1064.0,"contact_point_centroid":[0.30056,0.18438,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.09971,0.31094,0.40534]},{"body_a":"world","body_b":"door_panel","contact_count":588.0,"contact_point_centroid":[0.30591,0.15082,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"align_contact","phase_type":"align","tcp_position_centroid":[0.09856,0.1899,0.40113]},{"body_a":"world","body_b":"door_panel","contact_count":908.0,"contact_point_centroid":[0.32045,0.11354,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.09898,0.116,0.36127]}],"total_contact_groups":7},"final_pose_error":0.15591,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.10186,0.04724,0.36727],"hinge_angle":0.56301,"initial_hinge_angle":0.00413,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.00413,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":37.32002,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":7.98854,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1340.0,"raw_peak_contact_force":37.32002,"subtask_id":"reach_door","tcp_end":[0.09973,0.19947,0.4465],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.4991,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":550.0,"n_steps_budget":630.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"align_contact","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":743.0,"raw_peak_contact_force":23.56061,"subtask_id":"reach_door","tcp_end":[0.09757,0.18032,0.3549],"tcp_start":[0.09973,0.19947,0.4465],"tcp_to_object_dist_end":0.40987,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"push_door","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1660.0,"raw_peak_contact_force":30.87715,"subtask_id":"open_door","tcp_end":[0.10186,0.04724,0.36727],"tcp_start":[0.09757,0.18032,0.3549],"tcp_to_object_dist_end":0.38405,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `5bc49f053da41ee2995fb91d1adc375d35d8209a2f6f497df40da3fd7dd59d69`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.07,"average_solve_count":100.0,"average_success_count":100.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_contact.align_time":2.56395,"align_contact.lateral_offset_x":0.00093,"approach.approach_speed":0.09093,"approach.approach_time":3.58017,"push_door.push_distance":0.36549,"push_door.push_speed":0.0658,"push_door.push_time":3.85111},"optimized_scores":{"best_composite_score":0.62,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link6","contact_count":254.0,"contact_point_centroid":[0.10129,0.17121,0.51028],"force_p95":23.34411,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":38.57158,"mean_force":15.36568,"phase_index":1.0,"phase_name":"align_contact","phase_type":"align","tcp_position_centroid":[0.09952,0.2417,0.40369]},{"body_a":"door_panel","body_b":"link6","contact_count":216.0,"contact_point_centroid":[0.1004,0.2137,0.53003],"force_p95":19.84224,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":37.9466,"mean_force":16.58194,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.09944,0.29234,0.42139]},{"body_a":"door_panel","body_b":"link7","contact_count":732.0,"contact_point_centroid":[0.1608,0.06735,0.38617],"force_p95":18.54833,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":29.08033,"mean_force":12.98706,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.10094,0.12906,0.35768]},{"body_a":"door_panel","body_b":"link7","contact_count":159.0,"contact_point_centroid":[0.16566,0.14077,0.38939],"force_p95":17.13462,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":27.57628,"mean_force":14.22247,"phase_index":1.0,"phase_name":"align_contact","phase_type":"align","tcp_position_centroid":[0.10032,0.19806,0.3653]},{"body_a":"world","body_b":"door_panel","contact_count":1080.0,"contact_point_centroid":[0.29985,0.20415,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.09959,0.34152,0.39176]},{"body_a":"world","body_b":"door_panel","contact_count":652.0,"contact_point_centroid":[0.30259,0.16852,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"align_contact","phase_type":"align","tcp_position_centroid":[0.0998,0.22649,0.39031]},{"body_a":"world","body_b":"door_panel","contact_count":888.0,"contact_point_centroid":[0.31806,0.11808,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.10097,0.12759,0.35758]}],"total_contact_groups":7},"final_pose_error":0.2588,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.1022,0.07295,0.36338],"hinge_angle":0.51018,"initial_hinge_angle":-0.08321,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":-0.08321,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":38.57158,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":15.47671,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1296.0,"raw_peak_contact_force":37.9466,"subtask_id":"reach_door","tcp_end":[0.09946,0.27055,0.43018],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.51783,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":705.0,"n_steps_budget":780.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":12.93624,"phase_name":"align_contact","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":1065.0,"raw_peak_contact_force":38.57158,"subtask_id":"reach_door","tcp_end":[0.10059,0.18394,0.35288],"tcp_start":[0.09946,0.27055,0.43018],"tcp_to_object_dist_end":0.41046,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"push_door","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1620.0,"raw_peak_contact_force":29.08033,"subtask_id":"open_door","tcp_end":[0.1022,0.07295,0.36338],"tcp_start":[0.10059,0.18394,0.35288],"tcp_to_object_dist_end":0.38446,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `36664242b94803fac749fdbd125449f5f6a464dcd4b70b6714af07046570273f`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.33333,"average_solve_count":93.0,"average_success_count":93.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_contact.align_time":2.63303,"align_contact.lateral_offset_x":0.00043,"approach.approach_speed":0.15487,"approach.approach_time":2.99745,"push_door.push_distance":0.18482,"push_door.push_speed":0.05734,"push_door.push_time":2.19369},"optimized_scores":{"best_composite_score":0.62,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link6","contact_count":331.0,"contact_point_centroid":[0.10097,0.19224,0.53707],"force_p95":24.53328,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":66.47501,"mean_force":17.10474,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.09956,0.26669,0.42974]},{"body_a":"door_panel","body_b":"link7","contact_count":96.0,"contact_point_centroid":[0.16502,0.14457,0.46993],"force_p95":19.36766,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":32.37498,"mean_force":13.74736,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.09976,0.20203,0.44607]},{"body_a":"door_panel","body_b":"link7","contact_count":788.0,"contact_point_centroid":[0.16077,0.06688,0.38664],"force_p95":17.81694,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":28.29691,"mean_force":12.62216,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.10051,0.12838,0.35857]},{"body_a":"door_panel","body_b":"link7","contact_count":104.0,"contact_point_centroid":[0.16517,0.12642,0.42215],"force_p95":16.54921,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":21.38872,"mean_force":13.408,"phase_index":1.0,"phase_name":"align_contact","phase_type":"align","tcp_position_centroid":[0.09987,0.18384,0.3982]},{"body_a":"world","body_b":"door_panel","contact_count":888.0,"contact_point_centroid":[0.30076,0.19408,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.09967,0.30284,0.40863]},{"body_a":"world","body_b":"door_panel","contact_count":528.0,"contact_point_centroid":[0.30676,0.14749,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"align_contact","phase_type":"align","tcp_position_centroid":[0.09986,0.18422,0.40195]},{"body_a":"world","body_b":"door_panel","contact_count":940.0,"contact_point_centroid":[0.31835,0.11705,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.10056,0.12568,0.35881]}],"total_contact_groups":7},"final_pose_error":0.08634,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.10156,0.08061,0.3624],"hinge_angle":0.49232,"initial_hinge_angle":-0.14464,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":-0.14464,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":66.47501,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":961.0,"n_steps_budget":990.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":12.97708,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1315.0,"raw_peak_contact_force":66.47501,"subtask_id":"reach_door","tcp_end":[0.0998,0.18907,0.44748],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.49593,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":547.0,"n_steps_budget":630.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"align_contact","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":632.0,"raw_peak_contact_force":21.38872,"subtask_id":"reach_door","tcp_end":[0.10017,0.17959,0.35491],"tcp_start":[0.0998,0.18907,0.44748],"tcp_to_object_dist_end":0.41018,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":12.982,"phase_name":"push_door","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1728.0,"raw_peak_contact_force":28.29691,"subtask_id":"open_door","tcp_end":[0.10156,0.08061,0.3624],"tcp_start":[0.10017,0.17959,0.35491],"tcp_to_object_dist_end":0.3849,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
```