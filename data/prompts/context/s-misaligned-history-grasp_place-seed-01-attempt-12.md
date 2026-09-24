## Search State

- **Seed**: 1
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | approach → align → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | impedance_control | impedance_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 9  | -0.0818 | 0.17 | ❌ rejected |
| 11 | approach → align → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | impedance_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 9  | -0.3114 | 0.18 | ❌ rejected |
| 10 | approach → align → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 12  | -0.0511 | 0.31 | ❌ rejected |
| 9 | approach → align → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 11  | -0.1265 | 0.41 | ✅ accepted |
| 8 | approach → align → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | impedance_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 9  | -0.0337 | 0.27 | ❌ rejected |

**Proposal policy**: task_score is 0.27 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.034) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
subtasks:
- id: reach_object
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.05
  weight: 0.3
- id: place_goal
  target_entity: object
  metric: goal_progress
  weight: 0.7
phases:
- id: approach_object
  type: approach
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
    - 0.1
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_object
- id: align_grasp
  type: align
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
    tolerance: 0.005
    orientation:
      mode: keep_current
  parameters:
    lateral_offset_x:
      type: scalar
      range:
      - -0.01
      - 0.01
      default: 0.0
      binds_to:
      - path: target.offset.x
        mode: add
    lateral_offset_y:
      type: scalar
      range:
      - -0.01
      - 0.01
      default: 0.0
      binds_to:
      - path: target.offset.y
        mode: add
  subtask_id: reach_object
- id: grasp
  type: grasp
  control: position_control
  termination: grasp_success
  end_effector_action: force_grasp
  target:
    source: yaml
    anchor: task_object
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.0
    orientation:
      mode: keep_current
  guards:
  - id: bilateral_grasp_check
    when: after_phase
    predicate: bilateral_grasp
    threshold: 1.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: repeat
- id: lift
  type: lift
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  end_effector_action: close
  target:
    source: yaml
    anchor: task_object
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.12
      axis: world_z
      mode: add_to_offset
      sign: positive
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.15
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    lift_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
- id: approach_goal
  type: approach
  generator: arc_cartesian
  control: impedance_control
  termination: pose_tolerance
  end_effector_action: force_grasp
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.1
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    arc_height:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.05
      binds_to:
      - path: generator.arc_height
        mode: replace
    transport_speed:
      type: scalar
      range:
      - 0.05
      - 0.25
      default: 0.15
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: object_dropped_guard
    when: during_phase
    predicate: contact_detected
    threshold: 0.5
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: reduce_speed
    offset:
    - 0.0
    - 0.0
    - 0.0
  subtask_id: place_goal
- id: descend_place
  type: descend
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    descend_speed:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: place_goal
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
    orientation:
      mode: keep_current
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
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.1
    tolerance: 0.01
    orientation:
      mode: keep_current

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_object** (`approach`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.1], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **align_grasp** (`align`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.03], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings:
    - lateral_offset_x: status=consumed; consumers=target.offset.x (add)
    - lateral_offset_y: status=consumed; consumers=target.offset.y (add)
- **grasp** (`grasp`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings: none
  - guards:
    - id=bilateral_grasp_check, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=1.0
  - retries: max_attempts=2, strategy=repeat
- **lift** (`lift`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.12, mode=add_to_offset, sign=positive}, tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - lift_speed: status=consumed; consumers=generator.speed (replace)
- **approach_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.1], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - arc_height: status=consumed; consumers=generator.arc_height (replace)
    - transport_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=object_dropped_guard, when=during_phase, predicate=contact_detected, on_failure=retry, threshold=0.5
  - retries: max_attempts=2, strategy=reduce_speed, offset=[0.0, 0.0, 0.0]
- **descend_place** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (replace)
- **release** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - release_duration: status=consumed; consumers=duration.max_time (replace)
- **retract** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.1], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings: none

## Design Metrics

- **Composite score**: -0.034
- **task_score** (E): 0.270
- **fitness_score**: 0.596  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.630

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1668 |
| align_grasp | 1.00 | 1.00 | 0.0822 |
| grasp | 1.00 | 1.00 | 0.0109 |
| lift | 1.00 | 1.00 | 0.1165 |
| approach_goal | 1.00 | 1.00 | 0.2328 |
| descend_place | 1.00 | 1.00 | 0.0765 |
| release | 1.00 | 1.00 | 0.0198 |
| retract | 1.00 | 1.00 | 0.0851 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.477, -0.000, 0.139) | (0.479, -0.000, 0.030)→(0.479, -0.000, 0.026) | 0.276→0.278 | 1.00 / 4.000 | 12.685 | 0.138 |
| align_grasp | align | 1.00 / step_budget | (0.477, -0.000, 0.139)→(0.479, -0.002, 0.057) | (0.479, -0.000, 0.026)→(0.479, -0.000, 0.026) | 0.278→0.278 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp | grasp | 1.00 / step_budget | (0.479, -0.002, 0.057)→(0.471, -0.002, 0.049) | (0.479, -0.000, 0.026)→(0.479, -0.002, 0.025) | 0.278→0.279 | 1.00 / 40.000 | 0.175 | 0.225 |
| lift | lift | 1.00 / step_budget | (0.473, -0.001, 0.127)→(0.475, 0.004, 0.184) | (0.479, -0.002, 0.025)→(0.475, -0.001, 0.138) | 0.279→0.252 | 1.00 / 20.333 | 0.113 | 0.755 |
| approach_goal | approach | 1.00 / step_budget | (0.475, 0.004, 0.184)→(0.594, 0.187, 0.243) | (0.480, 0.004, 0.102)→(0.519, 0.100, 0.016) | 0.262→0.209 | 1.00 / 8.333 | 0.123 | 1.283 |
| descend_place | descend | 1.00 / step_budget | (0.594, 0.187, 0.243)→(0.602, 0.198, 0.168) | (0.519, 0.100, 0.016)→(0.519, 0.100, 0.016) | 0.209→0.209 | 1.00 / 7.667 | 9748.819 | 0.123 |
| release | release | 1.00 / step_budget | (0.602, 0.198, 0.168)→(0.596, 0.196, 0.187) | (0.519, 0.100, 0.016)→(0.519, 0.100, 0.016) | 0.209→0.209 | 1.00 / 4.000 | 0.123 | 0.123 |
| retract | retract | 1.00 / step_budget | (0.596, 0.196, 0.187)→(0.593, 0.195, 0.272) | (0.519, 0.100, 0.016)→(0.519, 0.100, 0.016) | 0.209→0.209 | 1.00 / 4.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: 0.000
- terminal_score: 0.418
- phase_score: 0.186
- phase_breakdown.place_goal_score: 0.000
- phase_breakdown.reach_object_score: 0.620
- grasp_place_fitness: 0.674

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.674
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.418
- **Median Q (composite search score)**: -0.052
- **K-run variance**: 0.0033
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.354


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.61538,"average_solve_count":195.0,"average_success_count":195.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_grasp.lateral_offset_x":0.00927,"align_grasp.lateral_offset_y":0.00251,"approach_goal.arc_height":0.04484,"approach_goal.transport_speed":0.2104,"approach_object.approach_speed":0.04507,"descend_place.descend_speed":0.24359,"lift.lift_height":0.15976,"lift.lift_speed":0.09523,"release.release_duration":1.54229},"optimized_scores":{"best_composite_score":0.04439,"best_fitness_score":0.67439,"best_task_score":0.41788},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1505.0,"contact_point_centroid":[0.56012,0.24648,-0.00275],"force_p95":0.43085,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.12228,"mean_force":0.17289,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.55356,0.22598,0.23758]},{"body_a":"world","body_b":"grasp_target","contact_count":151.0,"contact_point_centroid":[0.49883,0.04618,-0.0012],"force_p95":0.27862,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.39405,"mean_force":0.04826,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49549,0.04574,0.04952]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":21069.0,"contact_point_centroid":[0.49538,0.06445,0.13029],"force_p95":0.0841,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30612,"mean_force":0.05811,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.4946,0.04532,0.12974]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":23898.0,"contact_point_centroid":[0.49487,0.02636,0.12908],"force_p95":0.07694,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28204,"mean_force":0.05121,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49461,0.04532,0.1284]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4530.0,"contact_point_centroid":[0.51539,0.12001,0.21414],"force_p95":0.13991,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20623,"mean_force":0.09838,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.51132,0.10157,0.21707]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50118,0.04513,-0.00208],"force_p95":0.14514,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19481,"mean_force":0.12891,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49815,0.04602,0.04892]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5064.0,"contact_point_centroid":[0.51486,0.08281,0.21432],"force_p95":0.12715,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18177,"mean_force":0.08688,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.51111,0.10098,0.21696]},{"body_a":"world","body_b":"grasp_target","contact_count":2248.0,"contact_point_centroid":[0.50118,0.04505,-0.00194],"force_p95":0.13153,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12284,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.49753,0.02009,0.21895]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4099.0,"contact_point_centroid":[0.49796,0.06512,0.04869],"force_p95":0.07793,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13826,"mean_force":0.05219,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49699,0.0459,0.04764]},{"body_a":"world","body_b":"grasp_target","contact_count":2084.0,"contact_point_centroid":[0.50118,0.04505,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"align_grasp","phase_type":"align","tcp_position_centroid":[0.49951,0.04381,0.09472]},{"body_a":"world","body_b":"grasp_target","contact_count":544.0,"contact_point_centroid":[0.56001,0.24867,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.55554,0.23135,0.20227]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.56001,0.24867,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.55392,0.23627,0.16467]},{"body_a":"world","body_b":"grasp_target","contact_count":2292.0,"contact_point_centroid":[0.56001,0.24867,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.54971,0.23426,0.22566]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4937.0,"contact_point_centroid":[0.49712,0.02683,0.04893],"force_p95":0.06894,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07336,"mean_force":0.04423,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.497,0.04591,0.04764]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1524.0,"contact_point_centroid":[0.55387,0.22593,0.23943],"force_p95":0.01146,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01502,"mean_force":0.01043,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.55343,0.2259,0.23721]},{"body_a":"left_finger","body_b":"right_finger","contact_count":577.0,"contact_point_centroid":[0.556,0.23137,0.20451],"force_p95":0.011,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01103,"mean_force":0.01049,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.55554,0.23134,0.20238]}],"total_contact_groups":17},"final_pose_error":0.01434,"key_states":{"actual_goal_position":[0.56442,0.24486,0.14677],"final_object_position":[0.56001,0.24867,0.01602],"final_tcp_position":[0.54997,0.23432,0.2706],"realised_goal_position":[0.56442,0.24486,0.14677],"realised_object_initial_position":[0.50118,0.04505,0.03]},"peak_contact_force":9748.72238,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":563.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.03],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.23992,"object_z_max":0.03,"peak_contact_force":20.04556,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2248.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.49721,0.04111,0.13825],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11237,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":521.0,"n_steps_budget":600.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"align_grasp","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":2084.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.5048,0.04665,0.05639],"tcp_start":[0.49721,0.04111,0.13825],"tcp_to_object_dist_end":0.03063,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50109,0.04572,0.02569],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24152,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.14296,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10836.0,"raw_peak_contact_force":0.19481,"tcp_end":[0.49696,0.0459,0.04761],"tcp_start":[0.5048,0.04665,0.05639],"tcp_to_object_dist_end":0.02231,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":35.0,"n_steps":813.0,"n_steps_budget":900.0,"object_pos_end":[0.49665,0.0448,0.1384],"object_pos_start":[0.50109,0.04572,0.02569],"object_to_goal_dist_end":0.2114,"object_to_goal_dist_start":0.24152,"object_z_max":0.14741,"peak_contact_force":0.10235,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":45118.0,"raw_peak_contact_force":0.39405,"tcp_end":[0.49333,0.04503,0.16801],"tcp_start":[0.49696,0.0459,0.04761],"tcp_to_object_dist_end":0.0298,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":565.0,"n_steps_budget":1000.0,"object_pos_end":[0.56001,0.24867,0.01602],"object_pos_start":[0.49665,0.0448,0.1384],"object_to_goal_dist_end":0.13089,"object_to_goal_dist_start":0.2114,"object_z_max":0.21317,"peak_contact_force":0.12263,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":12623.0,"raw_peak_contact_force":2.12228,"subtask_id":"place_goal","tcp_end":[0.55333,0.22579,0.23688],"tcp_start":[0.49333,0.04503,0.16801],"tcp_to_object_dist_end":0.22214,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":136.0,"n_steps_budget":1000.0,"object_pos_end":[0.56001,0.24867,0.01602],"object_pos_start":[0.56001,0.24867,0.01602],"object_to_goal_dist_end":0.13089,"object_to_goal_dist_start":0.13089,"object_z_max":0.01602,"peak_contact_force":9748.72238,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1121.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_goal","tcp_end":[0.55842,0.23814,0.16463],"tcp_start":[0.55333,0.22579,0.23688],"tcp_to_object_dist_end":0.14899,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.56001,0.24867,0.01602],"object_pos_start":[0.56001,0.24867,0.01602],"object_to_goal_dist_end":0.13089,"object_to_goal_dist_start":0.13089,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1019.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.55245,0.23553,0.18468],"tcp_start":[0.55842,0.23814,0.16463],"tcp_to_object_dist_end":0.16934,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":573.0,"n_steps_budget":660.0,"object_pos_end":[0.56001,0.24867,0.01602],"object_pos_start":[0.56001,0.24867,0.01602],"object_to_goal_dist_end":0.13089,"object_to_goal_dist_start":0.13089,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2292.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.54997,0.23432,0.2706],"tcp_start":[0.55245,0.23553,0.18468],"tcp_to_object_dist_end":0.25518,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.93056,"average_solve_count":216.0,"average_success_count":216.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_grasp.lateral_offset_x":0.00204,"align_grasp.lateral_offset_y":-0.00519,"approach_goal.arc_height":0.08259,"approach_goal.transport_speed":0.16745,"approach_object.approach_speed":0.06601,"descend_place.descend_speed":0.13576,"lift.lift_height":0.15097,"lift.lift_speed":0.09202,"release.release_duration":1.20366},"optimized_scores":{"best_composite_score":-0.0933,"best_fitness_score":0.5367,"best_task_score":0.15552},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":3649.0,"contact_point_centroid":[0.48671,-0.00583,-0.00221],"force_p95":0.12979,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.50495,"mean_force":0.13236,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.47003,-0.0202,0.22774]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12546.0,"contact_point_centroid":[0.47024,-0.04204,0.11853],"force_p95":0.13623,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3156,"mean_force":0.0964,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.4671,-0.02347,0.12178]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17102.0,"contact_point_centroid":[0.46909,-0.00529,0.11329],"force_p95":0.12631,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27923,"mean_force":0.07287,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46678,-0.02356,0.11439]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47626,-0.02039,-0.00232],"force_p95":0.21376,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.26385,"mean_force":0.14516,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46711,-0.02447,0.05088]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3416.0,"contact_point_centroid":[0.46673,-0.04356,0.04862],"force_p95":0.10982,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14379,"mean_force":0.06138,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46602,-0.02443,0.04975]},{"body_a":"world","body_b":"grasp_target","contact_count":2024.0,"contact_point_centroid":[0.47616,-0.02015,-0.00193],"force_p95":0.13256,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12287,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.4865,-0.00891,0.22011]},{"body_a":"world","body_b":"grasp_target","contact_count":1892.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"align_grasp","phase_type":"align","tcp_position_centroid":[0.47248,-0.0215,0.0961]},{"body_a":"world","body_b":"grasp_target","contact_count":4452.0,"contact_point_centroid":[0.48737,-0.00481,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.5612,0.0833,0.28408]},{"body_a":"world","body_b":"grasp_target","contact_count":564.0,"contact_point_centroid":[0.48737,-0.00481,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.61979,0.14903,0.24869]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.48737,-0.00481,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.62048,0.15333,0.2064]},{"body_a":"world","body_b":"grasp_target","contact_count":2292.0,"contact_point_centroid":[0.48737,-0.00481,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.61678,0.15213,0.2659]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5224.0,"contact_point_centroid":[0.4661,-0.00545,0.0504],"force_p95":0.07951,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08448,"mean_force":0.04229,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46603,-0.02443,0.04977]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3394.0,"contact_point_centroid":[0.47101,-0.01981,0.24181],"force_p95":0.01111,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0163,"mean_force":0.01067,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.47061,-0.0198,0.23956]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4739.0,"contact_point_centroid":[0.56181,0.08347,0.28672],"force_p95":0.01103,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01294,"mean_force":0.01047,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.56135,0.08347,0.28441]},{"body_a":"left_finger","body_b":"right_finger","contact_count":222.0,"contact_point_centroid":[0.62337,0.1541,0.20482],"force_p95":0.01094,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01256,"mean_force":0.01004,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.62276,0.15408,0.20265]},{"body_a":"left_finger","body_b":"right_finger","contact_count":608.0,"contact_point_centroid":[0.62041,0.14904,0.25096],"force_p95":0.01095,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01099,"mean_force":0.01034,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.61978,0.14902,0.24875]}],"total_contact_groups":16},"final_pose_error":0.01523,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.48737,-0.00481,0.01602],"final_tcp_position":[0.61718,0.15218,0.31077],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":273004.34185,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":507.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2024.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.47443,-0.01831,0.1396],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11361,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":473.0,"n_steps_budget":600.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"align_grasp","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":1892.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.47347,-0.02467,0.05745],"tcp_start":[0.47443,-0.01831,0.1396],"tcp_to_object_dist_end":0.03187,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":39.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47615,-0.02317,0.02484],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.29095,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.20891,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10440.0,"raw_peak_contact_force":0.26385,"tcp_end":[0.46599,-0.02443,0.04973],"tcp_start":[0.47347,-0.02467,0.05745],"tcp_to_object_dist_end":0.02691,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1846.0,"n_steps_budget":870.0,"object_pos_end":[0.47295,-0.02237,0.12236],"object_pos_start":[0.47615,-0.02317,0.02484],"object_to_goal_dist_end":0.25031,"object_to_goal_dist_start":0.29095,"object_z_max":0.13552,"peak_contact_force":0.12263,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":36691.0,"raw_peak_contact_force":1.50495,"tcp_end":[0.4817,-0.00718,0.19468],"tcp_start":[0.47012,-0.02231,0.28221],"tcp_to_object_dist_end":0.07442,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":713.0,"n_steps_budget":1000.0,"object_pos_end":[0.48737,-0.00481,0.01602],"object_pos_start":[0.48737,-0.00481,0.01602],"object_to_goal_dist_end":0.27915,"object_to_goal_dist_start":0.27915,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":9191.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_goal","tcp_end":[0.61575,0.1446,0.28634],"tcp_start":[0.4817,-0.00718,0.19468],"tcp_to_object_dist_end":0.33448,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":141.0,"n_steps_budget":1000.0,"object_pos_end":[0.48737,-0.00481,0.01602],"object_pos_start":[0.48737,-0.00481,0.01602],"object_to_goal_dist_end":0.27915,"object_to_goal_dist_start":0.27915,"object_z_max":0.01602,"peak_contact_force":9748.73887,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1172.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_goal","tcp_end":[0.62461,0.15442,0.20771],"tcp_start":[0.61575,0.1446,0.28634],"tcp_to_object_dist_end":0.28449,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48737,-0.00481,0.01602],"object_pos_start":[0.48737,-0.00481,0.01602],"object_to_goal_dist_end":0.27915,"object_to_goal_dist_start":0.27915,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1022.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.61915,0.15288,0.22585],"tcp_start":[0.62461,0.15442,0.20771],"tcp_to_object_dist_end":0.2937,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":573.0,"n_steps_budget":660.0,"object_pos_end":[0.48737,-0.00481,0.01602],"object_pos_start":[0.48737,-0.00481,0.01602],"object_to_goal_dist_end":0.27915,"object_to_goal_dist_start":0.27915,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2292.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.61718,0.15218,0.31077],"tcp_start":[0.61915,0.15288,0.22585],"tcp_to_object_dist_end":0.35829,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.44628,"average_solve_count":242.0,"average_success_count":242.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_grasp.lateral_offset_x":0.00419,"align_grasp.lateral_offset_y":-0.0025,"approach_goal.arc_height":0.05292,"approach_goal.transport_speed":0.22049,"approach_object.approach_speed":0.02091,"descend_place.descend_speed":0.27669,"lift.lift_height":0.18081,"lift.lift_speed":0.09756,"release.release_duration":0.77396},"optimized_scores":{"best_composite_score":-0.05213,"best_fitness_score":0.57787,"best_task_score":0.23626},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":3659.0,"contact_point_centroid":[0.51091,0.05649,-0.00229],"force_p95":0.12494,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.6043,"mean_force":0.13513,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.57818,0.14357,0.22538]},{"body_a":"world","body_b":"grasp_target","contact_count":141.0,"contact_point_centroid":[0.45659,-0.02962,-0.00132],"force_p95":0.26374,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.36656,"mean_force":0.0492,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.44953,-0.02791,0.0526]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13220.0,"contact_point_centroid":[0.45312,-0.04617,0.1324],"force_p95":0.12531,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33067,"mean_force":0.09255,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.4508,-0.02756,0.13535]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17463.0,"contact_point_centroid":[0.45212,-0.00924,0.12593],"force_p95":0.12196,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27329,"mean_force":0.07199,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.45049,-0.02759,0.12729]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":883.0,"contact_point_centroid":[0.46499,0.00316,0.19506],"force_p95":0.16649,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23725,"mean_force":0.10559,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.45933,-0.01454,0.20028]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45856,-0.02637,-0.00217],"force_p95":0.17067,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21526,"mean_force":0.13482,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.45189,-0.02802,0.05155]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":708.0,"contact_point_centroid":[0.46303,-0.03544,0.19263],"force_p95":0.1536,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17489,"mean_force":0.1114,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.4574,-0.01727,0.19804]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3849.0,"contact_point_centroid":[0.45113,-0.04713,0.0501],"force_p95":0.10352,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14647,"mean_force":0.05824,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.45083,-0.02798,0.05049]},{"body_a":"world","body_b":"grasp_target","contact_count":2164.0,"contact_point_centroid":[0.45856,-0.02632,-0.00193],"force_p95":0.13205,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12285,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.47862,-0.01165,0.22006]},{"body_a":"world","body_b":"grasp_target","contact_count":1928.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"align_grasp","phase_type":"align","tcp_position_centroid":[0.45675,-0.0261,0.0963]},{"body_a":"world","body_b":"grasp_target","contact_count":548.0,"contact_point_centroid":[0.51098,0.0565,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.61733,0.19672,0.1705]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.51098,0.0565,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.61681,0.20071,0.12986]},{"body_a":"world","body_b":"grasp_target","contact_count":2172.0,"contact_point_centroid":[0.51098,0.0565,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.61182,0.19885,0.1891]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5007.0,"contact_point_centroid":[0.45086,-0.00917,0.05092],"force_p95":0.07236,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07366,"mean_force":0.04259,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.45083,-0.02798,0.0505]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3734.0,"contact_point_centroid":[0.58298,0.14942,0.2273],"force_p95":0.011,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01597,"mean_force":0.01048,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.58258,0.14941,0.22503]},{"body_a":"left_finger","body_b":"right_finger","contact_count":220.0,"contact_point_centroid":[0.62028,0.20184,0.12817],"force_p95":0.01102,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01262,"mean_force":0.01013,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.61966,0.20181,0.12607]}],"total_contact_groups":17},"final_pose_error":0.01586,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.51098,0.0565,0.01602],"final_tcp_position":[0.61208,0.19888,0.23371],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":9748.99573,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":542.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":17.88709,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2164.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.45833,-0.02397,0.13945],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11346,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":482.0,"n_steps_budget":600.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"align_grasp","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":1928.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.45808,-0.02828,0.05771],"tcp_start":[0.45833,-0.02397,0.13945],"tcp_to_object_dist_end":0.03175,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45846,-0.02762,0.02527],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30493,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.17191,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10656.0,"raw_peak_contact_force":0.21526,"tcp_end":[0.4508,-0.02798,0.05047],"tcp_start":[0.45808,-0.02828,0.05771],"tcp_to_object_dist_end":0.02634,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":18.0,"n_steps":903.0,"n_steps_budget":990.0,"object_pos_end":[0.45591,-0.02673,0.15211],"object_pos_start":[0.45846,-0.02762,0.02527],"object_to_goal_dist_end":0.29494,"object_to_goal_dist_start":0.30493,"object_z_max":0.1606,"peak_contact_force":0.1136,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":30824.0,"raw_peak_contact_force":0.36656,"tcp_end":[0.45116,-0.02731,0.18996],"tcp_start":[0.4508,-0.02798,0.05047],"tcp_to_object_dist_end":0.03816,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":701.0,"n_steps_budget":1000.0,"object_pos_end":[0.51098,0.0565,0.01602],"object_pos_start":[0.45591,-0.02673,0.15211],"object_to_goal_dist_end":0.21642,"object_to_goal_dist_start":0.29494,"object_z_max":0.16814,"peak_contact_force":0.12263,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8984.0,"raw_peak_contact_force":1.6043,"subtask_id":"place_goal","tcp_end":[0.61369,0.19211,0.20647],"tcp_start":[0.45116,-0.02731,0.18996],"tcp_to_object_dist_end":0.25537,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":7.0,"n_steps":137.0,"n_steps_budget":1000.0,"object_pos_end":[0.51098,0.0565,0.01602],"object_pos_start":[0.51098,0.0565,0.01602],"object_to_goal_dist_end":0.21642,"object_to_goal_dist_start":0.21642,"object_z_max":0.01602,"peak_contact_force":9748.99573,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1133.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_goal","tcp_end":[0.62214,0.20246,0.13149],"tcp_start":[0.61369,0.19211,0.20647],"tcp_to_object_dist_end":0.21678,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51098,0.0565,0.01602],"object_pos_start":[0.51098,0.0565,0.01602],"object_to_goal_dist_end":0.21642,"object_to_goal_dist_start":0.21642,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1020.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.61503,0.20003,0.14926],"tcp_start":[0.62214,0.20246,0.13149],"tcp_to_object_dist_end":0.22177,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":543.0,"n_steps_budget":630.0,"object_pos_end":[0.51098,0.0565,0.01602],"object_pos_start":[0.51098,0.0565,0.01602],"object_to_goal_dist_end":0.21642,"object_to_goal_dist_start":0.21642,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2172.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.61208,0.19888,0.23371],"tcp_start":[0.61503,0.20003,0.14926],"tcp_to_object_dist_end":0.27908,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```