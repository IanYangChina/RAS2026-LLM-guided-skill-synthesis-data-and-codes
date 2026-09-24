## Search State

- **Seed**: 3
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

## Current Skill (Q=-0.069) — your mutation base

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
    - 0.03
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
      - 0.01
      - 0.05
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
    bilateral_grasp_threshold:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.05
      binds_to:
      - path: guards.grasp_check.threshold
        mode: replace
    grasp_time:
      type: scalar
      range:
      - 1.0
      - 4.0
      default: 3.0
      binds_to:
      - path: duration.max_time
        mode: replace
  guards:
  - id: grasp_check
    when: during_phase
    predicate: bilateral_grasp
    threshold: 0.05
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: repeat
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
    - 0.15
    orientation:
      mode: keep_current
  parameters:
    transport_speed:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.06
      binds_to:
      - path: generator.speed
        mode: replace
    transport_z:
      type: scalar
      range:
      - 0.1
      - 0.2
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
  guards:
  - id: transport_lift_check
    when: during_phase
    predicate: object_lifted
    threshold: 0.06
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
    - 0.01
    orientation:
      mode: keep_current
  parameters:
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
      - 0.0
      - 0.02
      default: 0.01
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
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.03]
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
    - bilateral_grasp_threshold: status=consumed; consumers=guards.grasp_check.threshold (replace)
    - grasp_time: status=consumed; consumers=duration.max_time (replace)
  - guards:
    - id=grasp_check, when=during_phase, predicate=bilateral_grasp, on_failure=retry, threshold=0.05
  - retries: max_attempts=2, strategy=repeat
- **lift_1** (`lift`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.12, mode=add_to_offset, sign=positive}
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
  - guards:
    - id=lift_check, when=after_phase, predicate=object_lifted, on_failure=abort, threshold=0.02
- **move_to_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.15]
  - orientation: mode=keep_current
  - parameter_bindings:
    - transport_speed: status=consumed; consumers=generator.speed (replace)
    - transport_z: status=consumed; consumers=target.offset.z (replace)
  - guards:
    - id=transport_lift_check, when=during_phase, predicate=object_lifted, on_failure=abort, threshold=0.06
- **descend_place** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.01]
  - orientation: mode=keep_current
  - parameter_bindings:
    - place_speed: status=consumed; consumers=generator.speed (replace)
    - place_z: status=consumed; consumers=target.offset.z (replace)
- **release_1** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none

## Design Metrics

- **Composite score**: -0.069
- **task_score** (E): 0.433
- **fitness_score**: 0.686  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.125
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.880

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1393 |
| descend_1 | 1.00 | 1.00 | 0.0015 |
| descend_to_grasp | 1.00 | 1.00 | 0.1183 |
| grasp_1 | 0.00 | 1.00 | 0.0000 |
| lift_1 | 1.00 | 1.00 | 0.1111 |
| move_to_goal | 0.00 | 1.00 | 0.0844 |
| descend_place | 0.33 | 0.67 | 0.1039 |
| release_1 | 1.00 | 1.00 | 0.0221 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.507, 0.002, 0.167) | (0.511, 0.002, 0.030)→(0.511, 0.002, 0.026) | 0.244→0.246 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / force_exceeded | (0.507, 0.002, 0.167)→(0.506, 0.002, 0.166) | (0.511, 0.002, 0.026)→(0.511, 0.002, 0.026) | 0.246→0.246 | 1.00 / 4.000 | 81.142 | 0.123 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.506, 0.002, 0.166)→(0.506, 0.002, 0.048) | (0.511, 0.002, 0.026)→(0.511, 0.002, 0.026) | 0.246→0.246 | 1.00 / 4.000 | 5.721 | 0.123 |
| grasp_1 | grasp | 0.00 / guard_failure | (0.501, 0.002, 0.042)→(0.501, 0.002, 0.042) | (0.511, 0.002, 0.026)→(0.511, 0.002, 0.026) | 0.246→0.246 | 1.00 / 44.000 | 0.135 | 0.172 |
| lift_1 | lift | 1.00 / step_budget | (0.501, 0.002, 0.042)→(0.497, 0.002, 0.153) | (0.511, 0.002, 0.026)→(0.510, 0.002, 0.131) | 0.246→0.218 | 1.00 / 27.000 | 0.094 | 0.490 |
| move_to_goal | approach | 0.00 / step_budget | (0.497, 0.002, 0.153)→(0.538, 0.063, 0.188) | (0.510, 0.002, 0.131)→(0.544, 0.063, 0.159) | 0.218→0.150 | 1.00 / 25.000 | 0.093 | 0.169 |
| descend_place | descend | 0.33 / step_budget | (0.538, 0.063, 0.188)→(0.591, 0.140, 0.149) | (0.544, 0.063, 0.159)→(0.604, 0.140, 0.049) | 0.150→0.101 | 0.67 / 6.333 | 0.164 | 0.533 |
| release_1 | release | 1.00 / step_budget | (0.591, 0.140, 0.149)→(0.584, 0.139, 0.170) | (0.604, 0.140, 0.049)→(0.600, 0.143, 0.019) | 0.101→0.130 | 1.00 / 4.000 | 0.139 | 0.963 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.564
- phase_score: 0.620
- phase_breakdown.lift_object_score: 0.661
- phase_breakdown.reach_object_score: 0.420
- phase_breakdown.reach_goal_score: 0.738
- grasp_place_fitness: 0.753

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.753
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.564
- **Median Q (composite search score)**: -0.067
- **K-run variance**: 0.0030
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.295


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.10484,"average_solve_count":248.0,"average_success_count":248.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_z":0.12845,"descend_1.contact_force_threshold":6.66967,"descend_1.descend_speed":0.04356,"descend_1.grasp_offset_z":0.1105,"descend_place.place_speed":0.04984,"descend_place.place_z":0.01303,"descend_to_grasp.descend_grasp_speed":0.02453,"descend_to_grasp.grasp_approach_z":0.01771,"descend_to_grasp.grasp_pose_tol":0.00575,"grasp_1.bilateral_grasp_threshold":0.09186,"grasp_1.grasp_time":2.9572,"lift_1.lift_distance":0.1257,"move_to_goal.transport_speed":0.07624,"move_to_goal.transport_z":0.10833},"optimized_scores":{"best_composite_score":-0.067,"best_fitness_score":0.688,"best_task_score":0.43625},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":86.0,"contact_point_centroid":[0.59316,0.13672,-0.00618],"force_p95":1.12789,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.24474,"mean_force":0.57284,"phase_index":6.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.57864,0.14888,0.14107]},{"body_a":"world","body_b":"grasp_target","contact_count":126.0,"contact_point_centroid":[0.45578,-0.02546,-0.00111],"force_p95":0.31771,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.44912,"mean_force":0.05558,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44833,-0.02576,0.04477]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.60072,0.13748,-0.00242],"force_p95":0.12618,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.33544,"mean_force":0.12003,"phase_index":7.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57478,0.14845,0.1424]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13759.0,"contact_point_centroid":[0.44721,-0.04472,0.09931],"force_p95":0.08381,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29335,"mean_force":0.05459,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44588,-0.02565,0.09746]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":13556.0,"contact_point_centroid":[0.44724,-0.0066,0.10024],"force_p95":0.08391,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2924,"mean_force":0.055,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44589,-0.02565,0.09809]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8671.0,"contact_point_centroid":[0.55158,0.12693,0.15419],"force_p95":0.1215,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20458,"mean_force":0.09552,"phase_index":6.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.54615,0.10862,0.15738]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14036.0,"contact_point_centroid":[0.48654,0.00541,0.16714],"force_p95":0.09307,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19905,"mean_force":0.06687,"phase_index":5.0,"phase_name":"move_to_goal","phase_type":"approach","tcp_position_centroid":[0.48181,0.02412,0.16651]},{"body_a":"world","body_b":"grasp_target","contact_count":1804.0,"contact_point_centroid":[0.45856,-0.02624,-0.00205],"force_p95":0.13509,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.16793,"mean_force":0.12662,"phase_index":3.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.45012,-0.02583,0.04341]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":13429.0,"contact_point_centroid":[0.4875,0.04398,0.16724],"force_p95":0.09435,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16537,"mean_force":0.06962,"phase_index":5.0,"phase_name":"move_to_goal","phase_type":"approach","tcp_position_centroid":[0.48268,0.02524,0.16679]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9039.0,"contact_point_centroid":[0.55194,0.09079,0.15426],"force_p95":0.11987,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15415,"mean_force":0.09089,"phase_index":6.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.54648,0.10903,0.15721]},{"body_a":"world","body_b":"grasp_target","contact_count":1636.0,"contact_point_centroid":[0.45856,-0.02632,-0.00192],"force_p95":0.13462,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12292,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.47946,-0.01137,0.23447]},{"body_a":"world","body_b":"grasp_target","contact_count":56.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.45869,-0.02365,0.16662]},{"body_a":"world","body_b":"grasp_target","contact_count":2756.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":2.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.4546,-0.02478,0.10445]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5834.0,"contact_point_centroid":[0.44986,-0.00663,0.0449],"force_p95":0.06918,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11171,"mean_force":0.04499,"phase_index":3.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44968,-0.02581,0.04298]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5899.0,"contact_point_centroid":[0.44987,-0.04501,0.04485],"force_p95":0.06944,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08833,"mean_force":0.04502,"phase_index":3.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44968,-0.02581,0.04298]}],"total_contact_groups":15},"final_pose_error":0.07882,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.60073,0.13754,0.01602],"final_tcp_position":[0.57925,0.14958,0.1408],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":81.14225,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":410.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1636.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.45939,-0.02354,0.1679],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.14191,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":14.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":81.14225,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":56.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.45821,-0.02372,0.16516],"tcp_start":[0.45939,-0.02354,0.1679],"tcp_to_object_dist_end":0.13917,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":689.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2756.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.45417,-0.02598,0.04736],"tcp_start":[0.45821,-0.02372,0.16516],"tcp_to_object_dist_end":0.02179,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45848,-0.02595,0.02584],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30347,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.13339,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":13537.0,"raw_peak_contact_force":0.16793,"tcp_end":[0.44966,-0.02581,0.04296],"tcp_start":[0.44966,-0.02581,0.04296],"tcp_to_object_dist_end":0.01926,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":28.0,"n_steps":723.0,"n_steps_budget":810.0,"object_pos_end":[0.45896,-0.02567,0.13472],"object_pos_start":[0.45848,-0.02594,0.02585],"object_to_goal_dist_end":0.29056,"object_to_goal_dist_start":0.30345,"object_z_max":0.13461,"peak_contact_force":0.08626,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":27441.0,"raw_peak_contact_force":0.44912,"subtask_id":"lift_object","tcp_end":[0.44602,-0.02565,0.15764],"tcp_start":[0.44966,-0.02581,0.04296],"tcp_to_object_dist_end":0.02633,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":24.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52367,0.06992,0.14787],"object_pos_start":[0.45896,-0.02567,0.13472],"object_to_goal_dist_end":0.17776,"object_to_goal_dist_start":0.29056,"object_z_max":0.14786,"peak_contact_force":0.09444,"phase_name":"move_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":27465.0,"raw_peak_contact_force":0.19905,"subtask_id":"reach_goal","tcp_end":[0.51791,0.07,0.17826],"tcp_start":[0.44602,-0.02565,0.15764],"tcp_to_object_dist_end":0.03093,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.60025,0.14028,0.00537],"object_pos_start":[0.52367,0.06992,0.14787],"object_to_goal_dist_end":0.13166,"object_to_goal_dist_start":0.17776,"object_z_max":0.14787,"peak_contact_force":0.35847,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":17796.0,"raw_peak_contact_force":1.24474,"subtask_id":"reach_goal","tcp_end":[0.57925,0.14958,0.1408],"tcp_start":[0.51791,0.07,0.17826],"tcp_to_object_dist_end":0.13737,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.60073,0.13754,0.01602],"object_pos_start":[0.60025,0.14028,0.00537],"object_to_goal_dist_end":0.12443,"object_to_goal_dist_start":0.13166,"object_z_max":0.01642,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":800.0,"raw_peak_contact_force":0.33544,"tcp_end":[0.57303,0.14794,0.16239],"tcp_start":[0.57925,0.14958,0.1408],"tcp_to_object_dist_end":0.14934,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.86538,"average_solve_count":260.0,"average_success_count":260.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_z":0.12837,"descend_1.contact_force_threshold":11.70172,"descend_1.descend_speed":0.02246,"descend_1.grasp_offset_z":0.07125,"descend_place.place_speed":0.03111,"descend_place.place_z":0.00784,"descend_to_grasp.descend_grasp_speed":0.02182,"descend_to_grasp.grasp_approach_z":0.01835,"descend_to_grasp.grasp_pose_tol":0.00741,"grasp_1.bilateral_grasp_threshold":0.07815,"grasp_1.grasp_time":2.07485,"lift_1.lift_distance":0.12731,"move_to_goal.transport_speed":0.04422,"move_to_goal.transport_z":0.18694},"optimized_scores":{"best_composite_score":-0.1369,"best_fitness_score":0.6181,"best_task_score":0.2991},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":696.0,"contact_point_centroid":[0.62119,0.11961,-0.0035],"force_p95":0.8744,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.62788,"mean_force":0.19946,"phase_index":7.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.59467,0.09908,0.19392]},{"body_a":"world","body_b":"grasp_target","contact_count":145.0,"contact_point_centroid":[0.54162,0.0009,-0.00114],"force_p95":0.33655,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.52454,"mean_force":0.07214,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53192,0.00091,0.04468]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12417.0,"contact_point_centroid":[0.53062,0.01992,0.09679],"force_p95":0.09742,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3048,"mean_force":0.05968,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52932,0.00087,0.09483]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13222.0,"contact_point_centroid":[0.53066,-0.01808,0.09639],"force_p95":0.09213,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30065,"mean_force":0.05655,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.5293,0.00087,0.0947]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9171.0,"contact_point_centroid":[0.58043,0.05043,0.19119],"force_p95":0.11876,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20979,"mean_force":0.09189,"phase_index":6.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.57492,0.06876,0.19397]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9386.0,"contact_point_centroid":[0.58069,0.08739,0.1911],"force_p95":0.1144,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17499,"mean_force":0.08945,"phase_index":6.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.57519,0.06911,0.19395]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13730.0,"contact_point_centroid":[0.54555,0.00168,0.17986],"force_p95":0.09348,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15522,"mean_force":0.06825,"phase_index":5.0,"phase_name":"move_to_goal","phase_type":"approach","tcp_position_centroid":[0.54074,0.02043,0.17912]},{"body_a":"world","body_b":"grasp_target","contact_count":1804.0,"contact_point_centroid":[0.5443,0.0011,-0.00204],"force_p95":0.13082,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15067,"mean_force":0.12564,"phase_index":3.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53405,0.00095,0.04359]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":13821.0,"contact_point_centroid":[0.54559,0.0389,0.17972],"force_p95":0.0932,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14542,"mean_force":0.06782,"phase_index":5.0,"phase_name":"move_to_goal","phase_type":"approach","tcp_position_centroid":[0.54053,0.02014,0.17873]},{"body_a":"world","body_b":"grasp_target","contact_count":1848.0,"contact_point_centroid":[0.54431,0.00113,-0.00192],"force_p95":0.13354,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12289,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.5171,0.00048,0.23172]},{"body_a":"world","body_b":"grasp_target","contact_count":2020.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":2.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.53581,0.00098,0.10506]},{"body_a":"world","body_b":"grasp_target","contact_count":24.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12262,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12262,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.53651,0.00097,0.16409]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5848.0,"contact_point_centroid":[0.53376,-0.01824,0.04491],"force_p95":0.06823,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08825,"mean_force":0.045,"phase_index":3.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53356,0.00094,0.04301]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5869.0,"contact_point_centroid":[0.53374,0.02013,0.04489],"force_p95":0.06834,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08669,"mean_force":0.04504,"phase_index":3.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53356,0.00094,0.04301]}],"total_contact_groups":14},"final_pose_error":0.07612,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.62145,0.12016,0.01602],"final_tcp_position":[0.59906,0.09986,0.19222],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":81.14225,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":463.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1848.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.53673,0.00098,0.1646],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13879,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":6.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":81.14225,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":24.0,"raw_peak_contact_force":0.12262,"subtask_id":"reach_object","tcp_end":[0.53624,0.00097,0.16343],"tcp_start":[0.53673,0.00098,0.1646],"tcp_to_object_dist_end":0.13765,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":505.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2020.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.53867,0.00103,0.04917],"tcp_start":[0.53624,0.00097,0.16343],"tcp_to_object_dist_end":0.02382,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54421,0.001,0.02587],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25034,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.13015,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":13521.0,"raw_peak_contact_force":0.15067,"tcp_end":[0.53354,0.00094,0.04298],"tcp_start":[0.53354,0.00094,0.04298],"tcp_to_object_dist_end":0.02017,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":26.0,"n_steps":723.0,"n_steps_budget":810.0,"object_pos_end":[0.54192,0.00096,0.1345],"object_pos_start":[0.54421,0.00099,0.02588],"object_to_goal_dist_end":0.19765,"object_to_goal_dist_start":0.25034,"object_z_max":0.13439,"peak_contact_force":0.09396,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":25784.0,"raw_peak_contact_force":0.52454,"subtask_id":"lift_object","tcp_end":[0.52957,0.00088,0.1576],"tcp_start":[0.53354,0.00094,0.04298],"tcp_to_object_dist_end":0.02619,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":24.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.55884,0.03678,0.17147],"object_pos_start":[0.54192,0.00096,0.1345],"object_to_goal_dist_end":0.1516,"object_to_goal_dist_start":0.19765,"object_z_max":0.17143,"peak_contact_force":0.09388,"phase_name":"move_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":27551.0,"raw_peak_contact_force":0.15522,"subtask_id":"reach_goal","tcp_end":[0.55309,0.03677,0.20154],"tcp_start":[0.52957,0.00088,0.1576],"tcp_to_object_dist_end":0.03062,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.61195,0.10866,0.06551],"object_pos_start":[0.55884,0.03678,0.17147],"object_to_goal_dist_end":0.1396,"object_to_goal_dist_start":0.1516,"object_z_max":0.17147,"peak_contact_force":0.0,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":18557.0,"raw_peak_contact_force":0.20979,"subtask_id":"reach_goal","tcp_end":[0.59906,0.09986,0.19222],"tcp_start":[0.55309,0.03677,0.20154],"tcp_to_object_dist_end":0.12767,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.62145,0.12016,0.01602],"object_pos_start":[0.61195,0.10866,0.06551],"object_to_goal_dist_end":0.18105,"object_to_goal_dist_start":0.1396,"object_z_max":0.06551,"peak_contact_force":0.12273,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":696.0,"raw_peak_contact_force":1.62788,"tcp_end":[0.59363,0.09886,0.21329],"tcp_start":[0.59906,0.09986,0.19222],"tcp_to_object_dist_end":0.20036,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.86364,"average_solve_count":286.0,"average_success_count":286.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_z":0.13309,"descend_1.contact_force_threshold":6.56847,"descend_1.descend_speed":0.04616,"descend_1.grasp_offset_z":0.09514,"descend_place.place_speed":0.01596,"descend_place.place_z":0.0096,"descend_to_grasp.descend_grasp_speed":0.03073,"descend_to_grasp.grasp_approach_z":0.01791,"descend_to_grasp.grasp_pose_tol":0.00616,"grasp_1.bilateral_grasp_threshold":0.07761,"grasp_1.grasp_time":2.32149,"lift_1.lift_distance":0.11601,"move_to_goal.transport_speed":0.05937,"move_to_goal.transport_z":0.16897},"optimized_scores":{"best_composite_score":-0.00213,"best_fitness_score":0.75287,"best_task_score":0.56384},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":279.0,"contact_point_centroid":[0.58289,0.16763,-0.00382],"force_p95":0.72402,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.92604,"mean_force":0.24506,"phase_index":7.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.58689,0.16961,0.12257]},{"body_a":"world","body_b":"grasp_target","contact_count":147.0,"contact_point_centroid":[0.5279,0.02944,-0.00118],"force_p95":0.34247,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.49623,"mean_force":0.07303,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51853,0.0298,0.04291]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12168.0,"contact_point_centroid":[0.51679,0.04874,0.09022],"force_p95":0.09109,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31003,"mean_force":0.05647,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51596,0.02964,0.08827]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12503.0,"contact_point_centroid":[0.51693,0.01062,0.09122],"force_p95":0.08526,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29861,"mean_force":0.05472,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51595,0.02964,0.08938]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":591.0,"contact_point_centroid":[0.59756,0.1528,0.10587],"force_p95":0.11561,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22303,"mean_force":0.0832,"phase_index":7.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.59142,0.17108,0.10978]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":571.0,"contact_point_centroid":[0.59727,0.18933,0.10544],"force_p95":0.13144,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21908,"mean_force":0.08854,"phase_index":7.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.59134,0.17106,0.10967]},{"body_a":"world","body_b":"grasp_target","contact_count":1804.0,"contact_point_centroid":[0.53052,0.03067,-0.00209],"force_p95":0.14426,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19746,"mean_force":0.12968,"phase_index":3.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52065,0.02995,0.04172]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":14374.0,"contact_point_centroid":[0.53381,0.0774,0.1662],"force_p95":0.09768,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15241,"mean_force":0.06631,"phase_index":5.0,"phase_name":"move_to_goal","phase_type":"approach","tcp_position_centroid":[0.52921,0.05857,0.16493]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10673.0,"contact_point_centroid":[0.57273,0.10893,0.14399],"force_p95":0.11858,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14558,"mean_force":0.08585,"phase_index":6.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.56703,0.12745,0.14531]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14990.0,"contact_point_centroid":[0.53323,0.03962,0.16562],"force_p95":0.09413,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14066,"mean_force":0.06405,"phase_index":5.0,"phase_name":"move_to_goal","phase_type":"approach","tcp_position_centroid":[0.52909,0.05836,0.16475]},{"body_a":"world","body_b":"grasp_target","contact_count":1744.0,"contact_point_centroid":[0.5305,0.03079,-0.00192],"force_p95":0.13403,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12291,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51082,0.01354,0.23463]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11206.0,"contact_point_centroid":[0.57332,0.14675,0.14323],"force_p95":0.11529,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13598,"mean_force":0.08119,"phase_index":6.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.56755,0.12833,0.14467]},{"body_a":"world","body_b":"grasp_target","contact_count":4.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52404,0.0277,0.16999]},{"body_a":"world","body_b":"grasp_target","contact_count":2456.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":2.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.52295,0.02891,0.10612]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5819.0,"contact_point_centroid":[0.52037,0.01074,0.04309],"force_p95":0.0707,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11938,"mean_force":0.04499,"phase_index":3.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52017,0.02992,0.04115]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5935.0,"contact_point_centroid":[0.52034,0.04913,0.04301],"force_p95":0.07106,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07622,"mean_force":0.04499,"phase_index":3.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52017,0.02992,0.04116]}],"total_contact_groups":16},"final_pose_error":0.01145,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.57646,0.16995,0.02633],"final_tcp_position":[0.59354,0.17158,0.11342],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":81.14225,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":437.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1744.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.52404,0.0277,0.16999],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.14414,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":81.14225,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.52396,0.02774,0.16974],"tcp_start":[0.52404,0.0277,0.16999],"tcp_to_object_dist_end":0.14391,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":614.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":16.91803,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2456.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.52519,0.03025,0.04699],"tcp_start":[0.52396,0.02774,0.16974],"tcp_to_object_dist_end":0.02164,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53042,0.03016,0.02571],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18405,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.14098,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":13558.0,"raw_peak_contact_force":0.19746,"tcp_end":[0.52015,0.02992,0.04113],"tcp_start":[0.52015,0.02992,0.04113],"tcp_to_object_dist_end":0.01853,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":27.0,"n_steps":663.0,"n_steps_budget":750.0,"object_pos_end":[0.52894,0.02993,0.12416],"object_pos_start":[0.53042,0.03014,0.02572],"object_to_goal_dist_end":0.16621,"object_to_goal_dist_start":0.18405,"object_z_max":0.12404,"peak_contact_force":0.1025,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":24818.0,"raw_peak_contact_force":0.49623,"subtask_id":"lift_object","tcp_end":[0.51612,0.02966,0.14483],"tcp_start":[0.52015,0.02992,0.04113],"tcp_to_object_dist_end":0.02433,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":27.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54858,0.08132,0.15658],"object_pos_start":[0.52894,0.02993,0.12416],"object_to_goal_dist_end":0.12089,"object_to_goal_dist_start":0.16621,"object_z_max":0.15656,"peak_contact_force":0.09019,"phase_name":"move_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":29364.0,"raw_peak_contact_force":0.15241,"subtask_id":"reach_goal","tcp_end":[0.5423,0.08132,0.1846],"tcp_start":[0.51612,0.02966,0.14483],"tcp_to_object_dist_end":0.02872,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":15.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.59911,0.17151,0.07737],"object_pos_start":[0.54858,0.08132,0.15658],"object_to_goal_dist_end":0.03162,"object_to_goal_dist_start":0.12089,"object_z_max":0.15658,"peak_contact_force":0.13495,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":21879.0,"raw_peak_contact_force":0.14558,"subtask_id":"reach_goal","tcp_end":[0.59354,0.17158,0.11342],"tcp_start":[0.5423,0.08132,0.1846],"tcp_to_object_dist_end":0.03648,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.57646,0.16995,0.02633],"object_pos_start":[0.59911,0.17151,0.07737],"object_to_goal_dist_end":0.08595,"object_to_goal_dist_start":0.03162,"object_z_max":0.07737,"peak_contact_force":0.17189,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1441.0,"raw_peak_contact_force":0.92604,"tcp_end":[0.58675,0.16956,0.13422],"tcp_start":[0.59354,0.17158,0.11342],"tcp_to_object_dist_end":0.10838,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```