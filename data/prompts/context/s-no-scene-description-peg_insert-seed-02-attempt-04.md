## Search State

- **Seed**: 2
- **Iteration**: 5 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 4 | approach → push | linear_cartesian | linear_cartesian | position_control | impedance_control | pose_tolerance | force_exceeded | 6 | 1.1291 | 0.93 | ✅ accepted |
| 3 | approach → push | linear_cartesian | linear_cartesian | position_control | impedance_control | pose_tolerance | force_exceeded | 10 | -0.5000 | 0.00 | ❌ rejected |
| 2 | approach → push | linear_cartesian | linear_cartesian | position_control | impedance_control | pose_tolerance | force_exceeded | 8 | 0.8506 | 0.92 | ✅ accepted |
| 1 | approach → push | linear_cartesian | linear_cartesian | position_control | impedance_control | pose_tolerance | force_exceeded | 6 | 1.1003 | 0.90 | ✅ accepted |
| 0 | align → align → pull | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 0 | 0.0712 | 0.10 | ✅ accepted |

**Proposal policy**: task_score is near-perfect (0.93). Preserve useful working parts and make only evidence-backed refinements. A HOLD is acceptable if you genuinely cannot find a better structure.

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

## Current Skill (Q=1.129) — your mutation base

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
      default: 0.08
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
- **insert_1** (`push`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.1, mode=add_to_offset, sign=negative}
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=world_z, tolerance=0.1
  - parameter_bindings:
    - insertion_depth: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - insertion_force_threshold: status=consumed; consumers=termination.force_threshold (replace)
    - insertion_speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=2, strategy=offset_target, offset=[0.005, 0.005, 0.0]

## Design Metrics

- **Composite score**: 1.129
- **task_score** (E): 0.929
- **fitness_score**: 0.929  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.500
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.300

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 0.00 | 0.0539 |
| insert_1 | 1.00 | 1.00 | 0.1729 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.493, -0.008, 0.252) | (0.504, -0.000, 0.340)→(0.500, -0.008, 0.291) | 0.260→0.212 | 0.00 / 0.000 | 0.000 | 0.000 |
| insert_1 | push | 1.00 / force_exceeded | (0.493, -0.008, 0.252)→(0.502, -0.010, 0.080) | (0.500, -0.008, 0.291)→(0.533, -0.010, 0.105) | 0.212→0.045 | 1.00 / 1.000 | 1220.516 | 1220.516 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.941
- alignment_error: None
- force_efficiency: 0.000

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.941
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.941
- **Median Q (composite search score)**: 1.138
- **K-run variance**: 0.0002
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.335


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.76,"average_solve_count":25.0,"average_success_count":25.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.14106,"approach_1.approach_speed":0.36076,"approach_1.approach_tolerance":0.02885,"insert_1.insertion_depth":0.11193,"insert_1.insertion_force_threshold":21.4732,"insert_1.insertion_speed":0.10548},"optimized_scores":{"best_composite_score":1.13818,"best_fitness_score":0.93818,"best_task_score":0.93818},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":1.0,"contact_point_centroid":[0.5122,-0.01201,0.07875],"force_p95":1258.85939,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1258.85939,"mean_force":1258.85939,"phase_index":1.0,"phase_name":"insert_1","phase_type":"push","tcp_position_centroid":[0.50255,-0.01218,0.08899]}],"total_contact_groups":1},"final_pose_error":0.1197,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.48093,-0.01612,0.025],"final_tcp_position":[0.50042,-0.01218,0.08611],"realised_fixture_position":[0.48093,-0.01612,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.48093,-0.01612,0.08]},"peak_contact_force":1258.85939,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":84.0,"n_steps_budget":600.0,"object_pos_end":[0.49505,-0.00994,0.28702],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.20732,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"pre_contact","tcp_end":[0.48704,-0.00989,0.24783],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":65.0,"n_steps_budget":1000.0,"object_pos_end":[0.53145,-0.01167,0.11135],"object_pos_start":[0.49505,-0.00994,0.28702],"object_to_goal_dist_end":0.04591,"object_to_goal_dist_start":0.20732,"object_z_max":0.28702,"peak_contact_force":1258.85939,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1.0,"raw_peak_contact_force":1258.85939,"subtask_id":"insertion","tcp_end":[0.50042,-0.01218,0.08611],"tcp_start":[0.48704,-0.00989,0.24783],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `7c892e828ea48eee928c80191ad243a972830b09953cba6358be1d4656816d00`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.76,"average_solve_count":25.0,"average_success_count":25.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.12085,"approach_1.approach_speed":0.22854,"approach_1.approach_tolerance":0.02334,"insert_1.insertion_depth":0.08831,"insert_1.insertion_force_threshold":28.57854,"insert_1.insertion_speed":0.06846},"optimized_scores":{"best_composite_score":1.10822,"best_fitness_score":0.90822,"best_task_score":0.90822},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":1.0,"contact_point_centroid":[0.50921,-0.01926,0.07863],"force_p95":1370.01782,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1370.01782,"mean_force":1370.01782,"phase_index":1.0,"phase_name":"insert_1","phase_type":"push","tcp_position_centroid":[0.49922,-0.01937,0.08846]}],"total_contact_groups":1},"final_pose_error":0.09842,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.46685,-0.02106,0.025],"final_tcp_position":[0.49727,-0.01934,0.08528],"realised_fixture_position":[0.46685,-0.02106,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.46685,-0.02106,0.08]},"peak_contact_force":1370.01782,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":143.0,"n_steps_budget":600.0,"object_pos_end":[0.48384,-0.01573,0.26086],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.18226,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"pre_contact","tcp_end":[0.47352,-0.0156,0.22221],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":60.0,"n_steps_budget":1000.0,"object_pos_end":[0.52752,-0.01901,0.11145],"object_pos_start":[0.48384,-0.01573,0.26086],"object_to_goal_dist_end":0.04591,"object_to_goal_dist_start":0.18226,"object_z_max":0.26086,"peak_contact_force":1370.01782,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1.0,"raw_peak_contact_force":1370.01782,"subtask_id":"insertion","tcp_end":[0.49727,-0.01934,0.08528],"tcp_start":[0.47352,-0.0156,0.22221],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `65c1f23a0338c26bf257d85b07ab64c0180da795e8d67e7d51a2ed2fb2a4d0db`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.0,"average_solve_count":25.0,"average_success_count":25.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.19987,"approach_1.approach_speed":0.46047,"approach_1.approach_tolerance":0.01922,"insert_1.insertion_depth":0.11945,"insert_1.insertion_force_threshold":16.89215,"insert_1.insertion_speed":0.02814},"optimized_scores":{"best_composite_score":1.14102,"best_fitness_score":0.94102,"best_task_score":0.94102},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":1.0,"contact_point_centroid":[0.50488,0.01157,0.07962],"force_p95":1032.66989,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1032.66989,"mean_force":1032.66989,"phase_index":1.0,"phase_name":"insert_1","phase_type":"push","tcp_position_centroid":[0.50981,0.00029,0.07119]}],"total_contact_groups":1},"final_pose_error":0.11219,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.53544,0.00091,0.025],"final_tcp_position":[0.50707,0.00028,0.06909],"realised_fixture_position":[0.53544,0.00091,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.53544,0.00091,0.08]},"peak_contact_force":1032.66989,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":62.0,"n_steps_budget":600.0,"object_pos_end":[0.52095,0.00047,0.32612],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.24701,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"pre_contact","tcp_end":[0.51735,0.00046,0.28628],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":82.0,"n_steps_budget":1000.0,"object_pos_end":[0.54054,0.00036,0.091],"object_pos_start":[0.52095,0.00047,0.32612],"object_to_goal_dist_end":0.04201,"object_to_goal_dist_start":0.24701,"object_z_max":0.32612,"peak_contact_force":1032.66989,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1.0,"raw_peak_contact_force":1032.66989,"subtask_id":"insertion","tcp_end":[0.50707,0.00028,0.06909],"tcp_start":[0.51735,0.00046,0.28628],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":false}]}
```