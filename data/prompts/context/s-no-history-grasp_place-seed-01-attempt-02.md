## Search State

- **Seed**: 1
- **Iteration**: 3 / 15

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

## Current Skill (Q=-0.239) — your mutation base

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

- **Composite score**: -0.239
- **task_score** (E): 0.197
- **fitness_score**: 0.301  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.540

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1473 |
| descend_to_grasp | 1.00 | 1.00 | 0.0955 |
| grasp | 1.00 | 1.00 | 0.0112 |
| lift_and_transport | 0.00 | 1.00 | 0.0837 |
| descend_to_place | 0.00 | 1.00 | 0.0695 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.477, -0.000, 0.159) | (0.479, -0.000, 0.030)→(0.479, -0.000, 0.026) | 0.276→0.278 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.477, -0.000, 0.159)→(0.482, 0.004, 0.064) | (0.479, -0.000, 0.026)→(0.479, -0.000, 0.026) | 0.278→0.278 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp | grasp | 1.00 / step_budget | (0.482, 0.004, 0.064)→(0.475, 0.004, 0.056) | (0.479, -0.000, 0.026)→(0.479, 0.003, 0.024) | 0.278→0.276 | 1.00 / 25.333 | 0.232 | 0.260 |
| lift_and_transport | approach | 0.00 / step_budget | (0.475, 0.004, 0.056)→(0.506, 0.059, 0.108) | (0.479, 0.003, 0.024)→(0.481, 0.050, 0.016) | 0.276→0.247 | 1.00 / 8.000 | 0.123 | 0.553 |
| descend_to_place | descend | 0.00 / step_budget | (0.506, 0.059, 0.108)→(0.540, 0.114, 0.129) | (0.481, 0.050, 0.016)→(0.481, 0.050, 0.016) | 0.247→0.247 | 1.00 / 8.000 | 3249.666 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 0.000
- transport_retention: None
- terminal_score: 0.253
- phase_score: 0.389
- phase_breakdown.reach_above_object_score: 0.821
- phase_breakdown.object_lifted_score: 0.009
- phase_breakdown.grasp_point_score: 0.850
- phase_breakdown.placed_at_goal_score: 0.174
- grasp_place_fitness: 0.331

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.331
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.253
- **Median Q (composite search score)**: -0.253
- **K-run variance**: 0.0005
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Parameters at lower bound**: lift_and_transport.transport_speed
- **Final σ (mean)**: 0.389


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.8972,"average_solve_count":214.0,"average_success_count":214.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.05043,"descend_to_grasp.descend_speed":0.03208,"descend_to_grasp.grasp_offset_x":0.00973,"descend_to_grasp.grasp_offset_y":0.00677,"descend_to_place.descend_place_speed":0.01154,"grasp.grasp_retry_offset_x":-0.00222,"grasp.grasp_retry_offset_y":0.00284,"lift_and_transport.lift_height":0.11075,"lift_and_transport.transport_speed":0.06496},"optimized_scores":{"best_composite_score":-0.20863,"best_fitness_score":0.33137,"best_task_score":0.25299},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":3264.0,"contact_point_centroid":[0.50218,0.08825,-0.00214],"force_p95":0.25237,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55994,"mean_force":0.14216,"phase_index":3.0,"phase_name":"lift_and_transport","phase_type":"approach","tcp_position_centroid":[0.50499,0.0843,0.0863]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1714.0,"contact_point_centroid":[0.49756,0.07559,0.05527],"force_p95":0.1854,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29741,"mean_force":0.10852,"phase_index":3.0,"phase_name":"lift_and_transport","phase_type":"approach","tcp_position_centroid":[0.49642,0.05738,0.05949]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50122,0.04525,-0.0023],"force_p95":0.20757,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.25834,"mean_force":0.14378,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49805,0.04931,0.05578]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2611.0,"contact_point_centroid":[0.49651,0.0399,0.05738],"force_p95":0.12938,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24875,"mean_force":0.08244,"phase_index":3.0,"phase_name":"lift_and_transport","phase_type":"approach","tcp_position_centroid":[0.49655,0.05809,0.06009]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2158.0,"contact_point_centroid":[0.49806,0.06799,0.05192],"force_p95":0.11546,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14074,"mean_force":0.09081,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49692,0.04919,0.0545]},{"body_a":"world","body_b":"grasp_target","contact_count":1984.0,"contact_point_centroid":[0.50118,0.04505,-0.00193],"force_p95":0.133,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12287,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.49773,0.01982,0.22897]},{"body_a":"world","body_b":"grasp_target","contact_count":1388.0,"contact_point_centroid":[0.50118,0.04505,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.49961,0.04511,0.1102]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.50261,0.09795,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":4.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.52156,0.14004,0.12077]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3177.0,"contact_point_centroid":[0.4966,0.03039,0.0516],"force_p95":0.1005,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10084,"mean_force":0.06671,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49693,0.04919,0.05452]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2774.0,"contact_point_centroid":[0.50757,0.09094,0.09513],"force_p95":0.01128,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01562,"mean_force":0.0106,"phase_index":3.0,"phase_name":"lift_and_transport","phase_type":"approach","tcp_position_centroid":[0.5071,0.09092,0.0929]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4276.0,"contact_point_centroid":[0.52202,0.14006,0.12304],"force_p95":0.01099,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01288,"mean_force":0.01043,"phase_index":4.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.52155,0.14003,0.12077]}],"total_contact_groups":11},"final_pose_error":0.09689,"key_states":{"actual_goal_position":[0.56442,0.24486,0.14677],"final_object_position":[0.50261,0.09795,0.01602],"final_tcp_position":[0.53101,0.16544,0.13246],"realised_goal_position":[0.56442,0.24486,0.14677],"realised_object_initial_position":[0.50118,0.04505,0.03]},"peak_contact_force":0.55994,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":497.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.03],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.23992,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1984.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_above_object","tcp_end":[0.49746,0.04071,0.15805],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13215,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":347.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1388.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_point","tcp_end":[0.50475,0.04996,0.06345],"tcp_start":[0.49746,0.04071,0.15805],"tcp_to_object_dist_end":0.03792,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50111,0.04776,0.02494],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24021,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.19707,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":7135.0,"raw_peak_contact_force":0.25834,"subtask_id":"grasp_point","tcp_end":[0.49689,0.04919,0.05447],"tcp_start":[0.50475,0.04996,0.06345],"tcp_to_object_dist_end":0.02986,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50261,0.09795,0.01602],"object_pos_start":[0.50111,0.04776,0.02494],"object_to_goal_dist_end":0.20616,"object_to_goal_dist_start":0.24021,"object_z_max":0.03286,"peak_contact_force":0.12263,"phase_name":"lift_and_transport","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":10363.0,"raw_peak_contact_force":0.55994,"subtask_id":"object_lifted","tcp_end":[0.51334,0.10846,0.11099],"tcp_start":[0.49689,0.04919,0.05447],"tcp_to_object_dist_end":0.09615,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50261,0.09795,0.01602],"object_pos_start":[0.50261,0.09795,0.01602],"object_to_goal_dist_end":0.20616,"object_to_goal_dist_start":0.20616,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8276.0,"raw_peak_contact_force":0.12263,"subtask_id":"placed_at_goal","tcp_end":[0.53101,0.16544,0.13246],"tcp_start":[0.51334,0.10846,0.11099],"tcp_to_object_dist_end":0.13755,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.18023,"average_solve_count":172.0,"average_success_count":172.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.0741,"descend_to_grasp.descend_speed":0.03952,"descend_to_grasp.grasp_offset_x":0.00864,"descend_to_grasp.grasp_offset_y":0.00998,"descend_to_place.descend_place_speed":0.03032,"grasp.grasp_retry_offset_x":-0.00483,"grasp.grasp_retry_offset_y":-0.0033,"lift_and_transport.lift_height":0.12292,"lift_and_transport.transport_speed":0.04507},"optimized_scores":{"best_composite_score":-0.25518,"best_fitness_score":0.28482,"best_task_score":0.17035},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":3347.0,"contact_point_centroid":[0.47896,0.02149,-0.00242],"force_p95":0.29952,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54923,"mean_force":0.14779,"phase_index":3.0,"phase_name":"lift_and_transport","phase_type":"approach","tcp_position_centroid":[0.49069,0.01352,0.08835]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47619,-0.01989,-0.00266],"force_p95":0.34969,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.36544,"mean_force":0.17024,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.47278,-0.01104,0.05717]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1910.0,"contact_point_centroid":[0.47428,-0.01409,0.057],"force_p95":0.10556,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23326,"mean_force":0.05076,"phase_index":3.0,"phase_name":"lift_and_transport","phase_type":"approach","tcp_position_centroid":[0.47397,-0.00517,0.06146]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1322.0,"contact_point_centroid":[0.47537,0.00495,0.04969],"force_p95":0.17745,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1921,"mean_force":0.1074,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.4717,-0.01104,0.05604]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":809.0,"contact_point_centroid":[0.47751,0.00329,0.05542],"force_p95":0.15052,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18507,"mean_force":0.08549,"phase_index":3.0,"phase_name":"lift_and_transport","phase_type":"approach","tcp_position_centroid":[0.47429,-0.00478,0.06198]},{"body_a":"world","body_b":"grasp_target","contact_count":1732.0,"contact_point_centroid":[0.47616,-0.02015,-0.00192],"force_p95":0.13411,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12291,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.48682,-0.00874,0.23036]},{"body_a":"world","body_b":"grasp_target","contact_count":1392.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.47561,-0.01469,0.1114]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.47956,0.02825,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":4.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.52598,0.05412,0.12737]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3386.0,"contact_point_centroid":[0.47148,-0.02816,0.05279],"force_p95":0.10343,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10748,"mean_force":0.05357,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.47174,-0.01104,0.05608]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2839.0,"contact_point_centroid":[0.49459,0.01765,0.0966],"force_p95":0.01129,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01642,"mean_force":0.01068,"phase_index":3.0,"phase_name":"lift_and_transport","phase_type":"approach","tcp_position_centroid":[0.49442,0.01765,0.09434]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4224.0,"contact_point_centroid":[0.52628,0.05406,0.1295],"force_p95":0.01101,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01286,"mean_force":0.01054,"phase_index":4.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.52592,0.05406,0.12732]}],"total_contact_groups":11},"final_pose_error":0.14414,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.47956,0.02825,0.01602],"final_tcp_position":[0.54483,0.07357,0.14288],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":0.54923,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":434.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1732.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_above_object","tcp_end":[0.47485,-0.01808,0.15958],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13358,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":348.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1392.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_point","tcp_end":[0.47924,-0.01112,0.06406],"tcp_start":[0.47485,-0.01808,0.15958],"tcp_to_object_dist_end":0.03922,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47618,-0.01137,0.02257],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.285,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.36551,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":6508.0,"raw_peak_contact_force":0.36544,"subtask_id":"grasp_point","tcp_end":[0.47167,-0.01105,0.05601],"tcp_start":[0.47924,-0.01112,0.06406],"tcp_to_object_dist_end":0.03374,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47956,0.02825,0.01602],"object_pos_start":[0.47618,-0.01137,0.02257],"object_to_goal_dist_end":0.26548,"object_to_goal_dist_start":0.285,"object_z_max":0.03076,"peak_contact_force":0.12263,"phase_name":"lift_and_transport","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8905.0,"raw_peak_contact_force":0.54923,"subtask_id":"object_lifted","tcp_end":[0.50606,0.02987,0.11263],"tcp_start":[0.47167,-0.01105,0.05601],"tcp_to_object_dist_end":0.10019,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47956,0.02825,0.01602],"object_pos_start":[0.47956,0.02825,0.01602],"object_to_goal_dist_end":0.26548,"object_to_goal_dist_start":0.26548,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8224.0,"raw_peak_contact_force":0.12263,"subtask_id":"placed_at_goal","tcp_end":[0.54483,0.07357,0.14288],"tcp_start":[0.50606,0.02987,0.11263],"tcp_to_object_dist_end":0.14969,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.95305,"average_solve_count":213.0,"average_success_count":213.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.05053,"descend_to_grasp.descend_speed":0.03269,"descend_to_grasp.grasp_offset_x":0.00908,"descend_to_grasp.grasp_offset_y":-0.00127,"descend_to_place.descend_place_speed":0.02843,"grasp.grasp_retry_offset_x":-0.00181,"grasp.grasp_retry_offset_y":0.0027,"lift_and_transport.lift_height":0.12523,"lift_and_transport.transport_speed":0.01},"optimized_scores":{"best_composite_score":-0.25317,"best_fitness_score":0.28683,"best_task_score":0.16744},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":3322.0,"contact_point_centroid":[0.46093,0.01355,-0.00218],"force_p95":0.28887,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54942,"mean_force":0.14464,"phase_index":3.0,"phase_name":"lift_and_transport","phase_type":"approach","tcp_position_centroid":[0.47911,0.01109,0.08159]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1688.0,"contact_point_centroid":[0.45859,-0.00117,0.05591],"force_p95":0.151,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2466,"mean_force":0.09972,"phase_index":3.0,"phase_name":"lift_and_transport","phase_type":"approach","tcp_position_centroid":[0.45831,-0.0179,0.06036]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2454.0,"contact_point_centroid":[0.45904,-0.03228,0.05719],"force_p95":0.13624,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2277,"mean_force":0.08237,"phase_index":3.0,"phase_name":"lift_and_transport","phase_type":"approach","tcp_position_centroid":[0.45922,-0.01641,0.06128]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45856,-0.02639,-0.00203],"force_p95":0.13333,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15486,"mean_force":0.12537,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.45605,-0.02669,0.05793]},{"body_a":"world","body_b":"grasp_target","contact_count":1872.0,"contact_point_centroid":[0.45856,-0.02632,-0.00193],"force_p95":0.13354,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12289,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.47921,-0.01144,0.2303]},{"body_a":"world","body_b":"grasp_target","contact_count":1408.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.45931,-0.0252,0.11173]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.46141,0.02445,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":4.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.5225,0.0732,0.10497]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2667.0,"contact_point_centroid":[0.45475,-0.0455,0.05385],"force_p95":0.09935,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11968,"mean_force":0.07621,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.45499,-0.02665,0.05686]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3179.0,"contact_point_centroid":[0.45502,-0.00799,0.05344],"force_p95":0.08696,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08718,"mean_force":0.06511,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.45499,-0.02665,0.05686]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2649.0,"contact_point_centroid":[0.48555,0.01961,0.09013],"force_p95":0.01134,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01616,"mean_force":0.01075,"phase_index":3.0,"phase_name":"lift_and_transport","phase_type":"approach","tcp_position_centroid":[0.48528,0.01961,0.08788]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4273.0,"contact_point_centroid":[0.52274,0.07317,0.10726],"force_p95":0.01097,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01285,"mean_force":0.01044,"phase_index":4.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.52248,0.07317,0.10497]}],"total_contact_groups":11},"final_pose_error":0.14056,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.46141,0.02445,0.01602],"final_tcp_position":[0.5444,0.10177,0.11129],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":9748.75272,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":469.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1872.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_above_object","tcp_end":[0.45907,-0.02367,0.15959],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.1336,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":352.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1408.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_point","tcp_end":[0.46238,-0.02693,0.06439],"tcp_start":[0.45907,-0.02367,0.15959],"tcp_to_object_dist_end":0.03856,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":28.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45848,-0.02672,0.02587],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30405,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.13197,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":7646.0,"raw_peak_contact_force":0.15486,"subtask_id":"grasp_point","tcp_end":[0.45496,-0.02665,0.05683],"tcp_start":[0.46238,-0.02693,0.06439],"tcp_to_object_dist_end":0.03116,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.46141,0.02445,0.01602],"object_pos_start":[0.45848,-0.02672,0.02587],"object_to_goal_dist_end":0.26807,"object_to_goal_dist_start":0.30405,"object_z_max":0.02983,"peak_contact_force":0.12263,"phase_name":"lift_and_transport","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":10113.0,"raw_peak_contact_force":0.54942,"subtask_id":"object_lifted","tcp_end":[0.49884,0.03763,0.10167],"tcp_start":[0.45496,-0.02665,0.05683],"tcp_to_object_dist_end":0.0944,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.46141,0.02445,0.01602],"object_pos_start":[0.46141,0.02445,0.01602],"object_to_goal_dist_end":0.26807,"object_to_goal_dist_start":0.26807,"object_z_max":0.01602,"peak_contact_force":9748.75272,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8273.0,"raw_peak_contact_force":0.12263,"subtask_id":"placed_at_goal","tcp_end":[0.5444,0.10177,0.11129],"tcp_start":[0.49884,0.03763,0.10167],"tcp_to_object_dist_end":0.14813,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```