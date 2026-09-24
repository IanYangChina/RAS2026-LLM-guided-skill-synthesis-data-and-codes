## Search State

- **Seed**: 6
- **Iteration**: 14 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 13 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | impedance_control | position_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 9 | -0.3601 | 0.08 | ❌ rejected |
| 12 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | impedance_control | impedance_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 9 | 0.0033 | 0.31 | ❌ rejected |
| 11 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | impedance_control | impedance_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 9 | 0.0036 | 0.31 | ❌ rejected |
| 10 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | impedance_control | impedance_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 9 | 0.0038 | 0.31 | ✅ accepted |
| 9 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | force_threshold_switch | position_control | impedance_control | position_control | impedance_control | position_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 10 | -0.3346 | 0.17 | ❌ rejected |

**Proposal policy**: task_score is 0.08 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen object start: [0.5869067239795378, 0.18744967655878825, 0.24811674852797]
- Frozen task target: [0.5, 0.0, 0.3]
- Goal object position: (0.5, 0.0, 0.3)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.5, 0.0, 0.3)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.5869067239795378, 0.18744967655878825, 0.24811674852797)
- Goal tolerance: 0.02 m
- Expressivity sigma: 0.15 m
- Expressivity threshold: 0.3
- Force limit: 20.0 N
- Robot initial TCP position: (0.5038164351471943, -0.015672913018666156, 0.03)
- Robot initial gripper state: **open** (gripper starts fully open; ensure a `grasp`/`force_grasp` phase closes it before lifting)
- Phase navigation guidance: the task `phase_target_map` may provide internal predefined TCP waypoint aliases / semantic phase ids. These names are not DSL phase types and are intentionally not enumerated here to avoid confusing ids with types. Phase `id` may be semantic, but phase `type` must be exactly one of the DSL enum values listed in the prompt.
- Primary evaluation target: **final object-to-realised-airborne-3D-target proximity. Grasp/lift signals are optimiser fitness diagnostics only; they do not gate the canonical task_score.**

## Scene Entities

robot:
  model: panda_full
  tcp_site: attachment_site
  gripper: franka_hand
  tcp_initial_world: [0.5038164351471943, -0.015672913018666156, 0.03]
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
  frozen_object_starts: {'grasp_target': [0.5869067239795378, 0.18744967655878825, 0.24811674852797]}
  frozen_targets: {'place_target': [0.5, 0.0, 0.3]}
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
| `object` | offset from object initial position (0.5869067239795378, 0.18744967655878825, 0.24811674852797) | approach/contact targets near object start |
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

## Current Skill (Q=-0.360) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: reach_object
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.15
  weight: 0.2
- id: grasp_success
  anchor: object
  metric: contact
  weight: 0.2
- id: lift_clearance
  anchor: object
  target_entity: object
  metric: goal_progress
  offset:
  - 0.0
  - 0.0
  - 0.15
  weight: 0.2
- id: transport_accuracy
  offset:
  - 0.0
  - 0.0
  - 0.15
  weight: 0.2
- id: place_accuracy
  offset:
  - 0.0
  - 0.0
  - 0.03
  weight: 0.2
phases:
- id: approach_object
  type: approach
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
    - 0.15
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: contact_before_approach
    when: before_phase
    predicate: contact_detected
    threshold: 1.0
    on_failure: continue
  subtask_id: reach_object
- id: descend_grasp
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
    - 0.0
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    grasp_z_offset:
      type: scalar
      range:
      - -0.01
      - 0.01
      default: 0.0
      binds_to:
      - path: target.offset.z
        mode: add
  subtask_id: grasp_success
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
  parameters:
    grasp_duration:
      type: scalar
      range:
      - 0.5
      - 2.0
      default: 1.0
      binds_to:
      - path: duration.max_time
        mode: replace
  guards:
  - id: bilateral_grasp_check
    when: after_phase
    predicate: bilateral_grasp
    threshold: 0.5
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - -0.005
  subtask_id: grasp_success
- id: lift_1
  type: lift
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.2
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.08
      - 0.25
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
    lift_speed:
      type: scalar
      range:
      - 0.02
      - 0.08
      default: 0.04
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: object_lifted_check
    when: after_phase
    predicate: object_lifted
    threshold: 0.05
    on_failure: abort
  subtask_id: lift_clearance
- id: transport_to_goal
  type: approach
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.2
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    transport_speed:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: transport_contact
    when: during_phase
    predicate: force_below
    threshold: 18.0
    on_failure: retry
  retries:
    max_attempts: 1
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - 0.02
  subtask_id: transport_accuracy
- id: descend_place
  type: descend
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.03
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    place_z_offset:
      type: scalar
      range:
      - -0.01
      - 0.01
      default: 0.0
      binds_to:
      - path: target.offset.z
        mode: add
  subtask_id: place_accuracy
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
      - 0.3
      - 1.0
      default: 0.5
      binds_to:
      - path: duration.max_time
        mode: replace
  subtask_id: place_accuracy
- id: retract_1
  type: retract
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.25
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    retract_height:
      type: scalar
      range:
      - 0.15
      - 0.3
      default: 0.25
      binds_to:
      - path: target.offset.z
        mode: replace

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_object** (`approach`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=contact_before_approach, when=before_phase, predicate=contact_detected, on_failure=continue, threshold=1.0
- **descend_grasp** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - grasp_z_offset: status=consumed; consumers=target.offset.z (add)
- **grasp_1** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings:
    - grasp_duration: status=consumed; consumers=duration.max_time (replace)
  - guards:
    - id=bilateral_grasp_check, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=0.5
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, -0.005]
- **lift_1** (`lift`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.2], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
    - lift_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=object_lifted_check, when=after_phase, predicate=object_lifted, on_failure=abort, threshold=0.05
- **transport_to_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.2], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - transport_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=transport_contact, when=during_phase, predicate=force_below, on_failure=retry, threshold=18.0
  - retries: max_attempts=1, strategy=offset_target, offset=[0.0, 0.0, 0.02]
- **descend_place** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.03], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - place_z_offset: status=consumed; consumers=target.offset.z (add)
- **release_1** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings:
    - release_duration: status=consumed; consumers=duration.max_time (replace)
- **retract_1** (`retract`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.25], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - retract_height: status=consumed; consumers=target.offset.z (replace)

## Design Metrics

- **Composite score**: -0.360
- **task_score** (E): 0.080
- **fitness_score**: 0.270  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.630

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 0.00 | 0.00 | 0.0000 |
| descend_grasp | 1.00 | 1.00 | 0.2694 |
| grasp_1 | 1.00 | 1.00 | 0.0118 |
| lift_1 | 0.33 | 1.00 | 0.1782 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 0.00 / guard_failure | (0.500, -0.000, 0.301)→(0.500, -0.000, 0.301) | (0.500, 0.024, 0.030)→(0.500, 0.024, 0.030) | 0.269→0.269 | 0.00 / 0.000 | 0.000 | 0.000 |
| descend_grasp | descend | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.495, 0.023, 0.034) | (0.500, 0.024, 0.030)→(0.500, 0.024, 0.026) | 0.269→0.271 | 1.00 / 4.000 | 0.123 | 0.138 |
| grasp_1 | grasp | 1.00 / step_budget | (0.495, 0.023, 0.034)→(0.487, 0.022, 0.025) | (0.500, 0.024, 0.026)→(0.500, 0.023, 0.025) | 0.271→0.273 | 1.00 / 41.333 | 0.176 | 0.274 |
| lift_1 | lift | 0.33 / step_budget | (0.487, 0.022, 0.025)→(0.507, 0.026, 0.202) | (0.500, 0.023, 0.025)→(0.672, 0.070, -14.253) | 0.273→14.494 | 1.00 / 16.333 | 142.131 | 745.799 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 0.000
- transport_retention: None
- terminal_score: 0.239
- phase_score: 0.216
- phase_breakdown.lift_clearance_score: 0.000
- phase_breakdown.reach_object_score: 0.078
- phase_breakdown.transport_accuracy_score: 0.000
- phase_breakdown.grasp_success_score: 1.000
- phase_breakdown.place_accuracy_score: 0.000
- grasp_place_fitness: 0.348

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.348
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.239
- **Median Q (composite search score)**: -0.398
- **K-run variance**: 0.0031
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.335


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
{"anchors":[{"name":"object","value":[0.58691,0.18745,0.24812]},{"name":"goal","value":[0.50382,-0.01567,0.03]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.58691,0.18745,0.24812]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.50382,-0.01567,0.03]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":33.0,"average_failure_rate":0.26613,"average_mean_iterations":56.48387,"average_solve_count":124.0,"average_success_count":91.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.06868,"descend_grasp.grasp_z_offset":-0.00388,"descend_place.place_z_offset":0.00335,"grasp_1.grasp_duration":1.4134,"lift_1.lift_height":0.20419,"lift_1.lift_speed":0.05732,"release_1.release_duration":0.769,"retract_1.retract_height":0.22095,"transport_to_goal.transport_speed":0.07572},"optimized_scores":{"best_composite_score":-0.4004,"best_fitness_score":0.2296,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"hand","contact_count":62.0,"contact_point_centroid":[0.57764,-0.00454,-0.00067],"force_p95":658.04825,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":955.0637,"mean_force":247.88533,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51879,0.02506,-0.00931]},{"body_a":"world","body_b":"link6","contact_count":812.0,"contact_point_centroid":[0.58149,0.06215,-0.00016],"force_p95":283.28276,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":752.35637,"mean_force":245.12773,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.54501,-0.00346,0.2659]},{"body_a":"world","body_b":"link7","contact_count":15.0,"contact_point_centroid":[0.62353,0.02594,-0.00028],"force_p95":577.24168,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":631.09548,"mean_force":256.05204,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49902,-0.01756,0.03899]},{"body_a":"world","body_b":"left_finger","contact_count":1145.0,"contact_point_centroid":[0.53505,-0.00802,-0.01085],"force_p95":25.73855,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":45.85886,"mean_force":9.90422,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52072,0.0275,-0.0092]},{"body_a":"world","body_b":"right_finger","contact_count":986.0,"contact_point_centroid":[0.50931,0.06596,-0.00829],"force_p95":15.00743,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":30.18977,"mean_force":9.28904,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.5217,0.02874,-0.01134]},{"body_a":"world","body_b":"grasp_target","contact_count":116.0,"contact_point_centroid":[0.51448,-0.00709,-0.01315],"force_p95":4.57106,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.96522,"mean_force":2.45798,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.50742,0.00848,0.01051]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":480.0,"contact_point_centroid":[0.50745,-0.02152,0.01514],"force_p95":2.03848,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.83842,"mean_force":0.83443,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.50439,0.00442,0.01525]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":72.0,"contact_point_centroid":[0.49149,0.005,0.02893],"force_p95":0.26608,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.47916,"mean_force":0.07995,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4913,-0.01398,0.02592]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50383,-0.01542,-0.00208],"force_p95":0.1478,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.2209,"mean_force":0.12941,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49212,-0.01477,0.02747]},{"body_a":"world","body_b":"grasp_target","contact_count":3268.0,"contact_point_centroid":[0.50382,-0.01567,-0.00195],"force_p95":0.127,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12278,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.49843,-0.00738,0.16607]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4079.0,"contact_point_centroid":[0.49137,0.00445,0.02902],"force_p95":0.07863,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13048,"mean_force":0.05182,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49095,-0.01475,0.02625]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4948.0,"contact_point_centroid":[0.49143,-0.03387,0.02812],"force_p95":0.07075,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08888,"mean_force":0.04479,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49096,-0.01475,0.02625]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3171.0,"contact_point_centroid":[0.53703,0.00914,0.28282],"force_p95":0.01095,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01651,"mean_force":0.01018,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53665,0.00877,0.2852]}],"total_contact_groups":13},"final_pose_error":0.06451,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.88876,0.26215,-21.61478],"final_tcp_position":[0.51884,-0.00097,0.2911],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":955.0637,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":0.0,"n_steps_budget":0.0,"object_pos_end":[0.50382,-0.01567,0.03],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.30942,"object_to_goal_dist_start":0.30942,"peak_contact_force":0.0,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_object","tcp_end":[0.49977,-0.0,0.30085],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.27133,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":818.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3268.0,"raw_peak_contact_force":0.13845,"subtask_id":"grasp_success","tcp_end":[0.49911,-0.01482,0.03489],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.01008,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50369,-0.01467,0.02572],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31183,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.14216,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10827.0,"raw_peak_contact_force":0.2209,"subtask_id":"grasp_success","tcp_end":[0.49093,-0.01475,0.02622],"tcp_start":[0.49911,-0.01482,0.03489],"tcp_to_object_dist_end":0.01277,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.88876,0.26215,-21.61478],"object_pos_start":[0.50369,-0.01467,0.02572],"object_to_goal_dist_end":21.86511,"object_to_goal_dist_start":0.31183,"object_z_max":0.02572,"peak_contact_force":210.89082,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":6859.0,"raw_peak_contact_force":955.0637,"subtask_id":"lift_clearance","tcp_end":[0.51884,-0.00097,0.2911],"tcp_start":[0.49093,-0.01475,0.02622],"tcp_to_object_dist_end":21.91058,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `fe7e0be33c0bb4db9d2bbbb069b6113d0e5a69a675a0d70bc1f582243e99e3cf`; realized-scene SHA-256: `8a4edc50bf1a337961423afe5cdf858aa28147f944f8fcd30a2ce1adc75d1bd6`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.62757,0.17252,0.14502]},{"name":"goal","value":[0.51251,0.03972,0.03]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.62757,0.17252,0.14502]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.51251,0.03972,0.03]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":51.0,"average_failure_rate":0.47222,"average_mean_iterations":96.52778,"average_solve_count":108.0,"average_success_count":57.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.08493,"descend_grasp.grasp_z_offset":-0.00353,"descend_place.place_z_offset":-0.00379,"grasp_1.grasp_duration":1.31596,"lift_1.lift_height":0.11724,"lift_1.lift_speed":0.04771,"release_1.release_duration":0.70657,"retract_1.retract_height":0.24852,"transport_to_goal.transport_speed":0.08143},"optimized_scores":{"best_composite_score":-0.28169,"best_fitness_score":0.34831,"best_task_score":0.23923},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51264,0.03916,-0.00227],"force_p95":0.20255,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.29022,"mean_force":0.1435,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50027,0.03692,0.02677]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3556.0,"contact_point_centroid":[0.50065,0.01763,0.0287],"force_p95":0.0926,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16655,"mean_force":0.05808,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49909,0.03682,0.0255]},{"body_a":"world","body_b":"grasp_target","contact_count":3344.0,"contact_point_centroid":[0.51251,0.03972,-0.00195],"force_p95":0.12689,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12277,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.50253,0.01865,0.1657]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4929.0,"contact_point_centroid":[0.50004,0.0561,0.02745],"force_p95":0.08216,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08944,"mean_force":0.04669,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4991,0.03682,0.02551]}],"total_contact_groups":4},"final_pose_error":0.10806,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.51242,0.0369,0.02512],"final_tcp_position":[0.50731,0.03743,0.03442],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":0.29022,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":0.0,"n_steps_budget":0.0,"object_pos_end":[0.51251,0.03972,0.03],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21001,"object_to_goal_dist_start":0.21001,"peak_contact_force":0.0,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_object","tcp_end":[0.49977,-0.0,0.30085],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.27404,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":837.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3344.0,"raw_peak_contact_force":0.13845,"subtask_id":"grasp_success","tcp_end":[0.50731,0.03743,0.03442],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.01014,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51242,0.0369,0.02512],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21455,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.18392,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10285.0,"raw_peak_contact_force":0.29022,"subtask_id":"grasp_success","tcp_end":[0.49906,0.03682,0.02547],"tcp_start":[0.50731,0.03743,0.03442],"tcp_to_object_dist_end":0.01336,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":0.0,"n_steps_budget":1000.0,"object_pos_end":[0.51242,0.0369,0.02512],"object_pos_start":[0.51242,0.0369,0.02512],"object_to_goal_dist_end":0.21455,"object_to_goal_dist_start":0.21455,"peak_contact_force":0.18392,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"lift_clearance","tcp_end":[0.49906,0.03682,0.02547],"tcp_start":[0.49906,0.03682,0.02547],"tcp_to_object_dist_end":0.01336,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `28f75809d7d1d0a11ca1a36dd459ad950e5a80b6bae34006f33ac9620425f5e5`; realized-scene SHA-256: `f44a4a1356de6cb8b5dec75995af4354e38cafd01c85526c1c2a33c8dd2e5b1c`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.58187,0.22885,0.23048]},{"name":"goal","value":[0.4827,0.04873,0.03]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.58187,0.22885,0.23048]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.4827,0.04873,0.03]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":18.0,"average_failure_rate":0.16364,"average_mean_iterations":36.70909,"average_solve_count":110.0,"average_success_count":92.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.02516,"descend_grasp.grasp_z_offset":-0.00599,"descend_place.place_z_offset":0.00115,"grasp_1.grasp_duration":1.05757,"lift_1.lift_height":0.23589,"lift_1.lift_speed":0.07592,"release_1.release_duration":0.54864,"retract_1.retract_height":0.18178,"transport_to_goal.transport_speed":0.10113},"optimized_scores":{"best_composite_score":-0.3982,"best_fitness_score":0.2318,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"hand","contact_count":23.0,"contact_point_centroid":[0.52794,0.01297,-0.00124],"force_p95":1129.72845,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1282.33348,"mean_force":457.23025,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4994,0.01434,-0.00662]},{"body_a":"world","body_b":"link7","contact_count":22.0,"contact_point_centroid":[0.60883,-0.02232,-0.00047],"force_p95":604.8107,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":673.53266,"mean_force":302.72422,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49499,0.03963,0.02574]},{"body_a":"world","body_b":"link6","contact_count":825.0,"contact_point_centroid":[0.57809,-0.01045,-0.00014],"force_p95":311.98313,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":612.89986,"mean_force":235.0729,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.5279,0.04951,0.26746]},{"body_a":"link5","body_b":"hand","contact_count":639.0,"contact_point_centroid":[0.50222,-0.06387,0.24901],"force_p95":176.86697,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":204.36747,"mean_force":150.8391,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51651,0.03919,0.28695]},{"body_a":"world","body_b":"right_finger","contact_count":713.0,"contact_point_centroid":[0.50846,0.04476,-0.01124],"force_p95":26.78574,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":42.30961,"mean_force":11.84538,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.50208,0.00773,-0.00795]},{"body_a":"world","body_b":"left_finger","contact_count":758.0,"contact_point_centroid":[0.49488,-0.02714,-0.0055],"force_p95":21.09228,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":33.98604,"mean_force":9.7854,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.50109,0.01032,-0.0066]},{"body_a":"world","body_b":"grasp_target","contact_count":123.0,"contact_point_centroid":[0.49306,0.03918,-0.01329],"force_p95":4.62566,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.05588,"mean_force":2.46455,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4882,0.02321,0.00816]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":563.0,"contact_point_centroid":[0.48729,0.0531,0.01175],"force_p95":1.84849,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.66428,"mean_force":0.73365,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48598,0.02612,0.01178]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":84.0,"contact_point_centroid":[0.47122,0.02539,0.02758],"force_p95":0.28249,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.47417,"mean_force":0.07313,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4717,0.04447,0.02446]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48286,0.04811,-0.00234],"force_p95":0.21931,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.31073,"mean_force":0.14865,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47242,0.04532,0.02593]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4477.0,"contact_point_centroid":[0.4716,0.02592,0.02744],"force_p95":0.08294,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16115,"mean_force":0.04774,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47129,0.04521,0.0248]},{"body_a":"world","body_b":"grasp_target","contact_count":3328.0,"contact_point_centroid":[0.4827,0.04873,-0.00195],"force_p95":0.12693,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12277,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.48848,0.02287,0.16489]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5715.0,"contact_point_centroid":[0.47068,0.06475,0.02619],"force_p95":0.07687,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08549,"mean_force":0.04156,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47131,0.04521,0.02482]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3193.0,"contact_point_centroid":[0.52062,0.039,0.28358],"force_p95":0.01091,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01566,"mean_force":0.01016,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.5201,0.03934,0.28573]}],"total_contact_groups":14},"final_pose_error":0.0369,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.61527,-0.09023,-21.16909],"final_tcp_position":[0.5041,0.04298,0.29064],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":1282.33348,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":0.0,"n_steps_budget":0.0,"object_pos_end":[0.4827,0.04873,0.03],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28719,"object_to_goal_dist_start":0.28719,"peak_contact_force":0.0,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_object","tcp_end":[0.49977,-0.0,0.30085],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.27573,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":833.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3328.0,"raw_peak_contact_force":0.13845,"subtask_id":"grasp_success","tcp_end":[0.47917,0.0459,0.03281],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.00815,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48261,0.04542,0.02485],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29289,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.20086,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11992.0,"raw_peak_contact_force":0.31073,"subtask_id":"grasp_success","tcp_end":[0.47127,0.0452,0.02478],"tcp_start":[0.47917,0.0459,0.03281],"tcp_to_object_dist_end":0.01134,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":6.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.61527,-0.09023,-21.16909],"object_pos_start":[0.48261,0.04542,0.02485],"object_to_goal_dist_end":21.40198,"object_to_goal_dist_start":0.29289,"object_z_max":0.02485,"peak_contact_force":215.318,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":6943.0,"raw_peak_contact_force":1282.33348,"subtask_id":"lift_clearance","tcp_end":[0.5041,0.04298,0.29064],"tcp_start":[0.47127,0.0452,0.02478],"tcp_to_object_dist_end":21.46044,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```