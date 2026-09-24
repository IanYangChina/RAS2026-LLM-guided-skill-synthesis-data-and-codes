## Search State

- **Seed**: 1
- **Iteration**: 4 / 15

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

## Current Skill (Q=-0.264) — your mutation base

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
  - 0.1
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
    - 0.03
    offset_along_axis:
      distance: 0.1
      axis: world_z
      mode: add_to_offset
      sign: positive
    tolerance: 0.005
    orientation:
      mode: keep_current
  parameters:
    lift_distance:
      type: scalar
      range:
      - 0.05
      - 0.15
      default: 0.1
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    lift_speed:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: object_lifted
- id: transport_to_goal
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
    tolerance: 0.005
    orientation:
      mode: keep_current
  parameters:
    transport_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: near_goal
- id: place_at_goal
  type: release
  generator: linear_cartesian
  control: position_control
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
- **lift** (`lift`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.03], offset_along_axis={axis=world_z, distance=0.1, mode=add_to_offset, sign=positive}, tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - lift_speed: status=consumed; consumers=generator.speed (replace)
- **transport_to_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.1], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings:
    - transport_speed: status=consumed; consumers=generator.speed (replace)
- **place_at_goal** (`release`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings: none

## Design Metrics

- **Composite score**: -0.264
- **task_score** (E): 0.242
- **fitness_score**: 0.356  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.620

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1533 |
| descend_to_grasp | 1.00 | 1.00 | 0.1214 |
| grasp | 1.00 | 1.00 | 0.0109 |
| lift | 0.00 | 1.00 | 0.0852 |
| transport_to_goal | 0.00 | 0.67 | 0.0698 |
| place_at_goal | 1.00 | 1.00 | 0.0252 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.476, -0.000, 0.153) | (0.479, -0.000, 0.030)→(0.479, -0.000, 0.026) | 0.276→0.278 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.476, -0.000, 0.153)→(0.477, 0.002, 0.032) | (0.479, -0.000, 0.026)→(0.479, -0.000, 0.026) | 0.278→0.278 | 1.00 / 4.000 | 16.595 | 0.123 |
| grasp | grasp | 1.00 / step_budget | (0.477, 0.002, 0.032)→(0.469, 0.002, 0.024) | (0.479, -0.000, 0.026)→(0.479, 0.002, 0.024) | 0.278→0.277 | 1.00 / 43.667 | 0.249 | 0.358 |
| lift | lift | 0.00 / step_budget | (0.469, 0.002, 0.066)→(0.473, 0.002, 0.151) | (0.479, 0.002, 0.024)→(0.477, 0.002, 0.060) | 0.277→0.262 | 1.00 / 31.667 | 0.090 | 0.587 |
| transport_to_goal | approach | 0.00 / step_budget | (0.473, 0.002, 0.151)→(0.505, 0.058, 0.173) | (0.485, 0.002, 0.138)→(0.513, 0.064, 0.112) | 0.242→0.186 | 0.67 / 16.667 | 19.919 | 0.177 |
| place_at_goal | release | 1.00 / step_budget | (0.505, 0.058, 0.173)→(0.500, 0.058, 0.198) | (0.513, 0.064, 0.112)→(0.509, 0.079, 0.014) | 0.186→0.215 | 1.00 / 4.000 | 0.099 | 1.616 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 0.000
- transport_retention: None
- terminal_score: 0.301
- phase_score: 0.477
- phase_breakdown.near_goal_score: 0.044
- phase_breakdown.reach_above_object_score: 0.906
- phase_breakdown.object_lifted_score: 0.616
- phase_breakdown.grasp_point_score: 0.773
- phase_breakdown.placed_at_goal_score: 0.045
- grasp_place_fitness: 0.382

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.382
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.301
- **Median Q (composite search score)**: -0.273
- **K-run variance**: 0.0003
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.303


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.18135,"average_solve_count":193.0,"average_success_count":193.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.0838,"descend_to_grasp.descend_speed":0.02974,"descend_to_grasp.grasp_offset_x":0.00193,"descend_to_grasp.grasp_offset_y":-0.00452,"grasp.grasp_retry_offset_x":0.00131,"grasp.grasp_retry_offset_y":0.00084,"lift.lift_distance":0.09845,"lift.lift_speed":0.0299,"place_at_goal.release_duration":0.49334,"transport_to_goal.transport_speed":0.09962},"optimized_scores":{"best_composite_score":-0.23839,"best_fitness_score":0.38161,"best_task_score":0.30109},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":769.0,"contact_point_centroid":[0.52372,0.12789,-0.00321],"force_p95":0.5974,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.7059,"mean_force":0.17882,"phase_index":5.0,"phase_name":"place_at_goal","phase_type":"release","tcp_position_centroid":[0.51259,0.11153,0.18387]},{"body_a":"world","body_b":"grasp_target","contact_count":666.0,"contact_point_centroid":[0.49692,0.03837,-0.00175],"force_p95":0.27016,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.5777,"mean_force":0.11452,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.48699,0.03945,0.02941]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50143,0.04422,-0.00249],"force_p95":0.26058,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.34183,"mean_force":0.15926,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49095,0.0398,0.02873]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":37228.0,"contact_point_centroid":[0.4899,0.0586,0.07602],"force_p95":0.08135,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27037,"mean_force":0.05175,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.48958,0.03945,0.07441]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10160.0,"contact_point_centroid":[0.5053,0.05042,0.16035],"force_p95":0.15228,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26732,"mean_force":0.08445,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.50215,0.06925,0.16145]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":13087.0,"contact_point_centroid":[0.50634,0.09011,0.16164],"force_p95":0.1026,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24032,"mean_force":0.06612,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.50295,0.07175,0.1625]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":37159.0,"contact_point_centroid":[0.49003,0.02033,0.07798],"force_p95":0.07912,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2282,"mean_force":0.05068,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.48967,0.03945,0.07621]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4230.0,"contact_point_centroid":[0.4904,0.02033,0.03056],"force_p95":0.09202,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15423,"mean_force":0.05081,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.48977,0.03971,0.02749]},{"body_a":"world","body_b":"grasp_target","contact_count":3088.0,"contact_point_centroid":[0.50118,0.04505,-0.00195],"force_p95":0.12782,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12278,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.49749,0.02142,0.22338]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.50118,0.04505,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.49612,0.04114,0.07986]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5777.0,"contact_point_centroid":[0.48915,0.05953,0.02863],"force_p95":0.08273,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09549,"mean_force":0.04273,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.48979,0.03971,0.02751]}],"total_contact_groups":11},"final_pose_error":0.15577,"key_states":{"actual_goal_position":[0.56442,0.24486,0.14677],"final_object_position":[0.52359,0.12801,0.01602],"final_tcp_position":[0.51656,0.11231,0.18042],"realised_goal_position":[0.56442,0.24486,0.14677],"realised_object_initial_position":[0.50118,0.04505,0.03]},"peak_contact_force":1.7059,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":773.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.03],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.23992,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3088.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_above_object","tcp_end":[0.49726,0.04259,0.15171],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12578,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_point","tcp_end":[0.49761,0.04036,0.03581],"tcp_start":[0.49726,0.04259,0.15171],"tcp_to_object_dist_end":0.01143,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50113,0.04031,0.02436],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24664,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.23445,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11807.0,"raw_peak_contact_force":0.34183,"subtask_id":"grasp_point","tcp_end":[0.48974,0.0397,0.02746],"tcp_start":[0.49761,0.04036,0.03581],"tcp_to_object_dist_end":0.01182,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":31.0,"n_steps":1902.0,"n_steps_budget":1000.0,"object_pos_end":[0.49986,0.03981,0.06327],"object_pos_start":[0.50113,0.04031,0.02436],"object_to_goal_dist_end":0.23063,"object_to_goal_dist_start":0.24664,"object_z_max":0.1367,"peak_contact_force":0.08457,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":75053.0,"raw_peak_contact_force":0.5777,"subtask_id":"object_lifted","tcp_end":[0.49561,0.03949,0.15294],"tcp_start":[0.49122,0.03965,0.07287],"tcp_to_object_dist_end":0.08977,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52848,0.12981,0.03845],"object_pos_start":[0.50602,0.03948,0.13674],"object_to_goal_dist_end":0.16206,"object_to_goal_dist_start":0.21376,"object_z_max":0.1523,"peak_contact_force":0.0,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":23247.0,"raw_peak_contact_force":0.26732,"subtask_id":"near_goal","tcp_end":[0.51656,0.11231,0.18042],"tcp_start":[0.49561,0.03949,0.15294],"tcp_to_object_dist_end":0.14355,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.52359,0.12801,0.01602],"object_pos_start":[0.52848,0.12981,0.03845],"object_to_goal_dist_end":0.18005,"object_to_goal_dist_start":0.16206,"object_z_max":0.03845,"peak_contact_force":0.12263,"phase_name":"place_at_goal","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":769.0,"raw_peak_contact_force":1.7059,"subtask_id":"placed_at_goal","tcp_end":[0.51127,0.11121,0.20447],"tcp_start":[0.51656,0.11231,0.18042],"tcp_to_object_dist_end":0.1896,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.11364,"average_solve_count":220.0,"average_success_count":220.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.03791,"descend_to_grasp.descend_speed":0.04066,"descend_to_grasp.grasp_offset_x":0.0073,"descend_to_grasp.grasp_offset_y":0.00549,"grasp.grasp_retry_offset_x":-0.0016,"grasp.grasp_retry_offset_y":0.00251,"lift.lift_distance":0.12464,"lift.lift_speed":0.03785,"place_at_goal.release_duration":0.34703,"transport_to_goal.transport_speed":0.08902},"optimized_scores":{"best_composite_score":-0.28107,"best_fitness_score":0.33893,"best_task_score":0.19695},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":169.0,"contact_point_centroid":[0.51991,0.03461,-0.00825],"force_p95":1.45638,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.9151,"mean_force":0.46818,"phase_index":5.0,"phase_name":"place_at_goal","phase_type":"release","tcp_position_centroid":[0.50974,0.03606,0.2338]},{"body_a":"world","body_b":"grasp_target","contact_count":581.0,"contact_point_centroid":[0.47163,-0.01402,-0.00188],"force_p95":0.30087,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.68645,"mean_force":0.12306,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46733,-0.01485,0.02714]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47627,-0.01927,-0.00253],"force_p95":0.26287,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.33751,"mean_force":0.16233,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.47141,-0.01488,0.02621]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":38864.0,"contact_point_centroid":[0.46771,-0.03406,0.09391],"force_p95":0.07543,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3023,"mean_force":0.05012,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.4674,-0.01493,0.09205]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":38375.0,"contact_point_centroid":[0.46771,0.00422,0.09327],"force_p95":0.07653,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25772,"mean_force":0.04974,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.4674,-0.01492,0.09132]},{"body_a":"world","body_b":"grasp_target","contact_count":2892.0,"contact_point_centroid":[0.47616,-0.02015,-0.00195],"force_p95":0.12867,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12279,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.48587,-0.00927,0.22614]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4535.0,"contact_point_centroid":[0.47042,0.00436,0.02711],"force_p95":0.09005,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13815,"mean_force":0.04691,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.47026,-0.01488,0.02507]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.47468,-0.01659,0.0831]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":15813.0,"contact_point_centroid":[0.49393,-0.00765,0.20404],"force_p95":0.08411,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10097,"mean_force":0.06026,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.49118,0.01122,0.20308]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5311.0,"contact_point_centroid":[0.47051,-0.03472,0.02686],"force_p95":0.09095,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10025,"mean_force":0.04604,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.47029,-0.01488,0.02509]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":15211.0,"contact_point_centroid":[0.49367,0.03,0.20391],"force_p95":0.09008,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09864,"mean_force":0.06252,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.49104,0.01109,0.20299]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":942.0,"contact_point_centroid":[0.51643,0.01739,0.2148],"force_p95":0.0834,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09352,"mean_force":0.05344,"phase_index":5.0,"phase_name":"place_at_goal","phase_type":"release","tcp_position_centroid":[0.51306,0.03637,0.21383]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1004.0,"contact_point_centroid":[0.51668,0.05533,0.21421],"force_p95":0.08056,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09182,"mean_force":0.05089,"phase_index":5.0,"phase_name":"place_at_goal","phase_type":"release","tcp_position_centroid":[0.51307,0.03637,0.21383]}],"total_contact_groups":13},"final_pose_error":0.18489,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.52166,0.03527,0.01114],"final_tcp_position":[0.5145,0.0364,0.21628],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":49.53926,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":724.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2892.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_above_object","tcp_end":[0.4738,-0.01882,0.15409],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12809,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":49.53926,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_point","tcp_end":[0.47791,-0.01497,0.03272],"tcp_start":[0.4738,-0.01882,0.15409],"tcp_to_object_dist_end":0.00865,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.476,-0.01524,0.02412],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28654,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.23889,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11646.0,"raw_peak_contact_force":0.33751,"subtask_id":"grasp_point","tcp_end":[0.47024,-0.01487,0.02504],"tcp_start":[0.47791,-0.01497,0.03272],"tcp_to_object_dist_end":0.00584,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":34.0,"n_steps":1951.0,"n_steps_budget":1000.0,"object_pos_end":[0.47377,-0.01507,0.07865],"object_pos_start":[0.476,-0.01524,0.02412],"object_to_goal_dist_end":0.26004,"object_to_goal_dist_start":0.28654,"object_z_max":0.18138,"peak_contact_force":0.08817,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":77820.0,"raw_peak_contact_force":0.68645,"subtask_id":"object_lifted","tcp_end":[0.47012,-0.015,0.19375],"tcp_start":[0.46882,-0.01498,0.0835],"tcp_to_object_dist_end":0.11516,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":31.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52027,0.03652,0.19644],"object_pos_start":[0.48172,-0.01493,0.18144],"object_to_goal_dist_end":0.16566,"object_to_goal_dist_start":0.22979,"object_z_max":0.19643,"peak_contact_force":0.08309,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":31024.0,"raw_peak_contact_force":0.10097,"subtask_id":"near_goal","tcp_end":[0.5145,0.0364,0.21628],"tcp_start":[0.47012,-0.015,0.19375],"tcp_to_object_dist_end":0.02066,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.52166,0.03527,0.01114],"object_pos_start":[0.52027,0.03652,0.19644],"object_to_goal_dist_end":0.24372,"object_to_goal_dist_start":0.16566,"object_z_max":0.19644,"peak_contact_force":0.07982,"phase_name":"place_at_goal","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2115.0,"raw_peak_contact_force":1.9151,"subtask_id":"placed_at_goal","tcp_end":[0.50968,0.03606,0.24049],"tcp_start":[0.5145,0.0364,0.21628],"tcp_to_object_dist_end":0.22966,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.76349,"average_solve_count":241.0,"average_success_count":241.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.07936,"descend_to_grasp.descend_speed":0.0171,"descend_to_grasp.grasp_offset_x":0.00191,"descend_to_grasp.grasp_offset_y":0.00715,"grasp.grasp_retry_offset_x":-0.00033,"grasp.grasp_retry_offset_y":0.00141,"lift.lift_distance":0.07457,"lift.lift_speed":0.01384,"place_at_goal.release_duration":0.57934,"transport_to_goal.transport_speed":0.07173},"optimized_scores":{"best_composite_score":-0.27329,"best_fitness_score":0.34671,"best_task_score":0.2273},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":237.0,"contact_point_centroid":[0.48264,0.07414,-0.00504],"force_p95":0.73082,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.22828,"mean_force":0.25814,"phase_index":5.0,"phase_name":"place_at_goal","phase_type":"release","tcp_position_centroid":[0.47811,0.02585,0.13956]},{"body_a":"world","body_b":"grasp_target","contact_count":1406.0,"contact_point_centroid":[0.45519,-0.01687,-0.00172],"force_p95":0.27503,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.49665,"mean_force":0.10943,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.44529,-0.01908,0.0235]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45888,-0.02486,-0.00265],"force_p95":0.30782,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.39507,"mean_force":0.17433,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.44944,-0.01918,0.02179]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":619.0,"contact_point_centroid":[0.48488,0.04594,0.11581],"force_p95":0.26776,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30199,"mean_force":0.14314,"phase_index":5.0,"phase_name":"place_at_goal","phase_type":"release","tcp_position_centroid":[0.48157,0.02609,0.12054]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":37618.0,"contact_point_centroid":[0.44705,-0.03819,0.05098],"force_p95":0.07995,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21851,"mean_force":0.05129,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.44668,-0.01906,0.04931]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":37005.0,"contact_point_centroid":[0.44709,8e-05,0.05102],"force_p95":0.08039,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17082,"mean_force":0.05075,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.4467,-0.01906,0.04922]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12542.0,"contact_point_centroid":[0.46813,0.02159,0.11161],"force_p95":0.11468,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16363,"mean_force":0.07596,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.46565,0.00265,0.11232]},{"body_a":"world","body_b":"grasp_target","contact_count":2628.0,"contact_point_centroid":[0.45856,-0.02632,-0.00194],"force_p95":0.12988,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12281,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.47793,-0.01207,0.22653]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3962.0,"contact_point_centroid":[0.44886,0.00018,0.0237],"force_p95":0.10323,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12821,"mean_force":0.05313,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.44834,-0.01916,0.02076]},{"body_a":"world","body_b":"grasp_target","contact_count":3696.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.45497,-0.02182,0.08764]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":15733.0,"contact_point_centroid":[0.46707,-0.01597,0.11117],"force_p95":0.08674,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11614,"mean_force":0.06113,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.46568,0.00267,0.11233]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":627.0,"contact_point_centroid":[0.48218,0.00852,0.11621],"force_p95":0.11372,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11536,"mean_force":0.07045,"phase_index":5.0,"phase_name":"place_at_goal","phase_type":"release","tcp_position_centroid":[0.48221,0.02613,0.1208]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5431.0,"contact_point_centroid":[0.44863,-0.03949,0.02245],"force_p95":0.09597,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11381,"mean_force":0.04815,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.44837,-0.01917,0.0208]}],"total_contact_groups":13},"final_pose_error":0.25068,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.48285,0.07413,0.01557],"final_tcp_position":[0.48393,0.02616,0.1229],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":59.67457,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":658.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2628.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_above_object","tcp_end":[0.45745,-0.02458,0.15441],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.1284,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":924.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3696.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_point","tcp_end":[0.45582,-0.01932,0.02781],"tcp_start":[0.45745,-0.02458,0.15441],"tcp_to_object_dist_end":0.00772,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.4584,-0.01933,0.02377],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.29905,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.27319,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11193.0,"raw_peak_contact_force":0.39507,"subtask_id":"grasp_point","tcp_end":[0.44832,-0.01915,0.02074],"tcp_start":[0.45582,-0.01932,0.02781],"tcp_to_object_dist_end":0.01053,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":30.0,"n_steps":1902.0,"n_steps_budget":1000.0,"object_pos_end":[0.45704,-0.01917,0.03922],"object_pos_start":[0.4584,-0.01933,0.02377],"object_to_goal_dist_end":0.29542,"object_to_goal_dist_start":0.29905,"object_z_max":0.09592,"peak_contact_force":0.09604,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":76029.0,"raw_peak_contact_force":0.49665,"subtask_id":"object_lifted","tcp_end":[0.45258,-0.01905,0.10657],"tcp_start":[0.44713,-0.0191,0.04159],"tcp_to_object_dist_end":0.0675,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":19.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.4892,0.02654,0.10133],"object_pos_start":[0.46583,-0.01901,0.09595],"object_to_goal_dist_end":0.23028,"object_to_goal_dist_start":0.28099,"object_z_max":0.10133,"peak_contact_force":59.67457,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":28275.0,"raw_peak_contact_force":0.16363,"subtask_id":"near_goal","tcp_end":[0.48393,0.02616,0.1229],"tcp_start":[0.45258,-0.01905,0.10657],"tcp_to_object_dist_end":0.0222,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48285,0.07413,0.01557],"object_pos_start":[0.4892,0.02654,0.10133],"object_to_goal_dist_end":0.22222,"object_to_goal_dist_start":0.23028,"object_z_max":0.10133,"peak_contact_force":0.09496,"phase_name":"place_at_goal","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1483.0,"raw_peak_contact_force":1.22828,"subtask_id":"placed_at_goal","tcp_end":[0.478,0.02585,0.14857],"tcp_start":[0.48393,0.02616,0.1229],"tcp_to_object_dist_end":0.14158,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
```