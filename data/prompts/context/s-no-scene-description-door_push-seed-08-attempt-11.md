## Search State

- **Seed**: 8
- **Iteration**: 12 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 11 | approach → align → contact → push | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 8 | 0.2523 | 0.55 | ❌ rejected |
| 10 | approach → contact → push | arc_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | time_limit | 8 | 0.0749 | 0.17 | ❌ rejected |
| 9 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | time_limit | 7 | 0.4353 | 0.32 | ❌ rejected |
| 8 | approach → align → contact → push | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 8 | 0.1131 | 0.49 | ❌ rejected |
| 7 | approach → contact → push | arc_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | time_limit | 7 | 0.2526 | 0.13 | ❌ rejected |

**Proposal policy**: task_score is 0.55 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
- task_score stagnant: change coupled targets, parameters, terminations, phase types, controls, subtasks, or ordering when evidence shows they need to change together.
A HOLD wastes an iteration when task_score is below 0.9.

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

## Current Skill (Q=0.252) — your mutation base

```yaml
skill: door_push
dsl_version: 2
subtasks:
- id: approach_goal
  offset:
  - 0.0
  - 0.0
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
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.15
    tolerance: 0.02
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: world_z
      tolerance: 0.05
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
  subtask_id: approach_goal
- id: contact_1
  type: contact
  generator: linear_cartesian
  control: force_threshold_switch
  termination: force_exceeded
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    contact_force_threshold:
      type: scalar
      range:
      - 2.0
      - 15.0
      default: 5.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    contact_speed:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: approach_goal
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
      distance: 0.35
      axis: world_x
      mode: add_to_offset
      sign: positive
    orientation:
      mode: keep_current
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.1
      - 0.5
      default: 0.35
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_max_time:
      type: scalar
      range:
      - 2.0
      - 8.0
      default: 5.0
      binds_to:
      - path: duration.max_time
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.1
      - 0.5
      default: 0.3
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: push_hinge

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=world_z, tolerance=0.05
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **contact_1** (`contact`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - contact_force_threshold: status=consumed; consumers=termination.force_threshold (replace)
    - contact_speed: status=consumed; consumers=generator.speed (replace)
- **push_1** (`push`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_x, distance=0.35, mode=add_to_offset, sign=positive}
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_max_time: status=consumed; consumers=duration.max_time (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: 0.252
- **task_score** (E): 0.546
- **fitness_score**: 0.546  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.167
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.460

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 0.00 | 1.00 | 0.2557 |
| align_1 | 0.67 | 0.33 | 0.0732 |
| contact_1 | 0.67 | 0.67 | 0.0309 |
| push_1 | 0.33 | 0.33 | 0.0509 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 0.00 / step_budget | (0.100, 0.399, 0.350)→(0.066, 0.162, 0.439) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 2.667 | 349.333 | 2039.378 |
| align_1 | align | 0.67 / step_budget | (0.066, 0.162, 0.439)→(0.080, 0.166, 0.368) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 0.33 / 2.000 | 0.125 | 1186.557 |
| contact_1 | contact | 0.67 / force_exceeded | (0.080, 0.166, 0.368)→(0.089, 0.181, 0.394) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 0.67 / 2.333 | 150.716 | 47.075 |
| push_1 | push | 0.33 / guard_failure | (0.096, 0.194, 0.414)→(0.113, 0.224, 0.451) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 0.33 / 0.333 | 0.000 | 32.875 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- hinge_angle_ratio: 0.622
- arc_quality: 0.500

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.646
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.646
- **Median Q (composite search score)**: 0.186
- **K-run variance**: 0.0128
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.381


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":6.65909,"average_solve_count":44.0,"average_success_count":44.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.align_speed":0.10603,"approach_1.approach_speed":0.37773,"approach_1.arc_height":0.24781,"contact_1.contact_force_threshold":6.08731,"contact_1.contact_speed":0.05433,"push_1.push_distance":0.19407,"push_1.push_max_time":5.01927,"push_1.push_speed":0.11831},"optimized_scores":{"best_composite_score":0.15883,"best_fitness_score":0.36883,"best_task_score":0.36883},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link5","contact_count":284.0,"contact_point_centroid":[0.10152,0.21455,0.59336],"force_p95":501.08866,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1531.77591,"mean_force":377.77382,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.0567,0.25478,0.42725]},{"body_a":"door_panel","body_b":"link4","contact_count":452.0,"contact_point_centroid":[0.10592,0.13316,0.61474],"force_p95":556.61716,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1003.82518,"mean_force":493.58018,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.05372,0.14763,0.41934]},{"body_a":"door_panel","body_b":"link4","contact_count":293.0,"contact_point_centroid":[0.10088,0.22975,0.63747],"force_p95":534.74403,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":576.38914,"mean_force":435.99939,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.05946,0.31437,0.42638]},{"body_a":"door_panel","body_b":"link7","contact_count":456.0,"contact_point_centroid":[0.10575,0.13314,0.40933],"force_p95":200.14161,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":336.79182,"mean_force":152.02739,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.05373,0.14779,0.41948]},{"body_a":"door_panel","body_b":"link7","contact_count":115.0,"contact_point_centroid":[0.10085,0.18489,0.42457],"force_p95":214.45733,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":224.09574,"mean_force":156.01768,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.05154,0.19881,0.43863]},{"body_a":"door_panel","body_b":"link4","contact_count":1.0,"contact_point_centroid":[0.10369,0.14726,0.61556],"force_p95":132.88355,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":132.88355,"mean_force":132.88355,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.05492,0.16203,0.4181]},{"body_a":"door_panel","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.10352,0.14721,0.40752],"force_p95":88.64952,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":88.64952,"mean_force":88.64952,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.05492,0.16203,0.4181]},{"body_a":"door_panel","body_b":"link4","contact_count":3.0,"contact_point_centroid":[0.10369,0.14716,0.61563],"force_p95":61.1062,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":61.15586,"mean_force":58.34874,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.05487,0.16208,0.4181]},{"body_a":"door_panel","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.1035,0.14721,0.40751],"force_p95":52.50424,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":52.50424,"mean_force":52.50424,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.05489,0.16207,0.4181]},{"body_a":"door_panel","body_b":"link5","contact_count":1.0,"contact_point_centroid":[0.10289,0.15217,0.59818],"force_p95":14.62037,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":14.62037,"mean_force":14.62037,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.05403,0.16812,0.43685]},{"body_a":"world","body_b":"door_panel","contact_count":560.0,"contact_point_centroid":[0.30031,0.20539,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.05939,0.28731,0.42411]},{"body_a":"world","body_b":"door_panel","contact_count":580.0,"contact_point_centroid":[0.30442,0.15714,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.05376,0.14858,0.41992]},{"body_a":"world","body_b":"door_panel","contact_count":4.0,"contact_point_centroid":[0.30307,0.16371,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.05492,0.16203,0.4181]},{"body_a":"world","body_b":"door_panel","contact_count":4.0,"contact_point_centroid":[0.30308,0.16362,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.05485,0.16209,0.41809]}],"total_contact_groups":14},"final_pose_error":0.19408,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.05483,0.16209,0.41809],"hinge_angle":0.13287,"initial_hinge_angle":-0.0604,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":-0.0604,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":1531.77591,"phases":[{"contact_detected":true,"contact_event_count":6.0,"n_steps":542.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.63123,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1252.0,"raw_peak_contact_force":1531.77591,"subtask_id":"approach_door","tcp_end":[0.05403,0.16812,0.43685],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.47119,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":6.0,"n_steps":466.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.37517,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":1489.0,"raw_peak_contact_force":1003.82518,"subtask_id":"approach_door","tcp_end":[0.05492,0.16203,0.4181],"tcp_start":[0.05403,0.16812,0.43685],"tcp_to_object_dist_end":0.45174,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":443.80517,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":6.0,"raw_peak_contact_force":132.88355,"subtask_id":"approach_door","tcp_end":[0.05489,0.16207,0.4181],"tcp_start":[0.05492,0.16203,0.4181],"tcp_to_object_dist_end":0.45176,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":8.0,"raw_peak_contact_force":61.15586,"subtask_id":"push_hinge","tcp_end":[0.05483,0.16209,0.41809],"tcp_start":[0.05485,0.16209,0.41809],"tcp_to_object_dist_end":0.45175,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `6091bac9443f311cc90f1388d6700bb5b9c315c724ba8069ca061d7c4a07c1f1`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":6.34737,"average_solve_count":95.0,"average_success_count":95.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.align_speed":0.05009,"approach_1.approach_speed":0.40582,"approach_1.arc_height":0.23374,"contact_1.contact_force_threshold":7.61486,"contact_1.contact_speed":0.07707,"push_1.push_distance":0.20339,"push_1.push_max_time":7.98981,"push_1.push_speed":0.19382},"optimized_scores":{"best_composite_score":0.41173,"best_fitness_score":0.62173,"best_task_score":0.62173},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link4","contact_count":489.0,"contact_point_centroid":[0.10244,0.16254,0.63386],"force_p95":795.67052,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2245.8533,"mean_force":647.02027,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.03875,0.2846,0.421]},{"body_a":"door_panel","body_b":"link4","contact_count":217.0,"contact_point_centroid":[0.12811,0.05619,0.62704],"force_p95":989.60455,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1243.41949,"mean_force":723.86713,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.06328,0.12535,0.43263]},{"body_a":"door_panel","body_b":"link4","contact_count":132.0,"contact_point_centroid":[0.13865,0.0285,0.64014],"force_p95":11.53097,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":37.46922,"mean_force":9.54071,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.10754,0.1937,0.3885]},{"body_a":"door_panel","body_b":"link4","contact_count":2.0,"contact_point_centroid":[0.13601,0.03415,0.63297],"force_p95":8.30553,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":8.34194,"mean_force":7.97785,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.10123,0.18249,0.36907]},{"body_a":"world","body_b":"door_panel","contact_count":496.0,"contact_point_centroid":[0.30154,0.1783,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.0433,0.29088,0.41803]},{"body_a":"world","body_b":"door_panel","contact_count":912.0,"contact_point_centroid":[0.32221,0.1083,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.07507,0.14698,0.38413]},{"body_a":"world","body_b":"door_panel","contact_count":468.0,"contact_point_centroid":[0.32258,0.10714,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.097,0.17524,0.35485]},{"body_a":"world","body_b":"door_panel","contact_count":376.0,"contact_point_centroid":[0.32388,0.10472,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.10978,0.19778,0.39487]}],"total_contact_groups":8},"final_pose_error":0.13052,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.12207,0.22038,0.42852],"hinge_angle":0.45503,"initial_hinge_angle":0.12924,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.12924,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":2245.8533,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":542.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":551.22849,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":985.0,"raw_peak_contact_force":2245.8533,"subtask_id":"approach_door","tcp_end":[0.06889,0.1606,0.43583],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.46956,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":996.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":1129.0,"raw_peak_contact_force":1243.41949,"subtask_id":"approach_door","tcp_end":[0.09345,0.16924,0.34157],"tcp_start":[0.06889,0.1606,0.43583],"tcp_to_object_dist_end":0.39249,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":471.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":8.34194,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":470.0,"raw_peak_contact_force":8.34194,"subtask_id":"approach_door","tcp_end":[0.10126,0.18254,0.36915],"tcp_start":[0.09345,0.16924,0.34157],"tcp_to_object_dist_end":0.42408,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":424.0,"n_steps_budget":660.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":508.0,"raw_peak_contact_force":37.46922,"subtask_id":"push_hinge","tcp_end":[0.12207,0.22038,0.42852],"tcp_start":[0.12207,0.22037,0.42849],"tcp_to_object_dist_end":0.49709,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `3d62b54ff2d8b84e841b6e4711bcf5c00d2771c3332b770c71c3a72dad860645`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":6.67568,"average_solve_count":111.0,"average_success_count":111.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.align_speed":0.11651,"approach_1.approach_speed":0.31711,"approach_1.arc_height":0.14331,"contact_1.contact_force_threshold":5.0852,"contact_1.contact_speed":0.06631,"push_1.push_distance":0.35734,"push_1.push_max_time":3.13789,"push_1.push_speed":0.14256},"optimized_scores":{"best_composite_score":0.18646,"best_fitness_score":0.64646,"best_task_score":0.64646},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link4","contact_count":478.0,"contact_point_centroid":[0.10377,0.15554,0.63772],"force_p95":898.35973,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2340.50552,"mean_force":658.25241,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.03871,0.29901,0.43486]},{"body_a":"door_panel","body_b":"link4","contact_count":154.0,"contact_point_centroid":[0.13627,0.03753,0.63078],"force_p95":1030.35716,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1312.42718,"mean_force":790.22996,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.07119,0.12449,0.43846]},{"body_a":"world","body_b":"door_panel","contact_count":524.0,"contact_point_centroid":[0.30189,0.17663,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.04167,0.31976,0.42514]},{"body_a":"world","body_b":"door_panel","contact_count":408.0,"contact_point_centroid":[0.33068,0.09432,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.0776,0.14348,0.39611]},{"body_a":"world","body_b":"door_panel","contact_count":812.0,"contact_point_centroid":[0.33289,0.08967,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.10012,0.18309,0.37036]},{"body_a":"world","body_b":"door_panel","contact_count":936.0,"contact_point_centroid":[0.3303,0.09369,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.13327,0.23873,0.44708]}],"total_contact_groups":6},"final_pose_error":0.21109,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.16117,0.2891,0.50544],"hinge_angle":0.49792,"initial_hinge_angle":0.15917,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.15917,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":2340.50552,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":544.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":496.13992,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1002.0,"raw_peak_contact_force":2340.50552,"subtask_id":"approach_door","tcp_end":[0.07645,0.15758,0.44452],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.47778,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":513.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":562.0,"raw_peak_contact_force":1312.42718,"subtask_id":"approach_door","tcp_end":[0.09179,0.16819,0.34426],"tcp_start":[0.07645,0.15758,0.44452],"tcp_to_object_dist_end":0.39399,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":812.0,"raw_peak_contact_force":0.0,"subtask_id":"approach_door","tcp_end":[0.11033,0.1983,0.39394],"tcp_start":[0.09179,0.16819,0.34426],"tcp_to_object_dist_end":0.45463,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":936.0,"raw_peak_contact_force":0.0,"subtask_id":"push_hinge","tcp_end":[0.16117,0.2891,0.50544],"tcp_start":[0.11033,0.1983,0.39394],"tcp_to_object_dist_end":0.60418,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
```