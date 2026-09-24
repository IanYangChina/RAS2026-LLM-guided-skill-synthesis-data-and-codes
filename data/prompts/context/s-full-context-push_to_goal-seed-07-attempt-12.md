## Search State

- **Seed**: 7
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | time_limit | 8 | 0.1526 | 0.68 | ❌ rejected |
| 11 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | time_limit | 8 | 0.2666 | 0.82 | ✅ accepted |
| 10 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | time_limit | 5 | 0.2466 | 0.61 | ✅ accepted |
| 9 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | time_limit | 5 | 0.2459 | 0.61 | ✅ accepted |
| 8 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | admittance_control | pose_tolerance | pose_tolerance | pose_tolerance | 5 | -0.2552 | 0.00 | ❌ rejected |

**Proposal policy**: task_score is 0.68 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.819, which indicates the subtask decomposition is already effective.
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

## Current Skill (Q=0.153) — your mutation base

```yaml
skill: push_to_goal
dsl_version: 2
subtasks:
- id: approach_sub
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.1
  weight: 0.3
- id: push_sub
  target_entity: object
  metric: goal_progress
  weight: 0.7
phases:
- id: approach_behind
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.05
    - 0.1
    tolerance: 0.03
    orientation:
      mode: keep_current
  parameters:
    approach_height_z:
      type: scalar
      range:
      - 0.05
      - 0.15
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: replace
    approach_speed:
      type: scalar
      range:
      - 0.05
      - 0.1
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
    behind_offset_y:
      type: scalar
      range:
      - 0.03
      - 0.08
      default: 0.05
      binds_to:
      - path: target.offset.y
        mode: replace
  subtask_id: approach_sub
- id: descend_to_push
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.05
    - 0.0
    tolerance: 0.015
    orientation:
      mode: keep_current
  parameters:
    behind_offset_y:
      type: scalar
      range:
      - 0.03
      - 0.08
      default: 0.05
      binds_to:
      - path: target.offset.y
        mode: replace
    descend_speed:
      type: scalar
      range:
      - 0.05
      - 0.1
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: approach_sub
- id: push_to_goal
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: time_limit
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.35
      axis: task_goal_direction
      mode: replace_offset_projection
      sign: positive
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    push_speed:
      type: scalar
      range:
      - 0.05
      - 0.25
      default: 0.15
      binds_to:
      - path: generator.speed
        mode: replace
    push_stroke:
      type: scalar
      range:
      - 0.15
      - 0.45
      default: 0.35
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_time:
      type: scalar
      range:
      - 3.0
      - 8.0
      default: 5.0
      binds_to:
      - path: duration.max_time
        mode: replace
  subtask_id: push_sub

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_behind** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.05, 0.1], tolerance=0.03
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_height_z: status=consumed; consumers=target.offset.z (replace)
    - approach_speed: status=consumed; consumers=generator.speed (replace)
    - behind_offset_y: status=consumed; consumers=target.offset.y (replace)
- **descend_to_push** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.05, 0.0], tolerance=0.015
  - orientation: mode=keep_current
  - parameter_bindings:
    - behind_offset_y: status=consumed; consumers=target.offset.y (replace)
    - descend_speed: status=consumed; consumers=generator.speed (replace)
- **push_to_goal** (`push`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.35, mode=replace_offset_projection, sign=positive}, tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_speed: status=consumed; consumers=generator.speed (replace)
    - push_stroke: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_time: status=consumed; consumers=duration.max_time (replace)

## Design Metrics

- **Composite score**: 0.153
- **task_score** (E): 0.680
- **fitness_score**: 0.583  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.430

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_behind | 1.00 | 1.00 | 0.1791 |
| descend_to_push | 1.00 | 1.00 | 0.1000 |
| push_to_goal | 1.00 | 1.00 | 0.2631 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_behind | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.508, 0.062, 0.138) | (0.513, 0.027, 0.025)→(0.513, 0.027, 0.025) | 0.180→0.180 | 1.00 / 4.000 | 0.245 | 0.245 |
| descend_to_push | descend | 1.00 / step_budget | (0.508, 0.062, 0.138)→(0.510, 0.067, 0.039) | (0.513, 0.027, 0.025)→(0.513, 0.026, 0.025) | 0.180→0.179 | 1.00 / 3.000 | 0.357 | 85.219 |
| push_to_goal | push | 1.00 / time_limit | (0.510, 0.067, 0.039)→(0.485, -0.190, 0.034) | (0.513, 0.026, 0.025)→(0.531, -0.112, 0.026) | 0.179→0.054 | 1.00 / 3.333 | 0.378 | 53.767 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 1.000
- lateral_force_integral: None
- approach_alignment: 0.779
- goal_progress: 0.855
- terminal_score: 0.855
- phase_score: 0.643
- phase_breakdown.approach_sub_score: 0.149
- phase_breakdown.push_sub_score: 0.855

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.728
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.855
- **Median Q (composite search score)**: 0.111
- **K-run variance**: 0.0112
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.331


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.78462,"average_solve_count":130.0,"average_success_count":130.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.approach_height_z":0.10605,"approach_behind.approach_speed":0.07335,"approach_behind.behind_offset_y":0.04059,"descend_to_push.behind_offset_y":0.05021,"descend_to_push.descend_speed":0.05908,"push_to_goal.push_speed":0.2336,"push_to_goal.push_stroke":0.32278,"push_to_goal.push_time":6.61558},"optimized_scores":{"best_composite_score":0.11108,"best_fitness_score":0.54108,"best_task_score":0.62893},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":323.0,"contact_point_centroid":[0.50954,-0.0173,0.04918],"force_p95":24.83122,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":44.41492,"mean_force":6.42447,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.49929,-0.00983,0.03403]},{"body_a":"world","body_b":"push_box","contact_count":1853.0,"contact_point_centroid":[0.52861,-0.05481,-3e-05],"force_p95":9.86477,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":25.49161,"mean_force":1.50088,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.49333,-0.08934,0.03397]},{"body_a":"world","body_b":"push_box","contact_count":956.0,"contact_point_centroid":[0.51501,0.04767,-0.0],"force_p95":0.24532,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.50467,0.03455,0.22996]},{"body_a":"world","body_b":"push_box","contact_count":1208.0,"contact_point_centroid":[0.51501,0.04767,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"descend_to_push","phase_type":"descend","tcp_position_centroid":[0.50948,0.08272,0.09661]}],"total_contact_groups":4},"final_pose_error":0.01686,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.52353,-0.08031,0.02499],"final_tcp_position":[0.48371,-0.21243,0.03335],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.51501,0.04767,0.025]},"peak_contact_force":44.41492,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":239.0,"n_steps_budget":1000.0,"object_pos_end":[0.51501,0.04767,0.02499],"object_pos_start":[0.51501,0.04767,0.025],"object_to_goal_dist_end":0.19823,"object_to_goal_dist_start":0.19823,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":956.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach_sub","tcp_end":[0.51043,0.07255,0.15551],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.13295,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":302.0,"n_steps_budget":1000.0,"object_pos_end":[0.51501,0.04767,0.02499],"object_pos_start":[0.51501,0.04767,0.02499],"object_to_goal_dist_end":0.19823,"object_to_goal_dist_start":0.19823,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"descend_to_push","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1208.0,"raw_peak_contact_force":0.24525,"subtask_id":"approach_sub","tcp_end":[0.51069,0.09359,0.03853],"tcp_start":[0.51043,0.07255,0.15551],"tcp_to_object_dist_end":0.04807,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":841.0,"n_steps_budget":870.0,"object_pos_end":[0.52353,-0.08031,0.02499],"object_pos_start":[0.51501,0.04767,0.02499],"object_to_goal_dist_end":0.07356,"object_to_goal_dist_start":0.19823,"object_z_max":0.0299,"peak_contact_force":0.24525,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2176.0,"raw_peak_contact_force":44.41492,"subtask_id":"push_sub","tcp_end":[0.48371,-0.21243,0.03335],"tcp_start":[0.51069,0.09359,0.03853],"tcp_to_object_dist_end":0.13824,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.15652,"average_solve_count":115.0,"average_success_count":115.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.approach_height_z":0.08178,"approach_behind.approach_speed":0.08378,"approach_behind.behind_offset_y":0.05928,"descend_to_push.behind_offset_y":0.04226,"descend_to_push.descend_speed":0.07444,"push_to_goal.push_speed":0.21336,"push_to_goal.push_stroke":0.29581,"push_to_goal.push_time":7.41826},"optimized_scores":{"best_composite_score":0.29774,"best_fitness_score":0.72774,"best_task_score":0.85477},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":1058.0,"contact_point_centroid":[0.5159,-0.058,-9e-05],"force_p95":17.39832,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":68.16049,"mean_force":3.90806,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.48544,-0.02716,0.0353]},{"body_a":"attachment","body_b":"push_box","contact_count":494.0,"contact_point_centroid":[0.49511,-0.04778,0.04764],"force_p95":30.74486,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":68.03152,"mean_force":7.12321,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.48644,-0.03926,0.03504]},{"body_a":"world","body_b":"push_box","contact_count":1152.0,"contact_point_centroid":[0.47924,0.05847,-1e-05],"force_p95":0.24532,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.4901,0.04831,0.21678]},{"body_a":"world","body_b":"push_box","contact_count":896.0,"contact_point_centroid":[0.47924,0.05847,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"descend_to_push","phase_type":"descend","tcp_position_centroid":[0.47705,0.10003,0.08481]}],"total_contact_groups":4},"final_pose_error":0.01616,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.5301,-0.14754,0.02871],"final_tcp_position":[0.50013,-0.18002,0.0342],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47924,0.05847,0.025]},"peak_contact_force":68.16049,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":288.0,"n_steps_budget":1000.0,"object_pos_end":[0.47924,0.05847,0.02499],"object_pos_start":[0.47924,0.05847,0.025],"object_to_goal_dist_end":0.2095,"object_to_goal_dist_start":0.2095,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1152.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach_sub","tcp_end":[0.48003,0.10013,0.13023],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.11319,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":224.0,"n_steps_budget":900.0,"object_pos_end":[0.47924,0.05847,0.02499],"object_pos_start":[0.47924,0.05847,0.02499],"object_to_goal_dist_end":0.2095,"object_to_goal_dist_start":0.2095,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"descend_to_push","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":896.0,"raw_peak_contact_force":0.24525,"subtask_id":"approach_sub","tcp_end":[0.47596,0.09992,0.03939],"tcp_start":[0.48003,0.10013,0.13023],"tcp_to_object_dist_end":0.044,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":841.0,"n_steps_budget":870.0,"object_pos_end":[0.5301,-0.14754,0.02871],"object_pos_start":[0.47924,0.05847,0.02499],"object_to_goal_dist_end":0.03043,"object_to_goal_dist_start":0.2095,"object_z_max":0.03007,"peak_contact_force":0.6444,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1552.0,"raw_peak_contact_force":68.16049,"subtask_id":"push_sub","tcp_end":[0.50013,-0.18002,0.0342],"tcp_start":[0.47596,0.09992,0.03939],"tcp_to_object_dist_end":0.04454,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.00952,"average_solve_count":105.0,"average_success_count":105.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.approach_height_z":0.07557,"approach_behind.approach_speed":0.07795,"approach_behind.behind_offset_y":0.04328,"descend_to_push.behind_offset_y":0.03039,"descend_to_push.descend_speed":0.0711,"push_to_goal.push_speed":0.22761,"push_to_goal.push_stroke":0.21472,"push_to_goal.push_time":6.86172},"optimized_scores":{"best_composite_score":0.04905,"best_fitness_score":0.47905,"best_task_score":0.55544},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":40.0,"contact_point_centroid":[0.54775,-0.00065,0.04763],"force_p95":248.84288,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":255.16589,"mean_force":162.13273,"phase_index":1.0,"phase_name":"descend_to_push","phase_type":"descend","tcp_position_centroid":[0.54093,0.00815,0.04763]},{"body_a":"world","body_b":"push_box","contact_count":886.0,"contact_point_centroid":[0.54514,-0.02521,-7e-05],"force_p95":46.19498,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":200.92723,"mean_force":7.64372,"phase_index":1.0,"phase_name":"descend_to_push","phase_type":"descend","tcp_position_centroid":[0.53614,0.01082,0.0828]},{"body_a":"attachment","body_b":"push_box","contact_count":180.0,"contact_point_centroid":[0.52912,-0.05134,0.04668],"force_p95":36.65611,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":48.72547,"mean_force":8.82594,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.52169,-0.04132,0.03451]},{"body_a":"world","body_b":"push_box","contact_count":1402.0,"contact_point_centroid":[0.5443,-0.09589,-7e-05],"force_p95":9.21494,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":30.6331,"mean_force":1.4651,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.49905,-0.10249,0.03386]},{"body_a":"world","body_b":"push_box","contact_count":1024.0,"contact_point_centroid":[0.54443,-0.02558,-1e-05],"force_p95":0.24532,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.51638,0.00698,0.21707]}],"total_contact_groups":5},"final_pose_error":0.01514,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.5408,-0.10775,0.02499],"final_tcp_position":[0.4709,-0.17894,0.03326],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.54443,-0.02558,0.025]},"peak_contact_force":255.16589,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":256.0,"n_steps_budget":1000.0,"object_pos_end":[0.54443,-0.02558,0.02499],"object_pos_start":[0.54443,-0.02558,0.025],"object_to_goal_dist_end":0.13211,"object_to_goal_dist_start":0.13211,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1024.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach_sub","tcp_end":[0.53485,0.01462,0.12873],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.11167,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":238.0,"n_steps_budget":930.0,"object_pos_end":[0.54424,-0.02909,0.02579],"object_pos_start":[0.54443,-0.02558,0.02499],"object_to_goal_dist_end":0.12875,"object_to_goal_dist_start":0.13211,"object_z_max":0.02578,"peak_contact_force":0.58065,"phase_name":"descend_to_push","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":926.0,"raw_peak_contact_force":255.16589,"subtask_id":"approach_sub","tcp_end":[0.54341,0.00835,0.03926],"tcp_start":[0.53485,0.01462,0.12873],"tcp_to_object_dist_end":0.0398,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":571.0,"n_steps_budget":600.0,"object_pos_end":[0.5408,-0.10775,0.02499],"object_pos_start":[0.54424,-0.02909,0.02579],"object_to_goal_dist_end":0.05873,"object_to_goal_dist_start":0.12875,"object_z_max":0.02824,"peak_contact_force":0.24525,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1582.0,"raw_peak_contact_force":48.72547,"subtask_id":"push_sub","tcp_end":[0.4709,-0.17894,0.03326],"tcp_start":[0.54341,0.00835,0.03926],"tcp_to_object_dist_end":0.10011,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
```