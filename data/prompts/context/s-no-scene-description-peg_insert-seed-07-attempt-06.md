## Search State

- **Seed**: 7
- **Iteration**: 7 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 6 | approach → descend → grasp → retract → approach → align → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | position_control | impedance_control | admittance_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 9 | -0.0691 | 0.87 | ✅ accepted |
| 5 | approach → descend → grasp → retract → approach → align → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | position_control | impedance_control | admittance_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | 10 | -0.0733 | 0.82 | ❌ rejected |
| 4 | approach → descend → grasp → retract → approach → align → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | admittance_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | 10 | -0.0088 | 0.76 | ❌ rejected |
| 3 | approach → descend → grasp → retract → approach → align → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | position_control | impedance_control | admittance_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | 9 | 0.0842 | 0.87 | ✅ accepted |
| 2 | approach → descend → grasp → retract → approach → align → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | position_control | impedance_control | admittance_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | 9 | 0.0765 | 0.87 | ✅ accepted |

**Proposal policy**: task_score is 0.87 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.069) — your mutation base

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
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.02
    tolerance: 0.003
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
      distance: 0.08
      axis: world_z
      mode: replace_offset_projection
      sign: negative
    tolerance: 0.005
    orientation:
      mode: keep_current
  parameters:
    insert_force_limit:
      type: scalar
      range:
      - 10.0
      - 40.0
      default: 30.0
      binds_to:
      - path: guards.insert_force.threshold
        mode: replace
    insertion_depth:
      type: scalar
      range:
      - 0.02
      - 0.12
      default: 0.08
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
  guards:
  - id: insert_force
    when: during_phase
    predicate: force_below
    threshold: 30.0
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
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.02], tolerance=0.003
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=world_z, tolerance=0.1
  - parameter_bindings:
    - lateral_offset_x: status=consumed; consumers=target.offset.x (add)
    - lateral_offset_y: status=consumed; consumers=target.offset.y (add)
- **descend_insert** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.08, mode=replace_offset_projection, sign=negative}, tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings:
    - insert_force_limit: status=consumed; consumers=guards.insert_force.threshold (replace)
    - insertion_depth: status=consumed; consumers=target.offset_along_axis.distance (replace)
  - guards:
    - id=insert_force, when=during_phase, predicate=force_below, on_failure=abort, threshold=30.0
  - retries: max_attempts=3, strategy=offset_target, offset=[0.003, 0.003, 0.0]

## Design Metrics

- **Composite score**: -0.069
- **task_score** (E): 0.875
- **fitness_score**: 0.531  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.600

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_peg | 1.00 | 0.00 | 0.0795 |
| descend_to_peg | 0.00 | 0.00 | 0.0319 |
| grasp_peg | 1.00 | 0.00 | 0.0000 |
| lift_peg | 1.00 | 0.00 | 0.0378 |
| approach_hole | 0.00 | 0.00 | 0.2009 |
| align_hole | 0.67 | 1.00 | 0.1196 |
| descend_insert | 0.00 | 0.67 | 0.0003 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_peg | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.502, -0.000, 0.380) | (0.504, -0.000, 0.340)→(0.501, -0.000, 0.420) | 0.260→0.340 | 0.00 / 0.000 | 0.000 | 0.000 |
| descend_to_peg | descend | 0.00 / step_budget | (0.502, -0.000, 0.380)→(0.500, -0.000, 0.412) | (0.501, -0.000, 0.420)→(0.497, 0.000, 0.452) | 0.340→0.372 | 0.00 / 0.000 | 0.000 | 0.000 |
| grasp_peg | grasp | 1.00 / step_budget | (0.498, -0.000, 0.404)→(0.498, -0.000, 0.404) | (0.497, 0.000, 0.452)→(0.495, 0.000, 0.444) | 0.372→0.364 | 0.00 / 0.000 | 0.000 | 0.000 |
| lift_peg | retract | 1.00 / step_budget | (0.498, -0.000, 0.404)→(0.497, -0.000, 0.442) | (0.495, 0.000, 0.444)→(0.492, 0.000, 0.481) | 0.364→0.401 | 0.00 / 0.000 | 0.000 | 0.000 |
| approach_hole | approach | 0.00 / step_budget | (0.497, -0.000, 0.442)→(0.502, 0.011, 0.242) | (0.492, 0.000, 0.481)→(0.509, 0.011, 0.281) | 0.401→0.203 | 0.00 / 0.000 | 0.000 | 0.000 |
| align_hole | align | 0.67 / step_budget | (0.502, 0.011, 0.242)→(0.494, 0.005, 0.139) | (0.509, 0.011, 0.281)→(0.531, 0.004, 0.128) | 0.203→0.082 | 1.00 / 1.000 | 335.440 | 4510.597 |
| descend_insert | descend | 0.00 / guard_failure | (0.494, 0.005, 0.139)→(0.494, 0.005, 0.139) | (0.531, 0.004, 0.128)→(0.531, 0.004, 0.128) | 0.082→0.082 | 0.67 / 0.667 | 101.194 | 124.112 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.850
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.850
- phase_score: 0.346
- phase_breakdown.approach_hole_score: 0.071
- phase_breakdown.approach_peg_score: 0.805
- phase_breakdown.insert_task_score: 0.328

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.548
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.928
- **Median Q (composite search score)**: -0.062
- **K-run variance**: 0.0003
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.317


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":2.0,"average_failure_rate":0.01258,"average_mean_iterations":6.64151,"average_solve_count":159.0,"average_success_count":157.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_hole.lateral_offset_x":-0.00411,"align_hole.lateral_offset_y":-0.00638,"approach_hole.speed":0.08203,"approach_peg.speed":0.05281,"descend_insert.insert_force_limit":22.93137,"descend_insert.insertion_depth":0.09158,"descend_to_peg.contact_force_threshold":4.04385,"descend_to_peg.descend_speed":0.12361,"lift_peg.lift_height":0.04521},"optimized_scores":{"best_composite_score":-0.06226,"best_fitness_score":0.53774,"best_task_score":0.84552},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link7","contact_count":557.0,"contact_point_centroid":[0.5696,0.00969,0.07572],"force_p95":1049.24769,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1585.4454,"mean_force":518.02707,"phase_index":5.0,"phase_name":"align_hole","phase_type":"align","tcp_position_centroid":[0.49295,0.04387,0.09847]},{"body_a":"attachment","body_b":"peg_socket","contact_count":492.0,"contact_point_centroid":[0.56031,0.03765,0.07964],"force_p95":949.51338,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1503.03039,"mean_force":436.90006,"phase_index":5.0,"phase_name":"align_hole","phase_type":"align","tcp_position_centroid":[0.49701,0.04441,0.0968]},{"body_a":"peg_socket","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.56997,0.02427,0.07483],"force_p95":68.75404,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":68.75404,"mean_force":68.75404,"phase_index":6.0,"phase_name":"descend_insert","phase_type":"descend","tcp_position_centroid":[0.4998,0.05994,0.10917]}],"total_contact_groups":3},"final_pose_error":0.1245,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.51001,0.03178,0.025],"final_tcp_position":[0.4999,0.06022,0.1092],"realised_fixture_position":[0.51001,0.03178,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.51001,0.03178,0.08]},"peak_contact_force":1585.4454,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50105,-0.0,0.41954],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.33954,"object_to_goal_dist_start":0.26034,"object_z_max":0.41944,"peak_contact_force":0.0,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach_peg","tcp_end":[0.50226,-1e-05,0.37956],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":513.0,"n_steps_budget":600.0,"object_pos_end":[0.49661,1e-05,0.45123],"object_pos_start":[0.50105,-0.0,0.41954],"object_to_goal_dist_end":0.37125,"object_to_goal_dist_start":0.33954,"object_z_max":0.45118,"peak_contact_force":0.0,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.49999,-1e-05,0.41137],"tcp_start":[0.50226,-1e-05,0.37956],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":200.0,"n_steps_budget":50.0,"object_pos_end":[0.49529,1e-05,0.44326],"object_pos_start":[0.49661,1e-05,0.45123],"object_to_goal_dist_end":0.36329,"object_to_goal_dist_start":0.37125,"object_z_max":0.45124,"peak_contact_force":0.0,"phase_name":"grasp_peg","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.49797,-3e-05,0.40335],"tcp_start":[0.49797,-3e-05,0.40335],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":513.0,"n_steps_budget":600.0,"object_pos_end":[0.49165,2e-05,0.47968],"object_pos_start":[0.49529,1e-05,0.44326],"object_to_goal_dist_end":0.39977,"object_to_goal_dist_start":0.36329,"object_z_max":0.47962,"peak_contact_force":0.0,"phase_name":"lift_peg","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.49705,-3e-05,0.44005],"tcp_start":[0.49797,-3e-05,0.40335],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51065,0.0212,0.26702],"object_pos_start":[0.49165,2e-05,0.47968],"object_to_goal_dist_end":0.18852,"object_to_goal_dist_start":0.39977,"object_z_max":0.4797,"peak_contact_force":0.0,"phase_name":"approach_hole","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach_hole","tcp_end":[0.50301,0.0211,0.22775],"tcp_start":[0.49705,-3e-05,0.44005],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":721.0,"n_steps_budget":810.0,"object_pos_end":[0.53855,0.05356,0.10156],"object_pos_start":[0.51065,0.0212,0.26702],"object_to_goal_dist_end":0.06942,"object_to_goal_dist_start":0.18852,"object_z_max":0.26702,"peak_contact_force":333.14439,"phase_name":"align_hole","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":1049.0,"raw_peak_contact_force":1585.4454,"tcp_end":[0.4998,0.05994,0.10917],"tcp_start":[0.50301,0.0211,0.22775],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1.0,"n_steps_budget":780.0,"object_pos_end":[0.53864,0.05381,0.10159],"object_pos_start":[0.53855,0.05356,0.10156],"object_to_goal_dist_end":0.06968,"object_to_goal_dist_start":0.06942,"object_z_max":0.10156,"peak_contact_force":0.0,"phase_name":"descend_insert","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1.0,"raw_peak_contact_force":68.75404,"subtask_id":"insert_task","tcp_end":[0.4999,0.06022,0.1092],"tcp_start":[0.4998,0.05994,0.10917],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `02e4649f08bda5439eae760bf0bc4b5a6b47c91c93317c6956c2509043be6196`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.12281,"average_solve_count":171.0,"average_success_count":171.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_hole.lateral_offset_x":-0.02428,"align_hole.lateral_offset_y":-0.02935,"approach_hole.speed":0.05597,"approach_peg.speed":0.08876,"descend_insert.insert_force_limit":23.69237,"descend_insert.insertion_depth":0.04101,"descend_to_peg.contact_force_threshold":6.61927,"descend_to_peg.descend_speed":0.15009,"lift_peg.lift_height":0.06382},"optimized_scores":{"best_composite_score":-0.05199,"best_fitness_score":0.54801,"best_task_score":0.85036},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":26.0,"contact_point_centroid":[0.51659,0.02705,0.07884],"force_p95":9901.26416,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":10545.04847,"mean_force":6181.43477,"phase_index":5.0,"phase_name":"align_hole","phase_type":"align","tcp_position_centroid":[0.45697,0.02704,0.07182]},{"body_a":"peg_socket","body_b":"link7","contact_count":910.0,"contact_point_centroid":[0.54595,0.01792,0.07361],"force_p95":304.88385,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":6041.31257,"mean_force":372.97358,"phase_index":5.0,"phase_name":"align_hole","phase_type":"align","tcp_position_centroid":[0.46979,0.0303,0.10839]},{"body_a":"attachment","body_b":"peg_socket","contact_count":20.0,"contact_point_centroid":[0.45455,0.02682,0.07941],"force_p95":5721.31427,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":5734.64469,"mean_force":3500.71972,"phase_index":5.0,"phase_name":"align_hole","phase_type":"align","tcp_position_centroid":[0.45578,0.02694,0.0712]},{"body_a":"peg_socket","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.54607,0.00782,0.07547],"force_p95":264.12853,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":264.12853,"mean_force":264.12853,"phase_index":6.0,"phase_name":"descend_insert","phase_type":"descend","tcp_position_centroid":[0.47391,0.03777,0.11167]}],"total_contact_groups":4},"final_pose_error":0.07366,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.48616,0.03898,0.025],"final_tcp_position":[0.47397,0.03772,0.11162],"realised_fixture_position":[0.48616,0.03898,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.48616,0.03898,0.08]},"peak_contact_force":10545.04847,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":602.0,"n_steps_budget":660.0,"object_pos_end":[0.5011,-0.0,0.41957],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.33957,"object_to_goal_dist_start":0.26034,"object_z_max":0.41946,"peak_contact_force":0.0,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach_peg","tcp_end":[0.50231,-1e-05,0.37959],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":513.0,"n_steps_budget":600.0,"object_pos_end":[0.49665,1e-05,0.45126],"object_pos_start":[0.5011,-0.0,0.41957],"object_to_goal_dist_end":0.37127,"object_to_goal_dist_start":0.33957,"object_z_max":0.4512,"peak_contact_force":0.0,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.50003,-1e-05,0.4114],"tcp_start":[0.50231,-1e-05,0.37959],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":200.0,"n_steps_budget":50.0,"object_pos_end":[0.49533,1e-05,0.44329],"object_pos_start":[0.49665,1e-05,0.45126],"object_to_goal_dist_end":0.36332,"object_to_goal_dist_start":0.37127,"object_z_max":0.45127,"peak_contact_force":0.0,"phase_name":"grasp_peg","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.49801,-2e-05,0.40338],"tcp_start":[0.49801,-2e-05,0.40338],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":542.0,"n_steps_budget":600.0,"object_pos_end":[0.49049,3e-05,0.49693],"object_pos_start":[0.49533,1e-05,0.44329],"object_to_goal_dist_end":0.41704,"object_to_goal_dist_start":0.36332,"object_z_max":0.49685,"peak_contact_force":0.0,"phase_name":"lift_peg","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.49726,-2e-05,0.45751],"tcp_start":[0.49801,-2e-05,0.40338],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49543,0.02297,0.2992],"object_pos_start":[0.49049,3e-05,0.49693],"object_to_goal_dist_end":0.22045,"object_to_goal_dist_start":0.41704,"object_z_max":0.49697,"peak_contact_force":0.0,"phase_name":"approach_hole","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach_hole","tcp_end":[0.48829,0.02281,0.25984],"tcp_start":[0.49726,-2e-05,0.45751],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":991.0,"n_steps_budget":1000.0,"object_pos_end":[0.513,0.03373,0.10421],"object_pos_start":[0.49543,0.02297,0.2992],"object_to_goal_dist_end":0.04351,"object_to_goal_dist_start":0.22045,"object_z_max":0.2992,"peak_contact_force":306.38092,"phase_name":"align_hole","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":956.0,"raw_peak_contact_force":10545.04847,"tcp_end":[0.47391,0.03777,0.11167],"tcp_start":[0.48829,0.02281,0.25984],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.51306,0.03368,0.10418],"object_pos_start":[0.513,0.03373,0.10421],"object_to_goal_dist_end":0.04347,"object_to_goal_dist_start":0.04351,"object_z_max":0.10421,"peak_contact_force":264.12853,"phase_name":"descend_insert","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1.0,"raw_peak_contact_force":264.12853,"subtask_id":"insert_task","tcp_end":[0.47397,0.03772,0.11162],"tcp_start":[0.47391,0.03777,0.11167],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `7363bc0b3fa7329ef53220378736f8cf8ba8a5eef8ffe48ac32070ac53331cd4`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":4.0,"average_failure_rate":0.02247,"average_mean_iterations":8.25843,"average_solve_count":178.0,"average_success_count":174.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_hole.lateral_offset_x":-0.01736,"align_hole.lateral_offset_y":0.01247,"approach_hole.speed":0.02193,"approach_peg.speed":0.06433,"descend_insert.insert_force_limit":30.7837,"descend_insert.insertion_depth":0.07946,"descend_to_peg.contact_force_threshold":13.84552,"descend_to_peg.descend_speed":0.08869,"lift_peg.lift_height":0.02973},"optimized_scores":{"best_composite_score":-0.09294,"best_fitness_score":0.50706,"best_task_score":0.92768},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":11.0,"contact_point_centroid":[0.5625,-0.01243,0.07762],"force_p95":1392.36847,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1401.29724,"mean_force":766.65603,"phase_index":5.0,"phase_name":"align_hole","phase_type":"align","tcp_position_centroid":[0.54556,-0.01308,0.07903]},{"body_a":"peg_socket","body_b":"link7","contact_count":274.0,"contact_point_centroid":[0.58291,-0.03611,0.07953],"force_p95":529.04778,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1196.27332,"mean_force":321.95484,"phase_index":5.0,"phase_name":"align_hole","phase_type":"align","tcp_position_centroid":[0.48538,-0.03794,0.16274]},{"body_a":"attachment","body_b":"peg_socket","contact_count":14.0,"contact_point_centroid":[0.4936,-0.01151,0.07812],"force_p95":890.19903,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":913.10904,"mean_force":266.24966,"phase_index":5.0,"phase_name":"align_hole","phase_type":"align","tcp_position_centroid":[0.4897,-0.01648,0.08765]},{"body_a":"peg_socket","body_b":"link6","contact_count":321.0,"contact_point_centroid":[0.58956,-0.01704,0.07987],"force_p95":333.35847,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":357.91232,"mean_force":273.8803,"phase_index":5.0,"phase_name":"align_hole","phase_type":"align","tcp_position_centroid":[0.47862,-0.03504,0.17583]},{"body_a":"peg_socket","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.57862,-0.07691,0.07978],"force_p95":39.45367,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":39.45367,"mean_force":39.45367,"phase_index":6.0,"phase_name":"descend_insert","phase_type":"descend","tcp_position_centroid":[0.50716,-0.08354,0.19656]}],"total_contact_groups":5},"final_pose_error":0.20842,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.52962,-0.01705,0.025],"final_tcp_position":[0.50727,-0.08401,0.19664],"realised_fixture_position":[0.52962,-0.01705,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.52962,-0.01705,0.08]},"peak_contact_force":1401.29724,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":812.0,"n_steps_budget":870.0,"object_pos_end":[0.50105,-0.0,0.42078],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.34078,"object_to_goal_dist_start":0.26034,"object_z_max":0.42069,"peak_contact_force":0.0,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach_peg","tcp_end":[0.50235,-1e-05,0.3808],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":513.0,"n_steps_budget":600.0,"object_pos_end":[0.49654,1e-05,0.45246],"object_pos_start":[0.50105,-0.0,0.42078],"object_to_goal_dist_end":0.37248,"object_to_goal_dist_start":0.34078,"object_z_max":0.45241,"peak_contact_force":0.0,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.5,-1e-05,0.41261],"tcp_start":[0.50235,-1e-05,0.3808],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":200.0,"n_steps_budget":50.0,"object_pos_end":[0.49523,2e-05,0.4445],"object_pos_start":[0.49654,1e-05,0.45246],"object_to_goal_dist_end":0.36453,"object_to_goal_dist_start":0.37248,"object_z_max":0.45247,"peak_contact_force":0.0,"phase_name":"grasp_peg","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.498,-2e-05,0.40459],"tcp_start":[0.498,-2e-05,0.40459],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":484.0,"n_steps_budget":600.0,"object_pos_end":[0.49256,2e-05,0.46678],"object_pos_start":[0.49523,2e-05,0.4445],"object_to_goal_dist_end":0.38686,"object_to_goal_dist_start":0.36453,"object_z_max":0.46674,"peak_contact_force":0.0,"phase_name":"lift_peg","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.49696,-3e-05,0.42703],"tcp_start":[0.498,-2e-05,0.40459],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5208,-0.01051,0.27746],"object_pos_start":[0.49256,2e-05,0.46678],"object_to_goal_dist_end":0.19883,"object_to_goal_dist_start":0.38686,"object_z_max":0.46679,"peak_contact_force":0.0,"phase_name":"approach_hole","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach_hole","tcp_end":[0.51452,-0.01056,0.23796],"tcp_start":[0.49696,-3e-05,0.42703],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":721.0,"n_steps_budget":870.0,"object_pos_end":[0.54253,-0.07593,0.1795],"object_pos_start":[0.5208,-0.01051,0.27746],"object_to_goal_dist_end":0.13218,"object_to_goal_dist_start":0.19883,"object_z_max":0.27746,"peak_contact_force":366.79466,"phase_name":"align_hole","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":620.0,"raw_peak_contact_force":1401.29724,"tcp_end":[0.50716,-0.08354,0.19656],"tcp_start":[0.51452,-0.01056,0.23796],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.54265,-0.07639,0.17959],"object_pos_start":[0.54253,-0.07593,0.1795],"object_to_goal_dist_end":0.13256,"object_to_goal_dist_start":0.13218,"object_z_max":0.1795,"peak_contact_force":39.45367,"phase_name":"descend_insert","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1.0,"raw_peak_contact_force":39.45367,"subtask_id":"insert_task","tcp_end":[0.50727,-0.08401,0.19664],"tcp_start":[0.50716,-0.08354,0.19656],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```