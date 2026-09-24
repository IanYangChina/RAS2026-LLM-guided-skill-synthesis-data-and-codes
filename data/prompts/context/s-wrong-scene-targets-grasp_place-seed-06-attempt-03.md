## Search State

- **Seed**: 6
- **Iteration**: 4 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 3 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | impedance_control | impedance_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 9 | 0.0038 | 0.31 | ✅ accepted |
| 2 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | impedance_control | impedance_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 9 | 0.0037 | 0.31 | ✅ accepted |
| 1 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 5 | 0.1410 | 0.18 | ❌ rejected |
| 0 | align → lift → push → approach → approach → descend → grasp → rotate | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | arc_cartesian | linear_cartesian | — | impedance_motion | position_control | position_control | impedance_control | force_threshold_switch | position_control | admittance_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 6 | -0.1416 | 0.25 | ✅ accepted |

**Proposal policy**: task_score is 0.31 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.004) — your mutation base

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

- **Composite score**: 0.004
- **task_score** (E): 0.308
- **fitness_score**: 0.634  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.630

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 0.00 | 0.00 | 0.0000 |
| descend_grasp | 1.00 | 1.00 | 0.2682 |
| grasp_1 | 1.00 | 1.00 | 0.0118 |
| lift_1 | 1.00 | 1.00 | 0.1957 |
| transport_to_goal | 1.00 | 1.00 | 0.2538 |
| descend_place | 1.00 | 1.00 | 0.1396 |
| release_1 | 1.00 | 1.00 | 0.0202 |
| retract_1 | 1.00 | 1.00 | 0.1554 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 0.00 / guard_failure | (0.500, -0.000, 0.301)→(0.500, -0.000, 0.301) | (0.500, 0.024, 0.030)→(0.500, 0.024, 0.030) | 0.269→0.269 | 0.00 / 0.000 | 0.000 | 0.000 |
| descend_grasp | descend | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.495, 0.023, 0.035) | (0.500, 0.024, 0.030)→(0.500, 0.024, 0.026) | 0.269→0.271 | 1.00 / 4.000 | 0.123 | 0.138 |
| grasp_1 | grasp | 1.00 / step_budget | (0.495, 0.023, 0.035)→(0.487, 0.022, 0.027) | (0.500, 0.024, 0.026)→(0.500, 0.023, 0.025) | 0.271→0.273 | 1.00 / 41.333 | 0.176 | 0.272 |
| lift_1 | lift | 1.00 / step_budget | (0.487, 0.022, 0.027)→(0.496, 0.022, 0.222) | (0.500, 0.023, 0.025)→(0.506, 0.022, 0.216) | 0.273→0.201 | 1.00 / 42.667 | 0.072 | 0.612 |
| transport_to_goal | approach | 1.00 / step_budget | (0.496, 0.022, 0.222)→(0.592, 0.186, 0.389) | (0.506, 0.022, 0.216)→(0.600, 0.186, 0.376) | 0.201→0.168 | 1.00 / 39.667 | 3253.458 | 0.092 |
| descend_place | descend | 1.00 / step_budget | (0.592, 0.186, 0.389)→(0.596, 0.194, 0.250) | (0.600, 0.186, 0.376)→(0.584, 0.193, 0.234) | 0.168→0.030 | 1.00 / 40.000 | 0.082 | 0.156 |
| release_1 | release | 1.00 / step_budget | (0.596, 0.194, 0.250)→(0.591, 0.192, 0.269) | (0.584, 0.193, 0.234)→(0.579, 0.193, 0.017) | 0.030→0.193 | 1.00 / 4.000 | 0.215 | 2.067 |
| retract_1 | retract | 1.00 / step_budget | (0.591, 0.192, 0.269)→(0.598, 0.196, 0.424) | (0.579, 0.193, 0.017)→(0.575, 0.197, 0.026) | 0.193→0.184 | 1.00 / 4.000 | 0.123 | 0.227 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.443
- phase_score: 0.450
- phase_breakdown.lift_clearance_score: 0.160
- phase_breakdown.reach_object_score: 0.078
- phase_breakdown.transport_accuracy_score: 0.493
- phase_breakdown.grasp_success_score: 1.000
- phase_breakdown.place_accuracy_score: 0.518
- grasp_place_fitness: 0.700

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.700
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.443
- **Median Q (composite search score)**: -0.021
- **K-run variance**: 0.0022
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.319


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.31915,"average_solve_count":329.0,"average_success_count":329.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.02653,"descend_grasp.grasp_z_offset":-0.00298,"descend_place.place_z_offset":0.00454,"grasp_1.grasp_duration":1.4572,"lift_1.lift_height":0.21925,"lift_1.lift_speed":0.04732,"release_1.release_duration":0.34771,"retract_1.retract_height":0.21402,"transport_to_goal.transport_speed":0.03414},"optimized_scores":{"best_composite_score":-0.03765,"best_fitness_score":0.59235,"best_task_score":0.22566},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":124.0,"contact_point_centroid":[0.564,0.18824,-0.01056],"force_p95":1.52701,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.27384,"mean_force":0.64043,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.58072,0.18344,0.30692]},{"body_a":"world","body_b":"grasp_target","contact_count":86.0,"contact_point_centroid":[0.49992,-0.01453,-0.00147],"force_p95":0.6009,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.62088,"mean_force":0.22316,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49001,-0.01475,0.02812]},{"body_a":"world","body_b":"grasp_target","contact_count":1924.0,"contact_point_centroid":[0.56397,0.18846,-0.00217],"force_p95":0.13528,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.35496,"mean_force":0.12001,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.58279,0.18487,0.37737]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":14329.0,"contact_point_centroid":[0.49326,0.00452,0.12848],"force_p95":0.0725,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30223,"mean_force":0.05044,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4935,-0.01467,0.12657]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14675.0,"contact_point_centroid":[0.49309,-0.03382,0.12619],"force_p95":0.072,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28746,"mean_force":0.04978,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49337,-0.01467,0.1246]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50383,-0.01542,-0.00208],"force_p95":0.14761,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21996,"mean_force":0.12936,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49213,-0.01477,0.02823]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6796.0,"contact_point_centroid":[0.58268,0.19741,0.35993],"force_p95":0.07715,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16735,"mean_force":0.05164,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.58207,0.17836,0.35798]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7437.0,"contact_point_centroid":[0.58249,0.15921,0.35932],"force_p95":0.07409,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15581,"mean_force":0.04876,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.58209,0.17841,0.35738]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1328.0,"contact_point_centroid":[0.58356,0.1654,0.29004],"force_p95":0.07484,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14444,"mean_force":0.04155,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.58288,0.18445,0.2876]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1123.0,"contact_point_centroid":[0.58407,0.20375,0.28897],"force_p95":0.08061,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13971,"mean_force":0.04855,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.58285,0.18444,0.28751]},{"body_a":"world","body_b":"grasp_target","contact_count":3252.0,"contact_point_centroid":[0.50382,-0.01567,-0.00195],"force_p95":0.12703,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12278,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.49843,-0.00738,0.1664]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4079.0,"contact_point_centroid":[0.49138,0.00445,0.02978],"force_p95":0.07861,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13157,"mean_force":0.05184,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49096,-0.01476,0.02701]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":21207.0,"contact_point_centroid":[0.53871,0.0598,0.32343],"force_p95":0.07189,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10317,"mean_force":0.04772,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.53849,0.07886,0.32254]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":19179.0,"contact_point_centroid":[0.54001,0.10023,0.32617],"force_p95":0.0778,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09267,"mean_force":0.05221,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.53945,0.08105,0.32489]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4947.0,"contact_point_centroid":[0.49143,-0.03387,0.02888],"force_p95":0.07073,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08839,"mean_force":0.04478,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49096,-0.01476,0.02701]}],"total_contact_groups":15},"final_pose_error":0.01977,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.56368,0.18873,0.02602],"final_tcp_position":[0.58634,0.18681,0.44239],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":9760.30694,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":0.0,"n_steps_budget":0.0,"object_pos_end":[0.50382,-0.01567,0.03],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.30942,"object_to_goal_dist_start":0.30942,"peak_contact_force":0.0,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_object","tcp_end":[0.49977,-0.0,0.30085],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.27133,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":814.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3252.0,"raw_peak_contact_force":0.13845,"subtask_id":"grasp_success","tcp_end":[0.4991,-0.01483,0.03565],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.01076,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50369,-0.01468,0.02572],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31184,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.14208,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10826.0,"raw_peak_contact_force":0.21996,"subtask_id":"grasp_success","tcp_end":[0.49093,-0.01475,0.02698],"tcp_start":[0.4991,-0.01483,0.03565],"tcp_to_object_dist_end":0.01282,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":697.0,"n_steps_budget":1000.0,"object_pos_end":[0.51082,-0.01466,0.21869],"object_pos_start":[0.50369,-0.01468,0.02572],"object_to_goal_dist_end":0.21795,"object_to_goal_dist_start":0.31184,"object_z_max":0.21843,"peak_contact_force":0.06935,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":29090.0,"raw_peak_contact_force":0.62088,"subtask_id":"lift_clearance","tcp_end":[0.49983,-0.01464,0.22559],"tcp_start":[0.49093,-0.01475,0.02698],"tcp_to_object_dist_end":0.01297,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":36.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.58847,0.1725,0.4098],"object_pos_start":[0.51082,-0.01466,0.21869],"object_to_goal_dist_end":0.16238,"object_to_goal_dist_start":0.21795,"object_z_max":0.4096,"peak_contact_force":9760.30694,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":40386.0,"raw_peak_contact_force":0.10317,"subtask_id":"transport_accuracy","tcp_end":[0.58025,0.17248,0.42424],"tcp_start":[0.49983,-0.01464,0.22559],"tcp_to_object_dist_end":0.01661,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":350.0,"n_steps_budget":1000.0,"object_pos_end":[0.57322,0.18414,0.27446],"object_pos_start":[0.58847,0.1725,0.4098],"object_to_goal_dist_end":0.02987,"object_to_goal_dist_start":0.16238,"object_z_max":0.40985,"peak_contact_force":0.08137,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":14233.0,"raw_peak_contact_force":0.16735,"subtask_id":"place_accuracy","tcp_end":[0.58415,0.18484,0.29164],"tcp_start":[0.58025,0.17248,0.42424],"tcp_to_object_dist_end":0.02038,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.57087,0.18301,0.00988],"object_pos_start":[0.57322,0.18414,0.27446],"object_to_goal_dist_end":0.23881,"object_to_goal_dist_start":0.02987,"object_z_max":0.27446,"peak_contact_force":0.37474,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2575.0,"raw_peak_contact_force":2.27384,"subtask_id":"place_accuracy","tcp_end":[0.58071,0.18344,0.3118],"tcp_start":[0.58415,0.18484,0.29164],"tcp_to_object_dist_end":0.30208,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":488.0,"n_steps_budget":960.0,"object_pos_end":[0.56368,0.18873,0.02602],"object_pos_start":[0.57087,0.18301,0.00988],"object_to_goal_dist_end":0.22331,"object_to_goal_dist_start":0.23881,"object_z_max":0.02708,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1924.0,"raw_peak_contact_force":0.35496,"tcp_end":[0.58634,0.18681,0.44239],"tcp_start":[0.58071,0.18344,0.3118],"tcp_to_object_dist_end":0.41699,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.29752,"average_solve_count":363.0,"average_success_count":363.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.0615,"descend_grasp.grasp_z_offset":-0.0015,"descend_place.place_z_offset":0.00346,"grasp_1.grasp_duration":1.27029,"lift_1.lift_height":0.19437,"lift_1.lift_speed":0.02194,"release_1.release_duration":0.69707,"retract_1.retract_height":0.22247,"transport_to_goal.transport_speed":0.03642},"optimized_scores":{"best_composite_score":0.07008,"best_fitness_score":0.70008,"best_task_score":0.44343},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":234.0,"contact_point_centroid":[0.6007,0.17202,-0.00643],"force_p95":1.00355,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.71812,"mean_force":0.31025,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61763,0.16872,0.19731]},{"body_a":"world","body_b":"grasp_target","contact_count":103.0,"contact_point_centroid":[0.50846,0.03591,-0.00173],"force_p95":0.51312,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.53813,"mean_force":0.20623,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49802,0.03668,0.0288]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51264,0.03919,-0.00227],"force_p95":0.20172,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.287,"mean_force":0.14319,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.5003,0.03688,0.02896]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12811.0,"contact_point_centroid":[0.50156,0.05564,0.11266],"force_p95":0.07902,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2807,"mean_force":0.05165,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.50154,0.03656,0.11074]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11643.0,"contact_point_centroid":[0.50176,0.01738,0.11345],"force_p95":0.08307,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28041,"mean_force":0.05474,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.50154,0.03656,0.1108]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3566.0,"contact_point_centroid":[0.50067,0.0176,0.03089],"force_p95":0.09248,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16923,"mean_force":0.05799,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49912,0.03679,0.02769]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1328.0,"contact_point_centroid":[0.62221,0.15095,0.18544],"force_p95":0.0743,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15651,"mean_force":0.04163,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.62139,0.16998,0.1828]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7264.0,"contact_point_centroid":[0.62119,0.18631,0.26175],"force_p95":0.0751,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14921,"mean_force":0.05024,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.62081,0.16723,0.25998]},{"body_a":"world","body_b":"grasp_target","contact_count":2280.0,"contact_point_centroid":[0.60079,0.17206,-0.00197],"force_p95":0.12536,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.14676,"mean_force":0.1217,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.6203,0.16979,0.27643]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7572.0,"contact_point_centroid":[0.62116,0.14807,0.26066],"force_p95":0.071,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14662,"mean_force":0.04836,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.62087,0.16729,0.25851]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1126.0,"contact_point_centroid":[0.62268,0.1893,0.18428],"force_p95":0.08003,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14244,"mean_force":0.04851,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.62134,0.16997,0.18269]},{"body_a":"world","body_b":"grasp_target","contact_count":3320.0,"contact_point_centroid":[0.51251,0.03972,-0.00195],"force_p95":0.12693,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12277,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.50254,0.01864,0.16673]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4929.0,"contact_point_centroid":[0.50006,0.05606,0.02964],"force_p95":0.08221,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08837,"mean_force":0.04659,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49914,0.03679,0.0277]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16710.0,"contact_point_centroid":[0.564,0.1215,0.26499],"force_p95":0.06863,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08516,"mean_force":0.04777,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.56396,0.1023,0.26389]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17396.0,"contact_point_centroid":[0.56365,0.0828,0.26499],"force_p95":0.06848,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.085,"mean_force":0.04572,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.56367,0.10197,0.26356]}],"total_contact_groups":15},"final_pose_error":0.01984,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.60079,0.17206,0.02602],"final_tcp_position":[0.62556,0.17165,0.34778],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":1.71812,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":0.0,"n_steps_budget":0.0,"object_pos_end":[0.51251,0.03972,0.03],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21001,"object_to_goal_dist_start":0.21001,"peak_contact_force":0.0,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_object","tcp_end":[0.49977,-0.0,0.30085],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.27404,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":831.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3320.0,"raw_peak_contact_force":0.13845,"subtask_id":"grasp_success","tcp_end":[0.50733,0.03739,0.03663],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.01203,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51244,0.03695,0.02512],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.2145,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.18377,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10295.0,"raw_peak_contact_force":0.287,"subtask_id":"grasp_success","tcp_end":[0.4991,0.03678,0.02766],"tcp_start":[0.50733,0.03739,0.03663],"tcp_to_object_dist_end":0.01358,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":625.0,"n_steps_budget":1000.0,"object_pos_end":[0.51916,0.03672,0.19268],"object_pos_start":[0.51244,0.03695,0.02512],"object_to_goal_dist_end":0.18018,"object_to_goal_dist_start":0.2145,"object_z_max":0.19242,"peak_contact_force":0.07541,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":24557.0,"raw_peak_contact_force":0.53813,"subtask_id":"lift_clearance","tcp_end":[0.50817,0.03667,0.20013],"tcp_start":[0.4991,0.03678,0.02766],"tcp_to_object_dist_end":0.01328,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":798.0,"n_steps_budget":1000.0,"object_pos_end":[0.62785,0.16461,0.31542],"object_pos_start":[0.51916,0.03672,0.19268],"object_to_goal_dist_end":0.17058,"object_to_goal_dist_start":0.18018,"object_z_max":0.31529,"peak_contact_force":0.06856,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":34106.0,"raw_peak_contact_force":0.08516,"subtask_id":"transport_accuracy","tcp_end":[0.61962,0.16466,0.32861],"tcp_start":[0.50817,0.03667,0.20013],"tcp_to_object_dist_end":0.01554,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":361.0,"n_steps_budget":1000.0,"object_pos_end":[0.61307,0.16988,0.17168],"object_pos_start":[0.62785,0.16461,0.31542],"object_to_goal_dist_end":0.03045,"object_to_goal_dist_start":0.17058,"object_z_max":0.31544,"peak_contact_force":0.08052,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":14836.0,"raw_peak_contact_force":0.14921,"subtask_id":"place_accuracy","tcp_end":[0.62332,0.17053,0.18725],"tcp_start":[0.61962,0.16466,0.32861],"tcp_to_object_dist_end":0.01866,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.60275,0.17096,0.02533],"object_pos_start":[0.61307,0.16988,0.17168],"object_to_goal_dist_end":0.12225,"object_to_goal_dist_start":0.03045,"object_z_max":0.17168,"peak_contact_force":0.08107,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2688.0,"raw_peak_contact_force":1.71812,"subtask_id":"place_accuracy","tcp_end":[0.61759,0.1687,0.20614],"tcp_start":[0.62332,0.17053,0.18725],"tcp_to_object_dist_end":0.18143,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":570.0,"n_steps_budget":1000.0,"object_pos_end":[0.60079,0.17206,0.02602],"object_pos_start":[0.60275,0.17096,0.02533],"object_to_goal_dist_end":0.12198,"object_to_goal_dist_start":0.12225,"object_z_max":0.02667,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2280.0,"raw_peak_contact_force":0.14676,"tcp_end":[0.62556,0.17165,0.34778],"tcp_start":[0.61759,0.1687,0.20614],"tcp_to_object_dist_end":0.32271,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.32086,"average_solve_count":374.0,"average_success_count":374.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.04474,"descend_grasp.grasp_z_offset":-0.00499,"descend_place.place_z_offset":0.00027,"grasp_1.grasp_duration":1.76033,"lift_1.lift_height":0.23582,"lift_1.lift_speed":0.02738,"release_1.release_duration":0.67392,"retract_1.retract_height":0.2725,"transport_to_goal.transport_speed":0.03149},"optimized_scores":{"best_composite_score":-0.02116,"best_fitness_score":0.60884,"best_task_score":0.25418},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":143.0,"contact_point_centroid":[0.56158,0.22998,-0.01039],"force_p95":1.36407,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.20768,"mean_force":0.55184,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.5754,0.22492,0.28414]},{"body_a":"world","body_b":"grasp_target","contact_count":98.0,"contact_point_centroid":[0.4786,0.04405,-0.00176],"force_p95":0.63193,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.67618,"mean_force":0.23111,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47025,0.0451,0.02712]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48286,0.04814,-0.00234],"force_p95":0.21811,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.30906,"mean_force":0.14832,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47243,0.04533,0.0268]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":15006.0,"contact_point_centroid":[0.4734,0.06415,0.13583],"force_p95":0.07844,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29264,"mean_force":0.05124,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47333,0.04501,0.1339]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14688.0,"contact_point_centroid":[0.47324,0.02584,0.13407],"force_p95":0.07781,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25909,"mean_force":0.0512,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47323,0.045,0.13209]},{"body_a":"world","body_b":"grasp_target","contact_count":2868.0,"contact_point_centroid":[0.56173,0.22982,-0.00205],"force_p95":0.12492,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17883,"mean_force":0.11977,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.5778,0.22625,0.38478]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4642.0,"contact_point_centroid":[0.47139,0.02594,0.02809],"force_p95":0.08082,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16443,"mean_force":0.04613,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4713,0.04523,0.02567]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1328.0,"contact_point_centroid":[0.57861,0.20715,0.26843],"force_p95":0.07734,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1508,"mean_force":0.04236,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57778,0.22621,0.2657]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7053.0,"contact_point_centroid":[0.57827,0.24204,0.34484],"force_p95":0.07639,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15037,"mean_force":0.05263,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.57774,0.223,0.34288]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7779.0,"contact_point_centroid":[0.57804,0.20378,0.34527],"force_p95":0.07193,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14678,"mean_force":0.04822,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.57774,0.223,0.34291]},{"body_a":"world","body_b":"grasp_target","contact_count":3316.0,"contact_point_centroid":[0.4827,0.04873,-0.00195],"force_p95":0.12693,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12277,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.48848,0.02289,0.16525]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1202.0,"contact_point_centroid":[0.57871,0.24549,0.26731],"force_p95":0.08216,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13815,"mean_force":0.04608,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57773,0.22618,0.26553]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":19691.0,"contact_point_centroid":[0.52706,0.11419,0.32841],"force_p95":0.06885,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08673,"mean_force":0.04645,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52704,0.13333,0.32628]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5706.0,"contact_point_centroid":[0.47069,0.06477,0.02705],"force_p95":0.07709,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08498,"mean_force":0.04155,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47131,0.04523,0.02568]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18850.0,"contact_point_centroid":[0.52647,0.15135,0.32692],"force_p95":0.07018,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08114,"mean_force":0.04874,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52638,0.13215,0.3251]}],"total_contact_groups":15},"final_pose_error":0.01995,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.56173,0.22981,0.02602],"final_tcp_position":[0.58231,0.22855,0.48304],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":2.20768,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":0.0,"n_steps_budget":0.0,"object_pos_end":[0.4827,0.04873,0.03],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28719,"object_to_goal_dist_start":0.28719,"peak_contact_force":0.0,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_object","tcp_end":[0.49977,-0.0,0.30085],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.27573,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":830.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3316.0,"raw_peak_contact_force":0.13845,"subtask_id":"grasp_success","tcp_end":[0.47916,0.04592,0.03366],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.00888,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48261,0.04548,0.02485],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29285,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.20074,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12148.0,"raw_peak_contact_force":0.30906,"subtask_id":"grasp_success","tcp_end":[0.47127,0.04522,0.02564],"tcp_start":[0.47916,0.04592,0.03366],"tcp_to_object_dist_end":0.01137,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":740.0,"n_steps_budget":1000.0,"object_pos_end":[0.4889,0.04525,0.23537],"object_pos_start":[0.48261,0.04548,0.02485],"object_to_goal_dist_end":0.20586,"object_to_goal_dist_start":0.29285,"object_z_max":0.2351,"peak_contact_force":0.072,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":29792.0,"raw_peak_contact_force":0.67618,"subtask_id":"lift_clearance","tcp_end":[0.47908,0.04518,0.24118],"tcp_start":[0.47127,0.04522,0.02564],"tcp_to_object_dist_end":0.01141,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":925.0,"n_steps_budget":1000.0,"object_pos_end":[0.58408,0.21982,0.40215],"object_pos_start":[0.4889,0.04525,0.23537],"object_to_goal_dist_end":0.17191,"object_to_goal_dist_start":0.20586,"object_z_max":0.402,"peak_contact_force":0.0,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":38541.0,"raw_peak_contact_force":0.08673,"subtask_id":"transport_accuracy","tcp_end":[0.57663,0.21977,0.4136],"tcp_start":[0.47908,0.04518,0.24118],"tcp_to_object_dist_end":0.01367,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":372.0,"n_steps_budget":1000.0,"object_pos_end":[0.56693,0.22585,0.25525],"object_pos_start":[0.58408,0.21982,0.40215],"object_to_goal_dist_end":0.02908,"object_to_goal_dist_start":0.17191,"object_z_max":0.40215,"peak_contact_force":0.08307,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":14832.0,"raw_peak_contact_force":0.15037,"subtask_id":"place_accuracy","tcp_end":[0.57914,0.22677,0.26983],"tcp_start":[0.57663,0.21977,0.4136],"tcp_to_object_dist_end":0.01903,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.56336,0.22443,0.01432],"object_pos_start":[0.56693,0.22585,0.25525],"object_to_goal_dist_end":0.217,"object_to_goal_dist_start":0.02908,"object_z_max":0.25525,"peak_contact_force":0.19066,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2673.0,"raw_peak_contact_force":2.20768,"subtask_id":"place_accuracy","tcp_end":[0.57538,0.22492,0.28972],"tcp_start":[0.57914,0.22677,0.26983],"tcp_to_object_dist_end":0.27565,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":717.0,"n_steps_budget":1000.0,"object_pos_end":[0.56173,0.22981,0.02602],"object_pos_start":[0.56336,0.22443,0.01432],"object_to_goal_dist_end":0.20546,"object_to_goal_dist_start":0.217,"object_z_max":0.02691,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2868.0,"raw_peak_contact_force":0.17883,"tcp_end":[0.58231,0.22855,0.48304],"tcp_start":[0.57538,0.22492,0.28972],"tcp_to_object_dist_end":0.45749,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```