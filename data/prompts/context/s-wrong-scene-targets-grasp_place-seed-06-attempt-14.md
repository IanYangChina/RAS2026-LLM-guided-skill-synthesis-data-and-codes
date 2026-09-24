## Search State

- **Seed**: 6
- **Iteration**: 15 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 14 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | impedance_control | impedance_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 9 | 0.0037 | 0.31 | ❌ rejected |
| 13 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | impedance_control | position_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 9 | -0.3601 | 0.08 | ❌ rejected |
| 12 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | impedance_control | impedance_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 9 | 0.0033 | 0.31 | ❌ rejected |
| 11 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | impedance_control | impedance_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 9 | 0.0036 | 0.31 | ❌ rejected |
| 10 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | impedance_control | impedance_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 9 | 0.0038 | 0.31 | ✅ accepted |

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
| descend_grasp | 1.00 | 1.00 | 0.2683 |
| grasp_1 | 1.00 | 1.00 | 0.0118 |
| lift_1 | 1.00 | 1.00 | 0.1974 |
| transport_to_goal | 1.00 | 1.00 | 0.2507 |
| descend_place | 1.00 | 1.00 | 0.1421 |
| release_1 | 1.00 | 1.00 | 0.0203 |
| retract_1 | 1.00 | 1.00 | 0.1558 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 0.00 / guard_failure | (0.500, -0.000, 0.301)→(0.500, -0.000, 0.301) | (0.500, 0.024, 0.030)→(0.500, 0.024, 0.030) | 0.269→0.269 | 0.00 / 0.000 | 0.000 | 0.000 |
| descend_grasp | descend | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.495, 0.023, 0.035) | (0.500, 0.024, 0.030)→(0.500, 0.024, 0.026) | 0.269→0.271 | 1.00 / 4.000 | 0.123 | 0.138 |
| grasp_1 | grasp | 1.00 / step_budget | (0.495, 0.023, 0.035)→(0.487, 0.022, 0.027) | (0.500, 0.024, 0.026)→(0.500, 0.023, 0.025) | 0.271→0.273 | 1.00 / 41.333 | 0.175 | 0.272 |
| lift_1 | lift | 1.00 / step_budget | (0.487, 0.022, 0.027)→(0.496, 0.022, 0.224) | (0.500, 0.023, 0.025)→(0.506, 0.022, 0.217) | 0.273→0.202 | 1.00 / 41.333 | 0.074 | 0.623 |
| transport_to_goal | approach | 1.00 / step_budget | (0.496, 0.022, 0.224)→(0.591, 0.184, 0.387) | (0.506, 0.022, 0.217)→(0.600, 0.184, 0.374) | 0.202→0.167 | 1.00 / 41.667 | 0.074 | 0.092 |
| descend_place | descend | 1.00 / step_budget | (0.591, 0.184, 0.387)→(0.595, 0.194, 0.246) | (0.600, 0.184, 0.374)→(0.584, 0.193, 0.230) | 0.167→0.027 | 1.00 / 40.000 | 0.082 | 0.149 |
| release_1 | release | 1.00 / step_budget | (0.595, 0.194, 0.246)→(0.591, 0.192, 0.265) | (0.584, 0.193, 0.230)→(0.578, 0.193, 0.017) | 0.027→0.192 | 1.00 / 4.000 | 0.202 | 2.038 |
| retract_1 | retract | 1.00 / step_budget | (0.591, 0.192, 0.265)→(0.598, 0.196, 0.421) | (0.578, 0.193, 0.017)→(0.575, 0.197, 0.026) | 0.192→0.184 | 1.00 / 4.000 | 0.123 | 0.210 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.444
- phase_score: 0.459
- phase_breakdown.lift_clearance_score: 0.157
- phase_breakdown.reach_object_score: 0.078
- phase_breakdown.transport_accuracy_score: 0.492
- phase_breakdown.grasp_success_score: 1.000
- phase_breakdown.place_accuracy_score: 0.569
- grasp_place_fitness: 0.700

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.700
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.444
- **Median Q (composite search score)**: -0.021
- **K-run variance**: 0.0022
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
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
{"anchors":[{"name":"object","value":[0.58691,0.18745,0.24812]},{"name":"goal","value":[0.50382,-0.01567,0.03]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.58691,0.18745,0.24812]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.50382,-0.01567,0.03]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.33939,"average_solve_count":330.0,"average_success_count":330.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.04297,"descend_grasp.grasp_z_offset":-0.0031,"descend_place.place_z_offset":0.00147,"grasp_1.grasp_duration":1.46871,"lift_1.lift_height":0.21114,"lift_1.lift_speed":0.04613,"release_1.release_duration":0.82016,"retract_1.retract_height":0.24531,"transport_to_goal.transport_speed":0.05523},"optimized_scores":{"best_composite_score":-0.03766,"best_fitness_score":0.59234,"best_task_score":0.22561},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":126.0,"contact_point_centroid":[0.56385,0.18763,-0.01058],"force_p95":1.51616,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.25542,"mean_force":0.63005,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.58036,0.18294,0.30352]},{"body_a":"world","body_b":"grasp_target","contact_count":86.0,"contact_point_centroid":[0.49992,-0.01453,-0.00148],"force_p95":0.59514,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.61531,"mean_force":0.2234,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49002,-0.01475,0.02799]},{"body_a":"world","body_b":"grasp_target","contact_count":2422.0,"contact_point_centroid":[0.56354,0.18784,-0.00212],"force_p95":0.12718,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.32466,"mean_force":0.12017,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.58278,0.18465,0.39063]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":13795.0,"contact_point_centroid":[0.4932,0.00451,0.12407],"force_p95":0.07259,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29804,"mean_force":0.05046,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49345,-0.01466,0.12214]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14091.0,"contact_point_centroid":[0.49305,-0.03382,0.12193],"force_p95":0.0722,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28397,"mean_force":0.04991,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49332,-0.01467,0.12032]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50383,-0.01542,-0.00208],"force_p95":0.1476,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22008,"mean_force":0.12936,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49213,-0.01477,0.02812]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1328.0,"contact_point_centroid":[0.58331,0.16492,0.28675],"force_p95":0.07467,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14784,"mean_force":0.04147,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.58257,0.18397,0.28427]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6887.0,"contact_point_centroid":[0.58149,0.19502,0.35573],"force_p95":0.07729,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14699,"mean_force":0.05107,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.58092,0.17598,0.35385]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7405.0,"contact_point_centroid":[0.58134,0.15685,0.35512],"force_p95":0.07397,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14291,"mean_force":0.04888,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.58095,0.17606,0.35319]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1123.0,"contact_point_centroid":[0.58383,0.20327,0.28569],"force_p95":0.08035,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14079,"mean_force":0.04856,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.58254,0.18395,0.28418]},{"body_a":"world","body_b":"grasp_target","contact_count":3252.0,"contact_point_centroid":[0.50382,-0.01567,-0.00195],"force_p95":0.12703,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12278,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.49843,-0.00738,0.16634]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4079.0,"contact_point_centroid":[0.49138,0.00445,0.02966],"force_p95":0.07861,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13141,"mean_force":0.05183,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49096,-0.01476,0.02689]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":21258.0,"contact_point_centroid":[0.53778,0.05802,0.31702],"force_p95":0.0716,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09938,"mean_force":0.04766,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.53759,0.07709,0.3161]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":19207.0,"contact_point_centroid":[0.53911,0.09852,0.31993],"force_p95":0.0777,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09308,"mean_force":0.05216,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.53857,0.07934,0.31862]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4947.0,"contact_point_centroid":[0.49143,-0.03387,0.02876],"force_p95":0.07073,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08848,"mean_force":0.04478,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49096,-0.01476,0.0269]}],"total_contact_groups":15},"final_pose_error":0.0198,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.56336,0.18801,0.02602],"final_tcp_position":[0.58697,0.18697,0.47363],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":2.25542,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":0.0,"n_steps_budget":0.0,"object_pos_end":[0.50382,-0.01567,0.03],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.30942,"object_to_goal_dist_start":0.30942,"peak_contact_force":0.0,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_object","tcp_end":[0.49977,-0.0,0.30085],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.27133,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":814.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3252.0,"raw_peak_contact_force":0.13845,"subtask_id":"grasp_success","tcp_end":[0.4991,-0.01483,0.03553],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.01065,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50369,-0.01468,0.02572],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31184,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.14205,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10826.0,"raw_peak_contact_force":0.22008,"subtask_id":"grasp_success","tcp_end":[0.49093,-0.01475,0.02686],"tcp_start":[0.4991,-0.01483,0.03553],"tcp_to_object_dist_end":0.01281,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":671.0,"n_steps_budget":1000.0,"object_pos_end":[0.51074,-0.01466,0.21075],"object_pos_start":[0.50369,-0.01468,0.02572],"object_to_goal_dist_end":0.21919,"object_to_goal_dist_start":0.31184,"object_z_max":0.21048,"peak_contact_force":0.06974,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":27972.0,"raw_peak_contact_force":0.61531,"subtask_id":"lift_clearance","tcp_end":[0.49971,-0.01463,0.21732],"tcp_start":[0.49093,-0.01475,0.02686],"tcp_to_object_dist_end":0.01284,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.58672,0.16847,0.4048],"object_pos_start":[0.51074,-0.01466,0.21075],"object_to_goal_dist_end":0.15783,"object_to_goal_dist_start":0.21919,"object_z_max":0.40459,"peak_contact_force":0.0845,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":40465.0,"raw_peak_contact_force":0.09938,"subtask_id":"transport_accuracy","tcp_end":[0.57839,0.16844,0.41908],"tcp_start":[0.49971,-0.01463,0.21732],"tcp_to_object_dist_end":0.01653,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":350.0,"n_steps_budget":1000.0,"object_pos_end":[0.57326,0.18366,0.27141],"object_pos_start":[0.58672,0.16847,0.4048],"object_to_goal_dist_end":0.02726,"object_to_goal_dist_start":0.15783,"object_z_max":0.40486,"peak_contact_force":0.08111,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":14292.0,"raw_peak_contact_force":0.14699,"subtask_id":"place_accuracy","tcp_end":[0.58387,0.18434,0.2883],"tcp_start":[0.57839,0.16844,0.41908],"tcp_to_object_dist_end":0.01996,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.56982,0.18245,0.01056],"object_pos_start":[0.57326,0.18366,0.27141],"object_to_goal_dist_end":0.23822,"object_to_goal_dist_start":0.02726,"object_z_max":0.27141,"peak_contact_force":0.34345,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2577.0,"raw_peak_contact_force":2.25542,"subtask_id":"place_accuracy","tcp_end":[0.58035,0.18294,0.30849],"tcp_start":[0.58387,0.18434,0.2883],"tcp_to_object_dist_end":0.29811,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":611.0,"n_steps_budget":1000.0,"object_pos_end":[0.56336,0.18801,0.02602],"object_pos_start":[0.56982,0.18245,0.01056],"object_to_goal_dist_end":0.22334,"object_to_goal_dist_start":0.23822,"object_z_max":0.02694,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2422.0,"raw_peak_contact_force":0.32466,"tcp_end":[0.58697,0.18697,0.47363],"tcp_start":[0.58035,0.18294,0.30849],"tcp_to_object_dist_end":0.44824,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.34012,"average_solve_count":344.0,"average_success_count":344.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.04736,"descend_grasp.grasp_z_offset":-0.00121,"descend_place.place_z_offset":-0.00169,"grasp_1.grasp_duration":1.05373,"lift_1.lift_height":0.19755,"lift_1.lift_speed":0.04262,"release_1.release_duration":0.61024,"retract_1.retract_height":0.2526,"transport_to_goal.transport_speed":0.03772},"optimized_scores":{"best_composite_score":0.07005,"best_fitness_score":0.70005,"best_task_score":0.44353},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":242.0,"contact_point_centroid":[0.60093,0.17202,-0.00612],"force_p95":0.97591,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.6679,"mean_force":0.29722,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61747,0.16869,0.19192]},{"body_a":"world","body_b":"grasp_target","contact_count":98.0,"contact_point_centroid":[0.50854,0.03602,-0.00165],"force_p95":0.55656,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57601,"mean_force":0.19544,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49809,0.03668,0.02932]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11651.0,"contact_point_centroid":[0.50185,0.0174,0.11544],"force_p95":0.08337,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3076,"mean_force":0.05524,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.50159,0.03657,0.11278]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12754.0,"contact_point_centroid":[0.50164,0.05564,0.11407],"force_p95":0.07955,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30195,"mean_force":0.05219,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.50154,0.03657,0.11207]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51264,0.0392,-0.00227],"force_p95":0.20161,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.28648,"mean_force":0.14315,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50031,0.03688,0.02924]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3567.0,"contact_point_centroid":[0.50067,0.0176,0.03117],"force_p95":0.09244,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17015,"mean_force":0.05799,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49913,0.03679,0.02797]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1326.0,"contact_point_centroid":[0.62194,0.15093,0.18024],"force_p95":0.07498,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1627,"mean_force":0.042,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.62131,0.16997,0.17768]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7467.0,"contact_point_centroid":[0.62113,0.18621,0.25948],"force_p95":0.07684,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15064,"mean_force":0.05074,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.62069,0.16712,0.25773]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7893.0,"contact_point_centroid":[0.62109,0.14799,0.25784],"force_p95":0.07085,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14821,"mean_force":0.04825,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.62077,0.16721,0.25566]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1126.0,"contact_point_centroid":[0.62241,0.18928,0.17902],"force_p95":0.08099,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14668,"mean_force":0.04876,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.62126,0.16995,0.17756]},{"body_a":"world","body_b":"grasp_target","contact_count":2832.0,"contact_point_centroid":[0.60095,0.17206,-0.00198],"force_p95":0.12431,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.14373,"mean_force":0.12203,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.62038,0.16981,0.28878]},{"body_a":"world","body_b":"grasp_target","contact_count":3316.0,"contact_point_centroid":[0.51251,0.03972,-0.00195],"force_p95":0.12693,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12277,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.50254,0.01863,0.16692]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4929.0,"contact_point_centroid":[0.50007,0.05606,0.02992],"force_p95":0.08221,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08815,"mean_force":0.04657,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49914,0.03679,0.02798]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16495.0,"contact_point_centroid":[0.56414,0.12158,0.26666],"force_p95":0.06853,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08788,"mean_force":0.04773,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.56408,0.10238,0.26563]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17128.0,"contact_point_centroid":[0.56359,0.08266,0.26644],"force_p95":0.06842,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08497,"mean_force":0.04576,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.56359,0.10182,0.26507]}],"total_contact_groups":15},"final_pose_error":0.01994,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.60094,0.17206,0.02602],"final_tcp_position":[0.62614,0.17181,0.37774],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":1.6679,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":0.0,"n_steps_budget":0.0,"object_pos_end":[0.51251,0.03972,0.03],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21001,"object_to_goal_dist_start":0.21001,"peak_contact_force":0.0,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_object","tcp_end":[0.49977,-0.0,0.30085],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.27404,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":830.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3316.0,"raw_peak_contact_force":0.13845,"subtask_id":"grasp_success","tcp_end":[0.50733,0.03739,0.03691],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.01228,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51244,0.03696,0.02512],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21449,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.18374,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10296.0,"raw_peak_contact_force":0.28648,"subtask_id":"grasp_success","tcp_end":[0.4991,0.03678,0.02794],"tcp_start":[0.50733,0.03739,0.03691],"tcp_to_object_dist_end":0.01363,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":629.0,"n_steps_budget":1000.0,"object_pos_end":[0.51916,0.03685,0.19526],"object_pos_start":[0.51244,0.03696,0.02512],"object_to_goal_dist_end":0.18078,"object_to_goal_dist_start":0.21449,"object_z_max":0.195,"peak_contact_force":0.08025,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":24503.0,"raw_peak_contact_force":0.57601,"subtask_id":"lift_clearance","tcp_end":[0.50823,0.03669,0.20337],"tcp_start":[0.4991,0.03678,0.02794],"tcp_to_object_dist_end":0.01361,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":787.0,"n_steps_budget":1000.0,"object_pos_end":[0.62756,0.16439,0.31494],"object_pos_start":[0.51916,0.03685,0.19526],"object_to_goal_dist_end":0.17011,"object_to_goal_dist_start":0.18078,"object_z_max":0.3148,"peak_contact_force":0.0677,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":33623.0,"raw_peak_contact_force":0.08788,"subtask_id":"transport_accuracy","tcp_end":[0.61947,0.16449,0.32861],"tcp_start":[0.50823,0.03669,0.20337],"tcp_to_object_dist_end":0.01588,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":374.0,"n_steps_budget":1000.0,"object_pos_end":[0.61231,0.16983,0.16597],"object_pos_start":[0.62756,0.16439,0.31494],"object_to_goal_dist_end":0.02606,"object_to_goal_dist_start":0.17011,"object_z_max":0.31496,"peak_contact_force":0.08143,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":15360.0,"raw_peak_contact_force":0.15064,"subtask_id":"place_accuracy","tcp_end":[0.62327,0.17053,0.18213],"tcp_start":[0.61947,0.16449,0.32861],"tcp_to_object_dist_end":0.01953,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.60227,0.17109,0.02566],"object_pos_start":[0.61231,0.16983,0.16597],"object_to_goal_dist_end":0.12203,"object_to_goal_dist_start":0.02606,"object_z_max":0.16597,"peak_contact_force":0.09019,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2694.0,"raw_peak_contact_force":1.6679,"subtask_id":"place_accuracy","tcp_end":[0.61743,0.16867,0.20102],"tcp_start":[0.62327,0.17053,0.18213],"tcp_to_object_dist_end":0.17604,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":708.0,"n_steps_budget":1000.0,"object_pos_end":[0.60094,0.17206,0.02602],"object_pos_start":[0.60227,0.17109,0.02566],"object_to_goal_dist_end":0.12195,"object_to_goal_dist_start":0.12203,"object_z_max":0.02663,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2832.0,"raw_peak_contact_force":0.14373,"tcp_end":[0.62614,0.17181,0.37774],"tcp_start":[0.61743,0.16867,0.20102],"tcp_to_object_dist_end":0.35262,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.3011,"average_solve_count":362.0,"average_success_count":362.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.09749,"descend_grasp.grasp_z_offset":-0.00568,"descend_place.place_z_offset":-0.00349,"grasp_1.grasp_duration":1.39762,"lift_1.lift_height":0.24525,"lift_1.lift_speed":0.03873,"release_1.release_duration":0.61596,"retract_1.retract_height":0.20045,"transport_to_goal.transport_speed":0.04035},"optimized_scores":{"best_composite_score":-0.02119,"best_fitness_score":0.60881,"best_task_score":0.25406},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":146.0,"contact_point_centroid":[0.56095,0.22964,-0.0103],"force_p95":1.36814,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.19053,"mean_force":0.53911,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57527,0.22486,0.2804]},{"body_a":"world","body_b":"grasp_target","contact_count":96.0,"contact_point_centroid":[0.4785,0.04437,-0.00176],"force_p95":0.64083,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.67692,"mean_force":0.23436,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47025,0.0451,0.02642]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48285,0.04812,-0.00234],"force_p95":0.21883,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.31019,"mean_force":0.1485,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47241,0.04534,0.02611]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":15764.0,"contact_point_centroid":[0.47341,0.06414,0.14058],"force_p95":0.07773,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28692,"mean_force":0.05095,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47337,0.045,0.13864]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":15426.0,"contact_point_centroid":[0.47325,0.02583,0.13893],"force_p95":0.07766,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25087,"mean_force":0.05096,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47328,0.04499,0.13694]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4483.0,"contact_point_centroid":[0.4716,0.02595,0.02762],"force_p95":0.08284,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16334,"mean_force":0.04769,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47129,0.04523,0.02498]},{"body_a":"world","body_b":"grasp_target","contact_count":1896.0,"contact_point_centroid":[0.56102,0.22961,-0.00208],"force_p95":0.13044,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.16186,"mean_force":0.11833,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.57722,0.22606,0.34787]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1328.0,"contact_point_centroid":[0.57851,0.20711,0.26477],"force_p95":0.07768,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15448,"mean_force":0.04251,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57771,0.22617,0.26206]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7238.0,"contact_point_centroid":[0.57815,0.24185,0.3432],"force_p95":0.07665,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14838,"mean_force":0.05272,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.57762,0.2228,0.34123]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8023.0,"contact_point_centroid":[0.57791,0.20358,0.34362],"force_p95":0.07207,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1458,"mean_force":0.0481,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.57762,0.2228,0.34126]},{"body_a":"world","body_b":"grasp_target","contact_count":3324.0,"contact_point_centroid":[0.4827,0.04873,-0.00195],"force_p95":0.12693,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12277,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.48847,0.02289,0.16489]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1199.0,"contact_point_centroid":[0.5786,0.24546,0.26364],"force_p95":0.08245,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13714,"mean_force":0.04631,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57765,0.22614,0.2619]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":19089.0,"contact_point_centroid":[0.52755,0.11475,0.33376],"force_p95":0.06903,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08819,"mean_force":0.04657,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52748,0.13389,0.33175]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5710.0,"contact_point_centroid":[0.47068,0.06476,0.02638],"force_p95":0.07692,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08536,"mean_force":0.04156,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4713,0.04523,0.02499]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18167.0,"contact_point_centroid":[0.52725,0.15239,0.33281],"force_p95":0.0704,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08086,"mean_force":0.04912,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52709,0.13319,0.3311]}],"total_contact_groups":15},"final_pose_error":0.01995,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.56102,0.2296,0.02602],"final_tcp_position":[0.58086,0.22801,0.41102],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":2.19053,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":0.0,"n_steps_budget":0.0,"object_pos_end":[0.4827,0.04873,0.03],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28719,"object_to_goal_dist_start":0.28719,"peak_contact_force":0.0,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_object","tcp_end":[0.49977,-0.0,0.30085],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.27573,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":832.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3324.0,"raw_peak_contact_force":0.13845,"subtask_id":"grasp_success","tcp_end":[0.47916,0.04592,0.03298],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.0083,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48261,0.04545,0.02485],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29287,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.20052,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11993.0,"raw_peak_contact_force":0.31019,"subtask_id":"grasp_success","tcp_end":[0.47126,0.04522,0.02495],"tcp_start":[0.47916,0.04592,0.03298],"tcp_to_object_dist_end":0.01135,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":774.0,"n_steps_budget":1000.0,"object_pos_end":[0.48915,0.04526,0.24524],"object_pos_start":[0.48261,0.04545,0.02485],"object_to_goal_dist_end":0.20621,"object_to_goal_dist_start":0.29287,"object_z_max":0.24496,"peak_contact_force":0.07134,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":31286.0,"raw_peak_contact_force":0.67692,"subtask_id":"lift_clearance","tcp_end":[0.4792,0.04516,0.25068],"tcp_start":[0.47126,0.04522,0.02495],"tcp_to_object_dist_end":0.01135,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":897.0,"n_steps_budget":1000.0,"object_pos_end":[0.58425,0.21947,0.40248],"object_pos_start":[0.48915,0.04526,0.24524],"object_to_goal_dist_end":0.17227,"object_to_goal_dist_start":0.20621,"object_z_max":0.40233,"peak_contact_force":0.06867,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":37256.0,"raw_peak_contact_force":0.08819,"subtask_id":"transport_accuracy","tcp_end":[0.57644,0.21943,0.41373],"tcp_start":[0.4792,0.04516,0.25068],"tcp_to_object_dist_end":0.0137,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":382.0,"n_steps_budget":1000.0,"object_pos_end":[0.56659,0.2258,0.25169],"object_pos_start":[0.58425,0.21947,0.40248],"object_to_goal_dist_end":0.02632,"object_to_goal_dist_start":0.17227,"object_z_max":0.40248,"peak_contact_force":0.08341,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":15261.0,"raw_peak_contact_force":0.14838,"subtask_id":"place_accuracy","tcp_end":[0.57909,0.22674,0.26618],"tcp_start":[0.57644,0.21943,0.41373],"tcp_to_object_dist_end":0.01916,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.56289,0.22483,0.01515],"object_pos_start":[0.56659,0.2258,0.25169],"object_to_goal_dist_end":0.21621,"object_to_goal_dist_start":0.02632,"object_z_max":0.25169,"peak_contact_force":0.17272,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2673.0,"raw_peak_contact_force":2.19053,"subtask_id":"place_accuracy","tcp_end":[0.57525,0.22486,0.28608],"tcp_start":[0.57909,0.22674,0.26618],"tcp_to_object_dist_end":0.27122,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":474.0,"n_steps_budget":930.0,"object_pos_end":[0.56102,0.2296,0.02602],"object_pos_start":[0.56289,0.22483,0.01515],"object_to_goal_dist_end":0.20553,"object_to_goal_dist_start":0.21621,"object_z_max":0.02688,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1896.0,"raw_peak_contact_force":0.16186,"tcp_end":[0.58086,0.22801,0.41102],"tcp_start":[0.57525,0.22486,0.28608],"tcp_to_object_dist_end":0.38552,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```