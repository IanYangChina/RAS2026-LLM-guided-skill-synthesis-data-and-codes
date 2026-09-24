## Search State

- **Seed**: 1
- **Iteration**: 13 / 15

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

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 1.000, which indicates the subtask decomposition is already effective.
> Preserve the current subtask decomposition unless the evidence shows a subtask change is necessary. Prefer refining phases, parameters, control modes, or termination conditions first.
> Unnecessary subtask redesign when performance is already high often causes regression.

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

## Current Skill (Q=-0.212) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: reach_above_object
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.12
  weight: 0.2
- id: grasp_point
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.03
  weight: 0.2
- id: object_lifted
  anchor: object
  target_entity: object
  offset:
  - 0.0
  - 0.0
  - 0.15
  weight: 0.2
- id: near_goal
  offset:
  - 0.0
  - 0.0
  - 0.1
  weight: 0.2
- id: placed_at_goal
  target_entity: object
  weight: 0.2
phases:
- id: approach_object
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
    - 0.12
    tolerance: 0.005
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
  subtask_id: reach_above_object
- id: descend_to_grasp
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
    - 0.03
    tolerance: 0.005
    orientation:
      mode: keep_current
  parameters:
    descend_speed:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
    grasp_offset_x:
      type: scalar
      range:
      - -0.01
      - 0.01
      default: 0.0
      binds_to:
      - path: target.offset.x
        mode: add
    grasp_offset_y:
      type: scalar
      range:
      - -0.01
      - 0.01
      default: 0.0
      binds_to:
      - path: target.offset.y
        mode: add
  subtask_id: grasp_point
- id: grasp
  type: grasp
  control: position_control
  termination: grasp_success
  end_effector_action: force_grasp
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.03
    orientation:
      mode: keep_current
  parameters:
    grasp_retry_offset_x:
      type: scalar
      range:
      - -0.005
      - 0.005
      default: 0.0
      binds_to:
      - path: retry.offset.x
        mode: add
    grasp_retry_offset_y:
      type: scalar
      range:
      - -0.005
      - 0.005
      default: 0.0
      binds_to:
      - path: retry.offset.y
        mode: add
  guards:
  - id: grasp_check
    when: after_phase
    predicate: bilateral_grasp
    threshold: 0.8
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - 0.0
  subtask_id: grasp_point
- id: lift_object
  type: lift
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.15
      axis: world_z
      mode: replace_offset_projection
      sign: positive
    tolerance: 0.015
    orientation:
      mode: keep_current
  parameters:
    lift_distance:
      type: scalar
      range:
      - 0.1
      - 0.2
      default: 0.15
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    lift_speed:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: object_lifted
- id: transport_to_goal
  type: approach
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
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
    transport_speed:
      type: scalar
      range:
      - 0.05
      - 0.15
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: near_goal
- id: place_at_goal
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
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    place_offset_x:
      type: scalar
      range:
      - -0.02
      - 0.02
      default: 0.0
      binds_to:
      - path: target.offset.x
        mode: add
    place_offset_y:
      type: scalar
      range:
      - -0.02
      - 0.02
      default: 0.0
      binds_to:
      - path: target.offset.y
        mode: add
    place_offset_z:
      type: scalar
      range:
      - 0.02
      - 0.07
      default: 0.05
      binds_to:
      - path: target.offset.z
        mode: add
    place_speed:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: placed_at_goal

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_object** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.12], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_grasp** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.03], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (replace)
    - grasp_offset_x: status=consumed; consumers=target.offset.x (add)
    - grasp_offset_y: status=consumed; consumers=target.offset.y (add)
- **grasp** (`grasp`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.03]
  - orientation: mode=keep_current
  - parameter_bindings:
    - grasp_retry_offset_x: status=consumed; consumers=retry.offset.x (add)
    - grasp_retry_offset_y: status=consumed; consumers=retry.offset.y (add)
  - guards:
    - id=grasp_check, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=0.8
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, 0.0]
- **lift_object** (`lift`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.15, mode=replace_offset_projection, sign=positive}, tolerance=0.015
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - lift_speed: status=consumed; consumers=generator.speed (replace)
- **transport_to_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.1], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - transport_speed: status=consumed; consumers=generator.speed (replace)
- **place_at_goal** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - place_offset_x: status=consumed; consumers=target.offset.x (add)
    - place_offset_y: status=consumed; consumers=target.offset.y (add)
    - place_offset_z: status=consumed; consumers=target.offset.z (add)
    - place_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: -0.212
- **task_score** (E): 0.407
- **fitness_score**: 0.668  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.880

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1532 |
| descend_to_grasp | 1.00 | 1.00 | 0.0979 |
| grasp | 1.00 | 1.00 | 0.0109 |
| lift_object | 1.00 | 1.00 | 0.1346 |
| transport_to_goal | 1.00 | 1.00 | 0.2419 |
| place_at_goal | 1.00 | 1.00 | 0.0541 |
| release_object | 1.00 | 1.00 | 0.0202 |
| retract_from_goal | 1.00 | 1.00 | 0.1302 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.476, -0.000, 0.153) | (0.479, -0.000, 0.030)→(0.479, -0.000, 0.026) | 0.276→0.278 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.476, -0.000, 0.153)→(0.481, -0.001, 0.056) | (0.479, -0.000, 0.026)→(0.479, -0.000, 0.026) | 0.278→0.278 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp | grasp | 1.00 / step_budget | (0.481, -0.001, 0.056)→(0.474, -0.001, 0.048) | (0.479, -0.000, 0.026)→(0.479, -0.001, 0.025) | 0.278→0.278 | 1.00 / 40.333 | 0.176 | 0.234 |
| lift_object | lift | 1.00 / step_budget | (0.474, -0.001, 0.048)→(0.470, -0.001, 0.182) | (0.479, -0.001, 0.025)→(0.479, -0.001, 0.155) | 0.278→0.246 | 1.00 / 30.000 | 0.115 | 0.437 |
| transport_to_goal | approach | 1.00 / step_budget | (0.470, -0.001, 0.182)→(0.599, 0.192, 0.239) | (0.479, -0.001, 0.155)→(0.592, 0.183, 0.076) | 0.246→0.114 | 1.00 / 11.000 | 3252.773 | 1.207 |
| place_at_goal | descend | 1.00 / step_budget | (0.599, 0.192, 0.239)→(0.607, 0.207, 0.188) | (0.592, 0.183, 0.076)→(0.590, 0.194, 0.016) | 0.114→0.138 | 1.00 / 8.000 | 3248.977 | 1.000 |
| release_object | release | 1.00 / step_budget | (0.607, 0.207, 0.188)→(0.602, 0.205, 0.207) | (0.590, 0.194, 0.016)→(0.590, 0.194, 0.016) | 0.138→0.138 | 1.00 / 4.000 | 0.123 | 0.123 |
| retract_from_goal | retract | 1.00 / step_budget | (0.602, 0.205, 0.207)→(0.600, 0.204, 0.337) | (0.590, 0.194, 0.016)→(0.590, 0.194, 0.016) | 0.138→0.138 | 1.00 / 4.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.499
- phase_score: 0.679
- phase_breakdown.near_goal_score: 0.674
- phase_breakdown.reach_above_object_score: 0.906
- phase_breakdown.object_lifted_score: 0.657
- phase_breakdown.grasp_point_score: 0.772
- phase_breakdown.placed_at_goal_score: 0.386
- grasp_place_fitness: 0.709

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.709
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.499
- **Median Q (composite search score)**: -0.206
- **K-run variance**: 0.0013
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Parameters at upper bound**: approach_object.approach_speed
- **Final σ (mean)**: 0.337


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.0,"average_solve_count":152.0,"average_success_count":152.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.3,"descend_to_grasp.descend_speed":0.14167,"descend_to_grasp.descend_z_offset":0.00201,"descend_to_grasp.grasp_offset_x":0.0099,"descend_to_grasp.grasp_offset_y":0.00024,"lift_object.lift_distance":0.14859,"lift_object.lift_speed":0.06881,"place_at_goal.place_offset_x":0.00792,"place_at_goal.place_offset_y":0.00568,"place_at_goal.place_offset_z":0.02152,"place_at_goal.place_speed":0.075,"release_object.release_timeout":0.35809,"retract_from_goal.retract_speed":0.13927,"transport_to_goal.transport_speed":0.20713},"optimized_scores":{"best_composite_score":-0.20617,"best_fitness_score":0.67383,"best_task_score":0.41342},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":355.0,"contact_point_centroid":[0.54756,0.25722,-0.00534],"force_p95":1.052,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.80407,"mean_force":0.25984,"phase_index":5.0,"phase_name":"place_at_goal","phase_type":"descend","tcp_position_centroid":[0.56332,0.24135,0.18664]},{"body_a":"world","body_b":"grasp_target","contact_count":111.0,"contact_point_centroid":[0.49799,0.04367,-0.00137],"force_p95":0.36158,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.4397,"mean_force":0.07256,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49684,0.04392,0.04824]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":13761.0,"contact_point_centroid":[0.49446,0.06269,0.11399],"force_p95":0.07639,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31593,"mean_force":0.05149,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49425,0.04369,0.11279]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11594.0,"contact_point_centroid":[0.49353,0.02454,0.11461],"force_p95":0.08627,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29886,"mean_force":0.05922,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49424,0.04369,0.11332]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":420.0,"contact_point_centroid":[0.55679,0.24924,0.22586],"force_p95":0.16782,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28143,"mean_force":0.07155,"phase_index":5.0,"phase_name":"place_at_goal","phase_type":"descend","tcp_position_centroid":[0.55733,0.23181,0.23043]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":224.0,"contact_point_centroid":[0.55497,0.2131,0.22776],"force_p95":0.20615,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25689,"mean_force":0.10914,"phase_index":5.0,"phase_name":"place_at_goal","phase_type":"descend","tcp_position_centroid":[0.55727,0.23151,0.23255]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7780.0,"contact_point_centroid":[0.52056,0.1083,0.2023],"force_p95":0.11277,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21594,"mean_force":0.06808,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52125,0.1273,0.20299]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50118,0.04493,-0.00209],"force_p95":0.14731,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19587,"mean_force":0.12961,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49933,0.04416,0.04792]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8771.0,"contact_point_centroid":[0.52137,0.14723,0.20266],"force_p95":0.09778,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17768,"mean_force":0.06019,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52166,0.12843,0.20336]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4100.0,"contact_point_centroid":[0.49748,0.02485,0.04828],"force_p95":0.07934,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13894,"mean_force":0.05199,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49817,0.04405,0.04663]},{"body_a":"world","body_b":"grasp_target","contact_count":2628.0,"contact_point_centroid":[0.50118,0.04505,-0.00194],"force_p95":0.12988,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12281,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.49748,0.02141,0.22344]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.54753,0.258,-0.00197],"force_p95":0.12467,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12513,"mean_force":0.12294,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.56187,0.24326,0.17407]},{"body_a":"world","body_b":"grasp_target","contact_count":3616.0,"contact_point_centroid":[0.50118,0.04505,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.50077,0.04373,0.0946]},{"body_a":"world","body_b":"grasp_target","contact_count":1844.0,"contact_point_centroid":[0.54753,0.258,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":7.0,"phase_name":"retract_from_goal","phase_type":"retract","tcp_position_centroid":[0.5583,0.24143,0.25861]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4936.0,"contact_point_centroid":[0.49832,0.06315,0.04811],"force_p95":0.0719,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0725,"mean_force":0.04444,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49817,0.04405,0.04663]},{"body_a":"left_finger","body_b":"right_finger","contact_count":112.0,"contact_point_centroid":[0.56541,0.244,0.17986],"force_p95":0.01605,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01653,"mean_force":0.01263,"phase_index":5.0,"phase_name":"place_at_goal","phase_type":"descend","tcp_position_centroid":[0.56518,0.24396,0.17731]}],"total_contact_groups":17},"final_pose_error":0.0199,"key_states":{"actual_goal_position":[0.56442,0.24486,0.14677],"final_object_position":[0.54753,0.258,0.01602],"final_tcp_position":[0.5588,0.24157,0.32407],"realised_goal_position":[0.56442,0.24486,0.14677],"realised_object_initial_position":[0.50118,0.04505,0.03]},"peak_contact_force":9746.68583,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":658.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.03],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.23992,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2628.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_above_object","tcp_end":[0.49716,0.04259,0.15164],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.1257,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":904.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3616.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_point","tcp_end":[0.50592,0.04476,0.05533],"tcp_start":[0.49716,0.04259,0.15164],"tcp_to_object_dist_end":0.02969,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50108,0.04423,0.02565],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24277,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.1444,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10836.0,"raw_peak_contact_force":0.19587,"subtask_id":"grasp_point","tcp_end":[0.49814,0.04405,0.0466],"tcp_start":[0.50592,0.04476,0.05533],"tcp_to_object_dist_end":0.02115,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":682.0,"n_steps_budget":1000.0,"object_pos_end":[0.50088,0.04383,0.15668],"object_pos_start":[0.50108,0.04423,0.02565],"object_to_goal_dist_end":0.21106,"object_to_goal_dist_start":0.24277,"object_z_max":0.15651,"peak_contact_force":0.08441,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":25466.0,"raw_peak_contact_force":0.4397,"subtask_id":"object_lifted","tcp_end":[0.49448,0.04372,0.18078],"tcp_start":[0.49814,0.04405,0.0466],"tcp_to_object_dist_end":0.02493,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":21.0,"n_steps":529.0,"n_steps_budget":1000.0,"object_pos_end":[0.557,0.23081,0.20034],"object_pos_start":[0.50088,0.04383,0.15668],"object_to_goal_dist_end":0.05587,"object_to_goal_dist_start":0.21106,"object_z_max":0.2003,"peak_contact_force":0.21594,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":16551.0,"raw_peak_contact_force":0.21594,"subtask_id":"near_goal","tcp_end":[0.55723,0.23049,0.23499],"tcp_start":[0.49448,0.04372,0.18078],"tcp_to_object_dist_end":0.03465,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":200.0,"n_steps_budget":1000.0,"object_pos_end":[0.5475,0.25803,0.01654],"object_pos_start":[0.557,0.23081,0.20034],"object_to_goal_dist_end":0.13199,"object_to_goal_dist_start":0.05587,"object_z_max":0.20034,"peak_contact_force":9746.68583,"phase_name":"place_at_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1111.0,"raw_peak_contact_force":1.80407,"subtask_id":"placed_at_goal","tcp_end":[0.56595,0.24506,0.17342],"tcp_start":[0.55723,0.23049,0.23499],"tcp_to_object_dist_end":0.1585,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54753,0.258,0.01602],"object_pos_start":[0.5475,0.25803,0.01654],"object_to_goal_dist_end":0.13249,"object_to_goal_dist_start":0.13199,"object_z_max":0.01654,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1026.0,"raw_peak_contact_force":0.12513,"tcp_end":[0.56042,0.24252,0.19388],"tcp_start":[0.56595,0.24506,0.17342],"tcp_to_object_dist_end":0.179,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":461.0,"n_steps_budget":690.0,"object_pos_end":[0.54753,0.258,0.01602],"object_pos_start":[0.54753,0.258,0.01602],"object_to_goal_dist_end":0.13249,"object_to_goal_dist_start":0.13249,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_from_goal","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1844.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.5588,0.24157,0.32407],"tcp_start":[0.56042,0.24252,0.19388],"tcp_to_object_dist_end":0.3087,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.03165,"average_solve_count":158.0,"average_success_count":158.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.29935,"descend_to_grasp.descend_speed":0.15803,"descend_to_grasp.descend_z_offset":3e-05,"descend_to_grasp.grasp_offset_x":0.00916,"descend_to_grasp.grasp_offset_y":-0.00382,"lift_object.lift_distance":0.17164,"lift_object.lift_speed":0.12237,"place_at_goal.place_offset_x":-0.00198,"place_at_goal.place_offset_y":0.01688,"place_at_goal.place_offset_z":0.03384,"place_at_goal.place_speed":0.08579,"release_object.release_timeout":0.3377,"retract_from_goal.retract_speed":0.10381,"transport_to_goal.transport_speed":0.14108},"optimized_scores":{"best_composite_score":-0.25966,"best_fitness_score":0.62034,"best_task_score":0.30738},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":534.0,"contact_point_centroid":[0.60147,0.14757,-0.00413],"force_p95":1.02438,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.94976,"mean_force":0.23347,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.60638,0.13273,0.27016]},{"body_a":"world","body_b":"grasp_target","contact_count":108.0,"contact_point_centroid":[0.47359,-0.0239,-0.00156],"force_p95":0.37346,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.4801,"mean_force":0.06493,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.47152,-0.02341,0.04821]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":13242.0,"contact_point_centroid":[0.46992,-0.0046,0.12345],"force_p95":0.08858,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31981,"mean_force":0.05401,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46927,-0.02332,0.12228]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11640.0,"contact_point_centroid":[0.46896,-0.04246,0.12398],"force_p95":0.11536,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30548,"mean_force":0.06157,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46925,-0.02332,0.12377]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3797.0,"contact_point_centroid":[0.52236,0.01533,0.22177],"force_p95":0.15584,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26512,"mean_force":0.11132,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.51799,0.03376,0.22552]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47618,-0.02037,-0.00228],"force_p95":0.19576,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.2523,"mean_force":0.14246,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.47401,-0.02348,0.04739]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5172.0,"contact_point_centroid":[0.52025,0.04862,0.22285],"force_p95":0.1349,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21301,"mean_force":0.08547,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.5152,0.03064,0.2241]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4062.0,"contact_point_centroid":[0.47216,-0.04272,0.04741],"force_p95":0.08504,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15487,"mean_force":0.05229,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.47289,-0.02345,0.04623]},{"body_a":"world","body_b":"grasp_target","contact_count":2252.0,"contact_point_centroid":[0.47616,-0.02015,-0.00194],"force_p95":0.13153,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12284,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.48607,-0.00923,0.22658]},{"body_a":"world","body_b":"grasp_target","contact_count":656.0,"contact_point_centroid":[0.60118,0.14812,-0.00199],"force_p95":0.12323,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12374,"mean_force":0.12265,"phase_index":5.0,"phase_name":"place_at_goal","phase_type":"descend","tcp_position_centroid":[0.62187,0.15787,0.25238]},{"body_a":"world","body_b":"grasp_target","contact_count":2888.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.47618,-0.02152,0.09592]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.60118,0.14812,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.62084,0.16771,0.22759]},{"body_a":"world","body_b":"grasp_target","contact_count":2032.0,"contact_point_centroid":[0.60118,0.14812,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_from_goal","phase_type":"retract","tcp_position_centroid":[0.61796,0.1666,0.31139]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5637.0,"contact_point_centroid":[0.47382,-0.00423,0.04858],"force_p95":0.07589,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07865,"mean_force":0.04007,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.4729,-0.02345,0.04624]},{"body_a":"left_finger","body_b":"right_finger","contact_count":379.0,"contact_point_centroid":[0.61142,0.13797,0.27493],"force_p95":0.01441,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01632,"mean_force":0.01127,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.61108,0.13797,0.27252]},{"body_a":"left_finger","body_b":"right_finger","contact_count":696.0,"contact_point_centroid":[0.62236,0.15786,0.25464],"force_p95":0.01097,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01275,"mean_force":0.0105,"phase_index":5.0,"phase_name":"place_at_goal","phase_type":"descend","tcp_position_centroid":[0.62186,0.15785,0.2524]}],"total_contact_groups":17},"final_pose_error":0.01989,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.60118,0.14812,0.01602],"final_tcp_position":[0.61871,0.16674,0.37707],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":9748.68151,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":564.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2252.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_above_object","tcp_end":[0.4738,-0.01882,0.15413],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12813,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":722.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2888.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_point","tcp_end":[0.48037,-0.02368,0.05404],"tcp_start":[0.4738,-0.01882,0.15413],"tcp_to_object_dist_end":0.02856,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47607,-0.02246,0.02499],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.29046,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.18809,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11499.0,"raw_peak_contact_force":0.2523,"subtask_id":"grasp_point","tcp_end":[0.47287,-0.02345,0.0462],"tcp_start":[0.48037,-0.02368,0.05404],"tcp_to_object_dist_end":0.02147,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":33.0,"n_steps":683.0,"n_steps_budget":900.0,"object_pos_end":[0.47941,-0.02189,0.17503],"object_pos_start":[0.47607,-0.02246,0.02499],"object_to_goal_dist_end":0.2369,"object_to_goal_dist_start":0.29046,"object_z_max":0.17486,"peak_contact_force":0.13009,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":24990.0,"raw_peak_contact_force":0.4801,"subtask_id":"object_lifted","tcp_end":[0.46959,-0.02332,0.20336],"tcp_start":[0.47287,-0.02345,0.0462],"tcp_to_object_dist_end":0.03002,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":694.0,"n_steps_budget":1000.0,"object_pos_end":[0.60124,0.14814,0.01599],"object_pos_start":[0.47941,-0.02189,0.17503],"object_to_goal_dist_end":0.17696,"object_to_goal_dist_start":0.2369,"object_z_max":0.21224,"peak_contact_force":9748.68151,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":9882.0,"raw_peak_contact_force":1.94976,"subtask_id":"near_goal","tcp_end":[0.62054,0.14862,0.27723],"tcp_start":[0.46959,-0.02332,0.20336],"tcp_to_object_dist_end":0.26195,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":164.0,"n_steps_budget":1000.0,"object_pos_end":[0.60118,0.14812,0.01602],"object_pos_start":[0.60124,0.14814,0.01599],"object_to_goal_dist_end":0.17695,"object_to_goal_dist_start":0.17696,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"place_at_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1352.0,"raw_peak_contact_force":0.12374,"subtask_id":"placed_at_goal","tcp_end":[0.62442,0.16861,0.22795],"tcp_start":[0.62054,0.14862,0.27723],"tcp_to_object_dist_end":0.21418,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.60118,0.14812,0.01602],"object_pos_start":[0.60118,0.14812,0.01602],"object_to_goal_dist_end":0.17695,"object_to_goal_dist_start":0.17695,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1031.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.61963,0.16724,0.24693],"tcp_start":[0.62442,0.16861,0.22795],"tcp_to_object_dist_end":0.23243,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":508.0,"n_steps_budget":900.0,"object_pos_end":[0.60118,0.14812,0.01602],"object_pos_start":[0.60118,0.14812,0.01602],"object_to_goal_dist_end":0.17695,"object_to_goal_dist_start":0.17695,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_from_goal","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2032.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.61871,0.16674,0.37707],"tcp_start":[0.61963,0.16724,0.24693],"tcp_to_object_dist_end":0.36195,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.00599,"average_solve_count":167.0,"average_success_count":167.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.26786,"descend_to_grasp.descend_speed":0.22169,"descend_to_grasp.descend_z_offset":0.00017,"descend_to_grasp.grasp_offset_x":0.00371,"descend_to_grasp.grasp_offset_y":0.0035,"lift_object.lift_distance":0.12669,"lift_object.lift_speed":0.09526,"place_at_goal.place_offset_x":0.009,"place_at_goal.place_offset_y":0.00464,"place_at_goal.place_offset_z":0.04675,"place_at_goal.place_speed":0.11778,"release_object.release_timeout":0.34916,"retract_from_goal.retract_speed":0.15159,"transport_to_goal.transport_speed":0.10664},"optimized_scores":{"best_composite_score":-0.17143,"best_fitness_score":0.70857,"best_task_score":0.49948},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":12.0,"contact_point_centroid":[0.6125,0.14863,-0.00413],"force_p95":1.42024,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.45436,"mean_force":1.24825,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.61797,0.19538,0.20343]},{"body_a":"world","body_b":"grasp_target","contact_count":644.0,"contact_point_centroid":[0.62043,0.1747,-0.00355],"force_p95":0.60245,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.07205,"mean_force":0.16949,"phase_index":5.0,"phase_name":"place_at_goal","phase_type":"descend","tcp_position_centroid":[0.62375,0.20169,0.1816]},{"body_a":"world","body_b":"grasp_target","contact_count":102.0,"contact_point_centroid":[0.45648,-0.02129,-0.00154],"force_p95":0.2814,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.39089,"mean_force":0.05269,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.44907,-0.02252,0.05279]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5314.0,"contact_point_centroid":[0.44812,-0.00353,0.10194],"force_p95":0.1331,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32189,"mean_force":0.0912,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.4468,-0.02243,0.10472]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6656.0,"contact_point_centroid":[0.52725,0.05878,0.1754],"force_p95":0.13762,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30399,"mean_force":0.10337,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52316,0.07689,0.17945]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8933.0,"contact_point_centroid":[0.44716,-0.04082,0.10337],"force_p95":0.11133,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28148,"mean_force":0.05921,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.44678,-0.02243,0.10346]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45863,-0.02609,-0.00228],"force_p95":0.20383,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.25395,"mean_force":0.14213,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.45142,-0.02259,0.0518]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6206.0,"contact_point_centroid":[0.52988,0.09769,0.17555],"force_p95":0.13776,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2324,"mean_force":0.10776,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52521,0.07956,0.1799]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2910.0,"contact_point_centroid":[0.45165,-0.00347,0.04861],"force_p95":0.10993,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14566,"mean_force":0.07015,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.45035,-0.02256,0.05074]},{"body_a":"world","body_b":"grasp_target","contact_count":2248.0,"contact_point_centroid":[0.45856,-0.02632,-0.00194],"force_p95":0.13153,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12284,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.47805,-0.01203,0.22682]},{"body_a":"world","body_b":"grasp_target","contact_count":2196.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.45606,-0.0236,0.10365]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.62044,0.17467,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.62631,0.20619,0.16103]},{"body_a":"world","body_b":"grasp_target","contact_count":1908.0,"contact_point_centroid":[0.62044,0.17467,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_from_goal","phase_type":"retract","tcp_position_centroid":[0.62238,0.2046,0.24463]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5179.0,"contact_point_centroid":[0.45042,-0.04143,0.05106],"force_p95":0.07744,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08287,"mean_force":0.04235,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.45037,-0.02256,0.05076]},{"body_a":"left_finger","body_b":"right_finger","contact_count":448.0,"contact_point_centroid":[0.62645,0.20364,0.17637],"force_p95":0.01386,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01775,"mean_force":0.01102,"phase_index":5.0,"phase_name":"place_at_goal","phase_type":"descend","tcp_position_centroid":[0.62588,0.20362,0.17399]},{"body_a":"left_finger","body_b":"right_finger","contact_count":224.0,"contact_point_centroid":[0.62953,0.20729,0.15996],"force_p95":0.01094,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01096,"mean_force":0.00998,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.62906,0.20727,0.1579]}],"total_contact_groups":16},"final_pose_error":0.01998,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.62044,0.17467,0.01602],"final_tcp_position":[0.62299,0.20474,0.31028],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":9.42254,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":563.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2248.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_above_object","tcp_end":[0.45739,-0.02455,0.15447],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12846,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":549.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2196.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_point","tcp_end":[0.4576,-0.02279,0.05794],"tcp_start":[0.45739,-0.02455,0.15447],"tcp_to_object_dist_end":0.03213,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45854,-0.02363,0.02503],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30188,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.19628,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":9889.0,"raw_peak_contact_force":0.25395,"subtask_id":"grasp_point","tcp_end":[0.45033,-0.02256,0.05072],"tcp_start":[0.4576,-0.02279,0.05794],"tcp_to_object_dist_end":0.02699,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":20.0,"n_steps":486.0,"n_steps_budget":840.0,"object_pos_end":[0.45616,-0.02383,0.13189],"object_pos_start":[0.45854,-0.02363,0.02503],"object_to_goal_dist_end":0.29056,"object_to_goal_dist_start":0.30188,"object_z_max":0.13172,"peak_contact_force":0.13172,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":14349.0,"raw_peak_contact_force":0.39089,"subtask_id":"object_lifted","tcp_end":[0.44679,-0.02242,0.163],"tcp_start":[0.45033,-0.02256,0.05072],"tcp_to_object_dist_end":0.03252,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":835.0,"n_steps_budget":1000.0,"object_pos_end":[0.61898,0.1708,0.01164],"object_pos_start":[0.45616,-0.02383,0.13189],"object_to_goal_dist_end":0.10966,"object_to_goal_dist_start":0.29056,"object_z_max":0.15897,"peak_contact_force":9.42254,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":12874.0,"raw_peak_contact_force":1.45436,"subtask_id":"near_goal","tcp_end":[0.61856,0.19619,0.20354],"tcp_start":[0.44679,-0.02242,0.163],"tcp_to_object_dist_end":0.19357,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":161.0,"n_steps_budget":1000.0,"object_pos_end":[0.62044,0.17467,0.01601],"object_pos_start":[0.61898,0.1708,0.01164],"object_to_goal_dist_end":0.10414,"object_to_goal_dist_start":0.10966,"object_z_max":0.01659,"peak_contact_force":0.12259,"phase_name":"place_at_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1092.0,"raw_peak_contact_force":1.07205,"subtask_id":"placed_at_goal","tcp_end":[0.63071,0.20772,0.1617],"tcp_start":[0.61856,0.19619,0.20354],"tcp_to_object_dist_end":0.14975,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.62044,0.17467,0.01602],"object_pos_start":[0.62044,0.17467,0.01601],"object_to_goal_dist_end":0.10413,"object_to_goal_dist_start":0.10414,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1024.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.62469,0.20554,0.18017],"tcp_start":[0.63071,0.20772,0.1617],"tcp_to_object_dist_end":0.16709,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":477.0,"n_steps_budget":630.0,"object_pos_end":[0.62044,0.17467,0.01602],"object_pos_start":[0.62044,0.17467,0.01602],"object_to_goal_dist_end":0.10413,"object_to_goal_dist_start":0.10413,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_from_goal","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1908.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.62299,0.20474,0.31028],"tcp_start":[0.62469,0.20554,0.18017],"tcp_to_object_dist_end":0.2958,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```