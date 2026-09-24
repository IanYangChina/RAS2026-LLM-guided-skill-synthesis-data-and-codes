## Search State

- **Seed**: 3
- **Iteration**: 7 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 6 | approach → contact → grasp → lift → retract → approach → descend → release | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 9 | -0.3276 | 0.18 | ❌ rejected |
| 5 | approach → descend → contact → grasp → lift → approach → descend → release | arc_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 9 | -0.0332 | 0.21 | ❌ rejected |
| 4 | approach → descend → contact → grasp → lift → approach → descend → release | arc_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 9 | -0.3230 | 0.21 | ✅ accepted |
| 3 | approach → descend → grasp → lift → approach → descend → release → retract | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 9 | -0.4496 | 0.17 | ❌ rejected |
| 2 | approach → descend → grasp → lift → approach → descend → release → retract | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | position_control | force_threshold_switch | position_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 9 | -0.2003 | 0.21 | ✅ accepted |

**Proposal policy**: task_score is 0.18 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.328) — your mutation base

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

- **Composite score**: -0.328
- **task_score** (E): 0.185
- **fitness_score**: 0.177  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.125
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.630

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 0.00 | 1.00 | 0.1490 |
| touch_object_top | 1.00 | 1.00 | 0.0003 |
| grasp_object | 1.00 | 1.00 | 0.0000 |
| lift_object | 1.00 | 1.00 | 0.1172 |
| retract_upward | 0.00 | 1.00 | 0.1187 |
| approach_goal | 0.00 | 1.00 | 0.0009 |
| descend_at_goal | 0.00 | 1.00 | 0.2643 |
| release_object | 1.00 | 1.00 | 0.0254 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 0.00 / step_budget | (0.500, -0.000, 0.301)→(0.435, 0.032, 0.175) | (0.511, 0.002, 0.030)→(0.473, 0.005, 0.016) | 0.244→0.268 | 1.00 / 5.000 | 184.208 | 1392.672 |
| touch_object_top | contact | 1.00 / force_exceeded | (0.435, 0.032, 0.175)→(0.435, 0.032, 0.174) | (0.473, 0.005, 0.016)→(0.473, 0.005, 0.016) | 0.268→0.268 | 1.00 / 5.000 | 627.875 | 458.785 |
| grasp_object | grasp | 1.00 / step_budget | (0.435, 0.032, 0.173)→(0.435, 0.032, 0.173) | (0.473, 0.005, 0.016)→(0.473, 0.005, 0.016) | 0.268→0.268 | 1.00 / 9.333 | 91047.903 | 309.974 |
| lift_object | lift | 1.00 / step_budget | (0.432, 0.032, 0.324)→(0.433, 0.032, 0.441) | (0.473, 0.005, 0.016)→(0.473, 0.005, 0.016) | 0.268→0.268 | 1.00 / 8.333 | 91002.349 | 145.380 |
| retract_upward | retract | 0.00 / step_budget | (0.433, 0.032, 0.441)→(0.444, 0.040, 0.556) | (0.473, 0.005, 0.016)→(0.473, 0.005, 0.016) | 0.268→0.268 | 1.00 / 8.667 | 90982.629 | 120.738 |
| approach_goal | approach | 0.00 / guard_failure | (0.444, 0.040, 0.557)→(0.444, 0.039, 0.557) | (0.473, 0.005, 0.016)→(0.473, 0.005, 0.016) | 0.268→0.268 | 1.00 / 8.333 | 3346.123 | 96.521 |
| descend_at_goal | descend | 0.00 / step_budget | (0.444, 0.039, 0.557)→(0.507, 0.106, 0.323) | (0.473, 0.005, 0.016)→(0.478, 0.007, 0.016) | 0.268→0.264 | 1.00 / 9.000 | 299.880 | 529.151 |
| release_object | release | 1.00 / step_budget | (0.507, 0.106, 0.323)→(0.506, 0.105, 0.348) | (0.478, 0.007, 0.016)→(0.477, 0.006, 0.016) | 0.264→0.265 | 1.00 / 4.000 | 0.123 | 88.408 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 0.000
- place_accuracy: 0.000
- lift_clearance: 0.000
- transport_retention: 0.000
- terminal_score: 0.286
- phase_score: 0.322
- phase_breakdown.lift_clear_score: 0.001
- phase_breakdown.reach_pregrasp_score: 0.089
- phase_breakdown.grasp_contact_score: 1.000
- phase_breakdown.place_goal_score: 0.021
- grasp_place_fitness: 0.207

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.207
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.286
- **Median Q (composite search score)**: -0.339
- **K-run variance**: 0.0004
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.365


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":6.12409,"average_solve_count":137.0,"average_success_count":137.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_z":0.2102,"approach_goal.transport_speed":0.19627,"approach_object.approach_z":0.14982,"approach_object.arc_height":0.19759,"descend_at_goal.descend_goal_tolerance":0.01117,"lift_object.lift_height":0.18658,"release_object.release_duration":1.3859,"retract_upward.retract_distance":0.1554,"touch_object_top.contact_force":14.446},"optimized_scores":{"best_composite_score":-0.34522,"best_fitness_score":0.15978,"best_task_score":0.10897},"replay_outcomes":[{"contacts":{"omitted_contact_groups":4,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":887.0,"contact_point_centroid":[0.63231,0.00869,-0.00046],"force_p95":201.18557,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1320.46967,"mean_force":200.86832,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.38708,0.00739,0.11407]},{"body_a":"world","body_b":"link7","contact_count":24.0,"contact_point_centroid":[0.52508,0.01147,-0.00305],"force_p95":328.03353,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1263.91753,"mean_force":68.74331,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.37229,0.00625,0.0483]},{"body_a":"world","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.62828,0.00674,-0.00025],"force_p95":234.49188,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":234.49188,"mean_force":234.49188,"phase_index":1.0,"phase_name":"touch_object_top","phase_type":"contact","tcp_position_centroid":[0.39385,0.00495,0.13963]},{"body_a":"world","body_b":"link6","contact_count":550.0,"contact_point_centroid":[0.62883,0.00673,-0.00014],"force_p95":91.91356,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":181.5221,"mean_force":73.83312,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.39419,0.00499,0.13948]},{"body_a":"world","body_b":"link6","contact_count":4.0,"contact_point_centroid":[0.62902,0.0067,-0.00011],"force_p95":90.53239,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":90.80737,"mean_force":82.50615,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.39427,0.00496,0.13934]},{"body_a":"grasp_target","body_b":"hand","contact_count":40.0,"contact_point_centroid":[0.43862,-0.03702,0.04207],"force_p95":3.38255,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.75714,"mean_force":1.45875,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.38286,0.0063,0.04979]},{"body_a":"world","body_b":"grasp_target","contact_count":3920.0,"contact_point_centroid":[0.42256,-0.02768,-0.00213],"force_p95":0.13759,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.30743,"mean_force":0.13823,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.39935,0.0071,0.12465]},{"body_a":"world","body_b":"grasp_target","contact_count":4.0,"contact_point_centroid":[0.41755,-0.02788,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"touch_object_top","phase_type":"contact","tcp_position_centroid":[0.39385,0.00495,0.13963]},{"body_a":"world","body_b":"grasp_target","contact_count":2200.0,"contact_point_centroid":[0.41755,-0.02788,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.39419,0.00499,0.13948]},{"body_a":"world","body_b":"grasp_target","contact_count":3716.0,"contact_point_centroid":[0.41755,-0.02788,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.39319,0.00482,0.30026]},{"body_a":"world","body_b":"grasp_target","contact_count":3300.0,"contact_point_centroid":[0.41755,-0.02788,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":4.0,"phase_name":"retract_upward","phase_type":"retract","tcp_position_centroid":[0.39922,0.00578,0.51335]},{"body_a":"world","body_b":"grasp_target","contact_count":8.0,"contact_point_centroid":[0.41755,-0.02788,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.40761,0.00748,0.54116]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.41755,-0.02788,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"descend_at_goal","phase_type":"descend","tcp_position_centroid":[0.336,0.02601,0.41666]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.41755,-0.02788,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.34883,0.03947,0.38512]},{"body_a":"left_finger","body_b":"right_finger","contact_count":748.0,"contact_point_centroid":[0.39618,0.00498,0.13845],"force_p95":0.01295,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01566,"mean_force":0.01099,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.39427,0.00497,0.13933]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3913.0,"contact_point_centroid":[0.39507,0.00483,0.29981],"force_p95":0.01103,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01288,"mean_force":0.01057,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.39319,0.00482,0.30068]}],"total_contact_groups":20},"final_pose_error":0.42211,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.41755,-0.02788,0.01602],"final_tcp_position":[0.34976,0.03947,0.38075],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":273006.8025,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.41755,-0.02788,0.01602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.3325,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":199.95785,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4871.0,"raw_peak_contact_force":1320.46967,"subtask_id":"reach_pregrasp","tcp_end":[0.39385,0.00495,0.13963],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13007,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1.0,"n_steps_budget":660.0,"object_pos_end":[0.41755,-0.02788,0.01602],"object_pos_start":[0.41755,-0.02788,0.01602],"object_to_goal_dist_end":0.3325,"object_to_goal_dist_start":0.3325,"object_z_max":0.01602,"peak_contact_force":741.7615,"phase_name":"touch_object_top","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":5.0,"raw_peak_contact_force":234.49188,"subtask_id":"grasp_contact","tcp_end":[0.39384,0.00505,0.13966],"tcp_start":[0.39385,0.00495,0.13963],"tcp_to_object_dist_end":0.13013,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.41755,-0.02788,0.01602],"object_pos_start":[0.41755,-0.02788,0.01602],"object_to_goal_dist_end":0.3325,"object_to_goal_dist_start":0.3325,"object_z_max":0.01602,"peak_contact_force":273004.12069,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":3498.0,"raw_peak_contact_force":181.5221,"subtask_id":"grasp_contact","tcp_end":[0.39428,0.00496,0.13932],"tcp_start":[0.39427,0.00496,0.13932],"tcp_to_object_dist_end":0.1297,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":929.0,"n_steps_budget":1000.0,"object_pos_end":[0.41755,-0.02788,0.01602],"object_pos_start":[0.41755,-0.02788,0.01602],"object_to_goal_dist_end":0.3325,"object_to_goal_dist_start":0.3325,"object_z_max":0.01602,"peak_contact_force":273006.8025,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":7633.0,"raw_peak_contact_force":90.80737,"subtask_id":"lift_clear","tcp_end":[0.39462,0.00482,0.47283],"tcp_start":[0.39342,0.00486,0.30602],"tcp_to_object_dist_end":0.45856,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":825.0,"n_steps_budget":990.0,"object_pos_end":[0.41755,-0.02788,0.01602],"object_pos_start":[0.41755,-0.02788,0.01602],"object_to_goal_dist_end":0.3325,"object_to_goal_dist_start":0.3325,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_upward","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":6802.0,"raw_peak_contact_force":0.12263,"subtask_id":"lift_clear","tcp_end":[0.40769,0.00746,0.54114],"tcp_start":[0.39462,0.00482,0.47283],"tcp_to_object_dist_end":0.5264,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":2.0,"n_steps_budget":1000.0,"object_pos_end":[0.41755,-0.02788,0.01602],"object_pos_start":[0.41755,-0.02788,0.01602],"object_to_goal_dist_end":0.3325,"object_to_goal_dist_start":0.3325,"object_z_max":0.01602,"peak_contact_force":9748.92689,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":17.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_goal","tcp_end":[0.4072,0.00746,0.54124],"tcp_start":[0.40753,0.0075,0.54119],"tcp_to_object_dist_end":0.52651,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.41755,-0.02788,0.01602],"object_pos_start":[0.41755,-0.02788,0.01602],"object_to_goal_dist_end":0.3325,"object_to_goal_dist_start":0.3325,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_at_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8198.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_goal","tcp_end":[0.34976,0.03947,0.38075],"tcp_start":[0.4072,0.00746,0.54124],"tcp_to_object_dist_end":0.37704,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.41755,-0.02788,0.01602],"object_pos_start":[0.41755,-0.02788,0.01602],"object_to_goal_dist_end":0.3325,"object_to_goal_dist_start":0.3325,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1029.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.34667,0.03942,0.40311],"tcp_start":[0.34976,0.03947,0.38075],"tcp_to_object_dist_end":0.39924,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":5.22115,"average_solve_count":208.0,"average_success_count":208.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_z":0.18585,"approach_goal.transport_speed":0.20656,"approach_object.approach_z":0.14945,"approach_object.arc_height":0.086,"descend_at_goal.descend_goal_tolerance":0.02476,"lift_object.lift_height":0.18946,"release_object.release_duration":1.47212,"retract_upward.retract_distance":0.24198,"touch_object_top.contact_force":9.94697},"optimized_scores":{"best_composite_score":-0.3392,"best_fitness_score":0.1658,"best_task_score":0.1594},"replay_outcomes":[{"contacts":{"omitted_contact_groups":11,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":859.0,"contact_point_centroid":[0.64021,0.03957,-0.00042],"force_p95":410.20243,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1415.8972,"mean_force":255.57144,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.42394,0.0376,0.16276]},{"body_a":"world","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.67942,0.03645,-8e-05],"force_p95":915.32115,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":915.32115,"mean_force":915.32115,"phase_index":1.0,"phase_name":"touch_object_top","phase_type":"contact","tcp_position_centroid":[0.46416,0.04398,0.16776]},{"body_a":"world","body_b":"link6","contact_count":92.0,"contact_point_centroid":[0.59787,0.11318,-0.00033],"force_p95":765.51435,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":783.04835,"mean_force":544.94627,"phase_index":6.0,"phase_name":"descend_at_goal","phase_type":"descend","tcp_position_centroid":[0.60879,0.12903,0.29312]},{"body_a":"world","body_b":"link7","contact_count":21.0,"contact_point_centroid":[0.53305,0.02149,-0.00317],"force_p95":0.0,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":441.23769,"mean_force":21.01132,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.37949,0.02231,0.05038]},{"body_a":"link5","body_b":"hand","contact_count":89.0,"contact_point_centroid":[0.42162,-0.03015,0.55878],"force_p95":272.84225,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":367.05228,"mean_force":225.76486,"phase_index":6.0,"phase_name":"descend_at_goal","phase_type":"descend","tcp_position_centroid":[0.42233,0.01242,0.64375]},{"body_a":"link5","body_b":"hand","contact_count":567.0,"contact_point_centroid":[0.5101,-0.02724,0.5352],"force_p95":339.7863,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":361.9679,"mean_force":299.08179,"phase_index":4.0,"phase_name":"retract_upward","phase_type":"retract","tcp_position_centroid":[0.47619,0.04537,0.5592]},{"body_a":"link5","body_b":"hand","contact_count":2.0,"contact_point_centroid":[0.50347,-0.03733,0.55619],"force_p95":289.30849,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":289.3185,"mean_force":289.21838,"phase_index":5.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.46689,0.02736,0.61668]},{"body_a":"world","body_b":"link6","contact_count":550.0,"contact_point_centroid":[0.68146,0.0356,-0.00013],"force_p95":76.83641,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":249.33362,"mean_force":70.12445,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.46393,0.0433,0.16469]},{"body_a":"world","body_b":"link6","contact_count":5.0,"contact_point_centroid":[0.68154,0.03553,-0.0001],"force_p95":190.55971,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":196.82054,"mean_force":117.60161,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46391,0.04334,0.16462]},{"body_a":"world","body_b":"link6","contact_count":83.0,"contact_point_centroid":[0.59635,0.12758,-0.00011],"force_p95":75.06367,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":145.83419,"mean_force":55.53175,"phase_index":7.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.61324,0.13202,0.29375]},{"body_a":"grasp_target","body_b":"link6","contact_count":135.0,"contact_point_centroid":[0.54239,0.0157,0.02655],"force_p95":0.83073,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.5105,"mean_force":0.47369,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.38928,0.02409,0.09483]},{"body_a":"grasp_target","body_b":"link7","contact_count":195.0,"contact_point_centroid":[0.51322,0.00028,0.03928],"force_p95":2.89059,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.12318,"mean_force":0.65655,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.3936,0.02481,0.09991]},{"body_a":"world","body_b":"grasp_target","contact_count":3630.0,"contact_point_centroid":[0.51096,0.00098,-0.00221],"force_p95":0.30319,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.10214,"mean_force":0.15261,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.43742,0.03657,0.17444]},{"body_a":"grasp_target","body_b":"hand","contact_count":128.0,"contact_point_centroid":[0.49701,-0.00391,0.04924],"force_p95":2.37821,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.89369,"mean_force":0.97272,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.3902,0.0237,0.08754]},{"body_a":"world","body_b":"grasp_target","contact_count":4.0,"contact_point_centroid":[0.50473,0.00061,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"touch_object_top","phase_type":"contact","tcp_position_centroid":[0.46416,0.04398,0.16776]},{"body_a":"world","body_b":"grasp_target","contact_count":2200.0,"contact_point_centroid":[0.50473,0.00061,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.46393,0.0433,0.16469]}],"total_contact_groups":27},"final_pose_error":0.11141,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.50473,0.00061,0.01602],"final_tcp_position":[0.61328,0.13211,0.29386],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":272947.64087,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50473,0.00061,0.01602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.27545,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.0,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4968.0,"raw_peak_contact_force":1415.8972,"subtask_id":"reach_pregrasp","tcp_end":[0.46416,0.04398,0.16776],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16295,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1.0,"n_steps_budget":870.0,"object_pos_end":[0.50473,0.00061,0.01602],"object_pos_start":[0.50473,0.00061,0.01602],"object_to_goal_dist_end":0.27545,"object_to_goal_dist_start":0.27545,"object_z_max":0.01602,"peak_contact_force":915.32115,"phase_name":"touch_object_top","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":5.0,"raw_peak_contact_force":915.32115,"subtask_id":"grasp_contact","tcp_end":[0.46413,0.04372,0.16696],"tcp_start":[0.46416,0.04398,0.16776],"tcp_to_object_dist_end":0.16214,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.50473,0.00061,0.01602],"object_pos_start":[0.50473,0.00061,0.01602],"object_to_goal_dist_end":0.27545,"object_to_goal_dist_start":0.27545,"object_z_max":0.01602,"peak_contact_force":67.53452,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":3526.0,"raw_peak_contact_force":249.33362,"subtask_id":"grasp_contact","tcp_end":[0.46392,0.04332,0.1646],"tcp_start":[0.46392,0.04331,0.1646],"tcp_to_object_dist_end":0.15989,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1438.0,"n_steps_budget":1000.0,"object_pos_end":[0.50473,0.00061,0.01602],"object_pos_start":[0.50473,0.00061,0.01602],"object_to_goal_dist_end":0.27545,"object_to_goal_dist_start":0.27545,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":12004.0,"raw_peak_contact_force":196.82054,"subtask_id":"lift_clear","tcp_end":[0.47111,0.04033,0.4282],"tcp_start":[0.46307,0.04282,0.33407],"tcp_to_object_dist_end":0.41546,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50473,0.00061,0.01602],"object_pos_start":[0.50473,0.00061,0.01602],"object_to_goal_dist_end":0.27545,"object_to_goal_dist_start":0.27545,"object_z_max":0.01602,"peak_contact_force":272947.64087,"phase_name":"retract_upward","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":8980.0,"raw_peak_contact_force":361.9679,"subtask_id":"lift_clear","tcp_end":[0.46694,0.02748,0.61655],"tcp_start":[0.47111,0.04033,0.4282],"tcp_to_object_dist_end":0.60231,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":2.0,"n_steps_budget":1000.0,"object_pos_end":[0.50473,0.00061,0.01602],"object_pos_start":[0.50473,0.00061,0.01602],"object_to_goal_dist_end":0.27545,"object_to_goal_dist_start":0.27545,"object_z_max":0.01602,"peak_contact_force":289.3185,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":19.0,"raw_peak_contact_force":289.3185,"subtask_id":"place_goal","tcp_end":[0.46664,0.02683,0.61724],"tcp_start":[0.46683,0.02725,0.61682],"tcp_to_object_dist_end":0.603,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50473,0.00061,0.01602],"object_pos_start":[0.50473,0.00061,0.01602],"object_to_goal_dist_end":0.27545,"object_to_goal_dist_start":0.27545,"object_z_max":0.01602,"peak_contact_force":451.87423,"phase_name":"descend_at_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8529.0,"raw_peak_contact_force":783.04835,"subtask_id":"place_goal","tcp_end":[0.61328,0.13211,0.29386],"tcp_start":[0.46664,0.02683,0.61724],"tcp_to_object_dist_end":0.32599,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50473,0.00061,0.01602],"object_pos_start":[0.50473,0.00061,0.01602],"object_to_goal_dist_end":0.27545,"object_to_goal_dist_start":0.27545,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1106.0,"raw_peak_contact_force":145.83419,"tcp_end":[0.61345,0.13172,0.31996],"tcp_start":[0.61328,0.13211,0.29386],"tcp_to_object_dist_end":0.34841,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":5.61364,"average_solve_count":176.0,"average_success_count":176.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_z":0.18087,"approach_goal.transport_speed":0.06118,"approach_object.approach_z":0.12084,"approach_object.arc_height":0.19543,"descend_at_goal.descend_goal_tolerance":0.01635,"lift_object.lift_height":0.15166,"release_object.release_duration":1.46495,"retract_upward.retract_distance":0.22529,"touch_object_top.contact_force":9.41268},"optimized_scores":{"best_composite_score":-0.29843,"best_fitness_score":0.20657,"best_task_score":0.28625},"replay_outcomes":[{"contacts":{"omitted_contact_groups":13,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":882.0,"contact_point_centroid":[0.63387,0.03176,-0.00044],"force_p95":274.07728,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1441.64842,"mean_force":224.11773,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.4132,0.02927,0.15484]},{"body_a":"world","body_b":"link6","contact_count":440.0,"contact_point_centroid":[0.53906,0.13513,-0.00033],"force_p95":676.07695,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":804.2822,"mean_force":507.52174,"phase_index":6.0,"phase_name":"descend_at_goal","phase_type":"descend","tcp_position_centroid":[0.54782,0.14103,0.29354]},{"body_a":"link5","body_b":"hand","contact_count":7.0,"contact_point_centroid":[0.44476,-0.01083,0.48646],"force_p95":621.21621,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":638.10443,"mean_force":513.12315,"phase_index":6.0,"phase_name":"descend_at_goal","phase_type":"descend","tcp_position_centroid":[0.4656,0.07714,0.53617]},{"body_a":"world","body_b":"link6","contact_count":548.0,"contact_point_centroid":[0.62902,0.03907,-0.00013],"force_p95":81.23016,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":499.06618,"mean_force":76.33245,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.44798,0.04648,0.21601]},{"body_a":"world","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.62799,0.03985,-0.00028],"force_p95":226.54165,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":226.54165,"mean_force":226.54165,"phase_index":1.0,"phase_name":"touch_object_top","phase_type":"contact","tcp_position_centroid":[0.44804,0.04695,0.21664]},{"body_a":"world","body_b":"link6","contact_count":4.0,"contact_point_centroid":[0.62914,0.03899,-0.00011],"force_p95":145.58258,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":148.51149,"mean_force":114.74539,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.44799,0.04643,0.21597]},{"body_a":"world","body_b":"link6","contact_count":82.0,"contact_point_centroid":[0.55731,0.14341,-0.00013],"force_p95":78.81289,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":119.26683,"mean_force":57.66206,"phase_index":7.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.55735,0.14527,0.29422]},{"body_a":"grasp_target","body_b":"link7","contact_count":229.0,"contact_point_centroid":[0.51356,0.02665,0.03227],"force_p95":3.33226,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.85174,"mean_force":0.54534,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.39205,0.01752,0.10021]},{"body_a":"grasp_target","body_b":"hand","contact_count":103.0,"contact_point_centroid":[0.49265,0.04352,0.04769],"force_p95":2.44443,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.87698,"mean_force":0.95984,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.38759,0.01613,0.07968]},{"body_a":"world","body_b":"grasp_target","contact_count":3745.0,"contact_point_centroid":[0.50195,0.04005,-0.00226],"force_p95":0.31766,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.09225,"mean_force":0.15807,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.42501,0.02795,0.16438]},{"body_a":"grasp_target","body_b":"link6","contact_count":460.0,"contact_point_centroid":[0.49501,0.07418,0.02964],"force_p95":0.31475,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.5689,"mean_force":0.21667,"phase_index":6.0,"phase_name":"descend_at_goal","phase_type":"descend","tcp_position_centroid":[0.54718,0.14066,0.29372]},{"body_a":"grasp_target","body_b":"link5","contact_count":451.0,"contact_point_centroid":[0.52636,0.02616,0.03331],"force_p95":0.28345,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.16498,"mean_force":0.21645,"phase_index":6.0,"phase_name":"descend_at_goal","phase_type":"descend","tcp_position_centroid":[0.54749,0.14085,0.29359]},{"body_a":"world","body_b":"grasp_target","contact_count":3590.0,"contact_point_centroid":[0.50214,0.04304,-0.0028],"force_p95":0.50837,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.03904,"mean_force":0.18393,"phase_index":6.0,"phase_name":"descend_at_goal","phase_type":"descend","tcp_position_centroid":[0.51281,0.11711,0.37634]},{"body_a":"grasp_target","body_b":"link6","contact_count":103.0,"contact_point_centroid":[0.53862,0.04523,0.02723],"force_p95":0.74899,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.91337,"mean_force":0.40141,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.38564,0.01637,0.0877]},{"body_a":"world","body_b":"grasp_target","contact_count":689.0,"contact_point_centroid":[0.51387,0.04524,-0.00275],"force_p95":0.39275,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.4318,"mean_force":0.16756,"phase_index":7.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.5574,0.14515,0.30188]},{"body_a":"grasp_target","body_b":"link5","contact_count":103.0,"contact_point_centroid":[0.54177,0.03724,0.032],"force_p95":0.17392,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17439,"mean_force":0.15817,"phase_index":7.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.55733,0.14523,0.29445]}],"total_contact_groups":29},"final_pose_error":0.19382,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.50892,0.04385,0.01603],"final_tcp_position":[0.5573,0.14551,0.29387],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":1441.64842,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49622,0.04183,0.01602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.19562,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":352.66657,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":5083.0,"raw_peak_contact_force":1441.64842,"subtask_id":"reach_pregrasp","tcp_end":[0.44804,0.04695,0.21664],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.20639,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.49622,0.04183,0.01602],"object_pos_start":[0.49622,0.04183,0.01602],"object_to_goal_dist_end":0.19562,"object_to_goal_dist_start":0.19562,"object_z_max":0.01602,"peak_contact_force":226.54165,"phase_name":"touch_object_top","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":5.0,"raw_peak_contact_force":226.54165,"subtask_id":"grasp_contact","tcp_end":[0.44801,0.04693,0.21666],"tcp_start":[0.44804,0.04695,0.21664],"tcp_to_object_dist_end":0.20641,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.49622,0.04183,0.01602],"object_pos_start":[0.49622,0.04183,0.01602],"object_to_goal_dist_end":0.19562,"object_to_goal_dist_start":0.19562,"object_z_max":0.01602,"peak_contact_force":72.05347,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":3494.0,"raw_peak_contact_force":499.06618,"subtask_id":"grasp_contact","tcp_end":[0.44799,0.04644,0.21593],"tcp_start":[0.44799,0.04644,0.21593],"tcp_to_object_dist_end":0.2057,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1488.0,"n_steps_budget":960.0,"object_pos_end":[0.49622,0.04183,0.01602],"object_pos_start":[0.49622,0.04183,0.01602],"object_to_goal_dist_end":0.19562,"object_to_goal_dist_start":0.19562,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":12251.0,"raw_peak_contact_force":148.51149,"subtask_id":"lift_clear","tcp_end":[0.43211,0.05087,0.42293],"tcp_start":[0.44001,0.04725,0.33319],"tcp_to_object_dist_end":0.41203,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49622,0.04183,0.01602],"object_pos_start":[0.49622,0.04183,0.01602],"object_to_goal_dist_end":0.19562,"object_to_goal_dist_start":0.19562,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_upward","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":8246.0,"raw_peak_contact_force":0.12263,"subtask_id":"lift_clear","tcp_end":[0.45814,0.0847,0.51064],"tcp_start":[0.43211,0.05087,0.42293],"tcp_to_object_dist_end":0.49793,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":2.0,"n_steps_budget":1000.0,"object_pos_end":[0.49622,0.04183,0.01602],"object_pos_start":[0.49622,0.04183,0.01602],"object_to_goal_dist_end":0.19562,"object_to_goal_dist_start":0.19562,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":16.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_goal","tcp_end":[0.45773,0.08309,0.51362],"tcp_start":[0.45797,0.08388,0.5121],"tcp_to_object_dist_end":0.50079,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51247,0.04804,0.01505],"object_pos_start":[0.49622,0.04183,0.01602],"object_to_goal_dist_end":0.18338,"object_to_goal_dist_start":0.19562,"object_z_max":0.01602,"peak_contact_force":447.6446,"phase_name":"descend_at_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":9252.0,"raw_peak_contact_force":804.2822,"subtask_id":"place_goal","tcp_end":[0.5573,0.14551,0.29387],"tcp_start":[0.45773,0.08309,0.51362],"tcp_to_object_dist_end":0.29876,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50892,0.04385,0.01603],"object_pos_start":[0.51247,0.04804,0.01505],"object_to_goal_dist_end":0.18763,"object_to_goal_dist_start":0.18338,"object_z_max":0.01606,"peak_contact_force":0.12286,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1191.0,"raw_peak_contact_force":119.26683,"tcp_end":[0.55756,0.14508,0.32137],"tcp_start":[0.5573,0.14551,0.29387],"tcp_to_object_dist_end":0.32535,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
```