## Search State

- **Seed**: 7
- **Iteration**: 10 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 9 | approach → descend → grasp → retract → approach → align → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | admittance_control | admittance_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.1107 | 0.85 | ❌ rejected |
| 8 | approach → descend → grasp → retract → approach → align → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | position_control | admittance_control | admittance_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.0358 | 0.83 | ❌ rejected |
| 7 | approach → descend → grasp → retract → approach → align → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | position_control | admittance_control | admittance_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 9 | -0.0423 | 0.89 | ✅ accepted |
| 6 | approach → descend → grasp → retract → approach → align → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | position_control | impedance_control | admittance_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 9 | -0.0691 | 0.87 | ✅ accepted |
| 5 | approach → descend → grasp → retract → approach → align → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | position_control | impedance_control | admittance_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | 10 | -0.0733 | 0.82 | ❌ rejected |

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

## Current Skill (Q=0.111) — your mutation base

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

- **Composite score**: 0.111
- **task_score** (E): 0.854
- **fitness_score**: 0.661  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.550

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_peg | 1.00 | 0.00 | 0.0800 |
| descend_to_peg | 1.00 | 0.00 | 0.0302 |
| grasp_peg | 1.00 | 0.00 | 0.0000 |
| lift_peg | 1.00 | 0.00 | 0.0131 |
| approach_hole | 1.00 | 0.00 | 0.3088 |
| align_hole | 0.33 | 0.00 | 0.0006 |
| descend_insert | 0.00 | 1.00 | 0.0001 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_peg | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.502, -0.000, 0.380) | (0.504, -0.000, 0.340)→(0.501, -0.000, 0.420) | 0.260→0.340 | 0.00 / 0.000 | 0.000 | 0.000 |
| descend_to_peg | descend | 1.00 / step_budget | (0.502, -0.000, 0.380)→(0.500, -0.000, 0.411) | (0.501, -0.000, 0.420)→(0.497, 0.000, 0.450) | 0.340→0.370 | 0.00 / 0.000 | 0.000 | 0.000 |
| grasp_peg | grasp | 1.00 / step_budget | (0.498, -0.000, 0.403)→(0.498, -0.000, 0.403) | (0.497, 0.000, 0.450)→(0.495, 0.000, 0.443) | 0.370→0.363 | 0.00 / 0.000 | 0.000 | 0.000 |
| lift_peg | retract | 1.00 / step_budget | (0.498, -0.000, 0.403)→(0.497, -0.000, 0.416) | (0.495, 0.000, 0.443)→(0.493, 0.000, 0.456) | 0.363→0.376 | 0.00 / 0.000 | 0.000 | 0.000 |
| approach_hole | approach | 1.00 / step_budget | (0.497, -0.000, 0.416)→(0.504, 0.017, 0.109) | (0.493, 0.000, 0.456)→(0.516, 0.017, 0.147) | 0.376→0.076 | 0.00 / 0.000 | 0.000 | 0.000 |
| align_hole | align | 0.33 / guard_failure | (0.505, 0.016, 0.108)→(0.506, 0.016, 0.108) | (0.516, 0.017, 0.147)→(0.516, 0.017, 0.147) | 0.076→0.076 | 0.00 / 0.000 | 0.000 | 0.000 |
| descend_insert | descend | 0.00 / guard_failure | (0.503, 0.016, 0.054)→(0.503, 0.016, 0.054) | (0.518, 0.016, 0.146)→(0.515, 0.017, 0.092) | 0.075→0.038 | 1.00 / 1.000 | 52.716 | 182.146 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.876
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.876
- phase_score: 0.560
- phase_breakdown.approach_hole_score: 0.542
- phase_breakdown.approach_peg_score: 0.819
- phase_breakdown.insert_task_score: 0.466

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.686
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.876
- **Median Q (composite search score)**: 0.129
- **K-run variance**: 0.0009
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.474


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":11.0,"average_failure_rate":0.05914,"average_mean_iterations":16.8871,"average_solve_count":186.0,"average_success_count":175.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_hole.lateral_offset_x":-0.01567,"align_hole.lateral_offset_y":-0.00759,"approach_hole.speed":0.07815,"approach_peg.speed":0.06039,"descend_insert.force_guard_threshold":63.54883,"descend_insert.insertion_depth":0.14363,"descend_to_peg.descend_speed":0.12054,"lift_peg.lift_height":0.02002},"optimized_scores":{"best_composite_score":0.12871,"best_fitness_score":0.67871,"best_task_score":0.87038},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":4.0,"contact_point_centroid":[0.5187,0.02924,0.04981],"force_p95":120.18815,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":125.21744,"mean_force":82.20686,"phase_index":6.0,"phase_name":"descend_insert","phase_type":"descend","tcp_position_centroid":[0.50444,0.02886,0.05427]}],"total_contact_groups":1},"final_pose_error":0.1178,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.51001,0.03178,0.025],"final_tcp_position":[0.50444,0.02885,0.054],"realised_fixture_position":[0.51001,0.03178,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.51001,0.03178,0.08]},"peak_contact_force":125.21744,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":777.0,"n_steps_budget":930.0,"object_pos_end":[0.50105,-0.0,0.42043],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.34043,"object_to_goal_dist_start":0.26034,"object_z_max":0.42035,"peak_contact_force":0.0,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach_peg","tcp_end":[0.50233,-1e-05,0.38045],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":293.0,"n_steps_budget":600.0,"object_pos_end":[0.49674,1e-05,0.4504],"object_pos_start":[0.50105,-0.0,0.42043],"object_to_goal_dist_end":0.37042,"object_to_goal_dist_start":0.34043,"object_z_max":0.45031,"peak_contact_force":0.0,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.50006,-1e-05,0.41054],"tcp_start":[0.50233,-1e-05,0.38045],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":200.0,"n_steps_budget":50.0,"object_pos_end":[0.49541,1e-05,0.44248],"object_pos_start":[0.49674,1e-05,0.4504],"object_to_goal_dist_end":0.36251,"object_to_goal_dist_start":0.37042,"object_z_max":0.45045,"peak_contact_force":0.0,"phase_name":"grasp_peg","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.49804,-2e-05,0.40256],"tcp_start":[0.49804,-2e-05,0.40256],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":455.0,"n_steps_budget":600.0,"object_pos_end":[0.49336,2e-05,0.45543],"object_pos_start":[0.49541,1e-05,0.44248],"object_to_goal_dist_end":0.37549,"object_to_goal_dist_start":0.36251,"object_z_max":0.45541,"peak_contact_force":0.0,"phase_name":"lift_peg","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.49689,-3e-05,0.41559],"tcp_start":[0.49804,-2e-05,0.40256],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":982.0,"n_steps_budget":1000.0,"object_pos_end":[0.51759,0.0302,0.14713],"object_pos_start":[0.49336,2e-05,0.45543],"object_to_goal_dist_end":0.07568,"object_to_goal_dist_start":0.37549,"object_z_max":0.45543,"peak_contact_force":0.0,"phase_name":"approach_hole","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach_hole","tcp_end":[0.50581,0.03012,0.10891],"tcp_start":[0.49689,-3e-05,0.41559],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":4.0,"n_steps_budget":600.0,"object_pos_end":[0.51779,0.03004,0.14679],"object_pos_start":[0.51759,0.0302,0.14713],"object_to_goal_dist_end":0.07537,"object_to_goal_dist_start":0.07568,"object_z_max":0.14713,"peak_contact_force":0.0,"phase_name":"align_hole","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.50758,0.0282,0.10733],"tcp_start":[0.50688,0.02892,0.10779],"tcp_to_object_dist_end":0.04081,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":162.0,"n_steps_budget":1000.0,"object_pos_end":[0.51682,0.0292,0.09234],"object_pos_start":[0.51951,0.0285,0.14551],"object_to_goal_dist_end":0.03589,"object_to_goal_dist_start":0.07406,"object_z_max":0.14551,"peak_contact_force":48.79029,"phase_name":"descend_insert","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4.0,"raw_peak_contact_force":125.21744,"subtask_id":"insert_task","tcp_end":[0.50444,0.02885,0.054],"tcp_start":[0.50445,0.02886,0.05406],"tcp_to_object_dist_end":0.04029,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `02e4649f08bda5439eae760bf0bc4b5a6b47c91c93317c6956c2509043be6196`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.48295,"average_solve_count":176.0,"average_success_count":176.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_hole.lateral_offset_x":-0.02923,"align_hole.lateral_offset_y":-0.00316,"approach_hole.speed":0.08559,"approach_peg.speed":0.04809,"descend_insert.force_guard_threshold":125.55431,"descend_insert.insertion_depth":0.11141,"descend_to_peg.descend_speed":0.1554,"lift_peg.lift_height":0.02016},"optimized_scores":{"best_composite_score":0.06748,"best_fitness_score":0.61748,"best_task_score":0.81694},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":4.0,"contact_point_centroid":[0.49546,0.03701,0.04979],"force_p95":128.17803,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":133.82254,"mean_force":86.05448,"phase_index":6.0,"phase_name":"descend_insert","phase_type":"descend","tcp_position_centroid":[0.48144,0.03671,0.05489]}],"total_contact_groups":1},"final_pose_error":0.08617,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.48616,0.03898,0.025],"final_tcp_position":[0.48147,0.0367,0.0546],"realised_fixture_position":[0.48616,0.03898,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.48616,0.03898,0.08]},"peak_contact_force":133.82254,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":786.0,"n_steps_budget":1000.0,"object_pos_end":[0.50105,-0.0,0.4205],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.3405,"object_to_goal_dist_start":0.26034,"object_z_max":0.42041,"peak_contact_force":0.0,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach_peg","tcp_end":[0.50233,-1e-05,0.38052],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":293.0,"n_steps_budget":600.0,"object_pos_end":[0.49674,1e-05,0.45047],"object_pos_start":[0.50105,-0.0,0.4205],"object_to_goal_dist_end":0.37049,"object_to_goal_dist_start":0.3405,"object_z_max":0.45038,"peak_contact_force":0.0,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.50006,-1e-05,0.41061],"tcp_start":[0.50233,-1e-05,0.38052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":200.0,"n_steps_budget":50.0,"object_pos_end":[0.49541,1e-05,0.44255],"object_pos_start":[0.49674,1e-05,0.45047],"object_to_goal_dist_end":0.36258,"object_to_goal_dist_start":0.37049,"object_z_max":0.45052,"peak_contact_force":0.0,"phase_name":"grasp_peg","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.49804,-2e-05,0.40263],"tcp_start":[0.49804,-2e-05,0.40263],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":455.0,"n_steps_budget":600.0,"object_pos_end":[0.49335,2e-05,0.45563],"object_pos_start":[0.49541,1e-05,0.44255],"object_to_goal_dist_end":0.37569,"object_to_goal_dist_start":0.36258,"object_z_max":0.45561,"peak_contact_force":0.0,"phase_name":"lift_peg","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.4969,-3e-05,0.41579],"tcp_start":[0.49804,-2e-05,0.40263],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":971.0,"n_steps_budget":1000.0,"object_pos_end":[0.49664,0.03723,0.14679],"object_pos_start":[0.49335,2e-05,0.45563],"object_to_goal_dist_end":0.07654,"object_to_goal_dist_start":0.37569,"object_z_max":0.45563,"peak_contact_force":0.0,"phase_name":"approach_hole","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach_hole","tcp_end":[0.48307,0.03698,0.10917],"tcp_start":[0.4969,-3e-05,0.41579],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":4.0,"n_steps_budget":600.0,"object_pos_end":[0.49681,0.03708,0.14646],"object_pos_start":[0.49664,0.03723,0.14679],"object_to_goal_dist_end":0.07617,"object_to_goal_dist_start":0.07654,"object_z_max":0.14679,"peak_contact_force":0.0,"phase_name":"align_hole","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.4846,0.03604,0.1076],"tcp_start":[0.48398,0.03633,0.10805],"tcp_to_object_dist_end":0.04075,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":165.0,"n_steps_budget":870.0,"object_pos_end":[0.49559,0.03701,0.09233],"object_pos_start":[0.49834,0.03632,0.14516],"object_to_goal_dist_end":0.03926,"object_to_goal_dist_start":0.07462,"object_z_max":0.14516,"peak_contact_force":49.35576,"phase_name":"descend_insert","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4.0,"raw_peak_contact_force":133.82254,"subtask_id":"insert_task","tcp_end":[0.48147,0.0367,0.0546],"tcp_start":[0.48147,0.03671,0.05466],"tcp_to_object_dist_end":0.04029,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `7363bc0b3fa7329ef53220378736f8cf8ba8a5eef8ffe48ac32070ac53331cd4`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":80.0,"average_failure_rate":0.33473,"average_mean_iterations":69.24686,"average_solve_count":239.0,"average_success_count":159.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_hole.lateral_offset_x":-0.0146,"align_hole.lateral_offset_y":-0.00452,"approach_hole.speed":0.08806,"approach_peg.speed":0.07088,"descend_insert.force_guard_threshold":199.93338,"descend_insert.insertion_depth":0.14693,"descend_to_peg.descend_speed":0.1574,"lift_peg.lift_height":0.02001},"optimized_scores":{"best_composite_score":0.136,"best_fitness_score":0.686,"best_task_score":0.8757},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":4.0,"contact_point_centroid":[0.53636,-0.01637,0.04982],"force_p95":258.75049,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":287.39814,"mean_force":127.56098,"phase_index":6.0,"phase_name":"descend_insert","phase_type":"descend","tcp_position_centroid":[0.52192,-0.01649,0.05368]}],"total_contact_groups":1},"final_pose_error":0.1206,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.52962,-0.01705,0.025],"final_tcp_position":[0.52189,-0.01649,0.05342],"realised_fixture_position":[0.52962,-0.01705,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.52962,-0.01705,0.08]},"peak_contact_force":287.39814,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":698.0,"n_steps_budget":810.0,"object_pos_end":[0.50106,-0.0,0.42045],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.34045,"object_to_goal_dist_start":0.26034,"object_z_max":0.42035,"peak_contact_force":0.0,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach_peg","tcp_end":[0.50234,-1e-05,0.38047],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":293.0,"n_steps_budget":600.0,"object_pos_end":[0.49675,1e-05,0.45042],"object_pos_start":[0.50106,-0.0,0.42045],"object_to_goal_dist_end":0.37043,"object_to_goal_dist_start":0.34045,"object_z_max":0.45033,"peak_contact_force":0.0,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.50007,-1e-05,0.41056],"tcp_start":[0.50234,-1e-05,0.38047],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":200.0,"n_steps_budget":50.0,"object_pos_end":[0.49542,1e-05,0.44249],"object_pos_start":[0.49675,1e-05,0.45042],"object_to_goal_dist_end":0.36252,"object_to_goal_dist_start":0.37043,"object_z_max":0.45047,"peak_contact_force":0.0,"phase_name":"grasp_peg","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.49805,-2e-05,0.40258],"tcp_start":[0.49805,-2e-05,0.40258],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":455.0,"n_steps_budget":600.0,"object_pos_end":[0.49337,2e-05,0.45544],"object_pos_start":[0.49542,1e-05,0.44249],"object_to_goal_dist_end":0.3755,"object_to_goal_dist_start":0.36252,"object_z_max":0.45541,"peak_contact_force":0.0,"phase_name":"lift_peg","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.4969,-3e-05,0.41559],"tcp_start":[0.49805,-2e-05,0.40258],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":981.0,"n_steps_budget":1000.0,"object_pos_end":[0.53482,-0.01621,0.14701],"object_pos_start":[0.49337,2e-05,0.45544],"object_to_goal_dist_end":0.07724,"object_to_goal_dist_start":0.3755,"object_z_max":0.45544,"peak_contact_force":0.0,"phase_name":"approach_hole","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach_hole","tcp_end":[0.5245,-0.01629,0.10836],"tcp_start":[0.4969,-3e-05,0.41559],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":0.0,"n_steps_budget":600.0,"object_pos_end":[0.53482,-0.01621,0.14701],"object_pos_start":[0.53482,-0.01621,0.14701],"object_to_goal_dist_end":0.07724,"object_to_goal_dist_start":0.07724,"peak_contact_force":0.0,"phase_name":"align_hole","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.5245,-0.01629,0.10836],"tcp_start":[0.5245,-0.01629,0.10836],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":172.0,"n_steps_budget":1000.0,"object_pos_end":[0.53271,-0.01641,0.09223],"object_pos_start":[0.53482,-0.01621,0.14701],"object_to_goal_dist_end":0.03859,"object_to_goal_dist_start":0.07724,"object_z_max":0.14701,"peak_contact_force":60.00048,"phase_name":"descend_insert","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4.0,"raw_peak_contact_force":287.39814,"subtask_id":"insert_task","tcp_end":[0.52189,-0.01649,0.05342],"tcp_start":[0.52191,-0.01649,0.05348],"tcp_to_object_dist_end":0.04029,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```