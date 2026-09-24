## Search State

- **Seed**: 0
- **Iteration**: 7 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 6 | approach → insert | arc_cartesian | linear_cartesian | position_control | admittance_control | pose_tolerance | pose_tolerance | 5 | 0.1530 | 0.82 | ❌ rejected |
| 5 | approach → descend → insert | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | pose_tolerance | force_exceeded | pose_tolerance | 5 | 0.7240 | 0.88 | ❌ rejected |
| 4 | approach → descend → insert | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | pose_tolerance | force_exceeded | pose_tolerance | 5 | 0.7240 | 0.88 | ✅ accepted |
| 3 | approach → align → descend → insert | linear_cartesian | arc_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | admittance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 7 | 0.1414 | 0.84 | ❌ rejected |
| 2 | approach → descend → insert | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | pose_tolerance | force_exceeded | pose_tolerance | 5 | 0.7244 | 0.88 | ✅ accepted |

**Proposal policy**: task_score is 0.82 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.153) — your mutation base

```yaml
skill: peg_insert
dsl_version: 2
subtasks:
- id: approach_hole
  offset:
  - 0.0
  - 0.0
  - 0.12
  weight: 0.3
- id: insert_peg
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
    - 0.12
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: world_z
      tolerance: 0.1
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: approach_hole
- id: descend_1
  type: descend
  generator: linear_cartesian
  control: force_threshold_switch
  termination: force_exceeded
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
      tolerance: 0.1
  parameters:
    contact_force_threshold:
      type: scalar
      range:
      - 2.0
      - 20.0
      default: 5.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
  subtask_id: approach_hole
- id: insert_1
  type: insert
  generator: linear_cartesian
  control: admittance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.08
      axis: channel_axis
      mode: add_to_offset
      sign: positive
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: channel_axis
      tolerance: 0.05
  parameters:
    insert_depth:
      type: scalar
      range:
      - 0.03
      - 0.15
      default: 0.08
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    insert_speed:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
    pose_tolerance:
      type: scalar
      range:
      - 0.005
      - 0.02
      default: 0.01
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  subtask_id: insert_peg

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.12]
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=world_z, tolerance=0.1
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.02]
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=world_z, tolerance=0.1
  - parameter_bindings:
    - contact_force_threshold: status=consumed; consumers=termination.force_threshold (replace)
- **insert_1** (`insert`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.08, mode=add_to_offset, sign=positive}
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=channel_axis, tolerance=0.05
  - parameter_bindings:
    - insert_depth: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - insert_speed: status=consumed; consumers=generator.speed (replace)
    - pose_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)

## Design Metrics

- **Composite score**: 0.153
- **task_score** (E): 0.819
- **fitness_score**: 0.403  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.250

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 0.00 | 1.00 | 0.1496 |
| insert_1 | 0.00 | 1.00 | 0.0004 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 0.00 / step_budget | (0.500, -0.000, 0.301)→(0.443, -0.002, 0.163) | (0.504, -0.000, 0.340)→(0.481, -0.002, 0.151) | 0.260→0.075 | 1.00 / 2.000 | 281.718 | 1058.390 |
| insert_1 | insert | 0.00 / guard_failure | (0.443, -0.002, 0.163)→(0.443, -0.002, 0.162) | (0.481, -0.002, 0.151)→(0.481, -0.002, 0.151) | 0.075→0.075 | 1.00 / 2.000 | 335.193 | 408.829 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.841
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.841
- phase_score: 0.144
- phase_breakdown.insert_peg_score: 0.172
- phase_breakdown.approach_hole_score: 0.080

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.423
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.841
- **Median Q (composite search score)**: 0.147
- **K-run variance**: 0.0002
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.400


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `193ea3a1ce1ed79056963f057d25ec25a24d300f4824e32f67c8dd96cb6cee27`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `a8b82e05e54fe244d72795229d8ab0587efc7638aafbc9b6be7ad9630911a897`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":8.21739,"average_solve_count":23.0,"average_success_count":23.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.09624,"approach_1.arc_height":0.05976,"insert_1.insert_depth":0.10449,"insert_1.insert_speed":0.01285,"insert_1.pose_tolerance":0.01483},"optimized_scores":{"best_composite_score":0.17289,"best_fitness_score":0.42289,"best_task_score":0.84129},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":10.0,"contact_point_centroid":[0.4561,-0.01013,0.07894],"force_p95":989.65585,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1034.57279,"mean_force":196.93302,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.45186,-0.01006,0.09226]},{"body_a":"peg_socket","body_b":"link7","contact_count":350.0,"contact_point_centroid":[0.56799,-0.01248,0.07969],"force_p95":513.86973,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":943.57835,"mean_force":269.17965,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4506,-0.01454,0.14923]},{"body_a":"peg_socket","body_b":"link6","contact_count":185.0,"contact_point_centroid":[0.57078,-0.01815,0.07941],"force_p95":577.87049,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":599.92309,"mean_force":342.3302,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.44925,-0.01572,0.15445]},{"body_a":"peg_socket","body_b":"link6","contact_count":3.0,"contact_point_centroid":[0.57076,-0.01832,0.07939],"force_p95":396.65114,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":399.13512,"mean_force":340.76777,"phase_index":1.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.44477,-0.01634,0.14701]},{"body_a":"peg_socket","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.5698,-0.01251,0.07993],"force_p95":241.18334,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":242.51819,"mean_force":229.09902,"phase_index":1.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.44477,-0.01634,0.14701]}],"total_contact_groups":5},"final_pose_error":0.18337,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.51096,-0.01842,0.025],"final_tcp_position":[0.44444,-0.01656,0.14638],"realised_fixture_position":[0.51096,-0.01842,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.51096,-0.01842,0.08]},"peak_contact_force":1034.57279,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":455.0,"n_steps_budget":600.0,"object_pos_end":[0.48422,-0.01636,0.14003],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.06419,"object_to_goal_dist_start":0.26034,"object_z_max":0.34469,"peak_contact_force":371.51795,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":545.0,"raw_peak_contact_force":1034.57279,"subtask_id":"approach_hole","tcp_end":[0.44487,-0.0162,0.1472],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.48415,-0.01649,0.13993],"object_pos_start":[0.48422,-0.01636,0.14003],"object_to_goal_dist_end":0.06415,"object_to_goal_dist_start":0.06419,"object_z_max":0.14003,"peak_contact_force":399.13512,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":6.0,"raw_peak_contact_force":399.13512,"subtask_id":"insert_peg","tcp_end":[0.44444,-0.01656,0.14638],"tcp_start":[0.44465,-0.01646,0.14678],"tcp_to_object_dist_end":0.04023,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `8b3071e2f56806ea19629fc8ca21c92088a0ed2e080a3c941a59355284793364`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":8.21739,"average_solve_count":23.0,"average_success_count":23.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.06782,"approach_1.arc_height":0.0409,"insert_1.insert_depth":0.13894,"insert_1.insert_speed":0.03432,"insert_1.pose_tolerance":0.00528},"optimized_scores":{"best_composite_score":0.14713,"best_fitness_score":0.39713,"best_task_score":0.8077},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link7","contact_count":414.0,"contact_point_centroid":[0.55789,0.02551,0.07975],"force_p95":315.22941,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1056.83911,"mean_force":175.09349,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.44238,0.02014,0.15506]},{"body_a":"peg_socket","body_b":"link7","contact_count":25.0,"contact_point_centroid":[0.52952,0.0058,0.0785],"force_p95":839.4845,"geom_a":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":927.01431,"mean_force":419.65368,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.43502,0.01439,0.10383]},{"body_a":"peg_socket","body_b":"link6","contact_count":355.0,"contact_point_centroid":[0.56089,0.02524,0.07971],"force_p95":312.65182,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":384.83766,"mean_force":230.34013,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.44355,0.02074,0.16076]},{"body_a":"peg_socket","body_b":"link6","contact_count":3.0,"contact_point_centroid":[0.5609,0.02676,0.07999],"force_p95":303.02777,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":304.40816,"mean_force":290.82647,"phase_index":1.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.44172,0.02092,0.15825]},{"body_a":"peg_socket","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.55985,0.02952,0.07998],"force_p95":279.21527,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":288.55556,"mean_force":204.10064,"phase_index":1.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.44172,0.02092,0.15825]},{"body_a":"attachment","body_b":"peg_socket","contact_count":6.0,"contact_point_centroid":[0.44268,0.01303,0.07948],"force_p95":0.0,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.43773,0.01297,0.09318]}],"total_contact_groups":6},"final_pose_error":0.22514,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.50095,0.03604,0.025],"final_tcp_position":[0.44131,0.02096,0.15764],"realised_fixture_position":[0.50095,0.03604,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.50095,0.03604,0.08]},"peak_contact_force":1056.83911,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":513.0,"n_steps_budget":600.0,"object_pos_end":[0.48036,0.02256,0.14774],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.07405,"object_to_goal_dist_start":0.26034,"object_z_max":0.34423,"peak_contact_force":235.31113,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":800.0,"raw_peak_contact_force":1056.83911,"subtask_id":"approach_hole","tcp_end":[0.44186,0.02087,0.15845],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.48026,0.02263,0.14763],"object_pos_start":[0.48036,0.02256,0.14774],"object_to_goal_dist_end":0.074,"object_to_goal_dist_start":0.07405,"object_z_max":0.14774,"peak_contact_force":277.46705,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":6.0,"raw_peak_contact_force":304.40816,"subtask_id":"insert_peg","tcp_end":[0.44131,0.02096,0.15764],"tcp_start":[0.44157,0.02095,0.15802],"tcp_to_object_dist_end":0.04025,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `9052c43e0ec79f8dbaeeb446a29f2f8fb71a40595590f857e4c93b1d7e78cc51`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":8.13158,"average_solve_count":38.0,"average_success_count":38.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.0284,"approach_1.arc_height":0.05928,"insert_1.insert_depth":0.12688,"insert_1.insert_speed":0.04809,"insert_1.pose_tolerance":0.00816},"optimized_scores":{"best_composite_score":0.13884,"best_fitness_score":0.38884,"best_task_score":0.80734},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link7","contact_count":749.0,"contact_point_centroid":[0.5399,-0.00564,0.07982],"force_p95":291.91807,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1083.75925,"mean_force":183.96831,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.43588,-0.00933,0.17103]},{"body_a":"attachment","body_b":"peg_socket","contact_count":9.0,"contact_point_centroid":[0.43911,-0.00509,0.07922],"force_p95":535.80369,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":893.00615,"mean_force":99.22291,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4351,-0.00502,0.09289]},{"body_a":"peg_socket","body_b":"link6","contact_count":3.0,"contact_point_centroid":[0.54089,-0.01227,0.07915],"force_p95":503.54661,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":522.94309,"mean_force":384.46684,"phase_index":1.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.44343,-0.0114,0.18359]},{"body_a":"peg_socket","body_b":"link6","contact_count":546.0,"contact_point_centroid":[0.54088,-0.01152,0.07924],"force_p95":262.41671,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":338.54496,"mean_force":235.19275,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.43775,-0.01018,0.17801]},{"body_a":"peg_socket","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.54027,-0.00621,0.07995],"force_p95":287.89331,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":296.41875,"mean_force":184.38913,"phase_index":1.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.44343,-0.0114,0.18359]}],"total_contact_groups":5},"final_pose_error":0.23323,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.48093,-0.01612,0.025],"final_tcp_position":[0.443,-0.01145,0.1832],"realised_fixture_position":[0.48093,-0.01612,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.48093,-0.01612,0.08]},"peak_contact_force":1083.75925,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":905.0,"n_steps_budget":1000.0,"object_pos_end":[0.47853,-0.01122,0.16428],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.0877,"object_to_goal_dist_start":0.26034,"object_z_max":0.34401,"peak_contact_force":238.32533,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1304.0,"raw_peak_contact_force":1083.75925,"subtask_id":"approach_hole","tcp_end":[0.44355,-0.01132,0.18369],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.47846,-0.0113,0.16424],"object_pos_start":[0.47853,-0.01122,0.16428],"object_to_goal_dist_end":0.08768,"object_to_goal_dist_start":0.0877,"object_z_max":0.16428,"peak_contact_force":328.97827,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":6.0,"raw_peak_contact_force":522.94309,"subtask_id":"insert_peg","tcp_end":[0.443,-0.01145,0.1832],"tcp_start":[0.44328,-0.01144,0.18345],"tcp_to_object_dist_end":0.04021,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```