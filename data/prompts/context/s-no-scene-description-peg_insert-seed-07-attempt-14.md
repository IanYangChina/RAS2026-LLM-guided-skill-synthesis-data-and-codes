## Search State

- **Seed**: 7
- **Iteration**: 15 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 14 | approach → descend → grasp → retract → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | position_control | admittance_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 9 | 0.3274 | 0.90 | ✅ accepted |
| 13 | approach → descend → grasp → retract → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | position_control | admittance_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 9 | 0.3247 | 0.89 | ❌ rejected |
| 12 | approach → descend → grasp → retract → retract → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | arc_cartesian | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | admittance_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 11 | -0.1344 | 0.57 | ❌ rejected |
| 11 | approach → descend → grasp → retract → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | position_control | admittance_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 10 | -0.2702 | 0.35 | ❌ rejected |
| 10 | approach → descend → grasp → retract → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | position_control | admittance_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 9 | 0.3273 | 0.90 | ✅ accepted |

**Proposal policy**: task_score is 0.90 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.327) — your mutation base

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

- **Composite score**: 0.327
- **task_score** (E): 0.897
- **fitness_score**: 0.897  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.570

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_peg | 1.00 | 0.00 | 0.0788 |
| descend_to_peg | 0.00 | 0.00 | 0.0319 |
| grasp_peg | 1.00 | 0.00 | 0.0000 |
| lift_peg | 1.00 | 0.00 | 0.0620 |
| approach_hole | 0.00 | 0.00 | 0.1977 |
| descend_insert | 0.00 | 1.00 | 0.0003 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_peg | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.502, -0.000, 0.379) | (0.504, -0.000, 0.340)→(0.501, -0.000, 0.419) | 0.260→0.339 | 0.00 / 0.000 | 0.000 | 0.000 |
| descend_to_peg | descend | 0.00 / step_budget | (0.502, -0.000, 0.379)→(0.500, -0.000, 0.411) | (0.501, -0.000, 0.419)→(0.497, 0.000, 0.451) | 0.339→0.371 | 0.00 / 0.000 | 0.000 | 0.000 |
| grasp_peg | grasp | 1.00 / step_budget | (0.498, -0.000, 0.403)→(0.498, -0.000, 0.403) | (0.497, 0.000, 0.451)→(0.495, 0.000, 0.443) | 0.371→0.363 | 0.00 / 0.000 | 0.000 | 0.000 |
| lift_peg | retract | 1.00 / step_budget | (0.498, -0.000, 0.403)→(0.497, -0.000, 0.465) | (0.495, 0.000, 0.443)→(0.490, 0.000, 0.504) | 0.363→0.424 | 0.00 / 0.000 | 0.000 | 0.000 |
| approach_hole | approach | 0.00 / step_budget | (0.497, -0.000, 0.465)→(0.501, 0.011, 0.268) | (0.490, 0.000, 0.504)→(0.507, 0.011, 0.308) | 0.424→0.229 | 0.00 / 0.000 | 0.000 | 0.000 |
| descend_insert | descend | 0.00 / guard_failure | (0.488, 0.012, 0.071)→(0.488, 0.012, 0.071) | (0.507, 0.011, 0.308)→(0.524, 0.013, 0.092) | 0.229→0.035 | 1.00 / 1.667 | 1264.208 | 1254.063 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.927
- alignment_error: None
- force_efficiency: 0.000

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.927
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.927
- **Median Q (composite search score)**: 0.334
- **K-run variance**: 0.0007
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.381


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":60.0,"average_failure_rate":0.29851,"average_mean_iterations":62.10448,"average_solve_count":201.0,"average_success_count":141.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_hole.speed":0.05393,"approach_peg.speed":0.0805,"descend_insert.force_guard_threshold":296.39591,"descend_insert.insert_offset_x":-0.00763,"descend_insert.insert_offset_y":-0.03989,"descend_insert.insertion_depth":0.07135,"descend_to_peg.contact_force_threshold":11.82331,"descend_to_peg.descend_speed":0.13367,"lift_peg.lift_height":0.07804},"optimized_scores":{"best_composite_score":0.33354,"best_fitness_score":0.90354,"best_task_score":0.90354},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":1.0,"contact_point_centroid":[0.47888,0.00837,0.07941],"force_p95":1025.66651,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1025.66651,"mean_force":1025.66651,"phase_index":5.0,"phase_name":"descend_insert","phase_type":"descend","tcp_position_centroid":[0.48219,0.02027,0.07087]}],"total_contact_groups":1},"final_pose_error":0.07045,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.51001,0.03178,0.025],"final_tcp_position":[0.47951,0.02021,0.06896],"realised_fixture_position":[0.51001,0.03178,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.51001,0.03178,0.08]},"peak_contact_force":1590.75612,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":662.0,"n_steps_budget":720.0,"object_pos_end":[0.50108,-0.0,0.42006],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.34007,"object_to_goal_dist_start":0.26034,"object_z_max":0.41996,"peak_contact_force":0.0,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach_peg","tcp_end":[0.50233,-1e-05,0.38008],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":513.0,"n_steps_budget":600.0,"object_pos_end":[0.49661,1e-05,0.45175],"object_pos_start":[0.50108,-0.0,0.42006],"object_to_goal_dist_end":0.37176,"object_to_goal_dist_start":0.34007,"object_z_max":0.45169,"peak_contact_force":0.0,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.50002,-1e-05,0.41189],"tcp_start":[0.50233,-1e-05,0.38008],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":200.0,"n_steps_budget":50.0,"object_pos_end":[0.49529,1e-05,0.44378],"object_pos_start":[0.49661,1e-05,0.45175],"object_to_goal_dist_end":0.36381,"object_to_goal_dist_start":0.37176,"object_z_max":0.45176,"peak_contact_force":0.0,"phase_name":"grasp_peg","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.49801,-2e-05,0.40387],"tcp_start":[0.49801,-2e-05,0.40387],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":542.0,"n_steps_budget":600.0,"object_pos_end":[0.4895,3e-05,0.5108],"object_pos_start":[0.49529,1e-05,0.44378],"object_to_goal_dist_end":0.43092,"object_to_goal_dist_start":0.36381,"object_z_max":0.51069,"peak_contact_force":0.0,"phase_name":"lift_peg","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.49739,-2e-05,0.47158],"tcp_start":[0.49801,-2e-05,0.40387],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50751,0.01785,0.31397],"object_pos_start":[0.4895,3e-05,0.5108],"object_to_goal_dist_end":0.23477,"object_to_goal_dist_start":0.43092,"object_z_max":0.51085,"peak_contact_force":0.0,"phase_name":"approach_hole","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach_hole","tcp_end":[0.50218,0.01777,0.27432],"tcp_start":[0.49739,-2e-05,0.47158],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":83.0,"n_steps_budget":1000.0,"object_pos_end":[0.5151,0.01971,0.08722],"object_pos_start":[0.50751,0.01785,0.31397],"object_to_goal_dist_end":0.02586,"object_to_goal_dist_start":0.23477,"object_z_max":0.31397,"peak_contact_force":1590.75612,"phase_name":"descend_insert","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1.0,"raw_peak_contact_force":1025.66651,"subtask_id":"insert_task","tcp_end":[0.47951,0.02021,0.06896],"tcp_start":[0.47951,0.02021,0.06896],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `02e4649f08bda5439eae760bf0bc4b5a6b47c91c93317c6956c2509043be6196`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":60.0,"average_failure_rate":0.27523,"average_mean_iterations":57.33486,"average_solve_count":218.0,"average_success_count":158.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_hole.speed":0.0179,"approach_peg.speed":0.0488,"descend_insert.force_guard_threshold":144.25444,"descend_insert.insert_offset_x":0.03155,"descend_insert.insert_offset_y":-0.03631,"descend_insert.insertion_depth":0.05501,"descend_to_peg.contact_force_threshold":8.16771,"descend_to_peg.descend_speed":0.14497,"lift_peg.lift_height":0.05835},"optimized_scores":{"best_composite_score":0.29122,"best_fitness_score":0.86122,"best_task_score":0.86122},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":1.0,"contact_point_centroid":[0.51638,0.02955,0.07967],"force_p95":1138.53861,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1138.53861,"mean_force":1138.53861,"phase_index":5.0,"phase_name":"descend_insert","phase_type":"descend","tcp_position_centroid":[0.49161,0.02968,0.08053]}],"total_contact_groups":1},"final_pose_error":0.06629,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.48616,0.03898,0.025],"final_tcp_position":[0.48879,0.0295,0.07827],"realised_fixture_position":[0.48616,0.03898,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.48616,0.03898,0.08]},"peak_contact_force":1138.53861,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50109,-0.0,0.41734],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.33734,"object_to_goal_dist_start":0.26034,"object_z_max":0.41724,"peak_contact_force":0.0,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach_peg","tcp_end":[0.50214,-1e-05,0.37735],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":513.0,"n_steps_budget":600.0,"object_pos_end":[0.49678,1e-05,0.44903],"object_pos_start":[0.50109,-0.0,0.41734],"object_to_goal_dist_end":0.36905,"object_to_goal_dist_start":0.33734,"object_z_max":0.44898,"peak_contact_force":0.0,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.49999,-1e-05,0.40916],"tcp_start":[0.50214,-1e-05,0.37735],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":200.0,"n_steps_budget":50.0,"object_pos_end":[0.49543,1e-05,0.44106],"object_pos_start":[0.49678,1e-05,0.44903],"object_to_goal_dist_end":0.36109,"object_to_goal_dist_start":0.36905,"object_z_max":0.44905,"peak_contact_force":0.0,"phase_name":"grasp_peg","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.49794,-3e-05,0.40114],"tcp_start":[0.49794,-3e-05,0.40114],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":542.0,"n_steps_budget":600.0,"object_pos_end":[0.49093,2e-05,0.48968],"object_pos_start":[0.49543,1e-05,0.44106],"object_to_goal_dist_end":0.40978,"object_to_goal_dist_start":0.36109,"object_z_max":0.4896,"peak_contact_force":0.0,"phase_name":"lift_peg","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.49712,-3e-05,0.45016],"tcp_start":[0.49794,-3e-05,0.40114],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49556,0.02341,0.29253],"object_pos_start":[0.49093,2e-05,0.48968],"object_to_goal_dist_end":0.21386,"object_to_goal_dist_start":0.40978,"object_z_max":0.48971,"peak_contact_force":0.0,"phase_name":"approach_hole","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach_hole","tcp_end":[0.48805,0.02324,0.25324],"tcp_start":[0.49712,-3e-05,0.45016],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":74.0,"n_steps_budget":1000.0,"object_pos_end":[0.52232,0.0292,0.10008],"object_pos_start":[0.49556,0.02341,0.29253],"object_to_goal_dist_end":0.04188,"object_to_goal_dist_start":0.21386,"object_z_max":0.29253,"peak_contact_force":1034.00911,"phase_name":"descend_insert","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1.0,"raw_peak_contact_force":1138.53861,"subtask_id":"insert_task","tcp_end":[0.48879,0.0295,0.07827],"tcp_start":[0.48879,0.0295,0.07827],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `7363bc0b3fa7329ef53220378736f8cf8ba8a5eef8ffe48ac32070ac53331cd4`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":41.0,"average_failure_rate":0.21809,"average_mean_iterations":47.87766,"average_solve_count":188.0,"average_success_count":147.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_hole.speed":0.05578,"approach_peg.speed":0.06894,"descend_insert.force_guard_threshold":162.14183,"descend_insert.insert_offset_x":0.02341,"descend_insert.insert_offset_y":0.01797,"descend_insert.insertion_depth":0.10964,"descend_to_peg.contact_force_threshold":3.28748,"descend_to_peg.descend_speed":0.08342,"lift_peg.lift_height":0.07959},"optimized_scores":{"best_composite_score":0.35739,"best_fitness_score":0.92739,"best_task_score":0.92739},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.58888,-0.00193,0.07844],"force_p95":1578.01832,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1597.98398,"mean_force":1388.05644,"phase_index":5.0,"phase_name":"descend_insert","phase_type":"descend","tcp_position_centroid":[0.49731,-0.01369,0.06735]},{"body_a":"attachment","body_b":"peg_socket","contact_count":4.0,"contact_point_centroid":[0.49623,-0.00275,0.07835],"force_p95":1011.40832,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1075.24272,"mean_force":641.56365,"phase_index":5.0,"phase_name":"descend_insert","phase_type":"descend","tcp_position_centroid":[0.49843,-0.0137,0.06814]}],"total_contact_groups":2},"final_pose_error":0.11322,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.52962,-0.01705,0.025],"final_tcp_position":[0.49482,-0.01356,0.06639],"realised_fixture_position":[0.52962,-0.01705,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.52962,-0.01705,0.08]},"peak_contact_force":1597.98398,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":782.0,"n_steps_budget":840.0,"object_pos_end":[0.50106,-0.0,0.4205],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.3405,"object_to_goal_dist_start":0.26034,"object_z_max":0.42042,"peak_contact_force":0.0,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach_peg","tcp_end":[0.50234,-1e-05,0.38052],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":513.0,"n_steps_budget":600.0,"object_pos_end":[0.49656,1e-05,0.45218],"object_pos_start":[0.50106,-0.0,0.4205],"object_to_goal_dist_end":0.3722,"object_to_goal_dist_start":0.3405,"object_z_max":0.45213,"peak_contact_force":0.0,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.50001,-1e-05,0.41233],"tcp_start":[0.50234,-1e-05,0.38052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":200.0,"n_steps_budget":50.0,"object_pos_end":[0.49525,2e-05,0.44422],"object_pos_start":[0.49656,1e-05,0.45218],"object_to_goal_dist_end":0.36425,"object_to_goal_dist_start":0.3722,"object_z_max":0.4522,"peak_contact_force":0.0,"phase_name":"grasp_peg","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.498,-2e-05,0.40431],"tcp_start":[0.498,-2e-05,0.40431],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":542.0,"n_steps_budget":600.0,"object_pos_end":[0.48936,3e-05,0.51265],"object_pos_start":[0.49525,2e-05,0.44422],"object_to_goal_dist_end":0.43278,"object_to_goal_dist_start":0.36425,"object_z_max":0.51254,"peak_contact_force":0.0,"phase_name":"lift_peg","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.4974,-2e-05,0.47346],"tcp_start":[0.498,-2e-05,0.40431],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51731,-0.00939,0.31768],"object_pos_start":[0.48936,3e-05,0.51265],"object_to_goal_dist_end":0.23849,"object_to_goal_dist_start":0.43278,"object_z_max":0.5127,"peak_contact_force":0.0,"phase_name":"approach_hole","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach_hole","tcp_end":[0.51296,-0.00946,0.27791],"tcp_start":[0.4974,-2e-05,0.47346],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":86.0,"n_steps_budget":1000.0,"object_pos_end":[0.53369,-0.01137,0.08838],"object_pos_start":[0.51731,-0.00939,0.31768],"object_to_goal_dist_end":0.03653,"object_to_goal_dist_start":0.23849,"object_z_max":0.31768,"peak_contact_force":1167.85795,"phase_name":"descend_insert","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":7.0,"raw_peak_contact_force":1597.98398,"subtask_id":"insert_task","tcp_end":[0.49482,-0.01356,0.06639],"tcp_start":[0.49572,-0.01357,0.06647],"tcp_to_object_dist_end":0.04471,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```