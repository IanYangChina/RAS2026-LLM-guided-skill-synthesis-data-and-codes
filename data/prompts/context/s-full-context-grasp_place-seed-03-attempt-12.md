## Search State

- **Seed**: 3
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | approach → contact → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 7 | -0.1267 | 0.22 | ❌ rejected |
| 11 | approach → contact → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 8 | -0.2169 | 0.19 | ❌ rejected |
| 10 | retract → approach → contact → grasp → lift → approach → descend → release | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 9 | -0.3474 | 0.27 | ✅ accepted |
| 9 | approach → descend → contact → grasp → lift → approach → descend → release | arc_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 9 | -0.3300 | 0.20 | ❌ rejected |
| 8 | approach → descend → contact → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 9 | -0.3745 | 0.16 | ❌ rejected |

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

## Current Skill (Q=-0.127) — your mutation base

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

- **Composite score**: -0.127
- **task_score** (E): 0.224
- **fitness_score**: 0.230  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.143
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.500

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 0.33 | 1.00 | 0.1549 |
| descend_contact | 1.00 | 1.00 | 0.0290 |
| grasp_object | 1.00 | 1.00 | 0.0000 |
| lift_object | 0.00 | 1.00 | 0.0650 |
| approach_goal | 0.00 | 1.00 | 0.1698 |
| descend_at_goal | 0.00 | 1.00 | 0.0663 |
| release_object | 1.00 | 1.00 | 0.0277 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 0.33 / step_budget | (0.500, -0.000, 0.301)→(0.435, 0.002, 0.183) | (0.511, 0.002, 0.030)→(0.487, 0.007, 0.020) | 0.244→0.257 | 1.00 / 4.667 | 138.670 | 993.298 |
| descend_contact | contact | 1.00 / force_exceeded | (0.435, 0.002, 0.183)→(0.440, 0.002, 0.155) | (0.487, 0.007, 0.020)→(0.487, 0.007, 0.019) | 0.257→0.258 | 1.00 / 4.667 | 335.156 | 285.835 |
| grasp_object | grasp | 1.00 / step_budget | (0.406, 0.001, 0.082)→(0.406, 0.001, 0.082) | (0.487, 0.007, 0.019)→(0.484, 0.007, 0.016) | 0.258→0.261 | 1.00 / 16.333 | 91024.948 | 386.202 |
| lift_object | lift | 0.00 / step_budget | (0.406, 0.001, 0.082)→(0.447, 0.003, 0.118) | (0.484, 0.007, 0.016)→(0.484, 0.007, 0.016) | 0.261→0.261 | 1.00 / 16.667 | 91041.163 | 536.815 |
| approach_goal | approach | 0.00 / step_budget | (0.447, 0.003, 0.118)→(0.489, 0.050, 0.243) | (0.484, 0.007, 0.016)→(0.482, 0.035, 0.016) | 0.261→0.246 | 1.00 / 9.667 | 91458.912 | 671.717 |
| descend_at_goal | descend | 0.00 / step_budget | (0.489, 0.050, 0.243)→(0.527, 0.072, 0.275) | (0.482, 0.035, 0.016)→(0.487, 0.048, 0.016) | 0.246→0.238 | 1.00 / 9.667 | 182050.443 | 659.834 |
| release_object | release | 1.00 / step_budget | (0.527, 0.072, 0.275)→(0.527, 0.072, 0.303) | (0.487, 0.048, 0.016)→(0.488, 0.048, 0.016) | 0.238→0.238 | 1.00 / 4.000 | 0.141 | 107.526 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 0.000
- place_accuracy: 0.000
- lift_clearance: 0.000
- transport_retention: 0.000
- terminal_score: 0.243
- phase_score: 0.355
- phase_breakdown.reach_above_object_score: 0.222
- phase_breakdown.lift_clear_score: 0.017
- phase_breakdown.grasp_contact_score: 1.000
- phase_breakdown.place_goal_score: 0.025
- grasp_place_fitness: 0.260

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.260
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.320
- **Median Q (composite search score)**: -0.115
- **K-run variance**: 0.0009
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.525


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":7.29545,"average_solve_count":88.0,"average_success_count":88.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_z":0.09049,"approach_goal.goal_arc_height":0.07388,"approach_object.approach_z":0.231,"descend_at_goal.descend_goal_tolerance":0.01121,"descend_contact.contact_force":9.53362,"lift_object.lift_height":0.19233,"release_object.release_duration":1.2323},"optimized_scores":{"best_composite_score":-0.16886,"best_fitness_score":0.18829,"best_task_score":0.10986},"replay_outcomes":[{"contacts":{"omitted_contact_groups":8,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":886.0,"contact_point_centroid":[0.61805,-0.01274,-0.00046],"force_p95":215.22086,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1533.69222,"mean_force":212.36931,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.36847,-0.00941,0.0965]},{"body_a":"world","body_b":"link6","contact_count":989.0,"contact_point_centroid":[0.5751,0.02415,-0.00022],"force_p95":424.75948,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":780.66178,"mean_force":260.61263,"phase_index":5.0,"phase_name":"descend_at_goal","phase_type":"descend","tcp_position_centroid":[0.39021,-0.00448,0.1983]},{"body_a":"world","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.61016,-0.02248,-0.00027],"force_p95":553.60112,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":553.60112,"mean_force":553.60112,"phase_index":1.0,"phase_name":"descend_contact","phase_type":"contact","tcp_position_centroid":[0.36229,-0.01661,0.09332]},{"body_a":"world","body_b":"link6","contact_count":669.0,"contact_point_centroid":[0.61205,-0.01879,-0.00026],"force_p95":206.17581,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":521.5419,"mean_force":204.30712,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.36352,-0.02395,0.09776]},{"body_a":"world","body_b":"link6","contact_count":1000.0,"contact_point_centroid":[0.60846,-0.01633,-0.00021],"force_p95":227.00579,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":520.29294,"mean_force":211.58537,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.36843,-0.02886,0.12834]},{"body_a":"world","body_b":"link6","contact_count":550.0,"contact_point_centroid":[0.61106,-0.02316,-0.00013],"force_p95":80.86261,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":150.9974,"mean_force":71.46429,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.36299,-0.01713,0.09304]},{"body_a":"world","body_b":"link6","contact_count":71.0,"contact_point_centroid":[0.57533,0.05405,-0.00017],"force_p95":100.14992,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":110.54137,"mean_force":77.05484,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.42952,0.02074,0.24114]},{"body_a":"grasp_target","body_b":"hand","contact_count":38.0,"contact_point_centroid":[0.43986,-0.02025,0.04302],"force_p95":3.52408,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.94861,"mean_force":1.57248,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.3736,-0.00448,0.05496]},{"body_a":"world","body_b":"grasp_target","contact_count":3922.0,"contact_point_centroid":[0.42222,-0.0258,-0.00212],"force_p95":0.13759,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.2326,"mean_force":0.13741,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.3823,-0.00873,0.10855]},{"body_a":"grasp_target","body_b":"link7","contact_count":18.0,"contact_point_centroid":[0.46862,-0.00902,0.0097],"force_p95":0.43602,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.44453,"mean_force":0.20168,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.36265,-0.00454,0.05399]},{"body_a":"world","body_b":"grasp_target","contact_count":2676.0,"contact_point_centroid":[0.41709,-0.02573,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12965,"mean_force":0.12265,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.36352,-0.02395,0.09776]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.41708,-0.02574,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12677,"mean_force":0.12263,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.36843,-0.02886,0.12834]},{"body_a":"world","body_b":"grasp_target","contact_count":4.0,"contact_point_centroid":[0.41709,-0.02573,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_contact","phase_type":"contact","tcp_position_centroid":[0.36229,-0.01661,0.09332]},{"body_a":"world","body_b":"grasp_target","contact_count":2200.0,"contact_point_centroid":[0.41709,-0.02573,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.36299,-0.01713,0.09304]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.41708,-0.02574,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_at_goal","phase_type":"descend","tcp_position_centroid":[0.39029,-0.00442,0.19849]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.41708,-0.02574,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.42913,0.0206,0.2485]}],"total_contact_groups":24},"final_pose_error":0.30248,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.41708,-0.02574,0.01602],"final_tcp_position":[0.42969,0.02085,0.24146],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":273005.9492,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.41709,-0.02573,0.01602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.33127,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":214.88963,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4883.0,"raw_peak_contact_force":1533.69222,"subtask_id":"reach_above_object","tcp_end":[0.36229,-0.01661,0.09332],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.09519,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1.0,"n_steps_budget":630.0,"object_pos_end":[0.41709,-0.02573,0.01602],"object_pos_start":[0.41709,-0.02573,0.01602],"object_to_goal_dist_end":0.33127,"object_to_goal_dist_start":0.33127,"object_z_max":0.01602,"peak_contact_force":553.60112,"phase_name":"descend_contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":5.0,"raw_peak_contact_force":553.60112,"subtask_id":"grasp_contact","tcp_end":[0.36242,-0.01665,0.09354],"tcp_start":[0.36229,-0.01661,0.09332],"tcp_to_object_dist_end":0.09529,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.41709,-0.02573,0.01602],"object_pos_start":[0.41709,-0.02573,0.01602],"object_to_goal_dist_end":0.33127,"object_to_goal_dist_start":0.33127,"object_z_max":0.01602,"peak_contact_force":273004.12066,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":3495.0,"raw_peak_contact_force":150.9974,"subtask_id":"grasp_contact","tcp_end":[0.36313,-0.01718,0.09284],"tcp_start":[0.36312,-0.01717,0.09284],"tcp_to_object_dist_end":0.09427,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":669.0,"n_steps_budget":810.0,"object_pos_end":[0.41706,-0.02577,0.016],"object_pos_start":[0.41709,-0.02573,0.01602],"object_to_goal_dist_end":0.33132,"object_to_goal_dist_start":0.33127,"object_z_max":0.01602,"peak_contact_force":204.57523,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":6166.0,"raw_peak_contact_force":521.5419,"subtask_id":"lift_clear","tcp_end":[0.35451,-0.0296,0.08373],"tcp_start":[0.36313,-0.01718,0.09284],"tcp_to_object_dist_end":0.09227,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.41708,-0.02574,0.01602],"object_pos_start":[0.41706,-0.02577,0.016],"object_to_goal_dist_end":0.33128,"object_to_goal_dist_start":0.33132,"object_z_max":0.01602,"peak_contact_force":216.64964,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":9206.0,"raw_peak_contact_force":520.29294,"subtask_id":"place_goal","tcp_end":[0.36838,-0.01184,0.15247],"tcp_start":[0.35451,-0.0296,0.08373],"tcp_to_object_dist_end":0.14555,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.41708,-0.02574,0.01602],"object_pos_start":[0.41708,-0.02574,0.01602],"object_to_goal_dist_end":0.33128,"object_to_goal_dist_start":0.33128,"object_z_max":0.01602,"peak_contact_force":273005.9492,"phase_name":"descend_at_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":9275.0,"raw_peak_contact_force":780.66178,"subtask_id":"place_goal","tcp_end":[0.42969,0.02085,0.24146],"tcp_start":[0.36838,-0.01184,0.15247],"tcp_to_object_dist_end":0.23055,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.41708,-0.02574,0.01602],"object_pos_start":[0.41708,-0.02574,0.01602],"object_to_goal_dist_end":0.33128,"object_to_goal_dist_start":0.33128,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1100.0,"raw_peak_contact_force":110.54137,"tcp_end":[0.42885,0.0205,0.2698],"tcp_start":[0.42969,0.02085,0.24146],"tcp_to_object_dist_end":0.25823,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":45.0,"average_failure_rate":0.43269,"average_mean_iterations":90.23077,"average_solve_count":104.0,"average_success_count":59.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_z":0.10177,"approach_goal.goal_arc_height":0.10195,"approach_object.approach_z":0.28034,"descend_at_goal.descend_goal_tolerance":0.01612,"descend_contact.contact_force":9.39255,"lift_object.lift_height":0.12464,"release_object.release_duration":0.93096},"optimized_scores":{"best_composite_score":-0.09687,"best_fitness_score":0.26027,"best_task_score":0.24276},"replay_outcomes":[{"contacts":{"omitted_contact_groups":11,"reported_contact_groups":[{"body_a":"world","body_b":"hand","contact_count":53.0,"contact_point_centroid":[0.48694,-0.02868,-0.00249],"force_p95":528.48636,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":713.1862,"mean_force":91.99984,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.44255,4e-05,-0.00794]},{"body_a":"world","body_b":"link7","contact_count":23.0,"contact_point_centroid":[0.57749,-0.00114,-0.00131],"force_p95":607.84393,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":681.08132,"mean_force":307.14351,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.45775,-0.00249,0.02568]},{"body_a":"world","body_b":"link6","contact_count":977.0,"contact_point_centroid":[0.52183,-0.0085,-0.00027],"force_p95":517.1658,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":582.22304,"mean_force":391.17334,"phase_index":5.0,"phase_name":"descend_at_goal","phase_type":"descend","tcp_position_centroid":[0.52787,0.00898,0.29318]},{"body_a":"link5","body_b":"hand","contact_count":20.0,"contact_point_centroid":[0.46134,-0.09706,0.24436],"force_p95":407.19482,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":427.59424,"mean_force":245.28327,"phase_index":5.0,"phase_name":"descend_at_goal","phase_type":"descend","tcp_position_centroid":[0.49749,-0.01065,0.28738]},{"body_a":"world","body_b":"link6","contact_count":902.0,"contact_point_centroid":[0.61779,-0.04235,-0.00016],"force_p95":291.4181,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":375.7347,"mean_force":219.88566,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.49286,0.00205,0.2159]},{"body_a":"link5","body_b":"hand","contact_count":542.0,"contact_point_centroid":[0.47341,-0.10124,0.24076],"force_p95":278.9793,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":313.56162,"mean_force":266.37322,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.50323,-0.01167,0.28026]},{"body_a":"world","body_b":"link6","contact_count":81.0,"contact_point_centroid":[0.55429,0.01604,-0.00017],"force_p95":89.08143,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":89.28068,"mean_force":63.53676,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.55565,0.03476,0.29355]},{"body_a":"world","body_b":"right_finger","contact_count":6641.0,"contact_point_centroid":[0.45121,0.04138,-0.0033],"force_p95":2.64956,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":28.44868,"mean_force":1.49019,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.4469,-8e-05,-0.00082]},{"body_a":"world","body_b":"left_finger","contact_count":6965.0,"contact_point_centroid":[0.45163,-0.04138,-0.00329],"force_p95":2.68151,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":27.76477,"mean_force":1.48473,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.44697,-8e-05,-0.00075]},{"body_a":"world","body_b":"right_finger","contact_count":178.0,"contact_point_centroid":[0.4535,0.0392,-0.00211],"force_p95":7.5516,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":9.3899,"mean_force":4.21179,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.45136,-0.00062,0.00333]},{"body_a":"world","body_b":"left_finger","contact_count":201.0,"contact_point_centroid":[0.45572,-0.04022,-0.00217],"force_p95":8.53563,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":8.87607,"mean_force":5.41547,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.45168,-0.00067,0.0037]},{"body_a":"grasp_target","body_b":"hand","contact_count":512.0,"contact_point_centroid":[0.5361,0.0017,0.03171],"force_p95":1.37062,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.74568,"mean_force":1.06285,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.44772,-9e-05,0.00025]},{"body_a":"grasp_target","body_b":"link7","contact_count":329.0,"contact_point_centroid":[0.56155,0.00612,0.0378],"force_p95":0.85624,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.09905,"mean_force":0.4247,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.46279,0.01471,0.07323]},{"body_a":"grasp_target","body_b":"hand","contact_count":313.0,"contact_point_centroid":[0.55486,0.00542,0.04016],"force_p95":1.49112,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.00637,"mean_force":0.62615,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.46187,0.01068,0.07235]},{"body_a":"grasp_target","body_b":"link6","contact_count":979.0,"contact_point_centroid":[0.5451,0.0347,0.03357],"force_p95":0.44902,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.85762,"mean_force":0.38006,"phase_index":5.0,"phase_name":"descend_at_goal","phase_type":"descend","tcp_position_centroid":[0.52787,0.00893,0.29324]},{"body_a":"world","body_b":"grasp_target","contact_count":2136.0,"contact_point_centroid":[0.54233,0.00124,-0.00567],"force_p95":0.58523,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.36636,"mean_force":0.37432,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.45292,-9e-05,0.00984]}],"total_contact_groups":27},"final_pose_error":0.18456,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.55812,0.0786,0.01571],"final_tcp_position":[0.55563,0.03488,0.29318],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":1366.84211,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":29.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.0266],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.24974,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.13762,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":112.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_above_object","tcp_end":[0.53709,0.00068,0.30493],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.27843,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":32.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02587],"object_pos_start":[0.54431,0.00113,0.0266],"object_to_goal_dist_end":0.25022,"object_to_goal_dist_start":0.24974,"object_z_max":0.0266,"peak_contact_force":82.26629,"phase_name":"descend_contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":128.0,"raw_peak_contact_force":0.13728,"subtask_id":"grasp_contact","tcp_end":[0.55085,0.00016,0.21938],"tcp_start":[0.53709,0.00068,0.30493],"tcp_to_object_dist_end":0.19363,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":30.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.53594,0.00096,0.01712],"object_pos_start":[0.54431,0.00113,0.02587],"object_to_goal_dist_end":0.25967,"object_to_goal_dist_start":0.25022,"object_z_max":0.02601,"peak_contact_force":1.97737,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":16812.0,"raw_peak_contact_force":713.1862,"subtask_id":"grasp_contact","tcp_end":[0.44926,-0.00018,0.00104],"tcp_start":[0.4492,-0.00018,0.00103],"tcp_to_object_dist_end":0.08817,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":30.0,"n_steps":0.0,"n_steps_budget":1000.0,"object_pos_end":[0.53623,0.00099,0.01715],"object_pos_start":[0.53623,0.00099,0.01715],"object_to_goal_dist_end":0.25951,"object_to_goal_dist_start":0.25951,"peak_contact_force":1.97843,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"lift_clear","tcp_end":[0.44926,-0.00018,0.00104],"tcp_start":[0.44926,-0.00018,0.00104],"tcp_to_object_dist_end":0.08846,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54028,0.03957,0.01602],"object_pos_start":[0.53623,0.00099,0.01715],"object_to_goal_dist_end":0.23711,"object_to_goal_dist_start":0.25951,"object_z_max":0.02565,"peak_contact_force":1366.84211,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":9890.0,"raw_peak_contact_force":681.08132,"subtask_id":"place_goal","tcp_end":[0.49704,-0.00881,0.28413],"tcp_start":[0.44926,-0.00018,0.00104],"tcp_to_object_dist_end":0.27585,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5577,0.07776,0.01689],"object_pos_start":[0.54028,0.03957,0.01602],"object_to_goal_dist_end":0.21187,"object_to_goal_dist_start":0.23711,"object_z_max":0.01721,"peak_contact_force":136.72825,"phase_name":"descend_at_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":9477.0,"raw_peak_contact_force":582.22304,"subtask_id":"place_goal","tcp_end":[0.55563,0.03488,0.29318],"tcp_start":[0.49704,-0.00881,0.28413],"tcp_to_object_dist_end":0.2796,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.55812,0.0786,0.01571],"object_pos_start":[0.5577,0.07776,0.01689],"object_to_goal_dist_end":0.21235,"object_to_goal_dist_start":0.21187,"object_z_max":0.02154,"peak_contact_force":0.17739,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":993.0,"raw_peak_contact_force":89.28068,"tcp_end":[0.55581,0.03429,0.32134],"tcp_start":[0.55563,0.03488,0.29318],"tcp_to_object_dist_end":0.30883,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":6.28571,"average_solve_count":91.0,"average_success_count":91.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_z":0.11016,"approach_goal.goal_arc_height":0.08111,"approach_object.approach_z":0.28041,"descend_at_goal.descend_goal_tolerance":0.00622,"descend_contact.contact_force":10.87467,"lift_object.lift_height":0.08426,"release_object.release_duration":1.84217},"optimized_scores":{"best_composite_score":-0.1145,"best_fitness_score":0.24264,"best_task_score":0.3203},"replay_outcomes":[{"contacts":{"omitted_contact_groups":8,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":617.0,"contact_point_centroid":[0.63655,0.01697,-0.00053],"force_p95":205.25415,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1446.06204,"mean_force":207.52535,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.39721,0.01564,0.1273]},{"body_a":"world","body_b":"link6","contact_count":585.0,"contact_point_centroid":[0.63499,0.02513,-0.0002],"force_p95":604.27236,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1088.90351,"mean_force":290.67567,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.4359,0.03365,0.18756]},{"body_a":"world","body_b":"link6","contact_count":271.0,"contact_point_centroid":[0.58262,0.10281,-0.00019],"force_p95":517.53741,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":813.77611,"mean_force":358.36407,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.58091,0.12163,0.29223]},{"body_a":"world","body_b":"link6","contact_count":1000.0,"contact_point_centroid":[0.60488,0.16671,-0.00032],"force_p95":487.83689,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":616.61676,"mean_force":371.52233,"phase_index":5.0,"phase_name":"descend_at_goal","phase_type":"descend","tcp_position_centroid":[0.60443,0.17252,0.29343]},{"body_a":"world","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.63265,0.02153,-0.00024],"force_p95":303.76672,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":303.76672,"mean_force":303.76672,"phase_index":1.0,"phase_name":"descend_contact","phase_type":"contact","tcp_position_centroid":[0.40586,0.02155,0.1517]},{"body_a":"world","body_b":"link6","contact_count":550.0,"contact_point_centroid":[0.63329,0.02093,-0.00013],"force_p95":78.62166,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":294.42145,"mean_force":72.839,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.40622,0.02103,0.1515]},{"body_a":"world","body_b":"link6","contact_count":84.0,"contact_point_centroid":[0.6346,0.15786,-0.00013],"force_p95":76.17309,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":122.75624,"mean_force":56.5718,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.59688,0.16001,0.29214]},{"body_a":"grasp_target","body_b":"link7","contact_count":279.0,"contact_point_centroid":[0.51594,0.02345,0.03418],"force_p95":2.67157,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.28918,"mean_force":0.40687,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.3923,0.0126,0.10771]},{"body_a":"grasp_target","body_b":"hand","contact_count":99.0,"contact_point_centroid":[0.4941,0.04226,0.05166],"force_p95":2.07099,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.95165,"mean_force":0.84755,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.3873,0.01148,0.08592]},{"body_a":"world","body_b":"grasp_target","contact_count":2618.0,"contact_point_centroid":[0.50661,0.04171,-0.00234],"force_p95":0.41096,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.87533,"mean_force":0.16827,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.41572,0.01475,0.14308]},{"body_a":"grasp_target","body_b":"link6","contact_count":645.0,"contact_point_centroid":[0.50231,0.06639,0.03963],"force_p95":0.69225,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.09914,"mean_force":0.34211,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.56291,0.08866,0.30323]},{"body_a":"grasp_target","body_b":"link6","contact_count":120.0,"contact_point_centroid":[0.53818,0.04185,0.03019],"force_p95":0.81342,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.89777,"mean_force":0.41608,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.38675,0.01174,0.09715]},{"body_a":"world","body_b":"grasp_target","contact_count":2943.0,"contact_point_centroid":[0.48268,0.07927,-0.00331],"force_p95":0.67555,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.70364,"mean_force":0.22223,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.57269,0.10887,0.30187]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.48738,0.09109,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12389,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_at_goal","phase_type":"descend","tcp_position_centroid":[0.60443,0.17252,0.29343]},{"body_a":"world","body_b":"grasp_target","contact_count":4.0,"contact_point_centroid":[0.49979,0.04558,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_contact","phase_type":"contact","tcp_position_centroid":[0.40586,0.02155,0.1517]},{"body_a":"world","body_b":"grasp_target","contact_count":2200.0,"contact_point_centroid":[0.49979,0.04558,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.40622,0.02103,0.1515]}],"total_contact_groups":24},"final_pose_error":0.18467,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.48738,0.09109,0.01602],"final_tcp_position":[0.59684,0.16041,0.2918],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":273008.65228,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":734.0,"n_steps_budget":1000.0,"object_pos_end":[0.49979,0.04558,0.01602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.19109,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":200.98176,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3748.0,"raw_peak_contact_force":1446.06204,"subtask_id":"reach_above_object","tcp_end":[0.40586,0.02155,0.1517],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16676,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.49979,0.04558,0.01602],"object_pos_start":[0.49979,0.04558,0.01602],"object_to_goal_dist_end":0.19109,"object_to_goal_dist_start":0.19109,"object_z_max":0.01602,"peak_contact_force":369.60011,"phase_name":"descend_contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":5.0,"raw_peak_contact_force":303.76672,"subtask_id":"grasp_contact","tcp_end":[0.40586,0.02145,0.15176],"tcp_start":[0.40586,0.02155,0.1517],"tcp_to_object_dist_end":0.16683,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.49979,0.04558,0.01602],"object_pos_start":[0.49979,0.04558,0.01602],"object_to_goal_dist_end":0.19109,"object_to_goal_dist_start":0.19109,"object_z_max":0.01602,"peak_contact_force":68.74686,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":3495.0,"raw_peak_contact_force":294.42145,"subtask_id":"grasp_contact","tcp_end":[0.40629,0.02099,0.15135],"tcp_start":[0.40628,0.02099,0.15135],"tcp_to_object_dist_end":0.16632,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":632.0,"n_steps_budget":690.0,"object_pos_end":[0.49979,0.04558,0.01602],"object_pos_start":[0.49979,0.04558,0.01602],"object_to_goal_dist_end":0.19109,"object_to_goal_dist_start":0.19109,"object_z_max":0.01602,"peak_contact_force":272916.93471,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":5796.0,"raw_peak_contact_force":1088.90351,"subtask_id":"lift_clear","tcp_end":[0.53865,0.03811,0.26829],"tcp_start":[0.40629,0.02099,0.15135],"tcp_to_object_dist_end":0.25536,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.48738,0.09108,0.01603],"object_pos_start":[0.49979,0.04558,0.01602],"object_to_goal_dist_end":0.17078,"object_to_goal_dist_start":0.19109,"object_z_max":0.01984,"peak_contact_force":272793.24495,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8224.0,"raw_peak_contact_force":813.77611,"subtask_id":"place_goal","tcp_end":[0.60306,0.17111,0.29332],"tcp_start":[0.53865,0.03811,0.26829],"tcp_to_object_dist_end":0.31093,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.48738,0.09109,0.01602],"object_pos_start":[0.48738,0.09108,0.01603],"object_to_goal_dist_end":0.17077,"object_to_goal_dist_start":0.17078,"object_z_max":0.01603,"peak_contact_force":273008.65228,"phase_name":"descend_at_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":9299.0,"raw_peak_contact_force":616.61676,"subtask_id":"place_goal","tcp_end":[0.59684,0.16041,0.2918],"tcp_start":[0.60306,0.17111,0.29332],"tcp_to_object_dist_end":0.3047,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48738,0.09109,0.01602],"object_pos_start":[0.48738,0.09109,0.01602],"object_to_goal_dist_end":0.17077,"object_to_goal_dist_start":0.17077,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1108.0,"raw_peak_contact_force":122.75624,"tcp_end":[0.59709,0.15995,0.31835],"tcp_start":[0.59684,0.16041,0.2918],"tcp_to_object_dist_end":0.32891,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
```