## Search State

- **Seed**: 6
- **Iteration**: 14 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 13 | approach → descend → grasp → lift → push → descend | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 10  | 0.3594 | 1.00 | ✅ accepted |
| 12 | approach → descend → grasp → lift → push → descend | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 10  | 0.3340 | 1.00 | ❌ rejected |
| 11 | approach → descend → grasp → lift → push → descend | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 10  | 0.3594 | 1.00 | ❌ rejected |
| 10 | approach → descend → grasp → lift → push → descend | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 10  | 0.3541 | 1.00 | ❌ rejected |
| 9 | approach → descend → grasp → lift → push → descend | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 10  | 0.3594 | 1.00 | ❌ rejected |

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

## Current Skill (Q=0.359) — your mutation base

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

- **Composite score**: 0.359
- **task_score** (E): 1.000
- **fitness_score**: 0.979  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.620

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1256 |
| descend_1 | 1.00 | 1.00 | 0.1486 |
| grasp_1 | 1.00 | 1.00 | 0.0118 |
| lift_1 | 1.00 | 1.00 | 0.2577 |
| transport_1 | 1.00 | 1.00 | 0.1930 |
| descend_2 | 1.00 | 1.00 | 0.0407 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.497, 0.032, 0.183) | (0.500, 0.024, 0.030)→(0.500, 0.024, 0.026) | 0.269→0.271 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.497, 0.032, 0.183)→(0.495, 0.025, 0.035) | (0.500, 0.024, 0.026)→(0.500, 0.024, 0.026) | 0.271→0.271 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.495, 0.025, 0.035)→(0.487, 0.024, 0.026) | (0.500, 0.024, 0.026)→(0.500, 0.024, 0.026) | 0.271→0.272 | 1.00 / 43.000 | 0.138 | 0.199 |
| lift_1 | lift | 1.00 / step_budget | (0.487, 0.024, 0.026)→(0.496, 0.024, 0.283) | (0.500, 0.024, 0.026)→(0.507, 0.024, 0.275) | 0.272→0.213 | 1.00 / 43.000 | 0.070 | 0.643 |
| transport_1 | push | 1.00 / step_budget | (0.496, 0.024, 0.283)→(0.590, 0.184, 0.270) | (0.507, 0.024, 0.275)→(0.601, 0.184, 0.255) | 0.213→0.049 | 1.00 / 28.667 | 55983.968 | 0.160 |
| descend_2 | descend | 1.00 / step_budget | (0.590, 0.184, 0.270)→(0.593, 0.192, 0.230) | (0.601, 0.184, 0.255)→(0.604, 0.191, 0.214) | 0.049→0.010 | 1.00 / 24.667 | 0.117 | 0.289 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.427
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 1.000
- phase_score: 0.422
- phase_breakdown.reach_pre_grasp_score: 0.097
- phase_breakdown.reach_goal_score: 0.561
- grasp_place_fitness: 0.980

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.980
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.359
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.334


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.73853,"average_solve_count":436.0,"average_success_count":436.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.generator.arc_height":0.09752,"approach_1.generator.speed":0.09792,"descend_1.generator.speed":0.01318,"descend_2.generator.speed":0.01385,"descend_2.target.offset.z":0.01665,"grasp_1.duration.max_time":1.67834,"lift_1.generator.speed":0.02798,"lift_1.target.offset_along_axis.distance":0.26862,"transport_1.generator.arc_height":0.06964,"transport_1.generator.speed":0.04424},"optimized_scores":{"best_composite_score":0.35916,"best_fitness_score":0.97916,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":86.0,"contact_point_centroid":[0.49989,-0.01449,-0.00147],"force_p95":0.60548,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.62846,"mean_force":0.23069,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48969,-0.01471,0.02692]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17614.0,"contact_point_centroid":[0.4936,0.00454,0.15445],"force_p95":0.07585,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29524,"mean_force":0.05118,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49363,-0.01462,0.15242]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18003.0,"contact_point_centroid":[0.49344,-0.03376,0.15093],"force_p95":0.07316,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2819,"mean_force":0.05058,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49346,-0.01462,0.14922]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1620.0,"contact_point_centroid":[0.58367,0.19525,0.29107],"force_p95":0.10901,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26424,"mean_force":0.07922,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.57966,0.17628,0.29087]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1847.0,"contact_point_centroid":[0.58349,0.15773,0.2903],"force_p95":0.09282,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25057,"mean_force":0.06577,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.57969,0.17637,0.29037]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50384,-0.01541,-0.00209],"force_p95":0.14875,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.2226,"mean_force":0.12968,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49184,-0.01473,0.02705]},{"body_a":"world","body_b":"grasp_target","contact_count":1816.0,"contact_point_centroid":[0.50382,-0.01567,-0.00192],"force_p95":0.1336,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.1229,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49912,0.01638,0.23735]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4076.0,"contact_point_centroid":[0.4912,0.00448,0.02858],"force_p95":0.07896,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13159,"mean_force":0.05183,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49066,-0.01472,0.02582]},{"body_a":"world","body_b":"grasp_target","contact_count":2072.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49794,-0.01057,0.10679]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12569.0,"contact_point_centroid":[0.53252,0.04058,0.32541],"force_p95":0.0828,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11618,"mean_force":0.05639,"phase_index":4.0,"phase_name":"transport_1","phase_type":"push","tcp_position_centroid":[0.53059,0.05945,0.32439]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10972.0,"contact_point_centroid":[0.5332,0.08004,0.32589],"force_p95":0.091,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10772,"mean_force":0.06349,"phase_index":4.0,"phase_name":"transport_1","phase_type":"push","tcp_position_centroid":[0.53125,0.06099,0.32423]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4953.0,"contact_point_centroid":[0.49125,-0.03384,0.02767],"force_p95":0.07079,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08697,"mean_force":0.04479,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49066,-0.01472,0.02583]}],"total_contact_groups":12},"final_pose_error":0.00986,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.59381,0.18193,0.25441],"final_tcp_position":[0.58203,0.18175,0.27116],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":0.62846,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":455.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1816.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_pre_grasp","tcp_end":[0.49999,-0.00648,0.17975],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.15405,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":518.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2072.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_pre_grasp","tcp_end":[0.49883,-0.01479,0.03446],"tcp_start":[0.49999,-0.00648,0.17975],"tcp_to_object_dist_end":0.00985,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50368,-0.01464,0.02571],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31182,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.14285,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10829.0,"raw_peak_contact_force":0.2226,"tcp_end":[0.49063,-0.01471,0.02579],"tcp_start":[0.49883,-0.01479,0.03446],"tcp_to_object_dist_end":0.01305,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":876.0,"n_steps_budget":1000.0,"object_pos_end":[0.5115,-0.01461,0.26725],"object_pos_start":[0.50368,-0.01464,0.02571],"object_to_goal_dist_end":0.21652,"object_to_goal_dist_start":0.31182,"object_z_max":0.26699,"peak_contact_force":0.06956,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":35703.0,"raw_peak_contact_force":0.62846,"subtask_id":"reach_pre_grasp","tcp_end":[0.50043,-0.0146,0.27479],"tcp_start":[0.49063,-0.01471,0.02579],"tcp_to_object_dist_end":0.0134,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":31.0,"n_steps":708.0,"n_steps_budget":1000.0,"object_pos_end":[0.59067,0.17223,0.29294],"object_pos_start":[0.5115,-0.01461,0.26725],"object_to_goal_dist_end":0.04748,"object_to_goal_dist_start":0.21652,"object_z_max":0.3363,"peak_contact_force":0.08302,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":23541.0,"raw_peak_contact_force":0.11618,"subtask_id":"reach_goal","tcp_end":[0.57902,0.17236,0.30794],"tcp_start":[0.50043,-0.0146,0.27479],"tcp_to_object_dist_end":0.019,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":24.0,"n_steps":126.0,"n_steps_budget":1000.0,"object_pos_end":[0.59381,0.18193,0.25441],"object_pos_start":[0.59067,0.17223,0.29294],"object_to_goal_dist_end":0.01085,"object_to_goal_dist_start":0.04748,"object_z_max":0.29294,"peak_contact_force":0.10928,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3467.0,"raw_peak_contact_force":0.26424,"subtask_id":"reach_goal","tcp_end":[0.58203,0.18175,0.27116],"tcp_start":[0.57902,0.17236,0.30794],"tcp_to_object_dist_end":0.02048,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.08211,"average_solve_count":341.0,"average_success_count":341.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.generator.arc_height":0.06819,"approach_1.generator.speed":0.06787,"descend_1.generator.speed":0.02841,"descend_2.generator.speed":0.03357,"descend_2.target.offset.z":0.0101,"grasp_1.duration.max_time":1.51865,"lift_1.generator.speed":0.03282,"lift_1.target.offset_along_axis.distance":0.27289,"transport_1.generator.arc_height":0.03334,"transport_1.generator.speed":0.10629},"optimized_scores":{"best_composite_score":0.35889,"best_fitness_score":0.97889,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":85.0,"contact_point_centroid":[0.50869,0.03905,-0.00142],"force_p95":0.60389,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.64465,"mean_force":0.23131,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4982,0.03932,0.02662]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1850.0,"contact_point_centroid":[0.61896,0.14552,0.18412],"force_p95":0.09904,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31207,"mean_force":0.07502,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.61693,0.16447,0.18284]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18020.0,"contact_point_centroid":[0.50206,0.05821,0.15265],"force_p95":0.07592,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29136,"mean_force":0.05176,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.50202,0.03906,0.15083]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18177.0,"contact_point_centroid":[0.50234,0.01993,0.15664],"force_p95":0.07449,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29104,"mean_force":0.05104,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.50222,0.03906,0.15458]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2374.0,"contact_point_centroid":[0.61958,0.18331,0.18293],"force_p95":0.08638,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28078,"mean_force":0.06114,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.61697,0.16452,0.18247]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7275.0,"contact_point_centroid":[0.56167,0.0791,0.26198],"force_p95":0.09202,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18401,"mean_force":0.06253,"phase_index":4.0,"phase_name":"transport_1","phase_type":"push","tcp_position_centroid":[0.56009,0.09813,0.26009]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7795.0,"contact_point_centroid":[0.56319,0.11881,0.26038],"force_p95":0.08451,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16327,"mean_force":0.05815,"phase_index":4.0,"phase_name":"transport_1","phase_type":"push","tcp_position_centroid":[0.56158,0.09987,0.25943]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.5125,0.03963,-0.00202],"force_p95":0.13189,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15101,"mean_force":0.12517,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50036,0.03951,0.02688]},{"body_a":"world","body_b":"grasp_target","contact_count":2640.0,"contact_point_centroid":[0.51251,0.03972,-0.00194],"force_p95":0.1296,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12281,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50133,0.05166,0.25618]},{"body_a":"world","body_b":"grasp_target","contact_count":2036.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50636,0.04426,0.10714]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4362.0,"contact_point_centroid":[0.49982,0.02027,0.02806],"force_p95":0.07658,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09912,"mean_force":0.04881,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49917,0.03941,0.02561]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4626.0,"contact_point_centroid":[0.49976,0.05854,0.02768],"force_p95":0.07033,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09326,"mean_force":0.0472,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49917,0.03941,0.02561]}],"total_contact_groups":12},"final_pose_error":0.00982,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.63193,0.16805,0.14733],"final_tcp_position":[0.62055,0.16835,0.16059],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":0.64465,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":661.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2640.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_pre_grasp","tcp_end":[0.50821,0.04855,0.18041],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.1547,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":509.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2036.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_pre_grasp","tcp_end":[0.50742,0.04013,0.03459],"tcp_start":[0.50821,0.04855,0.18041],"tcp_to_object_dist_end":0.00997,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51237,0.0393,0.02589],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21263,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.13018,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10788.0,"raw_peak_contact_force":0.15101,"tcp_end":[0.49914,0.03941,0.02558],"tcp_start":[0.50742,0.04013,0.03459],"tcp_to_object_dist_end":0.01323,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":901.0,"n_steps_budget":1000.0,"object_pos_end":[0.52034,0.03914,0.27164],"object_pos_start":[0.51237,0.0393,0.02589],"object_to_goal_dist_end":0.21289,"object_to_goal_dist_start":0.21263,"object_z_max":0.27139,"peak_contact_force":0.07038,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":36282.0,"raw_peak_contact_force":0.64465,"subtask_id":"reach_pre_grasp","tcp_end":[0.50917,0.03907,0.27923],"tcp_start":[0.49914,0.03941,0.02558],"tcp_to_object_dist_end":0.0135,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":30.0,"n_steps":442.0,"n_steps_budget":1000.0,"object_pos_end":[0.62687,0.16105,0.1942],"object_pos_start":[0.52034,0.03914,0.27164],"object_to_goal_dist_end":0.0505,"object_to_goal_dist_start":0.21289,"object_z_max":0.272,"peak_contact_force":0.0897,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":15070.0,"raw_peak_contact_force":0.18401,"subtask_id":"reach_goal","tcp_end":[0.61552,0.16129,0.20611],"tcp_start":[0.50917,0.03907,0.27923],"tcp_to_object_dist_end":0.01644,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":30.0,"n_steps":141.0,"n_steps_budget":1000.0,"object_pos_end":[0.63193,0.16805,0.14733],"object_pos_start":[0.62687,0.16105,0.1942],"object_to_goal_dist_end":0.00666,"object_to_goal_dist_start":0.0505,"object_z_max":0.1942,"peak_contact_force":0.09632,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4224.0,"raw_peak_contact_force":0.31207,"subtask_id":"reach_goal","tcp_end":[0.62055,0.16835,0.16059],"tcp_start":[0.61552,0.16129,0.20611],"tcp_to_object_dist_end":0.01748,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.10236,"average_solve_count":381.0,"average_success_count":381.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.generator.arc_height":0.0308,"approach_1.generator.speed":0.07693,"descend_1.generator.speed":0.01206,"descend_2.generator.speed":0.03479,"descend_2.target.offset.z":0.0207,"grasp_1.duration.max_time":1.66604,"lift_1.generator.speed":0.03818,"lift_1.target.offset_along_axis.distance":0.29036,"transport_1.generator.arc_height":0.07807,"transport_1.generator.speed":0.05536},"optimized_scores":{"best_composite_score":0.36021,"best_fitness_score":0.98021,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":84.0,"contact_point_centroid":[0.47949,0.04766,-0.00143],"force_p95":0.60091,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.65527,"mean_force":0.17047,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46921,0.04769,0.02778]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18043.0,"contact_point_centroid":[0.47312,0.06665,0.16215],"force_p95":0.07708,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30136,"mean_force":0.05256,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47291,0.04752,0.16026]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1284.0,"contact_point_centroid":[0.57934,0.20263,0.2757],"force_p95":0.13773,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29065,"mean_force":0.09363,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.57547,0.22117,0.27739]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18151.0,"contact_point_centroid":[0.47337,0.02841,0.16588],"force_p95":0.07612,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26941,"mean_force":0.05186,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47307,0.04752,0.16373]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1200.0,"contact_point_centroid":[0.57985,0.23958,0.27581],"force_p95":0.12903,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22511,"mean_force":0.09174,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.57547,0.22116,0.27747]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48271,0.04853,-0.00207],"force_p95":0.14502,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22391,"mean_force":0.1288,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4714,0.04793,0.02781]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10057.0,"contact_point_centroid":[0.52159,0.09955,0.33724],"force_p95":0.10158,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18048,"mean_force":0.06563,"phase_index":4.0,"phase_name":"transport_1","phase_type":"push","tcp_position_centroid":[0.51834,0.11831,0.33685]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9117.0,"contact_point_centroid":[0.52237,0.13875,0.33759],"force_p95":0.10643,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16371,"mean_force":0.07121,"phase_index":4.0,"phase_name":"transport_1","phase_type":"push","tcp_position_centroid":[0.51919,0.11981,0.33692]},{"body_a":"world","body_b":"grasp_target","contact_count":1780.0,"contact_point_centroid":[0.4827,0.04873,-0.00192],"force_p95":0.1336,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.1229,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49136,0.03841,0.25355]},{"body_a":"world","body_b":"grasp_target","contact_count":2212.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47836,0.05066,0.11121]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5044.0,"contact_point_centroid":[0.47009,0.02859,0.02963],"force_p95":0.06755,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10289,"mean_force":0.04289,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47027,0.04782,0.02667]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5439.0,"contact_point_centroid":[0.4699,0.06711,0.02902],"force_p95":0.06695,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08276,"mean_force":0.04124,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47027,0.04782,0.02668]}],"total_contact_groups":12},"final_pose_error":0.00984,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.58727,0.22424,0.23949],"final_tcp_position":[0.57724,0.2244,0.25864],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":167951.73011,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":446.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1780.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_pre_grasp","tcp_end":[0.48147,0.05296,0.18878],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16282,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":553.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2212.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_pre_grasp","tcp_end":[0.47811,0.04862,0.03465],"tcp_start":[0.48147,0.05296,0.18878],"tcp_to_object_dist_end":0.00978,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":47.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48258,0.04789,0.02573],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29075,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.14127,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12283.0,"raw_peak_contact_force":0.22391,"tcp_end":[0.47024,0.04782,0.02664],"tcp_start":[0.47811,0.04862,0.03465],"tcp_to_object_dist_end":0.01237,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":919.0,"n_steps_budget":1000.0,"object_pos_end":[0.49058,0.04765,0.28739],"object_pos_start":[0.48258,0.04789,0.02573],"object_to_goal_dist_end":0.21073,"object_to_goal_dist_start":0.29075,"object_z_max":0.28712,"peak_contact_force":0.06937,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":36278.0,"raw_peak_contact_force":0.65527,"subtask_id":"reach_pre_grasp","tcp_end":[0.47964,0.04763,0.29646],"tcp_start":[0.47024,0.04782,0.02664],"tcp_to_object_dist_end":0.01421,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":649.0,"n_steps_budget":1000.0,"object_pos_end":[0.58541,0.21789,0.27843],"object_pos_start":[0.49058,0.04765,0.28739],"object_to_goal_dist_end":0.04931,"object_to_goal_dist_start":0.21073,"object_z_max":0.34551,"peak_contact_force":167951.73011,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":19174.0,"raw_peak_contact_force":0.18048,"subtask_id":"reach_goal","tcp_end":[0.57492,0.21865,0.29586],"tcp_start":[0.47964,0.04763,0.29646],"tcp_to_object_dist_end":0.02036,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":20.0,"n_steps":110.0,"n_steps_budget":1000.0,"object_pos_end":[0.58727,0.22424,0.23949],"object_pos_start":[0.58541,0.21789,0.27843],"object_to_goal_dist_end":0.01147,"object_to_goal_dist_start":0.04931,"object_z_max":0.27843,"peak_contact_force":0.14391,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2484.0,"raw_peak_contact_force":0.29065,"subtask_id":"reach_goal","tcp_end":[0.57724,0.2244,0.25864],"tcp_start":[0.57492,0.21865,0.29586],"tcp_to_object_dist_end":0.02162,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```