## Search State

- **Seed**: 6
- **Iteration**: 12 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 11 | approach → descend → grasp → lift → approach → descend → release → retract | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 16 | -0.3662 | 0.30 | ❌ rejected |
| 10 | approach → descend → grasp → lift → approach → release → retract | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 12 | -0.1459 | 0.28 | ❌ rejected |
| 9 | approach → descend → grasp → lift → approach → descend → release → retract | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 14 | -0.2636 | 0.31 | ❌ rejected |
| 8 | approach → descend → grasp → lift → approach | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 9 | 0.2855 | 0.73 | ✅ accepted |
| 7 | approach → descend → grasp → lift → approach → release → retract | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 12 | -0.1355 | 0.30 | ✅ accepted |

**Proposal policy**: task_score is 0.30 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

- Task name: grasp_place
- Frozen realised-scene SHA-256: `584133b5261cffac0dd4282704ff39e97bf4d452e60b02507679bbdea5a4de22`
- Frozen object start: [0.5038164351471943, -0.015672913018666156, 0.03]
- Frozen task target: [0.5869067239795378, 0.18744967655878825, 0.24811674852797]
- Goal object position: (0.5869067239795378, 0.18744967655878825, 0.24811674852797)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.5869067239795378, 0.18744967655878825, 0.24811674852797)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.5038164351471943, -0.015672913018666156, 0.03)
- Goal tolerance: 0.02 m
- Expressivity sigma: 0.15 m
- Expressivity threshold: 0.3
- Force limit: 20.0 N
- Robot initial TCP position: (0.5, 0.0, 0.3)
- Robot initial gripper state: **open** (gripper starts fully open; ensure a `grasp`/`force_grasp` phase closes it before lifting)
- Phase navigation guidance: the task `phase_target_map` may provide internal predefined TCP waypoint aliases / semantic phase ids. These names are not DSL phase types and are intentionally not enumerated here to avoid confusing ids with types. Phase `id` may be semantic, but phase `type` must be exactly one of the DSL enum values listed in the prompt.
- Primary evaluation target: **final object-to-realised-airborne-3D-target proximity. Grasp/lift signals are optimiser fitness diagnostics only; they do not gate the canonical task_score.**

## Scene Entities

robot:
  model: panda_full
  tcp_site: attachment_site
  gripper: franka_hand
  tcp_initial_world: [0.5, 0, 0.3]
objects:
  - name: grasp_target
    role: manipulated_object
    dynamics: free
    geometry: box
    dimensions_m: [0.04, 0.04, 0.06]
    mass_kg: 0.05
  - name: placement_surface
    role: goal_area
    dynamics: static
    geometry: point
task_landmarks:
  frozen_object_start: [0.5038, -0.0157, 0.03]
  frozen_task_target: [0.5869, 0.1874, 0.2481]
  frozen_object_starts: {'grasp_target': [0.5038164351471943, -0.015672913018666156, 0.03]}
  frozen_targets: {'place_target': [0.5869067239795378, 0.18744967655878825, 0.24811674852797]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: 584133b5261cffac0dd4282704ff39e97bf4d452e60b02507679bbdea5a4de22

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
| `object` | offset from object initial position (0.5038164351471943, -0.015672913018666156, 0.03) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5869067239795378, 0.18744967655878825, 0.24811674852797) | final destination targets |
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

## Current Skill (Q=-0.366) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: approach_pre_grasp
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.12
  weight: 0.2
- id: reach_grasp
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.04
  weight: 0.2
- id: lift_clearance
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.15
  weight: 0.2
- id: reach_goal
  offset:
  - 0.0
  - 0.0
  - 0.035
  weight: 0.4
phases:
- id: approach_above
  type: approach
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.12
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.08
      - 0.18
      default: 0.12
      binds_to:
      - path: target.offset.z
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
    speed:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: approach_pre_grasp
- id: descend_to_grasp
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.04
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    descend_offset:
      type: scalar
      range:
      - 0.02
      - 0.08
      default: 0.04
      binds_to:
      - path: target.offset.z
        mode: replace
    speed:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_grasp
- id: grasp_close
  type: grasp
  control: position_control
  termination: time_limit
  end_effector_action: force_grasp
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
  parameters:
    grasp_duration:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: duration.max_time
        mode: replace
  guards:
  - id: check_grasp
    when: after_phase
    predicate: bilateral_grasp
    threshold: 0.5
    on_failure: retry
  retries:
    max_attempts: 1
    strategy: repeat
- id: lift_object
  type: lift
  generator: linear_cartesian
  control: position_control
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
      axis: world_z
      mode: add_to_offset
      sign: positive
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    lift_distance:
      type: scalar
      range:
      - 0.1
      - 0.35
      default: 0.2
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    speed:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: lift_clearance
- id: transport_to_goal
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.035
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    transport_speed:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_goal

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_above** (`approach`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.12], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
    - arc_height: status=consumed; consumers=generator.arc_height (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_grasp** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.04], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_offset: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **grasp_close** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings:
    - grasp_duration: status=consumed; consumers=duration.max_time (replace)
  - guards:
    - id=check_grasp, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=0.5
  - retries: max_attempts=1, strategy=repeat
- **lift_object** (`lift`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.2, mode=add_to_offset, sign=positive}, tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **transport_to_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.035], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - transport_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: -0.366
- **task_score** (E): 0.301
- **fitness_score**: 0.614  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.980

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_above | 1.00 | 1.00 | 0.1469 |
| descend_to_grasp | 1.00 | 1.00 | 0.1066 |
| grasp_close | 1.00 | 1.00 | 0.0117 |
| lift_object | 1.00 | 1.00 | 0.2430 |
| transport_to_goal | 1.00 | 1.00 | 0.2044 |
| descend_to_goal | 1.00 | 1.00 | 0.1023 |
| release_object | 1.00 | 1.00 | 0.0203 |
| retract_from_goal | 1.00 | 1.00 | 0.0957 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_above | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.496, 0.033, 0.161) | (0.500, 0.024, 0.030)→(0.500, 0.024, 0.026) | 0.269→0.271 | 1.00 / 4.000 | 27.638 | 0.138 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.496, 0.033, 0.161)→(0.495, 0.025, 0.055) | (0.500, 0.024, 0.026)→(0.500, 0.024, 0.026) | 0.271→0.271 | 1.00 / 4.000 | 13.273 | 0.123 |
| grasp_close | grasp | 1.00 / step_budget | (0.495, 0.025, 0.055)→(0.487, 0.025, 0.046) | (0.500, 0.024, 0.026)→(0.500, 0.025, 0.026) | 0.271→0.271 | 1.00 / 44.667 | 0.167 | 0.194 |
| lift_object | lift | 1.00 / step_budget | (0.487, 0.025, 0.046)→(0.484, 0.024, 0.289) | (0.500, 0.025, 0.026)→(0.490, 0.024, 0.263) | 0.271→0.218 | 1.00 / 38.000 | 0.076 | 0.428 |
| transport_to_goal | approach | 1.00 / step_budget | (0.484, 0.024, 0.289)→(0.589, 0.182, 0.359) | (0.490, 0.024, 0.263)→(0.574, 0.164, 0.026) | 0.218→0.188 | 1.00 / 8.333 | 94301.549 | 2.752 |
| descend_to_goal | descend | 1.00 / step_budget | (0.589, 0.182, 0.359)→(0.595, 0.193, 0.257) | (0.574, 0.164, 0.026)→(0.574, 0.162, 0.026) | 0.188→0.188 | 1.00 / 8.333 | 0.123 | 0.199 |
| release_object | release | 1.00 / step_budget | (0.595, 0.193, 0.257)→(0.591, 0.191, 0.277) | (0.574, 0.162, 0.026)→(0.574, 0.162, 0.026) | 0.188→0.188 | 1.00 / 4.000 | 0.123 | 0.123 |
| retract_from_goal | retract | 1.00 / step_budget | (0.591, 0.191, 0.277)→(0.590, 0.191, 0.373) | (0.574, 0.162, 0.026)→(0.574, 0.162, 0.026) | 0.188→0.188 | 1.00 / 4.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.442
- phase_score: 0.294
- phase_breakdown.approach_pre_grasp_score: 0.586
- phase_breakdown.reach_goal_score: 0.039
- phase_breakdown.reach_grasp_score: 0.722
- phase_breakdown.lift_clearance_score: 0.101
- grasp_place_fitness: 0.685

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.685
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.442
- **Median Q (composite search score)**: -0.395
- **K-run variance**: 0.0026
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.339


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `daf90631fcbaf423e19452d0c9b90b9715013985cc94ef12ca0cd881e96195aa`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `94660347aa4f41f6801e53bd449f8df59691da8bebfa4fef4947a3513fe04781`; realized-scene SHA-256: `584133b5261cffac0dd4282704ff39e97bf4d452e60b02507679bbdea5a4de22`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50382,-0.01567,0.03]},{"name":"goal","value":[0.58691,0.18745,0.24812]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.50382,-0.01567,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.58691,0.18745,0.24812]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.00262,"average_solve_count":382.0,"average_success_count":382.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.approach_height":0.14483,"approach_above.arc_height":0.04939,"approach_above.speed":0.05876,"descend_to_goal.descend_goal_offset":0.05305,"descend_to_goal.speed":0.02676,"descend_to_grasp.descend_offset":0.02001,"descend_to_grasp.speed":0.01994,"grasp_close.grasp_duration":0.12003,"lift_object.lift_distance":0.27593,"lift_object.speed":0.02078,"release_object.release_duration":0.11868,"retract_from_goal.retract_distance":0.13859,"retract_from_goal.speed":0.19106,"transport_to_goal.arc_height":0.13676,"transport_to_goal.speed":0.16754,"transport_to_goal.transport_height":0.1007},"optimized_scores":{"best_composite_score":-0.40851,"best_fitness_score":0.57149,"best_task_score":0.21643},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":299.0,"contact_point_centroid":[0.57426,0.127,-0.00805],"force_p95":1.47734,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.74785,"mean_force":0.35788,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.57263,0.15887,0.38098]},{"body_a":"world","body_b":"grasp_target","contact_count":87.0,"contact_point_centroid":[0.50014,-0.0142,-0.00149],"force_p95":0.39959,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.42403,"mean_force":0.14926,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48988,-0.01457,0.04691]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5232.0,"contact_point_centroid":[0.5047,0.03248,0.35875],"force_p95":0.13696,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33945,"mean_force":0.08345,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.50148,0.01376,0.36031]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16538.0,"contact_point_centroid":[0.48779,0.00465,0.17251],"force_p95":0.07917,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2719,"mean_force":0.05603,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48769,-0.01452,0.17122]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18581.0,"contact_point_centroid":[0.48778,-0.03361,0.16991],"force_p95":0.07637,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2652,"mean_force":0.05095,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48768,-0.01452,0.16853]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5844.0,"contact_point_centroid":[0.5052,-0.0037,0.35928],"force_p95":0.12256,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21077,"mean_force":0.07394,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.502,0.01481,0.36071]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50384,-0.01558,-0.00209],"force_p95":0.1499,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.2047,"mean_force":0.12979,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.4921,-0.0146,0.047]},{"body_a":"world","body_b":"grasp_target","contact_count":636.0,"contact_point_centroid":[0.57583,0.13035,-0.00195],"force_p95":0.18002,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.20209,"mean_force":0.12487,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.5809,0.17822,0.33542]},{"body_a":"world","body_b":"grasp_target","contact_count":2292.0,"contact_point_centroid":[0.50382,-0.01567,-0.00194],"force_p95":0.13153,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12284,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.49903,0.02262,0.23214]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4342.0,"contact_point_centroid":[0.4915,0.00468,0.04763],"force_p95":0.07568,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12716,"mean_force":0.04972,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.49095,-0.01458,0.04576]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.57584,0.1304,-0.00199],"force_p95":0.12309,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12382,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.58082,0.18226,0.30978]},{"body_a":"world","body_b":"grasp_target","contact_count":1704.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.49801,-0.01072,0.11324]},{"body_a":"world","body_b":"grasp_target","contact_count":1604.0,"contact_point_centroid":[0.57584,0.1304,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_from_goal","phase_type":"retract","tcp_position_centroid":[0.57957,0.18147,0.38806]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5442.0,"contact_point_centroid":[0.4918,-0.03371,0.04823],"force_p95":0.06715,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.06894,"mean_force":0.04061,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.49096,-0.01458,0.04577]},{"body_a":"left_finger","body_b":"right_finger","contact_count":297.0,"contact_point_centroid":[0.5748,0.16256,0.37949],"force_p95":0.01447,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01552,"mean_force":0.01121,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.57439,0.16256,0.3771]},{"body_a":"left_finger","body_b":"right_finger","contact_count":677.0,"contact_point_centroid":[0.58122,0.17824,0.33765],"force_p95":0.01098,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01257,"mean_force":0.01048,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.58091,0.17822,0.3354]}],"total_contact_groups":17},"final_pose_error":0.01984,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.57584,0.1304,0.02602],"final_tcp_position":[0.5803,0.18161,0.4483],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":273015.30202,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":574.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2292.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_pre_grasp","tcp_end":[0.49996,-0.00696,0.17196],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.14626,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":426.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1704.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_grasp","tcp_end":[0.49887,-0.01466,0.05444],"tcp_start":[0.49996,-0.00696,0.17196],"tcp_to_object_dist_end":0.02886,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50376,-0.01483,0.02565],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31197,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.14818,"phase_name":"grasp_close","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11584.0,"raw_peak_contact_force":0.2047,"tcp_end":[0.49092,-0.01458,0.04573],"tcp_start":[0.49887,-0.01466,0.05444],"tcp_to_object_dist_end":0.02383,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":886.0,"n_steps_budget":1000.0,"object_pos_end":[0.4942,-0.01476,0.27599],"object_pos_start":[0.50376,-0.01483,0.02565],"object_to_goal_dist_end":0.22419,"object_to_goal_dist_start":0.31197,"object_z_max":0.27572,"peak_contact_force":0.07671,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":35206.0,"raw_peak_contact_force":0.42403,"subtask_id":"lift_clearance","tcp_end":[0.48862,-0.01454,0.30192],"tcp_start":[0.49092,-0.01458,0.04573],"tcp_to_object_dist_end":0.02653,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":669.0,"n_steps_budget":1000.0,"object_pos_end":[0.57533,0.12798,0.0275],"object_pos_start":[0.4942,-0.01476,0.27599],"object_to_goal_dist_end":0.22879,"object_to_goal_dist_start":0.22419,"object_z_max":0.37541,"peak_contact_force":273015.30202,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":11672.0,"raw_peak_contact_force":2.74785,"subtask_id":"reach_goal","tcp_end":[0.57974,0.17402,0.36157],"tcp_start":[0.48862,-0.01454,0.30192],"tcp_to_object_dist_end":0.33726,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":159.0,"n_steps_budget":1000.0,"object_pos_end":[0.57581,0.1303,0.02602],"object_pos_start":[0.57533,0.12798,0.0275],"object_to_goal_dist_end":0.2296,"object_to_goal_dist_start":0.22879,"object_z_max":0.0275,"peak_contact_force":0.12391,"phase_name":"descend_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1313.0,"raw_peak_contact_force":0.20209,"tcp_end":[0.58317,0.18315,0.30926],"tcp_start":[0.57974,0.17402,0.36157],"tcp_to_object_dist_end":0.28822,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.57584,0.1304,0.02602],"object_pos_start":[0.57581,0.1303,0.02602],"object_to_goal_dist_end":0.22957,"object_to_goal_dist_start":0.2296,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1021.0,"raw_peak_contact_force":0.12382,"tcp_end":[0.58016,0.18189,0.32955],"tcp_start":[0.58317,0.18315,0.30926],"tcp_to_object_dist_end":0.3079,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":401.0,"n_steps_budget":600.0,"object_pos_end":[0.57584,0.1304,0.02602],"object_pos_start":[0.57584,0.1304,0.02602],"object_to_goal_dist_end":0.22957,"object_to_goal_dist_start":0.22957,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"retract_from_goal","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1604.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.5803,0.18161,0.4483],"tcp_start":[0.58016,0.18189,0.32955],"tcp_to_object_dist_end":0.4254,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `fe7e0be33c0bb4db9d2bbbb069b6113d0e5a69a675a0d70bc1f582243e99e3cf`; realized-scene SHA-256: `8a4edc50bf1a337961423afe5cdf858aa28147f944f8fcd30a2ce1adc75d1bd6`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.51251,0.03972,0.03]},{"name":"goal","value":[0.62757,0.17252,0.14502]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.51251,0.03972,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.62757,0.17252,0.14502]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.27692,"average_solve_count":390.0,"average_success_count":390.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.approach_height":0.1451,"approach_above.arc_height":0.06452,"approach_above.speed":0.05955,"descend_to_goal.descend_goal_offset":0.04552,"descend_to_goal.speed":0.03556,"descend_to_grasp.descend_offset":0.02001,"descend_to_grasp.speed":0.03035,"grasp_close.grasp_duration":0.25267,"lift_object.lift_distance":0.26776,"lift_object.speed":0.03484,"release_object.release_duration":0.13854,"retract_from_goal.retract_distance":0.12702,"retract_from_goal.speed":0.16684,"transport_to_goal.arc_height":0.1256,"transport_to_goal.speed":0.13285,"transport_to_goal.transport_height":0.1861},"optimized_scores":{"best_composite_score":-0.29503,"best_fitness_score":0.68497,"best_task_score":0.4424},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":218.0,"contact_point_centroid":[0.59982,0.16602,-0.00937],"force_p95":1.4646,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.77908,"mean_force":0.43286,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.60833,0.15319,0.35168]},{"body_a":"world","body_b":"grasp_target","contact_count":85.0,"contact_point_centroid":[0.5087,0.03944,-0.00142],"force_p95":0.39214,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.40746,"mean_force":0.15012,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49839,0.03953,0.04649]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4509.0,"contact_point_centroid":[0.51617,0.03907,0.33349],"force_p95":0.13616,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32474,"mean_force":0.07823,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.51404,0.05773,0.33486]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17379.0,"contact_point_centroid":[0.49641,0.05845,0.1661],"force_p95":0.07712,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27289,"mean_force":0.0529,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49612,0.03934,0.16428]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16731.0,"contact_point_centroid":[0.4959,0.0202,0.16913],"force_p95":0.07855,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27287,"mean_force":0.05444,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49613,0.03934,0.1676]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4724.0,"contact_point_centroid":[0.51903,0.07862,0.3355],"force_p95":0.12382,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2182,"mean_force":0.07551,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.5163,0.06001,0.337]},{"body_a":"world","body_b":"grasp_target","contact_count":1576.0,"contact_point_centroid":[0.59992,0.16636,-0.00195],"force_p95":0.13672,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15285,"mean_force":0.11993,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.61843,0.16504,0.26928]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.5125,0.03976,-0.00202],"force_p95":0.12954,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.14799,"mean_force":0.12477,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.5006,0.03971,0.04677]},{"body_a":"world","body_b":"grasp_target","contact_count":2876.0,"contact_point_centroid":[0.51251,0.03972,-0.00195],"force_p95":0.12873,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.1228,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.50132,0.05428,0.25421]},{"body_a":"world","body_b":"grasp_target","contact_count":1648.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.50648,0.04446,0.11451]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.59992,0.16635,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.61886,0.16883,0.1984]},{"body_a":"world","body_b":"grasp_target","contact_count":1616.0,"contact_point_centroid":[0.59992,0.16635,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":7.0,"phase_name":"retract_from_goal","phase_type":"retract","tcp_position_centroid":[0.61543,0.16758,0.27102]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4668.0,"contact_point_centroid":[0.49986,0.05887,0.04844],"force_p95":0.06892,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09043,"mean_force":0.0466,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.49945,0.03962,0.04549]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5056.0,"contact_point_centroid":[0.50015,0.02048,0.04776],"force_p95":0.06574,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08185,"mean_force":0.04314,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.49945,0.03962,0.04549]},{"body_a":"left_finger","body_b":"right_finger","contact_count":138.0,"contact_point_centroid":[0.61205,0.15648,0.34986],"force_p95":0.01579,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01625,"mean_force":0.0122,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.6115,0.15646,0.34757]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1672.0,"contact_point_centroid":[0.61885,0.16507,0.27156],"force_p95":0.01101,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01283,"mean_force":0.0105,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.61843,0.16504,0.26927]}],"total_contact_groups":17},"final_pose_error":0.01986,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.59992,0.16635,0.02602],"final_tcp_position":[0.61584,0.16763,0.32504],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":9747.27204,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":720.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":41.47434,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2876.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_pre_grasp","tcp_end":[0.50823,0.04872,0.17478],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.14909,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":412.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1648.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_grasp","tcp_end":[0.5075,0.04032,0.05452],"tcp_start":[0.50823,0.04872,0.17478],"tcp_to_object_dist_end":0.02895,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51242,0.03971,0.02589],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21235,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.13037,"phase_name":"grasp_close","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11524.0,"raw_peak_contact_force":0.14799,"tcp_end":[0.49942,0.03962,0.04545],"tcp_start":[0.5075,0.04032,0.05452],"tcp_to_object_dist_end":0.02349,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":868.0,"n_steps_budget":1000.0,"object_pos_end":[0.50267,0.03955,0.26815],"object_pos_start":[0.51242,0.03971,0.02589],"object_to_goal_dist_end":0.2201,"object_to_goal_dist_start":0.21235,"object_z_max":0.26789,"peak_contact_force":0.07569,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":34195.0,"raw_peak_contact_force":0.40746,"subtask_id":"lift_clearance","tcp_end":[0.49703,0.0394,0.29357],"tcp_start":[0.49942,0.03962,0.04545],"tcp_to_object_dist_end":0.02604,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":551.0,"n_steps_budget":1000.0,"object_pos_end":[0.60061,0.17102,0.02383],"object_pos_start":[0.50267,0.03955,0.26815],"object_to_goal_dist_end":0.12416,"object_to_goal_dist_start":0.2201,"object_z_max":0.33914,"peak_contact_force":9747.27204,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":9589.0,"raw_peak_contact_force":2.77908,"subtask_id":"reach_goal","tcp_end":[0.61551,0.16069,0.34107],"tcp_start":[0.49703,0.0394,0.29357],"tcp_to_object_dist_end":0.31776,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":394.0,"n_steps_budget":1000.0,"object_pos_end":[0.59992,0.16635,0.02602],"object_pos_start":[0.60061,0.17102,0.02383],"object_to_goal_dist_end":0.12233,"object_to_goal_dist_start":0.12416,"object_z_max":0.02717,"peak_contact_force":0.12263,"phase_name":"descend_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3248.0,"raw_peak_contact_force":0.15285,"tcp_end":[0.62289,0.1701,0.1988],"tcp_start":[0.61551,0.16069,0.34107],"tcp_to_object_dist_end":0.17435,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.59992,0.16635,0.02602],"object_pos_start":[0.59992,0.16635,0.02602],"object_to_goal_dist_end":0.12233,"object_to_goal_dist_start":0.12233,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1022.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.61747,0.16833,0.21779],"tcp_start":[0.62289,0.1701,0.1988],"tcp_to_object_dist_end":0.19259,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":404.0,"n_steps_budget":600.0,"object_pos_end":[0.59992,0.16635,0.02602],"object_pos_start":[0.59992,0.16635,0.02602],"object_to_goal_dist_end":0.12233,"object_to_goal_dist_start":0.12233,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"retract_from_goal","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1616.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.61584,0.16763,0.32504],"tcp_start":[0.61747,0.16833,0.21779],"tcp_to_object_dist_end":0.29944,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `28f75809d7d1d0a11ca1a36dd459ad950e5a80b6bae34006f33ac9620425f5e5`; realized-scene SHA-256: `f44a4a1356de6cb8b5dec75995af4354e38cafd01c85526c1c2a33c8dd2e5b1c`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.4827,0.04873,0.03]},{"name":"goal","value":[0.58187,0.22885,0.23048]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.4827,0.04873,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.58187,0.22885,0.23048]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.4159,"average_solve_count":327.0,"average_success_count":327.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.approach_height":0.10583,"approach_above.arc_height":0.09002,"approach_above.speed":0.0539,"descend_to_goal.descend_goal_offset":0.0252,"descend_to_goal.speed":0.03413,"descend_to_grasp.descend_offset":0.02005,"descend_to_grasp.speed":0.03793,"grasp_close.grasp_duration":0.27776,"lift_object.lift_distance":0.24422,"lift_object.speed":0.05749,"release_object.release_duration":0.17147,"retract_from_goal.retract_distance":0.08096,"retract_from_goal.speed":0.15251,"transport_to_goal.arc_height":0.05004,"transport_to_goal.speed":0.14802,"transport_to_goal.transport_height":0.14612},"optimized_scores":{"best_composite_score":-0.39513,"best_fitness_score":0.58487,"best_task_score":0.24412},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":305.0,"contact_point_centroid":[0.54704,0.19708,-0.0076],"force_p95":1.42066,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.73037,"mean_force":0.36986,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.55667,0.18946,0.37768]},{"body_a":"world","body_b":"grasp_target","contact_count":80.0,"contact_point_centroid":[0.48013,0.04867,-0.00136],"force_p95":0.3571,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.45146,"mean_force":0.11912,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46917,0.04878,0.04784]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4466.0,"contact_point_centroid":[0.48594,0.05667,0.31287],"force_p95":0.14192,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33967,"mean_force":0.0832,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.48327,0.07527,0.31433]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":14440.0,"contact_point_centroid":[0.46751,0.06767,0.1585],"force_p95":0.08077,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2914,"mean_force":0.05573,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46697,0.04855,0.15708]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14385.0,"contact_point_centroid":[0.46686,0.02945,0.15861],"force_p95":0.08227,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26056,"mean_force":0.05598,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46696,0.04855,0.15754]},{"body_a":"world","body_b":"grasp_target","contact_count":1284.0,"contact_point_centroid":[0.54488,0.18933,-0.00202],"force_p95":0.1731,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24326,"mean_force":0.12504,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.574,0.21835,0.31906]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48269,0.04871,-0.00202],"force_p95":0.2234,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.2279,"mean_force":0.16338,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.47129,0.049,0.04777]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4689.0,"contact_point_centroid":[0.4885,0.09674,0.31565],"force_p95":0.12603,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20874,"mean_force":0.08021,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.48515,0.07821,0.31733]},{"body_a":"world","body_b":"grasp_target","contact_count":3724.0,"contact_point_centroid":[0.4827,0.04873,-0.00196],"force_p95":0.12536,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12276,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.49124,0.0687,0.23982]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.54487,0.1893,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12266,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.5751,0.22406,0.26425]},{"body_a":"world","body_b":"grasp_target","contact_count":1156.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.47737,0.05384,0.09526]},{"body_a":"world","body_b":"grasp_target","contact_count":936.0,"contact_point_centroid":[0.54487,0.1893,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_from_goal","phase_type":"retract","tcp_position_centroid":[0.57272,0.22277,0.31383]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5265.0,"contact_point_centroid":[0.46987,0.06811,0.0488],"force_p95":0.07285,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1171,"mean_force":0.05031,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.4702,0.0489,0.04663]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4941.0,"contact_point_centroid":[0.46948,0.02966,0.0491],"force_p95":0.07506,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11087,"mean_force":0.0524,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.4702,0.0489,0.04663]},{"body_a":"left_finger","body_b":"right_finger","contact_count":362.0,"contact_point_centroid":[0.56179,0.19645,0.37939],"force_p95":0.01399,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01627,"mean_force":0.0112,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.56116,0.19643,0.37707]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1363.0,"contact_point_centroid":[0.57443,0.21836,0.32156],"force_p95":0.01098,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01269,"mean_force":0.01049,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.57399,0.21833,0.31922]}],"total_contact_groups":17},"final_pose_error":0.01995,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.54487,0.1893,0.02602],"final_tcp_position":[0.57271,0.22266,0.34506],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":142.07318,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":932.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":41.31597,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3724.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_pre_grasp","tcp_end":[0.47933,0.05809,0.13575],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11018,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":289.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":39.57279,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1156.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_grasp","tcp_end":[0.47786,0.0497,0.05468],"tcp_start":[0.47933,0.05809,0.13575],"tcp_to_object_dist_end":0.02908,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":46.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.4826,0.04882,0.02589],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29005,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.22323,"phase_name":"grasp_close","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12006.0,"raw_peak_contact_force":0.2279,"tcp_end":[0.47017,0.04889,0.0466],"tcp_start":[0.47786,0.0497,0.05468],"tcp_to_object_dist_end":0.02416,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":749.0,"n_steps_budget":1000.0,"object_pos_end":[0.47354,0.04867,0.24475],"object_pos_start":[0.4826,0.04882,0.02589],"object_to_goal_dist_end":0.21073,"object_to_goal_dist_start":0.29005,"object_z_max":0.24447,"peak_contact_force":0.0755,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":28905.0,"raw_peak_contact_force":0.45146,"subtask_id":"lift_clearance","tcp_end":[0.46762,0.04862,0.27115],"tcp_start":[0.47017,0.04889,0.0466],"tcp_to_object_dist_end":0.02706,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":626.0,"n_steps_budget":1000.0,"object_pos_end":[0.54597,0.19335,0.02662],"object_pos_start":[0.47354,0.04867,0.24475],"object_to_goal_dist_end":0.21003,"object_to_goal_dist_start":0.21073,"object_z_max":0.32923,"peak_contact_force":142.07318,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":9822.0,"raw_peak_contact_force":2.73037,"subtask_id":"reach_goal","tcp_end":[0.57117,0.21223,0.37396],"tcp_start":[0.46762,0.04862,0.27115],"tcp_to_object_dist_end":0.34876,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":321.0,"n_steps_budget":1000.0,"object_pos_end":[0.54487,0.1893,0.02602],"object_pos_start":[0.54597,0.19335,0.02662],"object_to_goal_dist_end":0.21152,"object_to_goal_dist_start":0.21003,"object_z_max":0.02662,"peak_contact_force":0.12266,"phase_name":"descend_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2647.0,"raw_peak_contact_force":0.24326,"tcp_end":[0.57801,0.2254,0.26389],"tcp_start":[0.57117,0.21223,0.37396],"tcp_to_object_dist_end":0.24287,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54487,0.1893,0.02602],"object_pos_start":[0.54487,0.1893,0.02602],"object_to_goal_dist_end":0.21152,"object_to_goal_dist_start":0.21152,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1020.0,"raw_peak_contact_force":0.12266,"tcp_end":[0.57418,0.22353,0.28398],"tcp_start":[0.57801,0.2254,0.26389],"tcp_to_object_dist_end":0.26186,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":234.0,"n_steps_budget":600.0,"object_pos_end":[0.54487,0.1893,0.02602],"object_pos_start":[0.54487,0.1893,0.02602],"object_to_goal_dist_end":0.21152,"object_to_goal_dist_start":0.21152,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"retract_from_goal","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":936.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.57271,0.22266,0.34506],"tcp_start":[0.57418,0.22353,0.28398],"tcp_to_object_dist_end":0.32199,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```