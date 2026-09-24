## Search State

- **Seed**: 7
- **Iteration**: 5 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 4 | approach → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | position_control | admittance_control | position_control | pose_tolerance | time_limit | pose_tolerance | 5 | 0.2267 | 0.55 | ✅ accepted |
| 3 | approach → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | position_control | admittance_control | position_control | pose_tolerance | time_limit | pose_tolerance | 5 | -0.2092 | 0.00 | ✅ accepted |
| 2 | descend → insert → grasp → approach → align | linear_cartesian | impedance_motion | — | linear_cartesian | linear_cartesian | admittance_control | admittance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 5 | -0.3400 | 0.00 | ❌ rejected |
| 1 | descend → insert → grasp → approach → align | linear_cartesian | impedance_motion | — | linear_cartesian | linear_cartesian | admittance_control | admittance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 5 | -0.3400 | 0.00 | ❌ rejected |
| 0 | descend → insert → grasp → approach → align | linear_cartesian | impedance_motion | — | linear_cartesian | linear_cartesian | admittance_control | admittance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 5 | -0.3400 | 0.00 | ✅ accepted |

**Proposal policy**: task_score is 0.55 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen object start: [0.5, -0.15, 0.025]
- Frozen task target: [0.5, 0.0, 0.3]
- Goal object position: (0.5, 0.0, 0.3)
- Object initial pose: (0.5, -0.15, 0.025)
- Goal tolerance: 0.02 m
- Expressivity sigma: 1.0 m
- Expressivity threshold: 0.8
- Force limit: 25.0 N
- Robot initial TCP position: (0.51501145599256, 0.047665656116349056, 0.025)
- Phase navigation guidance: the task `phase_target_map` may provide internal predefined TCP waypoint aliases / semantic phase ids. These names are not DSL phase types and are intentionally not enumerated here to avoid confusing ids with types. Phase `id` may be semantic, but phase `type` must be exactly one of the DSL enum values listed in the prompt.
- Primary evaluation target: **object displacement ratio toward goal_object_position**

## Scene Entities

robot:
  model: panda_pusher
  tcp_site: attachment_site
  gripper: null
  tcp_initial_world: [0.51501145599256, 0.047665656116349056, 0.025]
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
  frozen_task_target: [0.5, 0.0, 0.3]
  frozen_object_starts: {'push_box': [0.5, -0.15, 0.025]}
  frozen_targets: {'task_goal': [0.5, 0.0, 0.3]}
  push_direction: [-0.015, -0.1977, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 25
  force_scale_n: 5
  realized_scene_sha256: c8d09cd43835becf8e5eb4413394fad8627e4bf404e9e7726e9f380b60e09752

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
| `object` | offset from object initial position (0.5, -0.15, 0.025) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5, 0.0, 0.3) | final destination targets |
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

## Current Skill (Q=0.227) — your mutation base

```yaml
skill: push_to_goal
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: reach_pre_contact
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.05
  weight: 0.3
- id: push_to_goal
  target_entity: object
  metric: goal_progress
phases:
- id: arc_approach
  type: approach
  generator: arc_cartesian
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
      distance: 0.05
      axis: task_goal_direction
      mode: add_to_offset
      sign: negative
    tolerance: 0.01
    orientation:
      mode: none
  parameters:
    approach_offset:
      type: scalar
      range:
      - 0.03
      - 0.08
      default: 0.05
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    arc_height:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.arc_height
        mode: replace
  subtask_id: reach_pre_contact
- id: push_task
  type: push
  generator: linear_cartesian
  control: admittance_control
  termination: time_limit
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.05
      axis: task_goal_direction
      mode: add_to_offset
      sign: positive
    tolerance: 0.01
    orientation:
      mode: none
  parameters:
    force_limit:
      type: scalar
      range:
      - 5.0
      - 25.0
      default: 15.0
      binds_to:
      - path: guards.force_guard.threshold
        mode: replace
    push_distance:
      type: scalar
      range:
      - 0.01
      - 0.15
      default: 0.05
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_time:
      type: scalar
      range:
      - 1.0
      - 5.0
      default: 2.0
      binds_to:
      - path: duration.max_time
        mode: replace
  guards:
  - id: force_guard
    when: during_phase
    predicate: force_below
    threshold: 15.0
    on_failure: abort
  subtask_id: push_to_goal
- id: retract_1
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
    tolerance: 0.01
    orientation:
      mode: keep_current

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **arc_approach** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.05, mode=add_to_offset, sign=negative}, tolerance=0.01
  - orientation: mode=none
  - parameter_bindings:
    - approach_offset: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - arc_height: status=consumed; consumers=generator.arc_height (replace)
- **push_task** (`push`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.05, mode=add_to_offset, sign=positive}, tolerance=0.01
  - orientation: mode=none
  - parameter_bindings:
    - force_limit: status=consumed; consumers=guards.force_guard.threshold (replace)
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_time: status=consumed; consumers=duration.max_time (replace)
  - guards:
    - id=force_guard, when=during_phase, predicate=force_below, on_failure=abort, threshold=15.0
- **retract_1** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.05], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.227
- **task_score** (E): 0.549
- **fitness_score**: 0.507  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.280

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| arc_approach | 1.00 | 1.00 | 0.2797 |
| push_task | 0.33 | 1.00 | 0.1429 |
| retract_1 | 1.00 | 1.00 | 0.0410 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| arc_approach | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.517, 0.080, 0.037) | (0.513, 0.027, 0.025)→(0.512, 0.024, 0.025) | 0.180→0.177 | 1.00 / 3.333 | 0.469 | 85.903 |
| push_task | push | 0.33 / guard_failure | (0.517, 0.080, 0.037)→(0.502, -0.059, 0.027) | (0.512, 0.024, 0.025)→(0.500, -0.075, 0.027) | 0.177→0.085 | 1.00 / 3.667 | 15.975 | 23.888 |
| retract_1 | retract | 1.00 / step_budget | (0.491, -0.071, 0.025)→(0.487, -0.071, 0.066) | (0.443, -0.057, 0.025)→(0.443, -0.057, 0.025) | 0.109→0.109 | 1.00 / 4.000 | 0.245 | 0.245 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.781
- lateral_force_integral: None
- approach_alignment: 0.639
- goal_progress: 0.735
- terminal_score: 0.735
- phase_score: 0.613
- phase_breakdown.reach_pre_contact_score: 0.207
- phase_breakdown.push_to_goal_score: 0.735

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.662
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.735
- **Median Q (composite search score)**: 0.170
- **K-run variance**: 0.0124
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.327


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
{"anchors":[{"name":"object","value":[0.5,-0.15,0.025]},{"name":"goal","value":[0.51501,0.04767,0.025]}],"axes":[{"name":"push_direction","value":[-0.01501,-0.19767,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.51501,0.04767,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.93182,"average_solve_count":88.0,"average_success_count":88.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"arc_approach.approach_offset":0.05798,"arc_approach.arc_height":0.0538,"push_task.force_limit":24.65514,"push_task.push_distance":0.08004,"push_task.push_time":2.24528},"optimized_scores":{"best_composite_score":0.12762,"best_fitness_score":0.40762,"best_task_score":0.43369},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":41.0,"contact_point_centroid":[0.54262,-0.01672,0.05925],"force_p95":19.84951,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":24.85654,"mean_force":13.44279,"phase_index":1.0,"phase_name":"push_task","phase_type":"push","tcp_position_centroid":[0.50259,-0.01217,0.03353]},{"body_a":"world","body_b":"push_box","contact_count":1503.0,"contact_point_centroid":[0.52238,0.01212,-4e-05],"force_p95":10.56321,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":23.90716,"mean_force":3.01788,"phase_index":1.0,"phase_name":"push_task","phase_type":"push","tcp_position_centroid":[0.50725,0.06322,0.03832]},{"body_a":"attachment","body_b":"push_box","contact_count":495.0,"contact_point_centroid":[0.51449,0.02262,0.04788],"force_p95":19.51237,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":23.88758,"mean_force":7.02832,"phase_index":1.0,"phase_name":"push_task","phase_type":"push","tcp_position_centroid":[0.50515,0.0336,0.03615]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.51501,0.04767,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"arc_approach","phase_type":"approach","tcp_position_centroid":[0.50478,0.08002,0.18865]}],"total_contact_groups":4},"final_pose_error":0.21514,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.52885,-0.04167,0.03097],"final_tcp_position":[0.5027,-0.01502,0.03363],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.51501,0.04767,0.025]},"peak_contact_force":24.85654,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51501,0.04767,0.02499],"object_pos_start":[0.51501,0.04767,0.025],"object_to_goal_dist_end":0.19823,"object_to_goal_dist_start":0.19823,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"arc_approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_pre_contact","tcp_end":[0.51364,0.11149,0.04569],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.06711,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":786.0,"n_steps_budget":1000.0,"object_pos_end":[0.52885,-0.04167,0.03097],"object_pos_start":[0.51501,0.04767,0.02499],"object_to_goal_dist_end":0.11226,"object_to_goal_dist_start":0.19823,"object_z_max":0.03095,"peak_contact_force":24.85654,"phase_name":"push_task","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2039.0,"raw_peak_contact_force":24.85654,"subtask_id":"push_to_goal","tcp_end":[0.5027,-0.01502,0.03363],"tcp_start":[0.51364,0.11149,0.04569],"tcp_to_object_dist_end":0.03744,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `4d55d9375783bea830660bf0a13dfc76a97a0d4f5645e7ebcc1ef7143776d0b7`; realized-scene SHA-256: `f3b8ea82cefd9504be10e2d47c49094a836a703404c06bdee3b01a27a59bf7be`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5,-0.15,0.025]},{"name":"goal","value":[0.47924,0.05847,0.025]}],"axes":[{"name":"push_direction","value":[0.02076,-0.20847,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.47924,0.05847,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.75862,"average_solve_count":116.0,"average_success_count":116.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"arc_approach.approach_offset":0.03098,"arc_approach.arc_height":0.02152,"push_task.force_limit":24.9987,"push_task.push_distance":0.11068,"push_task.push_time":3.81859},"optimized_scores":{"best_composite_score":0.17022,"best_fitness_score":0.45022,"best_task_score":0.47874},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":95.0,"contact_point_centroid":[0.48853,0.08442,0.04658],"force_p95":254.54037,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":257.21782,"mean_force":188.51749,"phase_index":0.0,"phase_name":"arc_approach","phase_type":"approach","tcp_position_centroid":[0.47969,0.08972,0.0494]},{"body_a":"world","body_b":"push_box","contact_count":3686.0,"contact_point_centroid":[0.47978,0.05887,-5e-05],"force_p95":21.55311,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":216.78558,"mean_force":5.14043,"phase_index":0.0,"phase_name":"arc_approach","phase_type":"approach","tcp_position_centroid":[0.48673,0.05572,0.17085]},{"body_a":"attachment","body_b":"push_box","contact_count":617.0,"contact_point_centroid":[0.47815,0.01106,0.02999],"force_p95":13.85243,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":23.98364,"mean_force":3.47745,"phase_index":1.0,"phase_name":"push_task","phase_type":"push","tcp_position_centroid":[0.48148,0.0219,0.02812]},{"body_a":"world","body_b":"push_box","contact_count":2193.0,"contact_point_centroid":[0.45617,-0.02131,-5e-05],"force_p95":5.0518,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.62365,"mean_force":1.29301,"phase_index":1.0,"phase_name":"push_task","phase_type":"push","tcp_position_centroid":[0.48342,0.00328,0.02769]},{"body_a":"world","body_b":"push_box","contact_count":1712.0,"contact_point_centroid":[0.44333,-0.05665,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24526,"mean_force":0.24525,"phase_index":2.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48695,-0.0711,0.04563]}],"total_contact_groups":5},"final_pose_error":0.00994,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.44333,-0.05665,0.02499],"final_tcp_position":[0.48668,-0.071,0.06606],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47924,0.05847,0.025]},"peak_contact_force":257.21782,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":966.0,"n_steps_budget":1000.0,"object_pos_end":[0.47571,0.04886,0.02492],"object_pos_start":[0.47924,0.05847,0.025],"object_to_goal_dist_end":0.20034,"object_to_goal_dist_start":0.2095,"object_z_max":0.0274,"peak_contact_force":0.91592,"phase_name":"arc_approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3781.0,"raw_peak_contact_force":257.21782,"subtask_id":"reach_pre_contact","tcp_end":[0.47852,0.09124,0.0344],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.04351,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.44333,-0.05665,0.02499],"object_pos_start":[0.47571,0.04886,0.02492],"object_to_goal_dist_end":0.10921,"object_to_goal_dist_start":0.20034,"object_z_max":0.02531,"peak_contact_force":0.24527,"phase_name":"push_task","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2810.0,"raw_peak_contact_force":23.98364,"subtask_id":"push_to_goal","tcp_end":[0.49054,-0.07136,0.02521],"tcp_start":[0.47852,0.09124,0.0344],"tcp_to_object_dist_end":0.04945,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":428.0,"n_steps_budget":600.0,"object_pos_end":[0.44333,-0.05665,0.02499],"object_pos_start":[0.44333,-0.05665,0.02499],"object_to_goal_dist_end":0.10921,"object_to_goal_dist_start":0.10921,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1712.0,"raw_peak_contact_force":0.24526,"tcp_end":[0.48668,-0.071,0.06606],"tcp_start":[0.49054,-0.07136,0.02521],"tcp_to_object_dist_end":0.06141,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `0a9238470f4497c7aa88b149b7cee960f9853513db10bf496723f5ea1d3a6043`; realized-scene SHA-256: `2cf7387f3e8baf02f18930263090d6f78777bdbc147b7fa30c178332e76b547b`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5,-0.15,0.025]},{"name":"goal","value":[0.54443,-0.02558,0.025]}],"axes":[{"name":"push_direction","value":[-0.04443,-0.12442,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.54443,-0.02558,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.93333,"average_solve_count":90.0,"average_success_count":90.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"arc_approach.approach_offset":0.06642,"arc_approach.arc_height":0.02025,"push_task.force_limit":22.7654,"push_task.push_distance":0.01896,"push_task.push_time":1.41387},"optimized_scores":{"best_composite_score":0.38212,"best_fitness_score":0.66212,"best_task_score":0.73519},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":1801.0,"contact_point_centroid":[0.53815,-0.06123,-3e-05],"force_p95":8.28502,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":22.82359,"mean_force":1.99738,"phase_index":1.0,"phase_name":"push_task","phase_type":"push","tcp_position_centroid":[0.53925,-0.01234,0.02489]},{"body_a":"push_box","body_b":"link7","contact_count":36.0,"contact_point_centroid":[0.54982,-0.10653,0.0515],"force_p95":21.04766,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":21.35012,"mean_force":12.11041,"phase_index":1.0,"phase_name":"push_task","phase_type":"push","tcp_position_centroid":[0.51478,-0.08819,0.02252]},{"body_a":"attachment","body_b":"push_box","contact_count":563.0,"contact_point_centroid":[0.53466,-0.05172,0.03379],"force_p95":16.8252,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":21.14374,"mean_force":4.76593,"phase_index":1.0,"phase_name":"push_task","phase_type":"push","tcp_position_centroid":[0.53005,-0.03986,0.02366]},{"body_a":"world","body_b":"push_box","contact_count":3760.0,"contact_point_centroid":[0.54443,-0.02558,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"arc_approach","phase_type":"approach","tcp_position_centroid":[0.52813,0.03077,0.16715]}],"total_contact_groups":4},"final_pose_error":0.07887,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.52644,-0.12714,0.02644],"final_tcp_position":[0.51402,-0.0917,0.02282],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.54443,-0.02558,0.025]},"peak_contact_force":22.82359,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":940.0,"n_steps_budget":1000.0,"object_pos_end":[0.54443,-0.02558,0.02499],"object_pos_start":[0.54443,-0.02558,0.025],"object_to_goal_dist_end":0.13211,"object_to_goal_dist_start":0.13211,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"arc_approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3760.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_pre_contact","tcp_end":[0.55939,0.03821,0.03152],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.06584,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":854.0,"n_steps_budget":1000.0,"object_pos_end":[0.52644,-0.12714,0.02644],"object_pos_start":[0.54443,-0.02558,0.02499],"object_to_goal_dist_end":0.03498,"object_to_goal_dist_start":0.13211,"object_z_max":0.02641,"peak_contact_force":22.82359,"phase_name":"push_task","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2400.0,"raw_peak_contact_force":22.82359,"subtask_id":"push_to_goal","tcp_end":[0.51402,-0.0917,0.02282],"tcp_start":[0.55939,0.03821,0.03152],"tcp_to_object_dist_end":0.03773,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
```