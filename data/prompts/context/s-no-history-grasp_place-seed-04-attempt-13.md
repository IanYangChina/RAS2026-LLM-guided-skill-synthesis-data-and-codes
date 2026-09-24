## Search State

- **Seed**: 4
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
- Frozen realised-scene SHA-256: `1959b3932a54fd3d3850620783d44a63a35b8fa059f78d939fdbdef5fbfc64e8`
- Frozen object start: [0.5443056105572368, 0.0011327552814361583, 0.03]
- Frozen task target: [0.6476243705707704, 0.15808360238956023, 0.19110337479925443]
- Goal object position: (0.6476243705707704, 0.15808360238956023, 0.19110337479925443)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.6476243705707704, 0.15808360238956023, 0.19110337479925443)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.5443056105572368, 0.0011327552814361583, 0.03)
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
  frozen_object_start: [0.5443, 0.0011, 0.03]
  frozen_task_target: [0.6476, 0.1581, 0.1911]
  frozen_object_starts: {'grasp_target': [0.5443056105572368, 0.0011327552814361583, 0.03]}
  frozen_targets: {'place_target': [0.6476243705707704, 0.15808360238956023, 0.19110337479925443]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: 1959b3932a54fd3d3850620783d44a63a35b8fa059f78d939fdbdef5fbfc64e8

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
| `object` | offset from object initial position (0.5443056105572368, 0.0011327552814361583, 0.03) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.6476243705707704, 0.15808360238956023, 0.19110337479925443) | final destination targets |
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

## Current Skill (Q=-0.244) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: pre_grasp
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.15
  weight: 0.3
- id: descend_grasp
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.03
  weight: 0.3
- id: lift
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.2
  weight: 0.2
- id: place_goal
  metric: goal_progress
  weight: 0.2
phases:
- id: approach_high
  type: approach
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.2
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.1
      - 1.0
      default: 0.5
      binds_to:
      - path: generator.speed
        mode: replace
    arc_height:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.arc_height
        mode: replace
  subtask_id: pre_grasp
- id: align_over_object
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
    - 0.2
    tolerance: 0.005
    orientation:
      mode: keep_current
  parameters:
    align_speed:
      type: scalar
      range:
      - 0.1
      - 0.5
      default: 0.3
      binds_to:
      - path: generator.speed
        mode: replace
- id: descend_to_grasp
  type: descend
  generator: linear_cartesian
  control: impedance_control
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
    descend_speed:
      type: scalar
      range:
      - 0.1
      - 0.5
      default: 0.2
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: force_guard
    when: during_phase
    predicate: force_below
    threshold: 15.0
    on_failure: retry
  retries:
    max_attempts: 1
    strategy: reduce_speed
  subtask_id: descend_grasp
- id: grasp_1
  type: grasp
  control: position_control
  termination: time_limit
  end_effector_action: force_grasp
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
  parameters:
    grasp_retry_offset_z:
      type: scalar
      range:
      - -0.02
      - 0.0
      default: -0.005
      binds_to:
      - path: retry.offset.z
        mode: replace
    grasp_timeout:
      type: scalar
      range:
      - 0.5
      - 2.0
      default: 1.0
      binds_to:
      - path: duration.max_time
        mode: replace
  guards:
  - id: bilateral_grasp_check
    when: after_phase
    predicate: bilateral_grasp
    threshold: 1.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - -0.005
- id: lift_1
  type: lift
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
    - 0.2
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    lift_height_offset:
      type: scalar
      range:
      - 0.15
      - 0.25
      default: 0.2
      binds_to:
      - path: target.offset.z
        mode: replace
    lift_speed:
      type: scalar
      range:
      - 0.2
      - 1.0
      default: 0.5
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: lift
- id: transport_1
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    entity: placement_surface
    offset:
    - 0.0
    - 0.0
    - 0.1
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    transport_speed:
      type: scalar
      range:
      - 0.2
      - 1.0
      default: 0.5
      binds_to:
      - path: generator.speed
        mode: replace
    transport_z_offset:
      type: scalar
      range:
      - 0.05
      - 0.15
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: place_goal
- id: release_1
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
  parameters:
    release_timeout:
      type: scalar
      range:
      - 0.5
      - 2.0
      default: 1.0
      binds_to:
      - path: duration.max_time
        mode: replace
- id: retract_1
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
    - 0.15
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    retract_speed:
      type: scalar
      range:
      - 0.2
      - 1.0
      default: 0.5
      binds_to:
      - path: generator.speed
        mode: replace
    retract_z_offset:
      type: scalar
      range:
      - 0.1
      - 0.2
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_high** (`approach`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.2], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
    - arc_height: status=consumed; consumers=generator.arc_height (replace)
- **align_over_object** (`approach`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.2], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings:
    - align_speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_grasp** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.03], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=force_guard, when=during_phase, predicate=force_below, on_failure=retry, threshold=15.0
  - retries: max_attempts=1, strategy=reduce_speed
- **grasp_1** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings:
    - grasp_retry_offset_z: status=consumed; consumers=retry.offset.z (replace)
    - grasp_timeout: status=consumed; consumers=duration.max_time (replace)
  - guards:
    - id=bilateral_grasp_check, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=1.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, -0.005]
- **lift_1** (`lift`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.2], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height_offset: status=consumed; consumers=target.offset.z (replace)
    - lift_speed: status=consumed; consumers=generator.speed (replace)
- **transport_1** (`approach`)
  - target: source=yaml, anchor=task_goal, entity=placement_surface, offset=[0.0, 0.0, 0.1], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - transport_speed: status=consumed; consumers=generator.speed (replace)
    - transport_z_offset: status=consumed; consumers=target.offset.z (replace)
- **release_1** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings:
    - release_timeout: status=consumed; consumers=duration.max_time (replace)
- **retract_1** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.15], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - retract_speed: status=consumed; consumers=generator.speed (replace)
    - retract_z_offset: status=consumed; consumers=target.offset.z (replace)

## Design Metrics

- **Composite score**: -0.244
- **task_score** (E): 0.247
- **fitness_score**: 0.586  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.830

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_high | 1.00 | 1.00 | 0.0709 |
| descend_to_grasp | 1.00 | 1.00 | 0.1817 |
| grasp_1 | 1.00 | 1.00 | 0.0123 |
| lift_1 | 1.00 | 1.00 | 0.1238 |
| transport_1 | 1.00 | 1.00 | 0.2123 |
| descend_to_place | 1.00 | 1.00 | 0.1145 |
| release_1 | 1.00 | 1.00 | 0.0209 |
| retract_1 | 1.00 | 1.00 | 0.1343 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_high | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.521, 0.007, 0.237) | (0.526, 0.005, 0.030)→(0.526, 0.005, 0.026) | 0.246→0.249 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.521, 0.007, 0.237)→(0.521, 0.005, 0.055) | (0.526, 0.005, 0.026)→(0.526, 0.005, 0.026) | 0.249→0.249 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.521, 0.005, 0.055)→(0.513, 0.005, 0.046) | (0.526, 0.005, 0.026)→(0.526, 0.005, 0.026) | 0.249→0.249 | 1.00 / 44.333 | 0.136 | 0.173 |
| lift_1 | lift | 1.00 / step_budget | (0.513, 0.005, 0.046)→(0.522, 0.005, 0.170) | (0.526, 0.005, 0.026)→(0.534, 0.005, 0.141) | 0.249→0.203 | 1.00 / 24.333 | 55983.974 | 0.423 |
| transport_1 | approach | 1.00 / step_budget | (0.522, 0.005, 0.170)→(0.599, 0.154, 0.291) | (0.534, 0.005, 0.141)→(0.554, 0.049, 0.016) | 0.203→0.219 | 1.00 / 8.667 | 91002.789 | 1.604 |
| descend_to_place | descend | 1.00 / step_budget | (0.599, 0.154, 0.291)→(0.608, 0.172, 0.179) | (0.554, 0.049, 0.016)→(0.554, 0.049, 0.016) | 0.219→0.219 | 1.00 / 8.000 | 0.123 | 0.123 |
| release_1 | release | 1.00 / step_budget | (0.608, 0.172, 0.179)→(0.602, 0.171, 0.199) | (0.554, 0.049, 0.016)→(0.554, 0.049, 0.016) | 0.219→0.219 | 1.00 / 4.000 | 0.123 | 0.123 |
| retract_1 | retract | 1.00 / step_budget | (0.602, 0.171, 0.199)→(0.601, 0.170, 0.333) | (0.554, 0.049, 0.016)→(0.554, 0.049, 0.016) | 0.219→0.219 | 1.00 / 4.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.351
- phase_score: 0.436
- phase_breakdown.pre_grasp_score: 0.313
- phase_breakdown.place_goal_score: 0.000
- phase_breakdown.descend_grasp_score: 0.865
- phase_breakdown.lift_score: 0.414
- grasp_place_fitness: 0.639

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.639
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.351
- **Median Q (composite search score)**: -0.245
- **K-run variance**: 0.0018
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.333


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `104d9d5641b6f93313b49acc931f841aa27a6ce63eca9eff4a16c33838e2c9c3`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `9de75aa839370ff688dada9a37e29517e2f368ed4f09f6a013379103594581cf`; realized-scene SHA-256: `1959b3932a54fd3d3850620783d44a63a35b8fa059f78d939fdbdef5fbfc64e8`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.54431,0.00113,0.03]},{"name":"goal","value":[0.64762,0.15808,0.1911]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.54431,0.00113,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.64762,0.15808,0.1911]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.31933,"average_solve_count":119.0,"average_success_count":119.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_high.approach_speed":0.50456,"approach_high.arc_height":0.1726,"descend_to_grasp.descend_speed":0.39233,"descend_to_place.descend_speed":0.35952,"grasp_1.grasp_retry_offset_z":-0.0158,"grasp_1.grasp_timeout":0.99885,"lift_1.lift_height_offset":0.15001,"lift_1.lift_speed":0.3754,"release_1.release_timeout":1.28832,"retract_1.retract_speed":0.74228,"retract_1.retract_z_offset":0.17108,"transport_1.transport_speed":0.464,"transport_1.transport_z_offset":0.12897},"optimized_scores":{"best_composite_score":-0.24516,"best_fitness_score":0.58484,"best_task_score":0.24068},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2672.0,"contact_point_centroid":[0.58261,0.05431,-0.00235],"force_p95":0.12927,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.60474,"mean_force":0.13962,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.59974,0.09213,0.2457]},{"body_a":"world","body_b":"grasp_target","contact_count":153.0,"contact_point_centroid":[0.54268,0.00085,-0.00116],"force_p95":0.24348,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.45428,"mean_force":0.06092,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52951,0.00086,0.04614]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8480.0,"contact_point_centroid":[0.53482,-0.01813,0.09252],"force_p95":0.10596,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29952,"mean_force":0.06559,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53207,0.00084,0.09048]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8905.0,"contact_point_centroid":[0.53483,0.01977,0.09243],"force_p95":0.10017,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29928,"mean_force":0.06304,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53206,0.00084,0.09041]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2954.0,"contact_point_centroid":[0.55369,0.03498,0.17079],"force_p95":0.12756,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27275,"mean_force":0.07903,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.5475,0.01654,0.17139]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2622.0,"contact_point_centroid":[0.55287,-0.00339,0.17006],"force_p95":0.1561,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23857,"mean_force":0.08736,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.54668,0.01524,0.17023]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.5443,0.00109,-0.00203],"force_p95":0.13141,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15306,"mean_force":0.12537,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53209,0.00091,0.04603]},{"body_a":"world","body_b":"grasp_target","contact_count":1116.0,"contact_point_centroid":[0.54431,0.00113,-0.00188],"force_p95":0.13645,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12306,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.52056,0.00055,0.27196]},{"body_a":"world","body_b":"grasp_target","contact_count":3228.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.53739,0.00101,0.13603]},{"body_a":"world","body_b":"grasp_target","contact_count":3148.0,"contact_point_centroid":[0.58263,0.05433,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.63801,0.1487,0.22442]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.58263,0.05433,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.63933,0.1553,0.18427]},{"body_a":"world","body_b":"grasp_target","contact_count":2168.0,"contact_point_centroid":[0.58263,0.05433,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.63584,0.15417,0.27393]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5056.0,"contact_point_centroid":[0.53119,-0.01835,0.04771],"force_p95":0.06541,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10469,"mean_force":0.04322,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53086,0.00089,0.04457]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5362.0,"contact_point_centroid":[0.5309,0.02013,0.04728],"force_p95":0.06383,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08553,"mean_force":0.04113,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53087,0.00089,0.04458]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2619.0,"contact_point_centroid":[0.60293,0.09603,0.2519],"force_p95":0.01119,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0155,"mean_force":0.0105,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.60247,0.09603,0.2496]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3392.0,"contact_point_centroid":[0.63849,0.14868,0.22679],"force_p95":0.01096,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01268,"mean_force":0.01035,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.63798,0.14867,0.22457]}],"total_contact_groups":17},"final_pose_error":0.02017,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.58263,0.05433,0.01602],"final_tcp_position":[0.63686,0.15436,0.35431],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":1.60474,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":280.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_high","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1116.0,"raw_peak_contact_force":0.13845,"subtask_id":"pre_grasp","tcp_end":[0.53798,0.001,0.23751],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.21158,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":807.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3228.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_grasp","tcp_end":[0.53909,0.00104,0.05444],"tcp_start":[0.53798,0.001,0.23751],"tcp_to_object_dist_end":0.02889,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":47.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54421,0.00094,0.02586],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25039,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.13082,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12218.0,"raw_peak_contact_force":0.15306,"tcp_end":[0.53084,0.00089,0.04454],"tcp_start":[0.53909,0.00104,0.05444],"tcp_to_object_dist_end":0.02298,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":24.0,"n_steps":542.0,"n_steps_budget":600.0,"object_pos_end":[0.55305,0.00102,0.13441],"object_pos_start":[0.54421,0.00094,0.02586],"object_to_goal_dist_end":0.19191,"object_to_goal_dist_start":0.25039,"object_z_max":0.13424,"peak_contact_force":0.09781,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":17538.0,"raw_peak_contact_force":0.45428,"subtask_id":"lift","tcp_end":[0.53944,0.00087,0.16029],"tcp_start":[0.53084,0.00089,0.04454],"tcp_to_object_dist_end":0.02924,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.58263,0.05433,0.01602],"object_pos_start":[0.55305,0.00102,0.13441],"object_to_goal_dist_end":0.21364,"object_to_goal_dist_start":0.19191,"object_z_max":0.15632,"peak_contact_force":0.12263,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":10867.0,"raw_peak_contact_force":1.60474,"subtask_id":"place_goal","tcp_end":[0.6318,0.13758,0.29109],"tcp_start":[0.53944,0.00087,0.16029],"tcp_to_object_dist_end":0.29157,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":787.0,"n_steps_budget":1000.0,"object_pos_end":[0.58263,0.05433,0.01602],"object_pos_start":[0.58263,0.05433,0.01602],"object_to_goal_dist_end":0.21364,"object_to_goal_dist_start":0.21364,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":6540.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_goal","tcp_end":[0.64336,0.15643,0.18461],"tcp_start":[0.6318,0.13758,0.29109],"tcp_to_object_dist_end":0.20624,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.58263,0.05433,0.01602],"object_pos_start":[0.58263,0.05433,0.01602],"object_to_goal_dist_end":0.21364,"object_to_goal_dist_start":0.21364,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1021.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.6378,0.15482,0.20337],"tcp_start":[0.64336,0.15643,0.18461],"tcp_to_object_dist_end":0.21965,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":542.0,"n_steps_budget":600.0,"object_pos_end":[0.58263,0.05433,0.01602],"object_pos_start":[0.58263,0.05433,0.01602],"object_to_goal_dist_end":0.21364,"object_to_goal_dist_start":0.21364,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2168.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.63686,0.15436,0.35431],"tcp_start":[0.6378,0.15482,0.20337],"tcp_to_object_dist_end":0.35691,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `349f925163f8e9284ad51ad55d38356f2e3c8deb4dc54e8ff12260e5f6d4b0f8`; realized-scene SHA-256: `e32d7866764afb23ec7c7faebb4bcca0aa39fbf2f1ab61f3c9c527b297153af9`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5305,0.03079,0.03]},{"name":"goal","value":[0.60153,0.17858,0.10809]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.5305,0.03079,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.60153,0.17858,0.10809]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.42017,"average_solve_count":119.0,"average_success_count":119.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_high.approach_speed":0.28852,"approach_high.arc_height":0.19698,"descend_to_grasp.descend_speed":0.28407,"descend_to_place.descend_speed":0.31552,"grasp_1.grasp_retry_offset_z":-0.0041,"grasp_1.grasp_timeout":1.83361,"lift_1.lift_height_offset":0.17695,"lift_1.lift_speed":0.38798,"release_1.release_timeout":1.50911,"retract_1.retract_speed":0.74585,"retract_1.retract_z_offset":0.14203,"transport_1.transport_speed":0.23866,"transport_1.transport_z_offset":0.13209},"optimized_scores":{"best_composite_score":-0.19121,"best_fitness_score":0.63879,"best_task_score":0.35064},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":3243.0,"contact_point_centroid":[0.55059,0.06182,-0.00232],"force_p95":0.12836,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.61886,"mean_force":0.13782,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.56489,0.11215,0.20924]},{"body_a":"world","body_b":"grasp_target","contact_count":124.0,"contact_point_centroid":[0.52882,0.02913,-0.00116],"force_p95":0.23435,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.42476,"mean_force":0.04668,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51617,0.02975,0.04737]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1117.0,"contact_point_centroid":[0.5358,0.05711,0.18525],"force_p95":0.14534,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30714,"mean_force":0.0859,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.52905,0.03895,0.18637]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7981.0,"contact_point_centroid":[0.52191,0.01079,0.10613],"force_p95":0.10818,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29791,"mean_force":0.06982,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51898,0.0297,0.10496]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8643.0,"contact_point_centroid":[0.52194,0.04858,0.10443],"force_p95":0.10341,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29596,"mean_force":0.06577,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51882,0.0297,0.10307]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":925.0,"contact_point_centroid":[0.53542,0.01913,0.18555],"force_p95":0.20239,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26396,"mean_force":0.10207,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.5286,0.03758,0.18628]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53052,0.0307,-0.00208],"force_p95":0.14532,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.20016,"mean_force":0.12887,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51854,0.02993,0.04684]},{"body_a":"world","body_b":"grasp_target","contact_count":1060.0,"contact_point_centroid":[0.5305,0.03079,-0.00188],"force_p95":0.1365,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12309,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.51304,0.01522,0.27155]},{"body_a":"world","body_b":"grasp_target","contact_count":3160.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.52394,0.02915,0.13857]},{"body_a":"world","body_b":"grasp_target","contact_count":3304.0,"contact_point_centroid":[0.55063,0.06178,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.59358,0.17153,0.1522]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.55063,0.06178,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.59154,0.17516,0.10423]},{"body_a":"world","body_b":"grasp_target","contact_count":2168.0,"contact_point_centroid":[0.55063,0.06178,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.58638,0.17346,0.18197]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4584.0,"contact_point_centroid":[0.51798,0.01064,0.04793],"force_p95":0.07146,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10548,"mean_force":0.0472,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51734,0.02985,0.04546]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5181.0,"contact_point_centroid":[0.51794,0.04905,0.04758],"force_p95":0.06829,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.06973,"mean_force":0.04273,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51735,0.02985,0.04546]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3236.0,"contact_point_centroid":[0.56717,0.11587,0.21286],"force_p95":0.01102,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01559,"mean_force":0.01047,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.56679,0.11585,0.21054]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3532.0,"contact_point_centroid":[0.59407,0.17157,0.15433],"force_p95":0.01097,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01279,"mean_force":0.01043,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.59358,0.17154,0.15206]}],"total_contact_groups":17},"final_pose_error":0.01795,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.55063,0.06178,0.01602],"final_tcp_position":[0.58686,0.17356,0.24826],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":273008.12311,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":266.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_high","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1060.0,"raw_peak_contact_force":0.13845,"subtask_id":"pre_grasp","tcp_end":[0.52487,0.02788,0.23771],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.21178,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":790.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3160.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_grasp","tcp_end":[0.52539,0.03039,0.05485],"tcp_start":[0.52487,0.02788,0.23771],"tcp_to_object_dist_end":0.02928,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53044,0.03011,0.02569],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18409,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.14315,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11565.0,"raw_peak_contact_force":0.20016,"tcp_end":[0.51731,0.02985,0.04542],"tcp_start":[0.52539,0.03039,0.05485],"tcp_to_object_dist_end":0.02369,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":26.0,"n_steps":542.0,"n_steps_budget":600.0,"object_pos_end":[0.53936,0.03022,0.15816],"object_pos_start":[0.53044,0.03011,0.02569],"object_to_goal_dist_end":0.16847,"object_to_goal_dist_start":0.18409,"object_z_max":0.15796,"peak_contact_force":0.09452,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":16748.0,"raw_peak_contact_force":0.42476,"subtask_id":"lift","tcp_end":[0.52614,0.02985,0.18611],"tcp_start":[0.51731,0.02985,0.04542],"tcp_to_object_dist_end":0.03092,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.55063,0.06178,0.01602],"object_pos_start":[0.53936,0.03022,0.15816],"object_to_goal_dist_end":0.1572,"object_to_goal_dist_start":0.16847,"object_z_max":0.15833,"peak_contact_force":273008.12311,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8521.0,"raw_peak_contact_force":1.61886,"subtask_id":"place_goal","tcp_end":[0.59195,0.16496,0.2276],"tcp_start":[0.52614,0.02985,0.18611],"tcp_to_object_dist_end":0.239,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":826.0,"n_steps_budget":1000.0,"object_pos_end":[0.55063,0.06178,0.01602],"object_pos_start":[0.55063,0.06178,0.01602],"object_to_goal_dist_end":0.1572,"object_to_goal_dist_start":0.1572,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":6836.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_goal","tcp_end":[0.59652,0.17672,0.10329],"tcp_start":[0.59195,0.16496,0.2276],"tcp_to_object_dist_end":0.15145,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.55063,0.06178,0.01602],"object_pos_start":[0.55063,0.06178,0.01602],"object_to_goal_dist_end":0.1572,"object_to_goal_dist_start":0.1572,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1015.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.58957,0.17451,0.12395],"tcp_start":[0.59652,0.17672,0.10329],"tcp_to_object_dist_end":0.16086,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":542.0,"n_steps_budget":600.0,"object_pos_end":[0.55063,0.06178,0.01602],"object_pos_start":[0.55063,0.06178,0.01602],"object_to_goal_dist_end":0.1572,"object_to_goal_dist_start":0.1572,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2168.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.58686,0.17356,0.24826],"tcp_start":[0.58957,0.17451,0.12395],"tcp_to_object_dist_end":0.26028,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `a1798e4fdcacfe8740623adfe3f78d2bc74e0d14c8233e64f02c40cf2a534ecc`; realized-scene SHA-256: `584133b5261cffac0dd4282704ff39e97bf4d452e60b02507679bbdea5a4de22`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50382,-0.01567,0.03]},{"name":"goal","value":[0.58691,0.18745,0.24812]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.50382,-0.01567,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.58691,0.18745,0.24812]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.44915,"average_solve_count":118.0,"average_success_count":118.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_high.approach_speed":0.78854,"approach_high.arc_height":0.14125,"descend_to_grasp.descend_speed":0.28352,"descend_to_place.descend_speed":0.32133,"grasp_1.grasp_retry_offset_z":-0.01428,"grasp_1.grasp_timeout":1.86703,"lift_1.lift_height_offset":0.15142,"lift_1.lift_speed":0.22877,"release_1.release_timeout":1.01787,"retract_1.retract_speed":0.67189,"retract_1.retract_z_offset":0.14487,"transport_1.transport_speed":0.38453,"transport_1.transport_z_offset":0.14527},"optimized_scores":{"best_composite_score":-0.29544,"best_fitness_score":0.53456,"best_task_score":0.14844},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2917.0,"contact_point_centroid":[0.5302,0.02877,-0.00241],"force_p95":0.17912,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.58827,"mean_force":0.14529,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.54454,0.09458,0.28149]},{"body_a":"world","body_b":"grasp_target","contact_count":148.0,"contact_point_centroid":[0.50237,-0.01498,-0.00113],"force_p95":0.22114,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.38906,"mean_force":0.05061,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4899,-0.01525,0.05018]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1244.0,"contact_point_centroid":[0.50684,0.01217,0.16719],"force_p95":0.17267,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31153,"mean_force":0.10197,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.50093,-0.00638,0.16968]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7755.0,"contact_point_centroid":[0.49483,0.00369,0.09468],"force_p95":0.1334,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29829,"mean_force":0.07352,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49232,-0.01524,0.09465]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8603.0,"contact_point_centroid":[0.49505,-0.03395,0.09548],"force_p95":0.10307,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28164,"mean_force":0.06467,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49238,-0.01524,0.09517]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1599.0,"contact_point_centroid":[0.50777,-0.02291,0.16995],"force_p95":0.13883,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20048,"mean_force":0.08021,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.50139,-0.00499,0.17099]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50382,-0.01563,-0.00204],"force_p95":0.13482,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.16543,"mean_force":0.1259,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49231,-0.01528,0.04975]},{"body_a":"world","body_b":"grasp_target","contact_count":832.0,"contact_point_centroid":[0.50382,-0.01567,-0.00184],"force_p95":0.13728,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12321,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.49947,-0.00057,0.26808]},{"body_a":"world","body_b":"grasp_target","contact_count":3064.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.49826,-0.01216,0.14185]},{"body_a":"world","body_b":"grasp_target","contact_count":1836.0,"contact_point_centroid":[0.53011,0.03004,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.57778,0.17167,0.29932]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.53011,0.03004,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57987,0.18322,0.24899]},{"body_a":"world","body_b":"grasp_target","contact_count":2168.0,"contact_point_centroid":[0.53011,0.03004,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.5773,0.18212,0.32834]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4358.0,"contact_point_centroid":[0.49158,0.00392,0.04961],"force_p95":0.07266,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11018,"mean_force":0.04944,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49116,-0.01526,0.04851]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4888.0,"contact_point_centroid":[0.49154,-0.0344,0.04943],"force_p95":0.06866,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08745,"mean_force":0.04458,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49116,-0.01526,0.04851]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3082.0,"contact_point_centroid":[0.54539,0.09579,0.28504],"force_p95":0.01123,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01616,"mean_force":0.0105,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.54508,0.09579,0.28285]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1956.0,"contact_point_centroid":[0.57818,0.17166,0.30163],"force_p95":0.01097,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01268,"mean_force":0.01046,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.57777,0.17165,0.29942]}],"total_contact_groups":17},"final_pose_error":0.01728,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.53011,0.03004,0.01602],"final_tcp_position":[0.57809,0.18229,0.39637],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":167951.73011,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":209.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_high","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":832.0,"raw_peak_contact_force":0.13845,"subtask_id":"pre_grasp","tcp_end":[0.50013,-0.00876,0.23614],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.21027,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":766.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3064.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_grasp","tcp_end":[0.49894,-0.01537,0.05703],"tcp_start":[0.50013,-0.00876,0.23614],"tcp_to_object_dist_end":0.03139,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50374,-0.01534,0.02584],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31217,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.13401,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11046.0,"raw_peak_contact_force":0.16543,"tcp_end":[0.49113,-0.01526,0.04847],"tcp_start":[0.49894,-0.01537,0.05703],"tcp_to_object_dist_end":0.02591,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":542.0,"n_steps_budget":600.0,"object_pos_end":[0.50936,-0.01627,0.13169],"object_pos_start":[0.50374,-0.01534,0.02584],"object_to_goal_dist_end":0.24713,"object_to_goal_dist_start":0.31217,"object_z_max":0.13153,"peak_contact_force":167951.73011,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":16506.0,"raw_peak_contact_force":0.38906,"subtask_id":"lift","tcp_end":[0.49918,-0.01528,0.16267],"tcp_start":[0.49113,-0.01526,0.04847],"tcp_to_object_dist_end":0.03263,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53011,0.03004,0.01602],"object_pos_start":[0.50936,-0.01627,0.13169],"object_to_goal_dist_end":0.28613,"object_to_goal_dist_start":0.24713,"object_z_max":0.1485,"peak_contact_force":0.12263,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8842.0,"raw_peak_contact_force":1.58827,"subtask_id":"place_goal","tcp_end":[0.57373,0.15974,0.35484],"tcp_start":[0.49918,-0.01528,0.16267],"tcp_to_object_dist_end":0.36541,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":459.0,"n_steps_budget":1000.0,"object_pos_end":[0.53011,0.03004,0.01602],"object_pos_start":[0.53011,0.03004,0.01602],"object_to_goal_dist_end":0.28613,"object_to_goal_dist_start":0.28613,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3792.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_goal","tcp_end":[0.58303,0.18432,0.24816],"tcp_start":[0.57373,0.15974,0.35484],"tcp_to_object_dist_end":0.28371,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53011,0.03004,0.01602],"object_pos_start":[0.53011,0.03004,0.01602],"object_to_goal_dist_end":0.28613,"object_to_goal_dist_start":0.28613,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1023.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.5788,0.18277,0.26876],"tcp_start":[0.58303,0.18432,0.24816],"tcp_to_object_dist_end":0.29929,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":542.0,"n_steps_budget":600.0,"object_pos_end":[0.53011,0.03004,0.01602],"object_pos_start":[0.53011,0.03004,0.01602],"object_to_goal_dist_end":0.28613,"object_to_goal_dist_start":0.28613,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2168.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.57809,0.18229,0.39637],"tcp_start":[0.5788,0.18277,0.26876],"tcp_to_object_dist_end":0.41249,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```