## Search State

- **Seed**: 7
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | approach → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | position_control | admittance_control | position_control | pose_tolerance | time_limit | pose_tolerance | 3 | 0.5431 | 0.79 | ❌ rejected |
| 11 | approach → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | position_control | admittance_control | position_control | pose_tolerance | time_limit | pose_tolerance | 3 | 0.5556 | 0.81 | ❌ rejected |
| 10 | approach → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | position_control | admittance_control | position_control | pose_tolerance | time_limit | pose_tolerance | 3 | 0.5609 | 0.81 | ✅ accepted |
| 9 | approach → descend → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | admittance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 6 | -0.0178 | 0.14 | ❌ rejected |
| 8 | approach → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | position_control | admittance_control | position_control | pose_tolerance | time_limit | pose_tolerance | 3 | 0.5425 | 0.79 | ✅ accepted |

**Proposal policy**: task_score is 0.79 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.809, which indicates the subtask decomposition is already effective.
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

## Current Skill (Q=0.543) — your mutation base

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
  subtask_id: reach_pre_contact
- id: push_to_goal_phase
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
      default: 3.0
      binds_to:
      - path: duration.max_time
        mode: replace
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
- **approach_behind** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.05, mode=add_to_offset, sign=negative}, tolerance=0.01
  - orientation: mode=none
  - parameter_bindings:
    - approach_offset: status=consumed; consumers=target.offset_along_axis.distance (replace)
- **push_to_goal_phase** (`push`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.05, mode=add_to_offset, sign=positive}, tolerance=0.01
  - orientation: mode=none
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_time: status=consumed; consumers=duration.max_time (replace)
- **retract_1** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.05], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.543
- **task_score** (E): 0.791
- **fitness_score**: 0.723  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.180

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_behind | 1.00 | 1.00 | 0.2709 |
| push_to_goal_phase | 1.00 | 1.00 | 0.1617 |
| retract_1 | 1.00 | 1.00 | 0.0410 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_behind | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.518, 0.071, 0.043) | (0.513, 0.027, 0.025)→(0.513, 0.027, 0.025) | 0.180→0.180 | 1.00 / 3.667 | 0.825 | 179.779 |
| push_to_goal_phase | push | 1.00 / time_limit | (0.518, 0.071, 0.043)→(0.498, -0.086, 0.028) | (0.513, 0.027, 0.025)→(0.514, -0.121, 0.027) | 0.180→0.040 | 1.00 / 3.000 | 14.641 | 31.343 |
| retract_1 | retract | 1.00 / step_budget | (0.498, -0.086, 0.028)→(0.494, -0.086, 0.069) | (0.514, -0.121, 0.027)→(0.512, -0.120, 0.025) | 0.040→0.038 | 1.00 / 4.000 | 0.245 | 10.101 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.944
- lateral_force_integral: None
- approach_alignment: 0.716
- goal_progress: 0.824
- terminal_score: 0.824
- phase_score: 0.671
- phase_breakdown.reach_pre_contact_score: 0.258
- phase_breakdown.push_to_goal_score: 0.795

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.732
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.824
- **Median Q (composite search score)**: 0.547
- **K-run variance**: 0.0001
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 10.0
- **Final σ (mean)**: 0.634


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.75862,"average_solve_count":116.0,"average_success_count":116.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.approach_offset":0.04319,"push_to_goal_phase.push_distance":0.01431,"push_to_goal_phase.push_time":3.36399},"optimized_scores":{"best_composite_score":0.54713,"best_fitness_score":0.72713,"best_task_score":0.78291},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":28.0,"contact_point_centroid":[0.52103,0.07321,0.04804],"force_p95":259.49502,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":264.15735,"mean_force":153.1763,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.51467,0.08172,0.04938]},{"body_a":"world","body_b":"push_box","contact_count":2130.0,"contact_point_centroid":[0.51524,0.04799,-2e-05],"force_p95":0.24533,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":237.30844,"mean_force":2.27682,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.5059,0.04055,0.17236]},{"body_a":"attachment","body_b":"push_box","contact_count":775.0,"contact_point_centroid":[0.51096,-0.00913,0.04093],"force_p95":20.28209,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":32.17779,"mean_force":6.80474,"phase_index":1.0,"phase_name":"push_to_goal_phase","phase_type":"push","tcp_position_centroid":[0.50689,0.00274,0.03278]},{"body_a":"world","body_b":"push_box","contact_count":1618.0,"contact_point_centroid":[0.51093,-0.03244,-0.0001],"force_p95":9.94161,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":18.21256,"mean_force":3.63887,"phase_index":1.0,"phase_name":"push_to_goal_phase","phase_type":"push","tcp_position_centroid":[0.50783,0.01498,0.03378]},{"body_a":"attachment","body_b":"push_box","contact_count":191.0,"contact_point_centroid":[0.50569,-0.08665,0.05079],"force_p95":0.6212,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":5.84932,"mean_force":0.5211,"phase_index":2.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49788,-0.07484,0.03896]},{"body_a":"world","body_b":"push_box","contact_count":1256.0,"contact_point_centroid":[0.51558,-0.11964,-1e-05],"force_p95":0.4774,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.43694,"mean_force":0.32666,"phase_index":2.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49753,-0.07475,0.05085]}],"total_contact_groups":6},"final_pose_error":0.01,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.51408,-0.10934,0.02499],"final_tcp_position":[0.49739,-0.07471,0.06764],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.51501,0.04767,0.025]},"peak_contact_force":264.15735,"phases":[{"contact_detected":true,"contact_event_count":3.0,"n_steps":541.0,"n_steps_budget":1000.0,"object_pos_end":[0.51479,0.04631,0.02478],"object_pos_start":[0.51501,0.04767,0.025],"object_to_goal_dist_end":0.19687,"object_to_goal_dist_start":0.19823,"object_z_max":0.025,"peak_contact_force":1.77337,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2158.0,"raw_peak_contact_force":264.15735,"subtask_id":"reach_pre_contact","tcp_end":[0.51674,0.08496,0.04376],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.04311,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51526,-0.11025,0.02626],"object_pos_start":[0.51479,0.04631,0.02478],"object_to_goal_dist_end":0.0426,"object_to_goal_dist_start":0.19687,"object_z_max":0.02655,"peak_contact_force":20.64597,"phase_name":"push_to_goal_phase","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2393.0,"raw_peak_contact_force":32.17779,"subtask_id":"push_to_goal","tcp_end":[0.50129,-0.0751,0.02684],"tcp_start":[0.51674,0.08496,0.04376],"tcp_to_object_dist_end":0.03782,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":449.0,"n_steps_budget":600.0,"object_pos_end":[0.51408,-0.10934,0.02499],"object_pos_start":[0.51526,-0.11025,0.02626],"object_to_goal_dist_end":0.04303,"object_to_goal_dist_start":0.0426,"object_z_max":0.02632,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1447.0,"raw_peak_contact_force":5.84932,"tcp_end":[0.49739,-0.07471,0.06764],"tcp_start":[0.50129,-0.0751,0.02684],"tcp_to_object_dist_end":0.05742,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.75652,"average_solve_count":115.0,"average_success_count":115.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.approach_offset":0.04184,"push_to_goal_phase.push_distance":0.01148,"push_to_goal_phase.push_time":3.9158},"optimized_scores":{"best_composite_score":0.52998,"best_fitness_score":0.70998,"best_task_score":0.76599},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":47.0,"contact_point_centroid":[0.48553,0.08548,0.04688],"force_p95":272.04324,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":274.93496,"mean_force":200.67687,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.47756,0.09185,0.04906]},{"body_a":"world","body_b":"push_box","contact_count":2141.0,"contact_point_centroid":[0.47932,0.05948,-4e-05],"force_p95":0.24534,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":226.99934,"mean_force":4.66603,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.48655,0.04495,0.17222]},{"body_a":"attachment","body_b":"push_box","contact_count":782.0,"contact_point_centroid":[0.48944,0.00376,0.04526],"force_p95":25.37201,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":37.25516,"mean_force":7.65282,"phase_index":1.0,"phase_name":"push_to_goal_phase","phase_type":"push","tcp_position_centroid":[0.48286,0.01555,0.03359]},{"body_a":"world","body_b":"push_box","contact_count":1472.0,"contact_point_centroid":[0.48739,-0.02745,-0.00011],"force_p95":13.21125,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":22.41337,"mean_force":4.48414,"phase_index":1.0,"phase_name":"push_to_goal_phase","phase_type":"push","tcp_position_centroid":[0.48223,0.02495,0.03444]},{"body_a":"world","body_b":"push_box","contact_count":1644.0,"contact_point_centroid":[0.49891,-0.10122,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.18261,"mean_force":0.25263,"phase_index":2.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48569,-0.06332,0.0485]},{"body_a":"attachment","body_b":"push_box","contact_count":12.0,"contact_point_centroid":[0.49912,-0.07579,0.04818],"force_p95":1.39127,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.46447,"mean_force":0.73029,"phase_index":2.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48825,-0.06381,0.02842]}],"total_contact_groups":6},"final_pose_error":0.01,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.49892,-0.10099,0.02499],"final_tcp_position":[0.4855,-0.06325,0.06836],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47924,0.05847,0.025]},"peak_contact_force":274.93496,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":557.0,"n_steps_budget":1000.0,"object_pos_end":[0.48102,0.05937,0.02429],"object_pos_start":[0.47924,0.05847,0.025],"object_to_goal_dist_end":0.21023,"object_to_goal_dist_start":0.2095,"object_z_max":0.02523,"peak_contact_force":0.45748,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2188.0,"raw_peak_contact_force":274.93496,"subtask_id":"reach_pre_contact","tcp_end":[0.48001,0.09668,0.04386],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.04215,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49982,-0.10007,0.02538],"object_pos_start":[0.48102,0.05937,0.02429],"object_to_goal_dist_end":0.04993,"object_to_goal_dist_start":0.21023,"object_z_max":0.02585,"peak_contact_force":1.37652,"phase_name":"push_to_goal_phase","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2254.0,"raw_peak_contact_force":37.25516,"subtask_id":"push_to_goal","tcp_end":[0.48934,-0.06357,0.02758],"tcp_start":[0.48001,0.09668,0.04386],"tcp_to_object_dist_end":0.03804,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":423.0,"n_steps_budget":600.0,"object_pos_end":[0.49892,-0.10099,0.02499],"object_pos_start":[0.49982,-0.10007,0.02538],"object_to_goal_dist_end":0.04903,"object_to_goal_dist_start":0.04993,"object_z_max":0.02559,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1656.0,"raw_peak_contact_force":2.18261,"tcp_end":[0.4855,-0.06325,0.06836],"tcp_start":[0.48934,-0.06357,0.02758],"tcp_to_object_dist_end":0.05903,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.75652,"average_solve_count":115.0,"average_success_count":115.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.approach_offset":0.06519,"push_to_goal_phase.push_distance":0.12343,"push_to_goal_phase.push_time":1.63699},"optimized_scores":{"best_composite_score":0.55234,"best_fitness_score":0.73234,"best_task_score":0.82447},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":663.0,"contact_point_centroid":[0.52968,-0.06519,0.0418],"force_p95":20.39685,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":24.59736,"mean_force":6.4487,"phase_index":1.0,"phase_name":"push_to_goal_phase","phase_type":"push","tcp_position_centroid":[0.52437,-0.05346,0.03209]},{"body_a":"push_box","body_b":"link7","contact_count":41.0,"contact_point_centroid":[0.54745,-0.12147,0.05477],"force_p95":22.61123,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":23.57299,"mean_force":16.79134,"phase_index":1.0,"phase_name":"push_to_goal_phase","phase_type":"push","tcp_position_centroid":[0.50553,-0.11122,0.02919]},{"body_a":"push_box","body_b":"link7","contact_count":11.0,"contact_point_centroid":[0.54381,-0.13233,0.0546],"force_p95":20.48883,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":22.27172,"mean_force":6.33347,"phase_index":2.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50244,-0.11984,0.02887]},{"body_a":"world","body_b":"push_box","contact_count":1962.0,"contact_point_centroid":[0.53733,-0.07529,-7e-05],"force_p95":9.96597,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":22.11905,"mean_force":2.84042,"phase_index":1.0,"phase_name":"push_to_goal_phase","phase_type":"push","tcp_position_centroid":[0.53319,-0.02751,0.03376]},{"body_a":"world","body_b":"push_box","contact_count":1434.0,"contact_point_centroid":[0.52687,-0.15436,-1e-05],"force_p95":0.47804,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":19.65239,"mean_force":0.35117,"phase_index":2.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49904,-0.11897,0.05267]},{"body_a":"attachment","body_b":"push_box","contact_count":138.0,"contact_point_centroid":[0.51442,-0.12893,0.05339],"force_p95":0.72765,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":8.17844,"mean_force":0.69182,"phase_index":2.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49968,-0.11916,0.03773]},{"body_a":"world","body_b":"push_box","contact_count":2104.0,"contact_point_centroid":[0.54443,-0.02558,-1e-05],"force_p95":0.24529,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.52729,0.01589,0.17255]}],"total_contact_groups":7},"final_pose_error":0.00994,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.52314,-0.14847,0.02499],"final_tcp_position":[0.49895,-0.11894,0.06965],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.54443,-0.02558,0.025]},"peak_contact_force":24.59736,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":526.0,"n_steps_budget":1000.0,"object_pos_end":[0.54443,-0.02558,0.02499],"object_pos_start":[0.54443,-0.02558,0.025],"object_to_goal_dist_end":0.13211,"object_to_goal_dist_start":0.13211,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2104.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_pre_contact","tcp_end":[0.55705,0.03251,0.04234],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.06193,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52687,-0.15135,0.0282],"object_pos_start":[0.54443,-0.02558,0.02499],"object_to_goal_dist_end":0.02709,"object_to_goal_dist_start":0.13211,"object_z_max":0.02843,"peak_contact_force":21.90133,"phase_name":"push_to_goal_phase","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2666.0,"raw_peak_contact_force":24.59736,"subtask_id":"push_to_goal","tcp_end":[0.50283,-0.11962,0.02879],"tcp_start":[0.55705,0.03251,0.04234],"tcp_to_object_dist_end":0.03982,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":463.0,"n_steps_budget":600.0,"object_pos_end":[0.52314,-0.14847,0.02499],"object_pos_start":[0.52687,-0.15135,0.0282],"object_to_goal_dist_end":0.02319,"object_to_goal_dist_start":0.02709,"object_z_max":0.02842,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1583.0,"raw_peak_contact_force":22.27172,"tcp_end":[0.49895,-0.11894,0.06965],"tcp_start":[0.50283,-0.11962,0.02879],"tcp_to_object_dist_end":0.05876,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```