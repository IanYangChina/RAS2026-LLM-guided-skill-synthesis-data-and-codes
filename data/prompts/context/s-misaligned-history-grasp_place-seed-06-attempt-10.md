## Search State

- **Seed**: 6
- **Iteration**: 11 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 10 | approach → descend → grasp → lift → push → descend | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 10  | 0.3541 | 1.00 | ❌ rejected |
| 9 | approach → descend → grasp → lift → push → descend | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 10  | 0.3594 | 1.00 | ✅ accepted |
| 8 | approach → descend → grasp → lift → push → descend | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 10  | -0.1048 | 0.29 | ✅ accepted |
| 7 | approach → descend → grasp → lift → push → descend → release → retract | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 11  | -0.1416 | 0.25 | ❌ rejected |
| 6 | align → lift → push → approach → approach → descend → grasp → rotate | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | arc_cartesian | linear_cartesian | — | impedance_motion | position_control | position_control | impedance_control | force_threshold_switch | position_control | admittance_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 6  | 0.3594 | 1.00 | ❌ rejected |

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
| approach_1 | 1.00 | 1.00 | 0.1249 |
| descend_1 | 1.00 | 1.00 | 0.1494 |
| grasp_1 | 1.00 | 1.00 | 0.0118 |
| lift_1 | 1.00 | 1.00 | 0.2265 |
| transport_1 | 1.00 | 1.00 | 0.1886 |
| descend_2 | 1.00 | 1.00 | 0.0374 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.497, 0.032, 0.184) | (0.500, 0.024, 0.030)→(0.500, 0.024, 0.026) | 0.269→0.271 | 1.00 / 4.000 | 6.758 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.497, 0.032, 0.184)→(0.495, 0.025, 0.035) | (0.500, 0.024, 0.026)→(0.500, 0.024, 0.026) | 0.271→0.271 | 1.00 / 4.000 | 35.130 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.495, 0.025, 0.035)→(0.487, 0.024, 0.026) | (0.500, 0.024, 0.026)→(0.500, 0.024, 0.026) | 0.271→0.272 | 1.00 / 43.000 | 0.137 | 0.202 |
| lift_1 | lift | 1.00 / step_budget | (0.487, 0.024, 0.026)→(0.496, 0.024, 0.252) | (0.500, 0.024, 0.026)→(0.507, 0.024, 0.245) | 0.272→0.205 | 1.00 / 41.000 | 0.074 | 0.628 |
| transport_1 | push | 1.00 / step_budget | (0.496, 0.024, 0.252)→(0.588, 0.181, 0.264) | (0.507, 0.024, 0.245)→(0.601, 0.181, 0.250) | 0.205→0.045 | 1.00 / 29.000 | 0.100 | 0.143 |
| descend_2 | descend | 1.00 / step_budget | (0.588, 0.181, 0.264)→(0.593, 0.190, 0.228) | (0.601, 0.181, 0.250)→(0.605, 0.190, 0.212) | 0.045→0.012 | 1.00 / 25.333 | 0.126 | 0.357 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.164
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 1.000
- phase_score: 0.469
- phase_breakdown.reach_pre_grasp_score: 0.253
- phase_breakdown.reach_goal_score: 0.562
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
- **Final σ (mean)**: 0.349


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.86977,"average_solve_count":430.0,"average_success_count":430.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.generator.arc_height":0.02722,"approach_1.generator.speed":0.06629,"descend_1.generator.speed":0.01083,"descend_2.generator.speed":0.01018,"descend_2.target.offset.z":0.01618,"grasp_1.duration.max_time":0.94947,"lift_1.generator.speed":0.03257,"lift_1.target.offset_along_axis.distance":0.25192,"transport_1.generator.arc_height":0.05634,"transport_1.generator.speed":0.06913},"optimized_scores":{"best_composite_score":0.35917,"best_fitness_score":0.97917,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":87.0,"contact_point_centroid":[0.49966,-0.01429,-0.00148],"force_p95":0.58474,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.61143,"mean_force":0.23517,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48968,-0.01478,0.02678]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1222.0,"contact_point_centroid":[0.58282,0.19321,0.28546],"force_p95":0.17033,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.43322,"mean_force":0.09872,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.57879,0.17467,0.28754]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1368.0,"contact_point_centroid":[0.58276,0.15652,0.28534],"force_p95":0.14718,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.39369,"mean_force":0.09122,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.57877,0.17463,0.28756]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16527.0,"contact_point_centroid":[0.49346,0.00447,0.14535],"force_p95":0.07527,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28649,"mean_force":0.05106,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49352,-0.01469,0.14332]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16863.0,"contact_point_centroid":[0.49329,-0.03383,0.14219],"force_p95":0.07301,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27314,"mean_force":0.05052,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49336,-0.01469,0.14047]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50383,-0.01541,-0.00208],"force_p95":0.14654,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22073,"mean_force":0.12915,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49184,-0.0148,0.02698]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10640.0,"contact_point_centroid":[0.53425,0.04301,0.30669],"force_p95":0.08933,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16024,"mean_force":0.06156,"phase_index":4.0,"phase_name":"transport_1","phase_type":"push","tcp_position_centroid":[0.53129,0.06172,0.30613]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8911.0,"contact_point_centroid":[0.53332,0.07875,0.30662],"force_p95":0.10968,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15893,"mean_force":0.07264,"phase_index":4.0,"phase_name":"transport_1","phase_type":"push","tcp_position_centroid":[0.53043,0.05975,0.30549]},{"body_a":"world","body_b":"grasp_target","contact_count":1660.0,"contact_point_centroid":[0.50382,-0.01567,-0.00192],"force_p95":0.13462,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12292,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49902,0.01023,0.23977]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4078.0,"contact_point_centroid":[0.49121,0.00441,0.02851],"force_p95":0.07855,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13019,"mean_force":0.05183,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49066,-0.01479,0.02576]},{"body_a":"world","body_b":"grasp_target","contact_count":2112.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49793,-0.0109,0.10813]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4944.0,"contact_point_centroid":[0.49124,-0.0339,0.02761],"force_p95":0.07052,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08973,"mean_force":0.04481,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49067,-0.01479,0.02576]}],"total_contact_groups":12},"final_pose_error":0.00999,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.59383,0.18107,0.25076],"final_tcp_position":[0.58159,0.18092,0.26968],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":0.61143,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":416.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1660.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_pre_grasp","tcp_end":[0.49997,-0.00706,0.18273],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.15699,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":528.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2112.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_pre_grasp","tcp_end":[0.49883,-0.01486,0.03439],"tcp_start":[0.49997,-0.00706,0.18273],"tcp_to_object_dist_end":0.00978,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50369,-0.0147,0.02573],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31184,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.14106,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10822.0,"raw_peak_contact_force":0.22073,"tcp_end":[0.49063,-0.01478,0.02573],"tcp_start":[0.49883,-0.01486,0.03439],"tcp_to_object_dist_end":0.01305,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":819.0,"n_steps_budget":1000.0,"object_pos_end":[0.51144,-0.01468,0.25139],"object_pos_start":[0.50369,-0.0147,0.02573],"object_to_goal_dist_end":0.21578,"object_to_goal_dist_start":0.31184,"object_z_max":0.25112,"peak_contact_force":0.06961,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":33477.0,"raw_peak_contact_force":0.61143,"subtask_id":"reach_pre_grasp","tcp_end":[0.50022,-0.01466,0.25818],"tcp_start":[0.49063,-0.01478,0.02573],"tcp_to_object_dist_end":0.01312,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":24.0,"n_steps":650.0,"n_steps_budget":1000.0,"object_pos_end":[0.59229,0.17037,0.28763],"object_pos_start":[0.51144,-0.01468,0.25139],"object_to_goal_dist_end":0.04338,"object_to_goal_dist_start":0.21578,"object_z_max":0.31543,"peak_contact_force":0.11293,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":19551.0,"raw_peak_contact_force":0.16024,"subtask_id":"reach_goal","tcp_end":[0.57808,0.17032,0.30287],"tcp_start":[0.50022,-0.01466,0.25818],"tcp_to_object_dist_end":0.02083,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":18.0,"n_steps":124.0,"n_steps_budget":1000.0,"object_pos_end":[0.59383,0.18107,0.25076],"object_pos_start":[0.59229,0.17037,0.28763],"object_to_goal_dist_end":0.00978,"object_to_goal_dist_start":0.04338,"object_z_max":0.28763,"peak_contact_force":0.17037,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2590.0,"raw_peak_contact_force":0.43322,"subtask_id":"reach_goal","tcp_end":[0.58159,0.18092,0.26968],"tcp_start":[0.57808,0.17032,0.30287],"tcp_to_object_dist_end":0.02253,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.98295,"average_solve_count":352.0,"average_success_count":352.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.generator.arc_height":0.06451,"approach_1.generator.speed":0.03995,"descend_1.generator.speed":0.02413,"descend_2.generator.speed":0.03997,"descend_2.target.offset.z":0.00614,"grasp_1.duration.max_time":0.95063,"lift_1.generator.speed":0.05432,"lift_1.target.offset_along_axis.distance":0.24356,"transport_1.generator.arc_height":0.03955,"transport_1.generator.speed":0.08593},"optimized_scores":{"best_composite_score":0.35889,"best_fitness_score":0.97889,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":84.0,"contact_point_centroid":[0.50977,0.03927,-0.00139],"force_p95":0.55887,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.66885,"mean_force":0.17401,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49812,0.03931,0.0266]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1830.0,"contact_point_centroid":[0.62028,0.1455,0.18071],"force_p95":0.11689,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32367,"mean_force":0.08429,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.61684,0.16442,0.18083]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2383.0,"contact_point_centroid":[0.62061,0.1831,0.18049],"force_p95":0.09095,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3106,"mean_force":0.0634,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.61688,0.16447,0.18043]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":14766.0,"contact_point_centroid":[0.50256,0.05815,0.13681],"force_p95":0.07943,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30322,"mean_force":0.05559,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.50179,0.03905,0.1346]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14910.0,"contact_point_centroid":[0.50278,0.01999,0.14025],"force_p95":0.07823,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30132,"mean_force":0.05484,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.50197,0.03905,0.13794]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7259.0,"contact_point_centroid":[0.56111,0.07816,0.24856],"force_p95":0.0954,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17009,"mean_force":0.06411,"phase_index":4.0,"phase_name":"transport_1","phase_type":"push","tcp_position_centroid":[0.55873,0.09704,0.24769]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.5125,0.03956,-0.00203],"force_p95":0.13183,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.16035,"mean_force":0.12533,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50036,0.03952,0.02678]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7192.0,"contact_point_centroid":[0.56341,0.11831,0.24759],"force_p95":0.09188,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15496,"mean_force":0.0651,"phase_index":4.0,"phase_name":"transport_1","phase_type":"push","tcp_position_centroid":[0.56079,0.09938,0.2466]},{"body_a":"world","body_b":"grasp_target","contact_count":3024.0,"contact_point_centroid":[0.51251,0.03972,-0.00195],"force_p95":0.12817,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12279,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50115,0.053,0.25707]},{"body_a":"world","body_b":"grasp_target","contact_count":2040.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50638,0.0443,0.10665]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4112.0,"contact_point_centroid":[0.49978,0.02023,0.0283],"force_p95":0.07655,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11342,"mean_force":0.0517,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49917,0.03942,0.0255]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4884.0,"contact_point_centroid":[0.4998,0.0585,0.02729],"force_p95":0.06871,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08889,"mean_force":0.04481,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49917,0.03942,0.02551]}],"total_contact_groups":12},"final_pose_error":0.00992,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.63358,0.16811,0.14171],"final_tcp_position":[0.62058,0.16842,0.1569],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":81.14225,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":757.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":20.02908,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3024.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_pre_grasp","tcp_end":[0.50825,0.04862,0.17943],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.15373,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":510.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":81.14225,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2040.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_pre_grasp","tcp_end":[0.50743,0.04014,0.03448],"tcp_start":[0.50825,0.04862,0.17943],"tcp_to_object_dist_end":0.00988,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51237,0.03929,0.02588],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21264,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12927,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10796.0,"raw_peak_contact_force":0.16035,"tcp_end":[0.49914,0.03942,0.02547],"tcp_start":[0.50743,0.04014,0.03448],"tcp_to_object_dist_end":0.01323,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":795.0,"n_steps_budget":1000.0,"object_pos_end":[0.52067,0.03908,0.24195],"object_pos_start":[0.51237,0.03929,0.02588],"object_to_goal_dist_end":0.19654,"object_to_goal_dist_start":0.21264,"object_z_max":0.24169,"peak_contact_force":0.08074,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":29760.0,"raw_peak_contact_force":0.66885,"subtask_id":"reach_pre_grasp","tcp_end":[0.50878,0.03904,0.24984],"tcp_start":[0.49914,0.03942,0.02547],"tcp_to_object_dist_end":0.01427,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":29.0,"n_steps":461.0,"n_steps_budget":1000.0,"object_pos_end":[0.62821,0.16094,0.19192],"object_pos_start":[0.52067,0.03908,0.24195],"object_to_goal_dist_end":0.04831,"object_to_goal_dist_start":0.19654,"object_z_max":0.2485,"peak_contact_force":0.097,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":14451.0,"raw_peak_contact_force":0.17009,"subtask_id":"reach_goal","tcp_end":[0.61538,0.16117,0.20546],"tcp_start":[0.50878,0.03904,0.24984],"tcp_to_object_dist_end":0.01865,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":28.0,"n_steps":149.0,"n_steps_budget":1000.0,"object_pos_end":[0.63358,0.16811,0.14171],"object_pos_start":[0.62821,0.16094,0.19192],"object_to_goal_dist_end":0.00816,"object_to_goal_dist_start":0.04831,"object_z_max":0.19192,"peak_contact_force":0.11834,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4213.0,"raw_peak_contact_force":0.32367,"subtask_id":"reach_goal","tcp_end":[0.62058,0.16842,0.1569],"tcp_start":[0.61538,0.16117,0.20546],"tcp_to_object_dist_end":0.01999,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.75877,"average_solve_count":456.0,"average_success_count":456.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.generator.arc_height":0.03105,"approach_1.generator.speed":0.09208,"descend_1.generator.speed":0.02696,"descend_2.generator.speed":0.01034,"descend_2.target.offset.z":0.02386,"grasp_1.duration.max_time":1.96078,"lift_1.generator.speed":0.03096,"lift_1.target.offset_along_axis.distance":0.24248,"transport_1.generator.arc_height":0.04667,"transport_1.generator.speed":0.03666},"optimized_scores":{"best_composite_score":0.3602,"best_fitness_score":0.9802,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":86.0,"contact_point_centroid":[0.47873,0.04762,-0.00147],"force_p95":0.58269,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.6042,"mean_force":0.23881,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46933,0.04772,0.02775]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1526.0,"contact_point_centroid":[0.57481,0.23555,0.27229],"force_p95":0.09134,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31338,"mean_force":0.06946,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.57239,0.21648,0.27119]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":15650.0,"contact_point_centroid":[0.47272,0.06669,0.13971],"force_p95":0.07287,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27812,"mean_force":0.05067,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47279,0.04751,0.13802]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1746.0,"contact_point_centroid":[0.57476,0.19776,0.27178],"force_p95":0.0853,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26607,"mean_force":0.06117,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.57238,0.21648,0.27119]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16052.0,"contact_point_centroid":[0.4725,0.02835,0.13955],"force_p95":0.07178,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24868,"mean_force":0.04908,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47277,0.04751,0.13779]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48271,0.04853,-0.00207],"force_p95":0.1448,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22379,"mean_force":0.12877,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4714,0.04794,0.02786]},{"body_a":"world","body_b":"grasp_target","contact_count":1748.0,"contact_point_centroid":[0.4827,0.04873,-0.00192],"force_p95":0.13393,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12291,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49138,0.03857,0.25363]},{"body_a":"world","body_b":"grasp_target","contact_count":2216.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47835,0.0507,0.11127]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5045.0,"contact_point_centroid":[0.47009,0.0286,0.02969],"force_p95":0.06752,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10296,"mean_force":0.04289,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47027,0.04783,0.02673]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12031.0,"contact_point_centroid":[0.51692,0.1356,0.28897],"force_p95":0.07791,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09858,"mean_force":0.05291,"phase_index":4.0,"phase_name":"transport_1","phase_type":"push","tcp_position_centroid":[0.51642,0.11639,0.28744]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13501.0,"contact_point_centroid":[0.51811,0.09995,0.28982],"force_p95":0.0715,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09593,"mean_force":0.04746,"phase_index":4.0,"phase_name":"transport_1","phase_type":"push","tcp_position_centroid":[0.5179,0.119,0.28838]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5438.0,"contact_point_centroid":[0.4699,0.06711,0.02908],"force_p95":0.06692,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08288,"mean_force":0.04124,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47027,0.04783,0.02673]}],"total_contact_groups":12},"final_pose_error":0.00993,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.58697,0.22193,0.24483],"final_tcp_position":[0.57562,0.22193,0.25775],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":24.12366,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":438.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1748.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_pre_grasp","tcp_end":[0.48145,0.05303,0.18893],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16298,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":554.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":24.12366,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2216.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_pre_grasp","tcp_end":[0.47811,0.04863,0.03471],"tcp_start":[0.48145,0.05303,0.18893],"tcp_to_object_dist_end":0.00983,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":47.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48258,0.04789,0.02573],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29074,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.14108,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12283.0,"raw_peak_contact_force":0.22379,"tcp_end":[0.47024,0.04782,0.0267],"tcp_start":[0.47811,0.04863,0.03471],"tcp_to_object_dist_end":0.01238,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":764.0,"n_steps_budget":1000.0,"object_pos_end":[0.48968,0.04763,0.24197],"object_pos_start":[0.48258,0.04789,0.02573],"object_to_goal_dist_end":0.20366,"object_to_goal_dist_start":0.29074,"object_z_max":0.2417,"peak_contact_force":0.07021,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":31788.0,"raw_peak_contact_force":0.6042,"subtask_id":"reach_pre_grasp","tcp_end":[0.47906,0.0476,0.24867],"tcp_start":[0.47024,0.04782,0.0267],"tcp_to_object_dist_end":0.01255,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":34.0,"n_steps":637.0,"n_steps_budget":1000.0,"object_pos_end":[0.58191,0.21265,0.27159],"object_pos_start":[0.48968,0.04763,0.24197],"object_to_goal_dist_end":0.04418,"object_to_goal_dist_start":0.20366,"object_z_max":0.29465,"peak_contact_force":0.08905,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":25532.0,"raw_peak_contact_force":0.09858,"subtask_id":"reach_goal","tcp_end":[0.57123,0.21263,0.28363],"tcp_start":[0.47906,0.0476,0.24867],"tcp_to_object_dist_end":0.0161,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":30.0,"n_steps":106.0,"n_steps_budget":1000.0,"object_pos_end":[0.58697,0.22193,0.24483],"object_pos_start":[0.58191,0.21265,0.27159],"object_to_goal_dist_end":0.01673,"object_to_goal_dist_start":0.04418,"object_z_max":0.27159,"peak_contact_force":0.08975,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3272.0,"raw_peak_contact_force":0.31338,"subtask_id":"reach_goal","tcp_end":[0.57562,0.22193,0.25775],"tcp_start":[0.57123,0.21263,0.28363],"tcp_to_object_dist_end":0.0172,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```