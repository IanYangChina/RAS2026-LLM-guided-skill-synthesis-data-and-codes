## Search State

- **Seed**: 3
- **Iteration**: 9 / 15

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

## Current Skill (Q=0.035) — your mutation base

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
      - 0.02
      - 0.06
      default: 0.03
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
      - 3.0
      default: 2.0
      binds_to:
      - path: duration.max_time
        mode: replace
  guards:
  - id: grasp_check
    when: during_phase
    predicate: bilateral_grasp
    threshold: 0.2
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
      distance: 0.1
      axis: world_z
      mode: add_to_offset
      sign: positive
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
    - 0.0
    orientation:
      mode: keep_current
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
- id: retract_1
  type: retract
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.1
    offset_along_axis:
      distance: 0.1
      axis: world_z
      mode: add_to_offset
      sign: positive
    orientation:
      mode: keep_current

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
    - grasp_time: status=consumed; consumers=duration.max_time (replace)
  - guards:
    - id=grasp_check, when=during_phase, predicate=bilateral_grasp, on_failure=retry, threshold=0.2
  - retries: max_attempts=2, strategy=repeat
- **lift_1** (`lift`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.1, mode=add_to_offset, sign=positive}
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
  - guards:
    - id=lift_check, when=after_phase, predicate=object_lifted, on_failure=abort, threshold=0.02
- **move_to_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings: none
- **release_1** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
- **retract_1** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.1], offset_along_axis={axis=world_z, distance=0.1, mode=add_to_offset, sign=positive}
  - orientation: mode=keep_current
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.035
- **task_score** (E): 0.350
- **fitness_score**: 0.640  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.125
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.730

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1583 |
| descend_1 | 1.00 | 1.00 | 0.0019 |
| descend_to_grasp | 1.00 | 1.00 | 0.0950 |
| grasp_1 | 0.00 | 1.00 | 0.0000 |
| lift_1 | 1.00 | 1.00 | 0.1239 |
| move_to_goal | 0.00 | 0.67 | 0.1199 |
| release_1 | 1.00 | 1.00 | 0.0232 |
| retract_1 | 1.00 | 1.00 | 0.1636 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.507, 0.002, 0.148) | (0.511, 0.002, 0.030)→(0.511, 0.002, 0.026) | 0.244→0.246 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / force_exceeded | (0.507, 0.002, 0.148)→(0.507, 0.002, 0.146) | (0.511, 0.002, 0.026)→(0.511, 0.002, 0.026) | 0.246→0.246 | 1.00 / 4.000 | 81.142 | 0.123 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.507, 0.002, 0.146)→(0.506, 0.002, 0.051) | (0.511, 0.002, 0.026)→(0.511, 0.002, 0.026) | 0.246→0.246 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 0.00 / guard_failure | (0.501, 0.002, 0.046)→(0.501, 0.002, 0.046) | (0.511, 0.002, 0.026)→(0.511, 0.002, 0.026) | 0.246→0.246 | 1.00 / 42.000 | 0.136 | 0.173 |
| lift_1 | lift | 1.00 / step_budget | (0.501, 0.002, 0.046)→(0.497, 0.002, 0.170) | (0.511, 0.002, 0.026)→(0.508, 0.002, 0.143) | 0.246→0.218 | 1.00 / 25.667 | 0.099 | 0.435 |
| move_to_goal | approach | 0.00 / step_budget | (0.497, 0.002, 0.170)→(0.563, 0.100, 0.166) | (0.508, 0.002, 0.143)→(0.571, 0.097, 0.099) | 0.218→0.125 | 0.67 / 11.000 | 0.089 | 0.266 |
| release_1 | release | 1.00 / step_budget | (0.563, 0.100, 0.166)→(0.557, 0.099, 0.188) | (0.571, 0.097, 0.099)→(0.561, 0.100, 0.022) | 0.125→0.163 | 1.00 / 3.333 | 0.132 | 1.311 |
| retract_1 | retract | 1.00 / step_budget | (0.557, 0.099, 0.188)→(0.555, 0.109, 0.352) | (0.561, 0.100, 0.022)→(0.558, 0.100, 0.023) | 0.163→0.164 | 1.00 / 4.000 | 0.123 | 0.154 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.504
- phase_score: 0.606
- phase_breakdown.lift_object_score: 0.652
- phase_breakdown.reach_object_score: 0.464
- phase_breakdown.reach_goal_score: 0.679
- grasp_place_fitness: 0.716

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.716
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.504
- **Median Q (composite search score)**: -0.002
- **K-run variance**: 0.0029
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.340


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.11905,"average_solve_count":252.0,"average_success_count":252.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_z":0.14604,"descend_1.contact_force_threshold":9.39953,"descend_1.descend_speed":0.04282,"descend_1.grasp_offset_z":0.06292,"descend_to_grasp.descend_grasp_speed":0.01989,"descend_to_grasp.grasp_approach_z":0.0215,"descend_to_grasp.grasp_pose_tol":0.00505,"grasp_1.bilateral_grasp_threshold":0.07876,"grasp_1.grasp_time":1.70135,"lift_1.lift_distance":0.14627,"move_to_goal.place_offset_z":0.08728},"optimized_scores":{"best_composite_score":-0.00164,"best_fitness_score":0.60336,"best_task_score":0.27374},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":184.0,"contact_point_centroid":[0.51672,0.08195,-0.00726],"force_p95":1.21813,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.29921,"mean_force":0.38243,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.52299,0.08207,0.19905]},{"body_a":"world","body_b":"grasp_target","contact_count":124.0,"contact_point_centroid":[0.45582,-0.02549,-0.00113],"force_p95":0.26449,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.4124,"mean_force":0.05109,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4484,-0.02578,0.04734]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":13586.0,"contact_point_centroid":[0.44775,-0.00664,0.10849],"force_p95":0.10093,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31428,"mean_force":0.06287,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44596,-0.02567,0.10719]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11133.0,"contact_point_centroid":[0.49174,0.01067,0.17924],"force_p95":0.11479,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29401,"mean_force":0.08255,"phase_index":5.0,"phase_name":"move_to_goal","phase_type":"approach","tcp_position_centroid":[0.48607,0.02912,0.18047]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":15363.0,"contact_point_centroid":[0.44749,-0.04461,0.10711],"force_p95":0.09403,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28564,"mean_force":0.05643,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44597,-0.02567,0.10595]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10887.0,"contact_point_centroid":[0.49158,0.04757,0.17899],"force_p95":0.1159,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1924,"mean_force":0.08471,"phase_index":5.0,"phase_name":"move_to_goal","phase_type":"approach","tcp_position_centroid":[0.48603,0.02907,0.18047]},{"body_a":"world","body_b":"grasp_target","contact_count":3971.0,"contact_point_centroid":[0.51162,0.08202,-0.00199],"force_p95":0.12732,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18443,"mean_force":0.12278,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.52046,0.09637,0.28839]},{"body_a":"world","body_b":"grasp_target","contact_count":1804.0,"contact_point_centroid":[0.45857,-0.02614,-0.00205],"force_p95":0.13582,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17208,"mean_force":0.12698,"phase_index":3.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.45017,-0.02585,0.046]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":575.0,"contact_point_centroid":[0.53269,0.06428,0.17738],"force_p95":0.13392,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17159,"mean_force":0.0857,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.52649,0.08271,0.18119]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":604.0,"contact_point_centroid":[0.53254,0.10095,0.17738],"force_p95":0.11869,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14795,"mean_force":0.0832,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.52656,0.08272,0.18131]},{"body_a":"world","body_b":"grasp_target","contact_count":1432.0,"contact_point_centroid":[0.45856,-0.02632,-0.00191],"force_p95":0.13533,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12297,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.47993,-0.01115,0.24324]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4962.0,"contact_point_centroid":[0.45049,-0.00658,0.04894],"force_p95":0.07726,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12715,"mean_force":0.05222,"phase_index":3.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44973,-0.02583,0.04557]},{"body_a":"world","body_b":"grasp_target","contact_count":3528.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":2.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.45487,-0.02462,0.11275]},{"body_a":"world","body_b":"grasp_target","contact_count":80.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12262,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12262,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.45936,-0.02332,0.18346]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6192.0,"contact_point_centroid":[0.45003,-0.04488,0.04773],"force_p95":0.06604,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0803,"mean_force":0.04301,"phase_index":3.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44973,-0.02583,0.04557]}],"total_contact_groups":15},"final_pose_error":0.03725,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.51147,0.08202,0.02602],"final_tcp_position":[0.5212,0.09176,0.37191],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":81.14225,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":359.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1432.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.4601,-0.0232,0.18538],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.1594,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":20.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":81.14225,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":80.0,"raw_peak_contact_force":0.12262,"subtask_id":"reach_object","tcp_end":[0.45878,-0.02334,0.18139],"tcp_start":[0.4601,-0.0232,0.18538],"tcp_to_object_dist_end":0.15539,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":882.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3528.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.4542,-0.026,0.04996],"tcp_start":[0.45878,-0.02334,0.18139],"tcp_to_object_dist_end":0.02434,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45849,-0.02576,0.02583],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30332,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.13191,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12958.0,"raw_peak_contact_force":0.17208,"tcp_end":[0.44971,-0.02583,0.04555],"tcp_start":[0.44971,-0.02583,0.04555],"tcp_to_object_dist_end":0.02159,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":26.0,"n_steps":843.0,"n_steps_budget":930.0,"object_pos_end":[0.45718,-0.02593,0.1535],"object_pos_start":[0.4585,-0.02574,0.02584],"object_to_goal_dist_end":0.29375,"object_to_goal_dist_start":0.30329,"object_z_max":0.15339,"peak_contact_force":0.09377,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":29073.0,"raw_peak_contact_force":0.4124,"subtask_id":"lift_object","tcp_end":[0.44623,-0.02567,0.18067],"tcp_start":[0.44971,-0.02583,0.04555],"tcp_to_object_dist_end":0.0293,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":16.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53372,0.08236,0.14816],"object_pos_start":[0.45718,-0.02593,0.1535],"object_to_goal_dist_end":0.16215,"object_to_goal_dist_start":0.29375,"object_z_max":0.15353,"peak_contact_force":0.13573,"phase_name":"move_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":22020.0,"raw_peak_contact_force":0.29401,"subtask_id":"reach_goal","tcp_end":[0.52826,0.08286,0.18406],"tcp_start":[0.44623,-0.02567,0.18067],"tcp_to_object_dist_end":0.03632,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51981,0.08198,0.02494],"object_pos_start":[0.53372,0.08236,0.14816],"object_to_goal_dist_end":0.18989,"object_to_goal_dist_start":0.16215,"object_z_max":0.14816,"peak_contact_force":0.12189,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1363.0,"raw_peak_contact_force":1.29921,"tcp_end":[0.52291,0.08207,0.20783],"tcp_start":[0.52826,0.08286,0.18406],"tcp_to_object_dist_end":0.18291,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51147,0.08202,0.02602],"object_pos_start":[0.51981,0.08198,0.02494],"object_to_goal_dist_end":0.19433,"object_to_goal_dist_start":0.18989,"object_z_max":0.02679,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3971.0,"raw_peak_contact_force":0.18443,"tcp_end":[0.5212,0.09176,0.37191],"tcp_start":[0.52291,0.08207,0.20783],"tcp_to_object_dist_end":0.34616,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.14545,"average_solve_count":220.0,"average_success_count":220.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_z":0.08098,"descend_1.contact_force_threshold":5.35527,"descend_1.descend_speed":0.06729,"descend_1.grasp_offset_z":0.06239,"descend_to_grasp.descend_grasp_speed":0.01655,"descend_to_grasp.grasp_approach_z":0.02358,"descend_to_grasp.grasp_pose_tol":0.00663,"grasp_1.bilateral_grasp_threshold":0.09316,"grasp_1.grasp_time":1.99552,"lift_1.lift_distance":0.14969,"move_to_goal.place_offset_z":0.03149},"optimized_scores":{"best_composite_score":-0.00487,"best_fitness_score":0.60013,"best_task_score":0.2719},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":705.0,"contact_point_centroid":[0.60721,0.08104,-0.00349],"force_p95":0.85419,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.64255,"mean_force":0.19541,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.58214,0.08034,0.19793]},{"body_a":"world","body_b":"grasp_target","contact_count":146.0,"contact_point_centroid":[0.54157,0.00059,-0.00115],"force_p95":0.31081,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.44879,"mean_force":0.0666,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53169,0.00091,0.048]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13842.0,"contact_point_centroid":[0.53067,-0.0181,0.10608],"force_p95":0.1015,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30174,"mean_force":0.0623,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52914,0.00087,0.10525]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":14244.0,"contact_point_centroid":[0.53126,0.0198,0.1076],"force_p95":0.09554,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28711,"mean_force":0.06082,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52914,0.00087,0.10633]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10493.0,"contact_point_centroid":[0.56159,0.05856,0.18532],"force_p95":0.11482,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23145,"mean_force":0.0814,"phase_index":5.0,"phase_name":"move_to_goal","phase_type":"approach","tcp_position_centroid":[0.55571,0.04008,0.18664]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10419.0,"contact_point_centroid":[0.56177,0.02189,0.18514],"force_p95":0.11536,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21581,"mean_force":0.08195,"phase_index":5.0,"phase_name":"move_to_goal","phase_type":"approach","tcp_position_centroid":[0.55594,0.04038,0.18671]},{"body_a":"world","body_b":"grasp_target","contact_count":1804.0,"contact_point_centroid":[0.5443,0.00103,-0.00204],"force_p95":0.13163,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15124,"mean_force":0.12577,"phase_index":3.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53382,0.00095,0.04696]},{"body_a":"world","body_b":"grasp_target","contact_count":2404.0,"contact_point_centroid":[0.54431,0.00113,-0.00194],"force_p95":0.13067,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12283,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51735,0.00049,0.20808]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.60724,0.08143,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12268,"mean_force":0.12262,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.57881,0.09437,0.29634]},{"body_a":"world","body_b":"grasp_target","contact_count":1348.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":2.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.53594,0.00098,0.08324]},{"body_a":"world","body_b":"grasp_target","contact_count":20.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12262,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12262,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.53699,0.00099,0.11732]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4975.0,"contact_point_centroid":[0.53266,-0.01827,0.04825],"force_p95":0.07626,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09811,"mean_force":0.05213,"phase_index":3.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53332,0.00094,0.04637]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5863.0,"contact_point_centroid":[0.53332,0.01998,0.04783],"force_p95":0.06747,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0882,"mean_force":0.04499,"phase_index":3.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53332,0.00094,0.04637]}],"total_contact_groups":13},"final_pose_error":0.03836,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.60724,0.08143,0.01602],"final_tcp_position":[0.57969,0.08986,0.38042],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":81.14225,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":602.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2404.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.53718,0.00099,0.11775],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.09201,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":5.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":81.14225,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":20.0,"raw_peak_contact_force":0.12262,"subtask_id":"reach_object","tcp_end":[0.53675,0.00098,0.11671],"tcp_start":[0.53718,0.00099,0.11775],"tcp_to_object_dist_end":0.09101,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":337.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1348.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.53839,0.00103,0.05248],"tcp_start":[0.53675,0.00098,0.11671],"tcp_to_object_dist_end":0.02712,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54422,0.00081,0.02587],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25046,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12998,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12642.0,"raw_peak_contact_force":0.15124,"tcp_end":[0.5333,0.00094,0.04634],"tcp_start":[0.5333,0.00094,0.04634],"tcp_to_object_dist_end":0.0232,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":24.0,"n_steps":845.0,"n_steps_budget":930.0,"object_pos_end":[0.53973,0.00111,0.15515],"object_pos_start":[0.54422,0.00079,0.02588],"object_to_goal_dist_end":0.19384,"object_to_goal_dist_start":0.25047,"object_z_max":0.15504,"peak_contact_force":0.09698,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":28232.0,"raw_peak_contact_force":0.44879,"subtask_id":"lift_object","tcp_end":[0.52958,0.00088,0.18316],"tcp_start":[0.5333,0.00094,0.04634],"tcp_to_object_dist_end":0.02979,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.60135,0.0715,0.06625],"object_pos_start":[0.53973,0.00111,0.15515],"object_to_goal_dist_end":0.15883,"object_to_goal_dist_start":0.19384,"object_z_max":0.15856,"peak_contact_force":0.0,"phase_name":"move_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":20912.0,"raw_peak_contact_force":0.23145,"subtask_id":"reach_goal","tcp_end":[0.58643,0.08092,0.19581],"tcp_start":[0.52958,0.00088,0.18316],"tcp_to_object_dist_end":0.13076,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.60724,0.08143,0.01602],"object_pos_start":[0.60135,0.0715,0.06625],"object_to_goal_dist_end":0.19535,"object_to_goal_dist_start":0.15883,"object_z_max":0.06625,"peak_contact_force":0.12269,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":705.0,"raw_peak_contact_force":1.64255,"tcp_end":[0.58109,0.08015,0.21751],"tcp_start":[0.58643,0.08092,0.19581],"tcp_to_object_dist_end":0.20318,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.60724,0.08143,0.01602],"object_pos_start":[0.60724,0.08143,0.01602],"object_to_goal_dist_end":0.19535,"object_to_goal_dist_start":0.19535,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12268,"tcp_end":[0.57969,0.08986,0.38042],"tcp_start":[0.58109,0.08015,0.21751],"tcp_to_object_dist_end":0.36554,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.95528,"average_solve_count":246.0,"average_success_count":246.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_z":0.10427,"descend_1.contact_force_threshold":3.28375,"descend_1.descend_speed":0.07004,"descend_1.grasp_offset_z":0.10043,"descend_to_grasp.descend_grasp_speed":0.01075,"descend_to_grasp.grasp_approach_z":0.02265,"descend_to_grasp.grasp_pose_tol":0.00647,"grasp_1.bilateral_grasp_threshold":0.10873,"grasp_1.grasp_time":1.922,"lift_1.lift_distance":0.11191,"move_to_goal.place_offset_z":0.00988},"optimized_scores":{"best_composite_score":0.11136,"best_fitness_score":0.71636,"best_task_score":0.5036},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":321.0,"contact_point_centroid":[0.55814,0.13562,-0.00344],"force_p95":0.74973,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.99018,"mean_force":0.21877,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.56719,0.13518,0.12819]},{"body_a":"world","body_b":"grasp_target","contact_count":148.0,"contact_point_centroid":[0.52787,0.029,-0.00119],"force_p95":0.29662,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.44249,"mean_force":0.06523,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51845,0.02977,0.04795]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11568.0,"contact_point_centroid":[0.5163,0.01055,0.09389],"force_p95":0.08904,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30619,"mean_force":0.05668,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51588,0.02961,0.09291]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12001.0,"contact_point_centroid":[0.5171,0.04865,0.09394],"force_p95":0.08983,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30601,"mean_force":0.05544,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51593,0.02961,0.09223]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10689.0,"contact_point_centroid":[0.54776,0.06585,0.12723],"force_p95":0.12882,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27213,"mean_force":0.08702,"phase_index":5.0,"phase_name":"move_to_goal","phase_type":"approach","tcp_position_centroid":[0.54381,0.08433,0.12919]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":559.0,"contact_point_centroid":[0.57603,0.1548,0.11057],"force_p95":0.13148,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23773,"mean_force":0.09009,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57154,0.13635,0.11476]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11252.0,"contact_point_centroid":[0.54798,0.10244,0.12792],"force_p95":0.1258,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21667,"mean_force":0.08189,"phase_index":5.0,"phase_name":"move_to_goal","phase_type":"approach","tcp_position_centroid":[0.54365,0.08404,0.12925]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":601.0,"contact_point_centroid":[0.57623,0.11813,0.11099],"force_p95":0.11647,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20585,"mean_force":0.08152,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57162,0.13638,0.11487]},{"body_a":"world","body_b":"grasp_target","contact_count":1804.0,"contact_point_centroid":[0.53052,0.03065,-0.00211],"force_p95":0.14738,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19606,"mean_force":0.13039,"phase_index":3.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52057,0.02992,0.04672]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.55664,0.13572,-0.00199],"force_p95":0.12442,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15531,"mean_force":0.12266,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.56396,0.14894,0.21909]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4952.0,"contact_point_centroid":[0.51941,0.01061,0.04795],"force_p95":0.07984,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14321,"mean_force":0.05255,"phase_index":3.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52009,0.02989,0.04616]},{"body_a":"world","body_b":"grasp_target","contact_count":2084.0,"contact_point_centroid":[0.5305,0.03079,-0.00193],"force_p95":0.13221,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12286,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51092,0.01382,0.22023]},{"body_a":"world","body_b":"grasp_target","contact_count":4.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52426,0.02816,0.14132]},{"body_a":"world","body_b":"grasp_target","contact_count":1860.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":2.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.52295,0.0291,0.09508]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6524.0,"contact_point_centroid":[0.52097,0.04893,0.04853],"force_p95":0.06745,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0681,"mean_force":0.04086,"phase_index":3.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52009,0.02989,0.04616]}],"total_contact_groups":15},"final_pose_error":0.03823,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.55664,0.13572,0.02602],"final_tcp_position":[0.56467,0.14448,0.30312],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":81.14225,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":522.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2084.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.52426,0.02816,0.14132],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.1155,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":81.14225,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.52417,0.02819,0.14107],"tcp_start":[0.52426,0.02816,0.14132],"tcp_to_object_dist_end":0.11526,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":465.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1860.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.52506,0.03022,0.05199],"tcp_start":[0.52417,0.02819,0.14107],"tcp_to_object_dist_end":0.02654,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53043,0.02998,0.02567],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.1842,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.14502,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":13280.0,"raw_peak_contact_force":0.19606,"tcp_end":[0.52007,0.02988,0.04613],"tcp_start":[0.52007,0.02988,0.04613],"tcp_to_object_dist_end":0.02293,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":27.0,"n_steps":633.0,"n_steps_budget":720.0,"object_pos_end":[0.52737,0.02995,0.12011],"object_pos_start":[0.53043,0.02995,0.02569],"object_to_goal_dist_end":0.16654,"object_to_goal_dist_start":0.18422,"object_z_max":0.12,"peak_contact_force":0.10483,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":23717.0,"raw_peak_contact_force":0.44249,"subtask_id":"lift_object","tcp_end":[0.51606,0.02962,0.14569],"tcp_start":[0.52007,0.02988,0.04613],"tcp_to_object_dist_end":0.02797,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":17.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.57843,0.13732,0.08299],"object_pos_start":[0.52737,0.02995,0.12011],"object_to_goal_dist_end":0.05354,"object_to_goal_dist_start":0.16654,"object_z_max":0.12015,"peak_contact_force":0.13205,"phase_name":"move_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":21941.0,"raw_peak_contact_force":0.27213,"subtask_id":"reach_goal","tcp_end":[0.57365,0.13669,0.11813],"tcp_start":[0.51606,0.02962,0.14569],"tcp_to_object_dist_end":0.03546,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.55667,0.13563,0.02648],"object_pos_start":[0.57843,0.13732,0.08299],"object_to_goal_dist_end":0.10255,"object_to_goal_dist_start":0.05354,"object_z_max":0.08299,"peak_contact_force":0.15165,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1481.0,"raw_peak_contact_force":0.99018,"tcp_end":[0.56705,0.13514,0.14011],"tcp_start":[0.57365,0.13669,0.11813],"tcp_to_object_dist_end":0.1141,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.55664,0.13572,0.02602],"object_pos_start":[0.55667,0.13563,0.02648],"object_to_goal_dist_end":0.1029,"object_to_goal_dist_start":0.10255,"object_z_max":0.02648,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.15531,"tcp_end":[0.56467,0.14448,0.30312],"tcp_start":[0.56705,0.13514,0.14011],"tcp_to_object_dist_end":0.27736,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```