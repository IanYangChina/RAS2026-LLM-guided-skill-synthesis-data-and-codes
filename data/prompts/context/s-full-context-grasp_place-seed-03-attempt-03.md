## Search State

- **Seed**: 3
- **Iteration**: 4 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 3 | approach → descend → grasp → lift → approach → descend → release → retract | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 9 | -0.4496 | 0.17 | ❌ rejected |
| 2 | approach → descend → grasp → lift → approach → descend → release → retract | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | position_control | force_threshold_switch | position_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 9 | -0.2003 | 0.21 | ✅ accepted |
| 1 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | admittance_control | position_control | position_control | position_control | admittance_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | contact_detected | time_limit | pose_tolerance | 7 | -0.3656 | 0.19 | ✅ accepted |
| 0 | rotate → retract → descend → pull → rotate | impedance_motion | arc_cartesian | linear_cartesian | arc_cartesian | arc_cartesian | position_control | position_control | admittance_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 3 | 0.0374 | 0.17 | ✅ accepted |

**Proposal policy**: task_score is 0.17 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.450) — your mutation base

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

- **Composite score**: -0.450
- **task_score** (E): 0.171
- **fitness_score**: 0.180  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.630

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.0943 |
| descend_to_object | 0.00 | 1.00 | 0.0971 |
| grasp_object | 1.00 | 1.00 | 0.0000 |
| lift_object | 1.00 | 1.00 | 0.1542 |
| approach_goal | 0.33 | 1.00 | 0.2179 |
| descend_at_goal | 0.00 | 1.00 | 0.0575 |
| release_object | 1.00 | 1.00 | 0.0244 |
| retract_after_place | 0.00 | 1.00 | 0.1593 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.503, 0.003, 0.215) | (0.511, 0.002, 0.030)→(0.511, 0.002, 0.026) | 0.244→0.246 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_to_object | descend | 0.00 / step_budget | (0.503, 0.003, 0.215)→(0.503, 0.023, 0.192) | (0.511, 0.002, 0.026)→(0.486, 0.019, 0.055) | 0.246→0.231 | 1.00 / 5.000 | 91228.905 | 1105.931 |
| grasp_object | grasp | 1.00 / step_budget | (0.503, 0.024, 0.192)→(0.503, 0.024, 0.192) | (0.486, 0.019, 0.055)→(0.487, 0.017, 0.052) | 0.231→0.234 | 1.00 / 9.000 | 56035.423 | 224.221 |
| lift_object | lift | 1.00 / step_budget | (0.503, 0.023, 0.337)→(0.506, 0.023, 0.491) | (0.488, 0.016, 0.051)→(0.543, -0.011, 0.016) | 0.234→0.274 | 1.00 / 8.667 | 94249.709 | 179.901 |
| approach_goal | approach | 0.33 / step_budget | (0.506, 0.023, 0.491)→(0.486, 0.127, 0.311) | (0.543, -0.011, 0.016)→(0.543, -0.011, 0.016) | 0.274→0.274 | 1.00 / 8.333 | 31.197 | 112.715 |
| descend_at_goal | descend | 0.00 / step_budget | (0.486, 0.127, 0.311)→(0.479, 0.134, 0.257) | (0.543, -0.011, 0.016)→(0.543, -0.011, 0.016) | 0.274→0.274 | 1.00 / 9.000 | 248.024 | 537.447 |
| release_object | release | 1.00 / step_budget | (0.479, 0.134, 0.257)→(0.478, 0.132, 0.282) | (0.543, -0.011, 0.016)→(0.543, -0.011, 0.016) | 0.274→0.274 | 1.00 / 5.333 | 51.427 | 205.113 |
| retract_after_place | retract | 0.00 / step_budget | (0.478, 0.132, 0.282)→(0.479, 0.133, 0.441) | (0.543, -0.011, 0.016)→(0.543, -0.011, 0.016) | 0.274→0.274 | 1.00 / 5.333 | 40.487 | 48.452 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 0.000
- place_accuracy: 0.000
- lift_clearance: 0.000
- transport_retention: 0.000
- terminal_score: 0.250
- phase_score: 0.353
- phase_breakdown.lift_clear_score: 0.006
- phase_breakdown.reach_pregrasp_score: 0.235
- phase_breakdown.grasp_contact_score: 1.000
- phase_breakdown.place_goal_score: 0.020
- grasp_place_fitness: 0.233

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.233
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.250
- **Median Q (composite search score)**: -0.474
- **K-run variance**: 0.0014
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Parameters at lower bound**: descend_to_object.descend_z
- **Final σ (mean)**: 0.298


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":5.50847,"average_solve_count":177.0,"average_success_count":177.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_z":0.13035,"approach_goal.arc_height":0.17813,"approach_object.approach_z":0.15428,"approach_object.arc_height":0.38688,"descend_at_goal.descend_goal_tolerance":0.00585,"descend_to_object.descend_z":0.07016,"lift_object.lift_height":0.19234,"release_object.release_duration":1.19699,"retract_after_place.retract_z":0.22664},"optimized_scores":{"best_composite_score":-0.4783,"best_fitness_score":0.1517,"best_task_score":0.10731},"replay_outcomes":[{"contacts":{"omitted_contact_groups":5,"reported_contact_groups":[{"body_a":"world","body_b":"link7","contact_count":37.0,"contact_point_centroid":[0.53931,-0.02773,-0.00415],"force_p95":1227.42712,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1414.6734,"mean_force":296.04458,"phase_index":1.0,"phase_name":"descend_to_object","phase_type":"descend","tcp_position_centroid":[0.41906,-0.02524,0.0167]},{"body_a":"world","body_b":"hand","contact_count":20.0,"contact_point_centroid":[0.4868,0.02925,-0.00275],"force_p95":97.11928,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1042.64003,"mean_force":54.49975,"phase_index":1.0,"phase_name":"descend_to_object","phase_type":"descend","tcp_position_centroid":[0.41948,-0.0251,0.00341]},{"body_a":"world","body_b":"link6","contact_count":906.0,"contact_point_centroid":[0.66784,-0.02545,-0.00031],"force_p95":210.52985,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":367.47846,"mean_force":192.18773,"phase_index":1.0,"phase_name":"descend_to_object","phase_type":"descend","tcp_position_centroid":[0.42784,-0.03209,0.09824]},{"body_a":"world","body_b":"link6","contact_count":550.0,"contact_point_centroid":[0.67503,-0.0324,-0.00013],"force_p95":88.65554,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":161.91046,"mean_force":71.53819,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.44755,-0.04126,0.15062]},{"body_a":"world","body_b":"link6","contact_count":35.0,"contact_point_centroid":[0.67171,-0.03283,-4e-05],"force_p95":101.77117,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":128.7942,"mean_force":38.76786,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.44688,-0.04131,0.1547]},{"body_a":"world","body_b":"right_finger","contact_count":236.0,"contact_point_centroid":[0.42307,0.0171,-0.00329],"force_p95":31.06871,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":37.42107,"mean_force":2.95705,"phase_index":1.0,"phase_name":"descend_to_object","phase_type":"descend","tcp_position_centroid":[0.42106,-0.02502,0.00043]},{"body_a":"world","body_b":"left_finger","contact_count":201.0,"contact_point_centroid":[0.42384,-0.06728,-0.00321],"force_p95":30.26448,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":36.81444,"mean_force":2.65896,"phase_index":1.0,"phase_name":"descend_to_object","phase_type":"descend","tcp_position_centroid":[0.42079,-0.02502,-1e-05]},{"body_a":"grasp_target","body_b":"hand","contact_count":56.0,"contact_point_centroid":[0.46495,-0.02621,0.02503],"force_p95":5.9511,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":6.41506,"mean_force":1.12002,"phase_index":1.0,"phase_name":"descend_to_object","phase_type":"descend","tcp_position_centroid":[0.42152,-0.02534,0.02224]},{"body_a":"world","body_b":"grasp_target","contact_count":3886.0,"contact_point_centroid":[0.41669,-0.02513,-0.00211],"force_p95":0.15015,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.53162,"mean_force":0.13587,"phase_index":1.0,"phase_name":"descend_to_object","phase_type":"descend","tcp_position_centroid":[0.43246,-0.0314,0.10177]},{"body_a":"world","body_b":"grasp_target","contact_count":1980.0,"contact_point_centroid":[0.45856,-0.02632,-0.00193],"force_p95":0.13308,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12287,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.47249,-0.00928,0.22795]},{"body_a":"world","body_b":"grasp_target","contact_count":2200.0,"contact_point_centroid":[0.41073,-0.02488,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.44755,-0.04126,0.15062]},{"body_a":"world","body_b":"grasp_target","contact_count":7608.0,"contact_point_centroid":[0.41073,-0.02488,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.44676,-0.04159,0.3104]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.41073,-0.02488,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.37098,-0.01083,0.41536]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.41073,-0.02488,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_at_goal","phase_type":"descend","tcp_position_centroid":[0.345,0.04257,0.33474]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.41073,-0.02488,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.35995,0.05787,0.30443]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.41073,-0.02488,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":7.0,"phase_name":"retract_after_place","phase_type":"retract","tcp_position_centroid":[0.35848,0.05765,0.40482]}],"total_contact_groups":21},"final_pose_error":0.06685,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.41073,-0.02488,0.01602],"final_tcp_position":[0.3596,0.05786,0.48533],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":273004.12069,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":346.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1980.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_pregrasp","tcp_end":[0.45612,-0.01974,0.18695],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16108,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.41073,-0.02488,0.01602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.3348,"object_to_goal_dist_start":0.30365,"object_z_max":0.0305,"peak_contact_force":193.16953,"phase_name":"descend_to_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5342.0,"raw_peak_contact_force":1414.6734,"subtask_id":"grasp_contact","tcp_end":[0.44737,-0.04141,0.15082],"tcp_start":[0.45612,-0.01974,0.18695],"tcp_to_object_dist_end":0.14067,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.41073,-0.02488,0.01602],"object_pos_start":[0.41073,-0.02488,0.01602],"object_to_goal_dist_end":0.3348,"object_to_goal_dist_start":0.3348,"object_z_max":0.01602,"peak_contact_force":67.29464,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":3505.0,"raw_peak_contact_force":161.91046,"subtask_id":"grasp_contact","tcp_end":[0.44759,-0.04131,0.1505],"tcp_start":[0.44759,-0.04131,0.1505],"tcp_to_object_dist_end":0.1404,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1902.0,"n_steps_budget":1000.0,"object_pos_end":[0.41073,-0.02488,0.01602],"object_pos_start":[0.41073,-0.02488,0.01602],"object_to_goal_dist_end":0.3348,"object_to_goal_dist_start":0.3348,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":15693.0,"raw_peak_contact_force":128.7942,"subtask_id":"lift_clear","tcp_end":[0.44912,-0.0419,0.49103],"tcp_start":[0.44687,-0.04143,0.31213],"tcp_to_object_dist_end":0.47687,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.41073,-0.02488,0.01602],"object_pos_start":[0.41073,-0.02488,0.01602],"object_to_goal_dist_end":0.3348,"object_to_goal_dist_start":0.3348,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8348.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_goal","tcp_end":[0.38737,0.03392,0.40917],"tcp_start":[0.44912,-0.0419,0.49103],"tcp_to_object_dist_end":0.39821,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.41073,-0.02488,0.01602],"object_pos_start":[0.41073,-0.02488,0.01602],"object_to_goal_dist_end":0.3348,"object_to_goal_dist_start":0.3348,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_at_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8283.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_goal","tcp_end":[0.36085,0.05803,0.29886],"tcp_start":[0.38737,0.03392,0.40917],"tcp_to_object_dist_end":0.29893,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.41073,-0.02488,0.01602],"object_pos_start":[0.41073,-0.02488,0.01602],"object_to_goal_dist_end":0.3348,"object_to_goal_dist_start":0.3348,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1022.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.35921,0.05775,0.32554],"tcp_start":[0.36085,0.05803,0.29886],"tcp_to_object_dist_end":0.32448,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.41073,-0.02488,0.01602],"object_pos_start":[0.41073,-0.02488,0.01602],"object_to_goal_dist_end":0.3348,"object_to_goal_dist_start":0.3348,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_after_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.3596,0.05786,0.48533],"tcp_start":[0.35921,0.05775,0.32554],"tcp_to_object_dist_end":0.47929,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":6.0,"average_failure_rate":0.02778,"average_mean_iterations":9.69444,"average_solve_count":216.0,"average_success_count":210.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_z":0.10005,"approach_goal.arc_height":0.2526,"approach_object.approach_z":0.17777,"approach_object.arc_height":0.27696,"descend_at_goal.descend_goal_tolerance":0.00586,"descend_to_object.descend_z":0.06684,"lift_object.lift_height":0.14822,"release_object.release_duration":1.50679,"retract_after_place.retract_z":0.28663},"optimized_scores":{"best_composite_score":-0.4735,"best_fitness_score":0.1565,"best_task_score":0.15445},"replay_outcomes":[{"contacts":{"omitted_contact_groups":17,"reported_contact_groups":[{"body_a":"world","body_b":"hand","contact_count":147.0,"contact_point_centroid":[0.61169,-0.03957,-0.00147],"force_p95":518.80625,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":934.10759,"mean_force":208.12282,"phase_index":1.0,"phase_name":"descend_to_object","phase_type":"descend","tcp_position_centroid":[0.56538,0.00894,-0.00577]},{"body_a":"world","body_b":"link7","contact_count":15.0,"contact_point_centroid":[0.6198,0.0161,-0.00173],"force_p95":885.40622,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":903.63414,"mean_force":269.82885,"phase_index":1.0,"phase_name":"descend_to_object","phase_type":"descend","tcp_position_centroid":[0.51634,-0.06069,0.03276]},{"body_a":"world","body_b":"link5","contact_count":594.0,"contact_point_centroid":[0.53478,0.05712,-0.00021],"force_p95":582.45772,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":736.46141,"mean_force":413.58046,"phase_index":1.0,"phase_name":"descend_to_object","phase_type":"descend","tcp_position_centroid":[0.58116,0.03245,0.28944]},{"body_a":"world","body_b":"link6","contact_count":987.0,"contact_point_centroid":[0.64797,0.16805,-0.0003],"force_p95":451.9247,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":648.60131,"mean_force":333.54509,"phase_index":5.0,"phase_name":"descend_at_goal","phase_type":"descend","tcp_position_centroid":[0.65302,0.16253,0.29367]},{"body_a":"world","body_b":"link6","contact_count":71.0,"contact_point_centroid":[0.66009,0.09482,-0.00064],"force_p95":512.58469,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":634.26448,"mean_force":283.44283,"phase_index":1.0,"phase_name":"descend_to_object","phase_type":"descend","tcp_position_centroid":[0.57164,-0.05264,0.18016]},{"body_a":"world","body_b":"link6","contact_count":88.0,"contact_point_centroid":[0.66259,0.18273,-0.00011],"force_p95":77.36782,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":138.90394,"mean_force":53.91308,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.65707,0.16189,0.29383]},{"body_a":"world","body_b":"link5","contact_count":550.0,"contact_point_centroid":[0.55828,0.04451,-0.00013],"force_p95":89.48917,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":122.41163,"mean_force":84.81968,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.59186,0.02997,0.29249]},{"body_a":"world","body_b":"link5","contact_count":8.0,"contact_point_centroid":[0.55839,0.0443,-0.0001],"force_p95":76.84709,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":93.82499,"mean_force":17.48822,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.59191,0.0299,0.29257]},{"body_a":"world","body_b":"right_finger","contact_count":1279.0,"contact_point_centroid":[0.57072,0.04928,-0.0079],"force_p95":12.98872,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":36.10496,"mean_force":7.80053,"phase_index":1.0,"phase_name":"descend_to_object","phase_type":"descend","tcp_position_centroid":[0.56856,0.00727,-0.00755]},{"body_a":"world","body_b":"left_finger","contact_count":1704.0,"contact_point_centroid":[0.56619,-0.03106,-0.0071],"force_p95":10.86658,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":35.12053,"mean_force":5.70989,"phase_index":1.0,"phase_name":"descend_to_object","phase_type":"descend","tcp_position_centroid":[0.56458,0.00954,-0.00478]},{"body_a":"world","body_b":"grasp_target","contact_count":991.0,"contact_point_centroid":[0.54301,0.0015,-0.0019],"force_p95":0.3994,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.83327,"mean_force":0.24975,"phase_index":1.0,"phase_name":"descend_to_object","phase_type":"descend","tcp_position_centroid":[0.57274,0.00512,0.04819]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1236.0,"contact_point_centroid":[0.53007,-0.04792,0.11016],"force_p95":1.34302,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.43846,"mean_force":0.58444,"phase_index":1.0,"phase_name":"descend_to_object","phase_type":"descend","tcp_position_centroid":[0.55755,-0.06966,0.1113]},{"body_a":"grasp_target","body_b":"link5","contact_count":541.0,"contact_point_centroid":[0.53284,0.06169,0.11163],"force_p95":0.77453,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.28102,"mean_force":0.48456,"phase_index":1.0,"phase_name":"descend_to_object","phase_type":"descend","tcp_position_centroid":[0.58113,0.03485,0.29052]},{"body_a":"world","body_b":"grasp_target","contact_count":4079.0,"contact_point_centroid":[0.73486,-0.04237,-0.00222],"force_p95":0.12627,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.87691,"mean_force":0.13618,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.59462,0.03073,0.47641]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":849.0,"contact_point_centroid":[0.5768,-0.03019,0.11399],"force_p95":0.33314,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.89861,"mean_force":0.10998,"phase_index":1.0,"phase_name":"descend_to_object","phase_type":"descend","tcp_position_centroid":[0.56408,0.00309,0.12161]},{"body_a":"grasp_target","body_b":"link5","contact_count":591.0,"contact_point_centroid":[0.58158,0.04019,0.13491],"force_p95":0.69791,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.8171,"mean_force":0.55891,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.59198,0.0299,0.33676]}],"total_contact_groups":33},"final_pose_error":0.12869,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.73503,-0.04244,0.01602],"final_tcp_position":[0.65954,0.16237,0.47665],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":273005.29022,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":337.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1944.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_pregrasp","tcp_end":[0.5325,0.00419,0.20612],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.18052,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":962.0,"n_steps_budget":1000.0,"object_pos_end":[0.56249,0.04751,0.13353],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.15096,"object_to_goal_dist_start":0.25012,"object_z_max":0.26182,"peak_contact_force":406.14841,"phase_name":"descend_to_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8269.0,"raw_peak_contact_force":934.10759,"subtask_id":"grasp_contact","tcp_end":[0.59134,0.02983,0.29213],"tcp_start":[0.5325,0.00419,0.20612],"tcp_to_object_dist_end":0.16217,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.56592,0.04064,0.12254],"object_pos_start":[0.56249,0.04751,0.13353],"object_to_goal_dist_end":0.15865,"object_to_goal_dist_start":0.15096,"object_z_max":0.13375,"peak_contact_force":167951.73011,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":2706.0,"raw_peak_contact_force":122.41163,"subtask_id":"grasp_contact","tcp_end":[0.59194,0.02989,0.2925],"tcp_start":[0.59194,0.02991,0.2925],"tcp_to_object_dist_end":0.17228,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1673.0,"n_steps_budget":930.0,"object_pos_end":[0.73503,-0.04244,0.01602],"object_pos_start":[0.5683,0.03754,0.12006],"object_to_goal_dist_end":0.28018,"object_to_goal_dist_start":0.16084,"object_z_max":0.17315,"peak_contact_force":9749.29862,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":12762.0,"raw_peak_contact_force":93.82499,"subtask_id":"lift_clear","tcp_end":[0.59596,0.0312,0.56107],"tcp_start":[0.59306,0.03025,0.42634],"tcp_to_object_dist_end":0.56731,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":999.0,"n_steps_budget":1000.0,"object_pos_end":[0.73503,-0.04244,0.01602],"object_pos_start":[0.73503,-0.04244,0.01602],"object_to_goal_dist_end":0.28019,"object_to_goal_dist_start":0.28019,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8346.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_goal","tcp_end":[0.65036,0.16548,0.29691],"tcp_start":[0.59596,0.0312,0.56107],"tcp_to_object_dist_end":0.35958,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.73503,-0.04244,0.01602],"object_pos_start":[0.73503,-0.04244,0.01602],"object_to_goal_dist_end":0.28019,"object_to_goal_dist_start":0.28019,"object_z_max":0.01602,"peak_contact_force":310.37563,"phase_name":"descend_at_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":9282.0,"raw_peak_contact_force":648.60131,"subtask_id":"place_goal","tcp_end":[0.65723,0.16172,0.29348],"tcp_start":[0.65036,0.16548,0.29691],"tcp_to_object_dist_end":0.35316,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.73503,-0.04244,0.01602],"object_pos_start":[0.73503,-0.04244,0.01602],"object_to_goal_dist_end":0.28019,"object_to_goal_dist_start":0.28019,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1112.0,"raw_peak_contact_force":138.90394,"tcp_end":[0.65739,0.16177,0.31869],"tcp_start":[0.65723,0.16172,0.29348],"tcp_to_object_dist_end":0.37328,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.73503,-0.04244,0.01602],"object_pos_start":[0.73503,-0.04244,0.01602],"object_to_goal_dist_end":0.28019,"object_to_goal_dist_start":0.28019,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_after_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.65954,0.16237,0.47665],"tcp_start":[0.65739,0.16177,0.31869],"tcp_to_object_dist_end":0.50973,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":5.85799,"average_solve_count":169.0,"average_success_count":169.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_z":0.10903,"approach_goal.arc_height":0.21956,"approach_object.approach_z":0.22369,"approach_object.arc_height":0.3152,"descend_at_goal.descend_goal_tolerance":0.00709,"descend_to_object.descend_z":0.04,"lift_object.lift_height":0.16777,"release_object.release_duration":1.25323,"retract_after_place.retract_z":0.21746},"optimized_scores":{"best_composite_score":-0.39708,"best_fitness_score":0.23292,"best_task_score":0.25036},"replay_outcomes":[{"contacts":{"omitted_contact_groups":16,"reported_contact_groups":[{"body_a":"world","body_b":"hand","contact_count":72.0,"contact_point_centroid":[0.54955,0.06931,-0.00093],"force_p95":234.09695,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":969.01086,"mean_force":117.11521,"phase_index":1.0,"phase_name":"descend_to_object","phase_type":"descend","tcp_position_centroid":[0.46913,0.07838,0.08025]},{"body_a":"world","body_b":"link7","contact_count":50.0,"contact_point_centroid":[0.57795,0.02255,-0.00218],"force_p95":896.89915,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":965.45902,"mean_force":384.45881,"phase_index":1.0,"phase_name":"descend_to_object","phase_type":"descend","tcp_position_centroid":[0.45853,0.04381,0.01453]},{"body_a":"world","body_b":"link6","contact_count":948.0,"contact_point_centroid":[0.57435,0.156,-0.0004],"force_p95":577.35563,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":963.61582,"mean_force":385.91196,"phase_index":5.0,"phase_name":"descend_at_goal","phase_type":"descend","tcp_position_centroid":[0.39456,0.19677,0.20697]},{"body_a":"world","body_b":"link6","contact_count":806.0,"contact_point_centroid":[0.69156,0.00983,-0.0002],"force_p95":266.1079,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":639.51871,"mean_force":218.12858,"phase_index":1.0,"phase_name":"descend_to_object","phase_type":"descend","tcp_position_centroid":[0.45935,0.08425,0.08593]},{"body_a":"link5","body_b":"hand","contact_count":1000.0,"contact_point_centroid":[0.47125,0.18769,0.23475],"force_p95":366.86543,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":535.32171,"mean_force":292.54342,"phase_index":5.0,"phase_name":"descend_at_goal","phase_type":"descend","tcp_position_centroid":[0.39538,0.19611,0.20712]},{"body_a":"link5","body_b":"hand","contact_count":200.0,"contact_point_centroid":[0.49108,0.20325,0.22051],"force_p95":270.42278,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":476.31326,"mean_force":195.59968,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.41826,0.18022,0.18433]},{"body_a":"link5","body_b":"hand","contact_count":550.0,"contact_point_centroid":[0.53199,0.04752,0.20084],"force_p95":139.46079,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":388.34143,"mean_force":96.42542,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.46923,0.08224,0.13192]},{"body_a":"link5","body_b":"hand","contact_count":1000.0,"contact_point_centroid":[0.48201,0.11407,0.32538],"force_p95":320.06034,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":337.89973,"mean_force":304.24914,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.40037,0.13452,0.29488]},{"body_a":"link5","body_b":"hand","contact_count":1865.0,"contact_point_centroid":[0.53137,0.06756,0.32852],"force_p95":308.35928,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":317.08499,"mean_force":262.24802,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46803,0.07983,0.26247]},{"body_a":"world","body_b":"link6","contact_count":72.0,"contact_point_centroid":[0.63111,0.18193,-0.0001],"force_p95":117.12772,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":297.83702,"mean_force":81.62511,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.41912,0.1814,0.17918]},{"body_a":"link5","body_b":"hand","contact_count":8.0,"contact_point_centroid":[0.53253,0.04743,0.20178],"force_p95":255.81457,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":257.6483,"mean_force":231.57606,"phase_index":1.0,"phase_name":"descend_to_object","phase_type":"descend","tcp_position_centroid":[0.46911,0.08186,0.13268]},{"body_a":"world","body_b":"link6","contact_count":550.0,"contact_point_centroid":[0.70374,0.03615,-0.00013],"force_p95":80.29893,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":228.20997,"mean_force":70.80896,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.46923,0.08224,0.13192]},{"body_a":"link5","body_b":"hand","contact_count":1000.0,"contact_point_centroid":[0.48753,0.19782,0.31902],"force_p95":129.86211,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":145.11086,"mean_force":121.75692,"phase_index":7.0,"phase_name":"retract_after_place","phase_type":"retract","tcp_position_centroid":[0.41584,0.177,0.2791]},{"body_a":"world","body_b":"link6","contact_count":170.0,"contact_point_centroid":[0.70167,0.03737,-2e-05],"force_p95":47.87663,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":88.62575,"mean_force":28.56648,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46835,0.0828,0.13445]},{"body_a":"world","body_b":"left_finger","contact_count":367.0,"contact_point_centroid":[0.46288,-0.00083,-0.00365],"force_p95":29.57159,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":39.99365,"mean_force":3.14613,"phase_index":1.0,"phase_name":"descend_to_object","phase_type":"descend","tcp_position_centroid":[0.46634,0.0408,-0.00095]},{"body_a":"world","body_b":"right_finger","contact_count":329.0,"contact_point_centroid":[0.47454,0.08199,-0.00346],"force_p95":29.09499,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":39.58252,"mean_force":2.51159,"phase_index":1.0,"phase_name":"descend_to_object","phase_type":"descend","tcp_position_centroid":[0.46592,0.04081,-0.00138]}],"total_contact_groups":32},"final_pose_error":0.0572,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.4841,0.03407,0.01602],"final_tcp_position":[0.41667,0.17742,0.36072],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":273087.39557,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":226.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1500.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_pregrasp","tcp_end":[0.5198,0.02561,0.25148],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.22578,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":6.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.4841,0.03407,0.01602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.20773,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":273087.39557,"phase_name":"descend_to_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5772.0,"raw_peak_contact_force":969.01086,"subtask_id":"grasp_contact","tcp_end":[0.46926,0.08186,0.13263],"tcp_start":[0.5198,0.02561,0.25148],"tcp_to_object_dist_end":0.12689,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.4841,0.03407,0.01602],"object_pos_start":[0.4841,0.03407,0.01602],"object_to_goal_dist_end":0.20773,"object_to_goal_dist_start":0.20773,"object_z_max":0.01602,"peak_contact_force":87.24488,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":4080.0,"raw_peak_contact_force":388.34143,"subtask_id":"grasp_contact","tcp_end":[0.46923,0.08228,0.13176],"tcp_start":[0.46923,0.08228,0.13176],"tcp_to_object_dist_end":0.12626,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":1865.0,"n_steps_budget":1000.0,"object_pos_end":[0.4841,0.03407,0.01602],"object_pos_start":[0.4841,0.03407,0.01602],"object_to_goal_dist_end":0.20773,"object_to_goal_dist_start":0.20773,"object_z_max":0.01602,"peak_contact_force":272999.70432,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":17524.0,"raw_peak_contact_force":317.08499,"subtask_id":"lift_clear","tcp_end":[0.47171,0.07965,0.4218],"tcp_start":[0.46817,0.07984,0.27293],"tcp_to_object_dist_end":0.40852,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.4841,0.03407,0.01602],"object_pos_start":[0.4841,0.03407,0.01602],"object_to_goal_dist_end":0.20773,"object_to_goal_dist_start":0.20773,"object_z_max":0.01602,"peak_contact_force":93.34656,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":9183.0,"raw_peak_contact_force":337.89973,"subtask_id":"place_goal","tcp_end":[0.41989,0.18063,0.22767],"tcp_start":[0.47171,0.07965,0.4218],"tcp_to_object_dist_end":0.26533,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.4841,0.03407,0.01602],"object_pos_start":[0.4841,0.03407,0.01602],"object_to_goal_dist_end":0.20773,"object_to_goal_dist_start":0.20773,"object_z_max":0.01602,"peak_contact_force":433.57364,"phase_name":"descend_at_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":10152.0,"raw_peak_contact_force":963.61582,"subtask_id":"place_goal","tcp_end":[0.41919,0.18178,0.17982],"tcp_start":[0.41989,0.18063,0.22767],"tcp_to_object_dist_end":0.22992,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.4841,0.03407,0.01602],"object_pos_start":[0.4841,0.03407,0.01602],"object_to_goal_dist_end":0.20773,"object_to_goal_dist_start":0.20773,"object_z_max":0.01602,"peak_contact_force":154.03524,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1496.0,"raw_peak_contact_force":476.31326,"tcp_end":[0.4168,0.17763,0.20046],"tcp_start":[0.41919,0.18178,0.17982],"tcp_to_object_dist_end":0.24323,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.4841,0.03407,0.01602],"object_pos_start":[0.4841,0.03407,0.01602],"object_to_goal_dist_end":0.20773,"object_to_goal_dist_start":0.20773,"object_z_max":0.01602,"peak_contact_force":121.21501,"phase_name":"retract_after_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":8000.0,"raw_peak_contact_force":145.11086,"tcp_end":[0.41667,0.17742,0.36072],"tcp_start":[0.4168,0.17763,0.20046],"tcp_to_object_dist_end":0.37936,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```