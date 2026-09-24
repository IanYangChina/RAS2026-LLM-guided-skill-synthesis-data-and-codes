## Search State

- **Seed**: 2
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | approach → align → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 8 | -0.0454 | 0.95 | ❌ rejected |
| 11 | approach → align → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | time_limit | 9 | -0.0922 | 0.95 | ❌ rejected |
| 10 | approach → align → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.0057 | 0.94 | ❌ rejected |
| 9 | approach → align → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | pose_tolerance | force_exceeded | force_exceeded | 8 | 0.3063 | 0.92 | ❌ rejected |
| 8 | approach → align → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | time_limit | 8 | -0.0462 | 0.95 | ❌ rejected |

**Proposal policy**: task_score is near-perfect (0.95). Preserve useful working parts and make only evidence-backed refinements. A HOLD is acceptable if you genuinely cannot find a better structure.

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

## Current Skill (Q=-0.045) — your mutation base

```yaml
skill: peg_insert
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: pre_contact
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.1
  weight: 0.3
- id: insertion
  metric: goal_progress
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
    - 0.1
    orientation:
      mode: none
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: replace
    approach_speed:
      type: scalar
      range:
      - 0.1
      - 0.5
      default: 0.3
      binds_to:
      - path: generator.speed
        mode: replace
    approach_tolerance:
      type: scalar
      range:
      - 0.005
      - 0.03
      default: 0.01
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  subtask_id: pre_contact
- id: align_1
  type: align
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.02
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: world_z
      tolerance: 0.05
  parameters:
    align_speed:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
    align_tolerance:
      type: scalar
      range:
      - 0.003
      - 0.015
      default: 0.005
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
- id: insert_1
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
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
    insertion_depth:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    insertion_force_guard_threshold:
      type: scalar
      range:
      - 25.0
      - 45.0
      default: 35.0
      binds_to:
      - path: guards.insertion_force_guard.threshold
        mode: replace
    insertion_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: insertion_force_guard
    when: during_phase
    predicate: force_below
    threshold: 35.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.005
    - 0.005
    - 0.0
  subtask_id: insertion

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.1]
  - orientation: mode=none
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
    - approach_speed: status=consumed; consumers=generator.speed (replace)
    - approach_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
- **align_1** (`align`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.02]
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=world_z, tolerance=0.05
  - parameter_bindings:
    - align_speed: status=consumed; consumers=generator.speed (replace)
    - align_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
- **insert_1** (`push`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.1, mode=add_to_offset, sign=negative}
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=world_z, tolerance=0.1
  - parameter_bindings:
    - insertion_depth: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - insertion_force_guard_threshold: status=consumed; consumers=guards.insertion_force_guard.threshold (replace)
    - insertion_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=insertion_force_guard, when=during_phase, predicate=force_below, on_failure=retry, threshold=35.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.005, 0.005, 0.0]

## Design Metrics

- **Composite score**: -0.045
- **task_score** (E): 0.949
- **fitness_score**: 0.385  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.430

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 0.00 | 0.0608 |
| align_1 | 0.67 | 1.00 | 0.0993 |
| insert_1 | 0.00 | 0.67 | 0.0005 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.495, -0.008, 0.245) | (0.504, -0.000, 0.340)→(0.503, -0.008, 0.284) | 0.260→0.205 | 0.00 / 0.000 | 0.000 | 0.000 |
| align_1 | align | 0.67 / step_budget | (0.495, -0.008, 0.245)→(0.510, -0.044, 0.174) | (0.503, -0.008, 0.284)→(0.539, -0.043, 0.152) | 0.205→0.095 | 1.00 / 1.333 | 267.701 | 4682.626 |
| insert_1 | push | 0.00 / guard_failure | (0.510, -0.044, 0.175)→(0.510, -0.044, 0.175) | (0.539, -0.043, 0.152)→(0.539, -0.043, 0.152) | 0.095→0.095 | 0.67 / 1.000 | 0.361 | 418.021 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.993
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.993
- phase_score: 0.010
- phase_breakdown.insertion_score: 0.000
- phase_breakdown.pre_contact_score: 0.033

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.403
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.993
- **Median Q (composite search score)**: -0.047
- **K-run variance**: 0.0002
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.299


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `d6921a9025d4eafab3a26182307d104597a59aa3c28d9e7087cf253b6e9b1c7f`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `d09be956b809b9acd01354eeb5f0494d5058516cbca42b9f2b0bee8c1b6b25a7`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":6.79032,"average_solve_count":62.0,"average_success_count":62.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.align_speed":0.08347,"align_1.align_tolerance":0.01025,"approach_1.approach_height":0.1318,"approach_1.approach_speed":0.34675,"approach_1.approach_tolerance":0.02959,"insert_1.insertion_depth":0.07613,"insert_1.insertion_force_guard_threshold":36.69651,"insert_1.insertion_speed":0.09828},"optimized_scores":{"best_composite_score":-0.04715,"best_fitness_score":0.38285,"best_task_score":0.93917},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":18.0,"contact_point_centroid":[0.51478,-0.01319,0.07663],"force_p95":1312.49779,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1349.35516,"mean_force":570.56061,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50227,-0.01336,0.08226]},{"body_a":"peg_socket","body_b":"link7","contact_count":841.0,"contact_point_centroid":[0.54068,-0.01781,0.07986],"force_p95":381.11136,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1109.15342,"mean_force":323.1602,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.47037,-0.02106,0.13223]},{"body_a":"peg_socket","body_b":"link7","contact_count":5.0,"contact_point_centroid":[0.54072,-0.01771,0.07995],"force_p95":442.21501,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":545.02732,"mean_force":123.29246,"phase_index":2.0,"phase_name":"insert_1","phase_type":"push","tcp_position_centroid":[0.47864,-0.03789,0.13982]}],"total_contact_groups":3},"final_pose_error":0.13725,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.48093,-0.01612,0.025],"final_tcp_position":[0.47917,-0.03694,0.13953],"realised_fixture_position":[0.48093,-0.01612,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.48093,-0.01612,0.08]},"peak_contact_force":1349.35516,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":93.0,"n_steps_budget":600.0,"object_pos_end":[0.49496,-0.01037,0.27878],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.19911,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"pre_contact","tcp_end":[0.48649,-0.01031,0.23969],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":934.0,"n_steps_budget":1000.0,"object_pos_end":[0.51523,-0.03309,0.12498],"object_pos_start":[0.49496,-0.01037,0.27878],"object_to_goal_dist_end":0.05788,"object_to_goal_dist_start":0.19911,"object_z_max":0.27878,"peak_contact_force":370.26927,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":859.0,"raw_peak_contact_force":1349.35516,"tcp_end":[0.47852,-0.03848,0.13991],"tcp_start":[0.48649,-0.01031,0.23969],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":8.0,"n_steps_budget":900.0,"object_pos_end":[0.51519,-0.03262,0.12463],"object_pos_start":[0.51523,-0.03309,0.12498],"object_to_goal_dist_end":0.05733,"object_to_goal_dist_start":0.05788,"object_z_max":0.12498,"peak_contact_force":0.0,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":5.0,"raw_peak_contact_force":545.02732,"subtask_id":"insertion","tcp_end":[0.47917,-0.03694,0.13953],"tcp_start":[0.47883,-0.03736,0.13971],"tcp_to_object_dist_end":0.03921,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `7c892e828ea48eee928c80191ad243a972830b09953cba6358be1d4656816d00`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":6.41176,"average_solve_count":51.0,"average_success_count":51.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.align_speed":0.09657,"align_1.align_tolerance":0.01157,"approach_1.approach_height":0.11742,"approach_1.approach_speed":0.43924,"approach_1.approach_tolerance":0.02992,"insert_1.insertion_depth":0.11696,"insert_1.insertion_force_guard_threshold":41.74333,"insert_1.insertion_speed":0.05147},"optimized_scores":{"best_composite_score":-0.0622,"best_fitness_score":0.3678,"best_task_score":0.91376},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link7","contact_count":455.0,"contact_point_centroid":[0.52651,-0.02376,0.06562],"force_p95":394.50833,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":11390.12832,"mean_force":597.65436,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.45905,-0.02275,0.11848]},{"body_a":"attachment","body_b":"peg_socket","contact_count":50.0,"contact_point_centroid":[0.51078,-0.01982,0.0769],"force_p95":9281.0755,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":10162.48239,"mean_force":2763.14622,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.47847,-0.02004,0.09189]},{"body_a":"peg_socket","body_b":"link7","contact_count":14.0,"contact_point_centroid":[0.52613,-0.02379,0.04874],"force_p95":2893.35071,"geom_a":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":3139.47632,"mean_force":1082.20911,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.44318,-0.02107,0.10506]},{"body_a":"world","body_b":"link6","contact_count":158.0,"contact_point_centroid":[0.67855,-0.02004,-5e-05],"force_p95":401.10939,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":925.29763,"mean_force":115.09642,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.46242,-0.02504,0.12215]},{"body_a":"world","body_b":"link6","contact_count":3.0,"contact_point_centroid":[0.6786,-0.01978,-3e-05],"force_p95":268.90306,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":269.55049,"mean_force":249.42319,"phase_index":2.0,"phase_name":"insert_1","phase_type":"push","tcp_position_centroid":[0.46315,-0.03066,0.12307]}],"total_contact_groups":5},"final_pose_error":0.16035,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.46685,-0.02106,0.025],"final_tcp_position":[0.46286,-0.03086,0.12305],"realised_fixture_position":[0.46685,-0.02106,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.46685,-0.02106,0.08]},"peak_contact_force":11390.12832,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":115.0,"n_steps_budget":600.0,"object_pos_end":[0.48558,-0.01475,0.26335],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.18451,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"pre_contact","tcp_end":[0.47553,-0.01463,0.22463],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":579.0,"n_steps_budget":810.0,"object_pos_end":[0.50054,-0.02844,0.10882],"object_pos_start":[0.48558,-0.01475,0.26335],"object_to_goal_dist_end":0.04049,"object_to_goal_dist_start":0.18451,"object_z_max":0.26335,"peak_contact_force":190.66367,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":677.0,"raw_peak_contact_force":11390.12832,"tcp_end":[0.46322,-0.03061,0.12305],"tcp_start":[0.47553,-0.01463,0.22463],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":4.0,"n_steps_budget":1000.0,"object_pos_end":[0.50053,-0.02844,0.10884],"object_pos_start":[0.50054,-0.02844,0.10882],"object_to_goal_dist_end":0.04051,"object_to_goal_dist_start":0.04049,"object_z_max":0.10885,"peak_contact_force":1.08379,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3.0,"raw_peak_contact_force":269.55049,"subtask_id":"insertion","tcp_end":[0.46286,-0.03086,0.12305],"tcp_start":[0.46303,-0.03075,0.12308],"tcp_to_object_dist_end":0.04033,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `65c1f23a0338c26bf257d85b07ab64c0180da795e8d67e7d51a2ed2fb2a4d0db`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":6.08197,"average_solve_count":61.0,"average_success_count":61.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.align_speed":0.08922,"align_1.align_tolerance":0.01231,"approach_1.approach_height":0.1878,"approach_1.approach_speed":0.31215,"approach_1.approach_tolerance":0.01172,"insert_1.insertion_depth":0.07133,"insert_1.insertion_force_guard_threshold":37.81292,"insert_1.insertion_speed":0.07117},"optimized_scores":{"best_composite_score":-0.02671,"best_fitness_score":0.40329,"best_task_score":0.9933},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link7","contact_count":686.0,"contact_point_centroid":[0.59518,-0.00535,0.07973],"force_p95":408.97685,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1308.39584,"mean_force":267.30878,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.51016,0.00101,0.10749]},{"body_a":"attachment","body_b":"peg_socket","contact_count":4.0,"contact_point_centroid":[0.56587,0.00068,0.07955],"force_p95":1123.07613,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1146.231,"mean_force":999.07141,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.54966,0.00063,0.08428]},{"body_a":"attachment","body_b":"peg_socket","contact_count":21.0,"contact_point_centroid":[0.50276,0.01391,0.07892],"force_p95":938.81338,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":987.96573,"mean_force":399.44543,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50127,3e-05,0.07551]},{"body_a":"peg_socket","body_b":"link6","contact_count":160.0,"contact_point_centroid":[0.59516,-0.05888,0.07981],"force_p95":402.18271,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":793.62603,"mean_force":168.45642,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.59336,-0.02526,0.24599]},{"body_a":"peg_socket","body_b":"link6","contact_count":2.0,"contact_point_centroid":[0.59542,-0.05899,0.07997],"force_p95":439.21379,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":439.48517,"mean_force":436.77137,"phase_index":2.0,"phase_name":"insert_1","phase_type":"push","tcp_position_centroid":[0.58779,-0.06278,0.26011]},{"body_a":"world","body_b":"link6","contact_count":133.0,"contact_point_centroid":[0.64829,-0.09417,-0.00011],"force_p95":285.00359,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":314.77393,"mean_force":218.51329,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.59485,-0.03013,0.24926]},{"body_a":"world","body_b":"link6","contact_count":3.0,"contact_point_centroid":[0.63795,-0.09453,-0.00013],"force_p95":192.1235,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":192.13583,"mean_force":175.90608,"phase_index":2.0,"phase_name":"insert_1","phase_type":"push","tcp_position_centroid":[0.58784,-0.06308,0.26025]}],"total_contact_groups":7},"final_pose_error":0.26658,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.53544,0.00091,0.025],"final_tcp_position":[0.58822,-0.06507,0.2615],"realised_fixture_position":[0.53544,0.00091,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.53544,0.00091,0.08]},"peak_contact_force":1308.39584,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":147.0,"n_steps_budget":600.0,"object_pos_end":[0.52811,0.00065,0.31098],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.23269,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"pre_contact","tcp_end":[0.52422,0.00064,0.27117],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.60028,-0.06837,0.22246],"object_pos_start":[0.52811,0.00065,0.31098],"object_to_goal_dist_end":0.18715,"object_to_goal_dist_start":0.23269,"object_z_max":0.31098,"peak_contact_force":242.17082,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":1004.0,"raw_peak_contact_force":1308.39584,"tcp_end":[0.58777,-0.06257,0.26001],"tcp_start":[0.52422,0.00064,0.27117],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":4.0,"n_steps_budget":1000.0,"object_pos_end":[0.6003,-0.06873,0.22264],"object_pos_start":[0.60028,-0.06837,0.22246],"object_to_goal_dist_end":0.18743,"object_to_goal_dist_start":0.18715,"object_z_max":0.2234,"peak_contact_force":0.0,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":5.0,"raw_peak_contact_force":439.48517,"subtask_id":"insertion","tcp_end":[0.58822,-0.06507,0.2615],"tcp_start":[0.58808,-0.06442,0.26103],"tcp_to_object_dist_end":0.04087,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```