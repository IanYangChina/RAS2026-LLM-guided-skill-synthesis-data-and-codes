## Search State

- **Seed**: 1
- **Iteration**: 15 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 14 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 13 | -0.1846 | 0.34 | ✅ accepted |
| 13 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 13 | -0.5557 | 0.16 | ❌ rejected |
| 12 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 14 | -0.2971 | 0.21 | ❌ rejected |
| 11 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 13 | -0.2110 | 0.29 | ❌ rejected |
| 10 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | impedance_control | impedance_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 14 | -0.2643 | 0.29 | ❌ rejected |

**Proposal policy**: task_score is 0.34 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.185) — your mutation base

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
    anchor: current_tcp
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
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.15]
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
    - lift_speed: status=consumed; consumers=generator.speed (replace)
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

- **Composite score**: -0.185
- **task_score** (E): 0.338
- **fitness_score**: 0.645  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.830

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach | 1.00 | 1.00 | 0.1445 |
| descend_grasp | 1.00 | 1.00 | 0.1278 |
| grasp | 1.00 | 1.00 | 0.0112 |
| lift | 1.00 | 1.00 | 0.1022 |
| approach_goal | 0.67 | 1.00 | 0.2649 |
| descend_place | 1.00 | 1.00 | 0.1066 |
| release | 1.00 | 1.00 | 0.0207 |
| retract | 1.00 | 1.00 | 0.1314 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.477, -0.000, 0.162) | (0.479, -0.000, 0.030)→(0.479, -0.000, 0.026) | 0.276→0.278 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_grasp | descend | 1.00 / step_budget | (0.477, -0.000, 0.162)→(0.474, -0.001, 0.034) | (0.479, -0.000, 0.026)→(0.479, -0.000, 0.026) | 0.278→0.278 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp | grasp | 1.00 / step_budget | (0.474, -0.001, 0.034)→(0.466, -0.001, 0.026) | (0.479, -0.000, 0.026)→(0.478, -0.001, 0.026) | 0.278→0.278 | 1.00 / 45.000 | 0.143 | 0.209 |
| lift | lift | 1.00 / step_budget | (0.466, -0.001, 0.026)→(0.462, -0.001, 0.128) | (0.478, -0.001, 0.026)→(0.480, -0.001, 0.117) | 0.278→0.250 | 1.00 / 25.667 | 0.108 | 0.749 |
| approach_goal | approach | 0.67 / step_budget | (0.462, -0.001, 0.128)→(0.587, 0.176, 0.256) | (0.480, -0.001, 0.117)→(0.539, 0.121, 0.054) | 0.250→0.155 | 1.00 / 10.667 | 91002.760 | 1.249 |
| descend_place | descend | 1.00 / step_budget | (0.587, 0.176, 0.256)→(0.602, 0.199, 0.154) | (0.539, 0.121, 0.054)→(0.547, 0.130, 0.016) | 0.155→0.174 | 1.00 / 8.333 | 91002.821 | 0.496 |
| release | release | 1.00 / step_budget | (0.602, 0.199, 0.154)→(0.596, 0.197, 0.174) | (0.547, 0.130, 0.016)→(0.547, 0.130, 0.016) | 0.174→0.174 | 1.00 / 4.000 | 0.123 | 0.123 |
| retract | retract | 1.00 / step_budget | (0.596, 0.197, 0.174)→(0.606, 0.203, 0.305) | (0.547, 0.130, 0.016)→(0.547, 0.130, 0.016) | 0.174→0.174 | 1.00 / 4.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: 1.000
- terminal_score: 0.520
- phase_score: 0.084
- phase_breakdown.reach_pre_grasp_score: 0.183
- phase_breakdown.lift_object_score: 0.157
- phase_breakdown.transport_goal_score: 0.000
- grasp_place_fitness: 0.733

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.733
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.520
- **Median Q (composite search score)**: -0.204
- **K-run variance**: 0.0043
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.339


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.1,"average_solve_count":150.0,"average_success_count":150.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_height":0.12064,"approach.approach_speed":0.29088,"approach_goal.approach_goal_height":0.19252,"approach_goal.approach_goal_speed":0.36014,"descend_grasp.descend_offset_z":-0.00249,"descend_grasp.descend_speed":0.09814,"descend_place.descend_place_speed":0.13365,"grasp.grasp_duration":1.04108,"lift.lift_height":0.13914,"lift.lift_speed":0.06344,"release.release_duration":0.51719,"retract.retract_height":0.15519,"retract.retract_speed":0.1523},"optimized_scores":{"best_composite_score":-0.20446,"best_fitness_score":0.62554,"best_task_score":0.29285},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2311.0,"contact_point_centroid":[0.50727,0.12836,-0.00241],"force_p95":0.14615,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.79947,"mean_force":0.14363,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.53059,0.16591,0.25094]},{"body_a":"world","body_b":"grasp_target","contact_count":179.0,"contact_point_centroid":[0.49767,0.04244,-0.00123],"force_p95":0.52183,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.73446,"mean_force":0.10542,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.4864,0.04326,0.02546]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17389.0,"contact_point_centroid":[0.48556,0.06205,0.07396],"force_p95":0.08788,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32478,"mean_force":0.05945,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.48388,0.04304,0.0724]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4325.0,"contact_point_centroid":[0.4944,0.08544,0.14843],"force_p95":0.16064,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31311,"mean_force":0.0817,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.49075,0.06715,0.14961]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17008.0,"contact_point_centroid":[0.48556,0.02405,0.07581],"force_p95":0.08885,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30854,"mean_force":0.06002,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.48386,0.04304,0.07405]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3363.0,"contact_point_centroid":[0.49365,0.04694,0.1467],"force_p95":0.16912,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28274,"mean_force":0.09396,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.49015,0.06562,0.14807]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50124,0.04465,-0.00215],"force_p95":0.16703,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.25978,"mean_force":0.13459,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.48931,0.04354,0.02482]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4040.0,"contact_point_centroid":[0.48868,0.02423,0.02641],"force_p95":0.08187,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14521,"mean_force":0.05194,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.48814,0.04343,0.0236]},{"body_a":"world","body_b":"grasp_target","contact_count":1644.0,"contact_point_centroid":[0.50118,0.04505,-0.00192],"force_p95":0.13462,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12292,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.4978,0.01983,0.22927]},{"body_a":"world","body_b":"grasp_target","contact_count":1596.0,"contact_point_centroid":[0.50118,0.04505,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.49551,0.04229,0.09487]},{"body_a":"world","body_b":"grasp_target","contact_count":1656.0,"contact_point_centroid":[0.5071,0.12845,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.55472,0.22802,0.22882]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.5071,0.12845,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.55517,0.23859,0.15512]},{"body_a":"world","body_b":"grasp_target","contact_count":2168.0,"contact_point_centroid":[0.5071,0.12845,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.55594,0.2398,0.22594]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5021.0,"contact_point_centroid":[0.48866,0.06262,0.02542],"force_p95":0.0743,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09179,"mean_force":0.04488,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.48815,0.04343,0.02361]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2259.0,"contact_point_centroid":[0.53282,0.17035,0.25772],"force_p95":0.01117,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01637,"mean_force":0.01051,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.53241,0.17033,0.25551]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1773.0,"contact_point_centroid":[0.55517,0.22794,0.23173],"force_p95":0.011,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01281,"mean_force":0.01041,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.55468,0.22791,0.22948]}],"total_contact_groups":17},"final_pose_error":0.01725,"key_states":{"actual_goal_position":[0.56442,0.24486,0.14677],"final_object_position":[0.5071,0.12845,0.01602],"final_tcp_position":[0.56148,0.24323,0.28505],"realised_goal_position":[0.56442,0.24486,0.14677],"realised_object_initial_position":[0.50118,0.04505,0.03]},"peak_contact_force":273008.33796,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":412.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.03],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.23992,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1644.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_pre_grasp","tcp_end":[0.49738,0.04065,0.15872],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13283,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":399.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1596.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_pre_grasp","tcp_end":[0.49629,0.04418,0.03221],"tcp_start":[0.49738,0.04065,0.15872],"tcp_to_object_dist_end":0.00794,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50106,0.04338,0.02551],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24355,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.15682,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10861.0,"raw_peak_contact_force":0.25978,"tcp_end":[0.48812,0.04343,0.02357],"tcp_start":[0.49629,0.04418,0.03221],"tcp_to_object_dist_end":0.01308,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":31.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49839,0.043,0.11738],"object_pos_start":[0.50106,0.04338,0.02551],"object_to_goal_dist_end":0.21441,"object_to_goal_dist_start":0.24355,"object_z_max":0.11726,"peak_contact_force":0.09149,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":34576.0,"raw_peak_contact_force":0.73446,"subtask_id":"lift_object","tcp_end":[0.48392,0.04305,0.12835],"tcp_start":[0.48812,0.04343,0.02357],"tcp_to_object_dist_end":0.01817,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5071,0.12845,0.01602],"object_pos_start":[0.49839,0.043,0.11738],"object_to_goal_dist_end":0.18422,"object_to_goal_dist_start":0.21441,"object_z_max":0.15943,"peak_contact_force":0.12263,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":12258.0,"raw_peak_contact_force":1.79947,"subtask_id":"transport_goal","tcp_end":[0.55158,0.21699,0.30356],"tcp_start":[0.48392,0.04305,0.12835],"tcp_to_object_dist_end":0.30413,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":414.0,"n_steps_budget":1000.0,"object_pos_end":[0.5071,0.12845,0.01602],"object_pos_start":[0.5071,0.12845,0.01602],"object_to_goal_dist_end":0.18422,"object_to_goal_dist_start":0.18422,"object_z_max":0.01602,"peak_contact_force":273008.33796,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3429.0,"raw_peak_contact_force":0.12263,"subtask_id":"transport_goal","tcp_end":[0.55955,0.2405,0.1543],"tcp_start":[0.55158,0.21699,0.30356],"tcp_to_object_dist_end":0.18555,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5071,0.12845,0.01602],"object_pos_start":[0.5071,0.12845,0.01602],"object_to_goal_dist_end":0.18422,"object_to_goal_dist_start":0.18422,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1019.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.55362,0.23784,0.17506],"tcp_start":[0.55955,0.2405,0.1543],"tcp_to_object_dist_end":0.19856,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":542.0,"n_steps_budget":600.0,"object_pos_end":[0.5071,0.12845,0.01602],"object_pos_start":[0.5071,0.12845,0.01602],"object_to_goal_dist_end":0.18422,"object_to_goal_dist_start":0.18422,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2168.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.56148,0.24323,0.28505],"tcp_start":[0.55362,0.23784,0.17506],"tcp_to_object_dist_end":0.2975,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.25758,"average_solve_count":132.0,"average_success_count":132.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_height":0.13103,"approach.approach_speed":0.27573,"approach_goal.approach_goal_height":0.14683,"approach_goal.approach_goal_speed":0.3554,"descend_grasp.descend_offset_z":-0.00946,"descend_grasp.descend_speed":0.10435,"descend_place.descend_place_speed":0.12236,"grasp.grasp_duration":1.30353,"lift.lift_height":0.11329,"lift.lift_speed":0.19632,"release.release_duration":1.60181,"retract.retract_height":0.15923,"retract.retract_speed":0.12482},"optimized_scores":{"best_composite_score":-0.25262,"best_fitness_score":0.57738,"best_task_score":0.20131},"replay_outcomes":[{"contacts":{"omitted_contact_groups":3,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2637.0,"contact_point_centroid":[0.50071,0.05571,-0.00238],"force_p95":0.1851,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.57724,"mean_force":0.14654,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.55562,0.08265,0.23699]},{"body_a":"world","body_b":"grasp_target","contact_count":138.0,"contact_point_centroid":[0.4733,-0.01967,-0.00124],"force_p95":0.77713,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.94938,"mean_force":0.14202,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46233,-0.01965,0.01903]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2437.0,"contact_point_centroid":[0.47698,0.01375,0.13224],"force_p95":0.20531,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.40345,"mean_force":0.10846,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.47187,-0.00429,0.13331]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1850.0,"contact_point_centroid":[0.47551,-0.02463,0.13091],"force_p95":0.22855,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.35277,"mean_force":0.11984,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.47019,-0.00615,0.13122]},{"body_a":"grasp_target","body_b":"hand","contact_count":111.0,"contact_point_centroid":[0.47864,-0.03854,0.06304],"force_p95":0.08224,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34247,"mean_force":0.0457,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46089,-0.01962,0.02514]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8265.0,"contact_point_centroid":[0.46195,-0.00058,0.06275],"force_p95":0.10829,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29503,"mean_force":0.06659,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.45993,-0.01958,0.0605]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9111.0,"contact_point_centroid":[0.46197,-0.03848,0.06121],"force_p95":0.10443,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28278,"mean_force":0.06163,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.45992,-0.01958,0.05956]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47612,-0.01994,-0.00206],"force_p95":0.13596,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17505,"mean_force":0.12796,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46491,-0.01971,0.01862]},{"body_a":"world","body_b":"grasp_target","contact_count":1440.0,"contact_point_centroid":[0.47616,-0.02015,-0.00191],"force_p95":0.13514,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12297,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.48717,-0.00865,0.23595]},{"body_a":"world","body_b":"grasp_target","contact_count":1856.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.47212,-0.01885,0.09707]},{"body_a":"world","body_b":"grasp_target","contact_count":1192.0,"contact_point_centroid":[0.50095,0.05666,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.61437,0.14406,0.24738]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.50095,0.05666,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.62061,0.15383,0.19565]},{"body_a":"world","body_b":"grasp_target","contact_count":2528.0,"contact_point_centroid":[0.50095,0.05666,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.62255,0.15533,0.26903]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5398.0,"contact_point_centroid":[0.46338,-0.03895,0.01975],"force_p95":0.06382,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08843,"mean_force":0.04139,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46378,-0.01969,0.01753]},{"body_a":"grasp_target","body_b":"hand","contact_count":317.0,"contact_point_centroid":[0.48131,-0.03918,0.05558],"force_p95":0.03094,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08736,"mean_force":0.01589,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46387,-0.01969,0.01761]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5049.0,"contact_point_centroid":[0.46354,-0.00045,0.0203],"force_p95":0.06561,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08137,"mean_force":0.04276,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46378,-0.01969,0.01753]}],"total_contact_groups":19},"final_pose_error":0.01729,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.50095,0.05666,0.01602],"final_tcp_position":[0.62909,0.15822,0.33215],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":273007.96991,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":361.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1440.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_pre_grasp","tcp_end":[0.47519,-0.01794,0.17049],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.14449,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":464.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1856.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_pre_grasp","tcp_end":[0.47167,-0.01986,0.02524],"tcp_start":[0.47519,-0.01794,0.17049],"tcp_to_object_dist_end":0.00457,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":48.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47587,-0.0197,0.02576],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28841,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.13474,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12564.0,"raw_peak_contact_force":0.17505,"tcp_end":[0.46375,-0.01968,0.0175],"tcp_start":[0.47167,-0.01986,0.02524],"tcp_to_object_dist_end":0.01466,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":534.0,"n_steps_budget":600.0,"object_pos_end":[0.48171,-0.01942,0.11498],"object_pos_start":[0.47587,-0.0197,0.02576],"object_to_goal_dist_end":0.24484,"object_to_goal_dist_start":0.28841,"object_z_max":0.11486,"peak_contact_force":0.11943,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":17625.0,"raw_peak_contact_force":0.94938,"subtask_id":"lift_object","tcp_end":[0.4599,-0.01957,0.11825],"tcp_start":[0.46375,-0.01968,0.0175],"tcp_to_object_dist_end":0.02205,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50095,0.05666,0.01602],"object_pos_start":[0.48171,-0.01942,0.11498],"object_to_goal_dist_end":0.24044,"object_to_goal_dist_start":0.24484,"object_z_max":0.13192,"peak_contact_force":273007.96991,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":9641.0,"raw_peak_contact_force":1.57724,"subtask_id":"transport_goal","tcp_end":[0.60619,0.13452,0.29916],"tcp_start":[0.4599,-0.01957,0.11825],"tcp_to_object_dist_end":0.31194,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":7.0,"n_steps":298.0,"n_steps_budget":1000.0,"object_pos_end":[0.50095,0.05666,0.01602],"object_pos_start":[0.50095,0.05666,0.01602],"object_to_goal_dist_end":0.24044,"object_to_goal_dist_start":0.24044,"object_z_max":0.01602,"peak_contact_force":0.0,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2469.0,"raw_peak_contact_force":0.12263,"subtask_id":"transport_goal","tcp_end":[0.62469,0.1549,0.19598],"tcp_start":[0.60619,0.13452,0.29916],"tcp_to_object_dist_end":0.23947,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50095,0.05666,0.01602],"object_pos_start":[0.50095,0.05666,0.01602],"object_to_goal_dist_end":0.24044,"object_to_goal_dist_start":0.24044,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1020.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.61917,0.15337,0.21506],"tcp_start":[0.62469,0.1549,0.19598],"tcp_to_object_dist_end":0.25089,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":632.0,"n_steps_budget":690.0,"object_pos_end":[0.50095,0.05666,0.01602],"object_pos_start":[0.50095,0.05666,0.01602],"object_to_goal_dist_end":0.24044,"object_to_goal_dist_start":0.24044,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2528.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.62909,0.15822,0.33215],"tcp_start":[0.61917,0.15337,0.21506],"tcp_to_object_dist_end":0.35591,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.22901,"average_solve_count":131.0,"average_success_count":131.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_height":0.11711,"approach.approach_speed":0.41787,"approach_goal.approach_goal_height":0.0639,"approach_goal.approach_goal_speed":0.39652,"descend_grasp.descend_offset_z":0.01025,"descend_grasp.descend_speed":0.0975,"descend_place.descend_place_speed":0.05412,"grasp.grasp_duration":0.72634,"lift.lift_height":0.1131,"lift.lift_speed":0.18238,"release.release_duration":1.6943,"retract.retract_height":0.20362,"retract.retract_speed":0.21521},"optimized_scores":{"best_composite_score":-0.09667,"best_fitness_score":0.73333,"best_task_score":0.51964},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":521.0,"contact_point_centroid":[0.63249,0.20569,-0.0034],"force_p95":0.64469,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.24385,"mean_force":0.19241,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.61744,0.19737,0.12088]},{"body_a":"world","body_b":"grasp_target","contact_count":129.0,"contact_point_centroid":[0.45587,-0.02519,-0.00123],"force_p95":0.34279,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.56416,"mean_force":0.08805,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.44563,-0.02555,0.0395]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":768.0,"contact_point_centroid":[0.60993,0.19962,0.14822],"force_p95":0.16789,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.49623,"mean_force":0.11104,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.60524,0.18208,0.15212]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10972.0,"contact_point_centroid":[0.52219,0.05107,0.14993],"force_p95":0.13732,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.37035,"mean_force":0.08742,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.51635,0.06975,0.14918]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":625.0,"contact_point_centroid":[0.61115,0.16356,0.14972],"force_p95":0.18353,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.36459,"mean_force":0.13103,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.60493,0.18163,0.15322]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8575.0,"contact_point_centroid":[0.44509,-0.00643,0.08304],"force_p95":0.10294,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32053,"mean_force":0.06358,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.44335,-0.02545,0.08077]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9223.0,"contact_point_centroid":[0.4451,-0.0444,0.08182],"force_p95":0.10036,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30546,"mean_force":0.06007,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.44333,-0.02545,0.08015]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12574.0,"contact_point_centroid":[0.52343,0.09079,0.14985],"force_p95":0.11792,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27938,"mean_force":0.07643,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.51839,0.07232,0.14952]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45857,-0.02621,-0.00206],"force_p95":0.14055,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19113,"mean_force":0.12741,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.44804,-0.02564,0.03904]},{"body_a":"world","body_b":"grasp_target","contact_count":1588.0,"contact_point_centroid":[0.45856,-0.02632,-0.00191],"force_p95":0.13466,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12293,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.47917,-0.01151,0.22871]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.63342,0.20551,-0.00199],"force_p95":0.123,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12352,"mean_force":0.12265,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.61716,0.20117,0.11137]},{"body_a":"world","body_b":"grasp_target","contact_count":1452.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.45548,-0.02473,0.10048]},{"body_a":"world","body_b":"grasp_target","contact_count":2168.0,"contact_point_centroid":[0.63342,0.20551,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.61938,0.20298,0.20864]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4832.0,"contact_point_centroid":[0.44694,-0.00636,0.04027],"force_p95":0.06832,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10279,"mean_force":0.04491,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.44697,-0.0256,0.03802]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5410.0,"contact_point_centroid":[0.44642,-0.04483,0.03968],"force_p95":0.0653,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07578,"mean_force":0.04109,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.44697,-0.0256,0.03802]},{"body_a":"left_finger","body_b":"right_finger","contact_count":202.0,"contact_point_centroid":[0.62087,0.20091,0.11721],"force_p95":0.01501,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01635,"mean_force":0.01171,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.62051,0.20089,0.1148]}],"total_contact_groups":17},"final_pose_error":0.02157,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.63342,0.20551,0.01602],"final_tcp_position":[0.62748,0.20692,0.29637],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":1.24385,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":398.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1588.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_pre_grasp","tcp_end":[0.45892,-0.02372,0.15656],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13057,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":363.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1452.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_pre_grasp","tcp_end":[0.45447,-0.02587,0.04526],"tcp_start":[0.45892,-0.02372,0.15656],"tcp_to_object_dist_end":0.01968,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":46.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45847,-0.02571,0.02578],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.3033,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.13791,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12042.0,"raw_peak_contact_force":0.19113,"tcp_end":[0.44694,-0.0256,0.03799],"tcp_start":[0.45447,-0.02587,0.04526],"tcp_to_object_dist_end":0.0168,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":532.0,"n_steps_budget":600.0,"object_pos_end":[0.45857,-0.02542,0.11835],"object_pos_start":[0.45847,-0.02571,0.02578],"object_to_goal_dist_end":0.28989,"object_to_goal_dist_start":0.3033,"object_z_max":0.11822,"peak_contact_force":0.11246,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":17927.0,"raw_peak_contact_force":0.56416,"subtask_id":"lift_object","tcp_end":[0.44331,-0.02544,0.13881],"tcp_start":[0.44694,-0.0256,0.03799],"tcp_to_object_dist_end":0.02552,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":15.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.60758,0.17876,0.13041],"object_pos_start":[0.45857,-0.02542,0.11835],"object_to_goal_dist_end":0.04052,"object_to_goal_dist_start":0.28989,"object_z_max":0.13041,"peak_contact_force":0.18824,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":23546.0,"raw_peak_contact_force":0.37035,"subtask_id":"transport_goal","tcp_end":[0.60289,0.17764,0.16456],"tcp_start":[0.44331,-0.02544,0.13881],"tcp_to_object_dist_end":0.0345,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":284.0,"n_steps_budget":1000.0,"object_pos_end":[0.63343,0.20554,0.01601],"object_pos_start":[0.60758,0.17876,0.13041],"object_to_goal_dist_end":0.0982,"object_to_goal_dist_start":0.04052,"object_z_max":0.13041,"peak_contact_force":0.12354,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2116.0,"raw_peak_contact_force":1.24385,"subtask_id":"transport_goal","tcp_end":[0.62217,0.20282,0.11148],"tcp_start":[0.60289,0.17764,0.16456],"tcp_to_object_dist_end":0.09617,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.63342,0.20551,0.01602],"object_pos_start":[0.63343,0.20554,0.01601],"object_to_goal_dist_end":0.09819,"object_to_goal_dist_start":0.0982,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1019.0,"raw_peak_contact_force":0.12352,"tcp_end":[0.61522,0.20045,0.13066],"tcp_start":[0.62217,0.20282,0.11148],"tcp_to_object_dist_end":0.11619,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":542.0,"n_steps_budget":600.0,"object_pos_end":[0.63342,0.20551,0.01602],"object_pos_start":[0.63342,0.20551,0.01602],"object_to_goal_dist_end":0.09819,"object_to_goal_dist_start":0.09819,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2168.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.62748,0.20692,0.29637],"tcp_start":[0.61522,0.20045,0.13066],"tcp_to_object_dist_end":0.28042,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```