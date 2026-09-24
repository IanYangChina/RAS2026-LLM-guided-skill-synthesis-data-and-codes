## Search State

- **Seed**: 3
- **Iteration**: 11 / 15

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

## Current Skill (Q=-0.032) — your mutation base

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

- **Composite score**: -0.032
- **task_score** (E): 0.441
- **fitness_score**: 0.696  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.153
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.880

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1394 |
| descend_1 | 1.00 | 1.00 | 0.0019 |
| descend_to_grasp | 1.00 | 1.00 | 0.1226 |
| grasp_1 | 0.00 | 1.00 | 0.0000 |
| lift_1 | 1.00 | 1.00 | 0.1163 |
| move_to_goal | 0.00 | 0.33 | 0.0847 |
| descend_place | 0.00 | 1.00 | 0.1111 |
| release_1 | 1.00 | 1.00 | 0.0231 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.507, 0.002, 0.167) | (0.511, 0.002, 0.030)→(0.511, 0.002, 0.026) | 0.244→0.246 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / force_exceeded | (0.507, 0.002, 0.167)→(0.506, 0.002, 0.166) | (0.511, 0.002, 0.026)→(0.511, 0.002, 0.026) | 0.246→0.246 | 1.00 / 4.000 | 81.142 | 0.123 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.506, 0.002, 0.166)→(0.506, 0.002, 0.043) | (0.511, 0.002, 0.026)→(0.511, 0.002, 0.026) | 0.246→0.246 | 1.00 / 4.000 | 31.967 | 0.123 |
| grasp_1 | grasp | 0.00 / guard_failure | (0.501, 0.002, 0.038)→(0.501, 0.002, 0.038) | (0.511, 0.002, 0.026)→(0.511, 0.002, 0.026) | 0.246→0.246 | 1.00 / 44.000 | 0.135 | 0.176 |
| lift_1 | lift | 1.00 / step_budget | (0.501, 0.002, 0.038)→(0.497, 0.002, 0.154) | (0.511, 0.002, 0.026)→(0.511, 0.002, 0.135) | 0.246→0.216 | 1.00 / 26.000 | 0.102 | 0.540 |
| move_to_goal | approach | 0.00 / guard_failure | (0.497, 0.002, 0.154)→(0.539, 0.067, 0.186) | (0.511, 0.002, 0.135)→(0.549, 0.074, 0.109) | 0.216→0.147 | 0.33 / 8.000 | 0.033 | 0.218 |
| descend_place | descend | 0.00 / step_budget | (0.503, 0.052, 0.177)→(0.567, 0.135, 0.141) | (0.510, 0.052, 0.148)→(0.588, 0.114, 0.016) | 0.201→0.142 | 1.00 / 4.000 | 0.120 | 1.294 |
| release_1 | release | 1.00 / step_budget | (0.567, 0.135, 0.141)→(0.561, 0.134, 0.163) | (0.588, 0.114, 0.016)→(0.588, 0.113, 0.016) | 0.142→0.143 | 1.00 / 4.000 | 0.123 | 0.129 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.596
- phase_score: 0.536
- phase_breakdown.lift_object_score: 0.714
- phase_breakdown.reach_object_score: 0.364
- phase_breakdown.reach_goal_score: 0.531
- grasp_place_fitness: 0.777

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.777
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.596
- **Median Q (composite search score)**: -0.069
- **K-run variance**: 0.0046
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.291


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.83039,"average_solve_count":283.0,"average_success_count":283.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_z":0.11781,"descend_1.contact_force_threshold":5.94923,"descend_1.descend_speed":0.05604,"descend_1.grasp_offset_z":0.08472,"descend_place.place_speed":0.0369,"descend_place.place_z":0.0103,"descend_to_grasp.descend_grasp_speed":0.02033,"descend_to_grasp.grasp_approach_z":0.01636,"descend_to_grasp.grasp_pose_tol":0.00525,"grasp_1.bilateral_grasp_threshold":0.11632,"grasp_1.grasp_time":2.20506,"lift_1.lift_distance":0.11736,"move_to_goal.transport_speed":0.04039,"move_to_goal.transport_z":0.13991},"optimized_scores":{"best_composite_score":-0.08907,"best_fitness_score":0.66593,"best_task_score":0.38619},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":283.0,"contact_point_centroid":[0.5865,0.11313,-0.00458],"force_p95":0.99663,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.29429,"mean_force":0.26138,"phase_index":6.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.5656,0.13271,0.14213]},{"body_a":"world","body_b":"grasp_target","contact_count":123.0,"contact_point_centroid":[0.45553,-0.0256,-0.00112],"force_p95":0.32451,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.47575,"mean_force":0.05857,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44828,-0.02578,0.04243]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12325.0,"contact_point_centroid":[0.44684,-0.04472,0.09176],"force_p95":0.08926,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29659,"mean_force":0.05566,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44582,-0.02567,0.09005]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12035.0,"contact_point_centroid":[0.44679,-0.00662,0.09248],"force_p95":0.09055,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29599,"mean_force":0.0565,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44583,-0.02567,0.09047]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8392.0,"contact_point_centroid":[0.535,0.10603,0.15782],"force_p95":0.13612,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24081,"mean_force":0.09273,"phase_index":6.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.52918,0.0875,0.15871]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9727.0,"contact_point_centroid":[0.53708,0.07197,0.15642],"force_p95":0.11319,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20438,"mean_force":0.08026,"phase_index":6.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.53135,0.09022,0.15768]},{"body_a":"world","body_b":"grasp_target","contact_count":1804.0,"contact_point_centroid":[0.45856,-0.02624,-0.00205],"force_p95":0.13488,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.16718,"mean_force":0.12654,"phase_index":3.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.45006,-0.02585,0.04109]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":15083.0,"contact_point_centroid":[0.47963,-0.00275,0.16213],"force_p95":0.09421,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1569,"mean_force":0.06317,"phase_index":5.0,"phase_name":"move_to_goal","phase_type":"approach","tcp_position_centroid":[0.47519,0.01598,0.1612]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":14427.0,"contact_point_centroid":[0.47987,0.03499,0.16227],"force_p95":0.0944,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14935,"mean_force":0.06562,"phase_index":5.0,"phase_name":"move_to_goal","phase_type":"approach","tcp_position_centroid":[0.47537,0.01622,0.1613]},{"body_a":"world","body_b":"grasp_target","contact_count":1760.0,"contact_point_centroid":[0.45856,-0.02632,-0.00192],"force_p95":0.13362,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.1229,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.47919,-0.0115,0.22907]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.58831,0.11338,-0.00196],"force_p95":0.1268,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12866,"mean_force":0.12223,"phase_index":7.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.56304,0.13401,0.14329]},{"body_a":"world","body_b":"grasp_target","contact_count":80.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.45821,-0.02386,0.15527]},{"body_a":"world","body_b":"grasp_target","contact_count":2912.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":2.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.45422,-0.02489,0.09692]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5834.0,"contact_point_centroid":[0.4498,-0.00665,0.04258],"force_p95":0.06911,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11074,"mean_force":0.04498,"phase_index":3.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44962,-0.02583,0.04066]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5899.0,"contact_point_centroid":[0.44981,-0.04503,0.04253],"force_p95":0.06936,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08877,"mean_force":0.04502,"phase_index":3.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44962,-0.02583,0.04066]},{"body_a":"left_finger","body_b":"right_finger","contact_count":193.0,"contact_point_centroid":[0.56605,0.13476,0.14069],"force_p95":0.0157,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01703,"mean_force":0.01146,"phase_index":7.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.56577,0.13475,0.13838]}],"total_contact_groups":16},"final_pose_error":0.09781,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.58831,0.11338,0.01602],"final_tcp_position":[0.56747,0.13502,0.1413],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":81.14225,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":441.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1760.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.45897,-0.02374,0.15716],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13117,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":20.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":81.14225,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":80.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.45761,-0.02391,0.15319],"tcp_start":[0.45897,-0.02374,0.15716],"tcp_to_object_dist_end":0.12719,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":728.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":14.63621,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2912.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.45411,-0.026,0.04504],"tcp_start":[0.45761,-0.02391,0.15319],"tcp_to_object_dist_end":0.01954,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45848,-0.02595,0.02584],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30347,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.13318,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":13537.0,"raw_peak_contact_force":0.16718,"tcp_end":[0.4496,-0.02583,0.04064],"tcp_start":[0.4496,-0.02583,0.04064],"tcp_to_object_dist_end":0.01726,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":27.0,"n_steps":663.0,"n_steps_budget":750.0,"object_pos_end":[0.45891,-0.02568,0.12605],"object_pos_start":[0.45848,-0.02594,0.02585],"object_to_goal_dist_end":0.29011,"object_to_goal_dist_start":0.30346,"object_z_max":0.12594,"peak_contact_force":0.10248,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":24483.0,"raw_peak_contact_force":0.47575,"subtask_id":"lift_object","tcp_end":[0.44589,-0.02566,0.14695],"tcp_start":[0.4496,-0.02583,0.04064],"tcp_to_object_dist_end":0.02462,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":24.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5095,0.05152,0.14845],"object_pos_start":[0.45891,-0.02568,0.12605],"object_to_goal_dist_end":0.20071,"object_to_goal_dist_start":0.29011,"object_z_max":0.14843,"peak_contact_force":0.09868,"phase_name":"move_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":29510.0,"raw_peak_contact_force":0.1569,"subtask_id":"reach_goal","tcp_end":[0.50326,0.05158,0.17679],"tcp_start":[0.44589,-0.02566,0.14695],"tcp_to_object_dist_end":0.02902,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.58834,0.11359,0.01642],"object_pos_start":[0.5095,0.05152,0.14845],"object_to_goal_dist_end":0.14228,"object_to_goal_dist_start":0.20071,"object_z_max":0.14845,"peak_contact_force":0.12035,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":18402.0,"raw_peak_contact_force":1.29429,"subtask_id":"reach_goal","tcp_end":[0.56747,0.13502,0.1413],"tcp_start":[0.50326,0.05158,0.17679],"tcp_to_object_dist_end":0.12841,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.58831,0.11338,0.01602],"object_pos_start":[0.58834,0.11359,0.01642],"object_to_goal_dist_end":0.14271,"object_to_goal_dist_start":0.14228,"object_z_max":0.01649,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":993.0,"raw_peak_contact_force":0.12866,"tcp_end":[0.56131,0.13355,0.16347],"tcp_start":[0.56747,0.13502,0.1413],"tcp_to_object_dist_end":0.15125,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.96651,"average_solve_count":209.0,"average_success_count":209.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_z":0.1472,"descend_1.contact_force_threshold":7.98528,"descend_1.descend_speed":0.05946,"descend_1.grasp_offset_z":0.10823,"descend_place.place_speed":0.03961,"descend_place.place_z":0.00661,"descend_to_grasp.descend_grasp_speed":0.02381,"descend_to_grasp.grasp_approach_z":0.01274,"descend_to_grasp.grasp_pose_tol":0.00792,"grasp_1.bilateral_grasp_threshold":0.07099,"grasp_1.grasp_time":3.33201,"lift_1.lift_distance":0.15071,"move_to_goal.transport_speed":0.06076,"move_to_goal.transport_z":0.12315},"optimized_scores":{"best_composite_score":-0.06905,"best_fitness_score":0.64429,"best_task_score":0.33987},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":147.0,"contact_point_centroid":[0.54183,0.00089,-0.00113],"force_p95":0.37273,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54369,"mean_force":0.07909,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.5319,0.00091,0.03983]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":14320.0,"contact_point_centroid":[0.531,0.01987,0.10085],"force_p95":0.10031,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31135,"mean_force":0.0618,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52932,0.00087,0.09891]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":15072.0,"contact_point_centroid":[0.531,-0.01805,0.10005],"force_p95":0.09599,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30671,"mean_force":0.05912,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.5293,0.00087,0.09843]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7745.0,"contact_point_centroid":[0.54769,0.00336,0.18861],"force_p95":0.15235,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24866,"mean_force":0.09525,"phase_index":5.0,"phase_name":"move_to_goal","phase_type":"approach","tcp_position_centroid":[0.5421,0.02175,0.18866]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8189.0,"contact_point_centroid":[0.54864,0.04124,0.18926],"force_p95":0.12776,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16767,"mean_force":0.09007,"phase_index":5.0,"phase_name":"move_to_goal","phase_type":"approach","tcp_position_centroid":[0.54298,0.02297,0.18963]},{"body_a":"world","body_b":"grasp_target","contact_count":1804.0,"contact_point_centroid":[0.5443,0.0011,-0.00204],"force_p95":0.1309,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.14981,"mean_force":0.12562,"phase_index":3.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53405,0.00095,0.03872]},{"body_a":"world","body_b":"grasp_target","contact_count":1640.0,"contact_point_centroid":[0.54431,0.00113,-0.00192],"force_p95":0.13462,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12292,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51693,0.00047,0.24105]},{"body_a":"world","body_b":"grasp_target","contact_count":24.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.53627,0.00097,0.18255]},{"body_a":"world","body_b":"grasp_target","contact_count":2256.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":2.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.5358,0.00098,0.11181]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5844.0,"contact_point_centroid":[0.53377,-0.01824,0.04005],"force_p95":0.06825,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10349,"mean_force":0.04502,"phase_index":3.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53357,0.00094,0.03815]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5872.0,"contact_point_centroid":[0.53375,0.02013,0.04003],"force_p95":0.06836,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08498,"mean_force":0.04503,"phase_index":3.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53357,0.00094,0.03815]}],"total_contact_groups":11},"final_pose_error":0.17783,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.5726,0.05757,0.08877],"final_tcp_position":[0.55974,0.04529,0.20854],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":81.14225,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":411.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1640.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.53643,0.00097,0.18311],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.15729,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":6.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":81.14225,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":24.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.53608,0.00096,0.18177],"tcp_start":[0.53643,0.00097,0.18311],"tcp_to_object_dist_end":0.15596,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":564.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":81.14225,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2256.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.53872,0.00103,0.04432],"tcp_start":[0.53608,0.00096,0.18177],"tcp_to_object_dist_end":0.01914,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5442,0.00098,0.02587],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25035,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.1302,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":13520.0,"raw_peak_contact_force":0.14981,"tcp_end":[0.53354,0.00094,0.03812],"tcp_start":[0.53354,0.00094,0.03812],"tcp_to_object_dist_end":0.01624,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":873.0,"n_steps_budget":960.0,"object_pos_end":[0.54252,0.00092,0.15569],"object_pos_start":[0.5442,0.00098,0.02588],"object_to_goal_dist_end":0.19235,"object_to_goal_dist_start":0.25035,"object_z_max":0.15558,"peak_contact_force":0.09855,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":29539.0,"raw_peak_contact_force":0.54369,"subtask_id":"lift_object","tcp_end":[0.52975,0.00088,0.17614],"tcp_start":[0.53354,0.00094,0.03812],"tcp_to_object_dist_end":0.02411,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":891.0,"n_steps_budget":1000.0,"object_pos_end":[0.5726,0.05757,0.08877],"object_pos_start":[0.54252,0.00092,0.15569],"object_to_goal_dist_end":0.16188,"object_to_goal_dist_start":0.19235,"object_z_max":0.1764,"peak_contact_force":0.0,"phase_name":"move_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":15934.0,"raw_peak_contact_force":0.24866,"subtask_id":"reach_goal","tcp_end":[0.55974,0.04529,0.20854],"tcp_start":[0.52975,0.00088,0.17614],"tcp_to_object_dist_end":0.12108,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.89552,"average_solve_count":201.0,"average_success_count":201.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_z":0.12518,"descend_1.contact_force_threshold":8.23414,"descend_1.descend_speed":0.0314,"descend_1.grasp_offset_z":0.09426,"descend_place.place_speed":0.04321,"descend_place.place_z":0.01071,"descend_to_grasp.descend_grasp_speed":0.02141,"descend_to_grasp.grasp_approach_z":0.01006,"descend_to_grasp.grasp_pose_tol":0.00666,"grasp_1.bilateral_grasp_threshold":0.09019,"grasp_1.grasp_time":1.65645,"lift_1.lift_distance":0.1168,"move_to_goal.transport_speed":0.08825,"move_to_goal.transport_z":0.10948},"optimized_scores":{"best_composite_score":0.06329,"best_fitness_score":0.77663,"best_task_score":0.59563},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":146.0,"contact_point_centroid":[0.52761,0.02923,-0.00118],"force_p95":0.42493,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.5998,"mean_force":0.0838,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51839,0.02979,0.03577]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11978.0,"contact_point_centroid":[0.51681,0.04872,0.08277],"force_p95":0.09196,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31943,"mean_force":0.05711,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51578,0.02962,0.08083]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12349.0,"contact_point_centroid":[0.51678,0.01061,0.08422],"force_p95":0.08692,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3065,"mean_force":0.05533,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51578,0.02962,0.08228]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10247.0,"contact_point_centroid":[0.53703,0.04665,0.15139],"force_p95":0.12893,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.249,"mean_force":0.08573,"phase_index":5.0,"phase_name":"move_to_goal","phase_type":"approach","tcp_position_centroid":[0.53283,0.06517,0.15167]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10779.0,"contact_point_centroid":[0.53795,0.08411,0.1518],"force_p95":0.12732,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22876,"mean_force":0.08176,"phase_index":5.0,"phase_name":"move_to_goal","phase_type":"approach","tcp_position_centroid":[0.53308,0.06566,0.15188]},{"body_a":"world","body_b":"grasp_target","contact_count":1804.0,"contact_point_centroid":[0.53052,0.03063,-0.0021],"force_p95":0.14614,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21108,"mean_force":0.13023,"phase_index":3.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52052,0.02994,0.03455]},{"body_a":"world","body_b":"grasp_target","contact_count":1840.0,"contact_point_centroid":[0.5305,0.03079,-0.00192],"force_p95":0.13354,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12289,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51086,0.01362,0.2307]},{"body_a":"world","body_b":"grasp_target","contact_count":2412.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":2.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.52292,0.02897,0.09893]},{"body_a":"world","body_b":"grasp_target","contact_count":4.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12262,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12262,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52413,0.02786,0.16202]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5811.0,"contact_point_centroid":[0.52023,0.01073,0.03592],"force_p95":0.07089,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11952,"mean_force":0.04498,"phase_index":3.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52003,0.0299,0.03399]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5940.0,"contact_point_centroid":[0.52021,0.04912,0.03585],"force_p95":0.07125,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08306,"mean_force":0.04504,"phase_index":3.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52003,0.02991,0.034]}],"total_contact_groups":11},"final_pose_error":0.09871,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.56584,0.11227,0.08887],"final_tcp_position":[0.55539,0.1044,0.17163],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":81.14225,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":461.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1840.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.52413,0.02786,0.16202],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13619,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":81.14225,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4.0,"raw_peak_contact_force":0.12262,"subtask_id":"reach_object","tcp_end":[0.52405,0.0279,0.16178],"tcp_start":[0.52413,0.02786,0.16202],"tcp_to_object_dist_end":0.13595,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":603.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2412.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.5251,0.03024,0.03982],"tcp_start":[0.52405,0.0279,0.16178],"tcp_to_object_dist_end":0.01483,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5304,0.03007,0.02569],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18413,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.14228,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":13555.0,"raw_peak_contact_force":0.21108,"tcp_end":[0.52001,0.0299,0.03397],"tcp_start":[0.52001,0.0299,0.03397],"tcp_to_object_dist_end":0.01328,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":26.0,"n_steps":663.0,"n_steps_budget":750.0,"object_pos_end":[0.53025,0.02976,0.12403],"object_pos_start":[0.5304,0.03006,0.02571],"object_to_goal_dist_end":0.16578,"object_to_goal_dist_start":0.18414,"object_z_max":0.12392,"peak_contact_force":0.10433,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":24473.0,"raw_peak_contact_force":0.5998,"subtask_id":"lift_object","tcp_end":[0.51594,0.02964,0.13843],"tcp_start":[0.52001,0.0299,0.03397],"tcp_to_object_dist_end":0.0203,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":992.0,"n_steps_budget":1000.0,"object_pos_end":[0.56584,0.11227,0.08887],"object_pos_start":[0.53025,0.02976,0.12403],"object_to_goal_dist_end":0.07772,"object_to_goal_dist_start":0.16578,"object_z_max":0.14378,"peak_contact_force":0.0,"phase_name":"move_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":21026.0,"raw_peak_contact_force":0.249,"subtask_id":"reach_goal","tcp_end":[0.55539,0.1044,0.17163],"tcp_start":[0.51594,0.02964,0.13843],"tcp_to_object_dist_end":0.08378,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
```