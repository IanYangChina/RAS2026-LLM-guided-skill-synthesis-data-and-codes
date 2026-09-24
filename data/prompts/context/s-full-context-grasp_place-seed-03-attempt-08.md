## Search State

- **Seed**: 3
- **Iteration**: 9 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 8 | approach → descend → contact → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 9 | -0.3745 | 0.16 | ❌ rejected |
| 7 | approach → descend → contact → grasp → lift → approach → descend → release | arc_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 9 | -0.3241 | 0.22 | ✅ accepted |
| 6 | approach → contact → grasp → lift → retract → approach → descend → release | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 9 | -0.3276 | 0.18 | ❌ rejected |
| 5 | approach → descend → contact → grasp → lift → approach → descend → release | arc_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 9 | -0.0332 | 0.21 | ❌ rejected |
| 4 | approach → descend → contact → grasp → lift → approach → descend → release | arc_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 9 | -0.3230 | 0.21 | ✅ accepted |

**Proposal policy**: task_score is 0.16 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.374) — your mutation base

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

- **Composite score**: -0.374
- **task_score** (E): 0.163
- **fitness_score**: 0.131  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.125
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.630

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_pregrasp | 0.33 | 1.00 | 0.0894 |
| descend_to_contact | 0.00 | 1.00 | 0.0267 |
| make_contact | 1.00 | 1.00 | 0.0002 |
| grasp_object | 1.00 | 1.00 | 0.0000 |
| lift_object | 0.33 | 1.00 | 0.0477 |
| transport_to_goal | 0.33 | 1.00 | 0.4059 |
| descend_to_place | 0.00 | 1.00 | 0.0790 |
| release_object | 1.00 | 1.00 | 0.0276 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_pregrasp | approach | 0.33 / step_budget | (0.500, -0.000, 0.301)→(0.509, -0.005, 0.246) | (0.511, 0.002, 0.030)→(0.470, 0.006, 0.016) | 0.244→0.269 | 1.00 / 5.000 | 275.431 | 1424.131 |
| descend_to_contact | descend | 0.00 / step_budget | (0.509, -0.005, 0.246)→(0.521, -0.005, 0.260) | (0.470, 0.006, 0.016)→(0.470, -0.004, 0.015) | 0.269→0.276 | 1.00 / 5.000 | 491.271 | 816.347 |
| make_contact | contact | 1.00 / force_exceeded | (0.521, -0.005, 0.260)→(0.521, -0.005, 0.260) | (0.470, -0.004, 0.015)→(0.470, -0.004, 0.015) | 0.276→0.276 | 1.00 / 5.000 | 189.663 | 189.663 |
| grasp_object | grasp | 1.00 / step_budget | (0.522, -0.005, 0.260)→(0.522, -0.005, 0.260) | (0.470, -0.004, 0.015)→(0.469, -0.006, 0.016) | 0.276→0.278 | 1.00 / 9.000 | 514.377 | 709.929 |
| lift_object | lift | 0.33 / step_budget | (0.522, -0.005, 0.260)→(0.485, -0.013, 0.249) | (0.469, -0.006, 0.016)→(0.464, -0.011, 0.015) | 0.279→0.285 | 1.00 / 10.667 | 182226.696 | 524.003 |
| transport_to_goal | approach | 0.33 / step_budget | (0.485, -0.013, 0.249)→(0.502, 0.232, 0.502) | (0.464, -0.011, 0.015)→(0.458, 0.013, 0.016) | 0.285→0.274 | 1.00 / 8.667 | 3393.162 | 774.008 |
| descend_to_place | descend | 0.00 / step_budget | (0.502, 0.232, 0.502)→(0.517, 0.169, 0.502) | (0.458, 0.013, 0.016)→(0.458, 0.013, 0.016) | 0.274→0.274 | 1.00 / 9.333 | 91099.707 | 487.747 |
| release_object | release | 1.00 / step_budget | (0.517, 0.169, 0.502)→(0.519, 0.170, 0.529) | (0.458, 0.013, 0.016)→(0.458, 0.013, 0.016) | 0.274→0.274 | 1.00 / 4.000 | 0.123 | 71.128 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 0.000
- place_accuracy: 0.000
- lift_clearance: 0.000
- transport_retention: None
- terminal_score: 0.188
- phase_score: 0.349
- phase_breakdown.lift_clear_score: 0.109
- phase_breakdown.reach_pregrasp_score: 0.059
- phase_breakdown.grasp_contact_score: 1.000
- phase_breakdown.place_goal_score: 0.025
- grasp_place_fitness: 0.132

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.132
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.188
- **Median Q (composite search score)**: -0.375
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.336


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":3.0,"average_failure_rate":0.03061,"average_mean_iterations":14.09184,"average_solve_count":98.0,"average_success_count":95.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_pregrasp.approach_speed":0.60963,"descend_to_contact.descend_speed":0.54277,"descend_to_contact.descend_tolerance":0.027,"descend_to_place.place_tolerance":0.01202,"lift_object.lift_height":0.14192,"make_contact.contact_force":4.34155,"release_object.release_duration":1.53259,"transport_to_goal.arc_height":0.14552,"transport_to_goal.transport_speed":0.54642},"optimized_scores":{"best_composite_score":-0.37467,"best_fitness_score":0.13033,"best_task_score":0.12482},"replay_outcomes":[{"contacts":{"omitted_contact_groups":8,"reported_contact_groups":[{"body_a":"world","body_b":"link7","contact_count":25.0,"contact_point_centroid":[0.52626,-0.00195,-0.00352],"force_p95":206.22407,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1370.42681,"mean_force":65.12828,"phase_index":0.0,"phase_name":"approach_pregrasp","phase_type":"approach","tcp_position_centroid":[0.37621,-0.00451,0.04558]},{"body_a":"world","body_b":"link6","contact_count":888.0,"contact_point_centroid":[0.63567,-0.01047,-0.00045],"force_p95":220.50176,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1363.41057,"mean_force":208.35862,"phase_index":0.0,"phase_name":"approach_pregrasp","phase_type":"approach","tcp_position_centroid":[0.39898,-0.01,0.12799]},{"body_a":"world","body_b":"link6","contact_count":578.0,"contact_point_centroid":[0.56139,0.01612,-0.00015],"force_p95":777.72585,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1304.5976,"mean_force":316.21655,"phase_index":5.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.36175,-0.02891,0.17254]},{"body_a":"world","body_b":"link6","contact_count":960.0,"contact_point_centroid":[0.61543,-0.02412,-0.00024],"force_p95":423.40395,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":882.88725,"mean_force":267.24305,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.42348,-0.02599,0.19753]},{"body_a":"world","body_b":"link6","contact_count":548.0,"contact_point_centroid":[0.64256,-0.03288,-0.00013],"force_p95":84.84738,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":725.90639,"mean_force":74.95862,"phase_index":3.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.45452,-0.03495,0.20752]},{"body_a":"world","body_b":"link6","contact_count":480.0,"contact_point_centroid":[0.60304,-0.04022,-0.00026],"force_p95":230.47885,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":263.45976,"mean_force":197.06627,"phase_index":4.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.39261,-0.05024,0.17433]},{"body_a":"world","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.64162,-0.03255,-0.00026],"force_p95":172.36769,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":172.36769,"mean_force":172.36769,"phase_index":2.0,"phase_name":"make_contact","phase_type":"contact","tcp_position_centroid":[0.45467,-0.03468,0.20824]},{"body_a":"link5","body_b":"hand","contact_count":69.0,"contact_point_centroid":[0.49745,0.19247,0.18876],"force_p95":131.31795,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":137.54038,"mean_force":39.54403,"phase_index":5.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.45542,0.09545,0.18037]},{"body_a":"grasp_target","body_b":"hand","contact_count":40.0,"contact_point_centroid":[0.44486,-0.01974,0.03431],"force_p95":3.48803,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.7181,"mean_force":1.21575,"phase_index":0.0,"phase_name":"approach_pregrasp","phase_type":"approach","tcp_position_centroid":[0.38581,-0.00449,0.04704]},{"body_a":"world","body_b":"grasp_target","contact_count":3954.0,"contact_point_centroid":[0.42065,-0.02654,-0.00211],"force_p95":0.13728,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.6447,"mean_force":0.13704,"phase_index":0.0,"phase_name":"approach_pregrasp","phase_type":"approach","tcp_position_centroid":[0.40991,-0.00924,0.13672]},{"body_a":"grasp_target","body_b":"link7","contact_count":208.0,"contact_point_centroid":[0.43946,-0.03573,0.03953],"force_p95":0.73896,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.15358,"mean_force":0.25642,"phase_index":5.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.31801,-0.0756,0.12549]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8.0,"contact_point_centroid":[0.43942,-0.04515,0.05583],"force_p95":0.61672,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.623,"mean_force":0.50977,"phase_index":0.0,"phase_name":"approach_pregrasp","phase_type":"approach","tcp_position_centroid":[0.42779,-0.00439,0.06073]},{"body_a":"world","body_b":"grasp_target","contact_count":3400.0,"contact_point_centroid":[0.41147,-0.00371,-0.00232],"force_p95":0.28797,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.58066,"mean_force":0.14787,"phase_index":5.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.37721,0.00077,0.22523]},{"body_a":"world","body_b":"grasp_target","contact_count":3856.0,"contact_point_centroid":[0.41574,-0.02657,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.42353,-0.02599,0.19752]},{"body_a":"world","body_b":"grasp_target","contact_count":4.0,"contact_point_centroid":[0.41574,-0.02657,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":2.0,"phase_name":"make_contact","phase_type":"contact","tcp_position_centroid":[0.45467,-0.03468,0.20824]},{"body_a":"world","body_b":"grasp_target","contact_count":2200.0,"contact_point_centroid":[0.41574,-0.02657,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":3.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.45452,-0.03495,0.20752]}],"total_contact_groups":24},"final_pose_error":0.86153,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.40999,0.00986,0.01602],"final_tcp_position":[0.27686,0.17302,0.9191],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":273005.5869,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.41574,-0.02657,0.01602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.33273,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":205.06382,"phase_name":"approach_pregrasp","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4915.0,"raw_peak_contact_force":1370.42681,"subtask_id":"reach_pregrasp","tcp_end":[0.42025,-0.01929,0.17662],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16083,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":964.0,"n_steps_budget":1000.0,"object_pos_end":[0.41574,-0.02657,0.01602],"object_pos_start":[0.41574,-0.02657,0.01602],"object_to_goal_dist_end":0.33273,"object_to_goal_dist_start":0.33273,"object_z_max":0.01602,"peak_contact_force":350.02072,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4816.0,"raw_peak_contact_force":882.88725,"subtask_id":"reach_pregrasp","tcp_end":[0.45467,-0.03468,0.20824],"tcp_start":[0.42025,-0.01929,0.17662],"tcp_to_object_dist_end":0.19629,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.41574,-0.02657,0.01602],"object_pos_start":[0.41574,-0.02657,0.01602],"object_to_goal_dist_end":0.33273,"object_to_goal_dist_start":0.33273,"object_z_max":0.01602,"peak_contact_force":172.36769,"phase_name":"make_contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":5.0,"raw_peak_contact_force":172.36769,"subtask_id":"grasp_contact","tcp_end":[0.45462,-0.03475,0.20831],"tcp_start":[0.45467,-0.03468,0.20824],"tcp_to_object_dist_end":0.19635,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.41574,-0.02657,0.01602],"object_pos_start":[0.41574,-0.02657,0.01602],"object_to_goal_dist_end":0.33273,"object_to_goal_dist_start":0.33273,"object_z_max":0.01602,"peak_contact_force":85.86251,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":3499.0,"raw_peak_contact_force":725.90639,"subtask_id":"grasp_contact","tcp_end":[0.45452,-0.03497,0.20742],"tcp_start":[0.45452,-0.03497,0.20742],"tcp_to_object_dist_end":0.19547,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":485.0,"n_steps_budget":600.0,"object_pos_end":[0.41574,-0.02657,0.01602],"object_pos_start":[0.41574,-0.02657,0.01602],"object_to_goal_dist_end":0.33273,"object_to_goal_dist_start":0.33273,"object_z_max":0.01602,"peak_contact_force":273005.5869,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":4467.0,"raw_peak_contact_force":263.45976,"subtask_id":"lift_clear","tcp_end":[0.38207,-0.05414,0.17348],"tcp_start":[0.45452,-0.03497,0.20742],"tcp_to_object_dist_end":0.16336,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":961.0,"n_steps_budget":1000.0,"object_pos_end":[0.40999,0.00986,0.01602],"object_pos_start":[0.41574,-0.02657,0.01602],"object_to_goal_dist_end":0.31214,"object_to_goal_dist_start":0.33273,"object_z_max":0.0204,"peak_contact_force":0.12263,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8317.0,"raw_peak_contact_force":1304.5976,"subtask_id":"place_goal","tcp_end":[0.25797,0.37783,0.91343],"tcp_start":[0.38207,-0.05414,0.17348],"tcp_to_object_dist_end":0.98176,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.40999,0.00986,0.01602],"object_pos_start":[0.40999,0.00986,0.01602],"object_to_goal_dist_end":0.31214,"object_to_goal_dist_start":0.31214,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8361.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_goal","tcp_end":[0.27686,0.17302,0.9191],"tcp_start":[0.25797,0.37783,0.91343],"tcp_to_object_dist_end":0.92731,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.40999,0.00986,0.01602],"object_pos_start":[0.40999,0.00986,0.01602],"object_to_goal_dist_end":0.31214,"object_to_goal_dist_start":0.31214,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1032.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.28213,0.17668,0.94968],"tcp_start":[0.27686,0.17302,0.9191],"tcp_to_object_dist_end":0.95703,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":6.58621,"average_solve_count":116.0,"average_success_count":116.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_pregrasp.approach_speed":0.88289,"descend_to_contact.descend_speed":0.317,"descend_to_contact.descend_tolerance":0.03089,"descend_to_place.place_tolerance":0.02171,"lift_object.lift_height":0.10267,"make_contact.contact_force":9.39017,"release_object.release_duration":1.10995,"transport_to_goal.arc_height":0.15205,"transport_to_goal.transport_speed":0.69944},"optimized_scores":{"best_composite_score":-0.37558,"best_fitness_score":0.12942,"best_task_score":0.17746},"replay_outcomes":[{"contacts":{"omitted_contact_groups":17,"reported_contact_groups":[{"body_a":"world","body_b":"link7","contact_count":24.0,"contact_point_centroid":[0.54212,0.00334,-0.00362],"force_p95":219.08892,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1378.67,"mean_force":68.18424,"phase_index":0.0,"phase_name":"approach_pregrasp","phase_type":"approach","tcp_position_centroid":[0.39232,-2e-05,0.04508]},{"body_a":"world","body_b":"link6","contact_count":853.0,"contact_point_centroid":[0.65476,-0.0083,-0.00038],"force_p95":401.66554,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1367.39561,"mean_force":223.86462,"phase_index":0.0,"phase_name":"approach_pregrasp","phase_type":"approach","tcp_position_centroid":[0.45308,0.00314,0.16523]},{"body_a":"world","body_b":"link6","contact_count":845.0,"contact_point_centroid":[0.64601,0.14761,-0.00031],"force_p95":524.15749,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":885.35757,"mean_force":375.43739,"phase_index":6.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.64845,0.15219,0.29367]},{"body_a":"world","body_b":"link6","contact_count":976.0,"contact_point_centroid":[0.5972,-0.03223,-0.00028],"force_p95":591.78676,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":826.54819,"mean_force":421.36709,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.5498,-0.0182,0.28863]},{"body_a":"world","body_b":"link6","contact_count":543.0,"contact_point_centroid":[0.64266,-0.04329,-0.00014],"force_p95":84.99682,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":722.81161,"mean_force":74.65653,"phase_index":3.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.56804,-0.01342,0.28039]},{"body_a":"world","body_b":"link6","contact_count":974.0,"contact_point_centroid":[0.58231,-0.02507,-0.00031],"force_p95":514.90416,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":591.39391,"mean_force":384.70293,"phase_index":4.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.54429,-0.0118,0.29078]},{"body_a":"link5","body_b":"hand","contact_count":920.0,"contact_point_centroid":[0.50691,-0.1003,0.23589],"force_p95":243.87849,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":277.1361,"mean_force":88.28078,"phase_index":4.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.54335,-0.01108,0.29082]},{"body_a":"link5","body_b":"hand","contact_count":544.0,"contact_point_centroid":[0.54086,-0.1081,0.22831],"force_p95":23.80536,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":272.54718,"mean_force":24.00353,"phase_index":3.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.56804,-0.01342,0.28039]},{"body_a":"world","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.64225,-0.04394,-0.00027],"force_p95":200.22472,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":200.22472,"mean_force":200.22472,"phase_index":2.0,"phase_name":"make_contact","phase_type":"contact","tcp_position_centroid":[0.56763,-0.01338,0.28004]},{"body_a":"world","body_b":"link6","contact_count":3.0,"contact_point_centroid":[0.60754,-0.02801,-0.00018],"force_p95":184.06873,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":184.36538,"mean_force":176.21247,"phase_index":5.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.55007,0.00703,0.28632]},{"body_a":"link5","body_b":"hand","contact_count":867.0,"contact_point_centroid":[0.51726,-0.10802,0.233],"force_p95":75.19875,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":175.29205,"mean_force":55.30479,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.54952,-0.01708,0.28814]},{"body_a":"world","body_b":"link6","contact_count":88.0,"contact_point_centroid":[0.66894,0.15425,-0.00013],"force_p95":77.21582,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":105.16961,"mean_force":56.30998,"phase_index":7.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.65649,0.15692,0.29394]},{"body_a":"grasp_target","body_b":"link7","contact_count":179.0,"contact_point_centroid":[0.52184,0.00254,0.03269],"force_p95":3.61564,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":5.34988,"mean_force":0.76991,"phase_index":0.0,"phase_name":"approach_pregrasp","phase_type":"approach","tcp_position_centroid":[0.40585,0.0001,0.09178]},{"body_a":"grasp_target","body_b":"hand","contact_count":117.0,"contact_point_centroid":[0.50542,-0.00033,0.04506],"force_p95":2.26929,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.25471,"mean_force":0.96245,"phase_index":0.0,"phase_name":"approach_pregrasp","phase_type":"approach","tcp_position_centroid":[0.40209,6e-05,0.07873]},{"body_a":"world","body_b":"grasp_target","contact_count":3732.0,"contact_point_centroid":[0.51384,0.00344,-0.00231],"force_p95":0.34808,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.17129,"mean_force":0.15728,"phase_index":0.0,"phase_name":"approach_pregrasp","phase_type":"approach","tcp_position_centroid":[0.46372,0.00374,0.17619]},{"body_a":"grasp_target","body_b":"link6","contact_count":576.0,"contact_point_centroid":[0.53141,-0.00364,0.03641],"force_p95":0.32312,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.62457,"mean_force":0.20073,"phase_index":4.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.54156,-0.0196,0.29227]}],"total_contact_groups":33},"final_pose_error":0.08297,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.49302,0.04537,0.01602],"final_tcp_position":[0.6565,0.1573,0.29359],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":273014.95941,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50767,0.00379,0.01602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.27212,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":284.02598,"phase_name":"approach_pregrasp","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4994.0,"raw_peak_contact_force":1378.67,"subtask_id":"reach_pregrasp","tcp_end":[0.56575,-0.01249,0.28643],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.27706,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":6.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50583,0.00681,0.01602],"object_pos_start":[0.50767,0.00379,0.01602],"object_to_goal_dist_end":0.27137,"object_to_goal_dist_start":0.27212,"object_z_max":0.01605,"peak_contact_force":424.60402,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":6231.0,"raw_peak_contact_force":826.54819,"subtask_id":"reach_pregrasp","tcp_end":[0.56763,-0.01338,0.28004],"tcp_start":[0.56575,-0.01249,0.28643],"tcp_to_object_dist_end":0.2719,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":6.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.50583,0.00681,0.01602],"object_pos_start":[0.50583,0.00681,0.01602],"object_to_goal_dist_end":0.27137,"object_to_goal_dist_start":0.27137,"object_z_max":0.01602,"peak_contact_force":200.22472,"phase_name":"make_contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":6.0,"raw_peak_contact_force":200.22472,"subtask_id":"grasp_contact","tcp_end":[0.56774,-0.01354,0.28027],"tcp_start":[0.56763,-0.01338,0.28004],"tcp_to_object_dist_end":0.27217,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.50583,0.00681,0.01602],"object_pos_start":[0.50583,0.00681,0.01602],"object_to_goal_dist_end":0.27137,"object_to_goal_dist_start":0.27137,"object_z_max":0.01602,"peak_contact_force":1366.84211,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":4082.0,"raw_peak_contact_force":722.81161,"subtask_id":"grasp_contact","tcp_end":[0.56807,-0.01338,0.28039],"tcp_start":[0.56807,-0.01339,0.28039],"tcp_to_object_dist_end":0.27235,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":11.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50179,0.01106,0.01602],"object_pos_start":[0.50583,0.00681,0.01602],"object_to_goal_dist_end":0.27118,"object_to_goal_dist_start":0.27137,"object_z_max":0.01607,"peak_contact_force":273014.95941,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":10906.0,"raw_peak_contact_force":591.39391,"subtask_id":"lift_clear","tcp_end":[0.54994,0.00713,0.28601],"tcp_start":[0.56807,-0.01338,0.28039],"tcp_to_object_dist_end":0.27428,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":414.0,"n_steps_budget":1000.0,"object_pos_end":[0.49302,0.04537,0.01602],"object_pos_start":[0.50179,0.01106,0.01602],"object_to_goal_dist_end":0.25935,"object_to_goal_dist_start":0.27118,"object_z_max":0.01962,"peak_contact_force":9748.88091,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3376.0,"raw_peak_contact_force":184.36538,"subtask_id":"place_goal","tcp_end":[0.639,0.14321,0.30045],"tcp_start":[0.54994,0.00713,0.28601],"tcp_to_object_dist_end":0.33434,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":865.0,"n_steps_budget":1000.0,"object_pos_end":[0.49302,0.04537,0.01602],"object_pos_start":[0.49302,0.04537,0.01602],"object_to_goal_dist_end":0.25935,"object_to_goal_dist_start":0.25935,"object_z_max":0.01602,"peak_contact_force":299.03262,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8019.0,"raw_peak_contact_force":885.35757,"subtask_id":"place_goal","tcp_end":[0.6565,0.1573,0.29359],"tcp_start":[0.639,0.14321,0.30045],"tcp_to_object_dist_end":0.34103,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.49302,0.04537,0.01602],"object_pos_start":[0.49302,0.04537,0.01602],"object_to_goal_dist_end":0.25935,"object_to_goal_dist_start":0.25935,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1120.0,"raw_peak_contact_force":105.16961,"tcp_end":[0.65672,0.15715,0.31886],"tcp_start":[0.6565,0.1573,0.29359],"tcp_to_object_dist_end":0.36195,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":5.22222,"average_solve_count":117.0,"average_success_count":117.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_pregrasp.approach_speed":0.87448,"descend_to_contact.descend_speed":0.20795,"descend_to_contact.descend_tolerance":0.0346,"descend_to_place.place_tolerance":0.00513,"lift_object.lift_height":0.10983,"make_contact.contact_force":6.37499,"release_object.release_duration":1.55424,"transport_to_goal.arc_height":0.14628,"transport_to_goal.transport_speed":0.76974},"optimized_scores":{"best_composite_score":-0.37318,"best_fitness_score":0.13182,"best_task_score":0.18782},"replay_outcomes":[{"contacts":{"omitted_contact_groups":19,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":813.0,"contact_point_centroid":[0.65633,0.01567,-0.0004],"force_p95":469.26069,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1523.29478,"mean_force":243.50591,"phase_index":0.0,"phase_name":"approach_pregrasp","phase_type":"approach","tcp_position_centroid":[0.43364,0.00941,0.14905]},{"body_a":"world","body_b":"link6","contact_count":338.0,"contact_point_centroid":[0.59541,0.16633,-0.00031],"force_p95":742.07278,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":833.06004,"mean_force":516.73914,"phase_index":5.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.60024,0.16108,0.29354]},{"body_a":"world","body_b":"link6","contact_count":716.0,"contact_point_centroid":[0.5606,0.05839,-0.00027],"force_p95":542.52954,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":739.60425,"mean_force":351.18001,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.53163,0.03504,0.29067]},{"body_a":"world","body_b":"link5","contact_count":152.0,"contact_point_centroid":[0.45951,0.04284,-0.00025],"force_p95":675.685,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":717.15513,"mean_force":471.26836,"phase_index":4.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.52204,0.01074,0.28807]},{"body_a":"world","body_b":"link5","contact_count":443.0,"contact_point_centroid":[0.47601,0.05298,-0.00029],"force_p95":698.06931,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":711.96165,"mean_force":547.97228,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.53504,0.0335,0.2891]},{"body_a":"world","body_b":"link5","contact_count":545.0,"contact_point_centroid":[0.49405,0.05497,-0.00014],"force_p95":103.00894,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":681.06876,"mean_force":96.12149,"phase_index":3.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.5425,0.03391,0.29157]},{"body_a":"world","body_b":"link6","contact_count":915.0,"contact_point_centroid":[0.54674,0.04524,-0.0003],"force_p95":529.21437,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":600.70693,"mean_force":376.86904,"phase_index":4.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.51956,0.0296,0.29156]},{"body_a":"world","body_b":"link6","contact_count":994.0,"contact_point_centroid":[0.61232,0.18669,-0.00031],"force_p95":423.8124,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":577.75989,"mean_force":328.26134,"phase_index":6.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.60702,0.17689,0.29363]},{"body_a":"world","body_b":"link5","contact_count":24.0,"contact_point_centroid":[0.541,0.13469,-0.00023],"force_p95":433.32257,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":467.73934,"mean_force":340.56389,"phase_index":0.0,"phase_name":"approach_pregrasp","phase_type":"approach","tcp_position_centroid":[0.52625,0.00138,0.25371]},{"body_a":"world","body_b":"link7","contact_count":23.0,"contact_point_centroid":[0.53864,0.00898,-0.00376],"force_p95":0.0,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":250.36318,"mean_force":10.88536,"phase_index":0.0,"phase_name":"approach_pregrasp","phase_type":"approach","tcp_position_centroid":[0.38915,0.00476,0.04476]},{"body_a":"world","body_b":"link5","contact_count":3.0,"contact_point_centroid":[0.46447,0.04375,-0.00023],"force_p95":205.28327,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":205.74852,"mean_force":199.9419,"phase_index":5.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52311,0.00752,0.2885]},{"body_a":"world","body_b":"link5","contact_count":1.0,"contact_point_centroid":[0.49403,0.0564,-0.00034],"force_p95":196.398,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":196.398,"mean_force":196.398,"phase_index":2.0,"phase_name":"make_contact","phase_type":"contact","tcp_position_centroid":[0.54207,0.03443,0.2912]},{"body_a":"link5","body_b":"hand","contact_count":774.0,"contact_point_centroid":[0.43202,0.05213,0.22222],"force_p95":74.23274,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":172.01815,"mean_force":36.57403,"phase_index":4.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.51766,0.02722,0.29129]},{"body_a":"link5","body_b":"hand","contact_count":184.0,"contact_point_centroid":[0.43959,0.06403,0.21589],"force_p95":78.62539,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":123.44657,"mean_force":44.45091,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.5221,0.04185,0.29011]},{"body_a":"world","body_b":"link6","contact_count":86.0,"contact_point_centroid":[0.62625,0.18938,-0.00014],"force_p95":78.07259,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":108.09078,"mean_force":57.64809,"phase_index":7.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.61651,0.17728,0.29328]},{"body_a":"grasp_target","body_b":"link7","contact_count":217.0,"contact_point_centroid":[0.51074,0.01487,0.0373],"force_p95":4.00923,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":5.99094,"mean_force":0.73322,"phase_index":0.0,"phase_name":"approach_pregrasp","phase_type":"approach","tcp_position_centroid":[0.40362,0.00563,0.09733]}],"total_contact_groups":35},"final_pose_error":0.16551,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.4722,-0.01562,0.01602],"final_tcp_position":[0.61666,0.177,0.2929],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":272999.96717,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.48693,0.03928,0.01602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.20252,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":337.20356,"phase_name":"approach_pregrasp","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4768.0,"raw_peak_contact_force":1523.29478,"subtask_id":"reach_pregrasp","tcp_end":[0.53971,0.01723,0.27441],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.26465,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.48867,0.00897,0.01431],"object_pos_start":[0.48693,0.03928,0.01602],"object_to_goal_dist_end":0.22428,"object_to_goal_dist_start":0.20252,"object_z_max":0.0168,"peak_contact_force":699.18753,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5315.0,"raw_peak_contact_force":739.60425,"subtask_id":"reach_pregrasp","tcp_end":[0.54207,0.03443,0.2912],"tcp_start":[0.53971,0.01723,0.27441],"tcp_to_object_dist_end":0.28314,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.48863,0.00886,0.01435],"object_pos_start":[0.48867,0.00897,0.01431],"object_to_goal_dist_end":0.22436,"object_to_goal_dist_start":0.22428,"object_z_max":0.01431,"peak_contact_force":196.398,"phase_name":"make_contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":4.0,"raw_peak_contact_force":196.398,"subtask_id":"grasp_contact","tcp_end":[0.54213,0.03453,0.29139],"tcp_start":[0.54207,0.03443,0.2912],"tcp_to_object_dist_end":0.28332,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.48613,0.00222,0.01614],"object_pos_start":[0.48863,0.00886,0.01435],"object_to_goal_dist_end":0.22995,"object_to_goal_dist_start":0.22436,"object_z_max":0.01614,"peak_contact_force":90.4264,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":2935.0,"raw_peak_contact_force":681.06876,"subtask_id":"grasp_contact","tcp_end":[0.54258,0.03379,0.29159],"tcp_start":[0.54258,0.03381,0.29159],"tcp_to_object_dist_end":0.28294,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":11.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47467,-0.01658,0.01411],"object_pos_start":[0.48569,0.00053,0.01591],"object_to_goal_dist_end":0.25103,"object_to_goal_dist_start":0.23156,"object_z_max":0.01795,"peak_contact_force":659.54167,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":10077.0,"raw_peak_contact_force":717.15513,"subtask_id":"lift_clear","tcp_end":[0.52305,0.00748,0.28826],"tcp_start":[0.54258,0.03379,0.29159],"tcp_to_object_dist_end":0.27942,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":675.0,"n_steps_budget":1000.0,"object_pos_end":[0.4722,-0.01562,0.01602],"object_pos_start":[0.47467,-0.01658,0.01411],"object_to_goal_dist_end":0.25084,"object_to_goal_dist_start":0.25103,"object_z_max":0.02113,"peak_contact_force":430.48103,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":5679.0,"raw_peak_contact_force":833.06004,"subtask_id":"place_goal","tcp_end":[0.60904,0.17543,0.29318],"tcp_start":[0.52305,0.00748,0.28826],"tcp_to_object_dist_end":0.36338,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.4722,-0.01562,0.01602],"object_pos_start":[0.4722,-0.01562,0.01602],"object_to_goal_dist_end":0.25084,"object_to_goal_dist_start":0.25084,"object_z_max":0.01602,"peak_contact_force":272999.96717,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":9159.0,"raw_peak_contact_force":577.75989,"subtask_id":"place_goal","tcp_end":[0.61666,0.177,0.2929],"tcp_start":[0.60904,0.17543,0.29318],"tcp_to_object_dist_end":0.36693,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.4722,-0.01562,0.01602],"object_pos_start":[0.4722,-0.01562,0.01602],"object_to_goal_dist_end":0.25084,"object_to_goal_dist_start":0.25084,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1107.0,"raw_peak_contact_force":108.09078,"tcp_end":[0.61669,0.17739,0.31907],"tcp_start":[0.61666,0.177,0.2929],"tcp_to_object_dist_end":0.38726,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
```