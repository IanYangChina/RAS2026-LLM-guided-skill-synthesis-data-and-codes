## Search State

- **Seed**: 3
- **Iteration**: 6 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 5 | approach → descend → contact → grasp → lift → approach → descend → release | arc_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 9 | -0.0332 | 0.21 | ❌ rejected |
| 4 | approach → descend → contact → grasp → lift → approach → descend → release | arc_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 9 | -0.3230 | 0.21 | ✅ accepted |
| 3 | approach → descend → grasp → lift → approach → descend → release → retract | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 9 | -0.4496 | 0.17 | ❌ rejected |
| 2 | approach → descend → grasp → lift → approach → descend → release → retract | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | position_control | force_threshold_switch | position_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 9 | -0.2003 | 0.21 | ✅ accepted |
| 1 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | admittance_control | position_control | position_control | position_control | admittance_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | contact_detected | time_limit | pose_tolerance | 7 | -0.3656 | 0.19 | ✅ accepted |

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

## Current Skill (Q=-0.033) — your mutation base

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

- **Composite score**: -0.033
- **task_score** (E): 0.207
- **fitness_score**: 0.472  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.125
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.630

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1016 |
| descend_to_contact | 1.00 | 1.00 | 0.1448 |
| touch_object_surface | 1.00 | 1.00 | 0.0010 |
| grasp_object | 1.00 | 1.00 | 0.0119 |
| lift_object | 1.00 | 1.00 | 0.1004 |
| approach_goal | 1.00 | 1.00 | 0.2297 |
| descend_to_place | 1.00 | 1.00 | 0.1138 |
| release_object | 1.00 | 1.00 | 0.0195 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.505, 0.009, 0.210) | (0.511, 0.002, 0.030)→(0.511, 0.002, 0.026) | 0.244→0.246 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_to_contact | descend | 1.00 / step_budget | (0.505, 0.009, 0.210)→(0.506, 0.002, 0.065) | (0.511, 0.002, 0.026)→(0.511, 0.002, 0.026) | 0.246→0.246 | 1.00 / 4.000 | 0.123 | 0.123 |
| touch_object_surface | contact | 1.00 / force_exceeded | (0.506, 0.002, 0.065)→(0.506, 0.002, 0.064) | (0.511, 0.002, 0.026)→(0.511, 0.002, 0.026) | 0.246→0.246 | 1.00 / 4.000 | 81.142 | 0.123 |
| grasp_object | grasp | 1.00 / step_budget | (0.506, 0.002, 0.064)→(0.498, 0.002, 0.055) | (0.511, 0.002, 0.026)→(0.511, 0.002, 0.026) | 0.246→0.246 | 1.00 / 27.333 | 0.156 | 0.181 |
| lift_object | lift | 1.00 / step_budget | (0.498, 0.002, 0.055)→(0.506, 0.002, 0.155) | (0.511, 0.002, 0.026)→(0.507, 0.009, 0.083) | 0.246→0.222 | 1.00 / 14.333 | 91001.705 | 0.398 |
| approach_goal | approach | 1.00 / step_budget | (0.506, 0.002, 0.155)→(0.615, 0.166, 0.269) | (0.507, 0.009, 0.083)→(0.519, 0.004, 0.016) | 0.222→0.247 | 1.00 / 8.667 | 182010.967 | 0.937 |
| descend_to_place | descend | 1.00 / step_budget | (0.615, 0.166, 0.269)→(0.621, 0.177, 0.156) | (0.519, 0.004, 0.016)→(0.519, 0.004, 0.016) | 0.247→0.247 | 1.00 / 8.000 | 6499.173 | 0.123 |
| release_object | release | 1.00 / step_budget | (0.621, 0.177, 0.156)→(0.614, 0.175, 0.174) | (0.519, 0.004, 0.016)→(0.519, 0.004, 0.016) | 0.247→0.247 | 1.00 / 4.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: 0.000
- terminal_score: 0.319
- phase_score: 0.620
- phase_breakdown.lift_clear_score: 0.592
- phase_breakdown.reach_pregrasp_score: 0.268
- phase_breakdown.grasp_contact_score: 1.000
- phase_breakdown.place_goal_score: 0.446
- grasp_place_fitness: 0.612

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.612
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.319
- **Median Q (composite search score)**: 0.032
- **K-run variance**: 0.0220
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Parameters at lower bound**: descend_to_contact.descend_z
- **Final σ (mean)**: 0.377


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.84324,"average_solve_count":185.0,"average_success_count":185.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_z":0.15844,"approach_goal.goal_arc_height":0.06436,"approach_object.approach_z":0.17999,"approach_object.arc_height":0.13127,"descend_to_contact.descend_z":0.03136,"descend_to_place.descend_goal_tolerance":0.02485,"lift_object.lift_height":0.14368,"release_object.release_duration":1.27481,"touch_object_surface.contact_force":13.34496},"optimized_scores":{"best_composite_score":-0.23842,"best_fitness_score":0.26658,"best_task_score":0.13573},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1792.0,"contact_point_centroid":[0.44449,-0.00893,-0.00222],"force_p95":0.3092,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.56742,"mean_force":0.13774,"phase_index":4.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.44993,-0.02571,0.11989]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1601.0,"contact_point_centroid":[0.44491,-0.00705,0.06418],"force_p95":0.14883,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26124,"mean_force":0.09565,"phase_index":4.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.44504,-0.02568,0.06871]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1873.0,"contact_point_centroid":[0.44522,-0.04405,0.06505],"force_p95":0.1256,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2558,"mean_force":0.08118,"phase_index":4.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.44507,-0.02568,0.06953]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45858,-0.02628,-0.00204],"force_p95":0.13604,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.1701,"mean_force":0.12573,"phase_index":3.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.44763,-0.02582,0.05922]},{"body_a":"world","body_b":"grasp_target","contact_count":680.0,"contact_point_centroid":[0.45856,-0.02632,-0.00181],"force_p95":0.13762,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12335,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.47481,-0.01514,0.27003]},{"body_a":"world","body_b":"grasp_target","contact_count":2088.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.45515,-0.02563,0.14706]},{"body_a":"world","body_b":"grasp_target","contact_count":24.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":2.0,"phase_name":"touch_object_surface","phase_type":"contact","tcp_position_centroid":[0.45413,-0.02607,0.06581]},{"body_a":"world","body_b":"grasp_target","contact_count":3760.0,"contact_point_centroid":[0.44306,-0.0042,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.5226,0.06818,0.24625]},{"body_a":"world","body_b":"grasp_target","contact_count":944.0,"contact_point_centroid":[0.44306,-0.0042,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.62015,0.19835,0.2024]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.44306,-0.0042,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.61894,0.20242,0.13064]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2671.0,"contact_point_centroid":[0.44621,-0.00703,0.05391],"force_p95":0.09686,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10186,"mean_force":0.07623,"phase_index":3.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.44659,-0.02578,0.05818]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2947.0,"contact_point_centroid":[0.44642,-0.04446,0.05388],"force_p95":0.09189,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09201,"mean_force":0.06983,"phase_index":3.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.44659,-0.02578,0.05819]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1415.0,"contact_point_centroid":[0.45134,-0.02573,0.13358],"force_p95":0.01222,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0165,"mean_force":0.01083,"phase_index":4.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.45102,-0.02572,0.13127]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4004.0,"contact_point_centroid":[0.52334,0.06867,0.24888],"force_p95":0.01099,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0129,"mean_force":0.01046,"phase_index":5.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.52297,0.06867,0.2466]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1000.0,"contact_point_centroid":[0.62059,0.19833,0.20496],"force_p95":0.01102,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01279,"mean_force":0.01051,"phase_index":6.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.62013,0.19832,0.20282]},{"body_a":"left_finger","body_b":"right_finger","contact_count":220.0,"contact_point_centroid":[0.62214,0.20354,0.12907],"force_p95":0.01097,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01099,"mean_force":0.01013,"phase_index":7.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.62181,0.20352,0.12692]}],"total_contact_groups":16},"final_pose_error":0.01952,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.44306,-0.0042,0.01602],"final_tcp_position":[0.62425,0.20422,0.1323],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":273015.75298,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":171.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":680.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_pregrasp","tcp_end":[0.45819,-0.02531,0.22993],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.20391,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":522.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2088.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_pregrasp","tcp_end":[0.4545,-0.02607,0.06629],"tcp_start":[0.45819,-0.02531,0.22993],"tcp_to_object_dist_end":0.04047,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":6.0,"n_steps_budget":600.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":81.14225,"phase_name":"touch_object_surface","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":24.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_contact","tcp_end":[0.45374,-0.02605,0.0653],"tcp_start":[0.4545,-0.02607,0.06629],"tcp_to_object_dist_end":0.03958,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":27.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.4585,-0.02593,0.02585],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30343,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.13537,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":7418.0,"raw_peak_contact_force":0.1701,"subtask_id":"grasp_contact","tcp_end":[0.44656,-0.02578,0.05816],"tcp_start":[0.45374,-0.02605,0.0653],"tcp_to_object_dist_end":0.03444,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":633.0,"n_steps_budget":720.0,"object_pos_end":[0.44306,-0.0042,0.01602],"object_pos_start":[0.4585,-0.02593,0.02585],"object_to_goal_dist_end":0.29956,"object_to_goal_dist_start":0.30343,"object_z_max":0.04386,"peak_contact_force":273004.82088,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":6681.0,"raw_peak_contact_force":0.56742,"subtask_id":"lift_clear","tcp_end":[0.45417,-0.02576,0.1584],"tcp_start":[0.44656,-0.02578,0.05816],"tcp_to_object_dist_end":0.14443,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":940.0,"n_steps_budget":1000.0,"object_pos_end":[0.44306,-0.0042,0.01602],"object_pos_start":[0.44306,-0.0042,0.01602],"object_to_goal_dist_end":0.29956,"object_to_goal_dist_start":0.29956,"object_z_max":0.01602,"peak_contact_force":273015.75298,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":7764.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_goal","tcp_end":[0.61742,0.19317,0.27009],"tcp_start":[0.45417,-0.02576,0.1584],"tcp_to_object_dist_end":0.36593,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":236.0,"n_steps_budget":1000.0,"object_pos_end":[0.44306,-0.0042,0.01602],"object_pos_start":[0.44306,-0.0042,0.01602],"object_to_goal_dist_end":0.29956,"object_to_goal_dist_start":0.29956,"object_z_max":0.01602,"peak_contact_force":9748.56203,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1944.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_goal","tcp_end":[0.62425,0.20422,0.1323],"tcp_start":[0.61742,0.19317,0.27009],"tcp_to_object_dist_end":0.29965,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.44306,-0.0042,0.01602],"object_pos_start":[0.44306,-0.0042,0.01602],"object_to_goal_dist_end":0.29956,"object_to_goal_dist_start":0.29956,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1020.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_goal","tcp_end":[0.61716,0.20173,0.15002],"tcp_start":[0.62425,0.20422,0.1323],"tcp_to_object_dist_end":0.30113,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.96855,"average_solve_count":159.0,"average_success_count":159.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_z":0.10662,"approach_goal.goal_arc_height":0.10246,"approach_object.approach_z":0.17062,"approach_object.arc_height":0.13777,"descend_to_contact.descend_z":0.03,"descend_to_place.descend_goal_tolerance":0.00884,"lift_object.lift_height":0.14012,"release_object.release_duration":0.59089,"touch_object_surface.contact_force":11.71947},"optimized_scores":{"best_composite_score":0.03152,"best_fitness_score":0.53652,"best_task_score":0.16594},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":3151.0,"contact_point_centroid":[0.56108,-0.02744,-0.00225],"force_p95":0.12884,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.4292,"mean_force":0.13778,"phase_index":5.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.56365,0.03954,0.27835]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5484.0,"contact_point_centroid":[0.5355,0.01981,0.0929],"force_p95":0.14146,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27946,"mean_force":0.10719,"phase_index":4.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.53187,0.00158,0.0961]},{"body_a":"world","body_b":"grasp_target","contact_count":152.0,"contact_point_centroid":[0.543,0.00183,-0.00115],"force_p95":0.21346,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.27574,"mean_force":0.04637,"phase_index":4.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.52858,0.00168,0.05484]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5926.0,"contact_point_centroid":[0.53578,-0.01654,0.09494],"force_p95":0.13497,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26602,"mean_force":0.09931,"phase_index":4.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.53217,0.00158,0.0984]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":60.0,"contact_point_centroid":[0.54564,0.01923,0.14832],"force_p95":0.22203,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25437,"mean_force":0.14844,"phase_index":5.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.53878,0.00129,0.15354]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":149.0,"contact_point_centroid":[0.54419,-0.01586,0.15023],"force_p95":0.17505,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21026,"mean_force":0.08078,"phase_index":5.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.5379,0.00075,0.1547]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54432,0.00119,-0.00205],"force_p95":0.13875,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17291,"mean_force":0.12674,"phase_index":3.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.53098,0.00174,0.05451]},{"body_a":"world","body_b":"grasp_target","contact_count":792.0,"contact_point_centroid":[0.54431,0.00113,-0.00184],"force_p95":0.13742,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12324,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51509,0.01343,0.25866]},{"body_a":"world","body_b":"grasp_target","contact_count":1804.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.53462,0.00654,0.13789]},{"body_a":"world","body_b":"grasp_target","contact_count":24.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":2.0,"phase_name":"touch_object_surface","phase_type":"contact","tcp_position_centroid":[0.5384,0.00192,0.06366]},{"body_a":"world","body_b":"grasp_target","contact_count":628.0,"contact_point_centroid":[0.56118,-0.02755,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.63827,0.14772,0.25649]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.56118,-0.02755,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.63783,0.15232,0.2078]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2668.0,"contact_point_centroid":[0.53086,0.02047,0.05034],"force_p95":0.09798,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10743,"mean_force":0.07624,"phase_index":3.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.52978,0.00172,0.05306]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3198.0,"contact_point_centroid":[0.53116,-0.01706,0.05061],"force_p95":0.09201,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09276,"mean_force":0.06472,"phase_index":3.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.52979,0.00172,0.05307]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3115.0,"contact_point_centroid":[0.56703,0.04371,0.28798],"force_p95":0.01102,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01618,"mean_force":0.01049,"phase_index":5.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.56662,0.0437,0.28567]},{"body_a":"left_finger","body_b":"right_finger","contact_count":669.0,"contact_point_centroid":[0.63885,0.14776,0.25853],"force_p95":0.01104,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01279,"mean_force":0.01046,"phase_index":6.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.63829,0.14774,0.25622]}],"total_contact_groups":17},"final_pose_error":0.01991,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.56118,-0.02755,0.01602],"final_tcp_position":[0.64197,0.15338,0.20961],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":81.14225,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":199.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":792.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_pregrasp","tcp_end":[0.5331,0.01117,0.21368],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.18826,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":451.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1804.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_pregrasp","tcp_end":[0.53874,0.00196,0.06423],"tcp_start":[0.5331,0.01117,0.21368],"tcp_to_object_dist_end":0.03862,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":6.0,"n_steps_budget":600.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":81.14225,"phase_name":"touch_object_surface","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":24.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_contact","tcp_end":[0.53797,0.00188,0.06301],"tcp_start":[0.53874,0.00196,0.06423],"tcp_to_object_dist_end":0.03753,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":28.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54424,0.00157,0.02581],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25002,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.13696,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":7666.0,"raw_peak_contact_force":0.17291,"subtask_id":"grasp_contact","tcp_end":[0.52976,0.00172,0.05303],"tcp_start":[0.53797,0.00188,0.06301],"tcp_to_object_dist_end":0.03083,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":15.0,"n_steps":633.0,"n_steps_budget":720.0,"object_pos_end":[0.54587,0.00157,0.11666],"object_pos_start":[0.54424,0.00157,0.02581],"object_to_goal_dist_end":0.20098,"object_to_goal_dist_start":0.25002,"object_z_max":0.11656,"peak_contact_force":0.18019,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":11562.0,"raw_peak_contact_force":0.27946,"subtask_id":"lift_clear","tcp_end":[0.53935,0.00151,0.15301],"tcp_start":[0.52976,0.00172,0.05303],"tcp_to_object_dist_end":0.03692,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":883.0,"n_steps_budget":1000.0,"object_pos_end":[0.56118,-0.02755,0.01602],"object_pos_start":[0.54587,0.00157,0.11666],"object_to_goal_dist_end":0.26942,"object_to_goal_dist_start":0.20098,"object_z_max":0.11699,"peak_contact_force":0.12263,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":6475.0,"raw_peak_contact_force":1.4292,"subtask_id":"place_goal","tcp_end":[0.63571,0.14246,0.30144],"tcp_start":[0.53935,0.00151,0.15301],"tcp_to_object_dist_end":0.34047,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":157.0,"n_steps_budget":1000.0,"object_pos_end":[0.56118,-0.02755,0.01602],"object_pos_start":[0.56118,-0.02755,0.01602],"object_to_goal_dist_end":0.26942,"object_to_goal_dist_start":0.26942,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1297.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_goal","tcp_end":[0.64197,0.15338,0.20961],"tcp_start":[0.63571,0.14246,0.30144],"tcp_to_object_dist_end":0.27702,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.56118,-0.02755,0.01602],"object_pos_start":[0.56118,-0.02755,0.01602],"object_to_goal_dist_end":0.26942,"object_to_goal_dist_start":0.26942,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1021.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_goal","tcp_end":[0.6365,0.15188,0.22706],"tcp_start":[0.64197,0.15338,0.20961],"tcp_to_object_dist_end":0.28706,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.87755,"average_solve_count":147.0,"average_success_count":147.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_z":0.12762,"approach_goal.goal_arc_height":0.15945,"approach_object.approach_z":0.13969,"approach_object.arc_height":0.13636,"descend_to_contact.descend_z":0.03001,"descend_to_place.descend_goal_tolerance":0.02032,"lift_object.lift_height":0.14095,"release_object.release_duration":1.12711,"touch_object_surface.contact_force":8.28735},"optimized_scores":{"best_composite_score":0.10729,"best_fitness_score":0.61229,"best_task_score":0.31936},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1749.0,"contact_point_centroid":[0.55227,0.04279,-0.00253],"force_p95":0.25804,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.2604,"mean_force":0.14564,"phase_index":5.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.55637,0.09549,0.23183]},{"body_a":"world","body_b":"grasp_target","contact_count":146.0,"contact_point_centroid":[0.52886,0.03073,-0.0011],"force_p95":0.22866,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.34562,"mean_force":0.08282,"phase_index":4.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.51575,0.03081,0.05618]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6296.0,"contact_point_centroid":[0.52211,0.01224,0.09689],"force_p95":0.1286,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28063,"mean_force":0.09628,"phase_index":4.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.51897,0.03059,0.1003]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6364.0,"contact_point_centroid":[0.52238,0.04893,0.09758],"force_p95":0.12923,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27036,"mean_force":0.0954,"phase_index":4.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.5191,0.03059,0.10114]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":680.0,"contact_point_centroid":[0.53123,0.01439,0.16004],"force_p95":0.13364,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23795,"mean_force":0.10024,"phase_index":5.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.52493,0.03267,0.16403]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":671.0,"contact_point_centroid":[0.53124,0.05077,0.15945],"force_p95":0.14927,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23043,"mean_force":0.10181,"phase_index":5.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.52492,0.03256,0.16358]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.5305,0.03078,-0.00202],"force_p95":0.19475,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19863,"mean_force":0.15313,"phase_index":3.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.5181,0.031,0.05581]},{"body_a":"world","body_b":"grasp_target","contact_count":1076.0,"contact_point_centroid":[0.5305,0.03079,-0.00188],"force_p95":0.1365,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12308,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.50906,0.03353,0.24875]},{"body_a":"world","body_b":"grasp_target","contact_count":1468.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.52255,0.03586,0.12372]},{"body_a":"world","body_b":"grasp_target","contact_count":4.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":2.0,"phase_name":"touch_object_surface","phase_type":"contact","tcp_position_centroid":[0.52516,0.03153,0.06431]},{"body_a":"world","body_b":"grasp_target","contact_count":780.0,"contact_point_centroid":[0.5525,0.04281,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.59255,0.16765,0.18213]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.5525,0.04281,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.5903,0.17241,0.1258]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2686.0,"contact_point_centroid":[0.51768,0.01217,0.05161],"force_p95":0.11331,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12162,"mean_force":0.08738,"phase_index":3.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.51694,0.03093,0.05444]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2924.0,"contact_point_centroid":[0.51733,0.04959,0.05126],"force_p95":0.1056,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11124,"mean_force":0.08163,"phase_index":3.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.51694,0.03093,0.05444]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1582.0,"contact_point_centroid":[0.56081,0.10329,0.23872],"force_p95":0.0118,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0164,"mean_force":0.01063,"phase_index":5.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.56044,0.10328,0.2365]},{"body_a":"left_finger","body_b":"right_finger","contact_count":831.0,"contact_point_centroid":[0.59303,0.16766,0.18442],"force_p95":0.01097,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01274,"mean_force":0.01046,"phase_index":6.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.59255,0.16764,0.18221]}],"total_contact_groups":17},"final_pose_error":0.01962,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.5525,0.04281,0.01602],"final_tcp_position":[0.59564,0.17396,0.12622],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":273017.02452,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":270.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1076.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_pregrasp","tcp_end":[0.52255,0.04036,0.1849],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.15937,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":367.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1468.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_pregrasp","tcp_end":[0.52516,0.03153,0.06431],"tcp_start":[0.52255,0.04036,0.1849],"tcp_to_object_dist_end":0.03867,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":81.14225,"phase_name":"touch_object_surface","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":4.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_contact","tcp_end":[0.52504,0.03151,0.06405],"tcp_start":[0.52516,0.03153,0.06431],"tcp_to_object_dist_end":0.03843,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":27.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53041,0.0308,0.02591],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18345,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.1945,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":7410.0,"raw_peak_contact_force":0.19863,"subtask_id":"grasp_contact","tcp_end":[0.51691,0.03092,0.0544],"tcp_start":[0.52504,0.03151,0.06405],"tcp_to_object_dist_end":0.03153,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":19.0,"n_steps":633.0,"n_steps_budget":720.0,"object_pos_end":[0.53153,0.03049,0.11771],"object_pos_start":[0.53041,0.0308,0.02591],"object_to_goal_dist_end":0.16408,"object_to_goal_dist_start":0.18345,"object_z_max":0.11759,"peak_contact_force":0.11253,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":12806.0,"raw_peak_contact_force":0.34562,"subtask_id":"lift_clear","tcp_end":[0.52565,0.03054,0.15425],"tcp_start":[0.51691,0.03092,0.0544],"tcp_to_object_dist_end":0.03701,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":591.0,"n_steps_budget":1000.0,"object_pos_end":[0.5525,0.04281,0.01602],"object_pos_start":[0.53153,0.03049,0.11771],"object_to_goal_dist_end":0.17122,"object_to_goal_dist_start":0.16408,"object_z_max":0.13719,"peak_contact_force":273017.02452,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4682.0,"raw_peak_contact_force":1.2604,"subtask_id":"place_goal","tcp_end":[0.59086,0.1619,0.23589],"tcp_start":[0.52565,0.03054,0.15425],"tcp_to_object_dist_end":0.25297,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":195.0,"n_steps_budget":1000.0,"object_pos_end":[0.5525,0.04281,0.01602],"object_pos_start":[0.5525,0.04281,0.01602],"object_to_goal_dist_end":0.17122,"object_to_goal_dist_start":0.17122,"object_z_max":0.01602,"peak_contact_force":9748.83409,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1611.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_goal","tcp_end":[0.59564,0.17396,0.12622],"tcp_start":[0.59086,0.1619,0.23589],"tcp_to_object_dist_end":0.17666,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5525,0.04281,0.01602],"object_pos_start":[0.5525,0.04281,0.01602],"object_to_goal_dist_end":0.17122,"object_to_goal_dist_start":0.17122,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1024.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_goal","tcp_end":[0.58851,0.17181,0.14567],"tcp_start":[0.59564,0.17396,0.12622],"tcp_to_object_dist_end":0.1864,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```