## Search State

- **Seed**: 7
- **Iteration**: 8 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 7 | approach → descend → grasp → retract → approach → align → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | position_control | admittance_control | admittance_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 9 | -0.0423 | 0.89 | ✅ accepted |
| 6 | approach → descend → grasp → retract → approach → align → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | position_control | impedance_control | admittance_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 9 | -0.0691 | 0.87 | ✅ accepted |
| 5 | approach → descend → grasp → retract → approach → align → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | position_control | impedance_control | admittance_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | 10 | -0.0733 | 0.82 | ❌ rejected |
| 4 | approach → descend → grasp → retract → approach → align → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | admittance_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | 10 | -0.0088 | 0.76 | ❌ rejected |
| 3 | approach → descend → grasp → retract → approach → align → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | position_control | impedance_control | admittance_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | 9 | 0.0842 | 0.87 | ✅ accepted |

**Proposal policy**: task_score is 0.89 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.042) — your mutation base

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
- id: align_hole
  type: align
  generator: linear_cartesian
  control: admittance_control
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
      tolerance: 0.1
  parameters:
    lateral_offset_x:
      type: scalar
      range:
      - -0.03
      - 0.03
      default: 0.0
      binds_to:
      - path: target.offset.x
        mode: add
    lateral_offset_y:
      type: scalar
      range:
      - -0.03
      - 0.03
      default: 0.0
      binds_to:
      - path: target.offset.y
        mode: add
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
      mode: keep_current
  parameters:
    force_guard_threshold:
      type: scalar
      range:
      - 10.0
      - 200.0
      default: 100.0
      binds_to:
      - path: guards.insert_force.threshold
        mode: replace
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
    threshold: 100.0
    on_failure: abort
  retries:
    max_attempts: 3
    strategy: offset_target
    offset:
    - 0.003
    - 0.003
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
- **align_hole** (`align`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.02], tolerance=0.005
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=world_z, tolerance=0.1
  - parameter_bindings:
    - lateral_offset_x: status=consumed; consumers=target.offset.x (add)
    - lateral_offset_y: status=consumed; consumers=target.offset.y (add)
- **descend_insert** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.1, mode=replace_offset_projection, sign=negative}, tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings:
    - force_guard_threshold: status=consumed; consumers=guards.insert_force.threshold (replace)
    - insertion_depth: status=consumed; consumers=target.offset_along_axis.distance (replace)
  - guards:
    - id=insert_force, when=during_phase, predicate=force_below, on_failure=abort, threshold=100.0
  - retries: max_attempts=3, strategy=offset_target, offset=[0.003, 0.003, 0.0]

## Design Metrics

- **Composite score**: -0.042
- **task_score** (E): 0.891
- **fitness_score**: 0.558  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.600

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_peg | 1.00 | 0.00 | 0.0799 |
| descend_to_peg | 0.00 | 0.00 | 0.0319 |
| grasp_peg | 1.00 | 0.00 | 0.0000 |
| lift_peg | 1.00 | 0.00 | 0.0520 |
| approach_hole | 0.00 | 0.00 | 0.2021 |
| align_hole | 0.67 | 1.00 | 0.1575 |
| descend_insert | 0.00 | 1.00 | 0.0001 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_peg | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.502, -0.000, 0.380) | (0.504, -0.000, 0.340)→(0.501, -0.000, 0.420) | 0.260→0.340 | 0.00 / 0.000 | 0.000 | 0.000 |
| descend_to_peg | descend | 0.00 / step_budget | (0.502, -0.000, 0.380)→(0.500, -0.000, 0.412) | (0.501, -0.000, 0.420)→(0.497, 0.000, 0.452) | 0.340→0.372 | 0.00 / 0.000 | 0.000 | 0.000 |
| grasp_peg | grasp | 1.00 / step_budget | (0.498, -0.000, 0.404)→(0.498, -0.000, 0.404) | (0.497, 0.000, 0.452)→(0.495, 0.000, 0.444) | 0.372→0.364 | 0.00 / 0.000 | 0.000 | 0.000 |
| lift_peg | retract | 1.00 / step_budget | (0.498, -0.000, 0.404)→(0.497, -0.000, 0.456) | (0.495, 0.000, 0.444)→(0.491, 0.000, 0.496) | 0.364→0.416 | 0.00 / 0.000 | 0.000 | 0.000 |
| approach_hole | approach | 0.00 / step_budget | (0.497, -0.000, 0.456)→(0.501, 0.011, 0.255) | (0.491, 0.000, 0.496)→(0.508, 0.011, 0.295) | 0.416→0.216 | 0.00 / 0.000 | 0.000 | 0.000 |
| align_hole | align | 0.67 / step_budget | (0.501, 0.011, 0.255)→(0.501, 0.003, 0.104) | (0.508, 0.011, 0.295)→(0.539, 0.004, 0.099) | 0.216→0.063 | 1.00 / 1.000 | 333.452 | 6311.359 |
| descend_insert | descend | 0.00 / guard_failure | (0.501, 0.003, 0.104)→(0.501, 0.003, 0.104) | (0.539, 0.004, 0.099)→(0.539, 0.003, 0.099) | 0.063→0.063 | 1.00 / 1.000 | 264.275 | 264.275 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.902
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.902
- phase_score: 0.373
- phase_breakdown.approach_hole_score: 0.061
- phase_breakdown.approach_peg_score: 0.826
- phase_breakdown.insert_task_score: 0.378

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.584
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.925
- **Median Q (composite search score)**: -0.051
- **K-run variance**: 0.0004
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.428


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.04396,"average_solve_count":182.0,"average_success_count":182.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_hole.lateral_offset_x":-0.02309,"align_hole.lateral_offset_y":-0.02997,"approach_hole.speed":0.01102,"approach_peg.speed":0.05946,"descend_insert.force_guard_threshold":76.93874,"descend_insert.insertion_depth":0.1313,"descend_to_peg.contact_force_threshold":7.33322,"descend_to_peg.descend_speed":0.19347,"lift_peg.lift_height":0.07072},"optimized_scores":{"best_composite_score":-0.0155,"best_fitness_score":0.5845,"best_task_score":0.90238},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":86.0,"contact_point_centroid":[0.55357,0.02218,0.07933],"force_p95":15291.0776,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":15812.06605,"mean_force":4859.30015,"phase_index":5.0,"phase_name":"align_hole","phase_type":"align","tcp_position_centroid":[0.48975,0.03029,0.08098]},{"body_a":"attachment","body_b":"peg_socket","contact_count":45.0,"contact_point_centroid":[0.47732,0.01731,0.07801],"force_p95":12560.86711,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":12731.85744,"mean_force":6247.31957,"phase_index":5.0,"phase_name":"align_hole","phase_type":"align","tcp_position_centroid":[0.48084,0.02033,0.06512]},{"body_a":"peg_socket","body_b":"link7","contact_count":912.0,"contact_point_centroid":[0.5697,0.00117,0.07979],"force_p95":749.8288,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":7254.752,"mean_force":427.49975,"phase_index":5.0,"phase_name":"align_hole","phase_type":"align","tcp_position_centroid":[0.48951,0.02836,0.09288]},{"body_a":"attachment","body_b":"peg_socket","contact_count":15.0,"contact_point_centroid":[0.48368,0.02051,0.04941],"force_p95":4638.32749,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":4640.44272,"mean_force":3563.54137,"phase_index":5.0,"phase_name":"align_hole","phase_type":"align","tcp_position_centroid":[0.47728,0.0206,0.06239]},{"body_a":"peg_socket","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.56985,-0.02822,0.07997],"force_p95":209.56585,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":209.56585,"mean_force":209.56585,"phase_index":6.0,"phase_name":"descend_insert","phase_type":"descend","tcp_position_centroid":[0.50187,0.04392,0.10076]}],"total_contact_groups":5},"final_pose_error":0.15275,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.51001,0.03178,0.025],"final_tcp_position":[0.50198,0.04392,0.10076],"realised_fixture_position":[0.51001,0.03178,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.51001,0.03178,0.08]},"peak_contact_force":15812.06605,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":902.0,"n_steps_budget":960.0,"object_pos_end":[0.50104,-0.0,0.42085],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.34085,"object_to_goal_dist_start":0.26034,"object_z_max":0.42078,"peak_contact_force":0.0,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach_peg","tcp_end":[0.50235,-1e-05,0.38087],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":513.0,"n_steps_budget":600.0,"object_pos_end":[0.49652,1e-05,0.45253],"object_pos_start":[0.50104,-0.0,0.42085],"object_to_goal_dist_end":0.37255,"object_to_goal_dist_start":0.34085,"object_z_max":0.45248,"peak_contact_force":0.0,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.5,-1e-05,0.41268],"tcp_start":[0.50235,-1e-05,0.38087],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":200.0,"n_steps_budget":50.0,"object_pos_end":[0.49522,2e-05,0.44457],"object_pos_start":[0.49652,1e-05,0.45253],"object_to_goal_dist_end":0.3646,"object_to_goal_dist_start":0.37255,"object_z_max":0.45255,"peak_contact_force":0.0,"phase_name":"grasp_peg","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.49799,-2e-05,0.40467],"tcp_start":[0.49799,-2e-05,0.40467],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":542.0,"n_steps_budget":600.0,"object_pos_end":[0.48991,3e-05,0.50487],"object_pos_start":[0.49522,2e-05,0.44457],"object_to_goal_dist_end":0.42499,"object_to_goal_dist_start":0.3646,"object_z_max":0.50477,"peak_contact_force":0.0,"phase_name":"lift_peg","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.49732,-2e-05,0.46556],"tcp_start":[0.49799,-2e-05,0.40467],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50787,0.01815,0.30814],"object_pos_start":[0.48991,3e-05,0.50487],"object_to_goal_dist_end":0.229,"object_to_goal_dist_start":0.42499,"object_z_max":0.50491,"peak_contact_force":0.0,"phase_name":"approach_hole","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach_hole","tcp_end":[0.50222,0.01807,0.26854],"tcp_start":[0.49732,-2e-05,0.46556],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54041,0.03368,0.09754],"object_pos_start":[0.50787,0.01815,0.30814],"object_to_goal_dist_end":0.05545,"object_to_goal_dist_start":0.229,"object_z_max":0.30814,"peak_contact_force":362.35172,"phase_name":"align_hole","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":1058.0,"raw_peak_contact_force":15812.06605,"tcp_end":[0.50187,0.04392,0.10076],"tcp_start":[0.50222,0.01807,0.26854],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":960.0,"object_pos_end":[0.5405,0.03365,0.09756],"object_pos_start":[0.54041,0.03368,0.09754],"object_to_goal_dist_end":0.05551,"object_to_goal_dist_start":0.05545,"object_z_max":0.09754,"peak_contact_force":209.56585,"phase_name":"descend_insert","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1.0,"raw_peak_contact_force":209.56585,"subtask_id":"insert_task","tcp_end":[0.50198,0.04392,0.10076],"tcp_start":[0.50187,0.04392,0.10076],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `02e4649f08bda5439eae760bf0bc4b5a6b47c91c93317c6956c2509043be6196`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.50633,"average_solve_count":158.0,"average_success_count":158.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_hole.lateral_offset_x":-0.02963,"align_hole.lateral_offset_y":-0.02995,"approach_hole.speed":0.07309,"approach_peg.speed":0.07859,"descend_insert.force_guard_threshold":42.2348,"descend_insert.insertion_depth":0.09242,"descend_to_peg.contact_force_threshold":10.00361,"descend_to_peg.descend_speed":0.10421,"lift_peg.lift_height":0.05934},"optimized_scores":{"best_composite_score":-0.05067,"best_fitness_score":0.54933,"best_task_score":0.84456},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link7","contact_count":790.0,"contact_point_centroid":[0.5459,0.02019,0.0724],"force_p95":305.88596,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1376.28329,"mean_force":294.11557,"phase_index":5.0,"phase_name":"align_hole","phase_type":"align","tcp_position_centroid":[0.47044,0.03437,0.10923]},{"body_a":"attachment","body_b":"peg_socket","contact_count":6.0,"contact_point_centroid":[0.5168,0.03414,0.07918],"force_p95":1161.55431,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1182.44753,"mean_force":959.40129,"phase_index":5.0,"phase_name":"align_hole","phase_type":"align","tcp_position_centroid":[0.49915,0.03427,0.08352]},{"body_a":"attachment","body_b":"peg_socket","contact_count":17.0,"contact_point_centroid":[0.45406,0.01858,0.0795],"force_p95":861.46835,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":969.32156,"mean_force":289.35987,"phase_index":5.0,"phase_name":"align_hole","phase_type":"align","tcp_position_centroid":[0.45089,0.03134,0.08527]},{"body_a":"peg_socket","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.54607,0.01108,0.07415],"force_p95":238.33237,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":238.33237,"mean_force":238.33237,"phase_index":6.0,"phase_name":"descend_insert","phase_type":"descend","tcp_position_centroid":[0.47393,0.04069,0.11065]}],"total_contact_groups":4},"final_pose_error":0.12364,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.48616,0.03898,0.025],"final_tcp_position":[0.47398,0.04065,0.11061],"realised_fixture_position":[0.48616,0.03898,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.48616,0.03898,0.08]},"peak_contact_force":1376.28329,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":662.0,"n_steps_budget":720.0,"object_pos_end":[0.50108,-0.0,0.42006],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.34007,"object_to_goal_dist_start":0.26034,"object_z_max":0.41996,"peak_contact_force":0.0,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach_peg","tcp_end":[0.50233,-1e-05,0.38008],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":513.0,"n_steps_budget":600.0,"object_pos_end":[0.49661,1e-05,0.45175],"object_pos_start":[0.50108,-0.0,0.42006],"object_to_goal_dist_end":0.37176,"object_to_goal_dist_start":0.34007,"object_z_max":0.45169,"peak_contact_force":0.0,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.50002,-1e-05,0.41189],"tcp_start":[0.50233,-1e-05,0.38008],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":200.0,"n_steps_budget":50.0,"object_pos_end":[0.49529,1e-05,0.44378],"object_pos_start":[0.49661,1e-05,0.45175],"object_to_goal_dist_end":0.36381,"object_to_goal_dist_start":0.37176,"object_z_max":0.45176,"peak_contact_force":0.0,"phase_name":"grasp_peg","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.49801,-2e-05,0.40387],"tcp_start":[0.49801,-2e-05,0.40387],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":542.0,"n_steps_budget":600.0,"object_pos_end":[0.49073,3e-05,0.49343],"object_pos_start":[0.49529,1e-05,0.44378],"object_to_goal_dist_end":0.41354,"object_to_goal_dist_start":0.36381,"object_z_max":0.49335,"peak_contact_force":0.0,"phase_name":"lift_peg","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.49723,-2e-05,0.45396],"tcp_start":[0.49801,-2e-05,0.40387],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49572,0.02509,0.28003],"object_pos_start":[0.49073,3e-05,0.49343],"object_to_goal_dist_end":0.20164,"object_to_goal_dist_start":0.41354,"object_z_max":0.49347,"peak_contact_force":0.0,"phase_name":"approach_hole","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach_hole","tcp_end":[0.48755,0.02491,0.24087],"tcp_start":[0.49723,-2e-05,0.45396],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":872.0,"n_steps_budget":930.0,"object_pos_end":[0.51302,0.03671,0.10316],"object_pos_start":[0.49572,0.02509,0.28003],"object_to_goal_dist_end":0.04531,"object_to_goal_dist_start":0.20164,"object_z_max":0.28003,"peak_contact_force":306.96672,"phase_name":"align_hole","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":813.0,"raw_peak_contact_force":1376.28329,"tcp_end":[0.47393,0.04069,0.11065],"tcp_start":[0.48755,0.02491,0.24087],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":780.0,"object_pos_end":[0.51307,0.03667,0.10312],"object_pos_start":[0.51302,0.03671,0.10316],"object_to_goal_dist_end":0.04528,"object_to_goal_dist_start":0.04531,"object_z_max":0.10316,"peak_contact_force":238.33237,"phase_name":"descend_insert","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1.0,"raw_peak_contact_force":238.33237,"subtask_id":"insert_task","tcp_end":[0.47398,0.04065,0.11061],"tcp_start":[0.47393,0.04069,0.11065],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `7363bc0b3fa7329ef53220378736f8cf8ba8a5eef8ffe48ac32070ac53331cd4`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":8.0,"average_failure_rate":0.04624,"average_mean_iterations":13.04046,"average_solve_count":173.0,"average_success_count":165.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_hole.lateral_offset_x":0.0002,"align_hole.lateral_offset_y":0.02012,"approach_hole.speed":0.05486,"approach_peg.speed":0.07637,"descend_insert.force_guard_threshold":158.78535,"descend_insert.insertion_depth":0.08948,"descend_to_peg.contact_force_threshold":11.68394,"descend_to_peg.descend_speed":0.10514,"lift_peg.lift_height":0.05412},"optimized_scores":{"best_composite_score":-0.06061,"best_fitness_score":0.53939,"best_task_score":0.92514},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link7","contact_count":583.0,"contact_point_centroid":[0.58943,-0.00993,0.0798],"force_p95":361.01386,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1745.72698,"mean_force":294.31685,"phase_index":5.0,"phase_name":"align_hole","phase_type":"align","tcp_position_centroid":[0.50829,-0.03499,0.10519]},{"body_a":"attachment","body_b":"peg_socket","contact_count":24.0,"contact_point_centroid":[0.58339,-0.03971,0.07948],"force_p95":1502.10991,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1510.32248,"mean_force":904.29905,"phase_index":5.0,"phase_name":"align_hole","phase_type":"align","tcp_position_centroid":[0.52799,-0.06181,0.09216]},{"body_a":"attachment","body_b":"peg_socket","contact_count":20.0,"contact_point_centroid":[0.49728,-0.00167,0.07907],"force_p95":889.99063,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":932.53956,"mean_force":391.01395,"phase_index":5.0,"phase_name":"align_hole","phase_type":"align","tcp_position_centroid":[0.49716,-0.0155,0.07543]},{"body_a":"peg_socket","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.58953,-0.01967,0.07999],"force_p95":344.92796,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":344.92796,"mean_force":344.92796,"phase_index":6.0,"phase_name":"descend_insert","phase_type":"descend","tcp_position_centroid":[0.52733,-0.07555,0.09933]},{"body_a":"attachment","body_b":"peg_socket","contact_count":10.0,"contact_point_centroid":[0.55961,-0.06004,0.07982],"force_p95":0.0,"geom_a":"peg_tip","geom_b":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0,"mean_force":0.0,"phase_index":5.0,"phase_name":"align_hole","phase_type":"align","tcp_position_centroid":[0.52751,-0.07449,0.09606]}],"total_contact_groups":5},"final_pose_error":0.12355,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.52962,-0.01705,0.025],"final_tcp_position":[0.52742,-0.07566,0.09926],"realised_fixture_position":[0.52962,-0.01705,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.52962,-0.01705,0.08]},"peak_contact_force":1745.72698,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":692.0,"n_steps_budget":750.0,"object_pos_end":[0.50107,-0.0,0.42028],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.34028,"object_to_goal_dist_start":0.26034,"object_z_max":0.42018,"peak_contact_force":0.0,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach_peg","tcp_end":[0.50234,-1e-05,0.3803],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":513.0,"n_steps_budget":600.0,"object_pos_end":[0.49659,1e-05,0.45196],"object_pos_start":[0.50107,-0.0,0.42028],"object_to_goal_dist_end":0.37198,"object_to_goal_dist_start":0.34028,"object_z_max":0.45191,"peak_contact_force":0.0,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.50002,-1e-05,0.41211],"tcp_start":[0.50234,-1e-05,0.3803],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":200.0,"n_steps_budget":50.0,"object_pos_end":[0.49527,1e-05,0.444],"object_pos_start":[0.49659,1e-05,0.45196],"object_to_goal_dist_end":0.36403,"object_to_goal_dist_start":0.37198,"object_z_max":0.45198,"peak_contact_force":0.0,"phase_name":"grasp_peg","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.49801,-2e-05,0.40409],"tcp_start":[0.49801,-2e-05,0.40409],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":542.0,"n_steps_budget":600.0,"object_pos_end":[0.49107,2e-05,0.48852],"object_pos_start":[0.49527,1e-05,0.444],"object_to_goal_dist_end":0.40861,"object_to_goal_dist_start":0.36403,"object_z_max":0.48844,"peak_contact_force":0.0,"phase_name":"lift_peg","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.49717,-3e-05,0.44898],"tcp_start":[0.49801,-2e-05,0.40409],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51918,-0.00996,0.2961],"object_pos_start":[0.49107,2e-05,0.48852],"object_to_goal_dist_end":0.21718,"object_to_goal_dist_start":0.40861,"object_z_max":0.48854,"peak_contact_force":0.0,"phase_name":"approach_hole","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach_hole","tcp_end":[0.51376,-0.01002,0.25647],"tcp_start":[0.49717,-3e-05,0.44898],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":692.0,"n_steps_budget":990.0,"object_pos_end":[0.56401,-0.05978,0.09685],"object_pos_start":[0.51918,-0.00996,0.2961],"object_to_goal_dist_end":0.08919,"object_to_goal_dist_start":0.21718,"object_z_max":0.2961,"peak_contact_force":331.0385,"phase_name":"align_hole","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":637.0,"raw_peak_contact_force":1745.72698,"tcp_end":[0.52733,-0.07555,0.09933],"tcp_start":[0.51376,-0.01002,0.25647],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":780.0,"object_pos_end":[0.56408,-0.05987,0.09678],"object_pos_start":[0.56401,-0.05978,0.09685],"object_to_goal_dist_end":0.08929,"object_to_goal_dist_start":0.08919,"object_z_max":0.09685,"peak_contact_force":344.92796,"phase_name":"descend_insert","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1.0,"raw_peak_contact_force":344.92796,"subtask_id":"insert_task","tcp_end":[0.52742,-0.07566,0.09926],"tcp_start":[0.52733,-0.07555,0.09933],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```