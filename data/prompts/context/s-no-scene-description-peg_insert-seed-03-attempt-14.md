## Search State

- **Seed**: 3
- **Iteration**: 15 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 14 | retract → descend → pull | arc_cartesian | linear_cartesian | linear_cartesian | position_control | admittance_control | impedance_control | pose_tolerance | pose_tolerance | time_limit | 3 | 0.8123 | 0.99 | ✅ accepted |
| 13 | rotate → retract → descend → pull | impedance_motion | arc_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | admittance_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 3 | 0.7625 | 0.97 | ❌ rejected |
| 12 | rotate → retract → descend → insert | impedance_motion | arc_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | admittance_control | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | force_exceeded | 5 | 0.6387 | 0.82 | ❌ rejected |
| 11 | approach → align → descend → insert | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | admittance_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | 7 | 0.3764 | 0.84 | ❌ rejected |
| 10 | approach → descend → pull | linear_cartesian | linear_cartesian | arc_cartesian | position_control | admittance_control | impedance_control | pose_tolerance | pose_tolerance | time_limit | 3 | 0.6763 | 0.86 | ❌ rejected |

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

## Current Skill (Q=0.812) — your mutation base

```yaml
skill: peg_insert
dsl_version: 2
subtasks:
- id: pre_contact
  anchor: fixture
  offset:
  - 0.0
  - 0.0
  - 0.1
  weight: 0.3
- id: insertion
  weight: 0.7
phases:
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
  subtask_id: pre_contact
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
  subtask_id: pre_contact
- id: pull_1
  type: pull
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
      tolerance: 0.05
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
  subtask_id: insertion

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
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
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=world_z, tolerance=0.05
  - parameter_bindings:
    - pull_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)

## Design Metrics

- **Composite score**: 0.812
- **task_score** (E): 0.992
- **fitness_score**: 0.992  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.180

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| retract_1 | 1.00 | 0.00 | 0.0533 |
| descend_1 | 1.00 | 0.00 | 0.0861 |
| pull_1 | 1.00 | 1.00 | 0.1333 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| retract_1 | retract | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.498, 0.002, 0.354) | (0.504, -0.000, 0.340)→(0.503, 0.002, 0.394) | 0.260→0.314 | 0.00 / 0.000 | 0.000 | 0.000 |
| descend_1 | descend | 1.00 / step_budget | (0.498, 0.002, 0.354)→(0.496, 0.002, 0.268) | (0.503, 0.002, 0.394)→(0.501, 0.002, 0.307) | 0.314→0.227 | 0.00 / 0.000 | 0.000 | 0.000 |
| pull_1 | pull | 1.00 / time_limit | (0.496, 0.002, 0.268)→(0.572, 0.016, 0.199) | (0.501, 0.002, 0.307)→(0.588, 0.011, 0.172) | 0.227→0.140 | 1.00 / 1.667 | 428.839 | 4948.624 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.997
- alignment_error: None
- force_efficiency: 0.000

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.997
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.997
- **Median Q (composite search score)**: 0.816
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 10.0
- **Final σ (mean)**: 0.427


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":5.72727,"average_solve_count":77.0,"average_success_count":77.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"descend_1.depth":0.09782,"pull_1.pull_distance":0.17395,"retract_1.retract_height":0.06457},"optimized_scores":{"best_composite_score":0.81667,"best_fitness_score":0.99667,"best_task_score":0.99667},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link7","contact_count":693.0,"contact_point_centroid":[0.5266,-0.00417,0.06435],"force_p95":331.53188,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":10016.26316,"mean_force":429.85119,"phase_index":2.0,"phase_name":"pull_1","phase_type":"pull","tcp_position_centroid":[0.46004,-0.00069,0.11856]},{"body_a":"attachment","body_b":"peg_socket","contact_count":256.0,"contact_point_centroid":[0.52384,-0.00037,0.07943],"force_p95":1208.25313,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":6792.17038,"mean_force":390.61971,"phase_index":2.0,"phase_name":"pull_1","phase_type":"pull","tcp_position_centroid":[0.46556,-0.00123,0.11434]},{"body_a":"peg_socket","body_b":"link7","contact_count":10.0,"contact_point_centroid":[0.52676,-0.00311,0.04933],"force_p95":3497.6668,"geom_a":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":3535.59047,"mean_force":2853.89605,"phase_index":2.0,"phase_name":"pull_1","phase_type":"pull","tcp_position_centroid":[0.44107,-0.00044,0.1044]},{"body_a":"world","body_b":"link6","contact_count":601.0,"contact_point_centroid":[0.67857,0.00128,-5e-05],"force_p95":255.48782,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":946.48436,"mean_force":96.12513,"phase_index":2.0,"phase_name":"pull_1","phase_type":"pull","tcp_position_centroid":[0.46347,-0.00251,0.12371]}],"total_contact_groups":4},"final_pose_error":0.2423,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.46685,-0.02106,0.025],"final_tcp_position":[0.47526,-0.01041,0.14798],"realised_fixture_position":[0.46685,-0.02106,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.46685,-0.02106,0.08]},"peak_contact_force":10016.26316,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":490.0,"n_steps_budget":600.0,"object_pos_end":[0.50276,0.00156,0.39507],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.31508,"object_to_goal_dist_start":0.26034,"object_z_max":0.39498,"peak_contact_force":0.0,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"pre_contact","tcp_end":[0.49818,0.00155,0.35533],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":272.0,"n_steps_budget":630.0,"object_pos_end":[0.501,0.00154,0.30671],"object_pos_start":[0.50276,0.00156,0.39507],"object_to_goal_dist_end":0.22672,"object_to_goal_dist_start":0.31508,"object_z_max":0.39511,"peak_contact_force":0.0,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"pre_contact","tcp_end":[0.49596,0.00152,0.26703],"tcp_start":[0.49818,0.00155,0.35533],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51064,-0.00906,0.12936],"object_pos_start":[0.501,0.00154,0.30671],"object_to_goal_dist_end":0.0513,"object_to_goal_dist_start":0.22672,"object_z_max":0.30671,"peak_contact_force":179.35172,"phase_name":"pull_1","phase_peak_obstacle_force":0.0,"phase_type":"pull","raw_contact_event_count":1560.0,"raw_peak_contact_force":10016.26316,"subtask_id":"insertion","tcp_end":[0.47526,-0.01041,0.14798],"tcp_start":[0.49596,0.00152,0.26703],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `23bedb35dfb8044c9064b13b9f8101cd4e2be35581b8354b6b999b22e5fca070`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":3.0,"average_failure_rate":0.03797,"average_mean_iterations":13.0,"average_solve_count":79.0,"average_success_count":76.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"descend_1.depth":0.09398,"pull_1.pull_distance":0.09914,"retract_1.retract_height":0.06143},"optimized_scores":{"best_composite_score":0.81602,"best_fitness_score":0.99602,"best_task_score":0.99602},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link7","contact_count":816.0,"contact_point_centroid":[0.59527,-0.00837,0.07984],"force_p95":355.06491,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1571.13674,"mean_force":255.10722,"phase_index":2.0,"phase_name":"pull_1","phase_type":"pull","tcp_position_centroid":[0.51111,0.0025,0.10809]},{"body_a":"attachment","body_b":"peg_socket","contact_count":36.0,"contact_point_centroid":[0.50241,0.0156,0.0783],"force_p95":1122.27002,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1150.93804,"mean_force":391.54748,"phase_index":2.0,"phase_name":"pull_1","phase_type":"pull","tcp_position_centroid":[0.49913,0.00083,0.07748]},{"body_a":"world","body_b":"link6","contact_count":47.0,"contact_point_centroid":[0.66806,-0.16696,-0.00168],"force_p95":522.98297,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":692.2732,"mean_force":272.88127,"phase_index":2.0,"phase_name":"pull_1","phase_type":"pull","tcp_position_centroid":[0.67613,0.02586,0.16495]}],"total_contact_groups":3},"final_pose_error":0.25678,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.53544,0.00091,0.025],"final_tcp_position":[0.67632,0.01105,0.1953],"realised_fixture_position":[0.53544,0.00091,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.53544,0.00091,0.08]},"peak_contact_force":1571.13674,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":476.0,"n_steps_budget":600.0,"object_pos_end":[0.50275,0.00154,0.39195],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.31197,"object_to_goal_dist_start":0.26034,"object_z_max":0.39187,"peak_contact_force":0.0,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"pre_contact","tcp_end":[0.49818,0.00153,0.35222],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":259.0,"n_steps_budget":600.0,"object_pos_end":[0.50101,0.00152,0.30759],"object_pos_start":[0.50275,0.00154,0.39195],"object_to_goal_dist_end":0.2276,"object_to_goal_dist_start":0.31197,"object_z_max":0.39199,"peak_contact_force":0.0,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"pre_contact","tcp_end":[0.49597,0.0015,0.26791],"tcp_start":[0.49818,0.00153,0.35222],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.67396,-0.01868,0.16865],"object_pos_start":[0.50101,0.00152,0.30759],"object_to_goal_dist_end":0.19614,"object_to_goal_dist_start":0.2276,"object_z_max":0.30759,"peak_contact_force":230.35684,"phase_name":"pull_1","phase_peak_obstacle_force":0.0,"phase_type":"pull","raw_contact_event_count":899.0,"raw_peak_contact_force":1571.13674,"subtask_id":"insertion","tcp_end":[0.67632,0.01105,0.1953],"tcp_start":[0.49597,0.0015,0.26791],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `0b9f57c3f8a8fdb0f6fef54a4b5c0cfa6a2779a7721b018896a4efe993ac60cd`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":2.0,"average_failure_rate":0.02469,"average_mean_iterations":10.48148,"average_solve_count":81.0,"average_success_count":79.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"descend_1.depth":0.09517,"pull_1.pull_distance":0.10308,"retract_1.retract_height":0.06304},"optimized_scores":{"best_composite_score":0.80419,"best_fitness_score":0.98419,"best_task_score":0.98419},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"link5","contact_count":62.0,"contact_point_centroid":[0.55105,0.14874,-0.00074],"force_p95":3039.45408,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":3258.4731,"mean_force":1151.96952,"phase_index":2.0,"phase_name":"pull_1","phase_type":"pull","tcp_position_centroid":[0.56312,0.024,0.23126]},{"body_a":"attachment","body_b":"peg_socket","contact_count":20.0,"contact_point_centroid":[0.49248,-0.00356,0.07899],"force_p95":2522.06104,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":2634.74467,"mean_force":699.84236,"phase_index":2.0,"phase_name":"pull_1","phase_type":"pull","tcp_position_centroid":[0.49265,0.01078,0.0744]},{"body_a":"attachment","body_b":"peg_socket","contact_count":10.0,"contact_point_centroid":[0.50471,-0.00693,0.07936],"force_p95":2169.22354,"geom_a":"peg_tip","geom_b":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":2242.25088,"mean_force":1223.32059,"phase_index":2.0,"phase_name":"pull_1","phase_type":"pull","tcp_position_centroid":[0.49891,0.00531,0.07912]},{"body_a":"peg_socket","body_b":"link5","contact_count":45.0,"contact_point_centroid":[0.53377,0.08399,0.04908],"force_p95":1801.9602,"geom_a":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1842.22417,"mean_force":795.39529,"phase_index":2.0,"phase_name":"pull_1","phase_type":"pull","tcp_position_centroid":[0.56616,0.03963,0.24959]},{"body_a":"peg_socket","body_b":"link5","contact_count":45.0,"contact_point_centroid":[0.52963,0.08397,0.05452],"force_p95":1383.54568,"geom_a":"socket_collar_y1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1428.77252,"mean_force":631.9293,"phase_index":2.0,"phase_name":"pull_1","phase_type":"pull","tcp_position_centroid":[0.56616,0.03963,0.24959]},{"body_a":"peg_socket","body_b":"link7","contact_count":784.0,"contact_point_centroid":[0.58423,0.0077,0.07985],"force_p95":344.3633,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":722.85581,"mean_force":257.7963,"phase_index":2.0,"phase_name":"pull_1","phase_type":"pull","tcp_position_centroid":[0.49848,0.00769,0.11045]},{"body_a":"world","body_b":"link6","contact_count":13.0,"contact_point_centroid":[0.6709,0.12083,-0.00154],"force_p95":118.50976,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":266.80476,"mean_force":22.03471,"phase_index":2.0,"phase_name":"pull_1","phase_type":"pull","tcp_position_centroid":[0.55468,-0.00809,0.19012]}],"total_contact_groups":7},"final_pose_error":0.28043,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.5244,0.02464,0.025],"final_tcp_position":[0.56453,0.04768,0.25351],"realised_fixture_position":[0.5244,0.02464,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.5244,0.02464,0.08]},"peak_contact_force":3258.4731,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":487.0,"n_steps_budget":600.0,"object_pos_end":[0.50274,0.00155,0.39356],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.31358,"object_to_goal_dist_start":0.26034,"object_z_max":0.39348,"peak_contact_force":0.0,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"pre_contact","tcp_end":[0.49816,0.00153,0.35382],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":264.0,"n_steps_budget":630.0,"object_pos_end":[0.501,0.00152,0.30791],"object_pos_start":[0.50274,0.00155,0.39356],"object_to_goal_dist_end":0.22791,"object_to_goal_dist_start":0.31358,"object_z_max":0.3936,"peak_contact_force":0.0,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"pre_contact","tcp_end":[0.49596,0.0015,0.26823],"tcp_start":[0.49816,0.00153,0.35382],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.58063,0.06099,0.21939],"object_pos_start":[0.501,0.00152,0.30791],"object_to_goal_dist_end":0.1722,"object_to_goal_dist_start":0.22791,"object_z_max":0.30791,"peak_contact_force":876.80738,"phase_name":"pull_1","phase_peak_obstacle_force":0.0,"phase_type":"pull","raw_contact_event_count":979.0,"raw_peak_contact_force":3258.4731,"subtask_id":"insertion","tcp_end":[0.56453,0.04768,0.25351],"tcp_start":[0.49596,0.0015,0.26823],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
```