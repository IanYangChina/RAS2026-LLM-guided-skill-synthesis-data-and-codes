## Search State

- **Seed**: 3
- **Iteration**: 3 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
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

## Current Skill (Q=-0.200) — your mutation base

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
- id: descend_to_object
  type: descend
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
    - 0.0
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: world_z
      tolerance: 0.1
  parameters:
    force_threshold:
      type: scalar
      range:
      - 5.0
      - 15.0
      default: 10.0
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
    approach_goal_z:
      type: scalar
      range:
      - 0.1
      - 0.2
      default: 0.15
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
  subtask_id: place_goal
- id: descend_at_goal
  type: descend
  generator: linear_cartesian
  control: force_threshold_switch
  termination: force_exceeded
  target:
    source: yaml
    anchor: task_goal
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.0
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: world_z
      tolerance: 0.1
  parameters:
    force_threshold:
      type: scalar
      range:
      - 5.0
      - 15.0
      default: 10.0
      binds_to:
      - path: termination.force_threshold
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
- id: retract_after_place
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
    - 0.2
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    retract_z:
      type: scalar
      range:
      - 0.1
      - 0.3
      default: 0.2
      binds_to:
      - path: target.offset.z
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_object** (`approach`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.1], tolerance=0.01
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=world_z, tolerance=0.1
  - parameter_bindings:
    - approach_z: status=consumed; consumers=target.offset.z (replace)
    - arc_height: status=consumed; consumers=generator.arc_height (replace)
  - retries: max_attempts=0, strategy=repeat
- **descend_to_object** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.0]
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=world_z, tolerance=0.1
  - parameter_bindings:
    - force_threshold: status=consumed; consumers=termination.force_threshold (replace)
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
  - target: source=yaml, anchor=task_goal, entity=grasp_target, offset=[0.0, 0.0, 0.15], tolerance=0.01
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=world_z, tolerance=0.1
  - parameter_bindings:
    - approach_goal_z: status=consumed; consumers=target.offset.z (replace)
    - arc_height: status=consumed; consumers=generator.arc_height (replace)
  - retries: max_attempts=0, strategy=repeat
- **descend_at_goal** (`descend`)
  - target: source=yaml, anchor=task_goal, entity=grasp_target, offset=[0.0, 0.0, 0.0]
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=world_z, tolerance=0.1
  - parameter_bindings:
    - force_threshold: status=consumed; consumers=termination.force_threshold (replace)
  - retries: max_attempts=0, strategy=repeat
- **release_object** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings:
    - release_duration: status=consumed; consumers=duration.max_time (replace)
  - retries: max_attempts=0, strategy=repeat
- **retract_after_place** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.2], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - retract_z: status=consumed; consumers=target.offset.z (replace)
  - retries: max_attempts=0, strategy=repeat

## Design Metrics

- **Composite score**: -0.200
- **task_score** (E): 0.210
- **fitness_score**: 0.180  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.250
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.630

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 0.00 | 1.00 | 0.1340 |
| descend_to_object | 1.00 | 1.00 | 0.0001 |
| grasp_object | 1.00 | 1.00 | 0.0000 |
| lift_object | 0.00 | 1.00 | 0.0954 |
| approach_goal | 0.00 | 1.00 | 0.0899 |
| descend_at_goal | 1.00 | 1.00 | 0.0002 |
| release_object | 1.00 | 1.00 | 0.0267 |
| retract_after_place | 0.67 | 1.00 | 0.1401 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 0.00 / step_budget | (0.500, -0.000, 0.301)→(0.429, 0.027, 0.193) | (0.511, 0.002, 0.030)→(0.476, 0.009, 0.016) | 0.244→0.263 | 1.00 / 5.000 | 273.411 | 1553.119 |
| descend_to_object | descend | 1.00 / force_exceeded | (0.429, 0.027, 0.193)→(0.429, 0.027, 0.193) | (0.476, 0.009, 0.016)→(0.476, 0.009, 0.016) | 0.263→0.263 | 1.00 / 5.000 | 387.050 | 225.280 |
| grasp_object | grasp | 1.00 / step_budget | (0.430, 0.027, 0.193)→(0.430, 0.027, 0.193) | (0.476, 0.009, 0.016)→(0.476, 0.009, 0.016) | 0.263→0.263 | 1.00 / 9.333 | 91054.297 | 370.860 |
| lift_object | lift | 0.00 / step_budget | (0.430, 0.027, 0.193)→(0.493, 0.014, 0.251) | (0.476, 0.009, 0.016)→(0.476, 0.009, 0.016) | 0.263→0.263 | 1.00 / 9.667 | 592.492 | 705.871 |
| approach_goal | approach | 0.00 / step_budget | (0.493, 0.014, 0.251)→(0.518, 0.072, 0.292) | (0.476, 0.009, 0.016)→(0.461, 0.043, 0.017) | 0.263→0.254 | 1.00 / 8.333 | 3426.479 | 416.238 |
| descend_at_goal | descend | 1.00 / force_exceeded | (0.518, 0.072, 0.292)→(0.518, 0.072, 0.292) | (0.461, 0.043, 0.017)→(0.461, 0.043, 0.017) | 0.254→0.253 | 1.00 / 8.667 | 91125.698 | 147.744 |
| release_object | release | 1.00 / step_budget | (0.518, 0.072, 0.292)→(0.518, 0.072, 0.318) | (0.461, 0.043, 0.017)→(0.463, 0.049, 0.016) | 0.253→0.250 | 1.00 / 4.000 | 0.133 | 265.410 |
| retract_after_place | retract | 0.67 / step_budget | (0.518, 0.072, 0.318)→(0.511, 0.071, 0.458) | (0.463, 0.049, 0.016)→(0.463, 0.049, 0.016) | 0.250→0.250 | 1.00 / 4.000 | 0.123 | 0.132 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 0.000
- place_accuracy: 0.000
- lift_clearance: 0.000
- transport_retention: 0.000
- terminal_score: 0.341
- phase_score: 0.369
- phase_breakdown.lift_clear_score: 0.164
- phase_breakdown.reach_pregrasp_score: 0.080
- phase_breakdown.grasp_contact_score: 1.000
- phase_breakdown.place_goal_score: 0.020
- grasp_place_fitness: 0.230

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.230
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.341
- **Median Q (composite search score)**: -0.223
- **K-run variance**: 0.0013
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.402


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":6.96907,"average_solve_count":97.0,"average_success_count":97.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_z":0.17591,"approach_goal.arc_height":0.2399,"approach_object.approach_z":0.14936,"approach_object.arc_height":0.27224,"descend_at_goal.force_threshold":10.71827,"descend_to_object.force_threshold":9.15551,"lift_object.lift_height":0.08274,"release_object.release_duration":0.8613,"retract_after_place.retract_z":0.20014},"optimized_scores":{"best_composite_score":-0.22328,"best_fitness_score":0.15672,"best_task_score":0.11061},"replay_outcomes":[{"contacts":{"omitted_contact_groups":7,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":886.0,"contact_point_centroid":[0.62738,0.00376,-0.00047],"force_p95":197.64424,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1341.7311,"mean_force":200.71615,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.38512,0.00305,0.12171]},{"body_a":"world","body_b":"link7","contact_count":20.0,"contact_point_centroid":[0.52422,0.00739,-0.00308],"force_p95":25.77094,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":515.41876,"mean_force":25.77094,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.36885,0.00224,0.05148]},{"body_a":"world","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.50225,0.02825,-0.00012],"force_p95":290.79542,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":290.79542,"mean_force":290.79542,"phase_index":5.0,"phase_name":"descend_at_goal","phase_type":"descend","tcp_position_centroid":[0.38964,0.01633,0.26354]},{"body_a":"world","body_b":"link6","contact_count":476.0,"contact_point_centroid":[0.61255,-0.00443,-0.0002],"force_p95":237.51842,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":288.07574,"mean_force":214.09457,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.39982,-0.0055,0.17011]},{"body_a":"world","body_b":"link6","contact_count":976.0,"contact_point_centroid":[0.5435,-0.00596,-0.00017],"force_p95":242.70354,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":263.8617,"mean_force":213.16281,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.36141,-0.00633,0.20692]},{"body_a":"world","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.62191,0.00253,-0.00025],"force_p95":214.95029,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":214.95029,"mean_force":214.95029,"phase_index":1.0,"phase_name":"descend_to_object","phase_type":"descend","tcp_position_centroid":[0.39197,0.0014,0.14687]},{"body_a":"world","body_b":"link6","contact_count":71.0,"contact_point_centroid":[0.50183,0.02816,-0.00012],"force_p95":123.87088,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":157.06282,"mean_force":76.99007,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.38984,0.01626,0.26381]},{"body_a":"world","body_b":"link6","contact_count":550.0,"contact_point_centroid":[0.62246,0.00252,-0.00014],"force_p95":92.97552,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":154.28115,"mean_force":74.29097,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.3923,0.00143,0.14675]},{"body_a":"grasp_target","body_b":"hand","contact_count":37.0,"contact_point_centroid":[0.44137,-0.01421,0.04277],"force_p95":3.56916,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.98216,"mean_force":1.54938,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.37953,0.00228,0.05303]},{"body_a":"world","body_b":"grasp_target","contact_count":3925.0,"contact_point_centroid":[0.42218,-0.02454,-0.00212],"force_p95":0.13759,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.25604,"mean_force":0.13751,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.39758,0.00292,0.1314]},{"body_a":"grasp_target","body_b":"link7","contact_count":8.0,"contact_point_centroid":[0.47219,-0.00781,0.00775],"force_p95":0.37154,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.37731,"mean_force":0.25884,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.36752,0.00221,0.04871]},{"body_a":"world","body_b":"grasp_target","contact_count":4.0,"contact_point_centroid":[0.41705,-0.02426,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_object","phase_type":"descend","tcp_position_centroid":[0.39197,0.0014,0.14687]},{"body_a":"world","body_b":"grasp_target","contact_count":2200.0,"contact_point_centroid":[0.41705,-0.02426,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.3923,0.00143,0.14675]},{"body_a":"world","body_b":"grasp_target","contact_count":1936.0,"contact_point_centroid":[0.41705,-0.02426,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.40006,-0.00559,0.17057]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.41705,-0.02426,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.36189,-0.00619,0.20749]},{"body_a":"world","body_b":"grasp_target","contact_count":4.0,"contact_point_centroid":[0.41705,-0.02426,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_at_goal","phase_type":"descend","tcp_position_centroid":[0.38964,0.01633,0.26354]}],"total_contact_groups":23},"final_pose_error":0.08332,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.41705,-0.02426,0.01602],"final_tcp_position":[0.36443,0.01568,0.41412],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":273004.12069,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.41705,-0.02426,0.01602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.33026,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":195.38023,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4876.0,"raw_peak_contact_force":1341.7311,"subtask_id":"reach_pregrasp","tcp_end":[0.39197,0.0014,0.14687],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13568,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.41705,-0.02426,0.01602],"object_pos_start":[0.41705,-0.02426,0.01602],"object_to_goal_dist_end":0.33026,"object_to_goal_dist_start":0.33026,"object_z_max":0.01602,"peak_contact_force":700.25851,"phase_name":"descend_to_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5.0,"raw_peak_contact_force":214.95029,"subtask_id":"grasp_contact","tcp_end":[0.39196,0.00148,0.14689],"tcp_start":[0.39197,0.0014,0.14687],"tcp_to_object_dist_end":0.13572,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.41705,-0.02426,0.01602],"object_pos_start":[0.41705,-0.02426,0.01602],"object_to_goal_dist_end":0.33026,"object_to_goal_dist_start":0.33026,"object_z_max":0.01602,"peak_contact_force":273004.12069,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":3499.0,"raw_peak_contact_force":154.28115,"subtask_id":"grasp_contact","tcp_end":[0.39238,0.0014,0.1466],"tcp_start":[0.39238,0.0014,0.1466],"tcp_to_object_dist_end":0.13534,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":484.0,"n_steps_budget":600.0,"object_pos_end":[0.41705,-0.02426,0.01602],"object_pos_start":[0.41705,-0.02426,0.01602],"object_to_goal_dist_end":0.33026,"object_to_goal_dist_start":0.33026,"object_z_max":0.01602,"peak_contact_force":111.39095,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":4440.0,"raw_peak_contact_force":288.07574,"subtask_id":"lift_clear","tcp_end":[0.43338,-0.01811,0.22584],"tcp_start":[0.39238,0.0014,0.1466],"tcp_to_object_dist_end":0.21055,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.41705,-0.02426,0.01602],"object_pos_start":[0.41705,-0.02426,0.01602],"object_to_goal_dist_end":0.33026,"object_to_goal_dist_start":0.33026,"object_z_max":0.01602,"peak_contact_force":150.41009,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":9206.0,"raw_peak_contact_force":263.8617,"subtask_id":"place_goal","tcp_end":[0.38964,0.01633,0.26354],"tcp_start":[0.43338,-0.01811,0.22584],"tcp_to_object_dist_end":0.25232,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.41705,-0.02426,0.01602],"object_pos_start":[0.41705,-0.02426,0.01602],"object_to_goal_dist_end":0.33026,"object_to_goal_dist_start":0.33026,"object_z_max":0.01602,"peak_contact_force":290.79542,"phase_name":"descend_at_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":9.0,"raw_peak_contact_force":290.79542,"subtask_id":"place_goal","tcp_end":[0.38967,0.01626,0.2636],"tcp_start":[0.38964,0.01633,0.26354],"tcp_to_object_dist_end":0.25237,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.41705,-0.02426,0.01602],"object_pos_start":[0.41705,-0.02426,0.01602],"object_to_goal_dist_end":0.33026,"object_to_goal_dist_start":0.33026,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1090.0,"raw_peak_contact_force":157.06282,"tcp_end":[0.3895,0.01621,0.29343],"tcp_start":[0.38967,0.01626,0.2636],"tcp_to_object_dist_end":0.2817,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.41705,-0.02426,0.01602],"object_pos_start":[0.41705,-0.02426,0.01602],"object_to_goal_dist_end":0.33026,"object_to_goal_dist_start":0.33026,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_after_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.36443,0.01568,0.41412],"tcp_start":[0.3895,0.01621,0.29343],"tcp_to_object_dist_end":0.40355,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":5.66364,"average_solve_count":110.0,"average_success_count":110.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_z":0.11496,"approach_goal.arc_height":0.27524,"approach_object.approach_z":0.13332,"approach_object.arc_height":0.12589,"descend_at_goal.force_threshold":14.68855,"descend_to_object.force_threshold":13.28658,"lift_object.lift_height":0.10853,"release_object.release_duration":1.72533,"retract_after_place.retract_z":0.18699},"optimized_scores":{"best_composite_score":-0.22807,"best_fitness_score":0.15193,"best_task_score":0.17683},"replay_outcomes":[{"contacts":{"omitted_contact_groups":7,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":880.0,"contact_point_centroid":[0.62871,0.02755,-0.00043],"force_p95":387.79022,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1641.65974,"mean_force":252.28319,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.41673,0.02595,0.16792]},{"body_a":"world","body_b":"link6","contact_count":581.0,"contact_point_centroid":[0.62696,0.02596,-0.00021],"force_p95":615.2843,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":913.01732,"mean_force":333.09808,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.44363,0.04612,0.2085]},{"body_a":"world","body_b":"link6","contact_count":544.0,"contact_point_centroid":[0.64136,0.03493,-0.00014],"force_p95":90.02537,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":726.97006,"mean_force":75.8299,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.45249,0.04252,0.20919]},{"body_a":"world","body_b":"link6","contact_count":391.0,"contact_point_centroid":[0.53823,-0.02178,-7e-05],"force_p95":344.63908,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":427.50109,"mean_force":201.74154,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.54106,-0.00333,0.29253]},{"body_a":"world","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.64039,0.0349,-0.00024],"force_p95":218.52533,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":218.52533,"mean_force":218.52533,"phase_index":1.0,"phase_name":"descend_to_object","phase_type":"descend","tcp_position_centroid":[0.45267,0.04251,0.21002]},{"body_a":"grasp_target","body_b":"link6","contact_count":274.0,"contact_point_centroid":[0.53959,0.01319,0.025],"force_p95":0.45649,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.49541,"mean_force":0.24373,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.39006,0.01385,0.11468]},{"body_a":"grasp_target","body_b":"link7","contact_count":206.0,"contact_point_centroid":[0.52398,0.00994,0.02816],"force_p95":3.17349,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.99827,"mean_force":0.48679,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.38812,0.01264,0.10312]},{"body_a":"world","body_b":"grasp_target","contact_count":3938.0,"contact_point_centroid":[0.51254,-0.00023,-0.00243],"force_p95":0.34135,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.80015,"mean_force":0.1585,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.4261,0.02401,0.17275]},{"body_a":"grasp_target","body_b":"hand","contact_count":20.0,"contact_point_centroid":[0.50387,-0.01071,0.03389],"force_p95":2.3123,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.64301,"mean_force":1.14751,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.39323,0.01068,0.05087]},{"body_a":"grasp_target","body_b":"link6","contact_count":794.0,"contact_point_centroid":[0.52163,0.01978,0.02186],"force_p95":0.68127,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.41971,"mean_force":0.51654,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.5516,0.01947,0.29897]},{"body_a":"world","body_b":"grasp_target","contact_count":3133.0,"contact_point_centroid":[0.493,0.03604,-0.00376],"force_p95":0.548,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.69145,"mean_force":0.26523,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.55723,0.02814,0.30169]},{"body_a":"world","body_b":"grasp_target","contact_count":16.0,"contact_point_centroid":[0.487,0.0528,-0.00199],"force_p95":0.12277,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12277,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_at_goal","phase_type":"descend","tcp_position_centroid":[0.59003,0.07975,0.31846]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.487,0.0528,-0.00199],"force_p95":0.12266,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12275,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.59002,0.07948,0.32068]},{"body_a":"world","body_b":"grasp_target","contact_count":4.0,"contact_point_centroid":[0.50847,-0.0003,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_object","phase_type":"descend","tcp_position_centroid":[0.45267,0.04251,0.21002]},{"body_a":"world","body_b":"grasp_target","contact_count":2200.0,"contact_point_centroid":[0.50847,-0.0003,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.45249,0.04252,0.2092]},{"body_a":"world","body_b":"grasp_target","contact_count":2532.0,"contact_point_centroid":[0.50847,-0.0003,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.44623,0.04655,0.20871]}],"total_contact_groups":23},"final_pose_error":0.02603,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.487,0.0528,0.01602],"final_tcp_position":[0.59183,0.07746,0.5022],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":273004.12056,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50847,-0.0003,0.01602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.27405,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":368.03256,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":5336.0,"raw_peak_contact_force":1641.65974,"subtask_id":"reach_pregrasp","tcp_end":[0.45267,0.04251,0.21002],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.20636,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.50847,-0.0003,0.01602],"object_pos_start":[0.50847,-0.0003,0.01602],"object_to_goal_dist_end":0.27405,"object_to_goal_dist_start":0.27405,"object_z_max":0.01602,"peak_contact_force":218.52533,"phase_name":"descend_to_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5.0,"raw_peak_contact_force":218.52533,"subtask_id":"grasp_contact","tcp_end":[0.45263,0.04249,0.2101],"tcp_start":[0.45267,0.04251,0.21002],"tcp_to_object_dist_end":0.20644,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.50847,-0.0003,0.01602],"object_pos_start":[0.50847,-0.0003,0.01602],"object_to_goal_dist_end":0.27405,"object_to_goal_dist_start":0.27405,"object_z_max":0.01602,"peak_contact_force":85.93176,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":3503.0,"raw_peak_contact_force":726.97006,"subtask_id":"grasp_contact","tcp_end":[0.45249,0.04249,0.20909],"tcp_start":[0.45249,0.04249,0.20909],"tcp_to_object_dist_end":0.20553,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":633.0,"n_steps_budget":720.0,"object_pos_end":[0.50847,-0.0003,0.01602],"object_pos_start":[0.50847,-0.0003,0.01602],"object_to_goal_dist_end":0.27405,"object_to_goal_dist_start":0.27405,"object_z_max":0.01602,"peak_contact_force":299.24298,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":5798.0,"raw_peak_contact_force":913.01732,"subtask_id":"lift_clear","tcp_end":[0.52774,-0.00474,0.26488],"tcp_start":[0.45249,0.04249,0.20909],"tcp_to_object_dist_end":0.24964,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.487,0.0528,0.01602],"object_pos_start":[0.50847,-0.0003,0.01602],"object_to_goal_dist_end":0.25988,"object_to_goal_dist_start":0.27405,"object_z_max":0.01607,"peak_contact_force":9748.85272,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8731.0,"raw_peak_contact_force":427.50109,"subtask_id":"place_goal","tcp_end":[0.59002,0.0796,0.31851],"tcp_start":[0.52774,-0.00474,0.26488],"tcp_to_object_dist_end":0.32068,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":4.0,"n_steps_budget":1000.0,"object_pos_end":[0.487,0.05281,0.01602],"object_pos_start":[0.487,0.0528,0.01602],"object_to_goal_dist_end":0.25988,"object_to_goal_dist_start":0.25988,"object_z_max":0.01602,"peak_contact_force":272933.98565,"phase_name":"descend_at_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":32.0,"raw_peak_contact_force":0.12277,"subtask_id":"place_goal","tcp_end":[0.59013,0.07998,0.31821],"tcp_start":[0.59002,0.0796,0.31851],"tcp_to_object_dist_end":0.32046,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.487,0.0528,0.01602],"object_pos_start":[0.487,0.05281,0.01602],"object_to_goal_dist_end":0.25988,"object_to_goal_dist_start":0.25988,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1028.0,"raw_peak_contact_force":0.12275,"tcp_end":[0.59031,0.07909,0.34114],"tcp_start":[0.59013,0.07998,0.31821],"tcp_to_object_dist_end":0.34215,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.487,0.0528,0.01602],"object_pos_start":[0.487,0.0528,0.01602],"object_to_goal_dist_end":0.25988,"object_to_goal_dist_start":0.25988,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_after_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.59183,0.07746,0.5022],"tcp_start":[0.59031,0.07909,0.34114],"tcp_to_object_dist_end":0.49796,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":5.93814,"average_solve_count":97.0,"average_success_count":97.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_z":0.13741,"approach_goal.arc_height":0.28802,"approach_object.approach_z":0.09756,"approach_object.arc_height":0.29895,"descend_at_goal.force_threshold":11.55778,"descend_to_object.force_threshold":8.83013,"lift_object.lift_height":0.10119,"release_object.release_duration":1.16986,"retract_after_place.retract_z":0.14907},"optimized_scores":{"best_composite_score":-0.1496,"best_fitness_score":0.2304,"best_task_score":0.3414},"replay_outcomes":[{"contacts":{"omitted_contact_groups":14,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":880.0,"contact_point_centroid":[0.62705,0.02154,-0.00045],"force_p95":258.72898,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1675.96643,"mean_force":219.3981,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.40853,0.01955,0.15849]},{"body_a":"world","body_b":"link6","contact_count":647.0,"contact_point_centroid":[0.6116,0.03937,-0.00021],"force_p95":625.38474,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":916.51951,"mean_force":367.15617,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.43862,0.05264,0.22018]},{"body_a":"link5","body_b":"hand","contact_count":17.0,"contact_point_centroid":[0.51043,-0.02674,0.22975],"force_p95":759.25146,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":793.84762,"mean_force":612.3853,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.51247,0.0698,0.25717]},{"body_a":"world","body_b":"link6","contact_count":82.0,"contact_point_centroid":[0.565,0.10713,-0.00014],"force_p95":183.44796,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":639.04474,"mean_force":87.11333,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.57517,0.12029,0.29373]},{"body_a":"world","body_b":"link6","contact_count":960.0,"contact_point_centroid":[0.54612,0.07261,-0.00024],"force_p95":428.35659,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":557.35032,"mean_force":343.39661,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.54973,0.08595,0.29297]},{"body_a":"link5","body_b":"hand","contact_count":91.0,"contact_point_centroid":[0.48668,-0.03316,0.2349],"force_p95":458.71888,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":542.86949,"mean_force":246.04274,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.52171,0.04805,0.28424]},{"body_a":"world","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.61704,0.02944,-0.00027],"force_p95":242.36523,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":242.36523,"mean_force":242.36523,"phase_index":1.0,"phase_name":"descend_to_object","phase_type":"descend","tcp_position_centroid":[0.44384,0.03639,0.22208]},{"body_a":"world","body_b":"link6","contact_count":550.0,"contact_point_centroid":[0.61741,0.02875,-0.00013],"force_p95":83.27122,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":231.32842,"mean_force":76.07339,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.44411,0.03594,0.22227]},{"body_a":"world","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.56498,0.10712,-0.00033],"force_p95":152.3143,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":152.3143,"mean_force":152.3143,"phase_index":5.0,"phase_name":"descend_at_goal","phase_type":"descend","tcp_position_centroid":[0.57521,0.12061,0.29334]},{"body_a":"grasp_target","body_b":"link7","contact_count":179.0,"contact_point_centroid":[0.51264,0.02612,0.0355],"force_p95":3.26163,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.60962,"mean_force":0.66338,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.38617,0.00852,0.09866]},{"body_a":"grasp_target","body_b":"link6","contact_count":154.0,"contact_point_centroid":[0.5356,0.03976,0.03531],"force_p95":0.94499,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.49364,"mean_force":0.47491,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.38401,0.00852,0.10134]},{"body_a":"world","body_b":"grasp_target","contact_count":3550.0,"contact_point_centroid":[0.50654,0.0467,-0.00223],"force_p95":0.33329,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.34971,"mean_force":0.15783,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.42239,0.0191,0.17034]},{"body_a":"grasp_target","body_b":"hand","contact_count":109.0,"contact_point_centroid":[0.49137,0.04102,0.05326],"force_p95":2.2729,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.92647,"mean_force":0.85874,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.38308,0.00793,0.08626]},{"body_a":"grasp_target","body_b":"link6","contact_count":958.0,"contact_point_centroid":[0.48726,0.05964,0.04458],"force_p95":0.63455,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.12646,"mean_force":0.40086,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.54986,0.08601,0.29331]},{"body_a":"grasp_target","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.50172,0.09234,0.04393],"force_p95":1.09433,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.09433,"mean_force":1.09433,"phase_index":5.0,"phase_name":"descend_at_goal","phase_type":"descend","tcp_position_centroid":[0.57521,0.12061,0.29334]},{"body_a":"world","body_b":"grasp_target","contact_count":2068.0,"contact_point_centroid":[0.47082,0.07766,-0.00558],"force_p95":0.60096,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.74673,"mean_force":0.3819,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.54669,0.08194,0.29188]}],"total_contact_groups":30},"final_pose_error":0.01309,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.48368,0.11842,0.01602],"final_tcp_position":[0.57664,0.11885,0.45695],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":1675.96643,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50264,0.05064,0.01602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18608,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":256.81921,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4891.0,"raw_peak_contact_force":1675.96643,"subtask_id":"reach_pregrasp","tcp_end":[0.44384,0.03639,0.22208],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.21475,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.50264,0.05064,0.01602],"object_pos_start":[0.50264,0.05064,0.01602],"object_to_goal_dist_end":0.18608,"object_to_goal_dist_start":0.18608,"object_z_max":0.01602,"peak_contact_force":242.36523,"phase_name":"descend_to_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5.0,"raw_peak_contact_force":242.36523,"subtask_id":"grasp_contact","tcp_end":[0.44379,0.03634,0.22203],"tcp_start":[0.44384,0.03639,0.22208],"tcp_to_object_dist_end":0.21473,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.50264,0.05064,0.01602],"object_pos_start":[0.50264,0.05064,0.01602],"object_to_goal_dist_end":0.18608,"object_to_goal_dist_start":0.18608,"object_z_max":0.01602,"peak_contact_force":72.8399,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":3510.0,"raw_peak_contact_force":231.32842,"subtask_id":"grasp_contact","tcp_end":[0.44413,0.03589,0.2222],"tcp_start":[0.44413,0.0359,0.22221],"tcp_to_object_dist_end":0.21483,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":693.0,"n_steps_budget":780.0,"object_pos_end":[0.502,0.05103,0.01602],"object_pos_start":[0.50264,0.05064,0.01602],"object_to_goal_dist_end":0.18615,"object_to_goal_dist_start":0.18608,"object_z_max":0.01633,"peak_contact_force":1366.84211,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":6536.0,"raw_peak_contact_force":916.51951,"subtask_id":"lift_clear","tcp_end":[0.51881,0.06528,0.2629],"tcp_start":[0.44413,0.03589,0.2222],"tcp_to_object_dist_end":0.24786,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47905,0.10115,0.01844],"object_pos_start":[0.502,0.05103,0.01602],"object_to_goal_dist_end":0.17039,"object_to_goal_dist_start":0.18615,"object_z_max":0.02027,"peak_contact_force":380.17539,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8447.0,"raw_peak_contact_force":557.35032,"subtask_id":"place_goal","tcp_end":[0.57521,0.12061,0.29334],"tcp_start":[0.51881,0.06528,0.2629],"tcp_to_object_dist_end":0.29189,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.479,0.10125,0.0185],"object_pos_start":[0.47905,0.10115,0.01844],"object_to_goal_dist_end":0.17036,"object_to_goal_dist_start":0.17039,"object_z_max":0.01844,"peak_contact_force":152.3143,"phase_name":"descend_at_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8.0,"raw_peak_contact_force":152.3143,"subtask_id":"place_goal","tcp_end":[0.5753,0.12055,0.29341],"tcp_start":[0.57521,0.12061,0.29334],"tcp_to_object_dist_end":0.29193,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48397,0.11985,0.0153],"object_pos_start":[0.479,0.10125,0.0185],"object_to_goal_dist_end":0.16087,"object_to_goal_dist_start":0.17036,"object_z_max":0.02031,"peak_contact_force":0.15236,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":890.0,"raw_peak_contact_force":639.04474,"tcp_end":[0.57542,0.11985,0.32087],"tcp_start":[0.5753,0.12055,0.29341],"tcp_to_object_dist_end":0.31896,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":843.0,"n_steps_budget":930.0,"object_pos_end":[0.48368,0.11842,0.01602],"object_pos_start":[0.48397,0.11985,0.0153],"object_to_goal_dist_end":0.1612,"object_to_goal_dist_start":0.16087,"object_z_max":0.01607,"peak_contact_force":0.12263,"phase_name":"retract_after_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3372.0,"raw_peak_contact_force":0.14972,"tcp_end":[0.57664,0.11885,0.45695],"tcp_start":[0.57542,0.11985,0.32087],"tcp_to_object_dist_end":0.45062,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```