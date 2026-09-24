## Search State

- **Seed**: 1
- **Iteration**: 6 / 15

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

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.792, which indicates the subtask decomposition is already effective.
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

## Current Skill (Q=0.090) — your mutation base

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
    tolerance: 0.005
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
      - -0.04
      - 0.04
      default: -0.02
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
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings:
    - place_offset_x: status=consumed; consumers=target.offset.x (add)
    - place_offset_y: status=consumed; consumers=target.offset.y (add)
    - place_offset_z: status=consumed; consumers=target.offset.z (add)
    - place_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: 0.090
- **task_score** (E): 0.792
- **fitness_score**: 0.860  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.770

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1532 |
| descend_to_grasp | 1.00 | 1.00 | 0.0986 |
| grasp | 1.00 | 1.00 | 0.0108 |
| lift_object | 1.00 | 1.00 | 0.1295 |
| transport_to_goal | 1.00 | 1.00 | 0.2452 |
| place_at_goal | 1.00 | 0.67 | 0.0736 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.476, -0.000, 0.153) | (0.479, -0.000, 0.030)→(0.479, -0.000, 0.026) | 0.276→0.278 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.476, -0.000, 0.153)→(0.479, 0.001, 0.055) | (0.479, -0.000, 0.026)→(0.479, -0.000, 0.026) | 0.278→0.278 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp | grasp | 1.00 / step_budget | (0.479, 0.001, 0.055)→(0.471, 0.001, 0.047) | (0.479, -0.000, 0.026)→(0.479, 0.000, 0.025) | 0.278→0.278 | 1.00 / 42.333 | 0.168 | 0.201 |
| lift_object | lift | 1.00 / step_budget | (0.471, 0.001, 0.047)→(0.467, 0.001, 0.177) | (0.479, 0.000, 0.025)→(0.476, 0.000, 0.150) | 0.278→0.248 | 1.00 / 29.000 | 0.116 | 0.421 |
| transport_to_goal | approach | 1.00 / step_budget | (0.467, 0.001, 0.177)→(0.599, 0.192, 0.238) | (0.476, 0.000, 0.150)→(0.602, 0.195, 0.152) | 0.248→0.074 | 1.00 / 16.667 | 0.344 | 0.717 |
| place_at_goal | descend | 1.00 / step_budget | (0.599, 0.192, 0.238)→(0.595, 0.199, 0.166) | (0.602, 0.195, 0.152)→(0.594, 0.208, 0.110) | 0.074→0.045 | 0.67 / 8.667 | 3249.653 | 0.442 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.151
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 1.000
- phase_score: 0.686
- phase_breakdown.near_goal_score: 0.672
- phase_breakdown.reach_above_object_score: 0.905
- phase_breakdown.object_lifted_score: 0.737
- phase_breakdown.grasp_point_score: 0.681
- phase_breakdown.placed_at_goal_score: 0.436
- grasp_place_fitness: 0.968

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.968
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.111
- **K-run variance**: 0.0096
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.288


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.01136,"average_solve_count":264.0,"average_success_count":264.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.04664,"descend_to_grasp.descend_speed":0.03522,"descend_to_grasp.grasp_offset_x":0.00254,"descend_to_grasp.grasp_offset_y":0.0005,"grasp.grasp_retry_offset_x":-0.00258,"grasp.grasp_retry_offset_y":-4e-05,"lift_object.lift_distance":0.15797,"lift_object.lift_speed":0.05017,"place_at_goal.place_offset_x":-0.0137,"place_at_goal.place_offset_y":0.01408,"place_at_goal.place_offset_z":0.02149,"place_at_goal.place_speed":0.02501,"transport_to_goal.transport_speed":0.13335},"optimized_scores":{"best_composite_score":0.19824,"best_fitness_score":0.96824,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":107.0,"contact_point_centroid":[0.4972,0.04415,-0.00133],"force_p95":0.4396,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.45998,"mean_force":0.11249,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49004,0.04423,0.04501]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9108.0,"contact_point_centroid":[0.55477,0.22254,0.19718],"force_p95":0.14168,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31763,"mean_force":0.09826,"phase_index":5.0,"phase_name":"place_at_goal","phase_type":"descend","tcp_position_centroid":[0.55102,0.24104,0.19996]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":15223.0,"contact_point_centroid":[0.48758,0.06311,0.11698],"force_p95":0.07372,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29747,"mean_force":0.05125,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48742,0.044,0.11513]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14490.0,"contact_point_centroid":[0.48716,0.02485,0.11457],"force_p95":0.07717,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2768,"mean_force":0.05303,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48741,0.044,0.11225]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10948.0,"contact_point_centroid":[0.5538,0.25908,0.19728],"force_p95":0.12698,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24617,"mean_force":0.08149,"phase_index":5.0,"phase_name":"place_at_goal","phase_type":"descend","tcp_position_centroid":[0.55103,0.24101,0.20007]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9417.0,"contact_point_centroid":[0.51869,0.11028,0.20784],"force_p95":0.11426,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18213,"mean_force":0.06363,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.51776,0.12935,0.20697]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50119,0.04498,-0.00206],"force_p95":0.1398,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18137,"mean_force":0.12743,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.4924,0.04446,0.04488]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11406.0,"contact_point_centroid":[0.52052,0.15324,0.2093],"force_p95":0.09018,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15444,"mean_force":0.05329,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.51968,0.13436,0.20836]},{"body_a":"world","body_b":"grasp_target","contact_count":3444.0,"contact_point_centroid":[0.50118,0.04505,-0.00196],"force_p95":0.12631,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12277,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.49744,0.02147,0.22317]},{"body_a":"world","body_b":"grasp_target","contact_count":3572.0,"contact_point_centroid":[0.50118,0.04505,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.49701,0.044,0.08867]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4829.0,"contact_point_centroid":[0.49145,0.02517,0.04557],"force_p95":0.0703,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11688,"mean_force":0.04476,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49124,0.04435,0.04362]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4909.0,"contact_point_centroid":[0.49143,0.06357,0.04544],"force_p95":0.07064,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0807,"mean_force":0.04477,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49125,0.04435,0.04362]}],"total_contact_groups":12},"final_pose_error":0.02106,"key_states":{"actual_goal_position":[0.56442,0.24486,0.14677],"final_object_position":[0.55231,0.25419,0.13936],"final_tcp_position":[0.54945,0.24675,0.18538],"realised_goal_position":[0.56442,0.24486,0.14677],"realised_object_initial_position":[0.50118,0.04505,0.03]},"peak_contact_force":0.45998,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":862.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.03],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.23992,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3444.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_above_object","tcp_end":[0.49728,0.04256,0.15182],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12589,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":893.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3572.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_point","tcp_end":[0.49892,0.04507,0.05204],"tcp_start":[0.49728,0.04256,0.15182],"tcp_to_object_dist_end":0.02612,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5011,0.04456,0.02577],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24244,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.13794,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11538.0,"raw_peak_contact_force":0.18137,"subtask_id":"grasp_point","tcp_end":[0.49121,0.04435,0.04359],"tcp_start":[0.49892,0.04507,0.05204],"tcp_to_object_dist_end":0.02038,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":752.0,"n_steps_budget":1000.0,"object_pos_end":[0.49302,0.04386,0.16506],"object_pos_start":[0.5011,0.04456,0.02577],"object_to_goal_dist_end":0.21409,"object_to_goal_dist_start":0.24244,"object_z_max":0.16489,"peak_contact_force":0.08157,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":29820.0,"raw_peak_contact_force":0.45998,"subtask_id":"object_lifted","tcp_end":[0.4877,0.04403,0.18705],"tcp_start":[0.49121,0.04435,0.04359],"tcp_to_object_dist_end":0.02262,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":30.0,"n_steps":590.0,"n_steps_budget":1000.0,"object_pos_end":[0.56333,0.23056,0.2079],"object_pos_start":[0.49302,0.04386,0.16506],"object_to_goal_dist_end":0.06279,"object_to_goal_dist_start":0.21409,"object_z_max":0.20786,"peak_contact_force":0.13434,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":20823.0,"raw_peak_contact_force":0.18213,"subtask_id":"near_goal","tcp_end":[0.55673,0.23043,0.2355],"tcp_start":[0.4877,0.04403,0.18705],"tcp_to_object_dist_end":0.02837,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.55231,0.25419,0.13936],"object_pos_start":[0.56333,0.23056,0.2079],"object_to_goal_dist_end":0.01698,"object_to_goal_dist_start":0.06279,"object_z_max":0.2079,"peak_contact_force":0.0,"phase_name":"place_at_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":20056.0,"raw_peak_contact_force":0.31763,"subtask_id":"placed_at_goal","tcp_end":[0.54945,0.24675,0.18538],"tcp_start":[0.55673,0.23043,0.2355],"tcp_to_object_dist_end":0.04671,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.02201,"average_solve_count":318.0,"average_success_count":318.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.04727,"descend_to_grasp.descend_speed":0.02422,"descend_to_grasp.grasp_offset_x":0.00825,"descend_to_grasp.grasp_offset_y":0.00417,"grasp.grasp_retry_offset_x":-0.00122,"grasp.grasp_retry_offset_y":0.00274,"lift_object.lift_distance":0.13984,"lift_object.lift_speed":0.07282,"place_at_goal.place_offset_x":-0.00982,"place_at_goal.place_offset_y":-0.00543,"place_at_goal.place_offset_z":0.0106,"place_at_goal.place_speed":0.03866,"transport_to_goal.transport_speed":0.0599},"optimized_scores":{"best_composite_score":0.11104,"best_fitness_score":0.88104,"best_task_score":0.83349},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":119.0,"contact_point_centroid":[0.47315,-0.01507,-0.00173],"force_p95":0.35563,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.44936,"mean_force":0.07549,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.47057,-0.01587,0.04957]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9095.0,"contact_point_centroid":[0.46921,0.00326,0.10489],"force_p95":0.12105,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34122,"mean_force":0.06789,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46817,-0.01581,0.10525]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11594.0,"contact_point_centroid":[0.46844,-0.03439,0.11021],"force_p95":0.09503,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29899,"mean_force":0.05386,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46817,-0.01581,0.10919]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2219.0,"contact_point_centroid":[0.6236,0.13266,0.23432],"force_p95":0.13924,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26961,"mean_force":0.11436,"phase_index":5.0,"phase_name":"place_at_goal","phase_type":"descend","tcp_position_centroid":[0.61881,0.15086,0.23878]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47622,-0.01997,-0.00236],"force_p95":0.21698,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.26594,"mean_force":0.14803,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.47313,-0.01591,0.04845]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2540.0,"contact_point_centroid":[0.62347,0.16888,0.23443],"force_p95":0.11995,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26472,"mean_force":0.09962,"phase_index":5.0,"phase_name":"place_at_goal","phase_type":"descend","tcp_position_centroid":[0.61881,0.15082,0.23947]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12566.0,"contact_point_centroid":[0.53568,0.0393,0.21512],"force_p95":0.11715,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22314,"mean_force":0.0645,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.53408,0.05735,0.21603]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8319.0,"contact_point_centroid":[0.54024,0.07985,0.2149],"force_p95":0.1448,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22197,"mean_force":0.09502,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.53773,0.06121,0.21855]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4055.0,"contact_point_centroid":[0.47289,0.00328,0.04765],"force_p95":0.0959,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15624,"mean_force":0.05714,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.47202,-0.01589,0.0473]},{"body_a":"world","body_b":"grasp_target","contact_count":2872.0,"contact_point_centroid":[0.47616,-0.02015,-0.00195],"force_p95":0.12878,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.1228,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.48598,-0.00926,0.22625]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.47596,-0.01708,0.09205]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5206.0,"contact_point_centroid":[0.47217,-0.03512,0.04855],"force_p95":0.08111,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08675,"mean_force":0.04279,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.47203,-0.01589,0.04731]}],"total_contact_groups":12},"final_pose_error":0.00488,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.62281,0.15106,0.1654],"final_tcp_position":[0.61807,0.1522,0.20359],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":0.44936,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":719.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2872.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_above_object","tcp_end":[0.47389,-0.01882,0.15417],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12817,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_point","tcp_end":[0.47944,-0.01602,0.05504],"tcp_start":[0.47389,-0.01882,0.15417],"tcp_to_object_dist_end":0.02949,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47612,-0.01735,0.02457],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.2875,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.21692,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11061.0,"raw_peak_contact_force":0.26594,"subtask_id":"grasp_point","tcp_end":[0.47199,-0.01589,0.04727],"tcp_start":[0.47944,-0.01602,0.05504],"tcp_to_object_dist_end":0.02312,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":32.0,"n_steps":586.0,"n_steps_budget":1000.0,"object_pos_end":[0.47808,-0.01759,0.14569],"object_pos_start":[0.47612,-0.01735,0.02457],"object_to_goal_dist_end":0.23818,"object_to_goal_dist_start":0.2875,"object_z_max":0.14552,"peak_contact_force":0.13546,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":20808.0,"raw_peak_contact_force":0.44936,"subtask_id":"object_lifted","tcp_end":[0.46832,-0.01581,0.17269],"tcp_start":[0.47199,-0.01589,0.04727],"tcp_to_object_dist_end":0.02876,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":16.0,"n_steps":852.0,"n_steps_budget":1000.0,"object_pos_end":[0.62599,0.14806,0.24055],"object_pos_start":[0.47808,-0.01759,0.14569],"object_to_goal_dist_end":0.05203,"object_to_goal_dist_start":0.23818,"object_z_max":0.24047,"peak_contact_force":0.12911,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":20885.0,"raw_peak_contact_force":0.22314,"subtask_id":"near_goal","tcp_end":[0.6211,0.14996,0.27567],"tcp_start":[0.46832,-0.01581,0.17269],"tcp_to_object_dist_end":0.03551,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":18.0,"n_steps":283.0,"n_steps_budget":1000.0,"object_pos_end":[0.62281,0.15106,0.1654],"object_pos_start":[0.62599,0.14806,0.24055],"object_to_goal_dist_end":0.02732,"object_to_goal_dist_start":0.05203,"object_z_max":0.24055,"peak_contact_force":0.11618,"phase_name":"place_at_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4759.0,"raw_peak_contact_force":0.26961,"subtask_id":"placed_at_goal","tcp_end":[0.61807,0.1522,0.20359],"tcp_start":[0.6211,0.14996,0.27567],"tcp_to_object_dist_end":0.03851,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.13699,"average_solve_count":292.0,"average_success_count":292.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.03946,"descend_to_grasp.descend_speed":0.0407,"descend_to_grasp.grasp_offset_x":0.00336,"descend_to_grasp.grasp_offset_y":-0.00095,"grasp.grasp_retry_offset_x":0.0028,"grasp.grasp_retry_offset_y":-0.00267,"lift_object.lift_distance":0.13388,"lift_object.lift_speed":0.08197,"place_at_goal.place_offset_x":-0.00872,"place_at_goal.place_offset_y":-0.00759,"place_at_goal.place_offset_z":-0.00644,"place_at_goal.place_speed":0.02552,"transport_to_goal.transport_speed":0.11283},"optimized_scores":{"best_composite_score":-0.03938,"best_fitness_score":0.73062,"best_task_score":0.54166},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":70.0,"contact_point_centroid":[0.60869,0.21407,-0.00748],"force_p95":1.52456,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.746,"mean_force":0.739,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.61658,0.19339,0.20352]},{"body_a":"world","body_b":"grasp_target","contact_count":3917.0,"contact_point_centroid":[0.60601,0.21782,-0.00216],"force_p95":0.14096,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.73917,"mean_force":0.12538,"phase_index":5.0,"phase_name":"place_at_goal","phase_type":"descend","tcp_position_centroid":[0.61624,0.19764,0.13119]},{"body_a":"world","body_b":"grasp_target","contact_count":95.0,"contact_point_centroid":[0.45625,-0.02768,-0.00133],"force_p95":0.25411,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.35431,"mean_force":0.06115,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.44886,-0.02659,0.05215]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6744.0,"contact_point_centroid":[0.44761,-0.04545,0.10122],"force_p95":0.13441,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33851,"mean_force":0.08152,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.44647,-0.02648,0.10279]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9595.0,"contact_point_centroid":[0.44734,-0.00807,0.10621],"force_p95":0.10609,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27253,"mean_force":0.05874,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.4464,-0.02648,0.10608]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6452.0,"contact_point_centroid":[0.52599,0.09112,0.17958],"force_p95":0.13632,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26628,"mean_force":0.10369,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52165,0.0729,0.18311]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6161.0,"contact_point_centroid":[0.52998,0.05947,0.18007],"force_p95":0.1365,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21649,"mean_force":0.1065,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52531,0.07762,0.18386]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45858,-0.02634,-0.00205],"force_p95":0.1412,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.1547,"mean_force":0.12687,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.4511,-0.02668,0.05163]},{"body_a":"world","body_b":"grasp_target","contact_count":2892.0,"contact_point_centroid":[0.45856,-0.02632,-0.00195],"force_p95":0.12867,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12279,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.47786,-0.01206,0.22653]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4236.0,"contact_point_centroid":[0.44936,-0.04583,0.05093],"force_p95":0.08685,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12826,"mean_force":0.05403,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.45003,-0.02664,0.05058]},{"body_a":"world","body_b":"grasp_target","contact_count":2608.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.45584,-0.0257,0.1035]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4880.0,"contact_point_centroid":[0.45007,-0.0077,0.05095],"force_p95":0.06831,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08625,"mean_force":0.04369,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.45004,-0.02664,0.05058]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4063.0,"contact_point_centroid":[0.61672,0.1977,0.13113],"force_p95":0.01104,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01558,"mean_force":0.01049,"phase_index":5.0,"phase_name":"place_at_goal","phase_type":"descend","tcp_position_centroid":[0.61619,0.19768,0.12888]}],"total_contact_groups":13},"final_pose_error":0.0054,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.60569,0.21818,0.02602],"final_tcp_position":[0.6165,0.19857,0.10858],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":9748.84413,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":724.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2892.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_above_object","tcp_end":[0.4575,-0.02457,0.15447],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12846,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":652.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2608.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_point","tcp_end":[0.45728,-0.02692,0.05777],"tcp_start":[0.4575,-0.02457,0.15447],"tcp_to_object_dist_end":0.03178,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.4585,-0.02673,0.02566],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.3041,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.14801,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10916.0,"raw_peak_contact_force":0.1547,"subtask_id":"grasp_point","tcp_end":[0.45001,-0.02664,0.05055],"tcp_start":[0.45728,-0.02692,0.05777],"tcp_to_object_dist_end":0.0263,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":18.0,"n_steps":530.0,"n_steps_budget":1000.0,"object_pos_end":[0.45588,-0.02503,0.13948],"object_pos_start":[0.4585,-0.02673,0.02566],"object_to_goal_dist_end":0.29225,"object_to_goal_dist_start":0.3041,"object_z_max":0.1393,"peak_contact_force":0.13153,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":16434.0,"raw_peak_contact_force":0.35431,"subtask_id":"object_lifted","tcp_end":[0.44646,-0.02647,0.16997],"tcp_start":[0.45001,-0.02664,0.05055],"tcp_to_object_dist_end":0.03195,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":826.0,"n_steps_budget":1000.0,"object_pos_end":[0.61542,0.20707,0.0081],"object_pos_start":[0.45588,-0.02503,0.13948],"object_to_goal_dist_end":0.10704,"object_to_goal_dist_start":0.29225,"object_z_max":0.16024,"peak_contact_force":0.76764,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":12683.0,"raw_peak_contact_force":1.746,"subtask_id":"near_goal","tcp_end":[0.61844,0.19585,0.20385],"tcp_start":[0.44646,-0.02647,0.16997],"tcp_to_object_dist_end":0.1961,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.60569,0.21818,0.02602],"object_pos_start":[0.61542,0.20707,0.0081],"object_to_goal_dist_end":0.09197,"object_to_goal_dist_start":0.10704,"object_z_max":0.02746,"peak_contact_force":9748.84413,"phase_name":"place_at_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":7980.0,"raw_peak_contact_force":0.73917,"subtask_id":"placed_at_goal","tcp_end":[0.6165,0.19857,0.10858],"tcp_start":[0.61844,0.19585,0.20385],"tcp_to_object_dist_end":0.08555,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```