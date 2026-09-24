## Search State

- **Seed**: 3
- **Iteration**: 14 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 13 | retract → approach → contact → grasp → lift → approach → descend → release | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 9 | -0.3646 | 0.25 | ❌ rejected |
| 12 | approach → contact → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 7 | -0.1267 | 0.22 | ❌ rejected |
| 11 | approach → contact → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 8 | -0.2169 | 0.19 | ❌ rejected |
| 10 | retract → approach → contact → grasp → lift → approach → descend → release | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 9 | -0.3474 | 0.27 | ✅ accepted |
| 9 | approach → descend → contact → grasp → lift → approach → descend → release | arc_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 9 | -0.3300 | 0.20 | ❌ rejected |

**Proposal policy**: task_score is 0.25 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.365) — your mutation base

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
- id: retract_up
  type: retract
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.3
    tolerance: 0.02
  parameters:
    retract_height:
      type: scalar
      range:
      - 0.2
      - 0.4
      default: 0.3
      binds_to:
      - path: target.offset.z
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat
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
    - 0.2
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
      - 0.15
      - 0.25
      default: 0.2
      binds_to:
      - path: target.offset.z
        mode: replace
    arc_height:
      type: scalar
      range:
      - 0.1
      - 0.3
      default: 0.2
      binds_to:
      - path: generator.arc_height
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat
  subtask_id: reach_pregrasp
- id: descend_contact
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
    - 0.01
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
      - 0.1
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
- **retract_up** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.3], tolerance=0.02
  - parameter_bindings:
    - retract_height: status=consumed; consumers=target.offset.z (replace)
  - retries: max_attempts=0, strategy=repeat
- **approach_object** (`approach`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.2], tolerance=0.02
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=world_z, tolerance=0.1
  - parameter_bindings:
    - approach_z: status=consumed; consumers=target.offset.z (replace)
    - arc_height: status=consumed; consumers=generator.arc_height (replace)
  - retries: max_attempts=0, strategy=repeat
- **descend_contact** (`contact`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.01]
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

- **Composite score**: -0.365
- **task_score** (E): 0.246
- **fitness_score**: 0.140  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.125
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.630

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| retract_up | 1.00 | 1.00 | 0.2451 |
| approach_object | 0.00 | 1.00 | 0.4245 |
| descend_contact | 1.00 | 1.00 | 0.0050 |
| grasp_object | 1.00 | 1.00 | 0.0000 |
| lift_object | 0.00 | 1.00 | 0.2711 |
| approach_goal | 0.33 | 1.00 | 0.1295 |
| descend_at_goal | 0.00 | 1.00 | 0.0322 |
| release_object | 1.00 | 1.00 | 0.0251 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| retract_up | retract | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.500, 0.000, 0.546) | (0.511, 0.002, 0.030)→(0.511, 0.002, 0.026) | 0.244→0.246 | 1.00 / 4.000 | 7.967 | 0.138 |
| approach_object | approach | 0.00 / step_budget | (0.500, 0.000, 0.546)→(0.808, 0.112, 0.282) | (0.511, 0.002, 0.026)→(0.511, 0.002, 0.026) | 0.246→0.246 | 1.00 / 4.000 | 0.123 | 0.123 |
| descend_contact | contact | 1.00 / force_exceeded | (0.808, 0.112, 0.282)→(0.812, 0.113, 0.283) | (0.511, 0.002, 0.026)→(0.511, 0.002, 0.026) | 0.246→0.246 | 1.00 / 4.000 | 565.970 | 0.123 |
| grasp_object | grasp | 1.00 / step_budget | (0.810, 0.113, 0.260)→(0.810, 0.113, 0.260) | (0.511, 0.002, 0.026)→(0.511, 0.002, 0.026) | 0.246→0.246 | 1.00 / 8.333 | 94251.046 | 0.123 |
| lift_object | lift | 0.00 / step_budget | (0.810, 0.113, 0.260)→(0.586, 0.089, 0.281) | (0.511, 0.002, 0.026)→(0.511, 0.002, 0.026) | 0.246→0.246 | 1.00 / 10.000 | 532.457 | 1581.771 |
| approach_goal | approach | 0.33 / step_budget | (0.586, 0.089, 0.281)→(0.619, 0.192, 0.310) | (0.511, 0.002, 0.026)→(0.508, 0.041, 0.019) | 0.246→0.227 | 1.00 / 10.000 | 182119.226 | 716.463 |
| descend_at_goal | descend | 0.00 / step_budget | (0.619, 0.192, 0.310)→(0.630, 0.205, 0.291) | (0.508, 0.041, 0.019)→(0.513, 0.043, 0.019) | 0.227→0.224 | 1.00 / 9.333 | 56207.335 | 626.624 |
| release_object | release | 1.00 / step_budget | (0.630, 0.205, 0.291)→(0.630, 0.205, 0.316) | (0.513, 0.043, 0.019)→(0.512, 0.042, 0.019) | 0.224→0.224 | 1.00 / 4.000 | 0.124 | 118.112 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 0.000
- place_accuracy: 0.000
- lift_clearance: 0.000
- transport_retention: 0.000
- terminal_score: 0.387
- phase_score: 0.320
- phase_breakdown.lift_clear_score: 0.051
- phase_breakdown.reach_pregrasp_score: 0.001
- phase_breakdown.grasp_contact_score: 1.000
- phase_breakdown.place_goal_score: 0.024
- grasp_place_fitness: 0.209

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.209
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.387
- **Median Q (composite search score)**: -0.382
- **K-run variance**: 0.0026
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.381


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":52.0,"average_failure_rate":0.27225,"average_mean_iterations":60.17277,"average_solve_count":191.0,"average_success_count":139.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_z":0.12589,"approach_goal.goal_arc_height":0.12974,"approach_object.approach_z":0.24533,"approach_object.arc_height":0.19727,"descend_at_goal.descend_goal_tolerance":0.02504,"descend_contact.contact_force":11.06163,"lift_object.lift_height":0.16005,"release_object.release_duration":1.27261,"retract_up.retract_height":0.20115},"optimized_scores":{"best_composite_score":-0.41616,"best_fitness_score":0.08884,"best_task_score":0.13208},"replay_outcomes":[{"contacts":{"omitted_contact_groups":6,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":98.0,"contact_point_centroid":[0.57209,0.24786,-0.00433],"force_p95":2094.37798,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":3099.43434,"mean_force":459.59518,"phase_index":4.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.58606,0.18308,0.27588]},{"body_a":"world","body_b":"link5","contact_count":312.0,"contact_point_centroid":[0.51471,0.16528,-0.00114],"force_p95":347.87765,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1767.65911,"mean_force":238.35294,"phase_index":4.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.58251,0.18145,0.28498]},{"body_a":"world","body_b":"link6","contact_count":817.0,"contact_point_centroid":[0.55158,0.32194,-0.00022],"force_p95":424.88631,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":722.96231,"mean_force":322.0603,"phase_index":5.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.58367,0.25687,0.28308]},{"body_a":"world","body_b":"link5","contact_count":975.0,"contact_point_centroid":[0.53482,0.26893,-0.0002],"force_p95":433.9034,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":629.24013,"mean_force":298.99554,"phase_index":6.0,"phase_name":"descend_at_goal","phase_type":"descend","tcp_position_centroid":[0.60333,0.28605,0.28354]},{"body_a":"world","body_b":"link5","contact_count":137.0,"contact_point_centroid":[0.52688,0.24773,-0.00016],"force_p95":414.07381,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":553.03446,"mean_force":270.39633,"phase_index":5.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.60545,0.26655,0.28126]},{"body_a":"world","body_b":"link6","contact_count":347.0,"contact_point_centroid":[0.57426,0.35155,-0.00016],"force_p95":228.37807,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":347.98839,"mean_force":168.43135,"phase_index":6.0,"phase_name":"descend_at_goal","phase_type":"descend","tcp_position_centroid":[0.60101,0.27928,0.2821]},{"body_a":"link5","body_b":"hand","contact_count":273.0,"contact_point_centroid":[0.4853,0.15228,0.22069],"force_p95":226.94339,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":229.64417,"mean_force":104.85737,"phase_index":4.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.57125,0.18097,0.28796]},{"body_a":"world","body_b":"link5","contact_count":90.0,"contact_point_centroid":[0.55523,0.28174,-0.00012],"force_p95":85.13275,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":136.21061,"mean_force":61.80263,"phase_index":7.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.61154,0.28612,0.28666]},{"body_a":"link5","body_b":"hand","contact_count":7.0,"contact_point_centroid":[0.47372,0.15115,0.22376],"force_p95":35.00708,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":40.89447,"mean_force":11.82878,"phase_index":5.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.56216,0.18282,0.2863]},{"body_a":"world","body_b":"grasp_target","contact_count":2312.0,"contact_point_centroid":[0.45856,-0.02632,-0.00194],"force_p95":0.13126,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12284,"phase_index":0.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.49853,-1e-05,0.39049]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.78246,0.0448,0.2141]},{"body_a":"world","body_b":"grasp_target","contact_count":8.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":2.0,"phase_name":"descend_contact","phase_type":"contact","tcp_position_centroid":[0.79333,0.06473,0.15499]},{"body_a":"world","body_b":"grasp_target","contact_count":2200.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":3.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.78877,0.06513,0.13836]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":4.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.20043,-0.03705,0.45923]},{"body_a":"world","body_b":"grasp_target","contact_count":3620.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.58352,0.25511,0.28317]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"descend_at_goal","phase_type":"descend","tcp_position_centroid":[0.6033,0.2858,0.2835]}],"total_contact_groups":22},"final_pose_error":0.18983,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.45856,-0.02632,0.02602],"final_tcp_position":[0.61145,0.28593,0.2863],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":273006.87155,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":579.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":23.65606,"phase_name":"retract_up","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2312.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.49928,-0.0,0.48209],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.45864,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_pregrasp","tcp_end":[0.79323,0.06462,0.15504],"tcp_start":[0.49928,-0.0,0.48209],"tcp_to_object_dist_end":0.37002,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":2.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":431.93571,"phase_name":"descend_contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":8.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_contact","tcp_end":[0.79384,0.06526,0.15487],"tcp_start":[0.79323,0.06462,0.15504],"tcp_to_object_dist_end":0.37067,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":273004.12084,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":2979.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_contact","tcp_end":[0.78804,0.06503,0.1361],"tcp_start":[0.78804,0.06503,0.1361],"tcp_to_object_dist_end":0.35919,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":1366.84211,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":8973.0,"raw_peak_contact_force":3099.43434,"subtask_id":"lift_clear","tcp_end":[0.56221,0.18217,0.28607],"tcp_start":[0.78804,0.06503,0.1361],"tcp_to_object_dist_end":0.34905,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":905.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":273006.87155,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8418.0,"raw_peak_contact_force":722.96231,"subtask_id":"place_goal","tcp_end":[0.60898,0.26644,0.28129],"tcp_start":[0.56221,0.18217,0.28607],"tcp_to_object_dist_end":0.41653,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":345.48251,"phase_name":"descend_at_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":9539.0,"raw_peak_contact_force":629.24013,"subtask_id":"place_goal","tcp_end":[0.61145,0.28593,0.2863],"tcp_start":[0.60898,0.26644,0.28129],"tcp_to_object_dist_end":0.4343,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1108.0,"raw_peak_contact_force":136.21061,"tcp_end":[0.61194,0.28583,0.31103],"tcp_start":[0.61145,0.28593,0.2863],"tcp_to_object_dist_end":0.44966,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":77.0,"average_failure_rate":0.32489,"average_mean_iterations":69.37131,"average_solve_count":237.0,"average_success_count":160.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_z":0.17208,"approach_goal.goal_arc_height":0.13313,"approach_object.approach_z":0.22137,"approach_object.arc_height":0.2596,"descend_at_goal.descend_goal_tolerance":0.02407,"descend_contact.contact_force":10.18205,"lift_object.lift_height":0.17611,"release_object.release_duration":1.17658,"retract_up.retract_height":0.32762},"optimized_scores":{"best_composite_score":-0.38189,"best_fitness_score":0.12311,"best_task_score":0.22017},"replay_outcomes":[{"contacts":{"omitted_contact_groups":3,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":102.0,"contact_point_centroid":[0.5602,0.05268,-0.00024],"force_p95":779.56467,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":849.4266,"mean_force":322.06062,"phase_index":5.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.60567,0.05285,0.28882]},{"body_a":"world","body_b":"link6","contact_count":889.0,"contact_point_centroid":[0.64465,0.15686,-0.00029],"force_p95":487.41367,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":723.98176,"mean_force":350.9076,"phase_index":6.0,"phase_name":"descend_at_goal","phase_type":"descend","tcp_position_centroid":[0.64942,0.15394,0.29398]},{"body_a":"world","body_b":"link6","contact_count":89.0,"contact_point_centroid":[0.66739,0.16767,-0.00013],"force_p95":78.12761,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":105.87306,"mean_force":54.97725,"phase_index":7.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.6573,0.15817,0.29425]},{"body_a":"grasp_target","body_b":"link6","contact_count":278.0,"contact_point_centroid":[0.55688,0.05341,0.01982],"force_p95":1.93383,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.53076,"mean_force":0.89844,"phase_index":5.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.60481,0.05693,0.29543]},{"body_a":"world","body_b":"grasp_target","contact_count":2233.0,"contact_point_centroid":[0.54885,0.03241,-0.00352],"force_p95":0.68711,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.48159,"mean_force":0.24131,"phase_index":5.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.61885,0.05935,0.31764]},{"body_a":"grasp_target","body_b":"link5","contact_count":900.0,"contact_point_centroid":[0.56996,0.05099,0.02951],"force_p95":0.31066,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.95692,"mean_force":0.23723,"phase_index":6.0,"phase_name":"descend_at_goal","phase_type":"descend","tcp_position_centroid":[0.64931,0.15389,0.294]},{"body_a":"world","body_b":"grasp_target","contact_count":3802.0,"contact_point_centroid":[0.55408,0.04427,-0.00279],"force_p95":0.35075,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.4598,"mean_force":0.17866,"phase_index":6.0,"phase_name":"descend_at_goal","phase_type":"descend","tcp_position_centroid":[0.64783,0.15308,0.29755]},{"body_a":"world","body_b":"grasp_target","contact_count":753.0,"contact_point_centroid":[0.55912,0.04618,-0.00266],"force_p95":0.33496,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.35055,"mean_force":0.15944,"phase_index":7.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.65739,0.15817,0.30014]},{"body_a":"grasp_target","body_b":"link5","contact_count":135.0,"contact_point_centroid":[0.58834,0.07116,0.02699],"force_p95":0.20153,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29361,"mean_force":0.17278,"phase_index":7.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.6573,0.15816,0.29519]},{"body_a":"world","body_b":"grasp_target","contact_count":3896.0,"contact_point_centroid":[0.54431,0.00113,-0.00196],"force_p95":0.12481,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12275,"phase_index":0.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.49908,-0.0,0.45329]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.79427,0.0724,0.42482]},{"body_a":"world","body_b":"grasp_target","contact_count":16.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":2.0,"phase_name":"descend_contact","phase_type":"contact","tcp_position_centroid":[0.8169,0.11908,0.37399]},{"body_a":"world","body_b":"grasp_target","contact_count":2200.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":3.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.81789,0.12265,0.35534]},{"body_a":"world","body_b":"grasp_target","contact_count":1320.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":4.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.56446,0.2723,0.28945]},{"body_a":"left_finger","body_b":"right_finger","contact_count":773.0,"contact_point_centroid":[0.81568,0.12242,0.35341],"force_p95":0.01291,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01423,"mean_force":0.01068,"phase_index":3.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.81775,0.1226,0.35289]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4301.0,"contact_point_centroid":[0.6483,0.15331,0.29512],"force_p95":0.01097,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01292,"mean_force":0.01037,"phase_index":6.0,"phase_name":"descend_at_goal","phase_type":"descend","tcp_position_centroid":[0.64812,0.15324,0.29738]}],"total_contact_groups":19},"final_pose_error":0.10329,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.55793,0.04475,0.01605],"final_tcp_position":[0.65744,0.15819,0.29393],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":273015.50538,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":975.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"retract_up","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3896.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.50045,2e-05,0.6087],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.58433,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_pregrasp","tcp_end":[0.81641,0.11844,0.37405],"tcp_start":[0.50045,2e-05,0.6087],"tcp_to_object_dist_end":0.45709,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":4.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":417.23035,"phase_name":"descend_contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":16.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_contact","tcp_end":[0.81833,0.12085,0.37401],"tcp_start":[0.81641,0.11844,0.37405],"tcp_to_object_dist_end":0.45882,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":2973.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_contact","tcp_end":[0.81775,0.1226,0.35288],"tcp_start":[0.81775,0.1226,0.35289],"tcp_to_object_dist_end":0.44313,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":330.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":2737.0,"raw_peak_contact_force":0.12263,"subtask_id":"lift_clear","tcp_end":[0.57945,0.09141,0.26379],"tcp_start":[0.81775,0.1226,0.35288],"tcp_to_object_dist_end":0.25675,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":595.0,"n_steps_budget":1000.0,"object_pos_end":[0.54911,0.04158,0.01602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.23223,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":273015.50538,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":5219.0,"raw_peak_contact_force":849.4266,"subtask_id":"place_goal","tcp_end":[0.63554,0.14506,0.35414],"tcp_start":[0.57945,0.09141,0.26379],"tcp_to_object_dist_end":0.36401,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.56171,0.0453,0.01445],"object_pos_start":[0.54911,0.04158,0.01602],"object_to_goal_dist_end":0.22652,"object_to_goal_dist_start":0.23223,"object_z_max":0.01602,"peak_contact_force":167951.73011,"phase_name":"descend_at_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":9892.0,"raw_peak_contact_force":723.98176,"subtask_id":"place_goal","tcp_end":[0.65744,0.15819,0.29393],"tcp_start":[0.63554,0.14506,0.35414],"tcp_to_object_dist_end":0.31625,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.55793,0.04475,0.01605],"object_pos_start":[0.56171,0.0453,0.01445],"object_to_goal_dist_end":0.22701,"object_to_goal_dist_start":0.22652,"object_z_max":0.01607,"peak_contact_force":0.12606,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1199.0,"raw_peak_contact_force":105.87306,"tcp_end":[0.65765,0.1582,0.3188],"tcp_start":[0.65744,0.15819,0.29393],"tcp_to_object_dist_end":0.33834,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":47.0,"average_failure_rate":0.21364,"average_mean_iterations":47.82273,"average_solve_count":220.0,"average_success_count":173.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_z":0.11243,"approach_goal.goal_arc_height":0.16918,"approach_object.approach_z":0.19548,"approach_object.arc_height":0.14962,"descend_at_goal.descend_goal_tolerance":0.02781,"descend_contact.contact_force":13.66805,"lift_object.lift_height":0.15094,"release_object.release_duration":0.7258,"retract_up.retract_height":0.26625},"optimized_scores":{"best_composite_score":-0.29574,"best_fitness_score":0.20926,"best_task_score":0.3869},"replay_outcomes":[{"contacts":{"omitted_contact_groups":11,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":710.0,"contact_point_centroid":[0.67203,-0.07069,-0.00025],"force_p95":320.39772,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1645.75543,"mean_force":259.16561,"phase_index":4.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.66591,-0.04497,0.28889]},{"body_a":"world","body_b":"hand","contact_count":118.0,"contact_point_centroid":[0.63,0.13446,-0.00409],"force_p95":1073.07971,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1592.95839,"mean_force":660.89806,"phase_index":4.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.65127,0.15436,-0.02334]},{"body_a":"world","body_b":"link5","contact_count":15.0,"contact_point_centroid":[0.4918,0.28356,-0.00225],"force_p95":902.49091,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1084.95738,"mean_force":339.85843,"phase_index":4.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.65187,0.13766,-0.0418]},{"body_a":"world","body_b":"link7","contact_count":9.0,"contact_point_centroid":[0.68572,0.03722,-0.00062],"force_p95":809.39376,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":835.95735,"mean_force":503.58403,"phase_index":4.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.67227,0.14584,0.11455]},{"body_a":"world","body_b":"link6","contact_count":645.0,"contact_point_centroid":[0.59997,0.1416,-0.00024],"force_p95":465.64047,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":577.0012,"mean_force":364.40094,"phase_index":5.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.60923,0.14918,0.29376]},{"body_a":"world","body_b":"link6","contact_count":996.0,"contact_point_centroid":[0.61779,0.15984,-0.00031],"force_p95":413.55616,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":526.64865,"mean_force":315.77363,"phase_index":6.0,"phase_name":"descend_at_goal","phase_type":"descend","tcp_position_centroid":[0.61309,0.16584,0.29402]},{"body_a":"world","body_b":"link6","contact_count":87.0,"contact_point_centroid":[0.63927,0.16806,-0.00013],"force_p95":79.06506,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":112.25361,"mean_force":55.96512,"phase_index":7.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.62012,0.17179,0.29393]},{"body_a":"world","body_b":"left_finger","contact_count":1741.0,"contact_point_centroid":[0.6483,0.15465,-0.03045],"force_p95":10.90823,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":58.34773,"mean_force":6.09663,"phase_index":4.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.65035,0.15695,-0.03249]},{"body_a":"world","body_b":"right_finger","contact_count":1733.0,"contact_point_centroid":[0.65183,0.15955,-0.03035],"force_p95":11.00129,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":56.9758,"mean_force":6.08773,"phase_index":4.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.65035,0.15692,-0.03264]},{"body_a":"grasp_target","body_b":"link6","contact_count":816.0,"contact_point_centroid":[0.53255,0.08717,0.03677],"force_p95":0.45302,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.17203,"mean_force":0.1915,"phase_index":5.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.60976,0.13125,0.29529]},{"body_a":"grasp_target","body_b":"link6","contact_count":52.0,"contact_point_centroid":[0.54862,0.01312,0.05622],"force_p95":0.48939,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.97229,"mean_force":0.15908,"phase_index":4.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.62128,-0.01191,0.29373]},{"body_a":"grasp_target","body_b":"link5","contact_count":989.0,"contact_point_centroid":[0.55515,0.10757,0.02971],"force_p95":0.21772,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.9668,"mean_force":0.1241,"phase_index":6.0,"phase_name":"descend_at_goal","phase_type":"descend","tcp_position_centroid":[0.613,0.16577,0.29403]},{"body_a":"grasp_target","body_b":"link6","contact_count":825.0,"contact_point_centroid":[0.54655,0.11372,0.03005],"force_p95":0.19622,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.88304,"mean_force":0.08517,"phase_index":6.0,"phase_name":"descend_at_goal","phase_type":"descend","tcp_position_centroid":[0.61179,0.16473,0.29407]},{"body_a":"world","body_b":"grasp_target","contact_count":2667.0,"contact_point_centroid":[0.5088,0.08921,-0.00421],"force_p95":0.58676,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.77619,"mean_force":0.27495,"phase_index":5.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.61039,0.11933,0.29829]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.5153,0.1067,-0.00255],"force_p95":0.29537,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.70157,"mean_force":0.16133,"phase_index":6.0,"phase_name":"descend_at_goal","phase_type":"descend","tcp_position_centroid":[0.61308,0.16584,0.29402]},{"body_a":"grasp_target","body_b":"link5","contact_count":684.0,"contact_point_centroid":[0.54018,0.08775,0.03433],"force_p95":0.30462,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.60694,"mean_force":0.17237,"phase_index":5.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.60908,0.14761,0.29399]}],"total_contact_groups":27},"final_pose_error":0.18657,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.51879,0.10812,0.01602],"final_tcp_position":[0.62019,0.17196,0.2936],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":9748.89381,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":784.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"retract_up","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3132.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.4999,1e-05,0.54721],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.52299,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_pregrasp","tcp_end":[0.81411,0.15222,0.31713],"tcp_start":[0.4999,1e-05,0.54721],"tcp_to_object_dist_end":0.42417,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":9.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":848.74428,"phase_name":"descend_contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":36.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_contact","tcp_end":[0.82435,0.15268,0.32136],"tcp_start":[0.81411,0.15222,0.31713],"tcp_to_object_dist_end":0.43408,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":9748.89381,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":2961.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_contact","tcp_end":[0.82524,0.15172,0.29067],"tcp_start":[0.82524,0.15172,0.29067],"tcp_to_object_dist_end":0.41417,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":11.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52877,0.0325,0.02493],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18317,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":230.40654,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":12708.0,"raw_peak_contact_force":1645.75543,"subtask_id":"lift_clear","tcp_end":[0.61777,-0.00787,0.29384],"tcp_start":[0.82524,0.15172,0.29067],"tcp_to_object_dist_end":0.28612,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":11.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51703,0.10714,0.01476],"object_pos_start":[0.52877,0.0325,0.02493],"object_to_goal_dist_end":0.14476,"object_to_goal_dist_start":0.18317,"object_z_max":0.02709,"peak_contact_force":335.30093,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":9134.0,"raw_peak_contact_force":577.0012,"subtask_id":"place_goal","tcp_end":[0.61191,0.16501,0.29429],"tcp_start":[0.61777,-0.00787,0.29384],"tcp_to_object_dist_end":0.30081,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51977,0.10884,0.01557],"object_pos_start":[0.51703,0.10714,0.01476],"object_to_goal_dist_end":0.14181,"object_to_goal_dist_start":0.14476,"object_z_max":0.01555,"peak_contact_force":324.79139,"phase_name":"descend_at_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":11097.0,"raw_peak_contact_force":526.64865,"subtask_id":"place_goal","tcp_end":[0.62019,0.17196,0.2936],"tcp_start":[0.61191,0.16501,0.29429],"tcp_to_object_dist_end":0.30227,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51879,0.10812,0.01602],"object_pos_start":[0.51977,0.10884,0.01557],"object_to_goal_dist_end":0.14244,"object_to_goal_dist_start":0.14181,"object_z_max":0.01605,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1109.0,"raw_peak_contact_force":112.25361,"tcp_end":[0.62039,0.17183,0.31926],"tcp_start":[0.62019,0.17196,0.2936],"tcp_to_object_dist_end":0.32609,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
```