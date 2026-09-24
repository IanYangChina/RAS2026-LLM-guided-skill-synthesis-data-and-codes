## Search State

- **Seed**: 4
- **Iteration**: 11 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 10 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | force_exceeded | time_limit | 8 | 0.3815 | 0.17 | ❌ rejected |
| 9 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | force_exceeded | time_limit | 9 | 0.3094 | 0.15 | ❌ rejected |
| 8 | approach → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | pose_tolerance | force_exceeded | time_limit | 7 | -0.1949 | 0.19 | ❌ rejected |
| 7 | approach → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | pose_tolerance | force_exceeded | time_limit | 7 | -0.0396 | 0.34 | ❌ rejected |
| 6 | approach → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | pose_tolerance | force_exceeded | time_limit | 6 | 0.1933 | 0.36 | ✅ accepted |

**Proposal policy**: task_score is 0.17 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.381) — your mutation base

```yaml
skill: door_push
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: push_door
  target_entity: hinge
  metric: hinge_angle
phases:
- id: approach_door
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
    - 0.0
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
- id: push_door
  type: push
  generator: linear_cartesian
  control: position_control
  termination: force_exceeded
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.2
      axis: world_x
      mode: add_to_offset
      sign: positive
  parameters:
    force_threshold:
      type: scalar
      range:
      - 10.0
      - 30.0
      default: 25.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    push_distance:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.2
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
  guards:
  - id: contact_check
    when: during_phase
    predicate: contact_detected
    threshold: 1.0
    on_failure: continue
- id: retract
  type: retract
  generator: linear_cartesian
  control: position_control
  termination: time_limit
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.1
      axis: world_x
      mode: add_to_offset
      sign: negative
  parameters:
    retract_distance:
      type: scalar
      range:
      - 0.05
      - 0.15
      default: 0.1
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    retract_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_door** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0]
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **push_door** (`push`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_x, distance=0.2, mode=add_to_offset, sign=positive}
  - parameter_bindings:
    - force_threshold: status=consumed; consumers=termination.force_threshold (replace)
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=contact_check, when=during_phase, predicate=contact_detected, on_failure=continue, threshold=1.0
- **retract** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_x, distance=0.1, mode=add_to_offset, sign=negative}
  - parameter_bindings:
    - retract_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - retract_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: 0.381
- **task_score** (E): 0.175
- **fitness_score**: 0.175  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.667
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.460

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_handle | 0.00 | 1.00 | 0.1713 |
| descend_to_handle | 1.00 | 1.00 | 0.0001 |
| push_door | 1.00 | 1.00 | 0.0001 |
| retract | 1.00 | 1.00 | 0.1304 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_handle | approach | 0.00 / step_budget | (0.100, 0.399, 0.350)→(0.248, 0.325, 0.393) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 1.000 | 417.291 | 440.452 |
| descend_to_handle | descend | 1.00 / force_exceeded | (0.248, 0.325, 0.393)→(0.248, 0.325, 0.393) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 2.333 | 43.686 | 53.919 |
| push_door | push | 1.00 / force_exceeded | (0.248, 0.325, 0.393)→(0.248, 0.325, 0.393) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 2.333 | 51.673 | 55.842 |
| retract | retract | 1.00 / time_limit | (0.248, 0.325, 0.393)→(0.212, 0.264, 0.283) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 1.000 | 274.667 | 351.225 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- hinge_angle_ratio: 0.251
- arc_quality: 0.750

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.251
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.251
- **Median Q (composite search score)**: 0.450
- **K-run variance**: 0.0105
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.360


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `6e4aa099e94fbceab0cbffcfa0782e5dc3f2f920fda4dd08a29a8751703a4594`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"hinge_delta_deg":10.0,"object_xy_delta":[0.0,0.0]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `1d4a12af4ca966b9ae057d85a80c022f8f485e56fbc5d1e540c4eac6bafb8e2f`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.37615,"average_solve_count":109.0,"average_success_count":109.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_handle.approach_speed":0.08348,"descend_to_handle.contact_force":12.38929,"descend_to_handle.descend_speed":0.03071,"push_door.push_distance":0.273,"push_door.push_force_threshold":21.93163,"push_door.push_speed":0.07306,"retract.retract_distance":0.14926,"retract.retract_speed":0.05402},"optimized_scores":{"best_composite_score":0.44967,"best_fitness_score":0.243,"best_task_score":0.243},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link5","contact_count":241.0,"contact_point_centroid":[0.10584,0.13272,0.6353],"force_p95":375.20092,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":378.16897,"mean_force":290.76126,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.2447,0.32568,0.38687]},{"body_a":"door_panel","body_b":"link4","contact_count":344.0,"contact_point_centroid":[0.1136,0.09679,0.63269],"force_p95":284.89318,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":297.44569,"mean_force":187.04665,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.22647,0.26383,0.28628]},{"body_a":"door_panel","body_b":"link5","contact_count":3.0,"contact_point_centroid":[0.108,0.12073,0.63772],"force_p95":36.25673,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":38.4707,"mean_force":22.15525,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.25918,0.31907,0.39316]},{"body_a":"door_panel","body_b":"link5","contact_count":238.0,"contact_point_centroid":[0.10966,0.11274,0.61857],"force_p95":26.43553,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":29.91329,"mean_force":17.20701,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.24567,0.2957,0.34699]},{"body_a":"door_panel","body_b":"link5","contact_count":1.0,"contact_point_centroid":[0.10799,0.12093,0.63773],"force_p95":15.06975,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":15.06975,"mean_force":15.06975,"phase_index":1.0,"phase_name":"descend_to_handle","phase_type":"descend","tcp_position_centroid":[0.25907,0.31915,0.39316]},{"body_a":"world","body_b":"door_panel","contact_count":1044.0,"contact_point_centroid":[0.30401,0.15896,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.18546,0.35529,0.36971]},{"body_a":"world","body_b":"door_panel","contact_count":4.0,"contact_point_centroid":[0.30595,0.15054,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.25921,0.31904,0.39315]},{"body_a":"world","body_b":"door_panel","contact_count":1036.0,"contact_point_centroid":[0.30783,0.14385,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.23873,0.28408,0.32485]}],"total_contact_groups":8},"final_pose_error":0.00981,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.22223,0.25685,0.27349],"hinge_angle":0.28199,"initial_hinge_angle":0.15466,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.15466,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":378.16897,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":338.55524,"phase_name":"approach_handle","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1285.0,"raw_peak_contact_force":378.16897,"subtask_id":"reach_handle","tcp_end":[0.25907,0.31915,0.39316],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.56882,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":15.06975,"phase_name":"descend_to_handle","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1.0,"raw_peak_contact_force":15.06975,"subtask_id":"reach_handle","tcp_end":[0.25915,0.3191,0.39318],"tcp_start":[0.25907,0.31915,0.39316],"tcp_to_object_dist_end":0.56883,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":38.4707,"phase_name":"push_door","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":7.0,"raw_peak_contact_force":38.4707,"subtask_id":"push_door","tcp_end":[0.25923,0.31904,0.39316],"tcp_start":[0.25915,0.3191,0.39318],"tcp_to_object_dist_end":0.56883,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":237.3752,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1618.0,"raw_peak_contact_force":297.44569,"tcp_end":[0.22223,0.25685,0.27349],"tcp_start":[0.25923,0.31904,0.39316],"tcp_to_object_dist_end":0.43607,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `74b09c110110eedfa033ccf01fd9064bfaa53943493bfa1a44417e7ed7258576`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.85057,"average_solve_count":87.0,"average_success_count":87.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_handle.approach_speed":0.04952,"descend_to_handle.contact_force":9.78203,"descend_to_handle.descend_speed":0.02205,"push_door.push_distance":0.18158,"push_door.push_force_threshold":25.63076,"push_door.push_speed":0.03405,"retract.retract_distance":0.14998,"retract.retract_speed":0.0921},"optimized_scores":{"best_composite_score":0.4581,"best_fitness_score":0.25143,"best_task_score":0.25143},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link5","contact_count":276.0,"contact_point_centroid":[0.1029,0.15343,0.63009],"force_p95":487.38779,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":495.91697,"mean_force":380.1283,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.23586,0.32963,0.38561]},{"body_a":"door_panel","body_b":"link5","contact_count":735.0,"contact_point_centroid":[0.10551,0.1345,0.61545],"force_p95":318.73424,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":419.06142,"mean_force":219.79254,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.22859,0.29853,0.34672]},{"body_a":"door_panel","body_b":"link4","contact_count":76.0,"contact_point_centroid":[0.11097,0.10716,0.62694],"force_p95":268.6342,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":296.56187,"mean_force":207.91274,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.21097,0.26226,0.27603]},{"body_a":"door_panel","body_b":"link5","contact_count":1.0,"contact_point_centroid":[0.10385,0.14589,0.63451],"force_p95":86.43378,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":86.43378,"mean_force":86.43378,"phase_index":1.0,"phase_name":"descend_to_handle","phase_type":"descend","tcp_position_centroid":[0.2467,0.32351,0.39473]},{"body_a":"door_panel","body_b":"link5","contact_count":1.0,"contact_point_centroid":[0.10385,0.14583,0.63454],"force_p95":74.83398,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":74.83398,"mean_force":74.83398,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.24675,0.32347,0.39479]},{"body_a":"world","body_b":"door_panel","contact_count":1128.0,"contact_point_centroid":[0.30225,0.16849,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.18392,0.3559,0.36966]},{"body_a":"world","body_b":"door_panel","contact_count":916.0,"contact_point_centroid":[0.30488,0.15538,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.22617,0.29335,0.33665]}],"total_contact_groups":7},"final_pose_error":0.00796,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.20925,0.26053,0.27265],"hinge_angle":0.23822,"initial_hinge_angle":0.10647,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.10647,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":495.91697,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":480.48605,"phase_name":"approach_handle","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1404.0,"raw_peak_contact_force":495.91697,"subtask_id":"reach_handle","tcp_end":[0.2467,0.32351,0.39473],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.56686,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":86.43378,"phase_name":"descend_to_handle","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1.0,"raw_peak_contact_force":86.43378,"subtask_id":"reach_handle","tcp_end":[0.24675,0.32347,0.39479],"tcp_start":[0.2467,0.32351,0.39473],"tcp_to_object_dist_end":0.5669,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":74.83398,"phase_name":"push_door","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1.0,"raw_peak_contact_force":74.83398,"subtask_id":"push_door","tcp_end":[0.24677,0.32345,0.39482],"tcp_start":[0.24675,0.32347,0.39479],"tcp_to_object_dist_end":0.56692,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":951.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":264.35657,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1727.0,"raw_peak_contact_force":419.06142,"tcp_end":[0.20925,0.26053,0.27265],"tcp_start":[0.24677,0.32345,0.39482],"tcp_to_object_dist_end":0.43127,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `19b9b4f2c5af25040a197573455096dd2f805f94d78c64c4126be8f0525fbcc6`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.84091,"average_solve_count":88.0,"average_success_count":88.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_handle.approach_speed":0.05325,"descend_to_handle.contact_force":11.00498,"descend_to_handle.descend_speed":0.03662,"push_door.push_distance":0.39751,"push_door.push_force_threshold":24.79854,"push_door.push_speed":0.06037,"retract.retract_distance":0.14999,"retract.retract_speed":0.09209},"optimized_scores":{"best_composite_score":0.23668,"best_fitness_score":0.03001,"best_task_score":0.03001},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link5","contact_count":284.0,"contact_point_centroid":[0.10064,0.17218,0.63362],"force_p95":439.19444,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":447.27055,"mean_force":365.18967,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.2329,0.3321,0.38453]},{"body_a":"door_panel","body_b":"link5","contact_count":938.0,"contact_point_centroid":[0.1005,0.17272,0.61328],"force_p95":326.61861,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":337.1679,"mean_force":268.82325,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.21734,0.30426,0.34128]},{"body_a":"door_panel","body_b":"link5","contact_count":1.0,"contact_point_centroid":[0.10076,0.17082,0.63621],"force_p95":60.25367,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":60.25367,"mean_force":60.25367,"phase_index":1.0,"phase_name":"descend_to_handle","phase_type":"descend","tcp_position_centroid":[0.23877,0.33142,0.39034]},{"body_a":"door_panel","body_b":"link5","contact_count":2.0,"contact_point_centroid":[0.10075,0.17078,0.63619],"force_p95":53.59717,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":54.22265,"mean_force":47.96783,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.23876,0.33142,0.39036]},{"body_a":"world","body_b":"door_panel","contact_count":972.0,"contact_point_centroid":[0.30017,0.18701,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.18406,0.35607,0.36958]},{"body_a":"world","body_b":"door_panel","contact_count":4.0,"contact_point_centroid":[0.30028,0.18539,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.23877,0.33142,0.39036]},{"body_a":"world","body_b":"door_panel","contact_count":940.0,"contact_point_centroid":[0.30022,0.1863,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.21808,0.305,0.34283]}],"total_contact_groups":7},"final_pose_error":0.04422,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.2035,0.27549,0.30401],"hinge_angle":0.02905,"initial_hinge_angle":0.01332,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.01332,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":447.27055,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":432.83301,"phase_name":"approach_handle","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1256.0,"raw_peak_contact_force":447.27055,"subtask_id":"reach_handle","tcp_end":[0.23877,0.33142,0.39034],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.56499,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":29.55337,"phase_name":"descend_to_handle","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1.0,"raw_peak_contact_force":60.25367,"subtask_id":"reach_handle","tcp_end":[0.23877,0.33142,0.39036],"tcp_start":[0.23877,0.33142,0.39034],"tcp_to_object_dist_end":0.56501,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":2.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":41.71301,"phase_name":"push_door","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":6.0,"raw_peak_contact_force":54.22265,"subtask_id":"push_door","tcp_end":[0.23874,0.33143,0.39037],"tcp_start":[0.23877,0.33142,0.39036],"tcp_to_object_dist_end":0.56501,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":962.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":322.26878,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1878.0,"raw_peak_contact_force":337.1679,"tcp_end":[0.2035,0.27549,0.30401],"tcp_start":[0.23874,0.33143,0.39037],"tcp_to_object_dist_end":0.45796,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
```