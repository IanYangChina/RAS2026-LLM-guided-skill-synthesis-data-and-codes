## Search State

- **Seed**: 3
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
- Frozen realised-scene SHA-256: `5ce27bcdb8582e1d517b17df0f9c2ad7b05701113a75707627744a889253e6a7`
- Frozen object start: [0.45856491671436245, -0.02631894934039003, 0.03]
- Frozen task target: [0.6301274465206397, 0.20821620360643678, 0.11411929633605987]
- Goal object position: (0.6301274465206397, 0.20821620360643678, 0.11411929633605987)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.6301274465206397, 0.20821620360643678, 0.11411929633605987)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.45856491671436245, -0.02631894934039003, 0.03)
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
  frozen_object_start: [0.4586, -0.0263, 0.03]
  frozen_task_target: [0.6301, 0.2082, 0.1141]
  frozen_object_starts: {'grasp_target': [0.45856491671436245, -0.02631894934039003, 0.03]}
  frozen_targets: {'place_target': [0.6301274465206397, 0.20821620360643678, 0.11411929633605987]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: 5ce27bcdb8582e1d517b17df0f9c2ad7b05701113a75707627744a889253e6a7

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
| `object` | offset from object initial position (0.45856491671436245, -0.02631894934039003, 0.03) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.6301274465206397, 0.20821620360643678, 0.11411929633605987) | final destination targets |
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

## Current Skill (Q=-0.019) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: reach_object
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.06
  weight: 0.3
- id: lift_object
  anchor: object
  target_entity: object
  offset:
  - 0.0
  - 0.0
  - 0.1
  weight: 0.3
- id: reach_goal
  target_entity: object
  metric: goal_progress
  weight: 0.4
phases:
- id: approach_1
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
    orientation:
      mode: keep_current
  parameters:
    approach_z:
      type: scalar
      range:
      - 0.08
      - 0.16
      default: 0.12
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: reach_object
- id: descend_1
  type: descend
  generator: linear_cartesian
  control: force_threshold_switch
  termination: force_exceeded
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.08
    orientation:
      mode: keep_current
  parameters:
    contact_force_threshold:
      type: scalar
      range:
      - 3.0
      - 12.0
      default: 8.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    descend_speed:
      type: scalar
      range:
      - 0.02
      - 0.08
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
    grasp_offset_z:
      type: scalar
      range:
      - 0.06
      - 0.12
      default: 0.08
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: reach_object
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
    - 0.02
    orientation:
      mode: keep_current
  parameters:
    descend_grasp_speed:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
    grasp_approach_z:
      type: scalar
      range:
      - 0.0
      - 0.04
      default: 0.02
      binds_to:
      - path: target.offset.z
        mode: replace
    grasp_pose_tol:
      type: scalar
      range:
      - 0.002
      - 0.01
      default: 0.005
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  guards:
  - id: descent_force_guard
    when: during_phase
    predicate: force_below
    threshold: 15.0
    on_failure: abort
  subtask_id: reach_object
- id: grasp_1
  type: grasp
  control: impedance_control
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
    grasp_time:
      type: scalar
      range:
      - 1.0
      - 4.0
      default: 3.0
      binds_to:
      - path: duration.max_time
        mode: replace
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
    - 0.0
    offset_along_axis:
      distance: 0.12
      axis: world_z
      mode: add_to_offset
      sign: positive
    orientation:
      mode: keep_current
  parameters:
    lift_distance:
      type: scalar
      range:
      - 0.08
      - 0.18
      default: 0.12
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
  guards:
  - id: lift_check
    when: after_phase
    predicate: object_lifted
    threshold: 0.02
    on_failure: abort
  subtask_id: lift_object
- id: move_to_goal
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
    - 0.08
    orientation:
      mode: keep_current
  parameters:
    transport_pose_tol:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.03
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
    transport_speed:
      type: scalar
      range:
      - 0.02
      - 0.12
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
    transport_z:
      type: scalar
      range:
      - 0.05
      - 0.15
      default: 0.08
      binds_to:
      - path: target.offset.z
        mode: replace
  guards:
  - id: transport_lift_check
    when: during_phase
    predicate: object_lifted
    threshold: 0.03
    on_failure: abort
  subtask_id: reach_goal
- id: descend_place
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.0
    orientation:
      mode: keep_current
  parameters:
    place_pose_tol:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.02
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
    place_speed:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
    place_z:
      type: scalar
      range:
      - -0.01
      - 0.02
      default: 0.0
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: reach_goal
- id: release_1
  type: release
  control: impedance_control
  termination: time_limit
  end_effector_action: open
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.12]
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_z: status=consumed; consumers=target.offset.z (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.08]
  - orientation: mode=keep_current
  - parameter_bindings:
    - contact_force_threshold: status=consumed; consumers=termination.force_threshold (replace)
    - descend_speed: status=consumed; consumers=generator.speed (replace)
    - grasp_offset_z: status=consumed; consumers=target.offset.z (replace)
- **descend_to_grasp** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.02]
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_grasp_speed: status=consumed; consumers=generator.speed (replace)
    - grasp_approach_z: status=consumed; consumers=target.offset.z (replace)
    - grasp_pose_tol: status=consumed; consumers=termination.pose_tolerance (replace)
  - guards:
    - id=descent_force_guard, when=during_phase, predicate=force_below, on_failure=abort, threshold=15.0
- **grasp_1** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings:
    - grasp_time: status=consumed; consumers=duration.max_time (replace)
- **lift_1** (`lift`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.12, mode=add_to_offset, sign=positive}
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
  - guards:
    - id=lift_check, when=after_phase, predicate=object_lifted, on_failure=abort, threshold=0.02
- **move_to_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.08]
  - orientation: mode=keep_current
  - parameter_bindings:
    - transport_pose_tol: status=consumed; consumers=termination.pose_tolerance (replace)
    - transport_speed: status=consumed; consumers=generator.speed (replace)
    - transport_z: status=consumed; consumers=target.offset.z (replace)
  - guards:
    - id=transport_lift_check, when=during_phase, predicate=object_lifted, on_failure=abort, threshold=0.03
- **descend_place** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - place_pose_tol: status=consumed; consumers=termination.pose_tolerance (replace)
    - place_speed: status=consumed; consumers=generator.speed (replace)
    - place_z: status=consumed; consumers=target.offset.z (replace)
- **release_1** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none

## Design Metrics

- **Composite score**: -0.019
- **task_score** (E): 0.541
- **fitness_score**: 0.744  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.167
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.930

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1430 |
| descend_1 | 1.00 | 1.00 | 0.0017 |
| descend_to_grasp | 1.00 | 1.00 | 0.1204 |
| grasp_1 | 1.00 | 1.00 | 0.0120 |
| lift_1 | 1.00 | 1.00 | 0.1193 |
| move_to_goal | 0.67 | 0.00 | 0.1910 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.507, 0.002, 0.164) | (0.511, 0.002, 0.030)→(0.511, 0.002, 0.026) | 0.244→0.246 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / force_exceeded | (0.507, 0.002, 0.164)→(0.506, 0.002, 0.162) | (0.511, 0.002, 0.026)→(0.511, 0.002, 0.026) | 0.246→0.246 | 1.00 / 4.000 | 81.142 | 0.123 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.506, 0.002, 0.162)→(0.506, 0.002, 0.042) | (0.511, 0.002, 0.026)→(0.511, 0.002, 0.026) | 0.246→0.246 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.506, 0.002, 0.042)→(0.498, 0.002, 0.033) | (0.511, 0.002, 0.026)→(0.511, 0.002, 0.026) | 0.246→0.246 | 1.00 / 42.333 | 0.137 | 0.189 |
| lift_1 | lift | 1.00 / step_budget | (0.498, 0.002, 0.033)→(0.494, 0.002, 0.152) | (0.511, 0.002, 0.026)→(0.509, 0.002, 0.132) | 0.246→0.219 | 1.00 / 23.667 | 0.119 | 0.604 |
| move_to_goal | approach | 0.67 / step_budget | (0.494, 0.002, 0.152)→(0.599, 0.148, 0.209) | (0.509, 0.002, 0.132)→(0.609, 0.158, 0.053) | 0.219→0.098 | 0.00 / 0.000 | 0.000 | 0.280 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.708
- phase_score: 0.547
- phase_breakdown.lift_object_score: 0.514
- phase_breakdown.reach_object_score: 0.383
- phase_breakdown.reach_goal_score: 0.694
- grasp_place_fitness: 0.829

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.829
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.708
- **Median Q (composite search score)**: -0.021
- **K-run variance**: 0.0048
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.300


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `a4a71a7b2980790489e8194d1356bdee33fb951291c2e0792659ad3d3b3dc711`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `8a78b0f0015ebaf8c4b14c8fbc8142d9b66e4b4efca10f362859101c0ae207df`; realized-scene SHA-256: `5ce27bcdb8582e1d517b17df0f9c2ad7b05701113a75707627744a889253e6a7`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.45856,-0.02632,0.03]},{"name":"goal","value":[0.63013,0.20822,0.11412]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.45856,-0.02632,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.63013,0.20822,0.11412]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.55682,"average_solve_count":176.0,"average_success_count":176.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_z":0.11927,"descend_1.contact_force_threshold":9.10027,"descend_1.descend_speed":0.06432,"descend_1.grasp_offset_z":0.08935,"descend_place.place_pose_tol":0.0196,"descend_place.place_speed":0.03786,"descend_place.place_z":0.00458,"descend_to_grasp.descend_grasp_speed":0.03848,"descend_to_grasp.grasp_approach_z":0.01896,"descend_to_grasp.grasp_pose_tol":0.0067,"grasp_1.grasp_time":2.3348,"lift_1.lift_distance":0.11292,"move_to_goal.transport_pose_tol":0.01563,"move_to_goal.transport_speed":0.09322,"move_to_goal.transport_z":0.11267},"optimized_scores":{"best_composite_score":-0.02103,"best_fitness_score":0.7423,"best_task_score":0.54875},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":123.0,"contact_point_centroid":[0.45588,-0.02524,-0.00111],"force_p95":0.35734,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.44672,"mean_force":0.05742,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4455,-0.02563,0.04456]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10362.0,"contact_point_centroid":[0.44565,-0.00657,0.09173],"force_p95":0.0953,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28275,"mean_force":0.06256,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4431,-0.02552,0.08951]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10629.0,"contact_point_centroid":[0.51056,0.07354,0.16866],"force_p95":0.12701,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27475,"mean_force":0.08125,"phase_index":5.0,"phase_name":"move_to_goal","phase_type":"approach","tcp_position_centroid":[0.50438,0.05483,0.16765]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10883.0,"contact_point_centroid":[0.44533,-0.04447,0.09004],"force_p95":0.09865,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27472,"mean_force":0.06039,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44309,-0.02552,0.08818]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11867.0,"contact_point_centroid":[0.51406,0.04086,0.16981],"force_p95":0.10075,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2401,"mean_force":0.0735,"phase_index":5.0,"phase_name":"move_to_goal","phase_type":"approach","tcp_position_centroid":[0.50802,0.05937,0.16915]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45857,-0.02625,-0.00205],"force_p95":0.13899,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18727,"mean_force":0.12706,"phase_index":3.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4479,-0.02571,0.04381]},{"body_a":"world","body_b":"grasp_target","contact_count":1732.0,"contact_point_centroid":[0.45856,-0.02632,-0.00192],"force_p95":0.13411,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12291,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.47919,-0.0115,0.22968]},{"body_a":"world","body_b":"grasp_target","contact_count":72.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.45834,-0.02382,0.15699]},{"body_a":"world","body_b":"grasp_target","contact_count":2072.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":2.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.45448,-0.02483,0.10148]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4836.0,"contact_point_centroid":[0.44684,-0.00645,0.04509],"force_p95":0.06823,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10193,"mean_force":0.04491,"phase_index":3.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44683,-0.02567,0.04278]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5153.0,"contact_point_centroid":[0.44669,-0.04489,0.0446],"force_p95":0.06695,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08392,"mean_force":0.04289,"phase_index":3.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44683,-0.02567,0.04279]}],"total_contact_groups":11},"final_pose_error":0.07544,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.60154,0.14268,0.05943],"final_tcp_position":[0.58429,0.15441,0.20044],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":81.14225,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":434.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1732.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.45903,-0.02371,0.15867],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13268,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":18.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":81.14225,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":72.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.45778,-0.02388,0.1551],"tcp_start":[0.45903,-0.02371,0.15867],"tcp_to_object_dist_end":0.12911,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":518.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2072.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.45417,-0.02594,0.04991],"tcp_start":[0.45778,-0.02388,0.1551],"tcp_to_object_dist_end":0.0243,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45849,-0.02583,0.02579],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30338,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.13689,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11789.0,"raw_peak_contact_force":0.18727,"tcp_end":[0.44681,-0.02567,0.04276],"tcp_start":[0.45417,-0.02594,0.04991],"tcp_to_object_dist_end":0.0206,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":29.0,"n_steps":633.0,"n_steps_budget":720.0,"object_pos_end":[0.4563,-0.02547,0.12082],"object_pos_start":[0.45849,-0.02583,0.02579],"object_to_goal_dist_end":0.29133,"object_to_goal_dist_start":0.30338,"object_z_max":0.12071,"peak_contact_force":0.08594,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":21368.0,"raw_peak_contact_force":0.44672,"subtask_id":"lift_object","tcp_end":[0.4431,-0.02551,0.14466],"tcp_start":[0.44681,-0.02567,0.04276],"tcp_to_object_dist_end":0.02725,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.60154,0.14268,0.05943],"object_pos_start":[0.4563,-0.02547,0.12082],"object_to_goal_dist_end":0.09002,"object_to_goal_dist_start":0.29133,"object_z_max":0.16421,"peak_contact_force":0.0,"phase_name":"move_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":22496.0,"raw_peak_contact_force":0.27475,"subtask_id":"reach_goal","tcp_end":[0.58429,0.15441,0.20044],"tcp_start":[0.4431,-0.02551,0.14466],"tcp_to_object_dist_end":0.14254,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `aa6ec658384c70fac6b4eb656cc8c53536c3d5c760368ab2b384dccf294e2c48`; realized-scene SHA-256: `1959b3932a54fd3d3850620783d44a63a35b8fa059f78d939fdbdef5fbfc64e8`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.54431,0.00113,0.03]},{"name":"goal","value":[0.64762,0.15808,0.1911]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.54431,0.00113,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.64762,0.15808,0.1911]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.02759,"average_solve_count":290.0,"average_success_count":290.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_z":0.14504,"descend_1.contact_force_threshold":5.16071,"descend_1.descend_speed":0.03401,"descend_1.grasp_offset_z":0.08842,"descend_place.place_pose_tol":0.01301,"descend_place.place_speed":0.04094,"descend_place.place_z":0.00849,"descend_to_grasp.descend_grasp_speed":0.0289,"descend_to_grasp.grasp_approach_z":0.00201,"descend_to_grasp.grasp_pose_tol":0.00748,"grasp_1.grasp_time":1.63304,"lift_1.lift_distance":0.14312,"move_to_goal.transport_pose_tol":0.04998,"move_to_goal.transport_speed":0.03661,"move_to_goal.transport_z":0.07762},"optimized_scores":{"best_composite_score":-0.10317,"best_fitness_score":0.66016,"best_task_score":0.36625},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":142.0,"contact_point_centroid":[0.54127,0.00071,-0.0011],"force_p95":0.5582,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.77351,"mean_force":0.10384,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52837,0.00083,0.02463]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11532.0,"contact_point_centroid":[0.52863,-0.01795,0.08188],"force_p95":0.11978,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33886,"mean_force":0.0727,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52566,0.00079,0.08107]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11550.0,"contact_point_centroid":[0.52912,0.01953,0.08042],"force_p95":0.12087,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32259,"mean_force":0.07309,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.5257,0.00079,0.07941]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1063.0,"contact_point_centroid":[0.54788,0.00966,0.16536],"force_p95":0.18899,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31007,"mean_force":0.12157,"phase_index":5.0,"phase_name":"move_to_goal","phase_type":"approach","tcp_position_centroid":[0.54643,0.02794,0.16971]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1427.0,"contact_point_centroid":[0.55351,0.05225,0.1695],"force_p95":0.184,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26971,"mean_force":0.11069,"phase_index":5.0,"phase_name":"move_to_goal","phase_type":"approach","tcp_position_centroid":[0.5517,0.03474,0.17424]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54429,0.00098,-0.00203],"force_p95":0.1316,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.16028,"mean_force":0.12528,"phase_index":3.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.5313,0.00089,0.02439]},{"body_a":"world","body_b":"grasp_target","contact_count":1664.0,"contact_point_centroid":[0.54431,0.00113,-0.00192],"force_p95":0.13454,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12292,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51698,0.00047,0.2399]},{"body_a":"world","body_b":"grasp_target","contact_count":20.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.53631,0.00097,0.18055]},{"body_a":"world","body_b":"grasp_target","contact_count":2508.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":2.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.53578,0.00098,0.10467]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4115.0,"contact_point_centroid":[0.53099,-0.01833,0.02565],"force_p95":0.07601,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10926,"mean_force":0.0517,"phase_index":3.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53004,0.00087,0.02295]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4878.0,"contact_point_centroid":[0.53094,0.01995,0.02477],"force_p95":0.068,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09663,"mean_force":0.0448,"phase_index":3.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53004,0.00087,0.02295]}],"total_contact_groups":11},"final_pose_error":0.04946,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.62552,0.1586,0.04207],"final_tcp_position":[0.6239,0.12709,0.23836],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":81.14225,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":417.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1664.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.53647,0.00097,0.18097],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.15515,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":5.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":81.14225,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":20.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.53611,0.00096,0.17996],"tcp_start":[0.53647,0.00097,0.18097],"tcp_to_object_dist_end":0.15416,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":627.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2508.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.53868,0.00103,0.03291],"tcp_start":[0.53611,0.00096,0.17996],"tcp_to_object_dist_end":0.0089,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54415,0.00073,0.02588],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25053,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.1295,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10793.0,"raw_peak_contact_force":0.16028,"tcp_end":[0.53001,0.00087,0.02291],"tcp_start":[0.53868,0.00103,0.03291],"tcp_to_object_dist_end":0.01445,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":20.0,"n_steps":813.0,"n_steps_budget":900.0,"object_pos_end":[0.54259,0.00079,0.13642],"object_pos_start":[0.54415,0.00073,0.02588],"object_to_goal_dist_end":0.19689,"object_to_goal_dist_start":0.25053,"object_z_max":0.13635,"peak_contact_force":0.155,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":23224.0,"raw_peak_contact_force":0.77351,"subtask_id":"lift_object","tcp_end":[0.52601,0.00081,0.15337],"tcp_start":[0.53001,0.00087,0.02291],"tcp_to_object_dist_end":0.02371,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":223.0,"n_steps_budget":1000.0,"object_pos_end":[0.62552,0.1586,0.04207],"object_pos_start":[0.54259,0.00079,0.13642],"object_to_goal_dist_end":0.15067,"object_to_goal_dist_start":0.19689,"object_z_max":0.17181,"peak_contact_force":0.0,"phase_name":"move_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2490.0,"raw_peak_contact_force":0.31007,"subtask_id":"reach_goal","tcp_end":[0.6239,0.12709,0.23836],"tcp_start":[0.52601,0.00081,0.15337],"tcp_to_object_dist_end":0.19881,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `e1209649252ffcf03853fe0727696e22a1eda11729c6c1ae21659980557d7e98`; realized-scene SHA-256: `e32d7866764afb23ec7c7faebb4bcca0aa39fbf2f1ab61f3c9c527b297153af9`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5305,0.03079,0.03]},{"name":"goal","value":[0.60153,0.17858,0.10809]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.5305,0.03079,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.60153,0.17858,0.10809]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.34426,"average_solve_count":183.0,"average_success_count":183.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_z":0.11442,"descend_1.contact_force_threshold":5.76442,"descend_1.descend_speed":0.03704,"descend_1.grasp_offset_z":0.0969,"descend_place.place_pose_tol":0.03075,"descend_place.place_speed":0.03689,"descend_place.place_z":0.00896,"descend_to_grasp.descend_grasp_speed":0.02905,"descend_to_grasp.grasp_approach_z":0.01224,"descend_to_grasp.grasp_pose_tol":0.00688,"grasp_1.grasp_time":2.42453,"lift_1.lift_distance":0.13773,"move_to_goal.transport_pose_tol":0.02375,"move_to_goal.transport_speed":0.09202,"move_to_goal.transport_z":0.09337},"optimized_scores":{"best_composite_score":0.06615,"best_fitness_score":0.82948,"best_task_score":0.70781},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":144.0,"contact_point_centroid":[0.52734,0.02892,-0.00117],"force_p95":0.43179,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.59112,"mean_force":0.08403,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51512,0.02956,0.03461]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11033.0,"contact_point_centroid":[0.51582,0.01058,0.08975],"force_p95":0.10808,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32759,"mean_force":0.07138,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51253,0.02939,0.0879]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11466.0,"contact_point_centroid":[0.51587,0.04819,0.08758],"force_p95":0.10605,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31996,"mean_force":0.06936,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51256,0.02939,0.08591]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2657.0,"contact_point_centroid":[0.54574,0.06169,0.16429],"force_p95":0.16027,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25566,"mean_force":0.10999,"phase_index":5.0,"phase_name":"move_to_goal","phase_type":"approach","tcp_position_centroid":[0.54058,0.07989,0.1677]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53053,0.03056,-0.0021],"force_p95":0.15181,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22066,"mean_force":0.13044,"phase_index":3.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51797,0.02975,0.03419]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2794.0,"contact_point_centroid":[0.54736,0.10068,0.16472],"force_p95":0.1386,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19679,"mean_force":0.10349,"phase_index":5.0,"phase_name":"move_to_goal","phase_type":"approach","tcp_position_centroid":[0.54221,0.08266,0.16841]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4078.0,"contact_point_centroid":[0.51753,0.01047,0.03558],"force_p95":0.07953,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1432,"mean_force":0.05186,"phase_index":3.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51676,0.02967,0.03281]},{"body_a":"world","body_b":"grasp_target","contact_count":1964.0,"contact_point_centroid":[0.5305,0.03079,-0.00193],"force_p95":0.13308,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12287,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51089,0.01372,0.22534]},{"body_a":"world","body_b":"grasp_target","contact_count":2044.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":2.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.52295,0.02903,0.0952]},{"body_a":"world","body_b":"grasp_target","contact_count":4.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12262,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12262,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52419,0.02801,0.15147]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4965.0,"contact_point_centroid":[0.51749,0.0488,0.03462],"force_p95":0.07206,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08288,"mean_force":0.04469,"phase_index":3.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51676,0.02967,0.03282]}],"total_contact_groups":11},"final_pose_error":0.02363,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.59942,0.17195,0.05672],"final_tcp_position":[0.58933,0.16244,0.18926],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":81.14225,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":492.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1964.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.52419,0.02801,0.15147],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12564,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":81.14225,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4.0,"raw_peak_contact_force":0.12262,"subtask_id":"reach_object","tcp_end":[0.52411,0.02804,0.15123],"tcp_start":[0.52419,0.02801,0.15147],"tcp_to_object_dist_end":0.1254,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":511.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2044.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.52506,0.03023,0.04227],"tcp_start":[0.52411,0.02804,0.15123],"tcp_to_object_dist_end":0.01715,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53041,0.02971,0.02566],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18443,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.14582,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10843.0,"raw_peak_contact_force":0.22066,"tcp_end":[0.51673,0.02967,0.03278],"tcp_start":[0.52506,0.03023,0.04227],"tcp_to_object_dist_end":0.01542,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":783.0,"n_steps_budget":870.0,"object_pos_end":[0.527,0.02957,0.14003],"object_pos_start":[0.53041,0.02971,0.02566],"object_to_goal_dist_end":0.16965,"object_to_goal_dist_start":0.18443,"object_z_max":0.13992,"peak_contact_force":0.11674,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":22643.0,"raw_peak_contact_force":0.59112,"subtask_id":"lift_object","tcp_end":[0.51283,0.02942,0.15812],"tcp_start":[0.51673,0.02967,0.03278],"tcp_to_object_dist_end":0.02298,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":390.0,"n_steps_budget":1000.0,"object_pos_end":[0.59942,0.17195,0.05672],"object_pos_start":[0.527,0.02957,0.14003],"object_to_goal_dist_end":0.05184,"object_to_goal_dist_start":0.16965,"object_z_max":0.15744,"peak_contact_force":0.0,"phase_name":"move_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":5451.0,"raw_peak_contact_force":0.25566,"subtask_id":"reach_goal","tcp_end":[0.58933,0.16244,0.18926],"tcp_start":[0.51283,0.02942,0.15812],"tcp_to_object_dist_end":0.13326,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```