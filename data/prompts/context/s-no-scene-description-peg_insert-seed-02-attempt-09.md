## Search State

- **Seed**: 2
- **Iteration**: 10 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 9 | approach → align → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | pose_tolerance | force_exceeded | force_exceeded | 8 | 0.3063 | 0.92 | ❌ rejected |
| 8 | approach → align → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | time_limit | 8 | -0.0462 | 0.95 | ❌ rejected |
| 7 | approach → align → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 8 | -0.0458 | 0.95 | ✅ accepted |
| 6 | approach → align → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | 8 | 0.2873 | 0.95 | ✅ accepted |
| 5 | approach → push | linear_cartesian | linear_cartesian | position_control | impedance_control | pose_tolerance | force_exceeded | 6 | 1.1393 | 0.94 | ✅ accepted |

**Proposal policy**: task_score is near-perfect (0.92). Preserve useful working parts and make only evidence-backed refinements. A HOLD is acceptable if you genuinely cannot find a better structure.

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

## Current Skill (Q=0.306) — your mutation base

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

- **Composite score**: 0.306
- **task_score** (E): 0.916
- **fitness_score**: 0.403  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.333
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.430

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 0.00 | 0.0481 |
| align_1 | 1.00 | 1.00 | 0.1824 |
| insert_1 | 0.00 | 1.00 | 0.0015 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.491, -0.008, 0.258) | (0.504, -0.000, 0.340)→(0.499, -0.008, 0.297) | 0.260→0.218 | 0.00 / 0.000 | 0.000 | 0.000 |
| align_1 | align | 1.00 / force_exceeded | (0.491, -0.008, 0.258)→(0.491, -0.010, 0.076) | (0.499, -0.008, 0.297)→(0.524, -0.010, 0.098) | 0.218→0.035 | 1.00 / 1.000 | 1134.160 | 1134.160 |
| insert_1 | push | 0.00 / guard_failure | (0.487, -0.010, 0.073)→(0.486, -0.010, 0.072) | (0.524, -0.010, 0.098)→(0.522, -0.010, 0.096) | 0.035→0.032 | 1.00 / 1.333 | 1196.233 | 1433.641 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.921
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.921
- phase_score: 0.081
- phase_breakdown.insertion_score: 0.105
- phase_breakdown.pre_contact_score: 0.025

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.417
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.933
- **Median Q (composite search score)**: 0.306
- **K-run variance**: 0.0001
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.293


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":5.34483,"average_solve_count":29.0,"average_success_count":29.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.align_force_threshold":35.40514,"align_1.align_speed":0.05276,"approach_1.approach_height":0.1526,"approach_1.approach_speed":0.32972,"approach_1.approach_tolerance":0.02684,"insert_1.insertion_depth":0.1529,"insert_1.insertion_force_threshold":111.66315,"insert_1.insertion_speed":0.05584},"optimized_scores":{"best_composite_score":0.32021,"best_fitness_score":0.41688,"best_task_score":0.92084},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":1.0,"contact_point_centroid":[0.51113,-0.01136,0.07968],"force_p95":1099.56398,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1099.56398,"mean_force":1099.56398,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.479,-0.01168,0.07661]},{"body_a":"attachment","body_b":"peg_socket","contact_count":3.0,"contact_point_centroid":[0.51144,-0.01129,0.07912],"force_p95":900.38131,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":919.84968,"mean_force":740.3998,"phase_index":2.0,"phase_name":"insert_1","phase_type":"push","tcp_position_centroid":[0.47397,-0.01174,0.07354]}],"total_contact_groups":2},"final_pose_error":0.14555,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.48093,-0.01612,0.025],"final_tcp_position":[0.47032,-0.01179,0.0722],"realised_fixture_position":[0.48093,-0.01612,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.48093,-0.01612,0.08]},"peak_contact_force":1099.56398,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":75.0,"n_steps_budget":600.0,"object_pos_end":[0.49517,-0.00935,0.29686],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.21711,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"pre_contact","tcp_end":[0.48772,-0.0093,0.25756],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":73.0,"n_steps_budget":1000.0,"object_pos_end":[0.51037,-0.01122,0.09545],"object_pos_start":[0.49517,-0.00935,0.29686],"object_to_goal_dist_end":0.02173,"object_to_goal_dist_start":0.21711,"object_z_max":0.29686,"peak_contact_force":1099.56398,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":1.0,"raw_peak_contact_force":1099.56398,"tcp_end":[0.4762,-0.01171,0.07466],"tcp_start":[0.48772,-0.0093,0.25756],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.5084,-0.01122,0.09349],"object_pos_start":[0.51037,-0.01122,0.09545],"object_to_goal_dist_end":0.01945,"object_to_goal_dist_start":0.02173,"object_z_max":0.09545,"peak_contact_force":576.1837,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3.0,"raw_peak_contact_force":919.84968,"subtask_id":"insertion","tcp_end":[0.47032,-0.01179,0.0722],"tcp_start":[0.47189,-0.01178,0.07258],"tcp_to_object_dist_end":0.04363,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `7c892e828ea48eee928c80191ad243a972830b09953cba6358be1d4656816d00`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":11.10714,"average_solve_count":28.0,"average_success_count":28.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.align_force_threshold":28.64084,"align_1.align_speed":0.09793,"approach_1.approach_height":0.13228,"approach_1.approach_speed":0.2752,"approach_1.approach_tolerance":0.01771,"insert_1.insertion_depth":0.08683,"insert_1.insertion_force_threshold":106.44983,"insert_1.insertion_speed":0.05026},"optimized_scores":{"best_composite_score":0.29239,"best_fitness_score":0.38905,"best_task_score":0.89527},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":1.0,"contact_point_centroid":[0.50087,-0.01966,0.07845],"force_p95":1257.94572,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1257.94572,"mean_force":1257.94572,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49138,-0.01971,0.08851]},{"body_a":"attachment","body_b":"peg_socket","contact_count":3.0,"contact_point_centroid":[0.49884,-0.01946,0.07739],"force_p95":1017.64423,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1037.88188,"mean_force":847.57063,"phase_index":2.0,"phase_name":"insert_1","phase_type":"push","tcp_position_centroid":[0.48743,-0.01952,0.08347]}],"total_contact_groups":2},"final_pose_error":0.08914,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.46685,-0.02106,0.025],"final_tcp_position":[0.48425,-0.0192,0.08057],"realised_fixture_position":[0.46685,-0.02106,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.46685,-0.02106,0.08]},"peak_contact_force":1257.94572,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":165.0,"n_steps_budget":600.0,"object_pos_end":[0.4825,-0.01628,0.26701],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.18853,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"pre_contact","tcp_end":[0.47238,-0.01614,0.22831],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":63.0,"n_steps_budget":840.0,"object_pos_end":[0.52063,-0.01942,0.1103],"object_pos_start":[0.4825,-0.01628,0.26701],"object_to_goal_dist_end":0.04149,"object_to_goal_dist_start":0.18853,"object_z_max":0.26701,"peak_contact_force":1257.94572,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":1.0,"raw_peak_contact_force":1257.94572,"tcp_end":[0.48925,-0.01968,0.0855],"tcp_start":[0.47238,-0.01614,0.22831],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.51917,-0.01927,0.1075],"object_pos_start":[0.52063,-0.01942,0.1103],"object_to_goal_dist_end":0.03867,"object_to_goal_dist_start":0.04149,"object_z_max":0.1103,"peak_contact_force":669.32464,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3.0,"raw_peak_contact_force":1037.88188,"subtask_id":"insertion","tcp_end":[0.48425,-0.0192,0.08057],"tcp_start":[0.48569,-0.01934,0.08166],"tcp_to_object_dist_end":0.0441,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `65c1f23a0338c26bf257d85b07ab64c0180da795e8d67e7d51a2ed2fb2a4d0db`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":50.0,"average_failure_rate":0.64935,"average_mean_iterations":134.36364,"average_solve_count":77.0,"average_success_count":27.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.align_force_threshold":21.91432,"align_1.align_speed":0.11776,"approach_1.approach_height":0.19406,"approach_1.approach_speed":0.29494,"approach_1.approach_tolerance":0.02495,"insert_1.insertion_depth":0.13015,"insert_1.insertion_force_threshold":123.38649,"insert_1.insertion_speed":0.07586},"optimized_scores":{"best_composite_score":0.30643,"best_fitness_score":0.4031,"best_task_score":0.93292},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.59498,-0.00332,0.0788],"force_p95":2343.19135,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":2343.19135,"mean_force":2343.19135,"phase_index":2.0,"phase_name":"insert_1","phase_type":"push","tcp_position_centroid":[0.50336,0.00025,0.06394]},{"body_a":"attachment","body_b":"peg_socket","contact_count":3.0,"contact_point_centroid":[0.50177,0.00601,0.07759],"force_p95":1129.08449,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1164.30689,"mean_force":876.49551,"phase_index":2.0,"phase_name":"insert_1","phase_type":"push","tcp_position_centroid":[0.50515,0.00025,0.06529]},{"body_a":"attachment","body_b":"peg_socket","contact_count":1.0,"contact_point_centroid":[0.50431,0.00951,0.07922],"force_p95":1044.96888,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1044.96888,"mean_force":1044.96888,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50978,0.00026,0.0689]}],"total_contact_groups":3},"final_pose_error":0.1182,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.53544,0.00091,0.025],"final_tcp_position":[0.50254,-0.00014,0.06338],"realised_fixture_position":[0.53544,0.00091,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.53544,0.00091,0.08]},"peak_contact_force":2343.19135,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":45.0,"n_steps_budget":600.0,"object_pos_end":[0.51809,0.00039,0.32666],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.24732,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"pre_contact","tcp_end":[0.51429,0.00038,0.28684],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":81.0,"n_steps_budget":990.0,"object_pos_end":[0.54037,0.00032,0.08898],"object_pos_start":[0.51809,0.00039,0.32666],"object_to_goal_dist_end":0.04136,"object_to_goal_dist_start":0.24732,"object_z_max":0.32666,"peak_contact_force":1044.96888,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":1.0,"raw_peak_contact_force":1044.96888,"tcp_end":[0.50709,0.00025,0.06678],"tcp_start":[0.51429,0.00038,0.28684],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":3.0,"n_steps_budget":990.0,"object_pos_end":[0.53863,0.00032,0.08679],"object_pos_start":[0.54037,0.00032,0.08898],"object_to_goal_dist_end":0.03923,"object_to_goal_dist_start":0.04136,"object_z_max":0.08898,"peak_contact_force":2343.19135,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":4.0,"raw_peak_contact_force":2343.19135,"subtask_id":"insertion","tcp_end":[0.50254,-0.00014,0.06338],"tcp_start":[0.50336,0.00025,0.06394],"tcp_to_object_dist_end":0.04303,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```