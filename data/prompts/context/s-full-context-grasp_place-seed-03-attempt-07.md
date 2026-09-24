## Search State

- **Seed**: 3
- **Iteration**: 8 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 7 | approach → descend → contact → grasp → lift → approach → descend → release | arc_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 9 | -0.3241 | 0.22 | ✅ accepted |
| 6 | approach → contact → grasp → lift → retract → approach → descend → release | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 9 | -0.3276 | 0.18 | ❌ rejected |
| 5 | approach → descend → contact → grasp → lift → approach → descend → release | arc_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 9 | -0.0332 | 0.21 | ❌ rejected |
| 4 | approach → descend → contact → grasp → lift → approach → descend → release | arc_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 9 | -0.3230 | 0.21 | ✅ accepted |
| 3 | approach → descend → grasp → lift → approach → descend → release → retract | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 9 | -0.4496 | 0.17 | ❌ rejected |

**Proposal policy**: task_score is 0.22 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.324) — your mutation base

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

- **Composite score**: -0.324
- **task_score** (E): 0.216
- **fitness_score**: 0.181  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.125
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.630

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 0.00 | 1.00 | 0.1389 |
| hover_above_object | 0.00 | 1.00 | 0.0626 |
| touch_object_top | 1.00 | 1.00 | 0.0002 |
| grasp_object | 1.00 | 1.00 | 0.0000 |
| lift_object | 0.00 | 1.00 | 0.1049 |
| approach_goal | 0.33 | 1.00 | 0.1429 |
| descend_at_goal | 0.00 | 1.00 | 0.0491 |
| release_object | 1.00 | 1.00 | 0.0267 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 0.00 / step_budget | (0.500, -0.000, 0.301)→(0.433, 0.037, 0.189) | (0.511, 0.002, 0.030)→(0.473, 0.002, 0.016) | 0.244→0.269 | 1.00 / 5.000 | 307.936 | 1334.207 |
| hover_above_object | descend | 0.00 / step_budget | (0.433, 0.037, 0.189)→(0.462, 0.051, 0.189) | (0.473, 0.002, 0.016)→(0.473, 0.002, 0.016) | 0.269→0.269 | 1.00 / 5.333 | 368.942 | 903.893 |
| touch_object_top | contact | 1.00 / force_exceeded | (0.462, 0.051, 0.189)→(0.462, 0.051, 0.189) | (0.473, 0.002, 0.016)→(0.473, 0.002, 0.016) | 0.269→0.269 | 1.00 / 5.333 | 261.252 | 261.252 |
| grasp_object | grasp | 1.00 / step_budget | (0.462, 0.052, 0.188)→(0.462, 0.051, 0.188) | (0.473, 0.002, 0.016)→(0.473, 0.002, 0.016) | 0.269→0.269 | 1.00 / 9.333 | 75.163 | 494.082 |
| lift_object | lift | 0.00 / step_budget | (0.462, 0.051, 0.188)→(0.497, 0.008, 0.263) | (0.473, 0.002, 0.016)→(0.472, 0.003, 0.016) | 0.269→0.270 | 1.00 / 11.000 | 147146.695 | 626.505 |
| approach_goal | approach | 0.33 / step_budget | (0.497, 0.008, 0.263)→(0.532, 0.115, 0.270) | (0.472, 0.003, 0.016)→(0.471, 0.032, 0.020) | 0.270→0.250 | 1.00 / 8.333 | 199.238 | 437.323 |
| descend_at_goal | descend | 0.00 / step_budget | (0.532, 0.115, 0.270)→(0.556, 0.128, 0.278) | (0.471, 0.032, 0.020)→(0.474, 0.033, 0.019) | 0.250→0.249 | 1.00 / 9.667 | 91121.426 | 727.529 |
| release_object | release | 1.00 / step_budget | (0.556, 0.128, 0.278)→(0.555, 0.128, 0.305) | (0.474, 0.033, 0.019)→(0.472, 0.033, 0.019) | 0.249→0.249 | 1.00 / 4.000 | 0.123 | 131.870 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 0.000
- place_accuracy: 0.000
- lift_clearance: 0.000
- transport_retention: 0.000
- terminal_score: 0.373
- phase_score: 0.359
- phase_breakdown.lift_clear_score: 0.123
- phase_breakdown.reach_pregrasp_score: 0.086
- phase_breakdown.grasp_contact_score: 1.000
- phase_breakdown.place_goal_score: 0.025
- grasp_place_fitness: 0.255

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.255
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.373
- **Median Q (composite search score)**: -0.342
- **K-run variance**: 0.0030
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.299


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":7.66667,"average_solve_count":108.0,"average_success_count":108.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_z":0.10966,"approach_goal.goal_arc_height":0.13779,"approach_object.approach_z":0.13946,"approach_object.arc_height":0.17375,"descend_at_goal.descend_goal_tolerance":0.0208,"hover_above_object.hover_z":0.03856,"lift_object.lift_height":0.08446,"release_object.release_duration":1.25198,"touch_object_top.contact_force":9.73587},"optimized_scores":{"best_composite_score":-0.38007,"best_fitness_score":0.12493,"best_task_score":0.11076},"replay_outcomes":[{"contacts":{"omitted_contact_groups":7,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":887.0,"contact_point_centroid":[0.63235,0.01382,-0.00046],"force_p95":201.30902,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1318.33428,"mean_force":200.82083,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.38856,0.01211,0.11714]},{"body_a":"world","body_b":"link7","contact_count":23.0,"contact_point_centroid":[0.52531,0.01464,-0.00304],"force_p95":349.27575,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1240.82667,"mean_force":70.82221,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.37262,0.00893,0.0481]},{"body_a":"world","body_b":"link6","contact_count":954.0,"contact_point_centroid":[0.62193,-0.00545,-0.00022],"force_p95":412.93975,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":888.19328,"mean_force":280.25237,"phase_index":1.0,"phase_name":"hover_above_object","phase_type":"descend","tcp_position_centroid":[0.42552,-0.0006,0.19271]},{"body_a":"world","body_b":"link6","contact_count":547.0,"contact_point_centroid":[0.64863,-0.01684,-0.00013],"force_p95":85.61989,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":745.84368,"mean_force":74.68877,"phase_index":3.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.45663,-0.01749,0.20387]},{"body_a":"world","body_b":"link6","contact_count":975.0,"contact_point_centroid":[0.51041,0.04849,-0.00027],"force_p95":642.1082,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":717.74354,"mean_force":427.27337,"phase_index":6.0,"phase_name":"descend_at_goal","phase_type":"descend","tcp_position_centroid":[0.38196,0.05188,0.25126]},{"body_a":"world","body_b":"link6","contact_count":990.0,"contact_point_centroid":[0.56457,-0.01567,-0.00023],"force_p95":249.21075,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":260.14536,"mean_force":221.86841,"phase_index":5.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.34594,0.002,0.16184]},{"body_a":"world","body_b":"link6","contact_count":624.0,"contact_point_centroid":[0.61593,-0.02418,-0.00025],"force_p95":209.21778,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":250.5375,"mean_force":195.9277,"phase_index":4.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.41296,-0.01489,0.18426]},{"body_a":"world","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.64771,-0.01697,-0.00027],"force_p95":203.75365,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":203.75365,"mean_force":203.75365,"phase_index":2.0,"phase_name":"touch_object_top","phase_type":"contact","tcp_position_centroid":[0.45675,-0.01766,0.20458]},{"body_a":"world","body_b":"link6","contact_count":72.0,"contact_point_centroid":[0.54722,0.0811,-0.00017],"force_p95":103.1148,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":133.16506,"mean_force":77.86584,"phase_index":7.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.40925,0.06805,0.25105]},{"body_a":"grasp_target","body_b":"hand","contact_count":40.0,"contact_point_centroid":[0.43882,-0.01813,0.04232],"force_p95":3.37234,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.74811,"mean_force":1.45279,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.38332,0.009,0.05018]},{"body_a":"world","body_b":"grasp_target","contact_count":3920.0,"contact_point_centroid":[0.42257,-0.02472,-0.00213],"force_p95":0.13759,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.29074,"mean_force":0.1382,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.40072,0.01154,0.12743]},{"body_a":"world","body_b":"grasp_target","contact_count":3860.0,"contact_point_centroid":[0.41757,-0.02446,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"hover_above_object","phase_type":"descend","tcp_position_centroid":[0.42565,-0.00066,0.19286]},{"body_a":"world","body_b":"grasp_target","contact_count":4.0,"contact_point_centroid":[0.41757,-0.02446,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":2.0,"phase_name":"touch_object_top","phase_type":"contact","tcp_position_centroid":[0.45675,-0.01766,0.20458]},{"body_a":"world","body_b":"grasp_target","contact_count":2200.0,"contact_point_centroid":[0.41757,-0.02446,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":3.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.45663,-0.01749,0.20388]},{"body_a":"world","body_b":"grasp_target","contact_count":2500.0,"contact_point_centroid":[0.41757,-0.02446,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":4.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.41301,-0.01489,0.18428]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.41757,-0.02446,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.34629,0.00201,0.16218]}],"total_contact_groups":23},"final_pose_error":0.2952,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.41757,-0.02446,0.01602],"final_tcp_position":[0.40958,0.06811,0.25148],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":273003.0364,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.41757,-0.02446,0.01602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.33006,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":194.39479,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4870.0,"raw_peak_contact_force":1318.33428,"subtask_id":"reach_pregrasp","tcp_end":[0.39675,0.01202,0.14506],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13571,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":965.0,"n_steps_budget":1000.0,"object_pos_end":[0.41757,-0.02446,0.01602],"object_pos_start":[0.41757,-0.02446,0.01602],"object_to_goal_dist_end":0.33006,"object_to_goal_dist_start":0.33006,"object_z_max":0.01602,"peak_contact_force":347.69213,"phase_name":"hover_above_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4814.0,"raw_peak_contact_force":888.19328,"subtask_id":"reach_pregrasp","tcp_end":[0.45675,-0.01766,0.20458],"tcp_start":[0.39675,0.01202,0.14506],"tcp_to_object_dist_end":0.19271,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.41757,-0.02446,0.01602],"object_pos_start":[0.41757,-0.02446,0.01602],"object_to_goal_dist_end":0.33006,"object_to_goal_dist_start":0.33006,"object_z_max":0.01602,"peak_contact_force":203.75365,"phase_name":"touch_object_top","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":5.0,"raw_peak_contact_force":203.75365,"subtask_id":"grasp_contact","tcp_end":[0.45671,-0.01759,0.20467],"tcp_start":[0.45675,-0.01766,0.20458],"tcp_to_object_dist_end":0.19279,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.41757,-0.02446,0.01602],"object_pos_start":[0.41757,-0.02446,0.01602],"object_to_goal_dist_end":0.33006,"object_to_goal_dist_start":0.33006,"object_z_max":0.01602,"peak_contact_force":70.64395,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":3511.0,"raw_peak_contact_force":745.84368,"subtask_id":"grasp_contact","tcp_end":[0.45663,-0.0175,0.20377],"tcp_start":[0.45663,-0.0175,0.20378],"tcp_to_object_dist_end":0.1919,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":625.0,"n_steps_budget":720.0,"object_pos_end":[0.41757,-0.02446,0.01602],"object_pos_start":[0.41757,-0.02446,0.01602],"object_to_goal_dist_end":0.33006,"object_to_goal_dist_start":0.33006,"object_z_max":0.01602,"peak_contact_force":273003.0364,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":5778.0,"raw_peak_contact_force":250.5375,"subtask_id":"lift_clear","tcp_end":[0.42927,-0.01881,0.21474],"tcp_start":[0.45663,-0.0175,0.20377],"tcp_to_object_dist_end":0.19915,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.41757,-0.02446,0.01602],"object_pos_start":[0.41757,-0.02446,0.01602],"object_to_goal_dist_end":0.33006,"object_to_goal_dist_start":0.33006,"object_z_max":0.01602,"peak_contact_force":227.80052,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":9316.0,"raw_peak_contact_force":260.14536,"subtask_id":"place_goal","tcp_end":[0.34961,0.02608,0.19423],"tcp_start":[0.42927,-0.01881,0.21474],"tcp_to_object_dist_end":0.19731,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.41757,-0.02446,0.01602],"object_pos_start":[0.41757,-0.02446,0.01602],"object_to_goal_dist_end":0.33006,"object_to_goal_dist_start":0.33006,"object_z_max":0.01602,"peak_contact_force":2.35947,"phase_name":"descend_at_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":9210.0,"raw_peak_contact_force":717.74354,"subtask_id":"place_goal","tcp_end":[0.40958,0.06811,0.25148],"tcp_start":[0.34961,0.02608,0.19423],"tcp_to_object_dist_end":0.25313,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.41757,-0.02446,0.01602],"object_pos_start":[0.41757,-0.02446,0.01602],"object_to_goal_dist_end":0.33006,"object_to_goal_dist_start":0.33006,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1095.0,"raw_peak_contact_force":133.16506,"tcp_end":[0.40858,0.068,0.27999],"tcp_start":[0.40958,0.06811,0.25148],"tcp_to_object_dist_end":0.27983,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":5.98462,"average_solve_count":130.0,"average_success_count":130.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_z":0.11819,"approach_goal.goal_arc_height":0.13631,"approach_object.approach_z":0.10701,"approach_object.arc_height":0.19898,"descend_at_goal.descend_goal_tolerance":0.02537,"hover_above_object.hover_z":0.0678,"lift_object.lift_height":0.15553,"release_object.release_duration":1.86187,"touch_object_top.contact_force":10.71172},"optimized_scores":{"best_composite_score":-0.34184,"best_fitness_score":0.16316,"best_task_score":0.16531},"replay_outcomes":[{"contacts":{"omitted_contact_groups":17,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":885.0,"contact_point_centroid":[0.64135,0.02689,-0.00043],"force_p95":302.5634,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1307.29384,"mean_force":219.76012,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.41994,0.02456,0.15342]},{"body_a":"world","body_b":"link7","contact_count":22.0,"contact_point_centroid":[0.53532,0.01148,-0.00302],"force_p95":360.23133,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1220.62182,"mean_force":72.71876,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.38293,0.01387,0.04852]},{"body_a":"link5","body_b":"hand","contact_count":362.0,"contact_point_centroid":[0.51288,-0.03973,0.2406],"force_p95":531.34924,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":977.56438,"mean_force":310.99734,"phase_index":4.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.52322,0.05242,0.25709]},{"body_a":"world","body_b":"link6","contact_count":977.0,"contact_point_centroid":[0.6321,0.02637,-0.00023],"force_p95":459.08038,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":935.27422,"mean_force":313.08998,"phase_index":1.0,"phase_name":"hover_above_object","phase_type":"descend","tcp_position_centroid":[0.44455,0.04871,0.20493]},{"body_a":"world","body_b":"link6","contact_count":947.0,"contact_point_centroid":[0.65131,0.15043,-0.00031],"force_p95":534.31339,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":850.48588,"mean_force":371.99515,"phase_index":6.0,"phase_name":"descend_at_goal","phase_type":"descend","tcp_position_centroid":[0.65,0.15407,0.29366]},{"body_a":"world","body_b":"link6","contact_count":440.0,"contact_point_centroid":[0.60941,-0.0067,-0.00031],"force_p95":323.04611,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":692.79762,"mean_force":247.78852,"phase_index":4.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.51268,0.06254,0.23782]},{"body_a":"world","body_b":"hand","contact_count":55.0,"contact_point_centroid":[0.53957,0.13074,-0.0003],"force_p95":360.32198,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":623.30057,"mean_force":307.60756,"phase_index":4.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.4606,0.14523,0.13177]},{"body_a":"world","body_b":"link6","contact_count":550.0,"contact_point_centroid":[0.68573,0.01005,-0.00012],"force_p95":73.56067,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":351.33681,"mean_force":70.67309,"phase_index":3.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.47081,0.06807,0.16548]},{"body_a":"world","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.68471,0.01019,-0.00014],"force_p95":338.73879,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":338.73879,"mean_force":338.73879,"phase_index":2.0,"phase_name":"touch_object_top","phase_type":"contact","tcp_position_centroid":[0.47089,0.0679,0.16698]},{"body_a":"world","body_b":"link6","contact_count":3.0,"contact_point_centroid":[0.57426,-0.02659,-0.00019],"force_p95":243.12059,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":250.47955,"mean_force":200.02019,"phase_index":5.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.53697,0.0074,0.28974]},{"body_a":"world","body_b":"link6","contact_count":88.0,"contact_point_centroid":[0.6774,0.15578,-0.00012],"force_p95":76.23813,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":123.44763,"mean_force":54.91563,"phase_index":7.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.65858,0.15757,0.29364]},{"body_a":"link5","body_b":"hand","contact_count":5.0,"contact_point_centroid":[0.50401,-0.08728,0.24364],"force_p95":88.62108,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":110.77635,"mean_force":22.15527,"phase_index":5.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.53715,0.00723,0.29025]},{"body_a":"grasp_target","body_b":"link6","contact_count":120.0,"contact_point_centroid":[0.54607,-0.00466,0.02887],"force_p95":0.90036,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.75358,"mean_force":0.48182,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.39079,0.01476,0.08714]},{"body_a":"grasp_target","body_b":"link7","contact_count":276.0,"contact_point_centroid":[0.52512,0.00476,0.0331],"force_p95":2.38647,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.38349,"mean_force":0.52103,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.39796,0.01607,0.10268]},{"body_a":"grasp_target","body_b":"hand","contact_count":115.0,"contact_point_centroid":[0.49873,-0.00647,0.04579],"force_p95":2.34065,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.90639,"mean_force":0.9238,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.39208,0.01455,0.08018]},{"body_a":"world","body_b":"grasp_target","contact_count":3739.0,"contact_point_centroid":[0.51467,-0.00283,-0.00222],"force_p95":0.26519,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.68555,"mean_force":0.15224,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.43132,0.02346,0.16342]}],"total_contact_groups":33},"final_pose_error":0.10277,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.48752,0.02921,0.01602],"final_tcp_position":[0.65861,0.15798,0.29328],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":273007.3688,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50898,-0.00355,0.01602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.27569,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":351.77177,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":5157.0,"raw_peak_contact_force":1307.29384,"subtask_id":"reach_pregrasp","tcp_end":[0.45495,0.03886,0.20612],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.20213,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":6.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50898,-0.00355,0.01602],"object_pos_start":[0.50898,-0.00355,0.01602],"object_to_goal_dist_end":0.27569,"object_to_goal_dist_start":0.27569,"object_z_max":0.01602,"peak_contact_force":401.94488,"phase_name":"hover_above_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4990.0,"raw_peak_contact_force":935.27422,"subtask_id":"reach_pregrasp","tcp_end":[0.47089,0.0679,0.16698],"tcp_start":[0.45495,0.03886,0.20612],"tcp_to_object_dist_end":0.1713,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":6.0,"n_steps":1.0,"n_steps_budget":930.0,"object_pos_end":[0.50898,-0.00355,0.01602],"object_pos_start":[0.50898,-0.00355,0.01602],"object_to_goal_dist_end":0.27569,"object_to_goal_dist_start":0.27569,"object_z_max":0.01602,"peak_contact_force":338.73879,"phase_name":"touch_object_top","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":6.0,"raw_peak_contact_force":338.73879,"subtask_id":"grasp_contact","tcp_end":[0.47088,0.0679,0.16677],"tcp_start":[0.47089,0.0679,0.16698],"tcp_to_object_dist_end":0.17112,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.50898,-0.00355,0.01602],"object_pos_start":[0.50898,-0.00355,0.01602],"object_to_goal_dist_end":0.27569,"object_to_goal_dist_start":0.27569,"object_z_max":0.01602,"peak_contact_force":68.86016,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":3582.0,"raw_peak_contact_force":351.33681,"subtask_id":"grasp_contact","tcp_end":[0.47079,0.06808,0.16536],"tcp_start":[0.47079,0.06808,0.16536],"tcp_to_object_dist_end":0.16998,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":12.0,"n_steps":513.0,"n_steps_budget":600.0,"object_pos_end":[0.50407,-0.00066,0.01454],"object_pos_start":[0.50898,-0.00355,0.01602],"object_to_goal_dist_end":0.27746,"object_to_goal_dist_start":0.27569,"object_z_max":0.01604,"peak_contact_force":167951.73011,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":5416.0,"raw_peak_contact_force":977.56438,"subtask_id":"lift_clear","tcp_end":[0.53686,0.00758,0.28943],"tcp_start":[0.47079,0.06808,0.16536],"tcp_to_object_dist_end":0.27696,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":526.0,"n_steps_budget":1000.0,"object_pos_end":[0.48752,0.02921,0.01602],"object_pos_start":[0.50407,-0.00066,0.01454],"object_to_goal_dist_end":0.26999,"object_to_goal_dist_start":0.27746,"object_z_max":0.01746,"peak_contact_force":0.12263,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4283.0,"raw_peak_contact_force":250.47955,"subtask_id":"place_goal","tcp_end":[0.63922,0.14452,0.32099],"tcp_start":[0.53686,0.00758,0.28943],"tcp_to_object_dist_end":0.35961,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.48752,0.02921,0.01602],"object_pos_start":[0.48752,0.02921,0.01602],"object_to_goal_dist_end":0.26999,"object_to_goal_dist_start":0.26999,"object_z_max":0.01602,"peak_contact_force":273007.3688,"phase_name":"descend_at_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":9241.0,"raw_peak_contact_force":850.48588,"subtask_id":"place_goal","tcp_end":[0.65861,0.15798,0.29328],"tcp_start":[0.63922,0.14452,0.32099],"tcp_to_object_dist_end":0.35033,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48752,0.02921,0.01602],"object_pos_start":[0.48752,0.02921,0.01602],"object_to_goal_dist_end":0.26999,"object_to_goal_dist_start":0.26999,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1111.0,"raw_peak_contact_force":123.44763,"tcp_end":[0.65882,0.15787,0.31842],"tcp_start":[0.65861,0.15798,0.29328],"tcp_to_object_dist_end":0.3706,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":5.98387,"average_solve_count":124.0,"average_success_count":124.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_z":0.13217,"approach_goal.goal_arc_height":0.13678,"approach_object.approach_z":0.12929,"approach_object.arc_height":0.12422,"descend_at_goal.descend_goal_tolerance":0.01879,"hover_above_object.hover_z":0.04103,"lift_object.lift_height":0.10727,"release_object.release_duration":0.85508,"touch_object_top.contact_force":9.2832},"optimized_scores":{"best_composite_score":-0.25027,"best_fitness_score":0.25473,"best_task_score":0.37325},"replay_outcomes":[{"contacts":{"omitted_contact_groups":14,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":879.0,"contact_point_centroid":[0.62953,0.0429,-0.00042],"force_p95":383.50294,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1376.99226,"mean_force":245.93222,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.41329,0.04005,0.16061]},{"body_a":"world","body_b":"link6","contact_count":986.0,"contact_point_centroid":[0.6115,0.06234,-0.00025],"force_p95":472.31623,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":888.21118,"mean_force":320.69552,"phase_index":1.0,"phase_name":"hover_above_object","phase_type":"descend","tcp_position_centroid":[0.43415,0.0754,0.21716]},{"body_a":"world","body_b":"link6","contact_count":460.0,"contact_point_centroid":[0.59131,0.15033,-0.00026],"force_p95":630.77358,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":801.34308,"mean_force":431.888,"phase_index":5.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.59904,0.16213,0.29349]},{"body_a":"link5","body_b":"hand","contact_count":286.0,"contact_point_centroid":[0.51333,-0.04653,0.24217],"force_p95":250.70496,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":651.41382,"mean_force":214.0374,"phase_index":4.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.5163,0.05586,0.28098]},{"body_a":"world","body_b":"link6","contact_count":568.0,"contact_point_centroid":[0.60156,0.04211,-0.00022],"force_p95":545.80544,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":649.09243,"mean_force":329.68763,"phase_index":4.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48187,0.10191,0.23879]},{"body_a":"world","body_b":"link6","contact_count":998.0,"contact_point_centroid":[0.61695,0.1675,-0.00032],"force_p95":468.46301,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":614.35698,"mean_force":352.33133,"phase_index":6.0,"phase_name":"descend_at_goal","phase_type":"descend","tcp_position_centroid":[0.60882,0.17289,0.2934]},{"body_a":"world","body_b":"link6","contact_count":546.0,"contact_point_centroid":[0.64834,0.05404,-0.00013],"force_p95":76.95067,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":385.06438,"mean_force":73.62786,"phase_index":3.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.45728,0.10393,0.19475]},{"body_a":"world","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.64758,0.05417,-3e-05],"force_p95":241.26296,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":241.26296,"mean_force":241.26296,"phase_index":2.0,"phase_name":"touch_object_top","phase_type":"contact","tcp_position_centroid":[0.45745,0.10348,0.19601]},{"body_a":"world","body_b":"link6","contact_count":84.0,"contact_point_centroid":[0.63567,0.16521,-0.00013],"force_p95":75.85936,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":138.99849,"mean_force":56.77523,"phase_index":7.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.5988,0.15768,0.29082]},{"body_a":"link5","body_b":"hand","contact_count":3.0,"contact_point_centroid":[0.5193,-0.06534,0.23815],"force_p95":46.17824,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":51.30915,"mean_force":17.10305,"phase_index":5.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.5255,0.03496,0.28478]},{"body_a":"world","body_b":"link7","contact_count":21.0,"contact_point_centroid":[0.5298,0.01953,-0.00296],"force_p95":0.0,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":25.46442,"mean_force":1.21259,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.3762,0.02071,0.05075]},{"body_a":"grasp_target","body_b":"link7","contact_count":270.0,"contact_point_centroid":[0.51558,0.02779,0.03177],"force_p95":2.78657,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.81992,"mean_force":0.47204,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.39084,0.02415,0.10371]},{"body_a":"grasp_target","body_b":"hand","contact_count":94.0,"contact_point_centroid":[0.48799,0.0234,0.04285],"force_p95":2.40103,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.08729,"mean_force":0.96502,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.38504,0.02154,0.07686]},{"body_a":"world","body_b":"grasp_target","contact_count":3793.0,"contact_point_centroid":[0.49958,0.03411,-0.00227],"force_p95":0.30017,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.93477,"mean_force":0.15451,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.42463,0.03803,0.16911]},{"body_a":"grasp_target","body_b":"link6","contact_count":674.0,"contact_point_centroid":[0.50671,0.07225,0.04327],"force_p95":0.67557,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.701,"mean_force":0.33594,"phase_index":5.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.57838,0.128,0.29725]},{"body_a":"grasp_target","body_b":"link6","contact_count":1000.0,"contact_point_centroid":[0.52524,0.09732,0.05594],"force_p95":0.22665,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.14712,"mean_force":0.0995,"phase_index":6.0,"phase_name":"descend_at_goal","phase_type":"descend","tcp_position_centroid":[0.60882,0.17289,0.2934]}],"total_contact_groups":30},"final_pose_error":0.18357,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.5122,0.09411,0.02602],"final_tcp_position":[0.59875,0.15811,0.29049],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":273004.12046,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49394,0.03467,0.01602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.2019,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":377.64214,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":5134.0,"raw_peak_contact_force":1376.99226,"subtask_id":"reach_pregrasp","tcp_end":[0.44789,0.06162,0.21474],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.20576,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49394,0.03467,0.01602],"object_pos_start":[0.49394,0.03467,0.01602],"object_to_goal_dist_end":0.2019,"object_to_goal_dist_start":0.2019,"object_z_max":0.01602,"peak_contact_force":357.18895,"phase_name":"hover_above_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4986.0,"raw_peak_contact_force":888.21118,"subtask_id":"reach_pregrasp","tcp_end":[0.45745,0.10348,0.19601],"tcp_start":[0.44789,0.06162,0.21474],"tcp_to_object_dist_end":0.19612,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.49394,0.03467,0.01602],"object_pos_start":[0.49394,0.03467,0.01602],"object_to_goal_dist_end":0.2019,"object_to_goal_dist_start":0.2019,"object_z_max":0.01602,"peak_contact_force":241.26296,"phase_name":"touch_object_top","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":5.0,"raw_peak_contact_force":241.26296,"subtask_id":"grasp_contact","tcp_end":[0.45742,0.1037,0.19588],"tcp_start":[0.45745,0.10348,0.19601],"tcp_to_object_dist_end":0.19608,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.49394,0.03467,0.01602],"object_pos_start":[0.49394,0.03467,0.01602],"object_to_goal_dist_end":0.2019,"object_to_goal_dist_start":0.2019,"object_z_max":0.01602,"peak_contact_force":85.98424,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":3506.0,"raw_peak_contact_force":385.06438,"subtask_id":"grasp_contact","tcp_end":[0.45728,0.10391,0.19466],"tcp_start":[0.45728,0.10392,0.19466],"tcp_to_object_dist_end":0.19507,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":11.0,"n_steps":603.0,"n_steps_budget":690.0,"object_pos_end":[0.49394,0.03467,0.01602],"object_pos_start":[0.49394,0.03467,0.01602],"object_to_goal_dist_end":0.2019,"object_to_goal_dist_start":0.2019,"object_z_max":0.01602,"peak_contact_force":485.31997,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":5863.0,"raw_peak_contact_force":651.41382,"subtask_id":"lift_clear","tcp_end":[0.52536,0.03509,0.28446],"tcp_start":[0.45728,0.10391,0.19466],"tcp_to_object_dist_end":0.27027,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":777.0,"n_steps_budget":1000.0,"object_pos_end":[0.50748,0.09224,0.02758],"object_pos_start":[0.49394,0.03467,0.01602],"object_to_goal_dist_end":0.15094,"object_to_goal_dist_start":0.2019,"object_z_max":0.02806,"peak_contact_force":369.78979,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":6290.0,"raw_peak_contact_force":801.34308,"subtask_id":"place_goal","tcp_end":[0.60724,0.17363,0.2936],"tcp_start":[0.52536,0.03509,0.28446],"tcp_to_object_dist_end":0.29555,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51651,0.09332,0.02371],"object_pos_start":[0.50748,0.09224,0.02758],"object_to_goal_dist_end":0.14703,"object_to_goal_dist_start":0.15094,"object_z_max":0.02779,"peak_contact_force":354.54953,"phase_name":"descend_at_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":9462.0,"raw_peak_contact_force":614.35698,"subtask_id":"place_goal","tcp_end":[0.59875,0.15811,0.29049],"tcp_start":[0.60724,0.17363,0.2936],"tcp_to_object_dist_end":0.28659,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5122,0.09411,0.02602],"object_pos_start":[0.51651,0.09332,0.02371],"object_to_goal_dist_end":0.14782,"object_to_goal_dist_start":0.14703,"object_z_max":0.02606,"peak_contact_force":0.1242,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1197.0,"raw_peak_contact_force":138.99849,"tcp_end":[0.59899,0.15768,0.31692],"tcp_start":[0.59875,0.15811,0.29049],"tcp_to_object_dist_end":0.31015,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
```