## Search State

- **Seed**: 6
- **Iteration**: 11 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 10 | approach → descend → contact → push | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | admittance_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 8 | -0.0651 | 0.01 | ❌ rejected |
| 9 | approach → descend → contact → push | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | admittance_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 8 | 0.3828 | 0.57 | ❌ rejected |
| 8 | approach → descend → contact → push | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | admittance_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 8 | 0.3419 | 0.48 | ❌ rejected |
| 7 | approach → descend → contact → push | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | admittance_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 8 | 0.3825 | 0.57 | ❌ rejected |
| 6 | approach → descend → contact → push | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | admittance_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 8 | 0.3831 | 0.57 | ✅ accepted |

**Proposal policy**: task_score is 0.01 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.065) — your mutation base

```yaml
skill: push_to_goal
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: pre_contact
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.1
  weight: 0.2
- id: contact
  anchor: object
  metric: contact
  offset:
  - 0.0
  - 0.0
  - 0.025
  weight: 0.2
- id: push_goal
  target_entity: object
  metric: goal_progress
  weight: 0.6
phases:
- id: approach_to_precontact
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
    - 0.1
    offset_along_axis:
      distance: 0.05
      axis: task_goal_direction
      mode: replace_offset_projection
      sign: negative
    orientation:
      mode: keep_current
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
    arc_height:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.arc_height
        mode: replace
  subtask_id: pre_contact
- id: descend_to_contact_height
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
    - 0.0
    offset_along_axis:
      distance: 0.05
      axis: task_goal_direction
      mode: replace_offset_projection
      sign: negative
    orientation:
      mode: keep_current
  parameters:
    descend_speed:
      type: scalar
      range:
      - 0.01
      - 0.08
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: pre_contact
- id: engage_contact
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
    offset_along_axis:
      distance: 0.1
      axis: task_goal_direction
      mode: add_to_offset
      sign: positive
    orientation:
      mode: keep_current
  parameters:
    contact_force_threshold:
      type: scalar
      range:
      - 0.5
      - 5.0
      default: 2.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    engage_speed:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: contact
- id: push_to_goal
  type: push
  generator: linear_cartesian
  control: admittance_control
  termination: time_limit
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.15
      axis: task_goal_direction
      mode: add_to_offset
      sign: positive
    orientation:
      mode: keep_current
  parameters:
    max_push_time:
      type: scalar
      range:
      - 2.0
      - 12.0
      default: 6.0
      binds_to:
      - path: duration.max_time
        mode: replace
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
  guards:
  - id: force_limit_push
    when: during_phase
    predicate: force_below
    threshold: 25.0
    on_failure: abort
  retries:
    max_attempts: 2
    strategy: reduce_speed
    offset:
    - 0.0
    - 0.0
    - 0.0
  subtask_id: push_goal

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_to_precontact** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.1], offset_along_axis={axis=task_goal_direction, distance=0.05, mode=replace_offset_projection, sign=negative}
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
    - arc_height: status=consumed; consumers=generator.arc_height (replace)
- **descend_to_contact_height** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.05, mode=replace_offset_projection, sign=negative}
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (replace)
- **engage_contact** (`contact`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.1, mode=add_to_offset, sign=positive}
  - orientation: mode=keep_current
  - parameter_bindings:
    - contact_force_threshold: status=consumed; consumers=termination.force_threshold (replace)
    - engage_speed: status=consumed; consumers=generator.speed (replace)
- **push_to_goal** (`push`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.15, mode=add_to_offset, sign=positive}
  - orientation: mode=keep_current
  - parameter_bindings:
    - max_push_time: status=consumed; consumers=duration.max_time (replace)
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=force_limit_push, when=during_phase, predicate=force_below, on_failure=abort, threshold=25.0
  - retries: max_attempts=2, strategy=reduce_speed, offset=[0.0, 0.0, 0.0]

## Design Metrics

- **Composite score**: -0.065
- **task_score** (E): 0.006
- **fitness_score**: 0.145  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.250
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.460

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_to_precontact | 1.00 | 1.00 | 0.1803 |
| descend_to_contact_height | 1.00 | 1.00 | 0.0927 |
| engage_contact | 1.00 | 1.00 | 0.0001 |
| push_to_goal | 0.00 | 1.00 | 0.0001 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_to_precontact | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.497, 0.047, 0.132) | (0.500, 0.029, 0.025)→(0.500, 0.029, 0.025) | 0.180→0.180 | 1.00 / 4.000 | 0.245 | 0.245 |
| descend_to_contact_height | descend | 1.00 / step_budget | (0.497, 0.047, 0.132)→(0.519, 0.031, 0.044) | (0.500, 0.029, 0.025)→(0.505, 0.028, 0.025) | 0.180→0.179 | 1.00 / 3.000 | 211.328 | 241.049 |
| engage_contact | contact | 1.00 / force_exceeded | (0.519, 0.031, 0.044)→(0.519, 0.031, 0.044) | (0.505, 0.028, 0.025)→(0.505, 0.028, 0.025) | 0.179→0.179 | 1.00 / 3.333 | 150.432 | 105.267 |
| push_to_goal | push | 0.00 / guard_failure | (0.519, 0.031, 0.044)→(0.519, 0.031, 0.044) | (0.505, 0.028, 0.025)→(0.505, 0.028, 0.025) | 0.179→0.179 | 1.00 / 3.333 | 121.632 | 134.074 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.032
- lateral_force_integral: None
- approach_alignment: 0.382
- goal_progress: 0.009
- terminal_score: 0.009
- phase_score: 0.238
- phase_breakdown.contact_score: 1.000
- phase_breakdown.push_goal_score: 0.000
- phase_breakdown.pre_contact_score: 0.188

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.146
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.009
- **Median Q (composite search score)**: -0.065
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.413


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.45333,"average_solve_count":150.0,"average_success_count":150.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_precontact.approach_speed":0.14297,"approach_to_precontact.arc_height":0.08462,"descend_to_contact_height.descend_speed":0.01163,"engage_contact.contact_force_threshold":4.48801,"engage_contact.engage_speed":0.04875,"push_to_goal.max_push_time":13.92616,"push_to_goal.push_distance":0.17873,"push_to_goal.push_speed":0.04048},"optimized_scores":{"best_composite_score":-0.06527,"best_fitness_score":0.14473,"best_task_score":0.00752},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":528.0,"contact_point_centroid":[0.52726,-0.01744,0.04645],"force_p95":205.6388,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":218.69013,"mean_force":185.86737,"phase_index":1.0,"phase_name":"descend_to_contact_height","phase_type":"descend","tcp_position_centroid":[0.51763,-0.01739,0.04586]},{"body_a":"attachment","body_b":"push_box","contact_count":3.0,"contact_point_centroid":[0.52444,-0.01808,0.04635],"force_p95":140.36904,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":142.14971,"mean_force":123.77158,"phase_index":3.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.52981,-0.01905,0.04338]},{"body_a":"world","body_b":"push_box","contact_count":2677.0,"contact_point_centroid":[0.5107,-0.01906,-0.00037],"force_p95":100.19369,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":133.8058,"mean_force":37.02295,"phase_index":1.0,"phase_name":"descend_to_contact_height","phase_type":"descend","tcp_position_centroid":[0.50905,-0.01423,0.0628]},{"body_a":"attachment","body_b":"push_box","contact_count":1.0,"contact_point_centroid":[0.5368,-0.01589,0.04538],"force_p95":110.04978,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":110.04978,"mean_force":110.04978,"phase_index":2.0,"phase_name":"engage_contact","phase_type":"contact","tcp_position_centroid":[0.52971,-0.01905,0.04331]},{"body_a":"world","body_b":"push_box","contact_count":6.0,"contact_point_centroid":[0.53333,-0.0204,-0.00093],"force_p95":74.23003,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":76.95027,"mean_force":62.43383,"phase_index":3.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.52981,-0.01905,0.04338]},{"body_a":"world","body_b":"push_box","contact_count":2.0,"contact_point_centroid":[0.53332,-0.0204,-0.00094],"force_p95":62.08401,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":62.80376,"mean_force":55.6063,"phase_index":2.0,"phase_name":"engage_contact","phase_type":"contact","tcp_position_centroid":[0.52971,-0.01905,0.04331]},{"body_a":"world","body_b":"push_box","contact_count":2864.0,"contact_point_centroid":[0.50458,-0.01881,-1e-05],"force_p95":0.24527,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_to_precontact","phase_type":"approach","tcp_position_centroid":[0.49985,0.04476,0.20873]}],"total_contact_groups":7},"final_pose_error":0.18331,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.51025,-0.02012,0.02495],"final_tcp_position":[0.52989,-0.01905,0.04348],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50458,-0.01881,0.025]},"peak_contact_force":218.69013,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":716.0,"n_steps_budget":780.0,"object_pos_end":[0.50458,-0.01881,0.02499],"object_pos_start":[0.50458,-0.01881,0.025],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_to_precontact","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2864.0,"raw_peak_contact_force":0.24534,"subtask_id":"pre_contact","tcp_end":[0.5013,-0.00567,0.12199],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.09794,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":794.0,"n_steps_budget":1000.0,"object_pos_end":[0.5102,-0.02011,0.02487],"object_pos_start":[0.50458,-0.01881,0.02499],"object_to_goal_dist_end":0.13029,"object_to_goal_dist_start":0.13127,"object_z_max":0.02592,"peak_contact_force":181.66312,"phase_name":"descend_to_contact_height","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3205.0,"raw_peak_contact_force":218.69013,"subtask_id":"pre_contact","tcp_end":[0.52971,-0.01905,0.04331],"tcp_start":[0.5013,-0.00567,0.12199],"tcp_to_object_dist_end":0.02686,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1.0,"n_steps_budget":780.0,"object_pos_end":[0.51024,-0.02012,0.02491],"object_pos_start":[0.5102,-0.02011,0.02487],"object_to_goal_dist_end":0.13029,"object_to_goal_dist_start":0.13029,"object_z_max":0.02487,"peak_contact_force":110.04978,"phase_name":"engage_contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":3.0,"raw_peak_contact_force":110.04978,"subtask_id":"contact","tcp_end":[0.52979,-0.01905,0.04335],"tcp_start":[0.52971,-0.01905,0.04331],"tcp_to_object_dist_end":0.02689,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.51022,-0.02012,0.02491],"object_pos_start":[0.51024,-0.02012,0.02491],"object_to_goal_dist_end":0.13029,"object_to_goal_dist_start":0.13029,"object_z_max":0.02491,"peak_contact_force":104.82202,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":9.0,"raw_peak_contact_force":142.14971,"subtask_id":"push_goal","tcp_end":[0.52989,-0.01905,0.04348],"tcp_start":[0.52984,-0.01905,0.04342],"tcp_to_object_dist_end":0.02707,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.92063,"average_solve_count":63.0,"average_success_count":63.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_precontact.approach_speed":0.12367,"approach_to_precontact.arc_height":0.04603,"descend_to_contact_height.descend_speed":0.07967,"engage_contact.contact_force_threshold":4.89791,"engage_contact.engage_speed":0.01499,"push_to_goal.max_push_time":10.10405,"push_to_goal.push_distance":0.29998,"push_to_goal.push_speed":0.03389},"optimized_scores":{"best_composite_score":-0.06623,"best_fitness_score":0.14377,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":131.0,"contact_point_centroid":[0.53049,0.04907,0.04666],"force_p95":250.77153,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":251.2178,"mean_force":216.67785,"phase_index":1.0,"phase_name":"descend_to_contact_height","phase_type":"descend","tcp_position_centroid":[0.51863,0.04933,0.04694]},{"body_a":"world","body_b":"push_box","contact_count":1520.0,"contact_point_centroid":[0.51603,0.04803,-0.00016],"force_p95":117.3802,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":134.82186,"mean_force":19.01797,"phase_index":1.0,"phase_name":"descend_to_contact_height","phase_type":"descend","tcp_position_centroid":[0.51226,0.05078,0.07734]},{"body_a":"attachment","body_b":"push_box","contact_count":3.0,"contact_point_centroid":[0.53902,0.04896,0.04549],"force_p95":131.86276,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":132.59465,"mean_force":126.59674,"phase_index":3.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.52708,0.04947,0.045]},{"body_a":"attachment","body_b":"push_box","contact_count":1.0,"contact_point_centroid":[0.53891,0.04894,0.04545],"force_p95":105.98811,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":105.98811,"mean_force":105.98811,"phase_index":2.0,"phase_name":"engage_contact","phase_type":"contact","tcp_position_centroid":[0.52696,0.04947,0.04494]},{"body_a":"world","body_b":"push_box","contact_count":9.0,"contact_point_centroid":[0.52667,0.056,-0.0008],"force_p95":70.10031,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":71.75581,"mean_force":42.64646,"phase_index":3.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.52708,0.04947,0.045]},{"body_a":"world","body_b":"push_box","contact_count":2.0,"contact_point_centroid":[0.54327,0.04764,-0.00119],"force_p95":53.43129,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":53.46247,"mean_force":53.1507,"phase_index":2.0,"phase_name":"engage_contact","phase_type":"contact","tcp_position_centroid":[0.52696,0.04947,0.04494]},{"body_a":"world","body_b":"push_box","contact_count":2556.0,"contact_point_centroid":[0.51501,0.04767,-1e-05],"force_p95":0.24528,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_to_precontact","phase_type":"approach","tcp_position_centroid":[0.50369,0.04996,0.22585]}],"total_contact_groups":7},"final_pose_error":0.30316,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.5195,0.04776,0.02382],"final_tcp_position":[0.5272,0.04948,0.04511],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.51501,0.04767,0.025]},"peak_contact_force":251.2178,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":639.0,"n_steps_budget":930.0,"object_pos_end":[0.51501,0.04767,0.02499],"object_pos_start":[0.51501,0.04767,0.025],"object_to_goal_dist_end":0.19823,"object_to_goal_dist_start":0.19823,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_to_precontact","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2556.0,"raw_peak_contact_force":0.24534,"subtask_id":"pre_contact","tcp_end":[0.51082,0.05395,0.13129],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.10656,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":388.0,"n_steps_budget":840.0,"object_pos_end":[0.51956,0.04777,0.02384],"object_pos_start":[0.51501,0.04767,0.02499],"object_to_goal_dist_end":0.19874,"object_to_goal_dist_start":0.19823,"object_z_max":0.02499,"peak_contact_force":240.2175,"phase_name":"descend_to_contact_height","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1651.0,"raw_peak_contact_force":251.2178,"subtask_id":"pre_contact","tcp_end":[0.52696,0.04947,0.04494],"tcp_start":[0.51082,0.05395,0.13129],"tcp_to_object_dist_end":0.02243,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.51953,0.04777,0.02381],"object_pos_start":[0.51956,0.04777,0.02384],"object_to_goal_dist_end":0.19873,"object_to_goal_dist_start":0.19874,"object_z_max":0.02384,"peak_contact_force":241.48381,"phase_name":"engage_contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":3.0,"raw_peak_contact_force":105.98811,"subtask_id":"contact","tcp_end":[0.52702,0.04947,0.04496],"tcp_start":[0.52696,0.04947,0.04494],"tcp_to_object_dist_end":0.0225,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.51951,0.04776,0.02379],"object_pos_start":[0.51953,0.04777,0.02381],"object_to_goal_dist_end":0.19873,"object_to_goal_dist_start":0.19873,"object_z_max":0.02381,"peak_contact_force":132.59465,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":12.0,"raw_peak_contact_force":132.59465,"subtask_id":"push_goal","tcp_end":[0.5272,0.04948,0.04511],"tcp_start":[0.52713,0.04948,0.04505],"tcp_to_object_dist_end":0.02273,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.91608,"average_solve_count":143.0,"average_success_count":143.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_precontact.approach_speed":0.03741,"approach_to_precontact.arc_height":0.09427,"descend_to_contact_height.descend_speed":0.05437,"engage_contact.contact_force_threshold":2.09923,"engage_contact.engage_speed":0.02951,"push_to_goal.max_push_time":8.63963,"push_to_goal.push_distance":0.22423,"push_to_goal.push_speed":0.05938},"optimized_scores":{"best_composite_score":-0.06389,"best_fitness_score":0.14611,"best_task_score":0.009},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":198.0,"contact_point_centroid":[0.49729,0.06269,0.04653],"force_p95":248.95512,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":253.23884,"mean_force":212.5977,"phase_index":1.0,"phase_name":"descend_to_contact_height","phase_type":"descend","tcp_position_centroid":[0.48657,0.06497,0.04644]},{"body_a":"world","body_b":"push_box","contact_count":1969.0,"contact_point_centroid":[0.48175,0.05888,-0.0002],"force_p95":118.56366,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":152.66918,"mean_force":21.7063,"phase_index":1.0,"phase_name":"descend_to_contact_height","phase_type":"descend","tcp_position_centroid":[0.47905,0.07526,0.0812]},{"body_a":"attachment","body_b":"push_box","contact_count":3.0,"contact_point_centroid":[0.51033,0.05734,0.04526],"force_p95":126.82472,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":127.47795,"mean_force":120.40091,"phase_index":3.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.4995,0.06286,0.04392]},{"body_a":"attachment","body_b":"push_box","contact_count":1.0,"contact_point_centroid":[0.50702,0.05356,0.04554],"force_p95":99.7625,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":99.7625,"mean_force":99.7625,"phase_index":2.0,"phase_name":"engage_contact","phase_type":"contact","tcp_position_centroid":[0.49937,0.06288,0.04389]},{"body_a":"world","body_b":"push_box","contact_count":6.0,"contact_point_centroid":[0.50806,0.05715,-0.00111],"force_p95":64.47085,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":64.54855,"mean_force":60.86944,"phase_index":3.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.4995,0.06286,0.04392]},{"body_a":"world","body_b":"push_box","contact_count":2.0,"contact_point_centroid":[0.50803,0.05716,-0.00114],"force_p95":59.434,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":60.45031,"mean_force":50.28716,"phase_index":2.0,"phase_name":"engage_contact","phase_type":"contact","tcp_position_centroid":[0.49937,0.06288,0.04389]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.47924,0.05847,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_to_precontact","phase_type":"approach","tcp_position_centroid":[0.49242,0.07742,0.25155]}],"total_contact_groups":7},"final_pose_error":0.23022,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.48583,0.05713,0.02531],"final_tcp_position":[0.49965,0.06286,0.04402],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47924,0.05847,0.025]},"peak_contact_force":253.23884,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47924,0.05847,0.02499],"object_pos_start":[0.47924,0.05847,0.025],"object_to_goal_dist_end":0.2095,"object_to_goal_dist_start":0.2095,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_to_precontact","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24534,"subtask_id":"pre_contact","tcp_end":[0.47885,0.09261,0.14304],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.12288,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":531.0,"n_steps_budget":1000.0,"object_pos_end":[0.48584,0.05715,0.02525],"object_pos_start":[0.47924,0.05847,0.02499],"object_to_goal_dist_end":0.20763,"object_to_goal_dist_start":0.2095,"object_z_max":0.02568,"peak_contact_force":212.1025,"phase_name":"descend_to_contact_height","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2167.0,"raw_peak_contact_force":253.23884,"subtask_id":"pre_contact","tcp_end":[0.49937,0.06288,0.04389],"tcp_start":[0.47885,0.09261,0.14304],"tcp_to_object_dist_end":0.02373,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.48583,0.05714,0.02525],"object_pos_start":[0.48584,0.05715,0.02525],"object_to_goal_dist_end":0.20762,"object_to_goal_dist_start":0.20763,"object_z_max":0.02525,"peak_contact_force":99.7625,"phase_name":"engage_contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":3.0,"raw_peak_contact_force":99.7625,"subtask_id":"contact","tcp_end":[0.49943,0.06287,0.04389],"tcp_start":[0.49937,0.06288,0.04389],"tcp_to_object_dist_end":0.02378,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.48582,0.05714,0.02525],"object_pos_start":[0.48583,0.05714,0.02525],"object_to_goal_dist_end":0.20762,"object_to_goal_dist_start":0.20762,"object_z_max":0.02528,"peak_contact_force":127.47795,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":9.0,"raw_peak_contact_force":127.47795,"subtask_id":"push_goal","tcp_end":[0.49965,0.06286,0.04402],"tcp_start":[0.49957,0.06286,0.04396],"tcp_to_object_dist_end":0.02401,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```