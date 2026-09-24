## Search State

- **Seed**: 3
- **Iteration**: 10 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 9 | rotate → retract → descend → pull | impedance_motion | arc_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | admittance_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 3 | 0.7628 | 0.97 | ✅ accepted |
| 8 | rotate → retract → descend → pull | impedance_motion | arc_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | admittance_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 3 | 0.7627 | 0.97 | ✅ accepted |
| 7 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | admittance_control | admittance_control | pose_tolerance | force_exceeded | force_exceeded | 6 | 1.2189 | 0.88 | ❌ rejected |
| 6 | approach → retract → descend → insert | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | admittance_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | 5 | 0.3242 | 0.82 | ❌ rejected |
| 5 | approach → retract → descend → push | arc_cartesian | arc_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | admittance_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | 4 | 0.5934 | 0.85 | ❌ rejected |

**Proposal policy**: task_score is near-perfect (0.97). Preserve useful working parts and make only evidence-backed refinements. A HOLD is acceptable if you genuinely cannot find a better structure.

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

- Task name: peg_insert
- Goal tolerance: 0.02 m
- Expressivity sigma: 0.15 m
- Expressivity threshold: 0.3
- Force limit: 40.0 N
- Primary evaluation target: **insertion depth ratio (axial progress into hole)**

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
| `object` | offset from object initial position | approach/contact targets near object start |
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

## Current Skill (Q=0.763) — your mutation base

```yaml
skill: peg_insert
dsl_version: 2
phases:
- id: rotate_1
  type: rotate
  generator: impedance_motion
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    orientation:
      mode: none
- id: retract_1
  type: retract
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.1
      axis: world_z
      mode: add_to_offset
      sign: positive
    orientation:
      mode: keep_current
  parameters:
    retract_height:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
- id: descend_1
  type: descend
  generator: linear_cartesian
  control: admittance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.05
      axis: world_z
      mode: add_to_offset
      sign: negative
    orientation:
      mode: keep_current
  parameters:
    depth:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
- id: pull_1
  type: pull
  generator: arc_cartesian
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
      distance: 0.1
      axis: world_z
      mode: add_to_offset
      sign: negative
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: world_z
      tolerance: 0.1
  parameters:
    pull_distance:
      type: scalar
      range:
      - 0.02
      - 0.2
      default: 0.1
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **rotate_1** (`rotate`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - orientation: mode=none
  - parameter_bindings: none
- **retract_1** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.1, mode=add_to_offset, sign=positive}
  - orientation: mode=keep_current
  - parameter_bindings:
    - retract_height: status=consumed; consumers=target.offset_along_axis.distance (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.05, mode=add_to_offset, sign=negative}
  - orientation: mode=keep_current
  - parameter_bindings:
    - depth: status=consumed; consumers=target.offset_along_axis.distance (replace)
- **pull_1** (`pull`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.1, mode=add_to_offset, sign=negative}
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=world_z, tolerance=0.1
  - parameter_bindings:
    - pull_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)

## Design Metrics

- **Composite score**: 0.763
- **task_score** (E): 0.973
- **fitness_score**: 0.973  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.210

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| rotate_1 | 1.00 | 0.00 | 0.0017 |
| retract_1 | 1.00 | 0.00 | 0.0520 |
| descend_1 | 1.00 | 0.00 | 0.0844 |
| pull_1 | 1.00 | 1.00 | 0.1055 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| rotate_1 | rotate | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.499, -0.000, 0.299) | (0.504, -0.000, 0.340)→(0.503, -0.000, 0.339) | 0.260→0.259 | 0.00 / 0.000 | 0.000 | 0.000 |
| retract_1 | retract | 1.00 / step_budget | (0.499, -0.000, 0.299)→(0.497, 0.002, 0.351) | (0.503, -0.000, 0.339)→(0.502, 0.002, 0.391) | 0.259→0.311 | 0.00 / 0.000 | 0.000 | 0.000 |
| descend_1 | descend | 1.00 / step_budget | (0.497, 0.002, 0.351)→(0.495, 0.001, 0.267) | (0.502, 0.002, 0.391)→(0.500, 0.001, 0.306) | 0.311→0.226 | 0.00 / 0.000 | 0.000 | 0.000 |
| pull_1 | pull | 1.00 / time_limit | (0.495, 0.001, 0.267)→(0.543, 0.022, 0.219) | (0.500, 0.001, 0.306)→(0.564, 0.022, 0.189) | 0.226→0.132 | 1.00 / 1.333 | 351.299 | 4339.479 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.978
- alignment_error: None
- force_efficiency: 0.000

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.978
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.978
- **Median Q (composite search score)**: 0.763
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 10.0
- **Final σ (mean)**: 0.428


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `2fc05e51a25fc23cdfa051e1c0c9cb8327fc4318047dd2c0794162fe696d964b`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `78de15924f40c9df864f10a8c33fe438e6928bbf6063e6b2cf47f87609839b79`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.63542,"average_solve_count":96.0,"average_success_count":96.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"descend_1.depth":0.0889,"pull_1.pull_distance":0.04584,"retract_1.retract_height":0.05489},"optimized_scores":{"best_composite_score":0.76839,"best_fitness_score":0.97839,"best_task_score":0.97839},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link7","contact_count":743.0,"contact_point_centroid":[0.5266,0.00429,0.06513],"force_p95":336.75232,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":10446.5906,"mean_force":470.14088,"phase_index":3.0,"phase_name":"pull_1","phase_type":"pull","tcp_position_centroid":[0.46019,0.00642,0.1194]},{"body_a":"attachment","body_b":"peg_socket","contact_count":97.0,"contact_point_centroid":[0.51926,0.00693,0.07853],"force_p95":7205.43075,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":7849.08231,"mean_force":1131.75144,"phase_index":3.0,"phase_name":"pull_1","phase_type":"pull","tcp_position_centroid":[0.47185,0.0067,0.10523]},{"body_a":"peg_socket","body_b":"link7","contact_count":13.0,"contact_point_centroid":[0.52662,0.00658,0.04903],"force_p95":3037.39111,"geom_a":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":3041.31939,"mean_force":2005.76178,"phase_index":3.0,"phase_name":"pull_1","phase_type":"pull","tcp_position_centroid":[0.44085,0.00677,0.10324]},{"body_a":"attachment","body_b":"peg_socket","contact_count":5.0,"contact_point_centroid":[0.49684,0.00896,0.0799],"force_p95":916.56729,"geom_a":"peg_tip","geom_b":"socket_collar_y1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1047.46869,"mean_force":397.01777,"phase_index":3.0,"phase_name":"pull_1","phase_type":"pull","tcp_position_centroid":[0.43995,0.00628,0.10169]},{"body_a":"world","body_b":"link6","contact_count":533.0,"contact_point_centroid":[0.67862,0.00892,-5e-05],"force_p95":297.00481,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":845.13619,"mean_force":90.55272,"phase_index":3.0,"phase_name":"pull_1","phase_type":"pull","tcp_position_centroid":[0.46288,0.00716,0.12284]}],"total_contact_groups":5},"final_pose_error":0.10967,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.46685,-0.02106,0.025],"final_tcp_position":[0.47048,0.00905,0.13955],"realised_fixture_position":[0.46685,-0.02106,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.46685,-0.02106,0.08]},"peak_contact_force":10446.5906,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":20.0,"n_steps_budget":600.0,"object_pos_end":[0.50343,-0.0,0.33877],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.25879,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"rotate_1","phase_peak_obstacle_force":0.0,"phase_type":"rotate","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.49918,-1e-05,0.299],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":452.0,"n_steps_budget":600.0,"object_pos_end":[0.5021,0.00149,0.38396],"object_pos_start":[0.50343,-0.0,0.33877],"object_to_goal_dist_end":0.30397,"object_to_goal_dist_start":0.25879,"object_z_max":0.38388,"peak_contact_force":0.0,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.49738,0.00147,0.34424],"tcp_start":[0.49918,-1e-05,0.299],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":245.0,"n_steps_budget":600.0,"object_pos_end":[0.50034,0.00146,0.30465],"object_pos_start":[0.5021,0.00149,0.38396],"object_to_goal_dist_end":0.22466,"object_to_goal_dist_start":0.30397,"object_z_max":0.384,"peak_contact_force":0.0,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.49516,0.00144,0.26499],"tcp_start":[0.49738,0.00147,0.34424],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50656,0.00885,0.12229],"object_pos_start":[0.50034,0.00146,0.30465],"object_to_goal_dist_end":0.0437,"object_to_goal_dist_start":0.22466,"object_z_max":0.30465,"peak_contact_force":202.90787,"phase_name":"pull_1","phase_peak_obstacle_force":0.0,"phase_type":"pull","raw_contact_event_count":1391.0,"raw_peak_contact_force":10446.5906,"tcp_end":[0.47048,0.00905,0.13955],"tcp_start":[0.49516,0.00144,0.26499],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `23bedb35dfb8044c9064b13b9f8101cd4e2be35581b8354b6b999b22e5fca070`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.8866,"average_solve_count":97.0,"average_success_count":97.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"descend_1.depth":0.09997,"pull_1.pull_distance":0.07042,"retract_1.retract_height":0.06785},"optimized_scores":{"best_composite_score":0.76325,"best_fitness_score":0.97325,"best_task_score":0.97325},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link7","contact_count":761.0,"contact_point_centroid":[0.59527,0.01672,0.07983],"force_p95":386.12077,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1607.06415,"mean_force":269.56703,"phase_index":3.0,"phase_name":"pull_1","phase_type":"pull","tcp_position_centroid":[0.50664,0.01056,0.10766]},{"body_a":"attachment","body_b":"peg_socket","contact_count":38.0,"contact_point_centroid":[0.50229,0.02066,0.07824],"force_p95":1164.22254,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1168.1749,"mean_force":417.65095,"phase_index":3.0,"phase_name":"pull_1","phase_type":"pull","tcp_position_centroid":[0.49868,0.00595,0.07799]},{"body_a":"world","body_b":"link5","contact_count":58.0,"contact_point_centroid":[0.52721,0.13693,-0.00056],"force_p95":623.19388,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":720.34182,"mean_force":407.1019,"phase_index":3.0,"phase_name":"pull_1","phase_type":"pull","tcp_position_centroid":[0.56629,0.03782,0.24649]},{"body_a":"peg_socket","body_b":"link5","contact_count":12.0,"contact_point_centroid":[0.51555,0.06058,0.06618],"force_p95":636.71367,"geom_a":"socket_collar_y1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":640.32127,"mean_force":495.0643,"phase_index":3.0,"phase_name":"pull_1","phase_type":"pull","tcp_position_centroid":[0.56426,0.05317,0.26164]},{"body_a":"peg_socket","body_b":"link6","contact_count":8.0,"contact_point_centroid":[0.59526,0.06082,0.07953],"force_p95":586.22543,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":588.8274,"mean_force":334.8641,"phase_index":3.0,"phase_name":"pull_1","phase_type":"pull","tcp_position_centroid":[0.55631,-0.00323,0.20155]},{"body_a":"world","body_b":"link6","contact_count":8.0,"contact_point_centroid":[0.65356,0.12565,-0.00069],"force_p95":295.20706,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":454.16471,"mean_force":56.77059,"phase_index":3.0,"phase_name":"pull_1","phase_type":"pull","tcp_position_centroid":[0.56485,0.00708,0.2121]}],"total_contact_groups":6},"final_pose_error":0.2605,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.53544,0.00091,0.025],"final_tcp_position":[0.56387,0.05616,0.26256],"realised_fixture_position":[0.53544,0.00091,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.53544,0.00091,0.08]},"peak_contact_force":1607.06415,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":20.0,"n_steps_budget":600.0,"object_pos_end":[0.50343,-0.0,0.33877],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.25879,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"rotate_1","phase_peak_obstacle_force":0.0,"phase_type":"rotate","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.49918,-1e-05,0.299],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":498.0,"n_steps_budget":600.0,"object_pos_end":[0.50225,0.00153,0.3969],"object_pos_start":[0.50343,-0.0,0.33877],"object_to_goal_dist_end":0.31691,"object_to_goal_dist_start":0.25879,"object_z_max":0.39681,"peak_contact_force":0.0,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.49754,0.00151,0.35718],"tcp_start":[0.49918,-1e-05,0.299],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":276.0,"n_steps_budget":630.0,"object_pos_end":[0.5005,0.00151,0.30662],"object_pos_start":[0.50225,0.00153,0.3969],"object_to_goal_dist_end":0.22663,"object_to_goal_dist_start":0.31691,"object_z_max":0.39695,"peak_contact_force":0.0,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.49532,0.00148,0.26696],"tcp_start":[0.49754,0.00151,0.35718],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.57681,0.06634,0.22611],"object_pos_start":[0.5005,0.00151,0.30662],"object_to_goal_dist_end":0.1779,"object_to_goal_dist_start":0.22663,"object_z_max":0.30662,"peak_contact_force":577.00966,"phase_name":"pull_1","phase_peak_obstacle_force":0.0,"phase_type":"pull","raw_contact_event_count":885.0,"raw_peak_contact_force":1607.06415,"tcp_end":[0.56387,0.05616,0.26256],"tcp_start":[0.49532,0.00148,0.26696],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `0b9f57c3f8a8fdb0f6fef54a4b5c0cfa6a2779a7721b018896a4efe993ac60cd`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.59375,"average_solve_count":96.0,"average_success_count":96.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"descend_1.depth":0.09319,"pull_1.pull_distance":0.05413,"retract_1.retract_height":0.06225},"optimized_scores":{"best_composite_score":0.75682,"best_fitness_score":0.96682,"best_task_score":0.96682},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":24.0,"contact_point_centroid":[0.49169,0.0119,0.07853],"force_p95":944.89093,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":964.78322,"mean_force":383.59267,"phase_index":3.0,"phase_name":"pull_1","phase_type":"pull","tcp_position_centroid":[0.4909,0.01255,0.07364]},{"body_a":"peg_socket","body_b":"link7","contact_count":784.0,"contact_point_centroid":[0.5842,0.01869,0.0798],"force_p95":387.60411,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":888.96999,"mean_force":268.15717,"phase_index":3.0,"phase_name":"pull_1","phase_type":"pull","tcp_position_centroid":[0.49786,0.01707,0.11048]},{"body_a":"attachment","body_b":"peg_socket","contact_count":4.0,"contact_point_centroid":[0.50046,-0.00609,0.0786],"force_p95":789.63134,"geom_a":"peg_tip","geom_b":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":832.86092,"mean_force":536.39844,"phase_index":3.0,"phase_name":"pull_1","phase_type":"pull","tcp_position_centroid":[0.4992,0.00784,0.07995]},{"body_a":"peg_socket","body_b":"link6","contact_count":65.0,"contact_point_centroid":[0.58393,-0.03499,0.07977],"force_p95":603.59906,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":809.92663,"mean_force":338.58492,"phase_index":3.0,"phase_name":"pull_1","phase_type":"pull","tcp_position_centroid":[0.59202,0.03293,0.24135]},{"body_a":"world","body_b":"link6","contact_count":31.0,"contact_point_centroid":[0.67114,-0.04827,-0.00089],"force_p95":476.19709,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":497.1398,"mean_force":302.77258,"phase_index":3.0,"phase_name":"pull_1","phase_type":"pull","tcp_position_centroid":[0.57188,0.06737,0.20527]}],"total_contact_groups":5},"final_pose_error":0.24011,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.5244,0.02464,0.025],"final_tcp_position":[0.59503,0.00118,0.25416],"realised_fixture_position":[0.5244,0.02464,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.5244,0.02464,0.08]},"peak_contact_force":964.78322,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":20.0,"n_steps_budget":600.0,"object_pos_end":[0.50343,-0.0,0.33877],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.25879,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"rotate_1","phase_peak_obstacle_force":0.0,"phase_type":"rotate","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.49918,-1e-05,0.299],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":483.0,"n_steps_budget":600.0,"object_pos_end":[0.50221,0.00155,0.39123],"object_pos_start":[0.50343,-0.0,0.33877],"object_to_goal_dist_end":0.31124,"object_to_goal_dist_start":0.25879,"object_z_max":0.39115,"peak_contact_force":0.0,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.49751,0.00153,0.35151],"tcp_start":[0.49918,-1e-05,0.299],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":258.0,"n_steps_budget":600.0,"object_pos_end":[0.50047,0.00152,0.30755],"object_pos_start":[0.50221,0.00155,0.39123],"object_to_goal_dist_end":0.22755,"object_to_goal_dist_start":0.31124,"object_z_max":0.39127,"peak_contact_force":0.0,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.4953,0.0015,0.26788],"tcp_start":[0.49751,0.00153,0.35151],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.60878,-0.00837,0.21783],"object_pos_start":[0.50047,0.00152,0.30755],"object_to_goal_dist_end":0.17579,"object_to_goal_dist_start":0.22755,"object_z_max":0.30755,"peak_contact_force":273.97802,"phase_name":"pull_1","phase_peak_obstacle_force":0.0,"phase_type":"pull","raw_contact_event_count":908.0,"raw_peak_contact_force":964.78322,"tcp_end":[0.59503,0.00118,0.25416],"tcp_start":[0.4953,0.0015,0.26788],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
```