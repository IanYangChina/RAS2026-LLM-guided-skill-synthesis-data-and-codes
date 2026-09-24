## Search State

- **Seed**: 2
- **Iteration**: 11 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 10 | approach → align → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.0057 | 0.94 | ❌ rejected |
| 9 | approach → align → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | pose_tolerance | force_exceeded | force_exceeded | 8 | 0.3063 | 0.92 | ❌ rejected |
| 8 | approach → align → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | time_limit | 8 | -0.0462 | 0.95 | ❌ rejected |
| 7 | approach → align → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 8 | -0.0458 | 0.95 | ✅ accepted |
| 6 | approach → align → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | 8 | 0.2873 | 0.95 | ✅ accepted |

**Proposal policy**: task_score is near-perfect (0.94). Preserve useful working parts and make only evidence-backed refinements. A HOLD is acceptable if you genuinely cannot find a better structure.

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

## Current Skill (Q=0.006) — your mutation base

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

- **Composite score**: 0.006
- **task_score** (E): 0.938
- **fitness_score**: 0.386  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.380

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 0.00 | 0.0586 |
| align_1 | 0.67 | 1.00 | 0.1259 |
| insert_1 | 0.00 | 1.00 | 0.1073 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.495, -0.008, 0.246) | (0.504, -0.000, 0.340)→(0.503, -0.008, 0.286) | 0.260→0.207 | 0.00 / 0.000 | 0.000 | 0.000 |
| align_1 | align | 0.67 / step_budget | (0.495, -0.008, 0.246)→(0.515, -0.054, 0.169) | (0.503, -0.008, 0.286)→(0.543, -0.052, 0.147) | 0.207→0.098 | 1.00 / 1.333 | 263.051 | 6030.044 |
| insert_1 | push | 0.00 / step_budget | (0.515, -0.054, 0.169)→(0.555, -0.051, 0.260) | (0.543, -0.052, 0.147)→(0.568, -0.051, 0.223) | 0.098→0.172 | 1.00 / 2.000 | 399.154 | 2237.394 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.965
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.965
- phase_score: 0.040
- phase_breakdown.insertion_score: 0.047
- phase_breakdown.pre_contact_score: 0.025

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.410
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.965
- **Median Q (composite search score)**: -0.001
- **K-run variance**: 0.0003
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.403


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":5.40698,"average_solve_count":86.0,"average_success_count":86.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.align_speed":0.12463,"align_1.align_tolerance":0.00959,"approach_1.approach_height":0.15036,"approach_1.approach_speed":0.19648,"approach_1.approach_tolerance":0.0299,"insert_1.insertion_depth":0.18749,"insert_1.insertion_speed":0.03375},"optimized_scores":{"best_composite_score":-0.00108,"best_fitness_score":0.37892,"best_task_score":0.93582},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":59.0,"contact_point_centroid":[0.53584,-0.01847,0.07991],"force_p95":3833.41865,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":4377.99715,"mean_force":599.52475,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.47247,-0.02219,0.11074]},{"body_a":"attachment","body_b":"peg_socket","contact_count":18.0,"contact_point_centroid":[0.44908,-0.00463,0.07959],"force_p95":2715.79568,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":2809.72298,"mean_force":776.72251,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.44687,-0.01183,0.08215]},{"body_a":"peg_socket","body_b":"link7","contact_count":158.0,"contact_point_centroid":[0.54075,-0.03259,0.07156],"force_p95":864.2154,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1422.00762,"mean_force":465.00408,"phase_index":2.0,"phase_name":"insert_1","phase_type":"push","tcp_position_centroid":[0.47721,-0.00302,0.11594]},{"body_a":"peg_socket","body_b":"link7","contact_count":642.0,"contact_point_centroid":[0.54052,-0.01185,0.0677],"force_p95":429.52711,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1289.21927,"mean_force":315.81346,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.4677,-0.01638,0.11152]},{"body_a":"attachment","body_b":"peg_socket","contact_count":43.0,"contact_point_centroid":[0.54092,-0.01652,0.07997],"force_p95":835.32228,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1276.70352,"mean_force":633.17494,"phase_index":2.0,"phase_name":"insert_1","phase_type":"push","tcp_position_centroid":[0.47529,-0.00425,0.1138]},{"body_a":"world","body_b":"link6","contact_count":431.0,"contact_point_centroid":[0.61249,-0.10558,-0.00014],"force_p95":490.48882,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1129.89548,"mean_force":328.66074,"phase_index":2.0,"phase_name":"insert_1","phase_type":"push","tcp_position_centroid":[0.54451,-0.06114,0.24829]},{"body_a":"peg_socket","body_b":"link6","contact_count":698.0,"contact_point_centroid":[0.54085,-0.07601,0.07998],"force_p95":431.31521,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":537.7643,"mean_force":270.29778,"phase_index":2.0,"phase_name":"insert_1","phase_type":"push","tcp_position_centroid":[0.54619,-0.06931,0.25932]}],"total_contact_groups":7},"final_pose_error":0.37197,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.48093,-0.01612,0.025],"final_tcp_position":[0.54491,-0.06349,0.25586],"realised_fixture_position":[0.48093,-0.01612,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.48093,-0.01612,0.08]},"peak_contact_force":4377.99715,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":69.0,"n_steps_budget":600.0,"object_pos_end":[0.49568,-0.00903,0.29706],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.21729,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"pre_contact","tcp_end":[0.48828,-0.00899,0.25775],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":725.0,"n_steps_budget":810.0,"object_pos_end":[0.51264,-0.02247,0.10524],"object_pos_start":[0.49568,-0.00903,0.29706],"object_to_goal_dist_end":0.03608,"object_to_goal_dist_start":0.21729,"object_z_max":0.29706,"peak_contact_force":297.0108,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":719.0,"raw_peak_contact_force":4377.99715,"tcp_end":[0.47476,-0.02509,0.1178],"tcp_start":[0.48828,-0.00899,0.25775],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.56007,-0.06887,0.21923],"object_pos_start":[0.51264,-0.02247,0.10524],"object_to_goal_dist_end":0.16655,"object_to_goal_dist_start":0.03608,"object_z_max":0.22643,"peak_contact_force":462.66757,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1330.0,"raw_peak_contact_force":1422.00762,"subtask_id":"insertion","tcp_end":[0.54491,-0.06349,0.25586],"tcp_start":[0.47476,-0.02509,0.1178],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `7c892e828ea48eee928c80191ad243a972830b09953cba6358be1d4656816d00`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":5.97872,"average_solve_count":94.0,"average_success_count":94.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.align_speed":0.07844,"align_1.align_tolerance":0.00854,"approach_1.approach_height":0.11679,"approach_1.approach_speed":0.32705,"approach_1.approach_tolerance":0.0296,"insert_1.insertion_depth":0.15037,"insert_1.insertion_speed":0.03132},"optimized_scores":{"best_composite_score":-0.01214,"best_fitness_score":0.36786,"best_task_score":0.91401},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link7","contact_count":750.0,"contact_point_centroid":[0.52661,-0.02195,0.06629],"force_p95":352.54788,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":12126.09907,"mean_force":499.71857,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.46084,-0.02454,0.12095]},{"body_a":"attachment","body_b":"peg_socket","contact_count":48.0,"contact_point_centroid":[0.50898,-0.01955,0.07681],"force_p95":8649.73014,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":9962.11628,"mean_force":2638.59652,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.47837,-0.01977,0.091]},{"body_a":"world","body_b":"link5","contact_count":555.0,"contact_point_centroid":[0.5162,0.09464,-5e-05],"force_p95":638.29398,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":4613.79257,"mean_force":354.92422,"phase_index":2.0,"phase_name":"insert_1","phase_type":"push","tcp_position_centroid":[0.51952,-0.00423,0.25335]},{"body_a":"peg_socket","body_b":"link7","contact_count":13.0,"contact_point_centroid":[0.52636,-0.02308,0.04857],"force_p95":3796.94281,"geom_a":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":4047.47087,"mean_force":1876.64253,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.44198,-0.02063,0.10444]},{"body_a":"peg_socket","body_b":"link5","contact_count":585.0,"contact_point_centroid":[0.5012,0.03875,0.05282],"force_p95":517.93283,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":2704.33532,"mean_force":305.28501,"phase_index":2.0,"phase_name":"insert_1","phase_type":"push","tcp_position_centroid":[0.51998,-0.00633,0.25231]},{"body_a":"peg_socket","body_b":"link5","contact_count":255.0,"contact_point_centroid":[0.50276,0.03862,0.04998],"force_p95":751.85985,"geom_a":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1866.85124,"mean_force":189.37437,"phase_index":2.0,"phase_name":"insert_1","phase_type":"push","tcp_position_centroid":[0.52208,-0.01161,0.24963]},{"body_a":"peg_socket","body_b":"link7","contact_count":351.0,"contact_point_centroid":[0.5267,-0.02105,0.06964],"force_p95":739.73636,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":970.45366,"mean_force":439.71601,"phase_index":2.0,"phase_name":"insert_1","phase_type":"push","tcp_position_centroid":[0.46253,-0.05206,0.11628]},{"body_a":"world","body_b":"link6","contact_count":290.0,"contact_point_centroid":[0.67837,-0.01947,-5e-05],"force_p95":384.16955,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":863.72992,"mean_force":90.31287,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.46265,-0.02628,0.12272]},{"body_a":"attachment","body_b":"peg_socket","contact_count":244.0,"contact_point_centroid":[0.52684,-0.03917,0.07997],"force_p95":695.46814,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":850.85731,"mean_force":376.72185,"phase_index":2.0,"phase_name":"insert_1","phase_type":"push","tcp_position_centroid":[0.46217,-0.05333,0.1154]},{"body_a":"world","body_b":"link6","contact_count":54.0,"contact_point_centroid":[0.66223,0.01642,-0.00047],"force_p95":414.81386,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":482.04688,"mean_force":240.24963,"phase_index":2.0,"phase_name":"insert_1","phase_type":"push","tcp_position_centroid":[0.49441,-0.06799,0.15824]},{"body_a":"peg_socket","body_b":"link5","contact_count":36.0,"contact_point_centroid":[0.4966,0.03836,0.06325],"force_p95":338.33259,"geom_a":"socket_collar_y1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":387.17961,"mean_force":162.65588,"phase_index":2.0,"phase_name":"insert_1","phase_type":"push","tcp_position_centroid":[0.53024,-0.0392,0.23558]}],"total_contact_groups":11},"final_pose_error":0.32927,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.46685,-0.02106,0.025],"final_tcp_position":[0.51831,-0.00245,0.25432],"realised_fixture_position":[0.46685,-0.02106,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.46685,-0.02106,0.08]},"peak_contact_force":12126.09907,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":117.0,"n_steps_budget":600.0,"object_pos_end":[0.48548,-0.01483,0.2625],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.18367,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"pre_contact","tcp_end":[0.47537,-0.01471,0.22379],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":876.0,"n_steps_budget":990.0,"object_pos_end":[0.50094,-0.03284,0.10859],"object_pos_start":[0.48548,-0.01483,0.2625],"object_to_goal_dist_end":0.04355,"object_to_goal_dist_start":0.18367,"object_z_max":0.2625,"peak_contact_force":194.28503,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":1101.0,"raw_peak_contact_force":12126.09907,"tcp_end":[0.46371,-0.03632,0.12279],"tcp_start":[0.47537,-0.01471,0.22379],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53789,0.00401,0.22005],"object_pos_start":[0.50094,-0.03284,0.10859],"object_to_goal_dist_end":0.14514,"object_to_goal_dist_start":0.04355,"object_z_max":0.22034,"peak_contact_force":188.48943,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2080.0,"raw_peak_contact_force":4613.79257,"subtask_id":"insertion","tcp_end":[0.51831,-0.00245,0.25432],"tcp_start":[0.46371,-0.03632,0.12279],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `65c1f23a0338c26bf257d85b07ab64c0180da795e8d67e7d51a2ed2fb2a4d0db`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":5.41489,"average_solve_count":94.0,"average_success_count":94.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.align_speed":0.0878,"align_1.align_tolerance":0.00554,"approach_1.approach_height":0.16437,"approach_1.approach_speed":0.29975,"approach_1.approach_tolerance":0.01861,"insert_1.insertion_depth":0.12891,"insert_1.insertion_speed":0.03686},"optimized_scores":{"best_composite_score":0.03018,"best_fitness_score":0.41018,"best_task_score":0.96502},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link7","contact_count":233.0,"contact_point_centroid":[0.59404,0.00387,0.07947],"force_p95":1008.01275,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1586.0372,"mean_force":377.47651,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.48897,0.00464,0.15894]},{"body_a":"peg_socket","body_b":"link6","contact_count":654.0,"contact_point_centroid":[0.59532,-0.01907,0.07791],"force_p95":564.90926,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1489.43397,"mean_force":295.89031,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.51522,-0.01943,0.19948]},{"body_a":"attachment","body_b":"peg_socket","contact_count":16.0,"contact_point_centroid":[0.56963,0.0008,0.07685],"force_p95":1321.05351,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1361.83945,"mean_force":613.84894,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.55503,0.00077,0.07955]},{"body_a":"attachment","body_b":"peg_socket","contact_count":9.0,"contact_point_centroid":[0.49794,0.00301,0.07847],"force_p95":881.63403,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":889.23767,"mean_force":195.49625,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49416,0.00046,0.09025]},{"body_a":"world","body_b":"link6","contact_count":134.0,"contact_point_centroid":[0.64185,-0.10698,-0.00016],"force_p95":526.81174,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":726.0707,"mean_force":225.47219,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.60342,-0.10169,0.26666]},{"body_a":"world","body_b":"link6","contact_count":967.0,"contact_point_centroid":[0.60122,-0.10292,-7e-05],"force_p95":583.71462,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":676.38292,"mean_force":400.08564,"phase_index":2.0,"phase_name":"insert_1","phase_type":"push","tcp_position_centroid":[0.59962,-0.09499,0.26937]},{"body_a":"peg_socket","body_b":"link6","contact_count":597.0,"contact_point_centroid":[0.59544,-0.05907,0.08],"force_p95":242.40692,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":489.94221,"mean_force":161.61759,"phase_index":2.0,"phase_name":"insert_1","phase_type":"push","tcp_position_centroid":[0.59925,-0.09688,0.26948]},{"body_a":"peg_socket","body_b":"link6","contact_count":7.0,"contact_point_centroid":[0.59544,-0.05907,0.04999],"force_p95":159.08682,"geom_a":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":160.32579,"mean_force":147.38151,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.60237,-0.10328,0.26623]}],"total_contact_groups":8},"final_pose_error":0.33579,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.53544,0.00091,0.025],"final_tcp_position":[0.60067,-0.08606,0.26879],"realised_fixture_position":[0.53544,0.00091,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.53544,0.00091,0.08]},"peak_contact_force":1586.0372,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":113.0,"n_steps_budget":600.0,"object_pos_end":[0.52725,0.0006,0.29718],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.21888,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"pre_contact","tcp_end":[0.52251,0.00059,0.25746],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.61632,-0.10044,0.22863],"object_pos_start":[0.52725,0.0006,0.29718],"object_to_goal_dist_end":0.2138,"object_to_goal_dist_start":0.21888,"object_z_max":0.29718,"peak_contact_force":297.85682,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":1053.0,"raw_peak_contact_force":1586.0372,"tcp_end":[0.60708,-0.10049,0.26754],"tcp_start":[0.52251,0.00059,0.25746],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.60649,-0.0889,0.22932],"object_pos_start":[0.61632,-0.10044,0.22863],"object_to_goal_dist_end":0.20382,"object_to_goal_dist_start":0.2138,"object_z_max":0.23022,"peak_contact_force":546.30439,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1564.0,"raw_peak_contact_force":676.38292,"subtask_id":"insertion","tcp_end":[0.60067,-0.08606,0.26879],"tcp_start":[0.60708,-0.10049,0.26754],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```