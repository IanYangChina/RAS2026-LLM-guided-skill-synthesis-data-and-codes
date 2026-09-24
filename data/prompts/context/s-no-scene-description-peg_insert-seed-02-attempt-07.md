## Search State

- **Seed**: 2
- **Iteration**: 8 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 7 | approach → align → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 8 | -0.0458 | 0.95 | ✅ accepted |
| 6 | approach → align → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | 8 | 0.2873 | 0.95 | ✅ accepted |
| 5 | approach → push | linear_cartesian | linear_cartesian | position_control | impedance_control | pose_tolerance | force_exceeded | 6 | 1.1393 | 0.94 | ✅ accepted |
| 4 | approach → push | linear_cartesian | linear_cartesian | position_control | impedance_control | pose_tolerance | force_exceeded | 6 | 1.1291 | 0.93 | ✅ accepted |
| 3 | approach → push | linear_cartesian | linear_cartesian | position_control | impedance_control | pose_tolerance | force_exceeded | 10 | -0.5000 | 0.00 | ❌ rejected |

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
- **task_score** (E): 0.950
- **fitness_score**: 0.384  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.430

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 0.00 | 0.0634 |
| align_1 | 0.67 | 1.00 | 0.0975 |
| insert_1 | 0.00 | 1.00 | 0.0004 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.494, -0.008, 0.242) | (0.504, -0.000, 0.340)→(0.502, -0.008, 0.281) | 0.260→0.202 | 0.00 / 0.000 | 0.000 | 0.000 |
| align_1 | align | 0.67 / step_budget | (0.494, -0.008, 0.242)→(0.510, -0.040, 0.174) | (0.502, -0.008, 0.281)→(0.540, -0.040, 0.152) | 0.202→0.094 | 1.00 / 1.333 | 120.178 | 4692.804 |
| insert_1 | push | 0.00 / guard_failure | (0.511, -0.040, 0.174)→(0.511, -0.040, 0.174) | (0.540, -0.040, 0.152)→(0.540, -0.040, 0.152) | 0.094→0.094 | 1.00 / 1.333 | 206.730 | 428.927 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.996
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.996
- phase_score: 0.009
- phase_breakdown.insertion_score: 0.000
- phase_breakdown.pre_contact_score: 0.031

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.404
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.996
- **Median Q (composite search score)**: -0.049
- **K-run variance**: 0.0002
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.290


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":6.5283,"average_solve_count":53.0,"average_success_count":53.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.align_speed":0.10797,"align_1.align_tolerance":0.00649,"approach_1.approach_height":0.13671,"approach_1.approach_speed":0.25859,"approach_1.approach_tolerance":0.0243,"insert_1.insertion_depth":0.07922,"insert_1.insertion_force_guard_threshold":37.55914,"insert_1.insertion_speed":0.08731},"optimized_scores":{"best_composite_score":-0.04917,"best_fitness_score":0.38083,"best_task_score":0.93836},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":13.0,"contact_point_centroid":[0.51338,-0.01346,0.07791],"force_p95":1253.65202,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1303.62603,"mean_force":678.3529,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.4985,-0.01362,0.08316]},{"body_a":"peg_socket","body_b":"link7","contact_count":665.0,"contact_point_centroid":[0.54061,-0.01831,0.0798],"force_p95":367.96187,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1112.10778,"mean_force":321.48514,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.46984,-0.01844,0.13437]},{"body_a":"peg_socket","body_b":"link7","contact_count":4.0,"contact_point_centroid":[0.54076,-0.01536,0.07996],"force_p95":462.3359,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":541.81577,"mean_force":138.44143,"phase_index":2.0,"phase_name":"insert_1","phase_type":"push","tcp_position_centroid":[0.47733,-0.02855,0.14258]},{"body_a":"attachment","body_b":"peg_socket","contact_count":1.0,"contact_point_centroid":[0.45024,-0.01417,0.07963],"force_p95":0.0,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.44783,-0.0142,0.09407]}],"total_contact_groups":4},"final_pose_error":0.14223,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.48093,-0.01612,0.025],"final_tcp_position":[0.47763,-0.02811,0.14246],"realised_fixture_position":[0.48093,-0.01612,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.48093,-0.01612,0.08]},"peak_contact_force":1303.62603,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":108.0,"n_steps_budget":600.0,"object_pos_end":[0.49401,-0.01093,0.2788],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.19919,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"pre_contact","tcp_end":[0.48547,-0.01087,0.23972],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":752.0,"n_steps_budget":810.0,"object_pos_end":[0.51413,-0.0258,0.12756],"object_pos_start":[0.49401,-0.01093,0.2788],"object_to_goal_dist_end":0.05592,"object_to_goal_dist_start":0.19919,"object_z_max":0.2788,"peak_contact_force":360.17376,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":679.0,"raw_peak_contact_force":1303.62603,"tcp_end":[0.47718,-0.02872,0.14261],"tcp_start":[0.48547,-0.01087,0.23972],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":7.0,"n_steps_budget":1000.0,"object_pos_end":[0.51417,-0.02569,0.12725],"object_pos_start":[0.51413,-0.0258,0.12756],"object_to_goal_dist_end":0.05562,"object_to_goal_dist_start":0.05592,"object_z_max":0.12756,"peak_contact_force":0.0,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":4.0,"raw_peak_contact_force":541.81577,"subtask_id":"insertion","tcp_end":[0.47763,-0.02811,0.14246],"tcp_start":[0.47741,-0.02835,0.14256],"tcp_to_object_dist_end":0.03966,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `7c892e828ea48eee928c80191ad243a972830b09953cba6358be1d4656816d00`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":6.67213,"average_solve_count":61.0,"average_success_count":61.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.align_speed":0.04737,"align_1.align_tolerance":0.00469,"approach_1.approach_height":0.11187,"approach_1.approach_speed":0.24748,"approach_1.approach_tolerance":0.02968,"insert_1.insertion_depth":0.05381,"insert_1.insertion_force_guard_threshold":33.52447,"insert_1.insertion_speed":0.09418},"optimized_scores":{"best_composite_score":-0.06208,"best_fitness_score":0.36792,"best_task_score":0.91465},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link7","contact_count":889.0,"contact_point_centroid":[0.52664,-0.02082,0.06487],"force_p95":336.47795,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":11573.01881,"mean_force":448.59306,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.46049,-0.02412,0.11901]},{"body_a":"attachment","body_b":"peg_socket","contact_count":329.0,"contact_point_centroid":[0.52425,-0.02447,0.07951],"force_p95":1393.83644,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":9581.25377,"mean_force":459.47147,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.46431,-0.02794,0.11523]},{"body_a":"peg_socket","body_b":"link7","contact_count":13.0,"contact_point_centroid":[0.52641,-0.023,0.04888],"force_p95":3745.68829,"geom_a":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":3970.27276,"mean_force":1676.77306,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.44164,-0.02046,0.10328]},{"body_a":"peg_socket","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.52679,-0.01918,0.06463],"force_p95":310.79174,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":312.28658,"mean_force":286.76178,"phase_index":2.0,"phase_name":"insert_1","phase_type":"push","tcp_position_centroid":[0.46226,-0.03374,0.11941]},{"body_a":"attachment","body_b":"peg_socket","contact_count":2.0,"contact_point_centroid":[0.52685,-0.02789,0.08],"force_p95":213.23047,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":221.16675,"mean_force":141.80397,"phase_index":2.0,"phase_name":"insert_1","phase_type":"push","tcp_position_centroid":[0.46226,-0.03378,0.1194]},{"body_a":"world","body_b":"link6","contact_count":346.0,"contact_point_centroid":[0.67909,-0.01866,-2e-05],"force_p95":66.9104,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":184.54736,"mean_force":27.85704,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.46196,-0.02454,0.12039]},{"body_a":"world","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.67946,-0.0176,-0.0],"force_p95":151.176,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":151.176,"mean_force":151.176,"phase_index":2.0,"phase_name":"insert_1","phase_type":"push","tcp_position_centroid":[0.46226,-0.03366,0.11941]}],"total_contact_groups":7},"final_pose_error":0.0942,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.46685,-0.02106,0.025],"final_tcp_position":[0.46225,-0.03389,0.1194],"realised_fixture_position":[0.46685,-0.02106,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.46685,-0.02106,0.08]},"peak_contact_force":11573.01881,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":122.0,"n_steps_budget":600.0,"object_pos_end":[0.48537,-0.01504,0.2579],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.17913,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"pre_contact","tcp_end":[0.47502,-0.01491,0.21926],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49974,-0.03048,0.1058],"object_pos_start":[0.48537,-0.01504,0.2579],"object_to_goal_dist_end":0.03994,"object_to_goal_dist_start":0.17913,"object_z_max":0.2579,"peak_contact_force":0.36087,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":1577.0,"raw_peak_contact_force":11573.01881,"tcp_end":[0.46226,-0.03366,0.11941],"tcp_start":[0.47502,-0.01491,0.21926],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":3.0,"n_steps_budget":630.0,"object_pos_end":[0.49974,-0.03056,0.1058],"object_pos_start":[0.49974,-0.03048,0.1058],"object_to_goal_dist_end":0.03999,"object_to_goal_dist_start":0.03994,"object_z_max":0.1058,"peak_contact_force":250.6606,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":6.0,"raw_peak_contact_force":312.28658,"subtask_id":"insertion","tcp_end":[0.46225,-0.03389,0.1194],"tcp_start":[0.46225,-0.03382,0.1194],"tcp_to_object_dist_end":0.04002,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `65c1f23a0338c26bf257d85b07ab64c0180da795e8d67e7d51a2ed2fb2a4d0db`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":5.94915,"average_solve_count":59.0,"average_success_count":59.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.align_speed":0.0955,"align_1.align_tolerance":0.00838,"approach_1.approach_height":0.17852,"approach_1.approach_speed":0.2863,"approach_1.approach_tolerance":0.01586,"insert_1.insertion_depth":0.13067,"insert_1.insertion_force_guard_threshold":32.03817,"insert_1.insertion_speed":0.0507},"optimized_scores":{"best_composite_score":-0.02601,"best_fitness_score":0.40399,"best_task_score":0.99617},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link7","contact_count":659.0,"contact_point_centroid":[0.59518,-0.00526,0.07973],"force_p95":405.4286,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1201.76727,"mean_force":267.89087,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50967,0.00177,0.10883]},{"body_a":"attachment","body_b":"peg_socket","contact_count":5.0,"contact_point_centroid":[0.56624,0.00065,0.07917],"force_p95":1133.89092,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1166.79533,"mean_force":956.0501,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.54857,0.00058,0.08176]},{"body_a":"attachment","body_b":"peg_socket","contact_count":21.0,"contact_point_centroid":[0.50297,0.01418,0.07898],"force_p95":923.29866,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":967.00892,"mean_force":400.43987,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50127,7e-05,0.07669]},{"body_a":"peg_socket","body_b":"link6","contact_count":183.0,"contact_point_centroid":[0.5952,-0.05891,0.07984],"force_p95":432.13859,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":788.74487,"mean_force":191.70435,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.59668,-0.02201,0.24475]},{"body_a":"peg_socket","body_b":"link6","contact_count":2.0,"contact_point_centroid":[0.59544,-0.05907,0.07999],"force_p95":429.52249,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":432.67998,"mean_force":401.10514,"phase_index":2.0,"phase_name":"insert_1","phase_type":"push","tcp_position_centroid":[0.59205,-0.05779,0.25887]},{"body_a":"world","body_b":"link6","contact_count":151.0,"contact_point_centroid":[0.6554,-0.09174,-9e-05],"force_p95":260.29582,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":289.21148,"mean_force":198.39065,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.5976,-0.02601,0.24714]}],"total_contact_groups":6},"final_pose_error":0.32087,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.53544,0.00091,0.025],"final_tcp_position":[0.59248,-0.05869,0.25942],"realised_fixture_position":[0.53544,0.00091,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.53544,0.00091,0.08]},"peak_contact_force":1201.76727,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":114.0,"n_steps_budget":600.0,"object_pos_end":[0.52669,0.0006,0.30682],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.22838,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"pre_contact","tcp_end":[0.52245,0.00059,0.26704],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.60534,-0.06362,0.22151],"object_pos_start":[0.52669,0.0006,0.30682],"object_to_goal_dist_end":0.18753,"object_to_goal_dist_start":0.22838,"object_z_max":0.30682,"peak_contact_force":0.0,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":1019.0,"raw_peak_contact_force":1201.76727,"tcp_end":[0.59191,-0.05745,0.25868],"tcp_start":[0.52245,0.00059,0.26704],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.60541,-0.06388,0.2216],"object_pos_start":[0.60534,-0.06362,0.22151],"object_to_goal_dist_end":0.18773,"object_to_goal_dist_start":0.18753,"object_z_max":0.22182,"peak_contact_force":369.5303,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2.0,"raw_peak_contact_force":432.67998,"subtask_id":"insertion","tcp_end":[0.59248,-0.05869,0.25942],"tcp_start":[0.59219,-0.05813,0.25906],"tcp_to_object_dist_end":0.0403,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```