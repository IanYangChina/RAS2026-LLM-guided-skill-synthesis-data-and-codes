## Search State

- **Seed**: 6
- **Iteration**: 14 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 13 | approach → descend → grasp → lift → approach → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.0553 | 0.20 | ❌ rejected |
| 12 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 11 | -0.0947 | 0.26 | ❌ rejected |
| 11 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 9 | 0.0448 | 0.33 | ✅ accepted |
| 10 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 9 | 0.0327 | 0.31 | ✅ accepted |
| 9 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.0676 | 0.29 | ✅ accepted |

**Proposal policy**: task_score is 0.20 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
- task_score stagnant: change coupled targets, parameters, terminations, phase types, controls, subtasks, or ordering when evidence shows they need to change together.
A HOLD wastes an iteration when task_score is below 0.9.

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
- Frozen realised-scene SHA-256: `584133b5261cffac0dd4282704ff39e97bf4d452e60b02507679bbdea5a4de22`
- Frozen object start: [0.5038164351471943, -0.015672913018666156, 0.03]
- Frozen task target: [0.5869067239795378, 0.18744967655878825, 0.24811674852797]
- Goal object position: (0.5869067239795378, 0.18744967655878825, 0.24811674852797)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.5869067239795378, 0.18744967655878825, 0.24811674852797)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.5038164351471943, -0.015672913018666156, 0.03)
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
  frozen_object_start: [0.5038, -0.0157, 0.03]
  frozen_task_target: [0.5869, 0.1874, 0.2481]
  frozen_object_starts: {'grasp_target': [0.5038164351471943, -0.015672913018666156, 0.03]}
  frozen_targets: {'place_target': [0.5869067239795378, 0.18744967655878825, 0.24811674852797]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: 584133b5261cffac0dd4282704ff39e97bf4d452e60b02507679bbdea5a4de22

## Subtask Layer

**Mode**: fixed (subtask targets are defined by the task configuration)

Available subtask IDs for phase binding:
| Subtask ID | Anchor | Target offset (m) | Metric | CMA-ES offset param |
|---|---|---|---|---|
| approach_1 | object | (0.00, 0.00, 0.00) | distance | approach_height |
| descend_1 | object | (0.00, 0.00, 0.02) | distance | grasp_z_offset |
| grasp_1 | object | (0.00, 0.00, 0.02) | contact | — |
| transport_arc | goal | (0.00, 0.00, 0.00) | distance | — |
| release_1 | goal | (0.00, 0.00, 0.00) | distance | — |

Annotate phases with `subtask_id: <id>` to bind them to a subtask target.
- A phase bound to a subtask receives a navigation waypoint computed from that subtask's anchor and offset.
- Only the **last phase** bound to a given subtask is used for subtask scoring.
- Phases without `subtask_id` are not scored against subtasks but still execute normally.

## Current Skill (Q=0.055) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: approach_1
  anchor: object
- id: descend_1
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.02
- id: grasp_1
  anchor: object
  metric: contact
  offset:
  - 0.0
  - 0.0
  - 0.02
- id: transport_arc
- id: release_1
phases:
- id: approach_1
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
    - 0.0
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.12
      binds_to:
      - path: target.offset.z
        mode: add
  subtask_id: approach_1
- id: descend_1
  type: descend
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
    - 0.0
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    grasp_z_offset:
      type: scalar
      range:
      - 0.0
      - 0.05
      default: 0.02
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: descend_1
- id: grasp_1
  type: grasp
  control: position_control
  termination: grasp_success
  end_effector_action: force_grasp
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    orientation:
      mode: keep_current
  parameters:
    grasp_retry_x:
      type: scalar
      range:
      - -0.01
      - 0.01
      default: 0.0
      binds_to:
      - path: retry.offset.x
        mode: replace
    grasp_retry_y:
      type: scalar
      range:
      - -0.01
      - 0.01
      default: 0.0
      binds_to:
      - path: retry.offset.y
        mode: replace
  guards:
  - id: grasp_check
    when: after_phase
    predicate: bilateral_grasp
    threshold: 1.0
    on_failure: retry
  retries:
    max_attempts: 3
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - 0.0
  subtask_id: grasp_1
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
      distance: 0.15
      axis: world_z
      mode: add_to_offset
      sign: positive
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.1
      - 0.25
      default: 0.15
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    lift_retry_z:
      type: scalar
      range:
      - 0.0
      - 0.02
      default: 0.0
      binds_to:
      - path: retry.offset.z
        mode: replace
  guards:
  - id: lift_check
    when: after_phase
    predicate: object_lifted
    threshold: 0.05
    on_failure: retry
  retries:
    max_attempts: 3
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - 0.0
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
    - 0.0
    tolerance: 0.03
    orientation:
      mode: keep_current
  parameters:
    transport_arc_height:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.12
      binds_to:
      - path: generator.arc_height
        mode: replace
    transport_speed:
      type: scalar
      range:
      - 0.1
      - 0.4
      default: 0.2
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: transport_grasp_check
    when: during_phase
    predicate: object_lifted
    threshold: 0.05
    on_failure: abort
  subtask_id: transport_arc
- id: place_descend_1
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
    offset_along_axis:
      distance: 0.07
      axis: world_z
      mode: add_to_offset
      sign: negative
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    place_height:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.07
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
- id: release_1
  type: release
  control: position_control
  termination: pose_tolerance
  end_effector_action: open
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    orientation:
      mode: keep_current
  subtask_id: release_1

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (add)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - grasp_z_offset: status=consumed; consumers=target.offset.z (replace)
- **grasp_1** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - grasp_retry_x: status=consumed; consumers=retry.offset.x (replace)
    - grasp_retry_y: status=consumed; consumers=retry.offset.y (replace)
  - guards:
    - id=grasp_check, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=1.0
  - retries: max_attempts=3, strategy=offset_target, offset=[0.0, 0.0, 0.0]
- **lift_1** (`lift`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.15, mode=add_to_offset, sign=positive}, tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - lift_retry_z: status=consumed; consumers=retry.offset.z (replace)
  - guards:
    - id=lift_check, when=after_phase, predicate=object_lifted, on_failure=retry, threshold=0.05
  - retries: max_attempts=3, strategy=offset_target, offset=[0.0, 0.0, 0.0]
- **transport_1** (`approach`)
  - target: source=yaml, anchor=task_goal, entity=placement_surface, offset=[0.0, 0.0, 0.0], tolerance=0.03
  - orientation: mode=keep_current
  - parameter_bindings:
    - transport_arc_height: status=consumed; consumers=generator.arc_height (replace)
    - transport_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=transport_grasp_check, when=during_phase, predicate=object_lifted, on_failure=abort, threshold=0.05
- **place_descend_1** (`descend`)
  - target: source=yaml, anchor=task_goal, entity=placement_surface, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.07, mode=add_to_offset, sign=negative}, tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - place_height: status=consumed; consumers=target.offset_along_axis.distance (replace)
- **release_1** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.055
- **task_score** (E): 0.197
- **fitness_score**: 0.575  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.520

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1374 |
| descend_1 | 1.00 | 1.00 | 0.1282 |
| grasp_1 | 1.00 | 1.00 | 0.0118 |
| lift_1 | 1.00 | 1.00 | 0.1222 |
| transport_1 | 1.00 | 1.00 | 0.1975 |
| release_1 | 1.00 | 1.00 | 0.0214 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.496, 0.021, 0.168) | (0.500, 0.024, 0.030)→(0.500, 0.024, 0.026) | 0.269→0.271 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.496, 0.021, 0.168)→(0.495, 0.024, 0.040) | (0.500, 0.024, 0.026)→(0.500, 0.024, 0.026) | 0.271→0.271 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.495, 0.024, 0.040)→(0.487, 0.023, 0.032) | (0.500, 0.024, 0.026)→(0.500, 0.023, 0.026) | 0.271→0.272 | 1.00 / 43.000 | 0.148 | 0.219 |
| lift_1 | lift | 1.00 / step_budget | (0.487, 0.023, 0.032)→(0.483, 0.023, 0.154) | (0.500, 0.023, 0.026)→(0.497, 0.023, 0.135) | 0.272→0.218 | 1.00 / 22.667 | 0.119 | 0.613 |
| transport_1 | approach | 1.00 / step_budget | (0.483, 0.023, 0.154)→(0.582, 0.174, 0.222) | (0.497, 0.023, 0.135)→(0.501, 0.065, 0.016) | 0.218→0.253 | 1.00 / 8.333 | 94253.027 | 1.767 |
| release_1 | release | 1.00 / step_budget | (0.582, 0.174, 0.222)→(0.578, 0.172, 0.243) | (0.501, 0.065, 0.016)→(0.501, 0.065, 0.016) | 0.253→0.253 | 1.00 / 4.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.305
- phase_score: 0.645
- phase_breakdown.transport_arc_score: 0.637
- phase_breakdown.descend_1_score: 0.758
- phase_breakdown.grasp_1_score: 1.000
- phase_breakdown.approach_1_score: 0.031
- phase_breakdown.release_1_score: 0.445
- grasp_place_fitness: 0.631

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.631
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.305
- **Median Q (composite search score)**: 0.034
- **K-run variance**: 0.0016
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.385


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `daf90631fcbaf423e19452d0c9b90b9715013985cc94ef12ca0cd881e96195aa`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `94660347aa4f41f6801e53bd449f8df59691da8bebfa4fef4947a3513fe04781`; realized-scene SHA-256: `584133b5261cffac0dd4282704ff39e97bf4d452e60b02507679bbdea5a4de22`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50382,-0.01567,0.03]},{"name":"goal","value":[0.58691,0.18745,0.24812]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.50382,-0.01567,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.58691,0.18745,0.24812]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.21782,"average_solve_count":101.0,"average_success_count":101.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.10555,"descend_1.grasp_z_offset":0.01309,"grasp_1.grasp_retry_x":0.00034,"grasp_1.grasp_retry_y":0.00019,"lift_1.lift_height":0.11782,"lift_1.lift_retry_z":0.00196,"transport_1.transport_arc_height":0.17573,"transport_1.transport_speed":0.32102},"optimized_scores":{"best_composite_score":0.02044,"best_fitness_score":0.54044,"best_task_score":0.13876},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2917.0,"contact_point_centroid":[0.49654,0.02713,-0.00233],"force_p95":0.1268,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.66167,"mean_force":0.13809,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.52614,0.06908,0.26227]},{"body_a":"world","body_b":"grasp_target","contact_count":132.0,"contact_point_centroid":[0.50105,-0.01504,-0.00111],"force_p95":0.37401,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.49217,"mean_force":0.06923,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48935,-0.0153,0.04079]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9880.0,"contact_point_centroid":[0.48949,0.00363,0.08751],"force_p95":0.10543,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32498,"mean_force":0.06798,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48678,-0.01526,0.08554]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1793.0,"contact_point_centroid":[0.49072,0.00411,0.16144],"force_p95":0.15848,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3089,"mean_force":0.09747,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.48476,-0.0143,0.1621]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1740.0,"contact_point_centroid":[0.49065,-0.03293,0.16041],"force_p95":0.16626,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29813,"mean_force":0.09829,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.48471,-0.01448,0.16082]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10505.0,"contact_point_centroid":[0.48939,-0.0341,0.08639],"force_p95":0.10148,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29001,"mean_force":0.06471,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48681,-0.01526,0.08468]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50381,-0.01556,-0.00204],"force_p95":0.13388,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.16252,"mean_force":0.12575,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49199,-0.01534,0.0403]},{"body_a":"world","body_b":"grasp_target","contact_count":1896.0,"contact_point_centroid":[0.50382,-0.01567,-0.00193],"force_p95":0.13354,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12288,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4989,-0.00695,0.22236]},{"body_a":"world","body_b":"grasp_target","contact_count":1220.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49807,-0.0148,0.0958]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.49643,0.02712,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.56568,0.15429,0.26743]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4113.0,"contact_point_centroid":[0.4913,0.00388,0.04184],"force_p95":0.07647,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11763,"mean_force":0.05182,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49083,-0.01532,0.03907]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4886.0,"contact_point_centroid":[0.49137,-0.0344,0.04092],"force_p95":0.06875,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08897,"mean_force":0.04469,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49084,-0.01532,0.03908]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2888.0,"contact_point_centroid":[0.52887,0.07385,0.26797],"force_p95":0.01107,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0165,"mean_force":0.01056,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.52853,0.07384,0.26566]},{"body_a":"left_finger","body_b":"right_finger","contact_count":221.0,"contact_point_centroid":[0.56793,0.155,0.26535],"force_p95":0.01101,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01102,"mean_force":0.01011,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.5675,0.15499,0.2631]}],"total_contact_groups":14},"final_pose_error":0.0413,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.49643,0.02712,0.01602],"final_tcp_position":[0.56862,0.15497,0.26589],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":273010.11607,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":475.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1896.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.49976,-0.01424,0.14453],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11859,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":305.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1220.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.49886,-0.01542,0.04777],"tcp_start":[0.49976,-0.01424,0.14453],"tcp_to_object_dist_end":0.02231,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50371,-0.01523,0.02586],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31209,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.13168,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10799.0,"raw_peak_contact_force":0.16252,"subtask_id":"grasp_1","tcp_end":[0.49081,-0.01532,0.03904],"tcp_start":[0.49886,-0.01542,0.04777],"tcp_to_object_dist_end":0.01845,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":663.0,"n_steps_budget":750.0,"object_pos_end":[0.49998,-0.0151,0.12384],"object_pos_start":[0.50371,-0.01523,0.02586],"object_to_goal_dist_end":0.25304,"object_to_goal_dist_start":0.31209,"object_z_max":0.12373,"peak_contact_force":0.0993,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":20517.0,"raw_peak_contact_force":0.49217,"tcp_end":[0.4869,-0.01525,0.14504],"tcp_start":[0.49081,-0.01532,0.03904],"tcp_to_object_dist_end":0.02491,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49643,0.02712,0.01602],"object_pos_start":[0.49998,-0.0151,0.12384],"object_to_goal_dist_end":0.29625,"object_to_goal_dist_start":0.25304,"object_z_max":0.15797,"peak_contact_force":273010.11607,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":9338.0,"raw_peak_contact_force":1.66167,"subtask_id":"transport_arc","tcp_end":[0.56862,0.15497,0.26589],"tcp_start":[0.4869,-0.01525,0.14504],"tcp_to_object_dist_end":0.28982,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.49643,0.02712,0.01602],"object_pos_start":[0.49643,0.02712,0.01602],"object_to_goal_dist_end":0.29625,"object_to_goal_dist_start":0.29625,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1021.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.56467,0.1539,0.28744],"tcp_start":[0.56862,0.15497,0.26589],"tcp_to_object_dist_end":0.30725,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `fe7e0be33c0bb4db9d2bbbb069b6113d0e5a69a675a0d70bc1f582243e99e3cf`; realized-scene SHA-256: `8a4edc50bf1a337961423afe5cdf858aa28147f944f8fcd30a2ce1adc75d1bd6`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.51251,0.03972,0.03]},{"name":"goal","value":[0.62757,0.17252,0.14502]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.51251,0.03972,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.62757,0.17252,0.14502]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.05769,"average_solve_count":104.0,"average_success_count":104.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.16612,"descend_1.grasp_z_offset":0.00262,"grasp_1.grasp_retry_x":0.00659,"grasp_1.grasp_retry_y":-0.00741,"lift_1.lift_height":0.11609,"lift_1.lift_retry_z":0.01071,"transport_1.transport_arc_height":0.15112,"transport_1.transport_speed":0.28151},"optimized_scores":{"best_composite_score":0.11115,"best_fitness_score":0.63115,"best_task_score":0.3049},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2425.0,"contact_point_centroid":[0.53396,0.09295,-0.00238],"force_p95":0.14636,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.79819,"mean_force":0.14218,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.57329,0.12011,0.18217]},{"body_a":"world","body_b":"grasp_target","contact_count":143.0,"contact_point_centroid":[0.50943,0.0372,-0.00121],"force_p95":0.49277,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.66805,"mean_force":0.09182,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49771,0.03813,0.02994]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10083.0,"contact_point_centroid":[0.49772,0.01905,0.07687],"force_p95":0.10574,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32945,"mean_force":0.06715,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49513,0.03792,0.07506]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10607.0,"contact_point_centroid":[0.49779,0.0568,0.07491],"force_p95":0.10366,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32566,"mean_force":0.06478,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49517,0.03793,0.07334]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2718.0,"contact_point_centroid":[0.50862,0.03034,0.14971],"force_p95":0.18055,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31636,"mean_force":0.10498,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.50313,0.04859,0.15079]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2899.0,"contact_point_centroid":[0.50977,0.06851,0.15165],"force_p95":0.17329,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30046,"mean_force":0.10788,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.50472,0.0503,0.15329]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51256,0.0394,-0.00213],"force_p95":0.16141,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24225,"mean_force":0.13304,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.5005,0.03836,0.02938]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4058.0,"contact_point_centroid":[0.4999,0.01907,0.0309],"force_p95":0.081,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14809,"mean_force":0.0519,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49932,0.03827,0.0281]},{"body_a":"world","body_b":"grasp_target","contact_count":1320.0,"contact_point_centroid":[0.51251,0.03972,-0.0019],"force_p95":0.13564,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.123,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50288,0.01674,0.25152]},{"body_a":"world","body_b":"grasp_target","contact_count":2052.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50635,0.03671,0.11922]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.53392,0.09295,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.60813,0.15896,0.15692]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5004.0,"contact_point_centroid":[0.49988,0.05743,0.02992],"force_p95":0.07355,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08539,"mean_force":0.04474,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49932,0.03827,0.02811]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2324.0,"contact_point_centroid":[0.57728,0.12371,0.18414],"force_p95":0.01143,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01653,"mean_force":0.01073,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.57683,0.1237,0.18195]},{"body_a":"left_finger","body_b":"right_finger","contact_count":219.0,"contact_point_centroid":[0.6112,0.15988,0.15528],"force_p95":0.01106,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01106,"mean_force":0.01022,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61085,0.15986,0.15309]}],"total_contact_groups":14},"final_pose_error":0.02255,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.53392,0.09295,0.01602],"final_tcp_position":[0.61286,0.16012,0.1568],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":1.79819,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":331.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1320.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.50772,0.03467,0.20305],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.17717,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":513.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2052.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.50756,0.03894,0.0371],"tcp_start":[0.50772,0.03467,0.20305],"tcp_to_object_dist_end":0.01216,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51241,0.03829,0.02556],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21343,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.15303,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10862.0,"raw_peak_contact_force":0.24225,"subtask_id":"grasp_1","tcp_end":[0.49929,0.03826,0.02807],"tcp_start":[0.50756,0.03894,0.0371],"tcp_to_object_dist_end":0.01336,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":663.0,"n_steps_budget":750.0,"object_pos_end":[0.51159,0.03806,0.11954],"object_pos_start":[0.51241,0.03829,0.02556],"object_to_goal_dist_end":0.17939,"object_to_goal_dist_start":0.21343,"object_z_max":0.11943,"peak_contact_force":0.11732,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":20833.0,"raw_peak_contact_force":0.66805,"tcp_end":[0.49525,0.03794,0.13229],"tcp_start":[0.49929,0.03826,0.02807],"tcp_to_object_dist_end":0.02073,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53392,0.09295,0.01602],"object_pos_start":[0.51159,0.03806,0.11954],"object_to_goal_dist_end":0.17817,"object_to_goal_dist_start":0.17939,"object_z_max":0.1505,"peak_contact_force":0.12263,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":10366.0,"raw_peak_contact_force":1.79819,"subtask_id":"transport_arc","tcp_end":[0.61286,0.16012,0.1568],"tcp_start":[0.49525,0.03794,0.13229],"tcp_to_object_dist_end":0.17482,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53392,0.09295,0.01602],"object_pos_start":[0.53392,0.09295,0.01602],"object_to_goal_dist_end":0.17817,"object_to_goal_dist_start":0.17817,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1019.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.60648,0.15843,0.17651],"tcp_start":[0.61286,0.16012,0.1568],"tcp_to_object_dist_end":0.18791,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `28f75809d7d1d0a11ca1a36dd459ad950e5a80b6bae34006f33ac9620425f5e5`; realized-scene SHA-256: `f44a4a1356de6cb8b5dec75995af4354e38cafd01c85526c1c2a33c8dd2e5b1c`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.4827,0.04873,0.03]},{"name":"goal","value":[0.58187,0.22885,0.23048]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.4827,0.04873,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.58187,0.22885,0.23048]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.05172,"average_solve_count":116.0,"average_success_count":116.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.11914,"descend_1.grasp_z_offset":0.00125,"grasp_1.grasp_retry_x":-0.00127,"grasp_1.grasp_retry_y":-0.00733,"lift_1.lift_height":0.16768,"lift_1.lift_retry_z":0.00977,"transport_1.transport_arc_height":0.19538,"transport_1.transport_speed":0.26583},"optimized_scores":{"best_composite_score":0.03417,"best_fitness_score":0.55417,"best_task_score":0.14853},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":3388.0,"contact_point_centroid":[0.47171,0.07497,-0.00229],"force_p95":0.12435,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.8415,"mean_force":0.13634,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.51645,0.12895,0.24957]},{"body_a":"world","body_b":"grasp_target","contact_count":134.0,"contact_point_centroid":[0.47962,0.04571,-0.00122],"force_p95":0.50344,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.67827,"mean_force":0.08934,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46881,0.04687,0.02981]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":13584.0,"contact_point_centroid":[0.46941,0.06545,0.09386],"force_p95":0.12731,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31929,"mean_force":0.07201,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46639,0.04664,0.09276]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":464.0,"contact_point_centroid":[0.46999,0.03031,0.18204],"force_p95":0.21146,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31133,"mean_force":0.11564,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.4666,0.04818,0.18698]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13096.0,"contact_point_centroid":[0.4695,0.02789,0.09479],"force_p95":0.1218,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29698,"mean_force":0.07346,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46638,0.04664,0.09346]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48275,0.04843,-0.00215],"force_p95":0.1663,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.251,"mean_force":0.13447,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47142,0.04714,0.02904]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":701.0,"contact_point_centroid":[0.46997,0.06648,0.18361],"force_p95":0.18074,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23856,"mean_force":0.10108,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.46683,0.04904,0.18873]},{"body_a":"world","body_b":"grasp_target","contact_count":1824.0,"contact_point_centroid":[0.4827,0.04873,-0.00192],"force_p95":0.13359,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12289,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48964,0.02144,0.2288]},{"body_a":"world","body_b":"grasp_target","contact_count":1560.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47815,0.04579,0.09626]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.47161,0.075,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.56248,0.20505,0.24434]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5009.0,"contact_point_centroid":[0.4701,0.02779,0.03087],"force_p95":0.07029,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11647,"mean_force":0.043,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47029,0.04703,0.02791]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5531.0,"contact_point_centroid":[0.46992,0.06638,0.03022],"force_p95":0.07036,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08234,"mean_force":0.04116,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4703,0.04703,0.02791]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3408.0,"contact_point_centroid":[0.51949,0.13296,0.25402],"force_p95":0.01102,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01643,"mean_force":0.0105,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.519,0.13295,0.25177]},{"body_a":"left_finger","body_b":"right_finger","contact_count":213.0,"contact_point_centroid":[0.56481,0.20603,0.24238],"force_p95":0.01103,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01281,"mean_force":0.01036,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.56437,0.206,0.24003]}],"total_contact_groups":14},"final_pose_error":0.03072,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.47161,0.075,0.01602],"final_tcp_position":[0.56581,0.20608,0.24341],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":9748.84306,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":457.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1824.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.48072,0.04403,0.15759],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13167,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":390.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1560.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.47814,0.04781,0.03591],"tcp_start":[0.48072,0.04403,0.15759],"tcp_to_object_dist_end":0.01093,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":47.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.4826,0.04721,0.02547],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29134,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.15895,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12340.0,"raw_peak_contact_force":0.251,"subtask_id":"grasp_1","tcp_end":[0.47026,0.04703,0.02788],"tcp_start":[0.47814,0.04781,0.03591],"tcp_to_object_dist_end":0.01257,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":20.0,"n_steps":963.0,"n_steps_budget":1000.0,"object_pos_end":[0.47804,0.04706,0.16268],"object_pos_start":[0.4826,0.04721,0.02547],"object_to_goal_dist_end":0.22007,"object_to_goal_dist_start":0.29134,"object_z_max":0.16258,"peak_contact_force":0.14015,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":26814.0,"raw_peak_contact_force":0.67827,"tcp_end":[0.46675,0.04669,0.18395],"tcp_start":[0.47026,0.04703,0.02788],"tcp_to_object_dist_end":0.02408,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47161,0.075,0.01602],"object_pos_start":[0.47804,0.04706,0.16268],"object_to_goal_dist_end":0.28605,"object_to_goal_dist_start":0.22007,"object_z_max":0.1682,"peak_contact_force":9748.84306,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":7961.0,"raw_peak_contact_force":1.8415,"subtask_id":"transport_arc","tcp_end":[0.56581,0.20608,0.24341],"tcp_start":[0.46675,0.04669,0.18395],"tcp_to_object_dist_end":0.27885,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47161,0.075,0.01602],"object_pos_start":[0.47161,0.075,0.01602],"object_to_goal_dist_end":0.28605,"object_to_goal_dist_start":0.28605,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1013.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.56141,0.20451,0.26428],"tcp_start":[0.56581,0.20608,0.24341],"tcp_to_object_dist_end":0.29406,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```