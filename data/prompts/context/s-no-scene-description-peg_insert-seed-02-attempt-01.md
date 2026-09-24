## Search State

- **Seed**: 2
- **Iteration**: 2 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 1 | approach → push | linear_cartesian | linear_cartesian | position_control | impedance_control | pose_tolerance | force_exceeded | 6 | 1.1003 | 0.90 | ✅ accepted |
| 0 | align → align → pull | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 0 | 0.0712 | 0.10 | ✅ accepted |

**Proposal policy**: task_score is near-perfect (0.90). Preserve useful working parts and make only evidence-backed refinements. A HOLD is acceptable if you genuinely cannot find a better structure.

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

## Current Skill (Q=1.100) — your mutation base

```yaml
skill: peg_insert
dsl_version: 2
subtasks:
- id: pre_contact
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
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: world_z
      tolerance: 0.1
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
      - 0.05
      - 0.25
      default: 0.1
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    insertion_force_threshold:
      type: scalar
      range:
      - 5.0
      - 30.0
      default: 15.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    insertion_speed:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: contact_guard
    when: during_phase
    predicate: contact_detected
    threshold: 1.0
    on_failure: continue
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - 0.0
  subtask_id: insertion

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.1]
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=world_z, tolerance=0.1
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
  - guards:
    - id=contact_guard, when=during_phase, predicate=contact_detected, on_failure=continue, threshold=1.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, 0.0]

## Design Metrics

- **Composite score**: 1.100
- **task_score** (E): 0.900
- **fitness_score**: 0.900  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.500
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.300

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 0.67 | 1.00 | 0.1866 |
| insert_1 | 1.00 | 1.00 | 0.0003 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 0.67 / step_budget | (0.500, -0.000, 0.301)→(0.472, -0.005, 0.116) | (0.504, -0.000, 0.340)→(0.511, -0.005, 0.110) | 0.260→0.034 | 1.00 / 2.000 | 326.651 | 6508.973 |
| insert_1 | push | 1.00 / force_exceeded | (0.472, -0.005, 0.116)→(0.472, -0.005, 0.117) | (0.511, -0.005, 0.110)→(0.511, -0.005, 0.110) | 0.034→0.034 | 1.00 / 1.333 | 169.425 | 170.445 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.951
- alignment_error: None
- force_efficiency: 0.000

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.951
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.951
- **Median Q (composite search score)**: 1.086
- **K-run variance**: 0.0014
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Parameters at upper bound**: approach_1.approach_tolerance
- **Final σ (mean)**: 0.436


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":8.13636,"average_solve_count":22.0,"average_success_count":22.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.05319,"approach_1.approach_speed":0.17559,"approach_1.approach_tolerance":0.02589,"insert_1.insertion_depth":0.11697,"insert_1.insertion_force_threshold":9.43743,"insert_1.insertion_speed":0.24195},"optimized_scores":{"best_composite_score":1.08606,"best_fitness_score":0.88606,"best_task_score":0.88606},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":54.0,"contact_point_centroid":[0.52664,-0.00526,0.07917],"force_p95":12377.78671,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":13617.34131,"mean_force":4121.98472,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.45826,-0.00505,0.09426]},{"body_a":"peg_socket","body_b":"link7","contact_count":422.0,"contact_point_centroid":[0.5404,-0.00905,0.06741],"force_p95":3099.71029,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":8492.36253,"mean_force":629.105,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.46601,-0.00444,0.10802]},{"body_a":"attachment","body_b":"peg_socket","contact_count":20.0,"contact_point_centroid":[0.44915,-0.00037,0.0796],"force_p95":4922.96082,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":4967.92014,"mean_force":3662.77842,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.44791,-0.00389,0.07735]},{"body_a":"attachment","body_b":"peg_socket","contact_count":1.0,"contact_point_centroid":[0.54092,-0.00658,0.07995],"force_p95":116.23681,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":116.23681,"mean_force":116.23681,"phase_index":1.0,"phase_name":"insert_1","phase_type":"push","tcp_position_centroid":[0.46741,-0.00617,0.10873]},{"body_a":"peg_socket","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.54081,-0.01041,0.0642],"force_p95":112.1782,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":112.1782,"mean_force":112.1782,"phase_index":1.0,"phase_name":"insert_1","phase_type":"push","tcp_position_centroid":[0.46741,-0.00617,0.10873]}],"total_contact_groups":5},"final_pose_error":0.14674,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.48093,-0.01612,0.025],"final_tcp_position":[0.46742,-0.00625,0.10881],"realised_fixture_position":[0.48093,-0.01612,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.48093,-0.01612,0.08]},"peak_contact_force":13617.34131,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":514.0,"n_steps_budget":630.0,"object_pos_end":[0.50674,-0.00638,0.10147],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.02339,"object_to_goal_dist_start":0.26034,"object_z_max":0.34478,"peak_contact_force":316.88527,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":496.0,"raw_peak_contact_force":13617.34131,"subtask_id":"pre_contact","tcp_end":[0.46741,-0.00617,0.10873],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.50675,-0.00647,0.10152],"object_pos_start":[0.50674,-0.00638,0.10147],"object_to_goal_dist_end":0.02347,"object_to_goal_dist_start":0.02339,"object_z_max":0.10147,"peak_contact_force":116.23681,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2.0,"raw_peak_contact_force":116.23681,"subtask_id":"insertion","tcp_end":[0.46742,-0.00625,0.10881],"tcp_start":[0.46741,-0.00617,0.10873],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `7c892e828ea48eee928c80191ad243a972830b09953cba6358be1d4656816d00`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":8.09091,"average_solve_count":22.0,"average_success_count":22.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.08228,"approach_1.approach_speed":0.37104,"approach_1.approach_tolerance":0.0294,"insert_1.insertion_depth":0.18061,"insert_1.insertion_force_threshold":10.4623,"insert_1.insertion_speed":0.27645},"optimized_scores":{"best_composite_score":1.06336,"best_fitness_score":0.86336,"best_task_score":0.86336},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link7","contact_count":390.0,"contact_point_centroid":[0.52654,-0.0137,0.06545],"force_p95":659.94478,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":4742.83261,"mean_force":455.5266,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.45623,-0.00868,0.11208]},{"body_a":"attachment","body_b":"peg_socket","contact_count":253.0,"contact_point_centroid":[0.52426,-0.0093,0.0799],"force_p95":1833.19923,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":4205.23228,"mean_force":322.8796,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.45743,-0.00869,0.1134]},{"body_a":"attachment","body_b":"peg_socket","contact_count":2.0,"contact_point_centroid":[0.45753,0.00909,0.07996],"force_p95":485.49126,"geom_a":"peg_tip","geom_b":"socket_collar_y1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":485.68998,"mean_force":483.70274,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.45609,-0.00523,0.08346]},{"body_a":"world","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.67952,-0.01247,-0.0],"force_p95":331.63207,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":331.63207,"mean_force":331.63207,"phase_index":1.0,"phase_name":"insert_1","phase_type":"push","tcp_position_centroid":[0.46179,-0.00893,0.11949]},{"body_a":"peg_socket","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.52678,-0.01399,0.06352],"force_p95":320.6149,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":328.57408,"mean_force":248.98226,"phase_index":1.0,"phase_name":"insert_1","phase_type":"push","tcp_position_centroid":[0.4618,-0.00893,0.11949]},{"body_a":"world","body_b":"link6","contact_count":47.0,"contact_point_centroid":[0.67939,-0.01078,-8e-05],"force_p95":200.89639,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":226.38122,"mean_force":61.2547,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.46178,-0.00909,0.11959]},{"body_a":"attachment","body_b":"peg_socket","contact_count":1.0,"contact_point_centroid":[0.52685,-0.01044,0.07999],"force_p95":144.1877,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":144.1877,"mean_force":144.1877,"phase_index":1.0,"phase_name":"insert_1","phase_type":"push","tcp_position_centroid":[0.46179,-0.00893,0.11949]}],"total_contact_groups":7},"final_pose_error":0.22051,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.46685,-0.02106,0.025],"final_tcp_position":[0.46181,-0.00888,0.1195],"realised_fixture_position":[0.46685,-0.02106,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.46685,-0.02106,0.08]},"peak_contact_force":4742.83261,"phases":[{"contact_detected":true,"contact_event_count":3.0,"n_steps":484.0,"n_steps_budget":600.0,"object_pos_end":[0.4994,-0.00977,0.10587],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.02766,"object_to_goal_dist_start":0.26034,"object_z_max":0.34446,"peak_contact_force":281.25802,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":692.0,"raw_peak_contact_force":4742.83261,"subtask_id":"pre_contact","tcp_end":[0.46179,-0.00893,0.11949],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":2.0,"n_steps_budget":600.0,"object_pos_end":[0.49942,-0.00972,0.1059],"object_pos_start":[0.4994,-0.00977,0.10587],"object_to_goal_dist_end":0.02767,"object_to_goal_dist_start":0.02766,"object_z_max":0.10589,"peak_contact_force":328.57408,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":4.0,"raw_peak_contact_force":331.63207,"subtask_id":"insertion","tcp_end":[0.46181,-0.00888,0.1195],"tcp_start":[0.46179,-0.00893,0.11949],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `65c1f23a0338c26bf257d85b07ab64c0180da795e8d67e7d51a2ed2fb2a4d0db`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":8.33333,"average_solve_count":21.0,"average_success_count":21.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.18915,"approach_1.approach_speed":0.31542,"approach_1.approach_tolerance":0.03,"insert_1.insertion_depth":0.10957,"insert_1.insertion_force_threshold":16.56704,"insert_1.insertion_speed":0.27864},"optimized_scores":{"best_composite_score":1.15145,"best_fitness_score":0.95145,"best_task_score":0.95145},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":17.0,"contact_point_centroid":[0.49428,0.00057,0.07749],"force_p95":1119.76484,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1166.74445,"mean_force":192.11902,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4895,0.00056,0.08918]},{"body_a":"peg_socket","body_b":"link7","contact_count":41.0,"contact_point_centroid":[0.58515,-0.00277,0.07818],"force_p95":679.42291,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":849.59531,"mean_force":333.63011,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48833,0.00052,0.10132]},{"body_a":"peg_socket","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.5782,-0.00271,0.07995],"force_p95":63.46461,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":63.46461,"mean_force":63.46461,"phase_index":1.0,"phase_name":"insert_1","phase_type":"push","tcp_position_centroid":[0.48661,0.00058,0.12104]}],"total_contact_groups":3},"final_pose_error":0.15906,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.53544,0.00091,0.025],"final_tcp_position":[0.48644,0.00059,0.12176],"realised_fixture_position":[0.53544,0.00091,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.53544,0.00091,0.08]},"peak_contact_force":1166.74445,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":137.0,"n_steps_budget":600.0,"object_pos_end":[0.52659,0.00061,0.12223],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.04991,"object_to_goal_dist_start":0.26034,"object_z_max":0.3467,"peak_contact_force":381.81026,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":58.0,"raw_peak_contact_force":1166.74445,"subtask_id":"pre_contact","tcp_end":[0.48661,0.00058,0.12104],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.52643,0.00061,0.12268],"object_pos_start":[0.52659,0.00061,0.12223],"object_to_goal_dist_end":0.0502,"object_to_goal_dist_start":0.04991,"object_z_max":0.12223,"peak_contact_force":63.46461,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1.0,"raw_peak_contact_force":63.46461,"subtask_id":"insertion","tcp_end":[0.48644,0.00059,0.12176],"tcp_start":[0.48661,0.00058,0.12104],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":false}]}
```