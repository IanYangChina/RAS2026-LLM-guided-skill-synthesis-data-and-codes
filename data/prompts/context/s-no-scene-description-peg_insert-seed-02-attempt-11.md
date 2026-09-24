## Search State

- **Seed**: 2
- **Iteration**: 12 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 11 | approach → align → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | time_limit | 9 | -0.0922 | 0.95 | ❌ rejected |
| 10 | approach → align → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.0057 | 0.94 | ❌ rejected |
| 9 | approach → align → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | pose_tolerance | force_exceeded | force_exceeded | 8 | 0.3063 | 0.92 | ❌ rejected |
| 8 | approach → align → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | time_limit | 8 | -0.0462 | 0.95 | ❌ rejected |
| 7 | approach → align → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 8 | -0.0458 | 0.95 | ✅ accepted |

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

## Current Skill (Q=-0.092) — your mutation base

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

- **Composite score**: -0.092
- **task_score** (E): 0.945
- **fitness_score**: 0.388  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.480

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 0.00 | 0.0651 |
| align_1 | 0.67 | 0.67 | 0.0915 |
| insert_1 | 0.00 | 1.00 | 0.0002 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.495, -0.008, 0.240) | (0.504, -0.000, 0.340)→(0.502, -0.009, 0.279) | 0.260→0.201 | 0.00 / 0.000 | 0.000 | 0.000 |
| align_1 | align | 0.67 / step_budget | (0.495, -0.008, 0.240)→(0.477, -0.022, 0.153) | (0.502, -0.009, 0.279)→(0.513, -0.020, 0.137) | 0.201→0.065 | 0.67 / 0.667 | 183.401 | 4544.305 |
| insert_1 | push | 0.00 / guard_failure | (0.477, -0.022, 0.151)→(0.478, -0.021, 0.151) | (0.513, -0.020, 0.137)→(0.514, -0.019, 0.135) | 0.065→0.064 | 1.00 / 1.000 | 152.220 | 448.428 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.985
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.985
- phase_score: 0.035
- phase_breakdown.insertion_score: 0.039
- phase_breakdown.pre_contact_score: 0.027

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.415
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.985
- **Median Q (composite search score)**: -0.100
- **K-run variance**: 0.0004
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.274


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":6.68966,"average_solve_count":58.0,"average_success_count":58.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.align_speed":0.08925,"align_1.align_tolerance":0.00723,"approach_1.approach_height":0.13568,"approach_1.approach_speed":0.30754,"approach_1.approach_tolerance":0.02283,"insert_1.insertion_depth":0.14712,"insert_1.insertion_force_guard_threshold":33.02737,"insert_1.insertion_speed":0.03877,"insert_1.insertion_time_limit":3.54258},"optimized_scores":{"best_composite_score":-0.09963,"best_fitness_score":0.38037,"best_task_score":0.93609},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":13.0,"contact_point_centroid":[0.51386,-0.01397,0.07744],"force_p95":1310.10388,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1328.614,"mean_force":680.15496,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49933,-0.01415,0.08227]},{"body_a":"peg_socket","body_b":"link7","contact_count":786.0,"contact_point_centroid":[0.54065,-0.01783,0.07983],"force_p95":371.07017,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1059.47786,"mean_force":320.65812,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.46977,-0.02062,0.1348]},{"body_a":"peg_socket","body_b":"link7","contact_count":4.0,"contact_point_centroid":[0.54076,-0.01724,0.07996],"force_p95":464.69208,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":543.79823,"mean_force":141.54509,"phase_index":2.0,"phase_name":"insert_1","phase_type":"push","tcp_position_centroid":[0.47821,-0.03479,0.14269]},{"body_a":"attachment","body_b":"peg_socket","contact_count":1.0,"contact_point_centroid":[0.44948,-0.01473,0.07957],"force_p95":0.0,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.44701,-0.01472,0.09394]}],"total_contact_groups":4},"final_pose_error":0.21049,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.48093,-0.01612,0.025],"final_tcp_position":[0.47849,-0.03424,0.14257],"realised_fixture_position":[0.48093,-0.01612,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.48093,-0.01612,0.08]},"peak_contact_force":1328.614,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":117.0,"n_steps_budget":600.0,"object_pos_end":[0.49367,-0.01125,0.2763],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.19672,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"pre_contact","tcp_end":[0.48497,-0.01119,0.23725],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":874.0,"n_steps_budget":960.0,"object_pos_end":[0.51479,-0.03061,0.1275],"object_pos_start":[0.49367,-0.01125,0.2763],"object_to_goal_dist_end":0.05842,"object_to_goal_dist_start":0.19672,"object_z_max":0.2763,"peak_contact_force":364.323,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":800.0,"raw_peak_contact_force":1328.614,"tcp_end":[0.47807,-0.03508,0.14273],"tcp_start":[0.48497,-0.01119,0.23725],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":7.0,"n_steps_budget":1000.0,"object_pos_end":[0.51481,-0.03033,0.12718],"object_pos_start":[0.51479,-0.03061,0.1275],"object_to_goal_dist_end":0.05801,"object_to_goal_dist_start":0.05842,"object_z_max":0.1275,"peak_contact_force":5.95821,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":4.0,"raw_peak_contact_force":543.79823,"subtask_id":"insertion","tcp_end":[0.47849,-0.03424,0.14257],"tcp_start":[0.47828,-0.03452,0.14268],"tcp_to_object_dist_end":0.03964,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `7c892e828ea48eee928c80191ad243a972830b09953cba6358be1d4656816d00`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":6.15909,"average_solve_count":44.0,"average_success_count":44.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.align_speed":0.1301,"align_1.align_tolerance":0.006,"approach_1.approach_height":0.11739,"approach_1.approach_speed":0.44674,"approach_1.approach_tolerance":0.02813,"insert_1.insertion_depth":0.17974,"insert_1.insertion_force_guard_threshold":34.96458,"insert_1.insertion_speed":0.02337,"insert_1.insertion_time_limit":3.8037},"optimized_scores":{"best_composite_score":-0.11226,"best_fitness_score":0.36774,"best_task_score":0.91374},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":114.0,"contact_point_centroid":[0.5185,-0.02138,0.07843],"force_p95":10197.10044,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":10944.02299,"mean_force":2078.16852,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.46441,-0.02234,0.1026]},{"body_a":"peg_socket","body_b":"link7","contact_count":448.0,"contact_point_centroid":[0.52641,-0.02152,0.06427],"force_p95":4388.20954,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":10535.14574,"mean_force":744.75562,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.45608,-0.02322,0.11285]},{"body_a":"world","body_b":"link6","contact_count":96.0,"contact_point_centroid":[0.67912,-0.02132,-0.0001],"force_p95":507.8943,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1003.18955,"mean_force":167.85448,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.46192,-0.02581,0.12018]},{"body_a":"world","body_b":"link6","contact_count":3.0,"contact_point_centroid":[0.67918,-0.02152,-4e-05],"force_p95":265.92712,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":270.13328,"mean_force":234.89889,"phase_index":2.0,"phase_name":"insert_1","phase_type":"push","tcp_position_centroid":[0.46274,-0.0285,0.12158]},{"body_a":"peg_socket","body_b":"link7","contact_count":19.0,"contact_point_centroid":[0.52516,-0.02383,0.04909],"force_p95":0.0,"geom_a":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.44214,-0.02126,0.10248]}],"total_contact_groups":5},"final_pose_error":0.22151,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.46685,-0.02106,0.025],"final_tcp_position":[0.46268,-0.02853,0.12161],"realised_fixture_position":[0.46685,-0.02106,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.46685,-0.02106,0.08]},"peak_contact_force":10944.02299,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":122.0,"n_steps_budget":600.0,"object_pos_end":[0.48517,-0.015,0.26205],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.18327,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"pre_contact","tcp_end":[0.47501,-0.01487,0.22336],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":572.0,"n_steps_budget":630.0,"object_pos_end":[0.50019,-0.02708,0.10755],"object_pos_start":[0.48517,-0.015,0.26205],"object_to_goal_dist_end":0.03863,"object_to_goal_dist_start":0.18327,"object_z_max":0.26205,"peak_contact_force":185.88072,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":677.0,"raw_peak_contact_force":10944.02299,"tcp_end":[0.46274,-0.02851,0.12154],"tcp_start":[0.47501,-0.01487,0.22336],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.50019,-0.02705,0.10759],"object_pos_start":[0.50019,-0.02708,0.10755],"object_to_goal_dist_end":0.03864,"object_to_goal_dist_start":0.03863,"object_z_max":0.10761,"peak_contact_force":228.0717,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3.0,"raw_peak_contact_force":270.13328,"subtask_id":"insertion","tcp_end":[0.46268,-0.02853,0.12161],"tcp_start":[0.46273,-0.0285,0.1216],"tcp_to_object_dist_end":0.04007,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `65c1f23a0338c26bf257d85b07ab64c0180da795e8d67e7d51a2ed2fb2a4d0db`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":6.90625,"average_solve_count":64.0,"average_success_count":64.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.align_speed":0.0522,"align_1.align_tolerance":0.00818,"approach_1.approach_height":0.17116,"approach_1.approach_speed":0.34186,"approach_1.approach_tolerance":0.0151,"insert_1.insertion_depth":0.10088,"insert_1.insertion_force_guard_threshold":31.34402,"insert_1.insertion_speed":0.07543,"insert_1.insertion_time_limit":3.55166},"optimized_scores":{"best_composite_score":-0.06477,"best_fitness_score":0.41523,"best_task_score":0.98526},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":11.0,"contact_point_centroid":[0.56833,0.00075,0.07779],"force_p95":1320.98403,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1360.27741,"mean_force":746.10366,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.55141,0.00071,0.07943]},{"body_a":"peg_socket","body_b":"link7","contact_count":156.0,"contact_point_centroid":[0.59347,0.00263,0.0793],"force_p95":1020.35526,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1201.27746,"mean_force":410.68256,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.47926,0.00017,0.13793]},{"body_a":"peg_socket","body_b":"link6","contact_count":766.0,"contact_point_centroid":[0.59537,-0.00091,0.0798],"force_p95":315.21662,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1095.54526,"mean_force":276.77048,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.47574,-0.00018,0.17092]},{"body_a":"attachment","body_b":"peg_socket","contact_count":13.0,"contact_point_centroid":[0.49798,0.00454,0.07773],"force_p95":903.58837,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":931.17034,"mean_force":250.33135,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49369,0.00034,0.08713]},{"body_a":"peg_socket","body_b":"link6","contact_count":3.0,"contact_point_centroid":[0.59525,4e-05,0.07966],"force_p95":500.4813,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":531.35378,"mean_force":304.36865,"phase_index":2.0,"phase_name":"insert_1","phase_type":"push","tcp_position_centroid":[0.49142,-0.00174,0.19033]}],"total_contact_groups":5},"final_pose_error":0.21553,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.53544,0.00091,0.025],"final_tcp_position":[0.49142,-0.00151,0.19009],"realised_fixture_position":[0.53544,0.00091,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.53544,0.00091,0.08]},"peak_contact_force":1360.27741,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":132.0,"n_steps_budget":600.0,"object_pos_end":[0.52808,0.00063,0.29988],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.22166,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"pre_contact","tcp_end":[0.52358,0.00062,0.26013],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52498,-0.00126,0.17445],"object_pos_start":[0.52808,0.00063,0.29988],"object_to_goal_dist_end":0.09771,"object_to_goal_dist_start":0.22166,"object_z_max":0.29988,"peak_contact_force":0.0,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":946.0,"raw_peak_contact_force":1360.27741,"tcp_end":[0.4906,-0.00237,0.19486],"tcp_start":[0.52358,0.00062,0.26013],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":10.0,"n_steps_budget":1000.0,"object_pos_end":[0.52597,-0.00089,0.17024],"object_pos_start":[0.52498,-0.00126,0.17445],"object_to_goal_dist_end":0.09391,"object_to_goal_dist_start":0.09771,"object_z_max":0.17445,"peak_contact_force":222.62893,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3.0,"raw_peak_contact_force":531.35378,"subtask_id":"insertion","tcp_end":[0.49142,-0.00151,0.19009],"tcp_start":[0.49134,-0.00165,0.19018],"tcp_to_object_dist_end":0.03985,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```