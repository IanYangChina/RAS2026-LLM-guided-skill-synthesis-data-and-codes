## Search State

- **Seed**: 6
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 8 | 0.1530 | 0.32 | ❌ rejected |
| 11 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | 0.1977 | 0.36 | ❌ rejected |
| 10 | approach → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | position_control | admittance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | 5 | -0.2659 | 0.00 | ❌ rejected |
| 9 | approach → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | position_control | admittance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.4958 | 0.85 | ❌ rejected |
| 8 | approach → push | linear_cartesian | linear_cartesian | position_control | admittance_control | pose_tolerance | pose_tolerance | 4 | 0.4968 | 0.75 | ❌ rejected |

**Proposal policy**: task_score is 0.32 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.153) — your mutation base

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

- **Composite score**: 0.153
- **task_score** (E): 0.323
- **fitness_score**: 0.363  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.250
  → phases frequently time out instead of reaching designed conditions
- **Complexity Penalty**: 0.460

## Per-Phase Performance

| Phase | Normal Term. Rate | Mean Displacement (m) |
| ------- | ------------------- | ------------------------ |
| approach_above | 1.00 | 0.1477 |
| descend_to_contact | 1.00 | 0.1080 |
| push_to_goal | 1.00 | 0.1393 |
| retract_after_push | 1.00 | 0.0967 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end |
| --- | --- | --- | --- | --- | --- |
| approach_above | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.497, 0.042, 0.162) | (0.500, 0.029, 0.025)→(0.500, 0.029, 0.025) | 0.180→0.180 |
| descend_to_contact | descend | 1.00 / force_exceeded | (0.497, 0.042, 0.162)→(0.495, 0.032, 0.055) | (0.500, 0.029, 0.025)→(0.500, 0.029, 0.025) | 0.180→0.180 |
| push_to_goal | push | 1.00 / step_budget | (0.495, 0.032, 0.055)→(0.494, -0.106, 0.041) | (0.500, 0.029, 0.025)→(0.499, -0.027, 0.025) | 0.180→0.124 |
| retract_after_push | retract | 1.00 / step_budget | (0.494, -0.106, 0.041)→(0.491, -0.106, 0.138) | (0.499, -0.027, 0.025)→(0.499, -0.027, 0.025) | 0.124→0.124 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.424
- approach_alignment: 0.816
- goal_progress: 0.424
- terminal_score: 0.424
- phase_score: 0.459
- phase_breakdown.push_complete_score: 0.424

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.445
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.424
- **Median Q (composite search score)**: 0.119
- **K-run variance**: 0.0034
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.331


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.01869,"average_solve_count":214.0,"average_success_count":214.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.approach_speed":0.09761,"approach_above.lateral_offset_y":0.01977,"descend_to_contact.descend_force_threshold":7.9228,"descend_to_contact.descend_speed":0.02622,"push_to_goal.lateral_push_offset":0.00531,"push_to_goal.push_distance":0.13626,"push_to_goal.push_speed":0.04092,"retract_after_push.retract_height":0.11921},"optimized_scores":{"best_composite_score":0.23521,"best_fitness_score":0.44521,"best_task_score":0.42397},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":241.0,"contact_point_centroid":[0.50972,-0.04334,0.05033],"force_p95":128.44636,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":131.68021,"mean_force":87.79847,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.50143,-0.0492,0.05325]},{"body_a":"world","body_b":"push_box","contact_count":770.0,"contact_point_centroid":[0.50483,-0.0537,-0.00033],"force_p95":89.94371,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":98.32473,"mean_force":27.89091,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.49987,-0.07144,0.04991]},{"body_a":"world","body_b":"push_box","contact_count":1240.0,"contact_point_centroid":[0.50396,-0.07449,-1e-05],"force_p95":0.24529,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24561,"mean_force":0.24514,"phase_index":3.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.49324,-0.13014,0.09033]},{"body_a":"world","body_b":"push_box","contact_count":1060.0,"contact_point_centroid":[0.50458,-0.01881,-1e-05],"force_p95":0.24532,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.50013,0.00036,0.2338]},{"body_a":"world","body_b":"push_box","contact_count":2720.0,"contact_point_centroid":[0.50458,-0.01881,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.49913,-0.00663,0.10725]}],"total_contact_groups":5},"final_pose_error":0.0198,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50396,-0.07449,0.02499],"final_tcp_position":[0.49328,-0.12992,0.14122],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50458,-0.01881,0.025]},"phases":[{"n_steps":265.0,"n_steps_budget":990.0,"object_pos_end":[0.50458,-0.01881,0.02499],"object_pos_start":[0.50458,-0.01881,0.025],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.025,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"pre_contact","tcp_end":[0.50131,0.00076,0.16429],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.1407,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":680.0,"n_steps_budget":1000.0,"object_pos_end":[0.50458,-0.01881,0.02499],"object_pos_start":[0.50458,-0.01881,0.02499],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.02499,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"pre_contact","tcp_end":[0.49974,-0.01391,0.05495],"tcp_start":[0.50131,0.00076,0.16429],"tcp_to_object_dist_end":0.03074,"terminated_normally":true,"termination_reason":"force_exceeded"},{"n_steps":339.0,"n_steps_budget":1000.0,"object_pos_end":[0.50396,-0.07455,0.02491],"object_pos_start":[0.50458,-0.01881,0.02499],"object_to_goal_dist_end":0.07555,"object_to_goal_dist_start":0.13127,"object_z_max":0.03502,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","subtask_id":"push_complete","tcp_end":[0.49632,-0.13057,0.04157],"tcp_start":[0.49974,-0.01391,0.05495],"tcp_to_object_dist_end":0.05893,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":310.0,"n_steps_budget":750.0,"object_pos_end":[0.50396,-0.07449,0.02499],"object_pos_start":[0.50396,-0.07455,0.02491],"object_to_goal_dist_end":0.07562,"object_to_goal_dist_start":0.07555,"object_z_max":0.02499,"phase_name":"retract_after_push","phase_peak_obstacle_force":0.0,"phase_type":"retract","tcp_end":[0.49328,-0.12992,0.14122],"tcp_start":[0.49632,-0.13057,0.04157],"tcp_to_object_dist_end":0.12921,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.06324,"average_solve_count":253.0,"average_success_count":253.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.approach_speed":0.11641,"approach_above.lateral_offset_y":0.01996,"descend_to_contact.descend_force_threshold":4.93878,"descend_to_contact.descend_speed":0.0285,"push_to_goal.lateral_push_offset":0.00172,"push_to_goal.push_distance":0.18732,"push_to_goal.push_speed":0.03139,"retract_after_push.retract_height":0.10782},"optimized_scores":{"best_composite_score":0.11884,"best_fitness_score":0.32884,"best_task_score":0.28095},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":228.0,"contact_point_centroid":[0.51742,0.02282,0.05096],"force_p95":115.44256,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":116.74254,"mean_force":78.07192,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.5094,0.01639,0.05375]},{"body_a":"world","body_b":"push_box","contact_count":1293.0,"contact_point_centroid":[0.51301,0.00332,-0.00018],"force_p95":71.66973,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":77.14306,"mean_force":14.10567,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.5035,-0.04383,0.0471]},{"body_a":"world","body_b":"push_box","contact_count":1184.0,"contact_point_centroid":[0.51501,0.04767,-1e-05],"force_p95":0.24532,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.50445,0.02786,0.23207]},{"body_a":"world","body_b":"push_box","contact_count":2552.0,"contact_point_centroid":[0.51501,0.04767,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.50866,0.05371,0.10604]},{"body_a":"world","body_b":"push_box","contact_count":1104.0,"contact_point_centroid":[0.51226,-0.00799,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":3.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.4948,-0.11779,0.0839]}],"total_contact_groups":5},"final_pose_error":0.01983,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.51226,-0.00799,0.02499],"final_tcp_position":[0.49473,-0.11753,0.12908],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.51501,0.04767,0.025]},"phases":[{"n_steps":296.0,"n_steps_budget":930.0,"object_pos_end":[0.51501,0.04767,0.02499],"object_pos_start":[0.51501,0.04767,0.025],"object_to_goal_dist_end":0.19823,"object_to_goal_dist_start":0.19823,"object_z_max":0.025,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"pre_contact","tcp_end":[0.51032,0.05783,0.16176],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.13723,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":638.0,"n_steps_budget":1000.0,"object_pos_end":[0.51501,0.04767,0.02499],"object_pos_start":[0.51501,0.04767,0.02499],"object_to_goal_dist_end":0.19823,"object_to_goal_dist_start":0.19823,"object_z_max":0.02499,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"pre_contact","tcp_end":[0.50976,0.04981,0.05463],"tcp_start":[0.51032,0.05783,0.16176],"tcp_to_object_dist_end":0.03018,"terminated_normally":true,"termination_reason":"force_exceeded"},{"n_steps":470.0,"n_steps_budget":1000.0,"object_pos_end":[0.51226,-0.00799,0.02499],"object_pos_start":[0.51501,0.04767,0.02499],"object_to_goal_dist_end":0.14254,"object_to_goal_dist_start":0.19823,"object_z_max":0.03516,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","subtask_id":"push_complete","tcp_end":[0.49789,-0.11811,0.04083],"tcp_start":[0.50976,0.04981,0.05463],"tcp_to_object_dist_end":0.11218,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":276.0,"n_steps_budget":690.0,"object_pos_end":[0.51226,-0.00799,0.02499],"object_pos_start":[0.51226,-0.00799,0.02499],"object_to_goal_dist_end":0.14254,"object_to_goal_dist_start":0.14254,"object_z_max":0.02499,"phase_name":"retract_after_push","phase_peak_obstacle_force":0.0,"phase_type":"retract","tcp_end":[0.49473,-0.11753,0.12908],"tcp_start":[0.49789,-0.11811,0.04083],"tcp_to_object_dist_end":0.15212,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.9087,"average_solve_count":230.0,"average_success_count":230.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.approach_speed":0.13056,"approach_above.lateral_offset_y":0.01921,"descend_to_contact.descend_force_threshold":7.41963,"descend_to_contact.descend_speed":0.01568,"push_to_goal.lateral_push_offset":0.00344,"push_to_goal.push_distance":0.15117,"push_to_goal.push_speed":0.03817,"retract_after_push.retract_height":0.12181},"optimized_scores":{"best_composite_score":0.10496,"best_fitness_score":0.31496,"best_task_score":0.26551},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":230.0,"contact_point_centroid":[0.48862,0.03215,0.0501],"force_p95":128.67509,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":131.51297,"mean_force":86.92946,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.48066,0.02603,0.05352]},{"body_a":"world","body_b":"push_box","contact_count":899.0,"contact_point_centroid":[0.48093,0.0193,-0.00026],"force_p95":106.43796,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":114.86191,"mean_force":22.71774,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.48304,-0.00874,0.04884]},{"body_a":"world","body_b":"push_box","contact_count":1196.0,"contact_point_centroid":[0.47924,0.05847,-1e-05],"force_p95":0.24532,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.48953,0.03231,0.23164]},{"body_a":"world","body_b":"push_box","contact_count":1252.0,"contact_point_centroid":[0.48188,0.00281,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24527,"mean_force":0.24525,"phase_index":3.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.48518,-0.06986,0.09158]},{"body_a":"world","body_b":"push_box","contact_count":2636.0,"contact_point_centroid":[0.47924,0.05847,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.4761,0.06335,0.10678]}],"total_contact_groups":5},"final_pose_error":0.01994,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.48188,0.00281,0.02499],"final_tcp_position":[0.48519,-0.06965,0.14365],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47924,0.05847,0.025]},"phases":[{"n_steps":299.0,"n_steps_budget":840.0,"object_pos_end":[0.47924,0.05847,0.02499],"object_pos_start":[0.47924,0.05847,0.025],"object_to_goal_dist_end":0.2095,"object_to_goal_dist_start":0.2095,"object_z_max":0.025,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"pre_contact","tcp_end":[0.4795,0.06682,0.16141],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.13668,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":659.0,"n_steps_budget":1000.0,"object_pos_end":[0.47924,0.05847,0.02499],"object_pos_start":[0.47924,0.05847,0.02499],"object_to_goal_dist_end":0.2095,"object_to_goal_dist_start":0.2095,"object_z_max":0.02499,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"pre_contact","tcp_end":[0.47539,0.06011,0.05551],"tcp_start":[0.4795,0.06682,0.16141],"tcp_to_object_dist_end":0.0308,"terminated_normally":true,"termination_reason":"force_exceeded"},{"n_steps":373.0,"n_steps_budget":1000.0,"object_pos_end":[0.48188,0.00281,0.02499],"object_pos_start":[0.47924,0.05847,0.02499],"object_to_goal_dist_end":0.15388,"object_to_goal_dist_start":0.2095,"object_z_max":0.035,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","subtask_id":"push_complete","tcp_end":[0.48821,-0.06997,0.04155],"tcp_start":[0.47539,0.06011,0.05551],"tcp_to_object_dist_end":0.0749,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":313.0,"n_steps_budget":780.0,"object_pos_end":[0.48188,0.00281,0.02499],"object_pos_start":[0.48188,0.00281,0.02499],"object_to_goal_dist_end":0.15388,"object_to_goal_dist_start":0.15388,"object_z_max":0.02499,"phase_name":"retract_after_push","phase_peak_obstacle_force":0.0,"phase_type":"retract","tcp_end":[0.48519,-0.06965,0.14365],"tcp_start":[0.48821,-0.06997,0.04155],"tcp_to_object_dist_end":0.13908,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```