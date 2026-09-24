## Search State

- **Seed**: 1
- **Iteration**: 7 / 15

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

## Current Skill (Q=0.077) — your mutation base

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

- **Composite score**: 0.077
- **task_score** (E): 0.763
- **fitness_score**: 0.847  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.770

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1532 |
| descend_to_grasp | 1.00 | 1.00 | 0.0994 |
| grasp | 1.00 | 1.00 | 0.0108 |
| lift_object | 1.00 | 1.00 | 0.1647 |
| transport_to_goal | 1.00 | 1.00 | 0.1472 |
| place_at_goal | 0.67 | 1.00 | 0.0666 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.476, -0.000, 0.153) | (0.479, -0.000, 0.030)→(0.479, -0.000, 0.026) | 0.276→0.278 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.476, -0.000, 0.153)→(0.478, 0.001, 0.054) | (0.479, -0.000, 0.026)→(0.479, -0.000, 0.026) | 0.278→0.278 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp | grasp | 1.00 / step_budget | (0.478, 0.001, 0.054)→(0.470, 0.001, 0.046) | (0.479, -0.000, 0.026)→(0.479, 0.000, 0.026) | 0.278→0.278 | 1.00 / 42.000 | 0.148 | 0.186 |
| lift_object | lift | 1.00 / step_budget | (0.470, 0.001, 0.046)→(0.467, 0.001, 0.211) | (0.479, 0.000, 0.026)→(0.470, 0.000, 0.186) | 0.278→0.253 | 1.00 / 32.000 | 0.091 | 0.387 |
| transport_to_goal | approach | 1.00 / step_budget | (0.525, 0.074, 0.210)→(0.600, 0.193, 0.239) | (0.470, 0.000, 0.186)→(0.598, 0.186, 0.189) | 0.253→0.054 | 1.00 / 27.667 | 0.368 | 0.554 |
| place_at_goal | descend | 0.67 / step_budget | (0.600, 0.193, 0.239)→(0.599, 0.200, 0.174) | (0.600, 0.186, 0.156)→(0.600, 0.189, 0.106) | 0.081→0.051 | 1.00 / 24.000 | 91001.476 | 0.429 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.242
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 1.000
- phase_score: 0.675
- phase_breakdown.near_goal_score: 0.671
- phase_breakdown.reach_above_object_score: 0.905
- phase_breakdown.object_lifted_score: 0.587
- phase_breakdown.grasp_point_score: 0.677
- phase_breakdown.placed_at_goal_score: 0.536
- grasp_place_fitness: 0.968

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.968
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.094
- **K-run variance**: 0.0113
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.279


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.952,"average_solve_count":375.0,"average_success_count":375.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.06298,"descend_to_grasp.descend_speed":0.03274,"descend_to_grasp.grasp_offset_x":0.00203,"descend_to_grasp.grasp_offset_y":0.00145,"grasp.grasp_retry_offset_x":-0.00359,"grasp.grasp_retry_offset_y":-0.00078,"lift_object.lift_distance":0.17368,"lift_object.lift_speed":0.0377,"place_at_goal.place_offset_x":-0.01404,"place_at_goal.place_offset_y":0.00359,"place_at_goal.place_offset_z":0.02564,"place_at_goal.place_speed":0.02404,"transport_to_goal.transport_speed":0.03918},"optimized_scores":{"best_composite_score":0.19809,"best_fitness_score":0.96809,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":110.0,"contact_point_centroid":[0.49705,0.04498,-0.00135],"force_p95":0.40007,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.42374,"mean_force":0.12303,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48952,0.04514,0.04474]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17181.0,"contact_point_centroid":[0.48712,0.064,0.12488],"force_p95":0.07315,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26696,"mean_force":0.05076,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48695,0.04491,0.12306]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16020.0,"contact_point_centroid":[0.48691,0.02576,0.12193],"force_p95":0.07678,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25343,"mean_force":0.05379,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48694,0.04491,0.11978]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7231.0,"contact_point_centroid":[0.55076,0.25573,0.20307],"force_p95":0.06826,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20428,"mean_force":0.04553,"phase_index":5.0,"phase_name":"place_at_goal","phase_type":"descend","tcp_position_centroid":[0.55105,0.23659,0.20286]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6558.0,"contact_point_centroid":[0.54986,0.21742,0.2039],"force_p95":0.07239,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16448,"mean_force":0.04883,"phase_index":5.0,"phase_name":"place_at_goal","phase_type":"descend","tcp_position_centroid":[0.55104,0.23661,0.20278]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50118,0.04506,-0.00203],"force_p95":0.13177,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.1518,"mean_force":0.12527,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.4919,0.04538,0.04483]},{"body_a":"world","body_b":"grasp_target","contact_count":3300.0,"contact_point_centroid":[0.50118,0.04505,-0.00195],"force_p95":0.12693,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12277,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.49739,0.02148,0.22313]},{"body_a":"world","body_b":"grasp_target","contact_count":3388.0,"contact_point_centroid":[0.50118,0.04505,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.49661,0.04452,0.09008]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4842.0,"contact_point_centroid":[0.49094,0.06447,0.04539],"force_p95":0.06767,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10569,"mean_force":0.04489,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49075,0.04527,0.04357]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11774.0,"contact_point_centroid":[0.52064,0.12125,0.21998],"force_p95":0.07468,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10385,"mean_force":0.052,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52174,0.14044,0.21801]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":13595.0,"contact_point_centroid":[0.52057,0.15716,0.21892],"force_p95":0.06721,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09333,"mean_force":0.04555,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52084,0.1381,0.21754]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4880.0,"contact_point_centroid":[0.49096,0.02608,0.04554],"force_p95":0.06774,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08393,"mean_force":0.04465,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49075,0.04527,0.04357]}],"total_contact_groups":12},"final_pose_error":0.00499,"key_states":{"actual_goal_position":[0.56442,0.24486,0.14677],"final_object_position":[0.5493,0.24397,0.14619],"final_tcp_position":[0.54753,0.2444,0.17298],"realised_goal_position":[0.56442,0.24486,0.14677],"realised_object_initial_position":[0.50118,0.04505,0.03]},"peak_contact_force":0.42374,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":826.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.03],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.23992,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3300.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_above_object","tcp_end":[0.49721,0.04257,0.15174],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12581,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":847.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3388.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_point","tcp_end":[0.49842,0.04599,0.05198],"tcp_start":[0.49721,0.04257,0.15174],"tcp_to_object_dist_end":0.02612,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50109,0.04519,0.02587],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24187,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.13149,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11522.0,"raw_peak_contact_force":0.1518,"subtask_id":"grasp_point","tcp_end":[0.49072,0.04526,0.04354],"tcp_start":[0.49842,0.04599,0.05198],"tcp_to_object_dist_end":0.02048,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":851.0,"n_steps_budget":1000.0,"object_pos_end":[0.49241,0.04473,0.18043],"object_pos_start":[0.50109,0.04519,0.02587],"object_to_goal_dist_end":0.21534,"object_to_goal_dist_start":0.24187,"object_z_max":0.18026,"peak_contact_force":0.08099,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":33311.0,"raw_peak_contact_force":0.42374,"subtask_id":"object_lifted","tcp_end":[0.48733,0.04495,0.20277],"tcp_start":[0.49072,0.04526,0.04354],"tcp_to_object_dist_end":0.0229,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":635.0,"n_steps_budget":1000.0,"object_pos_end":[0.55896,0.22966,0.21079],"object_pos_start":[0.49241,0.04473,0.18043],"object_to_goal_dist_end":0.06603,"object_to_goal_dist_start":0.21534,"object_z_max":0.21075,"peak_contact_force":0.07309,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":25369.0,"raw_peak_contact_force":0.10385,"subtask_id":"near_goal","tcp_end":[0.55644,0.22999,0.23614],"tcp_start":[0.48733,0.04495,0.20277],"tcp_to_object_dist_end":0.02547,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":329.0,"n_steps_budget":1000.0,"object_pos_end":[0.5493,0.24397,0.14619],"object_pos_start":[0.55896,0.22966,0.21079],"object_to_goal_dist_end":0.01515,"object_to_goal_dist_start":0.06603,"object_z_max":0.21079,"peak_contact_force":0.07273,"phase_name":"place_at_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":13789.0,"raw_peak_contact_force":0.20428,"subtask_id":"placed_at_goal","tcp_end":[0.54753,0.2444,0.17298],"tcp_start":[0.55644,0.22999,0.23614],"tcp_to_object_dist_end":0.02685,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.84878,"average_solve_count":410.0,"average_success_count":410.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.04933,"descend_to_grasp.descend_speed":0.03506,"descend_to_grasp.grasp_offset_x":0.00781,"descend_to_grasp.grasp_offset_y":0.00015,"grasp.grasp_retry_offset_x":0.00131,"grasp.grasp_retry_offset_y":0.00102,"lift_object.lift_distance":0.19203,"lift_object.lift_speed":0.03748,"place_at_goal.place_offset_x":0.00887,"place_at_goal.place_offset_y":-0.0101,"place_at_goal.place_offset_z":-0.03663,"place_at_goal.place_speed":0.0225,"transport_to_goal.transport_speed":0.04675},"optimized_scores":{"best_composite_score":0.094,"best_fitness_score":0.864,"best_task_score":0.78857},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":110.0,"contact_point_centroid":[0.47176,-0.01937,-0.00139],"force_p95":0.37137,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.40365,"mean_force":0.11301,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.47057,-0.01968,0.04597]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":15746.0,"contact_point_centroid":[0.46901,-0.0004,0.13428],"force_p95":0.07863,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2645,"mean_force":0.05722,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46814,-0.0196,0.13186]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18974.0,"contact_point_centroid":[0.46834,-0.0386,0.13315],"force_p95":0.07196,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26227,"mean_force":0.04861,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46814,-0.0196,0.13118]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11891.0,"contact_point_centroid":[0.62595,0.16671,0.21306],"force_p95":0.11013,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21367,"mean_force":0.0776,"phase_index":5.0,"phase_name":"place_at_goal","phase_type":"descend","tcp_position_centroid":[0.62566,0.1479,0.21538]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14371.0,"contact_point_centroid":[0.62518,0.12937,0.21387],"force_p95":0.09564,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20875,"mean_force":0.06496,"phase_index":5.0,"phase_name":"place_at_goal","phase_type":"descend","tcp_position_centroid":[0.62561,0.14788,0.21554]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47615,-0.02003,-0.00205],"force_p95":0.1359,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17036,"mean_force":0.12659,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.47292,-0.01973,0.04588]},{"body_a":"world","body_b":"grasp_target","contact_count":2868.0,"contact_point_centroid":[0.47616,-0.02015,-0.00195],"force_p95":0.12883,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.1228,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.48596,-0.00927,0.22617]},{"body_a":"world","body_b":"grasp_target","contact_count":3696.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.47573,-0.01942,0.09197]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4356.0,"contact_point_centroid":[0.47237,-0.00041,0.04827],"force_p95":0.075,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11729,"mean_force":0.04931,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.4718,-0.0197,0.04472]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":13159.0,"contact_point_centroid":[0.54637,0.08628,0.2496],"force_p95":0.0815,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10803,"mean_force":0.05672,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.54548,0.06713,0.24896]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":15300.0,"contact_point_centroid":[0.54478,0.04729,0.24941],"force_p95":0.07217,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09578,"mean_force":0.048,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.54468,0.06626,0.24865]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5377.0,"contact_point_centroid":[0.47148,-0.0388,0.04743],"force_p95":0.06439,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08331,"mean_force":0.04101,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.4718,-0.0197,0.04473]}],"total_contact_groups":12},"final_pose_error":0.0368,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.62935,0.14767,0.15636],"final_tcp_position":[0.62934,0.14784,0.18849],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":0.40365,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":718.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2868.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_above_object","tcp_end":[0.47387,-0.01883,0.15412],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12812,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":924.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3696.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_point","tcp_end":[0.47925,-0.01988,0.05247],"tcp_start":[0.47387,-0.01883,0.15412],"tcp_to_object_dist_end":0.02663,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47607,-0.01964,0.02581],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28823,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.13332,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11533.0,"raw_peak_contact_force":0.17036,"subtask_id":"grasp_point","tcp_end":[0.47177,-0.0197,0.04469],"tcp_start":[0.47925,-0.01988,0.05247],"tcp_to_object_dist_end":0.01937,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":907.0,"n_steps_budget":1000.0,"object_pos_end":[0.47106,-0.01954,0.19988],"object_pos_start":[0.47607,-0.01964,0.02581],"object_to_goal_dist_end":0.24033,"object_to_goal_dist_start":0.28823,"object_z_max":0.1997,"peak_contact_force":0.07933,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":34830.0,"raw_peak_contact_force":0.40365,"subtask_id":"object_lifted","tcp_end":[0.46858,-0.01961,0.2221],"tcp_start":[0.47177,-0.0197,0.04469],"tcp_to_object_dist_end":0.02235,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":39.0,"n_steps":765.0,"n_steps_budget":1000.0,"object_pos_end":[0.62168,0.14804,0.25225],"object_pos_start":[0.47106,-0.01954,0.19988],"object_to_goal_dist_end":0.06398,"object_to_goal_dist_start":0.24033,"object_z_max":0.2522,"peak_contact_force":0.1043,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":28459.0,"raw_peak_contact_force":0.10803,"subtask_id":"near_goal","tcp_end":[0.62001,0.14842,0.27769],"tcp_start":[0.46858,-0.01961,0.2221],"tcp_to_object_dist_end":0.02549,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":21.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.62935,0.14767,0.15636],"object_pos_start":[0.62168,0.14804,0.25225],"object_to_goal_dist_end":0.03563,"object_to_goal_dist_start":0.06398,"object_z_max":0.25225,"peak_contact_force":0.12185,"phase_name":"place_at_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":26262.0,"raw_peak_contact_force":0.21367,"subtask_id":"placed_at_goal","tcp_end":[0.62934,0.14784,0.18849],"tcp_start":[0.62001,0.14842,0.27769],"tcp_to_object_dist_end":0.03213,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.70861,"average_solve_count":453.0,"average_success_count":453.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.0479,"descend_to_grasp.descend_speed":0.02465,"descend_to_grasp.grasp_offset_x":0.0021,"descend_to_grasp.grasp_offset_y":0.00222,"grasp.grasp_retry_offset_x":0.00162,"grasp.grasp_retry_offset_y":0.00037,"lift_object.lift_distance":0.17184,"lift_object.lift_speed":0.02993,"place_at_goal.place_offset_x":-0.00214,"place_at_goal.place_offset_y":0.01689,"place_at_goal.place_offset_z":-0.00149,"place_at_goal.place_speed":0.01556,"transport_to_goal.transport_speed":0.04522},"optimized_scores":{"best_composite_score":-0.06093,"best_fitness_score":0.70907,"best_task_score":0.50148},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":25.0,"contact_point_centroid":[0.62073,0.19214,-0.00562],"force_p95":1.4368,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.45023,"mean_force":1.14917,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.62194,0.20073,0.20369]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.62038,0.17658,-0.00223],"force_p95":0.12391,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86982,"mean_force":0.12749,"phase_index":5.0,"phase_name":"place_at_goal","phase_type":"descend","tcp_position_centroid":[0.62063,0.20717,0.16874]},{"body_a":"world","body_b":"grasp_target","contact_count":120.0,"contact_point_centroid":[0.45477,-0.02253,-0.00158],"force_p95":0.28747,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.33287,"mean_force":0.09867,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.44761,-0.02369,0.05226]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9092.0,"contact_point_centroid":[0.44618,-0.00472,0.12363],"force_p95":0.11379,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25871,"mean_force":0.08341,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.44537,-0.02359,0.1262]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9729.0,"contact_point_centroid":[0.5235,0.09869,0.20124],"force_p95":0.10879,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25663,"mean_force":0.07706,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52552,0.07991,0.20492]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12201.0,"contact_point_centroid":[0.44506,-0.04209,0.1179],"force_p95":0.10484,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23864,"mean_force":0.06459,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.44535,-0.02359,0.11903]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45861,-0.02617,-0.00221],"force_p95":0.183,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.23546,"mean_force":0.13744,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.44994,-0.02376,0.05188]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3277.0,"contact_point_centroid":[0.45072,-0.00461,0.0494],"force_p95":0.10678,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15833,"mean_force":0.06403,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.44888,-0.02373,0.05083]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11203.0,"contact_point_centroid":[0.52815,0.06642,0.20127],"force_p95":0.09334,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15812,"mean_force":0.06725,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52961,0.08504,0.20494]},{"body_a":"world","body_b":"grasp_target","contact_count":2880.0,"contact_point_centroid":[0.45856,-0.02632,-0.00195],"force_p95":0.12868,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.1228,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.47795,-0.01206,0.22656]},{"body_a":"world","body_b":"grasp_target","contact_count":2704.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.45517,-0.02421,0.10379]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5103.0,"contact_point_centroid":[0.44893,-0.04252,0.05114],"force_p95":0.07391,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0786,"mean_force":0.04232,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.44888,-0.02373,0.05084]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4022.0,"contact_point_centroid":[0.62104,0.20747,0.1693],"force_p95":0.01102,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01565,"mean_force":0.01055,"phase_index":5.0,"phase_name":"place_at_goal","phase_type":"descend","tcp_position_centroid":[0.62056,0.20745,0.16706]}],"total_contact_groups":13},"final_pose_error":0.0503,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.62038,0.1766,0.01602],"final_tcp_position":[0.62082,0.2092,0.15981],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":273004.23262,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":721.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2880.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_above_object","tcp_end":[0.45743,-0.02457,0.15443],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12843,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":676.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2704.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_point","tcp_end":[0.4561,-0.02397,0.05798],"tcp_start":[0.45743,-0.02457,0.15443],"tcp_to_object_dist_end":0.03214,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45853,-0.02438,0.02524],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.3024,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.18017,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10180.0,"raw_peak_contact_force":0.23546,"subtask_id":"grasp_point","tcp_end":[0.44885,-0.02373,0.05081],"tcp_start":[0.4561,-0.02397,0.05798],"tcp_to_object_dist_end":0.02735,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":786.0,"n_steps_budget":1000.0,"object_pos_end":[0.44725,-0.02407,0.1765],"object_pos_start":[0.45853,-0.02438,0.02524],"object_to_goal_dist_end":0.30214,"object_to_goal_dist_start":0.3024,"object_z_max":0.17631,"peak_contact_force":0.11134,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":21413.0,"raw_peak_contact_force":0.33287,"subtask_id":"object_lifted","tcp_end":[0.44562,-0.02359,0.2081],"tcp_start":[0.44885,-0.02373,0.05081],"tcp_to_object_dist_end":0.03165,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":891.0,"n_steps_budget":1000.0,"object_pos_end":[0.61407,0.18165,0.10461],"object_pos_start":[0.44725,-0.02407,0.1765],"object_to_goal_dist_end":0.03246,"object_to_goal_dist_start":0.30214,"object_z_max":0.17659,"peak_contact_force":0.92521,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":20957.0,"raw_peak_contact_force":1.45023,"subtask_id":"near_goal","tcp_end":[0.62283,0.20173,0.20376],"tcp_start":[0.61773,0.19536,0.20518],"tcp_to_object_dist_end":0.10153,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.62038,0.1766,0.01602],"object_pos_start":[0.61989,0.18051,0.0042],"object_to_goal_dist_end":0.10353,"object_to_goal_dist_start":0.11382,"object_z_max":0.01662,"peak_contact_force":273004.23262,"phase_name":"place_at_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8022.0,"raw_peak_contact_force":0.86982,"subtask_id":"placed_at_goal","tcp_end":[0.62082,0.2092,0.15981],"tcp_start":[0.62283,0.20173,0.20376],"tcp_to_object_dist_end":0.14744,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```