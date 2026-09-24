## Search State

- **Seed**: 8
- **Iteration**: 3 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 2 | retract → approach → descend → insert | linear_cartesian | arc_cartesian | linear_cartesian | linear_cartesian | impedance_control | impedance_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 9 | 0.1028 | 0.68 | ❌ rejected |
| 1 | approach → align → descend → insert | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 11 | 0.0456 | 0.85 | ✅ accepted |
| 0 | pull → insert → descend → contact | arc_cartesian | impedance_motion | linear_cartesian | linear_cartesian | impedance_control | impedance_control | position_control | impedance_control | time_limit | pose_tolerance | contact_detected | force_exceeded | 5 | -0.1274 | 0.00 | ✅ accepted |

**Proposal policy**: task_score is 0.68 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.103) — your mutation base

```yaml
skill: peg_insert
dsl_version: 2
subtasks:
- id: reach_above_hole
  offset:
  - 0.0
  - 0.0
  - 0.2
  weight: 0.3
- id: reach_entry
  offset:
  - 0.0
  - 0.0
  - 0.02
  weight: 0.2
- id: insertion_subtask
  target_entity: object
  weight: 0.5
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
    - 0.2
    tolerance: 0.01
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: world_z
      tolerance: 0.05
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.1
      - 0.3
      default: 0.2
      binds_to:
      - path: target.offset.z
        mode: replace
    approach_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
    pose_tol:
      type: scalar
      range:
      - 0.005
      - 0.02
      default: 0.01
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  subtask_id: reach_above_hole
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
    - 0.02
    tolerance: 0.005
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: world_z
      tolerance: 0.02
  parameters:
    align_offset_z:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.02
      binds_to:
      - path: target.offset.z
        mode: replace
    align_speed:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
    align_tol:
      type: scalar
      range:
      - 0.003
      - 0.01
      default: 0.005
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  subtask_id: reach_entry
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
    - 0.0
    orientation:
      mode: keep_current
  parameters:
    descend_speed:
      type: scalar
      range:
      - 0.005
      - 0.03
      default: 0.01
      binds_to:
      - path: generator.speed
        mode: replace
    force_threshold:
      type: scalar
      range:
      - 1.0
      - 20.0
      default: 5.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
  guards:
  - id: contact_guard
    when: during_phase
    predicate: contact_detected
    threshold: 0.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: reduce_speed
    offset:
    - 0.0
    - 0.0
    - 0.0
  subtask_id: insertion_subtask
- id: insert_1
  type: insert
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
      mode: replace_offset_projection
      sign: negative
    orientation:
      mode: keep_current
  parameters:
    insert_depth:
      type: scalar
      range:
      - 0.05
      - 0.15
      default: 0.1
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    insert_speed:
      type: scalar
      range:
      - 0.005
      - 0.02
      default: 0.01
      binds_to:
      - path: generator.speed
        mode: replace
    insert_tol:
      type: scalar
      range:
      - 0.01
      - 0.03
      default: 0.02
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  guards:
  - id: force_limit_guard
    when: during_phase
    predicate: force_below
    threshold: 40.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.005
    - 0.005
    - 0.0
  subtask_id: insertion_subtask

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.2], tolerance=0.01
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=world_z, tolerance=0.05
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
    - approach_speed: status=consumed; consumers=generator.speed (replace)
    - pose_tol: status=consumed; consumers=termination.pose_tolerance (replace)
- **align_1** (`align`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.02], tolerance=0.005
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=world_z, tolerance=0.02
  - parameter_bindings:
    - align_offset_z: status=consumed; consumers=target.offset.z (replace)
    - align_speed: status=consumed; consumers=generator.speed (replace)
    - align_tol: status=consumed; consumers=termination.pose_tolerance (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (replace)
    - force_threshold: status=consumed; consumers=termination.force_threshold (replace)
  - guards:
    - id=contact_guard, when=during_phase, predicate=contact_detected, on_failure=retry, threshold=0.0
  - retries: max_attempts=2, strategy=reduce_speed, offset=[0.0, 0.0, 0.0]
- **insert_1** (`insert`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.1, mode=replace_offset_projection, sign=negative}
  - orientation: mode=keep_current
  - parameter_bindings:
    - insert_depth: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - insert_speed: status=consumed; consumers=generator.speed (replace)
    - insert_tol: status=consumed; consumers=termination.pose_tolerance (replace)
  - guards:
    - id=force_limit_guard, when=during_phase, predicate=force_below, on_failure=retry, threshold=40.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.005, 0.005, 0.0]

## Design Metrics

- **Composite score**: 0.103
- **task_score** (E): 0.677
- **fitness_score**: 0.363  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.250
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.510

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| retract_1 | 1.00 | 0.00 | 0.0402 |
| approach_1 | 0.33 | 1.00 | 0.1182 |
| descend_1 | 1.00 | 1.00 | 0.0001 |
| insert_1 | 0.00 | 0.67 | 0.0000 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| retract_1 | retract | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.498, -0.000, 0.341) | (0.504, -0.000, 0.340)→(0.500, -0.000, 0.381) | 0.260→0.301 | 0.00 / 0.000 | 0.000 | 0.000 |
| approach_1 | approach | 0.33 / step_budget | (0.498, -0.000, 0.341)→(0.455, 0.004, 0.231) | (0.500, -0.000, 0.381)→(0.487, 0.005, 0.206) | 0.301→0.128 | 1.00 / 1.000 | 267.004 | 3455.173 |
| descend_1 | descend | 1.00 / force_exceeded | (0.455, 0.004, 0.231)→(0.455, 0.004, 0.231) | (0.487, 0.005, 0.206)→(0.487, 0.005, 0.206) | 0.128→0.128 | 1.00 / 1.000 | 181.636 | 195.122 |
| insert_1 | insert | 0.00 / guard_failure | (0.455, 0.004, 0.231)→(0.455, 0.004, 0.231) | (0.487, 0.005, 0.206)→(0.487, 0.005, 0.206) | 0.128→0.127 | 0.67 / 0.667 | 55.765 | 140.511 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.684
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.684
- phase_score: 0.159
- phase_breakdown.insertion_subtask_score: 0.039
- phase_breakdown.reach_above_hole_score: 0.428
- phase_breakdown.reach_entry_score: 0.057

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.369
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.684
- **Median Q (composite search score)**: 0.105
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.353


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `6af64227b04102c511381eb024ec48290b429fbc7fcb6f0c4b42c66d0a974e9f`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `5cd76595591baa0f9f71873dced18f865534f529ba8f9daf4a3973579a78fb36`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":5.93548,"average_solve_count":62.0,"average_success_count":62.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.1433,"approach_1.approach_speed":0.0492,"approach_1.arc_height":0.17987,"descend_1.descend_speed":0.011,"descend_1.force_threshold":1.75539,"insert_1.insert_depth":0.07424,"insert_1.insert_speed":0.00841,"insert_1.insert_tol":0.01652,"retract_1.retract_speed":0.09105},"optimized_scores":{"best_composite_score":0.09416,"best_fitness_score":0.35416,"best_task_score":0.66482},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link7","contact_count":22.0,"contact_point_centroid":[0.5215,0.0068,0.07862],"force_p95":6533.28001,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":8050.64162,"mean_force":2046.53891,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.39303,0.00957,0.13341]},{"body_a":"peg_socket","body_b":"link6","contact_count":892.0,"contact_point_centroid":[0.5461,0.01845,0.07984],"force_p95":282.42061,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":7663.66504,"mean_force":313.54816,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.42765,0.01111,0.20133]},{"body_a":"peg_socket","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.54612,0.02456,0.07996],"force_p95":222.11885,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":222.11885,"mean_force":222.11885,"phase_index":2.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.45388,0.01794,0.22685]},{"body_a":"peg_socket","body_b":"link6","contact_count":2.0,"contact_point_centroid":[0.54614,0.02457,0.07998],"force_p95":173.80565,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":175.3288,"mean_force":160.09726,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.4539,0.01792,0.22677]},{"body_a":"peg_socket","body_b":"link7","contact_count":22.0,"contact_point_centroid":[0.51595,0.00823,0.07785],"force_p95":0.0,"geom_a":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.39303,0.00957,0.13341]}],"total_contact_groups":5},"final_pose_error":0.22425,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.48616,0.03898,0.025],"final_tcp_position":[0.45392,0.01789,0.22668],"realised_fixture_position":[0.48616,0.03898,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.48616,0.03898,0.08]},"peak_contact_force":8050.64162,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":392.0,"n_steps_budget":600.0,"object_pos_end":[0.49982,-1e-05,0.38065],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.30065,"object_to_goal_dist_start":0.26034,"object_z_max":0.38056,"peak_contact_force":0.0,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_above_hole","tcp_end":[0.49809,-2e-05,0.34069],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.48302,0.01967,0.1995],"object_pos_start":[0.49982,-1e-05,0.38065],"object_to_goal_dist_end":0.12229,"object_to_goal_dist_start":0.30065,"object_z_max":0.38743,"peak_contact_force":284.11533,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":936.0,"raw_peak_contact_force":8050.64162,"subtask_id":"reach_above_hole","tcp_end":[0.45388,0.01794,0.22685],"tcp_start":[0.49809,-2e-05,0.34069],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.48305,0.01967,0.19946],"object_pos_start":[0.48302,0.01967,0.1995],"object_to_goal_dist_end":0.12225,"object_to_goal_dist_start":0.12229,"object_z_max":0.1995,"peak_contact_force":222.11885,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1.0,"raw_peak_contact_force":222.11885,"subtask_id":"reach_entry","tcp_end":[0.4539,0.01793,0.2268],"tcp_start":[0.45388,0.01794,0.22685],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.48307,0.01965,0.19942],"object_pos_start":[0.48305,0.01967,0.19946],"object_to_goal_dist_end":0.12221,"object_to_goal_dist_start":0.12225,"object_z_max":0.19946,"peak_contact_force":0.0,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":2.0,"raw_peak_contact_force":175.3288,"subtask_id":"insertion_subtask","tcp_end":[0.45392,0.01789,0.22668],"tcp_start":[0.45391,0.0179,0.22669],"tcp_to_object_dist_end":0.03995,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `622d0229ecd682a86b582a15854ad918b7f35f1e42c4c70c71dc1687a4b64ce2`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":5.8254,"average_solve_count":63.0,"average_success_count":63.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.18046,"approach_1.approach_speed":0.04985,"approach_1.arc_height":0.12161,"descend_1.descend_speed":0.01261,"descend_1.force_threshold":3.3992,"insert_1.insert_depth":0.09166,"insert_1.insert_speed":0.00846,"insert_1.insert_tol":0.02032,"retract_1.retract_speed":0.0585},"optimized_scores":{"best_composite_score":0.10524,"best_fitness_score":0.36524,"best_task_score":0.68325},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link6","contact_count":880.0,"contact_point_centroid":[0.58945,0.00059,0.07974],"force_p95":265.11266,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1371.45704,"mean_force":230.8791,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.43072,0.00198,0.19646]},{"body_a":"peg_socket","body_b":"link7","contact_count":15.0,"contact_point_centroid":[0.49934,0.00298,0.0783],"force_p95":387.23678,"geom_a":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1290.78927,"mean_force":86.05262,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.40336,0.00308,0.12595]},{"body_a":"peg_socket","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.58962,-0.00266,0.08],"force_p95":126.74535,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":126.74535,"mean_force":126.74535,"phase_index":2.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.45363,-0.00342,0.22926]},{"body_a":"peg_socket","body_b":"link6","contact_count":3.0,"contact_point_centroid":[0.58961,-0.00261,0.07998],"force_p95":85.92402,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":86.94064,"mean_force":75.63517,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.45366,-0.00339,0.22911]},{"body_a":"peg_socket","body_b":"link6","contact_count":26.0,"contact_point_centroid":[0.55938,0.0133,0.0776],"force_p95":0.0,"geom_a":"socket_collar_y1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.40399,0.00312,0.13413]},{"body_a":"peg_socket","body_b":"link7","contact_count":19.0,"contact_point_centroid":[0.53016,0.01341,0.07806],"force_p95":0.0,"geom_a":"socket_collar_y1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.40347,0.00309,0.1285]}],"total_contact_groups":6},"final_pose_error":0.25278,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.52962,-0.01705,0.025],"final_tcp_position":[0.45367,-0.00338,0.22905],"realised_fixture_position":[0.52962,-0.01705,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.52962,-0.01705,0.08]},"peak_contact_force":1371.45704,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":392.0,"n_steps_budget":600.0,"object_pos_end":[0.49982,-1e-05,0.38065],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.30065,"object_to_goal_dist_start":0.26034,"object_z_max":0.38056,"peak_contact_force":0.0,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_above_hole","tcp_end":[0.49809,-2e-05,0.34069],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":994.0,"n_steps_budget":1000.0,"object_pos_end":[0.48631,-0.00227,0.20622],"object_pos_start":[0.49982,-1e-05,0.38065],"object_to_goal_dist_end":0.12698,"object_to_goal_dist_start":0.30065,"object_z_max":0.38795,"peak_contact_force":254.40195,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":940.0,"raw_peak_contact_force":1371.45704,"subtask_id":"reach_above_hole","tcp_end":[0.45363,-0.00342,0.22926],"tcp_start":[0.49809,-2e-05,0.34069],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.48634,-0.00225,0.20612],"object_pos_start":[0.48631,-0.00227,0.20622],"object_to_goal_dist_end":0.12687,"object_to_goal_dist_start":0.12698,"object_z_max":0.20622,"peak_contact_force":86.288,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1.0,"raw_peak_contact_force":126.74535,"subtask_id":"reach_entry","tcp_end":[0.45366,-0.00339,0.22915],"tcp_start":[0.45363,-0.00342,0.22926],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.48634,-0.00225,0.20608],"object_pos_start":[0.48634,-0.00225,0.20612],"object_to_goal_dist_end":0.12684,"object_to_goal_dist_start":0.12687,"object_z_max":0.20612,"peak_contact_force":63.19042,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":3.0,"raw_peak_contact_force":86.94064,"subtask_id":"insertion_subtask","tcp_end":[0.45367,-0.00338,0.22905],"tcp_start":[0.45366,-0.00338,0.22908],"tcp_to_object_dist_end":0.03996,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `0f6bb7aab939f458126b1b6d18ae56b7586f021b7d8e0537b172a4bcc3a97854`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":5.79104,"average_solve_count":67.0,"average_success_count":67.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.16422,"approach_1.approach_speed":0.04961,"approach_1.arc_height":0.16051,"descend_1.descend_speed":0.01245,"descend_1.force_threshold":3.23269,"insert_1.insert_depth":0.08215,"insert_1.insert_speed":0.00502,"insert_1.insert_tol":0.02199,"retract_1.retract_speed":0.04173},"optimized_scores":{"best_composite_score":0.10901,"best_fitness_score":0.36901,"best_task_score":0.68373},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link6","contact_count":29.0,"contact_point_centroid":[0.56527,0.00665,0.07734],"force_p95":158.37837,"geom_a":"socket_collar_y1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":943.41899,"mean_force":41.63389,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.40454,0.0025,0.13487]},{"body_a":"peg_socket","body_b":"link6","contact_count":882.0,"contact_point_centroid":[0.59633,0.00119,0.07971],"force_p95":257.38821,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":807.59004,"mean_force":223.17224,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.43221,0.00196,0.19996]},{"body_a":"peg_socket","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.59638,0.00089,0.07986],"force_p95":236.50236,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":236.50236,"mean_force":236.50236,"phase_index":2.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.4583,-0.00343,0.23709]},{"body_a":"peg_socket","body_b":"link6","contact_count":3.0,"contact_point_centroid":[0.59642,0.00113,0.07992],"force_p95":155.67554,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":159.26349,"mean_force":128.91756,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.45834,-0.00337,0.237]},{"body_a":"peg_socket","body_b":"link7","contact_count":16.0,"contact_point_centroid":[0.50542,0.00346,0.0782],"force_p95":0.0,"geom_a":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4036,0.00246,0.12658]},{"body_a":"peg_socket","body_b":"link7","contact_count":20.0,"contact_point_centroid":[0.53119,0.00913,0.07777],"force_p95":0.0,"geom_a":"socket_collar_y1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.40375,0.00247,0.12918]}],"total_contact_groups":6},"final_pose_error":0.2523,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.53648,-0.02339,0.025],"final_tcp_position":[0.45837,-0.00331,0.23691],"realised_fixture_position":[0.53648,-0.02339,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.53648,-0.02339,0.08]},"peak_contact_force":943.41899,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":398.0,"n_steps_budget":750.0,"object_pos_end":[0.49982,-1e-05,0.38066],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.30066,"object_to_goal_dist_start":0.26034,"object_z_max":0.38057,"peak_contact_force":0.0,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_above_hole","tcp_end":[0.49809,-2e-05,0.34069],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49031,-0.00209,0.21314],"object_pos_start":[0.49982,-1e-05,0.38066],"object_to_goal_dist_end":0.13351,"object_to_goal_dist_start":0.30066,"object_z_max":0.38804,"peak_contact_force":262.49548,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":947.0,"raw_peak_contact_force":943.41899,"subtask_id":"reach_above_hole","tcp_end":[0.4583,-0.00343,0.23709],"tcp_start":[0.49809,-2e-05,0.34069],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.49034,-0.00205,0.21311],"object_pos_start":[0.49031,-0.00209,0.21314],"object_to_goal_dist_end":0.13348,"object_to_goal_dist_start":0.13351,"object_z_max":0.21314,"peak_contact_force":236.50236,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1.0,"raw_peak_contact_force":236.50236,"subtask_id":"reach_entry","tcp_end":[0.45832,-0.00339,0.23705],"tcp_start":[0.4583,-0.00343,0.23709],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.49038,-0.00202,0.21308],"object_pos_start":[0.49034,-0.00205,0.21311],"object_to_goal_dist_end":0.13345,"object_to_goal_dist_start":0.13348,"object_z_max":0.21311,"peak_contact_force":104.10524,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":3.0,"raw_peak_contact_force":159.26349,"subtask_id":"insertion_subtask","tcp_end":[0.45837,-0.00331,0.23691],"tcp_start":[0.45836,-0.00334,0.23695],"tcp_to_object_dist_end":0.03992,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```