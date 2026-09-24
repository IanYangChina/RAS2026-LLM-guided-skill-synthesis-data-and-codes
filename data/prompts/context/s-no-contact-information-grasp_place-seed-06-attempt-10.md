## Search State

- **Seed**: 6
- **Iteration**: 11 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 10 | approach → descend → grasp → lift → approach → release → retract | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 5 | 0.2241 | 0.29 | ❌ rejected |
| 9 | approach → descend → grasp → lift → approach | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | 4 | 0.2215 | 0.24 | ❌ rejected |
| 8 | approach → descend → grasp → lift → approach → release → retract | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 5 | 0.2250 | 0.29 | ✅ accepted |
| 7 | approach → descend → grasp → lift → approach → descend → release → retract | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 7 | 0.0617 | 0.24 | ❌ rejected |
| 6 | approach → descend → grasp → lift → push → release → retract | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 5 | 0.2161 | 0.28 | ✅ accepted |

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

## Current Skill (Q=0.224) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: approach_object
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.15
  weight: 0.2
- id: grasp_lift
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.2
  weight: 0.3
- id: reach_goal
  weight: 0.5
phases:
- id: approach_1
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
    - 0.15
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    arc_height:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.arc_height
        mode: replace
  subtask_id: approach_object
- id: descend_1
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
    - 0.01
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    descend_offset_z:
      type: scalar
      range:
      - 0.0
      - 0.03
      default: 0.01
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: approach_object
- id: grasp_1
  type: grasp
  control: position_control
  termination: grasp_success
  end_effector_action: force_grasp
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
  guards:
  - id: bilateral_grasp
    when: after_phase
    predicate: bilateral_grasp
    threshold: 0.5
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: repeat
  subtask_id: grasp_lift
- id: lift_1
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
    lift_height:
      type: scalar
      range:
      - 0.1
      - 0.35
      default: 0.2
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
  subtask_id: grasp_lift
- id: transport_1
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    entity: placement_surface
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    transport_speed:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_goal
- id: release_1
  type: release
  control: position_control
  termination: time_limit
  end_effector_action: open
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
  parameters:
    release_duration:
      type: scalar
      range:
      - 0.1
      - 0.5
      default: 0.2
      binds_to:
      - path: duration.max_time
        mode: replace
  subtask_id: reach_goal
- id: retract_1
  type: retract
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: world
    offset:
    - 0.5
    - 0.0
    - 0.5
    tolerance: 0.05
    orientation:
      mode: keep_current

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - arc_height: status=consumed; consumers=generator.arc_height (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.01], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_offset_z: status=consumed; consumers=target.offset.z (replace)
- **grasp_1** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
  - guards:
    - id=bilateral_grasp, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=0.5
  - retries: max_attempts=2, strategy=repeat
- **lift_1** (`lift`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.2, mode=add_to_offset, sign=positive}, tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset_along_axis.distance (replace)
- **transport_1** (`approach`)
  - target: source=yaml, anchor=task_goal, entity=placement_surface, offset=[0.0, 0.0, 0.0], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - transport_speed: status=consumed; consumers=generator.speed (replace)
- **release_1** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings:
    - release_duration: status=consumed; consumers=duration.max_time (replace)
- **retract_1** (`retract`)
  - target: source=yaml, anchor=world, offset=[0.5, 0.0, 0.5], tolerance=0.05
  - orientation: mode=keep_current
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.224
- **task_score** (E): 0.291
- **fitness_score**: 0.624  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Complexity Penalty**: 0.400

## Per-Phase Performance

| Phase | Normal Term. Rate | Mean Displacement (m) |
| ------- | ------------------- | ------------------------ |
| approach_1 | 1.00 | 0.1203 |
| descend_1 | 1.00 | 0.1545 |
| grasp_1 | 1.00 | 0.0118 |
| lift_1 | 1.00 | 0.1038 |
| transport_1 | 1.00 | 0.2065 |
| release_1 | 1.00 | 0.0215 |
| retract_1 | 1.00 | 0.3005 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end |
| --- | --- | --- | --- | --- | --- |
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.497, 0.039, 0.191) | (0.500, 0.024, 0.030)→(0.500, 0.024, 0.026) | 0.269→0.271 |
| descend_1 | descend | 1.00 / step_budget | (0.497, 0.039, 0.191)→(0.495, 0.025, 0.037) | (0.500, 0.024, 0.026)→(0.500, 0.024, 0.026) | 0.271→0.271 |
| grasp_1 | grasp | 1.00 / step_budget | (0.495, 0.025, 0.037)→(0.487, 0.025, 0.028) | (0.500, 0.024, 0.026)→(0.500, 0.025, 0.026) | 0.271→0.271 |
| lift_1 | lift | 1.00 / step_budget | (0.487, 0.025, 0.028)→(0.483, 0.025, 0.132) | (0.500, 0.025, 0.026)→(0.501, 0.025, 0.125) | 0.271→0.218 |
| transport_1 | approach | 1.00 / step_budget | (0.483, 0.025, 0.132)→(0.588, 0.185, 0.196) | (0.501, 0.025, 0.125)→(0.599, 0.185, 0.176) | 0.218→0.034 |
| release_1 | release | 1.00 / step_budget | (0.588, 0.185, 0.196)→(0.583, 0.183, 0.216) | (0.599, 0.185, 0.176)→(0.591, 0.193, 0.008) | 0.034→0.200 |
| retract_1 | retract | 1.00 / step_budget | (0.583, 0.183, 0.216)→(0.512, 0.023, 0.458) | (0.591, 0.193, 0.008)→(0.592, 0.196, 0.016) | 0.200→0.192 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.421
- phase_score: 0.346
- phase_breakdown.reach_goal_score: 0.596
- phase_breakdown.approach_object_score: 0.055
- phase_breakdown.grasp_lift_score: 0.123
- grasp_place_fitness: 0.690

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.690
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.421
- **Median Q (composite search score)**: 0.197
- **K-run variance**: 0.0022
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Parameters at lower bound**: descend_1.descend_offset_z
- **Final σ (mean)**: 0.476


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.5037,"average_solve_count":270.0,"average_success_count":270.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.arc_height":0.0822,"descend_1.descend_offset_z":0.0,"lift_1.lift_height":0.1267,"release_1.release_duration":0.17005,"transport_1.transport_speed":0.02617},"optimized_scores":{"best_composite_score":0.18568,"best_fitness_score":0.58568,"best_task_score":0.21268},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":99.0,"contact_point_centroid":[0.58082,0.18872,-0.01136],"force_p95":1.62698,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.99114,"mean_force":0.75996,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57427,0.17455,0.25097]},{"body_a":"world","body_b":"grasp_target","contact_count":80.0,"contact_point_centroid":[0.50068,-0.01317,-0.00143],"force_p95":0.67791,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.70437,"mean_force":0.15519,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48946,-0.01399,0.02733]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":630.0,"contact_point_centroid":[0.58067,0.15734,0.22643],"force_p95":0.14697,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.44252,"mean_force":0.09724,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57718,0.17575,0.23069]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5193.0,"contact_point_centroid":[0.48916,0.00509,0.07563],"force_p95":0.10888,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3326,"mean_force":0.06797,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48709,-0.01395,0.07313]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5820.0,"contact_point_centroid":[0.48918,-0.03283,0.07396],"force_p95":0.10353,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32102,"mean_force":0.06256,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4871,-0.01395,0.07224]},{"body_a":"world","body_b":"grasp_target","contact_count":1148.0,"contact_point_centroid":[0.58118,0.19111,-0.00233],"force_p95":0.12895,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.29803,"mean_force":0.11734,"phase_index":6.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.54298,0.10101,0.35206]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":759.0,"contact_point_centroid":[0.57998,0.19417,0.22583],"force_p95":0.21394,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28683,"mean_force":0.09333,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57704,0.17569,0.23044]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50388,-0.01531,-0.00216],"force_p95":0.16923,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.25659,"mean_force":0.13506,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49197,-0.01402,0.02702]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9858.0,"contact_point_centroid":[0.53555,0.10006,0.18135],"force_p95":0.12028,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17259,"mean_force":0.08097,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.53141,0.08156,0.1818]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9801.0,"contact_point_centroid":[0.5336,0.05886,0.17933],"force_p95":0.1244,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16848,"mean_force":0.08214,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.52935,0.07741,0.17951]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4044.0,"contact_point_centroid":[0.49129,0.00521,0.02855],"force_p95":0.08194,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15051,"mean_force":0.05198,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49079,-0.014,0.0258]},{"body_a":"world","body_b":"grasp_target","contact_count":1044.0,"contact_point_centroid":[0.50382,-0.01567,-0.00187],"force_p95":0.1365,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12309,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49964,0.02094,0.24369]},{"body_a":"world","body_b":"grasp_target","contact_count":1912.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49827,-0.00556,0.10942]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5028.0,"contact_point_centroid":[0.49133,-0.03319,0.02767],"force_p95":0.07388,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08681,"mean_force":0.04475,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4908,-0.014,0.0258]}],"total_contact_groups":14},"final_pose_error":0.04983,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.58115,0.19104,0.01602],"final_tcp_position":[0.51184,0.0249,0.45849],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"phases":[{"n_steps":262.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"approach_object","tcp_end":[0.50019,0.00282,0.18584],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16093,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":478.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"approach_object","tcp_end":[0.49897,-0.01404,0.03445],"tcp_start":[0.50019,0.00282,0.18584],"tcp_to_object_dist_end":0.00986,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5037,-0.01399,0.02547],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31157,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","subtask_id":"grasp_lift","tcp_end":[0.49076,-0.014,0.02577],"tcp_start":[0.49897,-0.01404,0.03445],"tcp_to_object_dist_end":0.01293,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":338.0,"n_steps_budget":810.0,"object_pos_end":[0.50606,-0.01383,0.12798],"object_pos_start":[0.5037,-0.01399,0.02547],"object_to_goal_dist_end":0.24796,"object_to_goal_dist_start":0.31157,"object_z_max":0.12771,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","subtask_id":"grasp_lift","tcp_end":[0.48695,-0.01394,0.13287],"tcp_start":[0.49076,-0.014,0.02577],"tcp_to_object_dist_end":0.01973,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":807.0,"n_steps_budget":1000.0,"object_pos_end":[0.58781,0.17562,0.21283],"object_pos_start":[0.50606,-0.01383,0.12798],"object_to_goal_dist_end":0.03723,"object_to_goal_dist_start":0.24796,"object_z_max":0.21273,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_goal","tcp_end":[0.57872,0.1758,0.23418],"tcp_start":[0.48695,-0.01394,0.13287],"tcp_to_object_dist_end":0.02321,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.57945,0.18696,-0.00109],"object_pos_start":[0.58781,0.17562,0.21283],"object_to_goal_dist_end":0.24931,"object_to_goal_dist_start":0.03723,"object_z_max":0.21285,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","subtask_id":"reach_goal","tcp_end":[0.57424,0.17455,0.25537],"tcp_start":[0.57872,0.1758,0.23418],"tcp_to_object_dist_end":0.25681,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":287.0,"n_steps_budget":1000.0,"object_pos_end":[0.58115,0.19104,0.01602],"object_pos_start":[0.57945,0.18696,-0.00109],"object_to_goal_dist_end":0.2322,"object_to_goal_dist_start":0.24931,"object_z_max":0.01692,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","tcp_end":[0.51184,0.0249,0.45849],"tcp_start":[0.57424,0.17455,0.25537],"tcp_to_object_dist_end":0.47769,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.04739,"average_solve_count":211.0,"average_success_count":211.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.arc_height":0.06465,"descend_1.descend_offset_z":0.00076,"lift_1.lift_height":0.11995,"release_1.release_duration":0.49957,"transport_1.transport_speed":0.08751},"optimized_scores":{"best_composite_score":0.28955,"best_fitness_score":0.68955,"best_task_score":0.42104},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":232.0,"contact_point_centroid":[0.61341,0.17456,-0.00523],"force_p95":1.03215,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.41838,"mean_force":0.29121,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.60743,0.16017,0.14655]},{"body_a":"world","body_b":"grasp_target","contact_count":73.0,"contact_point_centroid":[0.5092,0.04035,-0.00136],"force_p95":0.66282,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.7036,"mean_force":0.16272,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.498,0.03988,0.02745]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4965.0,"contact_point_centroid":[0.49751,0.05875,0.07386],"force_p95":0.10729,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3448,"mean_force":0.06799,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4955,0.03967,0.07149]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":764.0,"contact_point_centroid":[0.61448,0.17985,0.12684],"force_p95":0.26675,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31724,"mean_force":0.10104,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61153,0.1615,0.1311]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5571.0,"contact_point_centroid":[0.49759,0.02084,0.07187],"force_p95":0.1017,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31004,"mean_force":0.06168,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49553,0.03967,0.07013]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":617.0,"contact_point_centroid":[0.61392,0.14341,0.12692],"force_p95":0.22214,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28294,"mean_force":0.1011,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61162,0.16153,0.13115]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6366.0,"contact_point_centroid":[0.5585,0.11937,0.12964],"force_p95":0.11975,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23313,"mean_force":0.08458,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.55346,0.10079,0.12907]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6240.0,"contact_point_centroid":[0.5594,0.08361,0.12955],"force_p95":0.12452,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22492,"mean_force":0.08557,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.55485,0.10218,0.12924]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.5125,0.03986,-0.00203],"force_p95":0.13259,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.16078,"mean_force":0.12549,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50045,0.0401,0.02747]},{"body_a":"world","body_b":"grasp_target","contact_count":1304.0,"contact_point_centroid":[0.51251,0.03972,-0.0019],"force_p95":0.13564,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.123,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50166,0.05271,0.25995]},{"body_a":"world","body_b":"grasp_target","contact_count":1536.0,"contact_point_centroid":[0.61386,0.17501,-0.00197],"force_p95":0.12484,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.1283,"mean_force":0.12166,"phase_index":6.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.55966,0.08954,0.29988]},{"body_a":"world","body_b":"grasp_target","contact_count":1912.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50632,0.04845,0.11141]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4112.0,"contact_point_centroid":[0.49983,0.05921,0.02887],"force_p95":0.07595,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11268,"mean_force":0.0518,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49926,0.04,0.0262]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4884.0,"contact_point_centroid":[0.49988,0.02093,0.02811],"force_p95":0.06779,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09071,"mean_force":0.04471,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49927,0.04,0.0262]}],"total_contact_groups":14},"final_pose_error":0.04936,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.61386,0.17501,0.01602],"final_tcp_position":[0.51303,0.01743,0.4557],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"phases":[{"n_steps":327.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"approach_object","tcp_end":[0.50772,0.05641,0.18952],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16442,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":478.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"approach_object","tcp_end":[0.50752,0.04075,0.03519],"tcp_start":[0.50772,0.05641,0.18952],"tcp_to_object_dist_end":0.01049,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51237,0.04014,0.02587],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21211,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","subtask_id":"grasp_lift","tcp_end":[0.49923,0.04,0.02616],"tcp_start":[0.50752,0.04075,0.03519],"tcp_to_object_dist_end":0.01314,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":321.0,"n_steps_budget":750.0,"object_pos_end":[0.51414,0.03985,0.12202],"object_pos_start":[0.51237,0.04014,0.02587],"object_to_goal_dist_end":0.17606,"object_to_goal_dist_start":0.21211,"object_z_max":0.12176,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","subtask_id":"grasp_lift","tcp_end":[0.49535,0.03966,0.12662],"tcp_start":[0.49923,0.04,0.02616],"tcp_to_object_dist_end":0.01935,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":533.0,"n_steps_budget":1000.0,"object_pos_end":[0.62832,0.16199,0.11743],"object_pos_start":[0.51414,0.03985,0.12202],"object_to_goal_dist_end":0.02955,"object_to_goal_dist_start":0.17606,"object_z_max":0.1223,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_goal","tcp_end":[0.61385,0.16177,0.13523],"tcp_start":[0.49535,0.03966,0.12662],"tcp_to_object_dist_end":0.02294,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.61377,0.17413,0.01566],"object_pos_start":[0.62832,0.16199,0.11743],"object_to_goal_dist_end":0.13011,"object_to_goal_dist_start":0.02955,"object_z_max":0.11743,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","subtask_id":"reach_goal","tcp_end":[0.60737,0.16015,0.15537],"tcp_start":[0.61385,0.16177,0.13523],"tcp_to_object_dist_end":0.14055,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":384.0,"n_steps_budget":1000.0,"object_pos_end":[0.61386,0.17501,0.01602],"object_pos_start":[0.61377,0.17413,0.01566],"object_to_goal_dist_end":0.12976,"object_to_goal_dist_start":0.13011,"object_z_max":0.01652,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","tcp_end":[0.51303,0.01743,0.4557],"tcp_start":[0.60737,0.16015,0.15537],"tcp_to_object_dist_end":0.47782,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.53114,"average_solve_count":273.0,"average_success_count":273.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.arc_height":0.04478,"descend_1.descend_offset_z":0.00632,"lift_1.lift_height":0.12309,"release_1.release_duration":0.27027,"transport_1.transport_speed":0.04161},"optimized_scores":{"best_composite_score":0.19714,"best_fitness_score":0.59714,"best_task_score":0.23914},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":159.0,"contact_point_centroid":[0.57806,0.22223,-0.00816],"force_p95":1.51533,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.90355,"mean_force":0.49317,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.56778,0.21567,0.23208]},{"body_a":"world","body_b":"grasp_target","contact_count":72.0,"contact_point_centroid":[0.47977,0.04844,-0.00133],"force_p95":0.55975,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.58195,"mean_force":0.1366,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46938,0.04821,0.03457]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5654.0,"contact_point_centroid":[0.46836,0.06709,0.08146],"force_p95":0.10199,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30385,"mean_force":0.06087,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4671,0.04798,0.07932]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5756.0,"contact_point_centroid":[0.46858,0.029,0.08273],"force_p95":0.0981,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.297,"mean_force":0.05972,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46707,0.04797,0.08068]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":805.0,"contact_point_centroid":[0.57607,0.23598,0.21355],"force_p95":0.10975,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27977,"mean_force":0.07072,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57092,0.21722,0.21408]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":772.0,"contact_point_centroid":[0.57538,0.19857,0.21288],"force_p95":0.11358,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27821,"mean_force":0.06679,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57093,0.21722,0.21409]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48269,0.04863,-0.00203],"force_p95":0.13181,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.1558,"mean_force":0.12509,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47169,0.04846,0.03441]},{"body_a":"world","body_b":"grasp_target","contact_count":1088.0,"contact_point_centroid":[0.4827,0.04873,-0.00188],"force_p95":0.1365,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12308,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49285,0.04448,0.26002]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9365.0,"contact_point_centroid":[0.52279,0.11512,0.17653],"force_p95":0.11248,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1376,"mean_force":0.07737,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.51887,0.13377,0.17581]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9731.0,"contact_point_centroid":[0.52591,0.156,0.17867],"force_p95":0.1035,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12955,"mean_force":0.07387,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.52118,0.13742,0.1776]},{"body_a":"world","body_b":"grasp_target","contact_count":1292.0,"contact_point_centroid":[0.58047,0.22117,-0.00204],"force_p95":0.12543,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12816,"mean_force":0.11818,"phase_index":6.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.53874,0.12302,0.34436]},{"body_a":"world","body_b":"grasp_target","contact_count":1948.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47952,0.05403,0.11816]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5343.0,"contact_point_centroid":[0.47013,0.0676,0.03537],"force_p95":0.06494,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09391,"mean_force":0.04147,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47058,0.04835,0.03327]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5082.0,"contact_point_centroid":[0.47031,0.02911,0.0359],"force_p95":0.06614,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08939,"mean_force":0.04279,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47058,0.04835,0.03327]}],"total_contact_groups":14},"final_pose_error":0.0499,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.58047,0.22116,0.01602],"final_tcp_position":[0.50996,0.02778,0.45976],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"phases":[{"n_steps":273.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"approach_object","tcp_end":[0.48317,0.05918,0.1969],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.1712,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":487.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"approach_object","tcp_end":[0.47842,0.04916,0.04132],"tcp_start":[0.48317,0.05918,0.1969],"tcp_to_object_dist_end":0.01589,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48258,0.04837,0.02588],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29033,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","subtask_id":"grasp_lift","tcp_end":[0.47055,0.04834,0.03324],"tcp_start":[0.47842,0.04916,0.04132],"tcp_to_object_dist_end":0.0141,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":321.0,"n_steps_budget":780.0,"object_pos_end":[0.48398,0.0482,0.12612],"object_pos_start":[0.48258,0.04837,0.02588],"object_to_goal_dist_end":0.23045,"object_to_goal_dist_start":0.29033,"object_z_max":0.12585,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","subtask_id":"grasp_lift","tcp_end":[0.46692,0.04796,0.13682],"tcp_start":[0.47055,0.04834,0.03324],"tcp_to_object_dist_end":0.02014,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":748.0,"n_steps_budget":1000.0,"object_pos_end":[0.58207,0.21726,0.19661],"object_pos_start":[0.48398,0.0482,0.12612],"object_to_goal_dist_end":0.03581,"object_to_goal_dist_start":0.23045,"object_z_max":0.19652,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_goal","tcp_end":[0.5724,0.21741,0.21729],"tcp_start":[0.46692,0.04796,0.13682],"tcp_to_object_dist_end":0.02283,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.57934,0.21894,0.00981],"object_pos_start":[0.58207,0.21726,0.19661],"object_to_goal_dist_end":0.22091,"object_to_goal_dist_start":0.03581,"object_z_max":0.19663,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","subtask_id":"reach_goal","tcp_end":[0.56774,0.21567,0.23837],"tcp_start":[0.5724,0.21741,0.21729],"tcp_to_object_dist_end":0.22887,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":323.0,"n_steps_budget":1000.0,"object_pos_end":[0.58047,0.22116,0.01602],"object_pos_start":[0.57934,0.21894,0.00981],"object_to_goal_dist_end":0.21461,"object_to_goal_dist_start":0.22091,"object_z_max":0.01667,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","tcp_end":[0.50996,0.02778,0.45976],"tcp_start":[0.56774,0.21567,0.23837],"tcp_to_object_dist_end":0.48916,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```