## Search State

- **Seed**: 1
- **Iteration**: 9 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 8 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 13 | -0.2424 | 0.23 | ❌ rejected |
| 7 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 13 | -0.2208 | 0.27 | ❌ rejected |
| 6 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 11 | -0.1690 | 0.21 | ❌ rejected |
| 5 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 13 | -0.1904 | 0.33 | ✅ accepted |
| 4 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 13 | -0.3458 | 0.16 | ❌ rejected |

**Proposal policy**: task_score is 0.23 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.242) — your mutation base

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

- **Composite score**: -0.242
- **task_score** (E): 0.230
- **fitness_score**: 0.588  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.830

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach | 1.00 | 1.00 | 0.1472 |
| descend_grasp | 1.00 | 1.00 | 0.1136 |
| grasp | 1.00 | 1.00 | 0.0111 |
| lift | 1.00 | 1.00 | 0.1166 |
| approach_goal | 0.33 | 1.00 | 0.2010 |
| descend_place | 1.00 | 1.00 | 0.1031 |
| release | 1.00 | 1.00 | 0.0215 |
| retract | 1.00 | 1.00 | 0.1869 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.477, -0.001, 0.159) | (0.479, -0.000, 0.030)→(0.479, -0.000, 0.026) | 0.276→0.278 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_grasp | descend | 1.00 / step_budget | (0.477, -0.001, 0.159)→(0.474, -0.000, 0.046) | (0.479, -0.000, 0.026)→(0.479, -0.000, 0.026) | 0.278→0.278 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp | grasp | 1.00 / step_budget | (0.474, -0.000, 0.046)→(0.466, -0.001, 0.038) | (0.479, -0.000, 0.026)→(0.479, -0.001, 0.026) | 0.278→0.278 | 1.00 / 44.333 | 0.143 | 0.202 |
| lift | lift | 1.00 / step_budget | (0.466, -0.001, 0.038)→(0.470, -0.001, 0.154) | (0.479, -0.001, 0.026)→(0.477, -0.000, 0.128) | 0.278→0.250 | 1.00 / 20.333 | 0.120 | 0.527 |
| approach_goal | approach | 0.33 / step_budget | (0.470, -0.001, 0.154)→(0.565, 0.151, 0.234) | (0.477, -0.000, 0.128)→(0.511, 0.068, 0.016) | 0.250→0.221 | 1.00 / 8.667 | 0.123 | 1.467 |
| descend_place | descend | 1.00 / step_budget | (0.565, 0.151, 0.234)→(0.592, 0.190, 0.149) | (0.511, 0.068, 0.016)→(0.511, 0.068, 0.016) | 0.221→0.221 | 1.00 / 8.000 | 0.123 | 0.123 |
| release | release | 1.00 / step_budget | (0.592, 0.190, 0.149)→(0.586, 0.188, 0.169) | (0.511, 0.068, 0.016)→(0.511, 0.068, 0.016) | 0.221→0.221 | 1.00 / 4.000 | 0.123 | 0.123 |
| retract | retract | 1.00 / step_budget | (0.586, 0.188, 0.169)→(0.606, 0.203, 0.354) | (0.511, 0.068, 0.016)→(0.511, 0.068, 0.016) | 0.221→0.221 | 1.00 / 4.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: 0.000
- terminal_score: 0.246
- phase_score: 0.089
- phase_breakdown.reach_pre_grasp_score: 0.170
- phase_breakdown.lift_object_score: 0.182
- phase_breakdown.transport_goal_score: 0.000
- grasp_place_fitness: 0.599

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.599
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.246
- **Median Q (composite search score)**: -0.244
- **K-run variance**: 0.0001
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.317


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.97386,"average_solve_count":153.0,"average_success_count":153.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_height":0.15234,"approach.approach_speed":0.14069,"approach_goal.approach_goal_height":0.07669,"approach_goal.approach_goal_speed":0.3208,"descend_grasp.descend_offset_z":0.00708,"descend_grasp.descend_speed":0.08102,"descend_place.descend_place_speed":0.06803,"grasp.grasp_duration":1.16918,"lift.lift_height":0.13984,"lift.lift_speed":0.22616,"release.release_duration":1.33888,"retract.retract_height":0.19609,"retract.retract_speed":0.11011},"optimized_scores":{"best_composite_score":-0.2308,"best_fitness_score":0.5992,"best_task_score":0.24567},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":5031.0,"contact_point_centroid":[0.51176,0.08832,-0.00216],"force_p95":0.12377,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.39758,"mean_force":0.13207,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.53375,0.16946,0.18606]},{"body_a":"world","body_b":"grasp_target","contact_count":151.0,"contact_point_centroid":[0.49962,0.04292,-0.00123],"force_p95":0.37812,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.60717,"mean_force":0.06874,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.48694,0.04327,0.03485]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11793.0,"contact_point_centroid":[0.49459,0.02435,0.10514],"force_p95":0.12827,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3403,"mean_force":0.07778,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49083,0.04306,0.10382]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12285.0,"contact_point_centroid":[0.49432,0.06177,0.10281],"force_p95":0.11764,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32996,"mean_force":0.07579,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49063,0.04306,0.10174]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50124,0.04476,-0.00214],"force_p95":0.16429,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.23937,"mean_force":0.13362,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.48938,0.04353,0.0342]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":358.0,"contact_point_centroid":[0.49767,0.03032,0.14076],"force_p95":0.2079,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23774,"mean_force":0.1526,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.49293,0.04818,0.14538]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":511.0,"contact_point_centroid":[0.4981,0.06705,0.14069],"force_p95":0.14432,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21015,"mean_force":0.10367,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.49321,0.04977,0.14559]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4066.0,"contact_point_centroid":[0.48872,0.02422,0.0358],"force_p95":0.08152,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15296,"mean_force":0.05185,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.48823,0.04342,0.03298]},{"body_a":"world","body_b":"grasp_target","contact_count":1412.0,"contact_point_centroid":[0.50118,0.04505,-0.0019],"force_p95":0.1356,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12297,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.49796,0.01916,0.24523]},{"body_a":"world","body_b":"grasp_target","contact_count":1896.0,"contact_point_centroid":[0.50118,0.04505,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.49569,0.04182,0.1152]},{"body_a":"world","body_b":"grasp_target","contact_count":2352.0,"contact_point_centroid":[0.51179,0.08843,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.55386,0.23403,0.15315]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.51179,0.08843,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.5496,0.23455,0.14384]},{"body_a":"world","body_b":"grasp_target","contact_count":3756.0,"contact_point_centroid":[0.51179,0.08843,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.55337,0.23791,0.24321]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5016.0,"contact_point_centroid":[0.48872,0.0626,0.0348],"force_p95":0.07434,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08486,"mean_force":0.04462,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.48823,0.04342,0.03299]},{"body_a":"left_finger","body_b":"right_finger","contact_count":5055.0,"contact_point_centroid":[0.536,0.17442,0.19006],"force_p95":0.01105,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01649,"mean_force":0.01056,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.5355,0.1744,0.18782]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2498.0,"contact_point_centroid":[0.55442,0.2341,0.15529],"force_p95":0.01098,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01268,"mean_force":0.01049,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.55387,0.23405,0.1531]}],"total_contact_groups":17},"final_pose_error":0.01558,"key_states":{"actual_goal_position":[0.56442,0.24486,0.14677],"final_object_position":[0.51179,0.08843,0.01602],"final_tcp_position":[0.5621,0.24345,0.32753],"realised_goal_position":[0.56442,0.24486,0.14677],"realised_object_initial_position":[0.50118,0.04505,0.03]},"peak_contact_force":1.39758,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":354.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.03],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.23992,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1412.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_pre_grasp","tcp_end":[0.49764,0.03972,0.19002],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16413,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":474.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1896.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_pre_grasp","tcp_end":[0.4963,0.04416,0.04162],"tcp_start":[0.49764,0.03972,0.19002],"tcp_to_object_dist_end":0.01637,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50111,0.04356,0.02552],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24338,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.15574,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10882.0,"raw_peak_contact_force":0.23937,"tcp_end":[0.4882,0.04342,0.03295],"tcp_start":[0.4963,0.04416,0.04162],"tcp_to_object_dist_end":0.0149,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":15.0,"n_steps":542.0,"n_steps_budget":600.0,"object_pos_end":[0.49871,0.04339,0.12086],"object_pos_start":[0.50111,0.04356,0.02552],"object_to_goal_dist_end":0.2135,"object_to_goal_dist_start":0.24338,"object_z_max":0.13387,"peak_contact_force":0.14093,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":24229.0,"raw_peak_contact_force":0.60717,"subtask_id":"lift_object","tcp_end":[0.49246,0.04286,0.14535],"tcp_start":[0.4882,0.04342,0.03295],"tcp_to_object_dist_end":0.02528,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51179,0.08843,0.01602],"object_pos_start":[0.49871,0.04339,0.12086],"object_to_goal_dist_end":0.21057,"object_to_goal_dist_start":0.2135,"object_z_max":0.12086,"peak_contact_force":0.12263,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":10955.0,"raw_peak_contact_force":1.39758,"subtask_id":"transport_goal","tcp_end":[0.55016,0.22024,0.20002],"tcp_start":[0.49246,0.04286,0.14535],"tcp_to_object_dist_end":0.22957,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":188.0,"n_steps_budget":1000.0,"object_pos_end":[0.51179,0.08843,0.01602],"object_pos_start":[0.51179,0.08843,0.01602],"object_to_goal_dist_end":0.21057,"object_to_goal_dist_start":0.21057,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4850.0,"raw_peak_contact_force":0.12263,"subtask_id":"transport_goal","tcp_end":[0.55379,0.23643,0.14232],"tcp_start":[0.55016,0.22024,0.20002],"tcp_to_object_dist_end":0.19904,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51179,0.08843,0.01602],"object_pos_start":[0.51179,0.08843,0.01602],"object_to_goal_dist_end":0.21057,"object_to_goal_dist_start":0.21057,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1025.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.54796,0.23378,0.16377],"tcp_start":[0.55379,0.23643,0.14232],"tcp_to_object_dist_end":0.21039,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":939.0,"n_steps_budget":1000.0,"object_pos_end":[0.51179,0.08843,0.01602],"object_pos_start":[0.51179,0.08843,0.01602],"object_to_goal_dist_end":0.21057,"object_to_goal_dist_start":0.21057,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3756.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.5621,0.24345,0.32753],"tcp_start":[0.54796,0.23378,0.16377],"tcp_to_object_dist_end":0.35157,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.48879,"average_solve_count":223.0,"average_success_count":223.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_height":0.10538,"approach.approach_speed":0.28754,"approach_goal.approach_goal_height":0.15227,"approach_goal.approach_goal_speed":0.35546,"descend_grasp.descend_offset_z":0.01159,"descend_grasp.descend_speed":0.02075,"descend_place.descend_place_speed":0.07458,"grasp.grasp_duration":1.31886,"lift.lift_height":0.15042,"lift.lift_speed":0.25855,"release.release_duration":1.55362,"retract.retract_height":0.25521,"retract.retract_speed":0.19115},"optimized_scores":{"best_composite_score":-0.25267,"best_fitness_score":0.57733,"best_task_score":0.21007},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":4466.0,"contact_point_centroid":[0.51134,0.05758,-0.00229],"force_p95":0.20507,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.4878,"mean_force":0.13949,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.57332,0.0985,0.26998]},{"body_a":"world","body_b":"grasp_target","contact_count":128.0,"contact_point_centroid":[0.47437,-0.01926,-0.00108],"force_p95":0.31689,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.52181,"mean_force":0.04995,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46275,-0.01959,0.04037]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":940.0,"contact_point_centroid":[0.47819,-0.02993,0.15746],"force_p95":0.18829,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32144,"mean_force":0.11586,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.47271,-0.01189,0.16181]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12449.0,"contact_point_centroid":[0.47004,-0.00076,0.11517],"force_p95":0.11483,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3113,"mean_force":0.07423,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46629,-0.01954,0.11359]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13096.0,"contact_point_centroid":[0.46979,-0.03829,0.11327],"force_p95":0.1078,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2947,"mean_force":0.07132,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.4662,-0.01954,0.11204]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1085.0,"contact_point_centroid":[0.47939,0.00737,0.15866],"force_p95":0.18989,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24632,"mean_force":0.11577,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.47391,-0.01041,0.1631]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47616,-0.02006,-0.00204],"force_p95":0.13593,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17606,"mean_force":0.12625,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46498,-0.01965,0.03966]},{"body_a":"world","body_b":"grasp_target","contact_count":1668.0,"contact_point_centroid":[0.47616,-0.02015,-0.00192],"force_p95":0.13444,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12292,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.4867,-0.00889,0.22274]},{"body_a":"world","body_b":"grasp_target","contact_count":1464.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.47166,-0.01898,0.09558]},{"body_a":"world","body_b":"grasp_target","contact_count":2872.0,"contact_point_centroid":[0.51134,0.05877,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.61803,0.14955,0.21451]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.51134,0.05877,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.61696,0.15276,0.18729]},{"body_a":"world","body_b":"grasp_target","contact_count":3008.0,"contact_point_centroid":[0.51134,0.05877,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.62158,0.15499,0.31095]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5076.0,"contact_point_centroid":[0.46363,-0.00038,0.04133],"force_p95":0.06586,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09742,"mean_force":0.04292,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46388,-0.01962,0.03856]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5392.0,"contact_point_centroid":[0.4635,-0.03888,0.04082],"force_p95":0.06485,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0844,"mean_force":0.04114,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46388,-0.01962,0.03856]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4844.0,"contact_point_centroid":[0.5728,0.0976,0.27141],"force_p95":0.011,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01605,"mean_force":0.01049,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.57248,0.09759,0.26909]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3042.0,"contact_point_centroid":[0.61855,0.1496,0.21662],"force_p95":0.01099,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01282,"mean_force":0.01051,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.61805,0.14958,0.21439]}],"total_contact_groups":17},"final_pose_error":0.02016,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.51134,0.05877,0.01602],"final_tcp_position":[0.63104,0.15871,0.42507],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":1.4878,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":418.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1668.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_pre_grasp","tcp_end":[0.47456,-0.01827,0.14485],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11886,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":366.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1464.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_pre_grasp","tcp_end":[0.47158,-0.0198,0.04631],"tcp_start":[0.47456,-0.01827,0.14485],"tcp_to_object_dist_end":0.02081,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":47.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47606,-0.01971,0.02583],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28827,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.13433,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12268.0,"raw_peak_contact_force":0.17606,"tcp_end":[0.46385,-0.01962,0.03853],"tcp_start":[0.47158,-0.0198,0.04631],"tcp_to_object_dist_end":0.01762,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":20.0,"n_steps":542.0,"n_steps_budget":600.0,"object_pos_end":[0.47411,-0.01943,0.1298],"object_pos_start":[0.47606,-0.01971,0.02583],"object_to_goal_dist_end":0.24551,"object_to_goal_dist_start":0.28827,"object_z_max":0.14047,"peak_contact_force":0.12853,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":25673.0,"raw_peak_contact_force":0.52181,"subtask_id":"lift_object","tcp_end":[0.46784,-0.01949,0.15686],"tcp_start":[0.46385,-0.01962,0.03853],"tcp_to_object_dist_end":0.02777,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51134,0.05877,0.01602],"object_pos_start":[0.47411,-0.01943,0.1298],"object_to_goal_dist_end":0.23405,"object_to_goal_dist_start":0.24551,"object_z_max":0.14056,"peak_contact_force":0.12263,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":11335.0,"raw_peak_contact_force":1.4878,"subtask_id":"transport_goal","tcp_end":[0.60545,0.1343,0.30097],"tcp_start":[0.46784,-0.01949,0.15686],"tcp_to_object_dist_end":0.30945,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":318.0,"n_steps_budget":1000.0,"object_pos_end":[0.51134,0.05877,0.01602],"object_pos_start":[0.51134,0.05877,0.01602],"object_to_goal_dist_end":0.23405,"object_to_goal_dist_start":0.23405,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5914.0,"raw_peak_contact_force":0.12263,"subtask_id":"transport_goal","tcp_end":[0.62088,0.15389,0.18694],"tcp_start":[0.60545,0.1343,0.30097],"tcp_to_object_dist_end":0.22419,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51134,0.05877,0.01602],"object_pos_start":[0.51134,0.05877,0.01602],"object_to_goal_dist_end":0.23405,"object_to_goal_dist_start":0.23405,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1021.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.61546,0.15229,0.20665],"tcp_start":[0.62088,0.15389,0.18694],"tcp_to_object_dist_end":0.23649,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":752.0,"n_steps_budget":810.0,"object_pos_end":[0.51134,0.05877,0.01602],"object_pos_start":[0.51134,0.05877,0.01602],"object_to_goal_dist_end":0.23405,"object_to_goal_dist_start":0.23405,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3008.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.63104,0.15871,0.42507],"tcp_start":[0.61546,0.15229,0.20665],"tcp_to_object_dist_end":0.43777,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.7177,"average_solve_count":209.0,"average_success_count":209.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_height":0.10347,"approach.approach_speed":0.11116,"approach_goal.approach_goal_height":0.147,"approach_goal.approach_goal_speed":0.19298,"descend_grasp.descend_offset_z":0.0144,"descend_grasp.descend_speed":0.07504,"descend_place.descend_place_speed":0.03118,"grasp.grasp_duration":0.5724,"lift.lift_height":0.15416,"lift.lift_speed":0.17508,"release.release_duration":1.33545,"retract.retract_height":0.21698,"retract.retract_speed":0.26785},"optimized_scores":{"best_composite_score":-0.24378,"best_fitness_score":0.58622,"best_task_score":0.23514},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":3909.0,"contact_point_centroid":[0.51031,0.05484,-0.00229],"force_p95":0.17014,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.51509,"mean_force":0.13959,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.52607,0.07826,0.19731]},{"body_a":"world","body_b":"grasp_target","contact_count":130.0,"contact_point_centroid":[0.45727,-0.02509,-0.00109],"force_p95":0.27186,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.45056,"mean_force":0.04076,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.44582,-0.02552,0.04422]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2584.0,"contact_point_centroid":[0.46968,0.01386,0.16328],"force_p95":0.13471,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28919,"mean_force":0.10092,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.46387,-0.00432,0.16626]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":13639.0,"contact_point_centroid":[0.45321,-0.00659,0.12268],"force_p95":0.09947,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28757,"mean_force":0.06838,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.4493,-0.02548,0.12086]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14428.0,"contact_point_centroid":[0.45303,-0.04432,0.12069],"force_p95":0.095,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27174,"mean_force":0.06546,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.4492,-0.02548,0.11926]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2609.0,"contact_point_centroid":[0.46832,-0.02437,0.1626],"force_p95":0.16022,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26431,"mean_force":0.09983,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.46251,-0.00622,0.1656]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45858,-0.02624,-0.00206],"force_p95":0.14128,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19085,"mean_force":0.12762,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.44795,-0.02561,0.04321]},{"body_a":"world","body_b":"grasp_target","contact_count":1900.0,"contact_point_centroid":[0.45856,-0.02632,-0.00193],"force_p95":0.13354,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12288,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.47885,-0.01164,0.22179]},{"body_a":"world","body_b":"grasp_target","contact_count":1252.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.45527,-0.02481,0.09599]},{"body_a":"world","body_b":"grasp_target","contact_count":5600.0,"contact_point_centroid":[0.51052,0.05584,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.58204,0.15451,0.14564]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.51052,0.05584,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.59556,0.1785,0.11807]},{"body_a":"world","body_b":"grasp_target","contact_count":2172.0,"contact_point_centroid":[0.51052,0.05584,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.60801,0.1909,0.2188]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4834.0,"contact_point_centroid":[0.44688,-0.00635,0.04447],"force_p95":0.06852,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10335,"mean_force":0.04489,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.44689,-0.02557,0.04219]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5161.0,"contact_point_centroid":[0.44673,-0.04479,0.04398],"force_p95":0.06728,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07929,"mean_force":0.0429,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.44689,-0.02557,0.0422]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4095.0,"contact_point_centroid":[0.52705,0.07905,0.19988],"force_p95":0.01104,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01644,"mean_force":0.01055,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.52668,0.07905,0.19763]},{"body_a":"left_finger","body_b":"right_finger","contact_count":5948.0,"contact_point_centroid":[0.58266,0.15464,0.1478],"force_p95":0.011,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01288,"mean_force":0.01049,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.58212,0.15462,0.14555]}],"total_contact_groups":17},"final_pose_error":0.02231,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.51052,0.05584,0.01602],"final_tcp_position":[0.62637,0.20555,0.30928],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":1.51509,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":476.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1900.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_pre_grasp","tcp_end":[0.45856,-0.02391,0.14306],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11706,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":313.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1252.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_pre_grasp","tcp_end":[0.45435,-0.02584,0.04945],"tcp_start":[0.45856,-0.02391,0.14306],"tcp_to_object_dist_end":0.02381,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45848,-0.02575,0.02577],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30333,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.13881,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11795.0,"raw_peak_contact_force":0.19085,"tcp_end":[0.44686,-0.02556,0.04217],"tcp_start":[0.45435,-0.02584,0.04945],"tcp_to_object_dist_end":0.0201,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":26.0,"n_steps":542.0,"n_steps_budget":600.0,"object_pos_end":[0.45897,-0.02542,0.13247],"object_pos_start":[0.45848,-0.02575,0.02577],"object_to_goal_dist_end":0.2902,"object_to_goal_dist_start":0.30333,"object_z_max":0.14148,"peak_contact_force":0.09026,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":28197.0,"raw_peak_contact_force":0.45056,"subtask_id":"lift_object","tcp_end":[0.4505,-0.02542,0.16111],"tcp_start":[0.44686,-0.02556,0.04217],"tcp_to_object_dist_end":0.02988,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51052,0.05584,0.01602],"object_pos_start":[0.45897,-0.02542,0.13247],"object_to_goal_dist_end":0.21713,"object_to_goal_dist_start":0.2902,"object_z_max":0.1399,"peak_contact_force":0.12263,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":13197.0,"raw_peak_contact_force":1.51509,"subtask_id":"transport_goal","tcp_end":[0.53921,0.09772,0.20126],"tcp_start":[0.4505,-0.02542,0.16111],"tcp_to_object_dist_end":0.19207,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51052,0.05584,0.01602],"object_pos_start":[0.51052,0.05584,0.01602],"object_to_goal_dist_end":0.21713,"object_to_goal_dist_start":0.21713,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":11548.0,"raw_peak_contact_force":0.12263,"subtask_id":"transport_goal","tcp_end":[0.60034,0.18004,0.11724],"tcp_start":[0.53921,0.09772,0.20126],"tcp_to_object_dist_end":0.18368,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51052,0.05584,0.01602],"object_pos_start":[0.51052,0.05584,0.01602],"object_to_goal_dist_end":0.21713,"object_to_goal_dist_start":0.21713,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1024.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.59366,0.17787,0.13768],"tcp_start":[0.60034,0.18004,0.11724],"tcp_to_object_dist_end":0.19132,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":543.0,"n_steps_budget":600.0,"object_pos_end":[0.51052,0.05584,0.01602],"object_pos_start":[0.51052,0.05584,0.01602],"object_to_goal_dist_end":0.21713,"object_to_goal_dist_start":0.21713,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2172.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.62637,0.20555,0.30928],"tcp_start":[0.59366,0.17787,0.13768],"tcp_to_object_dist_end":0.34904,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```