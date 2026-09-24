## Search State

- **Seed**: 4
- **Iteration**: 12 / 15

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

## Current Skill (Q=-0.235) — your mutation base

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

- **Composite score**: -0.235
- **task_score** (E): 0.263
- **fitness_score**: 0.595  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.830

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_high | 1.00 | 1.00 | 0.0708 |
| align_over_object | 1.00 | 1.00 | 0.0114 |
| descend_to_grasp | 1.00 | 1.00 | 0.1716 |
| grasp_1 | 1.00 | 1.00 | 0.0123 |
| lift_1 | 1.00 | 1.00 | 0.1208 |
| transport_1 | 1.00 | 1.00 | 0.1945 |
| release_1 | 1.00 | 1.00 | 0.0210 |
| retract_1 | 1.00 | 1.00 | 0.1535 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_high | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.522, 0.007, 0.238) | (0.526, 0.005, 0.030)→(0.526, 0.005, 0.026) | 0.246→0.249 | 1.00 / 4.000 | 0.123 | 0.138 |
| align_over_object | approach | 1.00 / step_budget | (0.522, 0.007, 0.238)→(0.522, 0.006, 0.227) | (0.526, 0.005, 0.026)→(0.526, 0.005, 0.026) | 0.249→0.249 | 1.00 / 4.000 | 0.123 | 0.123 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.522, 0.006, 0.227)→(0.521, 0.005, 0.055) | (0.526, 0.005, 0.026)→(0.526, 0.005, 0.026) | 0.249→0.249 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.521, 0.005, 0.055)→(0.513, 0.005, 0.046) | (0.526, 0.005, 0.026)→(0.526, 0.005, 0.026) | 0.249→0.249 | 1.00 / 42.333 | 0.136 | 0.166 |
| lift_1 | lift | 1.00 / step_budget | (0.513, 0.005, 0.046)→(0.522, 0.005, 0.166) | (0.526, 0.005, 0.026)→(0.534, 0.005, 0.138) | 0.249→0.201 | 1.00 / 24.333 | 55983.974 | 0.432 |
| transport_1 | approach | 1.00 / step_budget | (0.522, 0.005, 0.166)→(0.600, 0.156, 0.254) | (0.534, 0.005, 0.138)→(0.565, 0.061, 0.016) | 0.201→0.210 | 1.00 / 8.000 | 3249.664 | 1.625 |
| release_1 | release | 1.00 / step_budget | (0.600, 0.156, 0.254)→(0.596, 0.154, 0.274) | (0.565, 0.061, 0.016)→(0.565, 0.061, 0.016) | 0.210→0.210 | 1.00 / 4.000 | 0.123 | 0.123 |
| retract_1 | retract | 1.00 / step_budget | (0.596, 0.154, 0.274)→(0.596, 0.154, 0.428) | (0.565, 0.061, 0.016)→(0.565, 0.061, 0.016) | 0.210→0.210 | 1.00 / 4.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.369
- phase_score: 0.436
- phase_breakdown.pre_grasp_score: 0.306
- phase_breakdown.place_goal_score: 0.098
- phase_breakdown.descend_grasp_score: 0.862
- phase_breakdown.lift_score: 0.332
- grasp_place_fitness: 0.648

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.648
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.369
- **Median Q (composite search score)**: -0.231
- **K-run variance**: 0.0021
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.342


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.9916,"average_solve_count":119.0,"average_success_count":119.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_over_object.align_speed":0.25542,"approach_high.approach_speed":0.39978,"approach_high.arc_height":0.13913,"descend_to_grasp.descend_speed":0.36104,"grasp_1.grasp_retry_offset_z":-0.00787,"grasp_1.grasp_timeout":0.56381,"lift_1.lift_height_offset":0.15022,"lift_1.lift_speed":0.65927,"release_1.release_timeout":1.45228,"retract_1.retract_speed":0.32379,"retract_1.retract_z_offset":0.18306,"transport_1.transport_speed":0.53831,"transport_1.transport_z_offset":0.0562},"optimized_scores":{"best_composite_score":-0.23082,"best_fitness_score":0.59918,"best_task_score":0.26867},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2118.0,"contact_point_centroid":[0.60242,0.07948,-0.00244],"force_p95":0.17969,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.67559,"mean_force":0.14467,"phase_index":5.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.60819,0.10502,0.21027]},{"body_a":"world","body_b":"grasp_target","contact_count":153.0,"contact_point_centroid":[0.54268,0.00099,-0.00116],"force_p95":0.24398,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.46703,"mean_force":0.06121,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.5295,0.00087,0.04585]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8393.0,"contact_point_centroid":[0.53512,0.01982,0.09441],"force_p95":0.10075,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30532,"mean_force":0.06673,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53225,0.0009,0.09231]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8610.0,"contact_point_centroid":[0.53454,-0.01799,0.09189],"force_p95":0.10594,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30452,"mean_force":0.06477,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53198,0.00089,0.08979]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4982.0,"contact_point_centroid":[0.5626,0.04848,0.1706],"force_p95":0.11356,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26575,"mean_force":0.07527,"phase_index":5.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.55642,0.03009,0.1709]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4203.0,"contact_point_centroid":[0.56065,0.00866,0.16951],"force_p95":0.14551,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2606,"mean_force":0.08647,"phase_index":5.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.5546,0.02734,0.16957]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.5443,0.00114,-0.00203],"force_p95":0.1311,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.14734,"mean_force":0.12529,"phase_index":3.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53209,0.00091,0.04574]},{"body_a":"world","body_b":"grasp_target","contact_count":1136.0,"contact_point_centroid":[0.54431,0.00113,-0.00188],"force_p95":0.13644,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12306,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.52157,0.00058,0.27331]},{"body_a":"world","body_b":"grasp_target","contact_count":292.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"align_over_object","phase_type":"approach","tcp_position_centroid":[0.53861,0.00102,0.23177]},{"body_a":"world","body_b":"grasp_target","contact_count":3068.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":2.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.53798,0.00103,0.13114]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.60249,0.07951,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.63059,0.14118,0.22995]},{"body_a":"world","body_b":"grasp_target","contact_count":2168.0,"contact_point_centroid":[0.60249,0.07951,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.62809,0.14032,0.32563]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4803.0,"contact_point_centroid":[0.53139,-0.01819,0.04649],"force_p95":0.06823,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10377,"mean_force":0.04499,"phase_index":3.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53086,0.00089,0.04428]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4296.0,"contact_point_centroid":[0.53151,0.02011,0.0468],"force_p95":0.07509,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09338,"mean_force":0.05022,"phase_index":3.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53086,0.00089,0.04429]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2032.0,"contact_point_centroid":[0.61134,0.10895,0.21458],"force_p95":0.01161,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01635,"mean_force":0.01054,"phase_index":5.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.61093,0.10894,0.21237]},{"body_a":"left_finger","body_b":"right_finger","contact_count":223.0,"contact_point_centroid":[0.63309,0.14193,0.22923],"force_p95":0.01091,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01274,"mean_force":0.00996,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.63284,0.14192,0.22687]}],"total_contact_groups":16},"final_pose_error":0.02061,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.60249,0.07951,0.01602],"final_tcp_position":[0.62929,0.14053,0.41164],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":9748.74786,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":285.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_high","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1136.0,"raw_peak_contact_force":0.13845,"subtask_id":"pre_grasp","tcp_end":[0.53889,0.00102,0.2383],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.21235,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":73.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"align_over_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":292.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.53931,0.00104,0.22601],"tcp_start":[0.53889,0.00102,0.2383],"tcp_to_object_dist_end":0.20005,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":767.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3068.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_grasp","tcp_end":[0.5391,0.00104,0.05416],"tcp_start":[0.53931,0.00104,0.22601],"tcp_to_object_dist_end":0.02862,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54421,0.00108,0.02587],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25029,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.13417,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10899.0,"raw_peak_contact_force":0.14734,"tcp_end":[0.53083,0.00089,0.04424],"tcp_start":[0.5391,0.00104,0.05416],"tcp_to_object_dist_end":0.02273,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":24.0,"n_steps":542.0,"n_steps_budget":600.0,"object_pos_end":[0.55309,0.00115,0.13473],"object_pos_start":[0.54421,0.00108,0.02587],"object_to_goal_dist_end":0.19169,"object_to_goal_dist_start":0.25029,"object_z_max":0.13456,"peak_contact_force":0.09825,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":17156.0,"raw_peak_contact_force":0.46703,"subtask_id":"lift","tcp_end":[0.53944,0.001,0.16045],"tcp_start":[0.53083,0.00089,0.04424],"tcp_to_object_dist_end":0.02912,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.60249,0.07951,0.01602],"object_pos_start":[0.55309,0.00115,0.13473],"object_to_goal_dist_end":0.19714,"object_to_goal_dist_start":0.19169,"object_z_max":0.15093,"peak_contact_force":9748.74786,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":13335.0,"raw_peak_contact_force":1.67559,"subtask_id":"place_goal","tcp_end":[0.63399,0.14183,0.22992],"tcp_start":[0.53944,0.001,0.16045],"tcp_to_object_dist_end":0.22501,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.60249,0.07951,0.01602],"object_pos_start":[0.60249,0.07951,0.01602],"object_to_goal_dist_end":0.19714,"object_to_goal_dist_start":0.19714,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1023.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.62936,0.14078,0.24918],"tcp_start":[0.63399,0.14183,0.22992],"tcp_to_object_dist_end":0.24257,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":542.0,"n_steps_budget":600.0,"object_pos_end":[0.60249,0.07951,0.01602],"object_pos_start":[0.60249,0.07951,0.01602],"object_to_goal_dist_end":0.19714,"object_to_goal_dist_start":0.19714,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2168.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.62929,0.14053,0.41164],"tcp_start":[0.62936,0.14078,0.24918],"tcp_to_object_dist_end":0.40119,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.14286,"average_solve_count":119.0,"average_success_count":119.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_over_object.align_speed":0.35119,"approach_high.approach_speed":0.55136,"approach_high.arc_height":0.1085,"descend_to_grasp.descend_speed":0.32633,"grasp_1.grasp_retry_offset_z":-0.01828,"grasp_1.grasp_timeout":1.62452,"lift_1.lift_height_offset":0.16505,"lift_1.lift_speed":0.89636,"release_1.release_timeout":1.17433,"retract_1.retract_speed":0.64293,"retract_1.retract_z_offset":0.19131,"transport_1.transport_speed":0.75966,"transport_1.transport_z_offset":0.11651},"optimized_scores":{"best_composite_score":-0.18161,"best_fitness_score":0.64839,"best_task_score":0.36926},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":3055.0,"contact_point_centroid":[0.55552,0.07028,-0.00231],"force_p95":0.12936,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.60748,"mean_force":0.13842,"phase_index":5.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.56624,0.11518,0.19662]},{"body_a":"world","body_b":"grasp_target","contact_count":136.0,"contact_point_centroid":[0.52892,0.02954,-0.00115],"force_p95":0.23357,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.43866,"mean_force":0.05449,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51609,0.0298,0.04703]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8135.0,"contact_point_centroid":[0.52161,0.01081,0.10074],"force_p95":0.10725,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30402,"mean_force":0.06835,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51884,0.02973,0.09935]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8780.0,"contact_point_centroid":[0.52166,0.04863,0.09942],"force_p95":0.10272,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30046,"mean_force":0.06459,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51871,0.02973,0.09788]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1890.0,"contact_point_centroid":[0.53666,0.06105,0.17455],"force_p95":0.12968,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29453,"mean_force":0.07776,"phase_index":5.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.53026,0.04276,0.17537]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1513.0,"contact_point_centroid":[0.53624,0.02255,0.17493],"force_p95":0.175,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26357,"mean_force":0.09342,"phase_index":5.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.52968,0.04121,0.1752]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53052,0.0307,-0.00208],"force_p95":0.14431,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19705,"mean_force":0.12863,"phase_index":3.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51854,0.02998,0.04661]},{"body_a":"world","body_b":"grasp_target","contact_count":1128.0,"contact_point_centroid":[0.5305,0.03079,-0.00188],"force_p95":0.13644,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12306,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.51533,0.01756,0.27492]},{"body_a":"world","body_b":"grasp_target","contact_count":228.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"align_over_object","phase_type":"approach","tcp_position_centroid":[0.52618,0.03005,0.23372]},{"body_a":"world","body_b":"grasp_target","contact_count":3032.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":2.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.52458,0.03026,0.13419]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.55555,0.07023,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.58823,0.16396,0.21353]},{"body_a":"world","body_b":"grasp_target","contact_count":2168.0,"contact_point_centroid":[0.55555,0.07023,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.58537,0.1629,0.31422]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4586.0,"contact_point_centroid":[0.51771,0.01069,0.04779],"force_p95":0.07146,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11577,"mean_force":0.04718,"phase_index":3.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51734,0.0299,0.04522]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5176.0,"contact_point_centroid":[0.51785,0.0491,0.04738],"force_p95":0.06834,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0696,"mean_force":0.04276,"phase_index":3.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51735,0.0299,0.04523]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3007.0,"contact_point_centroid":[0.56869,0.1191,0.20006],"force_p95":0.01108,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01645,"mean_force":0.01055,"phase_index":5.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.56825,0.11908,0.19786]},{"body_a":"left_finger","body_b":"right_finger","contact_count":219.0,"contact_point_centroid":[0.59103,0.16481,0.21183],"force_p95":0.01095,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01097,"mean_force":0.01013,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.59058,0.16479,0.20965]}],"total_contact_groups":16},"final_pose_error":0.02036,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.55555,0.07023,0.01602],"final_tcp_position":[0.58648,0.16314,0.4042],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":1.60748,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":283.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_high","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1128.0,"raw_peak_contact_force":0.13845,"subtask_id":"pre_grasp","tcp_end":[0.52693,0.02995,0.23916],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.21317,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":57.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"align_over_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":228.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.52626,0.03021,0.22843],"tcp_start":[0.52693,0.02995,0.23916],"tcp_to_object_dist_end":0.20245,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":758.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3032.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_grasp","tcp_end":[0.52541,0.03044,0.05464],"tcp_start":[0.52626,0.03021,0.22843],"tcp_to_object_dist_end":0.02907,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53044,0.03013,0.02571],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18406,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.14219,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11562.0,"raw_peak_contact_force":0.19705,"tcp_end":[0.51731,0.0299,0.04519],"tcp_start":[0.52541,0.03044,0.05464],"tcp_to_object_dist_end":0.02349,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":26.0,"n_steps":542.0,"n_steps_budget":600.0,"object_pos_end":[0.53914,0.03023,0.14756],"object_pos_start":[0.53044,0.03013,0.02571],"object_to_goal_dist_end":0.16571,"object_to_goal_dist_start":0.18406,"object_z_max":0.14738,"peak_contact_force":0.09511,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":17051.0,"raw_peak_contact_force":0.43866,"subtask_id":"lift","tcp_end":[0.52598,0.02987,0.175],"tcp_start":[0.51731,0.0299,0.04519],"tcp_to_object_dist_end":0.03043,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.55555,0.07023,0.01602],"object_pos_start":[0.53914,0.03023,0.14756],"object_to_goal_dist_end":0.14944,"object_to_goal_dist_start":0.16571,"object_z_max":0.14769,"peak_contact_force":0.12263,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":9465.0,"raw_peak_contact_force":1.60748,"subtask_id":"place_goal","tcp_end":[0.59176,0.16492,0.2124],"tcp_start":[0.52598,0.02987,0.175],"tcp_to_object_dist_end":0.221,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.55555,0.07023,0.01602],"object_pos_start":[0.55555,0.07023,0.01602],"object_to_goal_dist_end":0.14944,"object_to_goal_dist_start":0.14944,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1019.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.58689,0.16349,0.23324],"tcp_start":[0.59176,0.16492,0.2124],"tcp_to_object_dist_end":0.23846,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":542.0,"n_steps_budget":600.0,"object_pos_end":[0.55555,0.07023,0.01602],"object_pos_start":[0.55555,0.07023,0.01602],"object_to_goal_dist_end":0.14944,"object_to_goal_dist_start":0.14944,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2168.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.58648,0.16314,0.4042],"tcp_start":[0.58689,0.16349,0.23324],"tcp_to_object_dist_end":0.40034,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.0339,"average_solve_count":118.0,"average_success_count":118.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_over_object.align_speed":0.12048,"approach_high.approach_speed":0.59003,"approach_high.arc_height":0.17572,"descend_to_grasp.descend_speed":0.49107,"grasp_1.grasp_retry_offset_z":-0.00728,"grasp_1.grasp_timeout":0.84385,"lift_1.lift_height_offset":0.15249,"lift_1.lift_speed":0.63678,"release_1.release_timeout":1.96238,"retract_1.retract_speed":0.69136,"retract_1.retract_z_offset":0.14376,"transport_1.transport_speed":0.49937,"transport_1.transport_z_offset":0.10241},"optimized_scores":{"best_composite_score":-0.29355,"best_fitness_score":0.53645,"best_task_score":0.15175},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2869.0,"contact_point_centroid":[0.536,0.03392,-0.00236],"force_p95":0.12727,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.59096,"mean_force":0.14014,"phase_index":5.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.54532,0.09692,0.26086]},{"body_a":"world","body_b":"grasp_target","contact_count":146.0,"contact_point_centroid":[0.50232,-0.01526,-0.00111],"force_p95":0.22357,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.3912,"mean_force":0.05103,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48985,-0.01539,0.04999]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1696.0,"contact_point_centroid":[0.50836,0.01666,0.16958],"force_p95":0.16511,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30561,"mean_force":0.10341,"phase_index":5.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.50264,-0.00187,0.17242]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7784.0,"contact_point_centroid":[0.49487,0.00356,0.09526],"force_p95":0.13341,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29777,"mean_force":0.07353,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4923,-0.01536,0.09514]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8610.0,"contact_point_centroid":[0.49501,-0.03408,0.09578],"force_p95":0.1026,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27982,"mean_force":0.06458,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49234,-0.01536,0.09543]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2191.0,"contact_point_centroid":[0.50963,-0.01817,0.17267],"force_p95":0.12781,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19704,"mean_force":0.07948,"phase_index":5.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.50323,-0.00021,0.17372]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50382,-0.01563,-0.00203],"force_p95":0.13199,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15278,"mean_force":0.12523,"phase_index":3.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49226,-0.01542,0.04957]},{"body_a":"world","body_b":"grasp_target","contact_count":816.0,"contact_point_centroid":[0.50382,-0.01567,-0.00184],"force_p95":0.13728,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12323,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.49947,-0.0016,0.26851]},{"body_a":"world","body_b":"grasp_target","contact_count":288.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"align_over_object","phase_type":"approach","tcp_position_centroid":[0.49946,-0.01116,0.23112]},{"body_a":"world","body_b":"grasp_target","contact_count":2968.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":2.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.49797,-0.01429,0.13686]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.53602,0.03404,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57126,0.15951,0.31982]},{"body_a":"world","body_b":"grasp_target","contact_count":2168.0,"contact_point_centroid":[0.53602,0.03404,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.56992,0.15883,0.3992]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4362.0,"contact_point_centroid":[0.49156,0.00378,0.04952],"force_p95":0.07239,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09963,"mean_force":0.04941,"phase_index":3.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49111,-0.01541,0.04832]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4879.0,"contact_point_centroid":[0.49152,-0.03454,0.04929],"force_p95":0.06825,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08633,"mean_force":0.04461,"phase_index":3.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49111,-0.01541,0.04832]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2865.0,"contact_point_centroid":[0.5474,0.10091,0.26673],"force_p95":0.01111,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01637,"mean_force":0.01049,"phase_index":5.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.54708,0.1009,0.26448]},{"body_a":"left_finger","body_b":"right_finger","contact_count":223.0,"contact_point_centroid":[0.57293,0.16011,0.31804],"force_p95":0.011,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01273,"mean_force":0.01004,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57263,0.1601,0.31577]}],"total_contact_groups":16},"final_pose_error":0.01672,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.53602,0.03404,0.01602],"final_tcp_position":[0.57077,0.15899,0.46672],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":167951.73011,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":205.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_high","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":816.0,"raw_peak_contact_force":0.13845,"subtask_id":"pre_grasp","tcp_end":[0.50012,-0.0094,0.23674],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.21084,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":72.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"align_over_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":288.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.49961,-0.01303,0.22609],"tcp_start":[0.50012,-0.0094,0.23674],"tcp_to_object_dist_end":0.20013,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":742.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2968.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_grasp","tcp_end":[0.4989,-0.01551,0.05686],"tcp_start":[0.49961,-0.01303,0.22609],"tcp_to_object_dist_end":0.03123,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50373,-0.01543,0.02587],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.3122,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.13141,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11041.0,"raw_peak_contact_force":0.15278,"tcp_end":[0.49108,-0.01541,0.04829],"tcp_start":[0.4989,-0.01551,0.05686],"tcp_to_object_dist_end":0.02574,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":542.0,"n_steps_budget":600.0,"object_pos_end":[0.50953,-0.01627,0.13281],"object_pos_start":[0.50373,-0.01543,0.02587],"object_to_goal_dist_end":0.24654,"object_to_goal_dist_start":0.3122,"object_z_max":0.13265,"peak_contact_force":167951.73011,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":16540.0,"raw_peak_contact_force":0.3912,"subtask_id":"lift","tcp_end":[0.49918,-0.01536,0.16367],"tcp_start":[0.49108,-0.01541,0.04829],"tcp_to_object_dist_end":0.03256,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53602,0.03404,0.01602],"object_pos_start":[0.50953,-0.01627,0.13281],"object_to_goal_dist_end":0.28283,"object_to_goal_dist_start":0.24654,"object_z_max":0.1529,"peak_contact_force":0.12263,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":9621.0,"raw_peak_contact_force":1.59096,"subtask_id":"place_goal","tcp_end":[0.57335,0.16011,0.31825],"tcp_start":[0.49918,-0.01536,0.16367],"tcp_to_object_dist_end":0.32959,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53602,0.03404,0.01602],"object_pos_start":[0.53602,0.03404,0.01602],"object_to_goal_dist_end":0.28283,"object_to_goal_dist_start":0.28283,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1023.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.57059,0.1592,0.33968],"tcp_start":[0.57335,0.16011,0.31825],"tcp_to_object_dist_end":0.34873,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":542.0,"n_steps_budget":600.0,"object_pos_end":[0.53602,0.03404,0.01602],"object_pos_start":[0.53602,0.03404,0.01602],"object_to_goal_dist_end":0.28283,"object_to_goal_dist_start":0.28283,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2168.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.57077,0.15899,0.46672],"tcp_start":[0.57059,0.1592,0.33968],"tcp_to_object_dist_end":0.46899,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```