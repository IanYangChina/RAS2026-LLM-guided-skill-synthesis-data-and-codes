## Search State

- **Seed**: 3
- **Iteration**: 13 / 15

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

## Current Skill (Q=-0.022) — your mutation base

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

- **Composite score**: -0.022
- **task_score** (E): 0.462
- **fitness_score**: 0.705  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.153
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.880

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1463 |
| descend_1 | 1.00 | 1.00 | 0.0018 |
| descend_to_grasp | 1.00 | 1.00 | 0.1149 |
| grasp_1 | 0.00 | 1.00 | 0.0000 |
| lift_1 | 1.00 | 1.00 | 0.1127 |
| move_to_goal | 0.00 | 0.33 | 0.0862 |
| descend_place | 0.00 | 1.00 | 0.1175 |
| release_1 | 1.00 | 1.00 | 0.0230 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.507, 0.002, 0.160) | (0.511, 0.002, 0.030)→(0.511, 0.002, 0.026) | 0.244→0.246 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / force_exceeded | (0.507, 0.002, 0.160)→(0.506, 0.002, 0.159) | (0.511, 0.002, 0.026)→(0.511, 0.002, 0.026) | 0.246→0.246 | 1.00 / 4.000 | 81.142 | 0.123 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.506, 0.002, 0.159)→(0.506, 0.002, 0.044) | (0.511, 0.002, 0.026)→(0.511, 0.002, 0.026) | 0.246→0.246 | 1.00 / 4.000 | 12.970 | 0.123 |
| grasp_1 | grasp | 0.00 / guard_failure | (0.501, 0.002, 0.038)→(0.501, 0.002, 0.038) | (0.511, 0.002, 0.026)→(0.511, 0.002, 0.026) | 0.246→0.246 | 1.00 / 44.000 | 0.135 | 0.172 |
| lift_1 | lift | 1.00 / step_budget | (0.501, 0.002, 0.038)→(0.497, 0.002, 0.151) | (0.511, 0.002, 0.026)→(0.510, 0.002, 0.132) | 0.246→0.222 | 1.00 / 25.333 | 524.433 | 0.567 |
| move_to_goal | approach | 0.00 / guard_failure | (0.497, 0.002, 0.151)→(0.539, 0.067, 0.184) | (0.510, 0.002, 0.132)→(0.548, 0.074, 0.112) | 0.222→0.147 | 0.33 / 8.000 | 0.032 | 0.213 |
| descend_place | descend | 0.00 / step_budget | (0.501, 0.048, 0.188)→(0.568, 0.135, 0.147) | (0.507, 0.048, 0.159)→(0.575, 0.134, 0.109) | 0.207→0.092 | 1.00 / 12.000 | 0.178 | 0.192 |
| release_1 | release | 1.00 / step_budget | (0.568, 0.135, 0.147)→(0.562, 0.134, 0.169) | (0.575, 0.134, 0.109)→(0.595, 0.129, 0.016) | 0.092→0.131 | 1.00 / 4.000 | 0.123 | 1.299 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.644
- phase_score: 0.482
- phase_breakdown.lift_object_score: 0.381
- phase_breakdown.reach_object_score: 0.403
- phase_breakdown.reach_goal_score: 0.616
- grasp_place_fitness: 0.796

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.796
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.644
- **Median Q (composite search score)**: -0.073
- **K-run variance**: 0.0054
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.296


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.19643,"average_solve_count":224.0,"average_success_count":224.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_z":0.12138,"descend_1.contact_force_threshold":9.48264,"descend_1.descend_speed":0.0461,"descend_1.grasp_offset_z":0.08569,"descend_place.place_speed":0.04231,"descend_place.place_z":0.01331,"descend_to_grasp.descend_grasp_speed":0.04002,"descend_to_grasp.grasp_approach_z":0.01558,"descend_to_grasp.grasp_pose_tol":0.00613,"grasp_1.bilateral_grasp_threshold":0.08147,"grasp_1.grasp_time":2.8846,"lift_1.lift_distance":0.12019,"move_to_goal.transport_speed":0.02344,"move_to_goal.transport_z":0.17106},"optimized_scores":{"best_composite_score":-0.07423,"best_fitness_score":0.68077,"best_task_score":0.41778},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":517.0,"contact_point_centroid":[0.59361,0.12849,-0.00333],"force_p95":0.80723,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.29863,"mean_force":0.20082,"phase_index":7.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.56227,0.13408,0.15193]},{"body_a":"world","body_b":"grasp_target","contact_count":127.0,"contact_point_centroid":[0.45562,-0.02561,-0.00111],"force_p95":0.33362,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.46589,"mean_force":0.05725,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44829,-0.02575,0.04321]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12861.0,"contact_point_centroid":[0.44687,-0.04468,0.09374],"force_p95":0.08964,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29514,"mean_force":0.05569,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44584,-0.02564,0.09203]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12542.0,"contact_point_centroid":[0.44682,-0.00659,0.09442],"force_p95":0.09154,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29424,"mean_force":0.05657,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44585,-0.02564,0.0924]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":13.0,"contact_point_centroid":[0.57511,0.1531,0.13964],"force_p95":0.20749,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21855,"mean_force":0.15199,"phase_index":7.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.5679,0.13547,0.14696]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10624.0,"contact_point_centroid":[0.53918,0.07446,0.16253],"force_p95":0.11348,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19169,"mean_force":0.08489,"phase_index":6.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.53352,0.09268,0.16445]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9352.0,"contact_point_centroid":[0.53834,0.1099,0.16332],"force_p95":0.13549,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17803,"mean_force":0.09621,"phase_index":6.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.53255,0.09145,0.16499]},{"body_a":"world","body_b":"grasp_target","contact_count":1804.0,"contact_point_centroid":[0.45856,-0.02623,-0.00205],"force_p95":0.13525,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.16845,"mean_force":0.12664,"phase_index":3.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.45008,-0.02582,0.04184]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":15069.0,"contact_point_centroid":[0.47761,-0.00542,0.16909],"force_p95":0.09309,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14897,"mean_force":0.06306,"phase_index":5.0,"phase_name":"move_to_goal","phase_type":"approach","tcp_position_centroid":[0.47315,0.01332,0.16825]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":114.0,"contact_point_centroid":[0.57373,0.11929,0.14162],"force_p95":0.089,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13965,"mean_force":0.03361,"phase_index":7.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.56756,0.13549,0.14637]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":14463.0,"contact_point_centroid":[0.47801,0.03255,0.16937],"force_p95":0.09338,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13875,"mean_force":0.06528,"phase_index":5.0,"phase_name":"move_to_goal","phase_type":"approach","tcp_position_centroid":[0.4735,0.01377,0.16849]},{"body_a":"world","body_b":"grasp_target","contact_count":1712.0,"contact_point_centroid":[0.45856,-0.02632,-0.00192],"force_p95":0.13411,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12291,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4793,-0.01144,0.23097]},{"body_a":"world","body_b":"grasp_target","contact_count":72.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.45847,-0.02376,0.15925]},{"body_a":"world","body_b":"grasp_target","contact_count":2364.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":2.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.45449,-0.02481,0.10011]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5832.0,"contact_point_centroid":[0.44982,-0.00662,0.04333],"force_p95":0.06918,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11156,"mean_force":0.04498,"phase_index":3.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44965,-0.0258,0.04141]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5900.0,"contact_point_centroid":[0.44984,-0.045,0.04328],"force_p95":0.06945,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08928,"mean_force":0.04504,"phase_index":3.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44965,-0.0258,0.04141]}],"total_contact_groups":16},"final_pose_error":0.09774,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.59536,0.1288,0.01601],"final_tcp_position":[0.56792,0.13542,0.14704],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":81.14225,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":429.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1712.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.45916,-0.02365,0.16095],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13496,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":18.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":81.14225,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":72.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.4579,-0.02381,0.15736],"tcp_start":[0.45916,-0.02365,0.16095],"tcp_to_object_dist_end":0.13137,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":591.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2364.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.45415,-0.02596,0.04581],"tcp_start":[0.4579,-0.02381,0.15736],"tcp_to_object_dist_end":0.02028,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45848,-0.02593,0.02584],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30345,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.13348,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":13536.0,"raw_peak_contact_force":0.16845,"tcp_end":[0.44962,-0.0258,0.04139],"tcp_start":[0.44963,-0.0258,0.04139],"tcp_to_object_dist_end":0.0179,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":27.0,"n_steps":693.0,"n_steps_budget":780.0,"object_pos_end":[0.45874,-0.02565,0.12899],"object_pos_start":[0.45848,-0.02592,0.02585],"object_to_goal_dist_end":0.29032,"object_to_goal_dist_start":0.30344,"object_z_max":0.12888,"peak_contact_force":0.10331,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":25530.0,"raw_peak_contact_force":0.46589,"subtask_id":"lift_object","tcp_end":[0.44594,-0.02563,0.15063],"tcp_start":[0.44962,-0.0258,0.04139],"tcp_to_object_dist_end":0.02514,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":24.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5066,0.04797,0.15866],"object_pos_start":[0.45874,-0.02565,0.12899],"object_to_goal_dist_end":0.20718,"object_to_goal_dist_start":0.29032,"object_z_max":0.15863,"peak_contact_force":0.09696,"phase_name":"move_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":29532.0,"raw_peak_contact_force":0.14897,"subtask_id":"reach_goal","tcp_end":[0.50056,0.04802,0.18754],"tcp_start":[0.44594,-0.02563,0.15063],"tcp_to_object_dist_end":0.0295,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":12.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.57466,0.13442,0.10861],"object_pos_start":[0.5066,0.04797,0.15866],"object_to_goal_dist_end":0.09248,"object_to_goal_dist_start":0.20718,"object_z_max":0.15866,"peak_contact_force":0.17803,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":19976.0,"raw_peak_contact_force":0.19169,"subtask_id":"reach_goal","tcp_end":[0.56792,0.13542,0.14704],"tcp_start":[0.50056,0.04802,0.18754],"tcp_to_object_dist_end":0.03903,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.59536,0.1288,0.01601],"object_pos_start":[0.57466,0.13442,0.10861],"object_to_goal_dist_end":0.13092,"object_to_goal_dist_start":0.09248,"object_z_max":0.10861,"peak_contact_force":0.12348,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":644.0,"raw_peak_contact_force":1.29863,"tcp_end":[0.56184,0.13397,0.16917],"tcp_start":[0.56792,0.13542,0.14704],"tcp_to_object_dist_end":0.15686,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.4,"average_solve_count":135.0,"average_success_count":135.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_z":0.10826,"descend_1.contact_force_threshold":3.92437,"descend_1.descend_speed":0.03312,"descend_1.grasp_offset_z":0.10971,"descend_place.place_speed":0.02164,"descend_place.place_z":0.01656,"descend_to_grasp.descend_grasp_speed":0.04132,"descend_to_grasp.grasp_approach_z":0.01017,"descend_to_grasp.grasp_pose_tol":0.0073,"grasp_1.bilateral_grasp_threshold":0.07666,"grasp_1.grasp_time":2.40788,"lift_1.lift_distance":0.10414,"move_to_goal.transport_speed":0.09547,"move_to_goal.transport_z":0.12275},"optimized_scores":{"best_composite_score":-0.07322,"best_fitness_score":0.64011,"best_task_score":0.32427},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":142.0,"contact_point_centroid":[0.54126,0.00073,-0.00113],"force_p95":0.43585,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.65391,"mean_force":0.08424,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53172,0.0009,0.03616]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10294.0,"contact_point_centroid":[0.53016,0.01994,0.07857],"force_p95":0.08948,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3162,"mean_force":0.05743,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52906,0.00086,0.07656]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10770.0,"contact_point_centroid":[0.53002,-0.01816,0.07857],"force_p95":0.08593,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31125,"mean_force":0.05529,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52904,0.00086,0.07663]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7973.0,"contact_point_centroid":[0.54599,0.03951,0.14451],"force_p95":0.13448,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2508,"mean_force":0.0888,"phase_index":5.0,"phase_name":"move_to_goal","phase_type":"approach","tcp_position_centroid":[0.54062,0.02113,0.14442]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7598.0,"contact_point_centroid":[0.5455,0.00214,0.1439],"force_p95":0.14787,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24825,"mean_force":0.09277,"phase_index":5.0,"phase_name":"move_to_goal","phase_type":"approach","tcp_position_centroid":[0.54025,0.02058,0.14384]},{"body_a":"world","body_b":"grasp_target","contact_count":1804.0,"contact_point_centroid":[0.54429,0.00109,-0.00204],"force_p95":0.13104,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.14915,"mean_force":0.12564,"phase_index":3.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53386,0.00094,0.03506]},{"body_a":"world","body_b":"grasp_target","contact_count":2076.0,"contact_point_centroid":[0.54431,0.00113,-0.00193],"force_p95":0.1323,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12286,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.5172,0.00048,0.22184]},{"body_a":"world","body_b":"grasp_target","contact_count":28.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.53664,0.00098,0.14436]},{"body_a":"world","body_b":"grasp_target","contact_count":1780.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":2.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.53582,0.00098,0.09083]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5844.0,"contact_point_centroid":[0.53357,-0.01825,0.03638],"force_p95":0.06825,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10203,"mean_force":0.04501,"phase_index":3.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53337,0.00093,0.03448]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5878.0,"contact_point_centroid":[0.53355,0.02013,0.03636],"force_p95":0.06835,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08591,"mean_force":0.045,"phase_index":3.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53337,0.00093,0.03448]}],"total_contact_groups":11},"final_pose_error":0.2065,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.5666,0.05066,0.08897],"final_tcp_position":[0.55662,0.04233,0.16908],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":81.14225,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":520.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2076.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.53693,0.00099,0.14497],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11918,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":7.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":81.14225,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":28.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.53633,0.00097,0.14368],"tcp_start":[0.53693,0.00099,0.14497],"tcp_to_object_dist_end":0.11793,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":445.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":21.04506,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1780.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.53855,0.00103,0.04063],"tcp_start":[0.53633,0.00097,0.14368],"tcp_to_object_dist_end":0.0157,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54419,0.00097,0.02587],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25037,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.13032,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":13526.0,"raw_peak_contact_force":0.14915,"tcp_end":[0.53334,0.00093,0.03446],"tcp_start":[0.53334,0.00093,0.03446],"tcp_to_object_dist_end":0.01383,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":26.0,"n_steps":573.0,"n_steps_budget":660.0,"object_pos_end":[0.54342,0.00085,0.11176],"object_pos_start":[0.54419,0.00097,0.02588],"object_to_goal_dist_end":0.20464,"object_to_goal_dist_start":0.25036,"object_z_max":0.11164,"peak_contact_force":0.10351,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":21206.0,"raw_peak_contact_force":0.65391,"subtask_id":"lift_object","tcp_end":[0.5291,0.00087,0.1259],"tcp_start":[0.53334,0.00093,0.03446],"tcp_to_object_dist_end":0.02012,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":814.0,"n_steps_budget":1000.0,"object_pos_end":[0.5666,0.05066,0.08897],"object_pos_start":[0.54342,0.00085,0.11176],"object_to_goal_dist_end":0.16893,"object_to_goal_dist_start":0.20464,"object_z_max":0.14048,"peak_contact_force":0.0,"phase_name":"move_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":15571.0,"raw_peak_contact_force":0.2508,"subtask_id":"reach_goal","tcp_end":[0.55662,0.04233,0.16908],"tcp_start":[0.5291,0.00087,0.1259],"tcp_to_object_dist_end":0.08115,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.44231,"average_solve_count":156.0,"average_success_count":156.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_z":0.13824,"descend_1.contact_force_threshold":5.95178,"descend_1.descend_speed":0.0419,"descend_1.grasp_offset_z":0.08992,"descend_place.place_speed":0.03193,"descend_place.place_z":0.00515,"descend_to_grasp.descend_grasp_speed":0.03783,"descend_to_grasp.grasp_approach_z":0.01607,"descend_to_grasp.grasp_pose_tol":0.00601,"grasp_1.bilateral_grasp_threshold":0.06246,"grasp_1.grasp_time":2.41985,"lift_1.lift_distance":0.14975,"move_to_goal.transport_speed":0.09567,"move_to_goal.transport_z":0.11389},"optimized_scores":{"best_composite_score":0.08224,"best_fitness_score":0.79557,"best_task_score":0.64412},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":146.0,"contact_point_centroid":[0.52742,0.02955,-0.00119],"force_p95":0.37559,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.58081,"mean_force":0.07545,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51853,0.02981,0.04076]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":14202.0,"contact_point_centroid":[0.51751,0.04868,0.10047],"force_p95":0.10065,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31181,"mean_force":0.0608,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51599,0.02965,0.09857]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14670.0,"contact_point_centroid":[0.51769,0.01074,0.10176],"force_p95":0.09505,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29016,"mean_force":0.05874,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51599,0.02965,0.10004]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7441.0,"contact_point_centroid":[0.54091,0.0501,0.18264],"force_p95":0.15336,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24016,"mean_force":0.10019,"phase_index":5.0,"phase_name":"move_to_goal","phase_type":"approach","tcp_position_centroid":[0.53544,0.0686,0.18229]},{"body_a":"world","body_b":"grasp_target","contact_count":1804.0,"contact_point_centroid":[0.53052,0.03066,-0.00209],"force_p95":0.14428,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19832,"mean_force":0.12966,"phase_index":3.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52065,0.02996,0.03959]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8927.0,"contact_point_centroid":[0.54141,0.08689,0.18223],"force_p95":0.12909,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16885,"mean_force":0.08404,"phase_index":5.0,"phase_name":"move_to_goal","phase_type":"approach","tcp_position_centroid":[0.5355,0.06868,0.18233]},{"body_a":"world","body_b":"grasp_target","contact_count":1688.0,"contact_point_centroid":[0.5305,0.03079,-0.00192],"force_p95":0.13411,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12292,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51081,0.01349,0.23714]},{"body_a":"world","body_b":"grasp_target","contact_count":4.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52401,0.02763,0.17493]},{"body_a":"world","body_b":"grasp_target","contact_count":2640.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":2.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.52295,0.02889,0.10718]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5818.0,"contact_point_centroid":[0.52036,0.01075,0.04096],"force_p95":0.07068,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11818,"mean_force":0.04498,"phase_index":3.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52016,0.02993,0.03902]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5936.0,"contact_point_centroid":[0.52033,0.04914,0.04088],"force_p95":0.07104,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07802,"mean_force":0.045,"phase_index":3.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52016,0.02993,0.03903]}],"total_contact_groups":11},"final_pose_error":0.08409,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.57225,0.12237,0.08975],"final_tcp_position":[0.55972,0.11105,0.19437],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":1573.09317,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":423.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1688.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.52401,0.02763,0.17493],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.14909,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":81.14225,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.52393,0.02767,0.17469],"tcp_start":[0.52401,0.02763,0.17493],"tcp_to_object_dist_end":0.14885,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":660.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":17.7418,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2640.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.52519,0.03026,0.04485],"tcp_start":[0.52393,0.02767,0.17469],"tcp_to_object_dist_end":0.01957,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53041,0.03014,0.02571],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18406,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.14094,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":13558.0,"raw_peak_contact_force":0.19832,"tcp_end":[0.52014,0.02993,0.039],"tcp_start":[0.52014,0.02993,0.039],"tcp_to_object_dist_end":0.0168,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":845.0,"n_steps_budget":930.0,"object_pos_end":[0.52912,0.02983,0.15497],"object_pos_start":[0.53041,0.03012,0.02573],"object_to_goal_dist_end":0.17195,"object_to_goal_dist_start":0.18407,"object_z_max":0.15486,"peak_contact_force":1573.09317,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":29018.0,"raw_peak_contact_force":0.58081,"subtask_id":"lift_object","tcp_end":[0.5164,0.02968,0.17615],"tcp_start":[0.52014,0.02993,0.039],"tcp_to_object_dist_end":0.0247,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":893.0,"n_steps_budget":1000.0,"object_pos_end":[0.57225,0.12237,0.08975],"object_pos_start":[0.52912,0.02983,0.15497],"object_to_goal_dist_end":0.06598,"object_to_goal_dist_start":0.17195,"object_z_max":0.16274,"peak_contact_force":0.0,"phase_name":"move_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":16368.0,"raw_peak_contact_force":0.24016,"subtask_id":"reach_goal","tcp_end":[0.55972,0.11105,0.19437],"tcp_start":[0.5164,0.02968,0.17615],"tcp_to_object_dist_end":0.10598,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
```