## Search State

- **Seed**: 4
- **Iteration**: 8 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 7 | approach → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | pose_tolerance | force_exceeded | time_limit | 7 | -0.0396 | 0.34 | ❌ rejected |
| 6 | approach → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | pose_tolerance | force_exceeded | time_limit | 6 | 0.1933 | 0.36 | ✅ accepted |
| 5 | push → align → release | impedance_motion | linear_cartesian | linear_cartesian | position_control | position_control | position_control | time_limit | pose_tolerance | time_limit | 3 | 0.0400 | 0.22 | ❌ rejected |
| 4 | push → align → release | impedance_motion | linear_cartesian | linear_cartesian | position_control | position_control | position_control | time_limit | pose_tolerance | time_limit | 3 | 0.0400 | 0.22 | ❌ rejected |
| 3 | push → align → release | impedance_motion | linear_cartesian | linear_cartesian | position_control | position_control | position_control | time_limit | pose_tolerance | time_limit | 3 | 0.0400 | 0.22 | ✅ accepted |

**Proposal policy**: task_score is 0.34 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.040) — your mutation base

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

- **Composite score**: -0.040
- **task_score** (E): 0.340
- **fitness_score**: 0.340  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.380

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_door | 1.00 | 1.00 | 0.2095 |
| push_door | 0.00 | 0.67 | 0.0001 |
| retract | 1.00 | 0.33 | 0.1007 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_door | approach | 1.00 / step_budget | (0.100, 0.399, 0.350)→(0.100, 0.190, 0.349) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 2.333 | 10.097 | 24.364 |
| push_door | push | 0.00 / guard_failure | (0.100, 0.190, 0.349)→(0.100, 0.190, 0.349) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 0.67 / 0.667 | 0.000 | 0.000 |
| retract | retract | 1.00 / time_limit | (0.100, 0.190, 0.349)→(0.075, 0.145, 0.262) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 0.33 / 1.333 | 0.000 | 14.657 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- hinge_angle_ratio: 0.489
- arc_quality: 0.667

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.489
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.489
- **Median Q (composite search score)**: -0.068
- **K-run variance**: 0.0125
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.311


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.77251,"average_solve_count":211.0,"average_success_count":211.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_door.approach_speed":0.03705,"push_door.force_threshold":15.14989,"push_door.hinge_angle_threshold":0.5425,"push_door.push_distance":0.23203,"push_door.push_speed":0.09056,"retract.retract_distance":0.10626,"retract.retract_speed":0.02409},"optimized_scores":{"best_composite_score":-0.16024,"best_fitness_score":0.21976,"best_task_score":0.21976},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link7","contact_count":56.0,"contact_point_centroid":[0.14712,0.13997,0.39887],"force_p95":20.12477,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":20.85309,"mean_force":14.2981,"phase_index":0.0,"phase_name":"approach_door","phase_type":"approach","tcp_position_centroid":[0.09983,0.19776,0.34841]},{"body_a":"door_panel","body_b":"link7","contact_count":315.0,"contact_point_centroid":[0.1388,0.11473,0.35714],"force_p95":13.53397,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":14.48628,"mean_force":12.06055,"phase_index":2.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.0876,0.16715,0.30546]},{"body_a":"world","body_b":"door_panel","contact_count":936.0,"contact_point_centroid":[0.30385,0.1597,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_door","phase_type":"approach","tcp_position_centroid":[0.09968,0.29849,0.34804]},{"body_a":"door_panel","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.14633,0.13197,0.39963],"force_p95":0.0,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.09986,0.18986,0.34851]},{"body_a":"world","body_b":"door_panel","contact_count":752.0,"contact_point_centroid":[0.30776,0.14415,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.08717,0.16642,0.30398]}],"total_contact_groups":5},"final_pose_error":0.00497,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.07471,0.14534,0.26094],"hinge_angle":0.26981,"initial_hinge_angle":0.15466,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.15466,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":20.85309,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":914.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":13.02898,"phase_name":"approach_door","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":992.0,"raw_peak_contact_force":20.85309,"tcp_end":[0.09986,0.18986,0.34851],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.40924,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"push_door","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1.0,"raw_peak_contact_force":0.0,"tcp_end":[0.09983,0.18978,0.34846],"tcp_start":[0.09986,0.18986,0.34851],"tcp_to_object_dist_end":0.40915,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":801.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1067.0,"raw_peak_contact_force":14.48628,"tcp_end":[0.07471,0.14534,0.26094],"tcp_start":[0.09983,0.18978,0.34846],"tcp_to_object_dist_end":0.30789,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `74b09c110110eedfa033ccf01fd9064bfaa53943493bfa1a44417e7ed7258576`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.72152,"average_solve_count":158.0,"average_success_count":158.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_door.approach_speed":0.09054,"push_door.force_threshold":10.06153,"push_door.hinge_angle_threshold":0.50533,"push_door.push_distance":0.32239,"push_door.push_speed":0.14144,"retract.retract_distance":0.10608,"retract.retract_speed":0.0201},"optimized_scores":{"best_composite_score":-0.06798,"best_fitness_score":0.31202,"best_task_score":0.31202},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link7","contact_count":115.0,"contact_point_centroid":[0.14792,0.14813,0.39817],"force_p95":24.32689,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":27.72375,"mean_force":13.53749,"phase_index":0.0,"phase_name":"approach_door","phase_type":"approach","tcp_position_centroid":[0.09981,0.20584,0.34842]},{"body_a":"door_panel","body_b":"link7","contact_count":339.0,"contact_point_centroid":[0.13871,0.11444,0.3569],"force_p95":13.28375,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":14.16944,"mean_force":11.94187,"phase_index":2.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.08751,0.16683,0.3052]},{"body_a":"world","body_b":"door_panel","contact_count":916.0,"contact_point_centroid":[0.30233,0.16814,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_door","phase_type":"approach","tcp_position_centroid":[0.09966,0.29605,0.34805]},{"body_a":"door_panel","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.14629,0.13185,0.39967],"force_p95":0.0,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.09985,0.18971,0.34855]},{"body_a":"world","body_b":"door_panel","contact_count":848.0,"contact_point_centroid":[0.30781,0.14397,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.08701,0.16596,0.30347]}],"total_contact_groups":5},"final_pose_error":0.00497,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.07475,0.14525,0.26115],"hinge_angle":0.26997,"initial_hinge_angle":0.10647,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.10647,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":27.72375,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":827.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":12.73001,"phase_name":"approach_door","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1031.0,"raw_peak_contact_force":27.72375,"tcp_end":[0.09985,0.18971,0.34855],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.4092,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"push_door","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1.0,"raw_peak_contact_force":0.0,"tcp_end":[0.09982,0.18963,0.3485],"tcp_start":[0.09985,0.18971,0.34855],"tcp_to_object_dist_end":0.40912,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":835.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1187.0,"raw_peak_contact_force":14.16944,"tcp_end":[0.07475,0.14525,0.26115],"tcp_start":[0.09982,0.18963,0.3485],"tcp_to_object_dist_end":0.30803,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `19b9b4f2c5af25040a197573455096dd2f805f94d78c64c4126be8f0525fbcc6`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.23967,"average_solve_count":121.0,"average_success_count":121.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_door.approach_speed":0.06356,"push_door.force_threshold":22.53697,"push_door.hinge_angle_threshold":0.47355,"push_door.push_distance":0.17843,"push_door.push_speed":0.08315,"retract.retract_distance":0.10448,"retract.retract_speed":0.0432},"optimized_scores":{"best_composite_score":0.10928,"best_fitness_score":0.48928,"best_task_score":0.48928},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link7","contact_count":220.0,"contact_point_centroid":[0.14951,0.16462,0.39664],"force_p95":21.47168,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":24.51516,"mean_force":13.74804,"phase_index":0.0,"phase_name":"approach_door","phase_type":"approach","tcp_position_centroid":[0.09975,0.22221,0.34839]},{"body_a":"door_panel","body_b":"link7","contact_count":288.0,"contact_point_centroid":[0.13877,0.11471,0.3573],"force_p95":14.90734,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":15.31658,"mean_force":12.26014,"phase_index":2.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.08759,0.16714,0.30561]},{"body_a":"world","body_b":"door_panel","contact_count":844.0,"contact_point_centroid":[0.30083,0.18189,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_door","phase_type":"approach","tcp_position_centroid":[0.09965,0.29383,0.34805]},{"body_a":"door_panel","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.14629,0.13189,0.39973],"force_p95":0.0,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.09983,0.18983,0.34861]},{"body_a":"world","body_b":"door_panel","contact_count":4.0,"contact_point_centroid":[0.30549,0.15239,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.09983,0.18983,0.34861]},{"body_a":"world","body_b":"door_panel","contact_count":696.0,"contact_point_centroid":[0.30779,0.144,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.08697,0.16602,0.30345]}],"total_contact_groups":6},"final_pose_error":0.00494,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.07525,0.14556,0.26281],"hinge_angle":0.26971,"initial_hinge_angle":0.01332,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.01332,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":24.51516,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":879.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":4.53182,"phase_name":"approach_door","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1064.0,"raw_peak_contact_force":24.51516,"tcp_end":[0.09983,0.18983,0.34861],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.4093,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"push_door","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":5.0,"raw_peak_contact_force":0.0,"tcp_end":[0.09981,0.18974,0.34856],"tcp_start":[0.09983,0.18983,0.34861],"tcp_to_object_dist_end":0.40922,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":727.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":984.0,"raw_peak_contact_force":15.31658,"tcp_end":[0.07525,0.14556,0.26281],"tcp_start":[0.09981,0.18974,0.34856],"tcp_to_object_dist_end":0.30971,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
```