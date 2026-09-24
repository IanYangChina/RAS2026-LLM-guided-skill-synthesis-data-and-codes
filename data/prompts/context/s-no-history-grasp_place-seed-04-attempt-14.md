## Search State

- **Seed**: 4
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

## Current Skill (Q=-0.270) — your mutation base

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
  target_entity: object
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
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.2
    tolerance: 0.01
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: world_z
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.1
      - 0.3
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
  generator: arc_cartesian
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
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: world_z
  parameters:
    transport_arc_height:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.arc_height
        mode: replace
    transport_speed:
      type: scalar
      range:
      - 0.2
      - 1.0
      default: 0.5
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: object_still_lifted
    when: during_phase
    predicate: object_lifted
    threshold: 0.05
    on_failure: continue
- id: descend_to_place
  type: descend
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
    - 0.0
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    descend_to_place_speed:
      type: scalar
      range:
      - 0.1
      - 0.5
      default: 0.2
      binds_to:
      - path: generator.speed
        mode: replace
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
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.2], tolerance=0.01
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=world_z
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
    - lift_speed: status=consumed; consumers=generator.speed (replace)
- **transport_1** (`approach`)
  - target: source=yaml, anchor=task_goal, entity=placement_surface, offset=[0.0, 0.0, 0.1], tolerance=0.01
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=world_z
  - parameter_bindings:
    - transport_arc_height: status=consumed; consumers=generator.arc_height (replace)
    - transport_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=object_still_lifted, when=during_phase, predicate=object_lifted, on_failure=continue, threshold=0.05
- **descend_to_place** (`descend`)
  - target: source=yaml, anchor=task_goal, entity=placement_surface, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_to_place_speed: status=consumed; consumers=generator.speed (replace)
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

- **Composite score**: -0.270
- **task_score** (E): 0.361
- **fitness_score**: 0.560  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.830

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_high | 1.00 | 1.00 | 0.0713 |
| descend_to_grasp | 1.00 | 1.00 | 0.1823 |
| grasp_1 | 1.00 | 1.00 | 0.0123 |
| lift_1 | 0.33 | 1.00 | 0.1642 |
| transport_1 | 0.33 | 1.00 | 0.1629 |
| descend_to_place | 0.33 | 1.00 | 0.0866 |
| release_1 | 1.00 | 1.00 | 0.0243 |
| retract_1 | 1.00 | 1.00 | 0.1162 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_high | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.522, 0.008, 0.238) | (0.526, 0.005, 0.030)→(0.526, 0.005, 0.026) | 0.246→0.249 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.522, 0.008, 0.238)→(0.521, 0.005, 0.056) | (0.526, 0.005, 0.026)→(0.526, 0.005, 0.026) | 0.249→0.249 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.521, 0.005, 0.056)→(0.513, 0.005, 0.046) | (0.526, 0.005, 0.026)→(0.526, 0.005, 0.026) | 0.249→0.249 | 1.00 / 44.333 | 0.136 | 0.172 |
| lift_1 | lift | 0.33 / step_budget | (0.513, 0.005, 0.046)→(0.559, 0.006, 0.155) | (0.526, 0.005, 0.026)→(0.573, 0.010, 0.166) | 0.249→0.204 | 1.00 / 26.333 | 3514.917 | 695.968 |
| transport_1 | approach | 0.33 / step_budget | (0.559, 0.006, 0.155)→(0.546, 0.137, 0.227) | (0.573, 0.010, 0.166)→(0.562, 0.136, 0.226) | 0.204→0.147 | 1.00 / 30.000 | 56070.561 | 697.570 |
| descend_to_place | descend | 0.33 / step_budget | (0.546, 0.137, 0.227)→(0.596, 0.169, 0.234) | (0.562, 0.136, 0.226)→(0.616, 0.170, 0.227) | 0.147→0.080 | 1.00 / 29.000 | 160.695 | 729.633 |
| release_1 | release | 1.00 / step_budget | (0.596, 0.169, 0.234)→(0.595, 0.168, 0.258) | (0.616, 0.170, 0.227)→(0.618, 0.172, 0.228) | 0.080→0.082 | 1.00 / 2.333 | 0.571 | 103.280 |
| retract_1 | retract | 1.00 / step_budget | (0.595, 0.168, 0.258)→(0.595, 0.168, 0.374) | (0.618, 0.172, 0.228)→(0.582, 0.186, 0.152) | 0.082→0.154 | 1.00 / 3.000 | 0.250 | 1.513 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.431
- phase_score: 0.359
- phase_breakdown.pre_grasp_score: 0.304
- phase_breakdown.place_goal_score: 0.000
- phase_breakdown.descend_grasp_score: 0.871
- phase_breakdown.lift_score: 0.034
- grasp_place_fitness: 0.679

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.679
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.431
- **Median Q (composite search score)**: -0.205
- **K-run variance**: 0.0174
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.236


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":16.0,"average_failure_rate":0.15842,"average_mean_iterations":35.84158,"average_solve_count":101.0,"average_success_count":85.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_high.approach_speed":0.69679,"approach_high.arc_height":0.13781,"descend_to_grasp.descend_speed":0.34827,"descend_to_place.descend_to_place_speed":0.36333,"grasp_1.grasp_retry_offset_z":-0.00752,"grasp_1.grasp_timeout":1.24477,"lift_1.lift_height":0.25469,"lift_1.lift_speed":0.517,"release_1.release_timeout":1.80345,"retract_1.retract_speed":0.38348,"retract_1.retract_z_offset":0.12377,"transport_1.transport_arc_height":0.0612,"transport_1.transport_speed":0.60741},"optimized_scores":{"best_composite_score":-0.45404,"best_fitness_score":0.37596,"best_task_score":0.323},"replay_outcomes":[{"contacts":{"omitted_contact_groups":9,"reported_contact_groups":[{"body_a":"world","body_b":"hand","contact_count":230.0,"contact_point_centroid":[0.64123,0.07823,-0.00099],"force_p95":358.95317,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":543.38593,"mean_force":221.03746,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.57338,0.02216,0.001]},{"body_a":"world","body_b":"hand","contact_count":32.0,"contact_point_centroid":[0.60489,0.10532,-3e-05],"force_p95":71.45925,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":317.96591,"mean_force":47.23208,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.50613,0.08077,0.04766]},{"body_a":"world","body_b":"left_finger","contact_count":1536.0,"contact_point_centroid":[0.59763,-0.01577,-0.01199],"force_p95":12.47172,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":46.95526,"mean_force":8.81979,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.59901,0.00747,-0.01312]},{"body_a":"world","body_b":"right_finger","contact_count":1820.0,"contact_point_centroid":[0.59722,0.03055,-0.01133],"force_p95":10.32372,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":44.13064,"mean_force":7.32666,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.59394,0.00931,-0.01032]},{"body_a":"world","body_b":"grasp_target","contact_count":529.0,"contact_point_centroid":[0.58683,0.00799,-0.00791],"force_p95":1.93911,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.0101,"mean_force":0.81695,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.59113,0.00574,-0.00501]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2180.0,"contact_point_centroid":[0.56039,0.0089,0.01902],"force_p95":0.54979,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.38644,"mean_force":0.21371,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.56301,0.02369,0.01093]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1644.0,"contact_point_centroid":[0.57328,0.03504,0.01201],"force_p95":0.55839,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.58657,"mean_force":0.20563,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.56825,0.01716,0.00741]},{"body_a":"world","body_b":"grasp_target","contact_count":1612.0,"contact_point_centroid":[0.65153,0.19633,-0.00252],"force_p95":0.27402,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.4905,"mean_force":0.14613,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.59196,0.12824,0.21497]},{"body_a":"grasp_target","body_b":"hand","contact_count":63.0,"contact_point_centroid":[0.6834,0.16682,0.13493],"force_p95":0.67413,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.9779,"mean_force":0.46328,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.59273,0.12846,0.15444]},{"body_a":"grasp_target","body_b":"hand","contact_count":200.0,"contact_point_centroid":[0.66177,0.13813,0.13026],"force_p95":0.92159,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.92587,"mean_force":0.69269,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.59476,0.12896,0.13251]},{"body_a":"grasp_target","body_b":"hand","contact_count":780.0,"contact_point_centroid":[0.5916,0.0898,0.1019],"force_p95":0.4598,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.87501,"mean_force":0.3217,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.55014,0.10287,0.08519]},{"body_a":"grasp_target","body_b":"hand","contact_count":1.0,"contact_point_centroid":[0.53553,0.0485,0.07387],"force_p95":0.84585,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.84585,"mean_force":0.84585,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.51007,0.0757,0.04425]},{"body_a":"grasp_target","body_b":"hand","contact_count":197.0,"contact_point_centroid":[0.58266,0.01603,0.04709],"force_p95":0.49572,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.83999,"mean_force":0.34459,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.56071,0.02959,0.00983]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4030.0,"contact_point_centroid":[0.56481,0.10749,0.0906],"force_p95":0.2219,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.52221,"mean_force":0.15659,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.553,0.1045,0.08805]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":970.0,"contact_point_centroid":[0.61398,0.14152,0.12963],"force_p95":0.28777,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.38437,"mean_force":0.18793,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.59473,0.12895,0.13258]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":370.0,"contact_point_centroid":[0.62441,0.15194,0.13979],"force_p95":0.2355,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28649,"mean_force":0.10399,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.59261,0.12843,0.15475]}],"total_contact_groups":25},"final_pose_error":0.01713,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.65156,0.19639,0.02602],"final_tcp_position":[0.59255,0.12834,0.25859],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":167951.73011,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":286.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_high","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1140.0,"raw_peak_contact_force":0.13845,"subtask_id":"pre_grasp","tcp_end":[0.53894,0.00102,0.23831],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.21236,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":790.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3160.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_grasp","tcp_end":[0.53911,0.00104,0.05448],"tcp_start":[0.53894,0.00102,0.23831],"tcp_to_object_dist_end":0.02894,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":47.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54421,0.00094,0.02586],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25039,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.13083,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12218.0,"raw_peak_contact_force":0.15304,"tcp_end":[0.53085,0.00089,0.04458],"tcp_start":[0.53911,0.00104,0.05448],"tcp_to_object_dist_end":0.023,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":7.0,"n_steps":300.0,"n_steps_budget":600.0,"object_pos_end":[0.53869,0.07394,0.07247],"object_pos_start":[0.54421,0.00094,0.02586],"object_to_goal_dist_end":0.18172,"object_to_goal_dist_start":0.25039,"object_z_max":0.07217,"peak_contact_force":9760.30694,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":8136.0,"raw_peak_contact_force":543.38593,"subtask_id":"lift","tcp_end":[0.51007,0.0757,0.04425],"tcp_start":[0.53085,0.00089,0.04458],"tcp_to_object_dist_end":0.04023,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.53821,0.07458,0.07276],"object_pos_start":[0.53869,0.07394,0.07247],"object_to_goal_dist_end":0.18152,"object_to_goal_dist_start":0.18172,"object_z_max":0.07247,"peak_contact_force":167951.73011,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":7.0,"raw_peak_contact_force":0.84585,"tcp_end":[0.50938,0.0765,0.04478],"tcp_start":[0.51007,0.0757,0.04425],"tcp_to_object_dist_end":0.04022,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":12.0,"n_steps":780.0,"n_steps_budget":1000.0,"object_pos_end":[0.63622,0.13349,0.14465],"object_pos_start":[0.53821,0.07458,0.07276],"object_to_goal_dist_end":0.05378,"object_to_goal_dist_start":0.18152,"object_z_max":0.14462,"peak_contact_force":0.41486,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":11072.0,"raw_peak_contact_force":317.96591,"tcp_end":[0.5978,0.12979,0.13209],"tcp_start":[0.50938,0.0765,0.04478],"tcp_to_object_dist_end":0.0406,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.6547,0.16072,0.13761],"object_pos_start":[0.63622,0.13349,0.14465],"object_to_goal_dist_end":0.05403,"object_to_goal_dist_start":0.05378,"object_z_max":0.14465,"peak_contact_force":0.67799,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1441.0,"raw_peak_contact_force":0.92587,"tcp_end":[0.59367,0.12869,0.15191],"tcp_start":[0.5978,0.12979,0.13209],"tcp_to_object_dist_end":0.07039,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":542.0,"n_steps_budget":600.0,"object_pos_end":[0.65156,0.19639,0.02602],"object_pos_start":[0.6547,0.16072,0.13761],"object_to_goal_dist_end":0.16952,"object_to_goal_dist_start":0.05403,"object_z_max":0.13783,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2045.0,"raw_peak_contact_force":1.4905,"tcp_end":[0.59255,0.12834,0.25859],"tcp_start":[0.59367,0.12869,0.15191],"tcp_to_object_dist_end":0.2494,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":15.0,"average_failure_rate":0.12712,"average_mean_iterations":29.5678,"average_solve_count":118.0,"average_success_count":103.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_high.approach_speed":0.70437,"approach_high.arc_height":0.08897,"descend_to_grasp.descend_speed":0.34494,"descend_to_place.descend_to_place_speed":0.39539,"grasp_1.grasp_retry_offset_z":-0.00759,"grasp_1.grasp_timeout":1.0781,"lift_1.lift_height":0.2404,"lift_1.lift_speed":0.62275,"release_1.release_timeout":1.28464,"retract_1.retract_speed":0.4703,"retract_1.retract_z_offset":0.12386,"transport_1.transport_arc_height":0.05887,"transport_1.transport_speed":0.52654},"optimized_scores":{"best_composite_score":-0.15142,"best_fitness_score":0.67858,"best_task_score":0.43109},"replay_outcomes":[{"contacts":{"omitted_contact_groups":16,"reported_contact_groups":[{"body_a":"world","body_b":"link7","contact_count":43.0,"contact_point_centroid":[0.73155,0.01182,-0.00039],"force_p95":1489.60456,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1776.39588,"mean_force":622.51182,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.79909,-0.05053,0.12955]},{"body_a":"world","body_b":"link6","contact_count":932.0,"contact_point_centroid":[0.64039,0.10392,-0.00033],"force_p95":488.034,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1657.5282,"mean_force":342.77662,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.72796,0.02747,0.22136]},{"body_a":"world","body_b":"link5","contact_count":616.0,"contact_point_centroid":[0.55403,0.08087,-0.00024],"force_p95":839.75971,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1045.12901,"mean_force":580.23159,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.56838,0.18368,0.27748]},{"body_a":"world","body_b":"hand","contact_count":131.0,"contact_point_centroid":[0.64282,-0.02414,-0.00023],"force_p95":444.50256,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":605.97659,"mean_force":201.88361,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.57564,-0.01051,-0.00335]},{"body_a":"world","body_b":"link6","contact_count":233.0,"contact_point_centroid":[0.61486,0.1862,-8e-05],"force_p95":294.91276,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":560.69408,"mean_force":170.0636,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.57516,0.18608,0.27663]},{"body_a":"world","body_b":"link6","contact_count":53.0,"contact_point_centroid":[0.51261,0.17237,-0.00071],"force_p95":392.39191,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":483.51876,"mean_force":271.33456,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.64102,-0.0383,0.10914]},{"body_a":"world","body_b":"link7","contact_count":33.0,"contact_point_centroid":[0.63307,0.07596,-0.0008],"force_p95":365.00421,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":416.62229,"mean_force":239.81589,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.61485,-0.05249,0.07784]},{"body_a":"world","body_b":"link5","contact_count":129.0,"contact_point_centroid":[0.50127,0.07934,-0.0003],"force_p95":324.63424,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":358.13692,"mean_force":247.54386,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.54779,0.16022,0.28139]},{"body_a":"world","body_b":"link6","contact_count":82.0,"contact_point_centroid":[0.63176,0.19296,-0.00011],"force_p95":75.30127,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":217.52808,"mean_force":59.17055,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.59948,0.19013,0.27526]},{"body_a":"world","body_b":"right_finger","contact_count":1848.0,"contact_point_centroid":[0.57745,0.02517,-0.01092],"force_p95":20.01663,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":47.47919,"mean_force":13.29923,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.5818,0.00507,-0.01343]},{"body_a":"world","body_b":"left_finger","contact_count":1937.0,"contact_point_centroid":[0.58706,-0.01518,-0.01112],"force_p95":13.56834,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":35.13695,"mean_force":8.58785,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.58074,0.00334,-0.01256]},{"body_a":"world","body_b":"grasp_target","contact_count":583.0,"contact_point_centroid":[0.56774,0.01298,-0.00645],"force_p95":2.2899,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.51308,"mean_force":0.80973,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.57404,0.01055,-0.00551]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2419.0,"contact_point_centroid":[0.58813,-0.0204,0.07657],"force_p95":0.73125,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.27505,"mean_force":0.28227,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.60022,-0.02566,0.06694]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1957.0,"contact_point_centroid":[0.619,-0.02488,0.06009],"force_p95":0.40333,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.2043,"mean_force":0.14882,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.61283,-0.02367,0.06358]},{"body_a":"grasp_target","body_b":"link5","contact_count":423.0,"contact_point_centroid":[0.59741,0.12208,0.1474],"force_p95":1.20204,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.17517,"mean_force":0.51005,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.60071,0.18866,0.33474]},{"body_a":"world","body_b":"grasp_target","contact_count":504.0,"contact_point_centroid":[0.51457,0.17739,-0.00388],"force_p95":0.89143,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.87766,"mean_force":0.22001,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.60107,0.18932,0.39483]}],"total_contact_groups":32},"final_pose_error":0.01674,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.51521,0.1774,0.01601],"final_tcp_position":[0.60115,0.18946,0.40847],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":1776.39588,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":297.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_high","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1184.0,"raw_peak_contact_force":0.13845,"subtask_id":"pre_grasp","tcp_end":[0.52799,0.03104,0.23955],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.21355,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":759.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3036.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_grasp","tcp_end":[0.52545,0.03046,0.05528],"tcp_start":[0.52799,0.03104,0.23955],"tcp_to_object_dist_end":0.0297,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53043,0.03009,0.0257],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.1841,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.14413,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11565.0,"raw_peak_contact_force":0.19555,"tcp_end":[0.51736,0.02992,0.04583],"tcp_start":[0.52545,0.03046,0.05528],"tcp_to_object_dist_end":0.024,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":330.0,"n_steps_budget":600.0,"object_pos_end":[0.64947,-0.00451,0.13382],"object_pos_start":[0.53043,0.03009,0.0257],"object_to_goal_dist_end":0.191,"object_to_goal_dist_start":0.1841,"object_z_max":0.13371,"peak_contact_force":485.3592,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":9199.0,"raw_peak_contact_force":605.97659,"subtask_id":"lift","tcp_end":[0.65194,-0.03246,0.13128],"tcp_start":[0.51736,0.02992,0.04583],"tcp_to_object_dist_end":0.02818,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.55656,0.17292,0.2603],"object_pos_start":[0.64947,-0.00451,0.13382],"object_to_goal_dist_end":0.15882,"object_to_goal_dist_start":0.191,"object_z_max":0.27285,"peak_contact_force":259.73133,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":35785.0,"raw_peak_contact_force":1776.39588,"tcp_end":[0.54562,0.16692,0.28001],"tcp_start":[0.65194,-0.03246,0.13128],"tcp_to_object_dist_end":0.02333,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":33.0,"n_steps":722.0,"n_steps_budget":1000.0,"object_pos_end":[0.61223,0.19772,0.25604],"object_pos_start":[0.55656,0.17292,0.2603],"object_to_goal_dist_end":0.14957,"object_to_goal_dist_start":0.15882,"object_z_max":0.26053,"peak_contact_force":97.08337,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":27761.0,"raw_peak_contact_force":1045.12901,"tcp_end":[0.59937,0.19048,0.27543],"tcp_start":[0.54562,0.16692,0.28001],"tcp_to_object_dist_end":0.02437,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.60329,0.17074,0.26361],"object_pos_start":[0.61223,0.19772,0.25604],"object_to_goal_dist_end":0.15573,"object_to_goal_dist_start":0.14957,"object_z_max":0.26346,"peak_contact_force":0.37304,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2295.0,"raw_peak_contact_force":217.52808,"tcp_end":[0.60004,0.18932,0.30132],"tcp_start":[0.59937,0.19048,0.27543],"tcp_to_object_dist_end":0.04216,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":542.0,"n_steps_budget":600.0,"object_pos_end":[0.51521,0.1774,0.01601],"object_pos_start":[0.60329,0.17074,0.26361],"object_to_goal_dist_end":0.12621,"object_to_goal_dist_start":0.15573,"object_z_max":0.26384,"peak_contact_force":0.1239,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":988.0,"raw_peak_contact_force":2.17517,"tcp_end":[0.60115,0.18946,0.40847],"tcp_start":[0.60004,0.18932,0.30132],"tcp_to_object_dist_end":0.40194,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":6.0,"average_failure_rate":0.05,"average_mean_iterations":14.44167,"average_solve_count":120.0,"average_success_count":114.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_high.approach_speed":0.48744,"approach_high.arc_height":0.12348,"descend_to_grasp.descend_speed":0.40589,"descend_to_place.descend_to_place_speed":0.34225,"grasp_1.grasp_retry_offset_z":-0.00865,"grasp_1.grasp_timeout":1.2152,"lift_1.lift_height":0.2192,"lift_1.lift_speed":0.62791,"release_1.release_timeout":1.76871,"retract_1.retract_speed":0.69895,"retract_1.retract_z_offset":0.15193,"transport_1.transport_arc_height":0.06708,"transport_1.transport_speed":0.48313},"optimized_scores":{"best_composite_score":-0.20507,"best_fitness_score":0.62493,"best_task_score":0.32915},"replay_outcomes":[{"contacts":{"omitted_contact_groups":11,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":176.0,"contact_point_centroid":[0.56532,-0.10407,-0.00069],"force_p95":389.45972,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":938.5417,"mean_force":329.86462,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.57162,0.0409,0.21124]},{"body_a":"world","body_b":"link6","contact_count":368.0,"contact_point_centroid":[0.57667,0.17103,-0.00034],"force_p95":582.31576,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":825.80272,"mean_force":443.87484,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.58714,0.18375,0.29326]},{"body_a":"world","body_b":"hand","contact_count":83.0,"contact_point_centroid":[0.60527,0.05485,-0.00061],"force_p95":372.28113,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":523.41704,"mean_force":175.3902,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.54874,0.00978,-0.00323]},{"body_a":"world","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.50045,-0.05604,-0.0],"force_p95":315.46849,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":315.46849,"mean_force":315.46849,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.51377,-0.02638,0.29087]},{"body_a":"world","body_b":"link6","contact_count":84.0,"contact_point_centroid":[0.58325,0.18024,-0.00016],"force_p95":86.94865,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":91.38649,"mean_force":62.62135,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.59,0.18725,0.294]},{"body_a":"world","body_b":"left_finger","contact_count":1355.0,"contact_point_centroid":[0.556,-0.01875,-0.00712],"force_p95":18.89608,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":50.4761,"mean_force":12.79998,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.55562,0.00501,-0.00819]},{"body_a":"world","body_b":"right_finger","contact_count":1429.0,"contact_point_centroid":[0.5566,0.02797,-0.00698],"force_p95":13.70715,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":45.80327,"mean_force":8.04096,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.55431,0.00554,-0.00745]},{"body_a":"world","body_b":"grasp_target","contact_count":400.0,"contact_point_centroid":[0.53962,-0.00154,-0.00846],"force_p95":2.4759,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.45955,"mean_force":0.98775,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.54645,0.00121,0.00298]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4960.0,"contact_point_centroid":[0.55174,0.02063,0.18915],"force_p95":0.53487,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.12194,"mean_force":0.12759,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.56241,0.03276,0.18226]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4476.0,"contact_point_centroid":[0.58123,0.04956,0.16594],"force_p95":0.27636,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.28663,"mean_force":0.1326,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.56888,0.03881,0.17245]},{"body_a":"grasp_target","body_b":"hand","contact_count":94.0,"contact_point_centroid":[0.5552,-0.00984,0.03787],"force_p95":1.03622,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.18185,"mean_force":0.49013,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53379,0.0184,0.00715]},{"body_a":"grasp_target","body_b":"hand","contact_count":542.0,"contact_point_centroid":[0.58695,0.18493,0.33355],"force_p95":0.63607,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.87471,"mean_force":0.52943,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.59107,0.18651,0.38363]},{"body_a":"grasp_target","body_b":"hand","contact_count":200.0,"contact_point_centroid":[0.60233,0.1787,0.25624],"force_p95":0.62122,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.71947,"mean_force":0.43475,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.59006,0.18709,0.30033]},{"body_a":"grasp_target","body_b":"hand","contact_count":542.0,"contact_point_centroid":[0.59954,0.17329,0.26039],"force_p95":0.2051,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.46442,"mean_force":0.17441,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.58577,0.18041,0.30338]},{"body_a":"grasp_target","body_b":"hand","contact_count":826.0,"contact_point_centroid":[0.55351,0.05527,0.3232],"force_p95":0.22099,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.35337,"mean_force":0.17,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.54746,0.07047,0.36602]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":19310.0,"contact_point_centroid":[0.55501,0.07179,0.35478],"force_p95":0.08191,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31014,"mean_force":0.05248,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.5428,0.05723,0.35682]}],"total_contact_groups":27},"final_pose_error":0.01732,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.57961,0.18278,0.41458],"final_tcp_position":[0.59187,0.18621,0.4551],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":938.5417,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":211.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_high","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":840.0,"raw_peak_contact_force":0.13845,"subtask_id":"pre_grasp","tcp_end":[0.50016,-0.00834,0.23566],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.2098,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":765.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3060.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_grasp","tcp_end":[0.49894,-0.01535,0.05701],"tcp_start":[0.50016,-0.00834,0.23566],"tcp_to_object_dist_end":0.03138,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50374,-0.01533,0.02584],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31216,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.13415,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11046.0,"raw_peak_contact_force":0.16597,"tcp_end":[0.49113,-0.01525,0.04846],"tcp_start":[0.49894,-0.01535,0.05701],"tcp_to_object_dist_end":0.0259,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":32.0,"n_steps":420.0,"n_steps_budget":600.0,"object_pos_end":[0.53136,-0.04056,0.29053],"object_pos_start":[0.50374,-0.01533,0.02584],"object_to_goal_dist_end":0.23848,"object_to_goal_dist_start":0.31216,"object_z_max":0.29072,"peak_contact_force":299.08471,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":12981.0,"raw_peak_contact_force":938.5417,"subtask_id":"lift","tcp_end":[0.51377,-0.02638,0.29087],"tcp_start":[0.49113,-0.01525,0.04846],"tcp_to_object_dist_end":0.0226,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.59002,0.16088,0.34392],"object_pos_start":[0.53136,-0.04056,0.29053],"object_to_goal_dist_end":0.09947,"object_to_goal_dist_start":0.23848,"object_z_max":0.3703,"peak_contact_force":0.22065,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":40408.0,"raw_peak_contact_force":315.46849,"tcp_end":[0.58153,0.16902,0.3562],"tcp_start":[0.51377,-0.02638,0.29087],"tcp_to_object_dist_end":0.01701,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":542.0,"n_steps_budget":1000.0,"object_pos_end":[0.60057,0.17896,0.28145],"object_pos_start":[0.59002,0.16088,0.34392],"object_to_goal_dist_end":0.03701,"object_to_goal_dist_start":0.09947,"object_z_max":0.34392,"peak_contact_force":384.58779,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":22590.0,"raw_peak_contact_force":825.80272,"tcp_end":[0.58992,0.18758,0.29359],"tcp_start":[0.58153,0.16902,0.3562],"tcp_to_object_dist_end":0.01831,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.59495,0.18534,0.28334],"object_pos_start":[0.60057,0.17896,0.28145],"object_to_goal_dist_end":0.0362,"object_to_goal_dist_start":0.03701,"object_z_max":0.2832,"peak_contact_force":0.66326,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2740.0,"raw_peak_contact_force":91.38649,"tcp_end":[0.59026,0.18696,0.3204],"tcp_start":[0.58992,0.18758,0.29359],"tcp_to_object_dist_end":0.03739,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":542.0,"n_steps_budget":600.0,"object_pos_end":[0.57961,0.18278,0.41458],"object_pos_start":[0.59495,0.18534,0.28334],"object_to_goal_dist_end":0.16669,"object_to_goal_dist_start":0.0362,"object_z_max":0.41434,"peak_contact_force":0.50408,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":542.0,"raw_peak_contact_force":0.87471,"tcp_end":[0.59187,0.18621,0.4551],"tcp_start":[0.59026,0.18696,0.3204],"tcp_to_object_dist_end":0.04248,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```