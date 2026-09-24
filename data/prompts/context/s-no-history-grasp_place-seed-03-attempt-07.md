## Search State

- **Seed**: 3
- **Iteration**: 8 / 15

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

## Current Skill (Q=0.061) — your mutation base

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

- **Composite score**: 0.061
- **task_score** (E): 0.373
- **fitness_score**: 0.566  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.125
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.630

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1678 |
| descend_1 | 1.00 | 1.00 | 0.0025 |
| descend_to_grasp | 1.00 | 1.00 | 0.0828 |
| grasp_1 | 0.00 | 1.00 | 0.0000 |
| lift_1 | 1.00 | 1.00 | 0.0888 |
| move_to_goal | 0.33 | 0.67 | 0.1220 |
| release_1 | 1.00 | 1.00 | 0.0236 |
| retract_1 | 1.00 | 1.00 | 0.1637 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.507, 0.002, 0.138) | (0.511, 0.002, 0.030)→(0.511, 0.002, 0.026) | 0.244→0.246 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / force_exceeded | (0.507, 0.002, 0.138)→(0.506, 0.002, 0.136) | (0.511, 0.002, 0.026)→(0.511, 0.002, 0.026) | 0.246→0.246 | 1.00 / 4.000 | 81.142 | 0.123 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.506, 0.002, 0.136)→(0.506, 0.002, 0.053) | (0.511, 0.002, 0.026)→(0.511, 0.002, 0.026) | 0.246→0.246 | 1.00 / 4.000 | 5.125 | 0.123 |
| grasp_1 | grasp | 0.00 / guard_failure | (0.501, 0.002, 0.048)→(0.501, 0.002, 0.048) | (0.511, 0.002, 0.026)→(0.511, 0.002, 0.026) | 0.246→0.246 | 1.00 / 42.000 | 0.143 | 0.172 |
| lift_1 | lift | 1.00 / step_budget | (0.501, 0.002, 0.048)→(0.497, 0.002, 0.137) | (0.511, 0.002, 0.026)→(0.506, 0.002, 0.109) | 0.246→0.224 | 1.00 / 24.333 | 0.111 | 0.416 |
| move_to_goal | approach | 0.33 / step_budget | (0.497, 0.002, 0.137)→(0.562, 0.100, 0.124) | (0.506, 0.002, 0.109)→(0.565, 0.104, 0.064) | 0.224→0.130 | 0.67 / 9.000 | 9962.969 | 0.265 |
| release_1 | release | 1.00 / step_budget | (0.562, 0.100, 0.124)→(0.555, 0.099, 0.147) | (0.565, 0.104, 0.064)→(0.564, 0.120, 0.019) | 0.130→0.153 | 1.00 / 3.667 | 0.201 | 1.068 |
| retract_1 | retract | 1.00 / step_budget | (0.555, 0.099, 0.147)→(0.553, 0.109, 0.310) | (0.564, 0.120, 0.019)→(0.560, 0.122, 0.019) | 0.153→0.155 | 1.00 / 4.000 | 0.123 | 0.199 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.536
- phase_score: 0.563
- phase_breakdown.lift_object_score: 0.464
- phase_breakdown.reach_object_score: 0.442
- phase_breakdown.reach_goal_score: 0.728
- grasp_place_fitness: 0.735

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.735
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.536
- **Median Q (composite search score)**: 0.094
- **K-run variance**: 0.0238
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.345


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.4433,"average_solve_count":194.0,"average_success_count":194.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_z":0.12205,"descend_1.contact_force_threshold":5.51515,"descend_1.descend_speed":0.06074,"descend_1.grasp_offset_z":0.08855,"descend_to_grasp.descend_grasp_speed":0.03051,"descend_to_grasp.grasp_approach_z":0.02663,"descend_to_grasp.grasp_pose_tol":0.00499,"grasp_1.grasp_time":1.70807,"lift_1.lift_distance":0.0568},"optimized_scores":{"best_composite_score":-0.14263,"best_fitness_score":0.36237,"best_task_score":0.30566},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":571.0,"contact_point_centroid":[0.52744,0.09395,-0.00285],"force_p95":0.55938,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.85128,"mean_force":0.18591,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.51757,0.07688,0.10522]},{"body_a":"world","body_b":"grasp_target","contact_count":173.0,"contact_point_centroid":[0.45519,-0.02398,-0.00127],"force_p95":0.23951,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.3788,"mean_force":0.06387,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44816,-0.02576,0.05245]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10792.0,"contact_point_centroid":[0.48548,0.04777,0.09352],"force_p95":0.11541,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33224,"mean_force":0.08581,"phase_index":5.0,"phase_name":"move_to_goal","phase_type":"approach","tcp_position_centroid":[0.48501,0.02915,0.09706]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5601.0,"contact_point_centroid":[0.4472,-0.00672,0.07047],"force_p95":0.11416,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32524,"mean_force":0.08011,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44601,-0.02567,0.07212]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8343.0,"contact_point_centroid":[0.44555,-0.04419,0.07334],"force_p95":0.10145,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26911,"mean_force":0.05638,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44593,-0.02567,0.07358]},{"body_a":"world","body_b":"grasp_target","contact_count":1804.0,"contact_point_centroid":[0.45858,-0.02634,-0.0021],"force_p95":0.15365,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.16787,"mean_force":0.13018,"phase_index":3.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.45016,-0.02584,0.05095]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12126.0,"contact_point_centroid":[0.48574,0.01089,0.09359],"force_p95":0.10073,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16332,"mean_force":0.07536,"phase_index":5.0,"phase_name":"move_to_goal","phase_type":"approach","tcp_position_centroid":[0.4852,0.02935,0.0971]},{"body_a":"world","body_b":"grasp_target","contact_count":1708.0,"contact_point_centroid":[0.45856,-0.02632,-0.00192],"force_p95":0.13411,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12291,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.47933,-0.01143,0.23136]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5226.0,"contact_point_centroid":[0.45012,-0.00664,0.05081],"force_p95":0.09576,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13275,"mean_force":0.05432,"phase_index":3.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44973,-0.02582,0.05053]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.52994,0.09891,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12337,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.51346,0.09085,0.20391]},{"body_a":"world","body_b":"grasp_target","contact_count":76.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.45844,-0.02376,0.15978]},{"body_a":"world","body_b":"grasp_target","contact_count":2672.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":2.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.45442,-0.02484,0.10405]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":33.0,"contact_point_centroid":[0.52356,0.06303,0.09345],"force_p95":0.07231,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09162,"mean_force":0.01425,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.5232,0.07771,0.09922]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5892.0,"contact_point_centroid":[0.44977,-0.04466,0.05087],"force_p95":0.06847,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08415,"mean_force":0.04342,"phase_index":3.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44973,-0.02582,0.05053]}],"total_contact_groups":14},"final_pose_error":0.03708,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.52994,0.09891,0.01602],"final_tcp_position":[0.51402,0.08633,0.28794],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":29888.77016,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":428.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1708.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.45918,-0.02364,0.16159],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.1356,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":19.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":81.14225,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":76.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.45787,-0.02381,0.15778],"tcp_start":[0.45918,-0.02364,0.16159],"tcp_to_object_dist_end":0.13179,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":668.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":15.13098,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2672.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.45417,-0.02599,0.05493],"tcp_start":[0.45787,-0.02381,0.15778],"tcp_to_object_dist_end":0.02924,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.4585,-0.02581,0.02553],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30344,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.15756,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12922.0,"raw_peak_contact_force":0.16787,"tcp_end":[0.44971,-0.02582,0.05051],"tcp_start":[0.44971,-0.02582,0.05051],"tcp_to_object_dist_end":0.02648,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":24.0,"n_steps":450.0,"n_steps_budget":600.0,"object_pos_end":[0.45234,-0.02614,0.06888],"object_pos_start":[0.45849,-0.02583,0.02546],"object_to_goal_dist_end":0.29763,"object_to_goal_dist_start":0.30347,"object_z_max":0.06881,"peak_contact_force":0.11132,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":14117.0,"raw_peak_contact_force":0.3788,"subtask_id":"lift_object","tcp_end":[0.44562,-0.02565,0.09823],"tcp_start":[0.44971,-0.02582,0.05051],"tcp_to_object_dist_end":0.03011,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52316,0.07425,0.05845],"object_pos_start":[0.45234,-0.02614,0.06888],"object_to_goal_dist_end":0.18024,"object_to_goal_dist_start":0.29763,"object_z_max":0.06888,"peak_contact_force":29888.77016,"phase_name":"move_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":22918.0,"raw_peak_contact_force":0.33224,"subtask_id":"reach_goal","tcp_end":[0.52318,0.07761,0.09929],"tcp_start":[0.44562,-0.02565,0.09823],"tcp_to_object_dist_end":0.04098,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.52995,0.09889,0.01603],"object_pos_start":[0.52316,0.07425,0.05845],"object_to_goal_dist_end":0.17779,"object_to_goal_dist_start":0.18024,"object_z_max":0.05845,"peak_contact_force":0.12339,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":604.0,"raw_peak_contact_force":0.85128,"tcp_end":[0.51671,0.07675,0.12366],"tcp_start":[0.52318,0.07761,0.09929],"tcp_to_object_dist_end":0.11068,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52994,0.09891,0.01602],"object_pos_start":[0.52995,0.09889,0.01603],"object_to_goal_dist_end":0.17779,"object_to_goal_dist_start":0.17779,"object_z_max":0.01603,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12337,"tcp_end":[0.51402,0.08633,0.28794],"tcp_start":[0.51671,0.07675,0.12366],"tcp_to_object_dist_end":0.27268,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.25758,"average_solve_count":198.0,"average_success_count":198.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_z":0.09637,"descend_1.contact_force_threshold":9.29273,"descend_1.descend_speed":0.05315,"descend_1.grasp_offset_z":0.10493,"descend_to_grasp.descend_grasp_speed":0.02338,"descend_to_grasp.grasp_approach_z":0.02598,"descend_to_grasp.grasp_pose_tol":0.00685,"grasp_1.grasp_time":1.18479,"lift_1.lift_distance":0.10925},"optimized_scores":{"best_composite_score":0.09391,"best_fitness_score":0.59891,"best_task_score":0.27705},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":742.0,"contact_point_centroid":[0.59249,0.09995,-0.00317],"force_p95":0.58062,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.31168,"mean_force":0.17076,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.5784,0.07653,0.16258]},{"body_a":"world","body_b":"grasp_target","contact_count":143.0,"contact_point_centroid":[0.54173,0.00049,-0.00113],"force_p95":0.28599,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.40429,"mean_force":0.06161,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.5318,0.00091,0.05109]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10806.0,"contact_point_centroid":[0.52972,-0.01815,0.09369],"force_p95":0.10467,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30459,"mean_force":0.05885,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52918,0.00087,0.0937]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10874.0,"contact_point_centroid":[0.5303,0.01987,0.0936],"force_p95":0.09827,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29384,"mean_force":0.05826,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.5292,0.00087,0.09317]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7858.0,"contact_point_centroid":[0.55977,0.02203,0.14756],"force_p95":0.13492,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24579,"mean_force":0.10647,"phase_index":5.0,"phase_name":"move_to_goal","phase_type":"approach","tcp_position_centroid":[0.55532,0.04021,0.15095]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8486.0,"contact_point_centroid":[0.56084,0.05958,0.14765],"force_p95":0.12293,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18846,"mean_force":0.09866,"phase_index":5.0,"phase_name":"move_to_goal","phase_type":"approach","tcp_position_centroid":[0.55627,0.04151,0.15126]},{"body_a":"world","body_b":"grasp_target","contact_count":1804.0,"contact_point_centroid":[0.54431,0.00105,-0.00204],"force_p95":0.13178,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15147,"mean_force":0.12574,"phase_index":3.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53391,0.00095,0.04999]},{"body_a":"world","body_b":"grasp_target","contact_count":2224.0,"contact_point_centroid":[0.54431,0.00113,-0.00194],"force_p95":0.13197,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12285,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51728,0.00048,0.21584]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.59248,0.09999,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12262,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.57434,0.09049,0.26143]},{"body_a":"world","body_b":"grasp_target","contact_count":32.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.5367,0.00098,0.13243]},{"body_a":"world","body_b":"grasp_target","contact_count":1480.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":2.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.53579,0.00098,0.09241]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4979.0,"contact_point_centroid":[0.53265,-0.01826,0.0502],"force_p95":0.07608,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09855,"mean_force":0.05217,"phase_index":3.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53342,0.00094,0.0494]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5868.0,"contact_point_centroid":[0.53348,0.01999,0.05008],"force_p95":0.06811,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08754,"mean_force":0.04482,"phase_index":3.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53342,0.00094,0.0494]}],"total_contact_groups":13},"final_pose_error":0.03829,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.59248,0.09999,0.01602],"final_tcp_position":[0.57514,0.08598,0.34548],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":81.14225,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":557.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2224.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.53706,0.00099,0.13311],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.10733,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":8.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":81.14225,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":32.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.53632,0.00097,0.13174],"tcp_start":[0.53706,0.00099,0.13311],"tcp_to_object_dist_end":0.10602,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":370.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1480.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.53847,0.00103,0.05554],"tcp_start":[0.53632,0.00097,0.13174],"tcp_to_object_dist_end":0.03009,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54422,0.00084,0.02587],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25044,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.13087,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12651.0,"raw_peak_contact_force":0.15147,"tcp_end":[0.5334,0.00094,0.04937],"tcp_start":[0.5334,0.00094,0.04938],"tcp_to_object_dist_end":0.02588,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":603.0,"n_steps_budget":690.0,"object_pos_end":[0.53871,0.00124,0.11652],"object_pos_start":[0.54422,0.00083,0.02588],"object_to_goal_dist_end":0.205,"object_to_goal_dist_start":0.25044,"object_z_max":0.11641,"peak_contact_force":0.12299,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":21823.0,"raw_peak_contact_force":0.40429,"subtask_id":"lift_object","tcp_end":[0.52933,0.00088,0.14587],"tcp_start":[0.5334,0.00094,0.04937],"tcp_to_object_dist_end":0.03081,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.58813,0.09226,0.05385],"object_pos_start":[0.53871,0.00124,0.11652],"object_to_goal_dist_end":0.16344,"object_to_goal_dist_start":0.205,"object_z_max":0.12025,"peak_contact_force":0.0,"phase_name":"move_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":16344.0,"raw_peak_contact_force":0.24579,"subtask_id":"reach_goal","tcp_end":[0.583,0.07711,0.16052],"tcp_start":[0.52933,0.00088,0.14587],"tcp_to_object_dist_end":0.10786,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.59248,0.09999,0.01602],"object_pos_start":[0.58813,0.09226,0.05385],"object_to_goal_dist_end":0.19254,"object_to_goal_dist_start":0.16344,"object_z_max":0.05385,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":742.0,"raw_peak_contact_force":1.31168,"tcp_end":[0.57703,0.07631,0.18247],"tcp_start":[0.583,0.07711,0.16052],"tcp_to_object_dist_end":0.16884,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.59248,0.09999,0.01602],"object_pos_start":[0.59248,0.09999,0.01602],"object_to_goal_dist_end":0.19254,"object_to_goal_dist_start":0.19254,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12264,"tcp_end":[0.57514,0.08598,0.34548],"tcp_start":[0.57703,0.07631,0.18247],"tcp_to_object_dist_end":0.33021,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.44949,"average_solve_count":198.0,"average_success_count":198.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_z":0.0829,"descend_1.contact_force_threshold":4.83573,"descend_1.descend_speed":0.07132,"descend_1.grasp_offset_z":0.11971,"descend_to_grasp.descend_grasp_speed":0.02586,"descend_to_grasp.grasp_approach_z":0.02025,"descend_to_grasp.grasp_pose_tol":0.00667,"grasp_1.grasp_time":2.72645,"lift_1.lift_distance":0.13439},"optimized_scores":{"best_composite_score":0.23049,"best_fitness_score":0.73549,"best_task_score":0.53608},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":223.0,"contact_point_centroid":[0.5683,0.16312,-0.00472],"force_p95":0.93217,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.04181,"mean_force":0.29013,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57228,0.14433,0.12157]},{"body_a":"world","body_b":"grasp_target","contact_count":146.0,"contact_point_centroid":[0.52778,0.0293,-0.00117],"force_p95":0.33218,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.4658,"mean_force":0.06922,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51812,0.02973,0.04548]},{"body_a":"world","body_b":"grasp_target","contact_count":3965.0,"contact_point_centroid":[0.55871,0.16585,-0.002],"force_p95":0.12897,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.35242,"mean_force":0.1241,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.56897,0.15814,0.21378]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":13315.0,"contact_point_centroid":[0.51743,0.04862,0.10283],"force_p95":0.08716,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30368,"mean_force":0.05898,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51561,0.02957,0.10066]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13718.0,"contact_point_centroid":[0.51682,0.0106,0.09991],"force_p95":0.0947,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28403,"mean_force":0.05669,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51557,0.02957,0.09789]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12126.0,"contact_point_centroid":[0.55334,0.07288,0.13533],"force_p95":0.11888,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21838,"mean_force":0.07798,"phase_index":5.0,"phase_name":"move_to_goal","phase_type":"approach","tcp_position_centroid":[0.54794,0.09159,0.13499]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":754.0,"contact_point_centroid":[0.58143,0.16398,0.10684],"force_p95":0.15074,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2099,"mean_force":0.08936,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.5765,0.14553,0.10889]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12907.0,"contact_point_centroid":[0.5532,0.11013,0.13555],"force_p95":0.09686,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20515,"mean_force":0.07329,"phase_index":5.0,"phase_name":"move_to_goal","phase_type":"approach","tcp_position_centroid":[0.54792,0.0915,0.13506]},{"body_a":"world","body_b":"grasp_target","contact_count":1804.0,"contact_point_centroid":[0.53052,0.03068,-0.0021],"force_p95":0.14543,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.1972,"mean_force":0.12997,"phase_index":3.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52023,0.02988,0.04426]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":515.0,"contact_point_centroid":[0.58101,0.12739,0.10735],"force_p95":0.13781,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18193,"mean_force":0.08564,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57692,0.14565,0.10944]},{"body_a":"world","body_b":"grasp_target","contact_count":2336.0,"contact_point_centroid":[0.5305,0.03079,-0.00194],"force_p95":0.13103,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12283,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51097,0.01398,0.20948]},{"body_a":"world","body_b":"grasp_target","contact_count":1416.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":2.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.52229,0.0292,0.083]},{"body_a":"world","body_b":"grasp_target","contact_count":56.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12262,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12262,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52357,0.02844,0.11932]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5820.0,"contact_point_centroid":[0.51995,0.01067,0.04563],"force_p95":0.07094,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12124,"mean_force":0.04499,"phase_index":3.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51974,0.02985,0.0437]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5934.0,"contact_point_centroid":[0.51993,0.04906,0.04555],"force_p95":0.07131,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.074,"mean_force":0.045,"phase_index":3.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51975,0.02985,0.0437]}],"total_contact_groups":15},"final_pose_error":0.03837,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.5585,0.16597,0.02602],"final_tcp_position":[0.56971,0.15358,0.29713],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":81.14225,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":585.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2336.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.52432,0.02838,0.12023],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.09444,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":14.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":81.14225,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":56.0,"raw_peak_contact_force":0.12262,"subtask_id":"reach_object","tcp_end":[0.52297,0.02845,0.1188],"tcp_start":[0.52432,0.02838,0.12023],"tcp_to_object_dist_end":0.09311,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":354.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1416.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.52474,0.03018,0.04954],"tcp_start":[0.52297,0.02845,0.1188],"tcp_to_object_dist_end":0.02422,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53043,0.03014,0.0257],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18407,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.14197,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":13558.0,"raw_peak_contact_force":0.1972,"tcp_end":[0.51972,0.02985,0.04367],"tcp_start":[0.51972,0.02985,0.04367],"tcp_to_object_dist_end":0.02093,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":26.0,"n_steps":754.0,"n_steps_budget":840.0,"object_pos_end":[0.5283,0.02969,0.14135],"object_pos_start":[0.53043,0.03012,0.02571],"object_to_goal_dist_end":0.16923,"object_to_goal_dist_start":0.18407,"object_z_max":0.14123,"peak_contact_force":0.0982,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":27179.0,"raw_peak_contact_force":0.4658,"subtask_id":"lift_object","tcp_end":[0.51589,0.0296,0.16552],"tcp_start":[0.51972,0.02985,0.04367],"tcp_to_object_dist_end":0.02717,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":19.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.58402,0.1463,0.08041],"object_pos_start":[0.5283,0.02969,0.14135],"object_to_goal_dist_end":0.04599,"object_to_goal_dist_start":0.16923,"object_z_max":0.14139,"peak_contact_force":0.13638,"phase_name":"move_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":25033.0,"raw_peak_contact_force":0.21838,"subtask_id":"reach_goal","tcp_end":[0.57887,0.14602,0.11258],"tcp_start":[0.51589,0.0296,0.16552],"tcp_to_object_dist_end":0.03258,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.56995,0.15988,0.02639],"object_pos_start":[0.58402,0.1463,0.08041],"object_to_goal_dist_end":0.08957,"object_to_goal_dist_start":0.04599,"object_z_max":0.08041,"peak_contact_force":0.3559,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1492.0,"raw_peak_contact_force":1.04181,"tcp_end":[0.57214,0.1443,0.13428],"tcp_start":[0.57887,0.14602,0.11258],"tcp_to_object_dist_end":0.10903,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5585,0.16597,0.02602],"object_pos_start":[0.56995,0.15988,0.02639],"object_to_goal_dist_end":0.09352,"object_to_goal_dist_start":0.08957,"object_z_max":0.0265,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3965.0,"raw_peak_contact_force":0.35242,"tcp_end":[0.56971,0.15358,0.29713],"tcp_start":[0.57214,0.1443,0.13428],"tcp_to_object_dist_end":0.27162,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```