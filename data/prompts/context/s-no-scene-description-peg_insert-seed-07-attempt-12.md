## Search State

- **Seed**: 7
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | approach → descend → grasp → retract → retract → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | arc_cartesian | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | admittance_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 11 | -0.1344 | 0.57 | ❌ rejected |
| 11 | approach → descend → grasp → retract → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | position_control | admittance_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 10 | -0.2702 | 0.35 | ❌ rejected |
| 10 | approach → descend → grasp → retract → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | position_control | admittance_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 9 | 0.3273 | 0.90 | ✅ accepted |
| 9 | approach → descend → grasp → retract → approach → align → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | admittance_control | admittance_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.1107 | 0.85 | ❌ rejected |
| 8 | approach → descend → grasp → retract → approach → align → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | position_control | admittance_control | admittance_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.0358 | 0.83 | ❌ rejected |

**Proposal policy**: task_score is 0.57 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.134) — your mutation base

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

- **Composite score**: -0.134
- **task_score** (E): 0.566
- **fitness_score**: 0.566  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.700

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_peg | 0.67 | 0.00 | 0.0512 |
| descend_to_peg | 0.00 | 0.00 | 0.0055 |
| grasp_peg | 1.00 | 0.00 | 0.0000 |
| lift_peg | 1.00 | 0.00 | 0.0328 |
| retract_up | 0.33 | 0.00 | 0.1584 |
| approach_hole | 0.00 | 0.00 | 0.3846 |
| descend_insert | 0.00 | 0.67 | 0.0064 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_peg | approach | 0.67 / step_budget | (0.500, -0.000, 0.301)→(0.501, -0.000, 0.352) | (0.504, -0.000, 0.340)→(0.502, -0.000, 0.392) | 0.260→0.312 | 0.00 / 0.000 | 0.000 | 0.000 |
| descend_to_peg | descend | 0.00 / step_budget | (0.501, -0.000, 0.352)→(0.500, -0.000, 0.346) | (0.502, -0.000, 0.392)→(0.501, -0.000, 0.386) | 0.312→0.306 | 0.00 / 0.000 | 0.000 | 0.000 |
| grasp_peg | grasp | 1.00 / step_budget | (0.497, -0.000, 0.338)→(0.497, -0.000, 0.338) | (0.501, -0.000, 0.386)→(0.499, -0.000, 0.378) | 0.306→0.298 | 0.00 / 0.000 | 0.000 | 0.000 |
| lift_peg | retract | 1.00 / step_budget | (0.497, -0.000, 0.338)→(0.496, -0.000, 0.371) | (0.499, -0.000, 0.378)→(0.495, -0.000, 0.411) | 0.298→0.331 | 0.00 / 0.000 | 0.000 | 0.000 |
| retract_up | retract | 0.33 / step_budget | (0.496, -0.000, 0.371)→(0.496, -0.000, 0.529) | (0.495, -0.000, 0.411)→(0.483, -0.000, 0.567) | 0.331→0.487 | 0.00 / 0.000 | 0.000 | 0.000 |
| approach_hole | approach | 0.00 / step_budget | (0.496, -0.000, 0.529)→(0.786, 0.126, 0.310) | (0.483, -0.000, 0.567)→(0.747, 0.124, 0.319) | 0.487→0.366 | 0.00 / 0.000 | 0.000 | 0.000 |
| descend_insert | descend | 0.00 / guard_failure | (0.534, -0.091, 0.083)→(0.531, -0.094, 0.082) | (0.747, 0.124, 0.319)→(0.526, -0.072, 0.095) | 0.366→0.124 | 0.67 / 1.333 | 1193.169 | 2363.571 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.913
- alignment_error: None
- force_efficiency: 0.000

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.913
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.913
- **Median Q (composite search score)**: -0.308
- **K-run variance**: 0.0604
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.293


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":15.0,"average_failure_rate":0.08523,"average_mean_iterations":22.94886,"average_solve_count":176.0,"average_success_count":161.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_hole.arc_height":0.24313,"approach_hole.speed":0.02844,"approach_peg.speed":0.01158,"descend_insert.force_guard_threshold":181.87398,"descend_insert.insert_offset_x":-0.01494,"descend_insert.insert_offset_y":0.03388,"descend_insert.insertion_depth":0.08329,"descend_to_peg.contact_force_threshold":6.3082,"descend_to_peg.descend_speed":0.1443,"lift_peg.lift_height":0.03855,"retract_up.retract_height":0.178},"optimized_scores":{"best_composite_score":-0.30758,"best_fitness_score":0.39242,"best_task_score":0.39242},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":4.0,"contact_point_centroid":[0.39915,-0.36501,-0.00262],"force_p95":3295.35936,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":3468.35723,"mean_force":2420.20399,"phase_index":6.0,"phase_name":"descend_insert","phase_type":"descend","tcp_position_centroid":[0.52329,-0.19001,0.10842]},{"body_a":"world","body_b":"link7","contact_count":4.0,"contact_point_centroid":[0.4637,-0.23871,-0.00409],"force_p95":0.0,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0,"mean_force":0.0,"phase_index":6.0,"phase_name":"descend_insert","phase_type":"descend","tcp_position_centroid":[0.52329,-0.19001,0.10842]}],"total_contact_groups":2},"final_pose_error":0.29665,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.51001,0.03178,0.025],"final_tcp_position":[0.50995,-0.20895,0.10794],"realised_fixture_position":[0.51001,0.03178,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.51001,0.03178,0.08]},"peak_contact_force":3468.35723,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50193,-1e-05,0.36328],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.28328,"object_to_goal_dist_start":0.26034,"object_z_max":0.36325,"peak_contact_force":0.0,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach_peg","tcp_end":[0.49917,-2e-05,0.32337],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":39.0,"n_steps_budget":600.0,"object_pos_end":[0.50228,-1e-05,0.35726],"object_pos_start":[0.50193,-1e-05,0.36328],"object_to_goal_dist_end":0.27727,"object_to_goal_dist_start":0.28328,"object_z_max":0.36328,"peak_contact_force":0.0,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.49915,-2e-05,0.31739],"tcp_start":[0.49917,-2e-05,0.32337],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":200.0,"n_steps_budget":50.0,"object_pos_end":[0.49957,-4e-05,0.34889],"object_pos_start":[0.50228,-1e-05,0.35726],"object_to_goal_dist_end":0.26889,"object_to_goal_dist_start":0.27727,"object_z_max":0.35726,"peak_contact_force":0.0,"phase_name":"grasp_peg","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.49568,-7e-05,0.30907],"tcp_start":[0.49568,-7e-05,0.30908],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":513.0,"n_steps_budget":600.0,"object_pos_end":[0.49597,-5e-05,0.37956],"object_pos_start":[0.49957,-4e-05,0.34889],"object_to_goal_dist_end":0.29959,"object_to_goal_dist_start":0.26889,"object_z_max":0.37951,"peak_contact_force":0.0,"phase_name":"lift_peg","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.49389,-9e-05,0.33962],"tcp_start":[0.49568,-7e-05,0.30907],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.48378,-3e-05,0.53661],"object_pos_start":[0.49597,-5e-05,0.37956],"object_to_goal_dist_end":0.4569,"object_to_goal_dist_start":0.29959,"object_z_max":0.53642,"peak_contact_force":0.0,"phase_name":"retract_up","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.49351,-8e-05,0.49781],"tcp_start":[0.49389,-9e-05,0.33962],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.74756,0.10912,0.28003],"object_pos_start":[0.48378,-3e-05,0.53661],"object_to_goal_dist_end":0.33646,"object_to_goal_dist_start":0.4569,"object_z_max":0.55625,"peak_contact_force":0.0,"phase_name":"approach_hole","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach_hole","tcp_end":[0.78578,0.11214,0.26861],"tcp_start":[0.49351,-8e-05,0.49781],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":127.0,"n_steps_budget":1000.0,"object_pos_end":[0.50393,-0.2174,0.09596],"object_pos_start":[0.74756,0.10912,0.28003],"object_to_goal_dist_end":0.21803,"object_to_goal_dist_start":0.33646,"object_z_max":0.28003,"peak_contact_force":1853.69263,"phase_name":"descend_insert","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8.0,"raw_peak_contact_force":3468.35723,"subtask_id":"insert_task","tcp_end":[0.50995,-0.20895,0.10794],"tcp_start":[0.51484,-0.20235,0.10641],"tcp_to_object_dist_end":0.01585,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `02e4649f08bda5439eae760bf0bc4b5a6b47c91c93317c6956c2509043be6196`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":4.0,"average_failure_rate":0.0274,"average_mean_iterations":10.78082,"average_solve_count":146.0,"average_success_count":142.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_hole.arc_height":0.1568,"approach_hole.speed":0.04021,"approach_peg.speed":0.0815,"descend_insert.force_guard_threshold":143.35835,"descend_insert.insert_offset_x":-0.01015,"descend_insert.insert_offset_y":-0.00616,"descend_insert.insertion_depth":0.08197,"descend_to_peg.contact_force_threshold":9.15543,"descend_to_peg.descend_speed":0.13544,"lift_peg.lift_height":0.03675,"retract_up.retract_height":0.22666},"optimized_scores":{"best_composite_score":-0.30882,"best_fitness_score":0.39118,"best_task_score":0.39118},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link5","contact_count":4.0,"contact_point_centroid":[0.4564,0.076,0.07675],"force_p95":2098.73396,"geom_a":"socket_collar_y1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":2164.54315,"mean_force":1820.27473,"phase_index":6.0,"phase_name":"descend_insert","phase_type":"descend","tcp_position_centroid":[0.62512,-0.0524,0.08168]},{"body_a":"peg_socket","body_b":"link5","contact_count":4.0,"contact_point_centroid":[0.4375,0.07668,0.07605],"force_p95":1693.81628,"geom_a":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1725.2333,"mean_force":1349.07839,"phase_index":6.0,"phase_name":"descend_insert","phase_type":"descend","tcp_position_centroid":[0.62512,-0.0524,0.08168]}],"total_contact_groups":2},"final_pose_error":0.18972,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.48616,0.03898,0.025],"final_tcp_position":[0.62918,-0.0505,0.0728],"realised_fixture_position":[0.48616,0.03898,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.48616,0.03898,0.08]},"peak_contact_force":2164.54315,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":662.0,"n_steps_budget":720.0,"object_pos_end":[0.50108,-0.0,0.42006],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.34007,"object_to_goal_dist_start":0.26034,"object_z_max":0.41996,"peak_contact_force":0.0,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach_peg","tcp_end":[0.50233,-1e-05,0.38008],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":34.0,"n_steps_budget":600.0,"object_pos_end":[0.50047,1e-05,0.41491],"object_pos_start":[0.50108,-0.0,0.42006],"object_to_goal_dist_end":0.33491,"object_to_goal_dist_start":0.34007,"object_z_max":0.42012,"peak_contact_force":0.0,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.5013,-1e-05,0.37492],"tcp_start":[0.50233,-1e-05,0.38008],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":200.0,"n_steps_budget":50.0,"object_pos_end":[0.49861,-0.0,0.40657],"object_pos_start":[0.50047,1e-05,0.41491],"object_to_goal_dist_end":0.32657,"object_to_goal_dist_start":0.33491,"object_z_max":0.41491,"peak_contact_force":0.0,"phase_name":"grasp_peg","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.4987,-4e-05,0.36657],"tcp_start":[0.4987,-4e-05,0.36657],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":513.0,"n_steps_budget":600.0,"object_pos_end":[0.49533,-0.0,0.43538],"object_pos_start":[0.49861,-0.0,0.40657],"object_to_goal_dist_end":0.35541,"object_to_goal_dist_start":0.32657,"object_z_max":0.43533,"peak_contact_force":0.0,"phase_name":"lift_peg","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.49739,-5e-05,0.39543],"tcp_start":[0.4987,-4e-05,0.36657],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.48299,2e-05,0.59042],"object_pos_start":[0.49533,-0.0,0.43538],"object_to_goal_dist_end":0.5107,"object_to_goal_dist_start":0.35541,"object_z_max":0.59023,"peak_contact_force":0.0,"phase_name":"retract_up","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.49747,-3e-05,0.55313],"tcp_start":[0.49739,-5e-05,0.39543],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.74176,0.13187,0.35502],"object_pos_start":[0.48299,2e-05,0.59042],"object_to_goal_dist_end":0.3892,"object_to_goal_dist_start":0.5107,"object_z_max":0.61146,"peak_contact_force":0.0,"phase_name":"approach_hole","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach_hole","tcp_end":[0.78115,0.13231,0.34806],"tcp_start":[0.49747,-3e-05,0.55313],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":77.0,"n_steps_budget":1000.0,"object_pos_end":[0.60875,-0.01827,0.09624],"object_pos_start":[0.74176,0.13187,0.35502],"object_to_goal_dist_end":0.11146,"object_to_goal_dist_start":0.3892,"object_z_max":0.35502,"peak_contact_force":1725.81519,"phase_name":"descend_insert","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8.0,"raw_peak_contact_force":2164.54315,"subtask_id":"insert_task","tcp_end":[0.62918,-0.0505,0.0728],"tcp_start":[0.62754,-0.05128,0.07505],"tcp_to_object_dist_end":0.04479,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `7363bc0b3fa7329ef53220378736f8cf8ba8a5eef8ffe48ac32070ac53331cd4`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":14.0,"average_failure_rate":0.08235,"average_mean_iterations":21.62941,"average_solve_count":170.0,"average_success_count":156.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_hole.arc_height":0.195,"approach_hole.speed":0.0574,"approach_peg.speed":0.03369,"descend_insert.force_guard_threshold":151.92397,"descend_insert.insert_offset_x":0.00595,"descend_insert.insert_offset_y":-0.00381,"descend_insert.insertion_depth":0.11745,"descend_to_peg.contact_force_threshold":9.40916,"descend_to_peg.descend_speed":0.15583,"lift_peg.lift_height":0.04757,"retract_up.retract_height":0.26366},"optimized_scores":{"best_composite_score":0.21321,"best_fitness_score":0.91321,"best_task_score":0.91321},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":4.0,"contact_point_centroid":[0.47461,-0.01239,0.073],"force_p95":1418.47077,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1457.81373,"mean_force":665.81247,"phase_index":6.0,"phase_name":"descend_insert","phase_type":"descend","tcp_position_centroid":[0.46976,-0.01617,0.07656]}],"total_contact_groups":1},"final_pose_error":0.1303,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.52962,-0.01705,0.025],"final_tcp_position":[0.45399,-0.02178,0.06415],"realised_fixture_position":[0.52962,-0.01705,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.52962,-0.01705,0.08]},"peak_contact_force":1457.81373,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50154,-1e-05,0.39158],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.31159,"object_to_goal_dist_start":0.26034,"object_z_max":0.39152,"peak_contact_force":0.0,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach_peg","tcp_end":[0.50072,-2e-05,0.35159],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":34.0,"n_steps_budget":600.0,"object_pos_end":[0.50141,-0.0,0.38639],"object_pos_start":[0.50154,-1e-05,0.39158],"object_to_goal_dist_end":0.30639,"object_to_goal_dist_start":0.31159,"object_z_max":0.3916,"peak_contact_force":0.0,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.50021,-2e-05,0.3464],"tcp_start":[0.50072,-2e-05,0.35159],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":200.0,"n_steps_budget":50.0,"object_pos_end":[0.49913,-2e-05,0.37802],"object_pos_start":[0.50141,-0.0,0.38639],"object_to_goal_dist_end":0.29802,"object_to_goal_dist_start":0.30639,"object_z_max":0.38639,"peak_contact_force":0.0,"phase_name":"grasp_peg","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.49719,-5e-05,0.33806],"tcp_start":[0.49719,-5e-05,0.33806],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":542.0,"n_steps_budget":600.0,"object_pos_end":[0.49512,-2e-05,0.41688],"object_pos_start":[0.49913,-2e-05,0.37802],"object_to_goal_dist_end":0.33692,"object_to_goal_dist_start":0.29802,"object_z_max":0.41682,"peak_contact_force":0.0,"phase_name":"lift_peg","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.49573,-6e-05,0.37689],"tcp_start":[0.49719,-5e-05,0.33806],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.48268,-0.0,0.57397],"object_pos_start":[0.49512,-2e-05,0.41688],"object_to_goal_dist_end":0.49427,"object_to_goal_dist_start":0.33692,"object_z_max":0.57378,"peak_contact_force":0.0,"phase_name":"retract_up","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.49567,-5e-05,0.53613],"tcp_start":[0.49573,-6e-05,0.37689],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.75055,0.13095,0.32221],"object_pos_start":[0.48268,-0.0,0.57397],"object_to_goal_dist_end":0.37227,"object_to_goal_dist_start":0.49427,"object_z_max":0.59453,"peak_contact_force":0.0,"phase_name":"approach_hole","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach_hole","tcp_end":[0.78967,0.13215,0.31396],"tcp_start":[0.49567,-5e-05,0.53613],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":100.0,"n_steps_budget":1000.0,"object_pos_end":[0.46655,0.02115,0.09423],"object_pos_start":[0.75055,0.13095,0.32221],"object_to_goal_dist_end":0.04206,"object_to_goal_dist_start":0.37227,"object_z_max":0.38955,"peak_contact_force":0.0,"phase_name":"descend_insert","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4.0,"raw_peak_contact_force":1457.81373,"subtask_id":"insert_task","tcp_end":[0.45399,-0.02178,0.06415],"tcp_start":[0.46008,-0.01978,0.06883],"tcp_to_object_dist_end":0.05391,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```