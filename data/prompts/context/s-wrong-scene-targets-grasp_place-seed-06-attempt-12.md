## Search State

- **Seed**: 6
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | impedance_control | impedance_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 9 | 0.0033 | 0.31 | ❌ rejected |
| 11 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | impedance_control | impedance_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 9 | 0.0036 | 0.31 | ❌ rejected |
| 10 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | impedance_control | impedance_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 9 | 0.0038 | 0.31 | ✅ accepted |
| 9 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | force_threshold_switch | position_control | impedance_control | position_control | impedance_control | position_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 10 | -0.3346 | 0.17 | ❌ rejected |
| 8 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | impedance_control | position_control | impedance_control | position_control | impedance_control | position_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 11 | -0.3128 | 0.17 | ❌ rejected |

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
- **task_score** (E): 0.308
- **fitness_score**: 0.633  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.630

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1078 |
| descend_grasp | 1.00 | 1.00 | 0.1621 |
| grasp_1 | 1.00 | 1.00 | 0.0118 |
| lift_1 | 1.00 | 1.00 | 0.1829 |
| transport_to_goal | 1.00 | 1.00 | 0.2615 |
| descend_place | 1.00 | 1.00 | 0.1397 |
| release_1 | 1.00 | 1.00 | 0.0202 |
| retract_1 | 1.00 | 1.00 | 0.1327 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.497, 0.020, 0.198) | (0.500, 0.024, 0.030)→(0.500, 0.024, 0.026) | 0.269→0.271 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_grasp | descend | 1.00 / step_budget | (0.497, 0.020, 0.198)→(0.495, 0.024, 0.036) | (0.500, 0.024, 0.026)→(0.500, 0.024, 0.026) | 0.271→0.271 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.495, 0.024, 0.036)→(0.487, 0.023, 0.027) | (0.500, 0.024, 0.026)→(0.500, 0.023, 0.026) | 0.271→0.272 | 1.00 / 43.000 | 0.152 | 0.226 |
| lift_1 | lift | 1.00 / step_budget | (0.487, 0.023, 0.027)→(0.495, 0.023, 0.210) | (0.500, 0.023, 0.026)→(0.506, 0.023, 0.203) | 0.272→0.199 | 1.00 / 40.333 | 0.075 | 0.570 |
| transport_to_goal | approach | 1.00 / step_budget | (0.495, 0.023, 0.210)→(0.592, 0.186, 0.388) | (0.506, 0.023, 0.203)→(0.600, 0.186, 0.375) | 0.199→0.168 | 1.00 / 40.333 | 0.079 | 0.095 |
| descend_place | descend | 1.00 / step_budget | (0.592, 0.186, 0.388)→(0.596, 0.194, 0.249) | (0.600, 0.186, 0.375)→(0.584, 0.193, 0.233) | 0.168→0.029 | 1.00 / 39.667 | 0.081 | 0.156 |
| release_1 | release | 1.00 / step_budget | (0.596, 0.194, 0.249)→(0.591, 0.192, 0.268) | (0.584, 0.193, 0.233)→(0.579, 0.193, 0.017) | 0.029→0.192 | 1.00 / 4.000 | 0.211 | 2.060 |
| retract_1 | retract | 1.00 / step_budget | (0.591, 0.192, 0.268)→(0.598, 0.196, 0.401) | (0.579, 0.193, 0.017)→(0.575, 0.196, 0.026) | 0.192→0.184 | 1.00 / 4.000 | 0.123 | 0.223 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.444
- phase_score: 0.570
- phase_breakdown.lift_clearance_score: 0.185
- phase_breakdown.reach_object_score: 0.676
- phase_breakdown.transport_accuracy_score: 0.503
- phase_breakdown.grasp_success_score: 1.000
- phase_breakdown.place_accuracy_score: 0.488
- grasp_place_fitness: 0.700

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.700
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.444
- **Median Q (composite search score)**: -0.023
- **K-run variance**: 0.0023
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.344


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.19324,"average_solve_count":414.0,"average_success_count":414.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.03179,"descend_grasp.grasp_z_offset":0.00108,"descend_place.place_z_offset":0.0054,"grasp_1.grasp_duration":1.83948,"lift_1.lift_height":0.24994,"lift_1.lift_speed":0.02393,"release_1.release_duration":0.96423,"retract_1.retract_height":0.2002,"transport_to_goal.transport_speed":0.04716},"optimized_scores":{"best_composite_score":-0.03789,"best_fitness_score":0.59211,"best_task_score":0.22553},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":123.0,"contact_point_centroid":[0.56318,0.18753,-0.01081],"force_p95":1.49288,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.28215,"mean_force":0.64723,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.58112,0.18408,0.30803]},{"body_a":"world","body_b":"grasp_target","contact_count":86.0,"contact_point_centroid":[0.49982,-0.01476,-0.00144],"force_p95":0.5701,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.59242,"mean_force":0.23168,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48985,-0.01525,0.02796]},{"body_a":"world","body_b":"grasp_target","contact_count":1721.0,"contact_point_centroid":[0.56302,0.18766,-0.00218],"force_p95":0.13495,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.32385,"mean_force":0.11863,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.58291,0.18518,0.37059]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16520.0,"contact_point_centroid":[0.49337,0.00402,0.14374],"force_p95":0.0724,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28724,"mean_force":0.05055,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49353,-0.01514,0.14187]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16808.0,"contact_point_centroid":[0.49324,-0.0343,0.14206],"force_p95":0.07212,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26872,"mean_force":0.04993,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49345,-0.01514,0.14039]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6846.0,"contact_point_centroid":[0.58425,0.20053,0.36283],"force_p95":0.07832,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16867,"mean_force":0.05329,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.58356,0.18146,0.36052]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50381,-0.0155,-0.00204],"force_p95":0.13454,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.16649,"mean_force":0.12598,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49199,-0.01528,0.02822]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7677.0,"contact_point_centroid":[0.58392,0.16218,0.36428],"force_p95":0.07142,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15541,"mean_force":0.04801,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.58354,0.18135,0.3622]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1273.0,"contact_point_centroid":[0.58366,0.16595,0.29071],"force_p95":0.07701,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14677,"mean_force":0.04385,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.58324,0.18508,0.2887]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1186.0,"contact_point_centroid":[0.58371,0.20432,0.29006],"force_p95":0.07825,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14122,"mean_force":0.04656,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.58321,0.18507,0.28859]},{"body_a":"world","body_b":"grasp_target","contact_count":832.0,"contact_point_centroid":[0.50382,-0.01567,-0.00184],"force_p95":0.13728,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12321,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.49944,-0.00575,0.25195]},{"body_a":"world","body_b":"grasp_target","contact_count":2028.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.49824,-0.01386,0.11617]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4103.0,"contact_point_centroid":[0.4913,0.00394,0.02976],"force_p95":0.07662,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11511,"mean_force":0.05178,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49082,-0.01526,0.02699]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18373.0,"contact_point_centroid":[0.54104,0.10167,0.34415],"force_p95":0.07532,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09903,"mean_force":0.05071,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.54058,0.08246,0.34256]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4899.0,"contact_point_centroid":[0.49136,-0.03435,0.02883],"force_p95":0.0687,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09052,"mean_force":0.04475,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49082,-0.01526,0.02699]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20308.0,"contact_point_centroid":[0.54046,0.0628,0.34327],"force_p95":0.06882,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08964,"mean_force":0.04638,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.54034,0.0819,0.34204]}],"total_contact_groups":16},"final_pose_error":0.01978,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.56286,0.18781,0.02602],"final_tcp_position":[0.58612,0.18678,0.42856],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":2.28215,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":209.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":832.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.50013,-0.01241,0.19902],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.17307,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":507.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2028.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_success","tcp_end":[0.49899,-0.01535,0.03565],"tcp_start":[0.50013,-0.01241,0.19902],"tcp_to_object_dist_end":0.01078,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50368,-0.01513,0.02586],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31204,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.13172,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10802.0,"raw_peak_contact_force":0.16649,"subtask_id":"grasp_success","tcp_end":[0.49079,-0.01526,0.02696],"tcp_start":[0.49899,-0.01535,0.03565],"tcp_to_object_dist_end":0.01294,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":808.0,"n_steps_budget":1000.0,"object_pos_end":[0.51103,-0.01506,0.24864],"object_pos_start":[0.50368,-0.01513,0.02586],"object_to_goal_dist_end":0.21626,"object_to_goal_dist_start":0.31204,"object_z_max":0.24838,"peak_contact_force":0.06999,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":33414.0,"raw_peak_contact_force":0.59242,"subtask_id":"lift_clearance","tcp_end":[0.50019,-0.0151,0.25624],"tcp_start":[0.49079,-0.01526,0.02696],"tcp_to_object_dist_end":0.01323,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":943.0,"n_steps_budget":1000.0,"object_pos_end":[0.59006,0.17788,0.41736],"object_pos_start":[0.51103,-0.01506,0.24864],"object_to_goal_dist_end":0.16955,"object_to_goal_dist_start":0.21626,"object_z_max":0.41721,"peak_contact_force":0.08784,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":38681.0,"raw_peak_contact_force":0.09903,"subtask_id":"transport_accuracy","tcp_end":[0.58263,0.17759,0.43126],"tcp_start":[0.50019,-0.0151,0.25624],"tcp_to_object_dist_end":0.01576,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":39.0,"n_steps":360.0,"n_steps_budget":1000.0,"object_pos_end":[0.57182,0.1847,0.27618],"object_pos_start":[0.59006,0.17788,0.41736],"object_to_goal_dist_end":0.03199,"object_to_goal_dist_start":0.16955,"object_z_max":0.41737,"peak_contact_force":0.08172,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":14523.0,"raw_peak_contact_force":0.16867,"subtask_id":"place_accuracy","tcp_end":[0.5845,0.1855,0.29277],"tcp_start":[0.58263,0.17759,0.43126],"tcp_to_object_dist_end":0.02089,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.56983,0.18381,0.00976],"object_pos_start":[0.57182,0.1847,0.27618],"object_to_goal_dist_end":0.239,"object_to_goal_dist_start":0.03199,"object_z_max":0.27618,"peak_contact_force":0.34368,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2582.0,"raw_peak_contact_force":2.28215,"subtask_id":"place_accuracy","tcp_end":[0.5811,0.18408,0.31287],"tcp_start":[0.5845,0.1855,0.29277],"tcp_to_object_dist_end":0.30332,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":434.0,"n_steps_budget":870.0,"object_pos_end":[0.56286,0.18781,0.02602],"object_pos_start":[0.56983,0.18381,0.00976],"object_to_goal_dist_end":0.2234,"object_to_goal_dist_start":0.239,"object_z_max":0.02692,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1721.0,"raw_peak_contact_force":0.32385,"tcp_end":[0.58612,0.18678,0.42856],"tcp_start":[0.5811,0.18408,0.31287],"tcp_to_object_dist_end":0.40322,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.0705,"average_solve_count":383.0,"average_success_count":383.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.0604,"descend_grasp.grasp_z_offset":0.00263,"descend_place.place_z_offset":0.00685,"grasp_1.grasp_duration":1.01185,"lift_1.lift_height":0.16409,"lift_1.lift_speed":0.0279,"release_1.release_duration":0.82631,"retract_1.retract_height":0.23131,"transport_to_goal.transport_speed":0.04188},"optimized_scores":{"best_composite_score":0.07044,"best_fitness_score":0.70044,"best_task_score":0.44367},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":229.0,"contact_point_centroid":[0.60118,0.17219,-0.0066],"force_p95":1.02808,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.7229,"mean_force":0.31812,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61781,0.16881,0.20072]},{"body_a":"world","body_b":"grasp_target","contact_count":108.0,"contact_point_centroid":[0.50891,0.03753,-0.0016],"force_p95":0.47121,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.51541,"mean_force":0.20632,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49817,0.03793,0.02901]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10935.0,"contact_point_centroid":[0.50135,0.05686,0.09747],"force_p95":0.07698,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25514,"mean_force":0.05148,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.50138,0.03775,0.09552]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51257,0.03938,-0.00215],"force_p95":0.16759,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24849,"mean_force":0.1346,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50045,0.03814,0.02937]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10231.0,"contact_point_centroid":[0.50149,0.01858,0.09821],"force_p95":0.08,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24258,"mean_force":0.05361,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.50139,0.03775,0.09564]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4051.0,"contact_point_centroid":[0.49987,0.01884,0.0309],"force_p95":0.08188,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15251,"mean_force":0.05192,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49927,0.03804,0.0281]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1328.0,"contact_point_centroid":[0.62252,0.15103,0.18879],"force_p95":0.0738,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14975,"mean_force":0.04138,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.62152,0.17007,0.18607]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7172.0,"contact_point_centroid":[0.62147,0.18673,0.26343],"force_p95":0.0726,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14894,"mean_force":0.04925,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.62118,0.16764,0.26175]},{"body_a":"world","body_b":"grasp_target","contact_count":2368.0,"contact_point_centroid":[0.60117,0.17213,-0.00198],"force_p95":0.1248,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.14634,"mean_force":0.12164,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.62048,0.16985,0.2824]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7282.0,"contact_point_centroid":[0.6215,0.14846,0.26236],"force_p95":0.07122,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14545,"mean_force":0.04856,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.62123,0.16771,0.26022]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1125.0,"contact_point_centroid":[0.62303,0.18938,0.18758],"force_p95":0.07946,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13888,"mean_force":0.04839,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.62147,0.17005,0.18597]},{"body_a":"world","body_b":"grasp_target","contact_count":884.0,"contact_point_centroid":[0.51251,0.03972,-0.00185],"force_p95":0.13709,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12318,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.50289,0.01513,0.25002]},{"body_a":"world","body_b":"grasp_target","contact_count":1976.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.50605,0.03524,0.11591]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":19468.0,"contact_point_centroid":[0.56398,0.08429,0.2508],"force_p95":0.06821,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08964,"mean_force":0.04568,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.56406,0.10344,0.2492]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18352.0,"contact_point_centroid":[0.56357,0.12207,0.2498],"force_p95":0.06936,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08636,"mean_force":0.04846,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.56354,0.10286,0.24847]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5026.0,"contact_point_centroid":[0.49984,0.05723,0.02991],"force_p95":0.07454,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08612,"mean_force":0.04474,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49928,0.03804,0.0281]}],"total_contact_groups":16},"final_pose_error":0.01999,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.60116,0.17213,0.02602],"final_tcp_position":[0.62574,0.1717,0.35645],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":1.7229,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":222.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":884.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.50725,0.03195,0.1972],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.17144,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":494.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1976.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_success","tcp_end":[0.50751,0.0387,0.03709],"tcp_start":[0.50725,0.03195,0.1972],"tcp_to_object_dist_end":0.01219,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51241,0.03809,0.02549],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21359,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.158,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10877.0,"raw_peak_contact_force":0.24849,"subtask_id":"grasp_success","tcp_end":[0.49924,0.03804,0.02806],"tcp_start":[0.50751,0.0387,0.03709],"tcp_to_object_dist_end":0.01342,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":533.0,"n_steps_budget":1000.0,"object_pos_end":[0.51876,0.0379,0.16362],"object_pos_start":[0.51241,0.03809,0.02549],"object_to_goal_dist_end":0.17409,"object_to_goal_dist_start":0.21359,"object_z_max":0.16337,"peak_contact_force":0.0796,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":21274.0,"raw_peak_contact_force":0.51541,"subtask_id":"lift_clearance","tcp_end":[0.50769,0.03779,0.17016],"tcp_start":[0.49924,0.03804,0.02806],"tcp_to_object_dist_end":0.01286,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":891.0,"n_steps_budget":1000.0,"object_pos_end":[0.62827,0.16537,0.31486],"object_pos_start":[0.51876,0.0379,0.16362],"object_to_goal_dist_end":0.16998,"object_to_goal_dist_start":0.17409,"object_z_max":0.31471,"peak_contact_force":0.06804,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":37820.0,"raw_peak_contact_force":0.08964,"subtask_id":"transport_accuracy","tcp_end":[0.62023,0.16543,0.32787],"tcp_start":[0.50769,0.03779,0.17016],"tcp_to_object_dist_end":0.0153,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":350.0,"n_steps_budget":1000.0,"object_pos_end":[0.61367,0.16995,0.17548],"object_pos_start":[0.62827,0.16537,0.31486],"object_to_goal_dist_end":0.03358,"object_to_goal_dist_start":0.16998,"object_z_max":0.31489,"peak_contact_force":0.08,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":14454.0,"raw_peak_contact_force":0.14894,"subtask_id":"place_accuracy","tcp_end":[0.62342,0.17061,0.19053],"tcp_start":[0.62023,0.16543,0.32787],"tcp_to_object_dist_end":0.01794,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.60298,0.17077,0.02512],"object_pos_start":[0.61367,0.16995,0.17548],"object_to_goal_dist_end":0.12241,"object_to_goal_dist_start":0.03358,"object_z_max":0.17548,"peak_contact_force":0.07881,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2682.0,"raw_peak_contact_force":1.7229,"subtask_id":"place_accuracy","tcp_end":[0.61777,0.16879,0.20938],"tcp_start":[0.62342,0.17061,0.19053],"tcp_to_object_dist_end":0.18486,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":592.0,"n_steps_budget":1000.0,"object_pos_end":[0.60116,0.17213,0.02602],"object_pos_start":[0.60298,0.17077,0.02512],"object_to_goal_dist_end":0.1219,"object_to_goal_dist_start":0.12241,"object_z_max":0.02667,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2368.0,"raw_peak_contact_force":0.14634,"tcp_end":[0.62574,0.1717,0.35645],"tcp_start":[0.61777,0.16879,0.20938],"tcp_to_object_dist_end":0.33134,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.32967,"average_solve_count":364.0,"average_success_count":364.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.07358,"descend_grasp.grasp_z_offset":2e-05,"descend_place.place_z_offset":-0.00619,"grasp_1.grasp_duration":0.91586,"lift_1.lift_height":0.1975,"lift_1.lift_speed":0.03657,"release_1.release_duration":0.73666,"retract_1.retract_height":0.20743,"transport_to_goal.transport_speed":0.04521},"optimized_scores":{"best_composite_score":-0.02265,"best_fitness_score":0.60735,"best_task_score":0.2538},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":151.0,"contact_point_centroid":[0.55944,0.22896,-0.0097],"force_p95":1.36926,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.1756,"mean_force":0.51781,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57484,0.2243,0.2772]},{"body_a":"world","body_b":"grasp_target","contact_count":92.0,"contact_point_centroid":[0.47862,0.04637,-0.00161],"force_p95":0.57465,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.60245,"mean_force":0.24062,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4695,0.04667,0.0278]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12403.0,"contact_point_centroid":[0.47279,0.06565,0.11678],"force_p95":0.07738,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27999,"mean_force":0.05142,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47271,0.04651,0.1149]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48277,0.0484,-0.00218],"force_p95":0.17463,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.26436,"mean_force":0.13669,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47162,0.0469,0.0279]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12126.0,"contact_point_centroid":[0.47262,0.02735,0.11549],"force_p95":0.07628,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24115,"mean_force":0.05164,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47261,0.04651,0.1135]},{"body_a":"world","body_b":"grasp_target","contact_count":2044.0,"contact_point_centroid":[0.55953,0.22892,-0.00205],"force_p95":0.12873,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19995,"mean_force":0.11887,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.57703,0.22577,0.34974]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1328.0,"contact_point_centroid":[0.57816,0.20659,0.26175],"force_p95":0.07625,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15331,"mean_force":0.04181,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57731,0.22562,0.25904]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7902.0,"contact_point_centroid":[0.57622,0.20083,0.33751],"force_p95":0.0712,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15135,"mean_force":0.04786,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.5759,0.22006,0.33527]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7283.0,"contact_point_centroid":[0.57638,0.23909,0.33749],"force_p95":0.07656,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15059,"mean_force":0.05133,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.57588,0.22003,0.33564]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1146.0,"contact_point_centroid":[0.57853,0.24493,0.26043],"force_p95":0.0817,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13903,"mean_force":0.04778,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57727,0.2256,0.25892]},{"body_a":"world","body_b":"grasp_target","contact_count":864.0,"contact_point_centroid":[0.4827,0.04873,-0.00185],"force_p95":0.13725,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12319,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.49141,0.01863,0.25006]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4994.0,"contact_point_centroid":[0.47026,0.02755,0.02956],"force_p95":0.0713,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12953,"mean_force":0.04308,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47049,0.04678,0.02677]},{"body_a":"world","body_b":"grasp_target","contact_count":2052.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.47941,0.04335,0.11485]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":21705.0,"contact_point_centroid":[0.52524,0.11267,0.30541],"force_p95":0.06888,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09695,"mean_force":0.04615,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52525,0.13182,0.30399]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20741.0,"contact_point_centroid":[0.52529,0.15096,0.30497],"force_p95":0.06928,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08949,"mean_force":0.04844,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52521,0.13175,0.30392]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5506.0,"contact_point_centroid":[0.47014,0.06615,0.02893],"force_p95":0.07204,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08405,"mean_force":0.04153,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4705,0.04679,0.02678]}],"total_contact_groups":16},"final_pose_error":0.01998,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.55953,0.22892,0.02602],"final_tcp_position":[0.581,0.22803,0.41798],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":2.1756,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":217.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":864.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.48306,0.03936,0.19719],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.17143,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":513.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2052.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_success","tcp_end":[0.47836,0.04755,0.03478],"tcp_start":[0.48306,0.03936,0.19719],"tcp_to_object_dist_end":0.00985,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":47.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.4826,0.04696,0.02537],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29157,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.16604,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12300.0,"raw_peak_contact_force":0.26436,"subtask_id":"grasp_success","tcp_end":[0.47047,0.04678,0.02674],"tcp_start":[0.47836,0.04755,0.03478],"tcp_to_object_dist_end":0.01221,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":611.0,"n_steps_budget":1000.0,"object_pos_end":[0.48899,0.04668,0.19807],"object_pos_start":[0.4826,0.04696,0.02537],"object_to_goal_dist_end":0.20703,"object_to_goal_dist_start":0.29157,"object_z_max":0.1978,"peak_contact_force":0.07463,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":24621.0,"raw_peak_contact_force":0.60245,"subtask_id":"lift_clearance","tcp_end":[0.47854,0.04663,0.20347],"tcp_start":[0.47047,0.04678,0.02674],"tcp_to_object_dist_end":0.01176,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.58213,0.21472,0.39285],"object_pos_start":[0.48899,0.04668,0.19807],"object_to_goal_dist_end":0.16298,"object_to_goal_dist_start":0.20703,"object_z_max":0.39264,"peak_contact_force":0.08073,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":42446.0,"raw_peak_contact_force":0.09695,"subtask_id":"transport_accuracy","tcp_end":[0.5736,0.21476,0.40559],"tcp_start":[0.47854,0.04663,0.20347],"tcp_to_object_dist_end":0.01532,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":374.0,"n_steps_budget":1000.0,"object_pos_end":[0.56767,0.22523,0.24771],"object_pos_start":[0.58213,0.21472,0.39285],"object_to_goal_dist_end":0.02261,"object_to_goal_dist_start":0.16298,"object_z_max":0.39292,"peak_contact_force":0.08256,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":15185.0,"raw_peak_contact_force":0.15135,"subtask_id":"place_accuracy","tcp_end":[0.5787,0.22617,0.26316],"tcp_start":[0.5736,0.21476,0.40559],"tcp_to_object_dist_end":0.01901,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.56347,0.22367,0.01587],"object_pos_start":[0.56767,0.22523,0.24771],"object_to_goal_dist_end":0.21547,"object_to_goal_dist_start":0.02261,"object_z_max":0.24771,"peak_contact_force":0.21098,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2625.0,"raw_peak_contact_force":2.1756,"subtask_id":"place_accuracy","tcp_end":[0.57482,0.22429,0.28307],"tcp_start":[0.5787,0.22617,0.26316],"tcp_to_object_dist_end":0.26744,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":511.0,"n_steps_budget":990.0,"object_pos_end":[0.55953,0.22892,0.02602],"object_pos_start":[0.56347,0.22367,0.01587],"object_to_goal_dist_end":0.20568,"object_to_goal_dist_start":0.21547,"object_z_max":0.02694,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2044.0,"raw_peak_contact_force":0.19995,"tcp_end":[0.581,0.22803,0.41798],"tcp_start":[0.57482,0.22429,0.28307],"tcp_to_object_dist_end":0.39255,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```