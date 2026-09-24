## Search State

- **Seed**: 3
- **Iteration**: 11 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 10 | retract → approach → contact → grasp → lift → approach → descend → release | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 9 | -0.3474 | 0.27 | ✅ accepted |
| 9 | approach → descend → contact → grasp → lift → approach → descend → release | arc_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 9 | -0.3300 | 0.20 | ❌ rejected |
| 8 | approach → descend → contact → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 9 | -0.3745 | 0.16 | ❌ rejected |
| 7 | approach → descend → contact → grasp → lift → approach → descend → release | arc_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 9 | -0.3241 | 0.22 | ✅ accepted |
| 6 | approach → contact → grasp → lift → retract → approach → descend → release | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 9 | -0.3276 | 0.18 | ❌ rejected |

**Proposal policy**: task_score is 0.27 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.347) — your mutation base

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

- **Composite score**: -0.347
- **task_score** (E): 0.270
- **fitness_score**: 0.158  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.125
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.630

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| retract_up | 1.00 | 1.00 | 0.2099 |
| approach_object | 0.00 | 1.00 | 0.4394 |
| descend_contact | 1.00 | 1.00 | 0.0009 |
| grasp_object | 1.00 | 1.00 | 0.0000 |
| lift_object | 0.00 | 1.00 | 0.3638 |
| approach_goal | 0.33 | 1.00 | 0.2831 |
| descend_at_goal | 0.00 | 1.00 | 0.0735 |
| release_object | 1.00 | 1.00 | 0.0232 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| retract_up | retract | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.500, 0.000, 0.511) | (0.511, 0.002, 0.030)→(0.511, 0.002, 0.026) | 0.244→0.246 | 1.00 / 4.000 | 15.752 | 0.138 |
| approach_object | approach | 0.00 / step_budget | (0.500, 0.000, 0.511)→(0.813, 0.101, 0.221) | (0.511, 0.002, 0.026)→(0.511, 0.002, 0.026) | 0.246→0.246 | 1.00 / 4.000 | 0.123 | 0.123 |
| descend_contact | contact | 1.00 / force_exceeded | (0.813, 0.101, 0.221)→(0.814, 0.102, 0.221) | (0.511, 0.002, 0.026)→(0.511, 0.002, 0.026) | 0.246→0.246 | 1.00 / 4.000 | 553.519 | 0.123 |
| grasp_object | grasp | 1.00 / step_budget | (0.810, 0.100, 0.201)→(0.810, 0.100, 0.201) | (0.511, 0.002, 0.026)→(0.511, 0.002, 0.026) | 0.246→0.246 | 1.00 / 8.333 | 94251.104 | 0.123 |
| lift_object | lift | 0.00 / step_budget | (0.810, 0.100, 0.201)→(0.627, 0.236, 0.256) | (0.511, 0.002, 0.026)→(0.525, 0.048, 0.019) | 0.246→0.214 | 1.00 / 8.333 | 97.826 | 2314.478 |
| approach_goal | approach | 0.33 / step_budget | (0.627, 0.236, 0.256)→(0.674, 0.323, 0.337) | (0.525, 0.048, 0.019)→(0.514, 0.073, 0.019) | 0.214→0.213 | 1.00 / 8.333 | 130.490 | 1193.513 |
| descend_at_goal | descend | 0.00 / step_budget | (0.674, 0.323, 0.337)→(0.655, 0.279, 0.323) | (0.514, 0.073, 0.019)→(0.513, 0.073, 0.019) | 0.213→0.214 | 1.00 / 9.333 | 91177.104 | 334.772 |
| release_object | release | 1.00 / step_budget | (0.655, 0.279, 0.323)→(0.656, 0.280, 0.346) | (0.513, 0.073, 0.019)→(0.513, 0.073, 0.019) | 0.214→0.214 | 1.00 / 4.000 | 0.124 | 145.056 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 0.000
- place_accuracy: 0.000
- lift_clearance: 0.000
- transport_retention: 0.000
- terminal_score: 0.463
- phase_score: 0.304
- phase_breakdown.lift_clear_score: 0.000
- phase_breakdown.reach_pregrasp_score: 0.001
- phase_breakdown.grasp_contact_score: 1.000
- phase_breakdown.place_goal_score: 0.019
- grasp_place_fitness: 0.251

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.251
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.463
- **Median Q (composite search score)**: -0.383
- **K-run variance**: 0.0044
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.333


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":83.0,"average_failure_rate":0.332,"average_mean_iterations":71.78,"average_solve_count":250.0,"average_success_count":167.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_z":0.13489,"approach_goal.goal_arc_height":0.14726,"approach_object.approach_z":0.20543,"approach_object.arc_height":0.21751,"descend_at_goal.descend_goal_tolerance":0.01447,"descend_contact.contact_force":12.48779,"lift_object.lift_height":0.12926,"release_object.release_duration":1.70849,"retract_up.retract_height":0.20963},"optimized_scores":{"best_composite_score":-0.40481,"best_fitness_score":0.10019,"best_task_score":0.15928},"replay_outcomes":[{"contacts":{"omitted_contact_groups":12,"reported_contact_groups":[{"body_a":"link1","body_b":"link5","contact_count":40.0,"contact_point_centroid":[0.04275,-0.02643,0.1658],"force_p95":2804.44749,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":3663.41867,"mean_force":619.71116,"phase_index":4.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.22321,0.16288,0.00184]},{"body_a":"world","body_b":"link5","contact_count":26.0,"contact_point_centroid":[0.33243,-0.20123,-0.006],"force_p95":1068.19795,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":3275.76349,"mean_force":214.52153,"phase_index":4.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.40037,-0.43277,0.09196]},{"body_a":"world","body_b":"link6","contact_count":175.0,"contact_point_centroid":[0.52341,-0.11094,-0.00148],"force_p95":1256.60178,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":2398.35114,"mean_force":543.54332,"phase_index":4.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.51873,-0.19179,0.25082]},{"body_a":"world","body_b":"hand","contact_count":59.0,"contact_point_centroid":[0.29221,-0.0164,-0.00508],"force_p95":1439.43451,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1848.00379,"mean_force":333.94947,"phase_index":4.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.29196,0.00568,0.02738]},{"body_a":"world","body_b":"link7","contact_count":28.0,"contact_point_centroid":[0.28482,-0.06732,-0.00064],"force_p95":1245.18619,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1375.13441,"mean_force":431.23536,"phase_index":4.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.27833,-0.0305,0.0205]},{"body_a":"world","body_b":"link6","contact_count":73.0,"contact_point_centroid":[0.61247,0.18647,-0.00039],"force_p95":743.33121,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":995.20459,"mean_force":479.46612,"phase_index":5.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.62827,0.19468,0.2931]},{"body_a":"link5","body_b":"hand","contact_count":148.0,"contact_point_centroid":[0.4555,-0.10066,0.2431],"force_p95":457.74125,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":610.84932,"mean_force":315.89547,"phase_index":4.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.55241,-0.1211,0.29017]},{"body_a":"world","body_b":"link6","contact_count":998.0,"contact_point_centroid":[0.6349,0.21371,-0.00029],"force_p95":406.56315,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":561.87502,"mean_force":323.7666,"phase_index":6.0,"phase_name":"descend_at_goal","phase_type":"descend","tcp_position_centroid":[0.63747,0.20961,0.294]},{"body_a":"world","body_b":"link6","contact_count":89.0,"contact_point_centroid":[0.65631,0.22476,-0.0001],"force_p95":78.00934,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":139.72989,"mean_force":52.87832,"phase_index":7.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.64291,0.21243,0.29407]},{"body_a":"link5","body_b":"hand","contact_count":19.0,"contact_point_centroid":[0.46443,-0.07363,0.24778],"force_p95":32.12509,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":62.92141,"mean_force":14.62088,"phase_index":5.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.5642,-0.08145,0.29496]},{"body_a":"world","body_b":"right_finger","contact_count":359.0,"contact_point_centroid":[0.22027,0.16119,-0.00373],"force_p95":20.11497,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":35.62381,"mean_force":4.57781,"phase_index":4.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.2231,0.16414,-0.00162]},{"body_a":"world","body_b":"left_finger","contact_count":340.0,"contact_point_centroid":[0.22727,0.1614,-0.00356],"force_p95":20.45813,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":29.78761,"mean_force":5.12002,"phase_index":4.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.22318,0.16424,-0.00178]},{"body_a":"grasp_target","body_b":"link6","contact_count":137.0,"contact_point_centroid":[0.48095,-0.00941,0.0519],"force_p95":0.87435,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.09103,"mean_force":0.44228,"phase_index":4.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.55551,-0.11362,0.29088]},{"body_a":"grasp_target","body_b":"link6","contact_count":13.0,"contact_point_centroid":[0.48198,-0.00227,0.04325],"force_p95":0.81886,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.0643,"mean_force":0.4003,"phase_index":5.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.56412,-0.08183,0.29414]},{"body_a":"world","body_b":"grasp_target","contact_count":2040.0,"contact_point_centroid":[0.45844,-0.02425,-0.00251],"force_p95":0.5047,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.61466,"mean_force":0.16351,"phase_index":4.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.47058,-0.04597,0.16671]},{"body_a":"world","body_b":"grasp_target","contact_count":3893.0,"contact_point_centroid":[0.45827,0.01557,-0.0021],"force_p95":0.1237,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54289,"mean_force":0.12763,"phase_index":5.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.59663,0.0579,0.3637]}],"total_contact_groups":28},"final_pose_error":0.18013,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.45833,0.01638,0.01602],"final_tcp_position":[0.64306,0.21248,0.29373],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":273004.12082,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":606.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":23.41161,"phase_name":"retract_up","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2420.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.49936,0.0,0.49049],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.467,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_pregrasp","tcp_end":[0.79712,0.08862,0.17237],"tcp_start":[0.49936,0.0,0.49049],"tcp_to_object_dist_end":0.38633,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":433.25146,"phase_name":"descend_contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":4.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_contact","tcp_end":[0.79731,0.08888,0.17227],"tcp_start":[0.79712,0.08862,0.17237],"tcp_to_object_dist_end":0.38654,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":9749.06927,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":2977.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_contact","tcp_end":[0.7919,0.08818,0.15344],"tcp_start":[0.7919,0.08818,0.15344],"tcp_to_object_dist_end":0.37478,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":570.0,"n_steps_budget":1000.0,"object_pos_end":[0.4619,-0.00181,0.02155],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.28457,"object_to_goal_dist_start":0.30365,"object_z_max":0.02616,"peak_contact_force":292.3116,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":5469.0,"raw_peak_contact_force":3663.41867,"subtask_id":"lift_clear","tcp_end":[0.56383,-0.0831,0.29294],"tcp_start":[0.7919,0.08818,0.15344],"tcp_to_object_dist_end":0.30108,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.45833,0.01638,0.01602],"object_pos_start":[0.4619,-0.00181,0.02155],"object_to_goal_dist_end":0.27557,"object_to_goal_dist_start":0.28457,"object_z_max":0.02209,"peak_contact_force":391.22474,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8115.0,"raw_peak_contact_force":995.20459,"subtask_id":"place_goal","tcp_end":[0.63222,0.20834,0.29378],"tcp_start":[0.56383,-0.0831,0.29294],"tcp_to_object_dist_end":0.37979,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.45833,0.01638,0.01602],"object_pos_start":[0.45833,0.01638,0.01602],"object_to_goal_dist_end":0.27557,"object_to_goal_dist_start":0.27557,"object_z_max":0.01602,"peak_contact_force":299.18372,"phase_name":"descend_at_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":9144.0,"raw_peak_contact_force":561.87502,"subtask_id":"place_goal","tcp_end":[0.64306,0.21248,0.29373],"tcp_start":[0.63222,0.20834,0.29378],"tcp_to_object_dist_end":0.38692,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45833,0.01638,0.01602],"object_pos_start":[0.45833,0.01638,0.01602],"object_to_goal_dist_end":0.27557,"object_to_goal_dist_start":0.27557,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1103.0,"raw_peak_contact_force":139.72989,"tcp_end":[0.64328,0.21247,0.31854],"tcp_start":[0.64306,0.21248,0.29373],"tcp_to_object_dist_end":0.40518,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":82.0,"average_failure_rate":0.37104,"average_mean_iterations":80.49321,"average_solve_count":221.0,"average_success_count":139.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_z":0.13395,"approach_goal.goal_arc_height":0.12448,"approach_object.approach_z":0.16657,"approach_object.arc_height":0.2755,"descend_at_goal.descend_goal_tolerance":0.0149,"descend_contact.contact_force":8.02286,"lift_object.lift_height":0.15934,"release_object.release_duration":1.07491,"retract_up.retract_height":0.2098},"optimized_scores":{"best_composite_score":-0.38283,"best_fitness_score":0.12217,"best_task_score":0.18872},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"hand","contact_count":8.0,"contact_point_centroid":[0.51813,-0.4912,-0.00096],"force_p95":1420.5596,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1452.5183,"mean_force":1080.03443,"phase_index":4.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.60867,-0.519,0.03869]},{"body_a":"world","body_b":"grasp_target","contact_count":2424.0,"contact_point_centroid":[0.54431,0.00113,-0.00194],"force_p95":0.13067,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12283,"phase_index":0.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.49856,-1e-05,0.39489]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.79852,0.0608,0.24243]},{"body_a":"world","body_b":"grasp_target","contact_count":8.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":2.0,"phase_name":"descend_contact","phase_type":"contact","tcp_position_centroid":[0.82437,0.09819,0.20015]},{"body_a":"world","body_b":"grasp_target","contact_count":2200.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":3.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.8215,0.09263,0.1824]},{"body_a":"world","body_b":"grasp_target","contact_count":3960.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":4.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.35402,0.03506,0.42635]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.60588,0.52337,0.38592]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"descend_at_goal","phase_type":"descend","tcp_position_centroid":[0.62548,0.4443,0.37905]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.6341,0.4268,0.39311]},{"body_a":"left_finger","body_b":"right_finger","contact_count":774.0,"contact_point_centroid":[0.81884,0.09219,0.18091],"force_p95":0.01281,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01622,"mean_force":0.01067,"phase_index":3.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.82092,0.09238,0.17993]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4259.0,"contact_point_centroid":[0.62556,0.44437,0.37664],"force_p95":0.011,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01283,"mean_force":0.01047,"phase_index":6.0,"phase_name":"descend_at_goal","phase_type":"descend","tcp_position_centroid":[0.62549,0.4443,0.37902]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4286.0,"contact_point_centroid":[0.60563,0.52295,0.38368],"force_p95":0.01098,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01277,"mean_force":0.0104,"phase_index":5.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.60598,0.5229,0.38595]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4276.0,"contact_point_centroid":[0.35343,0.03464,0.42578],"force_p95":0.0109,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01274,"mean_force":0.01015,"phase_index":4.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.35346,0.03398,0.42627]},{"body_a":"left_finger","body_b":"right_finger","contact_count":229.0,"contact_point_centroid":[0.63355,0.42529,0.38673],"force_p95":0.01088,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0109,"mean_force":0.00979,"phase_index":7.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.63337,0.42521,0.38901]}],"total_contact_groups":14},"final_pose_error":0.33287,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.54431,0.00113,0.02602],"final_tcp_position":[0.6332,0.42466,0.38993],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":273004.12084,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":607.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":23.72054,"phase_name":"retract_up","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2424.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.49936,0.0,0.49088],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.46703,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_pregrasp","tcp_end":[0.82425,0.09818,0.20015],"tcp_start":[0.49936,0.0,0.49088],"tcp_to_object_dist_end":0.34367,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":2.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":834.90123,"phase_name":"descend_contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":8.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_contact","tcp_end":[0.82496,0.09819,0.20021],"tcp_start":[0.82425,0.09818,0.20015],"tcp_to_object_dist_end":0.34429,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":273004.12084,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":2974.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_contact","tcp_end":[0.82092,0.09238,0.17993],"tcp_start":[0.82092,0.09238,0.17993],"tcp_to_object_dist_end":0.32944,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":990.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":8244.0,"raw_peak_contact_force":1452.5183,"subtask_id":"lift_clear","tcp_end":[0.64678,0.33331,0.38756],"tcp_start":[0.82092,0.09238,0.17993],"tcp_to_object_dist_end":0.50155,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8286.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_goal","tcp_end":[0.61898,0.52774,0.3787],"tcp_start":[0.64678,0.33331,0.38756],"tcp_to_object_dist_end":0.63818,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":273003.63473,"phase_name":"descend_at_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8259.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_goal","tcp_end":[0.6332,0.42466,0.38993],"tcp_start":[0.61898,0.52774,0.3787],"tcp_to_object_dist_end":0.56543,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1029.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.63494,0.42812,0.41113],"tcp_start":[0.6332,0.42466,0.38993],"tcp_to_object_dist_end":0.5821,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":134.0,"average_failure_rate":0.52964,"average_mean_iterations":111.14229,"average_solve_count":253.0,"average_success_count":119.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_z":0.12582,"approach_goal.goal_arc_height":0.16202,"approach_object.approach_z":0.20539,"approach_object.arc_height":0.25053,"descend_at_goal.descend_goal_tolerance":0.01924,"descend_contact.contact_force":6.42934,"lift_object.lift_height":0.17228,"release_object.release_duration":0.92705,"retract_up.retract_height":0.26989},"optimized_scores":{"best_composite_score":-0.25447,"best_fitness_score":0.25053,"best_task_score":0.46315},"replay_outcomes":[{"contacts":{"omitted_contact_groups":14,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":30.0,"contact_point_centroid":[0.65581,0.33576,-0.0103],"force_p95":2110.8115,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":2585.21288,"mean_force":512.33881,"phase_index":5.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.79577,0.26195,0.21482]},{"body_a":"world","body_b":"link5","contact_count":28.0,"contact_point_centroid":[0.49893,0.1211,-0.00157],"force_p95":1812.76619,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1827.49684,"mean_force":1025.4473,"phase_index":4.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.69793,0.21892,0.01281]},{"body_a":"world","body_b":"hand","contact_count":91.0,"contact_point_centroid":[0.5831,0.1003,-0.00411],"force_p95":1168.32721,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1701.29007,"mean_force":736.50615,"phase_index":4.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.6595,0.06002,0.02985]},{"body_a":"world","body_b":"link5","contact_count":26.0,"contact_point_centroid":[0.61917,0.22536,-0.00335],"force_p95":1242.60307,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1496.76052,"mean_force":291.82962,"phase_index":5.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.74496,0.3257,0.16299]},{"body_a":"world","body_b":"hand","contact_count":22.0,"contact_point_centroid":[0.60896,0.39566,-0.00303],"force_p95":715.9993,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":743.4286,"mean_force":357.86112,"phase_index":5.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.63024,0.43824,-0.01527]},{"body_a":"world","body_b":"link5","contact_count":935.0,"contact_point_centroid":[0.61832,0.1884,-0.00024],"force_p95":269.12865,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":442.31795,"mean_force":230.17983,"phase_index":6.0,"phase_name":"descend_at_goal","phase_type":"descend","tcp_position_centroid":[0.71252,0.1848,0.28133]},{"body_a":"world","body_b":"link6","contact_count":27.0,"contact_point_centroid":[0.70468,0.26875,-0.0008],"force_p95":372.47277,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":376.37603,"mean_force":214.86042,"phase_index":6.0,"phase_name":"descend_at_goal","phase_type":"descend","tcp_position_centroid":[0.74958,0.17539,0.26946]},{"body_a":"world","body_b":"link5","contact_count":93.0,"contact_point_centroid":[0.5997,0.20029,-0.00012],"force_p95":142.63632,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":295.31622,"mean_force":72.33389,"phase_index":7.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.68798,0.19862,0.28465]},{"body_a":"world","body_b":"right_finger","contact_count":382.0,"contact_point_centroid":[0.63741,0.43719,-0.00908],"force_p95":22.33336,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":45.80266,"mean_force":16.37735,"phase_index":5.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.63537,0.43934,-0.01017]},{"body_a":"world","body_b":"left_finger","contact_count":386.0,"contact_point_centroid":[0.63225,0.44019,-0.00904],"force_p95":21.67897,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":45.48632,"mean_force":16.22108,"phase_index":5.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.63555,0.43937,-0.00998]},{"body_a":"world","body_b":"right_finger","contact_count":220.0,"contact_point_centroid":[0.67878,0.17588,-0.00472],"force_p95":28.42452,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":38.52105,"mean_force":16.54829,"phase_index":4.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.67865,0.18111,-0.00397]},{"body_a":"world","body_b":"left_finger","contact_count":238.0,"contact_point_centroid":[0.6787,0.18426,-0.00506],"force_p95":30.1525,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":36.64119,"mean_force":15.8337,"phase_index":4.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.67946,0.18189,-0.00341]},{"body_a":"grasp_target","body_b":"hand","contact_count":80.0,"contact_point_centroid":[0.53625,0.04235,0.03284],"force_p95":2.48309,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":9.88227,"mean_force":1.2132,"phase_index":4.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.64835,0.00323,0.04734]},{"body_a":"grasp_target","body_b":"link5","contact_count":74.0,"contact_point_centroid":[0.56283,0.10959,0.03405],"force_p95":5.28195,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":7.9903,"mean_force":2.26914,"phase_index":4.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.72004,0.30091,0.0245]},{"body_a":"world","body_b":"grasp_target","contact_count":712.0,"contact_point_centroid":[0.5354,0.06224,-0.00529],"force_p95":1.56066,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.47744,"mean_force":0.46918,"phase_index":4.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.70523,0.12554,0.07245]},{"body_a":"grasp_target","body_b":"link5","contact_count":84.0,"contact_point_centroid":[0.56991,0.1948,0.03835],"force_p95":2.14639,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.68283,"mean_force":0.72662,"phase_index":5.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.70639,0.37429,0.12053]}],"total_contact_groups":30},"final_pose_error":0.19743,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.53629,0.20293,0.016],"final_tcp_position":[0.68757,0.19966,0.28453],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":273004.12082,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":795.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"retract_up","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3176.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.49993,1e-05,0.55093],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.5267,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_pregrasp","tcp_end":[0.818,0.11706,0.29192],"tcp_start":[0.49993,1e-05,0.55093],"tcp_to_object_dist_end":0.401,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":392.40542,"phase_name":"descend_contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":12.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_contact","tcp_end":[0.8192,0.11807,0.2917],"tcp_start":[0.818,0.11706,0.29192],"tcp_to_object_dist_end":0.40193,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":2978.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_contact","tcp_end":[0.81633,0.12009,0.27101],"tcp_start":[0.81633,0.12009,0.27102],"tcp_to_object_dist_end":0.38691,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":240.0,"n_steps_budget":1000.0,"object_pos_end":[0.56784,0.14601,0.00999],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.10872,"object_to_goal_dist_start":0.18336,"object_z_max":0.02798,"peak_contact_force":1.04371,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":3645.0,"raw_peak_contact_force":1827.49684,"subtask_id":"lift_clear","tcp_end":[0.67079,0.45737,0.0861],"tcp_start":[0.81633,0.12009,0.27101],"tcp_to_object_dist_end":0.33665,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53938,0.20133,0.01602],"object_pos_start":[0.56784,0.14601,0.00999],"object_to_goal_dist_end":0.11339,"object_to_goal_dist_start":0.10872,"object_z_max":0.03214,"peak_contact_force":0.1227,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8602.0,"raw_peak_contact_force":2585.21288,"subtask_id":"place_goal","tcp_end":[0.77018,0.23193,0.33955],"tcp_start":[0.67079,0.45737,0.0861],"tcp_to_object_dist_end":0.39859,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53635,0.20275,0.01565],"object_pos_start":[0.53938,0.20133,0.01602],"object_to_goal_dist_end":0.11567,"object_to_goal_dist_start":0.11339,"object_z_max":0.01603,"peak_contact_force":228.49271,"phase_name":"descend_at_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":9541.0,"raw_peak_contact_force":442.31795,"subtask_id":"place_goal","tcp_end":[0.68757,0.19966,0.28453],"tcp_start":[0.77018,0.23193,0.33955],"tcp_to_object_dist_end":0.30851,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53629,0.20293,0.016],"object_pos_start":[0.53635,0.20275,0.01565],"object_to_goal_dist_end":0.11545,"object_to_goal_dist_start":0.11567,"object_z_max":0.0166,"peak_contact_force":0.12568,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1253.0,"raw_peak_contact_force":295.31622,"tcp_end":[0.6885,0.19813,0.30767],"tcp_start":[0.68757,0.19966,0.28453],"tcp_to_object_dist_end":0.32903,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
```