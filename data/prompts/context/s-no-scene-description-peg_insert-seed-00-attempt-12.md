## Search State

- **Seed**: 0
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | approach → descend → insert | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | pose_tolerance | force_exceeded | pose_tolerance | 5 | 0.6646 | 0.86 | ❌ rejected |
| 11 | approach → descend → insert | arc_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | pose_tolerance | force_exceeded | pose_tolerance | 6 | 0.6625 | 0.89 | ❌ rejected |
| 10 | approach → descend → insert | arc_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | pose_tolerance | force_exceeded | pose_tolerance | 7 | 0.3299 | 0.82 | ❌ rejected |
| 9 | approach → descend → insert | arc_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | pose_tolerance | force_exceeded | pose_tolerance | 6 | 0.6972 | 0.91 | ✅ accepted |
| 8 | approach → descend → insert | arc_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | pose_tolerance | force_exceeded | pose_tolerance | 6 | 0.6928 | 0.91 | ✅ accepted |

**Proposal policy**: task_score is 0.86 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.665) — your mutation base

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

- **Composite score**: 0.665
- **task_score** (E): 0.864
- **fitness_score**: 0.611  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.333
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.280

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 0.00 | 1.00 | 0.1434 |
| descend_1 | 1.00 | 1.00 | 0.0001 |
| insert_1 | 0.67 | 0.33 | 0.1061 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 0.00 / step_budget | (0.500, -0.000, 0.301)→(0.440, 0.001, 0.172) | (0.504, -0.000, 0.340)→(0.477, 0.001, 0.158) | 0.260→0.083 | 1.00 / 1.333 | 253.545 | 1136.983 |
| descend_1 | descend | 1.00 / force_exceeded | (0.440, 0.001, 0.172)→(0.440, 0.001, 0.172) | (0.477, 0.001, 0.158)→(0.477, 0.001, 0.158) | 0.083→0.083 | 1.00 / 1.333 | 343.231 | 343.231 |
| insert_1 | insert | 0.67 / step_budget | (0.440, 0.001, 0.172)→(0.483, 0.001, 0.076) | (0.477, 0.001, 0.158)→(0.486, 0.001, 0.116) | 0.083→0.046 | 0.33 / 0.333 | 116.842 | 573.574 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.918
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.918
- phase_score: 0.530
- phase_breakdown.insert_peg_score: 0.695
- phase_breakdown.approach_hole_score: 0.145

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.685
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.918
- **Median Q (composite search score)**: 0.629
- **K-run variance**: 0.0027
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.321


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.5122,"average_solve_count":123.0,"average_success_count":123.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.07257,"descend_1.contact_force_threshold":13.72347,"insert_1.insert_depth":0.0309,"insert_1.insert_speed":0.02527,"insert_1.pose_tolerance":0.01499},"optimized_scores":{"best_composite_score":0.73859,"best_fitness_score":0.68526,"best_task_score":0.91768},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link7","contact_count":146.0,"contact_point_centroid":[0.56434,-0.00779,0.0793],"force_p95":483.18759,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1095.60336,"mean_force":284.32592,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.44931,-0.00897,0.13875]},{"body_a":"attachment","body_b":"peg_socket","contact_count":11.0,"contact_point_centroid":[0.45375,-0.00699,0.07884],"force_p95":469.75918,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":939.51835,"mean_force":85.41076,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4491,-0.00692,0.09194]},{"body_a":"attachment","body_b":"peg_socket","contact_count":569.0,"contact_point_centroid":[0.48095,-0.00793,0.07991],"force_p95":393.05303,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":545.18883,"mean_force":370.41099,"phase_index":2.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49044,-0.01702,0.07904]},{"body_a":"peg_socket","body_b":"link6","contact_count":6.0,"contact_point_centroid":[0.57093,-0.01696,0.07989],"force_p95":391.15876,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":402.26453,"mean_force":300.01484,"phase_index":2.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.4361,-0.01374,0.15486]},{"body_a":"peg_socket","body_b":"link7","contact_count":15.0,"contact_point_centroid":[0.54061,0.01175,0.07964],"force_p95":385.44957,"geom_a":"socket_collar_y1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":394.5068,"mean_force":244.83109,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.44628,-0.00711,0.09772]},{"body_a":"peg_socket","body_b":"link6","contact_count":149.0,"contact_point_centroid":[0.57092,-0.01454,0.07984],"force_p95":286.86448,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":304.40701,"mean_force":257.51073,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.44763,-0.01194,0.15906]},{"body_a":"peg_socket","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.5709,-0.01644,0.07974],"force_p95":266.67375,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":266.67375,"mean_force":266.67375,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.43997,-0.01361,0.15564]},{"body_a":"peg_socket","body_b":"link7","contact_count":4.0,"contact_point_centroid":[0.5409,-0.04843,0.07994],"force_p95":0.0,"geom_a":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.44586,-0.00708,0.09577]}],"total_contact_groups":8},"final_pose_error":0.03357,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.51096,-0.01842,0.025],"final_tcp_position":[0.49457,-0.01725,0.07838],"realised_fixture_position":[0.51096,-0.01842,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.51096,-0.01842,0.08]},"peak_contact_force":1095.60336,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":397.0,"n_steps_budget":600.0,"object_pos_end":[0.47891,-0.01387,0.14647],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.0711,"object_to_goal_dist_start":0.26034,"object_z_max":0.3446,"peak_contact_force":244.78611,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":325.0,"raw_peak_contact_force":1095.60336,"subtask_id":"approach_hole","tcp_end":[0.43997,-0.01361,0.15564],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.47883,-0.01386,0.14648],"object_pos_start":[0.47891,-0.01387,0.14647],"object_to_goal_dist_end":0.07113,"object_to_goal_dist_start":0.0711,"object_z_max":0.14647,"peak_contact_force":266.67375,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1.0,"raw_peak_contact_force":266.67375,"subtask_id":"approach_hole","tcp_end":[0.4399,-0.0136,0.15563],"tcp_start":[0.43997,-0.01361,0.15564],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49893,-0.01716,0.11814],"object_pos_start":[0.47883,-0.01386,0.14648],"object_to_goal_dist_end":0.04184,"object_to_goal_dist_start":0.07113,"object_z_max":0.17088,"peak_contact_force":350.52507,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":575.0,"raw_peak_contact_force":545.18883,"subtask_id":"insert_peg","tcp_end":[0.49457,-0.01725,0.07838],"tcp_start":[0.4399,-0.0136,0.15563],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `8b3071e2f56806ea19629fc8ca21c92088a0ed2e080a3c941a59355284793364`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.47244,"average_solve_count":127.0,"average_success_count":127.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.10715,"descend_1.contact_force_threshold":9.18399,"insert_1.insert_depth":0.0488,"insert_1.insert_speed":0.02207,"insert_1.pose_tolerance":0.01232},"optimized_scores":{"best_composite_score":0.6289,"best_fitness_score":0.57556,"best_task_score":0.83533},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link7","contact_count":87.0,"contact_point_centroid":[0.55145,0.01316,0.07886],"force_p95":616.91451,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1098.22468,"mean_force":307.96319,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.44071,0.0125,0.12975]},{"body_a":"attachment","body_b":"peg_socket","contact_count":10.0,"contact_point_centroid":[0.44772,0.00999,0.07881],"force_p95":508.8161,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":925.12017,"mean_force":92.51202,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.44362,0.00994,0.09203]},{"body_a":"attachment","body_b":"peg_socket","contact_count":463.0,"contact_point_centroid":[0.47094,0.02607,0.07989],"force_p95":402.3372,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":533.58349,"mean_force":384.18897,"phase_index":2.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.48245,0.03314,0.07921]},{"body_a":"peg_socket","body_b":"link6","contact_count":10.0,"contact_point_centroid":[0.56092,0.02977,0.07994],"force_p95":430.98724,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":460.9818,"mean_force":335.9911,"phase_index":2.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.43721,0.02684,0.18319]},{"body_a":"peg_socket","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.56084,0.02666,0.07978],"force_p95":318.80832,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":318.80832,"mean_force":318.80832,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.44341,0.02688,0.1845]},{"body_a":"peg_socket","body_b":"link6","contact_count":258.0,"contact_point_centroid":[0.56089,0.02101,0.07985],"force_p95":302.70526,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":309.9439,"mean_force":275.08944,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.44479,0.02091,0.17427]},{"body_a":"peg_socket","body_b":"link7","contact_count":15.0,"contact_point_centroid":[0.53052,0.00596,0.07951],"force_p95":285.4857,"geom_a":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":295.73162,"mean_force":123.42006,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.44054,0.0101,0.09835]}],"total_contact_groups":7},"final_pose_error":0.04836,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.50095,0.03604,0.025],"final_tcp_position":[0.48656,0.03363,0.07731],"realised_fixture_position":[0.50095,0.03604,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.50095,0.03604,0.08]},"peak_contact_force":1098.22468,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":455.0,"n_steps_budget":600.0,"object_pos_end":[0.47949,0.0276,0.16724],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.09377,"object_to_goal_dist_start":0.26034,"object_z_max":0.34435,"peak_contact_force":275.98157,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":370.0,"raw_peak_contact_force":1098.22468,"subtask_id":"approach_hole","tcp_end":[0.44341,0.02688,0.1845],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.47948,0.02761,0.1673],"object_pos_start":[0.47949,0.0276,0.16724],"object_to_goal_dist_end":0.09384,"object_to_goal_dist_start":0.09377,"object_z_max":0.16724,"peak_contact_force":318.80832,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1.0,"raw_peak_contact_force":318.80832,"subtask_id":"approach_hole","tcp_end":[0.44341,0.02688,0.18458],"tcp_start":[0.44341,0.02688,0.1845],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.48918,0.03345,0.11722],"object_pos_start":[0.47948,0.02761,0.1673],"object_to_goal_dist_end":0.0512,"object_to_goal_dist_start":0.09384,"object_z_max":0.19838,"peak_contact_force":0.0,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":473.0,"raw_peak_contact_force":533.58349,"subtask_id":"insert_peg","tcp_end":[0.48656,0.03363,0.07731],"tcp_start":[0.44341,0.02688,0.18458],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `9052c43e0ec79f8dbaeeb446a29f2f8fb71a40595590f857e4c93b1d7e78cc51`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.97414,"average_solve_count":116.0,"average_success_count":116.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.06432,"descend_1.contact_force_threshold":7.36811,"insert_1.insert_depth":0.09629,"insert_1.insert_speed":0.02585,"insert_1.pose_tolerance":0.01802},"optimized_scores":{"best_composite_score":0.6264,"best_fitness_score":0.57306,"best_task_score":0.83784},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link6","contact_count":104.0,"contact_point_centroid":[0.54069,-0.01094,0.07919],"force_p95":1166.03245,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1217.12003,"mean_force":476.97529,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.43476,-0.00923,0.17523]},{"body_a":"peg_socket","body_b":"link7","contact_count":348.0,"contact_point_centroid":[0.53951,-0.00511,0.07964],"force_p95":779.71925,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1098.91572,"mean_force":304.84175,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4334,-0.00775,0.16272]},{"body_a":"attachment","body_b":"peg_socket","contact_count":10.0,"contact_point_centroid":[0.4403,-0.00475,0.07894],"force_p95":501.7281,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":912.23292,"mean_force":91.22329,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.43635,-0.00467,0.09233]},{"body_a":"attachment","body_b":"peg_socket","contact_count":690.0,"contact_point_centroid":[0.45092,-0.00328,0.07989],"force_p95":421.09813,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":641.95078,"mean_force":398.97053,"phase_index":2.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.46063,-0.01304,0.07915]},{"body_a":"peg_socket","body_b":"link6","contact_count":20.0,"contact_point_centroid":[0.54087,-0.01058,0.07946],"force_p95":291.30939,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":526.82222,"mean_force":252.00991,"phase_index":2.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.42954,-0.00907,0.16866]},{"body_a":"peg_socket","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.54088,-0.01102,0.07926],"force_p95":444.21083,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":444.21083,"mean_force":444.21083,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.4352,-0.00951,0.17539]},{"body_a":"peg_socket","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.54021,-0.00541,0.07996],"force_p95":317.95403,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":317.95403,"mean_force":317.95403,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.4352,-0.00951,0.17539]},{"body_a":"peg_socket","body_b":"link7","contact_count":7.0,"contact_point_centroid":[0.54022,-0.00522,0.07998],"force_p95":286.12745,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":315.34726,"mean_force":185.07336,"phase_index":2.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.43449,-0.00943,0.17461]}],"total_contact_groups":8},"final_pose_error":0.09,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.48093,-0.01612,0.025],"final_tcp_position":[0.46774,-0.01372,0.07271],"realised_fixture_position":[0.48093,-0.01612,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.48093,-0.01612,0.08]},"peak_contact_force":1217.12003,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":455.0,"n_steps_budget":600.0,"object_pos_end":[0.47167,-0.00964,0.15895],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.08443,"object_to_goal_dist_start":0.26034,"object_z_max":0.34408,"peak_contact_force":239.8676,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":462.0,"raw_peak_contact_force":1217.12003,"subtask_id":"approach_hole","tcp_end":[0.4352,-0.00951,0.17539],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.47168,-0.00961,0.15895],"object_pos_start":[0.47167,-0.00964,0.15895],"object_to_goal_dist_end":0.08442,"object_to_goal_dist_start":0.08443,"object_z_max":0.15895,"peak_contact_force":444.21083,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2.0,"raw_peak_contact_force":444.21083,"subtask_id":"approach_hole","tcp_end":[0.43521,-0.00947,0.17539],"tcp_start":[0.4352,-0.00951,0.17539],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47092,-0.0135,0.11258],"object_pos_start":[0.47168,-0.00961,0.15895],"object_to_goal_dist_end":0.04571,"object_to_goal_dist_start":0.08442,"object_z_max":0.17127,"peak_contact_force":0.0,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":717.0,"raw_peak_contact_force":641.95078,"subtask_id":"insert_peg","tcp_end":[0.46774,-0.01372,0.07271],"tcp_start":[0.43521,-0.00947,0.17539],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```