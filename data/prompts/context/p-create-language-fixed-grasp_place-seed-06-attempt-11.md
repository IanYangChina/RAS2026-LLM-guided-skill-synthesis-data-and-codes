## Search State

- **Seed**: 6
- **Iteration**: 12 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 11 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 9 | 0.0448 | 0.33 | ✅ accepted |
| 10 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 9 | 0.0327 | 0.31 | ✅ accepted |
| 9 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.0676 | 0.29 | ✅ accepted |
| 8 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 7 | 0.0602 | 0.16 | ❌ rejected |
| 7 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 6 | 0.1530 | 0.25 | ✅ accepted |

**Proposal policy**: task_score is 0.33 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.045) — your mutation base

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

- **Composite score**: 0.045
- **task_score** (E): 0.333
- **fitness_score**: 0.645  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.600

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1210 |
| descend_1 | 1.00 | 1.00 | 0.1469 |
| grasp_1 | 1.00 | 1.00 | 0.0118 |
| lift_1 | 1.00 | 1.00 | 0.1317 |
| transport_1 | 0.00 | 0.00 | 0.1068 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.496, 0.021, 0.185) | (0.500, 0.024, 0.030)→(0.500, 0.024, 0.026) | 0.269→0.271 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.496, 0.021, 0.185)→(0.495, 0.024, 0.038) | (0.500, 0.024, 0.026)→(0.500, 0.024, 0.026) | 0.271→0.271 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.495, 0.024, 0.038)→(0.487, 0.023, 0.030) | (0.500, 0.024, 0.026)→(0.500, 0.023, 0.026) | 0.271→0.272 | 1.00 / 43.000 | 0.147 | 0.215 |
| lift_1 | lift | 1.00 / step_budget | (0.487, 0.023, 0.030)→(0.483, 0.023, 0.161) | (0.500, 0.023, 0.026)→(0.498, 0.023, 0.144) | 0.272→0.215 | 1.00 / 20.000 | 0.153 | 0.640 |
| transport_1 | approach | 0.00 / guard_failure | (0.483, 0.023, 0.161)→(0.529, 0.085, 0.225) | (0.498, 0.023, 0.144)→(0.539, 0.085, 0.079) | 0.215→0.181 | 0.00 / 0.000 | 0.000 | 0.323 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.556
- phase_score: 0.339
- phase_breakdown.transport_arc_score: 0.191
- phase_breakdown.descend_1_score: 0.829
- phase_breakdown.grasp_1_score: 1.000
- phase_breakdown.approach_1_score: 0.023
- phase_breakdown.release_1_score: 0.000
- grasp_place_fitness: 0.754

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.754
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.556
- **Median Q (composite search score)**: 0.008
- **K-run variance**: 0.0062
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.485


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.03704,"average_solve_count":108.0,"average_success_count":108.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.12645,"descend_1.grasp_z_offset":0.0006,"grasp_1.grasp_retry_x":0.00609,"grasp_1.grasp_retry_y":-0.00254,"lift_1.lift_height":0.14436,"lift_1.lift_retry_z":0.01495,"place_descend_1.place_height":0.08499,"transport_1.transport_arc_height":0.19795,"transport_1.transport_speed":0.12806},"optimized_scores":{"best_composite_score":-0.02804,"best_fitness_score":0.57196,"best_task_score":0.18542},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":128.0,"contact_point_centroid":[0.5004,-0.01527,-0.0011],"force_p95":0.49408,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.6906,"mean_force":0.08846,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48924,-0.01534,0.02822]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11301.0,"contact_point_centroid":[0.48974,0.00354,0.08551],"force_p95":0.11317,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34004,"mean_force":0.07278,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48662,-0.01529,0.08389]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":745.0,"contact_point_centroid":[0.49361,0.01025,0.17934],"force_p95":0.22613,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31613,"mean_force":0.14024,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.48881,-0.00782,0.18292]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1075.0,"contact_point_centroid":[0.49334,-0.02429,0.18126],"force_p95":0.2053,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3119,"mean_force":0.11471,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.4894,-0.00658,0.18558]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12173.0,"contact_point_centroid":[0.48979,-0.03403,0.08449],"force_p95":0.10942,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30851,"mean_force":0.06839,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48664,-0.01529,0.08333]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.5038,-0.01552,-0.00203],"force_p95":0.13245,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.16137,"mean_force":0.12545,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49189,-0.01537,0.02775]},{"body_a":"world","body_b":"grasp_target","contact_count":1644.0,"contact_point_centroid":[0.50382,-0.01567,-0.00192],"force_p95":0.13462,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12292,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49901,-0.00682,0.23293]},{"body_a":"world","body_b":"grasp_target","contact_count":1632.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49807,-0.01472,0.09964]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4112.0,"contact_point_centroid":[0.49123,0.00385,0.02928],"force_p95":0.07607,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11421,"mean_force":0.05172,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49072,-0.01536,0.02652]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4885.0,"contact_point_centroid":[0.49129,-0.03443,0.02836],"force_p95":0.06833,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09026,"mean_force":0.04479,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49072,-0.01536,0.02652]}],"total_contact_groups":10},"final_pose_error":0.17573,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.51683,0.01231,0.07987],"final_tcp_position":[0.50762,0.03067,0.24427],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":0.6906,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":412.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1644.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.49988,-0.01405,0.16528],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13933,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":408.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1632.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.4989,-0.01545,0.03518],"tcp_start":[0.49988,-0.01405,0.16528],"tcp_to_object_dist_end":0.0104,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50368,-0.01522,0.02588],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31208,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.13006,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10797.0,"raw_peak_contact_force":0.16137,"subtask_id":"grasp_1","tcp_end":[0.49069,-0.01535,0.02649],"tcp_start":[0.4989,-0.01545,0.03518],"tcp_to_object_dist_end":0.013,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":20.0,"n_steps":813.0,"n_steps_budget":900.0,"object_pos_end":[0.50281,-0.01518,0.14296],"object_pos_start":[0.50368,-0.01522,0.02588],"object_to_goal_dist_end":0.24329,"object_to_goal_dist_start":0.31208,"object_z_max":0.14289,"peak_contact_force":0.1813,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":23602.0,"raw_peak_contact_force":0.6906,"tcp_end":[0.4869,-0.01528,0.1589],"tcp_start":[0.49069,-0.01535,0.02649],"tcp_to_object_dist_end":0.02252,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":190.0,"n_steps_budget":1000.0,"object_pos_end":[0.51683,0.01231,0.07987],"object_pos_start":[0.50281,-0.01518,0.14296],"object_to_goal_dist_end":0.25277,"object_to_goal_dist_start":0.24329,"object_z_max":0.1865,"peak_contact_force":0.0,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1820.0,"raw_peak_contact_force":0.31613,"subtask_id":"transport_arc","tcp_end":[0.50762,0.03067,0.24427],"tcp_start":[0.4869,-0.01528,0.1589],"tcp_to_object_dist_end":0.16568,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.07273,"average_solve_count":110.0,"average_success_count":110.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.18193,"descend_1.grasp_z_offset":0.00734,"grasp_1.grasp_retry_x":-0.00993,"grasp_1.grasp_retry_y":-0.00163,"lift_1.lift_height":0.13841,"lift_1.lift_retry_z":0.0014,"place_descend_1.place_height":0.05819,"transport_1.transport_arc_height":0.17781,"transport_1.transport_speed":0.14176},"optimized_scores":{"best_composite_score":0.15441,"best_fitness_score":0.75441,"best_task_score":0.55639},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":139.0,"contact_point_centroid":[0.50946,0.03727,-0.00122],"force_p95":0.41811,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.5884,"mean_force":0.08293,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49786,0.03811,0.03484]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11248.0,"contact_point_centroid":[0.49841,0.01908,0.09048],"force_p95":0.10732,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32675,"mean_force":0.07008,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49533,0.03791,0.08857]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11709.0,"contact_point_centroid":[0.49843,0.05674,0.0882],"force_p95":0.1054,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3204,"mean_force":0.06812,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49535,0.03791,0.0865]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1247.0,"contact_point_centroid":[0.52085,0.04086,0.17407],"force_p95":0.20095,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29525,"mean_force":0.12148,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.51559,0.05915,0.17653]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51256,0.03946,-0.00213],"force_p95":0.16108,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.23533,"mean_force":0.13279,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50061,0.03834,0.03429]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1429.0,"contact_point_centroid":[0.52547,0.08186,0.17603],"force_p95":0.16141,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23439,"mean_force":0.10527,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.52017,0.06388,0.17918]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4070.0,"contact_point_centroid":[0.49997,0.01904,0.03582],"force_p95":0.08094,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15242,"mean_force":0.05186,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49943,0.03825,0.03301]},{"body_a":"world","body_b":"grasp_target","contact_count":1148.0,"contact_point_centroid":[0.51251,0.03972,-0.00188],"force_p95":0.13644,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12305,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50288,0.01636,0.25923]},{"body_a":"world","body_b":"grasp_target","contact_count":2176.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50638,0.03635,0.12934]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5001.0,"contact_point_centroid":[0.49996,0.05741,0.03483],"force_p95":0.0737,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08187,"mean_force":0.04462,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49944,0.03825,0.03302]}],"total_contact_groups":10},"final_pose_error":0.08281,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.58775,0.13131,0.07832],"final_tcp_position":[0.57789,0.12267,0.18865],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":0.5884,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":288.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1148.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.50765,0.03399,0.21847],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.1926,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":544.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2176.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.50762,0.03891,0.04203],"tcp_start":[0.50765,0.03399,0.21847],"tcp_to_object_dist_end":0.01676,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51243,0.03836,0.02555],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21338,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.15323,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10871.0,"raw_peak_contact_force":0.23533,"subtask_id":"grasp_1","tcp_end":[0.4994,0.03824,0.03298],"tcp_start":[0.50762,0.03891,0.04203],"tcp_to_object_dist_end":0.01499,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":783.0,"n_steps_budget":870.0,"object_pos_end":[0.50969,0.03812,0.14101],"object_pos_start":[0.51243,0.03836,0.02555],"object_to_goal_dist_end":0.17881,"object_to_goal_dist_start":0.21338,"object_z_max":0.14089,"peak_contact_force":0.10926,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":23096.0,"raw_peak_contact_force":0.5884,"tcp_end":[0.49559,0.03794,0.1593],"tcp_start":[0.4994,0.03824,0.03298],"tcp_to_object_dist_end":0.0231,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":221.0,"n_steps_budget":1000.0,"object_pos_end":[0.58775,0.13131,0.07832],"object_pos_start":[0.50969,0.03812,0.14101],"object_to_goal_dist_end":0.08794,"object_to_goal_dist_start":0.17881,"object_z_max":0.1667,"peak_contact_force":0.0,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2676.0,"raw_peak_contact_force":0.29525,"subtask_id":"transport_arc","tcp_end":[0.57789,0.12267,0.18865],"tcp_start":[0.49559,0.03794,0.1593],"tcp_to_object_dist_end":0.11111,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.99038,"average_solve_count":104.0,"average_success_count":104.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.13364,"descend_1.grasp_z_offset":0.00316,"grasp_1.grasp_retry_x":0.00263,"grasp_1.grasp_retry_y":-0.00258,"lift_1.lift_height":0.14761,"lift_1.lift_retry_z":0.01163,"place_descend_1.place_height":0.09392,"transport_1.transport_arc_height":0.19769,"transport_1.transport_speed":0.21043},"optimized_scores":{"best_composite_score":0.00793,"best_fitness_score":0.60793,"best_task_score":0.25759},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":135.0,"contact_point_centroid":[0.47983,0.04593,-0.00122],"force_p95":0.46473,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.64218,"mean_force":0.08519,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46888,0.04687,0.0319]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":762.0,"contact_point_centroid":[0.47677,0.03756,0.18247],"force_p95":0.20174,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.35816,"mean_force":0.12677,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.4714,0.05572,0.18585]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":854.0,"contact_point_centroid":[0.47784,0.07557,0.185],"force_p95":0.20628,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32205,"mean_force":0.12067,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.47248,0.05747,0.18888]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12613.0,"contact_point_centroid":[0.46938,0.06553,0.08906],"force_p95":0.10718,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31791,"mean_force":0.06807,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46645,0.04665,0.08741]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12287.0,"contact_point_centroid":[0.46941,0.02782,0.09115],"force_p95":0.1072,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29404,"mean_force":0.06914,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46644,0.04665,0.08933]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48275,0.04846,-0.00215],"force_p95":0.16613,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24761,"mean_force":0.13436,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47149,0.04714,0.03113]},{"body_a":"world","body_b":"grasp_target","contact_count":1656.0,"contact_point_centroid":[0.4827,0.04873,-0.00192],"force_p95":0.13462,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12292,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48983,0.02115,0.23609]},{"body_a":"world","body_b":"grasp_target","contact_count":1708.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47831,0.04558,0.10445]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5014.0,"contact_point_centroid":[0.47016,0.02779,0.03288],"force_p95":0.07001,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11893,"mean_force":0.04303,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47036,0.04703,0.02999]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5529.0,"contact_point_centroid":[0.46997,0.06637,0.03225],"force_p95":0.07037,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0805,"mean_force":0.04109,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47037,0.04703,0.03]}],"total_contact_groups":10},"final_pose_error":0.15076,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.51185,0.11186,0.07948],"final_tcp_position":[0.50065,0.1023,0.24129],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":0.64218,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":415.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1656.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.48098,0.04361,0.17196],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.14604,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":427.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1708.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.47819,0.0478,0.03801],"tcp_start":[0.48098,0.04361,0.17196],"tcp_to_object_dist_end":0.01284,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":47.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48261,0.04726,0.02547],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29131,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.15903,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12343.0,"raw_peak_contact_force":0.24761,"subtask_id":"grasp_1","tcp_end":[0.47034,0.04703,0.02997],"tcp_start":[0.47819,0.0478,0.03801],"tcp_to_object_dist_end":0.01307,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":18.0,"n_steps":843.0,"n_steps_budget":930.0,"object_pos_end":[0.48155,0.04675,0.1489],"object_pos_start":[0.48261,0.04726,0.02547],"object_to_goal_dist_end":0.22335,"object_to_goal_dist_start":0.29131,"object_z_max":0.1488,"peak_contact_force":0.16981,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":25035.0,"raw_peak_contact_force":0.64218,"tcp_end":[0.46669,0.04668,0.16604],"tcp_start":[0.47034,0.04703,0.02997],"tcp_to_object_dist_end":0.02269,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":177.0,"n_steps_budget":1000.0,"object_pos_end":[0.51185,0.11186,0.07948],"object_pos_start":[0.48155,0.04675,0.1489],"object_to_goal_dist_end":0.20346,"object_to_goal_dist_start":0.22335,"object_z_max":0.18809,"peak_contact_force":0.0,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1616.0,"raw_peak_contact_force":0.35816,"subtask_id":"transport_arc","tcp_end":[0.50065,0.1023,0.24129],"tcp_start":[0.46669,0.04668,0.16604],"tcp_to_object_dist_end":0.16248,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```