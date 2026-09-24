## Search State

- **Seed**: 6
- **Iteration**: 14 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 13 | approach → descend → grasp → lift → approach → descend → release → retract | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 16 | -0.3716 | 0.29 | ❌ rejected |
| 12 | approach → descend → grasp → lift → approach → descend → release → retract | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 16 | -0.3830 | 0.27 | ❌ rejected |
| 11 | approach → descend → grasp → lift → approach → descend → release → retract | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 16 | -0.3662 | 0.30 | ❌ rejected |
| 10 | approach → descend → grasp → lift → approach → release → retract | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 12 | -0.1459 | 0.28 | ❌ rejected |
| 9 | approach → descend → grasp → lift → approach → descend → release → retract | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 14 | -0.2636 | 0.31 | ❌ rejected |

**Proposal policy**: task_score is 0.29 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.372) — your mutation base

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

- **Composite score**: -0.372
- **task_score** (E): 0.293
- **fitness_score**: 0.608  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.980

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_above | 1.00 | 1.00 | 0.1499 |
| descend_to_grasp | 1.00 | 1.00 | 0.1026 |
| grasp_close | 1.00 | 1.00 | 0.0117 |
| lift_object | 1.00 | 1.00 | 0.2323 |
| transport_to_goal | 1.00 | 1.00 | 0.2318 |
| descend_to_place | 1.00 | 1.00 | 0.1674 |
| release_object | 1.00 | 1.00 | 0.0203 |
| retract_from_goal | 1.00 | 1.00 | 0.1650 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_above | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.496, 0.032, 0.158) | (0.500, 0.024, 0.030)→(0.500, 0.024, 0.026) | 0.269→0.271 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.496, 0.032, 0.158)→(0.495, 0.025, 0.056) | (0.500, 0.024, 0.026)→(0.500, 0.024, 0.026) | 0.271→0.271 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_close | grasp | 1.00 / step_budget | (0.495, 0.025, 0.056)→(0.487, 0.025, 0.047) | (0.500, 0.024, 0.026)→(0.500, 0.024, 0.026) | 0.271→0.272 | 1.00 / 44.000 | 0.168 | 0.196 |
| lift_object | lift | 1.00 / step_budget | (0.487, 0.025, 0.047)→(0.484, 0.024, 0.279) | (0.500, 0.024, 0.026)→(0.490, 0.024, 0.252) | 0.272→0.215 | 1.00 / 32.667 | 0.086 | 0.415 |
| transport_to_goal | approach | 1.00 / step_budget | (0.484, 0.024, 0.279)→(0.589, 0.182, 0.411) | (0.490, 0.024, 0.252)→(0.567, 0.151, 0.020) | 0.215→0.200 | 1.00 / 7.667 | 6499.282 | 2.612 |
| descend_to_place | descend | 1.00 / step_budget | (0.589, 0.182, 0.411)→(0.595, 0.194, 0.244) | (0.567, 0.151, 0.020)→(0.567, 0.148, 0.026) | 0.200→0.193 | 1.00 / 8.000 | 6499.194 | 0.262 |
| release_object | release | 1.00 / step_budget | (0.595, 0.194, 0.244)→(0.591, 0.192, 0.264) | (0.567, 0.148, 0.026)→(0.567, 0.148, 0.026) | 0.193→0.193 | 1.00 / 4.000 | 0.123 | 0.123 |
| retract_from_goal | retract | 1.00 / step_budget | (0.591, 0.192, 0.264)→(0.591, 0.192, 0.429) | (0.567, 0.148, 0.026)→(0.567, 0.148, 0.026) | 0.193→0.193 | 1.00 / 4.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.446
- phase_score: 0.537
- phase_breakdown.approach_pre_grasp_score: 0.535
- phase_breakdown.reach_goal_score: 0.619
- phase_breakdown.reach_grasp_score: 0.727
- phase_breakdown.lift_clearance_score: 0.188
- grasp_place_fitness: 0.686

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.686
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.446
- **Median Q (composite search score)**: -0.410
- **K-run variance**: 0.0030
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Parameters at upper bound**: descend_to_place.place_offset
- **Final σ (mean)**: 0.299


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.36269,"average_solve_count":386.0,"average_success_count":386.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.approach_height":0.10989,"approach_above.arc_height":0.06123,"approach_above.speed":0.07024,"descend_to_grasp.descend_offset":0.02025,"descend_to_grasp.speed":0.04615,"descend_to_place.place_offset":0.02381,"descend_to_place.speed":0.03543,"grasp_close.grasp_duration":0.20134,"lift_object.lift_distance":0.23412,"lift_object.speed":0.04762,"release_object.release_duration":0.06881,"retract_from_goal.retract_distance":0.22503,"retract_from_goal.speed":0.06609,"transport_to_goal.arc_height":0.03568,"transport_to_goal.speed":0.16146,"transport_to_goal.transport_height":0.19087},"optimized_scores":{"best_composite_score":-0.41041,"best_fitness_score":0.56959,"best_task_score":0.21383},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":274.0,"contact_point_centroid":[0.57562,0.1206,-0.00833],"force_p95":1.48715,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.73263,"mean_force":0.37151,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.57278,0.15874,0.42387]},{"body_a":"world","body_b":"grasp_target","contact_count":88.0,"contact_point_centroid":[0.50001,-0.01393,-0.00153],"force_p95":0.3933,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.42474,"mean_force":0.14642,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.4897,-0.01422,0.04722]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6517.0,"contact_point_centroid":[0.51119,0.04714,0.32179],"force_p95":0.13251,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29675,"mean_force":0.08066,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.5075,0.02842,0.32283]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":13922.0,"contact_point_centroid":[0.48747,0.00499,0.15295],"force_p95":0.08048,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27056,"mean_force":0.05606,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48739,-0.01418,0.1519]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":15230.0,"contact_point_centroid":[0.48758,-0.03327,0.14894],"force_p95":0.07897,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26733,"mean_force":0.0522,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48739,-0.01418,0.14737]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50386,-0.01558,-0.00213],"force_p95":0.15809,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21649,"mean_force":0.13201,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.49192,-0.01425,0.04726]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6995.0,"contact_point_centroid":[0.51219,0.01159,0.32405],"force_p95":0.1206,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20278,"mean_force":0.07513,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.50837,0.03018,0.32483]},{"body_a":"world","body_b":"grasp_target","contact_count":1673.0,"contact_point_centroid":[0.57617,0.12331,-0.00197],"force_p95":0.14619,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19713,"mean_force":0.12349,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.58149,0.17839,0.35481]},{"body_a":"world","body_b":"grasp_target","contact_count":2880.0,"contact_point_centroid":[0.50382,-0.01567,-0.00195],"force_p95":0.12868,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.1228,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.49886,0.03007,0.21433]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4335.0,"contact_point_centroid":[0.49138,0.00503,0.04771],"force_p95":0.07685,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13677,"mean_force":0.04974,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.49078,-0.01423,0.04603]},{"body_a":"world","body_b":"grasp_target","contact_count":1152.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.49795,-0.01058,0.09603]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.5762,0.12345,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.58111,0.18386,0.28145]},{"body_a":"world","body_b":"grasp_target","contact_count":3204.0,"contact_point_centroid":[0.5762,0.12345,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_from_goal","phase_type":"retract","tcp_position_centroid":[0.57961,0.18297,0.4024]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5486.0,"contact_point_centroid":[0.49187,-0.03338,0.04843],"force_p95":0.06885,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07047,"mean_force":0.04039,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.49078,-0.01423,0.04603]},{"body_a":"left_finger","body_b":"right_finger","contact_count":259.0,"contact_point_centroid":[0.57465,0.16189,0.42694],"force_p95":0.01473,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0164,"mean_force":0.01154,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.57435,0.16189,0.4249]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1793.0,"contact_point_centroid":[0.58195,0.17834,0.35787],"force_p95":0.01098,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01277,"mean_force":0.01044,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.58147,0.17832,0.35559]}],"total_contact_groups":17},"final_pose_error":0.01997,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.5762,0.12345,0.02602],"final_tcp_position":[0.58114,0.18337,0.50632],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":9748.80308,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":721.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2880.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_pre_grasp","tcp_end":[0.49971,-0.00703,0.13725],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11164,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":288.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1152.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_grasp","tcp_end":[0.4987,-0.0143,0.05471],"tcp_start":[0.49971,-0.00703,0.13725],"tcp_to_object_dist_end":0.02917,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50378,-0.01463,0.02554],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31191,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.15563,"phase_name":"grasp_close","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11621.0,"raw_peak_contact_force":0.21649,"tcp_end":[0.49075,-0.01423,0.046],"tcp_start":[0.4987,-0.0143,0.05471],"tcp_to_object_dist_end":0.02425,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":738.0,"n_steps_budget":1000.0,"object_pos_end":[0.49439,-0.01458,0.23486],"object_pos_start":[0.50378,-0.01463,0.02554],"object_to_goal_dist_end":0.2226,"object_to_goal_dist_start":0.31191,"object_z_max":0.23459,"peak_contact_force":0.07741,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":29240.0,"raw_peak_contact_force":0.42474,"subtask_id":"lift_clearance","tcp_end":[0.48804,-0.01419,0.26045],"tcp_start":[0.49075,-0.01423,0.046],"tcp_to_object_dist_end":0.02637,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":7.0,"n_steps":751.0,"n_steps_budget":1000.0,"object_pos_end":[0.57411,0.11988,0.02787],"object_pos_start":[0.49439,-0.01458,0.23486],"object_to_goal_dist_end":0.23073,"object_to_goal_dist_start":0.2226,"object_z_max":0.35865,"peak_contact_force":9748.44525,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":14045.0,"raw_peak_contact_force":2.73263,"subtask_id":"reach_goal","tcp_end":[0.5796,0.17253,0.42788],"tcp_start":[0.48804,-0.01419,0.26045],"tcp_to_object_dist_end":0.4035,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":420.0,"n_steps_budget":1000.0,"object_pos_end":[0.5762,0.12345,0.02602],"object_pos_start":[0.57411,0.11988,0.02787],"object_to_goal_dist_end":0.23138,"object_to_goal_dist_start":0.23073,"object_z_max":0.02787,"peak_contact_force":9748.80308,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3466.0,"raw_peak_contact_force":0.19713,"subtask_id":"reach_goal","tcp_end":[0.58387,0.18492,0.28097],"tcp_start":[0.5796,0.17253,0.42788],"tcp_to_object_dist_end":0.26237,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5762,0.12345,0.02602],"object_pos_start":[0.5762,0.12345,0.02602],"object_to_goal_dist_end":0.23138,"object_to_goal_dist_start":0.23138,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1023.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.58026,0.18344,0.30123],"tcp_start":[0.58387,0.18492,0.28097],"tcp_to_object_dist_end":0.28171,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":801.0,"n_steps_budget":1000.0,"object_pos_end":[0.5762,0.12345,0.02602],"object_pos_start":[0.5762,0.12345,0.02602],"object_to_goal_dist_end":0.23138,"object_to_goal_dist_start":0.23138,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"retract_from_goal","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3204.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.58114,0.18337,0.50632],"tcp_start":[0.58026,0.18344,0.30123],"tcp_to_object_dist_end":0.48405,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.1621,"average_solve_count":438.0,"average_success_count":438.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.approach_height":0.14992,"approach_above.arc_height":0.06329,"approach_above.speed":0.06547,"descend_to_grasp.descend_offset":0.02038,"descend_to_grasp.speed":0.02802,"descend_to_place.place_offset":0.01834,"descend_to_place.speed":0.02842,"grasp_close.grasp_duration":0.23221,"lift_object.lift_distance":0.23597,"lift_object.speed":0.04361,"release_object.release_duration":0.16832,"retract_from_goal.retract_distance":0.16386,"retract_from_goal.speed":0.07757,"transport_to_goal.arc_height":0.03171,"transport_to_goal.speed":0.18015,"transport_to_goal.transport_height":0.2291},"optimized_scores":{"best_composite_score":-0.29371,"best_fitness_score":0.68629,"best_task_score":0.44589},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":109.0,"contact_point_centroid":[0.60463,0.17192,-0.01161],"force_p95":1.75455,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.71471,"mean_force":0.76711,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.61117,0.15616,0.36501]},{"body_a":"world","body_b":"grasp_target","contact_count":2086.0,"contact_point_centroid":[0.60499,0.17149,-0.00225],"force_p95":0.15888,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.46379,"mean_force":0.12217,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.61843,0.16501,0.26595]},{"body_a":"world","body_b":"grasp_target","contact_count":87.0,"contact_point_centroid":[0.50877,0.03919,-0.00142],"force_p95":0.38608,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.40055,"mean_force":0.1486,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49841,0.03949,0.04686]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4935.0,"contact_point_centroid":[0.52496,0.04829,0.30221],"force_p95":0.14233,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30292,"mean_force":0.0791,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52266,0.06692,0.30376]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14611.0,"contact_point_centroid":[0.49566,0.02016,0.15339],"force_p95":0.07874,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27243,"mean_force":0.05456,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49604,0.0393,0.15197]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":15193.0,"contact_point_centroid":[0.49636,0.05841,0.15067],"force_p95":0.0776,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26462,"mean_force":0.05303,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49605,0.0393,0.14887]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5064.0,"contact_point_centroid":[0.52754,0.08758,0.30422],"force_p95":0.12713,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20489,"mean_force":0.07778,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52466,0.06894,0.30571]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.5125,0.03967,-0.00202],"force_p95":0.1299,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15189,"mean_force":0.12486,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.50062,0.03968,0.04713]},{"body_a":"world","body_b":"grasp_target","contact_count":2780.0,"contact_point_centroid":[0.51251,0.03972,-0.00195],"force_p95":0.12911,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.1228,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.50125,0.05336,0.2568]},{"body_a":"world","body_b":"grasp_target","contact_count":1756.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.50648,0.04444,0.11704]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.60492,0.17088,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.61841,0.16894,0.17124]},{"body_a":"world","body_b":"grasp_target","contact_count":2352.0,"contact_point_centroid":[0.60492,0.17088,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":7.0,"phase_name":"retract_from_goal","phase_type":"retract","tcp_position_centroid":[0.61444,0.16756,0.2619]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5354.0,"contact_point_centroid":[0.50043,0.05877,0.04825],"force_p95":0.06414,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08333,"mean_force":0.04106,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.49947,0.03959,0.04585]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4559.0,"contact_point_centroid":[0.49988,0.02035,0.04849],"force_p95":0.07001,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08196,"mean_force":0.04755,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.49947,0.03959,0.04585]},{"body_a":"left_finger","body_b":"right_finger","contact_count":16.0,"contact_point_centroid":[0.61475,0.15955,0.36731],"force_p95":0.01622,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01622,"mean_force":0.01557,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.61447,0.15953,0.36523]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2309.0,"contact_point_centroid":[0.61887,0.16493,0.27041],"force_p95":0.01108,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01466,"mean_force":0.01046,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.61834,0.16491,0.26819]}],"total_contact_groups":17},"final_pose_error":0.01988,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.60492,0.17088,0.02602],"final_tcp_position":[0.61519,0.16769,0.33471],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":2.71471,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":696.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2780.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_pre_grasp","tcp_end":[0.50825,0.04872,0.17968],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.15398,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":439.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1756.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_grasp","tcp_end":[0.50751,0.04029,0.05488],"tcp_start":[0.50825,0.04872,0.17968],"tcp_to_object_dist_end":0.0293,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51242,0.03947,0.02589],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.2125,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12951,"phase_name":"grasp_close","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11713.0,"raw_peak_contact_force":0.15189,"tcp_end":[0.49944,0.03959,0.04582],"tcp_start":[0.50751,0.04029,0.05488],"tcp_to_object_dist_end":0.02378,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":757.0,"n_steps_budget":1000.0,"object_pos_end":[0.50288,0.03947,0.23679],"object_pos_start":[0.51242,0.03947,0.02589],"object_to_goal_dist_end":0.20413,"object_to_goal_dist_start":0.2125,"object_z_max":0.23652,"peak_contact_force":0.07653,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":29891.0,"raw_peak_contact_force":0.40055,"subtask_id":"lift_clearance","tcp_end":[0.49674,0.03935,0.26198],"tcp_start":[0.49944,0.03959,0.04582],"tcp_to_object_dist_end":0.02592,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":560.0,"n_steps_budget":1000.0,"object_pos_end":[0.60497,0.18165,0.00505],"object_pos_start":[0.50288,0.03947,0.23679],"object_to_goal_dist_end":0.14208,"object_to_goal_dist_start":0.20413,"object_z_max":0.31525,"peak_contact_force":0.49037,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":10124.0,"raw_peak_contact_force":2.71471,"subtask_id":"reach_goal","tcp_end":[0.61505,0.16017,0.36522],"tcp_start":[0.49674,0.03935,0.26198],"tcp_to_object_dist_end":0.36096,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":537.0,"n_steps_budget":1000.0,"object_pos_end":[0.60492,0.17088,0.02602],"object_pos_start":[0.60497,0.18165,0.00505],"object_to_goal_dist_end":0.12115,"object_to_goal_dist_start":0.14208,"object_z_max":0.0282,"peak_contact_force":0.12263,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4395.0,"raw_peak_contact_force":0.46379,"subtask_id":"reach_goal","tcp_end":[0.62284,0.17032,0.17163],"tcp_start":[0.61505,0.16017,0.36522],"tcp_to_object_dist_end":0.14671,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.60492,0.17088,0.02602],"object_pos_start":[0.60492,0.17088,0.02602],"object_to_goal_dist_end":0.12115,"object_to_goal_dist_start":0.12115,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1021.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.61685,0.16841,0.19065],"tcp_start":[0.62284,0.17032,0.17163],"tcp_to_object_dist_end":0.16508,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":588.0,"n_steps_budget":1000.0,"object_pos_end":[0.60492,0.17088,0.02602],"object_pos_start":[0.60492,0.17088,0.02602],"object_to_goal_dist_end":0.12115,"object_to_goal_dist_start":0.12115,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"retract_from_goal","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2352.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.61519,0.16769,0.33471],"tcp_start":[0.61685,0.16841,0.19065],"tcp_to_object_dist_end":0.30887,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.93111,"average_solve_count":479.0,"average_success_count":479.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.approach_height":0.12001,"approach_above.arc_height":0.04109,"approach_above.speed":0.06546,"descend_to_grasp.descend_offset":0.02287,"descend_to_grasp.speed":0.01794,"descend_to_place.place_offset":0.04,"descend_to_place.speed":0.0231,"grasp_close.grasp_duration":0.26886,"lift_object.lift_distance":0.28581,"lift_object.speed":0.03076,"release_object.release_duration":0.09139,"retract_from_goal.retract_distance":0.16575,"retract_from_goal.speed":0.07909,"transport_to_goal.arc_height":0.05689,"transport_to_goal.speed":0.20664,"transport_to_goal.transport_height":0.21248},"optimized_scores":{"best_composite_score":-0.41078,"best_fitness_score":0.56922,"best_task_score":0.21957},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":905.0,"contact_point_centroid":[0.52001,0.15018,-0.00389],"force_p95":0.84635,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.38915,"mean_force":0.19752,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.54411,0.1684,0.43966]},{"body_a":"world","body_b":"grasp_target","contact_count":81.0,"contact_point_centroid":[0.47947,0.04833,-0.00143],"force_p95":0.36537,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.42078,"mean_force":0.12648,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46939,0.04816,0.05047]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":14905.0,"contact_point_centroid":[0.46725,0.0668,0.16812],"force_p95":0.10591,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29004,"mean_force":0.06304,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46728,0.04795,0.16805]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14262.0,"contact_point_centroid":[0.46693,0.02902,0.16407],"force_p95":0.10694,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24379,"mean_force":0.0656,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46726,0.04795,0.16485]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2254.0,"contact_point_centroid":[0.47931,0.04499,0.3515],"force_p95":0.15891,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2418,"mean_force":0.10529,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.47704,0.06331,0.35509]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.4827,0.04871,-0.00204],"force_p95":0.21984,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22055,"mean_force":0.16313,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.47153,0.04839,0.05059]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2689.0,"contact_point_centroid":[0.48094,0.08278,0.35343],"force_p95":0.12957,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21537,"mean_force":0.08985,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.47786,0.06462,0.35744]},{"body_a":"world","body_b":"grasp_target","contact_count":2296.0,"contact_point_centroid":[0.4827,0.04873,-0.00194],"force_p95":0.13153,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12284,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.49073,0.04586,0.23971]},{"body_a":"world","body_b":"grasp_target","contact_count":1832.0,"contact_point_centroid":[0.52067,0.15034,-0.00199],"force_p95":0.12284,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12391,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.57515,0.21874,0.35971]},{"body_a":"world","body_b":"grasp_target","contact_count":1488.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.47786,0.05191,0.10746]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.52067,0.15034,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.57603,0.22479,0.27973]},{"body_a":"world","body_b":"grasp_target","contact_count":2232.0,"contact_point_centroid":[0.52067,0.15034,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_from_goal","phase_type":"retract","tcp_position_centroid":[0.57425,0.22363,0.37158]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5085.0,"contact_point_centroid":[0.46957,0.02914,0.05042],"force_p95":0.07235,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11772,"mean_force":0.05049,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.47044,0.04828,0.04945]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4645.0,"contact_point_centroid":[0.47078,0.06753,0.05042],"force_p95":0.07846,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11649,"mean_force":0.05641,"phase_index":2.0,"phase_name":"grasp_close","phase_type":"grasp","tcp_position_centroid":[0.47044,0.04828,0.04945]},{"body_a":"left_finger","body_b":"right_finger","contact_count":942.0,"contact_point_centroid":[0.54543,0.17005,0.44232],"force_p95":0.01258,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01623,"mean_force":0.0107,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.54515,0.17003,0.44006]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1950.0,"contact_point_centroid":[0.57548,0.21878,0.36202],"force_p95":0.01098,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01282,"mean_force":0.01047,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.57515,0.21875,0.35969]}],"total_contact_groups":17},"final_pose_error":0.01992,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.52067,0.15034,0.02602],"final_tcp_position":[0.57519,0.22389,0.44526],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":9748.91021,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":575.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2296.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_pre_grasp","tcp_end":[0.48043,0.05492,0.1572],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13135,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":372.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1488.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_grasp","tcp_end":[0.47807,0.04906,0.05749],"tcp_start":[0.48043,0.05492,0.1572],"tcp_to_object_dist_end":0.03182,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48263,0.0485,0.02585],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29027,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.22012,"phase_name":"grasp_close","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11530.0,"raw_peak_contact_force":0.22055,"tcp_end":[0.47041,0.04828,0.04942],"tcp_start":[0.47807,0.04906,0.05749],"tcp_to_object_dist_end":0.02656,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":896.0,"n_steps_budget":1000.0,"object_pos_end":[0.47128,0.04834,0.28398],"object_pos_start":[0.48263,0.0485,0.02585],"object_to_goal_dist_end":0.21835,"object_to_goal_dist_start":0.29027,"object_z_max":0.28371,"peak_contact_force":0.10382,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":29248.0,"raw_peak_contact_force":0.42078,"subtask_id":"lift_clearance","tcp_end":[0.46829,0.04804,0.31562],"tcp_start":[0.47041,0.04828,0.04942],"tcp_to_object_dist_end":0.03178,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":626.0,"n_steps_budget":1000.0,"object_pos_end":[0.52058,0.15037,0.02602],"object_pos_start":[0.47128,0.04834,0.28398],"object_to_goal_dist_end":0.22743,"object_to_goal_dist_start":0.21835,"object_z_max":0.3593,"peak_contact_force":9748.91021,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":6790.0,"raw_peak_contact_force":2.38915,"subtask_id":"reach_goal","tcp_end":[0.572,0.21215,0.4393],"tcp_start":[0.46829,0.04804,0.31562],"tcp_to_object_dist_end":0.42102,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":458.0,"n_steps_budget":1000.0,"object_pos_end":[0.52067,0.15034,0.02602],"object_pos_start":[0.52058,0.15037,0.02602],"object_to_goal_dist_end":0.22741,"object_to_goal_dist_start":0.22743,"object_z_max":0.02602,"peak_contact_force":9748.65559,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3782.0,"raw_peak_contact_force":0.12391,"subtask_id":"reach_goal","tcp_end":[0.57871,0.22608,0.27944],"tcp_start":[0.572,0.21215,0.4393],"tcp_to_object_dist_end":0.27079,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.52067,0.15034,0.02602],"object_pos_start":[0.52067,0.15034,0.02602],"object_to_goal_dist_end":0.22741,"object_to_goal_dist_start":0.22741,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1020.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.57522,0.2243,0.29943],"tcp_start":[0.57871,0.22608,0.27944],"tcp_to_object_dist_end":0.28844,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":558.0,"n_steps_budget":1000.0,"object_pos_end":[0.52067,0.15034,0.02602],"object_pos_start":[0.52067,0.15034,0.02602],"object_to_goal_dist_end":0.22741,"object_to_goal_dist_start":0.22741,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"retract_from_goal","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2232.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.57519,0.22389,0.44526],"tcp_start":[0.57522,0.2243,0.29943],"tcp_to_object_dist_end":0.42912,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```