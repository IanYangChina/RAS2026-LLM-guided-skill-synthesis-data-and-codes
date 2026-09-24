## Search State

- **Seed**: 3
- **Iteration**: 10 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 9 | approach → descend → contact → grasp → lift → approach → descend → release | arc_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 9 | -0.3300 | 0.20 | ❌ rejected |
| 8 | approach → descend → contact → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 9 | -0.3745 | 0.16 | ❌ rejected |
| 7 | approach → descend → contact → grasp → lift → approach → descend → release | arc_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 9 | -0.3241 | 0.22 | ✅ accepted |
| 6 | approach → contact → grasp → lift → retract → approach → descend → release | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 9 | -0.3276 | 0.18 | ❌ rejected |
| 5 | approach → descend → contact → grasp → lift → approach → descend → release | arc_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 9 | -0.0332 | 0.21 | ❌ rejected |

**Proposal policy**: task_score is 0.20 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `5ce27bcdb8582e1d517b17df0f9c2ad7b05701113a75707627744a889253e6a7`
- Frozen object start: [0.45856491671436245, -0.02631894934039003, 0.03]
- Frozen task target: [0.6301274465206397, 0.20821620360643678, 0.11411929633605987]
- Goal object position: (0.6301274465206397, 0.20821620360643678, 0.11411929633605987)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.6301274465206397, 0.20821620360643678, 0.11411929633605987)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.45856491671436245, -0.02631894934039003, 0.03)
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
  frozen_object_start: [0.4586, -0.0263, 0.03]
  frozen_task_target: [0.6301, 0.2082, 0.1141]
  frozen_object_starts: {'grasp_target': [0.45856491671436245, -0.02631894934039003, 0.03]}
  frozen_targets: {'place_target': [0.6301274465206397, 0.20821620360643678, 0.11411929633605987]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: 5ce27bcdb8582e1d517b17df0f9c2ad7b05701113a75707627744a889253e6a7

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
| `object` | offset from object initial position (0.45856491671436245, -0.02631894934039003, 0.03) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.6301274465206397, 0.20821620360643678, 0.11411929633605987) | final destination targets |
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

## Current Skill (Q=-0.330) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: reach_pregrasp
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.1
  weight: 0.2
- id: grasp_contact
  anchor: object
  metric: contact
  weight: 0.3
- id: lift_clear
  anchor: object
  target_entity: object
  offset:
  - 0.0
  - 0.0
  - 0.15
  weight: 0.3
- id: place_goal
  target_entity: object
  weight: 0.2
phases:
- id: approach_object
  type: approach
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.1
    tolerance: 0.02
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: world_z
      tolerance: 0.1
  parameters:
    approach_z:
      type: scalar
      range:
      - 0.08
      - 0.15
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: replace
    arc_height:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.12
      binds_to:
      - path: generator.arc_height
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat
  subtask_id: reach_pregrasp
- id: hover_above_object
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
    - 0.05
    tolerance: 0.02
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: world_z
      tolerance: 0.1
  parameters:
    hover_z:
      type: scalar
      range:
      - 0.03
      - 0.07
      default: 0.05
      binds_to:
      - path: target.offset.z
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat
  subtask_id: reach_pregrasp
- id: touch_object_top
  type: contact
  generator: linear_cartesian
  control: force_threshold_switch
  termination: force_exceeded
  target:
    source: yaml
    anchor: task_object
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.03
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: world_z
      tolerance: 0.1
  parameters:
    contact_force:
      type: scalar
      range:
      - 5.0
      - 15.0
      default: 8.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
  guards:
  - id: check_contact
    when: during_phase
    predicate: contact_detected
    threshold: 0.5
    on_failure: continue
  retries:
    max_attempts: 0
    strategy: repeat
  subtask_id: grasp_contact
- id: grasp_object
  type: grasp
  control: position_control
  termination: grasp_success
  end_effector_action: force_grasp
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
  guards:
  - id: check_grasp
    when: after_phase
    predicate: bilateral_grasp
    threshold: 0.5
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: repeat
  subtask_id: grasp_contact
- id: lift_object
  type: lift
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
    tolerance: 0.01
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: world_z
      tolerance: 0.1
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.08
      - 0.2
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat
  subtask_id: lift_clear
- id: approach_goal
  type: approach
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.12
    tolerance: 0.02
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: world_z
      tolerance: 0.1
  parameters:
    approach_goal_z:
      type: scalar
      range:
      - 0.08
      - 0.18
      default: 0.12
      binds_to:
      - path: target.offset.z
        mode: replace
    goal_arc_height:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.12
      binds_to:
      - path: generator.arc_height
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat
  subtask_id: place_goal
- id: descend_at_goal
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.02
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: world_z
      tolerance: 0.1
  parameters:
    descend_goal_tolerance:
      type: scalar
      range:
      - 0.005
      - 0.03
      default: 0.02
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat
  subtask_id: place_goal
- id: release_object
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
      - 0.5
      - 2.0
      default: 1.0
      binds_to:
      - path: duration.max_time
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_object** (`approach`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.1], tolerance=0.02
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=world_z, tolerance=0.1
  - parameter_bindings:
    - approach_z: status=consumed; consumers=target.offset.z (replace)
    - arc_height: status=consumed; consumers=generator.arc_height (replace)
  - retries: max_attempts=0, strategy=repeat
- **hover_above_object** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.05], tolerance=0.02
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=world_z, tolerance=0.1
  - parameter_bindings:
    - hover_z: status=consumed; consumers=target.offset.z (replace)
  - retries: max_attempts=0, strategy=repeat
- **touch_object_top** (`contact`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.03]
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=world_z, tolerance=0.1
  - parameter_bindings:
    - contact_force: status=consumed; consumers=termination.force_threshold (replace)
  - guards:
    - id=check_contact, when=during_phase, predicate=contact_detected, on_failure=continue, threshold=0.5
  - retries: max_attempts=0, strategy=repeat
- **grasp_object** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
  - guards:
    - id=check_grasp, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=0.5
  - retries: max_attempts=2, strategy=repeat
- **lift_object** (`lift`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.15], tolerance=0.01
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=world_z, tolerance=0.1
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
  - retries: max_attempts=0, strategy=repeat
- **approach_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, entity=grasp_target, offset=[0.0, 0.0, 0.12], tolerance=0.02
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=world_z, tolerance=0.1
  - parameter_bindings:
    - approach_goal_z: status=consumed; consumers=target.offset.z (replace)
    - goal_arc_height: status=consumed; consumers=generator.arc_height (replace)
  - retries: max_attempts=0, strategy=repeat
- **descend_at_goal** (`descend`)
  - target: source=yaml, anchor=task_goal, entity=grasp_target, offset=[0.0, 0.0, 0.0], tolerance=0.02
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=world_z, tolerance=0.1
  - parameter_bindings:
    - descend_goal_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
  - retries: max_attempts=0, strategy=repeat
- **release_object** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings:
    - release_duration: status=consumed; consumers=duration.max_time (replace)
  - retries: max_attempts=0, strategy=repeat

## Design Metrics

- **Composite score**: -0.330
- **task_score** (E): 0.198
- **fitness_score**: 0.175  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.125
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.630

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 0.00 | 1.00 | 0.1365 |
| hover_above_object | 0.00 | 1.00 | 0.0688 |
| touch_object_top | 1.00 | 1.00 | 0.0002 |
| grasp_object | 1.00 | 1.00 | 0.0000 |
| lift_object | 0.00 | 1.00 | 0.1116 |
| approach_goal | 0.67 | 1.00 | 0.1686 |
| descend_at_goal | 0.00 | 1.00 | 0.0948 |
| release_object | 1.00 | 1.00 | 0.0268 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 0.00 / step_budget | (0.500, -0.000, 0.301)→(0.434, 0.028, 0.187) | (0.511, 0.002, 0.030)→(0.476, 0.004, 0.016) | 0.244→0.267 | 1.00 / 5.000 | 300.840 | 1417.541 |
| hover_above_object | descend | 0.00 / step_budget | (0.434, 0.028, 0.187)→(0.462, 0.045, 0.184) | (0.476, 0.004, 0.016)→(0.476, 0.004, 0.016) | 0.267→0.267 | 1.00 / 4.667 | 45073.698 | 894.508 |
| touch_object_top | contact | 1.00 / force_exceeded | (0.462, 0.045, 0.184)→(0.462, 0.046, 0.184) | (0.476, 0.004, 0.016)→(0.476, 0.004, 0.016) | 0.267→0.267 | 1.00 / 5.000 | 91373.489 | 160.268 |
| grasp_object | grasp | 1.00 / step_budget | (0.462, 0.046, 0.183)→(0.462, 0.046, 0.183) | (0.476, 0.004, 0.016)→(0.476, 0.004, 0.016) | 0.267→0.267 | 1.00 / 9.000 | 75.381 | 498.537 |
| lift_object | lift | 0.00 / step_budget | (0.462, 0.046, 0.183)→(0.488, -0.005, 0.256) | (0.476, 0.004, 0.016)→(0.475, 0.005, 0.016) | 0.267→0.267 | 1.00 / 10.000 | 978.594 | 425.381 |
| approach_goal | approach | 0.67 / step_budget | (0.488, -0.005, 0.256)→(0.519, 0.100, 0.240) | (0.475, 0.005, 0.016)→(0.462, 0.032, 0.015) | 0.267→0.258 | 1.00 / 9.000 | 455.733 | 202.637 |
| descend_at_goal | descend | 0.00 / step_budget | (0.519, 0.100, 0.240)→(0.554, 0.105, 0.271) | (0.462, 0.032, 0.015)→(0.462, 0.032, 0.016) | 0.258→0.259 | 1.00 / 9.333 | 287.818 | 744.878 |
| release_object | release | 1.00 / step_budget | (0.554, 0.105, 0.271)→(0.553, 0.105, 0.298) | (0.462, 0.032, 0.016)→(0.462, 0.032, 0.016) | 0.259→0.259 | 1.00 / 4.000 | 0.123 | 144.384 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 0.000
- place_accuracy: 0.000
- lift_clearance: 0.000
- transport_retention: 0.000
- terminal_score: 0.326
- phase_score: 0.364
- phase_breakdown.lift_clear_score: 0.123
- phase_breakdown.reach_pregrasp_score: 0.111
- phase_breakdown.grasp_contact_score: 1.000
- phase_breakdown.place_goal_score: 0.024
- grasp_place_fitness: 0.238

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.238
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.326
- **Median Q (composite search score)**: -0.343
- **K-run variance**: 0.0022
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.358


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `a4a71a7b2980790489e8194d1356bdee33fb951291c2e0792659ad3d3b3dc711`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `8a78b0f0015ebaf8c4b14c8fbc8142d9b66e4b4efca10f362859101c0ae207df`; realized-scene SHA-256: `5ce27bcdb8582e1d517b17df0f9c2ad7b05701113a75707627744a889253e6a7`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.45856,-0.02632,0.03]},{"name":"goal","value":[0.63013,0.20822,0.11412]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.45856,-0.02632,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.63013,0.20822,0.11412]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":7.46296,"average_solve_count":108.0,"average_success_count":108.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_z":0.16081,"approach_goal.goal_arc_height":0.14156,"approach_object.approach_z":0.14753,"approach_object.arc_height":0.17097,"descend_at_goal.descend_goal_tolerance":0.02287,"hover_above_object.hover_z":0.03391,"lift_object.lift_height":0.09219,"release_object.release_duration":1.11412,"touch_object_top.contact_force":8.84628},"optimized_scores":{"best_composite_score":-0.3802,"best_fitness_score":0.1248,"best_task_score":0.10764},"replay_outcomes":[{"contacts":{"omitted_contact_groups":9,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":887.0,"contact_point_centroid":[0.63245,0.01197,-0.00046],"force_p95":201.32598,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1320.35271,"mean_force":201.05046,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.38768,0.01033,0.11497]},{"body_a":"world","body_b":"link7","contact_count":24.0,"contact_point_centroid":[0.52525,0.01384,-0.00307],"force_p95":326.44263,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1274.08427,"mean_force":69.08893,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.37246,0.00823,0.04823]},{"body_a":"world","body_b":"link6","contact_count":988.0,"contact_point_centroid":[0.62281,-0.00822,-0.00022],"force_p95":420.49627,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":895.97975,"mean_force":285.05711,"phase_index":1.0,"phase_name":"hover_above_object","phase_type":"descend","tcp_position_centroid":[0.42651,-0.00462,0.19271]},{"body_a":"world","body_b":"link6","contact_count":545.0,"contact_point_centroid":[0.65335,-0.02338,-0.00013],"force_p95":79.55258,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":751.51784,"mean_force":73.30121,"phase_index":3.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.45787,-0.0229,0.20054]},{"body_a":"world","body_b":"link6","contact_count":982.0,"contact_point_centroid":[0.56706,0.01927,-0.00023],"force_p95":505.76814,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":707.06485,"mean_force":339.89252,"phase_index":6.0,"phase_name":"descend_at_goal","phase_type":"descend","tcp_position_centroid":[0.40612,0.01592,0.2241]},{"body_a":"world","body_b":"link6","contact_count":999.0,"contact_point_centroid":[0.57846,-0.02622,-0.00026],"force_p95":239.21515,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":253.27969,"mean_force":214.66177,"phase_index":5.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.3353,-0.02004,0.10138]},{"body_a":"world","body_b":"link6","contact_count":563.0,"contact_point_centroid":[0.62002,-0.03048,-0.00026],"force_p95":211.02054,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":248.87385,"mean_force":195.06888,"phase_index":4.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.41069,-0.02233,0.175]},{"body_a":"world","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.65239,-0.02345,-0.00021],"force_p95":202.67469,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":202.67469,"mean_force":202.67469,"phase_index":2.0,"phase_name":"touch_object_top","phase_type":"contact","tcp_position_centroid":[0.45799,-0.02302,0.20144]},{"body_a":"world","body_b":"link6","contact_count":70.0,"contact_point_centroid":[0.58306,0.0436,-0.00017],"force_p95":100.94543,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":124.87827,"mean_force":79.01095,"phase_index":7.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.43272,0.03372,0.23601]},{"body_a":"grasp_target","body_b":"hand","contact_count":40.0,"contact_point_centroid":[0.4385,-0.03706,0.04198],"force_p95":3.37648,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.75021,"mean_force":1.45635,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.38303,0.00829,0.04972]},{"body_a":"world","body_b":"grasp_target","contact_count":3921.0,"contact_point_centroid":[0.42254,-0.02766,-0.00213],"force_p95":0.13759,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.30469,"mean_force":0.13821,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.39989,0.00988,0.12545]},{"body_a":"grasp_target","body_b":"link7","contact_count":809.0,"contact_point_centroid":[0.44656,-0.02706,0.0266],"force_p95":0.38294,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.46214,"mean_force":0.31832,"phase_index":5.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.32646,-0.01904,0.0898]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.41533,-0.02738,-0.00295],"force_p95":0.32384,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.36362,"mean_force":0.18494,"phase_index":5.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.33536,-0.02004,0.10145]},{"body_a":"grasp_target","body_b":"link7","contact_count":16.0,"contact_point_centroid":[0.44454,-0.01922,0.02797],"force_p95":0.2868,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32586,"mean_force":0.0817,"phase_index":6.0,"phase_name":"descend_at_goal","phase_type":"descend","tcp_position_centroid":[0.32503,-0.0101,0.09656]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.41281,-0.02617,-0.00202],"force_p95":0.12276,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.30699,"mean_force":0.12283,"phase_index":6.0,"phase_name":"descend_at_goal","phase_type":"descend","tcp_position_centroid":[0.4057,0.01571,0.22368]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.41754,-0.02785,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"hover_above_object","phase_type":"descend","tcp_position_centroid":[0.42667,-0.0047,0.19284]}],"total_contact_groups":25},"final_pose_error":0.2903,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.41281,-0.02617,0.01602],"final_tcp_position":[0.43289,0.03378,0.23635],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":1366.84211,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.41754,-0.02785,0.01602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.33248,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":199.93034,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4872.0,"raw_peak_contact_force":1320.35271,"subtask_id":"reach_pregrasp","tcp_end":[0.39502,0.00847,0.14153],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13258,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.41754,-0.02785,0.01602],"object_pos_start":[0.41754,-0.02785,0.01602],"object_to_goal_dist_end":0.33248,"object_to_goal_dist_start":0.33248,"object_z_max":0.01602,"peak_contact_force":370.38509,"phase_name":"hover_above_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4988.0,"raw_peak_contact_force":895.97975,"subtask_id":"reach_pregrasp","tcp_end":[0.45799,-0.02302,0.20144],"tcp_start":[0.39502,0.00847,0.14153],"tcp_to_object_dist_end":0.18984,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.41754,-0.02785,0.01602],"object_pos_start":[0.41754,-0.02785,0.01602],"object_to_goal_dist_end":0.33248,"object_to_goal_dist_start":0.33248,"object_z_max":0.01602,"peak_contact_force":241.54123,"phase_name":"touch_object_top","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":5.0,"raw_peak_contact_force":202.67469,"subtask_id":"grasp_contact","tcp_end":[0.45796,-0.02296,0.20149],"tcp_start":[0.45799,-0.02302,0.20144],"tcp_to_object_dist_end":0.18989,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.41754,-0.02785,0.01602],"object_pos_start":[0.41754,-0.02785,0.01602],"object_to_goal_dist_end":0.33248,"object_to_goal_dist_start":0.33248,"object_z_max":0.01602,"peak_contact_force":85.71157,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":3502.0,"raw_peak_contact_force":751.51784,"subtask_id":"grasp_contact","tcp_end":[0.45787,-0.02291,0.20045],"tcp_start":[0.45787,-0.02291,0.20045],"tcp_to_object_dist_end":0.18885,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":564.0,"n_steps_budget":660.0,"object_pos_end":[0.41754,-0.02785,0.01602],"object_pos_start":[0.41754,-0.02785,0.01602],"object_to_goal_dist_end":0.33248,"object_to_goal_dist_start":0.33248,"object_z_max":0.01602,"peak_contact_force":195.97768,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":5201.0,"raw_peak_contact_force":248.87385,"subtask_id":"lift_clear","tcp_end":[0.41803,-0.0253,0.19591],"tcp_start":[0.45787,-0.02291,0.20045],"tcp_to_object_dist_end":0.17991,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.41414,-0.02493,0.01336],"object_pos_start":[0.41754,-0.02785,0.01602],"object_to_goal_dist_end":0.33341,"object_to_goal_dist_start":0.33248,"object_z_max":0.01602,"peak_contact_force":1366.84211,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":10031.0,"raw_peak_contact_force":253.27969,"subtask_id":"place_goal","tcp_end":[0.32128,-0.01003,0.08854],"tcp_start":[0.41803,-0.0253,0.19591],"tcp_to_object_dist_end":0.1204,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.41281,-0.02617,0.01602],"object_pos_start":[0.41414,-0.02493,0.01336],"object_to_goal_dist_end":0.33434,"object_to_goal_dist_start":0.33341,"object_z_max":0.01612,"peak_contact_force":410.67941,"phase_name":"descend_at_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":9227.0,"raw_peak_contact_force":707.06485,"subtask_id":"place_goal","tcp_end":[0.43289,0.03378,0.23635],"tcp_start":[0.32128,-0.01003,0.08854],"tcp_to_object_dist_end":0.22922,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.41281,-0.02617,0.01602],"object_pos_start":[0.41281,-0.02617,0.01602],"object_to_goal_dist_end":0.33434,"object_to_goal_dist_start":0.33434,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1089.0,"raw_peak_contact_force":124.87827,"tcp_end":[0.43198,0.03358,0.26455],"tcp_start":[0.43289,0.03378,0.23635],"tcp_to_object_dist_end":0.25632,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `aa6ec658384c70fac6b4eb656cc8c53536c3d5c760368ab2b384dccf294e2c48`; realized-scene SHA-256: `1959b3932a54fd3d3850620783d44a63a35b8fa059f78d939fdbdef5fbfc64e8`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.54431,0.00113,0.03]},{"name":"goal","value":[0.64762,0.15808,0.1911]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.54431,0.00113,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.64762,0.15808,0.1911]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":5.78676,"average_solve_count":136.0,"average_success_count":136.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_z":0.12884,"approach_goal.goal_arc_height":0.13086,"approach_object.approach_z":0.12608,"approach_object.arc_height":0.18138,"descend_at_goal.descend_goal_tolerance":0.02158,"hover_above_object.hover_z":0.0443,"lift_object.lift_height":0.14909,"release_object.release_duration":0.85481,"touch_object_top.contact_force":10.19625},"optimized_scores":{"best_composite_score":-0.34309,"best_fitness_score":0.16191,"best_task_score":0.16179},"replay_outcomes":[{"contacts":{"omitted_contact_groups":13,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":886.0,"contact_point_centroid":[0.63977,0.0249,-0.00047],"force_p95":354.48787,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1468.65104,"mean_force":220.74122,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.42116,0.02248,0.15838]},{"body_a":"world","body_b":"link6","contact_count":976.0,"contact_point_centroid":[0.63287,0.02345,-0.00023],"force_p95":472.91125,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":900.28435,"mean_force":313.12332,"phase_index":1.0,"phase_name":"hover_above_object","phase_type":"descend","tcp_position_centroid":[0.44484,0.0451,0.20443]},{"body_a":"world","body_b":"link6","contact_count":927.0,"contact_point_centroid":[0.65109,0.14994,-0.00031],"force_p95":543.34201,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":730.8357,"mean_force":377.0747,"phase_index":6.0,"phase_name":"descend_at_goal","phase_type":"descend","tcp_position_centroid":[0.65034,0.15479,0.29363]},{"body_a":"world","body_b":"link7","contact_count":21.0,"contact_point_centroid":[0.53508,0.01047,-0.00372],"force_p95":0.0,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":448.42481,"mean_force":21.35356,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.38153,0.01307,0.04922]},{"body_a":"world","body_b":"link6","contact_count":472.0,"contact_point_centroid":[0.60997,-0.01416,-0.00025],"force_p95":370.29291,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":423.1288,"mean_force":271.23396,"phase_index":4.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.50574,0.04959,0.23895]},{"body_a":"world","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.68483,0.00585,-0.00014],"force_p95":278.00592,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":278.00592,"mean_force":278.00592,"phase_index":2.0,"phase_name":"touch_object_top","phase_type":"contact","tcp_position_centroid":[0.47014,0.06616,0.16493]},{"body_a":"world","body_b":"link6","contact_count":549.0,"contact_point_centroid":[0.6859,0.0057,-0.00012],"force_p95":73.19863,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":225.78097,"mean_force":70.25534,"phase_index":3.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.47016,0.06642,0.16344]},{"body_a":"world","body_b":"link6","contact_count":3.0,"contact_point_centroid":[0.57841,-0.03248,-0.00025],"force_p95":168.13522,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":169.84467,"mean_force":154.20306,"phase_index":5.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.52674,-0.00914,0.28848]},{"body_a":"world","body_b":"link6","contact_count":88.0,"contact_point_centroid":[0.67657,0.15455,-0.0001],"force_p95":79.28616,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":156.44414,"mean_force":53.60929,"phase_index":7.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.65824,0.15804,0.2937]},{"body_a":"link5","body_b":"hand","contact_count":193.0,"contact_point_centroid":[0.51146,-0.10142,0.23965],"force_p95":94.50484,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":97.81993,"mean_force":63.13946,"phase_index":4.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.52463,-5e-05,0.28745]},{"body_a":"grasp_target","body_b":"link6","contact_count":165.0,"contact_point_centroid":[0.54383,-0.00599,0.03162],"force_p95":0.98143,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.75278,"mean_force":0.4515,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.39294,0.01439,0.09936]},{"body_a":"grasp_target","body_b":"link7","contact_count":247.0,"contact_point_centroid":[0.52493,0.00312,0.03405],"force_p95":3.08213,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.43406,"mean_force":0.55462,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.39711,0.01493,0.10469]},{"body_a":"grasp_target","body_b":"hand","contact_count":104.0,"contact_point_centroid":[0.49778,-0.00673,0.0458],"force_p95":2.41087,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.37082,"mean_force":0.96916,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.39127,0.01368,0.08104]},{"body_a":"world","body_b":"grasp_target","contact_count":3705.0,"contact_point_centroid":[0.51574,-0.00431,-0.00217],"force_p95":0.248,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.70701,"mean_force":0.1495,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.43288,0.02154,0.16832]},{"body_a":"grasp_target","body_b":"link6","contact_count":131.0,"contact_point_centroid":[0.51895,0.00176,0.0371],"force_p95":0.78381,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.46851,"mean_force":0.37085,"phase_index":5.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.53206,-0.00469,0.31148]},{"body_a":"grasp_target","body_b":"link6","contact_count":280.0,"contact_point_centroid":[0.53907,-0.01459,0.03523],"force_p95":0.3282,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.35061,"mean_force":0.24348,"phase_index":4.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.52548,0.00808,0.28623]}],"total_contact_groups":29},"final_pose_error":0.10276,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.48131,0.03028,0.01602],"final_tcp_position":[0.65825,0.1585,0.29331],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":1468.65104,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51097,-0.00571,0.01602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.27596,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":353.78611,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":5128.0,"raw_peak_contact_force":1468.65104,"subtask_id":"reach_pregrasp","tcp_end":[0.45586,0.03419,0.20529],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.20113,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51097,-0.00571,0.01602],"object_pos_start":[0.51097,-0.00571,0.01602],"object_to_goal_dist_end":0.27596,"object_to_goal_dist_start":0.27596,"object_z_max":0.01602,"peak_contact_force":450.65849,"phase_name":"hover_above_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4976.0,"raw_peak_contact_force":900.28435,"subtask_id":"reach_pregrasp","tcp_end":[0.47014,0.06616,0.16493],"tcp_start":[0.45586,0.03419,0.20529],"tcp_to_object_dist_end":0.17031,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1.0,"n_steps_budget":900.0,"object_pos_end":[0.51097,-0.00571,0.01602],"object_pos_start":[0.51097,-0.00571,0.01602],"object_to_goal_dist_end":0.27596,"object_to_goal_dist_start":0.27596,"object_z_max":0.01602,"peak_contact_force":278.00592,"phase_name":"touch_object_top","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":5.0,"raw_peak_contact_force":278.00592,"subtask_id":"grasp_contact","tcp_end":[0.47017,0.06629,0.16469],"tcp_start":[0.47014,0.06616,0.16493],"tcp_to_object_dist_end":0.17015,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.51097,-0.00571,0.01602],"object_pos_start":[0.51097,-0.00571,0.01602],"object_to_goal_dist_end":0.27596,"object_to_goal_dist_start":0.27596,"object_z_max":0.01602,"peak_contact_force":69.13034,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":3544.0,"raw_peak_contact_force":225.78097,"subtask_id":"grasp_contact","tcp_end":[0.47015,0.06643,0.16333],"tcp_start":[0.47015,0.06643,0.16333],"tcp_to_object_dist_end":0.16903,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":11.0,"n_steps":513.0,"n_steps_budget":600.0,"object_pos_end":[0.50742,-0.00329,0.01532],"object_pos_start":[0.51097,-0.00571,0.01602],"object_to_goal_dist_end":0.27676,"object_to_goal_dist_start":0.27596,"object_z_max":0.0161,"peak_contact_force":1372.96273,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":5273.0,"raw_peak_contact_force":423.1288,"subtask_id":"lift_clear","tcp_end":[0.52665,-0.00899,0.2882],"tcp_start":[0.47015,0.06643,0.16333],"tcp_to_object_dist_end":0.27361,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":627.0,"n_steps_budget":1000.0,"object_pos_end":[0.48131,0.03028,0.01602],"object_pos_start":[0.50742,-0.00329,0.01532],"object_to_goal_dist_end":0.27322,"object_to_goal_dist_start":0.27676,"object_z_max":0.02019,"peak_contact_force":0.12263,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":5098.0,"raw_peak_contact_force":169.84467,"subtask_id":"place_goal","tcp_end":[0.64055,0.14561,0.33352],"tcp_start":[0.52665,-0.00899,0.2882],"tcp_to_object_dist_end":0.37345,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.48131,0.03028,0.01602],"object_pos_start":[0.48131,0.03028,0.01602],"object_to_goal_dist_end":0.27322,"object_to_goal_dist_start":0.27322,"object_z_max":0.01602,"peak_contact_force":326.01839,"phase_name":"descend_at_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":9208.0,"raw_peak_contact_force":730.8357,"subtask_id":"place_goal","tcp_end":[0.65825,0.1585,0.29331],"tcp_start":[0.64055,0.14561,0.33352],"tcp_to_object_dist_end":0.35304,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48131,0.03028,0.01602],"object_pos_start":[0.48131,0.03028,0.01602],"object_to_goal_dist_end":0.27322,"object_to_goal_dist_start":0.27322,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1108.0,"raw_peak_contact_force":156.44414,"tcp_end":[0.65846,0.15837,0.31857],"tcp_start":[0.65825,0.1585,0.29331],"tcp_to_object_dist_end":0.37326,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `e1209649252ffcf03853fe0727696e22a1eda11729c6c1ae21659980557d7e98`; realized-scene SHA-256: `e32d7866764afb23ec7c7faebb4bcca0aa39fbf2f1ab61f3c9c527b297153af9`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5305,0.03079,0.03]},{"name":"goal","value":[0.60153,0.17858,0.10809]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.5305,0.03079,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.60153,0.17858,0.10809]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":5.90323,"average_solve_count":124.0,"average_success_count":124.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_z":0.17976,"approach_goal.goal_arc_height":0.05001,"approach_object.approach_z":0.14576,"approach_object.arc_height":0.19375,"descend_at_goal.descend_goal_tolerance":0.02219,"hover_above_object.hover_z":0.05072,"lift_object.lift_height":0.11086,"release_object.release_duration":1.80984,"touch_object_top.contact_force":12.98737},"optimized_scores":{"best_composite_score":-0.26661,"best_fitness_score":0.23839,"best_task_score":0.32585},"replay_outcomes":[{"contacts":{"omitted_contact_groups":12,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":884.0,"contact_point_centroid":[0.63495,0.02787,-0.00046],"force_p95":276.35238,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1463.61918,"mean_force":221.90898,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.41573,0.02577,0.15716]},{"body_a":"world","body_b":"link6","contact_count":986.0,"contact_point_centroid":[0.61854,0.04331,-0.00024],"force_p95":466.24644,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":887.25937,"mean_force":324.60888,"phase_index":1.0,"phase_name":"hover_above_object","phase_type":"descend","tcp_position_centroid":[0.43776,0.05712,0.21428]},{"body_a":"world","body_b":"link6","contact_count":988.0,"contact_point_centroid":[0.60702,0.15914,-0.00033],"force_p95":574.8426,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":796.7331,"mean_force":427.21378,"phase_index":6.0,"phase_name":"descend_at_goal","phase_type":"descend","tcp_position_centroid":[0.59367,0.1612,0.29245]},{"body_a":"world","body_b":"link6","contact_count":480.0,"contact_point_centroid":[0.60779,0.02638,-0.00022],"force_p95":508.74617,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":604.14174,"mean_force":310.26838,"phase_index":4.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48259,0.08851,0.23239]},{"body_a":"world","body_b":"link6","contact_count":550.0,"contact_point_centroid":[0.65616,0.05491,-0.00013],"force_p95":77.79839,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":518.31287,"mean_force":74.20445,"phase_index":3.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.45845,0.09361,0.18414]},{"body_a":"world","body_b":"link7","contact_count":21.0,"contact_point_centroid":[0.53231,0.01176,-0.0037],"force_p95":0.0,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":447.09111,"mean_force":21.29005,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.37893,0.01414,0.04975]},{"body_a":"world","body_b":"link6","contact_count":3.0,"contact_point_centroid":[0.58514,0.00418,-0.0002],"force_p95":183.30595,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":184.78749,"mean_force":163.1717,"phase_index":5.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.5191,0.01897,0.28358]},{"body_a":"world","body_b":"link6","contact_count":82.0,"contact_point_centroid":[0.63131,0.16189,-0.00012],"force_p95":75.57468,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":151.82953,"mean_force":55.05185,"phase_index":7.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.56925,0.12263,0.28393]},{"body_a":"link5","body_b":"hand","contact_count":135.0,"contact_point_centroid":[0.5201,-0.07794,0.23553],"force_p95":109.2827,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":114.79724,"mean_force":85.26408,"phase_index":4.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.51527,0.02396,0.28336]},{"body_a":"grasp_target","body_b":"link7","contact_count":199.0,"contact_point_centroid":[0.51473,0.02656,0.03274],"force_p95":3.50001,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.81737,"mean_force":0.6187,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.39246,0.01584,0.09914]},{"body_a":"grasp_target","body_b":"hand","contact_count":100.0,"contact_point_centroid":[0.49492,0.04314,0.04885],"force_p95":2.56199,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.31799,"mean_force":1.02154,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.38841,0.01481,0.08023]},{"body_a":"world","body_b":"grasp_target","contact_count":3702.0,"contact_point_centroid":[0.50468,0.04264,-0.00225],"force_p95":0.33677,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.15937,"mean_force":0.1575,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.4278,0.0247,0.16707]},{"body_a":"grasp_target","body_b":"link6","contact_count":150.0,"contact_point_centroid":[0.51746,0.1095,0.0332],"force_p95":0.35576,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.07532,"mean_force":0.15395,"phase_index":6.0,"phase_name":"descend_at_goal","phase_type":"descend","tcp_position_centroid":[0.59501,0.16629,0.29337]},{"body_a":"grasp_target","body_b":"link6","contact_count":117.0,"contact_point_centroid":[0.53939,0.04391,0.0282],"force_p95":0.79903,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.88454,"mean_force":0.43248,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.38753,0.01521,0.09258]},{"body_a":"world","body_b":"grasp_target","contact_count":1303.0,"contact_point_centroid":[0.48403,0.07745,-0.00313],"force_p95":0.64273,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.72236,"mean_force":0.21372,"phase_index":5.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.55866,0.094,0.31424]},{"body_a":"grasp_target","body_b":"link6","contact_count":240.0,"contact_point_centroid":[0.50324,0.04946,0.04226],"force_p95":0.50196,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.64561,"mean_force":0.32441,"phase_index":5.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.53964,0.05664,0.31458]}],"total_contact_groups":28},"final_pose_error":0.18687,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.49043,0.09215,0.01602],"final_tcp_position":[0.56979,0.1238,0.28391],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":273600.92011,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49973,0.0452,0.01602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.19139,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":348.80367,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":5023.0,"raw_peak_contact_force":1463.61918,"subtask_id":"reach_pregrasp","tcp_end":[0.45047,0.04018,0.21367],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.20376,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49973,0.0452,0.01602],"object_pos_start":[0.49973,0.0452,0.01602],"object_to_goal_dist_end":0.19139,"object_to_goal_dist_start":0.19139,"object_z_max":0.01602,"peak_contact_force":134400.05046,"phase_name":"hover_above_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4986.0,"raw_peak_contact_force":887.25937,"subtask_id":"reach_pregrasp","tcp_end":[0.45868,0.09311,0.18517],"tcp_start":[0.45047,0.04018,0.21367],"tcp_to_object_dist_end":0.18054,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1.0,"n_steps_budget":960.0,"object_pos_end":[0.49973,0.0452,0.01602],"object_pos_start":[0.49973,0.0452,0.01602],"object_to_goal_dist_end":0.19139,"object_to_goal_dist_start":0.19139,"object_z_max":0.01602,"peak_contact_force":273600.92011,"phase_name":"touch_object_top","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":4.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_contact","tcp_end":[0.45859,0.09336,0.18508],"tcp_start":[0.45868,0.09311,0.18517],"tcp_to_object_dist_end":0.18054,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.49973,0.0452,0.01602],"object_pos_start":[0.49973,0.0452,0.01602],"object_to_goal_dist_end":0.19139,"object_to_goal_dist_start":0.19139,"object_z_max":0.01602,"peak_contact_force":71.30225,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":3508.0,"raw_peak_contact_force":518.31287,"subtask_id":"grasp_contact","tcp_end":[0.45845,0.09361,0.18404],"tcp_start":[0.45845,0.09361,0.18404],"tcp_to_object_dist_end":0.17966,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":513.0,"n_steps_budget":600.0,"object_pos_end":[0.49973,0.0452,0.01602],"object_pos_start":[0.49973,0.0452,0.01602],"object_to_goal_dist_end":0.19139,"object_to_goal_dist_start":0.19139,"object_z_max":0.01602,"peak_contact_force":1366.84211,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":4867.0,"raw_peak_contact_force":604.14174,"subtask_id":"lift_clear","tcp_end":[0.51898,0.01907,0.28329],"tcp_start":[0.45845,0.09361,0.18404],"tcp_to_object_dist_end":0.26924,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":449.0,"n_steps_budget":1000.0,"object_pos_end":[0.48958,0.09195,0.01601],"object_pos_start":[0.49973,0.0452,0.01602],"object_to_goal_dist_end":0.16887,"object_to_goal_dist_start":0.19139,"object_z_max":0.02038,"peak_contact_force":0.23366,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3481.0,"raw_peak_contact_force":184.78749,"subtask_id":"place_goal","tcp_end":[0.59406,0.16321,0.29753],"tcp_start":[0.51898,0.01907,0.28329],"tcp_to_object_dist_end":0.30862,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49043,0.09215,0.01602],"object_pos_start":[0.48958,0.09195,0.01601],"object_to_goal_dist_end":0.1682,"object_to_goal_dist_start":0.16887,"object_z_max":0.01602,"peak_contact_force":126.75566,"phase_name":"descend_at_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":9407.0,"raw_peak_contact_force":796.7331,"subtask_id":"place_goal","tcp_end":[0.56979,0.1238,0.28391],"tcp_start":[0.59406,0.16321,0.29753],"tcp_to_object_dist_end":0.28119,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.49043,0.09215,0.01602],"object_pos_start":[0.49043,0.09215,0.01602],"object_to_goal_dist_end":0.1682,"object_to_goal_dist_start":0.1682,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1105.0,"raw_peak_contact_force":151.82953,"tcp_end":[0.56951,0.12271,0.31072],"tcp_start":[0.56979,0.1238,0.28391],"tcp_to_object_dist_end":0.30665,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
```