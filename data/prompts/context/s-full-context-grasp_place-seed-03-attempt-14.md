## Search State

- **Seed**: 3
- **Iteration**: 15 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 14 | approach → contact → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 8 | -0.1935 | 0.22 | ❌ rejected |
| 13 | retract → approach → contact → grasp → lift → approach → descend → release | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 9 | -0.3646 | 0.25 | ❌ rejected |
| 12 | approach → contact → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 7 | -0.1267 | 0.22 | ❌ rejected |
| 11 | approach → contact → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 8 | -0.2169 | 0.19 | ❌ rejected |
| 10 | retract → approach → contact → grasp → lift → approach → descend → release | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 9 | -0.3474 | 0.27 | ✅ accepted |

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

## Current Skill (Q=-0.194) — your mutation base

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

- **Composite score**: -0.194
- **task_score** (E): 0.219
- **fitness_score**: 0.214  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.143
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.550

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 0.00 | 1.00 | 0.1748 |
| descend_contact | 1.00 | 1.00 | 0.0002 |
| grasp_object | 1.00 | 1.00 | 0.0000 |
| lift_object | 0.00 | 1.00 | 0.1006 |
| approach_goal | 0.33 | 1.00 | 0.1490 |
| descend_at_goal | 0.00 | 1.00 | 0.0888 |
| release_object | 1.00 | 1.00 | 0.0260 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 0.00 / step_budget | (0.500, -0.000, 0.301)→(0.435, -0.010, 0.142) | (0.511, 0.002, 0.030)→(0.472, 0.006, 0.016) | 0.244→0.267 | 1.00 / 5.000 | 268.302 | 1379.113 |
| descend_contact | contact | 1.00 / force_exceeded | (0.435, -0.010, 0.142)→(0.435, -0.010, 0.142) | (0.472, 0.006, 0.016)→(0.472, 0.006, 0.016) | 0.267→0.267 | 1.00 / 5.000 | 514.829 | 401.785 |
| grasp_object | grasp | 1.00 / step_budget | (0.435, -0.011, 0.141)→(0.435, -0.011, 0.141) | (0.472, 0.006, 0.016)→(0.472, 0.006, 0.016) | 0.267→0.267 | 1.00 / 9.333 | 91051.956 | 134.345 |
| lift_object | lift | 0.00 / step_budget | (0.435, -0.011, 0.141)→(0.476, -0.013, 0.227) | (0.472, 0.006, 0.016)→(0.472, 0.018, 0.016) | 0.267→0.261 | 1.00 / 9.667 | 594.244 | 519.811 |
| approach_goal | approach | 0.33 / step_budget | (0.476, -0.013, 0.227)→(0.532, 0.099, 0.244) | (0.472, 0.018, 0.016)→(0.472, 0.046, 0.016) | 0.261→0.245 | 1.00 / 9.333 | 118.717 | 516.997 |
| descend_at_goal | descend | 0.00 / step_budget | (0.532, 0.099, 0.244)→(0.573, 0.116, 0.270) | (0.472, 0.046, 0.016)→(0.472, 0.045, 0.016) | 0.245→0.246 | 1.00 / 9.333 | 91222.063 | 722.769 |
| release_object | release | 1.00 / step_budget | (0.573, 0.116, 0.270)→(0.573, 0.115, 0.296) | (0.472, 0.045, 0.016)→(0.472, 0.045, 0.016) | 0.246→0.246 | 1.00 / 4.000 | 0.123 | 132.795 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 0.000
- place_accuracy: 0.000
- lift_clearance: 0.000
- transport_retention: 0.000
- terminal_score: 0.366
- phase_score: 0.383
- phase_breakdown.lift_clear_score: 0.120
- phase_breakdown.reach_pregrasp_score: 0.213
- phase_breakdown.grasp_contact_score: 1.000
- phase_breakdown.place_goal_score: 0.025
- grasp_place_fitness: 0.273

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.273
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.366
- **Median Q (composite search score)**: -0.221
- **K-run variance**: 0.0018
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Parameters at upper bound**: approach_object.approach_z
- **Final σ (mean)**: 0.312


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":7.36905,"average_solve_count":84.0,"average_success_count":84.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_z":0.13638,"approach_goal.goal_arc_height":0.10832,"approach_object.approach_speed":0.38831,"approach_object.approach_z":0.2,"descend_at_goal.descend_goal_tolerance":0.00818,"descend_contact.contact_force":12.74757,"lift_object.lift_height":0.16037,"release_object.release_duration":1.41921},"optimized_scores":{"best_composite_score":-0.22555,"best_fitness_score":0.1816,"best_task_score":0.11083},"replay_outcomes":[{"contacts":{"omitted_contact_groups":10,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":792.0,"contact_point_centroid":[0.6268,-0.01225,-0.00049],"force_p95":211.96215,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1311.41522,"mean_force":210.57894,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.37575,-0.01135,0.10136]},{"body_a":"world","body_b":"link7","contact_count":22.0,"contact_point_centroid":[0.51902,-0.00408,-0.00309],"force_p95":377.97354,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1226.61161,"mean_force":73.83993,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.36667,-0.00677,0.04869]},{"body_a":"world","body_b":"link6","contact_count":990.0,"contact_point_centroid":[0.60627,0.015,-0.00022],"force_p95":389.69376,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":776.61731,"mean_force":274.32204,"phase_index":5.0,"phase_name":"descend_at_goal","phase_type":"descend","tcp_position_centroid":[0.42166,-0.01081,0.20373]},{"body_a":"world","body_b":"link6","contact_count":1000.0,"contact_point_centroid":[0.59956,-0.01509,-0.00026],"force_p95":232.00596,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":491.92623,"mean_force":211.68879,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.35214,-0.03444,0.08215]},{"body_a":"world","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.62498,-0.01812,-0.00026],"force_p95":429.53346,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":429.53346,"mean_force":429.53346,"phase_index":1.0,"phase_name":"descend_contact","phase_type":"contact","tcp_position_centroid":[0.37526,-0.01788,0.11007]},{"body_a":"world","body_b":"link6","contact_count":508.0,"contact_point_centroid":[0.62352,-0.02134,-0.00026],"force_p95":202.05345,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":422.70317,"mean_force":201.41791,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.3739,-0.02322,0.11027]},{"body_a":"world","body_b":"link6","contact_count":68.0,"contact_point_centroid":[0.61726,0.03503,-0.00016],"force_p95":92.87953,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":125.18262,"mean_force":76.70302,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.44914,0.00959,0.22246]},{"body_a":"world","body_b":"link6","contact_count":550.0,"contact_point_centroid":[0.62582,-0.01825,-0.00013],"force_p95":83.45483,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":96.66408,"mean_force":70.81289,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.37583,-0.018,0.10972]},{"body_a":"grasp_target","body_b":"hand","contact_count":39.0,"contact_point_centroid":[0.43891,-0.01381,0.04182],"force_p95":3.58258,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.99222,"mean_force":1.57582,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.37763,-0.00678,0.05058]},{"body_a":"world","body_b":"grasp_target","contact_count":3545.0,"contact_point_centroid":[0.42311,-0.02461,-0.00214],"force_p95":0.13814,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.32193,"mean_force":0.13996,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.39027,-0.01056,0.1142]},{"body_a":"grasp_target","body_b":"link7","contact_count":9.0,"contact_point_centroid":[0.44358,-0.00651,0.03402],"force_p95":0.96196,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.97904,"mean_force":0.79309,"phase_index":5.0,"phase_name":"descend_at_goal","phase_type":"descend","tcp_position_centroid":[0.34365,-0.02757,0.07541]},{"body_a":"grasp_target","body_b":"hand","contact_count":11.0,"contact_point_centroid":[0.4435,-0.02743,0.03335],"force_p95":0.78223,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.78417,"mean_force":0.51661,"phase_index":5.0,"phase_name":"descend_at_goal","phase_type":"descend","tcp_position_centroid":[0.34425,-0.02783,0.07686]},{"body_a":"grasp_target","body_b":"link7","contact_count":14.0,"contact_point_centroid":[0.46995,-0.01064,0.00891],"force_p95":0.36796,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.37178,"mean_force":0.18181,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.36545,-0.00676,0.04767]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.41413,-0.02113,-0.00198],"force_p95":0.12444,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.32861,"mean_force":0.12206,"phase_index":5.0,"phase_name":"descend_at_goal","phase_type":"descend","tcp_position_centroid":[0.42178,-0.01074,0.20389]},{"body_a":"grasp_target","body_b":"hand","contact_count":630.0,"contact_point_centroid":[0.44548,-0.03133,0.03243],"force_p95":0.20879,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27362,"mean_force":0.15872,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.34688,-0.03364,0.07497]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.41661,-0.02382,-0.00238],"force_p95":0.23466,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.26116,"mean_force":0.14988,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.35214,-0.03444,0.08215]}],"total_contact_groups":26},"final_pose_error":0.28983,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.41414,-0.02113,0.01602],"final_tcp_position":[0.44922,0.00955,0.22279],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":272997.0727,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":905.0,"n_steps_budget":1000.0,"object_pos_end":[0.41763,-0.02433,0.01602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.32993,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":210.63909,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4412.0,"raw_peak_contact_force":1311.41522,"subtask_id":"reach_pregrasp","tcp_end":[0.37526,-0.01788,0.11007],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.10335,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.41763,-0.02433,0.01602],"object_pos_start":[0.41763,-0.02433,0.01602],"object_to_goal_dist_end":0.32993,"object_to_goal_dist_start":0.32993,"object_z_max":0.01602,"peak_contact_force":768.66598,"phase_name":"descend_contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":5.0,"raw_peak_contact_force":429.53346,"subtask_id":"grasp_contact","tcp_end":[0.37529,-0.01786,0.11025],"tcp_start":[0.37526,-0.01788,0.11007],"tcp_to_object_dist_end":0.10351,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.41763,-0.02433,0.01602],"object_pos_start":[0.41763,-0.02433,0.01602],"object_to_goal_dist_end":0.32993,"object_to_goal_dist_start":0.32993,"object_z_max":0.01602,"peak_contact_force":66.4975,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":3508.0,"raw_peak_contact_force":96.66408,"subtask_id":"grasp_contact","tcp_end":[0.37596,-0.01803,0.10952],"tcp_start":[0.37595,-0.01803,0.10952],"tcp_to_object_dist_end":0.10256,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":508.0,"n_steps_budget":600.0,"object_pos_end":[0.41763,-0.02433,0.01602],"object_pos_start":[0.41763,-0.02433,0.01602],"object_to_goal_dist_end":0.32993,"object_to_goal_dist_start":0.32993,"object_z_max":0.01602,"peak_contact_force":201.4279,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":4661.0,"raw_peak_contact_force":422.70317,"subtask_id":"lift_clear","tcp_end":[0.37025,-0.02763,0.10803],"tcp_start":[0.37596,-0.01803,0.10952],"tcp_to_object_dist_end":0.10355,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":11.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.41405,-0.0204,0.01452],"object_pos_start":[0.41763,-0.02433,0.01602],"object_to_goal_dist_end":0.32996,"object_to_goal_dist_start":0.32993,"object_z_max":0.01602,"peak_contact_force":231.99898,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":10280.0,"raw_peak_contact_force":491.92623,"subtask_id":"place_goal","tcp_end":[0.34242,-0.02677,0.07245],"tcp_start":[0.37025,-0.02763,0.10803],"tcp_to_object_dist_end":0.09235,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.41414,-0.02113,0.01602],"object_pos_start":[0.41405,-0.0204,0.01452],"object_to_goal_dist_end":0.32996,"object_to_goal_dist_start":0.32996,"object_z_max":0.01726,"peak_contact_force":272997.0727,"phase_name":"descend_at_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":9299.0,"raw_peak_contact_force":776.61731,"subtask_id":"place_goal","tcp_end":[0.44922,0.00955,0.22279],"tcp_start":[0.34242,-0.02677,0.07245],"tcp_to_object_dist_end":0.21196,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.41414,-0.02113,0.01602],"object_pos_start":[0.41414,-0.02113,0.01602],"object_to_goal_dist_end":0.32996,"object_to_goal_dist_start":0.32996,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1087.0,"raw_peak_contact_force":125.18262,"tcp_end":[0.44785,0.00905,0.24939],"tcp_start":[0.44922,0.00955,0.22279],"tcp_to_object_dist_end":0.23772,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":5.87097,"average_solve_count":124.0,"average_success_count":124.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_z":0.1605,"approach_goal.goal_arc_height":0.10886,"approach_object.approach_speed":0.47692,"approach_object.approach_z":0.16401,"descend_at_goal.descend_goal_tolerance":0.02084,"descend_contact.contact_force":13.24384,"lift_object.lift_height":0.15146,"release_object.release_duration":1.27527},"optimized_scores":{"best_composite_score":-0.22116,"best_fitness_score":0.18599,"best_task_score":0.18096},"replay_outcomes":[{"contacts":{"omitted_contact_groups":11,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":828.0,"contact_point_centroid":[0.65917,0.0013,-0.00037],"force_p95":454.69201,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1330.20171,"mean_force":229.23166,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.43324,-0.00031,0.14493]},{"body_a":"world","body_b":"link7","contact_count":24.0,"contact_point_centroid":[0.54377,0.0034,-0.00317],"force_p95":222.66682,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1289.12638,"mean_force":65.2885,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.39367,3e-05,0.04517]},{"body_a":"world","body_b":"link6","contact_count":872.0,"contact_point_centroid":[0.65059,0.15161,-0.00031],"force_p95":538.46496,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":804.43704,"mean_force":374.22236,"phase_index":5.0,"phase_name":"descend_at_goal","phase_type":"descend","tcp_position_centroid":[0.65076,0.15569,0.29366]},{"body_a":"world","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.6863,0.02455,-0.0001],"force_p95":641.55839,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":641.55839,"mean_force":641.55839,"phase_index":1.0,"phase_name":"descend_contact","phase_type":"contact","tcp_position_centroid":[0.4655,-0.0224,0.15353]},{"body_a":"world","body_b":"link6","contact_count":457.0,"contact_point_centroid":[0.59188,-0.05458,-0.00019],"force_p95":329.81968,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":372.91578,"mean_force":270.36093,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.50407,-0.00337,0.24409]},{"body_a":"world","body_b":"link6","contact_count":548.0,"contact_point_centroid":[0.68753,0.02239,-0.00013],"force_p95":72.19825,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":173.36694,"mean_force":69.68578,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.46565,-0.02383,0.15214]},{"body_a":"world","body_b":"link6","contact_count":3.0,"contact_point_centroid":[0.57263,-0.05715,-0.0002],"force_p95":172.75921,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":173.34196,"mean_force":169.2997,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.52951,-0.03015,0.28783]},{"body_a":"link5","body_b":"hand","contact_count":196.0,"contact_point_centroid":[0.50384,-0.13154,0.24453],"force_p95":149.26209,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":156.37266,"mean_force":90.98132,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.52595,-0.02947,0.28701]},{"body_a":"world","body_b":"link6","contact_count":88.0,"contact_point_centroid":[0.67354,0.15585,-0.00011],"force_p95":77.47999,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":140.49162,"mean_force":54.31926,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.65731,0.15827,0.29381]},{"body_a":"grasp_target","body_b":"link7","contact_count":207.0,"contact_point_centroid":[0.52218,-0.00047,0.03262],"force_p95":3.57594,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":5.42275,"mean_force":0.72414,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.4067,0.00015,0.09253]},{"body_a":"grasp_target","body_b":"hand","contact_count":135.0,"contact_point_centroid":[0.5073,-0.0035,0.04626],"force_p95":2.11921,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.96877,"mean_force":0.89217,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.40331,0.00012,0.08054]},{"body_a":"world","body_b":"grasp_target","contact_count":3551.0,"contact_point_centroid":[0.51404,0.00085,-0.0024],"force_p95":0.36601,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.15082,"mean_force":0.16128,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.44542,-0.0004,0.15742]},{"body_a":"grasp_target","body_b":"link7","contact_count":45.0,"contact_point_centroid":[0.53163,-0.00715,0.03623],"force_p95":1.36605,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.7798,"mean_force":0.64611,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.40265,0.01771,0.1306]},{"body_a":"grasp_target","body_b":"link6","contact_count":39.0,"contact_point_centroid":[0.53506,-0.00416,0.03458],"force_p95":1.48619,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.75366,"mean_force":1.16015,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.40267,0.02803,0.13117]},{"body_a":"grasp_target","body_b":"link6","contact_count":107.0,"contact_point_centroid":[0.55369,0.00462,0.02053],"force_p95":0.60698,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.81463,"mean_force":0.30316,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.40066,0.00011,0.08159]},{"body_a":"world","body_b":"grasp_target","contact_count":1832.0,"contact_point_centroid":[0.50572,0.02904,-0.00219],"force_p95":0.3767,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.80125,"mean_force":0.14907,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.50598,-0.00567,0.2461]}],"total_contact_groups":27},"final_pose_error":0.10279,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.50503,0.03657,0.01602],"final_tcp_position":[0.65732,0.15871,0.29343],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":273004.12076,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":964.0,"n_steps_budget":1000.0,"object_pos_end":[0.50727,0.00065,0.01602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.27411,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":395.56882,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4852.0,"raw_peak_contact_force":1330.20171,"subtask_id":"reach_pregrasp","tcp_end":[0.4655,-0.0224,0.15353],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.14555,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1.0,"n_steps_budget":870.0,"object_pos_end":[0.50727,0.00065,0.01602],"object_pos_start":[0.50727,0.00065,0.01602],"object_to_goal_dist_end":0.27411,"object_to_goal_dist_start":0.27411,"object_z_max":0.01602,"peak_contact_force":641.55839,"phase_name":"descend_contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":5.0,"raw_peak_contact_force":641.55839,"subtask_id":"grasp_contact","tcp_end":[0.46558,-0.02249,0.15329],"tcp_start":[0.4655,-0.0224,0.15353],"tcp_to_object_dist_end":0.14532,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.50727,0.00065,0.01602],"object_pos_start":[0.50727,0.00065,0.01602],"object_to_goal_dist_end":0.27411,"object_to_goal_dist_start":0.27411,"object_z_max":0.01602,"peak_contact_force":273004.12071,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":3540.0,"raw_peak_contact_force":173.36694,"subtask_id":"grasp_contact","tcp_end":[0.46563,-0.02384,0.15203],"tcp_start":[0.46563,-0.02384,0.15203],"tcp_to_object_dist_end":0.14434,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":484.0,"n_steps_budget":600.0,"object_pos_end":[0.50503,0.03657,0.01602],"object_pos_start":[0.50727,0.00065,0.01602],"object_to_goal_dist_end":0.25642,"object_to_goal_dist_start":0.27411,"object_z_max":0.01854,"peak_contact_force":1366.84211,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":4695.0,"raw_peak_contact_force":372.91578,"subtask_id":"lift_clear","tcp_end":[0.5294,-0.03005,0.28754],"tcp_start":[0.46563,-0.02384,0.15203],"tcp_to_object_dist_end":0.28063,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":773.0,"n_steps_budget":1000.0,"object_pos_end":[0.50503,0.03657,0.01602],"object_pos_start":[0.50503,0.03657,0.01602],"object_to_goal_dist_end":0.25642,"object_to_goal_dist_start":0.25642,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":6476.0,"raw_peak_contact_force":173.34196,"subtask_id":"place_goal","tcp_end":[0.64185,0.14574,0.36585],"tcp_start":[0.5294,-0.03005,0.28754],"tcp_to_object_dist_end":0.39118,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50503,0.03657,0.01602],"object_pos_start":[0.50503,0.03657,0.01602],"object_to_goal_dist_end":0.25642,"object_to_goal_dist_start":0.25642,"object_z_max":0.01602,"peak_contact_force":321.54783,"phase_name":"descend_at_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":9184.0,"raw_peak_contact_force":804.43704,"subtask_id":"place_goal","tcp_end":[0.65732,0.15871,0.29343],"tcp_start":[0.64185,0.14574,0.36585],"tcp_to_object_dist_end":0.33922,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50503,0.03657,0.01602],"object_pos_start":[0.50503,0.03657,0.01602],"object_to_goal_dist_end":0.25642,"object_to_goal_dist_start":0.25642,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1116.0,"raw_peak_contact_force":140.49162,"tcp_end":[0.65755,0.15855,0.31867],"tcp_start":[0.65732,0.15871,0.29343],"tcp_to_object_dist_end":0.36019,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":5.51456,"average_solve_count":103.0,"average_success_count":103.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_z":0.10118,"approach_goal.goal_arc_height":0.12046,"approach_object.approach_speed":0.43397,"approach_object.approach_z":0.14723,"descend_at_goal.descend_goal_tolerance":0.01609,"descend_contact.contact_force":12.43301,"lift_object.lift_height":0.12988,"release_object.release_duration":1.8051},"optimized_scores":{"best_composite_score":-0.13393,"best_fitness_score":0.27322,"best_task_score":0.36594},"replay_outcomes":[{"contacts":{"omitted_contact_groups":11,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":859.0,"contact_point_centroid":[0.64948,0.0144,-0.00043],"force_p95":508.75,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1495.72131,"mean_force":247.76035,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.4287,0.01239,0.15485]},{"body_a":"world","body_b":"link6","contact_count":616.0,"contact_point_centroid":[0.60092,0.16049,-0.00028],"force_p95":609.14668,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":885.7218,"mean_force":420.6479,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.60363,0.16961,0.29359]},{"body_a":"link5","body_b":"hand","contact_count":165.0,"contact_point_centroid":[0.49529,-0.05219,0.24109],"force_p95":527.64061,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":763.81277,"mean_force":228.2668,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.52176,0.03783,0.27557]},{"body_a":"world","body_b":"link6","contact_count":995.0,"contact_point_centroid":[0.62026,0.17329,-0.00031],"force_p95":441.53146,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":587.25184,"mean_force":325.5981,"phase_index":5.0,"phase_name":"descend_at_goal","phase_type":"descend","tcp_position_centroid":[0.60992,0.17648,0.29365]},{"body_a":"world","body_b":"link7","contact_count":22.0,"contact_point_centroid":[0.53794,0.00964,-0.0037],"force_p95":0.0,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":388.7117,"mean_force":17.66871,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.38548,0.00475,0.04694]},{"body_a":"world","body_b":"link6","contact_count":414.0,"contact_point_centroid":[0.62443,0.00804,-0.00015],"force_p95":339.0677,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":385.5527,"mean_force":244.87306,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.47804,0.05356,0.22168]},{"body_a":"link5","body_b":"hand","contact_count":4.0,"contact_point_centroid":[0.49239,-0.06475,0.24039],"force_p95":213.11846,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":213.23566,"mean_force":193.61078,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.52969,0.01984,0.28617]},{"body_a":"world","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.68706,0.03163,-0.00011],"force_p95":134.26311,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":134.26311,"mean_force":134.26311,"phase_index":1.0,"phase_name":"descend_contact","phase_type":"contact","tcp_position_centroid":[0.46362,0.01067,0.16305]},{"body_a":"world","body_b":"link6","contact_count":542.0,"contact_point_centroid":[0.68778,0.0282,-0.00013],"force_p95":78.5655,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":133.00491,"mean_force":69.28886,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.46372,0.00764,0.16221]},{"body_a":"world","body_b":"link6","contact_count":86.0,"contact_point_centroid":[0.64124,0.17952,-0.00012],"force_p95":76.27468,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":132.71039,"mean_force":55.56391,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.61366,0.17823,0.29294]},{"body_a":"grasp_target","body_b":"link7","contact_count":154.0,"contact_point_centroid":[0.50669,0.01655,0.0346],"force_p95":4.06099,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":5.80057,"mean_force":0.8194,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.39735,0.00529,0.08894]},{"body_a":"grasp_target","body_b":"hand","contact_count":132.0,"contact_point_centroid":[0.49937,0.02893,0.04935],"force_p95":2.5016,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.53597,"mean_force":0.83157,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.39615,0.00519,0.08497]},{"body_a":"world","body_b":"grasp_target","contact_count":3661.0,"contact_point_centroid":[0.49913,0.04057,-0.00237],"force_p95":0.38254,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.51176,"mean_force":0.16531,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.4413,0.01227,0.16628]},{"body_a":"grasp_target","body_b":"link6","contact_count":816.0,"contact_point_centroid":[0.52672,0.09932,0.03106],"force_p95":0.50395,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.52744,"mean_force":0.29046,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.58373,0.13172,0.29976]},{"body_a":"world","body_b":"grasp_target","contact_count":3104.0,"contact_point_centroid":[0.49883,0.10171,-0.00329],"force_p95":0.6195,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.98516,"mean_force":0.22331,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.58759,0.13771,0.29811]},{"body_a":"grasp_target","body_b":"link6","contact_count":50.0,"contact_point_centroid":[0.54318,0.0315,0.01226],"force_p95":0.71128,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.86253,"mean_force":0.43784,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.38855,0.00492,0.06996]}],"total_contact_groups":27},"final_pose_error":0.18492,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.49717,0.12053,0.01602],"final_tcp_position":[0.61363,0.1787,0.29261],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":1495.72131,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49187,0.04256,0.01602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.19749,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":198.69788,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4878.0,"raw_peak_contact_force":1495.72131,"subtask_id":"reach_pregrasp","tcp_end":[0.46362,0.01067,0.16305],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.15308,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1.0,"n_steps_budget":900.0,"object_pos_end":[0.49187,0.04256,0.01602],"object_pos_start":[0.49187,0.04256,0.01602],"object_to_goal_dist_end":0.19749,"object_to_goal_dist_start":0.19749,"object_z_max":0.01602,"peak_contact_force":134.26311,"phase_name":"descend_contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":5.0,"raw_peak_contact_force":134.26311,"subtask_id":"grasp_contact","tcp_end":[0.46364,0.01039,0.16311],"tcp_start":[0.46362,0.01067,0.16305],"tcp_to_object_dist_end":0.15319,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.49187,0.04256,0.01602],"object_pos_start":[0.49187,0.04256,0.01602],"object_to_goal_dist_end":0.19749,"object_to_goal_dist_start":0.19749,"object_z_max":0.01602,"peak_contact_force":85.24977,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":3535.0,"raw_peak_contact_force":133.00491,"subtask_id":"grasp_contact","tcp_end":[0.46371,0.00764,0.16212],"tcp_start":[0.46371,0.00764,0.16213],"tcp_to_object_dist_end":0.15284,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":455.0,"n_steps_budget":600.0,"object_pos_end":[0.49187,0.04256,0.01602],"object_pos_start":[0.49187,0.04256,0.01602],"object_to_goal_dist_end":0.19749,"object_to_goal_dist_start":0.19749,"object_z_max":0.01602,"peak_contact_force":214.46168,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":4377.0,"raw_peak_contact_force":763.81277,"subtask_id":"lift_clear","tcp_end":[0.52961,0.01998,0.28563],"tcp_start":[0.46371,0.00764,0.16212],"tcp_to_object_dist_end":0.27317,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49832,0.12073,0.01602],"object_pos_start":[0.49187,0.04256,0.01602],"object_to_goal_dist_end":0.14992,"object_to_goal_dist_start":0.19749,"object_z_max":0.02036,"peak_contact_force":124.02884,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8911.0,"raw_peak_contact_force":885.7218,"subtask_id":"place_goal","tcp_end":[0.61067,0.1794,0.29358],"tcp_start":[0.52961,0.01998,0.28563],"tcp_to_object_dist_end":0.30513,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49717,0.12053,0.01602],"object_pos_start":[0.49832,0.12073,0.01602],"object_to_goal_dist_end":0.15079,"object_to_goal_dist_start":0.14992,"object_z_max":0.01603,"peak_contact_force":347.56926,"phase_name":"descend_at_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":9700.0,"raw_peak_contact_force":587.25184,"subtask_id":"place_goal","tcp_end":[0.61363,0.1787,0.29261],"tcp_start":[0.61067,0.1794,0.29358],"tcp_to_object_dist_end":0.3057,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.49717,0.12053,0.01602],"object_pos_start":[0.49717,0.12053,0.01602],"object_to_goal_dist_end":0.15079,"object_to_goal_dist_start":0.15079,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1109.0,"raw_peak_contact_force":132.71039,"tcp_end":[0.61388,0.17825,0.31858],"tcp_start":[0.61363,0.1787,0.29261],"tcp_to_object_dist_end":0.32939,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
```