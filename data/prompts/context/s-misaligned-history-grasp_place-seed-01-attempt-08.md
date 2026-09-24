## Search State

- **Seed**: 1
- **Iteration**: 9 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 8 | approach → align → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | impedance_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 9  | 0.0758 | 0.39 | ✅ accepted |
| 7 | approach → align → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 8  | -0.0147 | 0.30 | ❌ rejected |
| 6 | approach → align → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 9  | 0.0115 | 0.36 | ✅ accepted |
| 5 | approach → align → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 9  | -0.0517 | 0.23 | ❌ rejected |
| 4 | approach → align → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 9  | -0.1265 | 0.41 | ✅ accepted |

**Proposal policy**: task_score is 0.41 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.126) — your mutation base

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

- **Composite score**: -0.126
- **task_score** (E): 0.414
- **fitness_score**: 0.504  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.630

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1669 |
| align_grasp | 1.00 | 1.00 | 0.0823 |
| grasp | 1.00 | 1.00 | 0.0110 |
| lift | 1.00 | 1.00 | 0.0452 |
| approach_goal | 1.00 | 0.67 | 0.2722 |
| descend_place | 1.00 | 1.00 | 0.0649 |
| release | 1.00 | 1.00 | 0.0198 |
| retract | 1.00 | 1.00 | 0.0849 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.477, -0.000, 0.139) | (0.479, -0.000, 0.030)→(0.479, -0.000, 0.026) | 0.276→0.278 | 1.00 / 4.000 | 0.123 | 0.138 |
| align_grasp | align | 1.00 / step_budget | (0.477, -0.000, 0.139)→(0.482, -0.001, 0.057) | (0.479, -0.000, 0.026)→(0.479, -0.000, 0.026) | 0.278→0.278 | 1.00 / 4.000 | 27.129 | 0.123 |
| grasp | grasp | 1.00 / step_budget | (0.482, -0.001, 0.057)→(0.474, -0.001, 0.049) | (0.479, -0.000, 0.026)→(0.479, -0.001, 0.026) | 0.278→0.278 | 1.00 / 41.000 | 0.145 | 0.185 |
| lift | lift | 1.00 / step_budget | (0.474, -0.001, 0.049)→(0.470, -0.001, 0.094) | (0.479, -0.001, 0.026)→(0.471, -0.000, 0.065) | 0.278→0.268 | 1.00 / 27.333 | 0.105 | 0.349 |
| approach_goal | approach | 1.00 / step_budget | (0.470, -0.001, 0.094)→(0.595, 0.190, 0.232) | (0.471, -0.000, 0.065)→(0.596, 0.197, 0.072) | 0.268→0.105 | 0.67 / 5.667 | 0.082 | 1.260 |
| descend_place | descend | 1.00 / step_budget | (0.595, 0.190, 0.232)→(0.602, 0.199, 0.168) | (0.596, 0.197, 0.072)→(0.596, 0.207, 0.015) | 0.105→0.137 | 1.00 / 6.667 | 3249.676 | 0.711 |
| release | release | 1.00 / step_budget | (0.602, 0.199, 0.168)→(0.595, 0.196, 0.186) | (0.596, 0.207, 0.015)→(0.596, 0.207, 0.016) | 0.137→0.136 | 1.00 / 4.000 | 0.123 | 0.124 |
| retract | retract | 1.00 / step_budget | (0.595, 0.196, 0.186)→(0.593, 0.195, 0.271) | (0.596, 0.207, 0.016)→(0.596, 0.207, 0.016) | 0.136→0.136 | 1.00 / 4.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: 1.000
- terminal_score: 0.414
- phase_score: 0.187
- phase_breakdown.place_goal_score: 0.000
- phase_breakdown.reach_object_score: 0.623
- grasp_place_fitness: 0.672

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.672
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.516
- **Median Q (composite search score)**: -0.160
- **K-run variance**: 0.0159
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.413


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.5364,"average_solve_count":261.0,"average_success_count":261.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_grasp.lateral_offset_x":0.00728,"align_grasp.lateral_offset_y":0.00223,"approach_goal.arc_height":0.03398,"approach_goal.transport_speed":0.06797,"approach_object.approach_speed":0.03502,"descend_place.descend_speed":0.16034,"lift.lift_height":0.13036,"lift.lift_speed":0.08805,"release.release_duration":0.72878},"optimized_scores":{"best_composite_score":0.04191,"best_fitness_score":0.67191,"best_task_score":0.41411},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":196.0,"contact_point_centroid":[0.55698,0.2606,-0.00774],"force_p95":1.37809,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.88918,"mean_force":0.4158,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.55698,0.23568,0.178]},{"body_a":"world","body_b":"grasp_target","contact_count":164.0,"contact_point_centroid":[0.49914,0.04593,-0.00119],"force_p95":0.24725,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.38321,"mean_force":0.05023,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49369,0.0455,0.04953]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":19107.0,"contact_point_centroid":[0.49452,0.06424,0.11284],"force_p95":0.08345,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29936,"mean_force":0.05788,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.4937,0.0451,0.1122]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11418.0,"contact_point_centroid":[0.52436,0.11746,0.20072],"force_p95":0.12674,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27928,"mean_force":0.08103,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.52231,0.13572,0.20315]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":21629.0,"contact_point_centroid":[0.49407,0.02612,0.11199],"force_p95":0.07555,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.273,"mean_force":0.05107,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49369,0.0451,0.11126]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10055.0,"contact_point_centroid":[0.52716,0.1596,0.20147],"force_p95":0.12984,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26807,"mean_force":0.09192,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.5242,0.14119,0.20467]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50118,0.04511,-0.00206],"force_p95":0.14014,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17333,"mean_force":0.1274,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49632,0.04577,0.049]},{"body_a":"world","body_b":"grasp_target","contact_count":2264.0,"contact_point_centroid":[0.50118,0.04505,-0.00194],"force_p95":0.13153,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12284,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.49749,0.02011,0.21888]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4109.0,"contact_point_centroid":[0.49615,0.06488,0.04879],"force_p95":0.07698,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13507,"mean_force":0.05212,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49517,0.04566,0.04772]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.55646,0.26297,-0.00197],"force_p95":0.12611,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12722,"mean_force":0.11779,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.55383,0.23643,0.16423]},{"body_a":"world","body_b":"grasp_target","contact_count":2068.0,"contact_point_centroid":[0.50118,0.04505,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"align_grasp","phase_type":"align","tcp_position_centroid":[0.49861,0.04371,0.09449]},{"body_a":"world","body_b":"grasp_target","contact_count":2172.0,"contact_point_centroid":[0.55646,0.26297,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.54963,0.23444,0.22514]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4902.0,"contact_point_centroid":[0.4953,0.0266,0.04899],"force_p95":0.06816,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08723,"mean_force":0.04439,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49517,0.04566,0.04773]},{"body_a":"left_finger","body_b":"right_finger","contact_count":215.0,"contact_point_centroid":[0.55682,0.23768,0.16174],"force_p95":0.01523,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0161,"mean_force":0.01129,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.55623,0.23763,0.1596]}],"total_contact_groups":14},"final_pose_error":0.01466,"key_states":{"actual_goal_position":[0.56442,0.24486,0.14677],"final_object_position":[0.55646,0.26297,0.01602],"final_tcp_position":[0.54988,0.23449,0.26984],"realised_goal_position":[0.56442,0.24486,0.14677],"realised_object_initial_position":[0.50118,0.04505,0.03]},"peak_contact_force":81.14225,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":567.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.03],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.23992,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2264.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.49721,0.04115,0.1381],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11222,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":517.0,"n_steps_budget":600.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":81.14225,"phase_name":"align_grasp","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":2068.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.50296,0.0464,0.05642],"tcp_start":[0.49721,0.04115,0.1381],"tcp_to_object_dist_end":0.03048,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5011,0.04556,0.02576],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24161,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.1386,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10811.0,"raw_peak_contact_force":0.17333,"tcp_end":[0.49514,0.04566,0.04769],"tcp_start":[0.50296,0.0464,0.05642],"tcp_to_object_dist_end":0.02272,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":35.0,"n_steps":693.0,"n_steps_budget":780.0,"object_pos_end":[0.49651,0.04462,0.11024],"object_pos_start":[0.5011,0.04556,0.02576],"object_to_goal_dist_end":0.21458,"object_to_goal_dist_start":0.24161,"object_z_max":0.11901,"peak_contact_force":0.1005,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":40900.0,"raw_peak_contact_force":0.38321,"tcp_end":[0.49272,0.04483,0.1394],"tcp_start":[0.49514,0.04566,0.04769],"tcp_to_object_dist_end":0.02941,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":720.0,"n_steps_budget":1000.0,"object_pos_end":[0.55685,0.23315,0.18489],"object_pos_start":[0.49651,0.04462,0.11024],"object_to_goal_dist_end":0.04058,"object_to_goal_dist_start":0.21458,"object_z_max":0.20475,"peak_contact_force":0.0,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":21473.0,"raw_peak_contact_force":0.27928,"subtask_id":"place_goal","tcp_end":[0.55331,0.22701,0.23172],"tcp_start":[0.49272,0.04483,0.1394],"tcp_to_object_dist_end":0.04736,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":128.0,"n_steps_budget":1000.0,"object_pos_end":[0.55525,0.26262,0.01353],"object_pos_start":[0.55685,0.23315,0.18489],"object_to_goal_dist_end":0.13473,"object_to_goal_dist_start":0.04058,"object_z_max":0.18489,"peak_contact_force":0.07783,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":196.0,"raw_peak_contact_force":1.88918,"subtask_id":"place_goal","tcp_end":[0.55833,0.23831,0.16418],"tcp_start":[0.55331,0.22701,0.23172],"tcp_to_object_dist_end":0.15262,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.55646,0.26297,0.01602],"object_pos_start":[0.55525,0.26262,0.01353],"object_to_goal_dist_end":0.13224,"object_to_goal_dist_start":0.13473,"object_z_max":0.01668,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1015.0,"raw_peak_contact_force":0.12722,"tcp_end":[0.55235,0.2357,0.18424],"tcp_start":[0.55833,0.23831,0.16418],"tcp_to_object_dist_end":0.17046,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":543.0,"n_steps_budget":630.0,"object_pos_end":[0.55646,0.26297,0.01602],"object_pos_start":[0.55646,0.26297,0.01602],"object_to_goal_dist_end":0.13224,"object_to_goal_dist_start":0.13224,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2172.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.54988,0.23449,0.26984],"tcp_start":[0.55235,0.2357,0.18424],"tcp_to_object_dist_end":0.2555,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.97576,"average_solve_count":165.0,"average_success_count":165.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_grasp.lateral_offset_x":0.00845,"align_grasp.lateral_offset_y":-0.00145,"approach_goal.arc_height":0.02044,"approach_goal.transport_speed":0.19319,"approach_object.approach_speed":0.07417,"descend_place.descend_speed":0.24622,"lift.lift_height":0.05308,"lift.lift_speed":0.04141,"release.release_duration":1.05052},"optimized_scores":{"best_composite_score":-0.26168,"best_fitness_score":0.36832,"best_task_score":0.31006},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2185.0,"contact_point_centroid":[0.6138,0.14286,-0.00249],"force_p95":0.16784,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.92216,"mean_force":0.14514,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.61615,0.14574,0.26634]},{"body_a":"world","body_b":"grasp_target","contact_count":207.0,"contact_point_centroid":[0.47246,-0.02149,-0.00125],"force_p95":0.26769,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.31689,"mean_force":0.06214,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.47057,-0.02098,0.05087]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9830.0,"contact_point_centroid":[0.46815,-0.03984,0.06297],"force_p95":0.10794,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2383,"mean_force":0.06529,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46863,-0.02075,0.06332]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12564.0,"contact_point_centroid":[0.46862,-0.002,0.06376],"force_p95":0.08284,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2344,"mean_force":0.05076,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46847,-0.02074,0.06347]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6598.0,"contact_point_centroid":[0.5138,0.01403,0.14334],"force_p95":0.13664,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22212,"mean_force":0.09473,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.51228,0.0324,0.14665]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7621.0,"contact_point_centroid":[0.51198,0.04879,0.14109],"force_p95":0.12738,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21208,"mean_force":0.08425,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.51044,0.0304,0.14364]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47616,-0.02024,-0.00208],"force_p95":0.14528,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19072,"mean_force":0.12881,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.47298,-0.02108,0.05032]},{"body_a":"world","body_b":"grasp_target","contact_count":1976.0,"contact_point_centroid":[0.47616,-0.02015,-0.00193],"force_p95":0.13308,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12287,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.48648,-0.00891,0.22008]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4102.0,"contact_point_centroid":[0.47109,-0.04026,0.04988],"force_p95":0.07766,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1365,"mean_force":0.05211,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.47187,-0.02105,0.04916]},{"body_a":"world","body_b":"grasp_target","contact_count":2072.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"align_grasp","phase_type":"align","tcp_position_centroid":[0.47542,-0.01978,0.09569]},{"body_a":"world","body_b":"grasp_target","contact_count":428.0,"contact_point_centroid":[0.61384,0.14281,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.62164,0.15204,0.23907]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.61384,0.14281,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.62073,0.15407,0.20669]},{"body_a":"world","body_b":"grasp_target","contact_count":2172.0,"contact_point_centroid":[0.61384,0.14281,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.61703,0.1529,0.26612]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4930.0,"contact_point_centroid":[0.47194,-0.00197,0.04996],"force_p95":0.07035,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07059,"mean_force":0.04433,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.47187,-0.02105,0.04917]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2120.0,"contact_point_centroid":[0.61841,0.14794,0.2699],"force_p95":0.01131,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01654,"mean_force":0.01053,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.61804,0.14793,0.26755]},{"body_a":"left_finger","body_b":"right_finger","contact_count":458.0,"contact_point_centroid":[0.62216,0.15208,0.24109],"force_p95":0.01095,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01099,"mean_force":0.01042,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.62166,0.15206,0.23882]}],"total_contact_groups":17},"final_pose_error":0.01554,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.61384,0.14281,0.01602],"final_tcp_position":[0.6174,0.15295,0.31075],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":9748.82842,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":495.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1976.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.47438,-0.01833,0.1394],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11341,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":518.0,"n_steps_budget":600.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"align_grasp","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":2072.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.4794,-0.02125,0.05704],"tcp_start":[0.47438,-0.01833,0.1394],"tcp_to_object_dist_end":0.03121,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47607,-0.02086,0.02569],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28906,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.1432,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10832.0,"raw_peak_contact_force":0.19072,"tcp_end":[0.47184,-0.02105,0.04913],"tcp_start":[0.4794,-0.02125,0.05704],"tcp_to_object_dist_end":0.02382,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":24.0,"n_steps":249.0,"n_steps_budget":600.0,"object_pos_end":[0.46789,-0.01994,0.0379],"object_pos_start":[0.47607,-0.02086,0.02569],"object_to_goal_dist_end":0.28631,"object_to_goal_dist_start":0.28906,"object_z_max":0.04572,"peak_contact_force":0.10864,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":22601.0,"raw_peak_contact_force":0.31689,"tcp_end":[0.46666,-0.02065,0.0654],"tcp_start":[0.47184,-0.02105,0.04913],"tcp_to_object_dist_end":0.02754,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":917.0,"n_steps_budget":1000.0,"object_pos_end":[0.61384,0.14281,0.01602],"object_pos_start":[0.46789,-0.01994,0.0379],"object_to_goal_dist_end":0.17565,"object_to_goal_dist_start":0.28631,"object_z_max":0.19186,"peak_contact_force":0.12263,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":18524.0,"raw_peak_contact_force":1.92216,"subtask_id":"place_goal","tcp_end":[0.61903,0.14955,0.26645],"tcp_start":[0.46666,-0.02065,0.0654],"tcp_to_object_dist_end":0.25057,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":107.0,"n_steps_budget":1000.0,"object_pos_end":[0.61384,0.14281,0.01602],"object_pos_start":[0.61384,0.14281,0.01602],"object_to_goal_dist_end":0.17565,"object_to_goal_dist_start":0.17565,"object_z_max":0.01602,"peak_contact_force":9748.82842,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":886.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_goal","tcp_end":[0.62488,0.15519,0.208],"tcp_start":[0.61903,0.14955,0.26645],"tcp_to_object_dist_end":0.1927,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.61384,0.14281,0.01602],"object_pos_start":[0.61384,0.14281,0.01602],"object_to_goal_dist_end":0.17565,"object_to_goal_dist_start":0.17565,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1020.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.61939,0.15363,0.22614],"tcp_start":[0.62488,0.15519,0.208],"tcp_to_object_dist_end":0.21048,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":543.0,"n_steps_budget":630.0,"object_pos_end":[0.61384,0.14281,0.01602],"object_pos_start":[0.61384,0.14281,0.01602],"object_to_goal_dist_end":0.17565,"object_to_goal_dist_start":0.17565,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2172.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.6174,0.15295,0.31075],"tcp_start":[0.61939,0.15363,0.22614],"tcp_to_object_dist_end":0.29493,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.54378,"average_solve_count":217.0,"average_success_count":217.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_grasp.lateral_offset_x":0.00963,"align_grasp.lateral_offset_y":-0.00164,"approach_goal.arc_height":0.04143,"approach_goal.transport_speed":0.09119,"approach_object.approach_speed":0.05794,"descend_place.descend_speed":0.09352,"lift.lift_height":0.0639,"lift.lift_speed":0.05883,"release.release_duration":1.44633},"optimized_scores":{"best_composite_score":-0.15963,"best_fitness_score":0.47037,"best_task_score":0.51633},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1784.0,"contact_point_centroid":[0.61762,0.21502,-0.00257],"force_p95":0.24552,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.5787,"mean_force":0.14832,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.61368,0.1923,0.19884]},{"body_a":"world","body_b":"grasp_target","contact_count":190.0,"contact_point_centroid":[0.45436,-0.02797,-0.00131],"force_p95":0.271,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.34681,"mean_force":0.06357,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.45436,-0.02714,0.05185]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9426.0,"contact_point_centroid":[0.4515,-0.04581,0.06878],"force_p95":0.10846,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30167,"mean_force":0.07393,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.45195,-0.02686,0.07026]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7987.0,"contact_point_centroid":[0.50675,0.03182,0.14549],"force_p95":0.14465,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25822,"mean_force":0.0999,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.50558,0.05023,0.14871]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11754.0,"contact_point_centroid":[0.45223,-0.00826,0.06984],"force_p95":0.09608,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25511,"mean_force":0.05931,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.45202,-0.02686,0.07057]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8830.0,"contact_point_centroid":[0.50917,0.07056,0.14622],"force_p95":0.12996,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19446,"mean_force":0.0913,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.5072,0.05232,0.14983]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45858,-0.02636,-0.0021],"force_p95":0.15236,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18986,"mean_force":0.13007,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.45688,-0.02726,0.05107]},{"body_a":"world","body_b":"grasp_target","contact_count":2112.0,"contact_point_centroid":[0.45856,-0.02632,-0.00193],"force_p95":0.13221,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12286,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.47868,-0.01166,0.22004]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4104.0,"contact_point_centroid":[0.45529,-0.04638,0.05031],"force_p95":0.08792,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1363,"mean_force":0.0556,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.4558,-0.02721,0.05]},{"body_a":"world","body_b":"grasp_target","contact_count":2080.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"align_grasp","phase_type":"align","tcp_position_centroid":[0.45929,-0.0257,0.09615]},{"body_a":"world","body_b":"grasp_target","contact_count":492.0,"contact_point_centroid":[0.61755,0.21522,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.61703,0.19686,0.1656]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.61755,0.21522,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.6164,0.20051,0.12945]},{"body_a":"world","body_b":"grasp_target","contact_count":2172.0,"contact_point_centroid":[0.61755,0.21522,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.6114,0.19866,0.18869]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4929.0,"contact_point_centroid":[0.45585,-0.00825,0.05055],"force_p95":0.07009,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07071,"mean_force":0.04361,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.4558,-0.02721,0.05]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1646.0,"contact_point_centroid":[0.61418,0.19281,0.20005],"force_p95":0.01237,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01649,"mean_force":0.01064,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.61377,0.1928,0.19778]},{"body_a":"left_finger","body_b":"right_finger","contact_count":525.0,"contact_point_centroid":[0.61756,0.19689,0.16779],"force_p95":0.01098,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01284,"mean_force":0.01046,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.61704,0.19687,0.16557]}],"total_contact_groups":17},"final_pose_error":0.01587,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.61755,0.21522,0.01602],"final_tcp_position":[0.61165,0.1987,0.2333],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":1.5787,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":529.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2112.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.45838,-0.02396,0.13954],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11355,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":520.0,"n_steps_budget":600.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"align_grasp","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":2080.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.46312,-0.0275,0.05736],"tcp_start":[0.45838,-0.02396,0.13954],"tcp_to_object_dist_end":0.0317,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.4585,-0.02703,0.02554],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30437,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.15402,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10833.0,"raw_peak_contact_force":0.18986,"tcp_end":[0.45577,-0.02721,0.04997],"tcp_start":[0.46312,-0.0275,0.05736],"tcp_to_object_dist_end":0.02459,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":319.0,"n_steps_budget":600.0,"object_pos_end":[0.44969,-0.02612,0.04695],"object_pos_start":[0.4585,-0.02703,0.02554],"object_to_goal_dist_end":0.30329,"object_to_goal_dist_start":0.30437,"object_z_max":0.05439,"peak_contact_force":0.10654,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":21370.0,"raw_peak_contact_force":0.34681,"tcp_end":[0.44969,-0.0267,0.07613],"tcp_start":[0.45577,-0.02721,0.04997],"tcp_to_object_dist_end":0.02918,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.61755,0.21522,0.01602],"object_pos_start":[0.44969,-0.02612,0.04695],"object_to_goal_dist_end":0.09915,"object_to_goal_dist_start":0.30329,"object_z_max":0.16535,"peak_contact_force":0.12263,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":20247.0,"raw_peak_contact_force":1.5787,"subtask_id":"place_goal","tcp_end":[0.61345,0.19258,0.19696],"tcp_start":[0.44969,-0.0267,0.07613],"tcp_to_object_dist_end":0.1824,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":123.0,"n_steps_budget":1000.0,"object_pos_end":[0.61755,0.21522,0.01602],"object_pos_start":[0.61755,0.21522,0.01602],"object_to_goal_dist_end":0.09915,"object_to_goal_dist_start":0.09915,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1017.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_goal","tcp_end":[0.62175,0.20225,0.13107],"tcp_start":[0.61345,0.19258,0.19696],"tcp_to_object_dist_end":0.11585,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.61755,0.21522,0.01602],"object_pos_start":[0.61755,0.21522,0.01602],"object_to_goal_dist_end":0.09915,"object_to_goal_dist_start":0.09915,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1021.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.61462,0.19983,0.14884],"tcp_start":[0.62175,0.20225,0.13107],"tcp_to_object_dist_end":0.13375,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":543.0,"n_steps_budget":630.0,"object_pos_end":[0.61755,0.21522,0.01602],"object_pos_start":[0.61755,0.21522,0.01602],"object_to_goal_dist_end":0.09915,"object_to_goal_dist_start":0.09915,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2172.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.61165,0.1987,0.2333],"tcp_start":[0.61462,0.19983,0.14884],"tcp_to_object_dist_end":0.21799,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```