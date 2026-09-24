## Search State

- **Seed**: 7
- **Iteration**: 12 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 11 | approach → descend → grasp → retract → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | position_control | admittance_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 10 | -0.2702 | 0.35 | ❌ rejected |
| 10 | approach → descend → grasp → retract → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | position_control | admittance_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 9 | 0.3273 | 0.90 | ✅ accepted |
| 9 | approach → descend → grasp → retract → approach → align → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | admittance_control | admittance_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.1107 | 0.85 | ❌ rejected |
| 8 | approach → descend → grasp → retract → approach → align → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | position_control | admittance_control | admittance_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.0358 | 0.83 | ❌ rejected |
| 7 | approach → descend → grasp → retract → approach → align → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | position_control | admittance_control | admittance_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 9 | -0.0423 | 0.89 | ✅ accepted |

**Proposal policy**: task_score is 0.35 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.270) — your mutation base

```yaml
skill: peg_insert
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: approach_peg
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.05
  weight: 0.2
- id: approach_hole
  offset:
  - 0.0
  - 0.0
  - 0.05
  weight: 0.3
- id: insert_task
  target_entity: object
  weight: 0.5
phases:
- id: approach_peg
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.05
    tolerance: 0.005
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: approach_peg
- id: descend_to_peg
  type: descend
  generator: linear_cartesian
  control: force_threshold_switch
  termination: force_exceeded
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.005
  parameters:
    contact_force_threshold:
      type: scalar
      range:
      - 2.0
      - 15.0
      default: 5.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    descend_speed:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.003
    - 0.003
    - 0.0
- id: grasp_peg
  type: grasp
  control: position_control
  termination: grasp_success
  end_effector_action: force_grasp
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
  guards:
  - id: grasp_check
    when: after_phase
    predicate: bilateral_grasp
    threshold: 1.0
    on_failure: retry
  retries:
    max_attempts: 3
    strategy: offset_target
    offset:
    - 0.002
    - 0.002
    - 0.0
- id: lift_peg
  type: retract
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.05
    tolerance: 0.005
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.02
      - 0.08
      default: 0.05
      binds_to:
      - path: target.offset.z
        mode: replace
- id: approach_hole
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
    - 0.05
    tolerance: 0.005
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: approach_hole
- id: descend_insert
  type: descend
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
      distance: 0.1
      axis: world_z
      mode: replace_offset_projection
      sign: negative
    tolerance: 0.005
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: world_z
      tolerance: 0.1
  parameters:
    force_guard_threshold:
      type: scalar
      range:
      - 50.0
      - 300.0
      default: 200.0
      binds_to:
      - path: guards.insert_force.threshold
        mode: replace
    insert_offset_x:
      type: scalar
      range:
      - -0.04
      - 0.04
      default: 0.0
      binds_to:
      - path: target.offset.x
        mode: add
    insert_offset_y:
      type: scalar
      range:
      - -0.04
      - 0.04
      default: 0.0
      binds_to:
      - path: target.offset.y
        mode: add
    insertion_depth:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.1
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
  guards:
  - id: insert_force
    when: during_phase
    predicate: force_below
    threshold: 200.0
    on_failure: retry
  retries:
    max_attempts: 3
    strategy: offset_target
    offset:
    - 0.005
    - 0.005
    - 0.0
  subtask_id: insert_task

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_peg** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.05], tolerance=0.005
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_peg** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0], tolerance=0.005
  - parameter_bindings:
    - contact_force_threshold: status=consumed; consumers=termination.force_threshold (replace)
    - descend_speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=2, strategy=offset_target, offset=[0.003, 0.003, 0.0]
- **grasp_peg** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
  - guards:
    - id=grasp_check, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=1.0
  - retries: max_attempts=3, strategy=offset_target, offset=[0.002, 0.002, 0.0]
- **lift_peg** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.05], tolerance=0.005
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
- **approach_hole** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.05], tolerance=0.005
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
- **descend_insert** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.1, mode=replace_offset_projection, sign=negative}, tolerance=0.005
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=world_z, tolerance=0.1
  - parameter_bindings:
    - force_guard_threshold: status=consumed; consumers=guards.insert_force.threshold (replace)
    - insert_offset_x: status=consumed; consumers=target.offset.x (add)
    - insert_offset_y: status=consumed; consumers=target.offset.y (add)
    - insertion_depth: status=consumed; consumers=target.offset_along_axis.distance (replace)
  - guards:
    - id=insert_force, when=during_phase, predicate=force_below, on_failure=retry, threshold=200.0
  - retries: max_attempts=3, strategy=offset_target, offset=[0.005, 0.005, 0.0]

## Design Metrics

- **Composite score**: -0.270
- **task_score** (E): 0.350
- **fitness_score**: 0.350  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.620

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_peg | 0.67 | 0.00 | 0.0391 |
| descend_to_peg | 0.00 | 0.00 | 0.0318 |
| grasp_peg | 1.00 | 0.00 | 0.0000 |
| lift_peg | 1.00 | 0.00 | 0.0318 |
| approach_hole | 0.00 | 0.67 | 0.2585 |
| descend_insert | 0.00 | 1.00 | 0.0020 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_peg | approach | 0.67 / step_budget | (0.500, -0.000, 0.301)→(0.500, -0.000, 0.340) | (0.504, -0.000, 0.340)→(0.502, -0.000, 0.380) | 0.260→0.300 | 0.00 / 0.000 | 0.000 | 0.000 |
| descend_to_peg | descend | 0.00 / step_budget | (0.500, -0.000, 0.340)→(0.500, -0.000, 0.371) | (0.502, -0.000, 0.380)→(0.500, -0.000, 0.411) | 0.300→0.331 | 0.00 / 0.000 | 0.000 | 0.000 |
| grasp_peg | grasp | 1.00 / step_budget | (0.497, -0.000, 0.363)→(0.497, -0.000, 0.363) | (0.500, -0.000, 0.411)→(0.498, -0.000, 0.403) | 0.331→0.323 | 0.00 / 0.000 | 0.000 | 0.000 |
| lift_peg | retract | 1.00 / step_budget | (0.497, -0.000, 0.363)→(0.496, -0.000, 0.395) | (0.498, -0.000, 0.403)→(0.494, -0.000, 0.435) | 0.323→0.355 | 0.00 / 0.000 | 0.000 | 0.000 |
| approach_hole | approach | 0.00 / step_budget | (0.496, -0.000, 0.395)→(0.586, 0.059, 0.226) | (0.494, -0.000, 0.435)→(0.581, 0.065, 0.208) | 0.355→0.233 | 0.67 / 0.667 | 177.188 | 885.322 |
| descend_insert | descend | 0.00 / guard_failure | (0.466, 0.105, 0.153)→(0.464, 0.105, 0.152) | (0.581, 0.065, 0.208)→(0.481, 0.117, 0.146) | 0.233→0.205 | 1.00 / 1.000 | 459.595 | 765.491 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.591
- alignment_error: None
- force_efficiency: 0.000

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.591
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.591
- **Median Q (composite search score)**: -0.269
- **K-run variance**: 0.0389
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.316


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `0c4288e4b4f4eb50f7d141bdaea44f8ed4eecfe7429f8148c247811f0f5250bc`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `2ae90e10c3e712e9da92b27bc0ded08b6d103e49e03139a26a0fa45d3ac81c97`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":85.0,"average_failure_rate":0.41463,"average_mean_iterations":87.26341,"average_solve_count":205.0,"average_success_count":120.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_hole.speed":0.11279,"approach_peg.speed":0.0338,"descend_insert.force_guard_threshold":340.23724,"descend_insert.insert_offset_x":-0.00483,"descend_insert.insert_offset_y":-0.01522,"descend_insert.insertion_depth":0.11345,"descend_insert.insertion_speed":0.02498,"descend_to_peg.contact_force_threshold":14.99703,"descend_to_peg.descend_speed":0.10648,"lift_peg.lift_height":0.0536},"optimized_scores":{"best_composite_score":-0.51228,"best_fitness_score":0.10772,"best_task_score":0.10772},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"world","contact_count":4.0,"contact_point_centroid":[0.49091,0.20232,-0.0035],"force_p95":1558.31799,"geom_a":"peg_tip","geom_b":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1620.75455,"mean_force":1160.84922,"phase_index":5.0,"phase_name":"descend_insert","phase_type":"descend","tcp_position_centroid":[0.48305,0.19072,-0.00165]},{"body_a":"peg_socket","body_b":"link5","contact_count":328.0,"contact_point_centroid":[0.56996,0.09177,0.07994],"force_p95":320.94032,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":461.4534,"mean_force":240.65825,"phase_index":4.0,"phase_name":"approach_hole","phase_type":"approach","tcp_position_centroid":[0.80515,0.02153,0.13004]},{"body_a":"peg_socket","body_b":"link6","contact_count":99.0,"contact_point_centroid":[0.56996,0.03494,0.07996],"force_p95":274.34372,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":308.21256,"mean_force":218.59738,"phase_index":4.0,"phase_name":"approach_hole","phase_type":"approach","tcp_position_centroid":[0.81465,0.02614,0.12457]},{"body_a":"peg_socket","body_b":"link5","contact_count":1.0,"contact_point_centroid":[0.56995,0.09178,0.07996],"force_p95":29.83186,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":29.83186,"mean_force":29.83186,"phase_index":5.0,"phase_name":"descend_insert","phase_type":"descend","tcp_position_centroid":[0.82004,0.02894,0.11947]}],"total_contact_groups":4},"final_pose_error":0.18197,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.51001,0.03178,0.025],"final_tcp_position":[0.46608,0.19233,-0.00721],"realised_fixture_position":[0.51001,0.03178,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.51001,0.03178,0.08]},"peak_contact_force":1620.75455,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50154,-1e-05,0.39158],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.31159,"object_to_goal_dist_start":0.26034,"object_z_max":0.39152,"peak_contact_force":0.0,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach_peg","tcp_end":[0.50072,-2e-05,0.35159],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":513.0,"n_steps_budget":600.0,"object_pos_end":[0.49872,-0.0,0.42337],"object_pos_start":[0.50154,-1e-05,0.39158],"object_to_goal_dist_end":0.34337,"object_to_goal_dist_start":0.31159,"object_z_max":0.42331,"peak_contact_force":0.0,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.50006,-2e-05,0.38339],"tcp_start":[0.50072,-2e-05,0.35159],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":200.0,"n_steps_budget":50.0,"object_pos_end":[0.49701,-0.0,0.41534],"object_pos_start":[0.49872,-0.0,0.42337],"object_to_goal_dist_end":0.33535,"object_to_goal_dist_start":0.34337,"object_z_max":0.42338,"peak_contact_force":0.0,"phase_name":"grasp_peg","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.49765,-4e-05,0.37534],"tcp_start":[0.49765,-4e-05,0.37534],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":542.0,"n_steps_budget":600.0,"object_pos_end":[0.49275,0.0,0.45955],"object_pos_start":[0.49701,-0.0,0.41534],"object_to_goal_dist_end":0.37962,"object_to_goal_dist_start":0.33535,"object_z_max":0.45948,"peak_contact_force":0.0,"phase_name":"lift_peg","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.49656,-5e-05,0.41973],"tcp_start":[0.49765,-4e-05,0.37534],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.78239,0.02782,0.13294],"object_pos_start":[0.49275,0.0,0.45955],"object_to_goal_dist_end":0.28866,"object_to_goal_dist_start":0.37962,"object_z_max":0.47568,"peak_contact_force":256.45563,"phase_name":"approach_hole","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":427.0,"raw_peak_contact_force":461.4534,"subtask_id":"approach_hole","tcp_end":[0.82004,0.02894,0.11947],"tcp_start":[0.49656,-5e-05,0.41973],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":146.0,"n_steps_budget":1000.0,"object_pos_end":[0.49435,0.20225,0.0367],"object_pos_start":[0.78239,0.02782,0.13294],"object_to_goal_dist_end":0.20691,"object_to_goal_dist_start":0.28866,"object_z_max":0.1878,"peak_contact_force":808.77997,"phase_name":"descend_insert","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5.0,"raw_peak_contact_force":1620.75455,"subtask_id":"insert_task","tcp_end":[0.46608,0.19233,-0.00721],"tcp_start":[0.47147,0.19178,-0.00594],"tcp_to_object_dist_end":0.05316,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `02e4649f08bda5439eae760bf0bc4b5a6b47c91c93317c6956c2509043be6196`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":5.21711,"average_solve_count":152.0,"average_success_count":152.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_hole.speed":0.11146,"approach_peg.speed":0.01277,"descend_insert.force_guard_threshold":436.43835,"descend_insert.insert_offset_x":0.01903,"descend_insert.insert_offset_y":-0.002,"descend_insert.insertion_depth":0.13644,"descend_insert.insertion_speed":0.02229,"descend_to_peg.contact_force_threshold":11.9657,"descend_to_peg.descend_speed":0.14817,"lift_peg.lift_height":0.02241},"optimized_scores":{"best_composite_score":-0.02945,"best_fitness_score":0.59055,"best_task_score":0.59055},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link6","contact_count":868.0,"contact_point_centroid":[0.54605,0.02299,0.07977],"force_p95":295.00446,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":894.96304,"mean_force":256.43605,"phase_index":4.0,"phase_name":"approach_hole","phase_type":"approach","tcp_position_centroid":[0.42991,-0.02437,0.21702]},{"body_a":"peg_socket","body_b":"link5","contact_count":5.0,"contact_point_centroid":[0.54615,0.08599,0.07998],"force_p95":497.02952,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":511.91767,"mean_force":280.22055,"phase_index":5.0,"phase_name":"descend_insert","phase_type":"descend","tcp_position_centroid":[0.47928,-0.10422,0.1994]},{"body_a":"peg_socket","body_b":"link6","contact_count":842.0,"contact_point_centroid":[0.54607,0.01057,0.0799],"force_p95":344.95275,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":429.19565,"mean_force":297.04965,"phase_index":5.0,"phase_name":"descend_insert","phase_type":"descend","tcp_position_centroid":[0.47028,-0.08758,0.21192]},{"body_a":"peg_socket","body_b":"link6","contact_count":17.0,"contact_point_centroid":[0.51583,0.00641,0.07852],"force_p95":0.0,"geom_a":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0,"mean_force":0.0,"phase_index":4.0,"phase_name":"approach_hole","phase_type":"approach","tcp_position_centroid":[0.38577,-0.02607,0.15237]},{"body_a":"peg_socket","body_b":"link7","contact_count":11.0,"contact_point_centroid":[0.50451,0.00508,0.07928],"force_p95":0.0,"geom_a":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0,"mean_force":0.0,"phase_index":4.0,"phase_name":"approach_hole","phase_type":"approach","tcp_position_centroid":[0.38504,-0.02613,0.14847]}],"total_contact_groups":5},"final_pose_error":0.29347,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.48616,0.03898,0.025],"final_tcp_position":[0.4795,-0.10437,0.19945],"realised_fixture_position":[0.48616,0.03898,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.48616,0.03898,0.08]},"peak_contact_force":894.96304,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50193,-1e-05,0.36328],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.28328,"object_to_goal_dist_start":0.26034,"object_z_max":0.36325,"peak_contact_force":0.0,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach_peg","tcp_end":[0.49917,-2e-05,0.32337],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":513.0,"n_steps_budget":600.0,"object_pos_end":[0.50068,-1e-05,0.39507],"object_pos_start":[0.50193,-1e-05,0.36328],"object_to_goal_dist_end":0.31508,"object_to_goal_dist_start":0.28328,"object_z_max":0.39502,"peak_contact_force":0.0,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.50006,-3e-05,0.35508],"tcp_start":[0.49917,-2e-05,0.32337],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":200.0,"n_steps_budget":50.0,"object_pos_end":[0.49858,-2e-05,0.387],"object_pos_start":[0.50068,-1e-05,0.39507],"object_to_goal_dist_end":0.307,"object_to_goal_dist_start":0.31508,"object_z_max":0.39509,"peak_contact_force":0.0,"phase_name":"grasp_peg","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.49723,-6e-05,0.34702],"tcp_start":[0.49723,-6e-05,0.34702],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":455.0,"n_steps_budget":600.0,"object_pos_end":[0.49603,-3e-05,0.40246],"object_pos_start":[0.49858,-2e-05,0.387],"object_to_goal_dist_end":0.32249,"object_to_goal_dist_start":0.307,"object_z_max":0.40243,"peak_contact_force":0.0,"phase_name":"lift_peg","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.49563,-7e-05,0.36247],"tcp_start":[0.49723,-6e-05,0.34702],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.4943,-0.02188,0.20766],"object_pos_start":[0.49603,-3e-05,0.40246],"object_to_goal_dist_end":0.12964,"object_to_goal_dist_start":0.32249,"object_z_max":0.40921,"peak_contact_force":275.10817,"phase_name":"approach_hole","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":896.0,"raw_peak_contact_force":894.96304,"subtask_id":"approach_hole","tcp_end":[0.46955,-0.03438,0.23649],"tcp_start":[0.49563,-7e-05,0.36247],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":877.0,"n_steps_budget":1000.0,"object_pos_end":[0.50513,-0.08496,0.17562],"object_pos_start":[0.4943,-0.02188,0.20766],"object_to_goal_dist_end":0.12801,"object_to_goal_dist_start":0.12964,"object_z_max":0.20766,"peak_contact_force":434.05125,"phase_name":"descend_insert","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":847.0,"raw_peak_contact_force":511.91767,"subtask_id":"insert_task","tcp_end":[0.4795,-0.10437,0.19945],"tcp_start":[0.4794,-0.10437,0.19929],"tcp_to_object_dist_end":0.04003,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `7363bc0b3fa7329ef53220378736f8cf8ba8a5eef8ffe48ac32070ac53331cd4`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":5.77305,"average_solve_count":141.0,"average_success_count":141.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_hole.speed":0.03317,"approach_peg.speed":0.0283,"descend_insert.force_guard_threshold":158.08186,"descend_insert.insert_offset_x":0.00789,"descend_insert.insert_offset_y":0.01827,"descend_insert.insertion_depth":0.09419,"descend_insert.insertion_speed":0.02819,"descend_to_peg.contact_force_threshold":2.04435,"descend_to_peg.descend_speed":0.15417,"lift_peg.lift_height":0.04401},"optimized_scores":{"best_composite_score":-0.26886,"best_fitness_score":0.35114,"best_task_score":0.35114},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"link1","body_b":"link5","contact_count":49.0,"contact_point_centroid":[0.02475,-0.08744,0.25906],"force_p95":1019.01874,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1299.55047,"mean_force":374.64514,"phase_index":4.0,"phase_name":"approach_hole","phase_type":"approach","tcp_position_centroid":[0.10674,-0.01076,0.04319]},{"body_a":"attachment","body_b":"link0","contact_count":7.0,"contact_point_centroid":[-0.06693,-0.07775,0.03115],"force_p95":806.96151,"geom_a":"peg_tip","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":846.40248,"mean_force":535.61622,"phase_index":4.0,"phase_name":"approach_hole","phase_type":"approach","tcp_position_centroid":[-0.0693,-0.08703,0.02053]},{"body_a":"world","body_b":"link6","contact_count":11.0,"contact_point_centroid":[0.41716,0.25297,-0.00015],"force_p95":157.14801,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":163.80097,"mean_force":106.09802,"phase_index":5.0,"phase_name":"descend_insert","phase_type":"descend","tcp_position_centroid":[0.44787,0.22678,0.2645]}],"total_contact_groups":3},"final_pose_error":0.36972,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.52962,-0.01705,0.025],"final_tcp_position":[0.44771,0.22702,0.26445],"realised_fixture_position":[0.52962,-0.01705,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.52962,-0.01705,0.08]},"peak_contact_force":1299.55047,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50165,-1e-05,0.38392],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.30392,"object_to_goal_dist_start":0.26034,"object_z_max":0.38386,"peak_contact_force":0.0,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach_peg","tcp_end":[0.5003,-2e-05,0.34394],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":513.0,"n_steps_budget":600.0,"object_pos_end":[0.49927,-0.0,0.41571],"object_pos_start":[0.50165,-1e-05,0.38392],"object_to_goal_dist_end":0.33571,"object_to_goal_dist_start":0.30392,"object_z_max":0.41566,"peak_contact_force":0.0,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.50007,-2e-05,0.37572],"tcp_start":[0.5003,-2e-05,0.34394],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":200.0,"n_steps_budget":50.0,"object_pos_end":[0.49745,-1e-05,0.40767],"object_pos_start":[0.49927,-0.0,0.41571],"object_to_goal_dist_end":0.32768,"object_to_goal_dist_start":0.33571,"object_z_max":0.41573,"peak_contact_force":0.0,"phase_name":"grasp_peg","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.49754,-5e-05,0.36767],"tcp_start":[0.49754,-5e-05,0.36767],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":513.0,"n_steps_budget":600.0,"object_pos_end":[0.49375,-1e-05,0.44315],"object_pos_start":[0.49745,-1e-05,0.40767],"object_to_goal_dist_end":0.36321,"object_to_goal_dist_start":0.32768,"object_z_max":0.44309,"peak_contact_force":0.0,"phase_name":"lift_peg","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.49631,-5e-05,0.40323],"tcp_start":[0.49754,-5e-05,0.36767],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.46619,0.18862,0.28375],"object_pos_start":[0.49375,-1e-05,0.44315],"object_to_goal_dist_end":0.2797,"object_to_goal_dist_start":0.36321,"object_z_max":0.44315,"peak_contact_force":0.0,"phase_name":"approach_hole","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":56.0,"raw_peak_contact_force":1299.55047,"subtask_id":"approach_hole","tcp_end":[0.46925,0.18103,0.3229],"tcp_start":[0.49631,-5e-05,0.40323],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":621.0,"n_steps_budget":1000.0,"object_pos_end":[0.44405,0.23434,0.22529],"object_pos_start":[0.46619,0.18862,0.28375],"object_to_goal_dist_end":0.28135,"object_to_goal_dist_start":0.2797,"object_z_max":0.28375,"peak_contact_force":135.95238,"phase_name":"descend_insert","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":11.0,"raw_peak_contact_force":163.80097,"subtask_id":"insert_task","tcp_end":[0.44771,0.22702,0.26445],"tcp_start":[0.44782,0.22684,0.26439],"tcp_to_object_dist_end":0.04001,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```