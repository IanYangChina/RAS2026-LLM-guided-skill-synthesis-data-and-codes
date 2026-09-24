## Search State

- **Seed**: 3
- **Iteration**: 5 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 4 | approach → descend → contact → grasp → lift → approach → descend → release | arc_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 9 | -0.3230 | 0.21 | ✅ accepted |
| 3 | approach → descend → grasp → lift → approach → descend → release → retract | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 9 | -0.4496 | 0.17 | ❌ rejected |
| 2 | approach → descend → grasp → lift → approach → descend → release → retract | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | position_control | force_threshold_switch | position_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 9 | -0.2003 | 0.21 | ✅ accepted |
| 1 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | admittance_control | position_control | position_control | position_control | admittance_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | contact_detected | time_limit | pose_tolerance | 7 | -0.3656 | 0.19 | ✅ accepted |
| 0 | rotate → retract → descend → pull → rotate | impedance_motion | arc_cartesian | linear_cartesian | arc_cartesian | arc_cartesian | position_control | position_control | admittance_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 3 | 0.0374 | 0.17 | ✅ accepted |

**Proposal policy**: task_score is 0.21 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.323) — your mutation base

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

- **Composite score**: -0.323
- **task_score** (E): 0.213
- **fitness_score**: 0.182  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.125
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.630

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 0.00 | 1.00 | 0.1379 |
| hover_above_object | 0.00 | 1.00 | 0.0662 |
| touch_object_top | 1.00 | 1.00 | 0.0001 |
| grasp_object | 1.00 | 1.00 | 0.0000 |
| lift_object | 0.33 | 1.00 | 0.1125 |
| approach_goal | 0.67 | 1.00 | 0.1386 |
| descend_at_goal | 0.00 | 1.00 | 0.0421 |
| release_object | 1.00 | 1.00 | 0.0264 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 0.00 / step_budget | (0.500, -0.000, 0.301)→(0.434, 0.027, 0.186) | (0.511, 0.002, 0.030)→(0.475, 0.002, 0.016) | 0.244→0.269 | 1.00 / 5.000 | 302.378 | 1407.865 |
| hover_above_object | descend | 0.00 / step_budget | (0.434, 0.027, 0.186)→(0.462, 0.044, 0.184) | (0.475, 0.002, 0.016)→(0.475, 0.002, 0.016) | 0.269→0.269 | 1.00 / 5.000 | 374.475 | 899.586 |
| touch_object_top | contact | 1.00 / force_exceeded | (0.462, 0.044, 0.184)→(0.462, 0.044, 0.184) | (0.475, 0.002, 0.016)→(0.475, 0.002, 0.016) | 0.269→0.269 | 1.00 / 4.667 | 316.654 | 224.386 |
| grasp_object | grasp | 1.00 / step_budget | (0.462, 0.044, 0.183)→(0.462, 0.044, 0.183) | (0.475, 0.002, 0.016)→(0.475, 0.002, 0.016) | 0.269→0.269 | 1.00 / 9.333 | 91048.300 | 335.672 |
| lift_object | lift | 0.33 / step_budget | (0.462, 0.044, 0.183)→(0.498, -0.005, 0.250) | (0.475, 0.002, 0.016)→(0.475, 0.002, 0.016) | 0.269→0.269 | 1.00 / 10.333 | 281.508 | 525.470 |
| approach_goal | approach | 0.67 / step_budget | (0.498, -0.005, 0.250)→(0.544, 0.110, 0.271) | (0.475, 0.002, 0.016)→(0.470, 0.039, 0.019) | 0.269→0.249 | 1.00 / 9.000 | 150235.627 | 430.214 |
| descend_at_goal | descend | 0.00 / step_budget | (0.544, 0.110, 0.271)→(0.569, 0.132, 0.274) | (0.470, 0.039, 0.019)→(0.467, 0.043, 0.016) | 0.249→0.251 | 1.00 / 9.333 | 91197.142 | 691.898 |
| release_object | release | 1.00 / step_budget | (0.569, 0.132, 0.274)→(0.569, 0.132, 0.300) | (0.467, 0.043, 0.016)→(0.467, 0.043, 0.016) | 0.251→0.251 | 1.00 / 4.000 | 0.123 | 133.591 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 0.000
- place_accuracy: 0.000
- lift_clearance: 0.000
- transport_retention: 0.000
- terminal_score: 0.363
- phase_score: 0.361
- phase_breakdown.lift_clear_score: 0.116
- phase_breakdown.reach_pregrasp_score: 0.105
- phase_breakdown.grasp_contact_score: 1.000
- phase_breakdown.place_goal_score: 0.024
- grasp_place_fitness: 0.257

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.257
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.363
- **Median Q (composite search score)**: -0.344
- **K-run variance**: 0.0030
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.393


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":7.71698,"average_solve_count":106.0,"average_success_count":106.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_z":0.11147,"approach_goal.goal_arc_height":0.07342,"approach_object.approach_z":0.14998,"approach_object.arc_height":0.19708,"descend_at_goal.descend_goal_tolerance":0.02669,"hover_above_object.hover_z":0.03002,"lift_object.lift_height":0.16373,"release_object.release_duration":1.6693,"touch_object_top.contact_force":8.73999},"optimized_scores":{"best_composite_score":-0.3777,"best_fitness_score":0.1273,"best_task_score":0.10897},"replay_outcomes":[{"contacts":{"omitted_contact_groups":7,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":887.0,"contact_point_centroid":[0.6323,0.00869,-0.00046],"force_p95":201.18692,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1320.45585,"mean_force":200.87454,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.38705,0.00739,0.11402]},{"body_a":"world","body_b":"link7","contact_count":24.0,"contact_point_centroid":[0.52507,0.01147,-0.00305],"force_p95":328.03422,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1262.51734,"mean_force":68.685,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.37228,0.00625,0.0483]},{"body_a":"world","body_b":"link6","contact_count":987.0,"contact_point_centroid":[0.62454,-0.00936,-0.00022],"force_p95":422.48189,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":900.80752,"mean_force":286.78137,"phase_index":1.0,"phase_name":"hover_above_object","phase_type":"descend","tcp_position_centroid":[0.42784,-0.00764,0.19241]},{"body_a":"world","body_b":"link6","contact_count":981.0,"contact_point_centroid":[0.55472,0.0477,-0.00023],"force_p95":560.82963,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":773.09308,"mean_force":363.45381,"phase_index":6.0,"phase_name":"descend_at_goal","phase_type":"descend","tcp_position_centroid":[0.40356,0.03885,0.23384]},{"body_a":"world","body_b":"link6","contact_count":544.0,"contact_point_centroid":[0.65907,-0.02616,-0.00014],"force_p95":82.11262,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":729.359,"mean_force":73.0669,"phase_index":3.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.45938,-0.02571,0.19635]},{"body_a":"world","body_b":"link6","contact_count":50.0,"contact_point_centroid":[0.64809,-0.03026,-9e-05],"force_p95":249.38882,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":255.10871,"mean_force":221.67027,"phase_index":4.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.44857,-0.0265,0.19157]},{"body_a":"world","body_b":"link6","contact_count":990.0,"contact_point_centroid":[0.6085,-0.01671,-0.0002],"force_p95":237.18198,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":244.25398,"mean_force":219.12841,"phase_index":5.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.37601,-0.01535,0.14108]},{"body_a":"world","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.65818,-0.02617,-0.00018],"force_p95":208.38781,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":208.38781,"mean_force":208.38781,"phase_index":2.0,"phase_name":"touch_object_top","phase_type":"contact","tcp_position_centroid":[0.45951,-0.02577,0.19729]},{"body_a":"world","body_b":"link6","contact_count":70.0,"contact_point_centroid":[0.58395,0.07982,-0.00014],"force_p95":91.098,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":148.14495,"mean_force":74.99798,"phase_index":7.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.43138,0.06078,0.23401]},{"body_a":"grasp_target","body_b":"hand","contact_count":40.0,"contact_point_centroid":[0.43863,-0.03702,0.04207],"force_p95":3.38234,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.75694,"mean_force":1.4586,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.38285,0.0063,0.04979]},{"body_a":"world","body_b":"grasp_target","contact_count":3920.0,"contact_point_centroid":[0.42256,-0.02768,-0.00213],"force_p95":0.13759,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.30732,"mean_force":0.13823,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.39932,0.0071,0.1246]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.41755,-0.02788,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"hover_above_object","phase_type":"descend","tcp_position_centroid":[0.42802,-0.00772,0.19256]},{"body_a":"world","body_b":"grasp_target","contact_count":4.0,"contact_point_centroid":[0.41755,-0.02788,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":2.0,"phase_name":"touch_object_top","phase_type":"contact","tcp_position_centroid":[0.45951,-0.02577,0.19729]},{"body_a":"world","body_b":"grasp_target","contact_count":2200.0,"contact_point_centroid":[0.41755,-0.02788,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":3.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.45938,-0.02571,0.19636]},{"body_a":"world","body_b":"grasp_target","contact_count":220.0,"contact_point_centroid":[0.41755,-0.02788,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":4.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.44823,-0.02653,0.19136]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.41755,-0.02788,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.37605,-0.01515,0.1414]}],"total_contact_groups":23},"final_pose_error":0.27499,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.41755,-0.02788,0.01602],"final_tcp_position":[0.43154,0.06085,0.23438],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":273006.30642,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.41755,-0.02788,0.01602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.3325,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":199.96696,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4871.0,"raw_peak_contact_force":1320.45585,"subtask_id":"reach_pregrasp","tcp_end":[0.39379,0.00495,0.13953],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12999,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.41755,-0.02788,0.01602],"object_pos_start":[0.41755,-0.02788,0.01602],"object_to_goal_dist_end":0.3325,"object_to_goal_dist_start":0.3325,"object_z_max":0.01602,"peak_contact_force":362.73838,"phase_name":"hover_above_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4987.0,"raw_peak_contact_force":900.80752,"subtask_id":"reach_pregrasp","tcp_end":[0.45951,-0.02577,0.19729],"tcp_start":[0.39379,0.00495,0.13953],"tcp_to_object_dist_end":0.18608,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1.0,"n_steps_budget":990.0,"object_pos_end":[0.41755,-0.02788,0.01602],"object_pos_start":[0.41755,-0.02788,0.01602],"object_to_goal_dist_end":0.3325,"object_to_goal_dist_start":0.3325,"object_z_max":0.01602,"peak_contact_force":208.38781,"phase_name":"touch_object_top","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":5.0,"raw_peak_contact_force":208.38781,"subtask_id":"grasp_contact","tcp_end":[0.45949,-0.02572,0.19734],"tcp_start":[0.45951,-0.02577,0.19729],"tcp_to_object_dist_end":0.18612,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.41755,-0.02788,0.01602],"object_pos_start":[0.41755,-0.02788,0.01602],"object_to_goal_dist_end":0.3325,"object_to_goal_dist_start":0.3325,"object_z_max":0.01602,"peak_contact_force":69.60304,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":3495.0,"raw_peak_contact_force":729.359,"subtask_id":"grasp_contact","tcp_end":[0.45938,-0.02572,0.19625],"tcp_start":[0.45938,-0.02572,0.19626],"tcp_to_object_dist_end":0.18504,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":55.0,"n_steps_budget":600.0,"object_pos_end":[0.41755,-0.02788,0.01602],"object_pos_start":[0.41755,-0.02788,0.01602],"object_to_goal_dist_end":0.3325,"object_to_goal_dist_start":0.3325,"object_z_max":0.01602,"peak_contact_force":173.51062,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":501.0,"raw_peak_contact_force":255.10871,"subtask_id":"lift_clear","tcp_end":[0.4265,-0.02797,0.17756],"tcp_start":[0.45938,-0.02572,0.19625],"tcp_to_object_dist_end":0.16179,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.41755,-0.02788,0.01602],"object_pos_start":[0.41755,-0.02788,0.01602],"object_to_goal_dist_end":0.3325,"object_to_goal_dist_start":0.3325,"object_z_max":0.01602,"peak_contact_force":273006.30642,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":9197.0,"raw_peak_contact_force":244.25398,"subtask_id":"place_goal","tcp_end":[0.38641,0.01351,0.19498],"tcp_start":[0.4265,-0.02797,0.17756],"tcp_to_object_dist_end":0.18631,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.41755,-0.02788,0.01602],"object_pos_start":[0.41755,-0.02788,0.01602],"object_to_goal_dist_end":0.3325,"object_to_goal_dist_start":0.3325,"object_z_max":0.01602,"peak_contact_force":456.13737,"phase_name":"descend_at_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":9209.0,"raw_peak_contact_force":773.09308,"subtask_id":"place_goal","tcp_end":[0.43154,0.06085,0.23438],"tcp_start":[0.38641,0.01351,0.19498],"tcp_to_object_dist_end":0.23612,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.41755,-0.02788,0.01602],"object_pos_start":[0.41755,-0.02788,0.01602],"object_to_goal_dist_end":0.3325,"object_to_goal_dist_start":0.3325,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1086.0,"raw_peak_contact_force":148.14495,"tcp_end":[0.43062,0.06062,0.26245],"tcp_start":[0.43154,0.06085,0.23438],"tcp_to_object_dist_end":0.26217,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":5.81679,"average_solve_count":131.0,"average_success_count":131.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_z":0.12234,"approach_goal.goal_arc_height":0.15647,"approach_object.approach_z":0.131,"approach_object.arc_height":0.1986,"descend_at_goal.descend_goal_tolerance":0.02541,"hover_above_object.hover_z":0.04524,"lift_object.lift_height":0.11165,"release_object.release_duration":0.56122,"touch_object_top.contact_force":8.72645},"optimized_scores":{"best_composite_score":-0.34365,"best_fitness_score":0.16135,"best_task_score":0.16637},"replay_outcomes":[{"contacts":{"omitted_contact_groups":12,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":886.0,"contact_point_centroid":[0.64059,0.02249,-0.00047],"force_p95":339.9329,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1470.34067,"mean_force":217.63208,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.42183,0.01967,0.15806]},{"body_a":"world","body_b":"link6","contact_count":979.0,"contact_point_centroid":[0.63087,0.0198,-0.00023],"force_p95":454.1404,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":911.62567,"mean_force":302.74417,"phase_index":1.0,"phase_name":"hover_above_object","phase_type":"descend","tcp_position_centroid":[0.44256,0.03841,0.20443]},{"body_a":"world","body_b":"link6","contact_count":944.0,"contact_point_centroid":[0.65115,0.14872,-0.00031],"force_p95":543.99649,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":737.86347,"mean_force":373.07364,"phase_index":6.0,"phase_name":"descend_at_goal","phase_type":"descend","tcp_position_centroid":[0.65005,0.15307,0.29364]},{"body_a":"link5","body_b":"hand","contact_count":284.0,"contact_point_centroid":[0.50681,-0.0735,0.2412],"force_p95":357.73307,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":702.35927,"mean_force":219.64404,"phase_index":4.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.53662,0.01693,0.2795]},{"body_a":"world","body_b":"link6","contact_count":484.0,"contact_point_centroid":[0.62388,-0.00922,-0.00021],"force_p95":488.07152,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":613.59295,"mean_force":292.71376,"phase_index":4.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.50308,0.05711,0.2291]},{"body_a":"world","body_b":"link7","contact_count":21.0,"contact_point_centroid":[0.53578,0.01669,-0.00373],"force_p95":0.0,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":447.68894,"mean_force":21.31852,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.38223,0.01159,0.04909]},{"body_a":"world","body_b":"link6","contact_count":3.0,"contact_point_centroid":[0.60026,-0.03663,-0.0002],"force_p95":239.32354,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":246.14585,"mean_force":200.62302,"phase_index":5.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.54227,-0.0069,0.28587]},{"body_a":"world","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.67793,0.00565,-0.0001],"force_p95":235.62283,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":235.62283,"mean_force":235.62283,"phase_index":2.0,"phase_name":"touch_object_top","phase_type":"contact","tcp_position_centroid":[0.4683,0.05705,0.17426]},{"body_a":"world","body_b":"link6","contact_count":546.0,"contact_point_centroid":[0.67877,0.00575,-0.00013],"force_p95":76.17311,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":198.10446,"mean_force":70.79541,"phase_index":3.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.46813,0.05723,0.17296]},{"body_a":"link5","body_b":"hand","contact_count":5.0,"contact_point_centroid":[0.50695,-0.09602,0.23499],"force_p95":186.54152,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":187.07674,"mean_force":154.85485,"phase_index":5.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.54246,-0.00714,0.28641]},{"body_a":"world","body_b":"link6","contact_count":88.0,"contact_point_centroid":[0.67748,0.15439,-0.00012],"force_p95":76.33922,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":126.81433,"mean_force":54.79443,"phase_index":7.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.65864,0.15711,0.29363]},{"body_a":"grasp_target","body_b":"link6","contact_count":152.0,"contact_point_centroid":[0.54473,-0.00994,0.03132],"force_p95":0.87701,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.75114,"mean_force":0.44672,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.39298,0.01264,0.09721]},{"body_a":"grasp_target","body_b":"link7","contact_count":243.0,"contact_point_centroid":[0.5244,0.0011,0.03432],"force_p95":3.11947,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.46549,"mean_force":0.57463,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.39772,0.01318,0.10412]},{"body_a":"grasp_target","body_b":"hand","contact_count":107.0,"contact_point_centroid":[0.49864,-0.007,0.04653],"force_p95":2.44156,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.386,"mean_force":0.98503,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.3921,0.01215,0.08175]},{"body_a":"world","body_b":"grasp_target","contact_count":3700.0,"contact_point_centroid":[0.51552,-0.00474,-0.00219],"force_p95":0.23251,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.64849,"mean_force":0.14829,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.43356,0.01887,0.16816]},{"body_a":"world","body_b":"grasp_target","contact_count":1969.0,"contact_point_centroid":[0.49369,0.02074,-0.00227],"force_p95":0.43727,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.71556,"mean_force":0.15282,"phase_index":5.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.58712,0.06159,0.33659]}],"total_contact_groups":28},"final_pose_error":0.10276,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.49244,0.02527,0.01602],"final_tcp_position":[0.65866,0.15753,0.29327],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":273007.72148,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51057,-0.00616,0.01602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.27643,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":349.98887,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":5109.0,"raw_peak_contact_force":1470.34067,"subtask_id":"reach_pregrasp","tcp_end":[0.4563,0.02944,0.20472],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.19955,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51057,-0.00616,0.01602],"object_pos_start":[0.51057,-0.00616,0.01602],"object_to_goal_dist_end":0.27643,"object_to_goal_dist_start":0.27643,"object_z_max":0.01602,"peak_contact_force":377.0326,"phase_name":"hover_above_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4979.0,"raw_peak_contact_force":911.62567,"subtask_id":"reach_pregrasp","tcp_end":[0.4683,0.05705,0.17426],"tcp_start":[0.4563,0.02944,0.20472],"tcp_to_object_dist_end":0.17557,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1.0,"n_steps_budget":930.0,"object_pos_end":[0.51057,-0.00616,0.01602],"object_pos_start":[0.51057,-0.00616,0.01602],"object_to_goal_dist_end":0.27643,"object_to_goal_dist_start":0.27643,"object_z_max":0.01602,"peak_contact_force":685.54894,"phase_name":"touch_object_top","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":5.0,"raw_peak_contact_force":235.62283,"subtask_id":"grasp_contact","tcp_end":[0.4683,0.05699,0.17429],"tcp_start":[0.4683,0.05705,0.17426],"tcp_to_object_dist_end":0.17557,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.51057,-0.00616,0.01602],"object_pos_start":[0.51057,-0.00616,0.01602],"object_to_goal_dist_end":0.27643,"object_to_goal_dist_start":0.27643,"object_z_max":0.01602,"peak_contact_force":273004.12072,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":3528.0,"raw_peak_contact_force":198.10446,"subtask_id":"grasp_contact","tcp_end":[0.46813,0.05723,0.17285],"tcp_start":[0.46813,0.05723,0.17285],"tcp_to_object_dist_end":0.17441,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":11.0,"n_steps":513.0,"n_steps_budget":600.0,"object_pos_end":[0.51057,-0.00616,0.01602],"object_pos_start":[0.51057,-0.00616,0.01602],"object_to_goal_dist_end":0.27643,"object_to_goal_dist_start":0.27643,"object_z_max":0.01602,"peak_contact_force":447.35287,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":5061.0,"raw_peak_contact_force":702.35927,"subtask_id":"lift_clear","tcp_end":[0.54213,-0.00672,0.28556],"tcp_start":[0.46813,0.05723,0.17285],"tcp_to_object_dist_end":0.27138,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":544.0,"n_steps_budget":1000.0,"object_pos_end":[0.49244,0.02527,0.01602],"object_pos_start":[0.51057,-0.00616,0.01602],"object_to_goal_dist_end":0.26903,"object_to_goal_dist_start":0.27643,"object_z_max":0.01759,"peak_contact_force":9748.84313,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4513.0,"raw_peak_contact_force":246.14585,"subtask_id":"place_goal","tcp_end":[0.63927,0.14286,0.32312],"tcp_start":[0.54213,-0.00672,0.28556],"tcp_to_object_dist_end":0.36014,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49244,0.02527,0.01602],"object_pos_start":[0.49244,0.02527,0.01602],"object_to_goal_dist_end":0.26903,"object_to_goal_dist_start":0.26903,"object_z_max":0.01602,"peak_contact_force":273007.72148,"phase_name":"descend_at_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":9245.0,"raw_peak_contact_force":737.86347,"subtask_id":"place_goal","tcp_end":[0.65866,0.15753,0.29327],"tcp_start":[0.63927,0.14286,0.32312],"tcp_to_object_dist_end":0.34927,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.49244,0.02527,0.01602],"object_pos_start":[0.49244,0.02527,0.01602],"object_to_goal_dist_end":0.26903,"object_to_goal_dist_start":0.26903,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1112.0,"raw_peak_contact_force":126.81433,"tcp_end":[0.65887,0.15742,0.31846],"tcp_start":[0.65866,0.15753,0.29327],"tcp_to_object_dist_end":0.36964,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":6.12903,"average_solve_count":124.0,"average_success_count":124.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_z":0.13792,"approach_goal.goal_arc_height":0.15064,"approach_object.approach_z":0.1437,"approach_object.arc_height":0.15586,"descend_at_goal.descend_goal_tolerance":0.01717,"hover_above_object.hover_z":0.05176,"lift_object.lift_height":0.143,"release_object.release_duration":1.01671,"touch_object_top.contact_force":10.15479},"optimized_scores":{"best_composite_score":-0.24761,"best_fitness_score":0.25739,"best_task_score":0.36339},"replay_outcomes":[{"contacts":{"omitted_contact_groups":13,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":884.0,"contact_point_centroid":[0.63488,0.03287,-0.00044],"force_p95":305.10707,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1432.7991,"mean_force":227.00181,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.41549,0.03046,0.1568]},{"body_a":"world","body_b":"link6","contact_count":982.0,"contact_point_centroid":[0.61898,0.04787,-0.00024],"force_p95":471.2442,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":886.32494,"mean_force":322.01642,"phase_index":1.0,"phase_name":"hover_above_object","phase_type":"descend","tcp_position_centroid":[0.43771,0.06326,0.21347]},{"body_a":"world","body_b":"link6","contact_count":394.0,"contact_point_centroid":[0.58995,0.15382,-0.00025],"force_p95":602.11094,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":800.24208,"mean_force":423.51034,"phase_index":5.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.59979,0.16266,0.29356]},{"body_a":"world","body_b":"link6","contact_count":488.0,"contact_point_centroid":[0.62526,0.03522,-0.00019],"force_p95":361.59131,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":618.94281,"mean_force":255.23525,"phase_index":4.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.4661,0.12125,0.19997]},{"body_a":"world","body_b":"link6","contact_count":999.0,"contact_point_centroid":[0.6151,0.17162,-0.00032],"force_p95":448.09864,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":564.73655,"mean_force":342.39275,"phase_index":6.0,"phase_name":"descend_at_goal","phase_type":"descend","tcp_position_centroid":[0.61082,0.17477,0.29366]},{"body_a":"link5","body_b":"hand","contact_count":200.0,"contact_point_centroid":[0.48838,0.00547,0.23153],"force_p95":428.04554,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":505.41885,"mean_force":254.22438,"phase_index":4.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49981,0.07901,0.25105]},{"body_a":"link5","body_b":"hand","contact_count":53.0,"contact_point_centroid":[0.46008,-0.04384,0.23971],"force_p95":256.65244,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":358.6493,"mean_force":213.47735,"phase_index":5.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.51894,0.01559,0.2952]},{"body_a":"world","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.65727,0.05415,-1e-05],"force_p95":229.14798,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":229.14798,"mean_force":229.14798,"phase_index":2.0,"phase_name":"touch_object_top","phase_type":"contact","tcp_position_centroid":[0.45835,0.10048,0.18129]},{"body_a":"world","body_b":"link6","contact_count":86.0,"contact_point_centroid":[0.63907,0.17666,-0.00012],"force_p95":77.36463,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":125.81407,"mean_force":55.39577,"phase_index":7.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.6164,0.17808,0.29337]},{"body_a":"world","body_b":"link6","contact_count":548.0,"contact_point_centroid":[0.65779,0.05532,-0.00013],"force_p95":75.30958,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":79.55278,"mean_force":71.44524,"phase_index":3.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.45807,0.10157,0.1802]},{"body_a":"grasp_target","body_b":"link7","contact_count":221.0,"contact_point_centroid":[0.51302,0.02728,0.03224],"force_p95":3.36675,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.85129,"mean_force":0.56806,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.39225,0.01883,0.09958]},{"body_a":"grasp_target","body_b":"hand","contact_count":102.0,"contact_point_centroid":[0.49188,0.0401,0.04654],"force_p95":2.43604,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.857,"mean_force":0.9635,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.38785,0.01746,0.07943]},{"body_a":"world","body_b":"grasp_target","contact_count":3753.0,"contact_point_centroid":[0.5013,0.03857,-0.00227],"force_p95":0.3074,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.07015,"mean_force":0.15747,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.42704,0.02904,0.16604]},{"body_a":"grasp_target","body_b":"link6","contact_count":811.0,"contact_point_centroid":[0.50525,0.08578,0.03933],"force_p95":0.6941,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.8619,"mean_force":0.40672,"phase_index":5.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.57367,0.11602,0.29997]},{"body_a":"grasp_target","body_b":"link6","contact_count":375.0,"contact_point_centroid":[0.52641,0.12664,0.03388],"force_p95":0.25969,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.31087,"mean_force":0.10691,"phase_index":6.0,"phase_name":"descend_at_goal","phase_type":"descend","tcp_position_centroid":[0.60815,0.17162,0.29379]},{"body_a":"world","body_b":"grasp_target","contact_count":1739.0,"contact_point_centroid":[0.49174,0.0884,-0.00602],"force_p95":0.81536,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.05708,"mean_force":0.4066,"phase_index":5.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.57044,0.10997,0.30093]}],"total_contact_groups":29},"final_pose_error":0.18553,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.49022,0.1318,0.01602],"final_tcp_position":[0.61638,0.17846,0.29302],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":167951.73011,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49553,0.04002,0.01602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.19726,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":357.17819,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":5079.0,"raw_peak_contact_force":1432.7991,"subtask_id":"reach_pregrasp","tcp_end":[0.45061,0.04658,0.21279],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.20194,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49553,0.04002,0.01602],"object_pos_start":[0.49553,0.04002,0.01602],"object_to_goal_dist_end":0.19726,"object_to_goal_dist_start":0.19726,"object_z_max":0.01602,"peak_contact_force":383.65515,"phase_name":"hover_above_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4982.0,"raw_peak_contact_force":886.32494,"subtask_id":"reach_pregrasp","tcp_end":[0.45835,0.10048,0.18129],"tcp_start":[0.45061,0.04658,0.21279],"tcp_to_object_dist_end":0.17987,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1.0,"n_steps_budget":960.0,"object_pos_end":[0.49553,0.04002,0.01602],"object_pos_start":[0.49553,0.04002,0.01602],"object_to_goal_dist_end":0.19726,"object_to_goal_dist_start":0.19726,"object_z_max":0.01602,"peak_contact_force":56.0261,"phase_name":"touch_object_top","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":5.0,"raw_peak_contact_force":229.14798,"subtask_id":"grasp_contact","tcp_end":[0.45829,0.10072,0.18119],"tcp_start":[0.45835,0.10048,0.18129],"tcp_to_object_dist_end":0.17987,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.49553,0.04002,0.01602],"object_pos_start":[0.49553,0.04002,0.01602],"object_to_goal_dist_end":0.19726,"object_to_goal_dist_start":0.19726,"object_z_max":0.01602,"peak_contact_force":71.17674,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":3513.0,"raw_peak_contact_force":79.55278,"subtask_id":"grasp_contact","tcp_end":[0.45807,0.10156,0.18011],"tcp_start":[0.45807,0.10156,0.18011],"tcp_to_object_dist_end":0.17921,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":11.0,"n_steps":513.0,"n_steps_budget":600.0,"object_pos_end":[0.49553,0.04002,0.01602],"object_pos_start":[0.49553,0.04002,0.01602],"object_to_goal_dist_end":0.19726,"object_to_goal_dist_start":0.19726,"object_z_max":0.01602,"peak_contact_force":223.65967,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":4939.0,"raw_peak_contact_force":618.94281,"subtask_id":"lift_clear","tcp_end":[0.52506,0.01993,0.2872],"tcp_start":[0.45807,0.10156,0.18011],"tcp_to_object_dist_end":0.27353,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":818.0,"n_steps_budget":1000.0,"object_pos_end":[0.50016,0.11957,0.02432],"object_pos_start":[0.49553,0.04002,0.01602],"object_to_goal_dist_end":0.14414,"object_to_goal_dist_start":0.19726,"object_z_max":0.02432,"peak_contact_force":167951.73011,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":6531.0,"raw_peak_contact_force":800.24208,"subtask_id":"place_goal","tcp_end":[0.6068,0.17251,0.29373],"tcp_start":[0.52506,0.01993,0.2872],"tcp_to_object_dist_end":0.29455,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49022,0.1318,0.01602],"object_pos_start":[0.50016,0.11957,0.02432],"object_to_goal_dist_end":0.15184,"object_to_goal_dist_start":0.14414,"object_z_max":0.0244,"peak_contact_force":127.56783,"phase_name":"descend_at_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":9472.0,"raw_peak_contact_force":564.73655,"subtask_id":"place_goal","tcp_end":[0.61638,0.17846,0.29302],"tcp_start":[0.6068,0.17251,0.29373],"tcp_to_object_dist_end":0.30794,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.49022,0.1318,0.01602],"object_pos_start":[0.49022,0.1318,0.01602],"object_to_goal_dist_end":0.15184,"object_to_goal_dist_start":0.15184,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1106.0,"raw_peak_contact_force":125.81407,"tcp_end":[0.61663,0.17807,0.3189],"tcp_start":[0.61638,0.17846,0.29302],"tcp_to_object_dist_end":0.33145,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
```