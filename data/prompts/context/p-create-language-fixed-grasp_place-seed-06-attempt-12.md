## Search State

- **Seed**: 6
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 11 | -0.0947 | 0.26 | ❌ rejected |
| 11 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 9 | 0.0448 | 0.33 | ✅ accepted |
| 10 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 9 | 0.0327 | 0.31 | ✅ accepted |
| 9 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.0676 | 0.29 | ✅ accepted |
| 8 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 7 | 0.0602 | 0.16 | ❌ rejected |

**Proposal policy**: task_score is 0.26 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.095) — your mutation base

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

- **Composite score**: -0.095
- **task_score** (E): 0.261
- **fitness_score**: 0.605  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.700

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1286 |
| descend_1 | 1.00 | 1.00 | 0.1340 |
| grasp_1 | 1.00 | 1.00 | 0.0118 |
| lift_1 | 1.00 | 1.00 | 0.1073 |
| transport_1 | 0.00 | 1.00 | 0.0000 |
| place_descend_1 | 0.00 | 1.00 | 0.1334 |
| release_1 | 1.00 | 1.00 | 0.0238 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.496, 0.022, 0.177) | (0.500, 0.024, 0.030)→(0.500, 0.024, 0.026) | 0.269→0.271 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.496, 0.022, 0.177)→(0.495, 0.024, 0.043) | (0.500, 0.024, 0.026)→(0.500, 0.024, 0.026) | 0.271→0.271 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.495, 0.024, 0.043)→(0.487, 0.023, 0.034) | (0.500, 0.024, 0.026)→(0.500, 0.024, 0.026) | 0.271→0.272 | 1.00 / 43.000 | 0.147 | 0.209 |
| lift_1 | lift | 1.00 / step_budget | (0.487, 0.023, 0.034)→(0.483, 0.023, 0.142) | (0.500, 0.024, 0.026)→(0.497, 0.023, 0.124) | 0.272→0.223 | 1.00 / 24.333 | 0.103 | 0.573 |
| transport_1 | approach | 0.00 / guard_failure | (0.483, 0.023, 0.142)→(0.483, 0.023, 0.142) | (0.497, 0.023, 0.124)→(0.498, 0.023, 0.124) | 0.223→0.223 | 1.00 / 24.333 | 0.114 | 0.152 |
| place_descend_1 | descend | 0.00 / step_budget | (0.483, 0.023, 0.142)→(0.551, 0.129, 0.118) | (0.498, 0.023, 0.124)→(0.549, 0.122, 0.026) | 0.223→0.203 | 1.00 / 10.000 | 91003.632 | 0.924 |
| release_1 | release | 1.00 / step_budget | (0.551, 0.129, 0.118)→(0.545, 0.127, 0.141) | (0.549, 0.122, 0.026)→(0.558, 0.121, 0.016) | 0.203→0.211 | 1.00 / 4.000 | 0.124 | 0.273 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.399
- phase_score: 0.283
- phase_breakdown.transport_arc_score: 0.023
- phase_breakdown.descend_1_score: 0.900
- phase_breakdown.grasp_1_score: 1.000
- phase_breakdown.approach_1_score: 0.031
- phase_breakdown.release_1_score: 0.193
- grasp_place_fitness: 0.666

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.666
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.399
- **Median Q (composite search score)**: -0.121
- **K-run variance**: 0.0018
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.392


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.81897,"average_solve_count":116.0,"average_success_count":116.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.15456,"descend_1.grasp_z_offset":0.00408,"grasp_1.grasp_retry_x":0.00474,"grasp_1.grasp_retry_y":0.00338,"lift_1.lift_height":0.1102,"lift_1.lift_retry_z":0.01492,"place_descend_1.place_height":0.12236,"transport_1.transport_arc_height":0.19566,"transport_1.transport_retry_x":0.00117,"transport_1.transport_retry_y":0.00045,"transport_1.transport_speed":0.27476},"optimized_scores":{"best_composite_score":-0.12901,"best_fitness_score":0.57099,"best_task_score":0.18499},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1017.0,"contact_point_centroid":[0.54058,0.09754,-0.0027],"force_p95":0.4132,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.06854,"mean_force":0.15374,"phase_index":5.0,"phase_name":"place_descend_1","phase_type":"descend","tcp_position_centroid":[0.53612,0.09252,0.12074]},{"body_a":"world","body_b":"grasp_target","contact_count":135.0,"contact_point_centroid":[0.50077,-0.01515,-0.0011],"force_p95":0.46659,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.62445,"mean_force":0.08339,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48934,-0.01533,0.03168]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9924.0,"contact_point_centroid":[0.48897,0.00362,0.07599],"force_p95":0.10371,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33621,"mean_force":0.06522,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48672,-0.01528,0.07414]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10430.0,"contact_point_centroid":[0.4891,-0.03414,0.07459],"force_p95":0.10187,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30284,"mean_force":0.06275,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48674,-0.01528,0.07315]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7008.0,"contact_point_centroid":[0.50829,0.00938,0.12163],"force_p95":0.15544,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22537,"mean_force":0.09038,"phase_index":5.0,"phase_name":"place_descend_1","phase_type":"descend","tcp_position_centroid":[0.5044,0.02781,0.12284]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7769.0,"contact_point_centroid":[0.50984,0.04797,0.12147],"force_p95":0.13113,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.213,"mean_force":0.08374,"phase_index":5.0,"phase_name":"place_descend_1","phase_type":"descend","tcp_position_centroid":[0.50535,0.02976,0.12276]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50381,-0.01553,-0.00203],"force_p95":0.13279,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15972,"mean_force":0.12552,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49202,-0.01536,0.0312]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":36.0,"contact_point_centroid":[0.49207,-0.03382,0.13089],"force_p95":0.12595,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14072,"mean_force":0.08869,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.48682,-0.01527,0.12857]},{"body_a":"world","body_b":"grasp_target","contact_count":1304.0,"contact_point_centroid":[0.50382,-0.01567,-0.0019],"force_p95":0.13564,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.123,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49916,-0.00657,0.24716]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":39.0,"contact_point_centroid":[0.49224,0.00342,0.13017],"force_p95":0.1285,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13291,"mean_force":0.08542,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.48682,-0.01527,0.12857]},{"body_a":"world","body_b":"grasp_target","contact_count":1928.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49822,-0.01453,0.11512]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.54068,0.09765,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.5381,0.10492,0.12321]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4112.0,"contact_point_centroid":[0.49132,0.00386,0.03273],"force_p95":0.07616,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11756,"mean_force":0.05174,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49085,-0.01535,0.02997]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4885.0,"contact_point_centroid":[0.49138,-0.03443,0.03182],"force_p95":0.06844,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0897,"mean_force":0.04477,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49085,-0.01535,0.02997]},{"body_a":"left_finger","body_b":"right_finger","contact_count":728.0,"contact_point_centroid":[0.53854,0.09674,0.12289],"force_p95":0.01298,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01614,"mean_force":0.01093,"phase_index":5.0,"phase_name":"place_descend_1","phase_type":"descend","tcp_position_centroid":[0.53821,0.09674,0.12062]},{"body_a":"left_finger","body_b":"right_finger","contact_count":221.0,"contact_point_centroid":[0.54137,0.10561,0.12021],"force_p95":0.01098,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01099,"mean_force":0.01009,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.54111,0.1056,0.11809]}],"total_contact_groups":16},"final_pose_error":0.09316,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.54068,0.09765,0.01602],"final_tcp_position":[0.54267,0.10564,0.12037],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":273010.52704,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":327.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1304.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.50002,-0.01367,0.19339],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16742,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":482.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1928.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.49899,-0.01544,0.03864],"tcp_start":[0.50002,-0.01367,0.19339],"tcp_to_object_dist_end":0.01351,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50369,-0.01522,0.02587],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31208,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.13048,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10797.0,"raw_peak_contact_force":0.15972,"subtask_id":"grasp_1","tcp_end":[0.49082,-0.01535,0.02994],"tcp_start":[0.49899,-0.01544,0.03864],"tcp_to_object_dist_end":0.01349,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":633.0,"n_steps_budget":720.0,"object_pos_end":[0.50283,-0.01511,0.11557],"object_pos_start":[0.50369,-0.01522,0.02587],"object_to_goal_dist_end":0.25626,"object_to_goal_dist_start":0.31208,"object_z_max":0.11546,"peak_contact_force":0.10194,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":20489.0,"raw_peak_contact_force":0.62445,"tcp_end":[0.48679,-0.01527,0.12851],"tcp_start":[0.49082,-0.01535,0.02994],"tcp_to_object_dist_end":0.02061,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.5029,-0.01511,0.11559],"object_pos_start":[0.50283,-0.01511,0.11557],"object_to_goal_dist_end":0.25623,"object_to_goal_dist_start":0.25626,"object_z_max":0.11559,"peak_contact_force":0.11174,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":75.0,"raw_peak_contact_force":0.14072,"subtask_id":"transport_arc","tcp_end":[0.48685,-0.01527,0.1286],"tcp_start":[0.48683,-0.01527,0.1286],"tcp_to_object_dist_end":0.02066,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54068,0.09765,0.01602],"object_pos_start":[0.50296,-0.01512,0.11552],"object_to_goal_dist_end":0.25312,"object_to_goal_dist_start":0.25625,"object_z_max":0.11552,"peak_contact_force":273010.52704,"phase_name":"place_descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":16522.0,"raw_peak_contact_force":1.06854,"tcp_end":[0.54267,0.10564,0.12037],"tcp_start":[0.48685,-0.01527,0.1286],"tcp_to_object_dist_end":0.10467,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54068,0.09765,0.01602],"object_pos_start":[0.54068,0.09765,0.01602],"object_to_goal_dist_end":0.25312,"object_to_goal_dist_start":0.25312,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1021.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.53629,0.10453,0.14377],"tcp_start":[0.54267,0.10564,0.12037],"tcp_to_object_dist_end":0.12801,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.82353,"average_solve_count":119.0,"average_success_count":119.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.16669,"descend_1.grasp_z_offset":0.01737,"grasp_1.grasp_retry_x":0.00166,"grasp_1.grasp_retry_y":-0.00247,"lift_1.lift_height":0.12024,"lift_1.lift_retry_z":0.01643,"place_descend_1.place_height":0.08846,"transport_1.transport_arc_height":0.09646,"transport_1.transport_retry_x":0.00362,"transport_1.transport_retry_y":-0.00927,"transport_1.transport_speed":0.15884},"optimized_scores":{"best_composite_score":-0.03413,"best_fitness_score":0.66587,"best_task_score":0.39856},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":468.0,"contact_point_centroid":[0.60725,0.12497,-0.00288],"force_p95":0.54627,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57407,"mean_force":0.20499,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57541,0.12842,0.08388]},{"body_a":"world","body_b":"grasp_target","contact_count":144.0,"contact_point_centroid":[0.50984,0.03762,-0.00121],"force_p95":0.33335,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.46008,"mean_force":0.07003,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49799,0.03813,0.04464]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10989.0,"contact_point_centroid":[0.49815,0.01911,0.09376],"force_p95":0.09832,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3139,"mean_force":0.06401,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49548,0.03793,0.09182]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10963.0,"contact_point_centroid":[0.49778,0.05689,0.09056],"force_p95":0.1039,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30345,"mean_force":0.06501,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49551,0.03793,0.0887]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11378.0,"contact_point_centroid":[0.54387,0.06582,0.11276],"force_p95":0.13657,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26668,"mean_force":0.08346,"phase_index":5.0,"phase_name":"place_descend_1","phase_type":"descend","tcp_position_centroid":[0.53786,0.08449,0.11197]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":317.0,"contact_point_centroid":[0.58751,0.14519,0.07425],"force_p95":0.20416,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24629,"mean_force":0.09944,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.58086,0.12979,0.07641]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12659.0,"contact_point_centroid":[0.54724,0.10631,0.10997],"force_p95":0.10464,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23059,"mean_force":0.07476,"phase_index":5.0,"phase_name":"place_descend_1","phase_type":"descend","tcp_position_centroid":[0.54106,0.0878,0.10949]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51255,0.03953,-0.00212],"force_p95":0.1568,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21813,"mean_force":0.13176,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50073,0.03836,0.04411]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":56.0,"contact_point_centroid":[0.58803,0.11225,0.07119],"force_p95":0.17549,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21762,"mean_force":0.13786,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.58161,0.12995,0.07751]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":36.0,"contact_point_centroid":[0.50095,0.05685,0.15342],"force_p95":0.14754,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15969,"mean_force":0.09634,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.49569,0.03796,0.15119]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":42.0,"contact_point_centroid":[0.50148,0.01942,0.15389],"force_p95":0.14847,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15584,"mean_force":0.09029,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.49569,0.03796,0.15119]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4084.0,"contact_point_centroid":[0.50004,0.01906,0.04563],"force_p95":0.08047,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1474,"mean_force":0.05186,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49957,0.03826,0.04283]},{"body_a":"world","body_b":"grasp_target","contact_count":1316.0,"contact_point_centroid":[0.51251,0.03972,-0.0019],"force_p95":0.13564,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.123,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50288,0.01674,0.25178]},{"body_a":"world","body_b":"grasp_target","contact_count":1876.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50642,0.03669,0.12706]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4996.0,"contact_point_centroid":[0.50006,0.05741,0.04465],"force_p95":0.07328,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07644,"mean_force":0.04443,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49958,0.03826,0.04283]}],"total_contact_groups":15},"final_pose_error":0.06603,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.61363,0.12546,0.01607],"final_tcp_position":[0.58204,0.12988,0.07822],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":0.57407,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":330.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1316.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.50772,0.03467,0.20356],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.17768,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":469.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1876.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.50764,0.03891,0.05186],"tcp_start":[0.50772,0.03467,0.20356],"tcp_to_object_dist_end":0.02631,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51246,0.03853,0.02558],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21324,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.15066,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10880.0,"raw_peak_contact_force":0.21813,"subtask_id":"grasp_1","tcp_end":[0.49954,0.03826,0.04279],"tcp_start":[0.50764,0.03891,0.05186],"tcp_to_object_dist_end":0.02152,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":26.0,"n_steps":693.0,"n_steps_budget":780.0,"object_pos_end":[0.50796,0.03824,0.12693],"object_pos_start":[0.51246,0.03853,0.02558],"object_to_goal_dist_end":0.18074,"object_to_goal_dist_start":0.21324,"object_z_max":0.12681,"peak_contact_force":0.09817,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":22096.0,"raw_peak_contact_force":0.46008,"tcp_end":[0.49565,0.03795,0.15114],"tcp_start":[0.49954,0.03826,0.04279],"tcp_to_object_dist_end":0.02716,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":26.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.50802,0.03824,0.12696],"object_pos_start":[0.50796,0.03824,0.12693],"object_to_goal_dist_end":0.18069,"object_to_goal_dist_start":0.18074,"object_z_max":0.12696,"peak_contact_force":0.11731,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":78.0,"raw_peak_contact_force":0.15969,"subtask_id":"transport_arc","tcp_end":[0.49572,0.03796,0.15122],"tcp_start":[0.49569,0.03796,0.15123],"tcp_to_object_dist_end":0.0272,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":13.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.58636,0.13005,0.04583],"object_pos_start":[0.50806,0.03825,0.1269],"object_to_goal_dist_end":0.1155,"object_to_goal_dist_start":0.18066,"object_z_max":0.1269,"peak_contact_force":0.24699,"phase_name":"place_descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":24037.0,"raw_peak_contact_force":0.26668,"tcp_end":[0.58204,0.12988,0.07822],"tcp_start":[0.49572,0.03796,0.15122],"tcp_to_object_dist_end":0.03267,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.61363,0.12546,0.01607],"object_pos_start":[0.58636,0.13005,0.04583],"object_to_goal_dist_end":0.13798,"object_to_goal_dist_start":0.1155,"object_z_max":0.04583,"peak_contact_force":0.12533,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":841.0,"raw_peak_contact_force":0.57407,"subtask_id":"release_1","tcp_end":[0.57468,0.12824,0.1],"tcp_start":[0.58204,0.12988,0.07822],"tcp_to_object_dist_end":0.09258,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.82051,"average_solve_count":117.0,"average_success_count":117.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.09513,"descend_1.grasp_z_offset":0.00367,"grasp_1.grasp_retry_x":-0.00013,"grasp_1.grasp_retry_y":0.00269,"lift_1.lift_height":0.12621,"lift_1.lift_retry_z":0.01134,"place_descend_1.place_height":0.05499,"transport_1.transport_arc_height":0.05559,"transport_1.transport_retry_x":-0.00036,"transport_1.transport_retry_y":-0.00209,"transport_1.transport_speed":0.26651},"optimized_scores":{"best_composite_score":-0.12081,"best_fitness_score":0.57919,"best_task_score":0.20093},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1499.0,"contact_point_centroid":[0.51942,0.13819,-0.00253],"force_p95":0.30105,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.43582,"mean_force":0.1565,"phase_index":5.0,"phase_name":"place_descend_1","phase_type":"descend","tcp_position_centroid":[0.51813,0.13337,0.15366]},{"body_a":"world","body_b":"grasp_target","contact_count":138.0,"contact_point_centroid":[0.47975,0.04582,-0.00122],"force_p95":0.44538,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.63344,"mean_force":0.08454,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46874,0.04682,0.03231]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11399.0,"contact_point_centroid":[0.46889,0.06551,0.08123],"force_p95":0.10447,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31901,"mean_force":0.06526,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4663,0.04659,0.0795]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10988.0,"contact_point_centroid":[0.4689,0.02772,0.08318],"force_p95":0.10481,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2926,"mean_force":0.06676,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46629,0.04659,0.08125]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48276,0.04846,-0.00216],"force_p95":0.16758,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24782,"mean_force":0.13471,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47136,0.04709,0.03151]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4685.0,"contact_point_centroid":[0.48663,0.05794,0.14398],"force_p95":0.16038,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23046,"mean_force":0.10182,"phase_index":5.0,"phase_name":"place_descend_1","phase_type":"descend","tcp_position_centroid":[0.48211,0.07624,0.14555]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5707.0,"contact_point_centroid":[0.48741,0.09563,0.14376],"force_p95":0.1382,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19349,"mean_force":0.08718,"phase_index":5.0,"phase_name":"place_descend_1","phase_type":"descend","tcp_position_centroid":[0.48294,0.07755,0.14574]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":32.0,"contact_point_centroid":[0.47216,0.06521,0.14688],"force_p95":0.14265,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15565,"mean_force":0.09688,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.46645,0.04662,0.14524]},{"body_a":"world","body_b":"grasp_target","contact_count":2092.0,"contact_point_centroid":[0.4827,0.04873,-0.00193],"force_p95":0.13221,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12286,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48937,0.02179,0.21679]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":34.0,"contact_point_centroid":[0.47241,0.02808,0.14676],"force_p95":0.13179,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13699,"mean_force":0.0928,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.46645,0.04661,0.14524]},{"body_a":"world","body_b":"grasp_target","contact_count":1224.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47798,0.04602,0.08582]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.51941,0.13914,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.5246,0.1489,0.15902]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5014.0,"contact_point_centroid":[0.47006,0.02773,0.03337],"force_p95":0.07073,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11866,"mean_force":0.04304,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47024,0.04698,0.03038]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5536.0,"contact_point_centroid":[0.46988,0.06632,0.03274],"force_p95":0.07076,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08042,"mean_force":0.04106,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47024,0.04698,0.03039]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1373.0,"contact_point_centroid":[0.52018,0.13585,0.15628],"force_p95":0.01176,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01556,"mean_force":0.01067,"phase_index":5.0,"phase_name":"place_descend_1","phase_type":"descend","tcp_position_centroid":[0.5197,0.13583,0.15403]},{"body_a":"left_finger","body_b":"right_finger","contact_count":219.0,"contact_point_centroid":[0.52749,0.14975,0.15625],"force_p95":0.011,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01101,"mean_force":0.01016,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.52729,0.14972,0.15388]}],"total_contact_groups":16},"final_pose_error":0.09708,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.51941,0.13914,0.01602],"final_tcp_position":[0.52868,0.14999,0.15612],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":1.43582,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":524.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2092.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.48035,0.04454,0.13389],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.10798,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":306.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1224.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.47806,0.04775,0.03839],"tcp_start":[0.48035,0.04454,0.13389],"tcp_to_object_dist_end":0.01325,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":47.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48261,0.04722,0.02545],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29134,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.16023,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12350.0,"raw_peak_contact_force":0.24782,"subtask_id":"grasp_1","tcp_end":[0.47021,0.04697,0.03035],"tcp_start":[0.47806,0.04775,0.03839],"tcp_to_object_dist_end":0.01334,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":723.0,"n_steps_budget":810.0,"object_pos_end":[0.48167,0.04679,0.12979],"object_pos_start":[0.48261,0.04722,0.02545],"object_to_goal_dist_end":0.23093,"object_to_goal_dist_start":0.29134,"object_z_max":0.12968,"peak_contact_force":0.10983,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":22525.0,"raw_peak_contact_force":0.63344,"tcp_end":[0.46641,0.04661,0.14518],"tcp_start":[0.47021,0.04697,0.03035],"tcp_to_object_dist_end":0.02168,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.48173,0.0468,0.12982],"object_pos_start":[0.48167,0.04679,0.12979],"object_to_goal_dist_end":0.23088,"object_to_goal_dist_start":0.23093,"object_z_max":0.12982,"peak_contact_force":0.11251,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":66.0,"raw_peak_contact_force":0.15565,"subtask_id":"transport_arc","tcp_end":[0.46648,0.04662,0.14527],"tcp_start":[0.46648,0.04662,0.14528],"tcp_to_object_dist_end":0.02172,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51941,0.13914,0.01602],"object_pos_start":[0.48173,0.04681,0.12974],"object_to_goal_dist_end":0.24072,"object_to_goal_dist_start":0.2309,"object_z_max":0.12974,"peak_contact_force":0.12263,"phase_name":"place_descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":13264.0,"raw_peak_contact_force":1.43582,"tcp_end":[0.52868,0.14999,0.15612],"tcp_start":[0.46648,0.04662,0.14527],"tcp_to_object_dist_end":0.14083,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51941,0.13914,0.01602],"object_pos_start":[0.51941,0.13914,0.01602],"object_to_goal_dist_end":0.24072,"object_to_goal_dist_start":0.24072,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1019.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.52302,0.14842,0.17959],"tcp_start":[0.52868,0.14999,0.15612],"tcp_to_object_dist_end":0.16387,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```