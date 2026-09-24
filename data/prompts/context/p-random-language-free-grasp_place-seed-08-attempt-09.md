## Search State

- **Seed**: 8
- **Iteration**: 10 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 9 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 6 | 0.0598 | 0.15 | ❌ rejected |
| 8 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 6 | 0.0637 | 0.16 | ❌ rejected |
| 7 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | impedance_control | impedance_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 8 | -0.0433 | 0.15 | ❌ rejected |
| 6 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | impedance_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 7 | 0.0039 | 0.14 | ❌ rejected |
| 5 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 7 | 0.0009 | 0.13 | ❌ rejected |

**Proposal policy**: task_score is 0.15 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `f44a4a1356de6cb8b5dec75995af4354e38cafd01c85526c1c2a33c8dd2e5b1c`
- Frozen object start: [0.48269722766055606, 0.048727684333792556, 0.03]
- Frozen task target: [0.5818710838485517, 0.2288548935820029, 0.2304844767544324]
- Goal object position: (0.5818710838485517, 0.2288548935820029, 0.2304844767544324)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.5818710838485517, 0.2288548935820029, 0.2304844767544324)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.48269722766055606, 0.048727684333792556, 0.03)
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
  frozen_object_start: [0.4827, 0.0487, 0.03]
  frozen_task_target: [0.5819, 0.2289, 0.2305]
  frozen_object_starts: {'grasp_target': [0.48269722766055606, 0.048727684333792556, 0.03]}
  frozen_targets: {'place_target': [0.5818710838485517, 0.2288548935820029, 0.2304844767544324]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: f44a4a1356de6cb8b5dec75995af4354e38cafd01c85526c1c2a33c8dd2e5b1c

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
| `object` | offset from object initial position (0.48269722766055606, 0.048727684333792556, 0.03) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5818710838485517, 0.2288548935820029, 0.2304844767544324) | final destination targets |
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

## Current Skill (Q=0.060) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: reach_object
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.1
  weight: 0.2
- id: grasp_success
  anchor: object
  metric: contact
  weight: 0.2
- id: lift_clearance
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.2
  weight: 0.2
- id: place_accuracy
  target_entity: object
  weight: 0.4
phases:
- id: approach_object
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  end_effector_action: open
  target:
    source: yaml
    anchor: task_object
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.15
    offset_along_axis:
      distance: 0.0
      axis: world_z
      mode: add_to_offset
      sign: positive
    tolerance: 0.01
    orientation:
      mode: keep_current
      tolerance: 0.05
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.05
      - 0.5
      default: 0.2
      binds_to:
      - path: generator.speed
        mode: replace
  retries:
    max_attempts: 1
    strategy: repeat
    offset:
    - 0.0
    - 0.0
    - 0.0
  subtask_id: reach_object
- id: descend_grasp
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
    - 0.03
    tolerance: 0.01
    orientation:
      mode: keep_current
      tolerance: 0.05
  parameters:
    descent_height:
      type: scalar
      range:
      - 0.02
      - 0.08
      default: 0.04
      binds_to:
      - path: target.offset.z
        mode: replace
  retries:
    max_attempts: 1
    strategy: repeat
    offset:
    - 0.0
    - 0.0
    - 0.0
  subtask_id: reach_object
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
    threshold: 0.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: repeat
    offset:
    - 0.0
    - 0.0
    - 0.0
  subtask_id: grasp_success
- id: lift_object
  type: lift
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.2
      axis: world_z
      mode: add_to_offset
      sign: positive
    tolerance: 0.01
    orientation:
      mode: keep_current
      tolerance: 0.05
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.1
      - 0.3
      default: 0.2
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
  guards:
  - id: check_lift
    when: after_phase
    predicate: object_lifted
    threshold: 0.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: repeat
    offset:
    - 0.0
    - 0.0
    - 0.02
  subtask_id: lift_clearance
- id: transport_goal
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.15
    tolerance: 0.01
    orientation:
      mode: keep_current
      tolerance: 0.05
  parameters:
    transport_speed:
      type: scalar
      range:
      - 0.05
      - 0.5
      default: 0.2
      binds_to:
      - path: generator.speed
        mode: replace
  retries:
    max_attempts: 1
    strategy: repeat
    offset:
    - 0.0
    - 0.0
    - 0.0
  subtask_id: place_accuracy
- id: descend_place
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.03
    tolerance: 0.01
    orientation:
      mode: keep_current
      tolerance: 0.05
  parameters:
    place_height:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.03
      binds_to:
      - path: target.offset.z
        mode: replace
  retries:
    max_attempts: 1
    strategy: repeat
    offset:
    - 0.0
    - 0.0
    - 0.0
  subtask_id: place_accuracy
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
  retries:
    max_attempts: 1
    strategy: repeat
    offset:
    - 0.0
    - 0.0
    - 0.0
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
    - 0.1
    tolerance: 0.01
    orientation:
      mode: keep_current
      tolerance: 0.05
  parameters:
    retract_height:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: replace
  retries:
    max_attempts: 1
    strategy: repeat
    offset:
    - 0.0
    - 0.0
    - 0.0

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_object** (`approach`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.15], offset_along_axis={axis=world_z, distance=0.0, mode=add_to_offset, sign=positive}, tolerance=0.01
  - orientation: mode=keep_current, tolerance=0.05
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=1, strategy=repeat, offset=[0.0, 0.0, 0.0]
- **descend_grasp** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.03], tolerance=0.01
  - orientation: mode=keep_current, tolerance=0.05
  - parameter_bindings:
    - descent_height: status=consumed; consumers=target.offset.z (replace)
  - retries: max_attempts=1, strategy=repeat, offset=[0.0, 0.0, 0.0]
- **grasp_object** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
  - guards:
    - id=check_grasp, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=0.0
  - retries: max_attempts=2, strategy=repeat, offset=[0.0, 0.0, 0.0]
- **lift_object** (`lift`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.2, mode=add_to_offset, sign=positive}, tolerance=0.01
  - orientation: mode=keep_current, tolerance=0.05
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset_along_axis.distance (replace)
  - guards:
    - id=check_lift, when=after_phase, predicate=object_lifted, on_failure=retry, threshold=0.0
  - retries: max_attempts=2, strategy=repeat, offset=[0.0, 0.0, 0.02]
- **transport_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.15], tolerance=0.01
  - orientation: mode=keep_current, tolerance=0.05
  - parameter_bindings:
    - transport_speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=1, strategy=repeat, offset=[0.0, 0.0, 0.0]
- **descend_place** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.03], tolerance=0.01
  - orientation: mode=keep_current, tolerance=0.05
  - parameter_bindings:
    - place_height: status=consumed; consumers=target.offset.z (replace)
  - retries: max_attempts=1, strategy=repeat, offset=[0.0, 0.0, 0.0]
- **release_object** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
  - retries: max_attempts=1, strategy=repeat, offset=[0.0, 0.0, 0.0]
- **retract_after_place** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.1], tolerance=0.01
  - orientation: mode=keep_current, tolerance=0.05
  - parameter_bindings:
    - retract_height: status=consumed; consumers=target.offset.z (replace)
  - retries: max_attempts=1, strategy=repeat, offset=[0.0, 0.0, 0.0]

## Design Metrics

- **Composite score**: 0.060
- **task_score** (E): 0.152
- **fitness_score**: 0.540  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.480

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1270 |
| descend_grasp | 1.00 | 1.00 | 0.1268 |
| grasp_object | 1.00 | 1.00 | 0.0125 |
| lift_object | 0.00 | 0.67 | 0.1614 |
| transport_goal | 0.00 | 0.67 | 0.0001 |
| descend_place | 0.00 | 1.00 | 0.1236 |
| release_object | 1.00 | 1.00 | 0.0228 |
| retract_after_place | 1.00 | 1.00 | 0.1028 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.513, -0.001, 0.181) | (0.522, -0.001, 0.030)→(0.522, -0.001, 0.026) | 0.287→0.289 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_grasp | descend | 1.00 / step_budget | (0.513, -0.001, 0.181)→(0.516, -0.001, 0.054) | (0.522, -0.001, 0.026)→(0.522, -0.001, 0.026) | 0.289→0.289 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_object | grasp | 1.00 / step_budget | (0.516, -0.001, 0.054)→(0.508, -0.001, 0.045) | (0.522, -0.001, 0.026)→(0.522, -0.001, 0.026) | 0.289→0.289 | 1.00 / 42.667 | 0.144 | 0.191 |
| lift_object | lift | 0.00 / step_budget | (0.508, -0.001, 0.045)→(0.505, -0.001, 0.206) | (0.522, -0.001, 0.026)→(0.514, -0.002, 0.174) | 0.289→0.234 | 0.67 / 7.333 | 0.116 | 0.441 |
| transport_goal | approach | 0.00 / guard_failure | (0.507, 0.010, 0.209)→(0.507, 0.010, 0.209) | (0.514, -0.002, 0.174)→(0.522, 0.007, 0.030) | 0.234→0.281 | 0.67 / 1.333 | 2584.068 | 1.316 |
| descend_place | descend | 0.00 / step_budget | (0.507, 0.010, 0.209)→(0.561, 0.120, 0.217) | (0.522, 0.007, 0.023)→(0.522, 0.012, 0.016) | 0.285→0.286 | 1.00 / 8.333 | 94251.408 | 1.642 |
| release_object | release | 1.00 / step_budget | (0.561, 0.120, 0.217)→(0.556, 0.119, 0.239) | (0.522, 0.012, 0.016)→(0.522, 0.012, 0.016) | 0.286→0.286 | 1.00 / 4.000 | 0.123 | 0.123 |
| retract_after_place | retract | 1.00 / step_budget | (0.556, 0.119, 0.239)→(0.554, 0.118, 0.342) | (0.522, 0.012, 0.016)→(0.522, 0.012, 0.016) | 0.286→0.286 | 1.00 / 4.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.203
- phase_score: 0.420
- phase_breakdown.grasp_success_score: 1.000
- phase_breakdown.reach_object_score: 0.218
- phase_breakdown.lift_clearance_score: 0.540
- phase_breakdown.place_accuracy_score: 0.172
- grasp_place_fitness: 0.566

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.566
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.203
- **Median Q (composite search score)**: 0.048
- **K-run variance**: 0.0004
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.362


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `2cbd02033d1f1347f2ac2d0b012406a96501e6b48f5b172bd88b34d6c745630c`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `5745d7c2d025a63f908a4bf0f58182445bb06541d436718f39304ac5569d60c0`; realized-scene SHA-256: `f44a4a1356de6cb8b5dec75995af4354e38cafd01c85526c1c2a33c8dd2e5b1c`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.4827,0.04873,0.03]},{"name":"goal","value":[0.58187,0.22885,0.23048]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.4827,0.04873,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.58187,0.22885,0.23048]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.81379,"average_solve_count":145.0,"average_success_count":145.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.21328,"descend_grasp.descent_height":0.02004,"descend_place.place_height":0.04194,"lift_object.lift_height":0.29584,"retract_after_place.retract_height":0.1061,"transport_goal.transport_speed":0.06956},"optimized_scores":{"best_composite_score":0.04831,"best_fitness_score":0.52831,"best_task_score":0.13219},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1.0,"contact_point_centroid":[0.45673,0.01847,-0.00057],"force_p95":1.79074,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.79074,"mean_force":1.79074,"phase_index":4.0,"phase_name":"transport_goal","phase_type":"approach","tcp_position_centroid":[0.46936,0.05442,0.21249]},{"body_a":"world","body_b":"grasp_target","contact_count":3992.0,"contact_point_centroid":[0.48372,0.03781,-0.00226],"force_p95":0.12425,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.7187,"mean_force":0.13354,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.5011,0.10776,0.22538]},{"body_a":"world","body_b":"grasp_target","contact_count":137.0,"contact_point_centroid":[0.48014,0.04602,-0.00121],"force_p95":0.2749,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.42126,"mean_force":0.0616,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46876,0.04681,0.04863]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":14650.0,"contact_point_centroid":[0.46974,0.06544,0.11416],"force_p95":0.10796,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.40103,"mean_force":0.06822,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46644,0.0466,0.11375]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13978.0,"contact_point_centroid":[0.46958,0.02779,0.11707],"force_p95":0.10845,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27043,"mean_force":0.06988,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46643,0.0466,0.11693]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48275,0.04862,-0.00214],"force_p95":0.16224,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22183,"mean_force":0.13313,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.47134,0.04707,0.04783]},{"body_a":"world","body_b":"grasp_target","contact_count":2024.0,"contact_point_centroid":[0.4827,0.04873,-0.00193],"force_p95":0.13256,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12287,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.48665,0.02732,0.22652]},{"body_a":"world","body_b":"grasp_target","contact_count":1652.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.47664,0.04508,0.11869]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.48373,0.0378,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.52754,0.15255,0.24273]},{"body_a":"world","body_b":"grasp_target","contact_count":2412.0,"contact_point_centroid":[0.48373,0.0378,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":7.0,"phase_name":"retract_after_place","phase_type":"retract","tcp_position_centroid":[0.52431,0.15149,0.3081]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4816.0,"contact_point_centroid":[0.46956,0.02772,0.04879],"force_p95":0.0713,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11379,"mean_force":0.04505,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.47024,0.04697,0.04669]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5502.0,"contact_point_centroid":[0.46985,0.06624,0.04865],"force_p95":0.07042,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07211,"mean_force":0.04071,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.47025,0.04697,0.04669]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4060.0,"contact_point_centroid":[0.5033,0.1107,0.22848],"force_p95":0.01102,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01616,"mean_force":0.01046,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.5029,0.11068,0.22619]},{"body_a":"left_finger","body_b":"right_finger","contact_count":220.0,"contact_point_centroid":[0.53021,0.15326,0.23974],"force_p95":0.01096,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01272,"mean_force":0.01013,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.52959,0.15324,0.23779]}],"total_contact_groups":14},"final_pose_error":0.01324,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.48373,0.0378,0.01602],"final_tcp_position":[0.52468,0.15155,0.35613],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":3326.05354,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":357.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2024.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.47773,0.04278,0.18305],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.15722,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":413.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1652.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.47795,0.04771,0.05477],"tcp_start":[0.47773,0.04278,0.18305],"tcp_to_object_dist_end":0.02916,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":46.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48268,0.04755,0.02548],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.2911,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.15865,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12118.0,"raw_peak_contact_force":0.22183,"subtask_id":"grasp_success","tcp_end":[0.47021,0.04696,0.04666],"tcp_start":[0.47795,0.04771,0.05477],"tcp_to_object_dist_end":0.02458,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47636,0.04338,0.16923],"object_pos_start":[0.48268,0.04755,0.02548],"object_to_goal_dist_end":0.222,"object_to_goal_dist_start":0.2911,"object_z_max":0.17334,"peak_contact_force":0.0,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":28765.0,"raw_peak_contact_force":0.42126,"subtask_id":"lift_clearance","tcp_end":[0.46677,0.04663,0.20879],"tcp_start":[0.47021,0.04696,0.04666],"tcp_to_object_dist_end":0.04083,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":75.0,"n_steps_budget":1000.0,"object_pos_end":[0.48365,0.03359,0.02952],"object_pos_start":[0.47636,0.04338,0.16923],"object_to_goal_dist_end":0.29691,"object_to_goal_dist_start":0.222,"object_z_max":0.16923,"peak_contact_force":3326.05354,"phase_name":"transport_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1.0,"raw_peak_contact_force":1.79074,"subtask_id":"place_accuracy","tcp_end":[0.46934,0.05447,0.21248],"tcp_start":[0.46936,0.05442,0.21249],"tcp_to_object_dist_end":0.18469,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.48373,0.0378,0.01602],"object_pos_start":[0.48392,0.03339,0.02286],"object_to_goal_dist_end":0.30352,"object_to_goal_dist_start":0.30151,"object_z_max":0.02286,"peak_contact_force":0.12263,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8052.0,"raw_peak_contact_force":1.7187,"subtask_id":"place_accuracy","tcp_end":[0.53069,0.15344,0.24012],"tcp_start":[0.46934,0.05447,0.21248],"tcp_to_object_dist_end":0.25651,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48373,0.0378,0.01602],"object_pos_start":[0.48373,0.0378,0.01602],"object_to_goal_dist_end":0.30352,"object_to_goal_dist_start":0.30352,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1020.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.52639,0.15215,0.26315],"tcp_start":[0.53069,0.15344,0.24012],"tcp_to_object_dist_end":0.27562,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":603.0,"n_steps_budget":690.0,"object_pos_end":[0.48373,0.0378,0.01602],"object_pos_start":[0.48373,0.0378,0.01602],"object_to_goal_dist_end":0.30352,"object_to_goal_dist_start":0.30352,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_after_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2412.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.52468,0.15155,0.35613],"tcp_start":[0.52639,0.15215,0.26315],"tcp_to_object_dist_end":0.36096,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `2b35d39beba75b46a5edd8e67b975c00ef2c88fb75a3753bdd32db5918adf9e2`; realized-scene SHA-256: `0143f6b0f71a2b9dc1b332d50c0ca91b210f169a33e3f94f972cb0659a69dba8`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.53702,-0.02132,0.03]},{"name":"goal","value":[0.61031,0.22775,0.20741]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.53702,-0.02132,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.61031,0.22775,0.20741]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.83784,"average_solve_count":148.0,"average_success_count":148.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.37191,"descend_grasp.descent_height":0.02004,"descend_place.place_height":0.02373,"lift_object.lift_height":0.26057,"retract_after_place.retract_height":0.1238,"transport_goal.transport_speed":0.10349},"optimized_scores":{"best_composite_score":0.04485,"best_fitness_score":0.52485,"best_task_score":0.12086},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1.0,"contact_point_centroid":[0.56654,-0.02386,-0.00145],"force_p95":1.88412,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.88412,"mean_force":1.88412,"phase_index":4.0,"phase_name":"transport_goal","phase_type":"approach","tcp_position_centroid":[0.52092,-0.0079,0.20745]},{"body_a":"world","body_b":"grasp_target","contact_count":3990.0,"contact_point_centroid":[0.53667,-0.01393,-0.00226],"force_p95":0.12416,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.69175,"mean_force":0.13365,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.54266,0.05785,0.20777]},{"body_a":"world","body_b":"grasp_target","contact_count":143.0,"contact_point_centroid":[0.53437,-0.02055,-0.00113],"force_p95":0.31546,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.46385,"mean_force":0.06948,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.52126,-0.0208,0.04578]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":14165.0,"contact_point_centroid":[0.52294,-0.00186,0.11617],"force_p95":0.11185,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33475,"mean_force":0.07043,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.51877,-0.02074,0.11395]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":15266.0,"contact_point_centroid":[0.52301,-0.03952,0.11707],"force_p95":0.10031,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28543,"mean_force":0.06625,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.51877,-0.02074,0.11549]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":118.0,"contact_point_centroid":[0.52542,-0.03541,0.20004],"force_p95":0.18039,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26793,"mean_force":0.06965,"phase_index":4.0,"phase_name":"transport_goal","phase_type":"approach","tcp_position_centroid":[0.51933,-0.01956,0.20506]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":33.0,"contact_point_centroid":[0.52598,-0.00281,0.1982],"force_p95":0.18137,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20078,"mean_force":0.12429,"phase_index":4.0,"phase_name":"transport_goal","phase_type":"approach","tcp_position_centroid":[0.51926,-0.02055,0.20491]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53703,-0.0212,-0.00205],"force_p95":0.13631,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.16855,"mean_force":0.12648,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.52409,-0.02086,0.04548]},{"body_a":"world","body_b":"grasp_target","contact_count":2124.0,"contact_point_centroid":[0.53702,-0.02132,-0.00193],"force_p95":0.13221,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12286,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51739,-0.01207,0.22551]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4111.0,"contact_point_centroid":[0.52379,-0.00163,0.04679],"force_p95":0.07716,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12853,"mean_force":0.05182,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.52289,-0.02083,0.04408]},{"body_a":"world","body_b":"grasp_target","contact_count":1568.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.52733,-0.01993,0.11677]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.53667,-0.01394,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.56025,0.11288,0.21458]},{"body_a":"world","body_b":"grasp_target","contact_count":2772.0,"contact_point_centroid":[0.53667,-0.01394,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_after_place","phase_type":"retract","tcp_position_centroid":[0.55658,0.112,0.28798]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4897.0,"contact_point_centroid":[0.52378,-0.03991,0.04586],"force_p95":0.06923,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08688,"mean_force":0.04466,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.52289,-0.02083,0.04408]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4021.0,"contact_point_centroid":[0.54429,0.06154,0.21029],"force_p95":0.01103,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01512,"mean_force":0.01051,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.54395,0.06154,0.20792]},{"body_a":"left_finger","body_b":"right_finger","contact_count":224.0,"contact_point_centroid":[0.563,0.1135,0.21229],"force_p95":0.01095,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01096,"mean_force":0.00999,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.56262,0.1135,0.21]}],"total_contact_groups":16},"final_pose_error":0.01392,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.53667,-0.01394,0.01602],"final_tcp_position":[0.55708,0.11206,0.34475],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":273005.25111,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":382.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2124.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.52601,-0.019,0.18034],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.15473,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":392.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1568.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.53126,-0.02099,0.05396],"tcp_start":[0.52601,-0.019,0.18034],"tcp_to_object_dist_end":0.02854,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53694,-0.0208,0.02582],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31645,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.13392,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10808.0,"raw_peak_contact_force":0.16855,"subtask_id":"grasp_success","tcp_end":[0.52286,-0.02083,0.04404],"tcp_start":[0.53126,-0.02099,0.05396],"tcp_to_object_dist_end":0.02303,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52843,-0.02055,0.17538],"object_pos_start":[0.53694,-0.0208,0.02582],"object_to_goal_dist_end":0.26341,"object_to_goal_dist_start":0.31645,"object_z_max":0.17531,"peak_contact_force":0.18692,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":29574.0,"raw_peak_contact_force":0.46385,"subtask_id":"lift_clearance","tcp_end":[0.51922,-0.02075,0.20469],"tcp_start":[0.52286,-0.02083,0.04404],"tcp_to_object_dist_end":0.03073,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":93.0,"n_steps_budget":1000.0,"object_pos_end":[0.53785,-0.02052,0.02999],"object_pos_start":[0.52843,-0.02055,0.17538],"object_to_goal_dist_end":0.31363,"object_to_goal_dist_start":0.26341,"object_z_max":0.17538,"peak_contact_force":4426.15063,"phase_name":"transport_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":152.0,"raw_peak_contact_force":1.88412,"subtask_id":"place_accuracy","tcp_end":[0.5209,-0.00782,0.20743],"tcp_start":[0.52092,-0.0079,0.20745],"tcp_to_object_dist_end":0.1787,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53667,-0.01394,0.01602],"object_pos_start":[0.53801,-0.02045,0.02333],"object_to_goal_dist_end":0.31697,"object_to_goal_dist_start":0.31736,"object_z_max":0.02333,"peak_contact_force":273005.25111,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8011.0,"raw_peak_contact_force":1.69175,"subtask_id":"place_accuracy","tcp_end":[0.56383,0.11346,0.21252],"tcp_start":[0.5209,-0.00782,0.20743],"tcp_to_object_dist_end":0.23575,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53667,-0.01394,0.01602],"object_pos_start":[0.53667,-0.01394,0.01602],"object_to_goal_dist_end":0.31697,"object_to_goal_dist_start":0.31697,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1024.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.5589,0.11254,0.23474],"tcp_start":[0.56383,0.11346,0.21252],"tcp_to_object_dist_end":0.25363,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":693.0,"n_steps_budget":780.0,"object_pos_end":[0.53667,-0.01394,0.01602],"object_pos_start":[0.53667,-0.01394,0.01602],"object_to_goal_dist_end":0.31697,"object_to_goal_dist_start":0.31697,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_after_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2772.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.55708,0.11206,0.34475],"tcp_start":[0.5589,0.11254,0.23474],"tcp_to_object_dist_end":0.35264,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `530652a2467d9ac78fab654e7ed7fc5283ca1649270bc8f158e04c16074f9f95`; realized-scene SHA-256: `9bdc6de22965641ffcaccb8421100561fe91fb98e16735236cc25272572d8879`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5456,-0.02923,0.03]},{"name":"goal","value":[0.63284,0.16493,0.17692]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.5456,-0.02923,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.63284,0.16493,0.17692]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.79592,"average_solve_count":147.0,"average_success_count":147.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.42692,"descend_grasp.descent_height":0.02007,"descend_place.place_height":0.02888,"lift_object.lift_height":0.28654,"retract_after_place.retract_height":0.11973,"transport_goal.transport_speed":0.06023},"optimized_scores":{"best_composite_score":0.08616,"best_fitness_score":0.56616,"best_task_score":0.20336},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":3994.0,"contact_point_centroid":[0.54451,0.012,-0.00228],"force_p95":0.12425,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.51454,"mean_force":0.13368,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.56135,0.04362,0.20005]},{"body_a":"world","body_b":"grasp_target","contact_count":145.0,"contact_point_centroid":[0.54301,-0.02808,-0.00116],"force_p95":0.31106,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.43798,"mean_force":0.07144,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.52956,-0.02846,0.04547]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":14082.0,"contact_point_centroid":[0.53151,-0.00951,0.11886],"force_p95":0.10869,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31214,"mean_force":0.07069,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.52706,-0.02837,0.11675]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14983.0,"contact_point_centroid":[0.53146,-0.04715,0.11702],"force_p95":0.10395,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28999,"mean_force":0.06746,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.52708,-0.02837,0.11549]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":230.0,"contact_point_centroid":[0.53402,-0.00839,0.20049],"force_p95":0.22144,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27308,"mean_force":0.13463,"phase_index":4.0,"phase_name":"transport_goal","phase_type":"approach","tcp_position_centroid":[0.52802,-0.02612,0.20509]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":194.0,"contact_point_centroid":[0.534,-0.04448,0.19992],"force_p95":0.20365,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22983,"mean_force":0.15944,"phase_index":4.0,"phase_name":"transport_goal","phase_type":"approach","tcp_position_centroid":[0.52792,-0.02668,0.2051]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54562,-0.0291,-0.00207],"force_p95":0.14169,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18371,"mean_force":0.12784,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.53244,-0.02855,0.04522]},{"body_a":"world","body_b":"grasp_target","contact_count":2224.0,"contact_point_centroid":[0.5456,-0.02923,-0.00194],"force_p95":0.13197,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12285,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.52224,-0.01653,0.22547]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4105.0,"contact_point_centroid":[0.53221,-0.0093,0.04649],"force_p95":0.07816,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13378,"mean_force":0.05184,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.53122,-0.02851,0.04377]},{"body_a":"world","body_b":"grasp_target","contact_count":1544.0,"contact_point_centroid":[0.5456,-0.02923,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.5355,-0.02741,0.11626]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.54451,0.012,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.58473,0.09157,0.20017]},{"body_a":"world","body_b":"grasp_target","contact_count":2652.0,"contact_point_centroid":[0.54451,0.012,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":7.0,"phase_name":"retract_after_place","phase_type":"retract","tcp_position_centroid":[0.58076,0.09081,0.27089]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4912.0,"contact_point_centroid":[0.53219,-0.0476,0.04553],"force_p95":0.07026,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07899,"mean_force":0.04467,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.53122,-0.02851,0.04377]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3998.0,"contact_point_centroid":[0.56336,0.04677,0.20205],"force_p95":0.01105,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01773,"mean_force":0.01057,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.56301,0.04678,0.19979]},{"body_a":"left_finger","body_b":"right_finger","contact_count":223.0,"contact_point_centroid":[0.58758,0.09208,0.19809],"force_p95":0.01093,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01096,"mean_force":0.01003,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.58726,0.09208,0.19598]}],"total_contact_groups":15},"final_pose_error":0.01443,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.54451,0.012,0.01602],"final_tcp_position":[0.58124,0.09085,0.32556],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"peak_contact_force":9748.85066,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":407.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2224.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.53395,-0.02622,0.17922],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.15367,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":386.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1544.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.5397,-0.02876,0.05399],"tcp_start":[0.53395,-0.02622,0.17922],"tcp_to_object_dist_end":0.02859,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54552,-0.02856,0.02576],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.2606,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.13838,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10817.0,"raw_peak_contact_force":0.18371,"subtask_id":"grasp_success","tcp_end":[0.53119,-0.02851,0.04373],"tcp_start":[0.5397,-0.02876,0.05399],"tcp_to_object_dist_end":0.02299,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":13.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5367,-0.02846,0.17634],"object_pos_start":[0.54552,-0.02856,0.02576],"object_to_goal_dist_end":0.21597,"object_to_goal_dist_start":0.2606,"object_z_max":0.17616,"peak_contact_force":0.16185,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":29210.0,"raw_peak_contact_force":0.43798,"subtask_id":"lift_clearance","tcp_end":[0.52755,-0.02838,0.20502],"tcp_start":[0.53119,-0.02851,0.04373],"tcp_to_object_dist_end":0.0301,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":120.0,"n_steps_budget":1000.0,"object_pos_end":[0.54485,0.00774,0.0297],"object_pos_start":[0.5367,-0.02846,0.17634],"object_to_goal_dist_end":0.23264,"object_to_goal_dist_start":0.21597,"object_z_max":0.17644,"peak_contact_force":0.0,"phase_name":"transport_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":424.0,"raw_peak_contact_force":0.27308,"subtask_id":"place_accuracy","tcp_end":[0.53121,-0.01572,0.20716],"tcp_start":[0.53123,-0.01576,0.2072],"tcp_to_object_dist_end":0.17952,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54451,0.012,0.01602],"object_pos_start":[0.54506,0.00849,0.0229],"object_to_goal_dist_end":0.23891,"object_to_goal_dist_start":0.23643,"object_z_max":0.0229,"peak_contact_force":9748.85066,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":7992.0,"raw_peak_contact_force":1.51454,"subtask_id":"place_accuracy","tcp_end":[0.58856,0.09216,0.19865],"tcp_start":[0.53121,-0.01572,0.20716],"tcp_to_object_dist_end":0.20426,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54451,0.012,0.01602],"object_pos_start":[0.54451,0.012,0.01602],"object_to_goal_dist_end":0.23891,"object_to_goal_dist_start":0.23891,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1023.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.58327,0.09128,0.2201],"tcp_start":[0.58856,0.09216,0.19865],"tcp_to_object_dist_end":0.22235,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":663.0,"n_steps_budget":750.0,"object_pos_end":[0.54451,0.012,0.01602],"object_pos_start":[0.54451,0.012,0.01602],"object_to_goal_dist_end":0.23891,"object_to_goal_dist_start":0.23891,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_after_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2652.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.58124,0.09085,0.32556],"tcp_start":[0.58327,0.09128,0.2201],"tcp_to_object_dist_end":0.32153,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```