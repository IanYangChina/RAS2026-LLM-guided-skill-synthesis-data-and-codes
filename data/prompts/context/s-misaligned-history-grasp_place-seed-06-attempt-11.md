## Search State

- **Seed**: 6
- **Iteration**: 12 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 11 | approach → descend → grasp → lift → push → descend | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 10  | 0.3594 | 1.00 | ❌ rejected |
| 10 | approach → descend → grasp → lift → push → descend | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 10  | 0.3541 | 1.00 | ❌ rejected |
| 9 | approach → descend → grasp → lift → push → descend | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 10  | 0.3594 | 1.00 | ✅ accepted |
| 8 | approach → descend → grasp → lift → push → descend | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 10  | -0.1048 | 0.29 | ✅ accepted |
| 7 | approach → descend → grasp → lift → push → descend → release → retract | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 11  | 0.3340 | 1.00 | ❌ rejected |

**Proposal policy**: task_score is near-perfect (1.00). Preserve useful working parts and make only evidence-backed refinements. A HOLD is acceptable if you genuinely cannot find a better structure.

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

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 1.000, which indicates the subtask decomposition is already effective.
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

## Current Skill (Q=0.334) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: reach_pre_grasp
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.15
  weight: 0.3
- id: reach_goal
  target_entity: object
  weight: 0.7
phases:
- id: approach_1
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
    - 0.15
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    generator.arc_height:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.arc_height
        mode: replace
    generator.speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_pre_grasp
- id: descend_1
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
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    generator.speed:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_pre_grasp
- id: grasp_1
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
    orientation:
      mode: keep_current
  parameters:
    duration.max_time:
      type: scalar
      range:
      - 0.5
      - 2.0
      default: 1.0
      binds_to:
      - path: duration.max_time
        mode: replace
  guards:
  - id: grasp_check
    when: after_phase
    predicate: bilateral_grasp
    threshold: 0.5
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: repeat
- id: lift_1
  type: lift
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
      distance: 0.25
      axis: world_z
      mode: add_to_offset
      sign: positive
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    generator.speed:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
    target.offset_along_axis.distance:
      type: scalar
      range:
      - 0.15
      - 0.3
      default: 0.25
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
  guards:
  - id: lift_check
    when: after_phase
    predicate: object_lifted
    threshold: 0.1
    on_failure: retry
  retries:
    max_attempts: 1
    strategy: repeat
  subtask_id: reach_pre_grasp
- id: transport_1
  type: push
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.05
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    generator.arc_height:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.arc_height
        mode: replace
    generator.speed:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_goal
- id: descend_2
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.015
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    generator.speed:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
    target.offset.z:
      type: scalar
      range:
      - 0.0
      - 0.03
      default: 0.015
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: reach_goal

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.15], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - generator.arc_height: status=consumed; consumers=generator.arc_height (replace)
    - generator.speed: status=consumed; consumers=generator.speed (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - generator.speed: status=consumed; consumers=generator.speed (replace)
- **grasp_1** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - duration.max_time: status=consumed; consumers=duration.max_time (replace)
  - guards:
    - id=grasp_check, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=0.5
  - retries: max_attempts=2, strategy=repeat
- **lift_1** (`lift`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.25, mode=add_to_offset, sign=positive}, tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - generator.speed: status=consumed; consumers=generator.speed (replace)
    - target.offset_along_axis.distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
  - guards:
    - id=lift_check, when=after_phase, predicate=object_lifted, on_failure=retry, threshold=0.1
  - retries: max_attempts=1, strategy=repeat
- **transport_1** (`push`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.05], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - generator.arc_height: status=consumed; consumers=generator.arc_height (replace)
    - generator.speed: status=consumed; consumers=generator.speed (replace)
- **descend_2** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.015], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - generator.speed: status=consumed; consumers=generator.speed (replace)
    - target.offset.z: status=consumed; consumers=target.offset.z (replace)

## Design Metrics

- **Composite score**: 0.334
- **task_score** (E): 1.000
- **fitness_score**: 0.954  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.620

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.0971 |
| descend_1 | 1.00 | 1.00 | 0.1502 |
| grasp_1 | 1.00 | 1.00 | 0.0154 |
| lift_1 | 1.00 | 1.00 | 0.1953 |
| transport_1 | 1.00 | 1.00 | 0.1782 |
| descend_2 | 1.00 | 0.67 | 0.0361 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.499, 0.039, 0.215) | (0.500, 0.024, 0.030)→(0.500, 0.024, 0.026) | 0.269→0.271 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.499, 0.039, 0.215)→(0.497, 0.028, 0.065) | (0.500, 0.024, 0.026)→(0.500, 0.024, 0.026) | 0.271→0.271 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.497, 0.028, 0.065)→(0.487, 0.027, 0.053) | (0.500, 0.024, 0.026)→(0.500, 0.026, 0.025) | 0.271→0.271 | 1.00 / 28.333 | 0.182 | 0.217 |
| lift_1 | lift | 1.00 / step_budget | (0.487, 0.027, 0.053)→(0.497, 0.026, 0.248) | (0.500, 0.026, 0.025)→(0.504, 0.025, 0.219) | 0.271→0.207 | 1.00 / 22.333 | 0.123 | 0.332 |
| transport_1 | push | 1.00 / step_budget | (0.497, 0.026, 0.248)→(0.583, 0.169, 0.278) | (0.504, 0.025, 0.219)→(0.591, 0.168, 0.245) | 0.207→0.048 | 1.00 / 16.667 | 833.773 | 0.267 |
| descend_2 | descend | 1.00 / step_budget | (0.583, 0.169, 0.278)→(0.588, 0.179, 0.245) | (0.591, 0.168, 0.245)→(0.599, 0.183, 0.203) | 0.048→0.016 | 0.67 / 10.667 | 0.086 | 0.476 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.080
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 1.000
- phase_score: 0.482
- phase_breakdown.reach_pre_grasp_score: 0.276
- phase_breakdown.reach_goal_score: 0.571
- grasp_place_fitness: 0.955

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.955
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.334
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.385


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.20448,"average_solve_count":357.0,"average_success_count":357.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.generator.arc_height":0.04281,"approach_1.generator.speed":0.05733,"descend_1.generator.speed":0.02715,"descend_2.generator.speed":0.03987,"descend_2.target.offset.z":0.02399,"grasp_1.duration.max_time":0.99066,"lift_1.generator.speed":0.03112,"lift_1.target.offset_along_axis.distance":0.25709,"transport_1.generator.arc_height":0.0682,"transport_1.generator.speed":0.10354},"optimized_scores":{"best_composite_score":0.3326,"best_fitness_score":0.9526,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":85.0,"contact_point_centroid":[0.50133,-0.01168,-0.00212],"force_p95":0.35371,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.38888,"mean_force":0.16081,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49012,-0.00906,0.05426]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":74.0,"contact_point_centroid":[0.57789,0.17043,0.30387],"force_p95":0.27246,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.36084,"mean_force":0.09677,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.57185,0.15458,0.30841]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2608.0,"contact_point_centroid":[0.52859,0.02866,0.28789],"force_p95":0.16802,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2959,"mean_force":0.10987,"phase_index":4.0,"phase_name":"transport_1","phase_type":"push","tcp_position_centroid":[0.5255,0.04685,0.29118]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50401,-0.01544,-0.00242],"force_p95":0.27351,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.29365,"mean_force":0.17683,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49221,-0.00904,0.05435]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3052.0,"contact_point_centroid":[0.49428,-0.02849,0.12796],"force_p95":0.1324,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29219,"mean_force":0.08088,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49378,-0.01002,0.1299]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2213.0,"contact_point_centroid":[0.4951,0.00874,0.12998],"force_p95":0.1387,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26104,"mean_force":0.10174,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49401,-0.01005,0.1328]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2619.0,"contact_point_centroid":[0.53214,0.07194,0.29062],"force_p95":0.14799,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23091,"mean_force":0.10602,"phase_index":4.0,"phase_name":"transport_1","phase_type":"push","tcp_position_centroid":[0.52847,0.05364,0.2942]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2622.0,"contact_point_centroid":[0.49087,0.00971,0.04983],"force_p95":0.1147,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15595,"mean_force":0.0871,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49113,-0.00903,0.05322]},{"body_a":"world","body_b":"grasp_target","contact_count":472.0,"contact_point_centroid":[0.50382,-0.01567,-0.00173],"force_p95":0.13805,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12366,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50078,0.01595,0.25915]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3345.0,"contact_point_centroid":[0.49251,-0.02849,0.05066],"force_p95":0.11361,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12739,"mean_force":0.07522,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49116,-0.00903,0.05326]},{"body_a":"world","body_b":"grasp_target","contact_count":704.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50054,0.00246,0.14294]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1.0,"contact_point_centroid":[0.57967,0.13836,0.3029],"force_p95":0.05071,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.05071,"mean_force":0.05071,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.5721,0.15326,0.3103]}],"total_contact_groups":12},"final_pose_error":0.03912,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.59102,0.17168,0.24062],"final_tcp_position":[0.57482,0.16111,0.29838],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":2203.50258,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":119.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12252,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":472.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_pre_grasp","tcp_end":[0.50136,0.01214,0.20833],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.18443,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":176.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":704.0,"raw_peak_contact_force":0.12264,"subtask_id":"reach_pre_grasp","tcp_end":[0.50081,-0.00887,0.06518],"tcp_start":[0.50136,0.01214,0.20833],"tcp_to_object_dist_end":0.03986,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":27.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50385,-0.01178,0.02448],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31081,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.26429,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":7767.0,"raw_peak_contact_force":0.29365,"tcp_end":[0.4911,-0.00903,0.05319],"tcp_start":[0.50081,-0.00887,0.06518],"tcp_to_object_dist_end":0.03153,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":21.0,"n_steps":222.0,"n_steps_budget":1000.0,"object_pos_end":[0.50773,-0.01291,0.20195],"object_pos_start":[0.50385,-0.01178,0.02448],"object_to_goal_dist_end":0.22033,"object_to_goal_dist_start":0.31081,"object_z_max":0.2011,"peak_contact_force":0.12916,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":5350.0,"raw_peak_contact_force":0.38888,"subtask_id":"reach_pre_grasp","tcp_end":[0.50056,-0.01127,0.23197],"tcp_start":[0.4911,-0.00903,0.05319],"tcp_to_object_dist_end":0.0309,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":295.0,"n_steps_budget":1000.0,"object_pos_end":[0.5815,0.15268,0.27328],"object_pos_start":[0.50773,-0.01291,0.20195],"object_to_goal_dist_end":0.04326,"object_to_goal_dist_start":0.22033,"object_z_max":0.29011,"peak_contact_force":2203.50258,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":5227.0,"raw_peak_contact_force":0.2959,"subtask_id":"reach_goal","tcp_end":[0.5721,0.15326,0.3103],"tcp_start":[0.50056,-0.01127,0.23197],"tcp_to_object_dist_end":0.0382,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":28.0,"n_steps_budget":1000.0,"object_pos_end":[0.59102,0.17168,0.24062],"object_pos_start":[0.5815,0.15268,0.27328],"object_to_goal_dist_end":0.01794,"object_to_goal_dist_start":0.04326,"object_z_max":0.27328,"peak_contact_force":0.0,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":75.0,"raw_peak_contact_force":0.36084,"subtask_id":"reach_goal","tcp_end":[0.57482,0.16111,0.29838],"tcp_start":[0.5721,0.15326,0.3103],"tcp_to_object_dist_end":0.06092,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.18551,"average_solve_count":345.0,"average_success_count":345.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.generator.arc_height":0.09245,"approach_1.generator.speed":0.06493,"descend_1.generator.speed":0.04245,"descend_2.generator.speed":0.03078,"descend_2.target.offset.z":0.00046,"grasp_1.duration.max_time":1.6603,"lift_1.generator.speed":0.0435,"lift_1.target.offset_along_axis.distance":0.29272,"transport_1.generator.arc_height":0.05252,"transport_1.generator.speed":0.11103},"optimized_scores":{"best_composite_score":0.33446,"best_fitness_score":0.95446,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"left_finger","body_b":"grasp_target","contact_count":601.0,"contact_point_centroid":[0.61468,0.13893,0.20469],"force_p95":0.18325,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.49729,"mean_force":0.11844,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.61198,0.15716,0.20813]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":592.0,"contact_point_centroid":[0.61448,0.17525,0.20434],"force_p95":0.19429,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3758,"mean_force":0.11217,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.61201,0.15719,0.20798]},{"body_a":"world","body_b":"grasp_target","contact_count":76.0,"contact_point_centroid":[0.50949,0.0405,-0.00165],"force_p95":0.29318,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.31245,"mean_force":0.16499,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49802,0.04102,0.05341]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2661.0,"contact_point_centroid":[0.55743,0.07369,0.26694],"force_p95":0.19,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29635,"mean_force":0.09039,"phase_index":4.0,"phase_name":"transport_1","phase_type":"push","tcp_position_centroid":[0.5564,0.09217,0.26895]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3185.0,"contact_point_centroid":[0.50322,0.05933,0.14454],"force_p95":0.12552,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28528,"mean_force":0.08739,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.5023,0.04067,0.14677]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2230.0,"contact_point_centroid":[0.56151,0.11431,0.26464],"force_p95":0.18288,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27927,"mean_force":0.09898,"phase_index":4.0,"phase_name":"transport_1","phase_type":"push","tcp_position_centroid":[0.55977,0.09601,0.2679]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3456.0,"contact_point_centroid":[0.50259,0.02206,0.14628],"force_p95":0.12686,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27465,"mean_force":0.08338,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.50241,0.04067,0.14846]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51255,0.03981,-0.00212],"force_p95":0.15598,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.20995,"mean_force":0.13118,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50003,0.04121,0.05373]},{"body_a":"world","body_b":"grasp_target","contact_count":504.0,"contact_point_centroid":[0.51251,0.03972,-0.00175],"force_p95":0.13797,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12359,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50262,0.03304,0.26772]},{"body_a":"world","body_b":"grasp_target","contact_count":708.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50727,0.0466,0.14518]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2779.0,"contact_point_centroid":[0.50001,0.05987,0.05003],"force_p95":0.09913,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11696,"mean_force":0.07302,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49893,0.04112,0.05256]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3575.0,"contact_point_centroid":[0.50022,0.02224,0.05081],"force_p95":0.09191,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09443,"mean_force":0.05908,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49894,0.04112,0.05257]}],"total_contact_groups":12},"final_pose_error":0.03947,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.62586,0.16196,0.14917],"final_tcp_position":[0.61693,0.16225,0.18208],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":297.6788,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":127.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12259,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":504.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_pre_grasp","tcp_end":[0.50702,0.0509,0.21714],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.19153,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":177.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":708.0,"raw_peak_contact_force":0.12264,"subtask_id":"reach_pre_grasp","tcp_end":[0.50878,0.04201,0.06506],"tcp_start":[0.50702,0.0509,0.21714],"tcp_to_object_dist_end":0.03928,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":31.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51246,0.04066,0.02558],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21191,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.15195,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":8154.0,"raw_peak_contact_force":0.20995,"tcp_end":[0.4989,0.04112,0.05253],"tcp_start":[0.50878,0.04201,0.06506],"tcp_to_object_dist_end":0.03016,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":262.0,"n_steps_budget":1000.0,"object_pos_end":[0.51739,0.04022,0.23902],"object_pos_start":[0.51246,0.04066,0.02558],"object_to_goal_dist_end":0.19616,"object_to_goal_dist_start":0.21191,"object_z_max":0.23816,"peak_contact_force":0.11465,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":6717.0,"raw_peak_contact_force":0.31245,"subtask_id":"reach_pre_grasp","tcp_end":[0.5097,0.04053,0.26853],"tcp_start":[0.4989,0.04112,0.05253],"tcp_to_object_dist_end":0.0305,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":212.0,"n_steps_budget":1000.0,"object_pos_end":[0.61659,0.15332,0.19398],"object_pos_start":[0.51739,0.04022,0.23902],"object_to_goal_dist_end":0.05372,"object_to_goal_dist_start":0.19616,"object_z_max":0.24984,"peak_contact_force":297.6788,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":4891.0,"raw_peak_contact_force":0.29635,"subtask_id":"reach_goal","tcp_end":[0.61115,0.15456,0.22599],"tcp_start":[0.5097,0.04053,0.26853],"tcp_to_object_dist_end":0.0325,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":16.0,"n_steps":63.0,"n_steps_budget":1000.0,"object_pos_end":[0.62586,0.16196,0.14917],"object_pos_start":[0.61659,0.15332,0.19398],"object_to_goal_dist_end":0.01147,"object_to_goal_dist_start":0.05372,"object_z_max":0.19398,"peak_contact_force":0.12833,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1193.0,"raw_peak_contact_force":0.49729,"subtask_id":"reach_goal","tcp_end":[0.61693,0.16225,0.18208],"tcp_start":[0.61115,0.15456,0.22599],"tcp_to_object_dist_end":0.0341,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.70667,"average_solve_count":525.0,"average_success_count":525.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.generator.arc_height":0.04025,"approach_1.generator.speed":0.023,"descend_1.generator.speed":0.0412,"descend_2.generator.speed":0.01453,"descend_2.target.offset.z":0.0011,"grasp_1.duration.max_time":1.6861,"lift_1.generator.speed":0.02014,"lift_1.target.offset_along_axis.distance":0.26757,"transport_1.generator.arc_height":0.06636,"transport_1.generator.speed":0.04792},"optimized_scores":{"best_composite_score":0.33488,"best_fitness_score":0.95488,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"right_finger","body_b":"grasp_target","contact_count":840.0,"contact_point_centroid":[0.57138,0.22302,0.2745],"force_p95":0.15226,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.56849,"mean_force":0.12258,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.56695,0.20482,0.27837]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":871.0,"contact_point_centroid":[0.57096,0.18662,0.27541],"force_p95":0.15155,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.43302,"mean_force":0.11675,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.56686,0.20463,0.27895]},{"body_a":"world","body_b":"grasp_target","contact_count":74.0,"contact_point_centroid":[0.47955,0.04851,-0.00157],"force_p95":0.27801,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.29544,"mean_force":0.15254,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47139,0.04881,0.05461]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3005.0,"contact_point_centroid":[0.47469,0.06696,0.13511],"force_p95":0.12385,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27623,"mean_force":0.0826,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47446,0.04849,0.13767]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2761.0,"contact_point_centroid":[0.47409,0.02975,0.13535],"force_p95":0.13181,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27489,"mean_force":0.08785,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47444,0.04849,0.13733]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3338.0,"contact_point_centroid":[0.51474,0.091,0.2927],"force_p95":0.12375,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2101,"mean_force":0.08367,"phase_index":4.0,"phase_name":"transport_1","phase_type":"push","tcp_position_centroid":[0.51444,0.10948,0.29559]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3095.0,"contact_point_centroid":[0.51508,0.12752,0.29209],"force_p95":0.12808,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19937,"mean_force":0.08878,"phase_index":4.0,"phase_name":"transport_1","phase_type":"push","tcp_position_centroid":[0.51416,0.10896,0.29524]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.4827,0.04869,-0.00202],"force_p95":0.1293,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.14661,"mean_force":0.12459,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4733,0.04902,0.05497]},{"body_a":"world","body_b":"grasp_target","contact_count":560.0,"contact_point_centroid":[0.4827,0.04873,-0.00177],"force_p95":0.13791,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.1235,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49531,0.0312,0.27097]},{"body_a":"world","body_b":"grasp_target","contact_count":720.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.48456,0.05266,0.14652]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2687.0,"contact_point_centroid":[0.47125,0.0301,0.05142],"force_p95":0.10015,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10054,"mean_force":0.07554,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47226,0.04891,0.05393]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2918.0,"contact_point_centroid":[0.47188,0.06753,0.05087],"force_p95":0.09217,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09247,"mean_force":0.07021,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47226,0.04891,0.05393]}],"total_contact_groups":12},"final_pose_error":0.02717,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.58107,0.21451,0.21899],"final_tcp_position":[0.57275,0.21495,0.25306],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":0.56849,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":141.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12264,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":560.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_pre_grasp","tcp_end":[0.48788,0.05528,0.21873],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.19289,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":180.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":720.0,"raw_peak_contact_force":0.12264,"subtask_id":"reach_pre_grasp","tcp_end":[0.48169,0.04986,0.06525],"tcp_start":[0.48788,0.05528,0.21873],"tcp_to_object_dist_end":0.03926,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":27.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48261,0.04866,0.02591],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29013,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12926,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":7405.0,"raw_peak_contact_force":0.14661,"tcp_end":[0.47223,0.04891,0.0539],"tcp_start":[0.48169,0.04986,0.06525],"tcp_to_object_dist_end":0.02985,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":232.0,"n_steps_budget":1000.0,"object_pos_end":[0.48564,0.04814,0.21536],"object_pos_start":[0.48261,0.04866,0.02591],"object_to_goal_dist_end":0.2053,"object_to_goal_dist_start":0.29013,"object_z_max":0.21449,"peak_contact_force":0.12606,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":5840.0,"raw_peak_contact_force":0.29544,"subtask_id":"reach_pre_grasp","tcp_end":[0.48017,0.04845,0.24429],"tcp_start":[0.47223,0.04891,0.0539],"tcp_to_object_dist_end":0.02945,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":18.0,"n_steps":286.0,"n_steps_budget":1000.0,"object_pos_end":[0.57407,0.19794,0.2664],"object_pos_start":[0.48564,0.04814,0.21536],"object_to_goal_dist_end":0.04803,"object_to_goal_dist_start":0.2053,"object_z_max":0.28767,"peak_contact_force":0.13899,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":6433.0,"raw_peak_contact_force":0.2101,"subtask_id":"reach_goal","tcp_end":[0.56474,0.19839,0.29827],"tcp_start":[0.48017,0.04845,0.24429],"tcp_to_object_dist_end":0.03321,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":16.0,"n_steps":105.0,"n_steps_budget":1000.0,"object_pos_end":[0.58107,0.21451,0.21899],"object_pos_start":[0.57407,0.19794,0.2664],"object_to_goal_dist_end":0.01841,"object_to_goal_dist_start":0.04803,"object_z_max":0.2664,"peak_contact_force":0.13026,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1711.0,"raw_peak_contact_force":0.56849,"subtask_id":"reach_goal","tcp_end":[0.57275,0.21495,0.25306],"tcp_start":[0.56474,0.19839,0.29827],"tcp_to_object_dist_end":0.03508,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```