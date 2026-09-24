## Search State

- **Seed**: 7
- **Iteration**: 14 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 13 | approach → descend → grasp → retract → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | position_control | admittance_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 9 | 0.3247 | 0.89 | ❌ rejected |
| 12 | approach → descend → grasp → retract → retract → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | arc_cartesian | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | admittance_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 11 | -0.1344 | 0.57 | ❌ rejected |
| 11 | approach → descend → grasp → retract → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | position_control | admittance_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 10 | -0.2702 | 0.35 | ❌ rejected |
| 10 | approach → descend → grasp → retract → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | position_control | admittance_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 9 | 0.3273 | 0.90 | ✅ accepted |
| 9 | approach → descend → grasp → retract → approach → align → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | admittance_control | admittance_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.1107 | 0.85 | ❌ rejected |

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

## Current Skill (Q=0.325) — your mutation base

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

- **Composite score**: 0.325
- **task_score** (E): 0.895
- **fitness_score**: 0.895  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.570

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_peg | 1.00 | 0.00 | 0.0779 |
| descend_to_peg | 0.00 | 0.00 | 0.0319 |
| grasp_peg | 1.00 | 0.00 | 0.0000 |
| lift_peg | 1.00 | 0.00 | 0.0641 |
| approach_hole | 0.00 | 0.00 | 0.1978 |
| descend_insert | 0.00 | 1.00 | 0.0010 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_peg | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.502, -0.000, 0.378) | (0.504, -0.000, 0.340)→(0.501, -0.000, 0.418) | 0.260→0.338 | 0.00 / 0.000 | 0.000 | 0.000 |
| descend_to_peg | descend | 0.00 / step_budget | (0.502, -0.000, 0.378)→(0.500, -0.000, 0.410) | (0.501, -0.000, 0.418)→(0.497, 0.000, 0.450) | 0.338→0.370 | 0.00 / 0.000 | 0.000 | 0.000 |
| grasp_peg | grasp | 1.00 / step_budget | (0.498, -0.000, 0.402)→(0.498, -0.000, 0.402) | (0.497, 0.000, 0.450)→(0.495, 0.000, 0.442) | 0.370→0.362 | 0.00 / 0.000 | 0.000 | 0.000 |
| lift_peg | retract | 1.00 / step_budget | (0.498, -0.000, 0.402)→(0.497, -0.000, 0.466) | (0.495, 0.000, 0.442)→(0.490, 0.000, 0.506) | 0.362→0.426 | 0.00 / 0.000 | 0.000 | 0.000 |
| approach_hole | approach | 0.00 / step_budget | (0.497, -0.000, 0.466)→(0.501, 0.010, 0.269) | (0.490, 0.000, 0.506)→(0.507, 0.011, 0.309) | 0.426→0.230 | 0.00 / 0.000 | 0.000 | 0.000 |
| descend_insert | descend | 0.00 / guard_failure | (0.484, 0.012, 0.070)→(0.483, 0.012, 0.070) | (0.507, 0.011, 0.309)→(0.522, 0.013, 0.092) | 0.230→0.034 | 1.00 / 1.333 | 1020.107 | 1212.272 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.928
- alignment_error: None
- force_efficiency: 0.000

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.928
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.928
- **Median Q (composite search score)**: 0.332
- **K-run variance**: 0.0009
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Parameters at lower bound**: descend_to_peg.descend_speed
- **Final σ (mean)**: 0.337


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":60.0,"average_failure_rate":0.30303,"average_mean_iterations":62.9899,"average_solve_count":198.0,"average_success_count":138.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_hole.speed":0.04532,"approach_peg.speed":0.09241,"descend_insert.force_guard_threshold":166.92827,"descend_insert.insert_offset_x":-0.03632,"descend_insert.insert_offset_y":-0.03998,"descend_insert.insertion_depth":0.11292,"descend_to_peg.contact_force_threshold":13.35952,"descend_to_peg.descend_speed":0.12833,"lift_peg.lift_height":0.07923},"optimized_scores":{"best_composite_score":0.3317,"best_fitness_score":0.9017,"best_task_score":0.9017},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":1.0,"contact_point_centroid":[0.47999,0.00746,0.07999],"force_p95":1004.78662,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1004.78662,"mean_force":1004.78662,"phase_index":5.0,"phase_name":"descend_insert","phase_type":"descend","tcp_position_centroid":[0.48371,0.02049,0.07361]}],"total_contact_groups":1},"final_pose_error":0.10863,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.51001,0.03178,0.025],"final_tcp_position":[0.48103,0.02043,0.07161],"realised_fixture_position":[0.51001,0.03178,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.51001,0.03178,0.08]},"peak_contact_force":1094.9954,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":572.0,"n_steps_budget":630.0,"object_pos_end":[0.50111,-0.0,0.41929],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.33929,"object_to_goal_dist_start":0.26034,"object_z_max":0.41917,"peak_contact_force":0.0,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach_peg","tcp_end":[0.5023,-1e-05,0.3793],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":513.0,"n_steps_budget":600.0,"object_pos_end":[0.49668,1e-05,0.45097],"object_pos_start":[0.50111,-0.0,0.41929],"object_to_goal_dist_end":0.37099,"object_to_goal_dist_start":0.33929,"object_z_max":0.45092,"peak_contact_force":0.0,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.50004,-1e-05,0.41111],"tcp_start":[0.5023,-1e-05,0.3793],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":200.0,"n_steps_budget":50.0,"object_pos_end":[0.49535,1e-05,0.44301],"object_pos_start":[0.49668,1e-05,0.45097],"object_to_goal_dist_end":0.36304,"object_to_goal_dist_start":0.37099,"object_z_max":0.45099,"peak_contact_force":0.0,"phase_name":"grasp_peg","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.49802,-2e-05,0.40309],"tcp_start":[0.49802,-2e-05,0.40309],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":542.0,"n_steps_budget":600.0,"object_pos_end":[0.48949,3e-05,0.51111],"object_pos_start":[0.49535,1e-05,0.443],"object_to_goal_dist_end":0.43124,"object_to_goal_dist_start":0.36303,"object_z_max":0.511,"peak_contact_force":0.0,"phase_name":"lift_peg","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.49741,-2e-05,0.4719],"tcp_start":[0.49802,-2e-05,0.40309],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50748,0.01783,0.3143],"object_pos_start":[0.48949,3e-05,0.51111],"object_to_goal_dist_end":0.2351,"object_to_goal_dist_start":0.43124,"object_z_max":0.51116,"peak_contact_force":0.0,"phase_name":"approach_hole","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach_hole","tcp_end":[0.50217,0.01775,0.27466],"tcp_start":[0.49741,-2e-05,0.4719],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":82.0,"n_steps_budget":1000.0,"object_pos_end":[0.5163,0.01994,0.09047],"object_pos_start":[0.50748,0.01783,0.3143],"object_to_goal_dist_end":0.0278,"object_to_goal_dist_start":0.2351,"object_z_max":0.3143,"peak_contact_force":1094.9954,"phase_name":"descend_insert","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1.0,"raw_peak_contact_force":1004.78662,"subtask_id":"insert_task","tcp_end":[0.48103,0.02043,0.07161],"tcp_start":[0.48103,0.02043,0.07161],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `02e4649f08bda5439eae760bf0bc4b5a6b47c91c93317c6956c2509043be6196`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.09317,"average_solve_count":161.0,"average_success_count":161.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_hole.speed":0.03892,"approach_peg.speed":0.04792,"descend_insert.force_guard_threshold":179.92479,"descend_insert.insert_offset_x":-0.00156,"descend_insert.insert_offset_y":-0.02301,"descend_insert.insertion_depth":0.09338,"descend_to_peg.contact_force_threshold":4.87654,"descend_to_peg.descend_speed":0.16096,"lift_peg.lift_height":0.0643},"optimized_scores":{"best_composite_score":0.28428,"best_fitness_score":0.85428,"best_task_score":0.85428},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":4.0,"contact_point_centroid":[0.51662,0.02962,0.07919],"force_p95":1125.87577,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1154.79736,"mean_force":878.60665,"phase_index":5.0,"phase_name":"descend_insert","phase_type":"descend","tcp_position_centroid":[0.47952,0.02978,0.07382]}],"total_contact_groups":1},"final_pose_error":0.08672,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.48616,0.03898,0.025],"final_tcp_position":[0.4742,0.02916,0.0717],"realised_fixture_position":[0.48616,0.03898,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.48616,0.03898,0.08]},"peak_contact_force":1154.79736,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50113,-0.0,0.41519],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.33519,"object_to_goal_dist_start":0.26034,"object_z_max":0.41509,"peak_contact_force":0.0,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach_peg","tcp_end":[0.50202,-1e-05,0.3752],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":513.0,"n_steps_budget":600.0,"object_pos_end":[0.49695,1e-05,0.44689],"object_pos_start":[0.50113,-0.0,0.41519],"object_to_goal_dist_end":0.36691,"object_to_goal_dist_start":0.33519,"object_z_max":0.44684,"peak_contact_force":0.0,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.5,-1e-05,0.40701],"tcp_start":[0.50202,-1e-05,0.3752],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":200.0,"n_steps_budget":50.0,"object_pos_end":[0.49557,1e-05,0.43892],"object_pos_start":[0.49695,1e-05,0.44689],"object_to_goal_dist_end":0.35895,"object_to_goal_dist_start":0.36691,"object_z_max":0.44691,"peak_contact_force":0.0,"phase_name":"grasp_peg","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.49792,-3e-05,0.39899],"tcp_start":[0.49792,-3e-05,0.39899],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":542.0,"n_steps_budget":600.0,"object_pos_end":[0.49068,2e-05,0.49303],"object_pos_start":[0.49557,1e-05,0.43892],"object_to_goal_dist_end":0.41314,"object_to_goal_dist_start":0.35894,"object_z_max":0.49295,"peak_contact_force":0.0,"phase_name":"lift_peg","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.49714,-3e-05,0.45356],"tcp_start":[0.49792,-3e-05,0.39899],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49549,0.02321,0.29554],"object_pos_start":[0.49068,2e-05,0.49303],"object_to_goal_dist_end":0.21683,"object_to_goal_dist_start":0.41314,"object_z_max":0.49307,"peak_contact_force":0.0,"phase_name":"approach_hole","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach_hole","tcp_end":[0.48814,0.02305,0.25622],"tcp_start":[0.49714,-3e-05,0.45356],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":79.0,"n_steps_budget":1000.0,"object_pos_end":[0.51487,0.02974,0.09476],"object_pos_start":[0.49549,0.02321,0.29554],"object_to_goal_dist_end":0.03638,"object_to_goal_dist_start":0.21683,"object_z_max":0.29554,"peak_contact_force":620.64155,"phase_name":"descend_insert","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4.0,"raw_peak_contact_force":1154.79736,"subtask_id":"insert_task","tcp_end":[0.4742,0.02916,0.0717],"tcp_start":[0.47598,0.02939,0.07203],"tcp_to_object_dist_end":0.04676,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `7363bc0b3fa7329ef53220378736f8cf8ba8a5eef8ffe48ac32070ac53331cd4`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":52.0,"average_failure_rate":0.26396,"average_mean_iterations":55.50761,"average_solve_count":197.0,"average_success_count":145.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_hole.speed":0.03693,"approach_peg.speed":0.07481,"descend_insert.force_guard_threshold":105.90688,"descend_insert.insert_offset_x":-0.02239,"descend_insert.insert_offset_y":0.00569,"descend_insert.insertion_depth":0.08978,"descend_to_peg.contact_force_threshold":9.55893,"descend_to_peg.descend_speed":0.05,"lift_peg.lift_height":0.07934},"optimized_scores":{"best_composite_score":0.35811,"best_fitness_score":0.92811,"best_task_score":0.92811},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.58896,-0.00244,0.07855],"force_p95":1470.60342,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1477.23083,"mean_force":1410.95675,"phase_index":5.0,"phase_name":"descend_insert","phase_type":"descend","tcp_position_centroid":[0.49662,-0.0141,0.06748]},{"body_a":"attachment","body_b":"peg_socket","contact_count":4.0,"contact_point_centroid":[0.4965,-0.00241,0.0784],"force_p95":1041.34386,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1080.47883,"mean_force":723.94398,"phase_index":5.0,"phase_name":"descend_insert","phase_type":"descend","tcp_position_centroid":[0.49871,-0.01406,0.06906]}],"total_contact_groups":2},"final_pose_error":0.07747,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.52962,-0.01705,0.025],"final_tcp_position":[0.4947,-0.01387,0.06663],"realised_fixture_position":[0.52962,-0.01705,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.52962,-0.01705,0.08]},"peak_contact_force":1477.23083,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":722.0,"n_steps_budget":780.0,"object_pos_end":[0.50106,-0.0,0.42048],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.34048,"object_to_goal_dist_start":0.26034,"object_z_max":0.42039,"peak_contact_force":0.0,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach_peg","tcp_end":[0.50235,-1e-05,0.3805],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":513.0,"n_steps_budget":600.0,"object_pos_end":[0.49657,1e-05,0.45216],"object_pos_start":[0.50106,-0.0,0.42048],"object_to_goal_dist_end":0.37218,"object_to_goal_dist_start":0.34048,"object_z_max":0.45211,"peak_contact_force":0.0,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.50001,-1e-05,0.41231],"tcp_start":[0.50235,-1e-05,0.3805],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":200.0,"n_steps_budget":50.0,"object_pos_end":[0.49526,2e-05,0.4442],"object_pos_start":[0.49657,1e-05,0.45216],"object_to_goal_dist_end":0.36423,"object_to_goal_dist_start":0.37218,"object_z_max":0.45217,"peak_contact_force":0.0,"phase_name":"grasp_peg","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.49801,-2e-05,0.40429],"tcp_start":[0.49801,-2e-05,0.40429],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":542.0,"n_steps_budget":600.0,"object_pos_end":[0.48939,3e-05,0.51239],"object_pos_start":[0.49526,2e-05,0.4442],"object_to_goal_dist_end":0.43252,"object_to_goal_dist_start":0.36423,"object_z_max":0.51228,"peak_contact_force":0.0,"phase_name":"lift_peg","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.49741,-2e-05,0.4732],"tcp_start":[0.49801,-2e-05,0.40429],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51735,-0.0094,0.31737],"object_pos_start":[0.48939,3e-05,0.51239],"object_to_goal_dist_end":0.23819,"object_to_goal_dist_start":0.43252,"object_z_max":0.51244,"peak_contact_force":0.0,"phase_name":"approach_hole","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach_hole","tcp_end":[0.51299,-0.00946,0.27761],"tcp_start":[0.49741,-2e-05,0.4732],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":85.0,"n_steps_budget":1000.0,"object_pos_end":[0.53375,-0.01169,0.09001],"object_pos_start":[0.51735,-0.0094,0.31737],"object_to_goal_dist_end":0.03709,"object_to_goal_dist_start":0.23819,"object_z_max":0.31737,"peak_contact_force":1344.68268,"phase_name":"descend_insert","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":6.0,"raw_peak_contact_force":1477.23083,"subtask_id":"insert_task","tcp_end":[0.4947,-0.01387,0.06663],"tcp_start":[0.49588,-0.01406,0.06702],"tcp_to_object_dist_end":0.04557,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
```