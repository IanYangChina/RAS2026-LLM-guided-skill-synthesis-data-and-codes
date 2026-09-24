## Search State

- **Seed**: 1
- **Iteration**: 2 / 15

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

## Current Skill (Q=-0.195) — your mutation base

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

- **Composite score**: -0.195
- **task_score** (E): 0.318
- **fitness_score**: 0.375  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.570

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1533 |
| descend_to_grasp | 1.00 | 1.00 | 0.0994 |
| grasp | 1.00 | 1.00 | 0.0109 |
| lift | 0.00 | 1.00 | 0.0370 |
| transport_to_goal | 0.00 | 1.00 | 0.0645 |
| place_at_goal | 0.33 | 1.00 | 0.1567 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.476, -0.000, 0.153) | (0.479, -0.000, 0.030)→(0.479, -0.000, 0.026) | 0.276→0.278 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.476, -0.000, 0.153)→(0.480, 0.001, 0.054) | (0.479, -0.000, 0.026)→(0.479, -0.000, 0.026) | 0.278→0.278 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp | grasp | 1.00 / step_budget | (0.480, 0.001, 0.054)→(0.472, 0.001, 0.046) | (0.479, -0.000, 0.026)→(0.479, 0.001, 0.026) | 0.278→0.277 | 1.00 / 41.667 | 0.152 | 0.202 |
| lift | lift | 0.00 / step_budget | (0.472, 0.001, 0.046)→(0.470, 0.001, 0.083) | (0.479, 0.001, 0.026)→(0.473, 0.001, 0.058) | 0.277→0.267 | 1.00 / 32.333 | 0.089 | 0.343 |
| transport_to_goal | approach | 0.00 / step_budget | (0.470, 0.001, 0.083)→(0.497, 0.049, 0.115) | (0.473, 0.001, 0.058)→(0.499, 0.048, 0.084) | 0.267→0.206 | 1.00 / 24.333 | 0.126 | 0.163 |
| place_at_goal | release | 0.33 / step_budget | (0.497, 0.049, 0.115)→(0.576, 0.171, 0.161) | (0.499, 0.048, 0.084)→(0.547, 0.131, 0.020) | 0.206→0.178 | 1.00 / 4.000 | 91001.442 | 1.108 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 0.000
- transport_retention: None
- terminal_score: 0.446
- phase_score: 0.525
- phase_breakdown.near_goal_score: 0.020
- phase_breakdown.reach_above_object_score: 0.905
- phase_breakdown.object_lifted_score: 0.370
- phase_breakdown.grasp_point_score: 0.687
- phase_breakdown.placed_at_goal_score: 0.644
- grasp_place_fitness: 0.440

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.440
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.446
- **Median Q (composite search score)**: -0.215
- **K-run variance**: 0.0022
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Parameters at lower bound**: grasp.grasp_retry_offset_y
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.84,"average_solve_count":250.0,"average_success_count":250.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.0164,"descend_to_grasp.descend_speed":0.04919,"descend_to_grasp.grasp_offset_x":0.00307,"descend_to_grasp.grasp_offset_y":0.00422,"grasp.grasp_retry_offset_x":0.00268,"grasp.grasp_retry_offset_y":-0.005,"lift.lift_distance":0.1129,"lift.lift_speed":0.02508,"transport_to_goal.transport_speed":0.09207},"optimized_scores":{"best_composite_score":-0.12964,"best_fitness_score":0.44036,"best_task_score":0.44639},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":241.0,"contact_point_centroid":[0.55494,0.2455,-0.00495],"force_p95":0.91225,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.27545,"mean_force":0.28173,"phase_index":5.0,"phase_name":"place_at_goal","phase_type":"release","tcp_position_centroid":[0.55478,0.23567,0.15272]},{"body_a":"world","body_b":"grasp_target","contact_count":789.0,"contact_point_centroid":[0.49754,0.04741,-0.00162],"force_p95":0.21339,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.35815,"mean_force":0.09719,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.48856,0.04751,0.04534]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50125,0.04532,-0.00224],"force_p95":0.18658,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24857,"mean_force":0.14012,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49287,0.04802,0.04531]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20844.0,"contact_point_centroid":[0.48908,0.02835,0.06273],"force_p95":0.0734,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23096,"mean_force":0.04768,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.48896,0.04733,0.06064]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17292.0,"contact_point_centroid":[0.48993,0.06654,0.06284],"force_p95":0.08101,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22146,"mean_force":0.05621,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.48898,0.04733,0.06084]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9283.0,"contact_point_centroid":[0.53194,0.18258,0.12426],"force_p95":0.12873,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.189,"mean_force":0.09088,"phase_index":5.0,"phase_name":"place_at_goal","phase_type":"release","tcp_position_centroid":[0.52861,0.16414,0.12761]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10323.0,"contact_point_centroid":[0.53067,0.14348,0.12484],"force_p95":0.12085,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14369,"mean_force":0.08005,"phase_index":5.0,"phase_name":"place_at_goal","phase_type":"release","tcp_position_centroid":[0.52766,0.16172,0.12729]},{"body_a":"world","body_b":"grasp_target","contact_count":3668.0,"contact_point_centroid":[0.50118,0.04505,-0.00196],"force_p95":0.12556,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12276,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.49733,0.02156,0.22283]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4125.0,"contact_point_centroid":[0.49253,0.06715,0.04723],"force_p95":0.08194,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13463,"mean_force":0.05133,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49172,0.0479,0.04405]},{"body_a":"world","body_b":"grasp_target","contact_count":3964.0,"contact_point_centroid":[0.50118,0.04505,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.49742,0.04637,0.08694]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17941.0,"contact_point_centroid":[0.49772,0.09441,0.10082],"force_p95":0.0835,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12194,"mean_force":0.05437,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.49698,0.07526,0.10022]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20224.0,"contact_point_centroid":[0.49749,0.05643,0.10115],"force_p95":0.07309,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11904,"mean_force":0.04831,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.49706,0.07544,0.10037]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5136.0,"contact_point_centroid":[0.49195,0.02863,0.04603],"force_p95":0.07598,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08061,"mean_force":0.04408,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49173,0.0479,0.04406]}],"total_contact_groups":13},"final_pose_error":0.0134,"key_states":{"actual_goal_position":[0.56442,0.24486,0.14677],"final_object_position":[0.55162,0.24737,0.0265],"final_tcp_position":[0.55794,0.23709,0.13799],"realised_goal_position":[0.56442,0.24486,0.14677],"realised_object_initial_position":[0.50118,0.04505,0.03]},"peak_contact_force":273004.08121,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":918.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.03],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.23992,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3668.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_above_object","tcp_end":[0.49721,0.04259,0.15169],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12576,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":991.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3964.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_point","tcp_end":[0.4994,0.04867,0.0525],"tcp_start":[0.49721,0.04259,0.15169],"tcp_to_object_dist_end":0.02679,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50115,0.0471,0.02515],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24063,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.1767,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11061.0,"raw_peak_contact_force":0.24857,"subtask_id":"grasp_point","tcp_end":[0.49169,0.0479,0.04402],"tcp_start":[0.4994,0.04867,0.0525],"tcp_to_object_dist_end":0.02112,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49505,0.04696,0.05787],"object_pos_start":[0.50115,0.0471,0.02515],"object_to_goal_dist_end":0.22777,"object_to_goal_dist_start":0.24063,"object_z_max":0.05783,"peak_contact_force":0.08065,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":38925.0,"raw_peak_contact_force":0.35815,"subtask_id":"object_lifted","tcp_end":[0.49044,0.04719,0.08147],"tcp_start":[0.49169,0.0479,0.04402],"tcp_to_object_dist_end":0.02404,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":30.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51314,0.10376,0.09542],"object_pos_start":[0.49505,0.04696,0.05787],"object_to_goal_dist_end":0.15867,"object_to_goal_dist_start":0.22777,"object_z_max":0.09539,"peak_contact_force":0.08741,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":38165.0,"raw_peak_contact_force":0.12194,"subtask_id":"near_goal","tcp_end":[0.50776,0.10399,0.1238],"tcp_start":[0.49044,0.04719,0.08147],"tcp_to_object_dist_end":0.02889,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":902.0,"n_steps_budget":960.0,"object_pos_end":[0.55162,0.24737,0.0265],"object_pos_start":[0.51314,0.10376,0.09542],"object_to_goal_dist_end":0.12098,"object_to_goal_dist_start":0.15867,"object_z_max":0.10154,"peak_contact_force":273004.08121,"phase_name":"place_at_goal","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":19847.0,"raw_peak_contact_force":1.27545,"subtask_id":"placed_at_goal","tcp_end":[0.55468,0.23559,0.16423],"tcp_start":[0.50776,0.10399,0.1238],"tcp_to_object_dist_end":0.13827,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.85043,"average_solve_count":234.0,"average_success_count":234.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.05303,"descend_to_grasp.descend_speed":0.02488,"descend_to_grasp.grasp_offset_x":0.00786,"descend_to_grasp.grasp_offset_y":0.00118,"grasp.grasp_retry_offset_x":0.00087,"grasp.grasp_retry_offset_y":-0.00219,"lift.lift_distance":0.1224,"lift.lift_speed":0.02637,"transport_to_goal.transport_speed":0.03209},"optimized_scores":{"best_composite_score":-0.21499,"best_fitness_score":0.35501,"best_task_score":0.27269},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":885.0,"contact_point_centroid":[0.58444,0.08515,-0.00297],"force_p95":0.51733,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.10469,"mean_force":0.16171,"phase_index":5.0,"phase_name":"place_at_goal","phase_type":"release","tcp_position_centroid":[0.5857,0.11563,0.16527]},{"body_a":"world","body_b":"grasp_target","contact_count":683.0,"contact_point_centroid":[0.47203,-0.01829,-0.00149],"force_p95":0.18509,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.37496,"mean_force":0.08877,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46868,-0.01865,0.04661]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8349.0,"contact_point_centroid":[0.52411,0.0666,0.12249],"force_p95":0.14916,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28595,"mean_force":0.09446,"phase_index":5.0,"phase_name":"place_at_goal","phase_type":"release","tcp_position_centroid":[0.52312,0.048,0.12592]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20587.0,"contact_point_centroid":[0.46858,-0.03764,0.06527],"force_p95":0.072,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24471,"mean_force":0.04775,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.4683,-0.01866,0.06362]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17000.0,"contact_point_centroid":[0.46922,0.00053,0.06579],"force_p95":0.08066,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24051,"mean_force":0.05656,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46831,-0.01866,0.06394]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47616,-0.01999,-0.00213],"force_p95":0.15805,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21528,"mean_force":0.13254,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.47294,-0.01873,0.04632]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9984.0,"contact_point_centroid":[0.52617,0.03236,0.12374],"force_p95":0.12771,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19432,"mean_force":0.07962,"phase_index":5.0,"phase_name":"place_at_goal","phase_type":"release","tcp_position_centroid":[0.52559,0.05062,0.12722]},{"body_a":"world","body_b":"grasp_target","contact_count":2860.0,"contact_point_centroid":[0.47616,-0.02015,-0.00195],"force_p95":0.12892,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.1228,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.48594,-0.00928,0.22612]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4093.0,"contact_point_centroid":[0.47285,0.00057,0.04818],"force_p95":0.08026,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13742,"mean_force":0.05207,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.47182,-0.01871,0.04516]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":14156.0,"contact_point_centroid":[0.47592,0.01179,0.09322],"force_p95":0.1065,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12999,"mean_force":0.06731,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.47532,-0.00722,0.09414]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17203.0,"contact_point_centroid":[0.47529,-0.02581,0.09388],"force_p95":0.09207,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1231,"mean_force":0.05476,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.47541,-0.0071,0.09427]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.47579,-0.01882,0.09126]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5346.0,"contact_point_centroid":[0.47193,-0.03782,0.04759],"force_p95":0.06867,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07212,"mean_force":0.04158,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.47183,-0.01871,0.04517]}],"total_contact_groups":13},"final_pose_error":0.06674,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.58441,0.08498,0.01602],"final_tcp_position":[0.58865,0.11722,0.16064],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":1.10469,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":716.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2860.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_above_object","tcp_end":[0.47384,-0.01883,0.15409],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.1281,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_point","tcp_end":[0.47928,-0.01887,0.05291],"tcp_start":[0.47384,-0.01883,0.15409],"tcp_to_object_dist_end":0.0271,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47608,-0.01899,0.02551],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.288,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.15198,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11239.0,"raw_peak_contact_force":0.21528,"subtask_id":"grasp_point","tcp_end":[0.4718,-0.01871,0.04513],"tcp_start":[0.47928,-0.01887,0.05291],"tcp_to_object_dist_end":0.02009,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47131,-0.01879,0.06225],"object_pos_start":[0.47608,-0.01899,0.02551],"object_to_goal_dist_end":0.27137,"object_to_goal_dist_start":0.288,"object_z_max":0.06219,"peak_contact_force":0.08048,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":38270.0,"raw_peak_contact_force":0.37496,"subtask_id":"object_lifted","tcp_end":[0.46889,-0.0187,0.0856],"tcp_start":[0.4718,-0.01871,0.04513],"tcp_to_object_dist_end":0.02348,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.4882,0.00616,0.08002],"object_pos_start":[0.47131,-0.01879,0.06225],"object_to_goal_dist_end":0.2367,"object_to_goal_dist_start":0.27137,"object_z_max":0.08,"peak_contact_force":0.10681,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":31359.0,"raw_peak_contact_force":0.12999,"subtask_id":"near_goal","tcp_end":[0.48785,0.00663,0.1096],"tcp_start":[0.46889,-0.0187,0.0856],"tcp_to_object_dist_end":0.02959,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.58441,0.08498,0.01602],"object_pos_start":[0.4882,0.00616,0.08002],"object_to_goal_dist_end":0.19491,"object_to_goal_dist_start":0.2367,"object_z_max":0.1148,"peak_contact_force":0.12263,"phase_name":"place_at_goal","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":19218.0,"raw_peak_contact_force":1.10469,"subtask_id":"placed_at_goal","tcp_end":[0.58539,0.11649,0.18691],"tcp_start":[0.48785,0.00663,0.1096],"tcp_to_object_dist_end":0.17378,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.05991,"average_solve_count":217.0,"average_success_count":217.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.04577,"descend_to_grasp.descend_speed":0.03944,"descend_to_grasp.grasp_offset_x":0.00735,"descend_to_grasp.grasp_offset_y":-0.00071,"grasp.grasp_retry_offset_x":-3e-05,"grasp.grasp_retry_offset_y":-0.005,"lift.lift_distance":0.09501,"lift.lift_speed":0.02126,"transport_to_goal.transport_speed":0.09942},"optimized_scores":{"best_composite_score":-0.24015,"best_fitness_score":0.32985,"best_task_score":0.23436},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":4173.0,"contact_point_centroid":[0.50348,0.0604,-0.00211],"force_p95":0.12342,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.94518,"mean_force":0.13053,"phase_index":5.0,"phase_name":"place_at_goal","phase_type":"release","tcp_position_centroid":[0.55177,0.11374,0.10727]},{"body_a":"world","body_b":"grasp_target","contact_count":725.0,"contact_point_centroid":[0.45371,-0.02593,-0.00129],"force_p95":0.14782,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.29739,"mean_force":0.07574,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.45072,-0.0263,0.05124]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":332.0,"contact_point_centroid":[0.49162,0.05609,0.10537],"force_p95":0.21348,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26949,"mean_force":0.15827,"phase_index":5.0,"phase_name":"place_at_goal","phase_type":"release","tcp_position_centroid":[0.49484,0.03767,0.11038]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10988.0,"contact_point_centroid":[0.4711,0.02415,0.09204],"force_p95":0.11616,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23604,"mean_force":0.08465,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.47132,0.00544,0.09563]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":13959.0,"contact_point_centroid":[0.45133,-0.00729,0.06215],"force_p95":0.10539,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21719,"mean_force":0.0688,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.45047,-0.02625,0.06313]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16519.0,"contact_point_centroid":[0.45045,-0.04495,0.06229],"force_p95":0.0949,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2161,"mean_force":0.05769,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.45046,-0.02625,0.06299]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12667.0,"contact_point_centroid":[0.47082,-0.01287,0.09202],"force_p95":0.09655,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17034,"mean_force":0.07338,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.47144,0.00561,0.09571]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":696.0,"contact_point_centroid":[0.49551,0.02124,0.10497],"force_p95":0.10939,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1449,"mean_force":0.06259,"phase_index":5.0,"phase_name":"place_at_goal","phase_type":"release","tcp_position_centroid":[0.49512,0.03846,0.10993]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45856,-0.02629,-0.00202],"force_p95":0.12835,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.14286,"mean_force":0.12466,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.45482,-0.02648,0.05078]},{"body_a":"world","body_b":"grasp_target","contact_count":2884.0,"contact_point_centroid":[0.45856,-0.02632,-0.00195],"force_p95":0.12867,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.1228,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.47794,-0.01208,0.22648]},{"body_a":"world","body_b":"grasp_target","contact_count":2836.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.45772,-0.02562,0.10245]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4140.0,"contact_point_centroid":[0.45465,-0.00723,0.0503],"force_p95":0.07547,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09196,"mean_force":0.05191,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.45375,-0.02644,0.04971]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4848.0,"contact_point_centroid":[0.45382,-0.0455,0.05026],"force_p95":0.06797,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09152,"mean_force":0.04457,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.45375,-0.02644,0.04971]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3466.0,"contact_point_centroid":[0.55057,0.11134,0.10852],"force_p95":0.01101,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01479,"mean_force":0.01044,"phase_index":5.0,"phase_name":"place_at_goal","phase_type":"release","tcp_position_centroid":[0.55021,0.11134,0.10619]}],"total_contact_groups":14},"final_pose_error":0.05975,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.50366,0.06075,0.01602],"final_tcp_position":[0.59139,0.16352,0.10561],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":0.94518,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":722.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2884.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_above_object","tcp_end":[0.45743,-0.02458,0.15439],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12839,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":709.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2836.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_point","tcp_end":[0.46104,-0.02672,0.057],"tcp_start":[0.45743,-0.02458,0.15439],"tcp_to_object_dist_end":0.03108,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45848,-0.02627,0.0259],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30369,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12826,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10788.0,"raw_peak_contact_force":0.14286,"subtask_id":"grasp_point","tcp_end":[0.45372,-0.02644,0.04968],"tcp_start":[0.46104,-0.02672,0.057],"tcp_to_object_dist_end":0.02425,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.45216,-0.02643,0.0527],"object_pos_start":[0.45848,-0.02627,0.0259],"object_to_goal_dist_end":0.30084,"object_to_goal_dist_start":0.30369,"object_z_max":0.05267,"peak_contact_force":0.10441,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":31203.0,"raw_peak_contact_force":0.29739,"subtask_id":"object_lifted","tcp_end":[0.45121,-0.0262,0.08245],"tcp_start":[0.45372,-0.02644,0.04968],"tcp_to_object_dist_end":0.02977,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":20.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.4953,0.03508,0.07507],"object_pos_start":[0.45216,-0.02643,0.0527],"object_to_goal_dist_end":0.22289,"object_to_goal_dist_start":0.30084,"object_z_max":0.07506,"peak_contact_force":0.1845,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":23655.0,"raw_peak_contact_force":0.23604,"subtask_id":"near_goal","tcp_end":[0.49423,0.03551,0.11192],"tcp_start":[0.45121,-0.0262,0.08245],"tcp_to_object_dist_end":0.03687,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50366,0.06075,0.01602],"object_pos_start":[0.4953,0.03508,0.07507],"object_to_goal_dist_end":0.21763,"object_to_goal_dist_start":0.22289,"object_z_max":0.07507,"peak_contact_force":0.12263,"phase_name":"place_at_goal","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":8667.0,"raw_peak_contact_force":0.94518,"subtask_id":"placed_at_goal","tcp_end":[0.58756,0.16239,0.13166],"tcp_start":[0.49423,0.03551,0.11192],"tcp_to_object_dist_end":0.17534,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```