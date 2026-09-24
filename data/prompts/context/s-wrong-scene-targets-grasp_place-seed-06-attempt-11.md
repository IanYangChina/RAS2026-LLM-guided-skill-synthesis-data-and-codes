## Search State

- **Seed**: 6
- **Iteration**: 12 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 11 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | impedance_control | impedance_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 9 | 0.0036 | 0.31 | ❌ rejected |
| 10 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | impedance_control | impedance_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 9 | 0.0038 | 0.31 | ✅ accepted |
| 9 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | force_threshold_switch | position_control | impedance_control | position_control | impedance_control | position_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 10 | -0.3346 | 0.17 | ❌ rejected |
| 8 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | impedance_control | position_control | impedance_control | position_control | impedance_control | position_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 11 | -0.3128 | 0.17 | ❌ rejected |
| 7 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | force_threshold_switch | position_control | impedance_control | impedance_control | impedance_control | position_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 10 | -0.2568 | 0.17 | ❌ rejected |

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
| descend_grasp | 1.00 | 1.00 | 0.2685 |
| grasp_1 | 1.00 | 1.00 | 0.0118 |
| lift_1 | 1.00 | 1.00 | 0.1829 |
| transport_to_goal | 1.00 | 1.00 | 0.2659 |
| descend_place | 1.00 | 1.00 | 0.1443 |
| release_1 | 1.00 | 1.00 | 0.0202 |
| retract_1 | 1.00 | 1.00 | 0.1620 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 0.00 / guard_failure | (0.500, -0.000, 0.301)→(0.500, -0.000, 0.301) | (0.500, 0.024, 0.030)→(0.500, 0.024, 0.030) | 0.269→0.269 | 0.00 / 0.000 | 0.000 | 0.000 |
| descend_grasp | descend | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.495, 0.023, 0.035) | (0.500, 0.024, 0.030)→(0.500, 0.024, 0.026) | 0.269→0.271 | 1.00 / 4.000 | 0.123 | 0.138 |
| grasp_1 | grasp | 1.00 / step_budget | (0.495, 0.023, 0.035)→(0.487, 0.022, 0.026) | (0.500, 0.024, 0.026)→(0.500, 0.023, 0.025) | 0.271→0.273 | 1.00 / 41.333 | 0.176 | 0.273 |
| lift_1 | lift | 1.00 / step_budget | (0.487, 0.022, 0.026)→(0.495, 0.022, 0.209) | (0.500, 0.023, 0.025)→(0.506, 0.022, 0.203) | 0.273→0.199 | 1.00 / 40.000 | 0.078 | 0.629 |
| transport_to_goal | approach | 1.00 / step_budget | (0.495, 0.022, 0.209)→(0.593, 0.188, 0.391) | (0.506, 0.022, 0.203)→(0.602, 0.188, 0.377) | 0.199→0.170 | 1.00 / 38.000 | 0.082 | 0.101 |
| descend_place | descend | 1.00 / step_budget | (0.593, 0.188, 0.391)→(0.596, 0.194, 0.247) | (0.602, 0.188, 0.377)→(0.584, 0.194, 0.230) | 0.170→0.028 | 1.00 / 40.667 | 0.081 | 0.159 |
| release_1 | release | 1.00 / step_budget | (0.596, 0.194, 0.247)→(0.591, 0.193, 0.266) | (0.584, 0.194, 0.230)→(0.579, 0.193, 0.017) | 0.028→0.192 | 1.00 / 4.000 | 0.205 | 2.062 |
| retract_1 | retract | 1.00 / step_budget | (0.591, 0.193, 0.266)→(0.598, 0.196, 0.428) | (0.579, 0.193, 0.017)→(0.575, 0.197, 0.026) | 0.192→0.184 | 1.00 / 4.000 | 0.123 | 0.217 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.442
- phase_score: 0.465
- phase_breakdown.lift_clearance_score: 0.189
- phase_breakdown.reach_object_score: 0.078
- phase_breakdown.transport_accuracy_score: 0.507
- phase_breakdown.grasp_success_score: 1.000
- phase_breakdown.place_accuracy_score: 0.551
- grasp_place_fitness: 0.700

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.700
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.442
- **Median Q (composite search score)**: -0.021
- **K-run variance**: 0.0022
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.318


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.31492,"average_solve_count":362.0,"average_success_count":362.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.02658,"descend_grasp.grasp_z_offset":-0.00303,"descend_place.place_z_offset":-0.00994,"grasp_1.grasp_duration":1.37226,"lift_1.lift_height":0.24911,"lift_1.lift_speed":0.04392,"release_1.release_duration":0.55855,"retract_1.retract_height":0.22897,"transport_to_goal.transport_speed":0.03209},"optimized_scores":{"best_composite_score":-0.03759,"best_fitness_score":0.59241,"best_task_score":0.22577},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":139.0,"contact_point_centroid":[0.5643,0.18772,-0.0104],"force_p95":1.41821,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.2441,"mean_force":0.56796,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.5806,0.18406,0.29209]},{"body_a":"world","body_b":"grasp_target","contact_count":88.0,"contact_point_centroid":[0.49952,-0.01454,-0.00147],"force_p95":0.58164,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.6028,"mean_force":0.2255,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48998,-0.01475,0.02808]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16714.0,"contact_point_centroid":[0.4934,0.00451,0.14408],"force_p95":0.07124,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29251,"mean_force":0.04969,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49367,-0.01467,0.14226]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16896.0,"contact_point_centroid":[0.49324,-0.03383,0.14121],"force_p95":0.0717,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2777,"mean_force":0.0496,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49352,-0.01467,0.13967]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50383,-0.01542,-0.00208],"force_p95":0.14761,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22001,"mean_force":0.12936,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49213,-0.01477,0.02819]},{"body_a":"world","body_b":"grasp_target","contact_count":2364.0,"contact_point_centroid":[0.56441,0.18777,-0.00207],"force_p95":0.12525,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.20855,"mean_force":0.11899,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.5827,0.18517,0.37642]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7479.0,"contact_point_centroid":[0.58415,0.20059,0.35619],"force_p95":0.07852,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16883,"mean_force":0.05433,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.58348,0.18151,0.35405]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1243.0,"contact_point_centroid":[0.58274,0.20435,0.27473],"force_p95":0.07793,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15809,"mean_force":0.04525,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.58292,0.1851,0.27316]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1279.0,"contact_point_centroid":[0.58315,0.16597,0.27501],"force_p95":0.0788,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15808,"mean_force":0.04472,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.58297,0.18512,0.27328]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8528.0,"contact_point_centroid":[0.58381,0.16231,0.35681],"force_p95":0.07167,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15475,"mean_force":0.04826,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.58347,0.18147,0.35475]},{"body_a":"world","body_b":"grasp_target","contact_count":3252.0,"contact_point_centroid":[0.50382,-0.01567,-0.00195],"force_p95":0.12703,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12278,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.49843,-0.00738,0.16638]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4079.0,"contact_point_centroid":[0.49138,0.00445,0.02973],"force_p95":0.07861,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1315,"mean_force":0.05183,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49096,-0.01476,0.02696]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18444.0,"contact_point_centroid":[0.54138,0.10279,0.34454],"force_p95":0.07475,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09771,"mean_force":0.05056,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.54096,0.08358,0.34293]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20348.0,"contact_point_centroid":[0.54049,0.06316,0.34295],"force_p95":0.06859,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09344,"mean_force":0.04641,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.54039,0.08226,0.3417]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4947.0,"contact_point_centroid":[0.49143,-0.03387,0.02883],"force_p95":0.07073,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08843,"mean_force":0.04478,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49096,-0.01476,0.02697]}],"total_contact_groups":15},"final_pose_error":0.01998,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.56442,0.18777,0.02602],"final_tcp_position":[0.58668,0.18696,0.45711],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":2.2441,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":0.0,"n_steps_budget":0.0,"object_pos_end":[0.50382,-0.01567,0.03],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.30942,"object_to_goal_dist_start":0.30942,"peak_contact_force":0.0,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_object","tcp_end":[0.49977,-0.0,0.30085],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.27133,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":814.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3252.0,"raw_peak_contact_force":0.13845,"subtask_id":"grasp_success","tcp_end":[0.4991,-0.01483,0.0356],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.01071,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50369,-0.01468,0.02572],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31184,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.14207,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10826.0,"raw_peak_contact_force":0.22001,"subtask_id":"grasp_success","tcp_end":[0.49093,-0.01475,0.02693],"tcp_start":[0.4991,-0.01483,0.0356],"tcp_to_object_dist_end":0.01282,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":803.0,"n_steps_budget":1000.0,"object_pos_end":[0.51101,-0.01466,0.24765],"object_pos_start":[0.50369,-0.01468,0.02572],"object_to_goal_dist_end":0.21589,"object_to_goal_dist_start":0.31184,"object_z_max":0.24738,"peak_contact_force":0.06943,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":33698.0,"raw_peak_contact_force":0.6028,"subtask_id":"lift_clearance","tcp_end":[0.5002,-0.01464,0.25535],"tcp_start":[0.49093,-0.01475,0.02693],"tcp_to_object_dist_end":0.01327,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":945.0,"n_steps_budget":1000.0,"object_pos_end":[0.59003,0.17805,0.41734],"object_pos_start":[0.51101,-0.01466,0.24765],"object_to_goal_dist_end":0.16951,"object_to_goal_dist_start":0.21589,"object_z_max":0.41719,"peak_contact_force":0.08754,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":38792.0,"raw_peak_contact_force":0.09771,"subtask_id":"transport_accuracy","tcp_end":[0.58268,0.17777,0.43138],"tcp_start":[0.5002,-0.01464,0.25535],"tcp_to_object_dist_end":0.01585,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":400.0,"n_steps_budget":1000.0,"object_pos_end":[0.56994,0.18469,0.26],"object_pos_start":[0.59003,0.17805,0.41734],"object_to_goal_dist_end":0.0209,"object_to_goal_dist_start":0.16951,"object_z_max":0.41734,"peak_contact_force":0.08215,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":16007.0,"raw_peak_contact_force":0.16883,"subtask_id":"place_accuracy","tcp_end":[0.58433,0.18557,0.27735],"tcp_start":[0.58268,0.17777,0.43138],"tcp_to_object_dist_end":0.02256,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.56864,0.1838,0.01361],"object_pos_start":[0.56994,0.18469,0.26],"object_to_goal_dist_end":0.23525,"object_to_goal_dist_start":0.0209,"object_z_max":0.26,"peak_contact_force":0.22239,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2661.0,"raw_peak_contact_force":2.2441,"subtask_id":"place_accuracy","tcp_end":[0.58058,0.18406,0.29753],"tcp_start":[0.58433,0.18557,0.27735],"tcp_to_object_dist_end":0.28417,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":591.0,"n_steps_budget":1000.0,"object_pos_end":[0.56442,0.18777,0.02602],"object_pos_start":[0.56864,0.1838,0.01361],"object_to_goal_dist_end":0.22323,"object_to_goal_dist_start":0.23525,"object_z_max":0.02694,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2364.0,"raw_peak_contact_force":0.20855,"tcp_end":[0.58668,0.18696,0.45711],"tcp_start":[0.58058,0.18406,0.29753],"tcp_to_object_dist_end":0.43167,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.36304,"average_solve_count":303.0,"average_success_count":303.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.08877,"descend_grasp.grasp_z_offset":-0.00227,"descend_place.place_z_offset":0.00025,"grasp_1.grasp_duration":1.01045,"lift_1.lift_height":0.14441,"lift_1.lift_speed":0.04244,"release_1.release_duration":0.57727,"retract_1.retract_height":0.21775,"transport_to_goal.transport_speed":0.04845},"optimized_scores":{"best_composite_score":0.06975,"best_fitness_score":0.69975,"best_task_score":0.44244},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":240.0,"contact_point_centroid":[0.59927,0.17198,-0.00612],"force_p95":1.02454,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.68117,"mean_force":0.30337,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61765,0.16884,0.19381]},{"body_a":"world","body_b":"grasp_target","contact_count":98.0,"contact_point_centroid":[0.50855,0.03598,-0.00167],"force_p95":0.56454,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.58299,"mean_force":0.19644,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49813,0.03668,0.0283]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8286.0,"contact_point_centroid":[0.50141,0.01734,0.08786],"force_p95":0.0843,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30357,"mean_force":0.05564,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.50123,0.03654,0.08509]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9319.0,"contact_point_centroid":[0.50137,0.05562,0.08859],"force_p95":0.0801,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29968,"mean_force":0.05161,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.50138,0.03654,0.08663]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51264,0.03918,-0.00227],"force_p95":0.20207,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.28836,"mean_force":0.14332,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50029,0.03688,0.02823]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3562.0,"contact_point_centroid":[0.50066,0.0176,0.03016],"force_p95":0.09254,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16614,"mean_force":0.05802,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49911,0.03679,0.02696]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1324.0,"contact_point_centroid":[0.62206,0.15108,0.18203],"force_p95":0.07265,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15825,"mean_force":0.0418,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.62146,0.17012,0.17952]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7398.0,"contact_point_centroid":[0.62182,0.18681,0.25974],"force_p95":0.07523,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15718,"mean_force":0.05013,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.6214,0.16792,0.25814]},{"body_a":"world","body_b":"grasp_target","contact_count":2268.0,"contact_point_centroid":[0.59931,0.17198,-0.00197],"force_p95":0.12624,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15104,"mean_force":0.12181,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.62025,0.16984,0.27247]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6881.0,"contact_point_centroid":[0.62149,0.14888,0.25399],"force_p95":0.08008,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14932,"mean_force":0.05487,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.62156,0.16815,0.25191]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1128.0,"contact_point_centroid":[0.6226,0.18943,0.18078],"force_p95":0.07867,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14829,"mean_force":0.04874,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.6214,0.1701,0.1794]},{"body_a":"world","body_b":"grasp_target","contact_count":3328.0,"contact_point_centroid":[0.51251,0.03972,-0.00195],"force_p95":0.12693,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12277,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.50253,0.01863,0.16641]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18098.0,"contact_point_centroid":[0.56362,0.08295,0.23951],"force_p95":0.07846,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10103,"mean_force":0.05268,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.5631,0.10206,0.23796]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18519.0,"contact_point_centroid":[0.5666,0.12443,0.2439],"force_p95":0.07492,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0953,"mean_force":0.05159,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.56605,0.10535,0.24258]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4929.0,"contact_point_centroid":[0.50005,0.05606,0.02892],"force_p95":0.08221,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08894,"mean_force":0.04664,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49912,0.03679,0.02698]}],"total_contact_groups":15},"final_pose_error":0.01982,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.5993,0.17199,0.02602],"final_tcp_position":[0.62548,0.17165,0.34308],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":1.68117,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":0.0,"n_steps_budget":0.0,"object_pos_end":[0.51251,0.03972,0.03],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21001,"object_to_goal_dist_start":0.21001,"peak_contact_force":0.0,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_object","tcp_end":[0.49977,-0.0,0.30085],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.27404,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":833.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3328.0,"raw_peak_contact_force":0.13845,"subtask_id":"grasp_success","tcp_end":[0.50733,0.03739,0.0359],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.0114,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51243,0.03692,0.02512],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21452,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.18389,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10291.0,"raw_peak_contact_force":0.28836,"subtask_id":"grasp_success","tcp_end":[0.49908,0.03678,0.02693],"tcp_start":[0.50733,0.03739,0.0359],"tcp_to_object_dist_end":0.01347,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":447.0,"n_steps_budget":1000.0,"object_pos_end":[0.51905,0.03658,0.14474],"object_pos_start":[0.51243,0.03692,0.02512],"object_to_goal_dist_end":0.17394,"object_to_goal_dist_start":0.21452,"object_z_max":0.14448,"peak_contact_force":0.0843,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":17703.0,"raw_peak_contact_force":0.58299,"subtask_id":"lift_clearance","tcp_end":[0.50741,0.03661,0.15018],"tcp_start":[0.49908,0.03678,0.02693],"tcp_to_object_dist_end":0.01285,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":35.0,"n_steps":956.0,"n_steps_budget":1000.0,"object_pos_end":[0.62937,0.16564,0.31359],"object_pos_start":[0.51905,0.03658,0.14474],"object_to_goal_dist_end":0.16871,"object_to_goal_dist_start":0.17394,"object_z_max":0.31344,"peak_contact_force":0.09077,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":36617.0,"raw_peak_contact_force":0.10103,"subtask_id":"transport_accuracy","tcp_end":[0.62063,0.16587,0.32761],"tcp_start":[0.50741,0.03661,0.15018],"tcp_to_object_dist_end":0.01653,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":365.0,"n_steps_budget":1000.0,"object_pos_end":[0.61259,0.17018,0.16732],"object_pos_start":[0.62937,0.16564,0.31359],"object_to_goal_dist_end":0.02696,"object_to_goal_dist_start":0.16871,"object_z_max":0.31362,"peak_contact_force":0.07905,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":14279.0,"raw_peak_contact_force":0.15718,"subtask_id":"place_accuracy","tcp_end":[0.6234,0.17068,0.18397],"tcp_start":[0.62063,0.16587,0.32761],"tcp_to_object_dist_end":0.01986,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.6016,0.17069,0.02553],"object_pos_start":[0.61259,0.17018,0.16732],"object_to_goal_dist_end":0.1223,"object_to_goal_dist_start":0.02696,"object_z_max":0.16732,"peak_contact_force":0.08522,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2692.0,"raw_peak_contact_force":1.68117,"subtask_id":"place_accuracy","tcp_end":[0.6176,0.16883,0.20285],"tcp_start":[0.6234,0.17068,0.18397],"tcp_to_object_dist_end":0.17805,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":567.0,"n_steps_budget":1000.0,"object_pos_end":[0.5993,0.17199,0.02602],"object_pos_start":[0.6016,0.17069,0.02553],"object_to_goal_dist_end":0.12232,"object_to_goal_dist_start":0.1223,"object_z_max":0.02668,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2268.0,"raw_peak_contact_force":0.15104,"tcp_end":[0.62548,0.17165,0.34308],"tcp_start":[0.6176,0.16883,0.20285],"tcp_to_object_dist_end":0.31814,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.34104,"average_solve_count":346.0,"average_success_count":346.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.04708,"descend_grasp.grasp_z_offset":-0.00543,"descend_place.place_z_offset":0.00886,"grasp_1.grasp_duration":0.60626,"lift_1.lift_height":0.21673,"lift_1.lift_speed":0.0465,"release_1.release_duration":0.87622,"retract_1.retract_height":0.27345,"transport_to_goal.transport_speed":0.04312},"optimized_scores":{"best_composite_score":-0.02129,"best_fitness_score":0.60871,"best_task_score":0.25388},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":135.0,"contact_point_centroid":[0.56017,0.23062,-0.01028],"force_p95":1.48014,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.2613,"mean_force":0.58622,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57569,0.225,0.29307]},{"body_a":"world","body_b":"grasp_target","contact_count":95.0,"contact_point_centroid":[0.47873,0.04414,-0.00173],"force_p95":0.65801,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.70204,"mean_force":0.22558,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47029,0.04507,0.02698]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48286,0.04813,-0.00234],"force_p95":0.2194,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.30985,"mean_force":0.14858,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47242,0.0453,0.02654]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":13547.0,"contact_point_centroid":[0.47334,0.06412,0.12565],"force_p95":0.07935,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30003,"mean_force":0.05167,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47323,0.04497,0.12375]},{"body_a":"world","body_b":"grasp_target","contact_count":2729.0,"contact_point_centroid":[0.56023,0.23066,-0.00208],"force_p95":0.12783,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.29242,"mean_force":0.12056,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.57803,0.22632,0.39013]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13301.0,"contact_point_centroid":[0.4732,0.0258,0.12413],"force_p95":0.07806,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26442,"mean_force":0.05148,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47314,0.04496,0.12217]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4492.0,"contact_point_centroid":[0.47159,0.02591,0.02803],"force_p95":0.08295,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16471,"mean_force":0.04762,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47129,0.04519,0.0254]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6655.0,"contact_point_centroid":[0.57839,0.2423,0.3489],"force_p95":0.07651,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15087,"mean_force":0.05199,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.57792,0.22324,0.34694]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7321.0,"contact_point_centroid":[0.57816,0.20401,0.34933],"force_p95":0.07121,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14939,"mean_force":0.04781,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.57791,0.22323,0.3471]},{"body_a":"world","body_b":"grasp_target","contact_count":3320.0,"contact_point_centroid":[0.4827,0.04873,-0.00195],"force_p95":0.12693,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12277,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.48849,0.02287,0.16516]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1328.0,"contact_point_centroid":[0.57893,0.20722,0.27712],"force_p95":0.07533,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.138,"mean_force":0.04134,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57794,0.22625,0.27435]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1127.0,"contact_point_centroid":[0.57943,0.24557,0.27582],"force_p95":0.08098,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13191,"mean_force":0.04808,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57791,0.22623,0.27425]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":21339.0,"contact_point_centroid":[0.52713,0.1148,0.3186],"force_p95":0.06896,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10363,"mean_force":0.04608,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52718,0.13397,0.31705]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20595.0,"contact_point_centroid":[0.52735,0.15346,0.31856],"force_p95":0.06922,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09672,"mean_force":0.04803,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52734,0.13425,0.31737]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5708.0,"contact_point_centroid":[0.47068,0.06473,0.02678],"force_p95":0.07697,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08549,"mean_force":0.04157,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47131,0.0452,0.02542]}],"total_contact_groups":15},"final_pose_error":0.01995,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.56006,0.23082,0.02602],"final_tcp_position":[0.58232,0.22855,0.48399],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":2.2613,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":0.0,"n_steps_budget":0.0,"object_pos_end":[0.4827,0.04873,0.03],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28719,"object_to_goal_dist_start":0.28719,"peak_contact_force":0.0,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_object","tcp_end":[0.49977,-0.0,0.30085],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.27573,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":831.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3320.0,"raw_peak_contact_force":0.13845,"subtask_id":"grasp_success","tcp_end":[0.47918,0.04589,0.03341],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.00867,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48261,0.04544,0.02485],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29288,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.20112,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12000.0,"raw_peak_contact_force":0.30985,"subtask_id":"grasp_success","tcp_end":[0.47127,0.04519,0.02538],"tcp_start":[0.47918,0.04589,0.03341],"tcp_to_object_dist_end":0.01136,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":672.0,"n_steps_budget":1000.0,"object_pos_end":[0.48882,0.04505,0.2167],"object_pos_start":[0.48261,0.04544,0.02485],"object_to_goal_dist_end":0.20648,"object_to_goal_dist_start":0.29288,"object_z_max":0.21643,"peak_contact_force":0.07943,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":26943.0,"raw_peak_contact_force":0.70204,"subtask_id":"lift_clearance","tcp_end":[0.47883,0.04513,0.22194],"tcp_start":[0.47127,0.04519,0.02538],"tcp_to_object_dist_end":0.01127,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":983.0,"n_steps_budget":1000.0,"object_pos_end":[0.58536,0.22019,0.40097],"object_pos_start":[0.48882,0.04505,0.2167],"object_to_goal_dist_end":0.17074,"object_to_goal_dist_start":0.20648,"object_z_max":0.40081,"peak_contact_force":0.06875,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":41934.0,"raw_peak_contact_force":0.10363,"subtask_id":"transport_accuracy","tcp_end":[0.57686,0.22022,0.41318],"tcp_start":[0.47883,0.04513,0.22194],"tcp_to_object_dist_end":0.01487,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":348.0,"n_steps_budget":1000.0,"object_pos_end":[0.569,0.2259,0.26336],"object_pos_start":[0.58536,0.22019,0.40097],"object_to_goal_dist_end":0.03542,"object_to_goal_dist_start":0.17074,"object_z_max":0.40099,"peak_contact_force":0.08174,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":13976.0,"raw_peak_contact_force":0.15087,"subtask_id":"place_accuracy","tcp_end":[0.57924,0.2268,0.27849],"tcp_start":[0.57686,0.22022,0.41318],"tcp_to_object_dist_end":0.01829,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.56547,0.22429,0.01228],"object_pos_start":[0.569,0.2259,0.26336],"object_to_goal_dist_end":0.21886,"object_to_goal_dist_start":0.03542,"object_z_max":0.26336,"peak_contact_force":0.3083,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2590.0,"raw_peak_contact_force":2.2613,"subtask_id":"place_accuracy","tcp_end":[0.57567,0.225,0.29835],"tcp_start":[0.57924,0.2268,0.27849],"tcp_to_object_dist_end":0.28625,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":688.0,"n_steps_budget":1000.0,"object_pos_end":[0.56006,0.23082,0.02602],"object_pos_start":[0.56547,0.22429,0.01228],"object_to_goal_dist_end":0.20563,"object_to_goal_dist_start":0.21886,"object_z_max":0.02693,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2729.0,"raw_peak_contact_force":0.29242,"tcp_end":[0.58232,0.22855,0.48399],"tcp_start":[0.57567,0.225,0.29835],"tcp_to_object_dist_end":0.45852,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```