## Search State

- **Seed**: 1
- **Iteration**: 11 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 10 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | impedance_control | impedance_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 14 | -0.2643 | 0.29 | ❌ rejected |
| 9 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 14 | -0.3089 | 0.19 | ❌ rejected |
| 8 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 13 | -0.2424 | 0.23 | ❌ rejected |
| 7 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 13 | -0.2208 | 0.27 | ❌ rejected |
| 6 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 11 | -0.1690 | 0.21 | ❌ rejected |

**Proposal policy**: task_score is 0.29 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.264) — your mutation base

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

- **Composite score**: -0.264
- **task_score** (E): 0.290
- **fitness_score**: 0.616  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.880

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach | 1.00 | 1.00 | 0.1082 |
| descend_grasp | 1.00 | 1.00 | 0.1529 |
| grasp | 1.00 | 1.00 | 0.0111 |
| lift | 0.67 | 0.67 | 0.1366 |
| approach_goal | 1.00 | 1.00 | 0.2695 |
| descend_place | 1.00 | 1.00 | 0.1545 |
| release | 1.00 | 1.00 | 0.0205 |
| retract | 1.00 | 1.00 | 0.1517 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.479, 0.000, 0.200) | (0.479, -0.000, 0.030)→(0.479, -0.000, 0.026) | 0.276→0.278 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_grasp | descend | 1.00 / step_budget | (0.479, 0.000, 0.200)→(0.474, -0.000, 0.047) | (0.479, -0.000, 0.026)→(0.479, -0.000, 0.026) | 0.278→0.278 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp | grasp | 1.00 / step_budget | (0.474, -0.000, 0.047)→(0.467, -0.001, 0.039) | (0.479, -0.000, 0.026)→(0.479, -0.001, 0.026) | 0.278→0.278 | 1.00 / 44.667 | 0.143 | 0.203 |
| lift | lift | 0.67 / step_budget | (0.467, -0.001, 0.039)→(0.473, -0.001, 0.176) | (0.479, -0.001, 0.026)→(0.485, -0.002, 0.145) | 0.278→0.245 | 0.67 / 21.000 | 0.062 | 0.507 |
| approach_goal | approach | 1.00 / step_budget | (0.473, -0.001, 0.176)→(0.598, 0.188, 0.312) | (0.485, -0.002, 0.145)→(0.542, 0.074, 0.080) | 0.245→0.207 | 1.00 / 8.000 | 3249.716 | 1.272 |
| descend_place | descend | 1.00 / step_budget | (0.598, 0.188, 0.312)→(0.604, 0.201, 0.158) | (0.542, 0.074, 0.080)→(0.549, 0.077, 0.016) | 0.207→0.208 | 1.00 / 8.667 | 94252.224 | 0.649 |
| release | release | 1.00 / step_budget | (0.604, 0.201, 0.158)→(0.598, 0.199, 0.178) | (0.549, 0.077, 0.016)→(0.549, 0.077, 0.016) | 0.208→0.208 | 1.00 / 4.000 | 0.123 | 0.123 |
| retract | retract | 1.00 / step_budget | (0.598, 0.199, 0.178)→(0.607, 0.203, 0.329) | (0.549, 0.077, 0.016)→(0.549, 0.077, 0.016) | 0.208→0.208 | 1.00 / 4.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: 1.000
- terminal_score: 0.515
- phase_score: 0.093
- phase_breakdown.reach_pre_grasp_score: 0.206
- phase_breakdown.lift_object_score: 0.174
- phase_breakdown.transport_goal_score: 0.000
- grasp_place_fitness: 0.725

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.725
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.515
- **Median Q (composite search score)**: -0.295
- **K-run variance**: 0.0063
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.298


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.42953,"average_solve_count":149.0,"average_success_count":149.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_height":0.1308,"approach.approach_speed":0.24004,"approach_goal.approach_goal_height":0.1583,"approach_goal.approach_goal_speed":0.3298,"approach_goal.arc_height":0.06395,"descend_grasp.descend_offset_z":0.00454,"descend_grasp.descend_speed":0.10767,"descend_place.descend_place_speed":0.11473,"grasp.grasp_duration":0.94526,"lift.lift_height":0.15059,"lift.lift_speed":0.12544,"release.release_duration":1.25675,"retract.retract_height":0.24653,"retract.retract_speed":0.16695},"optimized_scores":{"best_composite_score":-0.29488,"best_fitness_score":0.58512,"best_task_score":0.21416},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1756.0,"contact_point_centroid":[0.51585,0.06054,-0.00266],"force_p95":0.26992,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.53358,"mean_force":0.14858,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.52689,0.13808,0.28437]},{"body_a":"world","body_b":"grasp_target","contact_count":166.0,"contact_point_centroid":[0.49866,0.04286,-0.00128],"force_p95":0.39856,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.6306,"mean_force":0.08675,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.48688,0.04328,0.03222]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9912.0,"contact_point_centroid":[0.49276,0.02427,0.08823],"force_p95":0.10722,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33018,"mean_force":0.07042,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.48965,0.04311,0.08611]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10300.0,"contact_point_centroid":[0.49238,0.06198,0.08536],"force_p95":0.10826,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32444,"mean_force":0.06883,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.48942,0.04311,0.0835]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":854.0,"contact_point_centroid":[0.50179,0.065,0.17625],"force_p95":0.18541,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28537,"mean_force":0.11854,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.49616,0.04656,0.17957]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":877.0,"contact_point_centroid":[0.50186,0.02816,0.176],"force_p95":0.18414,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27616,"mean_force":0.11508,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.49613,0.04642,0.17904]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50124,0.04474,-0.00214],"force_p95":0.16472,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24267,"mean_force":0.13378,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.48942,0.04354,0.03174]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4058.0,"contact_point_centroid":[0.48874,0.02423,0.03333],"force_p95":0.08159,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15103,"mean_force":0.05191,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.48826,0.04344,0.03052]},{"body_a":"world","body_b":"grasp_target","contact_count":1560.0,"contact_point_centroid":[0.50118,0.04505,-0.00191],"force_p95":0.13468,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12294,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.49786,0.01964,0.2344]},{"body_a":"world","body_b":"grasp_target","contact_count":1612.0,"contact_point_centroid":[0.50118,0.04505,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.4956,0.0422,0.10316]},{"body_a":"world","body_b":"grasp_target","contact_count":1580.0,"contact_point_centroid":[0.51576,0.06056,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.55783,0.23369,0.22778]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.51576,0.06056,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.55575,0.23944,0.15576]},{"body_a":"world","body_b":"grasp_target","contact_count":3128.0,"contact_point_centroid":[0.51576,0.06056,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.55697,0.24053,0.27106]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5016.0,"contact_point_centroid":[0.48874,0.06261,0.03234],"force_p95":0.07429,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08677,"mean_force":0.04469,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.48826,0.04344,0.03052]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1638.0,"contact_point_centroid":[0.53084,0.14776,0.29266],"force_p95":0.01234,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01565,"mean_force":0.01061,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.53022,0.14774,0.29042]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1676.0,"contact_point_centroid":[0.55834,0.23371,0.23019],"force_p95":0.01103,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0128,"mean_force":0.0105,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.55783,0.23368,0.22792]}],"total_contact_groups":17},"final_pose_error":0.01796,"key_states":{"actual_goal_position":[0.56442,0.24486,0.14677],"final_object_position":[0.51576,0.06056,0.01602],"final_tcp_position":[0.56311,0.2439,0.37542],"realised_goal_position":[0.56442,0.24486,0.14677],"realised_object_initial_position":[0.50118,0.04505,0.03]},"peak_contact_force":273007.8616,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":391.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.03],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.23992,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1560.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_pre_grasp","tcp_end":[0.49746,0.04045,0.16859],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.14269,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":403.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1612.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_pre_grasp","tcp_end":[0.49632,0.04417,0.03914],"tcp_start":[0.49746,0.04045,0.16859],"tcp_to_object_dist_end":0.01402,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50109,0.04352,0.02552],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24342,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.15581,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10874.0,"raw_peak_contact_force":0.24267,"tcp_end":[0.48823,0.04343,0.03049],"tcp_start":[0.49632,0.04417,0.03914],"tcp_to_object_dist_end":0.01379,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":691.0,"n_steps_budget":750.0,"object_pos_end":[0.51284,0.04347,0.14603],"object_pos_start":[0.50109,0.04352,0.02552],"object_to_goal_dist_end":0.2079,"object_to_goal_dist_start":0.24342,"object_z_max":0.14589,"peak_contact_force":0.1136,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":20378.0,"raw_peak_contact_force":0.6306,"subtask_id":"lift_object","tcp_end":[0.49667,0.04318,0.16249],"tcp_start":[0.48823,0.04343,0.03049],"tcp_to_object_dist_end":0.02308,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":628.0,"n_steps_budget":1000.0,"object_pos_end":[0.51576,0.06056,0.01602],"object_pos_start":[0.51284,0.04347,0.14603],"object_to_goal_dist_end":0.23116,"object_to_goal_dist_start":0.2079,"object_z_max":0.17782,"peak_contact_force":9748.95465,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":5125.0,"raw_peak_contact_force":1.53358,"subtask_id":"transport_goal","tcp_end":[0.55713,0.22697,0.30106],"tcp_start":[0.49667,0.04318,0.16249],"tcp_to_object_dist_end":0.33264,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":395.0,"n_steps_budget":1000.0,"object_pos_end":[0.51576,0.06056,0.01602],"object_pos_start":[0.51576,0.06056,0.01602],"object_to_goal_dist_end":0.23116,"object_to_goal_dist_start":0.23116,"object_z_max":0.01602,"peak_contact_force":273007.8616,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3256.0,"raw_peak_contact_force":0.12263,"subtask_id":"transport_goal","tcp_end":[0.56012,0.24139,0.15497],"tcp_start":[0.55713,0.22697,0.30106],"tcp_to_object_dist_end":0.23233,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51576,0.06056,0.01602],"object_pos_start":[0.51576,0.06056,0.01602],"object_to_goal_dist_end":0.23116,"object_to_goal_dist_start":0.23116,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1020.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.55422,0.23869,0.17569],"tcp_start":[0.56012,0.24139,0.15497],"tcp_to_object_dist_end":0.24229,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":782.0,"n_steps_budget":840.0,"object_pos_end":[0.51576,0.06056,0.01602],"object_pos_start":[0.51576,0.06056,0.01602],"object_to_goal_dist_end":0.23116,"object_to_goal_dist_start":0.23116,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3128.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.56311,0.2439,0.37542],"tcp_start":[0.55422,0.23869,0.17569],"tcp_to_object_dist_end":0.40623,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.02525,"average_solve_count":198.0,"average_success_count":198.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_height":0.17913,"approach.approach_speed":0.17784,"approach_goal.approach_goal_height":0.19651,"approach_goal.approach_goal_speed":0.24238,"approach_goal.arc_height":0.09426,"descend_grasp.descend_offset_z":0.01603,"descend_grasp.descend_speed":0.06858,"descend_place.descend_place_speed":0.08218,"grasp.grasp_duration":1.30163,"lift.lift_height":0.21008,"lift.lift_speed":0.15483,"release.release_duration":1.47147,"retract.retract_height":0.16605,"retract.retract_speed":0.13131},"optimized_scores":{"best_composite_score":-0.34255,"best_fitness_score":0.53745,"best_task_score":0.14034},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2893.0,"contact_point_centroid":[0.48736,-0.02981,-0.00237],"force_p95":0.12494,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.94464,"mean_force":0.13878,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.52361,0.03899,0.35362]},{"body_a":"world","body_b":"grasp_target","contact_count":120.0,"contact_point_centroid":[0.47436,-0.01924,-0.0011],"force_p95":0.2634,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.45295,"mean_force":0.04241,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46309,-0.01958,0.04513]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9889.0,"contact_point_centroid":[0.46848,-0.00061,0.11508],"force_p95":0.11425,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29519,"mean_force":0.071,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46527,-0.01956,0.11307]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11088.0,"contact_point_centroid":[0.46856,-0.03838,0.11686],"force_p95":0.1043,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2787,"mean_force":0.06499,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.4654,-0.01956,0.11515]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47616,-0.02008,-0.00204],"force_p95":0.13623,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17606,"mean_force":0.12633,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46532,-0.01964,0.04432]},{"body_a":"world","body_b":"grasp_target","contact_count":1008.0,"contact_point_centroid":[0.47616,-0.02015,-0.00187],"force_p95":0.13691,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12311,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.4883,-0.00801,0.25991]},{"body_a":"world","body_b":"grasp_target","contact_count":2220.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.47318,-0.01831,0.13385]},{"body_a":"world","body_b":"grasp_target","contact_count":1940.0,"contact_point_centroid":[0.48732,-0.02981,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.62217,0.15031,0.29216]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.48732,-0.02981,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.62288,0.15571,0.19811]},{"body_a":"world","body_b":"grasp_target","contact_count":2528.0,"contact_point_centroid":[0.48732,-0.02981,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.62386,0.15634,0.27347]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4839.0,"contact_point_centroid":[0.46426,-0.00039,0.04561],"force_p95":0.06764,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0986,"mean_force":0.04489,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46422,-0.01961,0.04322]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5146.0,"contact_point_centroid":[0.46412,-0.03883,0.04513],"force_p95":0.06636,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08262,"mean_force":0.04291,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46423,-0.01961,0.04322]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2874.0,"contact_point_centroid":[0.52805,0.04348,0.36323],"force_p95":0.0112,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01554,"mean_force":0.01056,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.52768,0.04348,0.36091]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2076.0,"contact_point_centroid":[0.62255,0.15033,0.29434],"force_p95":0.01098,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01283,"mean_force":0.01042,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.62217,0.15032,0.29206]},{"body_a":"left_finger","body_b":"right_finger","contact_count":220.0,"contact_point_centroid":[0.62557,0.15649,0.19689],"force_p95":0.01099,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.011,"mean_force":0.01013,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.62529,0.15647,0.19457]}],"total_contact_groups":15},"final_pose_error":0.0175,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.48732,-0.02981,0.01602],"final_tcp_position":[0.62934,0.15834,0.33871],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":9748.68629,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":253.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1008.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_pre_grasp","tcp_end":[0.47692,-0.01693,0.21825],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.19226,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":555.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2220.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_pre_grasp","tcp_end":[0.4719,-0.01979,0.05103],"tcp_start":[0.47692,-0.01693,0.21825],"tcp_to_object_dist_end":0.02537,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47607,-0.01973,0.02582],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28828,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.13464,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11785.0,"raw_peak_contact_force":0.17606,"tcp_end":[0.4642,-0.01961,0.04319],"tcp_start":[0.4719,-0.01979,0.05103],"tcp_to_object_dist_end":0.02104,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":722.0,"n_steps_budget":780.0,"object_pos_end":[0.4865,-0.02525,0.17035],"object_pos_start":[0.47607,-0.01973,0.02582],"object_to_goal_dist_end":0.23538,"object_to_goal_dist_start":0.28828,"object_z_max":0.1835,"peak_contact_force":0.0,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":21097.0,"raw_peak_contact_force":0.45295,"subtask_id":"lift_object","tcp_end":[0.47246,-0.01963,0.22102],"tcp_start":[0.4642,-0.01961,0.04319],"tcp_to_object_dist_end":0.05288,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":790.0,"n_steps_budget":1000.0,"object_pos_end":[0.48732,-0.02981,0.01602],"object_pos_start":[0.4865,-0.02525,0.17035],"object_to_goal_dist_end":0.29456,"object_to_goal_dist_start":0.23538,"object_z_max":0.17035,"peak_contact_force":0.12263,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":5767.0,"raw_peak_contact_force":1.94464,"subtask_id":"transport_goal","tcp_end":[0.61831,0.14432,0.38658],"tcp_start":[0.47246,-0.01963,0.22102],"tcp_to_object_dist_end":0.42988,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":485.0,"n_steps_budget":1000.0,"object_pos_end":[0.48732,-0.02981,0.01602],"object_pos_start":[0.48732,-0.02981,0.01602],"object_to_goal_dist_end":0.29456,"object_to_goal_dist_start":0.29456,"object_z_max":0.01602,"peak_contact_force":9748.68629,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4016.0,"raw_peak_contact_force":0.12263,"subtask_id":"transport_goal","tcp_end":[0.62696,0.15689,0.19859],"tcp_start":[0.61831,0.14432,0.38658],"tcp_to_object_dist_end":0.29613,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48732,-0.02981,0.01602],"object_pos_start":[0.48732,-0.02981,0.01602],"object_to_goal_dist_end":0.29456,"object_to_goal_dist_start":0.29456,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1020.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.62148,0.15525,0.2175],"tcp_start":[0.62696,0.15689,0.19859],"tcp_to_object_dist_end":0.3047,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":632.0,"n_steps_budget":690.0,"object_pos_end":[0.48732,-0.02981,0.01602],"object_pos_start":[0.48732,-0.02981,0.01602],"object_to_goal_dist_end":0.29456,"object_to_goal_dist_start":0.29456,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2528.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.62934,0.15834,0.33871],"tcp_start":[0.62148,0.15525,0.2175],"tcp_to_object_dist_end":0.39963,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.93293,"average_solve_count":164.0,"average_success_count":164.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_height":0.17416,"approach.approach_speed":0.23776,"approach_goal.approach_goal_height":0.13926,"approach_goal.approach_goal_speed":0.44273,"approach_goal.arc_height":0.0558,"descend_grasp.descend_offset_z":0.01597,"descend_grasp.descend_speed":0.14436,"descend_place.descend_place_speed":0.09782,"grasp.grasp_duration":1.23009,"lift.lift_height":0.20266,"lift.lift_speed":0.05094,"release.release_duration":0.51132,"retract.retract_height":0.17614,"retract.retract_speed":0.12271},"optimized_scores":{"best_composite_score":-0.15539,"best_fitness_score":0.72461,"best_task_score":0.51528},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1007.0,"contact_point_centroid":[0.64416,0.19966,-0.00321],"force_p95":0.60361,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.70291,"mean_force":0.17198,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.62069,0.20031,0.16803]},{"body_a":"world","body_b":"grasp_target","contact_count":161.0,"contact_point_centroid":[0.45585,-0.02545,-0.00117],"force_p95":0.3193,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.4387,"mean_force":0.07296,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.44583,-0.02554,0.04538]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7889.0,"contact_point_centroid":[0.51258,0.07186,0.21345],"force_p95":0.14491,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3379,"mean_force":0.08577,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.5085,0.05313,0.21412]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8996.0,"contact_point_centroid":[0.51641,0.03913,0.21531],"force_p95":0.12256,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33342,"mean_force":0.07579,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.51206,0.05771,0.21608]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":21820.0,"contact_point_centroid":[0.44623,-0.04465,0.09554],"force_p95":0.06958,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25866,"mean_force":0.04707,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.44656,-0.0255,0.09373]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20205.0,"contact_point_centroid":[0.44629,-0.0063,0.09489],"force_p95":0.07178,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24537,"mean_force":0.0502,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.44652,-0.0255,0.09289]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":55.0,"contact_point_centroid":[0.62162,0.17908,0.24254],"force_p95":0.12604,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20298,"mean_force":0.02542,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.61732,0.19429,0.24805]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45857,-0.02626,-0.00206],"force_p95":0.14061,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18969,"mean_force":0.12748,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.44821,-0.02563,0.04478]},{"body_a":"world","body_b":"grasp_target","contact_count":1128.0,"contact_point_centroid":[0.45856,-0.02632,-0.00188],"force_p95":0.13644,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12306,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.48083,-0.0107,0.25706]},{"body_a":"world","body_b":"grasp_target","contact_count":1944.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.45682,-0.02414,0.13122]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.64414,0.19974,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.61923,0.2032,0.12063]},{"body_a":"world","body_b":"grasp_target","contact_count":2888.0,"contact_point_centroid":[0.64414,0.19974,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.62026,0.20399,0.20168]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5315.0,"contact_point_centroid":[0.44656,-0.00633,0.04538],"force_p95":0.06532,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1044,"mean_force":0.04115,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.44715,-0.02559,0.04375]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5404.0,"contact_point_centroid":[0.44657,-0.04486,0.04527],"force_p95":0.06548,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07889,"mean_force":0.0411,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.44715,-0.02559,0.04376]},{"body_a":"left_finger","body_b":"right_finger","contact_count":844.0,"contact_point_centroid":[0.62179,0.20128,0.16026],"force_p95":0.01253,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0156,"mean_force":0.01077,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.62141,0.20127,0.15799]},{"body_a":"left_finger","body_b":"right_finger","contact_count":217.0,"contact_point_centroid":[0.62264,0.20437,0.11956],"force_p95":0.01101,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01272,"mean_force":0.01022,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.62233,0.20435,0.11728]}],"total_contact_groups":16},"final_pose_error":0.01759,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.64414,0.19974,0.01602],"final_tcp_position":[0.62712,0.20691,0.27298],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":1.70291,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":283.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1128.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_pre_grasp","tcp_end":[0.46135,-0.02256,0.21265],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.18669,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":486.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1944.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_pre_grasp","tcp_end":[0.4546,-0.02586,0.05103],"tcp_start":[0.46135,-0.02256,0.21265],"tcp_to_object_dist_end":0.02532,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":48.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45849,-0.02581,0.02577],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30337,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.13878,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12519.0,"raw_peak_contact_force":0.18969,"tcp_end":[0.44712,-0.02559,0.04373],"tcp_start":[0.4546,-0.02586,0.05103],"tcp_to_object_dist_end":0.02125,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.45458,-0.02558,0.11904],"object_pos_start":[0.45849,-0.02581,0.02577],"object_to_goal_dist_end":0.2924,"object_to_goal_dist_start":0.30337,"object_z_max":0.11896,"peak_contact_force":0.07156,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":42186.0,"raw_peak_contact_force":0.4387,"subtask_id":"lift_object","tcp_end":[0.44971,-0.02555,0.14313],"tcp_start":[0.44712,-0.02559,0.04373],"tcp_to_object_dist_end":0.02458,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":701.0,"n_steps_budget":1000.0,"object_pos_end":[0.62143,0.19078,0.20765],"object_pos_start":[0.45458,-0.02558,0.11904],"object_to_goal_dist_end":0.09553,"object_to_goal_dist_start":0.2924,"object_z_max":0.22376,"peak_contact_force":0.06978,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":16885.0,"raw_peak_contact_force":0.3379,"subtask_id":"transport_goal","tcp_end":[0.61732,0.19387,0.24877],"tcp_start":[0.44971,-0.02555,0.14313],"tcp_to_object_dist_end":0.04144,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":339.0,"n_steps_budget":1000.0,"object_pos_end":[0.64414,0.19974,0.01602],"object_pos_start":[0.62143,0.19078,0.20765],"object_to_goal_dist_end":0.09946,"object_to_goal_dist_start":0.09553,"object_z_max":0.20765,"peak_contact_force":0.12263,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1906.0,"raw_peak_contact_force":1.70291,"subtask_id":"transport_goal","tcp_end":[0.62433,0.20497,0.12129],"tcp_start":[0.61732,0.19387,0.24877],"tcp_to_object_dist_end":0.10724,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.64414,0.19974,0.01602],"object_pos_start":[0.64414,0.19974,0.01602],"object_to_goal_dist_end":0.09946,"object_to_goal_dist_start":0.09946,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1017.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.61737,0.20249,0.13993],"tcp_start":[0.62433,0.20497,0.12129],"tcp_to_object_dist_end":0.12679,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":722.0,"n_steps_budget":780.0,"object_pos_end":[0.64414,0.19974,0.01602],"object_pos_start":[0.64414,0.19974,0.01602],"object_to_goal_dist_end":0.09946,"object_to_goal_dist_start":0.09946,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2888.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.62712,0.20691,0.27298],"tcp_start":[0.61737,0.20249,0.13993],"tcp_to_object_dist_end":0.25762,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```