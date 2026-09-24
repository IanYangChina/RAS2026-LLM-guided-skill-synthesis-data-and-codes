## Search State

- **Seed**: 2
- **Iteration**: 7 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 6 | approach → align → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | 8 | 0.2873 | 0.95 | ✅ accepted |
| 5 | approach → push | linear_cartesian | linear_cartesian | position_control | impedance_control | pose_tolerance | force_exceeded | 6 | 1.1393 | 0.94 | ✅ accepted |
| 4 | approach → push | linear_cartesian | linear_cartesian | position_control | impedance_control | pose_tolerance | force_exceeded | 6 | 1.1291 | 0.93 | ✅ accepted |
| 3 | approach → push | linear_cartesian | linear_cartesian | position_control | impedance_control | pose_tolerance | force_exceeded | 10 | -0.5000 | 0.00 | ❌ rejected |
| 2 | approach → push | linear_cartesian | linear_cartesian | position_control | impedance_control | pose_tolerance | force_exceeded | 8 | 0.8506 | 0.92 | ✅ accepted |

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

## Current Skill (Q=0.287) — your mutation base

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
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.05
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
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
    align_tolerance:
      type: scalar
      range:
      - 0.002
      - 0.02
      default: 0.005
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
- id: insert_1
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: force_exceeded
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
      - 0.02
      - 0.15
      default: 0.05
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    insertion_force_threshold:
      type: scalar
      range:
      - 10.0
      - 40.0
      default: 30.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    insertion_speed:
      type: scalar
      range:
      - 0.02
      - 0.2
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
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
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.05]
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=world_z, tolerance=0.05
  - parameter_bindings:
    - align_speed: status=consumed; consumers=generator.speed (replace)
    - align_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
- **insert_1** (`push`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.1, mode=add_to_offset, sign=negative}
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=world_z, tolerance=0.1
  - parameter_bindings:
    - insertion_depth: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - insertion_force_threshold: status=consumed; consumers=termination.force_threshold (replace)
    - insertion_speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=2, strategy=offset_target, offset=[0.005, 0.005, 0.0]

## Design Metrics

- **Composite score**: 0.287
- **task_score** (E): 0.950
- **fitness_score**: 0.384  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.333
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.430

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 0.00 | 0.0577 |
| align_1 | 0.67 | 1.00 | 0.1147 |
| insert_1 | 1.00 | 1.00 | 0.0006 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.495, -0.008, 0.248) | (0.504, -0.000, 0.340)→(0.502, -0.008, 0.287) | 0.260→0.208 | 0.00 / 0.000 | 0.000 | 0.000 |
| align_1 | align | 0.67 / step_budget | (0.495, -0.008, 0.248)→(0.515, -0.008, 0.155) | (0.502, -0.008, 0.287)→(0.544, -0.014, 0.137) | 0.208→0.081 | 1.00 / 1.667 | 265.532 | 4367.270 |
| insert_1 | push | 1.00 / force_exceeded | (0.515, -0.008, 0.155)→(0.515, -0.009, 0.156) | (0.544, -0.014, 0.137)→(0.544, -0.015, 0.137) | 0.081→0.081 | 1.00 / 1.667 | 281.399 | 281.399 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.997
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.997
- phase_score: 0.010
- phase_breakdown.insertion_score: 0.000
- phase_breakdown.pre_contact_score: 0.032

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.405
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.997
- **Median Q (composite search score)**: 0.283
- **K-run variance**: 0.0002
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.300


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":6.33333,"average_solve_count":48.0,"average_success_count":48.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.align_speed":0.09465,"align_1.align_tolerance":0.01265,"approach_1.approach_height":0.14368,"approach_1.approach_speed":0.23961,"approach_1.approach_tolerance":0.02857,"insert_1.insertion_depth":0.10502,"insert_1.insertion_force_threshold":28.78226,"insert_1.insertion_speed":0.15777},"optimized_scores":{"best_composite_score":0.2829,"best_fitness_score":0.37956,"best_task_score":0.93839},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":7.0,"contact_point_centroid":[0.51189,-0.01279,0.0787],"force_p95":1121.96965,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1145.50685,"mean_force":889.70561,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49394,-0.01297,0.08261]},{"body_a":"peg_socket","body_b":"link7","contact_count":612.0,"contact_point_centroid":[0.54068,-0.01292,0.07394],"force_p95":328.8225,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1116.28854,"mean_force":310.78878,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.4679,-0.01703,0.11843]},{"body_a":"attachment","body_b":"peg_socket","contact_count":11.0,"contact_point_centroid":[0.44989,-0.00222,0.07977],"force_p95":739.83577,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":793.57395,"mean_force":429.05956,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.44727,-0.01355,0.08832]},{"body_a":"peg_socket","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.54078,-0.01192,0.07202],"force_p95":340.42906,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":340.42906,"mean_force":340.42906,"phase_index":2.0,"phase_name":"insert_1","phase_type":"push","tcp_position_centroid":[0.46906,-0.02396,0.11787]}],"total_contact_groups":4},"final_pose_error":0.14361,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.48093,-0.01612,0.025],"final_tcp_position":[0.46909,-0.0239,0.11789],"realised_fixture_position":[0.48093,-0.01612,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.48093,-0.01612,0.08]},"peak_contact_force":1145.50685,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":81.0,"n_steps_budget":600.0,"object_pos_end":[0.49517,-0.00971,0.28977],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.21005,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"pre_contact","tcp_end":[0.48732,-0.00967,0.25055],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":694.0,"n_steps_budget":810.0,"object_pos_end":[0.50809,-0.02179,0.1094],"object_pos_start":[0.49517,-0.00971,0.28977],"object_to_goal_dist_end":0.03748,"object_to_goal_dist_start":0.21005,"object_z_max":0.28977,"peak_contact_force":309.87119,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":630.0,"raw_peak_contact_force":1145.50685,"tcp_end":[0.46906,-0.02396,0.11787],"tcp_start":[0.48732,-0.00967,0.25055],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.50812,-0.02174,0.1094],"object_pos_start":[0.50809,-0.02179,0.1094],"object_to_goal_dist_end":0.03746,"object_to_goal_dist_start":0.03748,"object_z_max":0.1094,"peak_contact_force":340.42906,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1.0,"raw_peak_contact_force":340.42906,"subtask_id":"insertion","tcp_end":[0.46909,-0.0239,0.11789],"tcp_start":[0.46906,-0.02396,0.11787],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `7c892e828ea48eee928c80191ad243a972830b09953cba6358be1d4656816d00`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":5.88636,"average_solve_count":44.0,"average_success_count":44.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.align_speed":0.17039,"align_1.align_tolerance":0.00452,"approach_1.approach_height":0.11795,"approach_1.approach_speed":0.10026,"approach_1.approach_tolerance":0.02845,"insert_1.insertion_depth":0.0417,"insert_1.insertion_force_threshold":24.57989,"insert_1.insertion_speed":0.03592},"optimized_scores":{"best_composite_score":0.27106,"best_fitness_score":0.36773,"best_task_score":0.91312},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":166.0,"contact_point_centroid":[0.52112,-0.02034,0.07905],"force_p95":8089.16025,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":9468.41176,"mean_force":1287.51373,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.45661,-0.02112,0.0985]},{"body_a":"peg_socket","body_b":"link7","contact_count":431.0,"contact_point_centroid":[0.52643,-0.02115,0.0644],"force_p95":3807.59648,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":9122.0626,"mean_force":698.35035,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.45425,-0.0228,0.11005]},{"body_a":"world","body_b":"link6","contact_count":35.0,"contact_point_centroid":[0.67902,-0.02169,-0.0002],"force_p95":383.8194,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":413.45349,"mean_force":124.98872,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.46192,-0.02392,0.12025]},{"body_a":"peg_socket","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.52678,-0.02847,0.06367],"force_p95":249.27627,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":249.27627,"mean_force":249.27627,"phase_index":2.0,"phase_name":"insert_1","phase_type":"push","tcp_position_centroid":[0.46168,-0.02594,0.11967]},{"body_a":"world","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.67926,-0.02188,-3e-05],"force_p95":147.90852,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":147.90852,"mean_force":147.90852,"phase_index":2.0,"phase_name":"insert_1","phase_type":"push","tcp_position_centroid":[0.46168,-0.02594,0.11967]},{"body_a":"peg_socket","body_b":"link7","contact_count":16.0,"contact_point_centroid":[0.52581,-0.02382,0.04941],"force_p95":0.0,"geom_a":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.44221,-0.02086,0.10213]}],"total_contact_groups":6},"final_pose_error":0.08167,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.46685,-0.02106,0.025],"final_tcp_position":[0.46167,-0.02592,0.11966],"realised_fixture_position":[0.46685,-0.02106,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.46685,-0.02106,0.08]},"peak_contact_force":9468.41176,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":121.0,"n_steps_budget":690.0,"object_pos_end":[0.48531,-0.01488,0.26302],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.18421,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"pre_contact","tcp_end":[0.47521,-0.01476,0.22432],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":542.0,"n_steps_budget":600.0,"object_pos_end":[0.49926,-0.02507,0.10601],"object_pos_start":[0.48531,-0.01488,0.26302],"object_to_goal_dist_end":0.03613,"object_to_goal_dist_start":0.18421,"object_z_max":0.26302,"peak_contact_force":321.91199,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":648.0,"raw_peak_contact_force":9468.41176,"tcp_end":[0.46168,-0.02594,0.11967],"tcp_start":[0.47521,-0.01476,0.22432],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.49926,-0.02505,0.10601],"object_pos_start":[0.49926,-0.02507,0.10601],"object_to_goal_dist_end":0.03612,"object_to_goal_dist_start":0.03613,"object_z_max":0.10601,"peak_contact_force":249.27627,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2.0,"raw_peak_contact_force":249.27627,"subtask_id":"insertion","tcp_end":[0.46167,-0.02592,0.11966],"tcp_start":[0.46168,-0.02594,0.11967],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `65c1f23a0338c26bf257d85b07ab64c0180da795e8d67e7d51a2ed2fb2a4d0db`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":6.56522,"average_solve_count":46.0,"average_success_count":46.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.align_speed":0.118,"align_1.align_tolerance":0.00627,"approach_1.approach_height":0.18194,"approach_1.approach_speed":0.47456,"approach_1.approach_tolerance":0.0146,"insert_1.insertion_depth":0.09922,"insert_1.insertion_force_threshold":28.71793,"insert_1.insertion_speed":0.06666},"optimized_scores":{"best_composite_score":0.30789,"best_fitness_score":0.40455,"best_task_score":0.99711},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link6","contact_count":14.0,"contact_point_centroid":[0.59493,-0.05864,0.07876],"force_p95":2362.85092,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":2487.89053,"mean_force":725.56851,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.61213,0.04113,0.21094]},{"body_a":"world","body_b":"link6","contact_count":36.0,"contact_point_centroid":[0.66899,-0.09946,-0.0013],"force_p95":2029.24979,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":2416.12721,"mean_force":405.39137,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.61084,0.05324,0.19523]},{"body_a":"attachment","body_b":"peg_socket","contact_count":6.0,"contact_point_centroid":[0.56665,0.0007,0.07923],"force_p95":1231.37303,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1297.09097,"mean_force":942.43212,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.55142,0.00066,0.08425]},{"body_a":"peg_socket","body_b":"link7","contact_count":521.0,"contact_point_centroid":[0.59516,-0.00652,0.07948],"force_p95":428.99788,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1284.25828,"mean_force":278.24376,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.51229,0.00382,0.10735]},{"body_a":"attachment","body_b":"peg_socket","contact_count":21.0,"contact_point_centroid":[0.50273,0.01436,0.07898],"force_p95":949.86394,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":967.87344,"mean_force":393.49578,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50019,0.00013,0.07818]},{"body_a":"peg_socket","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.59495,-0.05863,0.07973],"force_p95":254.49127,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":254.49127,"mean_force":254.49127,"phase_index":2.0,"phase_name":"insert_1","phase_type":"push","tcp_position_centroid":[0.61451,0.02557,0.22797]},{"body_a":"world","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.65232,-0.09465,-0.00032],"force_p95":159.14609,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":159.14609,"mean_force":159.14609,"phase_index":2.0,"phase_name":"insert_1","phase_type":"push","tcp_position_centroid":[0.61451,0.02557,0.22797]}],"total_contact_groups":7},"final_pose_error":0.26162,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.53544,0.00091,0.025],"final_tcp_position":[0.61473,0.02412,0.22902],"realised_fixture_position":[0.53544,0.00091,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.53544,0.00091,0.08]},"peak_contact_force":2487.89053,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":121.0,"n_steps_budget":600.0,"object_pos_end":[0.52696,0.00061,0.30857],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.23016,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"pre_contact","tcp_end":[0.52284,0.0006,0.26879],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":692.0,"n_steps_budget":750.0,"object_pos_end":[0.62408,0.00407,0.19563],"object_pos_start":[0.52696,0.00061,0.30857],"object_to_goal_dist_end":0.16965,"object_to_goal_dist_start":0.23016,"object_z_max":0.30857,"peak_contact_force":164.8122,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":598.0,"raw_peak_contact_force":2487.89053,"tcp_end":[0.61451,0.02557,0.22797],"tcp_start":[0.52284,0.0006,0.26879],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.62424,0.00283,0.19651],"object_pos_start":[0.62408,0.00407,0.19563],"object_to_goal_dist_end":0.17035,"object_to_goal_dist_start":0.16965,"object_z_max":0.19563,"peak_contact_force":254.49127,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2.0,"raw_peak_contact_force":254.49127,"subtask_id":"insertion","tcp_end":[0.61473,0.02412,0.22902],"tcp_start":[0.61451,0.02557,0.22797],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":false}]}
```