## Search State

- **Seed**: 8
- **Iteration**: 2 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 1 | approach → align → descend → insert | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 11 | 0.0456 | 0.85 | ✅ accepted |
| 0 | pull → insert → descend → contact | arc_cartesian | impedance_motion | linear_cartesian | linear_cartesian | impedance_control | impedance_control | position_control | impedance_control | time_limit | pose_tolerance | contact_detected | force_exceeded | 5 | -0.1274 | 0.00 | ✅ accepted |

**Proposal policy**: task_score is 0.85 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.046) — your mutation base

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

- **Composite score**: 0.046
- **task_score** (E): 0.854
- **fitness_score**: 0.406  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.250
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.610

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 0.33 | 1.00 | 0.1023 |
| align_1 | 0.00 | 1.00 | 0.0275 |
| descend_1 | 1.00 | 1.00 | 0.0001 |
| insert_1 | 0.00 | 1.00 | 0.0001 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 0.33 / step_budget | (0.500, -0.000, 0.301)→(0.473, -0.003, 0.203) | (0.504, -0.000, 0.340)→(0.506, -0.002, 0.181) | 0.260→0.102 | 1.00 / 1.000 | 308.909 | 1519.974 |
| align_1 | align | 0.00 / step_budget | (0.473, -0.003, 0.203)→(0.467, -0.029, 0.209) | (0.506, -0.002, 0.181)→(0.499, -0.023, 0.187) | 0.102→0.111 | 1.00 / 1.000 | 277.436 | 340.008 |
| descend_1 | descend | 1.00 / force_exceeded | (0.467, -0.029, 0.209)→(0.467, -0.029, 0.209) | (0.499, -0.023, 0.187)→(0.499, -0.023, 0.187) | 0.111→0.111 | 1.00 / 1.000 | 169.213 | 184.730 |
| insert_1 | insert | 0.00 / guard_failure | (0.467, -0.029, 0.209)→(0.467, -0.029, 0.209) | (0.499, -0.023, 0.187)→(0.499, -0.023, 0.187) | 0.111→0.111 | 1.00 / 1.000 | 115.949 | 139.660 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.868
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.868
- phase_score: 0.103
- phase_breakdown.insertion_subtask_score: 0.069
- phase_breakdown.reach_above_hole_score: 0.163
- phase_breakdown.reach_entry_score: 0.098

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.409
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.868
- **Median Q (composite search score)**: 0.048
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.378


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":7.60494,"average_solve_count":81.0,"average_success_count":81.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.align_offset_z":0.0498,"align_1.align_speed":0.03125,"align_1.align_tol":0.00806,"approach_1.approach_height":0.11786,"approach_1.approach_speed":0.05132,"approach_1.pose_tol":0.01169,"descend_1.descend_speed":0.01729,"descend_1.force_threshold":13.22877,"insert_1.insert_depth":0.07265,"insert_1.insert_speed":0.01473,"insert_1.insert_tol":0.01494},"optimized_scores":{"best_composite_score":0.04036,"best_fitness_score":0.40036,"best_task_score":0.83353},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":12.0,"contact_point_centroid":[0.44901,0.00445,0.0785],"force_p95":1233.14345,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":2740.31877,"mean_force":228.3599,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.44498,0.00376,0.09124]},{"body_a":"attachment","body_b":"peg_socket","contact_count":10.0,"contact_point_centroid":[0.45666,0.00377,0.07905],"force_p95":1688.29232,"geom_a":"peg_tip","geom_b":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":2286.73213,"mean_force":324.3598,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.44638,0.00378,0.09068]},{"body_a":"peg_socket","body_b":"link7","contact_count":331.0,"contact_point_centroid":[0.54552,0.01075,0.07963],"force_p95":378.41164,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":939.92487,"mean_force":291.95903,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.44501,0.00705,0.16442]},{"body_a":"peg_socket","body_b":"link6","contact_count":1000.0,"contact_point_centroid":[0.54612,0.02333,0.07997],"force_p95":313.93794,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":354.93099,"mean_force":309.35382,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.46933,0.01192,0.21287]},{"body_a":"peg_socket","body_b":"link6","contact_count":557.0,"contact_point_centroid":[0.54611,0.01363,0.07993],"force_p95":327.72966,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":349.13622,"mean_force":314.0775,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.46061,0.01511,0.20043]},{"body_a":"peg_socket","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.54616,0.02541,0.08],"force_p95":110.34385,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":110.34385,"mean_force":110.34385,"phase_index":2.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47018,0.00456,0.21532]},{"body_a":"peg_socket","body_b":"link6","contact_count":3.0,"contact_point_centroid":[0.54614,0.02551,0.07998],"force_p95":72.74339,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":73.39118,"mean_force":68.09527,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.47018,0.00464,0.21526]}],"total_contact_groups":7},"final_pose_error":0.21129,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.48616,0.03898,0.025],"final_tcp_position":[0.47018,0.00468,0.21522],"realised_fixture_position":[0.48616,0.03898,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.48616,0.03898,0.08]},"peak_contact_force":2740.31877,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49865,0.01988,0.18287],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.10479,"object_to_goal_dist_start":0.26034,"object_z_max":0.34436,"peak_contact_force":325.2086,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":910.0,"raw_peak_contact_force":2740.31877,"subtask_id":"reach_above_hole","tcp_end":[0.46919,0.01934,0.20992],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.4986,0.0101,0.18771],"object_pos_start":[0.49865,0.01988,0.18287],"object_to_goal_dist_end":0.10819,"object_to_goal_dist_start":0.10479,"object_z_max":0.18771,"peak_contact_force":306.5821,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":1000.0,"raw_peak_contact_force":354.93099,"subtask_id":"reach_entry","tcp_end":[0.47018,0.00456,0.21532],"tcp_start":[0.46919,0.01934,0.20992],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":2.0,"n_steps_budget":1000.0,"object_pos_end":[0.49859,0.01015,0.18768],"object_pos_start":[0.4986,0.0101,0.18771],"object_to_goal_dist_end":0.10817,"object_to_goal_dist_start":0.10819,"object_z_max":0.18771,"peak_contact_force":63.79156,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1.0,"raw_peak_contact_force":110.34385,"subtask_id":"insertion_subtask","tcp_end":[0.47018,0.00461,0.21529],"tcp_start":[0.47018,0.00456,0.21532],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.49859,0.01017,0.18766],"object_pos_start":[0.49859,0.01015,0.18768],"object_to_goal_dist_end":0.10815,"object_to_goal_dist_start":0.10817,"object_z_max":0.18768,"peak_contact_force":63.9814,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":3.0,"raw_peak_contact_force":73.39118,"subtask_id":"insertion_subtask","tcp_end":[0.47018,0.00468,0.21522],"tcp_start":[0.47017,0.00466,0.21524],"tcp_to_object_dist_end":0.03997,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `622d0229ecd682a86b582a15854ad918b7f35f1e42c4c70c71dc1687a4b64ce2`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":7.67143,"average_solve_count":70.0,"average_success_count":70.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.align_offset_z":0.03121,"align_1.align_speed":0.02363,"align_1.align_tol":0.00961,"approach_1.approach_height":0.11061,"approach_1.approach_speed":0.09192,"approach_1.pose_tol":0.00818,"descend_1.descend_speed":0.0118,"descend_1.force_threshold":15.88103,"insert_1.insert_depth":0.11851,"insert_1.insert_speed":0.01548,"insert_1.insert_tol":0.01829},"optimized_scores":{"best_composite_score":0.04754,"best_fitness_score":0.40754,"best_task_score":0.8601},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":5.0,"contact_point_centroid":[0.47013,-0.00248,0.07946],"force_p95":965.17688,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":995.44758,"mean_force":511.15581,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.46032,-0.00249,0.09132]},{"body_a":"peg_socket","body_b":"link7","contact_count":31.0,"contact_point_centroid":[0.56452,-0.00261,0.07945],"force_p95":750.53197,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":963.69216,"mean_force":275.68131,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.44644,-0.00315,0.11061]},{"body_a":"peg_socket","body_b":"link6","contact_count":601.0,"contact_point_centroid":[0.58951,-0.00816,0.07985],"force_p95":294.35674,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":398.64289,"mean_force":248.3838,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.45771,-0.00579,0.1732]},{"body_a":"peg_socket","body_b":"link6","contact_count":992.0,"contact_point_centroid":[0.58956,-0.0112,0.07988],"force_p95":285.67384,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":342.63951,"mean_force":242.2146,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.45436,-0.02419,0.19227]},{"body_a":"peg_socket","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.58946,-0.0169,0.07976],"force_p95":221.8403,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":221.8403,"mean_force":221.8403,"phase_index":2.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.46802,-0.04348,0.21289]},{"body_a":"peg_socket","body_b":"link6","contact_count":3.0,"contact_point_centroid":[0.5895,-0.01703,0.07982],"force_p95":215.71635,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":216.85492,"mean_force":202.73256,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.46811,-0.04354,0.21297]},{"body_a":"peg_socket","body_b":"link7","contact_count":14.0,"contact_point_centroid":[0.54488,0.01324,0.07919],"force_p95":119.85763,"geom_a":"socket_collar_y1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":142.49669,"mean_force":27.49549,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.44833,-0.00296,0.09918]}],"total_contact_groups":7},"final_pose_error":0.26035,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.52962,-0.01705,0.025],"final_tcp_position":[0.4682,-0.04358,0.21309],"realised_fixture_position":[0.52962,-0.01705,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.52962,-0.01705,0.08]},"peak_contact_force":995.44758,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":723.0,"n_steps_budget":810.0,"object_pos_end":[0.51011,-0.01124,0.1832],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.1043,"object_to_goal_dist_start":0.26034,"object_z_max":0.34465,"peak_contact_force":314.29166,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":651.0,"raw_peak_contact_force":995.44758,"subtask_id":"reach_above_hole","tcp_end":[0.47654,-0.01172,0.20495],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50094,-0.03725,0.19103],"object_pos_start":[0.51011,-0.01124,0.1832],"object_to_goal_dist_end":0.11712,"object_to_goal_dist_start":0.1043,"object_z_max":0.19097,"peak_contact_force":265.66938,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":992.0,"raw_peak_contact_force":342.63951,"subtask_id":"reach_entry","tcp_end":[0.46802,-0.04348,0.21289],"tcp_start":[0.47654,-0.01172,0.20495],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.50098,-0.03726,0.19107],"object_pos_start":[0.50094,-0.03725,0.19103],"object_to_goal_dist_end":0.11716,"object_to_goal_dist_start":0.11712,"object_z_max":0.19103,"peak_contact_force":221.8403,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1.0,"raw_peak_contact_force":221.8403,"subtask_id":"insertion_subtask","tcp_end":[0.46806,-0.04348,0.21293],"tcp_start":[0.46802,-0.04348,0.21289],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.50104,-0.03733,0.19112],"object_pos_start":[0.50098,-0.03726,0.19107],"object_to_goal_dist_end":0.11723,"object_to_goal_dist_start":0.11716,"object_z_max":0.19118,"peak_contact_force":205.46923,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":3.0,"raw_peak_contact_force":216.85492,"subtask_id":"insertion_subtask","tcp_end":[0.4682,-0.04358,0.21309],"tcp_start":[0.46816,-0.04355,0.21303],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `0f6bb7aab939f458126b1b6d18ae56b7586f021b7d8e0537b172a4bcc3a97854`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":7.66154,"average_solve_count":65.0,"average_success_count":65.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.align_offset_z":0.03486,"align_1.align_speed":0.01001,"align_1.align_tol":0.00998,"approach_1.approach_height":0.13162,"approach_1.approach_speed":0.09963,"approach_1.pose_tol":0.00939,"descend_1.descend_speed":0.02935,"descend_1.force_threshold":6.35973,"insert_1.insert_depth":0.07962,"insert_1.insert_speed":0.0123,"insert_1.insert_tol":0.02473},"optimized_scores":{"best_composite_score":0.049,"best_fitness_score":0.409,"best_task_score":0.86786},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":2.0,"contact_point_centroid":[0.4765,-0.00431,0.07995],"force_p95":822.86514,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":824.15507,"mean_force":811.25572,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.46793,-0.00431,0.09262]},{"body_a":"peg_socket","body_b":"link7","contact_count":26.0,"contact_point_centroid":[0.54432,0.00745,0.0777],"force_p95":731.7624,"geom_a":"socket_collar_y1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":782.72568,"mean_force":185.42993,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4491,-0.00487,0.10292]},{"body_a":"peg_socket","body_b":"link7","contact_count":33.0,"contact_point_centroid":[0.56903,-0.00441,0.0785],"force_p95":264.73074,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":372.67217,"mean_force":60.74991,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.44947,-0.00493,0.10731]},{"body_a":"peg_socket","body_b":"link6","contact_count":436.0,"contact_point_centroid":[0.59592,-0.01164,0.07979],"force_p95":289.07946,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":370.27341,"mean_force":247.19173,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.45978,-0.00889,0.16321]},{"body_a":"peg_socket","body_b":"link6","contact_count":994.0,"contact_point_centroid":[0.59644,-0.01572,0.0799],"force_p95":272.60285,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":322.45476,"mean_force":232.54002,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.45296,-0.02803,0.18205]},{"body_a":"peg_socket","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.59631,-0.01911,0.07968],"force_p95":222.0059,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":222.0059,"mean_force":222.0059,"phase_index":2.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.46217,-0.04661,0.19921]},{"body_a":"peg_socket","body_b":"link6","contact_count":3.0,"contact_point_centroid":[0.59633,-0.01925,0.07971],"force_p95":125.28709,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":128.73405,"mean_force":100.4649,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.46221,-0.0467,0.19926]},{"body_a":"peg_socket","body_b":"link7","contact_count":12.0,"contact_point_centroid":[0.54463,-0.0535,0.07934],"force_p95":0.0,"geom_a":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.44814,-0.00479,0.09705]}],"total_contact_groups":8},"final_pose_error":0.21362,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.53648,-0.02339,0.025],"final_tcp_position":[0.46224,-0.04682,0.19931],"realised_fixture_position":[0.53648,-0.02339,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.53648,-0.02339,0.08]},"peak_contact_force":824.15507,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":543.0,"n_steps_budget":630.0,"object_pos_end":[0.50793,-0.01542,0.17617],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.09772,"object_to_goal_dist_start":0.26034,"object_z_max":0.34483,"peak_contact_force":287.22798,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":509.0,"raw_peak_contact_force":824.15507,"subtask_id":"reach_above_hole","tcp_end":[0.4726,-0.01566,0.19492],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49721,-0.0406,0.18086],"object_pos_start":[0.50793,-0.01542,0.17617],"object_to_goal_dist_end":0.10876,"object_to_goal_dist_start":0.09772,"object_z_max":0.1808,"peak_contact_force":260.05786,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":994.0,"raw_peak_contact_force":322.45476,"subtask_id":"reach_entry","tcp_end":[0.46217,-0.04661,0.19921],"tcp_start":[0.4726,-0.01566,0.19492],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.49723,-0.04064,0.18089],"object_pos_start":[0.49721,-0.0406,0.18086],"object_to_goal_dist_end":0.1088,"object_to_goal_dist_start":0.10876,"object_z_max":0.18086,"peak_contact_force":222.0059,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1.0,"raw_peak_contact_force":222.0059,"subtask_id":"insertion_subtask","tcp_end":[0.46219,-0.04664,0.19923],"tcp_start":[0.46217,-0.04661,0.19921],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.49725,-0.04071,0.18091],"object_pos_start":[0.49723,-0.04064,0.18089],"object_to_goal_dist_end":0.10885,"object_to_goal_dist_start":0.1088,"object_z_max":0.18094,"peak_contact_force":78.39623,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":3.0,"raw_peak_contact_force":128.73405,"subtask_id":"insertion_subtask","tcp_end":[0.46224,-0.04682,0.19931],"tcp_start":[0.46223,-0.04676,0.19929],"tcp_to_object_dist_end":0.04002,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```