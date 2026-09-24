## Search State

- **Seed**: 3
- **Iteration**: 9 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 8 | rotate → retract → descend → pull | impedance_motion | arc_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | admittance_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 3 | 0.7627 | 0.97 | ✅ accepted |
| 7 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | admittance_control | admittance_control | pose_tolerance | force_exceeded | force_exceeded | 6 | 1.2189 | 0.88 | ❌ rejected |
| 6 | approach → retract → descend → insert | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | admittance_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | 5 | 0.3242 | 0.82 | ❌ rejected |
| 5 | approach → retract → descend → push | arc_cartesian | arc_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | admittance_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | 4 | 0.5934 | 0.85 | ❌ rejected |
| 4 | rotate → retract → descend → pull | impedance_motion | arc_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | admittance_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 3 | 0.7614 | 0.97 | ❌ rejected |

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
| retract_1 | 1.00 | 0.00 | 0.0517 |
| descend_1 | 1.00 | 0.00 | 0.0829 |
| pull_1 | 1.00 | 1.00 | 0.1197 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| rotate_1 | rotate | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.499, -0.000, 0.299) | (0.504, -0.000, 0.340)→(0.503, -0.000, 0.339) | 0.260→0.259 | 0.00 / 0.000 | 0.000 | 0.000 |
| retract_1 | retract | 1.00 / step_budget | (0.499, -0.000, 0.299)→(0.498, 0.002, 0.351) | (0.503, -0.000, 0.339)→(0.502, 0.002, 0.390) | 0.259→0.310 | 0.00 / 0.000 | 0.000 | 0.000 |
| descend_1 | descend | 1.00 / step_budget | (0.498, 0.002, 0.351)→(0.495, 0.001, 0.268) | (0.502, 0.002, 0.390)→(0.500, 0.002, 0.307) | 0.310→0.227 | 0.00 / 0.000 | 0.000 | 0.000 |
| pull_1 | pull | 1.00 / time_limit | (0.495, 0.001, 0.268)→(0.558, 0.033, 0.210) | (0.500, 0.002, 0.307)→(0.576, 0.032, 0.181) | 0.227→0.133 | 1.00 / 1.000 | 249.630 | 3567.888 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.977
- alignment_error: None
- force_efficiency: 0.000

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.977
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.977
- **Median Q (composite search score)**: 0.763
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 10.0
- **Final σ (mean)**: 0.484


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.72917,"average_solve_count":96.0,"average_success_count":96.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"descend_1.depth":0.0931,"pull_1.pull_distance":0.0822,"retract_1.retract_height":0.06112},"optimized_scores":{"best_composite_score":0.76731,"best_fitness_score":0.97731,"best_task_score":0.97731},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link7","contact_count":729.0,"contact_point_centroid":[0.52661,0.00946,0.06414],"force_p95":333.32018,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":8052.69577,"mean_force":371.65984,"phase_index":3.0,"phase_name":"pull_1","phase_type":"pull","tcp_position_centroid":[0.45989,0.00783,0.11792]},{"body_a":"attachment","body_b":"peg_socket","contact_count":573.0,"contact_point_centroid":[0.52542,0.00882,0.07974],"force_p95":236.08871,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":5454.3229,"mean_force":190.18962,"phase_index":3.0,"phase_name":"pull_1","phase_type":"pull","tcp_position_centroid":[0.4632,0.00775,0.11716]},{"body_a":"peg_socket","body_b":"link7","contact_count":9.0,"contact_point_centroid":[0.52681,0.00433,0.04967],"force_p95":2697.93387,"geom_a":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":2723.36148,"mean_force":2253.18682,"phase_index":3.0,"phase_name":"pull_1","phase_type":"pull","tcp_position_centroid":[0.44118,0.00672,0.10449]},{"body_a":"world","body_b":"link6","contact_count":608.0,"contact_point_centroid":[0.67889,0.01142,-4e-05],"force_p95":220.60719,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":922.96041,"mean_force":80.02775,"phase_index":3.0,"phase_name":"pull_1","phase_type":"pull","tcp_position_centroid":[0.46267,0.00937,0.12197]},{"body_a":"attachment","body_b":"peg_socket","contact_count":3.0,"contact_point_centroid":[0.4968,0.01998,0.07997],"force_p95":760.54621,"geom_a":"peg_tip","geom_b":"socket_collar_y1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":764.48691,"mean_force":726.78195,"phase_index":3.0,"phase_name":"pull_1","phase_type":"pull","tcp_position_centroid":[0.49703,0.00499,0.07973]}],"total_contact_groups":5},"final_pose_error":0.14821,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.46685,-0.02106,0.025],"final_tcp_position":[0.47142,0.01613,0.14119],"realised_fixture_position":[0.46685,-0.02106,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.46685,-0.02106,0.08]},"peak_contact_force":8052.69577,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":20.0,"n_steps_budget":600.0,"object_pos_end":[0.50343,-0.0,0.33877],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.25879,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"rotate_1","phase_peak_obstacle_force":0.0,"phase_type":"rotate","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.49918,-1e-05,0.299],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":475.0,"n_steps_budget":600.0,"object_pos_end":[0.50221,0.00154,0.39013],"object_pos_start":[0.50343,-0.0,0.33877],"object_to_goal_dist_end":0.31015,"object_to_goal_dist_start":0.25879,"object_z_max":0.39005,"peak_contact_force":0.0,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.49751,0.00152,0.35041],"tcp_start":[0.49918,-1e-05,0.299],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":258.0,"n_steps_budget":600.0,"object_pos_end":[0.50046,0.00151,0.30653],"object_pos_start":[0.50221,0.00154,0.39013],"object_to_goal_dist_end":0.22654,"object_to_goal_dist_start":0.31015,"object_z_max":0.39017,"peak_contact_force":0.0,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.49529,0.00149,0.26687],"tcp_start":[0.49751,0.00152,0.35041],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50736,0.01559,0.12364],"object_pos_start":[0.50046,0.00151,0.30653],"object_to_goal_dist_end":0.04692,"object_to_goal_dist_start":0.22654,"object_z_max":0.30653,"peak_contact_force":204.65407,"phase_name":"pull_1","phase_peak_obstacle_force":0.0,"phase_type":"pull","raw_contact_event_count":1922.0,"raw_peak_contact_force":8052.69577,"tcp_end":[0.47142,0.01613,0.14119],"tcp_start":[0.49529,0.00149,0.26687],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `23bedb35dfb8044c9064b13b9f8101cd4e2be35581b8354b6b999b22e5fca070`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":3.0,"average_failure_rate":0.0303,"average_mean_iterations":10.57576,"average_solve_count":99.0,"average_success_count":96.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"descend_1.depth":0.09149,"pull_1.pull_distance":0.10204,"retract_1.retract_height":0.0608},"optimized_scores":{"best_composite_score":0.76307,"best_fitness_score":0.97307,"best_task_score":0.97307},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link7","contact_count":802.0,"contact_point_centroid":[0.59527,0.01814,0.07984],"force_p95":357.04494,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1532.56318,"mean_force":265.33231,"phase_index":3.0,"phase_name":"pull_1","phase_type":"pull","tcp_position_centroid":[0.50791,0.00996,0.10795]},{"body_a":"attachment","body_b":"peg_socket","contact_count":37.0,"contact_point_centroid":[0.50224,0.02074,0.07822],"force_p95":1100.82508,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1156.53593,"mean_force":419.57184,"phase_index":3.0,"phase_name":"pull_1","phase_type":"pull","tcp_position_centroid":[0.49829,0.00606,0.07841]},{"body_a":"world","body_b":"link6","contact_count":48.0,"contact_point_centroid":[0.64666,0.13009,-0.00091],"force_p95":476.23205,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":550.3301,"mean_force":299.30281,"phase_index":3.0,"phase_name":"pull_1","phase_type":"pull","tcp_position_centroid":[0.60832,0.00122,0.2204]}],"total_contact_groups":3},"final_pose_error":0.28224,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.53544,0.00091,0.025],"final_tcp_position":[0.60567,0.04045,0.24844],"realised_fixture_position":[0.53544,0.00091,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.53544,0.00091,0.08]},"peak_contact_force":1532.56318,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":20.0,"n_steps_budget":600.0,"object_pos_end":[0.50343,-0.0,0.33877],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.25879,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"rotate_1","phase_peak_obstacle_force":0.0,"phase_type":"rotate","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.49918,-1e-05,0.299],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":473.0,"n_steps_budget":600.0,"object_pos_end":[0.50221,0.00153,0.38983],"object_pos_start":[0.50343,-0.0,0.33877],"object_to_goal_dist_end":0.30985,"object_to_goal_dist_start":0.25879,"object_z_max":0.38975,"peak_contact_force":0.0,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.4975,0.00151,0.35011],"tcp_start":[0.49918,-1e-05,0.299],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":253.0,"n_steps_budget":600.0,"object_pos_end":[0.50047,0.0015,0.30776],"object_pos_start":[0.50221,0.00153,0.38983],"object_to_goal_dist_end":0.22777,"object_to_goal_dist_start":0.30985,"object_z_max":0.38987,"peak_contact_force":0.0,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.4953,0.00148,0.2681],"tcp_start":[0.4975,0.00151,0.35011],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.61337,0.05648,0.21261],"object_pos_start":[0.50047,0.0015,0.30776],"object_to_goal_dist_end":0.18338,"object_to_goal_dist_start":0.22777,"object_z_max":0.30776,"peak_contact_force":273.12134,"phase_name":"pull_1","phase_peak_obstacle_force":0.0,"phase_type":"pull","raw_contact_event_count":887.0,"raw_peak_contact_force":1532.56318,"tcp_end":[0.60567,0.04045,0.24844],"tcp_start":[0.4953,0.00148,0.2681],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `0b9f57c3f8a8fdb0f6fef54a4b5c0cfa6a2779a7721b018896a4efe993ac60cd`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.63542,"average_solve_count":96.0,"average_success_count":96.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"descend_1.depth":0.09262,"pull_1.pull_distance":0.11729,"retract_1.retract_height":0.06202},"optimized_scores":{"best_composite_score":0.75762,"best_fitness_score":0.96762,"best_task_score":0.96762},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":25.0,"contact_point_centroid":[0.49178,0.01195,0.07858],"force_p95":935.44117,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1118.40638,"mean_force":374.74989,"phase_index":3.0,"phase_name":"pull_1","phase_type":"pull","tcp_position_centroid":[0.49065,0.01234,0.07455]},{"body_a":"attachment","body_b":"peg_socket","contact_count":4.0,"contact_point_centroid":[0.50015,-0.00617,0.07879],"force_p95":835.53927,"geom_a":"peg_tip","geom_b":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":880.81908,"mean_force":597.26777,"phase_index":3.0,"phase_name":"pull_1","phase_type":"pull","tcp_position_centroid":[0.49873,0.00762,0.08033]},{"body_a":"peg_socket","body_b":"link7","contact_count":819.0,"contact_point_centroid":[0.58422,0.01959,0.07982],"force_p95":376.00764,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":878.11367,"mean_force":266.93158,"phase_index":3.0,"phase_name":"pull_1","phase_type":"pull","tcp_position_centroid":[0.4981,0.01645,0.11021]},{"body_a":"peg_socket","body_b":"link6","contact_count":25.0,"contact_point_centroid":[0.58359,-0.03475,0.07958],"force_p95":551.12618,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":614.72956,"mean_force":359.47846,"phase_index":3.0,"phase_name":"pull_1","phase_type":"pull","tcp_position_centroid":[0.59359,0.05739,0.22952]},{"body_a":"world","body_b":"link6","contact_count":22.0,"contact_point_centroid":[0.6712,-0.05842,-0.00187],"force_p95":565.17565,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":579.72661,"mean_force":306.88662,"phase_index":3.0,"phase_name":"pull_1","phase_type":"pull","tcp_position_centroid":[0.57214,0.0796,0.18922]}],"total_contact_groups":5},"final_pose_error":0.28646,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.5244,0.02464,0.025],"final_tcp_position":[0.59572,0.0412,0.23965],"realised_fixture_position":[0.5244,0.02464,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.5244,0.02464,0.08]},"peak_contact_force":1118.40638,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":20.0,"n_steps_budget":600.0,"object_pos_end":[0.50343,-0.0,0.33877],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.25879,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"rotate_1","phase_peak_obstacle_force":0.0,"phase_type":"rotate","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.49918,-1e-05,0.299],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":481.0,"n_steps_budget":600.0,"object_pos_end":[0.50221,0.00153,0.39105],"object_pos_start":[0.50343,-0.0,0.33877],"object_to_goal_dist_end":0.31107,"object_to_goal_dist_start":0.25879,"object_z_max":0.39097,"peak_contact_force":0.0,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.49751,0.00152,0.35133],"tcp_start":[0.49918,-1e-05,0.299],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":256.0,"n_steps_budget":600.0,"object_pos_end":[0.50047,0.00151,0.3079],"object_pos_start":[0.50221,0.00153,0.39105],"object_to_goal_dist_end":0.22791,"object_to_goal_dist_start":0.31107,"object_z_max":0.39109,"peak_contact_force":0.0,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.4953,0.00148,0.26824],"tcp_start":[0.49751,0.00152,0.35133],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.60855,0.02434,0.20572],"object_pos_start":[0.50047,0.00151,0.3079],"object_to_goal_dist_end":0.16788,"object_to_goal_dist_start":0.22791,"object_z_max":0.3079,"peak_contact_force":271.11325,"phase_name":"pull_1","phase_peak_obstacle_force":0.0,"phase_type":"pull","raw_contact_event_count":895.0,"raw_peak_contact_force":1118.40638,"tcp_end":[0.59572,0.0412,0.23965],"tcp_start":[0.4953,0.00148,0.26824],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
```