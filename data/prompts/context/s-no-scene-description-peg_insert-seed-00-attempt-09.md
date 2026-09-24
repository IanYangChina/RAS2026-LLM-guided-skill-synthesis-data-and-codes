## Search State

- **Seed**: 0
- **Iteration**: 10 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 9 | approach → descend → insert | arc_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | pose_tolerance | force_exceeded | pose_tolerance | 6 | 0.6972 | 0.91 | ✅ accepted |
| 8 | approach → descend → insert | arc_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | pose_tolerance | force_exceeded | pose_tolerance | 6 | 0.6928 | 0.91 | ✅ accepted |
| 7 | approach → align → descend → insert | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | admittance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 8 | 0.1924 | 0.82 | ❌ rejected |
| 6 | approach → insert | arc_cartesian | linear_cartesian | position_control | admittance_control | pose_tolerance | pose_tolerance | 5 | 0.1530 | 0.82 | ❌ rejected |
| 5 | approach → descend → insert | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | pose_tolerance | force_exceeded | pose_tolerance | 5 | 0.7240 | 0.88 | ❌ rejected |

**Proposal policy**: task_score is near-perfect (0.91). Preserve useful working parts and make only evidence-backed refinements. A HOLD is acceptable if you genuinely cannot find a better structure.

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

## Current Skill (Q=0.697) — your mutation base

```yaml
skill: peg_insert
dsl_version: 2
subtasks:
- id: approach_hole
  offset:
  - 0.0
  - 0.0
  - 0.15
  weight: 0.3
- id: insert_peg
  weight: 0.7
phases:
- id: approach_1
  type: approach
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.15
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
      - 0.12
      default: 0.06
      binds_to:
      - path: generator.speed
        mode: replace
    arc_height:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.08
      binds_to:
      - path: generator.arc_height
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
    - 0.03
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
      - 3.0
      - 15.0
      default: 8.0
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
      default: 0.025
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
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.15]
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=world_z, tolerance=0.1
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
    - arc_height: status=consumed; consumers=generator.arc_height (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.03]
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

- **Composite score**: 0.697
- **task_score** (E): 0.912
- **fitness_score**: 0.694  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.333
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.330

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 0.00 | 1.00 | 0.1410 |
| descend_1 | 1.00 | 1.00 | 0.0001 |
| insert_1 | 0.00 | 1.00 | 0.0971 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 0.00 / step_budget | (0.500, -0.000, 0.301)→(0.456, 0.020, 0.169) | (0.504, -0.000, 0.340)→(0.493, 0.019, 0.154) | 0.260→0.078 | 1.00 / 1.333 | 275.823 | 1735.431 |
| descend_1 | descend | 1.00 / force_exceeded | (0.456, 0.020, 0.169)→(0.456, 0.020, 0.169) | (0.493, 0.019, 0.154)→(0.493, 0.019, 0.154) | 0.078→0.078 | 1.00 / 1.333 | 301.041 | 301.041 |
| insert_1 | insert | 0.00 / step_budget | (0.456, 0.020, 0.169)→(0.488, 0.010, 0.079) | (0.493, 0.019, 0.154)→(0.490, 0.010, 0.119) | 0.078→0.044 | 1.00 / 1.000 | 392.648 | 600.912 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.961
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.961
- phase_score: 0.676
- phase_breakdown.insert_peg_score: 0.840
- phase_breakdown.approach_hole_score: 0.291

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.790
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.961
- **Median Q (composite search score)**: 0.720
- **K-run variance**: 0.0079
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.424


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.40876,"average_solve_count":137.0,"average_success_count":137.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.04229,"approach_1.arc_height":0.03729,"descend_1.contact_force_threshold":9.0049,"insert_1.insert_depth":0.07475,"insert_1.insert_speed":0.02424,"insert_1.pose_tolerance":0.01498},"optimized_scores":{"best_composite_score":0.79298,"best_fitness_score":0.78965,"best_task_score":0.96058},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link7","contact_count":169.0,"contact_point_centroid":[0.56367,0.01664,0.07952],"force_p95":572.88004,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1104.17469,"mean_force":282.93997,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.45072,0.01843,0.13731]},{"body_a":"peg_socket","body_b":"link7","contact_count":37.0,"contact_point_centroid":[0.53994,0.01262,0.07888],"force_p95":927.22121,"geom_a":"socket_collar_y1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1074.9734,"mean_force":408.71567,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.44571,0.01405,0.10783]},{"body_a":"attachment","body_b":"peg_socket","contact_count":9.0,"contact_point_centroid":[0.45232,0.0127,0.07886],"force_p95":559.32652,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":932.21087,"mean_force":103.57899,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.44569,0.01266,0.09141]},{"body_a":"attachment","body_b":"peg_socket","contact_count":520.0,"contact_point_centroid":[0.48095,0.00734,0.0799],"force_p95":414.02179,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":754.75876,"mean_force":397.58198,"phase_index":2.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.48874,-0.00435,0.07945]},{"body_a":"peg_socket","body_b":"link6","contact_count":12.0,"contact_point_centroid":[0.57094,0.00724,0.07998],"force_p95":385.49169,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":390.38685,"mean_force":326.2277,"phase_index":2.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.4419,0.02021,0.19729]},{"body_a":"attachment","body_b":"peg_socket","contact_count":5.0,"contact_point_centroid":[0.48357,0.01161,0.07946],"force_p95":306.53047,"geom_a":"peg_tip","geom_b":"socket_collar_y1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":319.14921,"mean_force":187.70386,"phase_index":2.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.48315,-0.00333,0.07945]},{"body_a":"peg_socket","body_b":"link6","contact_count":685.0,"contact_point_centroid":[0.57091,0.02046,0.07987],"force_p95":289.46422,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":315.00212,"mean_force":252.75396,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.44494,0.02186,0.1715]},{"body_a":"peg_socket","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.57092,0.0117,0.07994],"force_p95":294.72741,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":294.72741,"mean_force":294.72741,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.44942,0.01876,0.20018]}],"total_contact_groups":8},"final_pose_error":0.07704,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.51096,-0.01842,0.025],"final_tcp_position":[0.49313,-0.00525,0.07903],"realised_fixture_position":[0.51096,-0.01842,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.51096,-0.01842,0.08]},"peak_contact_force":1104.17469,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":964.0,"n_steps_budget":1000.0,"object_pos_end":[0.484,0.01581,0.18029],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.10278,"object_to_goal_dist_start":0.26034,"object_z_max":0.34435,"peak_contact_force":258.76155,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":900.0,"raw_peak_contact_force":1104.17469,"subtask_id":"approach_hole","tcp_end":[0.44942,0.01876,0.20018],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":750.0,"object_pos_end":[0.48402,0.01592,0.18032],"object_pos_start":[0.484,0.01581,0.18029],"object_to_goal_dist_end":0.10282,"object_to_goal_dist_start":0.10278,"object_z_max":0.18029,"peak_contact_force":294.72741,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1.0,"raw_peak_contact_force":294.72741,"subtask_id":"approach_hole","tcp_end":[0.44944,0.01892,0.20021],"tcp_start":[0.44942,0.01876,0.20018],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49622,-0.00464,0.11891],"object_pos_start":[0.48402,0.01592,0.18032],"object_to_goal_dist_end":0.03937,"object_to_goal_dist_start":0.10282,"object_z_max":0.20789,"peak_contact_force":383.46527,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":537.0,"raw_peak_contact_force":754.75876,"subtask_id":"insert_peg","tcp_end":[0.49313,-0.00525,0.07903],"tcp_start":[0.44944,0.01892,0.20021],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `8b3071e2f56806ea19629fc8ca21c92088a0ed2e080a3c941a59355284793364`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.31395,"average_solve_count":86.0,"average_success_count":86.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.11766,"approach_1.arc_height":0.1464,"descend_1.contact_force_threshold":3.94115,"insert_1.insert_depth":0.06832,"insert_1.insert_speed":0.04769,"insert_1.pose_tolerance":0.01178},"optimized_scores":{"best_composite_score":0.57831,"best_fitness_score":0.57498,"best_task_score":0.83859},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":11.0,"contact_point_centroid":[0.45236,0.01221,0.07875],"force_p95":997.31349,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1045.47355,"mean_force":181.32973,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.44806,0.01217,0.09185]},{"body_a":"peg_socket","body_b":"link7","contact_count":349.0,"contact_point_centroid":[0.55855,0.02514,0.07969],"force_p95":343.65986,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":945.74731,"mean_force":201.54894,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.45032,0.02135,0.16155]},{"body_a":"attachment","body_b":"peg_socket","contact_count":596.0,"contact_point_centroid":[0.47094,0.02011,0.0799],"force_p95":413.61151,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":542.88839,"mean_force":387.16973,"phase_index":2.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.4794,0.03085,0.07918]},{"body_a":"peg_socket","body_b":"link6","contact_count":15.0,"contact_point_centroid":[0.56092,0.02549,0.07972],"force_p95":467.39888,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":496.48053,"mean_force":309.62889,"phase_index":2.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.44532,0.02336,0.1634]},{"body_a":"peg_socket","body_b":"link7","contact_count":7.0,"contact_point_centroid":[0.55992,0.03103,0.07997],"force_p95":426.7506,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":427.47234,"mean_force":278.58203,"phase_index":2.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.44778,0.02356,0.16669]},{"body_a":"peg_socket","body_b":"link6","contact_count":290.0,"contact_point_centroid":[0.56087,0.02425,0.07935],"force_p95":282.91092,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":316.22822,"mean_force":245.34025,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.45251,0.02331,0.17242]},{"body_a":"peg_socket","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.5609,0.02458,0.07942],"force_p95":256.30986,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":256.30986,"mean_force":256.30986,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.44861,0.02361,0.16774]},{"body_a":"peg_socket","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.55992,0.03107,0.07996],"force_p95":74.8314,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":74.8314,"mean_force":74.8314,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.44861,0.02361,0.16774]}],"total_contact_groups":8},"final_pose_error":0.0689,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.50095,0.03604,0.025],"final_tcp_position":[0.48396,0.03173,0.07832],"realised_fixture_position":[0.50095,0.03604,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.50095,0.03604,0.08]},"peak_contact_force":1045.47355,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":513.0,"n_steps_budget":600.0,"object_pos_end":[0.48614,0.02481,0.15393],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.07921,"object_to_goal_dist_start":0.26034,"object_z_max":0.34437,"peak_contact_force":236.14988,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":650.0,"raw_peak_contact_force":1045.47355,"subtask_id":"approach_hole","tcp_end":[0.44861,0.02361,0.16774],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.48611,0.02473,0.1539],"object_pos_start":[0.48614,0.02481,0.15393],"object_to_goal_dist_end":0.07915,"object_to_goal_dist_start":0.07921,"object_z_max":0.15393,"peak_contact_force":256.30986,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2.0,"raw_peak_contact_force":256.30986,"subtask_id":"approach_hole","tcp_end":[0.44858,0.02351,0.16769],"tcp_start":[0.44861,0.02361,0.16774],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.48895,0.03118,0.118],"object_pos_start":[0.48611,0.02473,0.1539],"object_to_goal_dist_end":0.05038,"object_to_goal_dist_start":0.07915,"object_z_max":0.17197,"peak_contact_force":362.8905,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":618.0,"raw_peak_contact_force":542.88839,"subtask_id":"insert_peg","tcp_end":[0.48396,0.03173,0.07832],"tcp_start":[0.44858,0.02351,0.16769],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `9052c43e0ec79f8dbaeeb446a29f2f8fb71a40595590f857e4c93b1d7e78cc51`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.48454,"average_solve_count":97.0,"average_success_count":97.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.06194,"approach_1.arc_height":0.03627,"descend_1.contact_force_threshold":9.57645,"insert_1.insert_depth":0.08116,"insert_1.insert_speed":0.03254,"insert_1.pose_tolerance":0.01123},"optimized_scores":{"best_composite_score":0.72033,"best_fitness_score":0.717,"best_task_score":0.93616},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":11.0,"contact_point_centroid":[0.44617,0.01582,0.07899],"force_p95":2472.55381,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":3056.6433,"mean_force":449.55524,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.44228,0.01431,0.09205]},{"body_a":"attachment","body_b":"peg_socket","contact_count":11.0,"contact_point_centroid":[0.45188,0.0144,0.07926],"force_p95":1980.77104,"geom_a":"peg_tip","geom_b":"socket_collar_y1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":2396.15054,"mean_force":539.17436,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.44389,0.01427,0.09184]},{"body_a":"peg_socket","body_b":"link7","contact_count":601.0,"contact_point_centroid":[0.54074,0.01615,0.07984],"force_p95":310.28718,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":940.4423,"mean_force":293.73287,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.46303,0.01535,0.13147]},{"body_a":"attachment","body_b":"peg_socket","contact_count":788.0,"contact_point_centroid":[0.48317,0.0162,0.07971],"force_p95":448.90892,"geom_a":"peg_tip","geom_b":"socket_collar_y1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":505.08906,"mean_force":421.86353,"phase_index":2.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.47761,0.00453,0.08011]},{"body_a":"peg_socket","body_b":"link7","contact_count":31.0,"contact_point_centroid":[0.54067,0.00823,0.07986],"force_p95":359.61563,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":380.12009,"mean_force":260.32179,"phase_index":2.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.46201,0.01814,0.12973]},{"body_a":"peg_socket","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.5407,-0.05903,0.07991],"force_p95":352.08498,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":352.08498,"mean_force":352.08498,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.46915,0.01833,0.13945]}],"total_contact_groups":6},"final_pose_error":0.08331,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.48093,-0.01612,0.025],"final_tcp_position":[0.48616,0.00257,0.07985],"realised_fixture_position":[0.48093,-0.01612,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.48093,-0.01612,0.08]},"peak_contact_force":3056.6433,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":693.0,"n_steps_budget":780.0,"object_pos_end":[0.5075,0.01552,0.12841],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.05139,"object_to_goal_dist_start":0.26034,"object_z_max":0.34425,"peak_contact_force":332.55664,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":623.0,"raw_peak_contact_force":3056.6433,"subtask_id":"approach_hole","tcp_end":[0.46915,0.01833,0.13945],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.50749,0.01555,0.12833],"object_pos_start":[0.5075,0.01552,0.12841],"object_to_goal_dist_end":0.05132,"object_to_goal_dist_start":0.05139,"object_z_max":0.12841,"peak_contact_force":352.08498,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1.0,"raw_peak_contact_force":352.08498,"subtask_id":"approach_hole","tcp_end":[0.46914,0.01837,0.13936],"tcp_start":[0.46915,0.01833,0.13945],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.48616,0.00261,0.11985],"object_pos_start":[0.50749,0.01555,0.12833],"object_to_goal_dist_end":0.04227,"object_to_goal_dist_start":0.05132,"object_z_max":0.14541,"peak_contact_force":431.58871,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":819.0,"raw_peak_contact_force":505.08906,"subtask_id":"insert_peg","tcp_end":[0.48616,0.00257,0.07985],"tcp_start":[0.46914,0.01837,0.13936],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```