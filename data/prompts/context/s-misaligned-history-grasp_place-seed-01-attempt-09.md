## Search State

- **Seed**: 1
- **Iteration**: 10 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 9 | approach → align → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 11  | -0.1265 | 0.41 | ✅ accepted |
| 8 | approach → align → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | impedance_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 9  | 0.0758 | 0.39 | ✅ accepted |
| 7 | approach → align → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 8  | -0.0147 | 0.30 | ❌ rejected |
| 6 | approach → align → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 9  | 0.0115 | 0.36 | ✅ accepted |
| 5 | approach → align → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 9  | -0.0511 | 0.31 | ❌ rejected |

**Proposal policy**: task_score is 0.31 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.051) — your mutation base

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

- **Composite score**: -0.051
- **task_score** (E): 0.312
- **fitness_score**: 0.619  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.670

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1668 |
| align_grasp | 1.00 | 1.00 | 0.0824 |
| grasp | 1.00 | 1.00 | 0.0110 |
| lift | 0.67 | 1.00 | 0.0969 |
| approach_goal | 0.67 | 1.00 | 0.2536 |
| descend_place | 1.00 | 1.00 | 0.1237 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.477, -0.000, 0.139) | (0.479, -0.000, 0.030)→(0.479, -0.000, 0.026) | 0.276→0.278 | 1.00 / 4.000 | 0.123 | 0.138 |
| align_grasp | align | 1.00 / step_budget | (0.477, -0.000, 0.139)→(0.482, -0.001, 0.057) | (0.479, -0.000, 0.026)→(0.479, -0.000, 0.026) | 0.278→0.278 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp | grasp | 1.00 / step_budget | (0.482, -0.001, 0.057)→(0.474, -0.001, 0.049) | (0.479, -0.000, 0.026)→(0.479, -0.001, 0.025) | 0.278→0.279 | 1.00 / 40.667 | 0.161 | 0.211 |
| lift | lift | 0.67 / step_budget | (0.474, -0.001, 0.049)→(0.473, -0.001, 0.146) | (0.479, -0.001, 0.025)→(0.475, -0.001, 0.116) | 0.279→0.252 | 1.00 / 22.667 | 0.114 | 0.379 |
| approach_goal | approach | 0.67 / step_budget | (0.473, -0.001, 0.146)→(0.591, 0.181, 0.272) | (0.475, -0.001, 0.116)→(0.554, 0.131, 0.083) | 0.252→0.160 | 1.00 / 11.667 | 94255.062 | 1.517 |
| descend_place | descend | 1.00 / step_budget | (0.591, 0.181, 0.272)→(0.603, 0.206, 0.153) | (0.554, 0.131, 0.083)→(0.550, 0.140, 0.016) | 0.160→0.179 | 1.00 / 8.000 | 3249.691 | 0.580 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: 1.000
- terminal_score: 0.416
- phase_score: 0.186
- phase_breakdown.place_goal_score: 0.000
- phase_breakdown.reach_object_score: 0.619
- grasp_place_fitness: 0.673

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.673
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.416
- **Median Q (composite search score)**: -0.062
- **K-run variance**: 0.0016
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.349


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.45148,"average_solve_count":237.0,"average_success_count":237.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_grasp.lateral_offset_x":0.0098,"align_grasp.lateral_offset_y":-0.00089,"approach_goal.arc_height":0.14419,"approach_goal.transport_speed":0.12019,"approach_object.approach_speed":0.03036,"descend_place.descend_speed":0.26132,"descend_place.lateral_place_x":-0.01266,"descend_place.lateral_place_y":-0.0108,"descend_place.placement_z_offset":0.00056,"lift.lift_height":0.15443,"lift.lift_speed":0.05968},"optimized_scores":{"best_composite_score":0.00291,"best_fitness_score":0.67291,"best_task_score":0.41573},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":370.0,"contact_point_centroid":[0.54841,0.25403,-0.00528],"force_p95":0.99117,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.49547,"mean_force":0.24804,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.55019,0.23071,0.17399]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":806.0,"contact_point_centroid":[0.55893,0.24633,0.23234],"force_p95":0.13534,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.43743,"mean_force":0.09636,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.55464,0.22855,0.23725]},{"body_a":"world","body_b":"grasp_target","contact_count":219.0,"contact_point_centroid":[0.49754,0.04189,-0.00135],"force_p95":0.2473,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.41399,"mean_force":0.06829,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49561,0.04266,0.04965]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":642.0,"contact_point_centroid":[0.55914,0.21017,0.23515],"force_p95":0.18455,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32135,"mean_force":0.11515,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.55487,0.22854,0.23991]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":19585.0,"contact_point_centroid":[0.49483,0.06144,0.09513],"force_p95":0.0808,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31017,"mean_force":0.05066,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49474,0.04271,0.09466]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7648.0,"contact_point_centroid":[0.51454,0.07952,0.23523],"force_p95":0.13475,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28132,"mean_force":0.09587,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.51252,0.0979,0.23836]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14845.0,"contact_point_centroid":[0.494,0.02359,0.09065],"force_p95":0.11091,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27489,"mean_force":0.06634,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49464,0.04269,0.09093]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7745.0,"contact_point_centroid":[0.5149,0.11611,0.23336],"force_p95":0.13459,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26666,"mean_force":0.09688,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.51248,0.09777,0.23677]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.5012,0.04489,-0.00219],"force_p95":0.17291,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22738,"mean_force":0.1364,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49863,0.04292,0.04891]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4078.0,"contact_point_centroid":[0.49673,0.02361,0.04863],"force_p95":0.08183,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15347,"mean_force":0.0521,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49748,0.04282,0.04762]},{"body_a":"world","body_b":"grasp_target","contact_count":2268.0,"contact_point_centroid":[0.50118,0.04505,-0.00194],"force_p95":0.13153,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12284,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.49749,0.02007,0.21902]},{"body_a":"world","body_b":"grasp_target","contact_count":2084.0,"contact_point_centroid":[0.50118,0.04505,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"align_grasp","phase_type":"align","tcp_position_centroid":[0.49976,0.04224,0.09467]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5065.0,"contact_point_centroid":[0.4976,0.06199,0.04882],"force_p95":0.07585,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07762,"mean_force":0.04384,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49748,0.04282,0.04763]},{"body_a":"left_finger","body_b":"right_finger","contact_count":121.0,"contact_point_centroid":[0.55026,0.23136,0.16388],"force_p95":0.01568,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01615,"mean_force":0.01231,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.54946,0.23133,0.1618]}],"total_contact_groups":14},"final_pose_error":0.00983,"key_states":{"actual_goal_position":[0.56442,0.24486,0.14677],"final_object_position":[0.54817,0.25456,0.01648],"final_tcp_position":[0.54908,0.23158,0.15647],"realised_goal_position":[0.56442,0.24486,0.14677],"realised_object_initial_position":[0.50118,0.04505,0.03]},"peak_contact_force":1.49547,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":568.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.03],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.23992,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2268.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.49721,0.04113,0.13815],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11227,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":521.0,"n_steps_budget":600.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"align_grasp","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":2084.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.50529,0.04352,0.05638],"tcp_start":[0.49721,0.04113,0.13815],"tcp_to_object_dist_end":0.03068,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50109,0.04348,0.0253],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24356,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.16739,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10943.0,"raw_peak_contact_force":0.22738,"tcp_end":[0.49745,0.04282,0.04759],"tcp_start":[0.50529,0.04352,0.05638],"tcp_to_object_dist_end":0.02259,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49682,0.04407,0.11647],"object_pos_start":[0.50109,0.04348,0.0253],"object_to_goal_dist_end":0.21402,"object_to_goal_dist_start":0.24356,"object_z_max":0.11637,"peak_contact_force":0.11126,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":34649.0,"raw_peak_contact_force":0.41399,"tcp_end":[0.49624,0.04298,0.14442],"tcp_start":[0.49745,0.04282,0.04759],"tcp_to_object_dist_end":0.02798,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":19.0,"n_steps":783.0,"n_steps_budget":1000.0,"object_pos_end":[0.56092,0.22764,0.21753],"object_pos_start":[0.49682,0.04407,0.11647],"object_to_goal_dist_end":0.07291,"object_to_goal_dist_start":0.21402,"object_z_max":0.252,"peak_contact_force":0.12235,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":15393.0,"raw_peak_contact_force":0.28132,"subtask_id":"place_goal","tcp_end":[0.55694,0.22801,0.25436],"tcp_start":[0.49624,0.04298,0.14442],"tcp_to_object_dist_end":0.03705,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":256.0,"n_steps_budget":1000.0,"object_pos_end":[0.54817,0.25456,0.01648],"object_pos_start":[0.56092,0.22764,0.21753],"object_to_goal_dist_end":0.13166,"object_to_goal_dist_start":0.07291,"object_z_max":0.21753,"peak_contact_force":0.12483,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1939.0,"raw_peak_contact_force":1.49547,"subtask_id":"place_goal","tcp_end":[0.54908,0.23158,0.15647],"tcp_start":[0.55694,0.22801,0.25436],"tcp_to_object_dist_end":0.14186,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.49412,"average_solve_count":170.0,"average_success_count":170.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_grasp.lateral_offset_x":0.01,"align_grasp.lateral_offset_y":-0.00187,"approach_goal.arc_height":0.05206,"approach_goal.transport_speed":0.20315,"approach_object.approach_speed":0.05647,"descend_place.descend_speed":0.20759,"descend_place.lateral_place_x":-0.00535,"descend_place.lateral_place_y":0.01051,"descend_place.placement_z_offset":-0.00496,"lift.lift_height":0.14065,"lift.lift_speed":0.05876},"optimized_scores":{"best_composite_score":-0.06182,"best_fitness_score":0.60818,"best_task_score":0.28936},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":732.0,"contact_point_centroid":[0.57527,0.12497,-0.00362],"force_p95":0.85859,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.01995,"mean_force":0.20615,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.59332,0.11787,0.28329]},{"body_a":"world","body_b":"grasp_target","contact_count":190.0,"contact_point_centroid":[0.47237,-0.02217,-0.00126],"force_p95":0.24242,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.37541,"mean_force":0.05797,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.47163,-0.02139,0.051]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4209.0,"contact_point_centroid":[0.49953,-0.00761,0.20239],"force_p95":0.14735,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30291,"mean_force":0.09887,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.49744,0.01071,0.20589]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13494.0,"contact_point_centroid":[0.46978,-0.04017,0.09133],"force_p95":0.11158,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28121,"mean_force":0.07257,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.47038,-0.02118,0.09249]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17182.0,"contact_point_centroid":[0.47044,-0.00253,0.09236],"force_p95":0.0965,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27783,"mean_force":0.05721,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.47036,-0.02118,0.09271]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47616,-0.02024,-0.00212],"force_p95":0.15388,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.20792,"mean_force":0.13122,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.4744,-0.02147,0.05026]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4469.0,"contact_point_centroid":[0.50308,0.03201,0.20622],"force_p95":0.13319,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19608,"mean_force":0.09492,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.50021,0.01379,0.20988]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4097.0,"contact_point_centroid":[0.4725,-0.04066,0.04973],"force_p95":0.07859,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14171,"mean_force":0.05212,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.47329,-0.02144,0.0491]},{"body_a":"world","body_b":"grasp_target","contact_count":2088.0,"contact_point_centroid":[0.47616,-0.02015,-0.00193],"force_p95":0.13221,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12286,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.48651,-0.00892,0.22002]},{"body_a":"world","body_b":"grasp_target","contact_count":984.0,"contact_point_centroid":[0.57504,0.12532,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12271,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.61917,0.15477,0.23761]},{"body_a":"world","body_b":"grasp_target","contact_count":2084.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"align_grasp","phase_type":"align","tcp_position_centroid":[0.47617,-0.01997,0.09583]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4971.0,"contact_point_centroid":[0.47337,-0.00235,0.04992],"force_p95":0.07174,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07217,"mean_force":0.04411,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.47329,-0.02144,0.0491]},{"body_a":"left_finger","body_b":"right_finger","contact_count":607.0,"contact_point_centroid":[0.59862,0.1235,0.28642],"force_p95":0.01312,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0163,"mean_force":0.01099,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.59835,0.1235,0.28404]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1037.0,"contact_point_centroid":[0.61954,0.15478,0.23989],"force_p95":0.01102,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0128,"mean_force":0.01057,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.61917,0.15477,0.23759]}],"total_contact_groups":14},"final_pose_error":0.00979,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.57504,0.12532,0.01602],"final_tcp_position":[0.62152,0.16484,0.19223],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":273015.91059,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":523.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2088.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.47446,-0.01833,0.13947],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11348,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":521.0,"n_steps_budget":600.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"align_grasp","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":2084.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.48083,-0.02164,0.05702],"tcp_start":[0.47446,-0.01833,0.13947],"tcp_to_object_dist_end":0.03138,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47607,-0.02109,0.02557],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28928,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.15073,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10868.0,"raw_peak_contact_force":0.20792,"tcp_end":[0.47326,-0.02144,0.04907],"tcp_start":[0.48083,-0.02164,0.05702],"tcp_to_object_dist_end":0.02367,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47501,-0.02045,0.11669],"object_pos_start":[0.47607,-0.02109,0.02557],"object_to_goal_dist_end":0.24922,"object_to_goal_dist_start":0.28928,"object_z_max":0.11659,"peak_contact_force":0.11001,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":30866.0,"raw_peak_contact_force":0.37541,"tcp_end":[0.47167,-0.02101,0.14651],"tcp_start":[0.47326,-0.02144,0.04907],"tcp_to_object_dist_end":0.03002,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":741.0,"n_steps_budget":1000.0,"object_pos_end":[0.57503,0.12532,0.01602],"object_pos_start":[0.47501,-0.02045,0.11669],"object_to_goal_dist_end":0.18602,"object_to_goal_dist_start":0.24922,"object_z_max":0.22464,"peak_contact_force":273015.91059,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":10017.0,"raw_peak_contact_force":2.01995,"subtask_id":"place_goal","tcp_end":[0.61824,0.14591,0.28321],"tcp_start":[0.47167,-0.02101,0.14651],"tcp_to_object_dist_end":0.27144,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":246.0,"n_steps_budget":1000.0,"object_pos_end":[0.57504,0.12532,0.01602],"object_pos_start":[0.57503,0.12532,0.01602],"object_to_goal_dist_end":0.18601,"object_to_goal_dist_start":0.18602,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2021.0,"raw_peak_contact_force":0.12271,"subtask_id":"place_goal","tcp_end":[0.62152,0.16484,0.19223],"tcp_start":[0.61824,0.14591,0.28321],"tcp_to_object_dist_end":0.18647,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.37828,"average_solve_count":267.0,"average_success_count":267.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_grasp.lateral_offset_x":0.00494,"align_grasp.lateral_offset_y":0.00055,"approach_goal.arc_height":0.1415,"approach_goal.transport_speed":0.08003,"approach_object.approach_speed":0.05728,"descend_place.descend_speed":0.06952,"descend_place.lateral_place_x":0.01559,"descend_place.lateral_place_y":0.01883,"descend_place.placement_z_offset":-0.00733,"lift.lift_height":0.17123,"lift.lift_speed":0.03553},"optimized_scores":{"best_composite_score":-0.09427,"best_fitness_score":0.57573,"best_task_score":0.23086},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1523.0,"contact_point_centroid":[0.52743,0.04029,-0.00292],"force_p95":0.39197,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.2498,"mean_force":0.15875,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.55462,0.1109,0.30597]},{"body_a":"world","body_b":"grasp_target","contact_count":193.0,"contact_point_centroid":[0.45454,-0.02342,-0.00136],"force_p95":0.26717,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.34633,"mean_force":0.0724,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.45,-0.02515,0.05225]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11727.0,"contact_point_centroid":[0.45075,-0.00627,0.09368],"force_p95":0.1117,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28728,"mean_force":0.08128,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.45004,-0.02512,0.09608]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4529.0,"contact_point_centroid":[0.46179,0.00653,0.21592],"force_p95":0.15178,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27693,"mean_force":0.10373,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.45991,-0.01196,0.21992]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14952.0,"contact_point_centroid":[0.44971,-0.04362,0.09171],"force_p95":0.10027,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24752,"mean_force":0.06453,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.44989,-0.02512,0.09318]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5428.0,"contact_point_centroid":[0.46073,-0.03083,0.21318],"force_p95":0.13537,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22897,"mean_force":0.08843,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.4594,-0.01267,0.21709]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45856,-0.0263,-0.00213],"force_p95":0.16227,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19862,"mean_force":0.13202,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.45259,-0.02525,0.05142]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4214.0,"contact_point_centroid":[0.45211,-0.00604,0.05047],"force_p95":0.09902,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14226,"mean_force":0.05472,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.45152,-0.02521,0.05036]},{"body_a":"world","body_b":"grasp_target","contact_count":2112.0,"contact_point_centroid":[0.45856,-0.02632,-0.00193],"force_p95":0.13221,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12286,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.47873,-0.01164,0.22019]},{"body_a":"world","body_b":"grasp_target","contact_count":1944.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"align_grasp","phase_type":"align","tcp_position_centroid":[0.45716,-0.02467,0.09633]},{"body_a":"world","body_b":"grasp_target","contact_count":2340.0,"contact_point_centroid":[0.52739,0.04037,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.61757,0.19507,0.18988]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4946.0,"contact_point_centroid":[0.45158,-0.04406,0.05076],"force_p95":0.07002,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07373,"mean_force":0.04293,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.45152,-0.02521,0.05036]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1499.0,"contact_point_centroid":[0.55895,0.11615,0.30782],"force_p95":0.01188,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01554,"mean_force":0.01056,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.55865,0.11615,0.30551]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2504.0,"contact_point_centroid":[0.6179,0.19501,0.19236],"force_p95":0.01097,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01267,"mean_force":0.01042,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.61752,0.195,0.19009]}],"total_contact_groups":14},"final_pose_error":0.00999,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.52739,0.04037,0.01602],"final_tcp_position":[0.63796,0.2213,0.10937],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":9749.1539,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":529.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2112.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.45843,-0.02394,0.13971],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11372,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":486.0,"n_steps_budget":600.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"align_grasp","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":1944.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.45879,-0.02547,0.05759],"tcp_start":[0.45843,-0.02394,0.13971],"tcp_to_object_dist_end":0.03158,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45847,-0.02541,0.02535],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30319,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.16512,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10960.0,"raw_peak_contact_force":0.19862,"tcp_end":[0.45149,-0.02521,0.05033],"tcp_start":[0.45879,-0.02547,0.05759],"tcp_to_object_dist_end":0.02594,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.45306,-0.02544,0.1147],"object_pos_start":[0.45847,-0.02541,0.02535],"object_to_goal_dist_end":0.29317,"object_to_goal_dist_start":0.30319,"object_z_max":0.11462,"peak_contact_force":0.11952,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":26872.0,"raw_peak_contact_force":0.34633,"tcp_end":[0.45251,-0.02519,0.14679],"tcp_start":[0.45149,-0.02521,0.05033],"tcp_to_object_dist_end":0.0321,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52739,0.04037,0.01602],"object_pos_start":[0.45306,-0.02544,0.1147],"object_to_goal_dist_end":0.21989,"object_to_goal_dist_start":0.29317,"object_z_max":0.25213,"peak_contact_force":9749.1539,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":12979.0,"raw_peak_contact_force":2.2498,"subtask_id":"place_goal","tcp_end":[0.59924,0.16946,0.27707],"tcp_start":[0.45251,-0.02519,0.14679],"tcp_to_object_dist_end":0.29996,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":585.0,"n_steps_budget":1000.0,"object_pos_end":[0.52739,0.04037,0.01602],"object_pos_start":[0.52739,0.04037,0.01602],"object_to_goal_dist_end":0.21989,"object_to_goal_dist_start":0.21989,"object_z_max":0.01602,"peak_contact_force":9748.82661,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4844.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_goal","tcp_end":[0.63796,0.2213,0.10937],"tcp_start":[0.59924,0.16946,0.27707],"tcp_to_object_dist_end":0.23168,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```