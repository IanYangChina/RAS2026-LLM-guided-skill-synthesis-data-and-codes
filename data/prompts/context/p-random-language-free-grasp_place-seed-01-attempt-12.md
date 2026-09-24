## Search State

- **Seed**: 1
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 14 | -0.2971 | 0.21 | ❌ rejected |
| 11 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 13 | -0.2110 | 0.29 | ❌ rejected |
| 10 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | impedance_control | impedance_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 14 | -0.2643 | 0.29 | ❌ rejected |
| 9 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 14 | -0.3089 | 0.19 | ❌ rejected |
| 8 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 13 | -0.2424 | 0.23 | ❌ rejected |

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

## Current Skill (Q=-0.297) — your mutation base

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

- **Composite score**: -0.297
- **task_score** (E): 0.212
- **fitness_score**: 0.583  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.880

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach | 1.00 | 1.00 | 0.1377 |
| descend_grasp | 1.00 | 1.00 | 0.1288 |
| grasp | 1.00 | 1.00 | 0.0111 |
| lift | 0.33 | 0.67 | 0.1365 |
| approach_goal | 0.00 | 1.00 | 0.0034 |
| descend_place | 1.00 | 1.00 | 0.1415 |
| release | 1.00 | 1.00 | 0.0204 |
| retract | 1.00 | 1.00 | 0.1227 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.477, -0.000, 0.169) | (0.479, -0.000, 0.030)→(0.479, -0.000, 0.026) | 0.276→0.278 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_grasp | descend | 1.00 / step_budget | (0.477, -0.000, 0.169)→(0.474, -0.000, 0.040) | (0.479, -0.000, 0.026)→(0.479, -0.000, 0.026) | 0.278→0.278 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp | grasp | 1.00 / step_budget | (0.474, -0.000, 0.040)→(0.466, -0.001, 0.032) | (0.479, -0.000, 0.026)→(0.479, -0.001, 0.026) | 0.278→0.278 | 1.00 / 44.000 | 0.143 | 0.206 |
| lift | lift | 0.33 / step_budget | (0.466, -0.001, 0.032)→(0.472, -0.001, 0.169) | (0.479, -0.001, 0.026)→(0.483, 0.004, 0.129) | 0.278→0.241 | 0.67 / 21.000 | 0.051 | 0.579 |
| approach_goal | approach | 0.00 / step_budget | (0.603, 0.198, 0.303)→(0.604, 0.199, 0.301) | (0.483, 0.004, 0.129)→(0.502, 0.043, 0.016) | 0.241→0.238 | 1.00 / 8.333 | 3249.669 | 1.909 |
| descend_place | descend | 1.00 / step_budget | (0.604, 0.199, 0.301)→(0.604, 0.202, 0.159) | (0.502, 0.043, 0.016)→(0.502, 0.043, 0.016) | 0.238→0.238 | 1.00 / 8.667 | 94251.862 | 0.123 |
| release | release | 1.00 / step_budget | (0.604, 0.202, 0.159)→(0.598, 0.200, 0.178) | (0.502, 0.043, 0.016)→(0.502, 0.043, 0.016) | 0.238→0.238 | 1.00 / 4.000 | 0.123 | 0.123 |
| retract | retract | 1.00 / step_budget | (0.598, 0.200, 0.178)→(0.606, 0.203, 0.301) | (0.502, 0.043, 0.016)→(0.502, 0.043, 0.016) | 0.238→0.238 | 1.00 / 4.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: 0.000
- terminal_score: 0.278
- phase_score: 0.080
- phase_breakdown.reach_pre_grasp_score: 0.177
- phase_breakdown.lift_object_score: 0.150
- phase_breakdown.transport_goal_score: 0.000
- grasp_place_fitness: 0.614

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.614
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.278
- **Median Q (composite search score)**: -0.297
- **K-run variance**: 0.0007
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.335


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.00541,"average_solve_count":185.0,"average_success_count":185.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_height":0.13749,"approach.approach_speed":0.13789,"approach_goal.approach_arc_height":0.15765,"approach_goal.approach_goal_height":0.13562,"approach_goal.approach_goal_speed":0.10425,"descend_grasp.descend_offset_z":0.00052,"descend_grasp.descend_speed":0.16626,"descend_place.descend_place_speed":0.14253,"grasp.grasp_duration":1.34535,"lift.lift_height":0.23319,"lift.lift_speed":0.11004,"release.release_duration":1.93755,"retract.retract_height":0.2074,"retract.retract_speed":0.20193},"optimized_scores":{"best_composite_score":-0.29703,"best_fitness_score":0.58297,"best_task_score":0.20739},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":7308.0,"contact_point_centroid":[0.49126,0.06257,-0.00212],"force_p95":0.12268,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.81309,"mean_force":0.12926,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.51413,0.10714,0.29549]},{"body_a":"world","body_b":"grasp_target","contact_count":151.0,"contact_point_centroid":[0.498,0.04225,-0.00131],"force_p95":0.44738,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.66918,"mean_force":0.08983,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.48673,0.04328,0.02816]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12849.0,"contact_point_centroid":[0.4915,0.06176,0.09569],"force_p95":0.13859,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31847,"mean_force":0.07621,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.48827,0.04307,0.09488]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12060.0,"contact_point_centroid":[0.49159,0.02437,0.09566],"force_p95":0.13453,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3102,"mean_force":0.07806,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.48823,0.04307,0.09451]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50124,0.04469,-0.00215],"force_p95":0.16586,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24935,"mean_force":0.1342,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.48932,0.04354,0.02771]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4049.0,"contact_point_centroid":[0.48868,0.02424,0.02931],"force_p95":0.08174,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15039,"mean_force":0.05191,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.48816,0.04344,0.02649]},{"body_a":"world","body_b":"grasp_target","contact_count":1572.0,"contact_point_centroid":[0.50118,0.04505,-0.00191],"force_p95":0.13468,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12294,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.49787,0.01951,0.23775]},{"body_a":"world","body_b":"grasp_target","contact_count":1608.0,"contact_point_centroid":[0.50118,0.04505,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.49564,0.04211,0.10452]},{"body_a":"world","body_b":"grasp_target","contact_count":1756.0,"contact_point_centroid":[0.4912,0.06259,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.55961,0.23953,0.24192]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.4912,0.06259,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.55609,0.24053,0.1563]},{"body_a":"world","body_b":"grasp_target","contact_count":2168.0,"contact_point_centroid":[0.4912,0.06259,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.55692,0.24099,0.25104]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5020.0,"contact_point_centroid":[0.48867,0.06262,0.02832],"force_p95":0.0743,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08998,"mean_force":0.04479,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.48816,0.04344,0.0265]},{"body_a":"left_finger","body_b":"right_finger","contact_count":7589.0,"contact_point_centroid":[0.51515,0.10907,0.30037],"force_p95":0.01102,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01655,"mean_force":0.01048,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.51478,0.10905,0.29809]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1870.0,"contact_point_centroid":[0.56017,0.23959,0.24377],"force_p95":0.011,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01268,"mean_force":0.01046,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.55961,0.23955,0.24146]},{"body_a":"left_finger","body_b":"right_finger","contact_count":224.0,"contact_point_centroid":[0.55943,0.24182,0.15454],"force_p95":0.01097,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01099,"mean_force":0.00999,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.55869,0.24177,0.15207]}],"total_contact_groups":15},"final_pose_error":0.01971,"key_states":{"actual_goal_position":[0.56442,0.24486,0.14677],"final_object_position":[0.4912,0.06259,0.01602],"final_tcp_position":[0.5625,0.24368,0.3346],"realised_goal_position":[0.56442,0.24486,0.14677],"realised_object_initial_position":[0.50118,0.04505,0.03]},"peak_contact_force":273006.60046,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":394.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.03],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.23992,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1572.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_pre_grasp","tcp_end":[0.49751,0.04026,0.17523],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.14933,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":402.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1608.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_pre_grasp","tcp_end":[0.49626,0.04417,0.03509],"tcp_start":[0.49751,0.04026,0.17523],"tcp_to_object_dist_end":0.01035,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50107,0.04344,0.02551],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24349,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.1563,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10869.0,"raw_peak_contact_force":0.24935,"tcp_end":[0.48813,0.04343,0.02646],"tcp_start":[0.49626,0.04417,0.03509],"tcp_to_object_dist_end":0.01298,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50311,0.05599,0.11699],"object_pos_start":[0.50107,0.04344,0.02551],"object_to_goal_dist_end":0.2008,"object_to_goal_dist_start":0.24349,"object_z_max":0.16779,"peak_contact_force":0.0,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":25060.0,"raw_peak_contact_force":0.66918,"subtask_id":"lift_object","tcp_end":[0.49479,0.04313,0.20184],"tcp_start":[0.48813,0.04343,0.02646],"tcp_to_object_dist_end":0.08623,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1866.0,"n_steps_budget":1000.0,"object_pos_end":[0.4912,0.06259,0.01602],"object_pos_start":[0.50311,0.05599,0.11699],"object_to_goal_dist_end":0.23597,"object_to_goal_dist_start":0.2008,"object_z_max":0.11699,"peak_contact_force":0.12263,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":14897.0,"raw_peak_contact_force":1.81309,"subtask_id":"transport_goal","tcp_end":[0.55993,0.23733,0.3284],"tcp_start":[0.55991,0.23616,0.33075],"tcp_to_object_dist_end":0.36447,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":439.0,"n_steps_budget":1000.0,"object_pos_end":[0.4912,0.06259,0.01602],"object_pos_start":[0.4912,0.06259,0.01602],"object_to_goal_dist_end":0.23597,"object_to_goal_dist_start":0.23597,"object_z_max":0.01602,"peak_contact_force":273006.60046,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3626.0,"raw_peak_contact_force":0.12263,"subtask_id":"transport_goal","tcp_end":[0.56044,0.24252,0.15558],"tcp_start":[0.55993,0.23733,0.3284],"tcp_to_object_dist_end":0.23801,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.4912,0.06259,0.01602],"object_pos_start":[0.4912,0.06259,0.01602],"object_to_goal_dist_end":0.23597,"object_to_goal_dist_start":0.23597,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1024.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.55456,0.23978,0.17622],"tcp_start":[0.56044,0.24252,0.15558],"tcp_to_object_dist_end":0.24713,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":542.0,"n_steps_budget":600.0,"object_pos_end":[0.4912,0.06259,0.01602],"object_pos_start":[0.4912,0.06259,0.01602],"object_to_goal_dist_end":0.23597,"object_to_goal_dist_start":0.23597,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2168.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.5625,0.24368,0.3346],"tcp_start":[0.55456,0.23978,0.17622],"tcp_to_object_dist_end":0.37333,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.0289,"average_solve_count":173.0,"average_success_count":173.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_height":0.17895,"approach.approach_speed":0.30825,"approach_goal.approach_arc_height":0.18177,"approach_goal.approach_goal_height":0.12918,"approach_goal.approach_goal_speed":0.22219,"descend_grasp.descend_offset_z":0.00703,"descend_grasp.descend_speed":0.13671,"descend_place.descend_place_speed":0.14617,"grasp.grasp_duration":1.14966,"lift.lift_height":0.15753,"lift.lift_speed":0.16831,"release.release_duration":0.96489,"retract.retract_height":0.14289,"retract.retract_speed":0.19978},"optimized_scores":{"best_composite_score":-0.3284,"best_fitness_score":0.5516,"best_task_score":0.14936},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":6475.0,"contact_point_centroid":[0.48057,-0.00905,-0.00215],"force_p95":0.12318,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.79093,"mean_force":0.13022,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.54034,0.05935,0.33431]},{"body_a":"world","body_b":"grasp_target","contact_count":116.0,"contact_point_centroid":[0.47425,-0.01917,-0.0011],"force_p95":0.3764,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.56769,"mean_force":0.04837,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46303,-0.01961,0.03596]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8183.0,"contact_point_centroid":[0.46788,-0.00064,0.09227],"force_p95":0.10747,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30695,"mean_force":0.06767,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46534,-0.01957,0.09013]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1359.0,"contact_point_centroid":[0.47393,-0.00334,0.17838],"force_p95":0.17893,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30455,"mean_force":0.10069,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.46773,-0.02177,0.1794]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1281.0,"contact_point_centroid":[0.47374,-0.04029,0.17882],"force_p95":0.18285,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29058,"mean_force":0.1063,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.46764,-0.02183,0.17962]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8610.0,"contact_point_centroid":[0.46762,-0.03848,0.09096],"force_p95":0.10497,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28844,"mean_force":0.06492,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46526,-0.01957,0.08908]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47616,-0.02006,-0.00204],"force_p95":0.13608,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17631,"mean_force":0.12637,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46521,-0.01966,0.03518]},{"body_a":"world","body_b":"grasp_target","contact_count":1008.0,"contact_point_centroid":[0.47616,-0.02015,-0.00187],"force_p95":0.13691,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12311,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.48832,-0.008,0.2599]},{"body_a":"world","body_b":"grasp_target","contact_count":2156.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.47319,-0.01831,0.12911]},{"body_a":"world","body_b":"grasp_target","contact_count":1544.0,"contact_point_centroid":[0.48056,-0.00906,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.62669,0.15594,0.28115]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.48056,-0.00906,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.62363,0.15653,0.19858]},{"body_a":"world","body_b":"grasp_target","contact_count":2168.0,"contact_point_centroid":[0.48056,-0.00906,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.62411,0.15674,0.26243]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5072.0,"contact_point_centroid":[0.46378,-0.00041,0.03665],"force_p95":0.06575,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09836,"mean_force":0.04287,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.4641,-0.01963,0.03408]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5151.0,"contact_point_centroid":[0.46402,-0.03888,0.03606],"force_p95":0.06642,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08598,"mean_force":0.04301,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.4641,-0.01963,0.03408]},{"body_a":"left_finger","body_b":"right_finger","contact_count":6658.0,"contact_point_centroid":[0.54365,0.0626,0.34068],"force_p95":0.01101,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01579,"mean_force":0.0105,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.54329,0.0626,0.33841]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1641.0,"contact_point_centroid":[0.62718,0.15597,0.28308],"force_p95":0.01097,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01282,"mean_force":0.01049,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.62669,0.15595,0.28086]}],"total_contact_groups":17},"final_pose_error":0.01726,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.48056,-0.00906,0.01602],"final_tcp_position":[0.62898,0.15829,0.31585],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":9748.86177,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":253.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1008.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_pre_grasp","tcp_end":[0.47693,-0.01691,0.21816],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.19217,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":539.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2156.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_pre_grasp","tcp_end":[0.47184,-0.01981,0.04184],"tcp_start":[0.47693,-0.01691,0.21816],"tcp_to_object_dist_end":0.0164,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":46.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47605,-0.01971,0.02583],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28828,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.13438,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12023.0,"raw_peak_contact_force":0.17631,"tcp_end":[0.46407,-0.01963,0.03405],"tcp_start":[0.47184,-0.01981,0.04184],"tcp_to_object_dist_end":0.01453,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":24.0,"n_steps":542.0,"n_steps_budget":600.0,"object_pos_end":[0.48891,-0.01965,0.15059],"object_pos_start":[0.47605,-0.01971,0.02583],"object_to_goal_dist_end":0.23206,"object_to_goal_dist_start":0.28828,"object_z_max":0.15041,"peak_contact_force":0.07469,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":16909.0,"raw_peak_contact_force":0.56769,"subtask_id":"lift_object","tcp_end":[0.47186,-0.0196,0.16853],"tcp_start":[0.46407,-0.01963,0.03405],"tcp_to_object_dist_end":0.02475,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1844.0,"n_steps_budget":1000.0,"object_pos_end":[0.48056,-0.00906,0.01602],"object_pos_start":[0.48891,-0.01965,0.15059],"object_to_goal_dist_end":0.28521,"object_to_goal_dist_start":0.23206,"object_z_max":0.17288,"peak_contact_force":0.12263,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":15773.0,"raw_peak_contact_force":1.79093,"subtask_id":"transport_goal","tcp_end":[0.6264,0.15459,0.36192],"tcp_start":[0.62518,0.15299,0.36452],"tcp_to_object_dist_end":0.40951,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":386.0,"n_steps_budget":1000.0,"object_pos_end":[0.48056,-0.00906,0.01602],"object_pos_start":[0.48056,-0.00906,0.01602],"object_to_goal_dist_end":0.28521,"object_to_goal_dist_start":0.28521,"object_z_max":0.01602,"peak_contact_force":9748.86177,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3185.0,"raw_peak_contact_force":0.12263,"subtask_id":"transport_goal","tcp_end":[0.62771,0.15774,0.19916],"tcp_start":[0.6264,0.15459,0.36192],"tcp_to_object_dist_end":0.28813,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48056,-0.00906,0.01602],"object_pos_start":[0.48056,-0.00906,0.01602],"object_to_goal_dist_end":0.28521,"object_to_goal_dist_start":0.28521,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1022.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.62224,0.15607,0.21794],"tcp_start":[0.62771,0.15774,0.19916],"tcp_to_object_dist_end":0.29684,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":542.0,"n_steps_budget":600.0,"object_pos_end":[0.48056,-0.00906,0.01602],"object_pos_start":[0.48056,-0.00906,0.01602],"object_to_goal_dist_end":0.28521,"object_to_goal_dist_start":0.28521,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2168.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.62898,0.15829,0.31585],"tcp_start":[0.62224,0.15607,0.21794],"tcp_to_object_dist_end":0.37407,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.70652,"average_solve_count":184.0,"average_success_count":184.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_height":0.07378,"approach.approach_speed":0.30168,"approach_goal.approach_arc_height":0.22625,"approach_goal.approach_goal_height":0.05702,"approach_goal.approach_goal_speed":0.25465,"descend_grasp.descend_offset_z":0.00861,"descend_grasp.descend_speed":0.14658,"descend_place.descend_place_speed":0.09317,"grasp.grasp_duration":1.53694,"lift.lift_height":0.18006,"lift.lift_speed":0.05128,"release.release_duration":0.99858,"retract.retract_height":0.15628,"retract.retract_speed":0.24976},"optimized_scores":{"best_composite_score":-0.26589,"best_fitness_score":0.61411,"best_task_score":0.27806},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":5238.0,"contact_point_centroid":[0.53354,0.07441,-0.00221],"force_p95":0.12367,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.12218,"mean_force":0.13257,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.58971,0.1598,0.22891]},{"body_a":"world","body_b":"grasp_target","contact_count":162.0,"contact_point_centroid":[0.45588,-0.0252,-0.00117],"force_p95":0.36386,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.49871,"mean_force":0.08024,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.44554,-0.02549,0.03803]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8223.0,"contact_point_centroid":[0.47116,0.01951,0.18288],"force_p95":0.11542,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.36428,"mean_force":0.0682,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.46756,0.00092,0.18212]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6898.0,"contact_point_centroid":[0.4695,-0.01943,0.18145],"force_p95":0.14274,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3409,"mean_force":0.07963,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.46642,-0.00054,0.1803]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20883.0,"contact_point_centroid":[0.44635,-0.0446,0.08785],"force_p95":0.07075,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2726,"mean_force":0.04886,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.4466,-0.02543,0.08618]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":21027.0,"contact_point_centroid":[0.44642,-0.00626,0.0895],"force_p95":0.07083,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26654,"mean_force":0.04814,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.44669,-0.02543,0.08753]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45857,-0.0262,-0.00206],"force_p95":0.14206,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19348,"mean_force":0.12781,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.44791,-0.02558,0.03741]},{"body_a":"world","body_b":"grasp_target","contact_count":1956.0,"contact_point_centroid":[0.45856,-0.02632,-0.00193],"force_p95":0.13308,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12288,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.4783,-0.01191,0.20655]},{"body_a":"world","body_b":"grasp_target","contact_count":932.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.455,-0.02497,0.07846]},{"body_a":"world","body_b":"grasp_target","contact_count":912.0,"contact_point_centroid":[0.53351,0.07442,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.62495,0.20614,0.16759]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.53351,0.07442,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.62016,0.20456,0.12169]},{"body_a":"world","body_b":"grasp_target","contact_count":2168.0,"contact_point_centroid":[0.53351,0.07442,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.62065,0.20468,0.19182]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4826.0,"contact_point_centroid":[0.44684,-0.00633,0.0387],"force_p95":0.06858,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10239,"mean_force":0.04489,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.44685,-0.02554,0.03639]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5172.0,"contact_point_centroid":[0.4467,-0.04477,0.0382],"force_p95":0.06735,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07425,"mean_force":0.04292,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.44685,-0.02554,0.03639]},{"body_a":"left_finger","body_b":"right_finger","contact_count":5423.0,"contact_point_centroid":[0.59255,0.16302,0.23072],"force_p95":0.011,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01566,"mean_force":0.01044,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.59217,0.16301,0.22838]},{"body_a":"left_finger","body_b":"right_finger","contact_count":966.0,"contact_point_centroid":[0.62552,0.20617,0.16992],"force_p95":0.011,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01275,"mean_force":0.01052,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.62495,0.20614,0.16771]}],"total_contact_groups":17},"final_pose_error":0.01873,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.53351,0.07442,0.01602],"final_tcp_position":[0.62675,0.20685,0.25203],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":9749.04135,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":490.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1956.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_pre_grasp","tcp_end":[0.45776,-0.02425,0.11333],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.08734,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":233.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":932.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_pre_grasp","tcp_end":[0.45436,-0.02581,0.04363],"tcp_start":[0.45776,-0.02425,0.11333],"tcp_to_object_dist_end":0.01811,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45847,-0.02568,0.02576],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30328,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.13927,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11798.0,"raw_peak_contact_force":0.19348,"tcp_end":[0.44682,-0.02554,0.03636],"tcp_start":[0.45436,-0.02581,0.04363],"tcp_to_object_dist_end":0.01575,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":39.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.4567,-0.02554,0.11805],"object_pos_start":[0.45847,-0.02568,0.02576],"object_to_goal_dist_end":0.2911,"object_to_goal_dist_start":0.30328,"object_z_max":0.11797,"peak_contact_force":0.07701,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":42072.0,"raw_peak_contact_force":0.49871,"subtask_id":"lift_object","tcp_end":[0.45008,-0.02546,0.13548],"tcp_start":[0.44682,-0.02554,0.03636],"tcp_to_object_dist_end":0.01865,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1988.0,"n_steps_budget":1000.0,"object_pos_end":[0.53351,0.07442,0.01602],"object_pos_start":[0.4567,-0.02554,0.11805],"object_to_goal_dist_end":0.19199,"object_to_goal_dist_start":0.2911,"object_z_max":0.20694,"peak_contact_force":9748.76227,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":25782.0,"raw_peak_contact_force":2.12218,"subtask_id":"transport_goal","tcp_end":[0.62625,0.20652,0.2114],"tcp_start":[0.62431,0.20389,0.21426],"tcp_to_object_dist_end":0.25342,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":228.0,"n_steps_budget":1000.0,"object_pos_end":[0.53351,0.07442,0.01602],"object_pos_start":[0.53351,0.07442,0.01602],"object_to_goal_dist_end":0.19199,"object_to_goal_dist_start":0.19199,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1878.0,"raw_peak_contact_force":0.12263,"subtask_id":"transport_goal","tcp_end":[0.62527,0.20641,0.12251],"tcp_start":[0.62625,0.20652,0.2114],"tcp_to_object_dist_end":0.19282,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53351,0.07442,0.01602],"object_pos_start":[0.53351,0.07442,0.01602],"object_to_goal_dist_end":0.19199,"object_to_goal_dist_start":0.19199,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1019.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.61831,0.20385,0.14094],"tcp_start":[0.62527,0.20641,0.12251],"tcp_to_object_dist_end":0.19887,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":542.0,"n_steps_budget":600.0,"object_pos_end":[0.53351,0.07442,0.01602],"object_pos_start":[0.53351,0.07442,0.01602],"object_to_goal_dist_end":0.19199,"object_to_goal_dist_start":0.19199,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2168.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.62675,0.20685,0.25203],"tcp_start":[0.61831,0.20385,0.14094],"tcp_to_object_dist_end":0.28623,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```