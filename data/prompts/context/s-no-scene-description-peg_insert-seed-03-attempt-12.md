## Search State

- **Seed**: 3
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | rotate → retract → descend → insert | impedance_motion | arc_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | admittance_control | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | force_exceeded | 5 | 0.6387 | 0.82 | ❌ rejected |
| 11 | approach → align → descend → insert | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | admittance_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | 7 | 0.3764 | 0.84 | ❌ rejected |
| 10 | approach → descend → pull | linear_cartesian | linear_cartesian | arc_cartesian | position_control | admittance_control | impedance_control | pose_tolerance | pose_tolerance | time_limit | 3 | 0.6763 | 0.86 | ❌ rejected |
| 9 | rotate → retract → descend → pull | impedance_motion | arc_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | admittance_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 3 | 0.7628 | 0.97 | ✅ accepted |
| 8 | rotate → retract → descend → pull | impedance_motion | arc_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | admittance_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 3 | 0.7627 | 0.97 | ✅ accepted |

**Proposal policy**: task_score is 0.82 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.639) — your mutation base

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

- **Composite score**: 0.639
- **task_score** (E): 0.816
- **fitness_score**: 0.449  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.500
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.310

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| rotate_1 | 0.00 | 1.00 | 0.1780 |
| retract_1 | 1.00 | 0.00 | 0.1629 |
| descend_1 | 1.00 | 1.00 | 0.1765 |
| insert_1 | 1.00 | 1.00 | 0.0001 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| rotate_1 | rotate | 0.00 / step_budget | (0.500, -0.000, 0.301)→(0.440, 0.000, 0.133) | (0.504, -0.000, 0.340)→(0.480, 0.000, 0.129) | 0.260→0.053 | 1.00 / 1.000 | 232.308 | 3387.021 |
| retract_1 | retract | 1.00 / step_budget | (0.440, 0.000, 0.133)→(0.439, 0.006, 0.296) | (0.480, 0.000, 0.129)→(0.479, 0.006, 0.291) | 0.053→0.213 | 0.00 / 0.000 | 0.000 | 202.194 |
| descend_1 | descend | 1.00 / force_exceeded | (0.439, 0.006, 0.296)→(0.478, 0.002, 0.126) | (0.479, 0.006, 0.291)→(0.518, 0.002, 0.121) | 0.213→0.047 | 1.00 / 1.000 | 78.500 | 37.877 |
| insert_1 | insert | 1.00 / force_exceeded | (0.478, 0.002, 0.126)→(0.478, 0.002, 0.125) | (0.518, 0.002, 0.121)→(0.518, 0.002, 0.120) | 0.047→0.047 | 1.00 / 1.000 | 290.265 | 290.265 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.816
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.816
- phase_score: 0.240
- phase_breakdown.descend_to_contact_score: 0.197
- phase_breakdown.insert_fully_score: 0.361
- phase_breakdown.reach_above_score: 0.002

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.471
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.816
- **Median Q (composite search score)**: 0.633
- **K-run variance**: 0.0003
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.395


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.75258,"average_solve_count":97.0,"average_success_count":97.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"descend_1.descend_distance":0.05097,"descend_1.force_threshold":37.26307,"insert_1.force_limit":20.43381,"insert_1.insert_distance":0.19391,"retract_1.retract_height":0.18838},"optimized_scores":{"best_composite_score":0.66052,"best_fitness_score":0.47052,"best_task_score":0.81629},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link7","contact_count":187.0,"contact_point_centroid":[0.52616,-0.0041,0.07935],"force_p95":382.04865,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1257.69697,"mean_force":278.40053,"phase_index":0.0,"phase_name":"rotate_1","phase_type":"rotate","tcp_position_centroid":[0.44388,-0.00022,0.11631]},{"body_a":"attachment","body_b":"peg_socket","contact_count":11.0,"contact_point_centroid":[0.43264,-0.00129,0.07905],"force_p95":955.49394,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1064.65858,"mean_force":249.58292,"phase_index":0.0,"phase_name":"rotate_1","phase_type":"rotate","tcp_position_centroid":[0.42977,-0.00025,0.09188]},{"body_a":"attachment","body_b":"peg_socket","contact_count":4.0,"contact_point_centroid":[0.43748,0.00906,0.07986],"force_p95":488.61101,"geom_a":"peg_tip","geom_b":"socket_collar_y1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":551.83251,"mean_force":170.54709,"phase_index":0.0,"phase_name":"rotate_1","phase_type":"rotate","tcp_position_centroid":[0.4331,-0.00012,0.09079]},{"body_a":"attachment","body_b":"peg_socket","contact_count":1.0,"contact_point_centroid":[0.52684,-0.01217,0.07989],"force_p95":314.23769,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":314.23769,"mean_force":314.23769,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.45743,-0.01226,0.10509]},{"body_a":"peg_socket","body_b":"link7","contact_count":5.0,"contact_point_centroid":[0.52682,-0.00399,0.07998],"force_p95":206.91691,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":217.25964,"mean_force":130.63049,"phase_index":1.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.44854,-5e-05,0.12336]},{"body_a":"attachment","body_b":"peg_socket","contact_count":1.0,"contact_point_centroid":[0.52685,-0.01215,0.07998],"force_p95":58.00972,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":58.00972,"mean_force":58.00972,"phase_index":2.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.4574,-0.01224,0.10528]}],"total_contact_groups":6},"final_pose_error":0.21936,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.46685,-0.02106,0.025],"final_tcp_position":[0.45737,-0.01227,0.10507],"realised_fixture_position":[0.46685,-0.02106,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.46685,-0.02106,0.08]},"peak_contact_force":1257.69697,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":281.0,"n_steps_budget":600.0,"object_pos_end":[0.48828,-0.00014,0.11856],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.04031,"object_to_goal_dist_start":0.26034,"object_z_max":0.34427,"peak_contact_force":262.94268,"phase_name":"rotate_1","phase_peak_obstacle_force":0.0,"phase_type":"rotate","raw_contact_event_count":202.0,"raw_peak_contact_force":1257.69697,"subtask_id":"reach_above","tcp_end":[0.44856,-0.00016,0.12327],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.48692,0.007,0.28094],"object_pos_start":[0.48828,-0.00014,0.11856],"object_to_goal_dist_end":0.20149,"object_to_goal_dist_start":0.04031,"object_z_max":0.2808,"peak_contact_force":0.0,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":5.0,"raw_peak_contact_force":217.25964,"tcp_end":[0.44726,0.00698,0.28618],"tcp_start":[0.44856,-0.00016,0.12327],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":853.0,"n_steps_budget":1000.0,"object_pos_end":[0.49701,-0.01223,0.0993],"object_pos_start":[0.48692,0.007,0.28094],"object_to_goal_dist_end":0.02305,"object_to_goal_dist_start":0.20149,"object_z_max":0.28101,"peak_contact_force":58.00972,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1.0,"raw_peak_contact_force":58.00972,"subtask_id":"descend_to_contact","tcp_end":[0.45743,-0.01226,0.10509],"tcp_start":[0.44726,0.00698,0.28618],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.49695,-0.01225,0.09928],"object_pos_start":[0.49701,-0.01223,0.0993],"object_to_goal_dist_end":0.02305,"object_to_goal_dist_start":0.02305,"object_z_max":0.0993,"peak_contact_force":314.23769,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":1.0,"raw_peak_contact_force":314.23769,"subtask_id":"insert_fully","tcp_end":[0.45737,-0.01227,0.10507],"tcp_start":[0.45743,-0.01226,0.10509],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `23bedb35dfb8044c9064b13b9f8101cd4e2be35581b8354b6b999b22e5fca070`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.76842,"average_solve_count":95.0,"average_success_count":95.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"descend_1.descend_distance":0.05128,"descend_1.force_threshold":30.67146,"insert_1.force_limit":18.36796,"insert_1.insert_distance":0.1515,"retract_1.retract_height":0.19088},"optimized_scores":{"best_composite_score":0.6327,"best_fitness_score":0.4427,"best_task_score":0.81629},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link6","contact_count":185.0,"contact_point_centroid":[0.59108,-0.00279,0.07961],"force_p95":5229.32826,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":7840.50613,"mean_force":703.76891,"phase_index":0.0,"phase_name":"rotate_1","phase_type":"rotate","tcp_position_centroid":[0.43279,-2e-05,0.13486]},{"body_a":"peg_socket","body_b":"link7","contact_count":24.0,"contact_point_centroid":[0.56634,-0.00147,0.07641],"force_p95":7297.79935,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":7428.0786,"mean_force":3765.07925,"phase_index":0.0,"phase_name":"rotate_1","phase_type":"rotate","tcp_position_centroid":[0.42955,-0.00049,0.10195]},{"body_a":"peg_socket","body_b":"link7","contact_count":26.0,"contact_point_centroid":[0.52601,-0.02952,0.07748],"force_p95":842.81776,"geom_a":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1004.13602,"mean_force":156.04779,"phase_index":0.0,"phase_name":"rotate_1","phase_type":"rotate","tcp_position_centroid":[0.43019,-0.00046,0.10118]},{"body_a":"peg_socket","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.59543,0.00452,0.07984],"force_p95":265.78321,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":265.78321,"mean_force":265.78321,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.48886,0.00388,0.13421]},{"body_a":"peg_socket","body_b":"link6","contact_count":5.0,"contact_point_centroid":[0.59544,-0.00324,0.07994],"force_p95":144.53064,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":163.70632,"mean_force":70.35704,"phase_index":1.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.42961,0.0002,0.13579]},{"body_a":"peg_socket","body_b":"link7","contact_count":5.0,"contact_point_centroid":[0.52383,0.03102,0.07988],"force_p95":50.28821,"geom_a":"socket_collar_y1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":62.86026,"mean_force":12.57205,"phase_index":0.0,"phase_name":"rotate_1","phase_type":"rotate","tcp_position_centroid":[0.42965,-0.00018,0.09446]},{"body_a":"peg_socket","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.59544,0.00454,0.07992],"force_p95":55.62082,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":55.62082,"mean_force":55.62082,"phase_index":2.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.48879,0.00388,0.13436]}],"total_contact_groups":7},"final_pose_error":0.21078,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.53544,0.00091,0.025],"final_tcp_position":[0.48887,0.00387,0.13405],"realised_fixture_position":[0.53544,0.00091,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.53544,0.00091,0.08]},"peak_contact_force":7840.50613,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":281.0,"n_steps_budget":600.0,"object_pos_end":[0.46961,0.00023,0.13275],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.06088,"object_to_goal_dist_start":0.26034,"object_z_max":0.34427,"peak_contact_force":205.45017,"phase_name":"rotate_1","phase_peak_obstacle_force":0.0,"phase_type":"rotate","raw_contact_event_count":240.0,"raw_peak_contact_force":7840.50613,"subtask_id":"reach_above","tcp_end":[0.42971,0.00019,0.1356],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.46831,0.0085,0.29441],"object_pos_start":[0.46961,0.00023,0.13275],"object_to_goal_dist_end":0.21691,"object_to_goal_dist_start":0.06088,"object_z_max":0.29423,"peak_contact_force":0.0,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":5.0,"raw_peak_contact_force":163.70632,"tcp_end":[0.42845,0.00845,0.29779],"tcp_start":[0.42971,0.00019,0.1356],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":984.0,"n_steps_budget":1000.0,"object_pos_end":[0.52867,0.00393,0.13031],"object_pos_start":[0.46831,0.0085,0.29441],"object_to_goal_dist_end":0.05803,"object_to_goal_dist_start":0.21691,"object_z_max":0.29449,"peak_contact_force":55.62082,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1.0,"raw_peak_contact_force":55.62082,"subtask_id":"descend_to_contact","tcp_end":[0.48886,0.00388,0.13421],"tcp_start":[0.42845,0.00845,0.29779],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.52868,0.00392,0.13017],"object_pos_start":[0.52867,0.00393,0.13031],"object_to_goal_dist_end":0.05792,"object_to_goal_dist_start":0.05803,"object_z_max":0.13031,"peak_contact_force":265.78321,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":1.0,"raw_peak_contact_force":265.78321,"subtask_id":"insert_fully","tcp_end":[0.48887,0.00387,0.13405],"tcp_start":[0.48886,0.00388,0.13421],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `0b9f57c3f8a8fdb0f6fef54a4b5c0cfa6a2779a7721b018896a4efe993ac60cd`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.7766,"average_solve_count":94.0,"average_success_count":94.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"descend_1.descend_distance":0.05025,"descend_1.force_threshold":13.90528,"insert_1.force_limit":33.48195,"insert_1.insert_distance":0.21508,"retract_1.retract_height":0.17455},"optimized_scores":{"best_composite_score":0.62277,"best_fitness_score":0.43277,"best_task_score":0.81629},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link7","contact_count":39.0,"contact_point_centroid":[0.53234,-0.00581,0.07732],"force_p95":882.61543,"geom_a":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1062.8589,"mean_force":189.81789,"phase_index":0.0,"phase_name":"rotate_1","phase_type":"rotate","tcp_position_centroid":[0.43518,0.00035,0.10736]},{"body_a":"peg_socket","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.58439,0.01452,0.07991],"force_p95":290.773,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":290.773,"mean_force":290.773,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.48768,0.01539,0.13751]},{"body_a":"peg_socket","body_b":"link6","contact_count":183.0,"contact_point_centroid":[0.5825,-0.00136,0.0797],"force_p95":235.14708,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":274.70694,"mean_force":225.73907,"phase_index":0.0,"phase_name":"rotate_1","phase_type":"rotate","tcp_position_centroid":[0.44299,0.00046,0.13726]},{"body_a":"peg_socket","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.5844,-0.00153,0.08],"force_p95":225.6154,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":225.6154,"mean_force":225.6154,"phase_index":1.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.44252,0.00045,0.14025]},{"body_a":"peg_socket","body_b":"link7","contact_count":46.0,"contact_point_centroid":[0.55966,0.00276,0.07859],"force_p95":117.66814,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":132.98568,"mean_force":14.63773,"phase_index":0.0,"phase_name":"rotate_1","phase_type":"rotate","tcp_position_centroid":[0.43571,0.00039,0.11211]}],"total_contact_groups":5},"final_pose_error":0.27502,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.5244,0.02464,0.025],"final_tcp_position":[0.48767,0.0154,0.13732],"realised_fixture_position":[0.5244,0.02464,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.5244,0.02464,0.08]},"peak_contact_force":1062.8589,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":281.0,"n_steps_budget":600.0,"object_pos_end":[0.48227,0.0005,0.13579],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.05854,"object_to_goal_dist_start":0.26034,"object_z_max":0.34427,"peak_contact_force":228.53066,"phase_name":"rotate_1","phase_peak_obstacle_force":0.0,"phase_type":"rotate","raw_contact_event_count":268.0,"raw_peak_contact_force":1062.8589,"subtask_id":"reach_above","tcp_end":[0.44252,0.00045,0.14025],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":995.0,"n_steps_budget":1000.0,"object_pos_end":[0.48111,0.00275,0.2985],"object_pos_start":[0.48227,0.0005,0.13579],"object_to_goal_dist_end":0.21933,"object_to_goal_dist_start":0.05854,"object_z_max":0.29837,"peak_contact_force":0.0,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1.0,"raw_peak_contact_force":225.6154,"tcp_end":[0.44142,0.00271,0.30347],"tcp_start":[0.44252,0.00045,0.14025],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":893.0,"n_steps_budget":1000.0,"object_pos_end":[0.5273,0.01543,0.13202],"object_pos_start":[0.48111,0.00275,0.2985],"object_to_goal_dist_end":0.06074,"object_to_goal_dist_start":0.21933,"object_z_max":0.29852,"peak_contact_force":121.87038,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"descend_to_contact","tcp_end":[0.48768,0.01539,0.13751],"tcp_start":[0.44142,0.00271,0.30347],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.52729,0.01544,0.13185],"object_pos_start":[0.5273,0.01543,0.13202],"object_to_goal_dist_end":0.06059,"object_to_goal_dist_start":0.06074,"object_z_max":0.13202,"peak_contact_force":290.773,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":1.0,"raw_peak_contact_force":290.773,"subtask_id":"insert_fully","tcp_end":[0.48767,0.0154,0.13732],"tcp_start":[0.48768,0.01539,0.13751],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":false}]}
```