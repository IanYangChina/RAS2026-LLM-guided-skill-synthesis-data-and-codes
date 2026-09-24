## Search State

- **Seed**: 6
- **Iteration**: 6 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 5 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | impedance_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 9 | 0.0037 | 0.31 | ❌ rejected |
| 4 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | impedance_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 9 | 0.0030 | 0.31 | ❌ rejected |
| 3 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | impedance_control | impedance_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 9 | 0.0038 | 0.31 | ✅ accepted |
| 2 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | impedance_control | impedance_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 9 | 0.0037 | 0.31 | ✅ accepted |
| 1 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 5 | 0.1410 | 0.18 | ❌ rejected |

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
- **task_score** (E): 0.307
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
| lift_1 | 1.00 | 1.00 | 0.1747 |
| transport_to_goal | 1.00 | 1.00 | 0.2632 |
| descend_place | 1.00 | 1.00 | 0.1655 |
| release_1 | 1.00 | 1.00 | 0.0205 |
| retract_1 | 1.00 | 1.00 | 0.1598 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 0.00 / guard_failure | (0.500, -0.000, 0.301)→(0.500, -0.000, 0.301) | (0.500, 0.024, 0.030)→(0.500, 0.024, 0.030) | 0.269→0.269 | 0.00 / 0.000 | 0.000 | 0.000 |
| descend_grasp | descend | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.495, 0.023, 0.035) | (0.500, 0.024, 0.030)→(0.500, 0.024, 0.026) | 0.269→0.271 | 1.00 / 4.000 | 0.123 | 0.138 |
| grasp_1 | grasp | 1.00 / step_budget | (0.495, 0.023, 0.035)→(0.487, 0.022, 0.027) | (0.500, 0.024, 0.026)→(0.500, 0.023, 0.025) | 0.271→0.273 | 1.00 / 42.333 | 0.177 | 0.273 |
| lift_1 | lift | 1.00 / step_budget | (0.487, 0.022, 0.027)→(0.495, 0.022, 0.201) | (0.500, 0.023, 0.025)→(0.506, 0.022, 0.195) | 0.273→0.201 | 1.00 / 40.000 | 0.077 | 0.598 |
| transport_to_goal | approach | 1.00 / step_budget | (0.495, 0.022, 0.201)→(0.591, 0.183, 0.384) | (0.506, 0.022, 0.195)→(0.599, 0.183, 0.371) | 0.201→0.164 | 1.00 / 40.667 | 0.074 | 0.092 |
| descend_place | descend | 1.00 / step_budget | (0.591, 0.183, 0.384)→(0.595, 0.194, 0.219) | (0.599, 0.183, 0.371)→(0.581, 0.193, 0.203) | 0.164→0.019 | 1.00 / 38.333 | 104.666 | 0.153 |
| release_1 | release | 1.00 / step_budget | (0.595, 0.194, 0.219)→(0.590, 0.192, 0.239) | (0.581, 0.193, 0.203)→(0.576, 0.193, 0.021) | 0.019→0.189 | 1.00 / 4.000 | 0.124 | 1.892 |
| retract_1 | retract | 1.00 / step_budget | (0.590, 0.192, 0.239)→(0.598, 0.195, 0.399) | (0.576, 0.193, 0.021)→(0.575, 0.196, 0.026) | 0.189→0.184 | 1.00 / 4.000 | 0.123 | 0.144 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.443
- phase_score: 0.506
- phase_breakdown.lift_clearance_score: 0.184
- phase_breakdown.reach_object_score: 0.078
- phase_breakdown.transport_accuracy_score: 0.501
- phase_breakdown.grasp_success_score: 1.000
- phase_breakdown.place_accuracy_score: 0.767
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
- **Final σ (mean)**: 0.293


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.32967,"average_solve_count":364.0,"average_success_count":364.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.06308,"descend_grasp.grasp_z_offset":-0.00255,"descend_place.place_z_offset":-0.0021,"grasp_1.grasp_duration":1.32782,"lift_1.lift_height":0.24042,"lift_1.lift_speed":0.04347,"release_1.release_duration":0.30544,"retract_1.retract_height":0.20752,"transport_to_goal.transport_speed":0.03434},"optimized_scores":{"best_composite_score":-0.0376,"best_fitness_score":0.5924,"best_task_score":0.22589},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":151.0,"contact_point_centroid":[0.56519,0.18915,-0.00969],"force_p95":1.2846,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.10055,"mean_force":0.50773,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57991,0.18401,0.26966]},{"body_a":"world","body_b":"grasp_target","contact_count":88.0,"contact_point_centroid":[0.49953,-0.01455,-0.00147],"force_p95":0.57478,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.5963,"mean_force":0.22364,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49,-0.01475,0.02854]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16020.0,"contact_point_centroid":[0.49336,0.00451,0.13972],"force_p95":0.07144,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29171,"mean_force":0.04982,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49362,-0.01467,0.13789]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16224.0,"contact_point_centroid":[0.49319,-0.03383,0.13697],"force_p95":0.07177,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27831,"mean_force":0.04966,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49348,-0.01467,0.13543]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1268.0,"contact_point_centroid":[0.58133,0.16622,0.25281],"force_p95":0.08754,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26583,"mean_force":0.05322,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.58256,0.18513,0.25113]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50383,-0.01543,-0.00208],"force_p95":0.14765,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21956,"mean_force":0.12936,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49214,-0.01477,0.02865]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1034.0,"contact_point_centroid":[0.58253,0.2043,0.25114],"force_p95":0.10662,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18904,"mean_force":0.05716,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.58253,0.18511,0.25106]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8509.0,"contact_point_centroid":[0.58399,0.20071,0.34593],"force_p95":0.07907,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16782,"mean_force":0.05485,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.58341,0.18162,0.34397]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9725.0,"contact_point_centroid":[0.58359,0.16243,0.34636],"force_p95":0.07275,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15431,"mean_force":0.04896,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.5834,0.18161,0.34431]},{"body_a":"world","body_b":"grasp_target","contact_count":2388.0,"contact_point_centroid":[0.56524,0.18891,-0.00205],"force_p95":0.12768,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.14727,"mean_force":0.11953,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.58206,0.18507,0.35503]},{"body_a":"world","body_b":"grasp_target","contact_count":3248.0,"contact_point_centroid":[0.50382,-0.01567,-0.00195],"force_p95":0.12703,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12278,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.49844,-0.00738,0.16667]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4080.0,"contact_point_centroid":[0.49138,0.00445,0.03019],"force_p95":0.07862,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1321,"mean_force":0.05183,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49097,-0.01476,0.02743]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20959.0,"contact_point_centroid":[0.54047,0.06342,0.33869],"force_p95":0.06838,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09493,"mean_force":0.04635,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.54039,0.08252,0.33742]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":19070.0,"contact_point_centroid":[0.54164,0.10372,0.34096],"force_p95":0.07427,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09471,"mean_force":0.05025,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.54126,0.08451,0.33935]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4947.0,"contact_point_centroid":[0.49144,-0.03387,0.0293],"force_p95":0.07075,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08805,"mean_force":0.04477,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49097,-0.01476,0.02743]}],"total_contact_groups":15},"final_pose_error":0.01983,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.56524,0.1889,0.02602],"final_tcp_position":[0.58627,0.18687,0.43583],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":313.8334,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":0.0,"n_steps_budget":0.0,"object_pos_end":[0.50382,-0.01567,0.03],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.30942,"object_to_goal_dist_start":0.30942,"peak_contact_force":0.0,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_object","tcp_end":[0.49977,-0.0,0.30085],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.27133,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":813.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3248.0,"raw_peak_contact_force":0.13845,"subtask_id":"grasp_success","tcp_end":[0.4991,-0.01482,0.03607],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.01113,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50369,-0.01469,0.02571],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31184,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.14215,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10827.0,"raw_peak_contact_force":0.21956,"subtask_id":"grasp_success","tcp_end":[0.49094,-0.01475,0.02739],"tcp_start":[0.4991,-0.01482,0.03607],"tcp_to_object_dist_end":0.01286,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":771.0,"n_steps_budget":1000.0,"object_pos_end":[0.51083,-0.01466,0.23875],"object_pos_start":[0.50369,-0.01469,0.02571],"object_to_goal_dist_end":0.21616,"object_to_goal_dist_start":0.31184,"object_z_max":0.23848,"peak_contact_force":0.06938,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":32332.0,"raw_peak_contact_force":0.5963,"subtask_id":"lift_clearance","tcp_end":[0.50009,-0.01464,0.24661],"tcp_start":[0.49094,-0.01475,0.02739],"tcp_to_object_dist_end":0.01331,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":972.0,"n_steps_budget":1000.0,"object_pos_end":[0.58994,0.17822,0.41693],"object_pos_start":[0.51083,-0.01466,0.23875],"object_to_goal_dist_end":0.16909,"object_to_goal_dist_start":0.21616,"object_z_max":0.41678,"peak_contact_force":0.08517,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":40029.0,"raw_peak_contact_force":0.09493,"subtask_id":"transport_accuracy","tcp_end":[0.58278,0.17803,0.43122],"tcp_start":[0.50009,-0.01464,0.24661],"tcp_to_object_dist_end":0.01599,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":35.0,"n_steps":457.0,"n_steps_budget":1000.0,"object_pos_end":[0.567,0.18466,0.23695],"object_pos_start":[0.58994,0.17822,0.41693],"object_to_goal_dist_end":0.023,"object_to_goal_dist_start":0.16909,"object_z_max":0.41693,"peak_contact_force":313.8334,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":18234.0,"raw_peak_contact_force":0.16782,"subtask_id":"place_accuracy","tcp_end":[0.5841,0.18564,0.2553],"tcp_start":[0.58278,0.17803,0.43122],"tcp_to_object_dist_end":0.02511,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.56536,0.18378,0.01629],"object_pos_start":[0.567,0.18466,0.23695],"object_to_goal_dist_end":0.23286,"object_to_goal_dist_start":0.023,"object_z_max":0.23695,"peak_contact_force":0.15618,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2453.0,"raw_peak_contact_force":2.10055,"subtask_id":"place_accuracy","tcp_end":[0.57989,0.18401,0.27553],"tcp_start":[0.5841,0.18564,0.2553],"tcp_to_object_dist_end":0.25965,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":597.0,"n_steps_budget":1000.0,"object_pos_end":[0.56524,0.1889,0.02602],"object_pos_start":[0.56536,0.18378,0.01629],"object_to_goal_dist_end":0.22316,"object_to_goal_dist_start":0.23286,"object_z_max":0.02683,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2388.0,"raw_peak_contact_force":0.14727,"tcp_end":[0.58627,0.18687,0.43583],"tcp_start":[0.57989,0.18401,0.27553],"tcp_to_object_dist_end":0.41036,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.36607,"average_solve_count":336.0,"average_success_count":336.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.0307,"descend_grasp.grasp_z_offset":-0.00262,"descend_place.place_z_offset":0.00943,"grasp_1.grasp_duration":1.10364,"lift_1.lift_height":0.1657,"lift_1.lift_speed":0.04215,"release_1.release_duration":0.67943,"retract_1.retract_height":0.24227,"transport_to_goal.transport_speed":0.03829},"optimized_scores":{"best_composite_score":0.06994,"best_fitness_score":0.69994,"best_task_score":0.4427},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":267.0,"contact_point_centroid":[0.5998,0.17121,-0.00544],"force_p95":0.89552,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.5657,"mean_force":0.26596,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61701,0.16873,0.17199]},{"body_a":"world","body_b":"grasp_target","contact_count":98.0,"contact_point_centroid":[0.50852,0.03597,-0.00167],"force_p95":0.56802,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.58724,"mean_force":0.20081,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49809,0.03668,0.02796]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9585.0,"contact_point_centroid":[0.50155,0.01734,0.09804],"force_p95":0.08427,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30304,"mean_force":0.05597,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.50133,0.03653,0.09526]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10845.0,"contact_point_centroid":[0.50153,0.05561,0.09895],"force_p95":0.07939,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29973,"mean_force":0.05155,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.50148,0.03654,0.09701]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51264,0.03918,-0.00227],"force_p95":0.20269,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.28899,"mean_force":0.1435,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50029,0.03688,0.02789]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1323.0,"contact_point_centroid":[0.62171,0.15103,0.16112],"force_p95":0.07622,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16787,"mean_force":0.04262,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.62112,0.17007,0.15858]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3561.0,"contact_point_centroid":[0.50065,0.01759,0.02983],"force_p95":0.0926,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16704,"mean_force":0.05804,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4991,0.03679,0.02663]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1149.0,"contact_point_centroid":[0.62195,0.18936,0.15988],"force_p95":0.08181,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15008,"mean_force":0.04823,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.62105,0.17005,0.15844]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8467.0,"contact_point_centroid":[0.62145,0.18675,0.25029],"force_p95":0.07423,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14749,"mean_force":0.05028,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.62105,0.16766,0.24864]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8823.0,"contact_point_centroid":[0.62145,0.14854,0.24788],"force_p95":0.0713,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14417,"mean_force":0.04842,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.62112,0.16776,0.24572]},{"body_a":"world","body_b":"grasp_target","contact_count":2980.0,"contact_point_centroid":[0.59972,0.17121,-0.00198],"force_p95":0.12396,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.14114,"mean_force":0.12236,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.61994,0.16979,0.27425]},{"body_a":"world","body_b":"grasp_target","contact_count":3332.0,"contact_point_centroid":[0.51251,0.03972,-0.00195],"force_p95":0.12693,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12277,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.50253,0.01863,0.16622]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":19329.0,"contact_point_centroid":[0.56378,0.08336,0.25095],"force_p95":0.06882,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09237,"mean_force":0.04593,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.56382,0.10253,0.24956]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4929.0,"contact_point_centroid":[0.50005,0.05606,0.02858],"force_p95":0.08229,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08919,"mean_force":0.04665,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49912,0.03679,0.02664]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18617.0,"contact_point_centroid":[0.56427,0.1222,0.25121],"force_p95":0.06894,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08535,"mean_force":0.04793,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.56425,0.103,0.25015]}],"total_contact_groups":15},"final_pose_error":0.01978,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.59972,0.17121,0.02602],"final_tcp_position":[0.62599,0.17179,0.36759],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":1.5657,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":0.0,"n_steps_budget":0.0,"object_pos_end":[0.51251,0.03972,0.03],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21001,"object_to_goal_dist_start":0.21001,"peak_contact_force":0.0,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_object","tcp_end":[0.49977,-0.0,0.30085],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.27404,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":834.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3332.0,"raw_peak_contact_force":0.13845,"subtask_id":"grasp_success","tcp_end":[0.50732,0.03739,0.03556],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.01111,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51243,0.03691,0.02511],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21454,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.18434,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10290.0,"raw_peak_contact_force":0.28899,"subtask_id":"grasp_success","tcp_end":[0.49908,0.03678,0.0266],"tcp_start":[0.50732,0.03739,0.03556],"tcp_to_object_dist_end":0.01343,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":523.0,"n_steps_budget":1000.0,"object_pos_end":[0.51931,0.03656,0.16575],"object_pos_start":[0.51243,0.03691,0.02511],"object_to_goal_dist_end":0.17503,"object_to_goal_dist_start":0.21454,"object_z_max":0.16549,"peak_contact_force":0.08399,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":20528.0,"raw_peak_contact_force":0.58724,"subtask_id":"lift_clearance","tcp_end":[0.50777,0.03661,0.17161],"tcp_start":[0.49908,0.03678,0.0266],"tcp_to_object_dist_end":0.01294,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":888.0,"n_steps_budget":1000.0,"object_pos_end":[0.62888,0.16535,0.31531],"object_pos_start":[0.51931,0.03656,0.16575],"object_to_goal_dist_end":0.17044,"object_to_goal_dist_start":0.17503,"object_z_max":0.31517,"peak_contact_force":0.06819,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":37946.0,"raw_peak_contact_force":0.09237,"subtask_id":"transport_accuracy","tcp_end":[0.62027,0.16543,0.32803],"tcp_start":[0.50777,0.03661,0.17161],"tcp_to_object_dist_end":0.01536,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":420.0,"n_steps_budget":1000.0,"object_pos_end":[0.61118,0.16996,0.14749],"object_pos_start":[0.62888,0.16535,0.31531],"object_to_goal_dist_end":0.01677,"object_to_goal_dist_start":0.17044,"object_z_max":0.31534,"peak_contact_force":0.08232,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":17290.0,"raw_peak_contact_force":0.14749,"subtask_id":"place_accuracy","tcp_end":[0.62319,0.17067,0.16301],"tcp_start":[0.62027,0.16543,0.32803],"tcp_to_object_dist_end":0.01964,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.60035,0.17064,0.02626],"object_pos_start":[0.61118,0.16996,0.14749],"object_to_goal_dist_end":0.12186,"object_to_goal_dist_start":0.01677,"object_z_max":0.14749,"peak_contact_force":0.11073,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2739.0,"raw_peak_contact_force":1.5657,"subtask_id":"place_accuracy","tcp_end":[0.61695,0.16871,0.18195],"tcp_start":[0.62319,0.17067,0.16301],"tcp_to_object_dist_end":0.15658,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":745.0,"n_steps_budget":1000.0,"object_pos_end":[0.59972,0.17121,0.02602],"object_pos_start":[0.60035,0.17064,0.02626],"object_to_goal_dist_end":0.12223,"object_to_goal_dist_start":0.12186,"object_z_max":0.02657,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2980.0,"raw_peak_contact_force":0.14114,"tcp_end":[0.62599,0.17179,0.36759],"tcp_start":[0.61695,0.16871,0.18195],"tcp_to_object_dist_end":0.34258,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.31161,"average_solve_count":353.0,"average_success_count":353.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.04581,"descend_grasp.grasp_z_offset":-0.00488,"descend_place.place_z_offset":0.00079,"grasp_1.grasp_duration":1.76036,"lift_1.lift_height":0.17976,"lift_1.lift_speed":0.03078,"release_1.release_duration":0.35138,"retract_1.retract_height":0.18156,"transport_to_goal.transport_speed":0.03483},"optimized_scores":{"best_composite_score":-0.02136,"best_fitness_score":0.60864,"best_task_score":0.25383},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":174.0,"contact_point_centroid":[0.55968,0.22753,-0.00873],"force_p95":1.21216,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.01094,"mean_force":0.43806,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57358,0.2234,0.25278]},{"body_a":"world","body_b":"grasp_target","contact_count":106.0,"contact_point_centroid":[0.47882,0.04435,-0.0018],"force_p95":0.56629,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.61177,"mean_force":0.22825,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47022,0.04505,0.02731]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48286,0.04816,-0.00234],"force_p95":0.21912,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.30897,"mean_force":0.14852,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47244,0.04529,0.02716]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11093.0,"contact_point_centroid":[0.47317,0.06414,0.10609],"force_p95":0.08117,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26492,"mean_force":0.05219,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.473,0.04498,0.10424]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11100.0,"contact_point_centroid":[0.4732,0.02582,0.10611],"force_p95":0.07835,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20977,"mean_force":0.0508,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.473,0.04498,0.10419]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5010.0,"contact_point_centroid":[0.47095,0.0259,0.02802],"force_p95":0.07866,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16402,"mean_force":0.04303,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47131,0.04518,0.02603]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1328.0,"contact_point_centroid":[0.5773,0.20578,0.23814],"force_p95":0.07696,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1613,"mean_force":0.04222,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57641,0.22482,0.2354]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1171.0,"contact_point_centroid":[0.57752,0.24412,0.23698],"force_p95":0.08176,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14752,"mean_force":0.04733,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57635,0.22479,0.23525]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8280.0,"contact_point_centroid":[0.5731,0.23413,0.32059],"force_p95":0.07434,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14263,"mean_force":0.05008,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.57278,0.21508,0.31879]},{"body_a":"world","body_b":"grasp_target","contact_count":2016.0,"contact_point_centroid":[0.55974,0.22745,-0.00201],"force_p95":0.12777,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.14262,"mean_force":0.11961,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.57606,0.22521,0.3253]},{"body_a":"world","body_b":"grasp_target","contact_count":3312.0,"contact_point_centroid":[0.4827,0.04873,-0.00195],"force_p95":0.12693,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12277,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.48849,0.02286,0.16546]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8630.0,"contact_point_centroid":[0.5731,0.19597,0.32001],"force_p95":0.07209,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13706,"mean_force":0.04833,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.57286,0.21523,0.31771]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":21397.0,"contact_point_centroid":[0.52339,0.10911,0.29267],"force_p95":0.06943,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0897,"mean_force":0.04651,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52344,0.12827,0.29067]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5707.0,"contact_point_centroid":[0.4707,0.06476,0.02739],"force_p95":0.07715,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08518,"mean_force":0.04154,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47133,0.04518,0.02605]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20693.0,"contact_point_centroid":[0.52301,0.14674,0.29142],"force_p95":0.07023,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08476,"mean_force":0.04839,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52303,0.12755,0.28973]}],"total_contact_groups":15},"final_pose_error":0.01982,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.55974,0.22745,0.02602],"final_tcp_position":[0.5805,0.22784,0.3923],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":2.01094,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":0.0,"n_steps_budget":0.0,"object_pos_end":[0.4827,0.04873,0.03],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28719,"object_to_goal_dist_start":0.28719,"peak_contact_force":0.0,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_object","tcp_end":[0.49977,-0.0,0.30085],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.27573,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":829.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3312.0,"raw_peak_contact_force":0.13845,"subtask_id":"grasp_success","tcp_end":[0.4792,0.04587,0.03405],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.00921,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":48.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48261,0.04551,0.02483],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29285,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.20319,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12517.0,"raw_peak_contact_force":0.30897,"subtask_id":"grasp_success","tcp_end":[0.47129,0.04517,0.026],"tcp_start":[0.4792,0.04587,0.03405],"tcp_to_object_dist_end":0.01139,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":554.0,"n_steps_budget":1000.0,"object_pos_end":[0.48822,0.0453,0.18084],"object_pos_start":[0.48261,0.04551,0.02483],"object_to_goal_dist_end":0.21197,"object_to_goal_dist_start":0.29285,"object_z_max":0.18056,"peak_contact_force":0.07815,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":22299.0,"raw_peak_contact_force":0.61177,"subtask_id":"lift_clearance","tcp_end":[0.47838,0.04516,0.18519],"tcp_start":[0.47129,0.04517,0.026],"tcp_to_object_dist_end":0.01076,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.57683,0.20632,0.38207],"object_pos_start":[0.48822,0.0453,0.18084],"object_to_goal_dist_end":0.15333,"object_to_goal_dist_start":0.21197,"object_z_max":0.38187,"peak_contact_force":0.06727,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":42090.0,"raw_peak_contact_force":0.0897,"subtask_id":"transport_accuracy","tcp_end":[0.56871,0.20638,0.39337],"tcp_start":[0.47838,0.04516,0.18519],"tcp_to_object_dist_end":0.01392,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":414.0,"n_steps_budget":1000.0,"object_pos_end":[0.56628,0.22453,0.22516],"object_pos_start":[0.57683,0.20632,0.38207],"object_to_goal_dist_end":0.01703,"object_to_goal_dist_start":0.15333,"object_z_max":0.38213,"peak_contact_force":0.08269,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":16910.0,"raw_peak_contact_force":0.14263,"subtask_id":"place_accuracy","tcp_end":[0.57795,0.22539,0.23945],"tcp_start":[0.56871,0.20638,0.39337],"tcp_to_object_dist_end":0.01847,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.56088,0.22396,0.02012],"object_pos_start":[0.56628,0.22453,0.22516],"object_to_goal_dist_end":0.21147,"object_to_goal_dist_start":0.01703,"object_z_max":0.22516,"peak_contact_force":0.10561,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2673.0,"raw_peak_contact_force":2.01094,"subtask_id":"place_accuracy","tcp_end":[0.57355,0.22339,0.25949],"tcp_start":[0.57795,0.22539,0.23945],"tcp_to_object_dist_end":0.23971,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":504.0,"n_steps_budget":960.0,"object_pos_end":[0.55974,0.22745,0.02602],"object_pos_start":[0.56088,0.22396,0.02012],"object_to_goal_dist_end":0.20566,"object_to_goal_dist_start":0.21147,"object_z_max":0.02676,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2016.0,"raw_peak_contact_force":0.14262,"tcp_end":[0.5805,0.22784,0.3923],"tcp_start":[0.57355,0.22339,0.25949],"tcp_to_object_dist_end":0.36687,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```