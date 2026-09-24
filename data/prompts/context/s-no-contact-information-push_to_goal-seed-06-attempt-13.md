## Search State

- **Seed**: 6
- **Iteration**: 14 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 13 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 8 | 0.0974 | 0.36 | ❌ rejected |
| 12 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 8 | 0.1530 | 0.32 | ❌ rejected |
| 11 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | 0.1977 | 0.36 | ❌ rejected |
| 10 | approach → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | position_control | admittance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | 5 | -0.2659 | 0.00 | ❌ rejected |
| 9 | approach → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | position_control | admittance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.4958 | 0.85 | ❌ rejected |

**Proposal policy**: task_score is 0.36 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `5f9daa62d5a7a2b8a7116f2dfbb5f9857bb0d5d4b297d304a4e76a9a270e7ec7`
- Frozen object start: [0.5045797221766332, -0.01880749562239939, 0.025]
- Frozen task target: [0.5, -0.15, 0.025]
- Goal object position: (0.5, -0.15, 0.025)
- Object initial pose: (0.5045797221766332, -0.01880749562239939, 0.025)
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
  frozen_object_start: [0.5046, -0.0188, 0.025]
  frozen_task_target: [0.5, -0.15, 0.025]
  frozen_object_starts: {'push_box': [0.5045797221766332, -0.01880749562239939, 0.025]}
  frozen_targets: {'task_goal': [0.5, -0.15, 0.025]}
  push_direction: [-0.0046, -0.1312, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 25
  force_scale_n: 5
  realized_scene_sha256: 5f9daa62d5a7a2b8a7116f2dfbb5f9857bb0d5d4b297d304a4e76a9a270e7ec7

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.949, which indicates the subtask decomposition is already effective.
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
| `object` | offset from object initial position (0.5045797221766332, -0.01880749562239939, 0.025) | approach/contact targets near object start |
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

## Current Skill (Q=0.097) — your mutation base

```yaml
skill: push_to_goal
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: pre_contact
  anchor: object
  weight: 0.3
- id: push_complete
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
    entity: push_box
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.03
      axis: task_goal_direction
      mode: add_to_offset
      sign: negative
    tolerance: 0.02
    orientation:
      mode: none
  parameters:
    lateral_offset_y:
      type: scalar
      range:
      - -0.02
      - 0.02
      default: 0.0
      binds_to:
      - path: target.offset.y
        mode: add
    speed:
      type: scalar
      range:
      - 0.03
      - 0.15
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: pre_contact
- id: push_to_goal
  type: push
  generator: linear_cartesian
  control: admittance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: push_box
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.15
      axis: task_goal_direction
      mode: add_to_offset
      sign: positive
    tolerance: 0.02
    orientation:
      mode: none
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.08
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: push_complete
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
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    retract_height:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: replace

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_object** (`approach`)
  - target: source=yaml, anchor=task_object, entity=push_box, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.03, mode=add_to_offset, sign=negative}, tolerance=0.02
  - orientation: mode=none
  - parameter_bindings:
    - lateral_offset_y: status=consumed; consumers=target.offset.y (add)
    - speed: status=consumed; consumers=generator.speed (replace)
- **push_to_goal** (`push`)
  - target: source=yaml, anchor=task_object, entity=push_box, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.15, mode=add_to_offset, sign=positive}, tolerance=0.02
  - orientation: mode=none
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
- **retract_after_push** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.1], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - retract_height: status=consumed; consumers=target.offset.z (replace)

## Design Metrics

- **Composite score**: 0.097
- **task_score** (E): 0.356
- **fitness_score**: 0.307  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.250
  → phases frequently time out instead of reaching designed conditions
- **Complexity Penalty**: 0.460

## Per-Phase Performance

| Phase | Normal Term. Rate | Mean Displacement (m) |
| ------- | ------------------- | ------------------------ |
| approach_above | 1.00 | 0.1327 |
| descend_to_contact | 1.00 | 0.1390 |
| push_to_goal | 1.00 | 0.1473 |
| retract_after_push | 1.00 | 0.1005 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end |
| --- | --- | --- | --- | --- | --- |
| approach_above | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.497, 0.066, 0.190) | (0.500, 0.029, 0.025)→(0.500, 0.029, 0.025) | 0.180→0.180 |
| descend_to_contact | descend | 1.00 / force_exceeded | (0.497, 0.066, 0.190)→(0.495, 0.036, 0.054) | (0.500, 0.029, 0.025)→(0.500, 0.029, 0.025) | 0.180→0.180 |
| push_to_goal | push | 1.00 / step_budget | (0.495, 0.036, 0.054)→(0.510, -0.107, 0.024) | (0.500, 0.029, 0.025)→(0.504, -0.032, 0.025) | 0.180→0.118 |
| retract_after_push | retract | 1.00 / step_budget | (0.510, -0.107, 0.024)→(0.507, -0.106, 0.124) | (0.504, -0.032, 0.025)→(0.504, -0.032, 0.025) | 0.118→0.118 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.455
- approach_alignment: 0.839
- goal_progress: 0.453
- terminal_score: 0.453
- phase_score: 0.343
- phase_breakdown.push_complete_score: 0.453

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.387
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.453
- **Median Q (composite search score)**: 0.066
- **K-run variance**: 0.0032
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.391


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `acf3715aaa310bcc73047d49f01e71bc863ef036ae437b7dc851a0f6d3fe40ae`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.06,0.06]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `ec1d0331416d42e6883eeb3b72499fac99c0735b785eb70ece69dc94e8044fc3`; realized-scene SHA-256: `5f9daa62d5a7a2b8a7116f2dfbb5f9857bb0d5d4b297d304a4e76a9a270e7ec7`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50458,-0.01881,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.00458,-0.13119,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.50458,-0.01881,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.00858,"average_solve_count":233.0,"average_success_count":233.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.lateral_offset_y":0.0171,"approach_above.speed":0.14039,"descend_to_contact.descend_speed":0.02454,"descend_to_contact.force_threshold":12.73949,"push_to_goal.lateral_push_offset":0.0162,"push_to_goal.push_distance":0.16162,"push_to_goal.push_speed":0.0414,"retract_after_push.retract_height":0.12406},"optimized_scores":{"best_composite_score":0.17716,"best_fitness_score":0.38716,"best_task_score":0.45282},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":315.0,"contact_point_centroid":[0.51637,-0.0452,0.04789],"force_p95":167.48176,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":174.23835,"mean_force":118.40114,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.50729,-0.05059,0.0492]},{"body_a":"world","body_b":"push_box","contact_count":1207.0,"contact_point_centroid":[0.50714,-0.06019,-0.00035],"force_p95":138.70281,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":158.28115,"mean_force":31.38221,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.50747,-0.08707,0.04006]},{"body_a":"world","body_b":"push_box","contact_count":836.0,"contact_point_centroid":[0.50458,-0.01881,-0.0],"force_p95":0.24533,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.50071,0.01092,0.24812]},{"body_a":"world","body_b":"push_box","contact_count":3512.0,"contact_point_centroid":[0.50458,-0.01881,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.49992,0.00596,0.12076]},{"body_a":"world","body_b":"push_box","contact_count":1328.0,"contact_point_centroid":[0.50647,-0.07846,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":3.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.50652,-0.16079,0.0739]}],"total_contact_groups":5},"final_pose_error":0.01989,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50647,-0.07846,0.02499],"final_tcp_position":[0.50659,-0.16059,0.12725],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50458,-0.01881,0.025]},"phases":[{"n_steps":209.0,"n_steps_budget":600.0,"object_pos_end":[0.50458,-0.01881,0.02499],"object_pos_start":[0.50458,-0.01881,0.025],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.025,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"pre_contact","tcp_end":[0.50232,0.02287,0.19355],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.17365,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":878.0,"n_steps_budget":1000.0,"object_pos_end":[0.50458,-0.01881,0.02499],"object_pos_start":[0.50458,-0.01881,0.02499],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.02499,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"pre_contact","tcp_end":[0.50016,-0.01049,0.05387],"tcp_start":[0.50232,0.02287,0.19355],"tcp_to_object_dist_end":0.03038,"terminated_normally":true,"termination_reason":"force_exceeded"},{"n_steps":467.0,"n_steps_budget":1000.0,"object_pos_end":[0.50647,-0.07846,0.02499],"object_pos_start":[0.50458,-0.01881,0.02499],"object_to_goal_dist_end":0.07183,"object_to_goal_dist_start":0.13127,"object_z_max":0.03482,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","subtask_id":"push_complete","tcp_end":[0.50974,-0.1614,0.02281],"tcp_start":[0.50016,-0.01049,0.05387],"tcp_to_object_dist_end":0.08303,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":332.0,"n_steps_budget":780.0,"object_pos_end":[0.50647,-0.07846,0.02499],"object_pos_start":[0.50647,-0.07846,0.02499],"object_to_goal_dist_end":0.07183,"object_to_goal_dist_start":0.07183,"object_z_max":0.02499,"phase_name":"retract_after_push","phase_peak_obstacle_force":0.0,"phase_type":"retract","tcp_end":[0.50659,-0.16059,0.12725],"tcp_start":[0.50974,-0.1614,0.02281],"tcp_to_object_dist_end":0.13115,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `589e611c6c27578474525e3fd29be4fb5907d8bbd5d1ca44922bfd811e342c78`; realized-scene SHA-256: `c8d09cd43835becf8e5eb4413394fad8627e4bf404e9e7726e9f380b60e09752`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.51501,0.04767,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.01501,-0.19767,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.51501,0.04767,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.35326,"average_solve_count":184.0,"average_success_count":184.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.lateral_offset_y":0.01995,"approach_above.speed":0.10541,"descend_to_contact.descend_speed":0.06727,"descend_to_contact.force_threshold":2.66856,"push_to_goal.lateral_push_offset":0.01958,"push_to_goal.push_distance":0.16412,"push_to_goal.push_speed":0.04058,"retract_after_push.retract_height":0.10334},"optimized_scores":{"best_composite_score":0.04906,"best_fitness_score":0.25906,"best_task_score":0.2967},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":316.0,"contact_point_centroid":[0.52537,0.02133,0.04807],"force_p95":161.42228,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":166.29442,"mean_force":113.87563,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.51643,0.01554,0.04927]},{"body_a":"world","body_b":"push_box","contact_count":1205.0,"contact_point_centroid":[0.51658,0.0057,-0.00035],"force_p95":129.03519,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":144.05576,"mean_force":30.31674,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.51609,-0.02243,0.03992]},{"body_a":"world","body_b":"push_box","contact_count":1156.0,"contact_point_centroid":[0.51501,0.04767,-1e-05],"force_p95":0.24532,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.50548,0.04028,0.24439]},{"body_a":"world","body_b":"push_box","contact_count":2912.0,"contact_point_centroid":[0.51501,0.04767,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.51017,0.06876,0.11833]},{"body_a":"world","body_b":"push_box","contact_count":1060.0,"contact_point_centroid":[0.51591,-0.01149,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":3.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.5138,-0.09695,0.06368]}],"total_contact_groups":5},"final_pose_error":0.01989,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.51591,-0.01149,0.02499],"final_tcp_position":[0.51366,-0.09668,0.10665],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.51501,0.04767,0.025]},"phases":[{"n_steps":289.0,"n_steps_budget":960.0,"object_pos_end":[0.51501,0.04767,0.02499],"object_pos_start":[0.51501,0.04767,0.025],"object_to_goal_dist_end":0.19823,"object_to_goal_dist_start":0.19823,"object_z_max":0.025,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"pre_contact","tcp_end":[0.51242,0.08328,0.18768],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.16657,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":728.0,"n_steps_budget":1000.0,"object_pos_end":[0.51501,0.04767,0.02499],"object_pos_start":[0.51501,0.04767,0.02499],"object_to_goal_dist_end":0.19823,"object_to_goal_dist_start":0.19823,"object_z_max":0.02499,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"pre_contact","tcp_end":[0.51049,0.05454,0.05351],"tcp_start":[0.51242,0.08328,0.18768],"tcp_to_object_dist_end":0.02969,"terminated_normally":true,"termination_reason":"force_exceeded"},{"n_steps":471.0,"n_steps_budget":1000.0,"object_pos_end":[0.51591,-0.01149,0.02499],"object_pos_start":[0.51501,0.04767,0.02499],"object_to_goal_dist_end":0.13942,"object_to_goal_dist_start":0.19823,"object_z_max":0.03478,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","subtask_id":"push_complete","tcp_end":[0.51703,-0.09714,0.02291],"tcp_start":[0.51049,0.05454,0.05351],"tcp_to_object_dist_end":0.08568,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":265.0,"n_steps_budget":660.0,"object_pos_end":[0.51591,-0.01149,0.02499],"object_pos_start":[0.51591,-0.01149,0.02499],"object_to_goal_dist_end":0.13942,"object_to_goal_dist_start":0.13942,"object_z_max":0.02499,"phase_name":"retract_after_push","phase_peak_obstacle_force":0.0,"phase_type":"retract","tcp_end":[0.51366,-0.09668,0.10665],"tcp_start":[0.51703,-0.09714,0.02291],"tcp_to_object_dist_end":0.11803,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `f2c9c63f0d9eca1b3ff8bf951759f6a3adee73f9f65e1cd3613c5e9d1203ebcc`; realized-scene SHA-256: `f3b8ea82cefd9504be10e2d47c49094a836a703404c06bdee3b01a27a59bf7be`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.47924,0.05847,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[0.02076,-0.20847,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.47924,0.05847,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.59172,"average_solve_count":169.0,"average_success_count":169.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.lateral_offset_y":0.01926,"approach_above.speed":0.08166,"descend_to_contact.descend_speed":0.05085,"descend_to_contact.force_threshold":10.712,"push_to_goal.lateral_push_offset":0.01704,"push_to_goal.push_distance":0.13912,"push_to_goal.push_speed":0.07588,"retract_after_push.retract_height":0.13276},"optimized_scores":{"best_composite_score":0.06612,"best_fitness_score":0.27612,"best_task_score":0.31738},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":751.0,"contact_point_centroid":[0.48915,0.02121,-0.00067],"force_p95":184.35042,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":200.1369,"mean_force":59.07208,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.49011,0.01289,0.04463]},{"body_a":"attachment","body_b":"push_box","contact_count":321.0,"contact_point_centroid":[0.49823,0.02974,0.04677],"force_p95":186.95098,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":198.76291,"mean_force":136.63095,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.48944,0.02423,0.04873]},{"body_a":"world","body_b":"push_box","contact_count":1212.0,"contact_point_centroid":[0.47924,0.05847,-1e-05],"force_p95":0.24531,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.48834,0.04467,0.24429]},{"body_a":"world","body_b":"push_box","contact_count":3176.0,"contact_point_centroid":[0.47924,0.05847,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.47479,0.07848,0.11888]},{"body_a":"world","body_b":"push_box","contact_count":1404.0,"contact_point_centroid":[0.48929,-0.00739,-2e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24469,"phase_index":3.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.49947,-0.06144,0.08044]}],"total_contact_groups":5},"final_pose_error":0.01973,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.48929,-0.00739,0.02499],"final_tcp_position":[0.49955,-0.06125,0.13806],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47924,0.05847,0.025]},"phases":[{"n_steps":303.0,"n_steps_budget":1000.0,"object_pos_end":[0.47924,0.05847,0.02499],"object_pos_start":[0.47924,0.05847,0.025],"object_to_goal_dist_end":0.2095,"object_to_goal_dist_start":0.2095,"object_z_max":0.025,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"pre_contact","tcp_end":[0.47715,0.09237,0.18759],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.16611,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":794.0,"n_steps_budget":1000.0,"object_pos_end":[0.47924,0.05847,0.02499],"object_pos_start":[0.47924,0.05847,0.02499],"object_to_goal_dist_end":0.2095,"object_to_goal_dist_start":0.2095,"object_z_max":0.02499,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"pre_contact","tcp_end":[0.475,0.06497,0.05429],"tcp_start":[0.47715,0.09237,0.18759],"tcp_to_object_dist_end":0.03031,"terminated_normally":true,"termination_reason":"force_exceeded"},{"n_steps":397.0,"n_steps_budget":1000.0,"object_pos_end":[0.48928,-0.00732,0.02451],"object_pos_start":[0.47924,0.05847,0.02499],"object_to_goal_dist_end":0.14309,"object_to_goal_dist_start":0.2095,"object_z_max":0.03526,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","subtask_id":"push_complete","tcp_end":[0.50263,-0.0615,0.02479],"tcp_start":[0.475,0.06497,0.05429],"tcp_to_object_dist_end":0.0558,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":351.0,"n_steps_budget":840.0,"object_pos_end":[0.48929,-0.00739,0.02499],"object_pos_start":[0.48928,-0.00732,0.02451],"object_to_goal_dist_end":0.14301,"object_to_goal_dist_start":0.14309,"object_z_max":0.02499,"phase_name":"retract_after_push","phase_peak_obstacle_force":0.0,"phase_type":"retract","tcp_end":[0.49955,-0.06125,0.13806],"tcp_start":[0.50263,-0.0615,0.02479],"tcp_to_object_dist_end":0.12567,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```