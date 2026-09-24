## Search State

- **Seed**: 6
- **Iteration**: 5 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 4 | approach → descend → push | arc_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | admittance_control | pose_tolerance | pose_tolerance | time_limit | 7 | 0.0972 | 0.38 | ✅ accepted |
| 3 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | pose_tolerance | force_exceeded | time_limit | 6 | 0.2279 | 0.00 | ❌ rejected |
| 2 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | time_limit | 5 | 0.5919 | 0.23 | ✅ accepted |
| 1 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | time_limit | 5 | 0.3042 | 0.00 | ✅ accepted |
| 0 | align → lift → push → approach → approach → descend → grasp | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | impedance_control | force_threshold_switch | position_control | admittance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 5 | -0.0821 | 0.00 | ✅ accepted |

**Proposal policy**: task_score is 0.38 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.097) — your mutation base

```yaml
skill: push_to_goal
dsl_version: 2
subtasks:
- id: reach_pre_contact
  anchor: object
  offset:
  - 0.0
  - 0.025
  - 0.05
  weight: 0.3
- id: contact_object
  anchor: object
  offset:
  - 0.0
  - 0.025
  - 0.0
  weight: 0.3
- id: push_to_goal
  target_entity: object
  metric: goal_progress
  weight: 0.4
phases:
- id: approach_1
  type: approach
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: push_box
    offset:
    - 0.0
    - 0.025
    - 0.05
    tolerance: 0.015
    orientation:
      mode: keep_current
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.12
      binds_to:
      - path: generator.speed
        mode: replace
    arc_height:
      type: scalar
      range:
      - 0.02
      - 0.07
      default: 0.04
      binds_to:
      - path: generator.arc_height
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat
  subtask_id: reach_pre_contact
- id: descend_1
  type: descend
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: push_box
    offset:
    - 0.0
    - 0.025
    - 0.0
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    descend_speed:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
    descend_tolerance:
      type: scalar
      range:
      - 0.005
      - 0.02
      default: 0.01
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat
  subtask_id: contact_object
- id: push_1
  type: push
  generator: linear_cartesian
  control: admittance_control
  termination: time_limit
  target:
    source: yaml
    anchor: task_object
    entity: push_box
    offset:
    - 0.0
    - 0.025
    - 0.0
    offset_along_axis:
      distance: 0.15
      axis: task_goal_direction
      mode: add_to_offset
      sign: positive
    orientation:
      mode: keep_current
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.02
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
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
    push_time:
      type: scalar
      range:
      - 1.0
      - 10.0
      default: 5.0
      binds_to:
      - path: duration.max_time
        mode: replace
  guards:
  - id: contact_maintained
    when: during_phase
    predicate: contact_detected
    threshold: 0.0
    on_failure: retry
  retries:
    max_attempts: 1
    strategy: offset_target
    offset:
    - 0.0
    - 0.005
    - 0.0
  subtask_id: push_to_goal

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, entity=push_box, offset=[0.0, 0.025, 0.05], tolerance=0.015
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
    - arc_height: status=consumed; consumers=generator.arc_height (replace)
  - retries: max_attempts=0, strategy=repeat
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, entity=push_box, offset=[0.0, 0.025, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (replace)
    - descend_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
  - retries: max_attempts=0, strategy=repeat
- **push_1** (`push`)
  - target: source=yaml, anchor=task_object, entity=push_box, offset=[0.0, 0.025, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.15, mode=add_to_offset, sign=positive}
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
    - push_time: status=consumed; consumers=duration.max_time (replace)
  - guards:
    - id=contact_maintained, when=during_phase, predicate=contact_detected, on_failure=retry, threshold=0.0
  - retries: max_attempts=1, strategy=offset_target, offset=[0.0, 0.005, 0.0]

## Design Metrics

- **Composite score**: 0.097
- **task_score** (E): 0.376
- **fitness_score**: 0.477  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.380

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2258 |
| descend_1 | 1.00 | 1.00 | 0.0496 |
| push_1 | 1.00 | 1.00 | 0.1501 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.496, 0.062, 0.086) | (0.500, 0.029, 0.025)→(0.500, 0.029, 0.025) | 0.180→0.180 | 1.00 / 4.000 | 213.380 | 229.101 |
| descend_1 | descend | 1.00 / step_budget | (0.496, 0.062, 0.086)→(0.520, 0.058, 0.043) | (0.500, 0.029, 0.025)→(0.505, 0.028, 0.025) | 0.180→0.179 | 1.00 / 3.000 | 0.263 | 180.916 |
| push_1 | push | 1.00 / time_limit | (0.520, 0.058, 0.043)→(0.500, -0.090, 0.027) | (0.505, 0.028, 0.025)→(0.492, -0.034, 0.026) | 0.179→0.116 | 1.00 / 4.000 | 0.245 | 0.245 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.544
- lateral_force_integral: None
- approach_alignment: 0.743
- goal_progress: 0.541
- terminal_score: 0.541
- phase_score: 0.612
- phase_breakdown.reach_pre_contact_score: 0.745
- phase_breakdown.contact_object_score: 0.579
- phase_breakdown.push_to_goal_score: 0.537

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.584
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.541
- **Median Q (composite search score)**: 0.088
- **K-run variance**: 0.0070
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.434


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.84615,"average_solve_count":104.0,"average_success_count":104.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.15291,"approach_1.arc_height":0.05057,"descend_1.descend_speed":0.03358,"descend_1.descend_tolerance":0.01967,"push_1.push_distance":0.27473,"push_1.push_speed":0.09878,"push_1.push_time":6.91724},"optimized_scores":{"best_composite_score":0.20375,"best_fitness_score":0.58375,"best_task_score":0.54121},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":278.0,"contact_point_centroid":[0.52225,0.00424,0.04558],"force_p95":225.38888,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":231.76355,"mean_force":199.2634,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51248,0.01057,0.04537]},{"body_a":"world","body_b":"push_box","contact_count":1301.0,"contact_point_centroid":[0.51117,-0.01483,-0.00043],"force_p95":193.40519,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":213.09213,"mean_force":43.14491,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50783,0.01195,0.05363]},{"body_a":"world","body_b":"push_box","contact_count":2270.0,"contact_point_centroid":[0.51387,-0.05861,-0.00046],"force_p95":148.16093,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":161.75181,"mean_force":44.98513,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51705,-0.07596,0.04027]},{"body_a":"attachment","body_b":"push_box","contact_count":772.0,"contact_point_centroid":[0.52993,-0.04196,0.04602],"force_p95":157.18783,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":160.75852,"mean_force":130.67962,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52372,-0.04807,0.04527]},{"body_a":"world","body_b":"push_box","contact_count":2144.0,"contact_point_centroid":[0.50458,-0.01881,-1e-05],"force_p95":0.24529,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49981,0.03577,0.19507]}],"total_contact_groups":5},"final_pose_error":0.11792,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.49738,-0.08983,0.02499],"final_tcp_position":[0.50009,-0.15185,0.02783],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50458,-0.01881,0.025]},"peak_contact_force":231.76355,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":536.0,"n_steps_budget":930.0,"object_pos_end":[0.50458,-0.01881,0.02499],"object_pos_start":[0.50458,-0.01881,0.025],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.025,"peak_contact_force":216.82228,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1579.0,"raw_peak_contact_force":231.76355,"subtask_id":"reach_pre_contact","tcp_end":[0.50098,0.01714,0.08416],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.06933,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":394.0,"n_steps_budget":1000.0,"object_pos_end":[0.50995,-0.02029,0.02454],"object_pos_start":[0.50458,-0.01881,0.02499],"object_to_goal_dist_end":0.13009,"object_to_goal_dist_start":0.13127,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3042.0,"raw_peak_contact_force":161.75181,"subtask_id":"contact_object","tcp_end":[0.52488,0.00879,0.04306],"tcp_start":[0.50098,0.01714,0.08416],"tcp_to_object_dist_end":0.03757,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49738,-0.08983,0.02499],"object_pos_start":[0.50995,-0.02029,0.02454],"object_to_goal_dist_end":0.06023,"object_to_goal_dist_start":0.13009,"object_z_max":0.03539,"peak_contact_force":0.24525,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2144.0,"raw_peak_contact_force":0.24534,"subtask_id":"push_to_goal","tcp_end":[0.50009,-0.15185,0.02783],"tcp_start":[0.52488,0.00879,0.04306],"tcp_to_object_dist_end":0.06214,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.63248,"average_solve_count":117.0,"average_success_count":117.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.10547,"approach_1.arc_height":0.0601,"descend_1.descend_speed":0.03786,"descend_1.descend_tolerance":0.01231,"push_1.push_distance":0.29538,"push_1.push_speed":0.0976,"push_1.push_time":5.18297},"optimized_scores":{"best_composite_score":0.08757,"best_fitness_score":0.46757,"best_task_score":0.35222},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":250.0,"contact_point_centroid":[0.53167,0.07148,0.04571],"force_p95":228.03943,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":232.55354,"mean_force":196.61459,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52146,0.07706,0.04567]},{"body_a":"world","body_b":"push_box","contact_count":1227.0,"contact_point_centroid":[0.52131,0.05196,-0.0004],"force_p95":195.42561,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":212.98328,"mean_force":40.58915,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51671,0.0776,0.05491]},{"body_a":"attachment","body_b":"push_box","contact_count":789.0,"contact_point_centroid":[0.53906,0.02368,0.04624],"force_p95":156.94911,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":159.93226,"mean_force":127.14984,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5301,0.02015,0.04566]},{"body_a":"world","body_b":"push_box","contact_count":2322.0,"contact_point_centroid":[0.5232,0.00959,-0.00045],"force_p95":142.03581,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":155.94018,"mean_force":43.75902,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52382,-0.0056,0.04116]},{"body_a":"world","body_b":"push_box","contact_count":2552.0,"contact_point_centroid":[0.51501,0.04767,-1e-05],"force_p95":0.24528,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50357,0.06974,0.20786]}],"total_contact_groups":5},"final_pose_error":0.13988,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50705,-0.02178,0.02499],"final_tcp_position":[0.5059,-0.08241,0.02871],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.51501,0.04767,0.025]},"peak_contact_force":232.55354,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":638.0,"n_steps_budget":1000.0,"object_pos_end":[0.51501,0.04767,0.02499],"object_pos_start":[0.51501,0.04767,0.025],"object_to_goal_dist_end":0.19823,"object_to_goal_dist_start":0.19823,"object_z_max":0.025,"peak_contact_force":221.77572,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1477.0,"raw_peak_contact_force":232.55354,"subtask_id":"reach_pre_contact","tcp_end":[0.51057,0.08083,0.08631],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.06986,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":369.0,"n_steps_budget":1000.0,"object_pos_end":[0.52019,0.04749,0.02447],"object_pos_start":[0.51501,0.04767,0.02499],"object_to_goal_dist_end":0.19852,"object_to_goal_dist_start":0.19823,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3111.0,"raw_peak_contact_force":159.93226,"subtask_id":"contact_object","tcp_end":[0.53263,0.07721,0.04318],"tcp_start":[0.51057,0.08083,0.08631],"tcp_to_object_dist_end":0.03726,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50705,-0.02178,0.02499],"object_pos_start":[0.52019,0.04749,0.02447],"object_to_goal_dist_end":0.12841,"object_to_goal_dist_start":0.19852,"object_z_max":0.0354,"peak_contact_force":0.24525,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2552.0,"raw_peak_contact_force":0.24534,"subtask_id":"push_to_goal","tcp_end":[0.5059,-0.08241,0.02871],"tcp_start":[0.53263,0.07721,0.04318],"tcp_to_object_dist_end":0.06075,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.39683,"average_solve_count":126.0,"average_success_count":126.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.1537,"approach_1.arc_height":0.05182,"descend_1.descend_speed":0.02194,"descend_1.descend_tolerance":0.0157,"push_1.push_distance":0.12275,"push_1.push_speed":0.08102,"push_1.push_time":1.72539},"optimized_scores":{"best_composite_score":0.00016,"best_fitness_score":0.38016,"best_task_score":0.23355},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":397.0,"contact_point_centroid":[0.499,0.08055,0.04553],"force_p95":211.42242,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":222.9846,"mean_force":194.70525,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49014,0.08735,0.04515]},{"body_a":"attachment","body_b":"push_box","contact_count":880.0,"contact_point_centroid":[0.50669,0.03661,0.04556],"force_p95":205.21073,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":221.06253,"mean_force":155.14797,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50894,0.03547,0.04379]},{"body_a":"world","body_b":"push_box","contact_count":1741.0,"contact_point_centroid":[0.48635,0.0632,-0.00046],"force_p95":182.67653,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":206.73619,"mean_force":44.8558,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.4856,0.08731,0.05324]},{"body_a":"world","body_b":"push_box","contact_count":1780.0,"contact_point_centroid":[0.50123,0.03594,-0.00078],"force_p95":160.51417,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":173.94826,"mean_force":77.43491,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50866,0.03819,0.04394]},{"body_a":"world","body_b":"push_box","contact_count":2284.0,"contact_point_centroid":[0.47924,0.05847,-1e-05],"force_p95":0.24528,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48973,0.06882,0.20809]}],"total_contact_groups":5},"final_pose_error":0.00496,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.47242,0.00818,0.02684],"final_tcp_position":[0.49388,-0.03442,0.0241],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47924,0.05847,0.025]},"peak_contact_force":222.9846,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":571.0,"n_steps_budget":990.0,"object_pos_end":[0.47924,0.05847,0.02499],"object_pos_start":[0.47924,0.05847,0.025],"object_to_goal_dist_end":0.2095,"object_to_goal_dist_start":0.2095,"object_z_max":0.025,"peak_contact_force":201.54266,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2138.0,"raw_peak_contact_force":222.9846,"subtask_id":"reach_pre_contact","tcp_end":[0.47785,0.08907,0.08872],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07071,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":534.0,"n_steps_budget":1000.0,"object_pos_end":[0.48451,0.05808,0.0245],"object_pos_start":[0.47924,0.05847,0.02499],"object_to_goal_dist_end":0.20866,"object_to_goal_dist_start":0.2095,"object_z_max":0.02499,"peak_contact_force":0.29846,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2660.0,"raw_peak_contact_force":221.06253,"subtask_id":"contact_object","tcp_end":[0.50315,0.08836,0.04331],"tcp_start":[0.47785,0.08907,0.08872],"tcp_to_object_dist_end":0.04023,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":919.0,"n_steps_budget":990.0,"object_pos_end":[0.47242,0.00818,0.02684],"object_pos_start":[0.48451,0.05808,0.0245],"object_to_goal_dist_end":0.16057,"object_to_goal_dist_start":0.20866,"object_z_max":0.03692,"peak_contact_force":0.24525,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2284.0,"raw_peak_contact_force":0.24534,"subtask_id":"push_to_goal","tcp_end":[0.49388,-0.03442,0.0241],"tcp_start":[0.50315,0.08836,0.04331],"tcp_to_object_dist_end":0.04777,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
```