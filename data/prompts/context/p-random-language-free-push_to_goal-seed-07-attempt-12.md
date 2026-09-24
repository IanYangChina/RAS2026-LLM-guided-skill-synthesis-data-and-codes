## Search State

- **Seed**: 7
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | approach → contact → push → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | admittance_control | position_control | pose_tolerance | force_exceeded | time_limit | time_limit | pose_tolerance | 9 | -0.0232 | 0.35 | ❌ rejected |
| 11 | approach → contact → push → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | admittance_control | position_control | pose_tolerance | force_exceeded | time_limit | time_limit | pose_tolerance | 9 | 0.0916 | 0.38 | ❌ rejected |
| 10 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 6 | 0.6665 | 0.74 | ❌ rejected |
| 9 | approach → contact → push → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | admittance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | 9 | 0.3836 | 0.88 | ✅ accepted |
| 8 | approach → contact → push → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | admittance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.3499 | 0.77 | ❌ rejected |

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

- Task name: push_to_goal
- Frozen realised-scene SHA-256: `c8d09cd43835becf8e5eb4413394fad8627e4bf404e9e7726e9f380b60e09752`
- Frozen object start: [0.51501145599256, 0.047665656116349056, 0.025]
- Frozen task target: [0.5, -0.15, 0.025]
- Goal object position: (0.5, -0.15, 0.025)
- Object initial pose: (0.51501145599256, 0.047665656116349056, 0.025)
- Goal tolerance: 0.02 m
- Expressivity sigma: 1.0 m
- Expressivity threshold: 0.8
- Force limit: 25.0 N
- Robot initial TCP position: (0.5, 0.0, 0.3)
- Phase navigation guidance: the task `phase_target_map` may provide internal predefined TCP waypoint aliases / semantic phase ids. These names are not DSL phase types and are intentionally not enumerated here to avoid confusing ids with types. Phase `id` may be semantic, but phase `type` must be exactly one of the DSL enum values listed in the prompt.
- Primary evaluation target: **object displacement ratio toward goal_object_position**

## Scene Entities

robot:
  model: panda_pusher
  tcp_site: attachment_site
  gripper: null
  tcp_initial_world: [0.5, 0, 0.3]
objects:
  - name: push_box
    role: manipulated_object
    dynamics: free
    geometry: box
    dimensions_m: [0.05, 0.05, 0.05]
    mass_kg: 0.1
  - name: goal_marker
    role: target_marker
    dynamics: static
    geometry: point
task_landmarks:
  frozen_object_start: [0.515, 0.0477, 0.025]
  frozen_task_target: [0.5, -0.15, 0.025]
  frozen_object_starts: {'push_box': [0.51501145599256, 0.047665656116349056, 0.025]}
  frozen_targets: {'task_goal': [0.5, -0.15, 0.025]}
  push_direction: [-0.015, -0.1977, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 25
  force_scale_n: 5
  realized_scene_sha256: c8d09cd43835becf8e5eb4413394fad8627e4bf404e9e7726e9f380b60e09752

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.885, which indicates the subtask decomposition is already effective.
> Preserve the current subtask decomposition unless the evidence shows a subtask change is necessary. Prefer refining phases, parameters, control modes, or termination conditions first.
> Unnecessary subtask redesign when performance is already high often causes regression.

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
| `object` | offset from object initial position (0.51501145599256, 0.047665656116349056, 0.025) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5, -0.15, 0.025) | final destination targets |
| `fixture` | offset from fixture pose (if defined, else world) | targets near fixture |

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

## Current Skill (Q=-0.023) — your mutation base

```yaml
skill: push_to_goal
dsl_version: 2
subtasks:
- id: reach_object
  anchor: object
  weight: 0.3
- id: push_goal
  target_entity: object
  metric: goal_progress
  weight: 0.7
phases:
- id: approach_object
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
    - 0.0
    offset_along_axis:
      distance: 0.1
      axis: task_goal_direction
      mode: add_to_offset
      sign: negative
    orientation:
      mode: keep_current
  parameters:
    approach_distance:
      type: scalar
      range:
      - 0.05
      - 0.15
      default: 0.1
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    approach_speed:
      type: scalar
      range:
      - 0.02
      - 0.08
      default: 0.04
      binds_to:
      - path: generator.speed
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat
  subtask_id: reach_object
- id: contact_object
  type: contact
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
    orientation:
      mode: keep_current
  parameters:
    contact_force_threshold:
      type: scalar
      range:
      - 3.0
      - 15.0
      default: 8.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
  guards:
  - id: contact_made
    when: after_phase
    predicate: contact_detected
    threshold: 0.5
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: reduce_speed
  subtask_id: reach_object
- id: push_stage1
  type: push
  generator: linear_cartesian
  control: admittance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.2
      axis: task_goal_direction
      mode: add_to_offset
      sign: positive
    orientation:
      mode: keep_current
  parameters:
    push1_distance:
      type: scalar
      range:
      - 0.1
      - 0.35
      default: 0.2
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push1_speed:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
    push1_tolerance:
      type: scalar
      range:
      - 0.01
      - 0.04
      default: 0.025
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat
  subtask_id: push_goal
- id: push_stage2
  type: push
  generator: linear_cartesian
  control: admittance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.12
      axis: task_goal_direction
      mode: add_to_offset
      sign: positive
    orientation:
      mode: keep_current
  parameters:
    push2_distance:
      type: scalar
      range:
      - 0.05
      - 0.25
      default: 0.12
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push2_speed:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
    push2_tolerance:
      type: scalar
      range:
      - 0.01
      - 0.04
      default: 0.025
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat
  subtask_id: push_goal
- id: retract_after_push
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
    - 0.1
    orientation:
      mode: keep_current
  retries:
    max_attempts: 0
    strategy: repeat

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_object** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.1, mode=add_to_offset, sign=negative}
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - approach_speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=0, strategy=repeat
- **contact_object** (`contact`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - contact_force_threshold: status=consumed; consumers=termination.force_threshold (replace)
  - guards:
    - id=contact_made, when=after_phase, predicate=contact_detected, on_failure=retry, threshold=0.5
  - retries: max_attempts=2, strategy=reduce_speed
- **push_stage1** (`push`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.2, mode=add_to_offset, sign=positive}
  - orientation: mode=keep_current
  - parameter_bindings:
    - push1_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push1_speed: status=consumed; consumers=generator.speed (replace)
    - push1_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
  - retries: max_attempts=0, strategy=repeat
- **push_stage2** (`push`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.12, mode=add_to_offset, sign=positive}
  - orientation: mode=keep_current
  - parameter_bindings:
    - push2_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push2_speed: status=consumed; consumers=generator.speed (replace)
    - push2_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
  - retries: max_attempts=0, strategy=repeat
- **retract_after_push** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.1]
  - orientation: mode=keep_current
  - parameter_bindings: none
  - retries: max_attempts=0, strategy=repeat

## Design Metrics

- **Composite score**: -0.023
- **task_score** (E): 0.354
- **fitness_score**: 0.183  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.333
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.540

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1848 |
| contact_object | 1.00 | 1.00 | 0.0709 |
| push_stage1 | 1.00 | 1.00 | 0.1654 |
| push_stage2 | 1.00 | 1.00 | 0.1695 |
| retract_after_push | 1.00 | 1.00 | 0.0878 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.509, 0.024, 0.123) | (0.513, 0.027, 0.025)→(0.513, 0.027, 0.025) | 0.180→0.180 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact_object | contact | 1.00 / force_exceeded | (0.509, 0.024, 0.123)→(0.507, 0.026, 0.052) | (0.513, 0.027, 0.025)→(0.513, 0.027, 0.025) | 0.180→0.180 | 1.00 / 5.000 | 25328.632 | 0.245 |
| push_stage1 | push | 1.00 / time_limit | (0.507, 0.026, 0.052)→(0.479, -0.134, 0.048) | (0.513, 0.027, 0.025)→(0.504, -0.032, 0.025) | 0.180→0.120 | 1.00 / 4.000 | 0.245 | 85.330 |
| push_stage2 | push | 1.00 / time_limit | (0.479, -0.134, 0.048)→(0.456, -0.298, 0.042) | (0.504, -0.032, 0.025)→(0.504, -0.032, 0.025) | 0.120→0.120 | 1.00 / 4.000 | 0.245 | 0.245 |
| retract_after_push | retract | 1.00 / step_budget | (0.456, -0.298, 0.042)→(0.453, -0.296, 0.130) | (0.504, -0.032, 0.025)→(0.504, -0.032, 0.025) | 0.120→0.120 | 1.00 / 4.000 | 0.245 | 0.245 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.508
- lateral_force_integral: None
- approach_alignment: 0.962
- goal_progress: 0.507
- terminal_score: 0.507
- phase_score: 0.070
- phase_breakdown.push_goal_score: 0.000
- phase_breakdown.reach_object_score: 0.233

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.245
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.507
- **Median Q (composite search score)**: -0.049
- **K-run variance**: 0.0019
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.333


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `75e2389a1a667086aa2b9c0de482ff37adf5571150b90a83772692baadf8b52e`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.06,0.06]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `154c216c563de6b8ee153943e5b668ca6d0c7dfd9253696b060f91a67dca06ec`; realized-scene SHA-256: `c8d09cd43835becf8e5eb4413394fad8627e4bf404e9e7726e9f380b60e09752`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.51501,0.04767,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.01501,-0.19767,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.51501,0.04767,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.62346,"average_solve_count":162.0,"average_success_count":162.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_height":0.07622,"approach_object.approach_speed":0.06099,"contact_object.contact_force_threshold":11.38352,"push_stage1.push1_distance":0.18539,"push_stage1.push1_max_time":1.98847,"push_stage1.push1_speed":0.11959,"push_stage2.push2_distance":0.14165,"push_stage2.push2_max_time":2.29622,"push_stage2.push2_speed":0.12736},"optimized_scores":{"best_composite_score":-0.04933,"best_fitness_score":0.15733,"best_task_score":0.28842},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":386.0,"contact_point_centroid":[0.51402,0.02023,0.05071],"force_p95":78.76362,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":82.28091,"mean_force":47.38581,"phase_index":2.0,"phase_name":"push_stage1","phase_type":"push","tcp_position_centroid":[0.5068,0.01258,0.05177]},{"body_a":"world","body_b":"push_box","contact_count":2792.0,"contact_point_centroid":[0.51093,0.00162,-9e-05],"force_p95":38.01519,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":51.13737,"mean_force":6.86758,"phase_index":2.0,"phase_name":"push_stage1","phase_type":"push","tcp_position_centroid":[0.49915,-0.05395,0.04888]},{"body_a":"world","body_b":"push_box","contact_count":2700.0,"contact_point_centroid":[0.51501,0.04767,-1e-05],"force_p95":0.24528,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.50432,0.02173,0.20455]},{"body_a":"world","body_b":"push_box","contact_count":1180.0,"contact_point_centroid":[0.51501,0.04767,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_object","phase_type":"contact","tcp_position_centroid":[0.50886,0.04498,0.07973]},{"body_a":"world","body_b":"push_box","contact_count":2700.0,"contact_point_centroid":[0.50979,-0.00928,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":3.0,"phase_name":"push_stage2","phase_type":"push","tcp_position_centroid":[0.48423,-0.1936,0.04279]},{"body_a":"world","body_b":"push_box","contact_count":2180.0,"contact_point_centroid":[0.50979,-0.00928,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":4.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.476,-0.26031,0.08472]}],"total_contact_groups":6},"final_pose_error":0.01267,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50979,-0.00928,0.02499],"final_tcp_position":[0.4761,-0.26029,0.12982],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.51501,0.04767,0.025]},"peak_contact_force":82.28091,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":675.0,"n_steps_budget":1000.0,"object_pos_end":[0.51501,0.04767,0.02499],"object_pos_start":[0.51501,0.04767,0.025],"object_to_goal_dist_end":0.19823,"object_to_goal_dist_start":0.19823,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2700.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_object","tcp_end":[0.51065,0.04422,0.10932],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.08452,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":295.0,"n_steps_budget":600.0,"object_pos_end":[0.51501,0.04767,0.02499],"object_pos_start":[0.51501,0.04767,0.02499],"object_to_goal_dist_end":0.19823,"object_to_goal_dist_start":0.19823,"object_z_max":0.02499,"peak_contact_force":41.3113,"phase_name":"contact_object","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1180.0,"raw_peak_contact_force":0.24525,"subtask_id":"reach_object","tcp_end":[0.5095,0.04595,0.05243],"tcp_start":[0.51065,0.04422,0.10932],"tcp_to_object_dist_end":0.02804,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":945.0,"n_steps_budget":990.0,"object_pos_end":[0.50979,-0.00928,0.02499],"object_pos_start":[0.51501,0.04767,0.02499],"object_to_goal_dist_end":0.14106,"object_to_goal_dist_start":0.19823,"object_z_max":0.03529,"peak_contact_force":0.24525,"phase_name":"push_stage1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3178.0,"raw_peak_contact_force":82.28091,"subtask_id":"push_goal","tcp_end":[0.49221,-0.1304,0.04756],"tcp_start":[0.5095,0.04595,0.05243],"tcp_to_object_dist_end":0.12446,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":675.0,"n_steps_budget":720.0,"object_pos_end":[0.50979,-0.00928,0.02499],"object_pos_start":[0.50979,-0.00928,0.02499],"object_to_goal_dist_end":0.14106,"object_to_goal_dist_start":0.14106,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"push_stage2","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2700.0,"raw_peak_contact_force":0.24525,"subtask_id":"push_goal","tcp_end":[0.47918,-0.26177,0.04201],"tcp_start":[0.49221,-0.1304,0.04756],"tcp_to_object_dist_end":0.25491,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":545.0,"n_steps_budget":630.0,"object_pos_end":[0.50979,-0.00928,0.02499],"object_pos_start":[0.50979,-0.00928,0.02499],"object_to_goal_dist_end":0.14106,"object_to_goal_dist_start":0.14106,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"retract_after_push","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2180.0,"raw_peak_contact_force":0.24525,"subtask_id":"push_goal","tcp_end":[0.4761,-0.26029,0.12982],"tcp_start":[0.47918,-0.26177,0.04201],"tcp_to_object_dist_end":0.2741,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `4d55d9375783bea830660bf0a13dfc76a97a0d4f5645e7ebcc1ef7143776d0b7`; realized-scene SHA-256: `f3b8ea82cefd9504be10e2d47c49094a836a703404c06bdee3b01a27a59bf7be`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.47924,0.05847,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[0.02076,-0.20847,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.47924,0.05847,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.7483,"average_solve_count":147.0,"average_success_count":147.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_height":0.13913,"approach_object.approach_speed":0.06841,"contact_object.contact_force_threshold":10.52023,"push_stage1.push1_distance":0.11542,"push_stage1.push1_max_time":1.77908,"push_stage1.push1_speed":0.10637,"push_stage2.push2_distance":0.19036,"push_stage2.push2_max_time":1.44388,"push_stage2.push2_speed":0.12839},"optimized_scores":{"best_composite_score":-0.05854,"best_fitness_score":0.14813,"best_task_score":0.26542},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":383.0,"contact_point_centroid":[0.48608,0.03346,0.05064],"force_p95":80.82547,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":84.48796,"mean_force":53.82013,"phase_index":2.0,"phase_name":"push_stage1","phase_type":"push","tcp_position_centroid":[0.47835,0.02611,0.05172]},{"body_a":"world","body_b":"push_box","contact_count":1482.0,"contact_point_centroid":[0.47964,0.02178,-0.00018],"force_p95":58.24561,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":67.93471,"mean_force":14.31823,"phase_index":2.0,"phase_name":"push_stage1","phase_type":"push","tcp_position_centroid":[0.47942,-0.00117,0.05001]},{"body_a":"world","body_b":"push_box","contact_count":1872.0,"contact_point_centroid":[0.47924,0.05847,-1e-05],"force_p95":0.2453,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.48864,0.02568,0.23618]},{"body_a":"world","body_b":"push_box","contact_count":2476.0,"contact_point_centroid":[0.47924,0.05847,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_object","phase_type":"contact","tcp_position_centroid":[0.47567,0.0547,0.11071]},{"body_a":"world","body_b":"push_box","contact_count":3564.0,"contact_point_centroid":[0.47923,0.00249,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":3.0,"phase_name":"push_stage2","phase_type":"push","tcp_position_centroid":[0.49067,-0.13724,0.04321]},{"body_a":"world","body_b":"push_box","contact_count":2176.0,"contact_point_centroid":[0.47923,0.00249,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":4.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.49971,-0.22828,0.08482]}],"total_contact_groups":6},"final_pose_error":0.01283,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.47923,0.00249,0.02499],"final_tcp_position":[0.49981,-0.22825,0.12984],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47924,0.05847,0.025]},"peak_contact_force":84.48796,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":468.0,"n_steps_budget":1000.0,"object_pos_end":[0.47924,0.05847,0.02499],"object_pos_start":[0.47924,0.05847,0.025],"object_to_goal_dist_end":0.2095,"object_to_goal_dist_start":0.2095,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1872.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_object","tcp_end":[0.47836,0.05283,0.17212],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.14725,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":619.0,"n_steps_budget":930.0,"object_pos_end":[0.47924,0.05847,0.02499],"object_pos_start":[0.47924,0.05847,0.02499],"object_to_goal_dist_end":0.2095,"object_to_goal_dist_start":0.2095,"object_z_max":0.02499,"peak_contact_force":51.0486,"phase_name":"contact_object","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2476.0,"raw_peak_contact_force":0.24525,"subtask_id":"reach_object","tcp_end":[0.47538,0.0568,0.05231],"tcp_start":[0.47836,0.05283,0.17212],"tcp_to_object_dist_end":0.02764,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":638.0,"n_steps_budget":690.0,"object_pos_end":[0.47923,0.00249,0.02499],"object_pos_start":[0.47924,0.05847,0.02499],"object_to_goal_dist_end":0.1539,"object_to_goal_dist_start":0.2095,"object_z_max":0.03534,"peak_contact_force":0.24524,"phase_name":"push_stage1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1865.0,"raw_peak_contact_force":84.48796,"subtask_id":"push_goal","tcp_end":[0.48237,-0.05083,0.04788],"tcp_start":[0.47538,0.0568,0.05231],"tcp_to_object_dist_end":0.05811,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":891.0,"n_steps_budget":930.0,"object_pos_end":[0.47923,0.00249,0.02499],"object_pos_start":[0.47923,0.00249,0.02499],"object_to_goal_dist_end":0.1539,"object_to_goal_dist_start":0.1539,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"push_stage2","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3564.0,"raw_peak_contact_force":0.24525,"subtask_id":"push_goal","tcp_end":[0.50301,-0.22953,0.0422],"tcp_start":[0.48237,-0.05083,0.04788],"tcp_to_object_dist_end":0.23387,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":544.0,"n_steps_budget":630.0,"object_pos_end":[0.47923,0.00249,0.02499],"object_pos_start":[0.47923,0.00249,0.02499],"object_to_goal_dist_end":0.1539,"object_to_goal_dist_start":0.1539,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"retract_after_push","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2176.0,"raw_peak_contact_force":0.24525,"subtask_id":"push_goal","tcp_end":[0.49981,-0.22825,0.12984],"tcp_start":[0.50301,-0.22953,0.0422],"tcp_to_object_dist_end":0.25428,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `0a9238470f4497c7aa88b149b7cee960f9853513db10bf496723f5ea1d3a6043`; realized-scene SHA-256: `2cf7387f3e8baf02f18930263090d6f78777bdbc147b7fa30c178332e76b547b`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.54443,-0.02558,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.04443,-0.12442,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.54443,-0.02558,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.51562,"average_solve_count":192.0,"average_success_count":192.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_height":0.05586,"approach_object.approach_speed":0.04706,"contact_object.contact_force_threshold":8.7461,"push_stage1.push1_distance":0.22257,"push_stage1.push1_max_time":1.62623,"push_stage1.push1_speed":0.18658,"push_stage2.push2_distance":0.24749,"push_stage2.push2_max_time":2.62236,"push_stage2.push2_speed":0.12289},"optimized_scores":{"best_composite_score":0.03818,"best_fitness_score":0.24485,"best_task_score":0.50741},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":288.0,"contact_point_centroid":[0.53475,-0.04971,0.05169],"force_p95":84.72505,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":89.21968,"mean_force":53.81004,"phase_index":2.0,"phase_name":"push_stage1","phase_type":"push","tcp_position_centroid":[0.52644,-0.05664,0.05274]},{"body_a":"world","body_b":"push_box","contact_count":2090.0,"contact_point_centroid":[0.52811,-0.07776,-0.0001],"force_p95":57.3886,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":78.33286,"mean_force":7.755,"phase_index":2.0,"phase_name":"push_stage1","phase_type":"push","tcp_position_centroid":[0.49503,-0.13517,0.04899]},{"body_a":"world","body_b":"push_box","contact_count":3112.0,"contact_point_centroid":[0.54443,-0.02558,-1e-05],"force_p95":0.24527,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.5179,-0.01185,0.19389]},{"body_a":"world","body_b":"push_box","contact_count":776.0,"contact_point_centroid":[0.54443,-0.02558,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_object","phase_type":"contact","tcp_position_centroid":[0.53665,-0.02436,0.06928]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.52441,-0.08967,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":3.0,"phase_name":"push_stage2","phase_type":"push","tcp_position_centroid":[0.42305,-0.31009,0.04265]},{"body_a":"world","body_b":"push_box","contact_count":2180.0,"contact_point_centroid":[0.52441,-0.08967,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":4.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.38288,-0.40008,0.08447]}],"total_contact_groups":6},"final_pose_error":0.01277,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.52441,-0.08967,0.02499],"final_tcp_position":[0.383,-0.40008,0.12957],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.54443,-0.02558,0.025]},"peak_contact_force":75893.53664,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":778.0,"n_steps_budget":1000.0,"object_pos_end":[0.54443,-0.02558,0.02499],"object_pos_start":[0.54443,-0.02558,0.025],"object_to_goal_dist_end":0.13211,"object_to_goal_dist_start":0.13211,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3112.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_object","tcp_end":[0.53818,-0.02402,0.08823],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.06357,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":194.0,"n_steps_budget":600.0,"object_pos_end":[0.54443,-0.02558,0.02499],"object_pos_start":[0.54443,-0.02558,0.02499],"object_to_goal_dist_end":0.13211,"object_to_goal_dist_start":0.13211,"object_z_max":0.02499,"peak_contact_force":75893.53664,"phase_name":"contact_object","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":776.0,"raw_peak_contact_force":0.24525,"subtask_id":"reach_object","tcp_end":[0.53718,-0.0247,0.05247],"tcp_start":[0.53818,-0.02402,0.08823],"tcp_to_object_dist_end":0.02843,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":721.0,"n_steps_budget":750.0,"object_pos_end":[0.52441,-0.08967,0.02499],"object_pos_start":[0.54443,-0.02558,0.02499],"object_to_goal_dist_end":0.06508,"object_to_goal_dist_start":0.13211,"object_z_max":0.03527,"peak_contact_force":0.24525,"phase_name":"push_stage1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2378.0,"raw_peak_contact_force":89.21968,"subtask_id":"push_goal","tcp_end":[0.4627,-0.22198,0.04755],"tcp_start":[0.53718,-0.0247,0.05247],"tcp_to_object_dist_end":0.14772,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52441,-0.08967,0.02499],"object_pos_start":[0.52441,-0.08967,0.02499],"object_to_goal_dist_end":0.06508,"object_to_goal_dist_start":0.06508,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"push_stage2","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24525,"subtask_id":"push_goal","tcp_end":[0.38552,-0.40237,0.04189],"tcp_start":[0.4627,-0.22198,0.04755],"tcp_to_object_dist_end":0.34258,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":545.0,"n_steps_budget":630.0,"object_pos_end":[0.52441,-0.08967,0.02499],"object_pos_start":[0.52441,-0.08967,0.02499],"object_to_goal_dist_end":0.06508,"object_to_goal_dist_start":0.06508,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"retract_after_push","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2180.0,"raw_peak_contact_force":0.24525,"subtask_id":"push_goal","tcp_end":[0.383,-0.40008,0.12957],"tcp_start":[0.38552,-0.40237,0.04189],"tcp_to_object_dist_end":0.35677,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```