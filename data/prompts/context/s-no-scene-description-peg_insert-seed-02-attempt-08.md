## Search State

- **Seed**: 2
- **Iteration**: 9 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 8 | approach → align → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | time_limit | 8 | -0.0462 | 0.95 | ❌ rejected |
| 7 | approach → align → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 8 | -0.0458 | 0.95 | ✅ accepted |
| 6 | approach → align → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | 8 | 0.2873 | 0.95 | ✅ accepted |
| 5 | approach → push | linear_cartesian | linear_cartesian | position_control | impedance_control | pose_tolerance | force_exceeded | 6 | 1.1393 | 0.94 | ✅ accepted |
| 4 | approach → push | linear_cartesian | linear_cartesian | position_control | impedance_control | pose_tolerance | force_exceeded | 6 | 1.1291 | 0.93 | ✅ accepted |

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

## Current Skill (Q=-0.046) — your mutation base

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

- **Composite score**: -0.046
- **task_score** (E): 0.949
- **fitness_score**: 0.384  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.430

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 0.00 | 0.0557 |
| align_1 | 0.67 | 1.00 | 0.1101 |
| insert_1 | 1.00 | 0.67 | 0.1030 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.494, -0.008, 0.249) | (0.504, -0.000, 0.340)→(0.502, -0.008, 0.289) | 0.260→0.209 | 0.00 / 0.000 | 0.000 | 0.000 |
| align_1 | align | 0.67 / step_budget | (0.494, -0.008, 0.249)→(0.510, -0.040, 0.167) | (0.502, -0.008, 0.289)→(0.539, -0.039, 0.145) | 0.209→0.090 | 1.00 / 1.333 | 278.675 | 5654.562 |
| insert_1 | push | 1.00 / time_limit | (0.510, -0.040, 0.167)→(0.543, -0.057, 0.255) | (0.539, -0.039, 0.145)→(0.559, -0.056, 0.219) | 0.090→0.167 | 0.67 / 0.667 | 359.054 | 2155.546 |

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
- **Median Q (composite search score)**: -0.050
- **K-run variance**: 0.0002
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.297


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":5.6,"average_solve_count":90.0,"average_success_count":90.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.align_speed":0.0935,"align_1.align_tolerance":0.01046,"approach_1.approach_height":0.14464,"approach_1.approach_speed":0.14889,"approach_1.approach_tolerance":0.02908,"insert_1.insertion_depth":0.10157,"insert_1.insertion_speed":0.05388,"insert_1.max_time":1.18314},"optimized_scores":{"best_composite_score":-0.04981,"best_fitness_score":0.38019,"best_task_score":0.94025},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":8.0,"contact_point_centroid":[0.5118,-0.0123,0.07879],"force_p95":1223.58265,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1292.48123,"mean_force":852.05017,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49404,-0.01247,0.08314]},{"body_a":"peg_socket","body_b":"link7","contact_count":822.0,"contact_point_centroid":[0.54069,-0.01201,0.07287],"force_p95":365.09567,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1015.79355,"mean_force":313.01041,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.46898,-0.01891,0.11867]},{"body_a":"world","body_b":"link6","contact_count":590.0,"contact_point_centroid":[0.60943,-0.1024,-0.00012],"force_p95":579.97739,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":690.65371,"mean_force":381.94947,"phase_index":2.0,"phase_name":"insert_1","phase_type":"push","tcp_position_centroid":[0.53648,-0.06178,0.2493]},{"body_a":"attachment","body_b":"peg_socket","contact_count":10.0,"contact_point_centroid":[0.44988,-0.00359,0.07977],"force_p95":632.95053,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":675.8656,"mean_force":367.91844,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.44711,-0.013,0.09002]},{"body_a":"peg_socket","body_b":"link7","contact_count":181.0,"contact_point_centroid":[0.5407,-0.03451,0.07453],"force_p95":440.88197,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":530.32417,"mean_force":358.77132,"phase_index":2.0,"phase_name":"insert_1","phase_type":"push","tcp_position_centroid":[0.47766,-0.00435,0.11757]},{"body_a":"peg_socket","body_b":"link6","contact_count":276.0,"contact_point_centroid":[0.54087,-0.07602,0.07996],"force_p95":270.22424,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":316.06679,"mean_force":205.31212,"phase_index":2.0,"phase_name":"insert_1","phase_type":"push","tcp_position_centroid":[0.54252,-0.06662,0.2591]}],"total_contact_groups":6},"final_pose_error":0.28052,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.48093,-0.01612,0.025],"final_tcp_position":[0.52048,-0.08812,0.24665],"realised_fixture_position":[0.48093,-0.01612,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.48093,-0.01612,0.08]},"peak_contact_force":1292.48123,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":78.0,"n_steps_budget":600.0,"object_pos_end":[0.49533,-0.00953,0.29128],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.21155,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"pre_contact","tcp_end":[0.48758,-0.00949,0.25204],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":906.0,"n_steps_budget":1000.0,"object_pos_end":[0.51385,-0.02776,0.10963],"object_pos_start":[0.49533,-0.00953,0.29128],"object_to_goal_dist_end":0.0429,"object_to_goal_dist_start":0.21155,"object_z_max":0.29128,"peak_contact_force":351.47322,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":840.0,"raw_peak_contact_force":1292.48123,"tcp_end":[0.47635,-0.0323,0.12279],"tcp_start":[0.48758,-0.00949,0.25204],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54055,-0.08874,0.21206],"object_pos_start":[0.51385,-0.02776,0.10963],"object_to_goal_dist_end":0.16419,"object_to_goal_dist_start":0.0429,"object_z_max":0.22285,"peak_contact_force":0.0,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1047.0,"raw_peak_contact_force":690.65371,"subtask_id":"insertion","tcp_end":[0.52048,-0.08812,0.24665],"tcp_start":[0.47635,-0.0323,0.12279],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `7c892e828ea48eee928c80191ad243a972830b09953cba6358be1d4656816d00`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":6.05319,"average_solve_count":94.0,"average_success_count":94.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.align_speed":0.06461,"align_1.align_tolerance":0.00692,"approach_1.approach_height":0.118,"approach_1.approach_speed":0.306,"approach_1.approach_tolerance":0.02985,"insert_1.insertion_depth":0.10081,"insert_1.insertion_speed":0.05185,"insert_1.max_time":1.03969},"optimized_scores":{"best_composite_score":-0.06204,"best_fitness_score":0.36796,"best_task_score":0.91404},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link7","contact_count":889.0,"contact_point_centroid":[0.52664,-0.02071,0.06472],"force_p95":348.27003,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":11998.86189,"mean_force":454.0702,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.46032,-0.02452,0.11854]},{"body_a":"attachment","body_b":"peg_socket","contact_count":350.0,"contact_point_centroid":[0.52434,-0.02457,0.07959],"force_p95":1274.58446,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":9888.43357,"mean_force":455.96729,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.46396,-0.0283,0.11562]},{"body_a":"world","body_b":"link5","contact_count":510.0,"contact_point_centroid":[0.51738,0.09444,-4e-05],"force_p95":917.25805,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":5094.58972,"mean_force":442.97689,"phase_index":2.0,"phase_name":"insert_1","phase_type":"push","tcp_position_centroid":[0.51456,-0.01251,0.24985]},{"body_a":"peg_socket","body_b":"link7","contact_count":13.0,"contact_point_centroid":[0.52634,-0.0227,0.04882],"force_p95":4005.42585,"geom_a":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":4239.43886,"mean_force":1663.59857,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.44122,-0.02018,0.10232]},{"body_a":"peg_socket","body_b":"link5","contact_count":353.0,"contact_point_centroid":[0.49998,0.03862,0.05207],"force_p95":944.48642,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":3108.04911,"mean_force":303.78829,"phase_index":2.0,"phase_name":"insert_1","phase_type":"push","tcp_position_centroid":[0.51582,-0.01561,0.24824]},{"body_a":"world","body_b":"link6","contact_count":46.0,"contact_point_centroid":[0.65271,0.02042,-0.0002],"force_p95":400.3243,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":2313.1264,"mean_force":359.19981,"phase_index":2.0,"phase_name":"insert_1","phase_type":"push","tcp_position_centroid":[0.49734,-0.06675,0.17495]},{"body_a":"peg_socket","body_b":"link7","contact_count":377.0,"contact_point_centroid":[0.52675,-0.02016,0.06787],"force_p95":676.43586,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1550.37855,"mean_force":397.2848,"phase_index":2.0,"phase_name":"insert_1","phase_type":"push","tcp_position_centroid":[0.46227,-0.04711,0.11709]},{"body_a":"peg_socket","body_b":"link5","contact_count":244.0,"contact_point_centroid":[0.49554,0.03878,0.0535],"force_p95":349.02123,"geom_a":"socket_collar_y1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1177.66827,"mean_force":147.98196,"phase_index":2.0,"phase_name":"insert_1","phase_type":"push","tcp_position_centroid":[0.5149,-0.01491,0.24859]},{"body_a":"peg_socket","body_b":"link5","contact_count":381.0,"contact_point_centroid":[0.49997,0.03867,0.04996],"force_p95":435.25603,"geom_a":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1126.65748,"mean_force":175.77979,"phase_index":2.0,"phase_name":"insert_1","phase_type":"push","tcp_position_centroid":[0.51549,-0.01504,0.24855]},{"body_a":"attachment","body_b":"peg_socket","contact_count":329.0,"contact_point_centroid":[0.52684,-0.03535,0.07996],"force_p95":625.22307,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":748.47641,"mean_force":341.66809,"phase_index":2.0,"phase_name":"insert_1","phase_type":"push","tcp_position_centroid":[0.46197,-0.04634,0.11708]},{"body_a":"world","body_b":"link6","contact_count":307.0,"contact_point_centroid":[0.67911,-0.01853,-2e-05],"force_p95":83.18858,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":269.49553,"mean_force":30.1071,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.46194,-0.0239,0.12034]}],"total_contact_groups":11},"final_pose_error":0.27586,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.46685,-0.02106,0.025],"final_tcp_position":[0.51333,-0.01045,0.2509],"realised_fixture_position":[0.46685,-0.02106,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.46685,-0.02106,0.08]},"peak_contact_force":11998.86189,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":114.0,"n_steps_budget":600.0,"object_pos_end":[0.4857,-0.01465,0.26427],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.1854,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"pre_contact","tcp_end":[0.4757,-0.01453,0.22554],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49992,-0.03267,0.10566],"object_pos_start":[0.4857,-0.01465,0.26427],"object_to_goal_dist_end":0.04155,"object_to_goal_dist_start":0.1854,"object_z_max":0.26427,"peak_contact_force":348.76816,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":1559.0,"raw_peak_contact_force":11998.86189,"tcp_end":[0.46248,-0.03672,0.11915],"tcp_start":[0.4757,-0.01453,0.22554],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53293,-0.00378,0.21668],"object_pos_start":[0.49992,-0.03267,0.10566],"object_to_goal_dist_end":0.14064,"object_to_goal_dist_start":0.04155,"object_z_max":0.21712,"peak_contact_force":647.15292,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2240.0,"raw_peak_contact_force":5094.58972,"subtask_id":"insertion","tcp_end":[0.51333,-0.01045,0.2509],"tcp_start":[0.46248,-0.03672,0.11915],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `65c1f23a0338c26bf257d85b07ab64c0180da795e8d67e7d51a2ed2fb2a4d0db`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":5.17391,"average_solve_count":92.0,"average_success_count":92.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.align_speed":0.09971,"align_1.align_tolerance":0.01166,"approach_1.approach_height":0.17669,"approach_1.approach_speed":0.19223,"approach_1.approach_tolerance":0.02123,"insert_1.insertion_depth":0.15222,"insert_1.insertion_speed":0.07072,"insert_1.max_time":1.40464},"optimized_scores":{"best_composite_score":-0.02669,"best_fitness_score":0.40331,"best_task_score":0.99343},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link6","contact_count":204.0,"contact_point_centroid":[0.59531,-0.05898,0.07995],"force_p95":904.93475,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":3672.34191,"mean_force":232.95319,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.59396,-0.02909,0.24892]},{"body_a":"world","body_b":"link6","contact_count":175.0,"contact_point_centroid":[0.65265,-0.09306,-0.0001],"force_p95":969.44065,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":3573.36957,"mean_force":272.63754,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.59412,-0.02726,0.24758]},{"body_a":"peg_socket","body_b":"link7","contact_count":635.0,"contact_point_centroid":[0.5952,-0.00511,0.07974],"force_p95":393.15709,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1217.08576,"mean_force":267.94903,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.51012,0.00212,0.10863]},{"body_a":"attachment","body_b":"peg_socket","contact_count":5.0,"contact_point_centroid":[0.56587,0.0006,0.07957],"force_p95":1134.10329,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1165.29755,"mean_force":976.24932,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.54885,0.00053,0.08337]},{"body_a":"attachment","body_b":"peg_socket","contact_count":21.0,"contact_point_centroid":[0.50288,0.01403,0.07892],"force_p95":929.8619,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":983.53397,"mean_force":405.84378,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50143,2e-05,0.07575]},{"body_a":"world","body_b":"link6","contact_count":902.0,"contact_point_centroid":[0.60752,-0.1049,-4e-05],"force_p95":446.59917,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":681.39374,"mean_force":236.64719,"phase_index":2.0,"phase_name":"insert_1","phase_type":"push","tcp_position_centroid":[0.60649,-0.09559,0.26915]},{"body_a":"peg_socket","body_b":"link6","contact_count":928.0,"contact_point_centroid":[0.59544,-0.05904,0.07344],"force_p95":363.04506,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":601.39867,"mean_force":223.35077,"phase_index":2.0,"phase_name":"insert_1","phase_type":"push","tcp_position_centroid":[0.6064,-0.09503,0.26906]}],"total_contact_groups":7},"final_pose_error":0.35117,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.53544,0.00091,0.025],"final_tcp_position":[0.59588,-0.07126,0.26609],"realised_fixture_position":[0.53544,0.00091,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.53544,0.00091,0.08]},"peak_contact_force":3672.34191,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":81.0,"n_steps_budget":600.0,"object_pos_end":[0.52406,0.00053,0.3102],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.23145,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"pre_contact","tcp_end":[0.51978,0.00052,0.27042],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":993.0,"n_steps_budget":1000.0,"object_pos_end":[0.60461,-0.05789,0.22078],"object_pos_start":[0.52406,0.00053,0.3102],"object_to_goal_dist_end":0.1847,"object_to_goal_dist_start":0.23145,"object_z_max":0.3102,"peak_contact_force":135.78352,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":1040.0,"raw_peak_contact_force":3672.34191,"tcp_end":[0.59145,-0.05091,0.2579],"tcp_start":[0.51978,0.00052,0.27042],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.60375,-0.076,0.22716],"object_pos_start":[0.60461,-0.05789,0.22078],"object_to_goal_dist_end":0.19544,"object_to_goal_dist_start":0.1847,"object_z_max":0.23012,"peak_contact_force":430.00976,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1830.0,"raw_peak_contact_force":681.39374,"subtask_id":"insertion","tcp_end":[0.59588,-0.07126,0.26609],"tcp_start":[0.59145,-0.05091,0.2579],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
```