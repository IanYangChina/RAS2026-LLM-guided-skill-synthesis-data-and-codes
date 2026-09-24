## Search State

- **Seed**: 8
- **Iteration**: 4 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 3 | retract → approach → descend → insert | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 11 | 0.0138 | 0.80 | ❌ rejected |
| 2 | retract → approach → descend → insert | linear_cartesian | arc_cartesian | linear_cartesian | linear_cartesian | impedance_control | impedance_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 9 | 0.1028 | 0.68 | ❌ rejected |
| 1 | approach → align → descend → insert | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 11 | 0.0456 | 0.85 | ✅ accepted |
| 0 | pull → insert → descend → contact | arc_cartesian | impedance_motion | linear_cartesian | linear_cartesian | impedance_control | impedance_control | position_control | impedance_control | time_limit | pose_tolerance | contact_detected | force_exceeded | 5 | -0.1274 | 0.00 | ✅ accepted |

**Proposal policy**: task_score is 0.80 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.014) — your mutation base

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

- **Composite score**: 0.014
- **task_score** (E): 0.795
- **fitness_score**: 0.374  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.250
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.610

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| retract_1 | 0.00 | 1.00 | 0.1720 |
| approach_1 | 0.00 | 1.00 | 0.0921 |
| descend_1 | 1.00 | 1.00 | 0.0000 |
| insert_1 | 0.00 | 1.00 | 0.0000 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| retract_1 | retract | 0.00 / step_budget | (0.500, -0.000, 0.301)→(0.406, -0.001, 0.158) | (0.504, -0.000, 0.340)→(0.446, -0.001, 0.151) | 0.260→0.090 | 1.00 / 1.000 | 154.309 | 2882.427 |
| approach_1 | approach | 0.00 / step_budget | (0.406, -0.001, 0.158)→(0.456, -0.004, 0.235) | (0.446, -0.001, 0.151)→(0.487, -0.004, 0.210) | 0.090→0.132 | 1.00 / 1.000 | 257.134 | 299.575 |
| descend_1 | descend | 1.00 / force_exceeded | (0.456, -0.004, 0.235)→(0.456, -0.004, 0.235) | (0.487, -0.004, 0.210)→(0.487, -0.004, 0.210) | 0.132→0.132 | 1.00 / 1.000 | 166.560 | 166.560 |
| insert_1 | insert | 0.00 / guard_failure | (0.456, -0.004, 0.235)→(0.456, -0.004, 0.235) | (0.487, -0.004, 0.210)→(0.487, -0.004, 0.210) | 0.132→0.132 | 1.00 / 1.000 | 102.468 | 135.891 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.796
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.796
- phase_score: 0.105
- phase_breakdown.insertion_subtask_score: 0.000
- phase_breakdown.reach_above_hole_score: 0.326
- phase_breakdown.reach_entry_score: 0.035

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.382
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.800
- **Median Q (composite search score)**: 0.015
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.352


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":7.13095,"average_solve_count":84.0,"average_success_count":84.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.19505,"approach_1.approach_speed":0.01863,"approach_1.approach_tol":0.00552,"descend_1.descend_speed":0.01327,"descend_1.force_threshold":19.27545,"insert_1.insert_depth":0.12035,"insert_1.insert_speed":0.01091,"insert_1.insert_tol":0.02095,"retract_1.retract_height":0.44401,"retract_1.retract_speed":0.04726,"retract_1.retract_tol":0.01313},"optimized_scores":{"best_composite_score":0.01464,"best_fitness_score":0.37464,"best_task_score":0.78883},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link7","contact_count":832.0,"contact_point_centroid":[0.54219,0.00835,0.07983],"force_p95":283.52088,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":966.36344,"mean_force":196.9338,"phase_index":0.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.41864,0.00438,0.13863]},{"body_a":"peg_socket","body_b":"link7","contact_count":103.0,"contact_point_centroid":[0.5056,0.00151,0.07974],"force_p95":541.75279,"geom_a":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":726.75412,"mean_force":246.78043,"phase_index":0.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.41345,0.00468,0.11963]},{"body_a":"peg_socket","body_b":"link6","contact_count":617.0,"contact_point_centroid":[0.54607,0.00355,0.07955],"force_p95":337.21941,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":463.41581,"mean_force":196.15209,"phase_index":0.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.41474,0.0051,0.13638]},{"body_a":"peg_socket","body_b":"link6","contact_count":998.0,"contact_point_centroid":[0.54612,0.01062,0.07995],"force_p95":284.49781,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":317.20668,"mean_force":263.48012,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.43418,0.01354,0.21664]},{"body_a":"peg_socket","body_b":"link6","contact_count":5.0,"contact_point_centroid":[0.54612,0.01251,0.07996],"force_p95":133.83833,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":140.16152,"mean_force":101.12571,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.45577,0.01587,0.24075]},{"body_a":"peg_socket","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.54612,0.01251,0.07996],"force_p95":56.00811,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":56.00811,"mean_force":56.00811,"phase_index":2.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.45574,0.01586,0.24076]}],"total_contact_groups":6},"final_pose_error":0.28366,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.48616,0.03898,0.025],"final_tcp_position":[0.45582,0.01587,0.24073],"realised_fixture_position":[0.48616,0.03898,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.48616,0.03898,0.08]},"peak_contact_force":966.36344,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.42973,0.0116,0.14409],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.09581,"object_to_goal_dist_start":0.26034,"object_z_max":0.34397,"peak_contact_force":155.17111,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1552.0,"raw_peak_contact_force":966.36344,"subtask_id":"reach_above_hole","tcp_end":[0.39029,0.01138,0.15073],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.48305,0.01595,0.21153],"object_pos_start":[0.42973,0.0116,0.14409],"object_to_goal_dist_end":0.13357,"object_to_goal_dist_start":0.09581,"object_z_max":0.21153,"peak_contact_force":284.68803,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":998.0,"raw_peak_contact_force":317.20668,"subtask_id":"reach_above_hole","tcp_end":[0.45574,0.01586,0.24076],"tcp_start":[0.39029,0.01138,0.15073],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.48305,0.01596,0.21153],"object_pos_start":[0.48305,0.01595,0.21153],"object_to_goal_dist_end":0.13357,"object_to_goal_dist_start":0.13357,"object_z_max":0.21153,"peak_contact_force":56.00811,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1.0,"raw_peak_contact_force":56.00811,"subtask_id":"reach_entry","tcp_end":[0.45574,0.01587,0.24076],"tcp_start":[0.45574,0.01586,0.24076],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":5.0,"n_steps_budget":1000.0,"object_pos_end":[0.48309,0.01596,0.21151],"object_pos_start":[0.48305,0.01596,0.21153],"object_to_goal_dist_end":0.13355,"object_to_goal_dist_start":0.13357,"object_z_max":0.21153,"peak_contact_force":108.54561,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":5.0,"raw_peak_contact_force":140.16152,"subtask_id":"insertion_subtask","tcp_end":[0.45582,0.01587,0.24073],"tcp_start":[0.4558,0.01587,0.24073],"tcp_to_object_dist_end":0.03997,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `622d0229ecd682a86b582a15854ad918b7f35f1e42c4c70c71dc1687a4b64ce2`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":7.72152,"average_solve_count":79.0,"average_success_count":79.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.10434,"approach_1.approach_speed":0.04438,"approach_1.approach_tol":0.00892,"descend_1.descend_speed":0.01605,"descend_1.force_threshold":20.26124,"insert_1.insert_depth":0.08305,"insert_1.insert_speed":0.01178,"insert_1.insert_tol":0.02125,"retract_1.retract_height":0.36864,"retract_1.retract_speed":0.0554,"retract_1.retract_tol":0.01444},"optimized_scores":{"best_composite_score":0.0215,"best_fitness_score":0.3815,"best_task_score":0.79644},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link6","contact_count":867.0,"contact_point_centroid":[0.58878,-0.00708,0.07988],"force_p95":224.55123,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":5421.55566,"mean_force":251.93463,"phase_index":0.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.42225,-0.00356,0.13742]},{"body_a":"peg_socket","body_b":"link7","contact_count":17.0,"contact_point_centroid":[0.56017,-0.00139,0.07712],"force_p95":5175.78187,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":5395.45882,"mean_force":2625.13487,"phase_index":0.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.42343,-0.00276,0.10387]},{"body_a":"peg_socket","body_b":"link7","contact_count":25.0,"contact_point_centroid":[0.51776,0.01365,0.07808],"force_p95":857.63366,"geom_a":"socket_collar_y1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":972.76245,"mean_force":141.87066,"phase_index":0.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.42397,-0.00299,0.10639]},{"body_a":"peg_socket","body_b":"link6","contact_count":991.0,"contact_point_centroid":[0.58957,-0.01191,0.07988],"force_p95":237.12579,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":264.84308,"mean_force":211.26752,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.41389,-0.01177,0.2158]},{"body_a":"peg_socket","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.58931,-0.01113,0.07959],"force_p95":227.45284,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":227.45284,"mean_force":227.45284,"phase_index":2.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.44959,-0.01399,0.25981]},{"body_a":"peg_socket","body_b":"link6","contact_count":3.0,"contact_point_centroid":[0.58934,-0.01116,0.07963],"force_p95":121.84349,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":123.4596,"mean_force":109.25921,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.44963,-0.01397,0.25973]},{"body_a":"peg_socket","body_b":"link7","contact_count":15.0,"contact_point_centroid":[0.51906,-0.04721,0.07909],"force_p95":0.0,"geom_a":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.42356,-0.00257,0.1028]}],"total_contact_groups":7},"final_pose_error":0.27458,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.52962,-0.01705,0.025],"final_tcp_position":[0.44963,-0.01397,0.2596],"realised_fixture_position":[0.52962,-0.01705,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.52962,-0.01705,0.08]},"peak_contact_force":5421.55566,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.44167,-0.01008,0.17812],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.11459,"object_to_goal_dist_start":0.26034,"object_z_max":0.34412,"peak_contact_force":102.27461,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":924.0,"raw_peak_contact_force":5421.55566,"subtask_id":"reach_above_hole","tcp_end":[0.40397,-0.00989,0.19149],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47943,-0.01367,0.23317],"object_pos_start":[0.44167,-0.01008,0.17812],"object_to_goal_dist_end":0.15515,"object_to_goal_dist_start":0.11459,"object_z_max":0.23303,"peak_contact_force":237.3444,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":991.0,"raw_peak_contact_force":264.84308,"subtask_id":"reach_above_hole","tcp_end":[0.44959,-0.01399,0.25981],"tcp_start":[0.40397,-0.00989,0.19149],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.47948,-0.01366,0.23318],"object_pos_start":[0.47943,-0.01367,0.23317],"object_to_goal_dist_end":0.15515,"object_to_goal_dist_start":0.15515,"object_z_max":0.23317,"peak_contact_force":227.45284,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1.0,"raw_peak_contact_force":227.45284,"subtask_id":"reach_entry","tcp_end":[0.44964,-0.01397,0.25981],"tcp_start":[0.44959,-0.01399,0.25981],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.47949,-0.01365,0.23311],"object_pos_start":[0.47948,-0.01366,0.23318],"object_to_goal_dist_end":0.15508,"object_to_goal_dist_start":0.15515,"object_z_max":0.23318,"peak_contact_force":97.01955,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":3.0,"raw_peak_contact_force":123.4596,"subtask_id":"insertion_subtask","tcp_end":[0.44963,-0.01397,0.2596],"tcp_start":[0.44963,-0.01397,0.25966],"tcp_to_object_dist_end":0.03992,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `0f6bb7aab939f458126b1b6d18ae56b7586f021b7d8e0537b172a4bcc3a97854`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":7.70588,"average_solve_count":85.0,"average_success_count":85.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.10356,"approach_1.approach_speed":0.04266,"approach_1.approach_tol":0.00642,"descend_1.descend_speed":0.01587,"descend_1.force_threshold":16.87833,"insert_1.insert_depth":0.12002,"insert_1.insert_speed":0.01111,"insert_1.insert_tol":0.02383,"retract_1.retract_height":0.36582,"retract_1.retract_speed":0.02533,"retract_1.retract_tol":0.01514},"optimized_scores":{"best_composite_score":0.0053,"best_fitness_score":0.3653,"best_task_score":0.79986},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link6","contact_count":900.0,"contact_point_centroid":[0.59552,-0.0071,0.07991],"force_p95":221.51167,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":2259.3609,"mean_force":240.88671,"phase_index":0.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.42819,-0.00352,0.1307]},{"body_a":"peg_socket","body_b":"link6","contact_count":17.0,"contact_point_centroid":[0.56634,0.00662,0.07999],"force_p95":2239.87319,"geom_a":"socket_collar_y1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":2241.06341,"mean_force":1772.15688,"phase_index":0.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.42797,-0.00279,0.11249]},{"body_a":"peg_socket","body_b":"link7","contact_count":5.0,"contact_point_centroid":[0.5667,0.0018,0.07897],"force_p95":1937.33187,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":2007.93552,"mean_force":947.71936,"phase_index":0.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.42747,-0.0023,0.09991]},{"body_a":"peg_socket","body_b":"link7","contact_count":33.0,"contact_point_centroid":[0.52312,0.00701,0.07792],"force_p95":877.0113,"geom_a":"socket_collar_y1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":977.1281,"mean_force":190.29561,"phase_index":0.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.42879,-0.00256,0.10883]},{"body_a":"peg_socket","body_b":"link6","contact_count":993.0,"contact_point_centroid":[0.59646,-0.00644,0.07994],"force_p95":257.01119,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":316.6741,"mean_force":231.89032,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.44674,-0.00845,0.17945]},{"body_a":"peg_socket","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.59642,-0.0052,0.07988],"force_p95":216.2198,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":216.2198,"mean_force":216.2198,"phase_index":2.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.46255,-0.01518,0.20484]},{"body_a":"peg_socket","body_b":"link6","contact_count":3.0,"contact_point_centroid":[0.59644,-0.00515,0.07992],"force_p95":141.80746,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":144.05212,"mean_force":122.49918,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.46261,-0.01513,0.2048]},{"body_a":"peg_socket","body_b":"link7","contact_count":6.0,"contact_point_centroid":[0.52294,-0.05342,0.07982],"force_p95":0.0,"geom_a":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.42699,-0.00245,0.10123]}],"total_contact_groups":8},"final_pose_error":0.25584,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.53648,-0.02339,0.025],"final_tcp_position":[0.46266,-0.0151,0.2048],"realised_fixture_position":[0.53648,-0.02339,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.53648,-0.02339,0.08]},"peak_contact_force":2259.3609,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.46517,-0.0044,0.12997],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.06106,"object_to_goal_dist_start":0.26034,"object_z_max":0.34423,"peak_contact_force":205.48259,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":961.0,"raw_peak_contact_force":2259.3609,"subtask_id":"reach_above_hole","tcp_end":[0.42522,-0.00454,0.13184],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49743,-0.01365,0.18532],"object_pos_start":[0.46517,-0.0044,0.12997],"object_to_goal_dist_end":0.10623,"object_to_goal_dist_start":0.06106,"object_z_max":0.18525,"peak_contact_force":249.36949,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":993.0,"raw_peak_contact_force":316.6741,"subtask_id":"reach_above_hole","tcp_end":[0.46255,-0.01518,0.20484],"tcp_start":[0.42522,-0.00454,0.13184],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.49747,-0.01362,0.1853],"object_pos_start":[0.49743,-0.01365,0.18532],"object_to_goal_dist_end":0.1062,"object_to_goal_dist_start":0.10623,"object_z_max":0.18532,"peak_contact_force":216.2198,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1.0,"raw_peak_contact_force":216.2198,"subtask_id":"reach_entry","tcp_end":[0.46258,-0.01515,0.20481],"tcp_start":[0.46255,-0.01518,0.20484],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.4975,-0.0136,0.1853],"object_pos_start":[0.49747,-0.01362,0.1853],"object_to_goal_dist_end":0.10621,"object_to_goal_dist_start":0.1062,"object_z_max":0.18531,"peak_contact_force":101.83993,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":3.0,"raw_peak_contact_force":144.05212,"subtask_id":"insertion_subtask","tcp_end":[0.46266,-0.0151,0.2048],"tcp_start":[0.46264,-0.01511,0.2048],"tcp_to_object_dist_end":0.03995,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```