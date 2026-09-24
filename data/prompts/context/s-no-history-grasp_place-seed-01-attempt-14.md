## Search State

- **Seed**: 1
- **Iteration**: 15 / 15

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

## Current Skill (Q=0.269) — your mutation base

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
    tolerance: 0.015
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
    - 0.0
    tolerance: 0.015
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
    - 0.0
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
    tolerance: 0.02
    orientation:
      mode: keep_current
      tolerance: 0.1
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
      - 0.01
      - 0.06
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: lift_grasp_check
    when: after_phase
    predicate: bilateral_grasp
    threshold: 0.5
    on_failure: abort
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
    tolerance: 0.025
    orientation:
      mode: keep_current
      tolerance: 0.1
  parameters:
    transport_speed:
      type: scalar
      range:
      - 0.03
      - 0.1
      default: 0.06
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: transport_grasp_check
    when: after_phase
    predicate: bilateral_grasp
    threshold: 0.5
    on_failure: abort
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
    tolerance: 0.015
    orientation:
      mode: keep_current
      tolerance: 0.1
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
    place_speed:
      type: scalar
      range:
      - 0.005
      - 0.04
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: placed_at_goal

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_object** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.12], tolerance=0.015
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_grasp** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0], tolerance=0.015
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (replace)
    - grasp_offset_x: status=consumed; consumers=target.offset.x (add)
    - grasp_offset_y: status=consumed; consumers=target.offset.y (add)
- **grasp** (`grasp`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - grasp_retry_offset_x: status=consumed; consumers=retry.offset.x (add)
    - grasp_retry_offset_y: status=consumed; consumers=retry.offset.y (add)
  - guards:
    - id=grasp_check, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=0.8
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, 0.0]
- **lift_object** (`lift`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.15, mode=replace_offset_projection, sign=positive}, tolerance=0.02
  - orientation: mode=keep_current, tolerance=0.1
  - parameter_bindings:
    - lift_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - lift_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=lift_grasp_check, when=after_phase, predicate=bilateral_grasp, on_failure=abort, threshold=0.5
- **transport_to_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.1], tolerance=0.025
  - orientation: mode=keep_current, tolerance=0.1
  - parameter_bindings:
    - transport_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=transport_grasp_check, when=after_phase, predicate=bilateral_grasp, on_failure=abort, threshold=0.5
- **place_at_goal** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.015
  - orientation: mode=keep_current, tolerance=0.1
  - parameter_bindings:
    - place_offset_x: status=consumed; consumers=target.offset.x (add)
    - place_offset_y: status=consumed; consumers=target.offset.y (add)
    - place_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: 0.269
- **task_score** (E): 1.000
- **fitness_score**: 0.989  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.720

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1422 |
| descend_to_grasp | 1.00 | 1.00 | 0.1246 |
| grasp | 1.00 | 1.00 | 0.0117 |
| lift_object | 1.00 | 1.00 | 0.1380 |
| transport_to_goal | 1.00 | 1.00 | 0.2402 |
| place_at_goal | 1.00 | 1.00 | 0.0749 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.478, -0.000, 0.164) | (0.479, -0.000, 0.030)→(0.479, -0.000, 0.026) | 0.276→0.278 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.478, -0.000, 0.164)→(0.483, -0.000, 0.040) | (0.479, -0.000, 0.026)→(0.479, -0.000, 0.026) | 0.278→0.278 | 1.00 / 4.000 | 10.805 | 0.123 |
| grasp | grasp | 1.00 / step_budget | (0.483, -0.000, 0.040)→(0.475, -0.000, 0.031) | (0.479, -0.000, 0.026)→(0.479, -0.000, 0.026) | 0.278→0.278 | 1.00 / 44.000 | 0.134 | 0.161 |
| lift_object | lift | 1.00 / step_budget | (0.475, -0.000, 0.031)→(0.471, -0.000, 0.169) | (0.479, -0.000, 0.026)→(0.474, -0.000, 0.162) | 0.278→0.249 | 1.00 / 40.000 | 0.071 | 0.562 |
| transport_to_goal | approach | 1.00 / step_budget | (0.471, -0.000, 0.169)→(0.597, 0.188, 0.236) | (0.474, -0.000, 0.162)→(0.602, 0.188, 0.227) | 0.249→0.079 | 1.00 / 40.000 | 0.071 | 0.096 |
| place_at_goal | descend | 1.00 / step_budget | (0.597, 0.188, 0.236)→(0.597, 0.201, 0.163) | (0.602, 0.188, 0.227)→(0.604, 0.201, 0.152) | 0.079→0.006 | 1.00 / 40.000 | 0.071 | 0.181 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.827
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 1.000
- phase_score: 0.771
- phase_breakdown.near_goal_score: 0.610
- phase_breakdown.reach_above_object_score: 0.746
- phase_breakdown.object_lifted_score: 0.845
- phase_breakdown.grasp_point_score: 0.912
- phase_breakdown.placed_at_goal_score: 0.742
- grasp_place_fitness: 0.990

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.990
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.269
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.355


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.07418,"average_solve_count":337.0,"average_success_count":337.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.08614,"descend_to_grasp.descend_speed":0.03322,"descend_to_grasp.grasp_offset_x":0.00999,"descend_to_grasp.grasp_offset_y":0.00164,"grasp.grasp_retry_offset_x":-0.00043,"grasp.grasp_retry_offset_y":0.00063,"lift_object.lift_distance":0.16742,"lift_object.lift_speed":0.04371,"place_at_goal.place_offset_x":-0.00437,"place_at_goal.place_offset_y":0.00763,"place_at_goal.place_speed":0.03439,"transport_to_goal.transport_speed":0.05476},"optimized_scores":{"best_composite_score":0.26994,"best_fitness_score":0.98994,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":92.0,"contact_point_centroid":[0.49697,0.04421,-0.00149],"force_p95":0.57759,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.59757,"mean_force":0.21066,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49548,0.04438,0.03126]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10320.0,"contact_point_centroid":[0.49314,0.0633,0.10466],"force_p95":0.07214,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29893,"mean_force":0.05095,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49293,0.04414,0.10286]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10320.0,"contact_point_centroid":[0.49317,0.025,0.10483],"force_p95":0.07127,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26585,"mean_force":0.05039,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49293,0.04414,0.10286]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50116,0.04493,-0.00205],"force_p95":0.13784,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17472,"mean_force":0.12716,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49778,0.04461,0.03131]},{"body_a":"world","body_b":"grasp_target","contact_count":1356.0,"contact_point_centroid":[0.50118,0.04505,-0.0019],"force_p95":0.13561,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12299,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.49817,0.01889,0.23238]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3700.0,"contact_point_centroid":[0.55522,0.25395,0.19882],"force_p95":0.07073,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12679,"mean_force":0.04971,"phase_index":5.0,"phase_name":"place_at_goal","phase_type":"descend","tcp_position_centroid":[0.55498,0.23474,0.19719]},{"body_a":"world","body_b":"grasp_target","contact_count":1292.0,"contact_point_centroid":[0.50118,0.04505,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.49992,0.04208,0.10146]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3700.0,"contact_point_centroid":[0.55528,0.21568,0.19932],"force_p95":0.07079,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11608,"mean_force":0.04866,"phase_index":5.0,"phase_name":"place_at_goal","phase_type":"descend","tcp_position_centroid":[0.55498,0.23474,0.19719]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4824.0,"contact_point_centroid":[0.49682,0.02532,0.03202],"force_p95":0.07002,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10739,"mean_force":0.0447,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49661,0.0445,0.03006]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4909.0,"contact_point_centroid":[0.4968,0.06372,0.03188],"force_p95":0.07035,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08593,"mean_force":0.04484,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49661,0.0445,0.03006]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9800.0,"contact_point_centroid":[0.52361,0.11647,0.2058],"force_p95":0.07126,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08472,"mean_force":0.04834,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52335,0.1356,0.20377]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9800.0,"contact_point_centroid":[0.52358,0.15474,0.20551],"force_p95":0.06994,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07847,"mean_force":0.04815,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52335,0.1356,0.20377]}],"total_contact_groups":12},"final_pose_error":0.01491,"key_states":{"actual_goal_position":[0.56442,0.24486,0.14677],"final_object_position":[0.56206,0.24477,0.1493],"final_tcp_position":[0.55565,0.2449,0.15883],"realised_goal_position":[0.56442,0.24486,0.14677],"realised_object_initial_position":[0.50118,0.04505,0.03]},"peak_contact_force":32.16866,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":340.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.03],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.23992,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1356.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_above_object","tcp_end":[0.49777,0.03924,0.16298],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13713,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":323.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":32.16866,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1292.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_point","tcp_end":[0.50492,0.04526,0.03919],"tcp_start":[0.49777,0.03924,0.16298],"tcp_to_object_dist_end":0.0137,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50105,0.04455,0.02578],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24245,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.13583,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11533.0,"raw_peak_contact_force":0.17472,"subtask_id":"grasp_point","tcp_end":[0.49658,0.04449,0.03003],"tcp_start":[0.50492,0.04526,0.03919],"tcp_to_object_dist_end":0.00616,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":516.0,"n_steps_budget":1000.0,"object_pos_end":[0.49677,0.04417,0.17175],"object_pos_start":[0.50105,0.04455,0.02578],"object_to_goal_dist_end":0.21325,"object_to_goal_dist_start":0.24245,"object_z_max":0.17147,"peak_contact_force":0.07083,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":20732.0,"raw_peak_contact_force":0.59757,"subtask_id":"object_lifted","tcp_end":[0.49312,0.04416,0.17781],"tcp_start":[0.49658,0.04449,0.03003],"tcp_to_object_dist_end":0.00707,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":490.0,"n_steps_budget":1000.0,"object_pos_end":[0.56017,0.2261,0.22498],"object_pos_start":[0.49677,0.04417,0.17175],"object_to_goal_dist_end":0.08054,"object_to_goal_dist_start":0.21325,"object_z_max":0.22488,"peak_contact_force":0.07034,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":19600.0,"raw_peak_contact_force":0.08472,"subtask_id":"near_goal","tcp_end":[0.55565,0.22618,0.2332],"tcp_start":[0.49312,0.04416,0.17781],"tcp_to_object_dist_end":0.00938,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":185.0,"n_steps_budget":1000.0,"object_pos_end":[0.56206,0.24477,0.1493],"object_pos_start":[0.56017,0.2261,0.22498],"object_to_goal_dist_end":0.00346,"object_to_goal_dist_start":0.08054,"object_z_max":0.22501,"peak_contact_force":0.07078,"phase_name":"place_at_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":7400.0,"raw_peak_contact_force":0.12679,"subtask_id":"placed_at_goal","tcp_end":[0.55565,0.2449,0.15883],"tcp_start":[0.55565,0.22618,0.2332],"tcp_to_object_dist_end":0.01148,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.11012,"average_solve_count":336.0,"average_success_count":336.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.08967,"descend_to_grasp.descend_speed":0.03174,"descend_to_grasp.grasp_offset_x":0.00998,"descend_to_grasp.grasp_offset_y":-0.00079,"grasp.grasp_retry_offset_x":-0.00153,"grasp.grasp_retry_offset_y":0.00145,"lift_object.lift_distance":0.16488,"lift_object.lift_speed":0.04904,"place_at_goal.place_offset_x":-0.01588,"place_at_goal.place_offset_y":-0.00713,"place_at_goal.place_speed":0.02739,"transport_to_goal.transport_speed":0.06853},"optimized_scores":{"best_composite_score":0.26906,"best_fitness_score":0.98906,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":86.0,"contact_point_centroid":[0.4718,-0.02014,-0.00143],"force_p95":0.57923,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.59776,"mean_force":0.20497,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.47147,-0.02016,0.03288]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9740.0,"contact_point_centroid":[0.46922,-0.03923,0.10488],"force_p95":0.07049,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29504,"mean_force":0.05095,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46899,-0.02008,0.10302]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9740.0,"contact_point_centroid":[0.4692,-0.00094,0.10494],"force_p95":0.07052,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29195,"mean_force":0.05089,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46899,-0.02008,0.10302]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3160.0,"contact_point_centroid":[0.61568,0.16702,0.24301],"force_p95":0.07277,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20329,"mean_force":0.05045,"phase_index":5.0,"phase_name":"place_at_goal","phase_type":"descend","tcp_position_centroid":[0.61545,0.14783,0.2412]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3160.0,"contact_point_centroid":[0.61575,0.12874,0.24316],"force_p95":0.07226,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14654,"mean_force":0.0493,"phase_index":5.0,"phase_name":"place_at_goal","phase_type":"descend","tcp_position_centroid":[0.61545,0.14783,0.2412]},{"body_a":"world","body_b":"grasp_target","contact_count":1276.0,"contact_point_centroid":[0.47616,-0.02015,-0.0019],"force_p95":0.13575,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12301,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.48781,-0.00836,0.23348]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47614,-0.02015,-0.00202],"force_p95":0.12842,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13062,"mean_force":0.12463,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.47363,-0.02021,0.03275]},{"body_a":"world","body_b":"grasp_target","contact_count":1316.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.47698,-0.01881,0.1027]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12120.0,"contact_point_centroid":[0.5437,0.04512,0.22618],"force_p95":0.0711,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11011,"mean_force":0.04878,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.54345,0.06425,0.22429]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12120.0,"contact_point_centroid":[0.54368,0.08339,0.22617],"force_p95":0.06997,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09636,"mean_force":0.04852,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.54345,0.06425,0.22429]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4864.0,"contact_point_centroid":[0.4727,-0.00098,0.03354],"force_p95":0.06761,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08756,"mean_force":0.04473,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.47251,-0.02018,0.03162]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4862.0,"contact_point_centroid":[0.47272,-0.03938,0.03349],"force_p95":0.06761,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08677,"mean_force":0.04473,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.47251,-0.02018,0.03162]}],"total_contact_groups":12},"final_pose_error":0.01478,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.62226,0.14969,0.19267],"final_tcp_position":[0.61323,0.14964,0.20441],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":0.59776,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":320.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1276.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_above_object","tcp_end":[0.47615,-0.01741,0.16465],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13866,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":329.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1316.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_point","tcp_end":[0.48053,-0.02036,0.0399],"tcp_start":[0.47615,-0.01741,0.16465],"tcp_to_object_dist_end":0.01455,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47603,-0.02018,0.02589],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28854,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.12826,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11526.0,"raw_peak_contact_force":0.13062,"subtask_id":"grasp_point","tcp_end":[0.47248,-0.02018,0.03159],"tcp_start":[0.48053,-0.02036,0.0399],"tcp_to_object_dist_end":0.00671,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":487.0,"n_steps_budget":1000.0,"object_pos_end":[0.47192,-0.02006,0.16943],"object_pos_start":[0.47603,-0.02018,0.02589],"object_to_goal_dist_end":0.24083,"object_to_goal_dist_start":0.28854,"object_z_max":0.16914,"peak_contact_force":0.06942,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":19566.0,"raw_peak_contact_force":0.59776,"subtask_id":"object_lifted","tcp_end":[0.46912,-0.02007,0.17677],"tcp_start":[0.47248,-0.02018,0.03159],"tcp_to_object_dist_end":0.00786,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":606.0,"n_steps_budget":1000.0,"object_pos_end":[0.62574,0.14637,0.26399],"object_pos_start":[0.47192,-0.02006,0.16943],"object_to_goal_dist_end":0.0753,"object_to_goal_dist_start":0.24083,"object_z_max":0.26386,"peak_contact_force":0.07038,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":24240.0,"raw_peak_contact_force":0.11011,"subtask_id":"near_goal","tcp_end":[0.61805,0.14622,0.27382],"tcp_start":[0.46912,-0.02007,0.17677],"tcp_to_object_dist_end":0.01247,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":158.0,"n_steps_budget":1000.0,"object_pos_end":[0.62226,0.14969,0.19267],"object_pos_start":[0.62574,0.14637,0.26399],"object_to_goal_dist_end":0.01346,"object_to_goal_dist_start":0.0753,"object_z_max":0.26403,"peak_contact_force":0.07208,"phase_name":"place_at_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":6320.0,"raw_peak_contact_force":0.20329,"subtask_id":"placed_at_goal","tcp_end":[0.61323,0.14964,0.20441],"tcp_start":[0.61805,0.14622,0.27382],"tcp_to_object_dist_end":0.01482,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.84375,"average_solve_count":448.0,"average_success_count":448.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.05483,"descend_to_grasp.descend_speed":0.01306,"descend_to_grasp.grasp_offset_x":0.0096,"descend_to_grasp.grasp_offset_y":-0.00025,"grasp.grasp_retry_offset_x":-0.00058,"grasp.grasp_retry_offset_y":0.00012,"lift_object.lift_distance":0.14036,"lift_object.lift_speed":0.02344,"place_at_goal.place_offset_x":-8e-05,"place_at_goal.place_offset_y":0.00654,"place_at_goal.place_speed":0.02896,"transport_to_goal.transport_speed":0.07324},"optimized_scores":{"best_composite_score":0.26851,"best_fitness_score":0.98851,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":108.0,"contact_point_centroid":[0.45479,-0.0256,-0.00158],"force_p95":0.42203,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.49022,"mean_force":0.20905,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.45408,-0.02562,0.03298]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8340.0,"contact_point_centroid":[0.45203,-0.04466,0.09248],"force_p95":0.07232,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24538,"mean_force":0.05122,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.45181,-0.02551,0.09063]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8340.0,"contact_point_centroid":[0.45201,-0.00637,0.09255],"force_p95":0.07139,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2325,"mean_force":0.05087,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.45181,-0.02551,0.09063]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3740.0,"contact_point_centroid":[0.6185,0.21859,0.16633],"force_p95":0.07005,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21438,"mean_force":0.04961,"phase_index":5.0,"phase_name":"place_at_goal","phase_type":"descend","tcp_position_centroid":[0.61826,0.1994,0.16455]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45855,-0.0262,-0.00206],"force_p95":0.13987,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17911,"mean_force":0.12761,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.45635,-0.02569,0.03312]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3740.0,"contact_point_centroid":[0.61855,0.18031,0.16654],"force_p95":0.06999,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14577,"mean_force":0.04878,"phase_index":5.0,"phase_name":"place_at_goal","phase_type":"descend","tcp_position_centroid":[0.61826,0.1994,0.16455]},{"body_a":"world","body_b":"grasp_target","contact_count":1376.0,"contact_point_centroid":[0.45856,-0.02632,-0.0019],"force_p95":0.1356,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12298,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.4803,-0.01095,0.23335]},{"body_a":"world","body_b":"grasp_target","contact_count":1360.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.4605,-0.02427,0.10289]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4816.0,"contact_point_centroid":[0.45544,-0.00647,0.03399],"force_p95":0.06987,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11159,"mean_force":0.04478,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.45526,-0.02565,0.03207]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13000.0,"contact_point_centroid":[0.53393,0.06572,0.17802],"force_p95":0.07028,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09195,"mean_force":0.04847,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.53368,0.08487,0.17613]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":13000.0,"contact_point_centroid":[0.53391,0.10399,0.17801],"force_p95":0.07021,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08486,"mean_force":0.04807,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.53368,0.08487,0.17613]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4920.0,"contact_point_centroid":[0.45546,-0.04488,0.03394],"force_p95":0.07019,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08435,"mean_force":0.04481,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.45526,-0.02565,0.03207]}],"total_contact_groups":12},"final_pose_error":0.01489,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.62769,0.20806,0.11467],"final_tcp_position":[0.6228,0.20812,0.12531],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":0.49022,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":345.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1376.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_above_object","tcp_end":[0.46064,-0.02283,0.16436],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.1384,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":340.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1360.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_point","tcp_end":[0.46303,-0.02592,0.03976],"tcp_start":[0.46064,-0.02283,0.16436],"tcp_to_object_dist_end":0.01445,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45844,-0.02574,0.02576],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30335,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.13751,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11536.0,"raw_peak_contact_force":0.17911,"subtask_id":"grasp_point","tcp_end":[0.45523,-0.02565,0.03204],"tcp_start":[0.46303,-0.02592,0.03976],"tcp_to_object_dist_end":0.00706,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":417.0,"n_steps_budget":1000.0,"object_pos_end":[0.45395,-0.02552,0.14581],"object_pos_start":[0.45844,-0.02574,0.02576],"object_to_goal_dist_end":0.29441,"object_to_goal_dist_start":0.30335,"object_z_max":0.14552,"peak_contact_force":0.0714,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":16788.0,"raw_peak_contact_force":0.49022,"subtask_id":"object_lifted","tcp_end":[0.45176,-0.02549,0.15298],"tcp_start":[0.45523,-0.02565,0.03204],"tcp_to_object_dist_end":0.00749,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":650.0,"n_steps_budget":1000.0,"object_pos_end":[0.61933,0.19211,0.19213],"object_pos_start":[0.45395,-0.02552,0.14581],"object_to_goal_dist_end":0.08038,"object_to_goal_dist_start":0.29441,"object_z_max":0.19207,"peak_contact_force":0.07142,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":26000.0,"raw_peak_contact_force":0.09195,"subtask_id":"near_goal","tcp_end":[0.61585,0.19215,0.20165],"tcp_start":[0.45176,-0.02549,0.15298],"tcp_to_object_dist_end":0.01013,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":187.0,"n_steps_budget":1000.0,"object_pos_end":[0.62769,0.20806,0.11467],"object_pos_start":[0.61933,0.19211,0.19213],"object_to_goal_dist_end":0.00251,"object_to_goal_dist_start":0.08038,"object_z_max":0.19213,"peak_contact_force":0.0699,"phase_name":"place_at_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":7480.0,"raw_peak_contact_force":0.21438,"subtask_id":"placed_at_goal","tcp_end":[0.6228,0.20812,0.12531],"tcp_start":[0.61585,0.19215,0.20165],"tcp_to_object_dist_end":0.01171,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```