## Search State

- **Seed**: 7
- **Iteration**: 9 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 8 | approach → descend → grasp → retract → approach → align → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | position_control | admittance_control | admittance_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.0358 | 0.83 | ❌ rejected |
| 7 | approach → descend → grasp → retract → approach → align → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | position_control | admittance_control | admittance_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 9 | -0.0423 | 0.89 | ✅ accepted |
| 6 | approach → descend → grasp → retract → approach → align → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | position_control | impedance_control | admittance_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 9 | -0.0691 | 0.87 | ✅ accepted |
| 5 | approach → descend → grasp → retract → approach → align → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | position_control | impedance_control | admittance_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | 10 | -0.0733 | 0.82 | ❌ rejected |
| 4 | approach → descend → grasp → retract → approach → align → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | admittance_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | 10 | -0.0088 | 0.76 | ❌ rejected |

**Proposal policy**: task_score is 0.83 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.036) — your mutation base

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

- **Composite score**: 0.036
- **task_score** (E): 0.829
- **fitness_score**: 0.586  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.550

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_peg | 1.00 | 0.00 | 0.0803 |
| descend_to_peg | 0.00 | 0.00 | 0.0153 |
| grasp_peg | 1.00 | 0.00 | 0.0000 |
| lift_peg | 1.00 | 0.00 | 0.0588 |
| approach_hole | 0.00 | 0.00 | 0.2117 |
| align_hole | 0.33 | 1.00 | 0.1206 |
| descend_insert | 0.00 | 1.00 | 0.0095 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_peg | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.502, -0.000, 0.381) | (0.504, -0.000, 0.340)→(0.501, -0.000, 0.421) | 0.260→0.341 | 0.00 / 0.000 | 0.000 | 0.000 |
| descend_to_peg | descend | 0.00 / step_budget | (0.502, -0.000, 0.381)→(0.500, -0.000, 0.366) | (0.501, -0.000, 0.421)→(0.500, 0.000, 0.406) | 0.341→0.326 | 0.00 / 0.000 | 0.000 | 0.000 |
| grasp_peg | grasp | 1.00 / step_budget | (0.498, -0.000, 0.357)→(0.498, -0.000, 0.357) | (0.500, 0.000, 0.406)→(0.498, -0.000, 0.397) | 0.326→0.317 | 0.00 / 0.000 | 0.000 | 0.000 |
| lift_peg | retract | 1.00 / step_budget | (0.498, -0.000, 0.357)→(0.497, -0.000, 0.416) | (0.498, -0.000, 0.397)→(0.493, -0.000, 0.456) | 0.317→0.376 | 0.00 / 0.000 | 0.000 | 0.000 |
| approach_hole | approach | 0.00 / step_budget | (0.497, -0.000, 0.416)→(0.502, 0.014, 0.206) | (0.493, -0.000, 0.456)→(0.510, 0.014, 0.245) | 0.376→0.167 | 0.00 / 0.000 | 0.000 | 0.000 |
| align_hole | align | 0.33 / step_budget | (0.502, 0.014, 0.206)→(0.521, 0.022, 0.093) | (0.510, 0.014, 0.245)→(0.559, 0.018, 0.096) | 0.167→0.072 | 1.00 / 1.333 | 459.571 | 5187.510 |
| descend_insert | descend | 0.00 / step_budget | (0.521, 0.022, 0.093)→(0.522, 0.016, 0.096) | (0.559, 0.018, 0.096)→(0.560, 0.014, 0.099) | 0.072→0.070 | 1.00 / 1.000 | 230.568 | 325.146 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.887
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.887
- phase_score: 0.463
- phase_breakdown.approach_hole_score: 0.152
- phase_breakdown.approach_peg_score: 0.827
- phase_breakdown.insert_task_score: 0.504

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.633
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.887
- **Median Q (composite search score)**: 0.016
- **K-run variance**: 0.0011
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.355


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":5.0,"average_failure_rate":0.02924,"average_mean_iterations":10.08772,"average_solve_count":171.0,"average_success_count":166.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_hole.lateral_offset_x":-0.02746,"align_hole.lateral_offset_y":-0.02616,"approach_hole.speed":0.08057,"approach_peg.speed":0.05867,"descend_insert.insertion_depth":0.05796,"descend_to_peg.contact_force_threshold":4.23532,"descend_to_peg.descend_speed":0.10786,"lift_peg.lift_height":0.07435},"optimized_scores":{"best_composite_score":0.0161,"best_fitness_score":0.5661,"best_task_score":0.83879},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link7","contact_count":524.0,"contact_point_centroid":[0.56952,0.0036,0.07679],"force_p95":954.62797,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":11449.90021,"mean_force":655.70071,"phase_index":5.0,"phase_name":"align_hole","phase_type":"align","tcp_position_centroid":[0.49325,0.04172,0.09772]},{"body_a":"attachment","body_b":"peg_socket","contact_count":417.0,"contact_point_centroid":[0.56168,0.03496,0.07958],"force_p95":852.75531,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":8024.84199,"mean_force":527.86226,"phase_index":5.0,"phase_name":"align_hole","phase_type":"align","tcp_position_centroid":[0.50082,0.04353,0.0955]},{"body_a":"peg_socket","body_b":"link7","contact_count":10.0,"contact_point_centroid":[0.56991,0.02759,0.04944],"force_p95":4840.70253,"geom_a":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":4874.78767,"mean_force":3756.76191,"phase_index":5.0,"phase_name":"align_hole","phase_type":"align","tcp_position_centroid":[0.48129,0.0312,0.10006]},{"body_a":"attachment","body_b":"peg_socket","contact_count":383.0,"contact_point_centroid":[0.56999,0.0321,0.07991],"force_p95":258.64919,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":341.3796,"mean_force":205.39814,"phase_index":6.0,"phase_name":"descend_insert","phase_type":"descend","tcp_position_centroid":[0.50487,0.04882,0.10366]},{"body_a":"peg_socket","body_b":"link7","contact_count":22.0,"contact_point_centroid":[0.56984,-0.02821,0.07696],"force_p95":141.14856,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":241.82058,"mean_force":99.16895,"phase_index":6.0,"phase_name":"descend_insert","phase_type":"descend","tcp_position_centroid":[0.50295,0.05227,0.09922]}],"total_contact_groups":5},"final_pose_error":0.08824,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.51001,0.03178,0.025],"final_tcp_position":[0.5077,0.04698,0.10893],"realised_fixture_position":[0.51001,0.03178,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.51001,0.03178,0.08]},"peak_contact_force":11449.90021,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":902.0,"n_steps_budget":960.0,"object_pos_end":[0.50104,-0.0,0.42085],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.34085,"object_to_goal_dist_start":0.26034,"object_z_max":0.42078,"peak_contact_force":0.0,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach_peg","tcp_end":[0.50235,-1e-05,0.38087],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":84.0,"n_steps_budget":600.0,"object_pos_end":[0.50026,0.0,0.40573],"object_pos_start":[0.50104,-0.0,0.42085],"object_to_goal_dist_end":0.32573,"object_to_goal_dist_start":0.34085,"object_z_max":0.42088,"peak_contact_force":0.0,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.50039,-2e-05,0.36573],"tcp_start":[0.50235,-1e-05,0.38087],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":200.0,"n_steps_budget":50.0,"object_pos_end":[0.49826,-1e-05,0.39739],"object_pos_start":[0.50026,0.0,0.40573],"object_to_goal_dist_end":0.3174,"object_to_goal_dist_start":0.32573,"object_z_max":0.40573,"peak_contact_force":0.0,"phase_name":"grasp_peg","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.49765,-5e-05,0.3574],"tcp_start":[0.49765,-5e-05,0.3574],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":542.0,"n_steps_budget":600.0,"object_pos_end":[0.49266,-0.0,0.46143],"object_pos_start":[0.49826,-1e-05,0.39739],"object_to_goal_dist_end":0.3815,"object_to_goal_dist_start":0.3174,"object_z_max":0.46133,"peak_contact_force":0.0,"phase_name":"lift_peg","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.49661,-5e-05,0.42162],"tcp_start":[0.49765,-5e-05,0.3574],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51157,0.02226,0.2509],"object_pos_start":[0.49266,-0.0,0.46143],"object_to_goal_dist_end":0.17273,"object_to_goal_dist_start":0.3815,"object_z_max":0.46148,"peak_contact_force":0.0,"phase_name":"approach_hole","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach_hole","tcp_end":[0.5032,0.02215,0.21178],"tcp_start":[0.49661,-5e-05,0.42162],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":662.0,"n_steps_budget":720.0,"object_pos_end":[0.54119,0.04216,0.09661],"object_pos_start":[0.51157,0.02226,0.2509],"object_to_goal_dist_end":0.06123,"object_to_goal_dist_start":0.17273,"object_z_max":0.2509,"peak_contact_force":777.50008,"phase_name":"align_hole","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":951.0,"raw_peak_contact_force":11449.90021,"tcp_end":[0.50266,0.0526,0.0991],"tcp_start":[0.5032,0.02215,0.21178],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":392.0,"n_steps_budget":600.0,"object_pos_end":[0.54585,0.03837,0.10053],"object_pos_start":[0.54119,0.04216,0.09661],"object_to_goal_dist_end":0.06321,"object_to_goal_dist_start":0.06123,"object_z_max":0.10063,"peak_contact_force":221.50727,"phase_name":"descend_insert","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":405.0,"raw_peak_contact_force":341.3796,"subtask_id":"insert_task","tcp_end":[0.5077,0.04698,0.10893],"tcp_start":[0.50266,0.0526,0.0991],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `02e4649f08bda5439eae760bf0bc4b5a6b47c91c93317c6956c2509043be6196`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.01899,"average_solve_count":158.0,"average_success_count":158.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_hole.lateral_offset_x":0.00349,"align_hole.lateral_offset_y":0.0228,"approach_hole.speed":0.09861,"approach_peg.speed":0.06759,"descend_insert.insertion_depth":0.08784,"descend_to_peg.contact_force_threshold":5.66744,"descend_to_peg.descend_speed":0.12886,"lift_peg.lift_height":0.05278},"optimized_scores":{"best_composite_score":0.00845,"best_fitness_score":0.55845,"best_task_score":0.76208},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":478.0,"contact_point_centroid":[0.54556,0.05363,0.07966],"force_p95":379.18845,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1539.71593,"mean_force":310.40235,"phase_index":5.0,"phase_name":"align_hole","phase_type":"align","tcp_position_centroid":[0.54709,0.04499,0.07463]},{"body_a":"attachment","body_b":"peg_socket","contact_count":649.0,"contact_point_centroid":[0.54595,0.01126,0.07991],"force_p95":297.41019,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":351.81787,"mean_force":258.28674,"phase_index":6.0,"phase_name":"descend_insert","phase_type":"descend","tcp_position_centroid":[0.54606,0.02613,0.08138]}],"total_contact_groups":2},"final_pose_error":0.10809,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.48616,0.03898,0.025],"final_tcp_position":[0.54523,0.0265,0.08181],"realised_fixture_position":[0.48616,0.03898,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.48616,0.03898,0.08]},"peak_contact_force":1539.71593,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":782.0,"n_steps_budget":840.0,"object_pos_end":[0.50106,-0.0,0.4205],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.3405,"object_to_goal_dist_start":0.26034,"object_z_max":0.42042,"peak_contact_force":0.0,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach_peg","tcp_end":[0.50234,-1e-05,0.38052],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":84.0,"n_steps_budget":600.0,"object_pos_end":[0.50028,0.0,0.40539],"object_pos_start":[0.50106,-0.0,0.4205],"object_to_goal_dist_end":0.32539,"object_to_goal_dist_start":0.3405,"object_z_max":0.42054,"peak_contact_force":0.0,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.50039,-2e-05,0.36539],"tcp_start":[0.50234,-1e-05,0.38052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":200.0,"n_steps_budget":50.0,"object_pos_end":[0.49828,-1e-05,0.39705],"object_pos_start":[0.50028,0.0,0.40539],"object_to_goal_dist_end":0.31705,"object_to_goal_dist_start":0.32539,"object_z_max":0.40539,"peak_contact_force":0.0,"phase_name":"grasp_peg","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.49765,-5e-05,0.35705],"tcp_start":[0.49765,-5e-05,0.35705],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":542.0,"n_steps_budget":600.0,"object_pos_end":[0.49402,-1e-05,0.4406],"object_pos_start":[0.49828,-1e-05,0.39705],"object_to_goal_dist_end":0.36065,"object_to_goal_dist_start":0.31705,"object_z_max":0.44053,"peak_contact_force":0.0,"phase_name":"lift_peg","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.4964,-5e-05,0.40067],"tcp_start":[0.49765,-5e-05,0.35705],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49626,0.03049,0.22285],"object_pos_start":[0.49402,-1e-05,0.4406],"object_to_goal_dist_end":0.14611,"object_to_goal_dist_start":0.36065,"object_z_max":0.44063,"peak_contact_force":0.0,"phase_name":"approach_hole","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach_hole","tcp_end":[0.48537,0.03025,0.18436],"tcp_start":[0.4964,-5e-05,0.40067],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":542.0,"n_steps_budget":600.0,"object_pos_end":[0.58485,0.03658,0.09442],"object_pos_start":[0.49626,0.03049,0.22285],"object_to_goal_dist_end":0.09351,"object_to_goal_dist_start":0.14611,"object_z_max":0.22285,"peak_contact_force":303.31696,"phase_name":"align_hole","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":478.0,"raw_peak_contact_force":1539.71593,"tcp_end":[0.54693,0.0406,0.08232],"tcp_start":[0.48537,0.03025,0.18436],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":661.0,"n_steps_budget":690.0,"object_pos_end":[0.58037,0.02537,0.1009],"object_pos_start":[0.58485,0.03658,0.09442],"object_to_goal_dist_end":0.08683,"object_to_goal_dist_start":0.09351,"object_z_max":0.1009,"peak_contact_force":256.91249,"phase_name":"descend_insert","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":649.0,"raw_peak_contact_force":351.81787,"subtask_id":"insert_task","tcp_end":[0.54523,0.0265,0.08181],"tcp_start":[0.54693,0.0406,0.08232],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `7363bc0b3fa7329ef53220378736f8cf8ba8a5eef8ffe48ac32070ac53331cd4`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":31.0,"average_failure_rate":0.17127,"average_mean_iterations":37.89503,"average_solve_count":181.0,"average_success_count":150.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_hole.lateral_offset_x":0.0079,"align_hole.lateral_offset_y":-0.00529,"approach_hole.speed":0.07168,"approach_peg.speed":0.06377,"descend_insert.insertion_depth":0.10043,"descend_to_peg.contact_force_threshold":6.3027,"descend_to_peg.descend_speed":0.17197,"lift_peg.lift_height":0.07901},"optimized_scores":{"best_composite_score":0.08274,"best_fitness_score":0.63274,"best_task_score":0.88706},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link7","contact_count":285.0,"contact_point_centroid":[0.58889,0.00736,0.07994],"force_p95":1147.88996,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":2572.91398,"mean_force":716.77692,"phase_index":5.0,"phase_name":"align_hole","phase_type":"align","tcp_position_centroid":[0.50984,-0.02478,0.09324]},{"body_a":"attachment","body_b":"peg_socket","contact_count":219.0,"contact_point_centroid":[0.56234,-0.01987,0.07931],"force_p95":1064.79811,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":2094.04109,"mean_force":696.6242,"phase_index":5.0,"phase_name":"align_hole","phase_type":"align","tcp_position_centroid":[0.51984,-0.02353,0.09111]},{"body_a":"attachment","body_b":"peg_socket","contact_count":52.0,"contact_point_centroid":[0.58962,-0.01872,0.0798],"force_p95":260.75984,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":282.2411,"mean_force":187.05956,"phase_index":6.0,"phase_name":"descend_insert","phase_type":"descend","tcp_position_centroid":[0.51269,-0.02439,0.0966]},{"body_a":"peg_socket","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.5896,0.00601,0.08],"force_p95":247.87167,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":258.97259,"mean_force":147.96339,"phase_index":6.0,"phase_name":"descend_insert","phase_type":"descend","tcp_position_centroid":[0.51243,-0.02732,0.09762]},{"body_a":"attachment","body_b":"peg_socket","contact_count":3.0,"contact_point_centroid":[0.49953,-0.01326,0.07999],"force_p95":0.0,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0,"mean_force":0.0,"phase_index":5.0,"phase_name":"align_hole","phase_type":"align","tcp_position_centroid":[0.49922,-0.02343,0.09098]}],"total_contact_groups":5},"final_pose_error":0.11894,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.52962,-0.01705,0.025],"final_tcp_position":[0.51378,-0.02627,0.09709],"realised_fixture_position":[0.52962,-0.01705,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.52962,-0.01705,0.08]},"peak_contact_force":2572.91398,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":842.0,"n_steps_budget":900.0,"object_pos_end":[0.50104,-0.0,0.42093],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.34094,"object_to_goal_dist_start":0.26034,"object_z_max":0.42085,"peak_contact_force":0.0,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach_peg","tcp_end":[0.50236,-1e-05,0.38096],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":84.0,"n_steps_budget":600.0,"object_pos_end":[0.50026,0.0,0.40582],"object_pos_start":[0.50104,-0.0,0.42093],"object_to_goal_dist_end":0.32582,"object_to_goal_dist_start":0.34094,"object_z_max":0.42097,"peak_contact_force":0.0,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.5004,-2e-05,0.36582],"tcp_start":[0.50236,-1e-05,0.38096],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":200.0,"n_steps_budget":50.0,"object_pos_end":[0.49826,-1e-05,0.39748],"object_pos_start":[0.50026,0.0,0.40582],"object_to_goal_dist_end":0.31749,"object_to_goal_dist_start":0.32582,"object_z_max":0.40582,"peak_contact_force":0.0,"phase_name":"grasp_peg","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.49766,-5e-05,0.35749],"tcp_start":[0.49766,-5e-05,0.35749],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":542.0,"n_steps_budget":600.0,"object_pos_end":[0.49237,-0.0,0.46582],"object_pos_start":[0.49826,-1e-05,0.39748],"object_to_goal_dist_end":0.38589,"object_to_goal_dist_start":0.31749,"object_z_max":0.46571,"peak_contact_force":0.0,"phase_name":"lift_peg","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.49666,-5e-05,0.42605],"tcp_start":[0.49766,-5e-05,0.35749],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52293,-0.0114,0.26145],"object_pos_start":[0.49237,-0.0,0.46582],"object_to_goal_dist_end":0.18325,"object_to_goal_dist_start":0.38589,"object_z_max":0.46587,"peak_contact_force":0.0,"phase_name":"approach_hole","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach_hole","tcp_end":[0.516,-0.01146,0.22206],"tcp_start":[0.49666,-5e-05,0.42605],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":422.0,"n_steps_budget":780.0,"object_pos_end":[0.55242,-0.02375,0.097],"object_pos_start":[0.52293,-0.0114,0.26145],"object_to_goal_dist_end":0.06,"object_to_goal_dist_start":0.18325,"object_z_max":0.26145,"peak_contact_force":297.89542,"phase_name":"align_hole","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":507.0,"raw_peak_contact_force":2572.91398,"tcp_end":[0.51261,-0.02766,0.0977],"tcp_start":[0.516,-0.01146,0.22206],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":63.0,"n_steps_budget":750.0,"object_pos_end":[0.55364,-0.02321,0.09587],"object_pos_start":[0.55242,-0.02375,0.097],"object_to_goal_dist_end":0.06057,"object_to_goal_dist_start":0.06,"object_z_max":0.09702,"peak_contact_force":213.28563,"phase_name":"descend_insert","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":54.0,"raw_peak_contact_force":282.2411,"subtask_id":"insert_task","tcp_end":[0.51378,-0.02627,0.09709],"tcp_start":[0.51261,-0.02766,0.0977],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```