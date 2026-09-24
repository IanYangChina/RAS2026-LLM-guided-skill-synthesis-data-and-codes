## Search State

- **Seed**: 1
- **Iteration**: 5 / 15

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

## Current Skill (Q=0.109) — your mutation base

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
  anchor: world
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
  type: release
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  end_effector_action: open
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
- **place_at_goal** (`release`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.109
- **task_score** (E): 0.424
- **fitness_score**: 0.679  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.570

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1532 |
| descend_to_grasp | 1.00 | 1.00 | 0.0998 |
| grasp | 1.00 | 1.00 | 0.0109 |
| lift_object | 1.00 | 1.00 | 0.1437 |
| transport_to_goal | 1.00 | 1.00 | 0.2401 |
| place_at_goal | 1.00 | 1.00 | 0.0661 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.476, -0.000, 0.153) | (0.479, -0.000, 0.030)→(0.479, -0.000, 0.026) | 0.276→0.278 | 1.00 / 4.000 | 5.852 | 0.138 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.476, -0.000, 0.153)→(0.480, -0.001, 0.054) | (0.479, -0.000, 0.026)→(0.479, -0.000, 0.026) | 0.278→0.278 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp | grasp | 1.00 / step_budget | (0.480, -0.001, 0.054)→(0.473, -0.001, 0.046) | (0.479, -0.000, 0.026)→(0.479, -0.001, 0.026) | 0.278→0.278 | 1.00 / 43.667 | 0.142 | 0.187 |
| lift_object | lift | 1.00 / step_budget | (0.473, -0.001, 0.046)→(0.469, -0.001, 0.190) | (0.479, -0.001, 0.026)→(0.475, -0.001, 0.166) | 0.278→0.248 | 1.00 / 37.000 | 0.090 | 0.423 |
| transport_to_goal | approach | 1.00 / step_budget | (0.469, -0.001, 0.190)→(0.598, 0.192, 0.239) | (0.475, -0.001, 0.166)→(0.601, 0.192, 0.210) | 0.248→0.061 | 1.00 / 30.667 | 0.099 | 0.174 |
| place_at_goal | release | 1.00 / step_budget | (0.598, 0.192, 0.239)→(0.600, 0.200, 0.173) | (0.601, 0.192, 0.210)→(0.595, 0.196, 0.020) | 0.061→0.132 | 1.00 / 4.000 | 0.115 | 1.483 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.518
- phase_score: 0.599
- phase_breakdown.near_goal_score: 0.671
- phase_breakdown.reach_above_object_score: 0.908
- phase_breakdown.object_lifted_score: 0.000
- phase_breakdown.grasp_point_score: 0.799
- phase_breakdown.placed_at_goal_score: 0.617
- grasp_place_fitness: 0.723

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.723
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.518
- **Median Q (composite search score)**: 0.120
- **K-run variance**: 0.0017
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.300


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.24031,"average_solve_count":258.0,"average_success_count":258.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.05137,"descend_to_grasp.descend_speed":0.03516,"descend_to_grasp.grasp_offset_x":0.00273,"descend_to_grasp.grasp_offset_y":0.00208,"grasp.grasp_retry_offset_x":0.00148,"grasp.grasp_retry_offset_y":-0.0018,"lift_object.lift_distance":0.15579,"lift_object.lift_speed":0.05007,"transport_to_goal.transport_speed":0.08364},"optimized_scores":{"best_composite_score":0.12039,"best_fitness_score":0.69039,"best_task_score":0.4441},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":288.0,"contact_point_centroid":[0.54647,0.24411,-0.00485],"force_p95":0.74777,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.35255,"mean_force":0.23704,"phase_index":5.0,"phase_name":"place_at_goal","phase_type":"release","tcp_position_centroid":[0.55679,0.24062,0.16043]},{"body_a":"world","body_b":"grasp_target","contact_count":109.0,"contact_point_centroid":[0.49727,0.04609,-0.00134],"force_p95":0.43231,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.46097,"mean_force":0.11102,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49021,0.04575,0.04501]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":14321.0,"contact_point_centroid":[0.48802,0.06469,0.11351],"force_p95":0.0788,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28929,"mean_force":0.05338,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48759,0.04551,0.11139]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":15257.0,"contact_point_centroid":[0.48775,0.02642,0.11603],"force_p95":0.07345,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2786,"mean_force":0.05045,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48759,0.04551,0.11393]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7163.0,"contact_point_centroid":[0.55711,0.25472,0.18846],"force_p95":0.10367,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2011,"mean_force":0.06506,"phase_index":5.0,"phase_name":"place_at_goal","phase_type":"release","tcp_position_centroid":[0.55716,0.23579,0.18922]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50119,0.04511,-0.00208],"force_p95":0.14372,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18672,"mean_force":0.12847,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49259,0.04599,0.04486]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8221.0,"contact_point_centroid":[0.55652,0.21691,0.18876],"force_p95":0.09603,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16852,"mean_force":0.05836,"phase_index":5.0,"phase_name":"place_at_goal","phase_type":"release","tcp_position_centroid":[0.55717,0.23585,0.18872]},{"body_a":"world","body_b":"grasp_target","contact_count":3440.0,"contact_point_centroid":[0.50118,0.04505,-0.00196],"force_p95":0.12633,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12277,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.49742,0.0215,0.22306]},{"body_a":"world","body_b":"grasp_target","contact_count":3964.0,"contact_point_centroid":[0.50118,0.04505,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.49724,0.04507,0.0862]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4823.0,"contact_point_centroid":[0.49162,0.06508,0.04542],"force_p95":0.06929,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11563,"mean_force":0.04489,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49143,0.04588,0.04359]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12623.0,"contact_point_centroid":[0.52236,0.12265,0.21061],"force_p95":0.07062,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09941,"mean_force":0.04751,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52237,0.14169,0.20905]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11336.0,"contact_point_centroid":[0.52381,0.16375,0.21118],"force_p95":0.07798,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09407,"mean_force":0.05248,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52347,0.14458,0.20989]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4928.0,"contact_point_centroid":[0.49164,0.02667,0.04557],"force_p95":0.06955,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07363,"mean_force":0.04461,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49143,0.04588,0.0436]}],"total_contact_groups":13},"final_pose_error":0.00557,"key_states":{"actual_goal_position":[0.56442,0.24486,0.14677],"final_object_position":[0.54613,0.24388,0.0264],"final_tcp_position":[0.5599,0.24211,0.14502],"realised_goal_position":[0.56442,0.24486,0.14677],"realised_object_initial_position":[0.50118,0.04505,0.03]},"peak_contact_force":1.35255,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":861.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.03],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.23992,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3440.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_above_object","tcp_end":[0.49726,0.04257,0.15179],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12586,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":991.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3964.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_point","tcp_end":[0.49911,0.04662,0.05203],"tcp_start":[0.49726,0.04257,0.15179],"tcp_to_object_dist_end":0.02614,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5011,0.04562,0.02572],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24159,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.14189,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11551.0,"raw_peak_contact_force":0.18672,"subtask_id":"grasp_point","tcp_end":[0.4914,0.04587,0.04356],"tcp_start":[0.49911,0.04662,0.05203],"tcp_to_object_dist_end":0.02031,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":747.0,"n_steps_budget":1000.0,"object_pos_end":[0.49335,0.04554,0.16306],"object_pos_start":[0.5011,0.04562,0.02572],"object_to_goal_dist_end":0.21223,"object_to_goal_dist_start":0.24159,"object_z_max":0.16289,"peak_contact_force":0.07809,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":29687.0,"raw_peak_contact_force":0.46097,"subtask_id":"object_lifted","tcp_end":[0.48787,0.04554,0.18485],"tcp_start":[0.4914,0.04587,0.04356],"tcp_to_object_dist_end":0.02248,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":616.0,"n_steps_budget":1000.0,"object_pos_end":[0.56004,0.2304,0.21029],"object_pos_start":[0.49335,0.04554,0.16306],"object_to_goal_dist_end":0.06529,"object_to_goal_dist_start":0.21223,"object_z_max":0.21022,"peak_contact_force":0.06788,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":23959.0,"raw_peak_contact_force":0.09941,"subtask_id":"near_goal","tcp_end":[0.55674,0.23072,0.2351],"tcp_start":[0.48787,0.04554,0.18485],"tcp_to_object_dist_end":0.02504,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":465.0,"n_steps_budget":600.0,"object_pos_end":[0.54613,0.24388,0.0264],"object_pos_start":[0.56004,0.2304,0.21029],"object_to_goal_dist_end":0.12175,"object_to_goal_dist_start":0.06529,"object_z_max":0.21029,"peak_contact_force":0.11507,"phase_name":"place_at_goal","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":15672.0,"raw_peak_contact_force":1.35255,"subtask_id":"placed_at_goal","tcp_end":[0.55672,0.24058,0.17115],"tcp_start":[0.55674,0.23072,0.2351],"tcp_to_object_dist_end":0.14517,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.21786,"average_solve_count":280.0,"average_success_count":280.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.03752,"descend_to_grasp.descend_speed":0.03734,"descend_to_grasp.grasp_offset_x":0.00773,"descend_to_grasp.grasp_offset_y":-0.00129,"grasp.grasp_retry_offset_x":0.00137,"grasp.grasp_retry_offset_y":-7e-05,"lift_object.lift_distance":0.18416,"lift_object.lift_speed":0.05634,"transport_to_goal.transport_speed":0.09599},"optimized_scores":{"best_composite_score":0.05473,"best_fitness_score":0.62473,"best_task_score":0.3108},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":262.0,"contact_point_centroid":[0.61593,0.14547,-0.00562],"force_p95":1.22021,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.68628,"mean_force":0.31217,"phase_index":5.0,"phase_name":"place_at_goal","phase_type":"release","tcp_position_centroid":[0.62391,0.15642,0.2025]},{"body_a":"world","body_b":"grasp_target","contact_count":107.0,"contact_point_centroid":[0.47325,-0.02175,-0.00137],"force_p95":0.33717,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.43689,"mean_force":0.07302,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.47046,-0.02106,0.04634]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":15207.0,"contact_point_centroid":[0.46768,-0.04017,0.12862],"force_p95":0.08278,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28978,"mean_force":0.05637,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46802,-0.02097,0.12686]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17644.0,"contact_point_centroid":[0.46825,-0.00195,0.12961],"force_p95":0.07318,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2859,"mean_force":0.04959,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46803,-0.02097,0.12774]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4095.0,"contact_point_centroid":[0.62115,0.13393,0.22632],"force_p95":0.13613,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24477,"mean_force":0.09327,"phase_index":5.0,"phase_name":"place_at_goal","phase_type":"release","tcp_position_centroid":[0.62271,0.15275,0.22892]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5062.0,"contact_point_centroid":[0.62219,0.17112,0.22501],"force_p95":0.11082,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24099,"mean_force":0.07688,"phase_index":5.0,"phase_name":"place_at_goal","phase_type":"release","tcp_position_centroid":[0.62279,0.15283,0.22818]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12207.0,"contact_point_centroid":[0.54351,0.04612,0.2453],"force_p95":0.09191,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20382,"mean_force":0.06008,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.54431,0.06527,0.24456]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47616,-0.02025,-0.00209],"force_p95":0.14755,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19648,"mean_force":0.12949,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.47282,-0.02111,0.04598]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":14394.0,"contact_point_centroid":[0.54453,0.08438,0.24536],"force_p95":0.07598,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17348,"mean_force":0.05093,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.54447,0.06545,0.24463]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4399.0,"contact_point_centroid":[0.47126,-0.04037,0.047],"force_p95":0.07668,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14191,"mean_force":0.04912,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.4717,-0.02108,0.04482]},{"body_a":"world","body_b":"grasp_target","contact_count":2896.0,"contact_point_centroid":[0.47616,-0.02015,-0.00195],"force_p95":0.12867,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12279,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.48587,-0.00927,0.22616]},{"body_a":"world","body_b":"grasp_target","contact_count":3680.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.47563,-0.02025,0.09216]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5423.0,"contact_point_centroid":[0.47146,-0.00198,0.04756],"force_p95":0.06676,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.06745,"mean_force":0.04067,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.4717,-0.02108,0.04482]}],"total_contact_groups":13},"final_pose_error":0.00563,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.61532,0.14279,0.01624],"final_tcp_position":[0.62683,0.15733,0.18735],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":17.31193,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":725.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":17.31193,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2896.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_above_object","tcp_end":[0.47379,-0.01883,0.15406],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12807,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":920.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3680.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_point","tcp_end":[0.47915,-0.02128,0.05256],"tcp_start":[0.47379,-0.01883,0.15406],"tcp_to_object_dist_end":0.02673,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":46.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47607,-0.02088,0.02566],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28909,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.14455,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11622.0,"raw_peak_contact_force":0.19648,"subtask_id":"grasp_point","tcp_end":[0.47167,-0.02108,0.04479],"tcp_start":[0.47915,-0.02128,0.05256],"tcp_to_object_dist_end":0.01963,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":853.0,"n_steps_budget":1000.0,"object_pos_end":[0.47101,-0.02088,0.19147],"object_pos_start":[0.47607,-0.02088,0.02566],"object_to_goal_dist_end":0.24117,"object_to_goal_dist_start":0.28909,"object_z_max":0.19129,"peak_contact_force":0.08181,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":32958.0,"raw_peak_contact_force":0.43689,"subtask_id":"object_lifted","tcp_end":[0.46844,-0.02098,0.21434],"tcp_start":[0.47167,-0.02108,0.04479],"tcp_to_object_dist_end":0.02302,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":26.0,"n_steps":723.0,"n_steps_budget":1000.0,"object_pos_end":[0.62058,0.14835,0.24979],"object_pos_start":[0.47101,-0.02088,0.19147],"object_to_goal_dist_end":0.06172,"object_to_goal_dist_start":0.24117,"object_z_max":0.24975,"peak_contact_force":0.10507,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":26601.0,"raw_peak_contact_force":0.20382,"subtask_id":"near_goal","tcp_end":[0.62006,0.14834,0.27768],"tcp_start":[0.46844,-0.02098,0.21434],"tcp_to_object_dist_end":0.02789,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":396.0,"n_steps_budget":600.0,"object_pos_end":[0.61532,0.14279,0.01624],"object_pos_start":[0.62058,0.14835,0.24979],"object_to_goal_dist_end":0.17529,"object_to_goal_dist_start":0.06172,"object_z_max":0.24979,"peak_contact_force":0.10727,"phase_name":"place_at_goal","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":9419.0,"raw_peak_contact_force":1.68628,"subtask_id":"placed_at_goal","tcp_end":[0.62387,0.15641,0.21243],"tcp_start":[0.62006,0.14834,0.27768],"tcp_to_object_dist_end":0.19686,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.32721,"average_solve_count":272.0,"average_success_count":272.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.04175,"descend_to_grasp.descend_speed":0.02935,"descend_to_grasp.grasp_offset_x":0.00918,"descend_to_grasp.grasp_offset_y":-0.00125,"grasp.grasp_retry_offset_x":6e-05,"grasp.grasp_retry_offset_y":0.00486,"lift_object.lift_distance":0.1345,"lift_object.lift_speed":0.07481,"transport_to_goal.transport_speed":0.08823},"optimized_scores":{"best_composite_score":0.15266,"best_fitness_score":0.72266,"best_task_score":0.51824},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1574.0,"contact_point_centroid":[0.62472,0.20013,-0.00253],"force_p95":0.2855,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.40891,"mean_force":0.14705,"phase_index":5.0,"phase_name":"place_at_goal","phase_type":"release","tcp_position_centroid":[0.62221,0.20381,0.12553]},{"body_a":"world","body_b":"grasp_target","contact_count":94.0,"contact_point_centroid":[0.45615,-0.02742,-0.0013],"force_p95":0.30336,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.37056,"mean_force":0.0565,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.45425,-0.0269,0.05076]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1535.0,"contact_point_centroid":[0.61811,0.17928,0.17693],"force_p95":0.20825,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30763,"mean_force":0.12433,"phase_index":5.0,"phase_name":"place_at_goal","phase_type":"release","tcp_position_centroid":[0.61797,0.19755,0.18137]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9542.0,"contact_point_centroid":[0.45129,-0.04595,0.11102],"force_p95":0.1006,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3033,"mean_force":0.06137,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.45176,-0.02679,0.11047]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10717.0,"contact_point_centroid":[0.45194,-0.00788,0.10906],"force_p95":0.08255,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29293,"mean_force":0.05333,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.45176,-0.02679,0.10836]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1937.0,"contact_point_centroid":[0.61892,0.21504,0.17517],"force_p95":0.13985,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27042,"mean_force":0.08696,"phase_index":5.0,"phase_name":"place_at_goal","phase_type":"release","tcp_position_centroid":[0.61809,0.19771,0.17976]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10379.0,"contact_point_centroid":[0.53186,0.06163,0.1818],"force_p95":0.11338,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21816,"mean_force":0.07815,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.53065,0.08043,0.18397]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45856,-0.02639,-0.00206],"force_p95":0.13973,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17838,"mean_force":0.1273,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.45657,-0.027,0.05032]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12542.0,"contact_point_centroid":[0.53084,0.0982,0.18284],"force_p95":0.10175,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1697,"mean_force":0.06509,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.53004,0.07968,0.18381]},{"body_a":"world","body_b":"grasp_target","contact_count":2896.0,"contact_point_centroid":[0.45856,-0.02632,-0.00195],"force_p95":0.12867,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12279,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.47798,-0.01207,0.22653]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4109.0,"contact_point_centroid":[0.45471,-0.04616,0.04998],"force_p95":0.07684,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13348,"mean_force":0.05208,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.45549,-0.02695,0.04925]},{"body_a":"world","body_b":"grasp_target","contact_count":3112.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.45867,-0.0259,0.10162]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4904.0,"contact_point_centroid":[0.45556,-0.00788,0.05003],"force_p95":0.06925,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08581,"mean_force":0.04442,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.45549,-0.02695,0.04925]},{"body_a":"left_finger","body_b":"right_finger","contact_count":734.0,"contact_point_centroid":[0.62386,0.20408,0.12653],"force_p95":0.01279,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01845,"mean_force":0.01074,"phase_index":5.0,"phase_name":"place_at_goal","phase_type":"release","tcp_position_centroid":[0.62324,0.20406,0.12436]}],"total_contact_groups":14},"final_pose_error":0.00664,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.62484,0.19987,0.01602],"final_tcp_position":[0.6247,0.20576,0.11118],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":1.40891,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":725.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2896.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_above_object","tcp_end":[0.45746,-0.02458,0.15439],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12839,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":778.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3112.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_point","tcp_end":[0.4628,-0.02724,0.05659],"tcp_start":[0.45746,-0.02458,0.15439],"tcp_to_object_dist_end":0.03087,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45847,-0.02686,0.02577],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30419,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.13815,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10813.0,"raw_peak_contact_force":0.17838,"subtask_id":"grasp_point","tcp_end":[0.45546,-0.02695,0.04922],"tcp_start":[0.4628,-0.02724,0.05659],"tcp_to_object_dist_end":0.02365,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":543.0,"n_steps_budget":1000.0,"object_pos_end":[0.46148,-0.02622,0.14262],"object_pos_start":[0.45847,-0.02686,0.02577],"object_to_goal_dist_end":0.29019,"object_to_goal_dist_start":0.30419,"object_z_max":0.14244,"peak_contact_force":0.11121,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":20353.0,"raw_peak_contact_force":0.37056,"subtask_id":"object_lifted","tcp_end":[0.45186,-0.02678,0.16932],"tcp_start":[0.45546,-0.02695,0.04922],"tcp_to_object_dist_end":0.02839,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":843.0,"n_steps_budget":1000.0,"object_pos_end":[0.62156,0.19649,0.16951],"object_pos_start":[0.46148,-0.02622,0.14262],"object_to_goal_dist_end":0.05726,"object_to_goal_dist_start":0.29019,"object_z_max":0.16949,"peak_contact_force":0.12372,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":22921.0,"raw_peak_contact_force":0.21816,"subtask_id":"near_goal","tcp_end":[0.61854,0.19613,0.20322],"tcp_start":[0.45186,-0.02678,0.16932],"tcp_to_object_dist_end":0.03384,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":495.0,"n_steps_budget":600.0,"object_pos_end":[0.62484,0.19987,0.01602],"object_pos_start":[0.62156,0.19649,0.16951],"object_to_goal_dist_end":0.0986,"object_to_goal_dist_start":0.05726,"object_z_max":0.16951,"peak_contact_force":0.12263,"phase_name":"place_at_goal","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":5780.0,"raw_peak_contact_force":1.40891,"subtask_id":"placed_at_goal","tcp_end":[0.62089,0.20434,0.13607],"tcp_start":[0.61854,0.19613,0.20322],"tcp_to_object_dist_end":0.1202,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```