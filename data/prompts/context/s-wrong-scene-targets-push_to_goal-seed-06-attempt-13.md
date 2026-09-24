## Search State

- **Seed**: 6
- **Iteration**: 14 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 13 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 10 | 0.0284 | 0.69 | ❌ rejected |
| 12 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 14 | -0.3172 | 0.50 | ❌ rejected |
| 11 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 11 | 0.0323 | 0.77 | ❌ rejected |
| 10 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.2502 | 0.87 | ❌ rejected |
| 9 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 11 | 0.1338 | 0.91 | ✅ accepted |

**Proposal policy**: task_score is 0.69 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen object start: [0.5, -0.15, 0.025]
- Frozen task target: [0.5, 0.0, 0.3]
- Goal object position: (0.5, 0.0, 0.3)
- Object initial pose: (0.5, -0.15, 0.025)
- Goal tolerance: 0.02 m
- Expressivity sigma: 1.0 m
- Expressivity threshold: 0.8
- Force limit: 25.0 N
- Robot initial TCP position: (0.5045797221766332, -0.01880749562239939, 0.025)
- Phase navigation guidance: the task `phase_target_map` may provide internal predefined TCP waypoint aliases / semantic phase ids. These names are not DSL phase types and are intentionally not enumerated here to avoid confusing ids with types. Phase `id` may be semantic, but phase `type` must be exactly one of the DSL enum values listed in the prompt.
- Primary evaluation target: **object displacement ratio toward goal_object_position**

## Scene Entities

robot:
  model: panda_pusher
  tcp_site: attachment_site
  gripper: null
  tcp_initial_world: [0.5045797221766332, -0.01880749562239939, 0.025]
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
  frozen_task_target: [0.5, 0.0, 0.3]
  frozen_object_starts: {'push_box': [0.5, -0.15, 0.025]}
  frozen_targets: {'task_goal': [0.5, 0.0, 0.3]}
  push_direction: [-0.0046, -0.1312, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 25
  force_scale_n: 5
  realized_scene_sha256: 5f9daa62d5a7a2b8a7116f2dfbb5f9857bb0d5d4b297d304a4e76a9a270e7ec7

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.913, which indicates the subtask decomposition is already effective.
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

## Current Skill (Q=0.028) — your mutation base

```yaml
skill: push_to_goal
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: reach_object
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.1
  weight: 0.3
- id: push_to_goal
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
    - 0.0
    - 0.1
    offset_along_axis:
      distance: -0.05
      axis: task_goal_direction
      mode: add_to_offset
      sign: positive
    tolerance: 0.02
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: replace
    approach_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
    approach_tolerance:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.02
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
    behind_distance:
      type: scalar
      range:
      - -0.15
      - -0.02
      default: -0.05
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
  subtask_id: reach_object
- id: descend_to_contact
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.025
    offset_along_axis:
      distance: -0.05
      axis: task_goal_direction
      mode: add_to_offset
      sign: positive
    tolerance: 0.02
  parameters:
    behind_distance:
      type: scalar
      range:
      - -0.15
      - -0.02
      default: -0.05
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    descend_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
    descend_tolerance:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.02
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
    descend_z_target:
      type: scalar
      range:
      - 0.015
      - 0.03
      default: 0.025
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: reach_object
- id: push_to_goal
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.025
    offset_along_axis:
      distance: 0.15
      axis: task_goal_direction
      mode: replace_offset_projection
      sign: positive
    tolerance: 0.02
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.1
      - 0.3
      default: 0.15
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
    push_tolerance:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.02
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  subtask_id: push_to_goal
- id: retract_high
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
    - 0.15
    tolerance: 0.05

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_behind** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.1], offset_along_axis={axis=task_goal_direction, distance=-0.05, mode=add_to_offset, sign=positive}, tolerance=0.02
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
    - approach_speed: status=consumed; consumers=generator.speed (replace)
    - approach_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
    - behind_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
- **descend_to_contact** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.025], offset_along_axis={axis=task_goal_direction, distance=-0.05, mode=add_to_offset, sign=positive}, tolerance=0.02
  - parameter_bindings:
    - behind_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - descend_speed: status=consumed; consumers=generator.speed (replace)
    - descend_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
    - descend_z_target: status=consumed; consumers=target.offset.z (replace)
- **push_to_goal** (`push`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.025], offset_along_axis={axis=task_goal_direction, distance=0.15, mode=replace_offset_projection, sign=positive}, tolerance=0.02
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
    - push_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
- **retract_high** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.15], tolerance=0.05
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.028
- **task_score** (E): 0.689
- **fitness_score**: 0.588  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.560

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_above | 1.00 | 1.00 | 0.1722 |
| descend_to_contact | 1.00 | 1.00 | 0.1111 |
| push_to_goal | 1.00 | 1.00 | 0.2126 |
| retract_high | 1.00 | 1.00 | 0.1006 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_above | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.497, 0.025, 0.134) | (0.500, 0.029, 0.025)→(0.500, 0.029, 0.025) | 0.180→0.180 | 1.00 / 4.000 | 0.245 | 0.245 |
| descend_to_contact | descend | 1.00 / step_budget | (0.497, 0.025, 0.134)→(0.495, 0.102, 0.054) | (0.500, 0.029, 0.025)→(0.500, 0.029, 0.025) | 0.180→0.180 | 1.00 / 4.000 | 0.245 | 0.245 |
| push_to_goal | push | 1.00 / time_limit | (0.495, 0.102, 0.054)→(0.493, -0.110, 0.050) | (0.500, 0.029, 0.025)→(0.511, -0.095, 0.031) | 0.180→0.061 | 1.00 / 2.333 | 27.810 | 127.110 |
| retract_high | retract | 1.00 / step_budget | (0.493, -0.110, 0.050)→(0.492, -0.110, 0.150) | (0.511, -0.095, 0.031)→(0.514, -0.107, 0.025) | 0.061→0.059 | 1.00 / 4.000 | 0.242 | 19.466 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 1.000
- lateral_force_integral: None
- approach_alignment: 0.884
- goal_progress: 0.816
- terminal_score: 0.816
- phase_score: 0.654
- phase_breakdown.push_to_goal_score: 0.879
- phase_breakdown.reach_object_score: 0.130

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.719
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.816
- **Median Q (composite search score)**: 0.030
- **K-run variance**: 0.0115
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.378


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
{"anchors":[{"name":"object","value":[0.5,-0.15,0.025]},{"name":"goal","value":[0.50458,-0.01881,0.025]}],"axes":[{"name":"push_direction","value":[-0.00458,-0.13119,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.50458,-0.01881,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.02941,"average_solve_count":136.0,"average_success_count":136.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.approach_height":0.07812,"approach_above.approach_speed":0.10519,"approach_above.approach_tolerance":0.01922,"descend_to_contact.behind_distance":-0.08863,"descend_to_contact.descend_speed":0.07943,"descend_to_contact.descend_tolerance":0.04991,"descend_to_contact.descend_z_target":0.01816,"push_to_goal.push_distance":0.20006,"push_to_goal.push_max_time":22.59544,"push_to_goal.push_speed":0.14933},"optimized_scores":{"best_composite_score":0.15887,"best_fitness_score":0.71887,"best_task_score":0.81604},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":781.0,"contact_point_centroid":[0.50783,-0.08455,0.04914],"force_p95":127.49152,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":156.42102,"mean_force":76.38467,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.50143,-0.08186,0.0514]},{"body_a":"world","body_b":"push_box","contact_count":2456.0,"contact_point_centroid":[0.50912,-0.07801,-0.00023],"force_p95":65.32815,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":100.80084,"mean_force":24.67024,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.50101,-0.04729,0.05078]},{"body_a":"world","body_b":"push_box","contact_count":282.0,"contact_point_centroid":[0.51139,-0.16432,-0.0004],"force_p95":0.93189,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.66664,"mean_force":0.45006,"phase_index":3.0,"phase_name":"retract_high","phase_type":"retract","tcp_position_centroid":[0.49546,-0.18191,0.10268]},{"body_a":"world","body_b":"push_box","contact_count":1384.0,"contact_point_centroid":[0.50458,-0.01881,-1e-05],"force_p95":0.24531,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.49998,-0.00797,0.2127]},{"body_a":"world","body_b":"push_box","contact_count":848.0,"contact_point_centroid":[0.50458,-0.01881,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.501,0.01706,0.08713]}],"total_contact_groups":5},"final_pose_error":0.04943,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.51092,-0.17154,0.02471],"final_tcp_position":[0.49631,-0.18181,0.14909],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50458,-0.01881,0.025]},"peak_contact_force":156.42102,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":346.0,"n_steps_budget":1000.0,"object_pos_end":[0.50458,-0.01881,0.02499],"object_pos_start":[0.50458,-0.01881,0.025],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1384.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_object","tcp_end":[0.50112,-0.01649,0.12242],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.09752,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":212.0,"n_steps_budget":930.0,"object_pos_end":[0.50458,-0.01881,0.02499],"object_pos_start":[0.50458,-0.01881,0.02499],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":848.0,"raw_peak_contact_force":0.24525,"subtask_id":"reach_object","tcp_end":[0.50292,0.05339,0.05284],"tcp_start":[0.50112,-0.01649,0.12242],"tcp_to_object_dist_end":0.0774,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51224,-0.14873,0.03508],"object_pos_start":[0.50458,-0.01881,0.02499],"object_to_goal_dist_end":0.01591,"object_to_goal_dist_start":0.13127,"object_z_max":0.03511,"peak_contact_force":0.4836,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3237.0,"raw_peak_contact_force":156.42102,"subtask_id":"push_to_goal","tcp_end":[0.49755,-0.18225,0.0485],"tcp_start":[0.50292,0.05339,0.05284],"tcp_to_object_dist_end":0.03898,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":120.0,"n_steps_budget":930.0,"object_pos_end":[0.51092,-0.17154,0.02471],"object_pos_start":[0.51224,-0.14873,0.03508],"object_to_goal_dist_end":0.02415,"object_to_goal_dist_start":0.01591,"object_z_max":0.03508,"peak_contact_force":0.23974,"phase_name":"retract_high","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":282.0,"raw_peak_contact_force":2.66664,"tcp_end":[0.49631,-0.18181,0.14909],"tcp_start":[0.49755,-0.18225,0.0485],"tcp_to_object_dist_end":0.12565,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `589e611c6c27578474525e3fd29be4fb5907d8bbd5d1ca44922bfd811e342c78`; realized-scene SHA-256: `c8d09cd43835becf8e5eb4413394fad8627e4bf404e9e7726e9f380b60e09752`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5,-0.15,0.025]},{"name":"goal","value":[0.51501,0.04767,0.025]}],"axes":[{"name":"push_direction","value":[-0.01501,-0.19767,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.51501,0.04767,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.02222,"average_solve_count":135.0,"average_success_count":135.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.approach_height":0.06619,"approach_above.approach_speed":0.11612,"approach_above.approach_tolerance":0.02343,"descend_to_contact.behind_distance":-0.0722,"descend_to_contact.descend_speed":0.07108,"descend_to_contact.descend_tolerance":0.02305,"descend_to_contact.descend_z_target":0.01935,"push_to_goal.push_distance":0.38471,"push_to_goal.push_max_time":16.88148,"push_to_goal.push_speed":0.14187},"optimized_scores":{"best_composite_score":0.03047,"best_fitness_score":0.59047,"best_task_score":0.6866},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":805.0,"contact_point_centroid":[0.51442,-0.01053,0.04958],"force_p95":115.84859,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":127.68473,"mean_force":68.14684,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.50795,-0.0088,0.05188]},{"body_a":"world","body_b":"push_box","contact_count":2340.0,"contact_point_centroid":[0.5161,-0.01293,-0.00023],"force_p95":60.89818,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":67.51804,"mean_force":23.83344,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.50821,0.00574,0.05126]},{"body_a":"world","body_b":"push_box","contact_count":451.0,"contact_point_centroid":[0.51165,-0.08837,-2e-05],"force_p95":0.34318,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.56717,"mean_force":0.28285,"phase_index":3.0,"phase_name":"retract_high","phase_type":"retract","tcp_position_centroid":[0.49389,-0.12332,0.09396]},{"body_a":"attachment","body_b":"push_box","contact_count":4.0,"contact_point_centroid":[0.49943,-0.11197,0.05006],"force_p95":5.93193,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":6.68835,"mean_force":2.78276,"phase_index":3.0,"phase_name":"retract_high","phase_type":"retract","tcp_position_centroid":[0.4959,-0.12378,0.04647]},{"body_a":"world","body_b":"push_box","contact_count":1524.0,"contact_point_centroid":[0.51501,0.04767,-1e-05],"force_p95":0.2453,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.50445,0.02047,0.20584]},{"body_a":"world","body_b":"push_box","contact_count":736.0,"contact_point_centroid":[0.51501,0.04767,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.51157,0.07108,0.08044]}],"total_contact_groups":6},"final_pose_error":0.0491,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.51225,-0.08909,0.02499],"final_tcp_position":[0.49496,-0.12318,0.1474],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.51501,0.04767,0.025]},"peak_contact_force":127.68473,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":381.0,"n_steps_budget":1000.0,"object_pos_end":[0.51501,0.04767,0.02499],"object_pos_start":[0.51501,0.04767,0.025],"object_to_goal_dist_end":0.19823,"object_to_goal_dist_start":0.19823,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1524.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_object","tcp_end":[0.51036,0.0421,0.10934],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.08466,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":184.0,"n_steps_budget":900.0,"object_pos_end":[0.51501,0.04767,0.02499],"object_pos_start":[0.51501,0.04767,0.02499],"object_to_goal_dist_end":0.19823,"object_to_goal_dist_start":0.19823,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":736.0,"raw_peak_contact_force":0.24525,"subtask_id":"reach_object","tcp_end":[0.51482,0.10268,0.05273],"tcp_start":[0.51036,0.0421,0.10934],"tcp_to_object_dist_end":0.06161,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51319,-0.08842,0.02532],"object_pos_start":[0.51501,0.04767,0.02499],"object_to_goal_dist_end":0.06298,"object_to_goal_dist_start":0.19823,"object_z_max":0.03516,"peak_contact_force":0.35413,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3145.0,"raw_peak_contact_force":127.68473,"subtask_id":"push_to_goal","tcp_end":[0.49615,-0.12341,0.04649],"tcp_start":[0.51482,0.10268,0.05273],"tcp_to_object_dist_end":0.0443,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":119.0,"n_steps_budget":930.0,"object_pos_end":[0.51225,-0.08909,0.02499],"object_pos_start":[0.51319,-0.08842,0.02532],"object_to_goal_dist_end":0.06213,"object_to_goal_dist_start":0.06298,"object_z_max":0.02532,"peak_contact_force":0.24525,"phase_name":"retract_high","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":455.0,"raw_peak_contact_force":7.56717,"tcp_end":[0.49496,-0.12318,0.1474],"tcp_start":[0.49615,-0.12341,0.04649],"tcp_to_object_dist_end":0.12824,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `f2c9c63f0d9eca1b3ff8bf951759f6a3adee73f9f65e1cd3613c5e9d1203ebcc`; realized-scene SHA-256: `f3b8ea82cefd9504be10e2d47c49094a836a703404c06bdee3b01a27a59bf7be`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5,-0.15,0.025]},{"name":"goal","value":[0.47924,0.05847,0.025]}],"axes":[{"name":"push_direction","value":[0.02076,-0.20847,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.47924,0.05847,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.17949,"average_solve_count":234.0,"average_success_count":234.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.approach_height":0.12713,"approach_above.approach_speed":0.02015,"approach_above.approach_tolerance":0.01465,"descend_to_contact.behind_distance":-0.10735,"descend_to_contact.descend_speed":0.07393,"descend_to_contact.descend_tolerance":0.02569,"descend_to_contact.descend_z_target":0.02002,"push_to_goal.push_distance":0.31565,"push_to_goal.push_max_time":26.06158,"push_to_goal.push_speed":0.11192},"optimized_scores":{"best_composite_score":-0.10425,"best_fitness_score":0.45575,"best_task_score":0.56305},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":554.0,"contact_point_centroid":[0.48093,0.02108,0.04961],"force_p95":80.82833,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":97.22366,"mean_force":32.02892,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.47664,0.03172,0.05119]},{"body_a":"world","body_b":"push_box","contact_count":2579.0,"contact_point_centroid":[0.48671,0.02743,-8e-05],"force_p95":34.94225,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":65.77377,"mean_force":7.2008,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.47093,0.08109,0.05166]},{"body_a":"attachment","body_b":"push_box","contact_count":11.0,"contact_point_centroid":[0.49395,-0.03244,0.05052],"force_p95":38.86529,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":48.16486,"mean_force":8.78515,"phase_index":3.0,"phase_name":"retract_high","phase_type":"retract","tcp_position_centroid":[0.48585,-0.02507,0.0542]},{"body_a":"world","body_b":"push_box","contact_count":250.0,"contact_point_centroid":[0.51231,-0.05534,-0.00043],"force_p95":1.73686,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":47.55048,"mean_force":0.89292,"phase_index":3.0,"phase_name":"retract_high","phase_type":"retract","tcp_position_centroid":[0.48476,-0.02486,0.11089]},{"body_a":"world","body_b":"push_box","contact_count":1204.0,"contact_point_centroid":[0.47924,0.05847,-1e-05],"force_p95":0.24531,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.48983,0.0233,0.23722]},{"body_a":"world","body_b":"push_box","contact_count":1288.0,"contact_point_centroid":[0.47924,0.05847,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.47249,0.09811,0.11273]}],"total_contact_groups":6},"final_pose_error":0.04983,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.51742,-0.06013,0.02465],"final_tcp_position":[0.48536,-0.02473,0.15372],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47924,0.05847,0.025]},"peak_contact_force":97.22366,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":301.0,"n_steps_budget":1000.0,"object_pos_end":[0.47924,0.05847,0.02499],"object_pos_start":[0.47924,0.05847,0.025],"object_to_goal_dist_end":0.2095,"object_to_goal_dist_start":0.2095,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1204.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_object","tcp_end":[0.4798,0.04942,0.16982],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.14511,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":322.0,"n_steps_budget":1000.0,"object_pos_end":[0.47924,0.05847,0.02499],"object_pos_start":[0.47924,0.05847,0.02499],"object_to_goal_dist_end":0.2095,"object_to_goal_dist_start":0.2095,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1288.0,"raw_peak_contact_force":0.24525,"subtask_id":"reach_object","tcp_end":[0.46676,0.14924,0.05656],"tcp_start":[0.4798,0.04942,0.16982],"tcp_to_object_dist_end":0.09691,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50826,-0.04708,0.03384],"object_pos_start":[0.47924,0.05847,0.02499],"object_to_goal_dist_end":0.10363,"object_to_goal_dist_start":0.2095,"object_z_max":0.03459,"peak_contact_force":82.59314,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3133.0,"raw_peak_contact_force":97.22366,"subtask_id":"push_to_goal","tcp_end":[0.48632,-0.02468,0.05354],"tcp_start":[0.46676,0.14924,0.05656],"tcp_to_object_dist_end":0.03703,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":116.0,"n_steps_budget":930.0,"object_pos_end":[0.51742,-0.06013,0.02465],"object_pos_start":[0.50826,-0.04708,0.03384],"object_to_goal_dist_end":0.09154,"object_to_goal_dist_start":0.10363,"object_z_max":0.03459,"peak_contact_force":0.24001,"phase_name":"retract_high","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":261.0,"raw_peak_contact_force":48.16486,"tcp_end":[0.48536,-0.02473,0.15372],"tcp_start":[0.48632,-0.02468,0.05354],"tcp_to_object_dist_end":0.13763,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```