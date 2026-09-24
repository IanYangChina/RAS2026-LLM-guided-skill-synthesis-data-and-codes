## Search State

- **Seed**: 1
- **Iteration**: 14 / 15

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
    - 0.0
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
    tolerance: 0.02
    orientation:
      mode: keep_current
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
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.12], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_grasp** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0], tolerance=0.005
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
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.15, mode=replace_offset_projection, sign=positive}, tolerance=0.015
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - lift_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=lift_grasp_check, when=after_phase, predicate=bilateral_grasp, on_failure=abort, threshold=0.5
- **transport_to_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.1], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - transport_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=transport_grasp_check, when=after_phase, predicate=bilateral_grasp, on_failure=abort, threshold=0.5
- **place_at_goal** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - orientation: mode=keep_current
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
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.720

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1532 |
| descend_to_grasp | 1.00 | 1.00 | 0.1205 |
| grasp | 1.00 | 1.00 | 0.0109 |
| lift_object | 1.00 | 1.00 | 0.1349 |
| transport_to_goal | 1.00 | 1.00 | 0.2507 |
| place_at_goal | 1.00 | 1.00 | 0.0825 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.476, -0.000, 0.153) | (0.479, -0.000, 0.030)→(0.479, -0.000, 0.026) | 0.276→0.278 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.476, -0.000, 0.153)→(0.480, -0.001, 0.033) | (0.479, -0.000, 0.026)→(0.479, -0.000, 0.026) | 0.278→0.278 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp | grasp | 1.00 / step_budget | (0.480, -0.001, 0.033)→(0.472, -0.002, 0.025) | (0.479, -0.000, 0.026)→(0.478, -0.001, 0.024) | 0.278→0.280 | 1.00 / 43.667 | 0.238 | 0.341 |
| lift_object | lift | 1.00 / step_budget | (0.472, -0.002, 0.025)→(0.468, -0.002, 0.160) | (0.478, -0.001, 0.024)→(0.474, -0.002, 0.156) | 0.280→0.251 | 1.00 / 40.000 | 0.078 | 0.645 |
| transport_to_goal | approach | 1.00 / step_budget | (0.468, -0.002, 0.160)→(0.599, 0.193, 0.237) | (0.474, -0.002, 0.156)→(0.604, 0.193, 0.229) | 0.251→0.080 | 1.00 / 40.667 | 0.071 | 0.092 |
| place_at_goal | descend | 1.00 / step_budget | (0.599, 0.193, 0.237)→(0.608, 0.202, 0.157) | (0.604, 0.193, 0.229)→(0.615, 0.202, 0.146) | 0.080→0.011 | 1.00 / 42.000 | 0.070 | 0.129 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.343
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 1.000
- phase_score: 0.730
- phase_breakdown.near_goal_score: 0.672
- phase_breakdown.reach_above_object_score: 0.907
- phase_breakdown.object_lifted_score: 0.419
- phase_breakdown.grasp_point_score: 0.830
- phase_breakdown.placed_at_goal_score: 0.822
- grasp_place_fitness: 0.995

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.995
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.270
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.323


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.0327,"average_solve_count":367.0,"average_success_count":367.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.05822,"descend_to_grasp.descend_speed":0.03154,"descend_to_grasp.grasp_offset_x":0.002,"descend_to_grasp.grasp_offset_y":-0.00625,"grasp.grasp_retry_offset_x":-0.00303,"grasp.grasp_retry_offset_y":-0.0004,"lift_object.lift_distance":0.17099,"lift_object.lift_speed":0.03432,"place_at_goal.place_offset_x":-0.00349,"place_at_goal.place_offset_y":-0.00231,"place_at_goal.place_speed":0.02508,"transport_to_goal.transport_speed":0.07542},"optimized_scores":{"best_composite_score":0.26184,"best_fitness_score":0.98184,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":143.0,"contact_point_centroid":[0.49599,0.03626,-0.00196],"force_p95":0.58274,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.65498,"mean_force":0.17225,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48828,0.03799,0.02717]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50153,0.04386,-0.00261],"force_p95":0.29683,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.3798,"mean_force":0.16978,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49108,0.03823,0.02622]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16734.0,"contact_point_centroid":[0.48612,0.05698,0.10475],"force_p95":0.08087,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30416,"mean_force":0.05186,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48597,0.03781,0.10285]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16403.0,"contact_point_centroid":[0.48608,0.01863,0.10388],"force_p95":0.08085,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2494,"mean_force":0.05086,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48596,0.03781,0.10188]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3984.0,"contact_point_centroid":[0.4904,0.01871,0.02846],"force_p95":0.09983,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14332,"mean_force":0.05375,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.48989,0.03814,0.02498]},{"body_a":"world","body_b":"grasp_target","contact_count":3432.0,"contact_point_centroid":[0.50118,0.04505,-0.00196],"force_p95":0.12647,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12277,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.49739,0.02151,0.22301]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5267.0,"contact_point_centroid":[0.55599,0.25345,0.19614],"force_p95":0.06914,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13793,"mean_force":0.04814,"phase_index":5.0,"phase_name":"place_at_goal","phase_type":"descend","tcp_position_centroid":[0.55574,0.23422,0.19549]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.50118,0.04505,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.4962,0.04017,0.0784]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5340.0,"contact_point_centroid":[0.55601,0.21506,0.19707],"force_p95":0.07016,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12028,"mean_force":0.04652,"phase_index":5.0,"phase_name":"place_at_goal","phase_type":"descend","tcp_position_centroid":[0.55575,0.23419,0.19591]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5619.0,"contact_point_centroid":[0.48963,0.05839,0.02603],"force_p95":0.08955,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10698,"mean_force":0.04599,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.48993,0.03814,0.02502]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13742.0,"contact_point_centroid":[0.52066,0.11629,0.20869],"force_p95":0.07006,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08754,"mean_force":0.0465,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52066,0.13545,0.2066]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":13278.0,"contact_point_centroid":[0.5203,0.15355,0.20807],"force_p95":0.07122,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08029,"mean_force":0.04856,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52026,0.13437,0.20629]}],"total_contact_groups":12},"final_pose_error":0.0099,"key_states":{"actual_goal_position":[0.56442,0.24486,0.14677],"final_object_position":[0.5652,0.23867,0.14185],"final_tcp_position":[0.55651,0.23879,0.1548],"realised_goal_position":[0.56442,0.24486,0.14677],"realised_object_initial_position":[0.50118,0.04505,0.03]},"peak_contact_force":0.65498,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":859.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.03],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.23992,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3432.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_above_object","tcp_end":[0.49723,0.04257,0.15175],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12582,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_point","tcp_end":[0.49777,0.03877,0.0333],"tcp_start":[0.49723,0.04257,0.15175],"tcp_to_object_dist_end":0.0102,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50112,0.03876,0.02395],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24814,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.26466,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11403.0,"raw_peak_contact_force":0.3798,"subtask_id":"grasp_point","tcp_end":[0.48987,0.03813,0.02496],"tcp_start":[0.49777,0.03877,0.0333],"tcp_to_object_dist_end":0.01131,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":832.0,"n_steps_budget":1000.0,"object_pos_end":[0.49556,0.03782,0.1749],"object_pos_start":[0.50112,0.03876,0.02395],"object_to_goal_dist_end":0.21999,"object_to_goal_dist_start":0.24814,"object_z_max":0.17473,"peak_contact_force":0.08073,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":33280.0,"raw_peak_contact_force":0.65498,"subtask_id":"object_lifted","tcp_end":[0.4863,0.03784,0.1814],"tcp_start":[0.48987,0.03813,0.02496],"tcp_to_object_dist_end":0.01131,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":647.0,"n_steps_budget":1000.0,"object_pos_end":[0.56475,0.23077,0.22403],"object_pos_start":[0.49556,0.03782,0.1749],"object_to_goal_dist_end":0.07853,"object_to_goal_dist_start":0.21999,"object_z_max":0.22396,"peak_contact_force":0.0717,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":27020.0,"raw_peak_contact_force":0.08754,"subtask_id":"near_goal","tcp_end":[0.55684,0.23076,0.23504],"tcp_start":[0.4863,0.03784,0.1814],"tcp_to_object_dist_end":0.01356,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":251.0,"n_steps_budget":1000.0,"object_pos_end":[0.5652,0.23867,0.14185],"object_pos_start":[0.56475,0.23077,0.22403],"object_to_goal_dist_end":0.00795,"object_to_goal_dist_start":0.07853,"object_z_max":0.22403,"peak_contact_force":0.06985,"phase_name":"place_at_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":10607.0,"raw_peak_contact_force":0.13793,"subtask_id":"placed_at_goal","tcp_end":[0.55651,0.23879,0.1548],"tcp_start":[0.55684,0.23076,0.23504],"tcp_to_object_dist_end":0.0156,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.8325,"average_solve_count":400.0,"average_success_count":400.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.04798,"descend_to_grasp.descend_speed":0.03497,"descend_to_grasp.grasp_offset_x":0.0076,"descend_to_grasp.grasp_offset_y":-0.00376,"grasp.grasp_retry_offset_x":-0.0005,"grasp.grasp_retry_offset_y":0.00092,"lift_object.lift_distance":0.149,"lift_object.lift_speed":0.02755,"place_at_goal.place_offset_x":0.00636,"place_at_goal.place_offset_y":-0.00625,"place_at_goal.place_speed":0.03623,"transport_to_goal.transport_speed":0.05342},"optimized_scores":{"best_composite_score":0.27022,"best_fitness_score":0.99022,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":135.0,"contact_point_centroid":[0.47154,-0.0239,-0.00169],"force_p95":0.50316,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.58406,"mean_force":0.17126,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46899,-0.02297,0.02851]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.4762,-0.02059,-0.0023],"force_p95":0.20171,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.2811,"mean_force":0.14498,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.47157,-0.02304,0.02811]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":14280.0,"contact_point_centroid":[0.46677,-0.00374,0.09548],"force_p95":0.07539,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25534,"mean_force":0.05029,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46657,-0.02288,0.09354]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14280.0,"contact_point_centroid":[0.4668,-0.04204,0.09537],"force_p95":0.07519,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23344,"mean_force":0.04951,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46657,-0.02288,0.09354]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4706.0,"contact_point_centroid":[0.47063,-0.0422,0.02885],"force_p95":0.07896,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15982,"mean_force":0.04519,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.47043,-0.023,0.02697]},{"body_a":"world","body_b":"grasp_target","contact_count":2868.0,"contact_point_centroid":[0.47616,-0.02015,-0.00195],"force_p95":0.12883,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.1228,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.48598,-0.00927,0.22621]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4650.0,"contact_point_centroid":[0.62542,0.16975,0.23852],"force_p95":0.07137,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13061,"mean_force":0.04916,"phase_index":5.0,"phase_name":"place_at_goal","phase_type":"descend","tcp_position_centroid":[0.62528,0.15059,0.23661]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4589.0,"contact_point_centroid":[0.6254,0.13147,0.23909],"force_p95":0.07119,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12594,"mean_force":0.04914,"phase_index":5.0,"phase_name":"place_at_goal","phase_type":"descend","tcp_position_centroid":[0.62522,0.15058,0.23704]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.47483,-0.02131,0.08392]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18180.0,"contact_point_centroid":[0.54517,0.04713,0.22022],"force_p95":0.07076,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09674,"mean_force":0.0484,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.54492,0.06628,0.21835]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18180.0,"contact_point_centroid":[0.54515,0.08541,0.22024],"force_p95":0.07055,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08855,"mean_force":0.04849,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.54492,0.06628,0.21835]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5160.0,"contact_point_centroid":[0.47062,-0.00358,0.02894],"force_p95":0.07954,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08493,"mean_force":0.04463,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.47044,-0.023,0.02698]}],"total_contact_groups":12},"final_pose_error":0.01,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.63789,0.15137,0.18723],"final_tcp_position":[0.63126,0.15143,0.19744],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":0.58406,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":718.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2868.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_above_object","tcp_end":[0.4739,-0.01881,0.15423],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12824,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_point","tcp_end":[0.47805,-0.02323,0.03465],"tcp_start":[0.4739,-0.01881,0.15423],"tcp_to_object_dist_end":0.00936,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47603,-0.02276,0.02493],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.2907,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.18891,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11666.0,"raw_peak_contact_force":0.2811,"subtask_id":"grasp_point","tcp_end":[0.4704,-0.02301,0.02694],"tcp_start":[0.47805,-0.02323,0.03465],"tcp_to_object_dist_end":0.00598,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":714.0,"n_steps_budget":1000.0,"object_pos_end":[0.47137,-0.02278,0.15681],"object_pos_start":[0.47603,-0.02276,0.02493],"object_to_goal_dist_end":0.24461,"object_to_goal_dist_start":0.2907,"object_z_max":0.15664,"peak_contact_force":0.0731,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":28695.0,"raw_peak_contact_force":0.58406,"subtask_id":"object_lifted","tcp_end":[0.46674,-0.02287,0.16143],"tcp_start":[0.4704,-0.02301,0.02694],"tcp_to_object_dist_end":0.00654,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":909.0,"n_steps_budget":1000.0,"object_pos_end":[0.62657,0.15004,0.26656],"object_pos_start":[0.47137,-0.02278,0.15681],"object_to_goal_dist_end":0.07725,"object_to_goal_dist_start":0.24461,"object_z_max":0.26647,"peak_contact_force":0.07037,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":36360.0,"raw_peak_contact_force":0.09674,"subtask_id":"near_goal","tcp_end":[0.62145,0.15003,0.27541],"tcp_start":[0.46674,-0.02287,0.16143],"tcp_to_object_dist_end":0.01022,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":230.0,"n_steps_budget":1000.0,"object_pos_end":[0.63789,0.15137,0.18723],"object_pos_start":[0.62657,0.15004,0.26656],"object_to_goal_dist_end":0.01052,"object_to_goal_dist_start":0.07725,"object_z_max":0.26656,"peak_contact_force":0.06827,"phase_name":"place_at_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":9239.0,"raw_peak_contact_force":0.13061,"subtask_id":"placed_at_goal","tcp_end":[0.63126,0.15143,0.19744],"tcp_start":[0.62145,0.15003,0.27541],"tcp_to_object_dist_end":0.01217,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.84352,"average_solve_count":409.0,"average_success_count":409.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.05604,"descend_to_grasp.descend_speed":0.02413,"descend_to_grasp.grasp_offset_x":0.00989,"descend_to_grasp.grasp_offset_y":0.00662,"grasp.grasp_retry_offset_x":0.00153,"grasp.grasp_retry_offset_y":-0.00051,"lift_object.lift_distance":0.12797,"lift_object.lift_speed":0.03467,"place_at_goal.place_offset_x":0.01408,"place_at_goal.place_offset_y":0.01193,"place_at_goal.place_speed":0.03194,"transport_to_goal.transport_speed":0.0543},"optimized_scores":{"best_composite_score":0.27525,"best_fitness_score":0.99525,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":144.0,"contact_point_centroid":[0.45403,-0.01806,-0.00204],"force_p95":0.59345,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.69604,"mean_force":0.17562,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.45403,-0.01976,0.02647]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45861,-0.02516,-0.00265],"force_p95":0.29136,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.36135,"mean_force":0.17183,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.45666,-0.01981,0.02517]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11220.0,"contact_point_centroid":[0.45202,-0.03887,0.08214],"force_p95":0.08399,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30835,"mean_force":0.05164,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.4518,-0.01968,0.08023]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11220.0,"contact_point_centroid":[0.45201,-0.00049,0.08209],"force_p95":0.08369,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2532,"mean_force":0.04913,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.4518,-0.01968,0.08023]},{"body_a":"world","body_b":"grasp_target","contact_count":2860.0,"contact_point_centroid":[0.45856,-0.02632,-0.00195],"force_p95":0.12892,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.1228,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.47789,-0.01207,0.22649]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4378.0,"contact_point_centroid":[0.45567,-0.00051,0.02633],"force_p95":0.09537,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13428,"mean_force":0.04862,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.45554,-0.01979,0.0241]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.45875,-0.02209,0.08787]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5900.0,"contact_point_centroid":[0.62645,0.22466,0.1601],"force_p95":0.07159,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11714,"mean_force":0.04877,"phase_index":5.0,"phase_name":"place_at_goal","phase_type":"descend","tcp_position_centroid":[0.62621,0.20549,0.15836]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5900.0,"contact_point_centroid":[0.62651,0.18639,0.16037],"force_p95":0.06958,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1126,"mean_force":0.04853,"phase_index":5.0,"phase_name":"place_at_goal","phase_type":"descend","tcp_position_centroid":[0.62621,0.20549,0.15836]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5379.0,"contact_point_centroid":[0.45579,-0.03993,0.0258],"force_p95":0.09667,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10702,"mean_force":0.0471,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.45558,-0.0198,0.02413]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18900.0,"contact_point_centroid":[0.53688,0.07314,0.1711],"force_p95":0.07216,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.093,"mean_force":0.04849,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.53663,0.09228,0.16918]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18900.0,"contact_point_centroid":[0.53686,0.11142,0.17104],"force_p95":0.07257,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08257,"mean_force":0.04771,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.53663,0.09228,0.16918]}],"total_contact_groups":12},"final_pose_error":0.00994,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.64064,0.21515,0.11034],"final_tcp_position":[0.63621,0.21521,0.11734],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":0.69604,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":716.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2860.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_above_object","tcp_end":[0.45738,-0.02457,0.15441],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.1284,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_point","tcp_end":[0.46306,-0.01996,0.03135],"tcp_start":[0.45738,-0.02457,0.15441],"tcp_to_object_dist_end":0.00944,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45835,-0.02015,0.02368],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.29973,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.25923,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11557.0,"raw_peak_contact_force":0.36135,"subtask_id":"grasp_point","tcp_end":[0.45552,-0.01979,0.02408],"tcp_start":[0.46306,-0.01996,0.03135],"tcp_to_object_dist_end":0.00288,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":561.0,"n_steps_budget":1000.0,"object_pos_end":[0.45394,-0.01981,0.13555],"object_pos_start":[0.45835,-0.02015,0.02368],"object_to_goal_dist_end":0.28896,"object_to_goal_dist_start":0.29973,"object_z_max":0.13536,"peak_contact_force":0.07934,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":22584.0,"raw_peak_contact_force":0.69604,"subtask_id":"object_lifted","tcp_end":[0.45179,-0.01967,0.13757],"tcp_start":[0.45552,-0.01979,0.02408],"tcp_to_object_dist_end":0.00295,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":945.0,"n_steps_budget":1000.0,"object_pos_end":[0.62212,0.19701,0.1961],"object_pos_start":[0.45394,-0.01981,0.13555],"object_to_goal_dist_end":0.08313,"object_to_goal_dist_start":0.28896,"object_z_max":0.19605,"peak_contact_force":0.07184,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":37800.0,"raw_peak_contact_force":0.093,"subtask_id":"near_goal","tcp_end":[0.61912,0.19707,0.20192],"tcp_start":[0.45179,-0.01967,0.13757],"tcp_to_object_dist_end":0.00655,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":295.0,"n_steps_budget":1000.0,"object_pos_end":[0.64064,0.21515,0.11034],"object_pos_start":[0.62212,0.19701,0.1961],"object_to_goal_dist_end":0.01315,"object_to_goal_dist_start":0.08313,"object_z_max":0.1961,"peak_contact_force":0.07175,"phase_name":"place_at_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":11800.0,"raw_peak_contact_force":0.11714,"subtask_id":"placed_at_goal","tcp_end":[0.63621,0.21521,0.11734],"tcp_start":[0.61912,0.19707,0.20192],"tcp_to_object_dist_end":0.00829,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```