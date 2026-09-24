## Search State

- **Seed**: 6
- **Iteration**: 5 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 4 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | impedance_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 9 | 0.0030 | 0.31 | ❌ rejected |
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

## Current Skill (Q=0.003) — your mutation base

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

- **Composite score**: 0.003
- **task_score** (E): 0.307
- **fitness_score**: 0.633  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.630

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1076 |
| descend_grasp | 1.00 | 1.00 | 0.1616 |
| grasp_1 | 1.00 | 1.00 | 0.0118 |
| lift_1 | 1.00 | 1.00 | 0.1738 |
| transport_to_goal | 0.67 | 1.00 | 0.2581 |
| descend_place | 1.00 | 1.00 | 0.1258 |
| release_1 | 1.00 | 1.00 | 0.0197 |
| retract_1 | 1.00 | 1.00 | 0.1510 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.497, 0.020, 0.198) | (0.500, 0.024, 0.030)→(0.500, 0.024, 0.026) | 0.269→0.271 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_grasp | descend | 1.00 / step_budget | (0.497, 0.020, 0.198)→(0.495, 0.024, 0.036) | (0.500, 0.024, 0.026)→(0.500, 0.024, 0.026) | 0.271→0.271 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.495, 0.024, 0.036)→(0.487, 0.023, 0.028) | (0.500, 0.024, 0.026)→(0.500, 0.023, 0.026) | 0.271→0.272 | 1.00 / 43.000 | 0.152 | 0.226 |
| lift_1 | lift | 1.00 / step_budget | (0.487, 0.023, 0.028)→(0.495, 0.023, 0.201) | (0.500, 0.023, 0.026)→(0.506, 0.023, 0.195) | 0.272→0.202 | 1.00 / 40.333 | 0.076 | 0.561 |
| transport_to_goal | approach | 0.67 / step_budget | (0.495, 0.023, 0.201)→(0.590, 0.180, 0.381) | (0.506, 0.023, 0.195)→(0.598, 0.180, 0.368) | 0.202→0.161 | 1.00 / 42.000 | 0.069 | 0.091 |
| descend_place | descend | 1.00 / step_budget | (0.590, 0.180, 0.381)→(0.595, 0.192, 0.256) | (0.598, 0.180, 0.368)→(0.587, 0.191, 0.241) | 0.161→0.036 | 1.00 / 40.000 | 0.079 | 0.148 |
| release_1 | release | 1.00 / step_budget | (0.595, 0.192, 0.256)→(0.591, 0.191, 0.275) | (0.587, 0.191, 0.241)→(0.580, 0.191, 0.015) | 0.036→0.194 | 1.00 / 4.000 | 0.245 | 2.041 |
| retract_1 | retract | 1.00 / step_budget | (0.591, 0.191, 0.275)→(0.598, 0.196, 0.426) | (0.580, 0.191, 0.015)→(0.574, 0.194, 0.026) | 0.194→0.184 | 1.00 / 4.000 | 0.123 | 0.252 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.443
- phase_score: 0.599
- phase_breakdown.lift_clearance_score: 0.182
- phase_breakdown.reach_object_score: 0.673
- phase_breakdown.transport_accuracy_score: 0.673
- phase_breakdown.grasp_success_score: 1.000
- phase_breakdown.place_accuracy_score: 0.467
- grasp_place_fitness: 0.700

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.700
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.443
- **Median Q (composite search score)**: -0.023
- **K-run variance**: 0.0023
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.298


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.27778,"average_solve_count":360.0,"average_success_count":360.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.06543,"descend_grasp.grasp_z_offset":0.00306,"descend_place.place_z_offset":-0.00241,"grasp_1.grasp_duration":1.41716,"lift_1.lift_height":0.1837,"lift_1.lift_speed":0.03134,"release_1.release_duration":0.90192,"retract_1.retract_height":0.22492,"transport_to_goal.transport_speed":0.05611},"optimized_scores":{"best_composite_score":-0.03871,"best_fitness_score":0.59129,"best_task_score":0.22474},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":119.0,"contact_point_centroid":[0.56094,0.18086,-0.01056],"force_p95":1.79012,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24972,"mean_force":0.66926,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57906,0.17908,0.30845]},{"body_a":"world","body_b":"grasp_target","contact_count":94.0,"contact_point_centroid":[0.50009,-0.01481,-0.00149],"force_p95":0.49737,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.51624,"mean_force":0.22522,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48985,-0.01524,0.02971]},{"body_a":"world","body_b":"grasp_target","contact_count":1980.0,"contact_point_centroid":[0.56009,0.18122,-0.00225],"force_p95":0.18539,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.38537,"mean_force":0.12516,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.58215,0.18278,0.38565]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11933.0,"contact_point_centroid":[0.49284,0.00403,0.10945],"force_p95":0.07275,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26036,"mean_force":0.05041,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49311,-0.01514,0.1075]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12173.0,"contact_point_centroid":[0.49276,-0.0343,0.10844],"force_p95":0.07171,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24674,"mean_force":0.04979,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49305,-0.01514,0.10676]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50381,-0.01551,-0.00204],"force_p95":0.13474,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.16527,"mean_force":0.12601,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49203,-0.01527,0.03015]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4179.0,"contact_point_centroid":[0.57748,0.18638,0.35061],"force_p95":0.07256,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14409,"mean_force":0.04862,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.57738,0.16737,0.34891]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.50382,-0.01567,-0.00184],"force_p95":0.1373,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12324,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.49958,-0.00582,0.25146]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4109.0,"contact_point_centroid":[0.57755,0.14812,0.35042],"force_p95":0.07357,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1364,"mean_force":0.04948,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.57741,0.16745,0.34853]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1221.0,"contact_point_centroid":[0.58151,0.1609,0.2907],"force_p95":0.07508,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12868,"mean_force":0.04367,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.58117,0.18011,0.28868]},{"body_a":"world","body_b":"grasp_target","contact_count":2004.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.49827,-0.01384,0.11718]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1223.0,"contact_point_centroid":[0.58154,0.1993,0.29044],"force_p95":0.07373,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11957,"mean_force":0.044,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.58117,0.18011,0.28868]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4105.0,"contact_point_centroid":[0.49132,0.00395,0.03169],"force_p95":0.07675,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11725,"mean_force":0.05178,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49086,-0.01526,0.02893]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":21712.0,"contact_point_centroid":[0.5348,0.05237,0.29573],"force_p95":0.06845,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0937,"mean_force":0.04632,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.5348,0.07148,0.29449]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4899.0,"contact_point_centroid":[0.49139,-0.03434,0.03077],"force_p95":0.06877,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0901,"mean_force":0.04474,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49086,-0.01526,0.02893]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":19815.0,"contact_point_centroid":[0.53586,0.09248,0.29824],"force_p95":0.07144,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0888,"mean_force":0.05005,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.53559,0.07328,0.29673]}],"total_contact_groups":16},"final_pose_error":0.01987,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.55903,0.18131,0.02602],"final_tcp_position":[0.58646,0.18656,0.45319],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":2.24972,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":201.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":800.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.50017,-0.01239,0.19922],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.17327,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":501.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2004.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_success","tcp_end":[0.49901,-0.01535,0.03759],"tcp_start":[0.50017,-0.01239,0.19922],"tcp_to_object_dist_end":0.01254,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50369,-0.01514,0.02585],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31204,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.13197,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10804.0,"raw_peak_contact_force":0.16527,"subtask_id":"grasp_success","tcp_end":[0.49083,-0.01525,0.02889],"tcp_start":[0.49901,-0.01535,0.03759],"tcp_to_object_dist_end":0.01321,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":578.0,"n_steps_budget":1000.0,"object_pos_end":[0.51008,-0.0151,0.18293],"object_pos_start":[0.50369,-0.01514,0.02585],"object_to_goal_dist_end":0.22623,"object_to_goal_dist_start":0.31204,"object_z_max":0.18266,"peak_contact_force":0.07048,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":24200.0,"raw_peak_contact_force":0.51624,"subtask_id":"lift_clearance","tcp_end":[0.4993,-0.01509,0.19004],"tcp_start":[0.49083,-0.01525,0.02889],"tcp_to_object_dist_end":0.01291,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.58034,0.15595,0.38668],"object_pos_start":[0.51008,-0.0151,0.18293],"object_to_goal_dist_end":0.14225,"object_to_goal_dist_start":0.22623,"object_z_max":0.38646,"peak_contact_force":0.07129,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":41527.0,"raw_peak_contact_force":0.0937,"subtask_id":"transport_accuracy","tcp_end":[0.57268,0.15595,0.40088],"tcp_start":[0.4993,-0.01509,0.19004],"tcp_to_object_dist_end":0.01613,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":198.0,"n_steps_budget":1000.0,"object_pos_end":[0.57615,0.17948,0.27766],"object_pos_start":[0.58034,0.15595,0.38668],"object_to_goal_dist_end":0.03244,"object_to_goal_dist_start":0.14225,"object_z_max":0.38679,"peak_contact_force":0.07656,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8288.0,"raw_peak_contact_force":0.14409,"subtask_id":"place_accuracy","tcp_end":[0.58256,0.18032,0.29339],"tcp_start":[0.57268,0.15595,0.40088],"tcp_to_object_dist_end":0.01701,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.57209,0.17909,0.00786],"object_pos_start":[0.57615,0.17948,0.27766],"object_to_goal_dist_end":0.24086,"object_to_goal_dist_start":0.03244,"object_z_max":0.27766,"peak_contact_force":0.41014,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2563.0,"raw_peak_contact_force":2.24972,"subtask_id":"place_accuracy","tcp_end":[0.57905,0.17908,0.31315],"tcp_start":[0.58256,0.18032,0.29339],"tcp_to_object_dist_end":0.30537,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":522.0,"n_steps_budget":1000.0,"object_pos_end":[0.55903,0.18131,0.02602],"object_pos_start":[0.57209,0.17909,0.00786],"object_to_goal_dist_end":0.22392,"object_to_goal_dist_start":0.24086,"object_z_max":0.02953,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1980.0,"raw_peak_contact_force":0.38537,"tcp_end":[0.58646,0.18656,0.45319],"tcp_start":[0.57905,0.17908,0.31315],"tcp_to_object_dist_end":0.42808,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.24538,"average_solve_count":379.0,"average_success_count":379.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.05264,"descend_grasp.grasp_z_offset":0.00214,"descend_place.place_z_offset":-0.00088,"grasp_1.grasp_duration":0.79609,"lift_1.lift_height":0.16964,"lift_1.lift_speed":0.03409,"release_1.release_duration":0.51151,"retract_1.retract_height":0.26746,"transport_to_goal.transport_speed":0.03143},"optimized_scores":{"best_composite_score":0.07031,"best_fitness_score":0.70031,"best_task_score":0.4432},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":225.0,"contact_point_centroid":[0.60045,0.17143,-0.00657],"force_p95":1.08087,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.66448,"mean_force":0.32706,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61778,0.16845,0.20303]},{"body_a":"world","body_b":"grasp_target","contact_count":96.0,"contact_point_centroid":[0.50861,0.03737,-0.00161],"force_p95":0.53144,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55465,"mean_force":0.22289,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49823,0.03793,0.02854]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11044.0,"contact_point_centroid":[0.50139,0.05685,0.10004],"force_p95":0.07695,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27232,"mean_force":0.05153,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.50142,0.03774,0.09809]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10329.0,"contact_point_centroid":[0.50154,0.01857,0.10075],"force_p95":0.07991,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25853,"mean_force":0.05368,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.50143,0.03774,0.09818]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51257,0.03937,-0.00215],"force_p95":0.16773,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24945,"mean_force":0.13466,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50044,0.03813,0.02889]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4050.0,"contact_point_centroid":[0.49986,0.01884,0.03041],"force_p95":0.08194,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15182,"mean_force":0.05191,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49925,0.03804,0.02761]},{"body_a":"world","body_b":"grasp_target","contact_count":2896.0,"contact_point_centroid":[0.60046,0.17143,-0.00198],"force_p95":0.1252,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15174,"mean_force":0.12173,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.62073,0.16973,0.30155]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4793.0,"contact_point_centroid":[0.62165,0.18664,0.26541],"force_p95":0.07327,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14771,"mean_force":0.04926,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.62155,0.16761,0.26377]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4717.0,"contact_point_centroid":[0.62174,0.14832,0.26526],"force_p95":0.07395,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1445,"mean_force":0.04976,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.62156,0.16763,0.26321]},{"body_a":"world","body_b":"grasp_target","contact_count":884.0,"contact_point_centroid":[0.51251,0.03972,-0.00185],"force_p95":0.13709,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12318,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.50283,0.01504,0.25027]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1217.0,"contact_point_centroid":[0.62171,0.15053,0.19006],"force_p95":0.07691,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12663,"mean_force":0.04466,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.62139,0.16969,0.18794]},{"body_a":"world","body_b":"grasp_target","contact_count":1988.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.50599,0.0352,0.11583]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1190.0,"contact_point_centroid":[0.62231,0.18889,0.18956],"force_p95":0.07832,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11924,"mean_force":0.0455,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.62136,0.16968,0.18788]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":19102.0,"contact_point_centroid":[0.56394,0.08414,0.25341],"force_p95":0.06832,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0899,"mean_force":0.04573,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.56401,0.10329,0.25184]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5027.0,"contact_point_centroid":[0.49983,0.05723,0.02943],"force_p95":0.07455,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08669,"mean_force":0.04475,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49926,0.03804,0.02762]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18001.0,"contact_point_centroid":[0.56359,0.12198,0.2525],"force_p95":0.06942,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08513,"mean_force":0.04851,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.56355,0.10277,0.2512]}],"total_contact_groups":16},"final_pose_error":0.01982,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.60045,0.17143,0.02602],"final_tcp_position":[0.62646,0.17187,0.39271],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":1.66448,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":222.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":884.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.50715,0.03188,0.19738],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.17162,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":497.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1988.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_success","tcp_end":[0.5075,0.0387,0.0366],"tcp_start":[0.50715,0.03188,0.19738],"tcp_to_object_dist_end":0.01175,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51241,0.03808,0.02549],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.2136,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.15806,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10877.0,"raw_peak_contact_force":0.24945,"subtask_id":"grasp_success","tcp_end":[0.49922,0.03803,0.02758],"tcp_start":[0.5075,0.0387,0.0366],"tcp_to_object_dist_end":0.01335,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":538.0,"n_steps_budget":1000.0,"object_pos_end":[0.51896,0.03789,0.16957],"object_pos_start":[0.51241,0.03808,0.02549],"object_to_goal_dist_end":0.17471,"object_to_goal_dist_start":0.2136,"object_z_max":0.16931,"peak_contact_force":0.08233,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":21469.0,"raw_peak_contact_force":0.55465,"subtask_id":"lift_clearance","tcp_end":[0.50779,0.03778,0.17568],"tcp_start":[0.49922,0.03803,0.02758],"tcp_to_object_dist_end":0.01274,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":874.0,"n_steps_budget":1000.0,"object_pos_end":[0.62852,0.16532,0.31545],"object_pos_start":[0.51896,0.03789,0.16957],"object_to_goal_dist_end":0.17058,"object_to_goal_dist_start":0.17471,"object_z_max":0.31531,"peak_contact_force":0.06869,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":37103.0,"raw_peak_contact_force":0.0899,"subtask_id":"transport_accuracy","tcp_end":[0.62019,0.16537,0.32807],"tcp_start":[0.50779,0.03778,0.17568],"tcp_to_object_dist_end":0.01512,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":229.0,"n_steps_budget":1000.0,"object_pos_end":[0.61571,0.16937,0.17916],"object_pos_start":[0.62852,0.16532,0.31545],"object_to_goal_dist_end":0.03627,"object_to_goal_dist_start":0.17058,"object_z_max":0.31548,"peak_contact_force":0.07831,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":9510.0,"raw_peak_contact_force":0.14771,"subtask_id":"place_accuracy","tcp_end":[0.62355,0.17029,0.19347],"tcp_start":[0.62019,0.16537,0.32807],"tcp_to_object_dist_end":0.01634,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.60371,0.1701,0.0248],"object_pos_start":[0.61571,0.16937,0.17916],"object_to_goal_dist_end":0.1226,"object_to_goal_dist_start":0.03627,"object_z_max":0.17916,"peak_contact_force":0.09316,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2632.0,"raw_peak_contact_force":1.66448,"subtask_id":"place_accuracy","tcp_end":[0.61774,0.16843,0.21155],"tcp_start":[0.62355,0.17029,0.19347],"tcp_to_object_dist_end":0.18729,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":724.0,"n_steps_budget":1000.0,"object_pos_end":[0.60045,0.17143,0.02602],"object_pos_start":[0.60371,0.1701,0.0248],"object_to_goal_dist_end":0.12206,"object_to_goal_dist_start":0.1226,"object_z_max":0.02673,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2896.0,"raw_peak_contact_force":0.15174,"tcp_end":[0.62646,0.17187,0.39271],"tcp_start":[0.61774,0.16843,0.21155],"tcp_to_object_dist_end":0.36761,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.20146,"average_solve_count":412.0,"average_success_count":412.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.03747,"descend_grasp.grasp_z_offset":0.0005,"descend_place.place_z_offset":0.00205,"grasp_1.grasp_duration":1.42682,"lift_1.lift_height":0.233,"lift_1.lift_speed":0.03784,"release_1.release_duration":0.43804,"retract_1.retract_height":0.2215,"transport_to_goal.transport_speed":0.0425},"optimized_scores":{"best_composite_score":-0.02252,"best_fitness_score":0.60748,"best_task_score":0.25423},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":132.0,"contact_point_centroid":[0.56221,0.23005,-0.01049],"force_p95":1.4678,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.20893,"mean_force":0.59899,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.576,0.2246,0.29594]},{"body_a":"world","body_b":"grasp_target","contact_count":91.0,"contact_point_centroid":[0.47883,0.04615,-0.0016],"force_p95":0.58641,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.61269,"mean_force":0.23213,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46951,0.04666,0.02838]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":14739.0,"contact_point_centroid":[0.47291,0.06567,0.13455],"force_p95":0.07555,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28944,"mean_force":0.05132,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47284,0.04652,0.1327]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48277,0.04841,-0.00219],"force_p95":0.17486,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.26331,"mean_force":0.13672,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47163,0.04689,0.02841]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14593.0,"contact_point_centroid":[0.47284,0.02737,0.13457],"force_p95":0.07592,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24823,"mean_force":0.05099,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47284,0.04652,0.13259]},{"body_a":"world","body_b":"grasp_target","contact_count":1980.0,"contact_point_centroid":[0.56207,0.23011,-0.00212],"force_p95":0.13056,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21779,"mean_force":0.11829,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.57785,0.226,0.36586]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4309.0,"contact_point_centroid":[0.57869,0.24195,0.35229],"force_p95":0.07811,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15203,"mean_force":0.05375,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.57815,0.22296,0.35031]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4804.0,"contact_point_centroid":[0.57843,0.20368,0.35241],"force_p95":0.07242,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15136,"mean_force":0.04879,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.57815,0.22297,0.35011]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1327.0,"contact_point_centroid":[0.57911,0.20679,0.27968],"force_p95":0.07616,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14872,"mean_force":0.04231,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57818,0.22584,0.27694]},{"body_a":"world","body_b":"grasp_target","contact_count":904.0,"contact_point_centroid":[0.4827,0.04873,-0.00186],"force_p95":0.13709,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12317,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.49138,0.01842,0.25052]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1127.0,"contact_point_centroid":[0.57954,0.24514,0.27834],"force_p95":0.0816,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13515,"mean_force":0.0489,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57815,0.22582,0.27685]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4996.0,"contact_point_centroid":[0.47026,0.02754,0.03005],"force_p95":0.07137,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13201,"mean_force":0.04308,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4705,0.04678,0.02728]},{"body_a":"world","body_b":"grasp_target","contact_count":2044.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.47943,0.04332,0.11531]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20060.0,"contact_point_centroid":[0.52778,0.11633,0.32829],"force_p95":0.06844,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08964,"mean_force":0.04603,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52777,0.13545,0.32642]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18720.0,"contact_point_centroid":[0.52728,0.15355,0.32689],"force_p95":0.07033,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08344,"mean_force":0.04927,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52712,0.13434,0.32526]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5501.0,"contact_point_centroid":[0.47016,0.06615,0.02943],"force_p95":0.07209,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08314,"mean_force":0.04155,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47051,0.04678,0.02729]}],"total_contact_groups":16},"final_pose_error":0.01996,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.56207,0.2301,0.02602],"final_tcp_position":[0.5813,0.22812,0.43204],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":2.20893,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":227.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":904.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.48307,0.03932,0.19731],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.17155,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":511.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2044.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_success","tcp_end":[0.47836,0.04754,0.03529],"tcp_start":[0.48307,0.03932,0.19731],"tcp_to_object_dist_end":0.0103,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":47.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.4826,0.04697,0.02537],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29156,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.16629,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12297.0,"raw_peak_contact_force":0.26331,"subtask_id":"grasp_success","tcp_end":[0.47048,0.04677,0.02725],"tcp_start":[0.47836,0.04754,0.03529],"tcp_to_object_dist_end":0.01227,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":728.0,"n_steps_budget":1000.0,"object_pos_end":[0.48917,0.04674,0.23179],"object_pos_start":[0.4826,0.04697,0.02537],"object_to_goal_dist_end":0.20435,"object_to_goal_dist_start":0.29156,"object_z_max":0.23151,"peak_contact_force":0.07373,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":29423.0,"raw_peak_contact_force":0.61269,"subtask_id":"lift_clearance","tcp_end":[0.47897,0.04667,0.23876],"tcp_start":[0.47048,0.04677,0.02725],"tcp_to_object_dist_end":0.01235,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":930.0,"n_steps_budget":1000.0,"object_pos_end":[0.58398,0.21979,0.40075],"object_pos_start":[0.48917,0.04674,0.23179],"object_to_goal_dist_end":0.17051,"object_to_goal_dist_start":0.20435,"object_z_max":0.40059,"peak_contact_force":0.0676,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":38780.0,"raw_peak_contact_force":0.08964,"subtask_id":"transport_accuracy","tcp_end":[0.57664,0.21984,0.41348],"tcp_start":[0.47897,0.04667,0.23876],"tcp_to_object_dist_end":0.0147,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":228.0,"n_steps_budget":1000.0,"object_pos_end":[0.56906,0.22525,0.26657],"object_pos_start":[0.58398,0.21979,0.40075],"object_to_goal_dist_end":0.03846,"object_to_goal_dist_start":0.17051,"object_z_max":0.40075,"peak_contact_force":0.08231,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":9113.0,"raw_peak_contact_force":0.15203,"subtask_id":"place_accuracy","tcp_end":[0.57953,0.2264,0.28173],"tcp_start":[0.57664,0.21984,0.41348],"tcp_to_object_dist_end":0.01846,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.56453,0.225,0.01242],"object_pos_start":[0.56906,0.22525,0.26657],"object_to_goal_dist_end":0.21878,"object_to_goal_dist_start":0.03846,"object_z_max":0.26657,"peak_contact_force":0.23314,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2586.0,"raw_peak_contact_force":2.20893,"subtask_id":"place_accuracy","tcp_end":[0.57599,0.2246,0.30111],"tcp_start":[0.57953,0.2264,0.28173],"tcp_to_object_dist_end":0.28891,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":495.0,"n_steps_budget":960.0,"object_pos_end":[0.56207,0.2301,0.02602],"object_pos_start":[0.56453,0.225,0.01242],"object_to_goal_dist_end":0.20543,"object_to_goal_dist_start":0.21878,"object_z_max":0.0269,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1980.0,"raw_peak_contact_force":0.21779,"tcp_end":[0.5813,0.22812,0.43204],"tcp_start":[0.57599,0.2246,0.30111],"tcp_to_object_dist_end":0.40648,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```