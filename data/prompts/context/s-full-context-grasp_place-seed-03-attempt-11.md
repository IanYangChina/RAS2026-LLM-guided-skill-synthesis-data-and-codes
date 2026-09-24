## Search State

- **Seed**: 3
- **Iteration**: 12 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 11 | approach → contact → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 8 | -0.2169 | 0.19 | ❌ rejected |
| 10 | retract → approach → contact → grasp → lift → approach → descend → release | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 9 | -0.3474 | 0.27 | ✅ accepted |
| 9 | approach → descend → contact → grasp → lift → approach → descend → release | arc_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 9 | -0.3300 | 0.20 | ❌ rejected |
| 8 | approach → descend → contact → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 9 | -0.3745 | 0.16 | ❌ rejected |
| 7 | approach → descend → contact → grasp → lift → approach → descend → release | arc_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 9 | -0.3241 | 0.22 | ✅ accepted |

**Proposal policy**: task_score is 0.19 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.217) — your mutation base

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

- **Composite score**: -0.217
- **task_score** (E): 0.187
- **fitness_score**: 0.190  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.143
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.550

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 0.00 | 1.00 | 0.1630 |
| descend_contact | 1.00 | 1.00 | 0.0002 |
| grasp_object | 1.00 | 1.00 | 0.0000 |
| lift_object | 0.00 | 1.00 | 0.0309 |
| approach_goal | 0.00 | 1.00 | 0.0974 |
| descend_at_goal | 0.00 | 1.00 | 0.1405 |
| release_object | 1.00 | 1.00 | 0.0275 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 0.00 / step_budget | (0.500, -0.000, 0.301)→(0.430, 0.001, 0.156) | (0.511, 0.002, 0.030)→(0.471, 0.007, 0.016) | 0.244→0.268 | 1.00 / 5.000 | 275.875 | 1389.622 |
| descend_contact | contact | 1.00 / force_exceeded | (0.430, 0.001, 0.156)→(0.430, 0.001, 0.156) | (0.471, 0.007, 0.016)→(0.471, 0.007, 0.016) | 0.268→0.268 | 1.00 / 5.000 | 528.695 | 304.034 |
| grasp_object | grasp | 1.00 / step_budget | (0.430, 0.001, 0.155)→(0.430, 0.001, 0.155) | (0.471, 0.007, 0.016)→(0.471, 0.007, 0.016) | 0.268→0.268 | 1.00 / 9.333 | 91051.869 | 161.689 |
| lift_object | lift | 0.00 / step_budget | (0.430, 0.001, 0.155)→(0.428, 0.007, 0.161) | (0.471, 0.007, 0.016)→(0.471, 0.007, 0.016) | 0.268→0.268 | 1.00 / 9.667 | 182132.035 | 577.218 |
| approach_goal | approach | 0.00 / step_budget | (0.428, 0.007, 0.161)→(0.380, 0.036, 0.144) | (0.471, 0.007, 0.016)→(0.468, 0.008, 0.014) | 0.268→0.270 | 1.00 / 10.000 | 91189.269 | 372.917 |
| descend_at_goal | descend | 0.00 / step_budget | (0.380, 0.036, 0.144)→(0.466, 0.056, 0.251) | (0.468, 0.008, 0.014)→(0.467, 0.014, 0.016) | 0.270→0.265 | 1.00 / 9.667 | 52854.714 | 774.599 |
| release_object | release | 1.00 / step_budget | (0.466, 0.056, 0.251)→(0.466, 0.056, 0.279) | (0.467, 0.014, 0.016)→(0.467, 0.016, 0.017) | 0.265→0.263 | 1.00 / 4.000 | 32.787 | 115.549 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 0.000
- place_accuracy: 0.000
- lift_clearance: 0.000
- transport_retention: 0.000
- terminal_score: 0.287
- phase_score: 0.390
- phase_breakdown.lift_clear_score: 0.207
- phase_breakdown.reach_pregrasp_score: 0.119
- phase_breakdown.grasp_contact_score: 1.000
- phase_breakdown.place_goal_score: 0.019
- grasp_place_fitness: 0.215

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.215
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.287
- **Median Q (composite search score)**: -0.226
- **K-run variance**: 0.0003
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.339


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":7.41176,"average_solve_count":85.0,"average_success_count":85.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_z":0.11663,"approach_goal.goal_arc_height":0.07043,"approach_object.approach_tolerance":0.03686,"approach_object.approach_z":0.19999,"descend_at_goal.descend_goal_tolerance":0.02923,"descend_contact.contact_force":10.69798,"lift_object.lift_height":0.17267,"release_object.release_duration":1.61591},"optimized_scores":{"best_composite_score":-0.22554,"best_fitness_score":0.18161,"best_task_score":0.11085},"replay_outcomes":[{"contacts":{"omitted_contact_groups":6,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":792.0,"contact_point_centroid":[0.6268,-0.01225,-0.00049],"force_p95":211.96148,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1311.42724,"mean_force":210.5786,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.37575,-0.01135,0.10137]},{"body_a":"world","body_b":"link7","contact_count":22.0,"contact_point_centroid":[0.51902,-0.00408,-0.00309],"force_p95":377.97528,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1226.66769,"mean_force":73.84256,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.36667,-0.00677,0.04869]},{"body_a":"world","body_b":"link6","contact_count":986.0,"contact_point_centroid":[0.591,0.03209,-0.00023],"force_p95":418.90558,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":838.13333,"mean_force":271.58519,"phase_index":5.0,"phase_name":"descend_at_goal","phase_type":"descend","tcp_position_centroid":[0.40639,0.00351,0.1999]},{"body_a":"world","body_b":"link6","contact_count":1000.0,"contact_point_centroid":[0.61575,-0.01197,-0.00023],"force_p95":231.22167,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":489.26532,"mean_force":215.96062,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.36823,-0.02565,0.11376]},{"body_a":"world","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.62498,-0.01812,-0.00026],"force_p95":429.34018,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":429.34018,"mean_force":429.34018,"phase_index":1.0,"phase_name":"descend_contact","phase_type":"contact","tcp_position_centroid":[0.37527,-0.01788,0.11007]},{"body_a":"world","body_b":"link6","contact_count":513.0,"contact_point_centroid":[0.62124,-0.02022,-0.00026],"force_p95":204.4526,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":422.52234,"mean_force":202.1152,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.37079,-0.02328,0.10284]},{"body_a":"world","body_b":"link6","contact_count":69.0,"contact_point_centroid":[0.59657,0.05601,-0.00015],"force_p95":93.81699,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":128.32346,"mean_force":76.62101,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.44019,0.02744,0.23048]},{"body_a":"world","body_b":"link6","contact_count":550.0,"contact_point_centroid":[0.62582,-0.01825,-0.00013],"force_p95":83.45508,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":96.65926,"mean_force":70.81275,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.37584,-0.018,0.10972]},{"body_a":"grasp_target","body_b":"hand","contact_count":39.0,"contact_point_centroid":[0.43891,-0.01381,0.04182],"force_p95":3.58258,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.99221,"mean_force":1.57582,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.37763,-0.00678,0.05058]},{"body_a":"world","body_b":"grasp_target","contact_count":3545.0,"contact_point_centroid":[0.42311,-0.02461,-0.00214],"force_p95":0.13814,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.32193,"mean_force":0.13997,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.39027,-0.01056,0.1142]},{"body_a":"grasp_target","body_b":"link7","contact_count":14.0,"contact_point_centroid":[0.46995,-0.01064,0.00891],"force_p95":0.36795,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.37176,"mean_force":0.18179,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.36545,-0.00676,0.04767]},{"body_a":"world","body_b":"grasp_target","contact_count":4.0,"contact_point_centroid":[0.41763,-0.02433,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_contact","phase_type":"contact","tcp_position_centroid":[0.37527,-0.01788,0.11007]},{"body_a":"world","body_b":"grasp_target","contact_count":2200.0,"contact_point_centroid":[0.41763,-0.02433,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.37584,-0.018,0.10972]},{"body_a":"world","body_b":"grasp_target","contact_count":2052.0,"contact_point_centroid":[0.41763,-0.02433,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.37079,-0.02328,0.10284]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.41763,-0.02433,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.36823,-0.02565,0.11376]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.41763,-0.02433,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_at_goal","phase_type":"descend","tcp_position_centroid":[0.40653,0.00361,0.20014]}],"total_contact_groups":22},"final_pose_error":0.28692,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.41763,-0.02433,0.01602],"final_tcp_position":[0.44031,0.02747,0.23083],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":273007.88422,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":905.0,"n_steps_budget":1000.0,"object_pos_end":[0.41763,-0.02433,0.01602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.32993,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":210.63844,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4412.0,"raw_peak_contact_force":1311.42724,"subtask_id":"reach_pregrasp","tcp_end":[0.37527,-0.01788,0.11007],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.10335,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1.0,"n_steps_budget":630.0,"object_pos_end":[0.41763,-0.02433,0.01602],"object_pos_start":[0.41763,-0.02433,0.01602],"object_to_goal_dist_end":0.32993,"object_to_goal_dist_start":0.32993,"object_z_max":0.01602,"peak_contact_force":768.61424,"phase_name":"descend_contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":5.0,"raw_peak_contact_force":429.34018,"subtask_id":"grasp_contact","tcp_end":[0.37529,-0.01786,0.11025],"tcp_start":[0.37527,-0.01788,0.11007],"tcp_to_object_dist_end":0.10351,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.41763,-0.02433,0.01602],"object_pos_start":[0.41763,-0.02433,0.01602],"object_to_goal_dist_end":0.32993,"object_to_goal_dist_start":0.32993,"object_z_max":0.01602,"peak_contact_force":66.49775,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":3492.0,"raw_peak_contact_force":96.65926,"subtask_id":"grasp_contact","tcp_end":[0.37596,-0.01803,0.10952],"tcp_start":[0.37596,-0.01803,0.10953],"tcp_to_object_dist_end":0.10256,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":513.0,"n_steps_budget":600.0,"object_pos_end":[0.41763,-0.02433,0.01602],"object_pos_start":[0.41763,-0.02433,0.01602],"object_to_goal_dist_end":0.32993,"object_to_goal_dist_start":0.32993,"object_z_max":0.01602,"peak_contact_force":273002.27246,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":4714.0,"raw_peak_contact_force":422.52234,"subtask_id":"lift_clear","tcp_end":[0.36472,-0.02762,0.09434],"tcp_start":[0.37596,-0.01803,0.10952],"tcp_to_object_dist_end":0.09458,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.41763,-0.02433,0.01602],"object_pos_start":[0.41763,-0.02433,0.01602],"object_to_goal_dist_end":0.32993,"object_to_goal_dist_start":0.32993,"object_z_max":0.01602,"peak_contact_force":273007.88422,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":9204.0,"raw_peak_contact_force":489.26532,"subtask_id":"place_goal","tcp_end":[0.36772,-0.00919,0.1316],"tcp_start":[0.36472,-0.02762,0.09434],"tcp_to_object_dist_end":0.1268,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.41763,-0.02433,0.01602],"object_pos_start":[0.41763,-0.02433,0.01602],"object_to_goal_dist_end":0.32993,"object_to_goal_dist_start":0.32993,"object_z_max":0.01602,"peak_contact_force":410.31521,"phase_name":"descend_at_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":9283.0,"raw_peak_contact_force":838.13333,"subtask_id":"place_goal","tcp_end":[0.44031,0.02747,0.23083],"tcp_start":[0.36772,-0.00919,0.1316],"tcp_to_object_dist_end":0.22213,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.41763,-0.02433,0.01602],"object_pos_start":[0.41763,-0.02433,0.01602],"object_to_goal_dist_end":0.32993,"object_to_goal_dist_start":0.32993,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1088.0,"raw_peak_contact_force":128.32346,"tcp_end":[0.43931,0.02713,0.25859],"tcp_start":[0.44031,0.02747,0.23083],"tcp_to_object_dist_end":0.24891,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":8.05882,"average_solve_count":85.0,"average_success_count":85.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_z":0.16139,"approach_goal.goal_arc_height":0.11545,"approach_object.approach_tolerance":0.01581,"approach_object.approach_z":0.18256,"descend_at_goal.descend_goal_tolerance":0.01986,"descend_contact.contact_force":7.58134,"lift_object.lift_height":0.13842,"release_object.release_duration":1.45865},"optimized_scores":{"best_composite_score":-0.23301,"best_fitness_score":0.17414,"best_task_score":0.16146},"replay_outcomes":[{"contacts":{"omitted_contact_groups":13,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":833.0,"contact_point_centroid":[0.65389,0.00051,-0.00043],"force_p95":465.57466,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1515.20547,"mean_force":225.91227,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.43033,0.00046,0.14804]},{"body_a":"world","body_b":"link6","contact_count":999.0,"contact_point_centroid":[0.59581,0.00939,-0.00021],"force_p95":358.72436,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":596.29919,"mean_force":226.74218,"phase_index":5.0,"phase_name":"descend_at_goal","phase_type":"descend","tcp_position_centroid":[0.40483,-0.03066,0.19323]},{"body_a":"world","body_b":"link6","contact_count":455.0,"contact_point_centroid":[0.66332,0.00204,-0.00038],"force_p95":249.76134,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":423.48341,"mean_force":195.72226,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.44949,-0.002,0.16926]},{"body_a":"world","body_b":"link7","contact_count":23.0,"contact_point_centroid":[0.54415,0.00368,-0.00377],"force_p95":0.0,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":316.60739,"mean_force":13.76554,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.39302,2e-05,0.04567]},{"body_a":"world","body_b":"link6","contact_count":993.0,"contact_point_centroid":[0.61017,-0.00196,-0.00027],"force_p95":215.79903,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":278.74971,"mean_force":201.85466,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.36669,-0.03162,0.11553]},{"body_a":"link5","body_b":"hand","contact_count":277.0,"contact_point_centroid":[0.48331,0.07714,0.21132],"force_p95":144.24566,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":222.25927,"mean_force":74.38072,"phase_index":5.0,"phase_name":"descend_at_goal","phase_type":"descend","tcp_position_centroid":[0.43623,-0.01428,0.23866]},{"body_a":"world","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.68568,0.00142,-4e-05],"force_p95":213.00852,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":213.00852,"mean_force":213.00852,"phase_index":1.0,"phase_name":"descend_contact","phase_type":"contact","tcp_position_centroid":[0.46365,0.00114,0.15897]},{"body_a":"world","body_b":"link6","contact_count":549.0,"contact_point_centroid":[0.68691,0.00131,-0.00012],"force_p95":69.86393,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":186.95043,"mean_force":66.97396,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.46338,0.00107,0.15669]},{"body_a":"world","body_b":"link6","contact_count":70.0,"contact_point_centroid":[0.58945,0.02059,-0.00018],"force_p95":100.2231,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":101.15644,"mean_force":78.28491,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.43833,-0.0144,0.23762]},{"body_a":"link5","body_b":"hand","contact_count":212.0,"contact_point_centroid":[0.48168,0.08106,0.21899],"force_p95":46.47922,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":56.35992,"mean_force":11.324,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.43788,-0.01458,0.24436]},{"body_a":"grasp_target","body_b":"link7","contact_count":222.0,"contact_point_centroid":[0.52607,0.00354,0.03161],"force_p95":3.56275,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":5.45634,"mean_force":0.66459,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.40676,0.00015,0.09576]},{"body_a":"grasp_target","body_b":"hand","contact_count":117.0,"contact_point_centroid":[0.50586,0.00496,0.04479],"force_p95":2.34502,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.05477,"mean_force":0.96571,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.40245,0.0001,0.07851]},{"body_a":"world","body_b":"grasp_target","contact_count":3595.0,"contact_point_centroid":[0.51479,0.00484,-0.00237],"force_p95":0.34456,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.18309,"mean_force":0.16194,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.4423,0.00048,0.15977]},{"body_a":"grasp_target","body_b":"link6","contact_count":95.0,"contact_point_centroid":[0.55337,0.0148,0.02206],"force_p95":0.67684,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.73629,"mean_force":0.35176,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.39955,9e-05,0.08081]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.49821,0.01048,-0.00216],"force_p95":0.19917,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.49732,"mean_force":0.13074,"phase_index":5.0,"phase_name":"descend_at_goal","phase_type":"descend","tcp_position_centroid":[0.40485,-0.03065,0.19327]},{"body_a":"grasp_target","body_b":"link6","contact_count":903.0,"contact_point_centroid":[0.53237,-0.00296,0.0226],"force_p95":0.47649,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.49435,"mean_force":0.4175,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.36033,-0.03321,0.10923]}],"total_contact_groups":29},"final_pose_error":0.27521,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.49824,0.01028,0.01602],"final_tcp_position":[0.43834,-0.01445,0.23774],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":272983.97843,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":965.0,"n_steps_budget":1000.0,"object_pos_end":[0.50853,0.00553,0.01602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.27069,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":418.84128,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4885.0,"raw_peak_contact_force":1515.20547,"subtask_id":"reach_pregrasp","tcp_end":[0.46365,0.00114,0.15897],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.14989,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1.0,"n_steps_budget":930.0,"object_pos_end":[0.50853,0.00553,0.01602],"object_pos_start":[0.50853,0.00553,0.01602],"object_to_goal_dist_end":0.27069,"object_to_goal_dist_start":0.27069,"object_z_max":0.01602,"peak_contact_force":547.71799,"phase_name":"descend_contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":5.0,"raw_peak_contact_force":213.00852,"subtask_id":"grasp_contact","tcp_end":[0.46361,0.00108,0.15872],"tcp_start":[0.46365,0.00114,0.15897],"tcp_to_object_dist_end":0.14967,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.50853,0.00553,0.01602],"object_pos_start":[0.50853,0.00553,0.01602],"object_to_goal_dist_end":0.27069,"object_to_goal_dist_start":0.27069,"object_z_max":0.01602,"peak_contact_force":84.98824,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":3522.0,"raw_peak_contact_force":186.95043,"subtask_id":"grasp_contact","tcp_end":[0.46337,0.00105,0.15655],"tcp_start":[0.46337,0.00105,0.15655],"tcp_to_object_dist_end":0.14768,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":455.0,"n_steps_budget":600.0,"object_pos_end":[0.50853,0.00553,0.01602],"object_pos_start":[0.50853,0.00553,0.01602],"object_to_goal_dist_end":0.27069,"object_to_goal_dist_start":0.27069,"object_z_max":0.01602,"peak_contact_force":272983.97843,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":4221.0,"raw_peak_contact_force":423.48341,"subtask_id":"lift_clear","tcp_end":[0.46142,-0.00523,0.19109],"tcp_start":[0.46337,0.00105,0.15655],"tcp_to_object_dist_end":0.18161,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":11.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49925,0.00926,0.01013],"object_pos_start":[0.50853,0.00553,0.01602],"object_to_goal_dist_end":0.27733,"object_to_goal_dist_start":0.27069,"object_z_max":0.01602,"peak_contact_force":215.2535,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":10931.0,"raw_peak_contact_force":278.74971,"subtask_id":"place_goal","tcp_end":[0.34969,-0.03403,0.1],"tcp_start":[0.46142,-0.00523,0.19109],"tcp_to_object_dist_end":0.17978,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":11.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49824,0.01028,0.01602],"object_pos_start":[0.49925,0.00926,0.01013],"object_to_goal_dist_end":0.27352,"object_to_goal_dist_start":0.27733,"object_z_max":0.01602,"peak_contact_force":371.42976,"phase_name":"descend_at_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":9820.0,"raw_peak_contact_force":596.29919,"subtask_id":"place_goal","tcp_end":[0.43834,-0.01445,0.23774],"tcp_start":[0.34969,-0.03403,0.1],"tcp_to_object_dist_end":0.231,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.49824,0.01028,0.01602],"object_pos_start":[0.49824,0.01028,0.01602],"object_to_goal_dist_end":0.27352,"object_to_goal_dist_start":0.27352,"object_z_max":0.01602,"peak_contact_force":3.53805,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1302.0,"raw_peak_contact_force":101.15644,"tcp_end":[0.4373,-0.01491,0.26541],"tcp_start":[0.43834,-0.01445,0.23774],"tcp_to_object_dist_end":0.25796,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":8.22619,"average_solve_count":84.0,"average_success_count":84.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_z":0.10128,"approach_goal.goal_arc_height":0.0986,"approach_object.approach_tolerance":0.02858,"approach_object.approach_z":0.14784,"descend_at_goal.descend_goal_tolerance":0.01067,"descend_contact.contact_force":6.16072,"lift_object.lift_height":0.11273,"release_object.release_duration":0.9379},"optimized_scores":{"best_composite_score":-0.19217,"best_fitness_score":0.21497,"best_task_score":0.28738},"replay_outcomes":[{"contacts":{"omitted_contact_groups":13,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":887.0,"contact_point_centroid":[0.64798,0.01119,-0.00043],"force_p95":221.77761,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1342.23368,"mean_force":203.10642,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.41989,0.01065,0.14137]},{"body_a":"world","body_b":"link7","contact_count":24.0,"contact_point_centroid":[0.53862,0.00951,-0.00327],"force_p95":212.61666,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1292.85786,"mean_force":64.29146,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.38871,0.00521,0.04549]},{"body_a":"world","body_b":"link6","contact_count":921.0,"contact_point_centroid":[0.59617,0.09718,-0.00024],"force_p95":533.53073,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":889.36425,"mean_force":345.02595,"phase_index":5.0,"phase_name":"descend_at_goal","phase_type":"descend","tcp_position_centroid":[0.42085,0.15427,0.20351]},{"body_a":"world","body_b":"link6","contact_count":496.0,"contact_point_centroid":[0.62494,0.02527,-0.00023],"force_p95":533.9475,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":885.64963,"mean_force":306.08518,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.43545,0.03237,0.20343]},{"body_a":"link5","body_b":"hand","contact_count":245.0,"contact_point_centroid":[0.48679,0.07002,0.24994],"force_p95":470.60511,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":670.61449,"mean_force":198.2685,"phase_index":5.0,"phase_name":"descend_at_goal","phase_type":"descend","tcp_position_centroid":[0.43649,0.13416,0.25239]},{"body_a":"world","body_b":"link6","contact_count":994.0,"contact_point_centroid":[0.60026,0.06104,-0.00026],"force_p95":285.67355,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":350.73573,"mean_force":229.92635,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.39554,0.11646,0.17171]},{"body_a":"world","body_b":"link5","contact_count":9.0,"contact_point_centroid":[0.60759,0.23245,-0.0001],"force_p95":307.13714,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":311.55259,"mean_force":195.96837,"phase_index":5.0,"phase_name":"descend_at_goal","phase_type":"descend","tcp_position_centroid":[0.42259,0.14192,0.1823]},{"body_a":"world","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.64679,0.02556,-0.00018],"force_p95":269.75418,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":269.75418,"mean_force":269.75418,"phase_index":1.0,"phase_name":"descend_contact","phase_type":"contact","tcp_position_centroid":[0.45066,0.0199,0.19972]},{"body_a":"world","body_b":"link6","contact_count":549.0,"contact_point_centroid":[0.64716,0.0251,-0.00013],"force_p95":76.02221,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":201.45628,"mean_force":72.21542,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.4509,0.01956,0.19971]},{"body_a":"world","body_b":"link6","contact_count":76.0,"contact_point_centroid":[0.58306,0.14062,-0.00014],"force_p95":75.29183,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":117.16595,"mean_force":50.42567,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.52073,0.15368,0.28577]},{"body_a":"link5","body_b":"hand","contact_count":200.0,"contact_point_centroid":[0.50031,0.0648,0.24536],"force_p95":94.49402,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":114.42697,"mean_force":68.80978,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.52091,0.15427,0.29238]},{"body_a":"grasp_target","body_b":"link7","contact_count":278.0,"contact_point_centroid":[0.50993,0.01491,0.03617],"force_p95":1.05258,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":5.84836,"mean_force":0.64659,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.40217,0.00617,0.09621]},{"body_a":"grasp_target","body_b":"hand","contact_count":251.0,"contact_point_centroid":[0.50155,0.01313,0.05094],"force_p95":1.99383,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.67337,"mean_force":0.56654,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.40133,0.00606,0.09387]},{"body_a":"world","body_b":"grasp_target","contact_count":3396.0,"contact_point_centroid":[0.4984,0.03717,-0.00272],"force_p95":0.40167,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.55098,"mean_force":0.18444,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.4336,0.01051,0.15593]},{"body_a":"grasp_target","body_b":"link6","contact_count":77.0,"contact_point_centroid":[0.51517,0.05087,0.03752],"force_p95":1.17038,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.41877,"mean_force":0.47879,"phase_index":5.0,"phase_name":"descend_at_goal","phase_type":"descend","tcp_position_centroid":[0.48854,0.1499,0.27949]},{"body_a":"world","body_b":"grasp_target","contact_count":3902.0,"contact_point_centroid":[0.48733,0.03931,-0.00208],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86879,"mean_force":0.13298,"phase_index":5.0,"phase_name":"descend_at_goal","phase_type":"descend","tcp_position_centroid":[0.41956,0.15217,0.20365]}],"total_contact_groups":29},"final_pose_error":0.19739,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.48385,0.06345,0.01932],"final_tcp_position":[0.51921,0.15391,0.28579],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":273004.12075,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.48773,0.03868,0.01602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.20249,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":198.14517,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4848.0,"raw_peak_contact_force":1342.23368,"subtask_id":"reach_pregrasp","tcp_end":[0.45066,0.0199,0.19972],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.18834,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.48773,0.03868,0.01602],"object_pos_start":[0.48773,0.03868,0.01602],"object_to_goal_dist_end":0.20249,"object_to_goal_dist_start":0.20249,"object_z_max":0.01602,"peak_contact_force":269.75418,"phase_name":"descend_contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":5.0,"raw_peak_contact_force":269.75418,"subtask_id":"grasp_contact","tcp_end":[0.45072,0.01987,0.1999],"tcp_start":[0.45066,0.0199,0.19972],"tcp_to_object_dist_end":0.18851,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.48773,0.03868,0.01602],"object_pos_start":[0.48773,0.03868,0.01602],"object_to_goal_dist_end":0.20249,"object_to_goal_dist_start":0.20249,"object_z_max":0.01602,"peak_contact_force":273004.12075,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":3509.0,"raw_peak_contact_force":201.45628,"subtask_id":"grasp_contact","tcp_end":[0.45091,0.01955,0.19962],"tcp_start":[0.45091,0.01955,0.19962],"tcp_to_object_dist_end":0.18823,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":513.0,"n_steps_budget":600.0,"object_pos_end":[0.48773,0.03868,0.01602],"object_pos_start":[0.48773,0.03868,0.01602],"object_to_goal_dist_end":0.20249,"object_to_goal_dist_start":0.20249,"object_z_max":0.01602,"peak_contact_force":409.85458,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":4711.0,"raw_peak_contact_force":885.64963,"subtask_id":"lift_clear","tcp_end":[0.45822,0.05524,0.19903],"tcp_start":[0.45091,0.01955,0.19962],"tcp_to_object_dist_end":0.18611,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.48737,0.03884,0.01602],"object_pos_start":[0.48773,0.03868,0.01602],"object_to_goal_dist_end":0.20258,"object_to_goal_dist_start":0.20249,"object_z_max":0.01602,"peak_contact_force":344.6706,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":9400.0,"raw_peak_contact_force":350.73573,"subtask_id":"place_goal","tcp_end":[0.42271,0.15251,0.20139],"tcp_start":[0.45822,0.05524,0.19903],"tcp_to_object_dist_end":0.22686,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.48616,0.0575,0.01481],"object_pos_start":[0.48737,0.03884,0.01602],"object_to_goal_dist_end":0.1915,"object_to_goal_dist_start":0.20258,"object_z_max":0.01602,"peak_contact_force":157782.39763,"phase_name":"descend_at_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":9374.0,"raw_peak_contact_force":889.36425,"subtask_id":"place_goal","tcp_end":[0.51921,0.15391,0.28579],"tcp_start":[0.42271,0.15251,0.20139],"tcp_to_object_dist_end":0.28951,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48385,0.06345,0.01932],"object_pos_start":[0.48616,0.0575,0.01481],"object_to_goal_dist_end":0.18704,"object_to_goal_dist_start":0.1915,"object_z_max":0.02045,"peak_contact_force":94.69891,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1051.0,"raw_peak_contact_force":117.16595,"tcp_end":[0.52206,0.15608,0.31256],"tcp_start":[0.51921,0.15391,0.28579],"tcp_to_object_dist_end":0.30988,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
```