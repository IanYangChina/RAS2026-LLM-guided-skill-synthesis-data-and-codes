## Search State

- **Seed**: 7
- **Iteration**: 12 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 11 | approach → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | position_control | admittance_control | position_control | pose_tolerance | time_limit | pose_tolerance | 3 | 0.5556 | 0.81 | ❌ rejected |
| 10 | approach → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | position_control | admittance_control | position_control | pose_tolerance | time_limit | pose_tolerance | 3 | 0.5609 | 0.81 | ✅ accepted |
| 9 | approach → descend → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | admittance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 6 | -0.0178 | 0.14 | ❌ rejected |
| 8 | approach → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | position_control | admittance_control | position_control | pose_tolerance | time_limit | pose_tolerance | 3 | 0.5425 | 0.79 | ✅ accepted |
| 7 | approach → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | position_control | admittance_control | position_control | pose_tolerance | time_limit | pose_tolerance | 5 | 0.2171 | 0.54 | ❌ rejected |

**Proposal policy**: task_score is 0.81 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.556) — your mutation base

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

- **Composite score**: 0.556
- **task_score** (E): 0.809
- **fitness_score**: 0.736  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.180

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_behind | 1.00 | 1.00 | 0.2813 |
| push_to_goal_phase | 1.00 | 1.00 | 0.1617 |
| retract_1 | 1.00 | 1.00 | 0.0410 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_behind | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.516, 0.072, 0.033) | (0.513, 0.027, 0.025)→(0.513, 0.026, 0.025) | 0.180→0.179 | 1.00 / 4.000 | 0.282 | 141.916 |
| push_to_goal_phase | push | 1.00 / time_limit | (0.516, 0.072, 0.033)→(0.498, -0.086, 0.025) | (0.513, 0.026, 0.025)→(0.509, -0.121, 0.027) | 0.179→0.037 | 1.00 / 2.667 | 21.862 | 44.576 |
| retract_1 | retract | 1.00 / step_budget | (0.498, -0.086, 0.025)→(0.494, -0.085, 0.066) | (0.509, -0.121, 0.027)→(0.507, -0.121, 0.025) | 0.037→0.037 | 1.00 / 4.000 | 0.245 | 16.102 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 1.000
- lateral_force_integral: None
- approach_alignment: 0.713
- goal_progress: 0.903
- terminal_score: 0.903
- phase_score: 0.747
- phase_breakdown.reach_pre_contact_score: 0.231
- phase_breakdown.push_to_goal_score: 0.902

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.809
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.903
- **Median Q (composite search score)**: 0.520
- **K-run variance**: 0.0027
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 10.0
- **Final σ (mean)**: 0.324


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.75862,"average_solve_count":116.0,"average_success_count":116.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.approach_offset":0.04231,"push_to_goal_phase.push_distance":0.11222,"push_to_goal_phase.push_time":2.26434},"optimized_scores":{"best_composite_score":0.51768,"best_fitness_score":0.69768,"best_task_score":0.75441},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":59.0,"contact_point_centroid":[0.52292,0.07381,0.04783],"force_p95":192.19534,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":226.40227,"mean_force":131.87673,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.51528,0.08145,0.04984]},{"body_a":"world","body_b":"push_box","contact_count":3626.0,"contact_point_centroid":[0.51513,0.04801,-3e-05],"force_p95":0.34714,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":214.53565,"mean_force":2.41056,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.50579,0.04176,0.16739]},{"body_a":"world","body_b":"push_box","contact_count":1497.0,"contact_point_centroid":[0.51941,-0.04124,-8e-05],"force_p95":29.55859,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":73.2694,"mean_force":7.80698,"phase_index":1.0,"phase_name":"push_to_goal_phase","phase_type":"push","tcp_position_centroid":[0.50698,0.01078,0.0277]},{"body_a":"push_box","body_b":"link7","contact_count":177.0,"contact_point_centroid":[0.53912,-0.07084,0.05443],"force_p95":44.77352,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":54.98411,"mean_force":26.16033,"phase_index":1.0,"phase_name":"push_to_goal_phase","phase_type":"push","tcp_position_centroid":[0.50295,-0.05593,0.02663]},{"body_a":"attachment","body_b":"push_box","contact_count":836.0,"contact_point_centroid":[0.51574,-0.00796,0.04395],"force_p95":26.98933,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":44.33623,"mean_force":8.76627,"phase_index":1.0,"phase_name":"push_to_goal_phase","phase_type":"push","tcp_position_centroid":[0.50628,0.00361,0.0273]},{"body_a":"push_box","body_b":"link7","contact_count":18.0,"contact_point_centroid":[0.53928,-0.09241,0.05537],"force_p95":38.68973,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":39.20128,"mean_force":13.4881,"phase_index":2.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.5024,-0.07409,0.02784]},{"body_a":"attachment","body_b":"push_box","contact_count":203.0,"contact_point_centroid":[0.51408,-0.08325,0.05574],"force_p95":6.53381,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":27.37705,"mean_force":1.24959,"phase_index":2.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49959,-0.07355,0.04124]},{"body_a":"world","body_b":"push_box","contact_count":1155.0,"contact_point_centroid":[0.52306,-0.11485,-4e-05],"force_p95":0.55375,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":20.20657,"mean_force":0.48563,"phase_index":2.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49926,-0.07349,0.05124]}],"total_contact_groups":8},"final_pose_error":0.00996,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.51555,-0.10387,0.02499],"final_tcp_position":[0.49908,-0.07345,0.0683],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.51501,0.04767,0.025]},"peak_contact_force":226.40227,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":942.0,"n_steps_budget":1000.0,"object_pos_end":[0.51545,0.04687,0.02456],"object_pos_start":[0.51501,0.04767,0.025],"object_to_goal_dist_end":0.19747,"object_to_goal_dist_start":0.19823,"object_z_max":0.02554,"peak_contact_force":0.35284,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3685.0,"raw_peak_contact_force":226.40227,"subtask_id":"reach_pre_contact","tcp_end":[0.51585,0.08643,0.03382],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.04064,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51993,-0.10747,0.02954],"object_pos_start":[0.51545,0.04687,0.02456],"object_to_goal_dist_end":0.04719,"object_to_goal_dist_start":0.19747,"object_z_max":0.02953,"peak_contact_force":54.98411,"phase_name":"push_to_goal_phase","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2510.0,"raw_peak_contact_force":73.2694,"subtask_id":"push_to_goal","tcp_end":[0.50298,-0.07383,0.02745],"tcp_start":[0.51585,0.08643,0.03382],"tcp_to_object_dist_end":0.03772,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":450.0,"n_steps_budget":600.0,"object_pos_end":[0.51555,-0.10387,0.02499],"object_pos_start":[0.51993,-0.10747,0.02954],"object_to_goal_dist_end":0.04868,"object_to_goal_dist_start":0.04719,"object_z_max":0.02988,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1376.0,"raw_peak_contact_force":39.20128,"tcp_end":[0.49908,-0.07345,0.0683],"tcp_start":[0.50298,-0.07383,0.02745],"tcp_to_object_dist_end":0.05543,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.76068,"average_solve_count":117.0,"average_success_count":117.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.approach_offset":0.04416,"push_to_goal_phase.push_distance":0.07216,"push_to_goal_phase.push_time":2.56115},"optimized_scores":{"best_composite_score":0.51961,"best_fitness_score":0.69961,"best_task_score":0.76808},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":49.0,"contact_point_centroid":[0.48286,0.08411,0.04819],"force_p95":170.04008,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":199.10083,"mean_force":124.30206,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.47579,0.09202,0.05084]},{"body_a":"world","body_b":"push_box","contact_count":3653.0,"contact_point_centroid":[0.47936,0.05872,-2e-05],"force_p95":0.25274,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":169.968,"mean_force":1.92164,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.48545,0.04809,0.16634]},{"body_a":"attachment","body_b":"push_box","contact_count":811.0,"contact_point_centroid":[0.48849,0.00492,0.04267],"force_p95":21.36202,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":36.64419,"mean_force":6.44201,"phase_index":1.0,"phase_name":"push_to_goal_phase","phase_type":"push","tcp_position_centroid":[0.47845,0.01654,0.02723]},{"body_a":"world","body_b":"push_box","contact_count":1376.0,"contact_point_centroid":[0.4919,-0.02383,-8e-05],"force_p95":13.12706,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":30.47309,"mean_force":4.63326,"phase_index":1.0,"phase_name":"push_to_goal_phase","phase_type":"push","tcp_position_centroid":[0.47733,0.02943,0.02786]},{"body_a":"push_box","body_b":"link7","contact_count":123.0,"contact_point_centroid":[0.51506,-0.02121,0.05402],"force_p95":16.04176,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":23.25941,"mean_force":5.22361,"phase_index":1.0,"phase_name":"push_to_goal_phase","phase_type":"push","tcp_position_centroid":[0.48078,-0.00532,0.02662]},{"body_a":"world","body_b":"push_box","contact_count":1577.0,"contact_point_centroid":[0.49469,-0.1025,-1e-05],"force_p95":0.26022,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.98881,"mean_force":0.26571,"phase_index":2.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48298,-0.06239,0.04634]},{"body_a":"push_box","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.522,-0.08652,0.0519],"force_p95":6.56092,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":6.86925,"mean_force":3.78599,"phase_index":2.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48668,-0.0627,0.02479]},{"body_a":"attachment","body_b":"push_box","contact_count":11.0,"contact_point_centroid":[0.50193,-0.07447,0.05085],"force_p95":1.40491,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.50634,"mean_force":0.77358,"phase_index":2.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48533,-0.06296,0.02602]}],"total_contact_groups":8},"final_pose_error":0.00996,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.49487,-0.10168,0.02499],"final_tcp_position":[0.48283,-0.06233,0.06561],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47924,0.05847,0.025]},"peak_contact_force":199.10083,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":936.0,"n_steps_budget":1000.0,"object_pos_end":[0.47943,0.05739,0.02491],"object_pos_start":[0.47924,0.05847,0.025],"object_to_goal_dist_end":0.2084,"object_to_goal_dist_start":0.2095,"object_z_max":0.02507,"peak_contact_force":0.24705,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3702.0,"raw_peak_contact_force":199.10083,"subtask_id":"reach_pre_contact","tcp_end":[0.47371,0.0982,0.03373],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.04214,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49802,-0.09908,0.02709],"object_pos_start":[0.47943,0.05739,0.02491],"object_to_goal_dist_end":0.051,"object_to_goal_dist_start":0.2084,"object_z_max":0.02839,"peak_contact_force":9.46657,"phase_name":"push_to_goal_phase","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2310.0,"raw_peak_contact_force":36.64419,"subtask_id":"push_to_goal","tcp_end":[0.48668,-0.06264,0.0248],"tcp_start":[0.47371,0.0982,0.03373],"tcp_to_object_dist_end":0.03823,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":418.0,"n_steps_budget":600.0,"object_pos_end":[0.49487,-0.10168,0.02499],"object_pos_start":[0.49802,-0.09908,0.02709],"object_to_goal_dist_end":0.04859,"object_to_goal_dist_start":0.051,"object_z_max":0.0271,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1590.0,"raw_peak_contact_force":6.98881,"tcp_end":[0.48283,-0.06233,0.06561],"tcp_start":[0.48668,-0.06264,0.0248],"tcp_to_object_dist_end":0.05783,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.75652,"average_solve_count":115.0,"average_success_count":115.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.approach_offset":0.06274,"push_to_goal_phase.push_distance":0.07954,"push_to_goal_phase.push_time":1.94236},"optimized_scores":{"best_composite_score":0.62938,"best_fitness_score":0.80938,"best_task_score":0.90323},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":733.0,"contact_point_centroid":[0.52767,-0.06542,0.02907],"force_p95":17.31652,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":23.81493,"mean_force":4.7572,"phase_index":1.0,"phase_name":"push_to_goal_phase","phase_type":"push","tcp_position_centroid":[0.52559,-0.05351,0.02396]},{"body_a":"world","body_b":"push_box","contact_count":1989.0,"contact_point_centroid":[0.53028,-0.07689,-5e-05],"force_p95":7.03298,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":11.41633,"mean_force":2.04483,"phase_index":1.0,"phase_name":"push_to_goal_phase","phase_type":"push","tcp_position_centroid":[0.53342,-0.03096,0.02485]},{"body_a":"world","body_b":"push_box","contact_count":1814.0,"contact_point_centroid":[0.50963,-0.1589,-1e-05],"force_p95":0.24532,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.11645,"mean_force":0.25231,"phase_index":2.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49942,-0.12042,0.04334]},{"body_a":"attachment","body_b":"push_box","contact_count":8.0,"contact_point_centroid":[0.51533,-0.13329,0.05025],"force_p95":1.32556,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.32561,"mean_force":0.83893,"phase_index":2.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50225,-0.12137,0.02277]},{"body_a":"world","body_b":"push_box","contact_count":3688.0,"contact_point_centroid":[0.54443,-0.02558,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.52811,0.01575,0.16475]}],"total_contact_groups":5},"final_pose_error":0.00997,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50952,-0.15853,0.02499],"final_tcp_position":[0.49926,-0.12032,0.0633],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.54443,-0.02558,0.025]},"peak_contact_force":23.81493,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":922.0,"n_steps_budget":1000.0,"object_pos_end":[0.54443,-0.02558,0.02499],"object_pos_start":[0.54443,-0.02558,0.025],"object_to_goal_dist_end":0.13211,"object_to_goal_dist_start":0.13211,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3688.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_pre_contact","tcp_end":[0.55824,0.03168,0.03139],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.05925,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51034,-0.15787,0.02536],"object_pos_start":[0.54443,-0.02558,0.02499],"object_to_goal_dist_end":0.013,"object_to_goal_dist_start":0.13211,"object_z_max":0.02542,"peak_contact_force":1.13614,"phase_name":"push_to_goal_phase","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2722.0,"raw_peak_contact_force":23.81493,"subtask_id":"push_to_goal","tcp_end":[0.50319,-0.12102,0.02244],"tcp_start":[0.55824,0.03168,0.03139],"tcp_to_object_dist_end":0.03765,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":464.0,"n_steps_budget":600.0,"object_pos_end":[0.50952,-0.15853,0.02499],"object_pos_start":[0.51034,-0.15787,0.02536],"object_to_goal_dist_end":0.01278,"object_to_goal_dist_start":0.013,"object_z_max":0.02536,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1822.0,"raw_peak_contact_force":2.11645,"tcp_end":[0.49926,-0.12032,0.0633],"tcp_start":[0.50319,-0.12102,0.02244],"tcp_to_object_dist_end":0.05507,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```