## Search State

- **Seed**: 1
- **Iteration**: 14 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 13 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 13 | -0.5557 | 0.16 | ❌ rejected |
| 12 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 14 | -0.2971 | 0.21 | ❌ rejected |
| 11 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 13 | -0.2110 | 0.29 | ❌ rejected |
| 10 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | impedance_control | impedance_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 14 | -0.2643 | 0.29 | ❌ rejected |
| 9 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 14 | -0.3089 | 0.19 | ❌ rejected |

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
- Frozen realised-scene SHA-256: `a2ed2c4162d37489f2d2d0fa0373774d72c951d58f2469e0ba2d602ff46b6cfb`
- Frozen object start: [0.5011821624700257, 0.045046369632593536, 0.03]
- Frozen task target: [0.5644159612719634, 0.2448649447137244, 0.1467747178015728]
- Goal object position: (0.5644159612719634, 0.2448649447137244, 0.1467747178015728)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.5644159612719634, 0.2448649447137244, 0.1467747178015728)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.5011821624700257, 0.045046369632593536, 0.03)
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
  frozen_object_start: [0.5012, 0.045, 0.03]
  frozen_task_target: [0.5644, 0.2449, 0.1468]
  frozen_object_starts: {'grasp_target': [0.5011821624700257, 0.045046369632593536, 0.03]}
  frozen_targets: {'place_target': [0.5644159612719634, 0.2448649447137244, 0.1467747178015728]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: a2ed2c4162d37489f2d2d0fa0373774d72c951d58f2469e0ba2d602ff46b6cfb

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
| `object` | offset from object initial position (0.5011821624700257, 0.045046369632593536, 0.03) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5644159612719634, 0.2448649447137244, 0.1467747178015728) | final destination targets |
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

## Current Skill (Q=-0.556) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
subtasks:
- id: reach_pre_grasp
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.1
  weight: 0.2
- id: lift_object
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.2
  weight: 0.3
- id: transport_goal
  target_entity: object
  metric: goal_progress
  weight: 0.5
phases:
- id: approach
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.1
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: replace
    approach_speed:
      type: scalar
      range:
      - 0.05
      - 0.5
      default: 0.2
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_pre_grasp
- id: descend_grasp
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.02
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    descend_offset_z:
      type: scalar
      range:
      - -0.01
      - 0.08
      default: 0.02
      binds_to:
      - path: target.offset.z
        mode: replace
    descend_speed:
      type: scalar
      range:
      - 0.02
      - 0.2
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_pre_grasp
- id: grasp
  type: grasp
  control: position_control
  termination: time_limit
  end_effector_action: force_grasp
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
  parameters:
    grasp_duration:
      type: scalar
      range:
      - 0.5
      - 2.0
      default: 1.0
      binds_to:
      - path: duration.max_time
        mode: replace
  guards:
  - id: check_grasp
    when: after_phase
    predicate: bilateral_grasp
    threshold: 0.01
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - -0.01
- id: lift
  type: lift
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.15
    orientation:
      mode: keep_current
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.1
      - 0.3
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
    lift_speed:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: check_lift
    when: after_phase
    predicate: object_lifted
    threshold: 0.02
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - 0.02
  subtask_id: lift_object
- id: approach_goal
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
    - 0.1
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    approach_goal_height:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: replace
    approach_goal_speed:
      type: scalar
      range:
      - 0.05
      - 0.5
      default: 0.2
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: transport_goal
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
    - 0.0
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    descend_place_speed:
      type: scalar
      range:
      - 0.02
      - 0.2
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: transport_goal
- id: release
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
- id: retract
  type: retract
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.2
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    retract_height:
      type: scalar
      range:
      - 0.1
      - 0.3
      default: 0.2
      binds_to:
      - path: target.offset.z
        mode: replace
    retract_speed:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: generator.speed
        mode: replace

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.1], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **descend_grasp** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.02], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_offset_z: status=consumed; consumers=target.offset.z (replace)
    - descend_speed: status=consumed; consumers=generator.speed (replace)
- **grasp** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings:
    - grasp_duration: status=consumed; consumers=duration.max_time (replace)
  - guards:
    - id=check_grasp, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=0.01
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, -0.01]
- **lift** (`lift`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.15]
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
    - lift_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=check_lift, when=after_phase, predicate=object_lifted, on_failure=retry, threshold=0.02
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, 0.02]
- **approach_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.1], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_goal_height: status=consumed; consumers=target.offset.z (replace)
    - approach_goal_speed: status=consumed; consumers=generator.speed (replace)
- **descend_place** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_place_speed: status=consumed; consumers=generator.speed (replace)
- **release** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings:
    - release_duration: status=consumed; consumers=duration.max_time (replace)
- **retract** (`retract`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.2], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - retract_height: status=consumed; consumers=target.offset.z (replace)
    - retract_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: -0.556
- **task_score** (E): 0.157
- **fitness_score**: 0.274  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.830

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach | 1.00 | 1.00 | 0.1160 |
| descend_grasp | 1.00 | 1.00 | 0.1248 |
| grasp | 1.00 | 1.00 | 0.0110 |
| lift | 0.00 | 1.00 | 0.0025 |
| approach_goal | 0.00 | 1.00 | 0.0000 |
| descend_place | 0.00 | 1.00 | 0.2082 |
| release | 1.00 | 1.00 | 0.0294 |
| retract | 0.00 | 1.00 | 0.2604 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.478, -0.000, 0.192) | (0.479, -0.000, 0.030)→(0.479, -0.000, 0.026) | 0.276→0.278 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_grasp | descend | 1.00 / step_budget | (0.478, -0.000, 0.192)→(0.474, -0.001, 0.067) | (0.479, -0.000, 0.026)→(0.479, -0.000, 0.026) | 0.278→0.278 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp | grasp | 1.00 / step_budget | (0.474, -0.001, 0.067)→(0.467, -0.001, 0.059) | (0.479, -0.000, 0.026)→(0.479, 0.000, 0.024) | 0.278→0.279 | 1.00 / 23.667 | 0.242 | 0.258 |
| lift | lift | 0.00 / step_budget | (0.056, 0.000, 0.314)→(0.054, 0.000, 0.315) | (0.479, 0.000, 0.024)→(0.462, 0.010, 0.023) | 0.279→0.281 | 1.00 / 28.000 | 203.948 | 182.677 |
| approach_goal | approach | 0.00 / guard_failure | (0.054, 0.000, 0.315)→(0.054, 0.000, 0.315) | (0.462, 0.010, 0.023)→(0.462, 0.010, 0.023) | 0.281→0.281 | 1.00 / 28.333 | 24.535 | 24.535 |
| descend_place | descend | 0.00 / step_budget | (0.054, 0.000, 0.315)→(0.240, 0.069, 0.256) | (0.462, 0.010, 0.023)→(0.462, 0.010, 0.023) | 0.281→0.281 | 1.00 / 8.000 | 0.123 | 44.796 |
| release | release | 1.00 / step_budget | (0.240, 0.069, 0.256)→(0.238, 0.068, 0.286) | (0.462, 0.010, 0.023)→(0.462, 0.010, 0.023) | 0.281→0.281 | 1.00 / 4.000 | 0.123 | 0.123 |
| retract | retract | 0.00 / step_budget | (0.238, 0.068, 0.286)→(0.478, 0.159, 0.309) | (0.462, 0.010, 0.023)→(0.462, 0.010, 0.023) | 0.281→0.281 | 1.00 / 4.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 0.000
- transport_retention: 0.000
- terminal_score: 0.201
- phase_score: 0.057
- phase_breakdown.reach_pre_grasp_score: 0.283
- phase_breakdown.lift_object_score: 0.000
- phase_breakdown.transport_goal_score: 0.000
- grasp_place_fitness: 0.296

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.296
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.201
- **Median Q (composite search score)**: -0.564
- **K-run variance**: 0.0002
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.248


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `8110053be9072e64e15984c6424e4a66fe19af4b6c37a60139a43e94cc34ad53`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `46ef03f7b16015a0d14bf26d80c05d326b92c02b0bf759391930f5ab902d1933`; realized-scene SHA-256: `a2ed2c4162d37489f2d2d0fa0373774d72c951d58f2469e0ba2d602ff46b6cfb`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50118,0.04505,0.03]},{"name":"goal","value":[0.56442,0.24486,0.14677]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.50118,0.04505,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.56442,0.24486,0.14677]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.52119,"average_solve_count":236.0,"average_success_count":236.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_height":0.15706,"approach.approach_speed":0.28786,"approach_goal.approach_goal_height":0.0687,"approach_goal.approach_goal_speed":0.21195,"descend_grasp.descend_offset_z":0.03244,"descend_grasp.descend_speed":0.06905,"descend_place.descend_place_speed":0.09986,"grasp.grasp_duration":1.04288,"lift.lift_height_world":0.31255,"lift.lift_speed":0.16366,"release.release_duration":1.07807,"retract.retract_height":0.1387,"retract.retract_speed":0.17118},"optimized_scores":{"best_composite_score":-0.53384,"best_fitness_score":0.29616,"best_task_score":0.2011},"replay_outcomes":[{"contacts":{"omitted_contact_groups":15,"reported_contact_groups":[{"body_a":"link1","body_b":"hand","contact_count":856.0,"contact_point_centroid":[0.04377,-0.0616,0.36956],"force_p95":83.0692,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":126.48961,"mean_force":62.03409,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.0489,0.0037,0.32646]},{"body_a":"link1","body_b":"hand","contact_count":7.0,"contact_point_centroid":[0.03799,-0.06201,0.3761],"force_p95":91.79296,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":94.80472,"mean_force":63.45692,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.04205,0.00283,0.33349]},{"body_a":"link1","body_b":"hand","contact_count":3.0,"contact_point_centroid":[0.03787,-0.06202,0.37616],"force_p95":36.79379,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":36.87005,"mean_force":35.36945,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.04192,0.00275,0.33354]},{"body_a":"right_finger","body_b":"link2","contact_count":468.0,"contact_point_centroid":[0.04615,0.00688,0.32857],"force_p95":5.90841,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":7.51582,"mean_force":3.01307,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.04995,0.00669,0.33]},{"body_a":"left_finger","body_b":"link1","contact_count":480.0,"contact_point_centroid":[0.04621,0.0045,0.32918],"force_p95":5.85725,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":6.87965,"mean_force":3.21273,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.05014,0.00678,0.32992]},{"body_a":"left_finger","body_b":"link2","contact_count":476.0,"contact_point_centroid":[0.04519,0.00333,0.3286],"force_p95":4.97885,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":6.82264,"mean_force":2.96136,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.05011,0.00677,0.32993]},{"body_a":"left_finger","body_b":"link1","contact_count":4003.0,"contact_point_centroid":[0.04539,0.00149,0.32728],"force_p95":3.76129,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":6.63083,"mean_force":2.51197,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.04784,0.00352,0.32778]},{"body_a":"right_finger","body_b":"link1","contact_count":3924.0,"contact_point_centroid":[0.04351,0.00704,0.32737],"force_p95":3.14859,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":6.39112,"mean_force":1.91249,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.04764,0.00349,0.32801]},{"body_a":"right_finger","body_b":"link2","contact_count":3613.0,"contact_point_centroid":[0.04321,0.00414,0.32924],"force_p95":3.05426,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":6.36788,"mean_force":1.92279,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.04651,0.00329,0.32948]},{"body_a":"right_finger","body_b":"link1","contact_count":373.0,"contact_point_centroid":[0.04296,0.00839,0.32968],"force_p95":5.04997,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":6.18188,"mean_force":3.05971,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.048,0.00581,0.33081]},{"body_a":"left_finger","body_b":"link2","contact_count":3504.0,"contact_point_centroid":[0.04188,0.00125,0.32919],"force_p95":2.14021,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":5.42724,"mean_force":1.10798,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.04646,0.00329,0.32949]},{"body_a":"left_finger","body_b":"link1","contact_count":15.0,"contact_point_centroid":[0.04019,0.00318,0.3336],"force_p95":3.97203,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":4.06347,"mean_force":2.94703,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.04192,0.00275,0.33354]},{"body_a":"right_finger","body_b":"link1","contact_count":15.0,"contact_point_centroid":[0.03862,0.00702,0.33335],"force_p95":2.89568,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":3.0081,"mean_force":2.28657,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.04192,0.00275,0.33354]},{"body_a":"right_finger","body_b":"link2","contact_count":15.0,"contact_point_centroid":[0.03898,0.0031,0.33222],"force_p95":2.82058,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":2.87235,"mean_force":2.07109,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.04192,0.00275,0.33354]},{"body_a":"left_finger","body_b":"link2","contact_count":15.0,"contact_point_centroid":[0.03824,0.00048,0.33224],"force_p95":1.76896,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1.86787,"mean_force":1.35424,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.04192,0.00275,0.33354]},{"body_a":"world","body_b":"grasp_target","contact_count":8276.0,"contact_point_centroid":[0.49466,0.04843,-0.00204],"force_p95":0.12869,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.47626,"mean_force":0.12672,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.16463,0.01465,0.26441]}],"total_contact_groups":31},"final_pose_error":0.10345,"key_states":{"actual_goal_position":[0.56442,0.24486,0.14677],"final_object_position":[0.49498,0.04869,0.02602],"final_tcp_position":[0.47049,0.20158,0.28312],"realised_goal_position":[0.56442,0.24486,0.14677],"realised_object_initial_position":[0.50118,0.04505,0.03]},"peak_contact_force":273002.54994,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":343.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.03],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.23992,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1368.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_pre_grasp","tcp_end":[0.49767,0.03965,0.19441],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16851,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":417.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1668.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_pre_grasp","tcp_end":[0.49646,0.04409,0.06713],"tcp_start":[0.49767,0.03965,0.19441],"tcp_to_object_dist_end":0.04139,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50127,0.04304,0.02382],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24462,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.267,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":7286.0,"raw_peak_contact_force":0.26644,"tcp_end":[0.48867,0.04339,0.0584],"tcp_start":[0.49646,0.04409,0.06713],"tcp_to_object_dist_end":0.0368,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":62.0,"n_steps":2135.0,"n_steps_budget":1000.0,"object_pos_end":[0.49498,0.04869,0.02602],"object_pos_start":[0.50127,0.04304,0.02382],"object_to_goal_dist_end":0.2406,"object_to_goal_dist_start":0.24462,"object_z_max":0.03018,"peak_contact_force":471.57913,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":49082.0,"raw_peak_contact_force":126.48961,"subtask_id":"lift_object","tcp_end":[0.04192,0.00276,0.33353],"tcp_start":[0.04664,0.00329,0.33016],"tcp_to_object_dist_end":0.54949,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":63.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.49498,0.04869,0.02602],"object_pos_start":[0.49498,0.04869,0.02602],"object_to_goal_dist_end":0.2406,"object_to_goal_dist_start":0.2406,"object_z_max":0.02602,"peak_contact_force":36.87005,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":187.0,"raw_peak_contact_force":36.87005,"subtask_id":"transport_goal","tcp_end":[0.04191,0.00275,0.33354],"tcp_start":[0.04191,0.00275,0.33354],"tcp_to_object_dist_end":0.5495,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49498,0.04869,0.02602],"object_pos_start":[0.49498,0.04869,0.02602],"object_to_goal_dist_end":0.2406,"object_to_goal_dist_start":0.2406,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":12027.0,"raw_peak_contact_force":94.80472,"subtask_id":"transport_goal","tcp_end":[0.22137,0.08594,0.26603],"tcp_start":[0.04191,0.00275,0.33354],"tcp_to_object_dist_end":0.36586,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.49498,0.04869,0.02602],"object_pos_start":[0.49498,0.04869,0.02602],"object_to_goal_dist_end":0.2406,"object_to_goal_dist_start":0.2406,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1011.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.21907,0.08484,0.29533],"tcp_start":[0.22137,0.08594,0.26603],"tcp_to_object_dist_end":0.38725,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49498,0.04869,0.02602],"object_pos_start":[0.49498,0.04869,0.02602],"object_to_goal_dist_end":0.2406,"object_to_goal_dist_start":0.2406,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.47049,0.20158,0.28312],"tcp_start":[0.21907,0.08484,0.29533],"tcp_to_object_dist_end":0.30013,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `1efc3ad2e58ea1c47cd56203c4986b53dab7b80d759e458b85d233ccc9cc04bd`; realized-scene SHA-256: `67b45068113fe0ef6f199d4981822d51bd0bd66bb4f388f7402a08094b41852a`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.47616,-0.02015,0.03]},{"name":"goal","value":[0.63142,0.15919,0.19002]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.47616,-0.02015,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.63142,0.15919,0.19002]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.52915,"average_solve_count":223.0,"average_success_count":223.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_height":0.14849,"approach.approach_speed":0.27945,"approach_goal.approach_goal_height":0.08899,"approach_goal.approach_goal_speed":0.14701,"descend_grasp.descend_offset_z":0.03242,"descend_grasp.descend_speed":0.05419,"descend_place.descend_place_speed":0.13849,"grasp.grasp_duration":1.20576,"lift.lift_height_world":0.22884,"lift.lift_speed":0.23334,"release.release_duration":1.24421,"retract.retract_height":0.2075,"retract.retract_speed":0.11236},"optimized_scores":{"best_composite_score":-0.5638,"best_fitness_score":0.2662,"best_task_score":0.14511},"replay_outcomes":[{"contacts":{"omitted_contact_groups":10,"reported_contact_groups":[{"body_a":"link2","body_b":"hand","contact_count":1639.0,"contact_point_centroid":[0.05313,0.06315,0.35066],"force_p95":78.57145,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":231.87097,"mean_force":72.41466,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.0598,-0.00176,0.30587]},{"body_a":"link2","body_b":"hand","contact_count":4.0,"contact_point_centroid":[0.05273,0.06361,0.35046],"force_p95":16.70074,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":19.64793,"mean_force":4.91198,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.05936,-0.00071,0.30576]},{"body_a":"link2","body_b":"hand","contact_count":3.0,"contact_point_centroid":[0.05269,0.06361,0.35048],"force_p95":18.04585,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":18.22945,"mean_force":16.08058,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.05929,-0.00075,0.30577]},{"body_a":"link1","body_b":"hand","contact_count":27.0,"contact_point_centroid":[0.05177,-0.00224,0.34974],"force_p95":0.0,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":7.4033,"mean_force":0.2742,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.05759,-0.00405,0.30539]},{"body_a":"right_finger","body_b":"link1","contact_count":4927.0,"contact_point_centroid":[0.05278,-0.00049,0.30488],"force_p95":1.03901,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":4.17958,"mean_force":0.81279,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.0598,-0.00176,0.30587]},{"body_a":"left_finger","body_b":"link1","contact_count":4927.0,"contact_point_centroid":[0.05285,-0.00292,0.30487],"force_p95":1.08997,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":4.1524,"mean_force":0.83773,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.0598,-0.00176,0.30587]},{"body_a":"left_finger","body_b":"link1","contact_count":71.0,"contact_point_centroid":[0.05354,-0.00242,0.30358],"force_p95":1.27415,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1.69202,"mean_force":0.53308,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.06138,-0.00013,0.30548]},{"body_a":"right_finger","body_b":"link1","contact_count":64.0,"contact_point_centroid":[0.05316,0.00222,0.30343],"force_p95":1.25096,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1.57579,"mean_force":0.47948,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.06116,-0.00019,0.30551]},{"body_a":"right_finger","body_b":"link2","contact_count":42.0,"contact_point_centroid":[0.05212,0.00231,0.31762],"force_p95":0.82155,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1.10389,"mean_force":0.51941,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.05731,-0.00406,0.30531]},{"body_a":"left_finger","body_b":"link1","contact_count":9.0,"contact_point_centroid":[0.0526,-0.00285,0.30479],"force_p95":1.03191,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1.03278,"mean_force":0.85692,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.05929,-0.00075,0.30577]},{"body_a":"right_finger","body_b":"link1","contact_count":9.0,"contact_point_centroid":[0.05238,0.00175,0.30481],"force_p95":0.97431,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.97814,"mean_force":0.77841,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.05929,-0.00075,0.30577]},{"body_a":"world","body_b":"grasp_target","contact_count":9771.0,"contact_point_centroid":[0.47423,-0.02067,-0.00204],"force_p95":0.12584,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55855,"mean_force":0.12632,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.13077,-0.00529,0.2688]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":44.0,"contact_point_centroid":[0.46716,-0.00987,0.05299],"force_p95":0.30355,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.37325,"mean_force":0.1756,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.45939,-0.01945,0.06015]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47622,-0.02042,-0.00228],"force_p95":0.26136,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.31878,"mean_force":0.14556,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46552,-0.01962,0.06062]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":257.0,"contact_point_centroid":[0.45999,-0.02931,0.05493],"force_p95":0.20194,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27681,"mean_force":0.08177,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.45825,-0.0194,0.06043]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1946.0,"contact_point_centroid":[0.46556,-0.00128,0.05388],"force_p95":0.15545,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1987,"mean_force":0.0906,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46446,-0.01959,0.05952]}],"total_contact_groups":26},"final_pose_error":0.22138,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.47471,-0.02075,0.02602],"final_tcp_position":[0.42645,0.10219,0.33632],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":231.87097,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":329.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1312.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_pre_grasp","tcp_end":[0.47571,-0.01764,0.188],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.162,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":416.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1664.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_pre_grasp","tcp_end":[0.47195,-0.01977,0.06736],"tcp_start":[0.47571,-0.01764,0.188],"tcp_to_object_dist_end":0.04155,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":18.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47637,-0.01641,0.02323],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28757,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.31946,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":6694.0,"raw_peak_contact_force":0.31878,"tcp_end":[0.46444,-0.0196,0.05949],"tcp_start":[0.47195,-0.01977,0.06736],"tcp_to_object_dist_end":0.03831,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":11.0,"n_steps":2510.0,"n_steps_budget":1000.0,"object_pos_end":[0.47471,-0.02075,0.02602],"object_pos_start":[0.47637,-0.01641,0.02323],"object_to_goal_dist_end":0.28954,"object_to_goal_dist_start":0.28757,"object_z_max":0.02859,"peak_contact_force":69.9509,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":26174.0,"raw_peak_contact_force":231.87097,"subtask_id":"lift_object","tcp_end":[0.05929,-0.00075,0.30577],"tcp_start":[0.05985,-0.00131,0.30587],"tcp_to_object_dist_end":0.50124,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":11.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.47471,-0.02075,0.02602],"object_pos_start":[0.47471,-0.02075,0.02602],"object_to_goal_dist_end":0.28954,"object_to_goal_dist_start":0.28954,"object_z_max":0.02602,"peak_contact_force":18.22945,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":33.0,"raw_peak_contact_force":18.22945,"subtask_id":"transport_goal","tcp_end":[0.05929,-0.00075,0.30577],"tcp_start":[0.05929,-0.00075,0.30577],"tcp_to_object_dist_end":0.50123,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47471,-0.02075,0.02602],"object_pos_start":[0.47471,-0.02075,0.02602],"object_to_goal_dist_end":0.28954,"object_to_goal_dist_start":0.28954,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":7949.0,"raw_peak_contact_force":19.64793,"subtask_id":"transport_goal","tcp_end":[0.25673,0.05456,0.26265],"tcp_start":[0.05929,-0.00075,0.30577],"tcp_to_object_dist_end":0.33043,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47471,-0.02075,0.02602],"object_pos_start":[0.47471,-0.02075,0.02602],"object_to_goal_dist_end":0.28954,"object_to_goal_dist_start":0.28954,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1024.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.254,0.05385,0.29175],"tcp_start":[0.25673,0.05456,0.26265],"tcp_to_object_dist_end":0.3534,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47471,-0.02075,0.02602],"object_pos_start":[0.47471,-0.02075,0.02602],"object_to_goal_dist_end":0.28954,"object_to_goal_dist_start":0.28954,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.42645,0.10219,0.33632],"tcp_start":[0.254,0.05385,0.29175],"tcp_to_object_dist_end":0.33724,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `37495cb43897015e78e007c86af160d11c8460c1ce7249e5c03dce38206c0daf`; realized-scene SHA-256: `5ce27bcdb8582e1d517b17df0f9c2ad7b05701113a75707627744a889253e6a7`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.45856,-0.02632,0.03]},{"name":"goal","value":[0.63013,0.20822,0.11412]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.45856,-0.02632,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.63013,0.20822,0.11412]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.8439,"average_solve_count":205.0,"average_success_count":205.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_height":0.15327,"approach.approach_speed":0.26747,"approach_goal.approach_goal_height":0.09478,"approach_goal.approach_goal_speed":0.20762,"descend_grasp.descend_offset_z":0.03098,"descend_grasp.descend_speed":0.10571,"descend_place.descend_place_speed":0.11195,"grasp.grasp_duration":1.48515,"lift.lift_height_world":0.24784,"lift.lift_speed":0.25689,"release.release_duration":1.75065,"retract.retract_height":0.21427,"retract.retract_speed":0.19593},"optimized_scores":{"best_composite_score":-0.5696,"best_fitness_score":0.2604,"best_task_score":0.12427},"replay_outcomes":[{"contacts":{"omitted_contact_groups":8,"reported_contact_groups":[{"body_a":"link2","body_b":"hand","contact_count":1588.0,"contact_point_centroid":[0.05339,0.06293,0.3507],"force_p95":80.14858,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":189.67086,"mean_force":72.96321,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.06023,-0.00196,0.30594]},{"body_a":"link2","body_b":"hand","contact_count":4.0,"contact_point_centroid":[0.05283,0.06352,0.35047],"force_p95":16.94434,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":19.93452,"mean_force":4.98363,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.05961,-0.00083,0.3058]},{"body_a":"link2","body_b":"hand","contact_count":3.0,"contact_point_centroid":[0.05279,0.06352,0.35049],"force_p95":18.3191,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":18.50665,"mean_force":16.28966,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.05954,-0.00087,0.30581]},{"body_a":"right_finger","body_b":"link1","contact_count":4775.0,"contact_point_centroid":[0.05301,-0.00086,0.30493],"force_p95":0.99768,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":2.77402,"mean_force":0.73293,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.06024,-0.00197,0.30594]},{"body_a":"left_finger","body_b":"link1","contact_count":4774.0,"contact_point_centroid":[0.05306,-0.00306,0.30492],"force_p95":1.0305,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":2.73858,"mean_force":0.75085,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.06024,-0.00197,0.30594]},{"body_a":"left_finger","body_b":"link1","contact_count":67.0,"contact_point_centroid":[0.05359,-0.00225,0.30351],"force_p95":1.50426,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1.66571,"mean_force":0.57014,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.06151,-0.00014,0.30557]},{"body_a":"right_finger","body_b":"link1","contact_count":60.0,"contact_point_centroid":[0.05325,0.00177,0.30348],"force_p95":1.46008,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1.54693,"mean_force":0.51866,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.06126,-0.00023,0.3056]},{"body_a":"left_finger","body_b":"link1","contact_count":9.0,"contact_point_centroid":[0.05273,-0.00262,0.30483],"force_p95":0.97928,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.9805,"mean_force":0.80307,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.05954,-0.00087,0.30581]},{"body_a":"right_finger","body_b":"link1","contact_count":9.0,"contact_point_centroid":[0.05255,0.0012,0.30484],"force_p95":0.9401,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.94433,"mean_force":0.74391,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.05954,-0.00087,0.30581]},{"body_a":"world","body_b":"grasp_target","contact_count":9075.0,"contact_point_centroid":[0.41742,7e-05,-0.00204],"force_p95":0.12313,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.65713,"mean_force":0.12868,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.11809,-0.00605,0.27756]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":693.0,"contact_point_centroid":[0.4322,-0.006,0.05823],"force_p95":0.28066,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.54466,"mean_force":0.14469,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.43083,-0.0247,0.0632]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1072.0,"contact_point_centroid":[0.42605,-0.04251,0.06039],"force_p95":0.24834,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.39054,"mean_force":0.12309,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.42511,-0.02438,0.06525]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45859,-0.0263,-0.00206],"force_p95":0.14123,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18774,"mean_force":0.12726,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.44842,-0.0256,0.05977]},{"body_a":"world","body_b":"grasp_target","contact_count":1316.0,"contact_point_centroid":[0.45856,-0.02632,-0.0019],"force_p95":0.13564,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.123,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.48013,-0.01105,0.24683]},{"body_a":"world","body_b":"grasp_target","contact_count":1612.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.45635,-0.02439,0.12863]},{"body_a":"world","body_b":"grasp_target","contact_count":12.0,"contact_point_centroid":[0.4171,0.00126,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.05954,-0.00087,0.30581]}],"total_contact_groups":24},"final_pose_error":0.10012,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.4171,0.00126,0.01602],"final_tcp_position":[0.53799,0.17454,0.30841],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":189.67086,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":330.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1316.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_pre_grasp","tcp_end":[0.4603,-0.02307,0.19231],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16633,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":403.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1612.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_pre_grasp","tcp_end":[0.45469,-0.02583,0.06605],"tcp_start":[0.4603,-0.02307,0.19231],"tcp_to_object_dist_end":0.04022,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":31.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45851,-0.02584,0.02578],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30338,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.14033,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":8401.0,"raw_peak_contact_force":0.18774,"tcp_end":[0.44735,-0.02556,0.05871],"tcp_start":[0.45469,-0.02583,0.06605],"tcp_to_object_dist_end":0.03478,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":11.0,"n_steps":2412.0,"n_steps_budget":1000.0,"object_pos_end":[0.4171,0.00126,0.01602],"object_pos_start":[0.45851,-0.02584,0.02578],"object_to_goal_dist_end":0.31279,"object_to_goal_dist_start":0.30338,"object_z_max":0.03924,"peak_contact_force":70.31253,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":27323.0,"raw_peak_contact_force":189.67086,"subtask_id":"lift_object","tcp_end":[0.05954,-0.00087,0.30581],"tcp_start":[0.06019,-0.00148,0.30592],"tcp_to_object_dist_end":0.46025,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":11.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.4171,0.00126,0.01602],"object_pos_start":[0.4171,0.00126,0.01602],"object_to_goal_dist_end":0.31279,"object_to_goal_dist_start":0.31279,"object_z_max":0.01602,"peak_contact_force":18.50665,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":33.0,"raw_peak_contact_force":18.50665,"subtask_id":"transport_goal","tcp_end":[0.05954,-0.00087,0.30581],"tcp_start":[0.05954,-0.00087,0.30581],"tcp_to_object_dist_end":0.46025,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.4171,0.00126,0.01602],"object_pos_start":[0.4171,0.00126,0.01602],"object_to_goal_dist_end":0.31279,"object_to_goal_dist_start":0.31279,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":7966.0,"raw_peak_contact_force":19.93452,"subtask_id":"transport_goal","tcp_end":[0.24311,0.06653,0.24074],"tcp_start":[0.05954,-0.00087,0.30581],"tcp_to_object_dist_end":0.2916,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.4171,0.00126,0.01602],"object_pos_start":[0.4171,0.00126,0.01602],"object_to_goal_dist_end":0.31279,"object_to_goal_dist_start":0.31279,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1020.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.24036,0.06559,0.27006],"tcp_start":[0.24311,0.06653,0.24074],"tcp_to_object_dist_end":0.31609,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.4171,0.00126,0.01602],"object_pos_start":[0.4171,0.00126,0.01602],"object_to_goal_dist_end":0.31279,"object_to_goal_dist_start":0.31279,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.53799,0.17454,0.30841],"tcp_start":[0.24036,0.06559,0.27006],"tcp_to_object_dist_end":0.36074,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```